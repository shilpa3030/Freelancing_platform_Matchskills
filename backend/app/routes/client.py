from flask import Blueprint, request, jsonify
from app import db
from app.models import ClientProfile, Project, Bid, Review, StudentProfile
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

bp = Blueprint('client', __name__, url_prefix='/api/client')

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user = get_jwt_identity()
        profile = ClientProfile.query.filter_by(user_id=current_user['id']).first()
        
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        return jsonify({
            'company': profile.company,
            'description': profile.description,
            'verified': profile.verified
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        profile = ClientProfile.query.filter_by(user_id=current_user['id']).first()
        
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        profile.company = data.get('company', profile.company)
        profile.description = data.get('description', profile.description)
        
        db.session.commit()
        
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        project = Project(
            client_id=current_user['id'],
            title=data['title'],
            description=data['description'],
            budget_min=data.get('budget_min'),
            budget_max=data.get('budget_max'),
            deadline=datetime.fromisoformat(data['deadline']) if data.get('deadline') else None,
            category=data.get('category'),
            required_skills=data.get('required_skills', '')
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({'message': 'Project created successfully', 'project_id': project.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/projects', methods=['GET'])
@jwt_required()
def get_my_projects():
    try:
        current_user = get_jwt_identity()
        
        projects = Project.query.filter_by(client_id=current_user['id']).order_by(
            Project.created_at.desc()
        ).all()
        
        return jsonify([{
            'id': p.id,
            'title': p.title,
            'description': p.description,
            'budget_min': p.budget_min,
            'budget_max': p.budget_max,
            'status': p.status,
            'category': p.category,
            'created_at': p.created_at.isoformat(),
            'bids_count': len(p.bids)
        } for p in projects]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/projects/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    try:
        current_user = get_jwt_identity()
        
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        if project.client_id != current_user['id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
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
            'created_at': project.created_at.isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/projects/<int:project_id>/bids', methods=['GET'])
@jwt_required()
def get_project_bids(project_id):
    try:
        current_user = get_jwt_identity()
        
        project = Project.query.get(project_id)
        
        if not project or project.client_id != current_user['id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        bids = Bid.query.filter_by(project_id=project_id).all()
        
        result = []
        for b in bids:
            student_profile = StudentProfile.query.filter_by(user_id=b.student_id).first()
            result.append({
                'id': b.id,
                'student_id': b.student_id,
                'student_name': student_profile.name if student_profile else 'Unknown',
                'student_rating': student_profile.avg_rating if student_profile else 0,
                'amount': b.amount,
                'proposal': b.proposal,
                'delivery_days': b.delivery_days,
                'status': b.status,
                'created_at': b.created_at.isoformat()
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/bids/<int:bid_id>/accept', methods=['POST'])
@jwt_required()
def accept_bid(bid_id):
    try:
        current_user = get_jwt_identity()
        
        bid = Bid.query.get(bid_id)
        
        if not bid:
            return jsonify({'error': 'Bid not found'}), 404
        
        project = Project.query.get(bid.project_id)
        
        if project.client_id != current_user['id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Reject all other bids
        Bid.query.filter_by(project_id=project.id).update({'status': 'rejected'})
        
        # Accept this bid
        bid.status = 'accepted'
        project.status = 'in_progress'
        project.accepted_bid_id = bid.id
        
        db.session.commit()
        
        return jsonify({'message': 'Bid accepted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/bids/<int:bid_id>/reject', methods=['POST'])
@jwt_required()
def reject_bid(bid_id):
    try:
        current_user = get_jwt_identity()
        
        bid = Bid.query.get(bid_id)
        
        if not bid:
            return jsonify({'error': 'Bid not found'}), 404
        
        project = Project.query.get(bid.project_id)
        
        if project.client_id != current_user['id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        bid.status = 'rejected'
        db.session.commit()
        
        return jsonify({'message': 'Bid rejected'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/projects/<int:project_id>/complete', methods=['POST'])
@jwt_required()
def complete_project(project_id):
    try:
        current_user = get_jwt_identity()
        
        project = Project.query.get(project_id)
        
        if not project or project.client_id != current_user['id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        project.status = 'completed'
        db.session.commit()
        
        return jsonify({'message': 'Project marked as completed'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/reviews', methods=['POST'])
@jwt_required()
def submit_review():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        project = Project.query.get(data['project_id'])
        
        if not project or project.client_id != current_user['id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        review = Review(
            project_id=data['project_id'],
            reviewer_id=current_user['id'],
            reviewee_id=data['student_id'],
            rating=data['rating'],
            comment=data.get('comment', '')
        )
        
        db.session.add(review)
        
        # Update student rating
        student_profile = StudentProfile.query.filter_by(user_id=data['student_id']).first()
        if student_profile:
            all_reviews = Review.query.filter_by(reviewee_id=data['student_id']).all()
            avg_rating = sum([r.rating for r in all_reviews]) / len(all_reviews) if all_reviews else 0
            student_profile.avg_rating = avg_rating
            student_profile.total_projects += 1
        
        db.session.commit()
        
        return jsonify({'message': 'Review submitted successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/students/recommended/<int:project_id>', methods=['GET'])
@jwt_required()
def get_recommended_students(project_id):
    try:
        current_user = get_jwt_identity()
        
        project = Project.query.get(project_id)
        if not project or project.client_id != current_user['id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        from app.ml_models.recommendation import StudentRecommender
        
        recommender = StudentRecommender()
        recommendations = recommender.recommend_students(project_id, top_n=10)
        
        return jsonify(recommendations), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
