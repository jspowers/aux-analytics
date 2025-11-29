"""Tournament service for managing tournament lifecycle"""
import math
from app.models import Round, Tournament
from app.extensions import db


class TournamentService:
    """Service for tournament operations"""

    @staticmethod
    def generate_rounds(tournament):
        """
        Auto-generate rounds for a tournament based on song count.
        Called when registration period ends.

        Args:
            tournament: Tournament object

        Returns:
            list: Created Round objects
        """
        song_count = tournament.songs.count()
        if song_count < 2:
            return []

        # Calculate rounds needed for single-elimination bracket
        num_rounds = tournament.get_num_rounds_needed()

        rounds = []
        for round_num in range(1, num_rounds + 1):
            round_name = TournamentService._get_round_name(round_num, num_rounds)

            round_obj = Round(
                tournament_id=tournament.id,
                round_number=round_num,
                name=round_name,
                status='pending'
            )
            db.session.add(round_obj)
            rounds.append(round_obj)

        db.session.commit()
        return rounds

    @staticmethod
    def _get_round_name(round_num, total_rounds):
        """
        Generate human-readable round names.

        Examples:
        - 4 rounds: Round of 16, Quarterfinals, Semifinals, Finals
        - 3 rounds: Round of 8, Semifinals, Finals
        - 2 rounds: Semifinals, Finals
        - 1 round: Finals
        """
        rounds_from_end = total_rounds - round_num

        if rounds_from_end == 0:
            return "Finals"
        elif rounds_from_end == 1:
            return "Semifinals"
        elif rounds_from_end == 2:
            return "Quarterfinals"
        else:
            # Calculate participants in this round
            participants = 2 ** (total_rounds - round_num + 1)
            return f"Round of {participants}"
