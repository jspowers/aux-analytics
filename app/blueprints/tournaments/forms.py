"""Tournament forms"""
from flask_wtf import FlaskForm
from wtforms import StringField, URLField, RadioField, SubmitField, TextAreaField, DateField, TimeField, IntegerField
from wtforms.validators import DataRequired, URL, Optional, Length, ValidationError, NumberRange
from datetime import datetime, time as time_type, timedelta
import time
import pytz


class SongSubmissionForm(FlaskForm):
    """Song submission form for tournaments"""
    submission_method = RadioField('How would you like to submit?',
        choices=[
            ('spotify', 'Paste Spotify URL'),
            # ('manual', 'Enter song details manually'),
            # ('youtube', 'Paste YouTube URL'),
        ],
        default='spotify',
        validators=[DataRequired()])

    # Manual entry fields
    title = StringField('Song Title', validators=[Optional(), Length(max=200)])
    artist = StringField('Artist', validators=[Optional(), Length(max=200)])
    album = StringField('Album', validators=[Optional(), Length(max=200)])

    # URL fields
    spotify_url = URLField('Spotify URL', validators=[Optional(), URL()])
    youtube_url = URLField('YouTube URL', validators=[Optional(), URL()])

    submit = SubmitField('Submit Song')

    def validate(self, extra_validators=None):
        """Custom validation based on submission method"""
        if not super().validate(extra_validators):
            return False

        method = self.submission_method.data

        if method == 'spotify':
            if not self.spotify_url.data:
                self.spotify_url.errors.append('Spotify URL is required')
                return False
        elif method == 'manual':
            if not self.title.data or not self.artist.data:
                self.title.errors.append('Title and Artist are required for manual entry')
                return False
        elif method == 'youtube':
            if not self.youtube_url.data:
                self.youtube_url.errors.append('YouTube URL is required')
                return False

        return True


class TournamentCreationForm(FlaskForm):
    """Tournament creation form"""
    name = StringField('Tournament Name', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    max_submissions_per_user = IntegerField(
        'Maximum Submissions Per User',
        validators=[DataRequired(), NumberRange(min=1, max=20, message='Must be between 1 and 20')],
        default=4
    )

    # Registration deadline with defaults
    registration_deadline_date = DateField('Registration Deadline Date', validators=[DataRequired()])
    registration_deadline_time = TimeField('Registration Deadline Time', validators=[DataRequired()])

    submit = SubmitField('Create Tournament')

    def __init__(self, *args, **kwargs):
        """Initialize form with default values"""
        super(TournamentCreationForm, self).__init__(*args, **kwargs)

        # Set defaults only if form is not being submitted (i.e., initial load)
        if not self.is_submitted():
            # Get current time in Eastern timezone
            eastern = pytz.timezone('America/New_York')
            now_eastern = datetime.now(eastern)

            # Registration deadline: 2 days from now at 3 AM Eastern
            deadline_date = (now_eastern + timedelta(days=2)).date()
            deadline_time = time_type(3, 0)  # 3:00 AM

            self.registration_deadline_date.data = deadline_date
            self.registration_deadline_time.data = deadline_time

    def _combine_datetime(self, date_obj, time_obj):
        """Combine date and time into Unix timestamp (Eastern timezone)"""
        # Create naive datetime
        dt = datetime.combine(date_obj, time_obj)
        # Localize to Eastern timezone
        eastern = pytz.timezone('America/New_York')
        dt_eastern = eastern.localize(dt)
        # Convert to Unix timestamp
        return int(dt_eastern.timestamp())

    def get_registration_deadline_timestamp(self):
        """Get registration deadline as Unix timestamp"""
        return self._combine_datetime(self.registration_deadline_date.data,
                                      self.registration_deadline_time.data)
