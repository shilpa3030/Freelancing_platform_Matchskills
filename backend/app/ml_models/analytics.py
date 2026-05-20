import pandas as pd
from sqlalchemy import func
from app.models import Project, Bid, Review, StudentProfile, User
from app import db
from datetime import datetime, timedelta

class Analytics:
    
    @staticmethod
    def get_platform_stats():
        """Get overall platform statistics"""
        total_projects = Project.query.count()
        active_projects = Project.query.filter_by(status='in_progress').count()
        completed_projects = Project.query.filter_by(status='completed').count()
        total_students = StudentProfile.query.count()
        total_users = User.query.count()
        
        avg_project_value = db.session.query(func.avg(Project.budget_max)).scalar() or 0
        
        return {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'completed_projects': completed_projects,
            'total_students': total_students,
            'total_users': total_users,
            'avg_project_value': float(avg_project_value)
        }
    
    @staticmethod
    def get_student_analytics(student_id):
        """Get analytics for a specific student"""
        student = StudentProfile.query.filter_by(user_id=student_id).first()
        
        if not student:
            return None
        
        total_bids = Bid.query.filter_by(student_id=student_id).count()
        accepted_bids = Bid.query.filter_by(student_id=student_id, status='accepted').count()
        
        win_rate = (accepted_bids / total_bids * 100) if total_bids > 0 else 0
        
        # Get earnings from completed projects
        earnings_query = db.session.query(func.sum(Bid.amount)).join(Project).filter(
            Bid.student_id == student_id,
            Bid.status == 'accepted',
            Project.status == 'completed'
        ).scalar()
        
        earnings = float(earnings_query) if earnings_query else 0
        
        # Get reviews
        reviews = Review.query.filter_by(reviewee_id=student_id).all()
        avg_rating = sum([r.rating for r in reviews]) / len(reviews) if reviews else 0
        
        return {
            'total_bids': total_bids,
            'accepted_bids': accepted_bids,
            'win_rate': round(win_rate, 2),
            'total_earnings': earnings,
            'avg_rating': round(avg_rating, 2),
            'total_projects': student.total_projects,
            'total_reviews': len(reviews)
        }
    
    @staticmethod
    def get_client_analytics(client_id):
        """Get analytics for a specific client"""
        total_projects = Project.query.filter_by(client_id=client_id).count()
        active_projects = Project.query.filter_by(client_id=client_id, status='in_progress').count()
        completed_projects = Project.query.filter_by(client_id=client_id, status='completed').count()
        
        # Get total spent
        spent_query = db.session.query(func.sum(Bid.amount)).join(Project).filter(
            Project.client_id == client_id,
            Bid.status == 'accepted',
            Project.status == 'completed'
        ).scalar()
        
        total_spent = float(spent_query) if spent_query else 0
        
        return {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'completed_projects': completed_projects,
            'total_spent': total_spent
        }
    
    @staticmethod
    def get_trending_skills():
        """Get trending skills based on project demand"""
        # Get projects from last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        projects = Project.query.filter(
            Project.created_at >= thirty_days_ago,
            Project.status == 'open'
        ).all()
        
        skill_count = {}
        for project in projects:
            if project.required_skills:
                skills = [s.strip() for s in project.required_skills.split(',')]
                for skill in skills:
                    if skill:
                        skill_count[skill] = skill_count.get(skill, 0) + 1
        
        trending = sorted(skill_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return [{'skill': s[0], 'count': s[1]} for s in trending]
    
    @staticmethod
    def get_category_distribution():
        """Get distribution of projects by category"""
        categories = db.session.query(
            Project.category,
            func.count(Project.id)
        ).group_by(Project.category).all()
        
        return [{'category': c[0] or 'Uncategorized', 'count': c[1]} for c in categories]
    
    @staticmethod
    def get_monthly_stats():
        """Get monthly statistics for the last 6 months"""
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        
        projects = Project.query.filter(Project.created_at >= six_months_ago).all()
        
        monthly_data = {}
        for project in projects:
            month_key = project.created_at.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {'projects': 0, 'value': 0}
            
            monthly_data[month_key]['projects'] += 1
            if project.budget_max:
                monthly_data[month_key]['value'] += project.budget_max
        
        return [
            {
                'month': k,
                'projects': v['projects'],
                'total_value': v['value']
            }
            for k, v in sorted(monthly_data.items())
        ]
