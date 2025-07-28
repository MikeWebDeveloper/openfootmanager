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
import datetime
import json
import sys
import uuid
from pathlib import Path
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ..core.db.models.base import Base
from ..core.db.generators import PlayerGenerator, TeamGenerator
from ..core.football.club import PlayerTeam
from ..core.football.formation import Formation
from ..core.football.player import Player, PlayerInjury, PlayerSimulation, PreferredFoot
from ..core.football.player_attributes import *
from ..core.football.playercontract import PlayerContract
from ..core.football.team_simulation import TeamSimulation
from ..core.settings import Settings
from ..core.simulation.simulation import Fixture, LiveGame, SimulationEngine
from ..defaults import PROJECT_DIR

# Import test utilities
try:
    from .utils import TestDataFactory
except ImportError:
    from ofm.tests.utils import TestDataFactory


@pytest.fixture
def settings(tmp_path):
    f = tmp_path / "settings.yaml"
    settings = Settings(PROJECT_DIR, f)
    settings.res = tmp_path / "res"
    settings.res.mkdir(exist_ok=True)
    settings.db = settings.res / "db"
    settings.db.mkdir(exist_ok=True)
    settings.clubs_file = settings.db / "clubs.json"
    settings.squads_file = settings.db / "squads.json"
    settings.players_file = settings.db / "players.json"
    return settings


@pytest.fixture
def player_gen(settings: Settings) -> PlayerGenerator:
    return PlayerGenerator(settings)


@pytest.fixture
def player_attributes() -> PlayerAttributes:
    return PlayerAttributes(
        OffensiveAttributes(85, 80, 75, 88, 90),
        PhysicalAttributes(80, 75, 40),
        DefensiveAttributes(54, 65, 50),
        IntelligenceAttributes(60, 88, 82, 87, 80, 83, 75),
        GkAttributes(20, 20, 10, 10),
    )


@pytest.fixture
def player_obj(player_attributes: PlayerAttributes) -> Player:
    return Player(
        uuid.UUID(int=1),
        "Brazil",
        datetime.date(1996, 12, 14),
        "John",
        "Doe",
        "J. Doe",
        [Positions.FW, Positions.MF],
        100.0,
        100.0,
        0.5,
        player_attributes,
        90,
        5,
        PreferredFoot.LEFT,
        10000.00,
    )


@pytest.fixture
def player_dict(player_attributes: PlayerAttributes) -> dict:
    positions = [Positions.FW, Positions.MF]
    preferred_foot = PreferredFoot.LEFT
    return {
        "id": 1,
        "nationality": "Brazil",
        "dob": "1996-12-14",
        "first_name": "John",
        "last_name": "Doe",
        "short_name": "J. Doe",
        "positions": [position.value for position in positions],
        "fitness": 100.0,
        "stamina": 100.0,
        "form": 0.5,
        "attributes": player_attributes.serialize(),
        "potential_skill": 90,
        "international_reputation": 5,
        "preferred_foot": PreferredFoot(preferred_foot),
        "value": 10000.00,
        "injured": False,
        "injury_type": PlayerInjury.NO_INJURY,
    }


@pytest.fixture
def player_team(player_obj) -> tuple[PlayerTeam, Player, dict]:
    player_id = uuid.UUID(int=1)
    team_id = uuid.UUID(int=1)
    shirt_number = 10
    contract_dict = {
        "wage": 10000.00,
        "started": "2020-01-01",
        "end": "2021-01-01",
        "bonus_for_goal": 500.00,
        "bonus_for_def": 500.00,
    }
    player_team_dict = {
        "player_id": player_id.int,
        "team_id": team_id.int,
        "shirt_number": shirt_number,
        "contract": contract_dict,
    }
    expected_contract = PlayerContract.get_from_dict(contract_dict)
    player_team = PlayerTeam(player_obj, team_id, shirt_number, expected_contract)
    return player_team, player_obj, player_team_dict


@pytest.fixture
def player_sim(player_team: tuple[PlayerTeam, Player, dict]) -> PlayerSimulation:
    position = player_team[0].details.get_best_position()
    return PlayerSimulation(player_team[0], position)


