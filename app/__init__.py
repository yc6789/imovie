import os
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from flask_cors import CORS
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()

# Initialize LoginManager
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, static_folder='../build', static_url_path='/')

    # Configuration
    app.config.from_object('app.config.Config')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)  # Initialize LoginManager with the Flask app

    # Set the session SQLAlchemy instance to the correct one
    app.config['SESSION_SQLALCHEMY'] = db

    # Setup Flask-Session
    Session(app)

    # Enable CORS with credentials support
    CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

    # Set the login view (the route where users will be redirected to log in)
    login_manager.login_view = "main.loginresource"  # Update to the correct endpoint

    # Import models only after initializing extensions
    from app import models

    # Register blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Serve React static files
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    return app

# User loader function required by Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))