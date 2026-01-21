# 🚀 Setup Guide - ATS Resume Analyzer

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning)

---

## Step 1: Clone/Download Project

If using Git:
```bash
git clone <repository-url>
cd ats-resume-analyzer
```

Or download and extract the project files.

---

## Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: This may take a few minutes as it downloads the sentence transformer model.

---

## Step 4: Install NLP Models

### Spacy Model
```bash
python -m spacy download en_core_web_sm
```

### NLTK Data
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

Or create a script `download_nltk.py`:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

Run: `python download_nltk.py`

---

## Step 5: Configure Environment

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your settings:

   **Required for Email (Optional - can skip for testing):**
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   EMAIL_FROM=your_email@gmail.com
   ```

   **Gmail App Password Setup:**
   1. Go to Google Account settings
   2. Enable 2-Factor Authentication
   3. Generate App Password
   4. Use that password in `.env`

   **For Testing (No Email):**
   - Leave email fields empty
   - System will show warning but still work

---

## Step 6: Initialize Database

```bash
python init_db.py
```

This creates the SQLite database with all required tables.

---

## Step 7: Run the Application

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or use the Python script:
```bash
python main.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
🔄 Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
✅ Model loaded successfully!
✅ Database initialized successfully!
INFO:     Application startup complete.
```

---

## Step 8: Access the Application

Open your browser and navigate to:
```
http://localhost:8000
```

You should see the ATS Resume Analyzer interface.

---

## Step 9: Test the System

### 9.1 Create a Job Role

1. Fill in job role details:
   - Title: "Full Stack Developer"
   - Description: "We are looking for a full stack developer..."
   - Required Skills: "Python, React, SQL, AWS"
   - Required Experience: 3

2. Click "Create Job Role"

### 9.2 Upload Test Resume

1. Click on upload area or drag & drop a PDF/DOCX resume
2. Click "Analyze Resumes"
3. Wait for processing (2-5 seconds)
4. View results with scores and explanations

---

## Troubleshooting

### Issue: Model Download Fails

**Solution**: The model downloads automatically on first use. If it fails:
1. Check internet connection
2. Try manually: `python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"`

### Issue: Port Already in Use

**Solution**: Use a different port:
```bash
uvicorn main:app --reload --port 8001
```

### Issue: Database Errors

**Solution**: Delete `ats_resume_analyzer.db` and run `python init_db.py` again.

### Issue: Email Not Sending

**Solution**: 
1. Check `.env` configuration
2. Verify Gmail App Password is correct
3. Check firewall/antivirus blocking SMTP
4. System works without email - it's optional

### Issue: Import Errors

**Solution**: 
1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

### Issue: PDF Parsing Fails

**Solution**:
1. Ensure PDF is not password-protected
2. Try a different PDF file
3. Check if file is corrupted

---

## Development Mode

For development with auto-reload:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Changes to Python files will automatically restart the server.

---

## Production Deployment

### Using Gunicorn (Linux/Mac)

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python -m spacy download en_core_web_sm
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t ats-analyzer .
docker run -p 8000:8000 ats-analyzer
```

---

## API Testing

### Using curl

```bash
# Health check
curl http://localhost:8000/api/health

# Get job roles
curl http://localhost:8000/api/job-roles

# Create job role
curl -X POST http://localhost:8000/api/job-roles \
  -H "Content-Type: application/json" \
  -d '{"title": "Developer", "description": "Job desc", "required_skills": ["Python"], "required_experience": 2}'
```

### Using Python requests

```python
import requests

# Analyze resume
files = {'file': open('resume.pdf', 'rb')}
data = {'job_role_id': 1}
response = requests.post('http://localhost:8000/api/analyze', files=files, data=data)
print(response.json())
```

---

## Next Steps

1. **Add Sample Resumes**: Create test resumes for different roles
2. **Customize Weights**: Adjust scoring weights in `ai_scorer.py`
3. **Add More Job Roles**: Create roles for different positions
4. **Configure Email**: Set up SMTP for email notifications
5. **Review Documentation**: Read `docs/` folder for detailed information

---

## Support

For issues or questions:
1. Check `docs/` folder for detailed documentation
2. Review error messages in console
3. Check database for stored data
4. Verify all dependencies are installed

---

## Quick Start Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Spacy model downloaded
- [ ] NLTK data downloaded
- [ ] `.env` file configured (optional for email)
- [ ] Database initialized (`python init_db.py`)
- [ ] Server running (`uvicorn main:app --reload`)
- [ ] Application accessible at `http://localhost:8000`
- [ ] Test job role created
- [ ] Test resume analyzed successfully

---

**🎉 You're all set! Start analyzing resumes!**

