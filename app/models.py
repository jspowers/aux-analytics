"""Database models for Auxiliary Analytics"""
import time
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db


class User(UserMixin, db.Model):
    """User model for authentication and song submissions"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.Integer, default=lambda: int(time.time()), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    songs = db.relationship(
        'Song', 
        backref='submitted_by', 
        lazy='dynamic', 
        foreign_keys='Song.submitted_by_user_id'
        )
    votes = db.relationship('Vote', backref='user', lazy='dynamic')

    def set_password(self, password):
        """Hash and store password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'


class Tournament(db.Model):
    """Tournament model for organizing song competitions"""
    __tablename__ = 'tournaments'

    id = db.Column(db.Integer, primary_key=True)
    tournament_code = db.Column(db.String(4), unique=True, nullable=False, index=True)  # 4-digit alphanumeric code
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    year = db.Column(db.Integer, index=True)
    status = db.Column(db.String(20), default='registration', nullable=False)  # registration, voting, completed
    registration_deadline = db.Column(db.Integer, nullable=False)  # Unix timestamp
    voting_start_date = db.Column(db.Integer)  # Unix timestamp (optional)
    voting_end_date = db.Column(db.Integer)  # Unix timestamp (optional)
    max_submissions_per_user = db.Column(db.Integer, default=4, nullable=False)
    created_at = db.Column(db.Integer, default=lambda: int(time.time()), nullable=False)  # Unix timestamp
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    songs = db.relationship('Song', backref='tournament', lazy='dynamic')
    registrations = db.relationship('Registration', backref='tournament', lazy='selectin', cascade='all, delete-orphan')
    rounds = db.relationship('Round', backref='tournament', lazy='dynamic', order_by='Round.round_number', cascade='all, delete-orphan')
    creator = db.relationship('User', backref='created_tournaments', foreign_keys=[created_by_user_id])
    matchups = db.relationship('Matchup', backref='tournament', lazy='dynamic', cascade='all, delete-orphan')

    def is_registration_open(self):
        """Check if song submissions are allowed"""
        if self.status != 'registration':
            return False
        if self.registration_deadline:
            now = int(time.time())
            if now > self.registration_deadline:
                return False
        return True

    def is_voting_open(self):
        """Check if voting is currently active"""
        if self.status != 'voting':
            return False
        now = int(time.time())
        if self.voting_start_date and now < self.voting_start_date:
            return False
        if self.voting_end_date and now > self.voting_end_date:
            return False
        return True

    def get_num_rounds_needed(self):
        """Calculate number of rounds needed based on song count"""
        import math
        song_count = self.songs.count()
        if song_count < 2:
            return 0
        # Calculate rounds needed for single-elimination bracket
        return math.ceil(math.log2(song_count))

    @property
    def formatted_code(self):
        """Return tournament code formatted with pound sign"""
        return f"#{self.tournament_code}"

    def get_registered_users(self):
        """Get list of User objects who are registered for this tournament"""
        return [reg.user for reg in self.registrations]

    def get_registered_user_names(self):
        """Get comma-separated string of registered user names"""
        users = self.get_registered_users()
        if not users:
            return "No registrants yet"
        return ", ".join([user.name for user in users])

    def get_registration_count(self):
        """Get count of registered users"""
        return len(self.registrations)

    def get_user_submission_count(self, user_id):
        """Get count of songs submitted by a specific user for this tournament"""
        return self.songs.filter_by(submitted_by_user_id=user_id).count()

    def user_can_submit_more(self, user_id):
        """Check if user can submit more songs to this tournament"""
        current_count = self.get_user_submission_count(user_id)
        return current_count < self.max_submissions_per_user

    def get_remaining_submissions(self, user_id):
        """Get number of submissions remaining for a user"""
        current_count = self.get_user_submission_count(user_id)
        remaining = self.max_submissions_per_user - current_count
        return max(0, remaining)

    def get_current_round_number(self):
        """Get the current active round number based on tournament status"""
        if self.status == 'registration' or self.status == 'completed':
            return None

        # Status format: voting_round_1, voting_round_2, etc.
        if self.status.startswith('voting_round_'):
            try:
                return int(self.status.split('_')[-1])
            except (ValueError, IndexError):
                return None

        return None

    def is_voting_phase(self):
        """Check if tournament is in a voting phase"""
        return self.status.startswith('voting_round_')

    def get_current_round(self):
        """Get the current active Round object"""
        round_number = self.get_current_round_number()
        if round_number is None:
            return None

        return Round.query.filter_by(
            tournament_id=self.id,
            round_number=round_number
        ).first()

    @staticmethod
    def generate_unique_code():
        """Generate a unique 4-character alphanumeric tournament code"""
        import random

        # Use uppercase letters and digits for better readability
        # Exclude confusing characters: 0, O, I, 1
        chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'

        max_attempts = 100
        for _ in range(max_attempts):
            code = ''.join(random.choice(chars) for _ in range(4))
            # Check if code already exists
            if not Tournament.query.filter_by(tournament_code=code).first():
                return code

        # If we couldn't find a unique code after max_attempts, raise an error
        raise ValueError("Unable to generate unique tournament code")

    def __repr__(self):
        return f'<Tournament {self.name} ({self.year})>'

class Registration(db.Model):
    """Registration model for tournament participants"""
    __tablename__ = 'registrations'

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    registered_at = db.Column(db.Integer, default=lambda: int(time.time()), nullable=False)

    # Relationships
    user = db.relationship('User', backref='tournament_registrations')

    # Unique constraint: one round number per tournament
    __table_args__ = (
        db.UniqueConstraint('tournament_id', 'user_id', name='uq_tournament_user_registration'),
    )

    def __repr__(self):
        return f'<Registration U{self.user_id} T{self.tournament_id}>'


