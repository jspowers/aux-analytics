"""Tournament routes"""
from flask import render_template, redirect, url_for, flash, current_app, request
from flask_login import login_required, current_user
from app.blueprints.tournaments import tournaments_bp
from app.blueprints.tournaments.forms import SongSubmissionForm, TournamentCreationForm
from app.models import Tournament, Song, Registration, Round
from app.extensions import db
from app.services.tournament_service import TournamentService
from datetime import datetime, timedelta


@tournaments_bp.route('/')
@login_required
def list():
    """List all tournaments"""
    from sqlalchemy.orm import joinedload

    # Get tournaments created by the user OR where they have registered
    # Use eager loading to fetch registrations and users in the same query
    tournaments = Tournament.query.options(
        joinedload(Tournament.registrations).joinedload(Registration.user)
    ).filter(
        db.or_(
            Tournament.created_by_user_id == current_user.id,
            Tournament.registrations.any(Registration.user_id == current_user.id)
        )
    ).order_by(Tournament.created_at.desc()).all()

    return render_template('tournaments/list.html', tournaments=tournaments)

@tournaments_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Tournament creation page"""
    form = TournamentCreationForm()

    if form.validate_on_submit():
        try:
            from datetime import datetime

            tournament = Tournament(
                tournament_code=Tournament.generate_unique_code(),
                name=form.name.data,
                description=form.description.data,
                year=datetime.now().year,
                status='registration',
                registration_deadline=form.get_registration_deadline_timestamp(),
                max_submissions_per_user=form.max_submissions_per_user.data,
                created_by_user_id=current_user.id
            )

            # Associate by object (do not rely on tournament.id yet)
            registrant = Registration(
                user_id=current_user.id,
            )
            registrant.tournament = tournament

            # Atomic transaction: commit both or neither
           
            db.session.add(tournament)
            db.session.add(registrant)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise

            flash(
                f'Tournament created successfully! Code: {tournament.formatted_code}', 
                'success'
                )
            
            return redirect(url_for('tournaments.detail', id=tournament.id))
            
        except Exception as e:
            # db.session.begin() will rollback automatically on exception,
            # but you can still call rollback here to be explicit
            db.session.rollback()
            flash(f'Error creating tournament: {str(e)}', 'danger')
            return render_template('tournaments/create.html', form=form)

    return render_template('tournaments/create.html', form=form)

@tournaments_bp.route('/<int:id>')
@login_required
def detail(id):
    """Tournament detail page"""
    tournament = Tournament.query.get_or_404(id)

    # Add submission count if user is authenticated
    user_submission_count = None
    if current_user.is_authenticated:
        user_submission_count = tournament.get_user_submission_count(current_user.id)

    return render_template('tournaments/detail.html',
                          tournament=tournament,
                          user_submission_count=user_submission_count)


@tournaments_bp.route('/<int:id>/submit', methods=['GET', 'POST'])
@login_required
def submit_song(id):
    """Submit a song to a tournament"""
    tournament = Tournament.query.get_or_404(id)

    if not tournament.is_registration_open():
        flash('Registration is closed for this tournament', 'danger')
        return redirect(url_for('tournaments.detail', id=id))

    # Check submission limit
    if not tournament.user_can_submit_more(current_user.id):
        flash(f'You have reached the submission limit of {tournament.max_submissions_per_user} songs for this tournament', 'warning')
        return redirect(url_for('tournaments.my_submissions', id=id))

    form = SongSubmissionForm()
    if form.validate_on_submit():
        song_data = {
            'submission_method': form.submission_method.data,
            'title': form.title.data,
            'artist': form.artist.data,
            'album': form.album.data,
            'spotify_url': form.spotify_url.data,
            'youtube_url': form.youtube_url.data
        }

        # Fetch metadata if URL provided
        if form.submission_method.data in ['spotify', 'youtube']:
            try:
                if form.submission_method.data == 'spotify':
                    from app.services.spotify_service import SpotifyService
                    spotify = SpotifyService(
                        current_app.config['SPOTIFY_CLIENT_ID'],
                        current_app.config['SPOTIFY_CLIENT_SECRET']
                    )
                    metadata = spotify.get_track_metadata(form.spotify_url.data)
                    song_data.update(metadata)
                elif form.submission_method.data == 'youtube':
                    from app.services.youtube_service import YouTubeService
                    youtube = YouTubeService(current_app.config['YOUTUBE_API_KEY'])
                    metadata = youtube.get_video_metadata(form.youtube_url.data)
                    song_data.update(metadata)
            except Exception as e:
                flash(f'Error fetching metadata: {str(e)}', 'danger')
                user_submission_count = tournament.get_user_submission_count(current_user.id)
                return render_template('tournaments/submit_song.html',
                                      form=form,
                                      tournament=tournament,
                                      user_submission_count=user_submission_count)

        # Create song
        song = Song(
            title=song_data['title'],
            artist=song_data['artist'],
            album=song_data.get('album'),
            release_date=song_data.get('release_date'),
            release_date_precision=song_data.get('release_date_precision'),
            popularity=song_data.get('popularity'),
            duration_seconds=song_data.get('duration_seconds'),
            isrc_number=song_data.get('isrc_number'),
            spotify_url=song_data.get('spotify_url'),
            youtube_url=song_data.get('youtube_url'),
            spotify_track_id=song_data.get('spotify_track_id'),
            youtube_video_id=song_data.get('youtube_video_id'),
            thumbnail_url=song_data.get('thumbnail_url'),
            submission_method=song_data['submission_method'],
            submitted_by_user_id=current_user.id,
            tournament_id=tournament.id
        )

        db.session.add(song)
        db.session.commit()

        flash('Song submitted successfully!', 'success')
        return redirect(url_for('tournaments.detail', id=id))

    # Get user's current submission count for display
    user_submission_count = tournament.get_user_submission_count(current_user.id)

    return render_template('tournaments/submit_song.html',
                          form=form,
                          tournament=tournament,
                          user_submission_count=user_submission_count)


@tournaments_bp.route('/<int:id>/my-submissions')
@login_required
def my_submissions(id):
    """View user's submissions for a tournament"""
    tournament = Tournament.query.get_or_404(id)
    songs = Song.query.filter_by(
        tournament_id=id,
        submitted_by_user_id=current_user.id
    ).all()

    user_submission_count = len(songs)

    return render_template('tournaments/my_submissions.html',
                         tournament=tournament,
                         songs=songs,
                         user_submission_count=user_submission_count)


