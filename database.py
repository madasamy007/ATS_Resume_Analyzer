"""
Database Models and Configuration
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ats_resume_analyzer.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class JobRole(Base):
    """Job Role Model"""
    __tablename__ = "job_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    required_skills = Column(JSON, nullable=True)  # List of skills
    required_experience = Column(Integer, default=0)  # Years
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="job_role")


class Resume(Base):
    """Resume Model"""
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    candidate_name = Column(String(200), nullable=True)
    candidate_email = Column(String(200), nullable=True, index=True)
    raw_text = Column(Text, nullable=True)
    parsed_data = Column(JSON, nullable=True)  # Structured data: skills, experience, education, projects
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="resume")


class Analysis(Base):
    """Resume Analysis Result Model"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_role_id = Column(Integer, ForeignKey("job_roles.id"), nullable=False)
    
    # Scores
    overall_score = Column(Float, nullable=False)  # 0-100
    semantic_score = Column(Float, nullable=False)  # 0-100
    skills_score = Column(Float, nullable=False)  # 0-100
    experience_score = Column(Float, nullable=False)  # 0-100
    education_score = Column(Float, nullable=False)  # 0-100
    projects_score = Column(Float, nullable=False)  # 0-100
    
    # Explanation
    explanation = Column(JSON, nullable=True)  # Detailed breakdown
    
    # Shortlisting
    is_shortlisted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume", back_populates="analyses")
    job_role = relationship("JobRole", back_populates="analyses")
    email_logs = relationship("EmailLog", back_populates="analysis")


class EmailLog(Base):
    """Email Log Model"""
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    recipient_email = Column(String(200), nullable=False)
    subject = Column(String(500), nullable=False)
    status = Column(String(50), default="pending")  # pending, sent, failed
    sent_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="email_logs")


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully!")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

