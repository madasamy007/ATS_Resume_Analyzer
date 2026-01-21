"""
Resume Parser - Extracts information from PDF and DOCX files
"""
import re
import pdfplumber
from docx import Document
from typing import Dict, List, Optional
import os


class ResumeParser:
    """Parse resumes from PDF and DOCX files"""
    
    def __init__(self):
        self.skills_keywords = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'mongodb',
            'postgresql', 'aws', 'docker', 'kubernetes', 'git', 'machine learning',
            'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas',
            'numpy', 'flask', 'fastapi', 'django', 'html', 'css', 'typescript',
            'angular', 'vue', 'redis', 'elasticsearch', 'kafka', 'spark',
            'hadoop', 'tableau', 'power bi', 'azure', 'gcp', 'linux', 'bash'
        ]
    
    def parse(self, file_path: str) -> Dict:
        """
        Parse resume file and extract structured data
        
        Returns:
            {
                'raw_text': str,
                'candidate_name': str,
                'candidate_email': str,
                'skills': List[str],
                'experience_years': int,
                'experience_details': List[Dict],
                'education': List[Dict],
                'projects': List[Dict],
                'certifications': List[str]
            }
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            text = self._extract_from_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            text = self._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        # Extract structured information
        parsed_data = {
            'raw_text': text,
            'candidate_name': self._extract_name(text),
            'candidate_email': self._extract_email(text),
            'skills': self._extract_skills(text),
            'experience_years': self._extract_experience_years(text),
            'experience_details': self._extract_experience(text),
            'education': self._extract_education(text),
            'projects': self._extract_projects(text),
            'certifications': self._extract_certifications(text)
        }
        
        return parsed_data
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            print(f"Error extracting PDF: {e}")
        return text
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"Error extracting DOCX: {e}")
        return text
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract candidate name (usually first line or after 'Name:')"""
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if len(line) > 3 and len(line) < 50:
                # Simple heuristic: name-like pattern
                if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', line):
                    return line
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume"""
        text_lower = text.lower()
        found_skills = []
        
        # Check for skills section
        skills_section_pattern = r'(?:skills|technical skills|technologies|tools|expertise)[:;]?\s*(.+?)(?:\n\n|\n[A-Z]|$)'
        skills_match = re.search(skills_section_pattern, text_lower, re.IGNORECASE | re.DOTALL)
        
        if skills_match:
            skills_text = skills_match.group(1)
            # Extract skills from the section
            for skill in self.skills_keywords:
                if skill in skills_text:
                    found_skills.append(skill)
        
        # Also search entire text
        for skill in self.skills_keywords:
            if skill in text_lower and skill not in found_skills:
                found_skills.append(skill)
        
        return list(set(found_skills))  # Remove duplicates
    
    def _extract_experience_years(self, text: str) -> int:
        """Extract years of experience"""
        # Look for patterns like "5 years", "3+ years", etc.
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            r'(?:experience|exp)[:;]?\s*(\d+)\+?\s*(?:years?|yrs?)',
        ]
        
        years = 0
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                years = max(years, int(matches[0]))
        
        # If not found, estimate from experience entries
        if years == 0:
            exp_entries = self._extract_experience(text)
            if exp_entries:
                # Rough estimate: count distinct years mentioned
                years = len(exp_entries)
        
        return years
    
    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience details"""
        experience = []
        
        # Look for experience section
        exp_pattern = r'(?:experience|work experience|employment|professional experience)[:;]?\s*(.+?)(?:\n\n\n|\n[A-Z]{3,}|$)'
        exp_match = re.search(exp_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if exp_match:
            exp_text = exp_match.group(1)
            # Extract job entries (simplified)
            job_pattern = r'(.+?)\s*[-–]\s*(\d{4}|\w+\s+\d{4})\s*[-–]\s*(?:present|current|\d{4})'
            jobs = re.findall(job_pattern, exp_text, re.IGNORECASE)
            
            for job in jobs:
                experience.append({
                    'title': job[0].strip(),
                    'duration': job[1] if len(job) > 1 else None
                })
        
        return experience
    
    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education details"""
        education = []
        
        # Look for education section
        edu_pattern = r'(?:education|academic|qualification)[:;]?\s*(.+?)(?:\n\n\n|\n[A-Z]{3,}|$)'
        edu_match = re.search(edu_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if edu_match:
            edu_text = edu_match.group(1)
            # Extract degree entries
            degree_pattern = r'(bachelor|master|phd|b\.?tech|m\.?tech|b\.?e|m\.?e|diploma)[^\n]*'
            degrees = re.findall(degree_pattern, edu_text, re.IGNORECASE)
            
            for degree in degrees:
                education.append({
                    'degree': degree.strip(),
                    'details': edu_text[:200]  # Simplified
                })
        
        return education
    
    def _extract_projects(self, text: str) -> List[Dict]:
        """Extract project details"""
        projects = []
        
        # Look for projects section
        proj_pattern = r'(?:projects?|project experience)[:;]?\s*(.+?)(?:\n\n\n|\n[A-Z]{3,}|$)'
        proj_match = re.search(proj_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if proj_match:
            proj_text = proj_match.group(1)
            # Split by common project separators
            project_entries = re.split(r'\n(?=[A-Z]|\d+\.)', proj_text)
            
            for entry in project_entries[:5]:  # Limit to 5 projects
                if len(entry.strip()) > 20:
                    projects.append({
                        'title': entry.split('\n')[0].strip(),
                        'description': entry[:300]  # First 300 chars
                    })
        
        return projects
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        certifications = []
        
        # Look for certifications section
        cert_pattern = r'(?:certifications?|certificates?|credentials?)[:;]?\s*(.+?)(?:\n\n\n|\n[A-Z]{3,}|$)'
        cert_match = re.search(cert_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if cert_match:
            cert_text = cert_match.group(1)
            # Extract certification entries
            cert_entries = re.split(r'\n', cert_text)
            
            for entry in cert_entries:
                entry = entry.strip()
                if len(entry) > 5 and any(keyword in entry.lower() for keyword in ['certified', 'certification', 'aws', 'google', 'microsoft']):
                    certifications.append(entry)
        
        return certifications

