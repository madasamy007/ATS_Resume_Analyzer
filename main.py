"""
FastAPI Backend - ATS Resume Analyzer API
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import shutil
import uuid
from pathlib import Path
import json

from database import get_db, init_db, JobRole, Resume, Analysis, EmailLog
from resume_parser import ResumeParser
from ai_scorer import AIScorer
from email_service import EmailService
from pydantic import BaseModel, field_serializer

# Initialize FastAPI app
app = FastAPI(
    title="ATS Resume Analyzer API",
    description="AI-powered Resume Analysis and Candidate Shortlisting System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
parser = ResumeParser()
scorer = AIScorer()
email_service = EmailService()

# Create uploads directory
UPLOAD_DIR = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Initialize database
init_db()

# Mount static files (for frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")


# Pydantic Models
class JobRoleCreate(BaseModel):
    title: str
    description: str
    required_skills: Optional[List[str]] = []
    required_experience: Optional[int] = 0


class JobRoleResponse(BaseModel):
    id: int
    title: str
    description: str
    required_skills: Optional[List[str]]
    required_experience: Optional[int]
    created_at: datetime

    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime, _info):
        return dt.isoformat() if dt else None

    class Config:
        from_attributes = True


class AnalysisResponse(BaseModel):
    id: int
    resume_id: int
    job_role_id: int
    overall_score: float
    semantic_score: float
    skills_score: float
    experience_score: float
    education_score: float
    projects_score: float
    explanation: dict
    is_shortlisted: bool
    created_at: datetime

    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime, _info):
        return dt.isoformat() if dt else None

    class Config:
        from_attributes = True


# API Routes

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve frontend"""
    return FileResponse("static/index.html")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "ATS Resume Analyzer API is running"}


# Job Role Endpoints

@app.get("/api/job-roles", response_model=List[JobRoleResponse])
async def get_job_roles(db: Session = Depends(get_db)):
    """Get all job roles"""
    roles = db.query(JobRole).all()
    return roles


