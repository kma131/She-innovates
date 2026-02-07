import os
import PyPDF2
from io import BytesIO
from PyPDF2.errors import PdfReadError
import google.generativeai as genai
import time
import json
from flask import current_app
from flask_mail import Message
from app import mail
import re
import smtplib

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            data = file.read()

        def _extract_from_bytes(data_bytes):
            reader = PyPDF2.PdfReader(BytesIO(data_bytes), strict=False)
            parts = []
            for page in reader.pages:
                ptext = page.extract_text()
                if ptext:
                    parts.append(ptext)
            return '\n'.join(parts)

        # First attempt
        try:
            return _extract_from_bytes(data)
        except Exception as e:
            # If it's a common EOF issue, try to repair by appending EOF marker
            msg = str(e)
            if isinstance(e, PdfReadError) or 'EOF' in msg or 'EOF marker' in msg:
                repaired = data + b"\n%%EOF"
                try:
                    return _extract_from_bytes(repaired)
                except Exception:
                    pass
            raise Exception(f"Error extracting PDF text: {str(e)}")
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
        model = genai.GenerativeModel('gemini-2.0-flash-lite')

        # Local fallback anonymizer (used when API quota/rate limits are hit)
        def local_anonymize(text):
            atext = text
            # Emails
            atext = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "[REDACTED_EMAIL]", atext)
            # Phone numbers (simple heuristic)
            atext = re.sub(r"\+?\d[\d\-\s().]{7,}\d", "[REDACTED_PHONE]", atext)
            # Zip codes
            atext = re.sub(r"\b\d{5}(?:-\d{4})?\b", "[REDACTED_ZIP]", atext)
            # Street addresses (heuristic)
            atext = re.sub(r"\d+\s+[^\n,]{1,60}\b(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|Lane|Ln\.?|Drive|Dr\.?)\b", "[REDACTED_ADDRESS]", atext, flags=re.IGNORECASE)
            # Years (simple redact)
            atext = re.sub(r"\b(19|20)\d{2}\b", "[REDACTED_YEAR]", atext)
            # Heuristic: redact a leading name line (e.g., "First Last")
            lines = atext.splitlines()
            if lines:
                first = lines[0].strip()
                if re.match(r"^[A-Z][a-z]+(?: [A-Z][a-z]+)+$", first):
                    lines[0] = "[REDACTED_NAME]"
                    atext = "\n".join(lines)
            result = {
                "anonymized_resume": atext,
                "technical_skills": [],
                "soft_skills": [],
                "years_experience": "Unknown",
                "key_achievements": [],
                "job_titles": []
            }
            return result

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

        # Retry with exponential backoff on quota/rate errors
        max_retries = current_app.config.get('GENAI_MAX_RETRIES', 3)
        backoff = current_app.config.get('GENAI_INITIAL_BACKOFF', 2)
        last_err = None
        for attempt in range(max_retries):
            try:
                response = model.generate_content(prompt)
                response_text = response.text

                # Extract JSON payload from response text if present
                json_match = response_text.find('{')
                if json_match != -1:
                    json_str = response_text[json_match:]
                    json_end = json_str.rfind('}') + 1
                    json_str = json_str[:json_end]
                    result = json.loads(json_str)
                else:
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
                last_err = e
                msg = str(e).lower()
                # Detect quota/rate-limit related messages
                if 'quota' in msg or 'exceeded' in msg or '429' in msg or 'rate' in msg:
                    if attempt < max_retries - 1:
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                    else:
                        # Use local fallback anonymizer when out of quota
                        try:
                            return local_anonymize(resume_text)
                        except Exception:
                            raise Exception(f"Error anonymizing resume (API quota exceeded and local fallback failed): {str(last_err)}")
                else:
                    raise Exception(f"Error anonymizing resume: {str(e)}")
        # If loop exits unexpectedly, raise the last error
        raise Exception(f"Error anonymizing resume: {str(last_err)}")
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
    except smtplib.SMTPAuthenticationError as e:
        # Provide actionable guidance for common Gmail auth issues
        hint = (
            "SMTP authentication failed. If you are using Gmail, ensure that either:\n"
            "  - you have enabled 2-Step Verification and are using an App Password (recommended), or\n"
            "  - your account allows SMTP access and the credentials in MAIL_USERNAME/MAIL_PASSWORD are correct.\n"
            "See: https://support.google.com/mail/?p=BadCredentials and https://support.google.com/accounts/answer/185833"
        )
        raise Exception(f"Error sending email: Authentication failed: {str(e)}. {hint}")
    except smtplib.SMTPException as e:
        raise Exception(f"Error sending email: SMTP error: {str(e)}. Check MAIL_SERVER, MAIL_PORT, and TLS settings.")
    except Exception as e:
        raise Exception(f"Error sending email: {str(e)}")

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
