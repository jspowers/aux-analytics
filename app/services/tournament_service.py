"""Tournament service for managing tournament lifecycle"""
import math
from app.models import Round, Tournament, Song, Matchup
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

    @staticmethod
    def seed_songs(tournament):
        """
        Seed songs for bracket based on popularity, then submission order.

        Args:
            tournament: Tournament object

        Returns:
            list: Seeded Song objects in order (highest seed first)
        """
        songs = tournament.songs.all()

        # Sort by popularity (descending, nulls last), then by created_at (ascending)
        # Songs with popularity get higher seeds, ties broken by submission order
        seeded_songs = sorted(
            songs,
            key=lambda s: (
                s.popularity is not None,  # Songs with popularity come first
                s.popularity if s.popularity is not None else 0,  # Higher popularity = higher seed
                -s.created_at  # Earlier submission = higher seed (negative for ascending)
            ),
            reverse=True
        )

        return seeded_songs

    @staticmethod
    def generate_matchups(tournament, seeded_songs):
        """
        Generate all matchups for the tournament bracket.

        Creates matchups for all rounds, handles byes for top seeds in non-power-of-2 brackets,
        and links matchups via next_matchup_id for progression.

        Args:
            tournament: Tournament object
            seeded_songs: List of Song objects in seeded order

        Returns:
            dict: {
                'round_1_matchups': List of Matchup objects for Round 1,
                'total_matchups': Total number of matchups created,
                'num_byes': Number of bye matchups (top seeds skip Round 1)
            }
        """
        song_count = len(seeded_songs)
        if song_count < 2:
            return {'round_1_matchups': [], 'total_matchups': 0, 'num_byes': 0}

        # Get rounds (should already exist from generate_rounds)
        rounds = Round.query.filter_by(tournament_id=tournament.id).order_by(Round.round_number).all()
        if not rounds:
            rounds = TournamentService.generate_rounds(tournament)

        # Calculate bracket size (next power of 2)
        bracket_size = 2 ** math.ceil(math.log2(song_count))
        num_byes = bracket_size - song_count

        # Round 1: Create matchups for non-bye songs
        # Top seeds get byes, remaining songs battle in Round 1
        round_1_matchups = []
        songs_in_round_1 = seeded_songs[num_byes:]  # Skip top N seeds

        # Pair songs: highest remaining seed vs lowest seed
        num_round_1_matchups = len(songs_in_round_1) // 2
        for i in range(num_round_1_matchups):
            high_seed_song = songs_in_round_1[i]
            low_seed_song = songs_in_round_1[-(i + 1)]

            matchup = Matchup(
                tournament_id=tournament.id,
                round_id=rounds[0].id,
                song1_id=high_seed_song.id,
                song2_id=low_seed_song.id,
                status='pending'
            )
            db.session.add(matchup)
            round_1_matchups.append(matchup)

        db.session.flush()  # Get IDs for round 1 matchups

        # Create placeholder matchups for subsequent rounds
        # We need to link them via next_matchup_id
        all_matchups_by_round = {1: round_1_matchups}

        for round_idx in range(1, len(rounds)):
            round_num = round_idx + 1
            prev_round_matchups = all_matchups_by_round[round_num - 1]

            # Number of matchups in this round = half of previous round matchups + byes advancing
            if round_num == 2:
                # Round 2: Include bye songs advancing
                num_matchups_this_round = (len(prev_round_matchups) + num_byes) // 2
            else:
                num_matchups_this_round = len(prev_round_matchups) // 2

            this_round_matchups = []
            for i in range(num_matchups_this_round):
                matchup = Matchup(
                    tournament_id=tournament.id,
                    round_id=rounds[round_idx].id,
                    status='pending'
                )
                db.session.add(matchup)
                this_round_matchups.append(matchup)

            db.session.flush()  # Get IDs for this round's matchups

            # Link previous round matchups to this round
            if round_num == 2:
                # Special case: Round 1 winners AND bye songs advance to Round 2
                # First, link bye songs (top seeds) to Round 2 matchups
                bye_songs = seeded_songs[:num_byes]

                # Pair byes into Round 2 matchups (high seed vs low seed among byes)
                for i in range(len(bye_songs) // 2):
                    round_2_matchup = this_round_matchups[i]
                    round_2_matchup.song1_id = bye_songs[i].id
                    round_2_matchup.song2_id = bye_songs[-(i + 1)].id

                # Link Round 1 matchups to remaining Round 2 slots
                offset = len(bye_songs) // 2
                for i, prev_matchup in enumerate(prev_round_matchups):
                    next_matchup_idx = offset + i // 2
                    prev_matchup.next_matchup_id = this_round_matchups[next_matchup_idx].id
            else:
                # Normal case: pair previous round matchups into next round
                for i, prev_matchup in enumerate(prev_round_matchups):
                    next_matchup_idx = i // 2
                    prev_matchup.next_matchup_id = this_round_matchups[next_matchup_idx].id

            all_matchups_by_round[round_num] = this_round_matchups

        db.session.commit()

        total_matchups = sum(len(matchups) for matchups in all_matchups_by_round.values())

        return {
            'round_1_matchups': round_1_matchups,
            'total_matchups': total_matchups,
            'num_byes': num_byes
        }

    @staticmethod
    def advance_round(tournament, current_round):
        """
        Advance winners from current round to next round.

        Args:
            tournament: Tournament object
            current_round: Round object to advance from

        Returns:
            dict: Information about advancement
        """
        import time

        # Mark current round as completed
        current_round.status = 'completed'
        current_round.end_date = int(time.time())  # Set actual end time

        # Get all matchups from current round
        matchups = Matchup.query.filter_by(round_id=current_round.id).all()

        # Determine winners and advance them
        winners_advanced = 0
        for matchup in matchups:
            winner = matchup.get_winner()
            if winner:
                # Set the winner in the matchup
                matchup.winner_song_id = winner.id
                matchup.status = 'completed'

                # Advance winner to next matchup if it exists
                if matchup.next_matchup_id:
                    next_matchup = Matchup.query.get(matchup.next_matchup_id)
                    if next_matchup:
                        # Place winner in next matchup
                        if not next_matchup.song1_id:
                            next_matchup.song1_id = winner.id
                            winners_advanced += 1
                        elif not next_matchup.song2_id:
                            next_matchup.song2_id = winner.id
                            winners_advanced += 1

        # Check if there's a next round
        next_round = Round.query.filter_by(
            tournament_id=tournament.id,
            round_number=current_round.round_number + 1
        ).first()

        if next_round:
            # Activate next round
            next_round.status = 'active'
            next_round.start_date = int(time.time())

            # Update tournament status
            tournament.status = f'voting_round_{next_round.round_number}'

            db.session.commit()

            return {
                'winners_advanced': winners_advanced,
                'next_round': next_round.name,
                'tournament_completed': False
            }
        else:
            # Tournament is complete
            tournament.status = 'completed'
            db.session.commit()

            # Get the final winner
            final_matchup = matchups[0] if matchups else None
            final_winner = final_matchup.get_winner() if final_matchup else None

            return {
                'winners_advanced': 0,
                'next_round': None,
                'tournament_completed': True,
                'final_winner': final_winner
            }
