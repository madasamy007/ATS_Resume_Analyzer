# ⚡ Quick Reference Guide

## 🚀 Quick Start (3 Steps)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize database
python init_db.py

# 3. Run server
python run.py
```

Open: `http://localhost:8000`

---

## 📁 Project Structure

```
├── main.py              # FastAPI backend
├── database.py          # Database models
├── resume_parser.py      # Resume parsing
├── ai_scorer.py         # AI/ML scoring
├── email_service.py      # Email automation
├── run.py               # Quick start script
├── requirements.txt     # Dependencies
├── static/              # Frontend files
└── docs/                # Documentation
```

---

## 🔑 Key Files

| File | Purpose |
|------|---------|
| `main.py` | Main FastAPI application |
| `ai_scorer.py` | AI/ML scoring logic |
| `resume_parser.py` | Extract data from PDF/DOCX |
| `database.py` | Database models |
| `email_service.py` | Send emails to candidates |

---

## 📊 Scoring Components

| Component | Weight | Description |
|-----------|--------|-------------|
| Semantic | 40% | AI embedding similarity |
| Skills | 30% | Skills match ratio |
| Experience | 15% | Years of experience |
| Education | 10% | Education level match |
| Projects | 5% | Project relevance |

**Shortlist Threshold**: ≥ 70%

---

## 🔌 API Quick Reference

### Create Job Role
```bash
POST /api/job-roles
Body: {
  "title": "Developer",
  "description": "...",
  "required_skills": ["Python"],
  "required_experience": 2
}
```

### Analyze Resume
```bash
POST /api/analyze
Form Data:
  - file: resume.pdf
  - job_role_id: 1
```

### Bulk Analyze
```bash
POST /api/analyze/bulk
Form Data:
  - files: [file1.pdf, file2.pdf]
  - job_role_id: 1
```

### Get Shortlisted
```bash
GET /api/shortlisted?job_role_id=1
```

### Send Emails
```bash
POST /api/shortlisted/send-emails?job_role_id=1
```

---

## 🛠️ Common Commands

```bash
# Run server
python run.py
# or
uvicorn main:app --reload

# Initialize database
python init_db.py

# Download NLTK data
python download_nltk.py

# Install dependencies
pip install -r requirements.txt
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port in use | Change port: `--port 8001` |
| Model not found | Check internet, model downloads automatically |
| Database error | Delete `.db` file, run `init_db.py` |
| Email fails | Check `.env` SMTP settings |
| Import error | Activate venv, reinstall requirements |

---

## 📝 Environment Variables

```env
# Required
DATABASE_URL=sqlite:///./ats_resume_analyzer.db

# Optional (for email)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
```

---

## 🎯 Workflow

1. **Create Job Role** → Define requirements
2. **Upload Resumes** → Single or bulk
3. **Analyze** → AI scores resumes
4. **Review Results** → See scores and explanations
5. **Shortlist** → Auto-shortlisted (≥70%)
6. **Send Emails** → Notify candidates

---

## 📚 Documentation Files

- `README.md` - Overview
- `SETUP_GUIDE.md` - Detailed setup
- `PROJECT_SUMMARY.md` - Project summary
- `docs/ARCHITECTURE.md` - System architecture
- `docs/API_DOCUMENTATION.md` - API details
- `docs/SCORING_FORMULA.md` - Scoring explanation
- `docs/ALGORITHM_FLOW.md` - Algorithm details
- `docs/EVALUATION_METRICS.md` - Metrics & evaluation

---

## 💡 Tips

1. **First Run**: Model downloads automatically (may take 1-2 min)
2. **Testing**: Use sample PDF resumes for testing
3. **Email**: Optional - system works without it
4. **Bulk Processing**: More efficient for multiple resumes
5. **Customization**: Adjust weights in `ai_scorer.py`

---

## 🎓 For Project Presentation

### Key Points to Highlight

1. **Semantic AI**: Not just keyword matching
2. **Explainable**: Clear score breakdown
3. **Scalable**: Handles bulk processing
4. **Modern Stack**: FastAPI, Sentence Transformers
5. **Production-Ready**: Error handling, logging

### Demo Flow

1. Show job role creation
2. Upload 2-3 resumes
3. Show scoring results
4. Explain score breakdown
5. Show shortlisting
6. Demonstrate email sending

---

## 📞 Support

- Check `docs/` folder for detailed docs
- Review `SETUP_GUIDE.md` for setup issues
- Check console logs for errors

---

**Happy Analyzing! 🚀**

