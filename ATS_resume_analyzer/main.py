"""
Main FastAPI Application for High-Scale Semantic ATS Resume Screening System
Handles bulk uploads, semantic analysis, ML predictions, and automated email sending
"""

from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import sqlite3
import asyncio
from typing import List, Optional
from datetime import datetime
import aiofiles
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import pandas as pd
import json

# Import utility functions
from utils import (
    extract_text_from_resume,
    extract_email_from_text,
    compute_semantic_score,
    get_embedding,
    load_ml_model,
    predict_fit,
    extract_skills_missing
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="ATS Resume Screening System", version="1.0.0")

# Templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Database setup
DB_PATH = "database.db"

def init_database():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS screening_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            email TEXT,
            semantic_score REAL,
            ml_fit INTEGER,
            final_status TEXT,
            email_sent INTEGER DEFAULT 0,
            email_status TEXT DEFAULT 'Pending',
            missing_skills TEXT,
            job_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

# Initialize database on startup
init_database()

# Load ML model
ml_model = None
try:
    ml_model = load_ml_model()
    if ml_model:
        print("ML model loaded successfully!")
except Exception as e:
    print(f"Warning: Could not load ML model: {str(e)}")

# Global variables for processing state
processing_state = {
    "total_files": 0,
    "processed_files": 0,
    "current_status": "idle"
}

# Email configuration from environment variables
GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD", "")
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

async def send_email_async(to_email: str, subject: str, body: str) -> bool:
    """
    Send email asynchronously using Gmail SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body
        
    Returns:
        True if email sent successfully, False otherwise
    """
    if not GMAIL_USER or not GMAIL_PASSWORD:
        print("Gmail credentials not configured. Skipping email send.")
        return False
    
    try:
        message = MIMEMultipart()
        message["From"] = GMAIL_USER
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=GMAIL_USER,
            password=GMAIL_PASSWORD,
            start_tls=True
        )
        
        return True
    except Exception as e:
        print(f"Error sending email to {to_email}: {str(e)}")
        return False

async def process_single_resume(file_path: str, filename: str, job_description: str, 
                                job_embedding, batch_results: list):
    """
    Process a single resume: extract text, compute score, predict fit, extract email
    
    Args:
        file_path: Path to the resume file
        filename: Original filename
        job_description: Job description text
        job_embedding: Pre-computed job description embedding
        batch_results: List to append results to
    """
    try:
        # Extract text from resume
        resume_text = extract_text_from_resume(file_path)
        
        if not resume_text:
            print(f"Warning: Could not extract text from {filename}")
            batch_results.append({
                "filename": filename,
                "email": None,
                "semantic_score": 0.0,
                "ml_fit": 0,
                "final_status": "Error",
                "email_sent": 0,
                "email_status": "Failed",
                "missing_skills": "[]"
            })
            return
        
        # Extract email
        email = extract_email_from_text(resume_text)
        
        # Compute semantic score
        semantic_score = compute_semantic_score(resume_text, job_description, job_embedding)
        
        # Get resume embedding for ML prediction
        resume_embedding = get_embedding(resume_text)
        
        # Predict Fit/Not Fit using ML model
        ml_fit = predict_fit(resume_embedding, ml_model) if ml_model else 1
        
        # Determine final status
        if semantic_score >= 80 and ml_fit == 1:
            final_status = "Shortlisted"
            email_subject = "Application Update - Shortlisted"
            email_body = f"Dear Candidate,\n\nYour resume scored {semantic_score}%. You are shortlisted for the next round.\n\nBest regards,\nHR Team"
        else:
            final_status = "Rejected"
            email_subject = "Application Update"
            email_body = "Dear Candidate,\n\nThank you for applying. Your profile does not fully match current requirements.\n\nBest regards,\nHR Team"
        
        # Extract missing skills
        missing_skills = extract_skills_missing(resume_text, job_description)
        
        # Send email asynchronously (don't wait)
        email_sent = False
        email_status = "Pending"
        if email:
            email_sent = await send_email_async(email, email_subject, email_body)
            email_status = "Sent Automatically" if email_sent else "Failed"
        else:
            email_status = "No Email Found"
        
        # Store result
        result = {
            "filename": filename,
            "email": email,
            "semantic_score": semantic_score,
            "ml_fit": ml_fit,
            "final_status": final_status,
            "email_sent": 1 if email_sent else 0,
            "email_status": email_status,
            "missing_skills": json.dumps(missing_skills),
            "job_description": job_description
        }
        
        batch_results.append(result)
        
        # Save to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO screening_results 
            (filename, email, semantic_score, ml_fit, final_status, email_sent, email_status, missing_skills, job_description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result["filename"], result["email"], result["semantic_score"],
            result["ml_fit"], result["final_status"], result["email_sent"],
            result["email_status"], result["missing_skills"], result["job_description"]
        ))
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
        batch_results.append({
            "filename": filename,
            "email": None,
            "semantic_score": 0.0,
            "ml_fit": 0,
            "final_status": "Error",
            "email_sent": 0,
            "email_status": "Failed",
            "missing_skills": "[]"
        })

