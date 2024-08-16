from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:220202@localhost:5433/imovie'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TMDB_API_KEY = '4908a00b5458f031729369ad88466209'
    SECRET_KEY = '220202'

    # Session configuration
    SESSION_TYPE = 'sqlalchemy'
    SESSION_SQLALCHEMY = SQLAlchemy()  # This will be replaced when initializing the app
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Adjust session cookies for local development
    SESSION_COOKIE_SAMESITE = 'Lax'  # Use 'Lax' for local development
    SESSION_COOKIE_SECURE = False    # Disable Secure for non-HTTPS local development
