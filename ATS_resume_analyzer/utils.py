"""
Utility functions for ATS Resume Screening System
Handles text extraction, embeddings, email extraction, and similarity computation
"""

import re
import pdfplumber
from docx import Document
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Optional
import pickle
import os

# Load the SentenceTransformer model (cached after first load)
_model = None
_embedding_cache = {}  # Cache for job description embeddings

def get_model():
    """Load and cache the SentenceTransformer model"""
    global _model
    if _model is None:
        print("Loading SentenceTransformer model...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded successfully!")
    return _model

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF file using pdfplumber
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text as string
    """
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF {file_path}: {str(e)}")
        return ""

def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from DOCX file using python-docx
    
    Args:
        file_path: Path to the DOCX file
        
    Returns:
        Extracted text as string
    """
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from DOCX {file_path}: {str(e)}")
        return ""

def extract_text_from_resume(file_path: str) -> str:
    """
    Automatically detect file type and extract text from resume
    
    Args:
        file_path: Path to the resume file (PDF or DOCX)
        
    Returns:
        Extracted text as string
    """
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        return extract_text_from_docx(file_path)
    else:
        print(f"Unsupported file type: {file_path}")
        return ""

def extract_email_from_text(text: str) -> Optional[str]:
    """
    Extract email address from resume text using regex
    
    Args:
        text: Resume text content
        
    Returns:
        Email address if found, None otherwise
    """
    # Common email regex pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, text)
    
    if matches:
        # Return the first valid email found
        return matches[0]
    return None

def get_embedding(text: str, model=None) -> np.ndarray:
    """
    Convert text to semantic embedding vector
    
    Args:
        text: Input text to embed
        model: SentenceTransformer model (optional, will load if not provided)
        
    Returns:
        Embedding vector as numpy array
    """
    if model is None:
        model = get_model()
    
    # Encode text to embedding
    embedding = model.encode(text, normalize_embeddings=True, show_progress_bar=False)
    return embedding

def compute_semantic_score(resume_text: str, job_description: str, 
                          job_embedding_cache: Optional[np.ndarray] = None) -> float:
    """
    Compute semantic similarity score between resume and job description using cosine similarity
    
    Args:
        resume_text: Resume text content
        job_description: Job description text
        job_embedding_cache: Pre-computed job description embedding (optional for optimization)
        
    Returns:
        Semantic ATS score (0-100)
    """
    model = get_model()
    
    # Get or compute job description embedding
    if job_embedding_cache is not None:
        job_embedding = job_embedding_cache
    else:
        job_embedding = get_embedding(job_description, model)
    
    # Get resume embedding
    resume_embedding = get_embedding(resume_text, model)
    
    # Compute cosine similarity
    # Since embeddings are normalized, dot product equals cosine similarity
    similarity = np.dot(resume_embedding, job_embedding)
    
    # Convert to 0-100 scale
    score = (similarity + 1) * 50  # Maps [-1, 1] to [0, 100]
    
    return round(score, 2)

def load_ml_model(model_path: str = "ml_model.pkl"):
    """
    Load trained ML model from pickle file
    
    Args:
        model_path: Path to the pickle file containing the model
        
    Returns:
        Loaded scikit-learn model
    """
    if not os.path.exists(model_path):
        print(f"ML model not found at {model_path}. Please train the model first.")
        return None
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model

def predict_fit(embedding: np.ndarray, model) -> int:
    """
    Predict if candidate is Fit (1) or Not Fit (0) using ML model
    
    Args:
        embedding: Resume embedding vector
        model: Trained scikit-learn model
        
    Returns:
        1 for Fit, 0 for Not Fit
    """
    if model is None:
        # Default prediction if model not available
        return 1
    
    # Reshape for single prediction
    embedding_2d = embedding.reshape(1, -1)
    prediction = model.predict(embedding_2d)[0]
    return int(prediction)

def extract_skills_missing(resume_text: str, job_description: str, 
                          common_skills: List[str] = None) -> List[str]:
    """
    Extract list of missing skills by comparing resume and job description
    Simple keyword-based approach for demonstration
    
    Args:
        resume_text: Resume text content
        job_description: Job description text
        common_skills: List of common skills to check (optional)
        
    Returns:
        List of missing skills
    """
    if common_skills is None:
        # Extract potential skills from job description (simple approach)
        # Look for capitalized words or technical terms
        job_lower = job_description.lower()
        resume_lower = resume_text.lower()
        
        # Common technical skills/keywords
        tech_keywords = ['python', 'java', 'javascript', 'sql', 'react', 'angular', 
                        'node.js', 'aws', 'docker', 'kubernetes', 'git', 'machine learning',
                        'deep learning', 'data science', 'api', 'rest', 'graphql']
        
        missing = []
        for keyword in tech_keywords:
            if keyword in job_lower and keyword not in resume_lower:
                missing.append(keyword.title())
        
        return missing[:5]  # Return top 5 missing skills
    
    missing = []
    resume_lower = resume_text.lower()
    for skill in common_skills:
        if skill.lower() not in resume_lower:
            missing.append(skill)
    
    return missing
