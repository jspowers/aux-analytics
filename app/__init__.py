from flask import Flask, render_template
from config import config

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Register authentication middleware
    from app.auth.middleware import setup_auth
    setup_auth(app)

    # Register blueprints
    from app.blueprints.main import main_bp
    from app.blueprints.voting import voting_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(voting_bp, url_prefix='/voting')

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    return app