async def process_resumes_batch(files: List[UploadFile], job_description: str, 
                               batch_size: int = 50):
    """
    Process resumes in batches for efficient handling of large volumes
    
    Args:
        files: List of uploaded files
        job_description: Job description text
        batch_size: Number of files to process in each batch
        
    Returns:
        List of all processing results
    """
    global processing_state
    
    # Compute job description embedding once (cached for efficiency)
    job_embedding = get_embedding(job_description)
    
    all_results = []
    total_files = len(files)
    processing_state["total_files"] = total_files
    processing_state["processed_files"] = 0
    processing_state["current_status"] = "processing"
    
    # Save all files first (since UploadFile can only be read once)
    file_paths = []
    for file in files:
        file_path = os.path.join("uploads", file.filename)
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)
        file_paths.append((file_path, file.filename))
    
    # Process files in batches
    for i in range(0, total_files, batch_size):
        batch = file_paths[i:i + batch_size]
        batch_results = []
        
        # Process batch concurrently
        tasks = []
        for file_path, filename in batch:
            # Create processing task
            task = process_single_resume(
                file_path, filename, job_description, job_embedding, batch_results
            )
            tasks.append(task)
        
        # Wait for batch to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        
        all_results.extend(batch_results)
        processing_state["processed_files"] = len(all_results)
    
    # Clean up temporary files
    for file_path, _ in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
    
    processing_state["current_status"] = "completed"
    
    # Sort results by semantic score (descending)
    all_results.sort(key=lambda x: x["semantic_score"], reverse=True)
    
    # Add ranking
    for idx, result in enumerate(all_results, 1):
        result["ranking"] = idx
    
    return all_results

# Routes

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """About page"""
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    """Contact page"""
    return templates.TemplateResponse("contact.html", {"request": request})

@app.get("/analyzer", response_class=HTMLResponse)
async def analyzer(request: Request):
    """Analyzer page"""
    return templates.TemplateResponse("analyzer.html", {"request": request})

@app.post("/upload")
async def upload_resumes(
    request: Request,
    files: List[UploadFile] = File(...),
    job_description: str = Form(...)
):
    """
    Handle bulk resume upload and processing
    
    Args:
        files: List of uploaded resume files (PDF/DOCX)
        job_description: Job description text
        
    Returns:
        JSON response with processing results
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    if len(files) > 1000:
        raise HTTPException(status_code=400, detail="Maximum 1000 files allowed per upload")
    
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required")
    
    # Process resumes asynchronously
    results = await process_resumes_batch(files, job_description, batch_size=50)
    
    return JSONResponse({
        "status": "success",
        "total_files": len(files),
        "processed": len(results),
        "results": results
    })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """HR Dashboard displaying all screening results"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT filename, email, semantic_score, ml_fit, final_status, 
               email_status, missing_skills, created_at
        FROM screening_results
        ORDER BY semantic_score DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    shortlisted_count = 0
    rejected_count = 0
    total_score = 0.0
    
    for row in rows:
        final_status = row[4]
        if final_status == "Shortlisted":
            shortlisted_count += 1
        elif final_status == "Rejected":
            rejected_count += 1
        
        total_score += row[2]
        
        results.append({
            "filename": row[0],
            "email": row[1] or "N/A",
            "semantic_score": row[2],
            "ml_fit": "Fit" if row[3] == 1 else "Not Fit",
            "final_status": final_status,
            "email_status": row[5],
            "missing_skills": json.loads(row[6]) if row[6] else [],
            "created_at": row[7]
        })
    
    avg_score = total_score / len(results) if results else 0.0
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "results": results,
        "total_candidates": len(results),
        "shortlisted_count": shortlisted_count,
        "rejected_count": rejected_count,
        "avg_score": round(avg_score, 1)
    })

@app.get("/progress")
async def get_progress():
    """Get current processing progress"""
    return JSONResponse(processing_state)

@app.get("/download-excel")
async def download_excel():
    """Download all results as Excel file"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT filename, email, semantic_score, ml_fit, final_status, 
               email_status, missing_skills, created_at
        FROM screening_results
        ORDER BY semantic_score DESC
    """, conn)
    conn.close()
    
    # Process missing_skills column
    df['missing_skills'] = df['missing_skills'].apply(
        lambda x: ', '.join(json.loads(x)) if x else ''
    )
    df['ml_fit'] = df['ml_fit'].apply(lambda x: 'Fit' if x == 1 else 'Not Fit')
    
    # Save to Excel
    excel_path = "screening_results.xlsx"
    df.to_excel(excel_path, index=False, engine='openpyxl')
    
    return FileResponse(
        excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="screening_results.xlsx"
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
