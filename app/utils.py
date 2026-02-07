import os
import PyPDF2
import google.generativeai as genai
from flask import current_app
from flask_mail import Message
from app import mail
import re

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    try:
        text = []
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text.append(page.extract_text())
        return '\n'.join(text)
    except Exception as e:
        raise Exception(f"Error extracting PDF text: {str(e)}")

def anonymize_resume(resume_text):
    """
    Use Gemini API to anonymize resume text.
    Strips identifying markers and highlights skills/experience.
    """
    try:
        # Configure Gemini API
        genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""You are a resume anonymization expert. Process the following resume to:

1. ANONYMIZE these elements (replace with [REDACTED]):
   - Names and personal identifiers
   - Email addresses and phone numbers
   - Specific addresses and zip codes (keep only state/country level)
   - Age-related information (graduation years converted to "X years ago", birth dates)
   - Gender-specific pronouns and names
   - Photos/profile pictures references
   - Any other identifying information

2. EXTRACT AND HIGHLIGHT:
   - Technical skills (programming languages, tools, frameworks)
   - Soft skills (leadership, communication, project management)
   - Years of experience in each area
   - Notable achievements with quantifiable impact

3. Return a JSON response with this structure:
   {{
     "anonymized_resume": "[full anonymized resume text]",
     "technical_skills": ["skill1", "skill2", ...],
     "soft_skills": ["skill1", "skill2", ...],
     "years_experience": "X years",
     "key_achievements": ["achievement1", "achievement2", ...],
     "job_titles": ["title1", "title2", ...]
   }}

Resume to process:
{resume_text}

Ensure the anonymized version is still professional and coherent."""

        response = model.generate_content(prompt)
        
        # Parse response
        import json
        response_text = response.text
        
        # Extract JSON from response
        json_match = response_text.find('{')
        if json_match != -1:
            json_str = response_text[json_match:]
            # Find the closing brace
            json_end = json_str.rfind('}') + 1
            json_str = json_str[:json_end]
            result = json.loads(json_str)
        else:
            # If no JSON found, structure the response
            result = {
                "anonymized_resume": response_text,
                "technical_skills": [],
                "soft_skills": [],
                "years_experience": "Unknown",
                "key_achievements": [],
                "job_titles": []
            }
        
        return result
    except Exception as e:
        raise Exception(f"Error anonymizing resume: {str(e)}")

def send_results_email(user_email, anonymized_text, skills, achievements):
    """Send anonymized resume results via email"""
    try:
        # Format the results for email
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #1a3a4a;">Your Anonymized Resume from Fair-Scan</h2>
                
                <p>Your resume has been successfully processed and anonymized. Here are your results:</p>
                
                <h3 style="color: #00b4d8; margin-top: 30px;">📋 Anonymized Resume</h3>
                <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #00b4d8; margin: 15px 0;">
                    <pre style="white-space: pre-wrap; word-wrap: break-word;">{anonymized_text}</pre>
                </div>
                
                <h3 style="color: #00b4d8; margin-top: 30px;">💼 Extracted Skills</h3>
                <ul>
                    {"".join([f"<li>{skill}</li>" for skill in skills.get('technical_skills', [])])}
                </ul>
                
                <h3 style="color: #00b4d8; margin-top: 30px;">⭐ Key Achievements</h3>
                <ul>
                    {"".join([f"<li>{achievement}</li>" for achievement in achievements])}
                </ul>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="color: #666; font-size: 12px;">
                    This email contains your anonymized resume data. 
                    Fair-Scan is committed to promoting fair and unbiased hiring practices.
                </p>
            </body>
        </html>
        """
        
        msg = Message(
            subject='Your Fair-Scan Anonymized Resume',
            recipients=[user_email],
            html=html_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        raise Exception(f"Error sending email: {str(e)}")

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
