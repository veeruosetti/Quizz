import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Some-random-secret-key-that-you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///"+os.path.join(basedir, 'site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking to avoid overhead
    
    # Add the UPLOAD_FOLDER configuration
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'images', 'avatars')  # Path for uploaded files
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # Limit uploaded files to 1 MB
