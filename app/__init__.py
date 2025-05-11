from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__,
               template_folder='templates',  # Explicit template path
               static_folder='static')       # Explicit static path
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/jobboard')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints with URL prefixes
    from .auth.routes import auth_bp
    from .jobs.routes import jobs_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(jobs_bp, url_prefix='/jobs')
    
    # Add essential routes
    @app.route('/')
    def home():
        return render_template('jobs/index.html')  # Or redirect to login
    
    @app.route('/healthcheck')
    def healthcheck():
        return 'OK', 200
    
    return app
