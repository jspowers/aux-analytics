"""Tournaments blueprint"""
from flask import Blueprint

tournaments_bp = Blueprint('tournaments', __name__, template_folder='templates')

from app.blueprints.tournaments import routes
