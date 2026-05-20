import json
from flask import Blueprint, request, jsonify
from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token
from app import db, socketio
from app.models import Message, User, StudentProfile, ClientProfile, Bid, Project

bp = Blueprint('chat', __name__, url_prefix='/api/chat')


def user_chat_label(user):
    if not user:
        return 'Unknown'
    sp = StudentProfile.query.filter_by(user_id=user.id).first()
    if sp and sp.name:
        return sp.name
    cp = ClientProfile.query.filter_by(user_id=user.id).first()
    if cp and cp.company:
        return cp.company
    return user.email or f'User #{user.id}'


def _has_message_thread(a_id, b_id):
    return Message.query.filter(
        db.or_(
            db.and_(Message.sender_id == a_id, Message.receiver_id == b_id),
            db.and_(Message.sender_id == b_id, Message.receiver_id == a_id),
        )
    ).first() is not None


def messaging_allowed(sender_id, receiver_id, sender_role):
    if sender_id == receiver_id or not db.session.get(User, receiver_id):
        return False
    if _has_message_thread(sender_id, receiver_id):
        return True
    if sender_role == 'student':
        return db.session.query(Bid).join(Project, Bid.project_id == Project.id).filter(
            Bid.student_id == sender_id,
            Project.client_id == receiver_id,
        ).first() is not None
    if sender_role == 'client':
        return db.session.query(Bid).join(Project, Bid.project_id == Project.id).filter(
            Project.client_id == sender_id,
            Bid.student_id == receiver_id,
        ).first() is not None
    return False


def _identity_from_socket_token(token):
    if not token:
        return None
    decoded = decode_token(token)
    sub = decoded.get('sub')
    if isinstance(sub, dict):
        return sub
    if isinstance(sub, str):
        try:
            return json.loads(sub)
        except json.JSONDecodeError:
            return None
    return None


def emit_message_to_users(message):
    payload = {
        'id': message.id,
        'sender_id': message.sender_id,
        'receiver_id': message.receiver_id,
        'content': message.content,
        'timestamp': message.timestamp.isoformat(),
        'project_id': message.project_id,
    }
    socketio.emit('receive_message', payload, room=f'user_{message.receiver_id}')
    socketio.emit('receive_message', payload, room=f'user_{message.sender_id}')


@bp.route('/contacts', methods=['GET'])
@jwt_required()
def get_contacts():
    try:
        current = get_jwt_identity()
        uid = current['id']
        role = current['role']
        ids = set()

        if role == 'student':
            rows = db.session.query(Project.client_id).join(
                Bid, Bid.project_id == Project.id
            ).filter(Bid.student_id == uid)
            ids.update(r[0] for r in rows)
        elif role == 'client':
            rows = db.session.query(Bid.student_id).join(
                Project, Bid.project_id == Project.id
            ).filter(Project.client_id == uid)
            ids.update(r[0] for r in rows)

        sent = db.session.query(Message.receiver_id).filter_by(sender_id=uid)
        recv = db.session.query(Message.sender_id).filter_by(receiver_id=uid)
        ids.update(r[0] for r in sent)
        ids.update(r[0] for r in recv)
        ids.discard(uid)

        out = []
        for pid in ids:
            u = db.session.get(User, pid)
            if not u:
                continue
            out.append({
                'user_id': u.id,
                'email': u.email,
                'role': u.role,
                'label': user_chat_label(u),
            })
        out.sort(key=lambda x: (x['label'] or '').lower())
        return jsonify(out), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    try:
        current_user = get_jwt_identity()

        sent = db.session.query(Message.receiver_id).filter_by(sender_id=current_user['id']).distinct()
        received = db.session.query(Message.sender_id).filter_by(receiver_id=current_user['id']).distinct()

        partner_ids = set([r[0] for r in sent] + [r[0] for r in received])

        conversations = []
        for partner_id in partner_ids:
            user = db.session.get(User, partner_id)
            if not user:
                continue
            last_message = Message.query.filter(
                db.or_(
                    db.and_(Message.sender_id == current_user['id'], Message.receiver_id == partner_id),
                    db.and_(Message.sender_id == partner_id, Message.receiver_id == current_user['id'])
                )
            ).order_by(Message.timestamp.desc()).first()

            unread_count = Message.query.filter_by(
                sender_id=partner_id,
                receiver_id=current_user['id'],
                is_read=False
            ).count()

            conversations.append({
                'user_id': user.id,
                'email': user.email,
                'label': user_chat_label(user),
                'last_message': last_message.content if last_message else None,
                'timestamp': last_message.timestamp.isoformat() if last_message else None,
                'unread_count': unread_count
            })

        conversations.sort(key=lambda c: c['timestamp'] or '', reverse=True)
        return jsonify(conversations), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/messages/<int:user_id>', methods=['GET'])
@jwt_required()
def get_messages(user_id):
    try:
        current_user = get_jwt_identity()

        if not messaging_allowed(current_user['id'], user_id, current_user.get('role')):
            return jsonify({'error': 'Messaging is not available with this user'}), 403

        messages = Message.query.filter(
            db.or_(
                db.and_(Message.sender_id == current_user['id'], Message.receiver_id == user_id),
                db.and_(Message.sender_id == user_id, Message.receiver_id == current_user['id'])
            )
        ).order_by(Message.timestamp.asc()).all()

        Message.query.filter_by(sender_id=user_id, receiver_id=current_user['id']).update({'is_read': True})
        db.session.commit()

        return jsonify([{
            'id': m.id,
            'sender_id': m.sender_id,
            'receiver_id': m.receiver_id,
            'content': m.content,
            'timestamp': m.timestamp.isoformat(),
            'is_read': m.is_read
        } for m in messages]), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/messages', methods=['POST'])
@jwt_required()
def send_message():
    try:
        current_user = get_jwt_identity()
        data = request.get_json(silent=True) or {}
        receiver_id = data.get('receiver_id')
        content = (data.get('content') or '').strip()

        if receiver_id is None:
            return jsonify({'error': 'receiver_id is required'}), 400
        if not content:
            return jsonify({'error': 'Message cannot be empty'}), 400

        try:
            receiver_id = int(receiver_id)
        except (TypeError, ValueError):
            return jsonify({'error': 'Invalid receiver_id'}), 400

        if not messaging_allowed(current_user['id'], receiver_id, current_user.get('role')):
            return jsonify({'error': 'Messaging is not available with this user'}), 403

        message = Message(
            sender_id=current_user['id'],
            receiver_id=receiver_id,
            content=content,
            project_id=data.get('project_id')
        )

        db.session.add(message)
        db.session.commit()

        emit_message_to_users(message)

        return jsonify({
            'id': message.id,
            'sender_id': message.sender_id,
            'receiver_id': message.receiver_id,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'project_id': message.project_id,
            'message': 'Message sent successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@socketio.on('connect')
def handle_connect(auth):
    token = None
    if isinstance(auth, dict):
        token = auth.get('token')
    identity = _identity_from_socket_token(token)
    if not identity or identity.get('id') is None:
        return False
    user_id = identity['id']
    join_room(f'user_{user_id}', sid=request.sid)


@socketio.on('disconnect')
def handle_disconnect():
    pass


@socketio.on('join')
def on_join(data):
    room = data.get('room')
    if room:
        join_room(room)
        emit('status', {'msg': f'User joined room {room}'}, room=room)


@socketio.on('leave')
def on_leave(data):
    room = data.get('room')
    if room:
        leave_room(room)
        emit('status', {'msg': f'User left room {room}'}, room=room)
