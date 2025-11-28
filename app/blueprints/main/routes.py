from flask import render_template
from app.blueprints.main import main_bp

@main_bp.route('/')
def index():
    """Homepage"""
    return render_template('main/index.html')
