"""Tournament routes"""
from flask import render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.blueprints.tournaments import tournaments_bp
from app.blueprints.tournaments.forms import SongSubmissionForm, TournamentCreationForm
from app.models import Tournament, Song
from app.extensions import db
from datetime import datetime


@tournaments_bp.route('/')
def list():
    """List all tournaments"""
    tournaments = Tournament.query.order_by(Tournament.created_at.desc()).all()
    return render_template('tournaments/list.html', tournaments=tournaments)

@tournaments_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Tournament creation page"""
    form = TournamentCreationForm()

    if form.validate_on_submit():
        try:
            # Create tournament with Unix timestamps
            tournament = Tournament(
                name=form.name.data,
                description=form.description.data,
                year=datetime.utcnow().year,  # Auto-set to current year
                status='registration',
                registration_deadline=form.get_registration_deadline_timestamp(),
                voting_start_date=form.get_voting_start_timestamp(),
                voting_end_date=form.get_voting_end_timestamp(),
                created_by_user_id=current_user.id
            )

            db.session.add(tournament)
            db.session.commit()

            flash('Tournament created successfully!', 'success')
            return redirect(url_for('tournaments.detail', id=tournament.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating tournament: {str(e)}', 'danger')
            return render_template('tournaments/create.html', form=form)

    return render_template('tournaments/create.html', form=form)

@tournaments_bp.route('/<int:id>')
def detail(id):
    """Tournament detail page"""
    tournament = Tournament.query.get_or_404(id)
    return render_template('tournaments/detail.html', tournament=tournament)


@tournaments_bp.route('/<int:id>/submit', methods=['GET', 'POST'])
@login_required
def submit_song(id):
    """Submit a song to a tournament"""
    tournament = Tournament.query.get_or_404(id)

    if not tournament.is_registration_open():
        flash('Registration is closed for this tournament', 'danger')
        return redirect(url_for('tournaments.detail', id=id))

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
                return render_template('tournaments/submit_song.html', form=form, tournament=tournament)

        # Create song
        song = Song(
            title=song_data['title'],
            artist=song_data['artist'],
            album=song_data.get('album'),
            duration_seconds=song_data.get('duration_seconds'),
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

    return render_template('tournaments/submit_song.html', form=form, tournament=tournament)


@tournaments_bp.route('/<int:id>/my-submissions')
@login_required
def my_submissions(id):
    """View user's submissions for a tournament"""
    tournament = Tournament.query.get_or_404(id)
    songs = Song.query.filter_by(
        tournament_id=id,
        submitted_by_user_id=current_user.id
    ).all()
    return render_template('tournaments/my_submissions.html',
                         tournament=tournament, songs=songs)
