import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models import Project, StudentProfile, StudentSkill, Skill
from app import db

class ProjectRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
    
    def get_student_skills_text(self, student_id):
        """Get student skills as text"""
        student = StudentProfile.query.filter_by(user_id=student_id).first()
        if not student:
            return ""
        
        skills = db.session.query(Skill.name).join(StudentSkill).filter(
            StudentSkill.student_id == student.id
        ).all()
        
        skills_text = ' '.join([s[0] for s in skills])
        
        # Add bio if available
        if student.bio:
            skills_text += ' ' + student.bio
        
        return skills_text
    
    def recommend_projects(self, student_id, top_n=10):
        """Recommend projects based on skill matching"""
        # Get student skills
        student_skills = self.get_student_skills_text(student_id)
        
        if not student_skills:
            return []
        
        # Get all open projects
        projects = Project.query.filter_by(status='open').all()
        
        if not projects:
            return []
        
        # Create corpus
        project_texts = []
        for p in projects:
            text = (p.required_skills or '') + ' ' + (p.description or '') + ' ' + (p.category or '')
            project_texts.append(text)
        
        corpus = [student_skills] + project_texts
        
        try:
            # Calculate TF-IDF and similarity
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
            
            # Get top recommendations
            top_indices = cosine_similarities.argsort()[-top_n:][::-1]
            
            recommendations = []
            for idx in top_indices:
                if idx < len(projects):
                    project = projects[idx]
                    recommendations.append({
                        'project_id': project.id,
                        'title': project.title,
                        'description': project.description[:200] + '...' if len(project.description) > 200 else project.description,
                        'budget_max': project.budget_max,
                        'similarity_score': float(cosine_similarities[idx]),
                        'deadline': project.deadline.isoformat() if project.deadline else None,
                        'category': project.category
                    })
            
            return recommendations
        except Exception as e:
            print(f"Error in recommendation: {str(e)}")
            return []

class StudentRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
    
    def recommend_students(self, project_id, top_n=10):
        """Recommend students for a project"""
        project = Project.query.get(project_id)
        
        if not project:
            return []
        
        # Get all approved students
        students = StudentProfile.query.filter_by(is_approved=True).all()
        
        if not students:
            return []
        
        # Create student skill texts
        student_texts = []
        for student in students:
            skills = db.session.query(Skill.name).join(StudentSkill).filter(
                StudentSkill.student_id == student.id
            ).all()
            skill_text = ' '.join([s[0] for s in skills])
            bio_text = student.bio or ''
            student_texts.append(skill_text + ' ' + bio_text)
        
        # Create corpus
        project_text = (project.required_skills or '') + ' ' + (project.description or '') + ' ' + (project.category or '')
        corpus = [project_text] + student_texts
        
        try:
            # Calculate similarity
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
            
            # Get top recommendations
            top_indices = cosine_similarities.argsort()[-top_n:][::-1]
            
            recommendations = []
            for idx in top_indices:
                if idx < len(students):
                    student = students[idx]
                    recommendations.append({
                        'student_id': student.user_id,
                        'name': student.name,
                        'college': student.college,
                        'avg_rating': student.avg_rating,
                        'total_projects': student.total_projects,
                        'match_score': float(cosine_similarities[idx])
                    })
            
            return recommendations
        except Exception as e:
            print(f"Error in recommendation: {str(e)}")
            return []
