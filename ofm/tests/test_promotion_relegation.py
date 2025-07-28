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

import uuid
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ofm.core.db.models import (
    Base,
    Competition,
    CompetitionType,
    Fixture,
    FixtureStatus,
    League,
    LeagueSeason,
    LeagueTableEntry,
)
from ofm.core.season import PromotionRelegationManager


@pytest.fixture
def db_session():
    """Create a test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_leagues(db_session):
    """Create sample league structure"""
    # Premier League
    premier_league = League(
        name="Premier League",
        country="ENG",
        level=1,
        num_teams=20,
        promotion_places=0,
        playoff_places=0,
        relegation_places=3,
    )

    # Championship
    championship = League(
        name="Championship",
        country="ENG",
        level=2,
        num_teams=24,
        promotion_places=2,
        playoff_places=4,
        relegation_places=3,
    )

    # League One
    league_one = League(
        name="League One",
        country="ENG",
        level=3,
        num_teams=24,
        promotion_places=2,
        playoff_places=4,
        relegation_places=4,
    )

    # Set up relationships
    premier_league.league_below_id = 2  # Will be championship.id
    championship.league_above_id = 1  # Will be premier_league.id
    championship.league_below_id = 3  # Will be league_one.id
    league_one.league_above_id = 2  # Will be championship.id

    db_session.add_all([premier_league, championship, league_one])
    db_session.commit()

    return premier_league, championship, league_one


@pytest.fixture
def completed_season(db_session, sample_leagues):
    """Create a completed Championship season"""
    premier_league, championship, league_one = sample_leagues

    # Create competition
    competition = Competition(
        name="Championship 2024/25",
        short_name="Championship",
        type=CompetitionType.LEAGUE,
        country="ENG",
        season=2024,
        start_date=datetime(2024, 8, 1),
        end_date=datetime(2025, 5, 31),
        active=True,
    )
    db_session.add(competition)
    db_session.flush()

    # Create league season
    league_season = LeagueSeason(
        league_id=championship.id, competition_id=competition.id, _team_ids_json=""
    )

    # Create 24 teams
    teams = [uuid.uuid4() for _ in range(24)]
    league_season.team_ids = teams
    db_session.add(league_season)
    db_session.flush()

    # Create table entries with varying points
    for i, team_id in enumerate(teams):
        # Top teams have more points
        if i < 2:  # Automatic promotion
            points_factor = 90 - (i * 3)
        elif i < 6:  # Playoff positions
            points_factor = 75 - (i * 2)
        elif i < 20:  # Mid-table
            points_factor = 50 - i
        else:  # Relegation zone
            points_factor = 30 - (i - 20) * 5

        entry = LeagueTableEntry(
            league_season_id=league_season.id,
            team_id=str(team_id),
            position=i + 1,
            played=46,
            won=int(points_factor / 3),
            drawn=points_factor % 10,
            lost=46 - (int(points_factor / 3) + points_factor % 10),
            goals_for=points_factor + 20,
            goals_against=100 - points_factor,
        )
        db_session.add(entry)

    # Mark all fixtures as completed
    for i in range(552):  # 24 teams * 23 opponents = 552 fixtures
        fixture = Fixture(
            competition_id=competition.id,
            home_team_id=str(uuid.uuid4()),
            away_team_id=str(uuid.uuid4()),
            match_date=datetime(2024, 8, 1),
            match_week=1,
            status=FixtureStatus.COMPLETED,
            home_score=1,
            away_score=0,
        )
        db_session.add(fixture)

    db_session.commit()
    return league_season


def test_calculate_promotion_relegation(db_session, completed_season):
    """Test basic promotion/relegation calculation"""
    manager = PromotionRelegationManager(db_session)
    result = manager.calculate_promotion_relegation(completed_season)

    assert (
        len(result.promoted_teams) == 2
    )  # Championship has 2 automatic promotion spots
    assert len(result.playoff_teams) == 4  # Championship has 4 playoff spots
    assert len(result.relegated_teams) == 3  # Championship has 3 relegation spots

    # Check that teams are from correct positions
    table = (
        db_session.query(LeagueTableEntry)
        .filter_by(league_season_id=completed_season.id)
        .order_by(LeagueTableEntry.position)
        .all()
    )

    # Promoted teams should be top 2
    assert result.promoted_teams[0] == table[0].team_id
    assert result.promoted_teams[1] == table[1].team_id

    # Playoff teams should be positions 3-6
    for i, team_id in enumerate(result.playoff_teams):
        assert team_id == table[i + 2].team_id

    # Relegated teams should be bottom 3
    assert result.relegated_teams[0] == table[-3].team_id
    assert result.relegated_teams[1] == table[-2].team_id
    assert result.relegated_teams[2] == table[-1].team_id


def test_apply_promotion_relegation(db_session, sample_leagues, completed_season):
    """Test applying promotion/relegation between leagues"""
    premier_league, championship, league_one = sample_leagues

    # Create a simple Premier League season
    pl_competition = Competition(
        name="Premier League 2024/25",
        short_name="PL",
        type=CompetitionType.LEAGUE,
        country="ENG",
        season=2024,
        start_date=datetime(2024, 8, 1),
        end_date=datetime(2025, 5, 31),
        active=True,
    )
    db_session.add(pl_competition)
    db_session.flush()

    pl_season = LeagueSeason(
        league_id=premier_league.id, competition_id=pl_competition.id, _team_ids_json=""
    )

    # Create 20 PL teams
    pl_teams = [uuid.uuid4() for _ in range(20)]
    pl_season.team_ids = pl_teams
    db_session.add(pl_season)
    db_session.flush()

    # Create table entries
    for i, team_id in enumerate(pl_teams):
        entry = LeagueTableEntry(
            league_season_id=pl_season.id,
            team_id=str(team_id),
            position=i + 1,
            played=38,
        )
        db_session.add(entry)

    # Mark PL fixtures as completed
    for i in range(380):
        fixture = Fixture(
            competition_id=pl_competition.id,
            home_team_id=str(uuid.uuid4()),
            away_team_id=str(uuid.uuid4()),
            match_date=datetime(2024, 8, 1),
            match_week=1,
            status=FixtureStatus.COMPLETED,
            home_score=1,
            away_score=0,
        )
        db_session.add(fixture)

    db_session.commit()

    # Apply promotion/relegation
    manager = PromotionRelegationManager(db_session)
    teams_up, teams_down = manager.apply_promotion_relegation(
        premier_league, championship, 2024
    )

    # Should have 2 teams going up from Championship
    assert len(teams_up) == 2

    # Should have 3 teams going down from Premier League
    # But since Championship only sends 2 up, we should match
    assert len(teams_down) == 2


def test_create_new_season_with_changes(db_session, completed_season):
    """Test creating new season with promoted/relegated teams"""
    manager = PromotionRelegationManager(db_session)

    # Get current teams
    old_teams = completed_season.team_ids

    # Simulate some teams to swap
    teams_in = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
    teams_out = [str(old_teams[-1]), str(old_teams[-2]), str(old_teams[-3])]

    new_teams = manager.create_new_season_with_changes(
        completed_season.league, completed_season, teams_in, teams_out
    )

    # Should have same number of teams
    assert len(new_teams) == 24

    # Should not contain relegated teams
    for team in teams_out:
        assert team not in [str(t) for t in new_teams]

    # Should contain promoted teams
    for team in teams_in:
        assert team in [str(t) for t in new_teams]


def test_handle_playoffs(db_session):
    """Test playoff handling"""
    manager = PromotionRelegationManager(db_session)

    playoff_teams = ["team1", "team2", "team3", "team4"]
    winners = manager.handle_playoffs(playoff_teams, 1)

    # Should return 1 winner (placeholder implementation)
    assert len(winners) == 1
    assert winners[0] in playoff_teams


def test_get_historical_movement(db_session, completed_season):
    """Test getting team's historical movement"""
    manager = PromotionRelegationManager(db_session)

    # Pick a team from the completed season
    team_id = str(completed_season.team_ids[0])

    history = manager.get_historical_movement(team_id, 5)

    # Should have one entry for our test season
    assert len(history) == 1
    assert history[0][0] == 2024  # Season year
    assert history[0][1] == 2  # Championship is level 2
    assert history[0][2] == 1  # First position
