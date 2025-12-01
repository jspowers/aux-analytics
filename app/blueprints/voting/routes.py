from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.blueprints.voting import voting_bp
from app.models import Tournament, Round, Matchup, Vote, Song
from app.extensions import db
import time

@voting_bp.route('/bracket')
@login_required
def bracket():
    """Tournament bracket voting page with tabs for rounds"""
    tournament_id = request.args.get('tournament_id', type=int)

    if not tournament_id:
        flash('Please select a tournament to view the bracket', 'warning')
        return redirect(url_for('tournaments.list'))

    tournament = Tournament.query.get_or_404(tournament_id)

    # Get all rounds for this tournament
    rounds = Round.query.filter_by(tournament_id=tournament_id).order_by(Round.round_number).all()

    if not rounds:
        flash('No bracket has been built for this tournament yet', 'warning')
        return redirect(url_for('tournaments.detail', id=tournament_id))

    # Get current round number
    current_round_number = tournament.get_current_round_number()

    # Build data for each round
    rounds_data = []
    for round_obj in rounds:
        matchups = Matchup.query.filter_by(round_id=round_obj.id).order_by(Matchup.position_in_round).all()

        # Check if round has been built yet
        if not matchups and round_obj.status == 'pending':
            # Round hasn't been built yet (matchups will be created when previous round is finalized)
            rounds_data.append({
                'round': round_obj,
                'matchups': [],
                'is_active': False,
                'is_voting_open': False,
                'not_built_yet': True
            })
            continue

        # Prepare matchup data with vote information
        matchups_data = []
        for matchup in matchups:
            # Get user's vote for this matchup
            user_vote = None
            if current_user.is_authenticated:
                vote = Vote.query.filter_by(user_id=current_user.id, matchup_id=matchup.id).first()
                if vote:
                    user_vote = vote.song_id

            # Determine matchup display state
            matchup_data = {
                'id': matchup.id,
                'song1': None,
                'song2': None,
                'song1_votes': 0,
                'song2_votes': 0,
                'user_vote': user_vote,
                'is_tbd': False,
                'tbd_message': None
            }

            # If both songs are present, show them
            if matchup.song1_id and matchup.song2_id:
                matchup_data['song1'] = Song.query.get(matchup.song1_id)
                matchup_data['song2'] = Song.query.get(matchup.song2_id)
                matchup_data['song1_votes'] = matchup.get_vote_count(matchup.song1_id)
                matchup_data['song2_votes'] = matchup.get_vote_count(matchup.song2_id)
            else:
                # TBD matchup - need to determine the message
                matchup_data['is_tbd'] = True

                # Check if this is the immediate next round
                if current_round_number and round_obj.round_number == current_round_number + 1:
                    # Show "Winner of X vs Y" for immediate next round
                    prev_matchups = Matchup.query.filter_by(next_matchup_id=matchup.id).all()

                    if len(prev_matchups) >= 2:
                        # Get the two previous matchups that feed into this one
                        prev1, prev2 = prev_matchups[0], prev_matchups[1]

                        # Build winner descriptions
                        def get_matchup_description(m):
                            if m.song1_id and m.song2_id:
                                s1 = Song.query.get(m.song1_id)
                                s2 = Song.query.get(m.song2_id)
                                return f"{s1.title} vs {s2.title}"
                            return "TBD"

                        desc1 = get_matchup_description(prev1)
                        desc2 = get_matchup_description(prev2)
                        matchup_data['tbd_message'] = f"Winner of ({desc1}) vs Winner of ({desc2})"
                    elif len(prev_matchups) == 1:
                        prev1 = prev_matchups[0]
                        if prev1.song1_id and prev1.song2_id:
                            s1 = Song.query.get(prev1.song1_id)
                            s2 = Song.query.get(prev1.song2_id)

                            # Check if one song is a bye (advancing from Round 2)
                            if matchup.song1_id:
                                bye_song = Song.query.get(matchup.song1_id)
                                matchup_data['tbd_message'] = f"{bye_song.title} vs Winner of ({s1.title} vs {s2.title})"
                            elif matchup.song2_id:
                                bye_song = Song.query.get(matchup.song2_id)
                                matchup_data['tbd_message'] = f"Winner of ({s1.title} vs {s2.title}) vs {bye_song.title}"
                            else:
                                matchup_data['tbd_message'] = f"Winner of ({s1.title} vs {s2.title})"
                else:
                    # Future rounds not immediately next
                    matchup_data['tbd_message'] = "TBD"

            matchups_data.append(matchup_data)

        # Check if round is active and voting is allowed
        now = int(time.time())
        is_active = round_obj.status == 'active'
        is_voting_open = is_active

        if round_obj.end_date and now > round_obj.end_date:
            is_voting_open = False

        rounds_data.append({
            'round': round_obj,
            'matchups': matchups_data,
            'is_active': is_active,
            'is_voting_open': is_voting_open
        })

    return render_template('voting/bracket.html',
                         tournament=tournament,
                         rounds_data=rounds_data,
                         current_round_number=current_round_number)

@voting_bp.route('/vote', methods=['POST'])
@login_required
def vote():
    """Submit or update a vote for a matchup"""
    matchup_id = request.form.get('matchup_id', type=int)
    song_id = request.form.get('song_id', type=int)

    if not matchup_id or not song_id:
        return jsonify({'success': False, 'error': 'Missing matchup_id or song_id'}), 400

    matchup = Matchup.query.get_or_404(matchup_id)

    # Verify song exists and is part of this matchup
    if song_id not in [matchup.song1_id, matchup.song2_id]:
        return jsonify({'success': False, 'error': 'Invalid song for this matchup'}), 400

    Song.query.get_or_404(song_id)  # Verify song exists

    # Verify round is active and voting is open
    round_obj = Round.query.get(matchup.round_id)
    now = int(time.time())

    if round_obj.status != 'active':
        return jsonify({'success': False, 'error': 'This round is not active'}), 400

    if round_obj.end_date and now > round_obj.end_date:
        return jsonify({'success': False, 'error': 'Voting deadline has passed'}), 400

    # Check if user already voted
    existing_vote = Vote.query.filter_by(user_id=current_user.id, matchup_id=matchup_id).first()

    if existing_vote:
        # User is changing their vote
        if existing_vote.song_id != song_id:
            existing_vote.song_id = song_id
            existing_vote.updated_at = int(time.time())
            existing_vote.is_vote_changed = True
            db.session.commit()
            return jsonify({'success': True, 'message': 'Vote updated successfully', 'vote_changed': True})
        else:
            # Same vote, no change needed
            return jsonify({'success': True, 'message': 'Vote already recorded', 'vote_changed': False})
    else:
        # New vote
        new_vote = Vote(
            user_id=current_user.id,
            matchup_id=matchup_id,
            song_id=song_id
        )
        db.session.add(new_vote)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Vote recorded successfully', 'vote_changed': False})