@pytest.fixture
def squads_def() -> list[dict]:
    return [
        {
            "name": "Munchen",
            "stadium": "Munchen National Stadium",
            "stadium_capacity": 40100,
            "country": "GER",
            "location": "Munich",
            "default_formation": "4-4-2",
            "squads_def": {
                "mu": 80,
                "sigma": 20,
            },
        },
        {
            "name": "Barcelona",
            "stadium": "Barcelona National Stadium",
            "stadium_capacity": 50000,
            "country": "ESP",
            "location": "Barcelona",
            "default_formation": "4-3-3",
            "squads_def": {
                "mu": 80,
                "sigma": 20,
            },
        },
    ]


@pytest.fixture
def mock_file() -> list[dict]:
    return [
        {
            "id": 1,
            "name": "Munchen",
            "country": "GER",
            "location": "Munich",
            "default_formation": "4-4-2",
            "squad": [],
            "stadium": "Munchen National Stadium",
            "stadium_capacity": 40100,
        },
        {
            "id": 2,
            "name": "Barcelona",
            "country": "ESP",
            "location": "Barcelona",
            "default_formation": "4-3-3",
            "squad": [],
            "stadium": "Barcelona National Stadium",
            "stadium_capacity": 50000,
        },
    ]


@pytest.fixture
def confederations_file(settings: Settings) -> list[dict]:
    with open(settings.fifa_conf, "r") as fp:
        return json.load(fp)


@pytest.fixture
def simulation_teams(
    squads_def, confederations_file, settings: Settings
) -> tuple[TeamSimulation, TeamSimulation]:
    team_gen = TeamGenerator(squads_def, confederations_file, settings)

    teams = team_gen.generate()
    home_team, away_team = teams[0], teams[1]

    home_team_formation = Formation(home_team.default_formation)
    home_team_formation.get_best_players(home_team.squad)
    home_team_sim = TeamSimulation(home_team, home_team_formation)
    away_team_formation = Formation(away_team.default_formation)
    away_team_formation.get_best_players(away_team.squad)
    away_team_sim = TeamSimulation(away_team, away_team_formation)

    return home_team_sim, away_team_sim


class MockSimulationEngine:
    def run(self):
        pass


@pytest.fixture
def live_game(monkeypatch, simulation_teams) -> LiveGame:
    def get_simulation_engine(*args, **kwargs):
        return MockSimulationEngine()

    home_team_sim, away_team_sim = simulation_teams
    home_team = home_team_sim.club
    away_team = away_team_sim.club
    fixture = Fixture(
        uuid.uuid4(),
        uuid.uuid4(),
        home_team.club_id,
        away_team.club_id,
        home_team.stadium,
    )

    def get_event_duration(self):
        return datetime.timedelta(seconds=5)

    monkeypatch.setattr(SimulationEngine, "run", get_simulation_engine)
    monkeypatch.setattr(SimulationEngine, "get_event_duration", get_event_duration)

    live_game = LiveGame(fixture, home_team_sim, away_team_sim, False, False, True)
    live_game.running = True
    return live_game


# Additional fixtures for enhanced testing
@pytest.fixture(scope="session")
def test_settings():
    """Create test settings."""
    # Settings uses default initialization
    settings = Settings()
    # Ensure test directories exist
    settings.save.mkdir(exist_ok=True)
    settings.db.mkdir(exist_ok=True)
    return settings


@pytest.fixture(scope="function")
def test_db_session(test_settings) -> Generator[Session, None, None]:
    """Create a test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_factory(test_db_session):
    """Provide test data factory with database session."""
    return TestDataFactory()


@pytest.fixture
def sample_league(test_db_session):
    """Create a sample league."""
    return TestDataFactory.create_test_league(test_db_session)


@pytest.fixture
def sample_club(test_db_session, sample_league):
    """Create a sample club."""
    return TestDataFactory.create_test_club(
        test_db_session,
        league=sample_league
    )


@pytest.fixture
def sample_player(test_db_session, sample_club):
    """Create a sample player."""
    return TestDataFactory.create_test_player(
        test_db_session,
        club=sample_club
    )


@pytest.fixture
def sample_team(test_db_session):
    """Create a complete team with players."""
    return TestDataFactory.create_test_team(test_db_session)


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset any singleton instances between tests."""
    # Add any singleton resets here if needed
    yield
