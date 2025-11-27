import os
from dotenv import load_dotenv

load_dotenv()

# Sub-Applications Registry
SUB_APPS = [
    {
        'id': 'example',
        'name': 'Example Application',
        'description': 'A placeholder to demonstrate the landing page structure',
        'url_prefix': '/example',
        'icon': '📝',
        'enabled': True
    }
]


class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Flask-WTF Configuration
    WTF_CSRF_ENABLED = True

    # Sub-Apps Registry
    SUB_APPS = SUB_APPS


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'

    # In production, SECRET_KEY must be set
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
