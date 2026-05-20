from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import EscrowAccount, Project, Bid
from datetime import datetime

bp = Blueprint('payment', __name__, url_prefix='/api/payment')

# Note: In production, you would integrate actual payment gateway like Razorpay
# This is a simplified version for demonstration

@bp.route('/create-escrow', methods=['POST'])
@jwt_required()
def create_escrow():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        project = Project.query.get(data['project_id'])
        
        if not project or project.client_id != current_user['id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Check if escrow already exists
        existing_escrow = EscrowAccount.query.filter_by(project_id=project.id).first()
        if existing_escrow:
            return jsonify({'error': 'Escrow already exists for this project'}), 400
        
        # Create escrow account
        escrow = EscrowAccount(
            project_id=project.id,
            amount=data['amount'],
            payment_id=f"PAY_{project.id}_{int(datetime.now().timestamp())}",
            status='held'
        )
        
        db.session.add(escrow)
        db.session.commit()
        
        return jsonify({
            'escrow_id': escrow.id,
            'amount': escrow.amount,
            'status': escrow.status,
            'message': 'Escrow account created successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/release-escrow/<int:project_id>', methods=['POST'])
@jwt_required()
def release_escrow(project_id):
    try:
        current_user = get_jwt_identity()
        
        project = Project.query.get(project_id)
        
        if not project or project.client_id != current_user['id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if project.status != 'completed':
            return jsonify({'error': 'Project must be completed before releasing payment'}), 400
        
        escrow = EscrowAccount.query.filter_by(project_id=project_id).first()
        
        if not escrow or escrow.status != 'held':
            return jsonify({'error': 'Invalid escrow state'}), 400
        
        # Release payment
        escrow.status = 'released'
        escrow.released_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Payment released successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/escrow/<int:project_id>', methods=['GET'])
@jwt_required()
def get_escrow_status(project_id):
    try:
        current_user = get_jwt_identity()
        
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check if user is client or the accepted student
        accepted_bid = Bid.query.get(project.accepted_bid_id) if project.accepted_bid_id else None
        
        if project.client_id != current_user['id'] and (not accepted_bid or accepted_bid.student_id != current_user['id']):
            return jsonify({'error': 'Unauthorized'}), 403
        
        escrow = EscrowAccount.query.filter_by(project_id=project_id).first()
        
        if not escrow:
            return jsonify({'error': 'Escrow not found'}), 404
        
        return jsonify({
            'escrow_id': escrow.id,
            'amount': escrow.amount,
            'status': escrow.status,
            'created_at': escrow.created_at.isoformat(),
            'released_at': escrow.released_at.isoformat() if escrow.released_at else None
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/dispute/<int:project_id>', methods=['POST'])
@jwt_required()
def raise_dispute(project_id):
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        escrow = EscrowAccount.query.filter_by(project_id=project_id).first()
        
        if not escrow or escrow.status != 'held':
            return jsonify({'error': 'Cannot raise dispute'}), 400
        
        escrow.status = 'disputed'
        db.session.commit()
        
        # In production, this would trigger admin notification
        
        return jsonify({'message': 'Dispute raised successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
