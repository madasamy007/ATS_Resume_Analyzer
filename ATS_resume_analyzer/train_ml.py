"""
ML Model Training Script for ATS Resume Screening System
Trains a Logistic Regression model to predict Fit (1) or Not Fit (0) based on resume embeddings
"""

import pickle
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sentence_transformers import SentenceTransformer
import os

def generate_synthetic_training_data():
    """
    Generate synthetic training data for demonstration purposes
    In production, this would use real resume-job description pairs with labels
    
    Returns:
        X: Array of embeddings (n_samples, embedding_dim)
        y: Array of labels (1 for Fit, 0 for Not Fit)
    """
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Example resume texts (Fit candidates)
    fit_resumes = [
        "Experienced software engineer with 5 years in Python, JavaScript, React, and Node.js. Strong background in full-stack development and cloud technologies like AWS and Docker.",
        "Data scientist specializing in machine learning and deep learning. Proficient in Python, TensorFlow, SQL, and data visualization. PhD in Computer Science.",
        "Senior backend developer with expertise in Java, Spring Boot, microservices, and REST APIs. Experience with SQL databases and CI/CD pipelines.",
        "Full-stack developer with React, Angular, TypeScript, and Node.js. Strong understanding of modern web development practices and Agile methodologies.",
        "DevOps engineer with Kubernetes, Docker, Git, and cloud infrastructure experience. Proficient in automation and infrastructure as code.",
        "Machine learning engineer with Python, scikit-learn, and deep learning frameworks. Experience in NLP and computer vision projects.",
        "Software engineer with Python, Java, and database management skills. Strong problem-solving abilities and team collaboration experience.",
        "Web developer proficient in JavaScript, HTML, CSS, React, and responsive design. Experience with version control and API integration.",
    ]
    
    # Example resume texts (Not Fit candidates)
    not_fit_resumes = [
        "Recent graduate with basic knowledge of HTML and CSS. Looking for entry-level position in marketing.",
        "Sales representative with 3 years of customer service experience. Strong communication skills.",
        "Graphic designer with Photoshop and Illustrator expertise. Portfolio includes logo design and branding projects.",
        "Accountant with CPA certification. Experience in financial reporting and tax preparation.",
        "Customer support specialist with excellent phone and email communication skills. Multilingual abilities.",
        "Human resources coordinator with recruiting and onboarding experience. Familiar with HRIS systems.",
        "Content writer with experience in blog writing and SEO. Published articles in various online publications.",
        "Retail manager with team leadership and inventory management skills. Experience in fast-paced retail environments.",
    ]
    
    # Example job description (software engineering role)
    job_description = "Looking for a software engineer with Python, JavaScript, React, and Node.js experience. Must have strong full-stack development skills and familiarity with cloud technologies. Machine learning knowledge is a plus."
    
    # Get job description embedding
    job_embedding = model.encode(job_description, normalize_embeddings=True)
    
    # Generate embeddings for fit resumes
    fit_embeddings = []
    for resume in fit_resumes:
        emb = model.encode(resume, normalize_embeddings=True)
        fit_embeddings.append(emb)
    
    # Generate embeddings for not fit resumes
    not_fit_embeddings = []
    for resume in not_fit_resumes:
        emb = model.encode(resume, normalize_embeddings=True)
        not_fit_embeddings.append(emb)
    
    # Combine all resume embeddings
    X = np.array(fit_embeddings + not_fit_embeddings)
    
    # Create labels (1 for Fit, 0 for Not Fit)
    y = np.array([1] * len(fit_resumes) + [0] * len(not_fit_resumes))
    
    return X, y

def train_model(X, y, test_size=0.2, random_state=42):
    """
    Train Logistic Regression model on resume embeddings
    
    Args:
        X: Array of embeddings
        y: Array of labels
        test_size: Proportion of data to use for testing
        random_state: Random seed for reproducibility
        
    Returns:
        Trained model
    """
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # Initialize and train Logistic Regression model
    model = LogisticRegression(random_state=random_state, max_iter=1000)
    model.fit(X_train, y_train)
    
    # Evaluate model
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"Model Training Complete!")
    print(f"Training Accuracy: {train_score:.2%}")
    print(f"Test Accuracy: {test_score:.2%}")
    
    return model

def save_model(model, filepath="ml_model.pkl"):
    """
    Save trained model to pickle file
    
    Args:
        model: Trained scikit-learn model
        filepath: Path to save the model
    """
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved to {filepath}")

def main():
    """Main training function"""
    print("Generating synthetic training data...")
    X, y = generate_synthetic_training_data()
    
    print(f"Training data shape: {X.shape}")
    print(f"Labels shape: {y.shape}")
    print(f"Fit samples: {np.sum(y == 1)}, Not Fit samples: {np.sum(y == 0)}")
    
    print("\nTraining Logistic Regression model...")
    model = train_model(X, y)
    
    print("\nSaving model...")
    save_model(model)
    
    print("\n" + "="*50)
    print("Model training completed successfully!")
    print("="*50)

if __name__ == "__main__":
    main()
