from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Resume
from app.utils import extract_text_from_pdf, anonymize_resume, send_results_email, allowed_file
import os
from datetime import datetime

# Create blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
main_bp = Blueprint('main', __name__)

# ==================== AUTH ROUTES ====================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
        
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_has_allowed_host_and_scheme(next_page):
            next_page = url_for('main.dashboard')
        return redirect(next_page)
    
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page and handler"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not email or not password or not confirm_password:
            flash('All fields are required', 'error')
            return redirect(url_for('auth.signup'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.signup'))
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return redirect(url_for('auth.signup'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('auth.signup'))
        
        # Create new user
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('signup.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout handler"""
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))

def url_has_allowed_host_and_scheme(url, allowed_hosts=None):
    """Security check for redirect URLs"""
    return url.startswith('/')

# ==================== MAIN ROUTES ====================

@main_bp.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()
    return render_template('dashboard.html', resumes=resumes)

@main_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Resume upload and processing"""
    if request.method == 'POST':
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        try:
            # Secure filename and save
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Extract text from PDF
            resume_text = extract_text_from_pdf(filepath)
            
            # Anonymize using Gemini
            result = anonymize_resume(resume_text)
            
            # Save to database
            resume = Resume(
                user_id=current_user.id,
                original_filename=file.filename,
                original_text=resume_text,
                anonymized_text=result.get('anonymized_resume', ''),
                extracted_skills={
                    'technical': result.get('technical_skills', []),
                    'soft': result.get('soft_skills', [])
                },
                highlighted_experience={
                    'years_experience': result.get('years_experience', ''),
                    'job_titles': result.get('job_titles', []),
                    'key_achievements': result.get('key_achievements', [])
                },
                processing_status='completed'
            )
            db.session.add(resume)
            db.session.commit()
            
            # Send email with results
            send_results_email(
                current_user.email,
                result.get('anonymized_resume', ''),
                resume.extracted_skills,
                result.get('key_achievements', [])
            )
            
            return jsonify({
                'success': True,
                'message': 'Resume processed successfully! Check your email for results.',
                'resume_id': resume.id
            })
        
        except Exception as e:
            return jsonify({'error': f'Processing error: {str(e)}'}), 500
    
    return render_template('upload.html')

@main_bp.route('/resume/<int:resume_id>')
@login_required
def view_resume(resume_id):
    """View processed resume details"""
    resume = Resume.query.get_or_404(resume_id)
    
    # Check authorization
    if resume.user_id != current_user.id:
        flash('Unauthorized', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('view_resume.html', resume=resume)

@main_bp.route('/api/resume/<int:resume_id>')
@login_required
def get_resume_data(resume_id):
    """API endpoint to get resume data"""
    resume = Resume.query.get_or_404(resume_id)
    
    # Check authorization
    if resume.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': resume.id,
        'filename': resume.original_filename,
        'uploaded_at': resume.uploaded_at.isoformat(),
        'anonymized_text': resume.anonymized_text,
        'skills': resume.extracted_skills,
        'experience': resume.highlighted_experience
    })

@main_bp.route('/delete/<int:resume_id>', methods=['POST'])
@login_required
def delete_resume(resume_id):
    """Delete a resume"""
    resume = Resume.query.get_or_404(resume_id)
    
    if resume.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        db.session.delete(resume)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Resume deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
