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

from dataclasses import dataclass
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from ..db.models import League, LeagueSeason, LeagueTableEntry


@dataclass
class PromotionRelegationResult:
    """Result of promotion/relegation calculation"""

    league_id: int
    promoted_teams: List[str]  # Team IDs
    relegated_teams: List[str]  # Team IDs
    playoff_teams: List[str]  # Team IDs for promotion playoffs


class PromotionRelegationManager:
    """Manages promotion and relegation between leagues"""

    def __init__(self, session: Session):
        self.session = session

    def calculate_promotion_relegation(
        self, league_season: LeagueSeason
    ) -> PromotionRelegationResult:
        """Calculate which teams are promoted/relegated from a league"""
        league = league_season.league

        # Get final league table
        table = (
            self.session.query(LeagueTableEntry)
            .filter_by(league_season_id=league_season.id)
            .order_by(LeagueTableEntry.position)
            .all()
        )

        promoted_teams = []
        relegated_teams = []
        playoff_teams = []

        # Determine promoted teams
        if league.promotion_places > 0:
            promoted_teams = [
                entry.team_id for entry in table[: league.promotion_places]
            ]

        # Determine playoff teams
        if league.playoff_places > 0:
            playoff_start = league.promotion_places
            playoff_end = playoff_start + league.playoff_places
            playoff_teams = [
                entry.team_id for entry in table[playoff_start:playoff_end]
            ]

        # Determine relegated teams
        if league.relegation_places > 0:
            relegated_teams = [
                entry.team_id for entry in table[-league.relegation_places :]
            ]

        return PromotionRelegationResult(
            league_id=league.id,
            promoted_teams=promoted_teams,
            relegated_teams=relegated_teams,
            playoff_teams=playoff_teams,
        )

    def get_league_changes_summary(
        self, season_year: int
    ) -> List[Tuple[League, PromotionRelegationResult]]:
        """Get promotion/relegation summary for all leagues in a season"""
        results = []

        # Get all leagues with completed seasons
        league_seasons = (
            self.session.query(LeagueSeason)
            .join(LeagueSeason.competition)
            .filter_by(season=season_year)
            .all()
        )

        for league_season in league_seasons:
            # Check if season is complete
            if self._is_season_complete(league_season):
                result = self.calculate_promotion_relegation(league_season)
                results.append((league_season.league, result))

        return results

    def apply_promotion_relegation(
        self, upper_league: League, lower_league: League, season_year: int
    ) -> Tuple[List[str], List[str]]:
        """
        Apply promotion/relegation between two leagues

        Returns:
            Tuple of (teams_going_up, teams_going_down)
        """
        # Get league seasons
        upper_season = self._get_league_season(upper_league, season_year)
        lower_season = self._get_league_season(lower_league, season_year)

        if not upper_season or not lower_season:
            return [], []

        # Calculate promotion/relegation
        upper_result = self.calculate_promotion_relegation(upper_season)
        lower_result = self.calculate_promotion_relegation(lower_season)

        # Teams going up from lower league
        teams_going_up = lower_result.promoted_teams

        # Teams going down from upper league
        teams_going_down = upper_result.relegated_teams

        # Validate the exchange
        if len(teams_going_up) != len(teams_going_down):
            # Handle mismatch - this might need adjustment based on league rules
            min_teams = min(len(teams_going_up), len(teams_going_down))
            teams_going_up = teams_going_up[:min_teams]
            teams_going_down = teams_going_down[:min_teams]

        return teams_going_up, teams_going_down

    def create_new_season_with_changes(
        self,
        league: League,
        old_season: LeagueSeason,
        teams_in: List[str],
        teams_out: List[str],
    ) -> List[UUID]:
        """
        Create team list for new season with promotion/relegation applied

        Args:
            league: The league
            old_season: Previous season
            teams_in: Teams coming into the league (promoted)
            teams_out: Teams leaving the league (relegated)

        Returns:
            New list of team IDs for the next season
        """
        # Get current teams
        current_teams = [str(team_id) for team_id in old_season.team_ids]

        # Remove relegated teams
        new_teams = [team for team in current_teams if team not in teams_out]

        # Add promoted teams
        new_teams.extend(teams_in)

        # Convert back to UUIDs
        return [UUID(team_id) for team_id in new_teams]

    def handle_playoffs(
        self, playoff_teams: List[str], num_promotion_spots: int
    ) -> List[str]:
        """
        Handle promotion playoffs

        This is a placeholder for playoff logic.
        In a real implementation, this would involve:
        - Creating playoff fixtures
        - Simulating playoff matches
        - Determining winners

        For now, just return the first N teams
        """
        return playoff_teams[:num_promotion_spots]

    def _is_season_complete(self, league_season: LeagueSeason) -> bool:
        """Check if all matches in a league season are complete"""
        from ..db.models import Fixture, FixtureStatus

        incomplete_count = (
            self.session.query(Fixture)
            .filter_by(competition_id=league_season.competition_id)
            .filter(Fixture.status != FixtureStatus.COMPLETED)
            .count()
        )

        return incomplete_count == 0

    def _get_league_season(
        self, league: League, season_year: int
    ) -> Optional[LeagueSeason]:
        """Get league season for a specific year"""
        return (
            self.session.query(LeagueSeason)
            .join(LeagueSeason.competition)
            .filter(
                LeagueSeason.league_id == league.id,
                LeagueSeason.competition.has(season=season_year),
            )
            .first()
        )

    def get_historical_movement(
        self, team_id: str, num_seasons: int = 5
    ) -> List[Tuple[int, int, int]]:
        """
        Get team's historical league movement

        Returns:
            List of (season_year, league_level, final_position)
        """
        history = []

        # Query all league table entries for this team
        entries = (
            self.session.query(LeagueTableEntry, LeagueSeason)
            .join(LeagueTableEntry.league_season)
            .filter(LeagueTableEntry.team_id == team_id)
            .all()
        )

        for entry, league_season in entries:
            season_year = league_season.competition.season
            league_level = league_season.league.level
            final_position = entry.position

            history.append((season_year, league_level, final_position))

        # Sort by season year descending and limit
        history.sort(key=lambda x: x[0], reverse=True)
        return history[:num_seasons]