@tournaments_bp.route('/<int:tournament_id>/delete-song/<int:song_id>', methods=['POST'])
@login_required
def delete_song(tournament_id, song_id):
    """Delete a user's submitted song from a tournament"""
    tournament = Tournament.query.get_or_404(tournament_id)
    song = Song.query.get_or_404(song_id)

    # Verify song belongs to current user and this tournament
    if song.submitted_by_user_id != current_user.id:
        flash('You can only delete your own submissions', 'danger')
        return redirect(url_for('tournaments.my_submissions', id=tournament_id))

    if song.tournament_id != tournament_id:
        flash('Invalid song for this tournament', 'danger')
        return redirect(url_for('tournaments.my_submissions', id=tournament_id))

    # Check if tournament is still in registration phase
    if not tournament.is_registration_open():
        flash('Cannot delete submissions after registration closes', 'danger')
        return redirect(url_for('tournaments.my_submissions', id=tournament_id))

    # Delete the song
    song_title = song.title  # Store for flash message
    db.session.delete(song)
    db.session.commit()

    flash(f'Successfully deleted "{song_title}"', 'success')
    return redirect(url_for('tournaments.my_submissions', id=tournament_id))


@tournaments_bp.route('/<int:tournament_id>/round/<int:round_id>/end-early', methods=['POST'])
@login_required
def end_round_early(tournament_id, round_id):
    """End a round early and advance to the next round"""
    tournament = Tournament.query.get_or_404(tournament_id)
    round_obj = Round.query.get_or_404(round_id)

    # Authorization: Only tournament creator can manage rounds
    if tournament.created_by_user_id != current_user.id:
        flash('Only the tournament creator can manage rounds', 'danger')
        return redirect(url_for('voting.bracket', tournament_id=tournament_id))

    # Verify round belongs to this tournament
    if round_obj.tournament_id != tournament_id:
        flash('Invalid round for this tournament', 'danger')
        return redirect(url_for('voting.bracket', tournament_id=tournament_id))

    # Can only end active rounds early
    if round_obj.status != 'active':
        flash('Can only end active rounds early', 'warning')
        return redirect(url_for('voting.bracket', tournament_id=tournament_id))

    try:
        # Advance the round
        from app.services.tournament_service import TournamentService
        TournamentService.advance_round(tournament, round_obj)

        flash(f'{round_obj.name} has been ended early and winners have advanced!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error ending round: {str(e)}', 'danger')

    return redirect(url_for('voting.bracket', tournament_id=tournament_id))


@tournaments_bp.route('/<int:tournament_id>/round/<int:round_id>/extend', methods=['POST'])
@login_required
def extend_round(tournament_id, round_id):
    """Extend a round's deadline"""
    tournament = Tournament.query.get_or_404(tournament_id)
    round_obj = Round.query.get_or_404(round_id)

    # Authorization: Only tournament creator can manage rounds
    if tournament.created_by_user_id != current_user.id:
        flash('Only the tournament creator can manage rounds', 'danger')
        return redirect(url_for('voting.bracket', tournament_id=tournament_id))

    # Verify round belongs to this tournament
    if round_obj.tournament_id != tournament_id:
        flash('Invalid round for this tournament', 'danger')
        return redirect(url_for('voting.bracket', tournament_id=tournament_id))

    # Can only extend active or pending rounds
    if round_obj.status not in ['active', 'pending']:
        flash('Can only extend active or pending rounds', 'warning')
        return redirect(url_for('voting.bracket', tournament_id=tournament_id))

    try:
        # Get extension hours from form (default 24 hours)
        extension_hours = int(request.form.get('extension_hours', 24))

        # Extend this round
        if round_obj.end_date:
            new_end_date = datetime.fromtimestamp(round_obj.end_date) + timedelta(hours=extension_hours)
            round_obj.end_date = int(new_end_date.timestamp())
        else:
            # If no end date set, extend from now
            new_end_date = datetime.now() + timedelta(hours=extension_hours)
            round_obj.end_date = int(new_end_date.timestamp())

        # Cascade delay to all following rounds
        rounds = Round.query.filter_by(tournament_id=tournament_id).order_by(Round.round_number).all()
        for r in rounds:
            if r.round_number > round_obj.round_number:
                # Shift start and end dates by extension_hours
                if r.start_date:
                    r.start_date = int(datetime.fromtimestamp(r.start_date).timestamp()) + (extension_hours * 3600)
                if r.end_date:
                    r.end_date = int(datetime.fromtimestamp(r.end_date).timestamp()) + (extension_hours * 3600)

        db.session.commit()
        flash(f'{round_obj.name} has been extended by {extension_hours} hours. All following rounds have been delayed accordingly.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error extending round: {str(e)}', 'danger')

    return redirect(url_for('voting.bracket', tournament_id=tournament_id))