@app.post("/api/job-roles", response_model=JobRoleResponse)
async def create_job_role(role: JobRoleCreate, db: Session = Depends(get_db)):
    """Create a new job role"""
    db_role = JobRole(
        title=role.title,
        description=role.description,
        required_skills=role.required_skills,
        required_experience=role.required_experience
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


@app.get("/api/job-roles/{role_id}", response_model=JobRoleResponse)
async def get_job_role(role_id: int, db: Session = Depends(get_db)):
    """Get job role by ID"""
    role = db.query(JobRole).filter(JobRole.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Job role not found")
    return role


# Resume Analysis Endpoints

@app.post("/api/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    job_role_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    Analyze a single resume against a job role
    """
    if not job_role_id:
        raise HTTPException(status_code=400, detail="job_role_id is required")
    
    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ['.pdf', '.docx', '.doc']:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
    
    # Get job role
    job_role = db.query(JobRole).filter(JobRole.id == job_role_id).first()
    if not job_role:
        raise HTTPException(status_code=404, detail="Job role not found")
    
    # Save uploaded file (handle duplicate filenames)
    unique_filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    file_path = UPLOAD_DIR / unique_filename
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Parse resume
        parsed_data = parser.parse(str(file_path))
        
        # Save resume to database
        db_resume = Resume(
            filename=file.filename,
            file_path=str(file_path),
            candidate_name=parsed_data.get('candidate_name'),
            candidate_email=parsed_data.get('candidate_email'),
            raw_text=parsed_data.get('raw_text'),
            parsed_data=parsed_data
        )
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)
        
        # Prepare job role data for scoring
        job_role_data = {
            'title': job_role.title,
            'description': job_role.description,
            'required_skills': job_role.required_skills or [],
            'required_experience': job_role.required_experience or 0
        }
        
        # Calculate scores
        scoring_result = scorer.calculate_overall_score(parsed_data, job_role_data)
        
        # Save analysis
        db_analysis = Analysis(
            resume_id=db_resume.id,
            job_role_id=job_role_id,
            overall_score=scoring_result['overall_score'],
            semantic_score=scoring_result['semantic_score'],
            skills_score=scoring_result['skills_score'],
            experience_score=scoring_result['experience_score'],
            education_score=scoring_result['education_score'],
            projects_score=scoring_result['projects_score'],
            explanation=scoring_result['explanation'],
            is_shortlisted=scoring_result['is_shortlisted']
        )
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        
        return {
            "analysis_id": db_analysis.id,
            "resume_id": db_resume.id,
            "candidate_name": db_resume.candidate_name,
            "candidate_email": db_resume.candidate_email,
            "scores": {
                "overall": scoring_result['overall_score'],
                "semantic": scoring_result['semantic_score'],
                "skills": scoring_result['skills_score'],
                "experience": scoring_result['experience_score'],
                "education": scoring_result['education_score'],
                "projects": scoring_result['projects_score']
            },
            "explanation": scoring_result['explanation'],
            "is_shortlisted": scoring_result['is_shortlisted']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing resume: {str(e)}")


@app.post("/api/analyze/bulk")
async def analyze_resumes_bulk(
    files: List[UploadFile] = File(...),
    job_role_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    Analyze multiple resumes in bulk
    """
    if not job_role_id:
        raise HTTPException(status_code=400, detail="job_role_id is required")
    
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    # Get job role
    job_role = db.query(JobRole).filter(JobRole.id == job_role_id).first()
    if not job_role:
        raise HTTPException(status_code=404, detail="Job role not found")
    
    results = []
    shortlisted_candidates = []
    
    for file in files:
        try:
            # Validate file type
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in ['.pdf', '.docx', '.doc']:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "message": "Unsupported file format"
                })
                continue
            
            # Save file (handle duplicate filenames)
            unique_filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
            file_path = UPLOAD_DIR / unique_filename
            UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Parse resume
            parsed_data = parser.parse(str(file_path))
            
            # Save resume
            db_resume = Resume(
                filename=file.filename,
                file_path=str(file_path),
                candidate_name=parsed_data.get('candidate_name'),
                candidate_email=parsed_data.get('candidate_email'),
                raw_text=parsed_data.get('raw_text'),
                parsed_data=parsed_data
            )
            db.add(db_resume)
            db.commit()
            db.refresh(db_resume)
            
            # Score resume
            job_role_data = {
                'title': job_role.title,
                'description': job_role.description,
                'required_skills': job_role.required_skills or [],
                'required_experience': job_role.required_experience or 0
            }
            
            scoring_result = scorer.calculate_overall_score(parsed_data, job_role_data)
            
            # Save analysis
            db_analysis = Analysis(
                resume_id=db_resume.id,
                job_role_id=job_role_id,
                overall_score=scoring_result['overall_score'],
                semantic_score=scoring_result['semantic_score'],
                skills_score=scoring_result['skills_score'],
                experience_score=scoring_result['experience_score'],
                education_score=scoring_result['education_score'],
                projects_score=scoring_result['projects_score'],
                explanation=scoring_result['explanation'],
                is_shortlisted=scoring_result['is_shortlisted']
            )
            db.add(db_analysis)
            db.commit()
            db.refresh(db_analysis)
            
            result = {
                "filename": file.filename,
                "status": "success",
                "analysis_id": db_analysis.id,
                "candidate_name": db_resume.candidate_name,
                "candidate_email": db_resume.candidate_email,
                "overall_score": scoring_result['overall_score'],
                "is_shortlisted": scoring_result['is_shortlisted']
            }
            results.append(result)
            
            # Collect shortlisted candidates
            if scoring_result['is_shortlisted'] and db_resume.candidate_email:
                shortlisted_candidates.append({
                    "email": db_resume.candidate_email,
                    "name": db_resume.candidate_name or "Candidate",
                    "score": scoring_result['overall_score'],
                    "analysis_id": db_analysis.id
                })
        
        except Exception as e:
            # Rollback on error to allow next file to be processed
            db.rollback()
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": str(e)
            })
    
    return {
        "total_processed": len(results),
        "successful": len([r for r in results if r.get('status') == 'success']),
        "shortlisted_count": len(shortlisted_candidates),
        "results": results,
        "shortlisted_candidates": shortlisted_candidates
    }


