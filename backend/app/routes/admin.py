from flask import Blueprint, request, jsonify
from app import db
from app.models import User, StudentProfile, ClientProfile, Project
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def admin_required():
    """Decorator to check if user is admin"""
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return False
    return True

@bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        users = User.query.all()
        
        result = []
        for u in users:
            user_data = {
                'id': u.id,
                'email': u.email,
                'role': u.role,
                'is_active': u.is_active,
                'created_at': u.created_at.isoformat()
            }
            
            if u.role == 'student':
                profile = StudentProfile.query.filter_by(user_id=u.id).first()
                if profile:
                    user_data['name'] = profile.name
                    user_data['college'] = profile.college
                    user_data['is_approved'] = profile.is_approved
            elif u.role == 'client':
                profile = ClientProfile.query.filter_by(user_id=u.id).first()
                if profile:
                    user_data['company'] = profile.company
                    user_data['verified'] = profile.verified
            
            result.append(user_data)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/students/approve/<int:user_id>', methods=['POST'])
@jwt_required()
def approve_student(user_id):
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        profile = StudentProfile.query.filter_by(user_id=user_id).first()
        
        if not profile:
            return jsonify({'error': 'Student not found'}), 404
        
        profile.is_approved = True
        db.session.commit()
        
        return jsonify({'message': 'Student approved successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/users/<int:user_id>/deactivate', methods=['POST'])
@jwt_required()
def deactivate_user(user_id):
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'User deactivated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/users/<int:user_id>/activate', methods=['POST'])
@jwt_required()
def activate_user(user_id):
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.is_active = True
        db.session.commit()
        
        return jsonify({'message': 'User activated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        from app.ml_models.analytics import Analytics
        
        stats = Analytics.get_platform_stats()
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/projects', methods=['GET'])
@jwt_required()
def get_all_projects():
    try:
        if not admin_required():
            return jsonify({'error': 'Admin access required'}), 403
        
        projects = Project.query.order_by(Project.created_at.desc()).all()
        
        return jsonify([{
            'id': p.id,
            'title': p.title,
            'client_id': p.client_id,
            'status': p.status,
            'budget_max': p.budget_max,
            'created_at': p.created_at.isoformat()
        } for p in projects]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