@tournaments_bp.route('/<int:id>/build-bracket', methods=['GET', 'POST'])
@login_required
def build_bracket(id):
    """Preview and confirm bracket generation for a tournament"""
    tournament = Tournament.query.get_or_404(id)

    # Authorization: Only tournament creator can build bracket
    if tournament.created_by_user_id != current_user.id:
        flash('Only the tournament creator can build the bracket', 'danger')
        return redirect(url_for('tournaments.detail', id=id))

    # Validation: Tournament must be in registration status
    if tournament.status != 'registration':
        flash('Bracket can only be built from registration status', 'danger')
        return redirect(url_for('tournaments.detail', id=id))

    # Validation: Must have at least 2 songs
    song_count = tournament.songs.count()
    if song_count < 2:
        flash('Cannot build bracket with fewer than 2 songs', 'danger')
        return redirect(url_for('tournaments.detail', id=id))

    # GET: Generate preview of matchups
    if request.method == 'GET':
        # Seed songs
        seeded_songs = TournamentService.seed_songs(tournament)

        # Generate rounds if they don't exist yet
        existing_rounds = Round.query.filter_by(tournament_id=tournament.id).count()
        if existing_rounds == 0:
            TournamentService.generate_rounds(tournament)

        # Create a preview data structure without DB operations
        import math
        bracket_size = 2 ** math.ceil(math.log2(song_count))
        num_byes = bracket_size - song_count

        # Preview matchups for Round 1
        songs_in_round_1 = seeded_songs[num_byes:]
        preview_matchups = []

        for i in range(len(songs_in_round_1) // 2):
            high_seed = songs_in_round_1[i]
            low_seed = songs_in_round_1[-(i + 1)]
            preview_matchups.append({
                'song1': high_seed,
                'song2': low_seed,
                'seed1': num_byes + i + 1,
                'seed2': song_count - i
            })

        # Preview bye information
        bye_songs = seeded_songs[:num_byes] if num_byes > 0 else []
        bye_info = [{'song': song, 'seed': idx + 1} for idx, song in enumerate(bye_songs)]

        # Get round info
        rounds = Round.query.filter_by(tournament_id=tournament.id).order_by(Round.round_number).all()

        return render_template('tournaments/build_bracket.html',
                             tournament=tournament,
                             preview_matchups=preview_matchups,
                             bye_info=bye_info,
                             num_byes=num_byes,
                             song_count=song_count,
                             rounds=rounds)

    # POST: Confirm and create the bracket
    if request.method == 'POST':
        try:
            # Get deadline from form (default 72 hours per round)
            deadline_hours = int(request.form.get('deadline_hours', 72))

            # Seed songs
            seeded_songs = TournamentService.seed_songs(tournament)

            # Generate matchups (this commits to DB)
            result = TournamentService.generate_matchups(tournament, seeded_songs)

            # Set deadlines for all rounds
            rounds = Round.query.filter_by(tournament_id=tournament.id).order_by(Round.round_number).all()
            current_time = datetime.now()

            for idx, round_obj in enumerate(rounds):
                if idx == 0:
                    # Round 1 starts immediately
                    round_obj.start_date = int(current_time.timestamp())
                    round_obj.end_date = int((current_time + timedelta(hours=deadline_hours)).timestamp())
                    round_obj.status = 'active'
                else:
                    # Subsequent rounds start after previous round ends
                    prev_round = rounds[idx - 1]
                    round_obj.start_date = prev_round.end_date
                    round_obj.end_date = int((datetime.fromtimestamp(prev_round.end_date) + timedelta(hours=deadline_hours)).timestamp())
                    round_obj.status = 'pending'

            # Update tournament status to voting_round_1
            tournament.status = 'voting_round_1'

            db.session.commit()

            flash(f'Bracket created successfully! {result["total_matchups"]} matchups generated with {result["num_byes"]} bye(s). Round 1 voting is now open!', 'success')
            return redirect(url_for('tournaments.detail', id=id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error building bracket: {str(e)}', 'danger')
            return redirect(url_for('tournaments.detail', id=id))
