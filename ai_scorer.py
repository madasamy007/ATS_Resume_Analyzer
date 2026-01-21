"""
AI/ML Scoring System - Semantic Embeddings + Rule-Based Scoring
"""
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import Dict, List, Tuple, Any
import os
from dotenv import load_dotenv

load_dotenv()


def convert_numpy_types(obj: Any) -> Any:
    """
    Recursively convert numpy types to Python native types for JSON serialization
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj


class AIScorer:
    """
    AI-powered resume scorer using semantic embeddings
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize the AI scorer with embedding model
        
        Args:
            model_name: Sentence transformer model name
        """
        model_name = model_name or os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        print(f"🔄 Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("✅ Model loaded successfully!")
        
        # Scoring weights (can be customized per role)
        self.weights = {
            'semantic': 0.40,  # Most important - semantic similarity
            'skills': 0.30,
            'experience': 0.15,
            'education': 0.10,
            'projects': 0.05
        }
    
    def calculate_semantic_similarity(self, resume_text: str, job_description: str) -> float:
        """
        Calculate semantic similarity between resume and job description
        
        Args:
            resume_text: Full resume text
            job_description: Job role description
            
        Returns:
            Similarity score (0-1)
        """
        # Generate embeddings
        resume_embedding = self.model.encode(resume_text, convert_to_numpy=True)
        job_embedding = self.model.encode(job_description, convert_to_numpy=True)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(
            resume_embedding.reshape(1, -1),
            job_embedding.reshape(1, -1)
        )[0][0]
        
        # Convert numpy type to Python float and normalize to 0-1 range
        return float(max(0, min(1, similarity)))
    
    def calculate_skills_score(self, resume_skills: List[str], required_skills: List[str]) -> Tuple[float, Dict]:
        """
        Calculate skills matching score
        
        Args:
            resume_skills: Skills found in resume
            required_skills: Required skills for job
            
        Returns:
            (score 0-100, explanation dict)
        """
        if not required_skills:
            return 50.0, {"matched": [], "missing": [], "extra": resume_skills}
        
        # Normalize skills (lowercase, remove spaces)
        resume_skills_normalized = [s.lower().strip() for s in resume_skills]
        required_skills_normalized = [s.lower().strip() for s in required_skills]
        
        # Find matches
        matched = []
        missing = []
        
        for req_skill in required_skills_normalized:
            # Check exact match or substring match
            found = False
            for res_skill in resume_skills_normalized:
                if req_skill in res_skill or res_skill in req_skill:
                    matched.append(req_skill)
                    found = True
                    break
            if not found:
                missing.append(req_skill)
        
        # Calculate score
        match_ratio = len(matched) / len(required_skills_normalized) if required_skills_normalized else 0
        score = float(match_ratio * 100)
        
        # Extra skills (bonus, but capped)
        extra = [s for s in resume_skills_normalized if s not in matched]
        
        explanation = {
            "matched": matched,
            "missing": missing,
            "extra": extra[:5],  # Top 5 extra skills
            "match_ratio": f"{len(matched)}/{len(required_skills_normalized)}"
        }
        
        return score, explanation
    
    def calculate_experience_score(self, resume_years: int, required_years: int) -> Tuple[float, Dict]:
        """
        Calculate experience score
        
        Args:
            resume_years: Years of experience in resume
            required_years: Required years of experience
            
        Returns:
            (score 0-100, explanation dict)
        """
        if required_years == 0:
            return 100.0, {"message": "No experience requirement"}
        
        if resume_years >= required_years:
            score = 100.0
        else:
            # Linear scaling: 50% score for half the required years
            score = float(min(100, (resume_years / required_years) * 100))
        
        explanation = {
            "resume_years": resume_years,
            "required_years": required_years,
            "meets_requirement": resume_years >= required_years
        }
        
        return score, explanation
    
    def calculate_education_score(self, resume_education: List[Dict], job_role: str) -> Tuple[float, Dict]:
        """
        Calculate education score based on role requirements
        
        Args:
            resume_education: Education details from resume
            job_role: Job role title
            
        Returns:
            (score 0-100, explanation dict)
        """
        if not resume_education:
            return 30.0, {"message": "No education information found"}
        
        # Role-based education requirements (simplified)
        role_requirements = {
            'engineer': ['bachelor', 'b.tech', 'b.e', 'master', 'm.tech'],
            'scientist': ['master', 'm.tech', 'phd', 'ph.d'],
            'developer': ['bachelor', 'b.tech', 'diploma'],
            'data': ['bachelor', 'master', 'phd']
        }
        
        # Determine required education level
        required_levels = []
        job_lower = job_role.lower()
        for key, levels in role_requirements.items():
            if key in job_lower:
                required_levels = levels
                break
        
        if not required_levels:
            # Default: bachelor's degree
            required_levels = ['bachelor', 'b.tech', 'b.e']
        
        # Check if resume has required education
        found_levels = []
        for edu in resume_education:
            edu_text = edu.get('degree', '').lower() + ' ' + edu.get('details', '').lower()
            for level in required_levels:
                if level in edu_text:
                    found_levels.append(level)
        
        if found_levels:
            score = 100.0
        else:
            # Partial credit for any degree
            score = 60.0
        
        explanation = {
            "found_education": [edu.get('degree', 'N/A') for edu in resume_education],
            "required_levels": required_levels,
            "meets_requirement": len(found_levels) > 0
        }
        
        return score, explanation
    
    def calculate_projects_score(self, resume_projects: List[Dict], job_description: str) -> Tuple[float, Dict]:
        """
        Calculate projects relevance score using semantic similarity
        
        Args:
            resume_projects: Projects from resume
            job_description: Job role description
            
        Returns:
            (score 0-100, explanation dict)
        """
        if not resume_projects:
            return 0.0, {"message": "No projects found"}
        
        # Generate embeddings for job description
        job_embedding = self.model.encode(job_description, convert_to_numpy=True)
        
        # Calculate similarity for each project
        project_scores = []
        relevant_projects = []
        
        for project in resume_projects:
            project_text = project.get('title', '') + ' ' + project.get('description', '')
            if len(project_text.strip()) < 10:
                continue
            
            project_embedding = self.model.encode(project_text, convert_to_numpy=True)
            similarity = cosine_similarity(
                project_embedding.reshape(1, -1),
                job_embedding.reshape(1, -1)
            )[0][0]
            
            similarity_float = float(similarity)
            project_scores.append(similarity_float)
            if similarity_float > 0.3:  # Threshold for relevance
                relevant_projects.append({
                    'title': project.get('title', 'N/A'),
                    'relevance': float(round(similarity_float * 100, 2))
                })
        
        if not project_scores:
            return 0.0, {"message": "No valid projects found"}
        
        # Average similarity score
        avg_similarity = float(np.mean(project_scores))
        score = float(min(100, avg_similarity * 100))
        
        explanation = {
            "total_projects": len(resume_projects),
            "relevant_projects": len(relevant_projects),
            "top_projects": relevant_projects[:3]  # Top 3 most relevant
        }
        
        # Convert numpy types in explanation
        explanation = convert_numpy_types(explanation)
        
        return score, explanation
    
    def calculate_overall_score(
        self,
        resume_data: Dict,
        job_role: Dict,
        custom_weights: Dict = None
    ) -> Dict:
        """
        Calculate overall resume score with explainable breakdown
        
        Args:
            resume_data: Parsed resume data
            job_role: Job role data (title, description, required_skills, required_experience)
            custom_weights: Optional custom weights for scoring
            
        Returns:
            Complete scoring result with breakdown
        """
        weights = custom_weights or self.weights
        
        # 1. Semantic Similarity Score
        resume_text = resume_data.get('raw_text', '')
        job_description = job_role.get('description', '')
        semantic_similarity = self.calculate_semantic_similarity(resume_text, job_description)
        semantic_score = float(semantic_similarity * 100)
        
        # 2. Skills Score
        resume_skills = resume_data.get('skills', [])
        required_skills = job_role.get('required_skills', [])
        skills_score, skills_explanation = self.calculate_skills_score(resume_skills, required_skills)
        
        # 3. Experience Score
        resume_years = resume_data.get('experience_years', 0)
        required_years = job_role.get('required_experience', 0)
        experience_score, experience_explanation = self.calculate_experience_score(resume_years, required_years)
        
        # 4. Education Score
        resume_education = resume_data.get('education', [])
        job_title = job_role.get('title', '')
        education_score, education_explanation = self.calculate_education_score(resume_education, job_title)
        
        # 5. Projects Score
        resume_projects = resume_data.get('projects', [])
        projects_score, projects_explanation = self.calculate_projects_score(resume_projects, job_description)
        
        # Calculate weighted overall score
        overall_score = float(
            weights['semantic'] * semantic_score +
            weights['skills'] * skills_score +
            weights['experience'] * experience_score +
            weights['education'] * education_score +
            weights['projects'] * projects_score
        )
        
        # Round to 2 decimal places
        overall_score = round(overall_score, 2)
        
        # Determine if shortlisted (threshold: 70%) - ensure Python bool
        is_shortlisted = bool(overall_score >= 70.0)
        
        # Build explanation - ensure all values are Python native types
        explanation = {
            "overall_score": float(overall_score),
            "breakdown": {
                "semantic": {
                    "score": float(round(semantic_score, 2)),
                    "weight": float(weights['semantic']),
                    "contribution": float(round(weights['semantic'] * semantic_score, 2)),
                    "explanation": f"Semantic similarity: {round(semantic_similarity * 100, 2)}%"
                },
                "skills": {
                    "score": float(round(skills_score, 2)),
                    "weight": float(weights['skills']),
                    "contribution": float(round(weights['skills'] * skills_score, 2)),
                    "details": convert_numpy_types(skills_explanation)
                },
                "experience": {
                    "score": float(round(experience_score, 2)),
                    "weight": float(weights['experience']),
                    "contribution": float(round(weights['experience'] * experience_score, 2)),
                    "details": convert_numpy_types(experience_explanation)
                },
                "education": {
                    "score": float(round(education_score, 2)),
                    "weight": float(weights['education']),
                    "contribution": float(round(weights['education'] * education_score, 2)),
                    "details": convert_numpy_types(education_explanation)
                },
                "projects": {
                    "score": float(round(projects_score, 2)),
                    "weight": float(weights['projects']),
                    "contribution": float(round(weights['projects'] * projects_score, 2)),
                    "details": convert_numpy_types(projects_explanation)
                }
            },
            "recommendations": self._generate_recommendations(
                overall_score, skills_explanation, experience_explanation, education_explanation
            ),
            "is_shortlisted": bool(is_shortlisted)
        }
        
        # Recursively convert any remaining numpy types
        explanation = convert_numpy_types(explanation)
        
        return {
            "overall_score": float(overall_score),
            "semantic_score": float(round(semantic_score, 2)),
            "skills_score": float(round(skills_score, 2)),
            "experience_score": float(round(experience_score, 2)),
            "education_score": float(round(education_score, 2)),
            "projects_score": float(round(projects_score, 2)),
            "explanation": explanation,
            "is_shortlisted": bool(is_shortlisted)
        }
    
    def _generate_recommendations(
        self,
        overall_score: float,
        skills_explanation: Dict,
        experience_explanation: Dict,
        education_explanation: Dict
    ) -> List[str]:
        """Generate recommendations for improvement"""
        recommendations = []
        
        if overall_score < 70:
            if skills_explanation.get('missing'):
                recommendations.append(f"Missing key skills: {', '.join(skills_explanation['missing'][:3])}")
            
            if not experience_explanation.get('meets_requirement'):
                recommendations.append(f"Need more experience: {experience_explanation.get('required_years', 0)} years required")
            
            if not education_explanation.get('meets_requirement'):
                recommendations.append("Consider highlighting relevant education credentials")
        else:
            recommendations.append("Strong candidate! Well-matched for the role.")
        
        return recommendations

