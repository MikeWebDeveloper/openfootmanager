#      Openfoot Manager - A free and open source soccer management simulation
#      Copyright (C) 2020-2025  Pedrenrique G. Guimarães
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

import gzip
import json
from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from sqlalchemy.orm import Session

from ..db.models import Competition, Fixture, League, LeagueSeason, LeagueTableEntry


class SaveSerializer:
    """Handles serialization and deserialization of game state"""

    SAVE_VERSION = 1

    def __init__(self, session: Session):
        self.session = session

    def serialize_game_state(self, game_state: Dict[str, Any]) -> str:
        """
        Serialize the entire game state to a compressed JSON string

        Args:
            game_state: Dictionary containing all game state data

        Returns:
            Compressed JSON string
        """
        # Convert special types to serializable format
        serializable_state = self._prepare_for_serialization(game_state)

        # Convert to JSON
        json_data = json.dumps(serializable_state, separators=(",", ":"))

        # Compress the data
        compressed = gzip.compress(json_data.encode("utf-8"))

        # Return as base64 string for storage
        import base64

        return base64.b64encode(compressed).decode("utf-8")

    def deserialize_game_state(self, compressed_data: str) -> Dict[str, Any]:
        """
        Deserialize a compressed game state string back to a dictionary

        Args:
            compressed_data: Compressed and encoded game state string

        Returns:
            Game state dictionary
        """
        import base64

        # Decode from base64
        compressed = base64.b64decode(compressed_data.encode("utf-8"))

        # Decompress
        json_data = gzip.decompress(compressed).decode("utf-8")

        # Parse JSON
        game_state = json.loads(json_data)

        # Convert back special types
        return self._restore_from_serialization(game_state)

    def extract_current_game_state(self) -> Dict[str, Any]:
        """Extract the current game state from the database"""
        state = {
            "save_version": self.SAVE_VERSION,
            "saved_at": datetime.utcnow().isoformat(),
            "competitions": self._serialize_competitions(),
            "leagues": self._serialize_leagues(),
            "league_seasons": self._serialize_league_seasons(),
            "fixtures": self._serialize_fixtures(),
            "table_entries": self._serialize_table_entries(),
        }

        return state

    def restore_game_state(self, game_state: Dict[str, Any]) -> None:
        """Restore the game state to the database"""
        # Check save version compatibility
        save_version = game_state.get("save_version", 0)
        if save_version > self.SAVE_VERSION:
            raise ValueError(
                f"Save file version {save_version} is newer than supported version {self.SAVE_VERSION}"
            )

        # Clear existing data (in a real game, this would be more sophisticated)
        # For now, we'll assume we're loading into a fresh database

        # Restore data in correct order due to foreign key constraints
        self._restore_leagues(game_state.get("leagues", []))
        self._restore_competitions(game_state.get("competitions", []))
        self._restore_league_seasons(game_state.get("league_seasons", []))
        self._restore_fixtures(game_state.get("fixtures", []))
        self._restore_table_entries(game_state.get("table_entries", []))

        self.session.commit()

    def _prepare_for_serialization(self, obj: Any) -> Any:
        """Convert non-JSON serializable types"""
        if isinstance(obj, (datetime,)):
            return obj.isoformat()
        elif isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: self._prepare_for_serialization(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._prepare_for_serialization(item) for item in obj]
        return obj

    def _restore_from_serialization(self, obj: Any) -> Any:
        """Restore special types from serialized format"""
        if isinstance(obj, str):
            # Try to parse as datetime
            try:
                return datetime.fromisoformat(obj)
            except ValueError:
                pass
        elif isinstance(obj, dict):
            return {k: self._restore_from_serialization(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._restore_from_serialization(item) for item in obj]
        return obj

    def _serialize_competitions(self) -> list:
        """Serialize all competitions"""
        competitions = self.session.query(Competition).all()
        return [
            {
                "id": comp.id,
                "name": comp.name,
                "short_name": comp.short_name,
                "type": comp.type.value,
                "country": comp.country,
                "season": comp.season,
                "start_date": comp.start_date.isoformat(),
                "end_date": comp.end_date.isoformat(),
                "active": comp.active,
            }
            for comp in competitions
        ]

    def _serialize_leagues(self) -> list:
        """Serialize all leagues"""
        leagues = self.session.query(League).all()
        return [
            {
                "id": league.id,
                "name": league.name,
                "country": league.country,
                "level": league.level,
                "num_teams": league.num_teams,
                "promotion_places": league.promotion_places,
                "playoff_places": league.playoff_places,
                "relegation_places": league.relegation_places,
                "league_above_id": league.league_above_id,
                "league_below_id": league.league_below_id,
            }
            for league in leagues
        ]

    def _serialize_league_seasons(self) -> list:
        """Serialize all league seasons"""
        seasons = self.session.query(LeagueSeason).all()
        return [
            {
                "id": season.id,
                "league_id": season.league_id,
                "competition_id": season.competition_id,
                "team_ids": [str(tid) for tid in season.team_ids],
            }
            for season in seasons
        ]

    def _serialize_fixtures(self) -> list:
        """Serialize all fixtures"""
        fixtures = self.session.query(Fixture).all()
        return [
            {
                "id": fixture.id,
                "competition_id": fixture.competition_id,
                "home_team_id": fixture.home_team_id,
                "away_team_id": fixture.away_team_id,
                "match_date": fixture.match_date.isoformat(),
                "match_week": fixture.match_week,
                "status": fixture.status.value,
                "home_score": fixture.home_score,
                "away_score": fixture.away_score,
            }
            for fixture in fixtures
        ]

    def _serialize_table_entries(self) -> list:
        """Serialize all league table entries"""
        entries = self.session.query(LeagueTableEntry).all()
        return [
            {
                "id": entry.id,
                "league_season_id": entry.league_season_id,
                "team_id": entry.team_id,
                "position": entry.position,
                "played": entry.played,
                "won": entry.won,
                "drawn": entry.drawn,
                "lost": entry.lost,
                "goals_for": entry.goals_for,
                "goals_against": entry.goals_against,
                "form": entry.form,
            }
            for entry in entries
        ]

    def _restore_leagues(self, leagues_data: list) -> None:
        """Restore leagues from serialized data"""
        for data in leagues_data:
            league = League(**data)
            self.session.add(league)
        self.session.flush()

    def _restore_competitions(self, competitions_data: list) -> None:
        """Restore competitions from serialized data"""
        from ..db.models import CompetitionType

        for data in competitions_data:
            # Convert string back to enum
            data["type"] = CompetitionType(data["type"])

            # Convert to datetime if needed
            if isinstance(data["start_date"], str):
                data["start_date"] = datetime.fromisoformat(data["start_date"])
            if isinstance(data["end_date"], str):
                data["end_date"] = datetime.fromisoformat(data["end_date"])

            competition = Competition(**data)
            self.session.add(competition)
        self.session.flush()

    def _restore_league_seasons(self, seasons_data: list) -> None:
        """Restore league seasons from serialized data"""
        for data in seasons_data:
            # Create season without team_ids first
            team_ids = data.pop("team_ids", [])
            season = LeagueSeason(**data, _team_ids_json="")

            # Set team_ids using the property
            season.team_ids = [UUID(tid) for tid in team_ids]

            self.session.add(season)
        self.session.flush()

    def _restore_fixtures(self, fixtures_data: list) -> None:
        """Restore fixtures from serialized data"""
        from ..db.models import FixtureStatus

        for data in fixtures_data:
            # Convert string back to enum and datetime
            data["status"] = FixtureStatus(data["status"])

            # Convert to datetime if needed
            if isinstance(data["match_date"], str):
                data["match_date"] = datetime.fromisoformat(data["match_date"])

            fixture = Fixture(**data)
            self.session.add(fixture)
        self.session.flush()

    def _restore_table_entries(self, entries_data: list) -> None:
        """Restore league table entries from serialized data"""
        for data in entries_data:
            entry = LeagueTableEntry(**data)
            self.session.add(entry)
        self.session.flush()