@app.get("/api/analyses", response_model=List[AnalysisResponse])
async def get_analyses(
    job_role_id: Optional[int] = None,
    shortlisted_only: Optional[bool] = False,
    db: Session = Depends(get_db)
):
    """Get all analyses, optionally filtered by job role or shortlisted status"""
    query = db.query(Analysis)
    
    if job_role_id:
        query = query.filter(Analysis.job_role_id == job_role_id)
    
    if shortlisted_only:
        query = query.filter(Analysis.is_shortlisted == True)
    
    analyses = query.order_by(Analysis.overall_score.desc()).all()
    return analyses


@app.get("/api/analyses/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Get analysis details by ID"""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


@app.get("/api/shortlisted")
async def get_shortlisted(
    job_role_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all shortlisted candidates with details"""
    query = db.query(Analysis).filter(Analysis.is_shortlisted == True)
    
    if job_role_id:
        query = query.filter(Analysis.job_role_id == job_role_id)
    
    analyses = query.order_by(Analysis.overall_score.desc()).all()
    
    shortlisted = []
    for analysis in analyses:
        resume = db.query(Resume).filter(Resume.id == analysis.resume_id).first()
        job_role = db.query(JobRole).filter(JobRole.id == analysis.job_role_id).first()
        
        shortlisted.append({
            "analysis_id": analysis.id,
            "candidate_name": resume.candidate_name,
            "candidate_email": resume.candidate_email,
            "job_role": job_role.title,
            "overall_score": analysis.overall_score,
            "scores": {
                "semantic": analysis.semantic_score,
                "skills": analysis.skills_score,
                "experience": analysis.experience_score,
                "education": analysis.education_score,
                "projects": analysis.projects_score
            },
            "explanation": analysis.explanation
        })
    
    return {
        "count": len(shortlisted),
        "candidates": shortlisted
    }


@app.post("/api/shortlisted/send-emails")
async def send_shortlist_emails(
    job_role_id: int = Query(..., description="Job role ID"),
    db: Session = Depends(get_db)
):
    """Send emails to all shortlisted candidates for a job role"""
    # Get shortlisted analyses
    analyses = db.query(Analysis).filter(
        Analysis.job_role_id == job_role_id,
        Analysis.is_shortlisted == True
    ).all()
    
    if not analyses:
        return {"message": "No shortlisted candidates found", "emails_sent": 0}
    
    job_role = db.query(JobRole).filter(JobRole.id == job_role_id).first()
    if not job_role:
        raise HTTPException(status_code=404, detail="Job role not found")
    
    # Prepare candidates list
    candidates = []
    for analysis in analyses:
        resume = db.query(Resume).filter(Resume.id == analysis.resume_id).first()
        if resume.candidate_email:
            candidates.append({
                "email": resume.candidate_email,
                "name": resume.candidate_name or "Candidate",
                "score": analysis.overall_score,
                "analysis_id": analysis.id
            })
    
    if not candidates:
        return {"message": "No email addresses found for shortlisted candidates", "emails_sent": 0}
    
    # Send emails
    try:
        email_results = email_service.send_bulk_emails(candidates, job_role.title)
        
        # Log email sends
        for i, result in enumerate(email_results):
            analysis_id = candidates[i]['analysis_id']
            recipient_email = result.get('email', candidates[i]['email'])
            
            db_email_log = EmailLog(
                analysis_id=analysis_id,
                recipient_email=recipient_email,
                subject=f"Shortlisted for {job_role.title}",
                status=result.get('status', 'failed'),
                sent_at=result.get('sent_at'),
                error_message=result.get('error') if result.get('status') != 'sent' else None
            )
            db.add(db_email_log)
        
        db.commit()
        
        sent_count = len([r for r in email_results if r.get('status') == 'sent'])
        failed_count = len([r for r in email_results if r.get('status') == 'failed'])
        
        return {
            "message": f"Emails sent to {sent_count} candidates",
            "total_candidates": len(candidates),
            "emails_sent": sent_count,
            "emails_failed": failed_count,
            "email_results": email_results
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error sending emails: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

