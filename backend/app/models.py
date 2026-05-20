from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student, client, admin
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    college = db.Column(db.String(200))
    year = db.Column(db.String(20))
    bio = db.Column(db.Text)
    portfolio_url = db.Column(db.String(300))
    avg_rating = db.Column(db.Float, default=0.0)
    total_projects = db.Column(db.Integer, default=0)
    is_approved = db.Column(db.Boolean, default=False)
    resume_filename = db.Column(db.String(500))
    resume_original_name = db.Column(db.String(300))
    
    user = db.relationship('User', backref='student_profile')
    skills = db.relationship('StudentSkill', backref='student', lazy=True, cascade='all, delete-orphan')

class ClientProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company = db.Column(db.String(200))
    description = db.Column(db.Text)
    verified = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='client_profile')

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    budget_min = db.Column(db.Float)
    budget_max = db.Column(db.Float)
    deadline = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='open')  # open, in_progress, completed, cancelled
    category = db.Column(db.String(50))
    required_skills = db.Column(db.Text)  # Comma-separated skills
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_bid_id = db.Column(db.Integer, db.ForeignKey('bid.id'), nullable=True)
    
    client = db.relationship('User', backref='projects')
    bids = db.relationship('Bid', backref='project', lazy=True, foreign_keys='Bid.project_id')

class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    proposal = db.Column(db.Text, nullable=False)
    delivery_days = db.Column(db.Integer)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    student = db.relationship('User', backref='bids')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])
    reviewee = db.relationship('User', foreign_keys=[reviewee_id])

class EscrowAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), unique=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='held')  # held, released, disputed, refunded
    payment_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    released_at = db.Column(db.DateTime)
    
    project = db.relationship('Project', backref='escrow')

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50))

class StudentSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profile.id'))
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'))
    proficiency = db.Column(db.Integer, default=1)  # 1-5
    
    skill = db.relationship('Skill', backref='student_skills')
