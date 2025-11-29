"""Tournament forms"""
from flask_wtf import FlaskForm
from wtforms import StringField, URLField, RadioField, SubmitField, TextAreaField, DateField, TimeField
from wtforms.validators import DataRequired, URL, Optional, Length, ValidationError
from datetime import datetime, time as time_type
import time


class SongSubmissionForm(FlaskForm):
    """Song submission form for tournaments"""
    submission_method = RadioField('How would you like to submit?',
        choices=[
            ('manual', 'Enter song details manually'),
            ('spotify', 'Paste Spotify URL'),
            ('youtube', 'Paste YouTube URL')
        ],
        default='manual',
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

        if method == 'manual':
            if not self.title.data or not self.artist.data:
                self.title.errors.append('Title and Artist are required for manual entry')
                return False
        elif method == 'spotify':
            if not self.spotify_url.data:
                self.spotify_url.errors.append('Spotify URL is required')
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

    # Registration deadline
    registration_deadline_date = DateField('Registration Deadline Date', validators=[DataRequired()])
    registration_deadline_time = TimeField('Registration Deadline Time', validators=[DataRequired()])

    # Voting start
    voting_start_date = DateField('Voting Start Date', validators=[DataRequired()])
    voting_start_time = TimeField('Voting Start Time', validators=[DataRequired()])

    # Voting end
    voting_end_date = DateField('Voting End Date', validators=[DataRequired()])
    voting_end_time = TimeField('Voting End Time', validators=[DataRequired()])

    submit = SubmitField('Create Tournament')

    def validate(self, extra_validators=None):
        """Custom validation for date ordering"""
        if not super().validate(extra_validators):
            return False

        # Combine date + time fields into timestamps
        try:
            reg_deadline = self._combine_datetime(self.registration_deadline_date.data,
                                                  self.registration_deadline_time.data)
            voting_start = self._combine_datetime(self.voting_start_date.data,
                                                  self.voting_start_time.data)
            voting_end = self._combine_datetime(self.voting_end_date.data,
                                               self.voting_end_time.data)
        except Exception as e:
            self.registration_deadline_date.errors.append('Invalid date/time values')
            return False

        # Validate: voting_start >= registration_deadline
        if voting_start < reg_deadline:
            self.voting_start_date.errors.append('Voting start must be after registration deadline')
            return False

        # Validate: voting_end > voting_start
        if voting_end <= voting_start:
            self.voting_end_date.errors.append('Voting end must be after voting start')
            return False

        return True

    def _combine_datetime(self, date_obj, time_obj):
        """Combine date and time into Unix timestamp"""
        dt = datetime.combine(date_obj, time_obj)
        return int(time.mktime(dt.timetuple()))

    def get_registration_deadline_timestamp(self):
        """Get registration deadline as Unix timestamp"""
        return self._combine_datetime(self.registration_deadline_date.data,
                                      self.registration_deadline_time.data)

    def get_voting_start_timestamp(self):
        """Get voting start as Unix timestamp"""
        return self._combine_datetime(self.voting_start_date.data,
                                      self.voting_start_time.data)

    def get_voting_end_timestamp(self):
        """Get voting end as Unix timestamp"""
        return self._combine_datetime(self.voting_end_date.data,
                                      self.voting_end_time.data)
