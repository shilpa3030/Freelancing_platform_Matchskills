import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from app import db
from app.models import StudentProfile, StudentSkill, Skill, Project, Bid, Review, User
from flask_jwt_extended import jwt_required, get_jwt_identity

ALLOWED_RESUME_EXT = {'pdf', 'doc', 'docx'}

bp = Blueprint('student', __name__, url_prefix='/api/student')

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user = get_jwt_identity()
        profile = StudentProfile.query.filter_by(user_id=current_user['id']).first()
        
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        skills = [{
            'id': ss.skill.id,
            'name': ss.skill.name,
            'proficiency': ss.proficiency
        } for ss in profile.skills]
        
        return jsonify({
            'name': profile.name,
            'college': profile.college,
            'year': profile.year,
            'bio': profile.bio,
            'portfolio_url': profile.portfolio_url,
            'avg_rating': profile.avg_rating,
            'total_projects': profile.total_projects,
            'is_approved': profile.is_approved,
            'has_resume': bool(profile.resume_filename),
            'resume_original_name': profile.resume_original_name,
            'skills': skills
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        profile = StudentProfile.query.filter_by(user_id=current_user['id']).first()
        
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        profile.name = data.get('name', profile.name)
        profile.college = data.get('college', profile.college)
        profile.year = data.get('year', profile.year)
        profile.bio = data.get('bio', profile.bio)
        profile.portfolio_url = data.get('portfolio_url', profile.portfolio_url)
        
        db.session.commit()
        
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/skills', methods=['POST'])
@jwt_required()
def add_skill():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        profile = StudentProfile.query.filter_by(user_id=current_user['id']).first()
        
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        # Check if skill exists
        skill = Skill.query.filter_by(name=data['skill_name']).first()
        if not skill:
            skill = Skill(name=data['skill_name'], category=data.get('category'))
            db.session.add(skill)
            db.session.commit()
        
        # Add skill to student
        student_skill = StudentSkill(
            student_id=profile.id,
            skill_id=skill.id,
            proficiency=data.get('proficiency', 3)
        )
        db.session.add(student_skill)
        db.session.commit()
        
        return jsonify({'message': 'Skill added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/projects/browse', methods=['GET'])
@jwt_required()
def browse_projects():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        projects = Project.query.filter_by(status='open').order_by(
            Project.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'projects': [{
                'id': p.id,
                'title': p.title,
                'description': p.description,
                'budget_min': p.budget_min,
                'budget_max': p.budget_max,
                'deadline': p.deadline.isoformat() if p.deadline else None,
                'required_skills': p.required_skills,
                'category': p.category,
                'created_at': p.created_at.isoformat()
            } for p in projects.items],
            'total': projects.total,
            'pages': projects.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/projects/<int:project_id>/bid', methods=['POST'])
@jwt_required()
def submit_bid(project_id):
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        if project.status != 'open':
            return jsonify({'error': 'Project is not accepting bids'}), 400
        
        # Check if already bid
        existing_bid = Bid.query.filter_by(
            project_id=project_id,
            student_id=current_user['id']
        ).first()
        
        if existing_bid:
            return jsonify({'error': 'You have already bid on this project'}), 400
        
        bid = Bid(
            project_id=project_id,
            student_id=current_user['id'],
            amount=data['amount'],
            proposal=data['proposal'],
            delivery_days=data.get('delivery_days')
        )
        
        db.session.add(bid)
        db.session.commit()
        
        return jsonify({'message': 'Bid submitted successfully', 'bid_id': bid.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/bids', methods=['GET'])
@jwt_required()
def get_my_bids():
    try:
        current_user = get_jwt_identity()
        
        bids = Bid.query.filter_by(student_id=current_user['id']).order_by(
            Bid.created_at.desc()
        ).all()
        
        return jsonify([{
            'id': b.id,
            'project_id': b.project_id,
            'project_title': b.project.title,
            'amount': b.amount,
            'proposal': b.proposal,
            'status': b.status,
            'created_at': b.created_at.isoformat()
        } for b in bids]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/reviews', methods=['GET'])
@jwt_required()
def get_my_reviews():
    try:
        current_user = get_jwt_identity()
        reviews = Review.query.filter_by(
            reviewee_id=current_user['id']
        ).order_by(Review.created_at.desc()).all()

        out = []
        for r in reviews:
            project = Project.query.get(r.project_id)
            reviewer = User.query.get(r.reviewer_id)
            out.append({
                'id': r.id,
                'project_id': r.project_id,
                'project_title': project.title if project else 'Project',
                'rating': r.rating,
                'comment': r.comment or '',
                'created_at': r.created_at.isoformat(),
                'reviewer_email': reviewer.email if reviewer else None
            })
        return jsonify(out), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/resume', methods=['POST'])
@jwt_required()
def upload_resume():
    try:
        current_user = get_jwt_identity()
        if current_user.get('role') != 'student':
            return jsonify({'error': 'Only freelancers may upload a resume'}), 403
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        file = request.files['file']
        if not file or not file.filename:
            return jsonify({'error': 'Empty file'}), 400
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        if ext not in ALLOWED_RESUME_EXT:
            return jsonify({'error': 'Allowed types: PDF, DOC, DOCX'}), 400

        profile = StudentProfile.query.filter_by(user_id=current_user['id']).first()
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404

        upload_dir = current_app.config['RESUME_UPLOAD_DIR']
        os.makedirs(upload_dir, exist_ok=True)

        old_name = profile.resume_filename
        stored = f"{current_user['id']}_{uuid.uuid4().hex}.{ext}"
        path = os.path.join(upload_dir, stored)
        file.save(path)

        if old_name:
            old_path = os.path.join(upload_dir, old_name)
            if old_path != path:
                try:
                    os.remove(old_path)
                except OSError:
                    pass

        profile.resume_filename = stored
        profile.resume_original_name = secure_filename(file.filename) or f'resume.{ext}'
        db.session.commit()

        return jsonify({
            'message': 'Resume uploaded',
            'has_resume': True,
            'resume_original_name': profile.resume_original_name
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/resume', methods=['DELETE'])
@jwt_required()
def delete_resume():
    try:
        current_user = get_jwt_identity()
        if current_user.get('role') != 'student':
            return jsonify({'error': 'Forbidden'}), 403
        profile = StudentProfile.query.filter_by(user_id=current_user['id']).first()
        if not profile or not profile.resume_filename:
            return jsonify({'error': 'No resume on file'}), 404
        upload_dir = current_app.config['RESUME_UPLOAD_DIR']
        try:
            os.remove(os.path.join(upload_dir, profile.resume_filename))
        except OSError:
            pass
        profile.resume_filename = None
        profile.resume_original_name = None
        db.session.commit()
        return jsonify({'message': 'Resume removed'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/resume/download', methods=['GET'])
@jwt_required()
def download_resume():
    try:
        current_user = get_jwt_identity()
        if current_user.get('role') != 'student':
            return jsonify({'error': 'Forbidden'}), 403
        profile = StudentProfile.query.filter_by(user_id=current_user['id']).first()
        if not profile or not profile.resume_filename:
            return jsonify({'error': 'No resume'}), 404
        upload_dir = current_app.config['RESUME_UPLOAD_DIR']
        return send_from_directory(
            upload_dir,
            profile.resume_filename,
            as_attachment=True,
            download_name=profile.resume_original_name or 'resume.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    try:
        current_user = get_jwt_identity()
        from app.ml_models.recommendation import ProjectRecommender
        
        recommender = ProjectRecommender()
        recommendations = recommender.recommend_projects(current_user['id'], top_n=10)
        
        return jsonify(recommendations), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
