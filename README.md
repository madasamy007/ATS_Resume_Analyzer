# ATS Resume Analyzer

An AI-powered resume analyzer that helps candidates check if their resumes are ATS-friendly.  
The system automatically scores resumes, shortlists qualified candidates, and sends email invitations for interviews.

## Features

### Resume Upload
Upload resumes in PDF or DOCX format with drag-and-drop support.

### AI-Powered Scoring
Get comprehensive ATS scores (0–100%) based on:
- Technical and soft skills (30 points)
- Education qualifications (20 points)
- Work experience (25 points)
- Resume format and structure (15 points)
- AI model prediction (10 points)

### Automatic Shortlisting
Candidates scoring ≥ 50% are automatically shortlisted.

### Email Notifications
Shortlisted candidates receive automated interview invitations via SMTP.

### Admin Dashboard
View and manage shortlisted candidates and download resumes.

### Improvement Suggestions
Rejected candidates receive actionable feedback.

## Setup Instructions

### Email Configuration (Required)
Configure Gmail SMTP credentials for email notifications.

### Running the Application
The application starts automatically. Use the web preview to access the system.

## How It Works

### Upload
Candidate uploads a resume (PDF or DOCX).

### Analysis
AI model extracts resume data and calculates the ATS score.

### Classification
- Score ≥ 50% → Shortlisted + Email sent
- Score < 50% → Rejected + Suggestions provided

### Admin Access
HR can view shortlisted candidates and download resumes.

## Scoring Breakdown

### Keywords and Skills (30 pts)
Technical skills, soft skills, industry keywords.

### Education (20 pts)
Degrees, certifications, academic background.

### Experience (25 pts)
Work history, years of experience, achievements.

### Format (15 pts)
Resume structure, sections, organization.

### AI Prediction (10 pts)
Machine learning model assessment.

## Technical Stack

### Backend
Flask (Python)

### AI / ML
scikit-learn (Random Forest Classifier)

### Resume Parsing
PyMuPDF (PDF), python-docx (DOCX)

### Email
SMTP (Gmail)

### Frontend
HTML5, CSS3, JavaScript

### Database
JSON file storage

## File Structure

