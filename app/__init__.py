import logging
from flask import Flask, render_template
from config import config
from app.extensions import db, migrate, login_manager, csrf
from app.models import (User, Tournament, Round, Song, Vote)

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Create Database
    with app.app_context():
        logging.info("Creating database tables...")
        db.create_all()

    # Register custom Jinja2 filters
    @app.template_filter("strftime")
    def timestamp_to_datetime(value, fmt="%B %d, %Y at %I:%M %p"):
        from datetime import datetime
        if value is None:
            return ""
        dt = datetime.fromtimestamp(value)
        return dt.strftime(fmt)

    # User loader for Flask-Login
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    from app.blueprints.main import main_bp
    from app.blueprints.voting import voting_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.tournaments import tournaments_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(voting_bp, url_prefix='/voting')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(tournaments_bp, url_prefix='/tournaments')

    # CLI command for creating users
    @app.cli.command()
    def create_user():
        """Create a new user via CLI"""
        from getpass import getpass

        username = input("Username: ")
        email = input("Email: ")
        first_name = input("First name: ")
        password = getpass("Password: ")

        user = User(username=username, email=email, first_name=first_name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        print(f"User '{username}' created successfully!")

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    return app
