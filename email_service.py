"""
Email Service - Send automated emails to shortlisted candidates
"""
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


class EmailService:
    """Email service for sending notifications to candidates"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "ahashmicheals@gmail.com")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "igyo yzlp gorn llgv")
        self.email_from = os.getenv("EMAIL_FROM", self.smtp_username)
        
        # Debug: Print email config status (without showing password)
        if self.smtp_username and self.smtp_password:
            print(f"✅ Email service configured: {self.smtp_username} via {self.smtp_server}")
        else:
            print("⚠️ Email service not configured. Set SMTP_USERNAME and SMTP_PASSWORD in .env file")
    
    def send_email(
        self,
        recipient_email: str,
        subject: str,
        body_html: str,
        body_text: str = None
    ) -> Dict:
        """
        Send email to recipient
        
        Args:
            recipient_email: Recipient email address
            subject: Email subject
            body_html: HTML email body
            body_text: Plain text email body (optional)
            
        Returns:
            Dict with status and message
        """
        if not self.smtp_username or not self.smtp_password:
            error_msg = "Email configuration not set. Please configure SMTP_USERNAME and SMTP_PASSWORD in .env file."
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg
            }
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Add body
            if body_text:
                msg.attach(MIMEText(body_text, 'plain'))
            msg.attach(MIMEText(body_html, 'html'))
            
            # Send email
            print(f"📧 Attempting to send email to {recipient_email}...")
            print(f"🌐 Connecting to {self.smtp_server}:{self.smtp_port}...")
            
            # Test DNS resolution first
            try:
                socket.gethostbyname(self.smtp_server)
                print(f"✅ DNS resolution successful for {self.smtp_server}")
            except socket.gaierror as dns_error:
                error_msg = f"DNS resolution failed for {self.smtp_server}. Check your internet connection. Error: {str(dns_error)}"
                print(f"❌ {error_msg}")
                return {
                    "status": "failed",
                    "message": error_msg,
                    "error": str(dns_error)
                }
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                print(f"✅ Connected to SMTP server")
                server.starttls()
                print(f"🔐 Logging in to {self.smtp_server}...")
                server.login(self.smtp_username, self.smtp_password)
                print(f"✅ Login successful. Sending email...")
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {recipient_email}")
            return {
                "status": "sent",
                "message": f"Email sent successfully to {recipient_email}",
                "sent_at": datetime.utcnow().isoformat()
            }
        
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP Authentication failed. Check username and password. Error: {str(e)}"
            print(f"❌ Email Error: {error_msg}")
            return {
                "status": "failed",
                "message": error_msg,
                "error": str(e)
            }
        except smtplib.SMTPException as e:
            error_msg = f"SMTP Error: {str(e)}"
            print(f"❌ Email Error: {error_msg}")
            return {
                "status": "failed",
                "message": error_msg,
                "error": str(e)
            }
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            print(f"❌ Email Error: {error_msg}")
            return {
                "status": "failed",
                "message": error_msg,
                "error": str(e)
            }
    
    def generate_shortlist_email(
        self,
        candidate_name: str,
        job_title: str,
        score: float,
        company_name: str = "Our Company"
    ) -> tuple:
        """
        Generate email content for shortlisted candidate
        
        Returns:
            (subject, html_body, text_body)
        """
        subject = f"Congratulations! You've been shortlisted for {job_title}"
        
        # HTML body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 20px; border-radius: 0 0 5px 5px; }}
                .score {{ font-size: 24px; color: #4CAF50; font-weight: bold; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Congratulations!</h1>
                </div>
                <div class="content">
                    <p>Dear {candidate_name or 'Candidate'},</p>
                    
                    <p>We are pleased to inform you that your application for the position of <strong>{job_title}</strong> has been shortlisted!</p>
                    
                    <p>Your resume scored <span class="score">{score}%</span> based on our AI-powered analysis system, which evaluates:</p>
                    <ul>
                        <li>Semantic match with job requirements</li>
                        <li>Technical skills alignment</li>
                        <li>Relevant experience</li>
                        <li>Education and certifications</li>
                        <li>Project portfolio relevance</li>
                    </ul>
                    
                    <p>Our recruitment team will review your profile and contact you shortly with next steps.</p>
                    
                    <p>Thank you for your interest in joining {company_name}!</p>
                    
                    <p>Best regards,<br>
                    Recruitment Team<br>
                    {company_name}</p>
                </div>
                <div class="footer">
                    <p>This is an automated email. Please do not reply to this message.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text body
        text_body = f"""
        Congratulations!
        
        Dear {candidate_name or 'Candidate'},
        
        We are pleased to inform you that your application for the position of {job_title} has been shortlisted!
        
        Your resume scored {score}% based on our AI-powered analysis system.
        
        Our recruitment team will review your profile and contact you shortly with next steps.
        
        Thank you for your interest in joining {company_name}!
        
        Best regards,
        Recruitment Team
        {company_name}
        
        ---
        This is an automated email. Please do not reply to this message.
        """
        
        return subject, html_body, text_body
    
    def send_bulk_emails(
        self,
        candidates: List[Dict],
        job_title: str
    ) -> List[Dict]:
        """
        Send emails to multiple candidates in bulk
        
        Args:
            candidates: List of candidate dicts with email, name, score
            job_title: Job title for email
            
        Returns:
            List of email send results
        """
        results = []
        
        for candidate in candidates:
            email = candidate.get('email')
            name = candidate.get('name', 'Candidate')
            score = candidate.get('score', 0)
            
            if not email:
                results.append({
                    "email": email,
                    "status": "skipped",
                    "message": "No email address found"
                })
                continue
            
            # Generate email content
            subject, html_body, text_body = self.generate_shortlist_email(
                name, job_title, score
            )
            
            # Send email
            result = self.send_email(email, subject, html_body, text_body)
            result['email'] = email
            result['candidate_name'] = name
            
            results.append(result)
        
        return results

