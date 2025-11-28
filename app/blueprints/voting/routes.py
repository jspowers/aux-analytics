from flask import render_template
from app.blueprints.voting import voting_bp

@voting_bp.route('/bracket')
def bracket():
    """Placeholder voting bracket page"""
    # Mock data for MVP
    mock_matchups = [
        {'round': 1, 'song1': 'Song A', 'song2': 'Song B'},
        {'round': 1, 'song3': 'Song C', 'song4': 'Song D'},
        {'round': 2, 'song5': 'Winner 1', 'song6': 'Winner 2'},
    ]
    return render_template('voting/bracket.html', matchups=mock_matchups)

