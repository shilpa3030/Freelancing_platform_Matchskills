from flask import Blueprint, request, jsonify
from app import db
from app.models import Project, Bid, StudentProfile
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('project', __name__, url_prefix='/api/projects')

@bp.route('/', methods=['GET'])
def get_all_projects():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', 'open')
        category = request.args.get('category')
        
        query = Project.query
        
        if status:
            query = query.filter_by(status=status)
        
        if category:
            query = query.filter_by(category=category)
        
        projects = query.order_by(Project.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'projects': [{
                'id': p.id,
                'title': p.title,
                'description': p.description,
                'budget_min': p.budget_min,
                'budget_max': p.budget_max,
                'deadline': p.deadline.isoformat() if p.deadline else None,
                'status': p.status,
                'category': p.category,
                'required_skills': p.required_skills,
                'created_at': p.created_at.isoformat(),
                'bids_count': len(p.bids)
            } for p in projects.items],
            'total': projects.total,
            'pages': projects.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:project_id>', methods=['GET'])
def get_project_details(project_id):
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        return jsonify({
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'budget_min': project.budget_min,
            'budget_max': project.budget_max,
            'deadline': project.deadline.isoformat() if project.deadline else None,
            'status': project.status,
            'category': project.category,
            'required_skills': project.required_skills,
            'created_at': project.created_at.isoformat(),
            'bids_count': len(project.bids)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/search', methods=['GET'])
def search_projects():
    try:
        query = request.args.get('q', '')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        projects = Project.query.filter(
            db.or_(
                Project.title.contains(query),
                Project.description.contains(query),
                Project.required_skills.contains(query)
            )
        ).filter_by(status='open').paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'projects': [{
                'id': p.id,
                'title': p.title,
                'description': p.description,
                'budget_max': p.budget_max,
                'required_skills': p.required_skills,
                'created_at': p.created_at.isoformat()
            } for p in projects.items],
            'total': projects.total,
            'pages': projects.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/categories', methods=['GET'])
def get_categories():
    try:
        categories = db.session.query(Project.category).distinct().all()
        return jsonify([c[0] for c in categories if c[0]]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
