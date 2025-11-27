import os
from flask import Blueprint, render_template, jsonify
from app.blueprints.main.services.app_registry import AppRegistryService

# Get the template folder path relative to this file
template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
main_bp = Blueprint('main', __name__, template_folder=template_dir)


@main_bp.route('/')
def index():
    """Landing page displaying all enabled sub-applications"""
    registry = AppRegistryService()
    apps = registry.get_enabled_apps()
    return render_template('index.html', apps=apps)


@main_bp.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({'status': 'healthy'}), 200
