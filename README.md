# ATS Resume Analyzer

An AI-powered resume analyzer that helps candidates check if their resumes are ATS-friendly.  
The system automatically scores resumes, shortlists qualified candidates, and sends email invitations for interviews.

---

## Features

- **Resume Upload**  
  Upload resumes in **PDF** or **DOCX** format with drag-and-drop support.

- **AI-Powered Scoring (0–100%)** based on:
  - Technical and soft skills (30 points)
  - Education qualifications (20 points)
  - Work experience (25 points)
  - Resume format and structure (15 points)
  - AI model prediction (10 points)

- **Automatic Shortlisting**  
  Candidates scoring **≥ 50%** are automatically shortlisted.

- **Email Notifications**  
  Shortlisted candidates receive automated interview invitations via **SMTP**.

- **Admin Dashboard**  
  View and manage shortlisted candidates and download resumes.

- **Improvement Suggestions**  
  Rejected candidates receive actionable feedback.

---

## Setup Instructions

### 1. Email Configuration (Required for Email Notifications)

To enable automated email invitations, configure **Gmail SMTP credentials**.

#### Get a Gmail App Password
1. Go to **Google Account Settings**
2. Enable **2-Step Verification**
3. Navigate to **Security → App passwords**
4. Generate a new password for **Mail**
5. Copy the **16-character app password**

#### Set Environment Secrets (Replit)
Add the following secrets:
- `EMAIL_USER` → your Gmail address  
- `EMAIL_PASSWORD` → 16-character app password

---

### 2. Running the Application

The application starts automatically.

Access:
- **Home Page** – Overview of features  
- **Analyze Resume** – Upload and analyze resumes  
- **Admin Dashboard** – View shortlisted candidates (HR access)

---

## How It Works

1. **Upload** – Candidate uploads resume (PDF or DOCX)
2. **Analysis** – AI extracts data and calculates ATS score
3. **Classification**
   - Score **≥ 50%** → Shortlisted + Email sent
   - Score **< 50%** → Rejected + Improvement suggestions
4. **Admin Access** – HR can view and download shortlisted resumes

---

## Scoring Breakdown

- **Keywords & Skills** – 30 pts  
- **Education** – 20 pts  
- **Experience** – 25 pts  
- **Format & Structure** – 15 pts  
- **AI Prediction** – 10 pts  

---

## Tech Stack

- **Backend**: Flask (Python)
- **AI / ML**: scikit-learn (Random Forest Classifier)
- **Resume Parsing**: PyMuPDF (PDF), python-docx (DOCX)
- **Email**: SMTP (Gmail)
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: JSON file storage

---
├── pycache/ # Python cache files
├── .venv/ # Virtual environment
├── docs/ # Documentation files
├── static/ # CSS, JS, assets
├── uploads/ # Uploaded resumes
│├── .gitignore
├── ai_scorer.py # ATS scoring logic
├── ats_resume_analyzer.db # SQLite database
├── database.py # Database operations
├── download_nltk.py # NLTK resource downloader
├── email_service.py # SMTP email handling
├── init_db.py # Database initialization
├── main.py # Core application logic
├── run.py # Application entry point
├── resume_parser.py # PDF/DOCX text extraction
├── test_dns.py # Testing script
├── README.md # Project overview
├── PROJECT_SUMMARY.md # Academic project summary
├── QUICK_REFERENCE.md # Quick usage guide
├── SETUP_GUIDE.md # Detailed setup instructions
├── requirements.txt # Python dependencies

---

## Usage Notes

- Maximum file size: **16MB**
- Supported formats: **PDF, DOCX**
- Email requires valid SMTP credentials
- Admin dashboard auto-refreshes every **30 seconds**

---

## Security

- Secrets stored as **environment variables**
- File uploads validated and sanitized
- SMTP uses **app-specific passwords**
- Resume files stored in secure directories

---

## Future Enhancements

- Train ML model on larger datasets
- Advanced NLP for experience extraction
- Bulk resume export (CSV / PDF)
- Analytics dashboard
- Keyword-based resume improvement suggestions
- Support for multiple job roles with custom scoring

## File Structure
├── pycache/ # Python cache files
├── .venv/ # Virtual environment
├── docs/ # Documentation files
├── static/ # CSS, JS, assets
├── uploads/ # Uploaded resumes
├── ai_scorer.py # ATS scoring logic
├── ats_resume_analyzer.db # SQLite database
├── database.py # Database operations
├── download_nltk.py # NLTK resource downloader
├── email_service.py # SMTP email handling
├── init_db.py # Database initialization
├── main.py # Core application logic
├── run.py # Application entry point
├── resume_parser.py # PDF/DOCX text extraction
├── test_dns.py # Testing script
├── PROJECT_SUMMARY.md # Academic project summary
├── QUICK_REFERENCE.md # Quick usage guide
├── SETUP_GUIDE.md # Detailed setup instructions
├── requirements.txt # Python dependencies

---

## Usage Notes

- Maximum file size: **16MB**
- Supported formats: **PDF, DOCX**
- Email requires valid SMTP credentials
- Admin dashboard auto-refreshes every **30 seconds**

---

## Security

- Secrets stored as **environment variables**
- File uploads validated and sanitized
- SMTP uses **app-specific passwords**
- Resume files stored in secure directories

---

## Future Enhancements

- Train ML model on larger datasets
- Advanced NLP for experience extraction
- Bulk resume export (CSV / PDF)
- Analytics dashboard
- Keyword-based resume improvement suggestions
- Support for multiple job roles with custom scoring