class Round(db.Model):
    """Round model for tournament progression"""
    __tablename__ = 'rounds'

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    round_number = db.Column(db.Integer, nullable=False)  # 1, 2, 3...
    name = db.Column(db.String(100))  # e.g., "Round of 16", "Quarterfinals", "Semifinals", "Finals"
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, active, completed
    start_date = db.Column(db.Integer)  # Unix timestamp
    end_date = db.Column(db.Integer)  # Unix timestamp
    created_at = db.Column(db.Integer, default=lambda: int(time.time()), nullable=False)

    # Relationships
    matchups = db.relationship('Matchup', backref='round', lazy='dynamic', cascade='all, delete-orphan')

    # Unique constraint: one round number per tournament
    __table_args__ = (
        db.UniqueConstraint('tournament_id', 'round_number', name='uq_tournament_round'),
    )

    def is_active(self):
        """Check if this round is currently active for voting"""
        if self.status != 'active':
            return False
        now = int(time.time())
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True

    def __repr__(self):
        return f'<Round {self.tournament_id} R{self.round_number} - {self.name}>'


class Song(db.Model):
    """Song model for tournament submissions"""
    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    album = db.Column(db.String(200))
    release_date = db.Column(db.String(200))
    release_date_precision = db.Column(db.String(200))
    popularity = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)
    isrc_number = db.Column(db.String(500))
    spotify_url = db.Column(db.String(500))
    youtube_url = db.Column(db.String(500))
    spotify_track_id = db.Column(db.String(100), index=True)
    youtube_video_id = db.Column(db.String(100), index=True)
    thumbnail_url = db.Column(db.String(500))
    submission_method = db.Column(db.String(20), nullable=False)  # manual, spotify, youtube
    submitted_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    created_at = db.Column(db.Integer, default=lambda: int(time.time()), nullable=False)

    # Unique constraint to prevent exact duplicates per user per tournament
    __table_args__ = (
        db.UniqueConstraint('submitted_by_user_id', 'tournament_id', 'title', 'artist',
                           name='uq_user_tournament_song'),
    )

    # Relationships for matchups (song can be in multiple matchups)
    matchups_as_song1 = db.relationship('Matchup', foreign_keys='Matchup.song1_id',
                                       backref='song1', lazy='dynamic')
    matchups_as_song2 = db.relationship('Matchup', foreign_keys='Matchup.song2_id',
                                       backref='song2', lazy='dynamic')
    matchups_as_winner = db.relationship('Matchup', foreign_keys='Matchup.winner_song_id',
                                        backref='winner', lazy='dynamic')

    def get_primary_url(self):
        """Return Spotify URL if available, else YouTube URL"""
        return self.spotify_url or self.youtube_url

    def get_display_duration(self):
        """Format duration as MM:SS"""
        if not self.duration_seconds:
            return None
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes}:{seconds:02d}"

    def __repr__(self):
        return f'<Song {self.title} by {self.artist}>'


class Matchup(db.Model):
    """Matchup model for bracket pairings"""
    __tablename__ = 'matchups'

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    round_id = db.Column(db.Integer, db.ForeignKey('rounds.id'), nullable=False)
    position_in_round = db.Column(db.Integer)  # For bracket placement
    song1_id = db.Column(db.Integer, db.ForeignKey('songs.id'))  # Nullable for TBD matchups
    song2_id = db.Column(db.Integer, db.ForeignKey('songs.id'))  # Nullable for TBD matchups
    winner_song_id = db.Column(db.Integer, db.ForeignKey('songs.id'))  # Nullable until voting completes
    next_matchup_id = db.Column(db.Integer, db.ForeignKey('matchups.id'))  # Self-referential for bracket progression
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, active, completed
    created_at = db.Column(db.Integer, default=lambda: int(time.time()), nullable=False)

    # Relationships
    votes = db.relationship('Vote', backref='matchup', lazy='dynamic', cascade='all, delete-orphan')
    next_matchup = db.relationship('Matchup', remote_side=[id], backref='previous_matchups')

    def get_vote_count(self, song_id):
        """Count votes for a specific song in this matchup"""
        return self.votes.filter_by(song_id=song_id).count()

    def get_winner(self):
        """Determine winner based on votes (returns Song object or None)"""
        if self.winner_song_id:
            return Song.query.get(self.winner_song_id)

        if not self.song1_id or not self.song2_id:
            return None

        song1_votes = self.get_vote_count(self.song1_id)
        song2_votes = self.get_vote_count(self.song2_id)

        if song1_votes > song2_votes:
            return Song.query.get(self.song1_id)
        elif song2_votes > song1_votes:
            return Song.query.get(self.song2_id)
        return None  # Tie

    def __repr__(self):
        return f'<Matchup R{self.round_id} P{self.position_in_round}>'


class Vote(db.Model):
    """Vote model for user voting on matchups"""
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    matchup_id = db.Column(db.Integer, db.ForeignKey('matchups.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)  # The song voted for
    voted_at = db.Column(db.Integer, default=lambda: int(time.time()), nullable=False)
    updated_at = db.Column(db.Integer, default=lambda: int(time.time()), onupdate=lambda: int(time.time()), nullable=False)
    is_vote_changed = db.Column(db.Boolean, default=False, nullable=False)

    # Unique constraint to prevent duplicate votes
    __table_args__ = (
        db.UniqueConstraint('user_id', 'matchup_id', name='uq_user_matchup_vote'),
    )

    # Relationship to song
    song = db.relationship('Song', backref='votes')

    def __repr__(self):
        return f'<Vote U{self.user_id} M{self.matchup_id} S{self.song_id}>'
