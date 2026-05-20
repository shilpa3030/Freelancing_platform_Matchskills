import os
from datetime import timedelta

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///freelance.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Razorpay settings
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID') or 'your_razorpay_key_id'
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET') or 'your_razorpay_secret'
    
    # SendGrid settings
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY') or 'your_sendgrid_api_key'
    
    # Upload settings (paths relative to backend/ directory when running run.py from backend/)
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    @staticmethod
    def resume_upload_dir():
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        return os.path.join(base, 'uploads', 'resumes')
