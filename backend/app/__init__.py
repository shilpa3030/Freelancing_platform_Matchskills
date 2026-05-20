from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_migrate import Migrate

db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO()
migrate = Migrate()

def create_app():
    app = Flask(__name__, 
                template_folder='../../frontend/templates',
                static_folder='../../frontend/static')
    app.config.from_object('app.config.Config')
    from app.config import Config as AppConfig
    app.config['RESUME_UPLOAD_DIR'] = AppConfig.resume_upload_dir()
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    socketio.init_app(app, cors_allowed_origins="*")
    migrate.init_app(app, db)
    
    # Register blueprints
    from app.routes import auth, student, client, admin, project, chat, payment, dashboard
    app.register_blueprint(auth.bp)
    app.register_blueprint(student.bp)
    app.register_blueprint(client.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(project.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(payment.bp)
    app.register_blueprint(dashboard.bp)
    
    # Main route
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')
    
    return app
