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
        Seed songs for bracket based on popularity (LOWER = better).
        Assigns seed_number to each song for permanent storage.

        Args:
            tournament: Tournament object

        Returns:
            list: Seeded Song objects in order (best seed first)
        """
        songs = tournament.songs.all()

        # Normalize popularity: NULL becomes 100 (worst popularity)
        for song in songs:
            if song.popularity is None:
                song.popularity = 100

        # Sort by popularity (ASCENDING - lower number is better), then submission order
        # Lower popularity number = better seed = more likely to get bye
        seeded_songs = sorted(
            songs,
            key=lambda s: (
                s.popularity,  # Lower popularity number = better seed
                s.created_at   # Earlier submission = tiebreaker (better seed)
            )
        )

        # Assign seed numbers (1 = best seed, gets bye if available)
        for idx, song in enumerate(seeded_songs):
            song.seed_number = idx + 1

        db.session.commit()
        return seeded_songs

    @staticmethod
    def generate_matchups(tournament, seeded_songs):
        """
        Generate ONLY Round 1 matchups for the tournament bracket.
        Future rounds are built on-demand as rounds are finalized.

        Args:
            tournament: Tournament object
            seeded_songs: List of Song objects in seeded order (best seed first)

        Returns:
            dict: {
                'round_1_matchups': List of Matchup objects for Round 1,
                'total_matchups': Total number of matchups created (just Round 1),
                'num_byes': Number of byes (best seeds skip Round 1)
            }
        """
        song_count = len(seeded_songs)
        if song_count < 2:
            return {'round_1_matchups': [], 'total_matchups': 0, 'num_byes': 0}

        # Get Round 1 (should already exist from generate_rounds)
        round_1 = Round.query.filter_by(
            tournament_id=tournament.id,
            round_number=1
        ).first()

        if not round_1:
            raise ValueError("Round 1 does not exist. Call generate_rounds() first.")

        # Calculate bracket size (next power of 2)
        bracket_size = 2 ** math.ceil(math.log2(song_count))
        num_byes = bracket_size - song_count

        # Round 1: Create matchups for non-bye songs
        # Best seeds (lowest seed_numbers) get byes, remaining songs compete in Round 1
        round_1_matchups = []
        songs_in_round_1 = seeded_songs[num_byes:]  # Skip best N seeds

        # Pair songs: best remaining seed vs worst seed
        num_round_1_matchups = len(songs_in_round_1) // 2
        for i in range(num_round_1_matchups):
            high_seed_song = songs_in_round_1[i]
            low_seed_song = songs_in_round_1[-(i + 1)]

            matchup = Matchup(
                tournament_id=tournament.id,
                round_id=round_1.id,
                position_in_round=i,
                song1_id=high_seed_song.id,
                song2_id=low_seed_song.id,
                status='pending'
            )
            db.session.add(matchup)
            round_1_matchups.append(matchup)

        db.session.commit()

        return {
            'round_1_matchups': round_1_matchups,
            'total_matchups': len(round_1_matchups),
            'num_byes': num_byes
        }

    @staticmethod
    def build_next_round_matchups(tournament, completed_round):
        """
        Build matchups for the round following the completed round.
        Uses winners from completed round to populate next round matchups.

        Args:
            tournament: Tournament object
            completed_round: Round object that was just completed

        Returns:
            list: Created Matchup objects, or None if tournament is complete
        """
        # Get next round
        next_round = Round.query.filter_by(
            tournament_id=tournament.id,
            round_number=completed_round.round_number + 1
        ).first()

        if not next_round:
            return None  # Tournament complete

        # Get winners from completed round
        completed_matchups = Matchup.query.filter_by(
            round_id=completed_round.id
        ).order_by(Matchup.position_in_round).all()

        winners = []
        for matchup in completed_matchups:
            winner = matchup.get_winner()
            if winner:
                winners.append(winner)

        # Special case: Round 1 → Round 2 (handle byes)
        if completed_round.round_number == 1:
            # Get bye songs by seed_number (best seeds got byes)
            num_songs = tournament.songs.count()
            bracket_size = 2 ** math.ceil(math.log2(num_songs))
            num_byes = bracket_size - num_songs

            bye_songs = Song.query.filter_by(tournament_id=tournament.id).filter(
                Song.seed_number <= num_byes
            ).order_by(Song.seed_number).all()

            return TournamentService._build_round_2_with_byes(
                tournament, next_round, winners, bye_songs
            )

        # Normal case: pair winners by seed
        matchups_created = []
        sorted_winners = sorted(winners, key=lambda s: s.seed_number)

        for i in range(0, len(sorted_winners), 2):
            if i + 1 < len(sorted_winners):
                matchup = Matchup(
                    tournament_id=tournament.id,
                    round_id=next_round.id,
                    position_in_round=i // 2,
                    song1_id=sorted_winners[i].id,
                    song2_id=sorted_winners[i + 1].id,
                    status='pending'
                )
                db.session.add(matchup)
                matchups_created.append(matchup)

        db.session.commit()
        return matchups_created

    @staticmethod
    def _build_round_2_with_byes(tournament, next_round, round_1_winners, bye_songs):
        """
        Build Round 2 matchups with bye songs and Round 1 winners.
        Pairs best seeds with worst seeds for balanced matchups.

        Args:
            tournament: Tournament object
            next_round: Round 2 object
            round_1_winners: List of Song objects that won Round 1
            bye_songs: List of Song objects that got byes

        Returns:
            list: Created Matchup objects
        """
        matchups_created = []

        # Sort both lists by seed_number (ascending - best seed first)
        sorted_byes = sorted(bye_songs, key=lambda s: s.seed_number)
        sorted_winners = sorted(round_1_winners, key=lambda s: s.seed_number)

        # Combine: byes first (they have better seeds), then winners
        all_advancing = sorted_byes + sorted_winners

        # Pair: best vs worst, 2nd best vs 2nd worst, etc.
        for i in range(len(all_advancing) // 2):
            high_seed = all_advancing[i]
            low_seed = all_advancing[-(i + 1)]

            matchup = Matchup(
                tournament_id=tournament.id,
                round_id=next_round.id,
                position_in_round=i,
                song1_id=high_seed.id,
                song2_id=low_seed.id,
                status='pending'
            )
            db.session.add(matchup)
            matchups_created.append(matchup)

        db.session.commit()
        return matchups_created
