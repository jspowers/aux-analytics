"""YouTube API service for fetching video metadata"""
from googleapiclient.discovery import build
import re


class YouTubeService:
    """Service for interacting with YouTube Data API"""

    def __init__(self, api_key):
        """Initialize YouTube client with API key"""
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def extract_video_id(self, url):
        """Extract video ID from YouTube URL

        Examples:
        - https://www.youtube.com/watch?v=dQw4w9WgXcQ
        - https://youtu.be/dQw4w9WgXcQ
        - https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=share
        """
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'youtu\.be\/([0-9A-Za-z_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_video_metadata(self, url):
        """Fetch video metadata from YouTube URL

        Args:
            url: YouTube video URL

        Returns:
            dict: Video metadata including title, channel, thumbnail, etc.

        Raises:
            ValueError: If URL is invalid or video not found
        """
        video_id = self.extract_video_id(url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        try:
            request = self.youtube.videos().list(
                part='snippet,contentDetails',
                id=video_id
            )
            response = request.execute()
        except Exception as e:
            raise ValueError(f"Could not fetch video from YouTube: {str(e)}")

        if not response['items']:
            raise ValueError("Video not found on YouTube")

        video = response['items'][0]
        snippet = video['snippet']

        # Parse ISO 8601 duration (PT4M13S -> 253 seconds)
        duration = self._parse_duration(video['contentDetails']['duration'])

        return {
            'title': snippet['title'],
            'artist': snippet['channelTitle'],  # Use channel name as artist
            'album': None,  # YouTube doesn't have album concept
            'duration_seconds': duration,
            'thumbnail_url': snippet['thumbnails']['high']['url'] if 'high' in snippet['thumbnails'] else None,
            'youtube_video_id': video_id,
            'youtube_url': url
        }

    def _parse_duration(self, duration_str):
        """Convert ISO 8601 duration to seconds

        Examples:
        - PT4M13S -> 253 seconds (4 * 60 + 13)
        - PT1H2M3S -> 3723 seconds (1 * 3600 + 2 * 60 + 3)
        - PT30S -> 30 seconds
        """
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
        if not match:
            return 0

        hours, minutes, seconds = match.groups()
        return int(hours or 0) * 3600 + int(minutes or 0) * 60 + int(seconds or 0)
