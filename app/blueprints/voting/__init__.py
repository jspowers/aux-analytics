from flask import Blueprint

voting_bp = Blueprint('voting', __name__, template_folder='templates')

from app.blueprints.voting import routes
