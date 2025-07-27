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

from ofm.core.db.models import Base, Fixture, FixtureStatus, League
from ofm.core.season import FixtureGenerator, SeasonManager


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
def sample_league(db_session):
    """Create a sample league"""
    league = League(
        name="Test Premier League",
        country="ENG",
        level=1,
        num_teams=20,
        promotion_places=0,
        playoff_places=0,
        relegation_places=3
    )
    db_session.add(league)
    db_session.commit()
    return league


@pytest.fixture
def sample_teams():
    """Generate sample team IDs"""
    return [uuid.uuid4() for _ in range(20)]


def test_fixture_generator_single_round_robin():
    """Test fixture generation for single round-robin"""
    teams = [uuid.uuid4() for _ in range(4)]
    generator = FixtureGenerator(
        start_date=datetime(2024, 8, 1),
        match_days=[5, 6]  # Friday, Saturday
    )

    fixtures = generator.generate_fixtures(teams, 1, double_round_robin=False)

    # Should have (n * (n-1)) / 2 fixtures for single round-robin
    assert len(fixtures) == 6

    # Each team should play exactly 3 matches
    team_match_count = {str(team): 0 for team in teams}
    for fixture in fixtures:
        team_match_count[fixture.home_team_id] += 1
        team_match_count[fixture.away_team_id] += 1

    for count in team_match_count.values():
        assert count == 3


def test_fixture_generator_double_round_robin():
    """Test fixture generation for double round-robin"""
    teams = [uuid.uuid4() for _ in range(4)]
    generator = FixtureGenerator(
        start_date=datetime(2024, 8, 1),
        match_days=[5, 6]
    )

    fixtures = generator.generate_fixtures(teams, 1, double_round_robin=True)

    # Should have n * (n-1) fixtures for double round-robin
    assert len(fixtures) == 12

    # Each team should play exactly 6 matches
    team_match_count = {str(team): 0 for team in teams}
    for fixture in fixtures:
        team_match_count[fixture.home_team_id] += 1
        team_match_count[fixture.away_team_id] += 1

    for count in team_match_count.values():
        assert count == 6

    # Each team should play home and away against each other
    for team1 in teams:
        for team2 in teams:
            if team1 != team2:
                home_fixtures = [f for f in fixtures if f.home_team_id == str(team1) and f.away_team_id == str(team2)]
                away_fixtures = [f for f in fixtures if f.home_team_id == str(team2) and f.away_team_id == str(team1)]
                assert len(home_fixtures) == 1
                assert len(away_fixtures) == 1


def test_fixture_generator_odd_teams():
    """Test fixture generation with odd number of teams"""
    teams = [uuid.uuid4() for _ in range(5)]
    generator = FixtureGenerator(
        start_date=datetime(2024, 8, 1),
        match_days=[6]  # Saturday only
    )

    fixtures = generator.generate_fixtures(teams, 1, double_round_robin=False)

    # With 5 teams, each round has 2 matches (one team sits out)
    # 5 rounds total, so 10 fixtures
    assert len(fixtures) == 10

    # Each team should play exactly 4 matches
    team_match_count = {str(team): 0 for team in teams}
    for fixture in fixtures:
        team_match_count[fixture.home_team_id] += 1
        team_match_count[fixture.away_team_id] += 1

    for count in team_match_count.values():
        assert count == 4


def test_season_manager_create_season(db_session, sample_league, sample_teams):
    """Test creating a new season"""
    manager = SeasonManager(db_session)

    league_season = manager.create_season(
        league=sample_league,
        teams=sample_teams,
        season_year=2024,
        start_date=datetime(2024, 8, 10),
        end_date=datetime(2025, 5, 25)
    )

    assert league_season is not None
    assert league_season.league_id == sample_league.id

    # Check fixtures were created
    fixtures = db_session.query(Fixture).all()
    assert len(fixtures) == 380  # 20 teams * 19 opponents * 2 (home/away)

    # Check all fixtures are scheduled
    for fixture in fixtures:
        assert fixture.status == FixtureStatus.SCHEDULED
        assert fixture.match_date >= datetime(2024, 8, 10)
        assert fixture.match_date <= datetime(2025, 5, 25)

    # Check league table entries were created
    assert len(league_season.table_entries) == 20
    for entry in league_season.table_entries:
        assert entry.played == 0
        assert entry.points == 0


def test_season_manager_update_table(db_session, sample_league):
    """Test updating league table after fixtures"""
    manager = SeasonManager(db_session)

    # Create small league for testing
    teams = [uuid.uuid4() for _ in range(4)]
    league_season = manager.create_season(
        league=sample_league,
        teams=teams,
        season_year=2024,
        start_date=datetime(2024, 8, 1),
        end_date=datetime(2025, 5, 1)
    )

    # Get first fixture and simulate result
    fixture = db_session.query(Fixture).first()
    fixture.status = FixtureStatus.COMPLETED
    fixture.home_score = 2
    fixture.away_score = 1

    # Update table
    manager.update_table_after_fixture(fixture)

    # Check home team entry
    home_entry = next(e for e in league_season.table_entries if e.team_id == fixture.home_team_id)
    assert home_entry.played == 1
    assert home_entry.won == 1
    assert home_entry.drawn == 0
    assert home_entry.lost == 0
    assert home_entry.goals_for == 2
    assert home_entry.goals_against == 1
    assert home_entry.points == 3
    assert home_entry.form == "W"

    # Check away team entry
    away_entry = next(e for e in league_season.table_entries if e.team_id == fixture.away_team_id)
    assert away_entry.played == 1
    assert away_entry.won == 0
    assert away_entry.drawn == 0
    assert away_entry.lost == 1
    assert away_entry.goals_for == 1
    assert away_entry.goals_against == 2
    assert away_entry.points == 0
    assert away_entry.form == "L"

    # Check positions were updated
    table = manager.get_league_table(league_season.id)
    assert table[0].team_id == fixture.home_team_id  # Winner should be first
