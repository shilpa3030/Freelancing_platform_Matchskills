from app import create_app, socketio, db
from app.models import User
from sqlalchemy import text
import os

app = create_app()


def ensure_default_admin():
    """If no admin exists, create one so / login works without running a manual snippet.

    Override with env: ADMIN_EMAIL, ADMIN_PASSWORD (use strong values in production).
    """
    if User.query.filter_by(role='admin').first():
        return
    email = os.environ.get('ADMIN_EMAIL', 'admin@freelancehub.com').strip()
    password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    if User.query.filter_by(email=email).first():
        print(
            'WARNING: No admin user, but %r is already registered. '
            'Set ADMIN_EMAIL to a different address or promote a user in the DB.' % email
        )
        return
    admin = User(email=email, role='admin')
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    print('Default admin created — email: %s (password from ADMIN_PASSWORD or default admin123)' % email)


def _ensure_student_resume_columns():
    """SQLite: add resume columns if missing (create_all does not migrate)."""
    if 'sqlite' not in str(db.engine.url):
        return
    insp = db.inspect(db.engine)
    try:
        cols = {c['name'] for c in insp.get_columns('student_profile')}
    except Exception:
        return
    alters = []
    if 'resume_filename' not in cols:
        alters.append('ALTER TABLE student_profile ADD COLUMN resume_filename VARCHAR(500)')
    if 'resume_original_name' not in cols:
        alters.append('ALTER TABLE student_profile ADD COLUMN resume_original_name VARCHAR(300)')
    if not alters:
        return
    with db.engine.begin() as conn:
        for sql in alters:
            conn.execute(text(sql))


# Create database tables
with app.app_context():
    db.create_all()
    _ensure_student_resume_columns()
    ensure_default_admin()
    os.makedirs(app.config['RESUME_UPLOAD_DIR'], exist_ok=True)
    print("Database tables created successfully!")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
