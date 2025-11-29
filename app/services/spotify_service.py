"""Spotify API service for fetching song metadata"""
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re


class SpotifyService:
    """Service for interacting with Spotify API"""

    def __init__(self, client_id, client_secret):
        """Initialize Spotify client with credentials"""
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        ))

    def extract_track_id(self, url):
        """Extract track ID from Spotify URL

        Examples:
        - https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT
        - https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT?si=xxx
        """
        match = re.search(r'track/([a-zA-Z0-9]+)', url)
        return match.group(1) if match else None

    def get_track_metadata(self, url):
        """Fetch song metadata from Spotify URL

        Args:
            url: Spotify track URL

        Returns:
            dict: Song metadata including title, artist, album, etc.

        Raises:
            ValueError: If URL is invalid or track not found
        """
        track_id = self.extract_track_id(url)
        if not track_id:
            raise ValueError("Invalid Spotify URL")

        try:
            track = self.sp.track(track_id)
        except Exception as e:
            raise ValueError(f"Could not fetch track from Spotify: {str(e)}")

        return {
            'title': track['name'],
            'artist': ', '.join([artist['name'] for artist in track['artists']]),
            'album': track['album']['name'],
            'duration_seconds': track['duration_ms'] // 1000,
            'thumbnail_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'spotify_track_id': track_id,
            'spotify_url': url
        }
