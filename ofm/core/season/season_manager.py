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

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..db.models import (
    Competition,
    CompetitionType,
    Fixture,
    League,
    LeagueSeason,
    LeagueTableEntry,
)
from .fixture_generator import FixtureGenerator


class SeasonManager:
    """Manages season progression, fixtures, and league tables"""

    def __init__(self, session: Session):
        self.session = session
        self.current_date = datetime.now()

    def create_season(
        self, 
        league: League, 
        teams: List[UUID], 
        season_year: int,
        start_date: datetime,
        end_date: datetime
    ) -> LeagueSeason:
        """
        Create a new season for a league
        
        Args:
            league: League object
            teams: List of team IDs participating
            season_year: Year of the season (e.g., 2024)
            start_date: Season start date
            end_date: Season end date
            
        Returns:
            Created LeagueSeason object
        """
        # Create competition
        competition = Competition(
            name=f"{league.name} {season_year}/{season_year + 1}",
            short_name=league.name[:20],
            type=CompetitionType.LEAGUE,
            country=league.country,
            season=season_year,
            start_date=start_date,
            end_date=end_date,
            active=True
        )
        self.session.add(competition)
        self.session.flush()  # Get competition.id
        
        # Create league season
        league_season = LeagueSeason(
            league_id=league.id,
            competition_id=competition.id,
            team_ids=teams
        )
        self.session.add(league_season)
        self.session.flush()
        
        # Create league table entries
        for team_id in teams:
            entry = LeagueTableEntry(
                league_season_id=league_season.id,
                team_id=team_id,
                position=0  # Will be updated after sorting
            )
            self.session.add(entry)
        
        # Generate fixtures
        fixture_gen = FixtureGenerator(
            start_date=start_date,
            match_days=[5, 6],  # Friday and Saturday
            winter_break=(
                datetime(season_year, 12, 20),
                datetime(season_year + 1, 1, 3)
            ) if league.country in ["ENG", "GER", "ESP"] else None
        )
        
        fixtures = fixture_gen.generate_fixtures(
            teams=teams,
            competition_id=competition.id,
            double_round_robin=True
        )
        
        # Add kick-off times
        fixture_gen.randomize_fixture_times(
            fixtures,
            kick_off_times=[(15, 0), (17, 30), (20, 0)]  # 3pm, 5:30pm, 8pm
        )
        
        for fixture in fixtures:
            self.session.add(fixture)
        
        self.session.commit()
        return league_season

    def update_table_after_fixture(self, fixture: Fixture) -> None:
        """Update league table entries after a fixture is completed"""
        if not fixture.is_completed:
            return
        
        # Find the league season for this fixture
        competition = self.session.query(Competition).get(fixture.competition_id)
        league_season = (
            self.session.query(LeagueSeason)
            .filter_by(competition_id=competition.id)
            .first()
        )
        
        if not league_season:
            return
        
        # Get table entries for both teams
        home_entry = (
            self.session.query(LeagueTableEntry)
            .filter_by(league_season_id=league_season.id, team_id=fixture.home_team_id)
            .first()
        )
        away_entry = (
            self.session.query(LeagueTableEntry)
            .filter_by(league_season_id=league_season.id, team_id=fixture.away_team_id)
            .first()
        )
        
        # Determine result
        if fixture.home_score > fixture.away_score:
            home_result, away_result = "W", "L"
        elif fixture.home_score < fixture.away_score:
            home_result, away_result = "L", "W"
        else:
            home_result, away_result = "D", "D"
        
        # Update entries
        home_entry.update_after_match(fixture.home_score, fixture.away_score, home_result)
        away_entry.update_after_match(fixture.away_score, fixture.home_score, away_result)
        
        # Update positions
        self._update_table_positions(league_season)
        
        self.session.commit()

    def _update_table_positions(self, league_season: LeagueSeason) -> None:
        """Update positions in league table based on points and goal difference"""
        entries = (
            self.session.query(LeagueTableEntry)
            .filter_by(league_season_id=league_season.id)
            .all()
        )
        
        # Sort by points (desc), goal difference (desc), goals for (desc)
        entries.sort(
            key=lambda e: (e.points, e.goal_difference, e.goals_for),
            reverse=True
        )
        
        # Update positions
        for i, entry in enumerate(entries, 1):
            entry.position = i

    def get_next_fixtures(
        self, 
        days_ahead: int = 7,
        team_id: Optional[UUID] = None
    ) -> List[Fixture]:
        """Get upcoming fixtures"""
        query = self.session.query(Fixture).filter(
            Fixture.match_date >= self.current_date,
            Fixture.match_date <= self.current_date + timedelta(days=days_ahead)
        )
        
        if team_id:
            query = query.filter(
                (Fixture.home_team_id == team_id) | (Fixture.away_team_id == team_id)
            )
        
        return query.order_by(Fixture.match_date).all()

    def advance_date(self, days: int = 1) -> None:
        """Advance the current date"""
        self.current_date += timedelta(days=days)

    def get_league_table(self, league_season_id: int) -> List[LeagueTableEntry]:
        """Get sorted league table"""
        return (
            self.session.query(LeagueTableEntry)
            .filter_by(league_season_id=league_season_id)
            .order_by(LeagueTableEntry.position)
            .all()
        )