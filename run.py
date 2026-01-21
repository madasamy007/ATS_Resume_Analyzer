"""
Quick start script for ATS Resume Analyzer
"""
import uvicorn
import os
from pathlib import Path

if __name__ == "__main__":
    # Create necessary directories
    Path("uploads/resumes").mkdir(parents=True, exist_ok=True)
    Path("static").mkdir(exist_ok=True)
    
    # Initialize database if needed
    if not Path("ats_resume_analyzer.db").exists():
        print("📦 Initializing database...")
        from init_db import init_db
        init_db()
    
    # Run server
    print("🚀 Starting ATS Resume Analyzer...")
    print("📱 Open http://localhost:8000 in your browser")
    print("🛑 Press CTRL+C to stop\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

