from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login_manager

class User(UserMixin, db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship
    resumes = db.relationship('Resume', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Resume(db.Model):
    """Resume model for storing processing results"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Processing results
    original_text = db.Column(db.Text)
    anonymized_text = db.Column(db.Text)
    extracted_skills = db.Column(db.JSON)
    highlighted_experience = db.Column(db.JSON)
    processing_status = db.Column(db.String(20), default='completed')  # pending, completed, failed
    
    def __repr__(self):
        return f'<Resume {self.original_filename}>'

@login_manager.user_loader
def load_user(id):
    """Load user for session management"""
    return User.query.get(int(id))
