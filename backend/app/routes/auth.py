from flask import Blueprint, request, jsonify
from app import db
from app.models import User, StudentProfile, ClientProfile
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate input
        if not data.get('email') or not data.get('password') or not data.get('role'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create user
        user = User(email=data['email'], role=data['role'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        
        # Create profile based on role
        if data['role'] == 'student':
            profile = StudentProfile(
                user_id=user.id,
                name=data.get('name', ''),
                college=data.get('college', ''),
                year=data.get('year', '')
            )
        elif data['role'] == 'client':
            profile = ClientProfile(
                user_id=user.id,
                company=data.get('company', ''),
                description=data.get('description', '')
            )
        else:
            return jsonify({'error': 'Invalid role'}), 400
        
        db.session.add(profile)
        db.session.commit()
        
        return jsonify({'message': 'Registration successful', 'user_id': user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        access_token = create_access_token(identity={'id': user.id, 'role': user.role})
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        current_user = get_jwt_identity()
        user = User.query.get(current_user['id'])
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'email': user.email,
            'role': user.role
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
