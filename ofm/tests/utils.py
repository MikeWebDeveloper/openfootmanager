"""Test utilities and helper functions for OpenFootManager tests."""

import random
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from ofm.core.db.generators import PlayerGenerator, TeamGenerator
from ofm.core.db.models import League
from ofm.core.db.models.base import Base, SessionLocal
from ofm.core.football.club import Club
from ofm.core.football.formation import Formation
from ofm.core.football.manager import Manager
from ofm.core.football.player import Player
from ofm.core.football.positions import Positions
from ofm.core.football.team_simulation import TeamSimulation
from ofm.core.settings import Settings


class TestDataFactory:
    """Factory for creating test data."""

    @staticmethod
    def create_test_league(session: Session, name: str = "Test League") -> League:
        """Create a test league with default settings."""
        league = League(
            name=name,
            country="ENG",  # Use valid ISO country code
            level=1,
            num_teams=20,
            promotion_places=3,
            relegation_places=3,
        )
        session.add(league)
        session.commit()
        return league

    @staticmethod
    def create_test_club(
        session: Session,
        name: str = "Test Club",
        league: Optional[League] = None,
        budget: int = 1000000,
    ) -> Club:
        """Create a test club with default settings."""
        if not league:
            league = TestDataFactory.create_test_league(session)

        club = Club(
            club_id=uuid4(),
            name=name,
            country=league.country,
            location=f"{name} City",
            default_formation="4-4-2",
            squad=[],  # Will be populated later
            stadium=f"{name} Stadium",
            stadium_capacity=20000,
            transfer_budget=float(budget),
            wage_budget=float(budget / 52),  # Weekly wage budget
            reputation=50,
        )
        # Club is a dataclass, not a database model, so don't add to session
        return club

    @staticmethod
    def create_test_player(
        session: Session,
        name: str = "Test Player",
        club: Optional[Club] = None,
        position: Positions = Positions.MF,
        overall: int = 70,
    ) -> Player:
        """Create a test player with specified attributes."""
        if not club:
            club = TestDataFactory.create_test_club(session)

        player = Player(
            name=name,
            club_id=club.id,
            position=position.value,
            age=25,
            nationality="Test Nation",
            overall=overall,
            potential=overall + 10,
            # Physical attributes
            pace=overall,
            acceleration=overall,
            sprint_speed=overall,
            stamina=overall,
            strength=overall,
            jumping=overall,
            # Technical attributes
            passing=overall,
            crossing=overall,
            short_passing=overall,
            long_passing=overall,
            dribbling=overall,
            ball_control=overall,
            first_touch=overall,
            technique=overall,
            shooting=overall,
            long_shots=overall,
            finishing=overall,
            heading=overall,
            # Mental attributes
            aggression=overall,
            anticipation=overall,
            bravery=overall,
            composure=overall,
            concentration=overall,
            creativity=overall,
            decisions=overall,
            determination=overall,
            flair=overall,
            leadership=overall,
            off_the_ball=overall,
            positioning=overall,
            teamwork=overall,
            vision=overall,
            work_rate=overall,
            # Goalkeeping attributes (if GK)
            handling=overall if position == Positions.GK else 10,
            reflexes=overall if position == Positions.GK else 10,
            one_on_ones=overall if position == Positions.GK else 10,
            command_of_area=overall if position == Positions.GK else 10,
            communication=overall if position == Positions.GK else 10,
            kicking=overall if position == Positions.GK else 10,
            throwing=overall if position == Positions.GK else 10,
        )
        session.add(player)
        session.commit()
        return player

    @staticmethod
    def create_test_manager(
        session: Session,
        name: str = "Test Manager",
        club: Optional[Club] = None,
    ) -> Manager:
        """Create a test manager."""
        if not club:
            club = TestDataFactory.create_test_club(session)

        manager = Manager(
            name=name,
            club_id=club.id,
            nationality="Test Nation",
            age=45,
            reputation=50,
            preferred_formation="4-4-2",
            preferred_style="Balanced",
        )
        session.add(manager)
        session.commit()
        return manager

    @staticmethod
    def create_test_team(
        session: Session,
        club_name: str = "Test Team",
        num_players: int = 25,
    ) -> Tuple[Club, List[Player]]:
        """Create a complete test team with players."""
        club = TestDataFactory.create_test_club(session, name=club_name)
        players = []

        # Create goalkeepers
        for i in range(3):
            player = TestDataFactory.create_test_player(
                session,
                name=f"GK {i+1}",
                club=club,
                position=Positions.GK,
                overall=60 + i * 5,
            )
            players.append(player)

        # Create defenders
        positions = [Positions.DL, Positions.DC, Positions.DC, Positions.DR]
        for i, pos in enumerate(positions * 2):  # 8 defenders
            player = TestDataFactory.create_test_player(
                session,
                name=f"DEF {i+1}",
                club=club,
                position=pos,
                overall=65 + random.randint(-5, 5),
            )
            players.append(player)

        # Create midfielders
        positions = [Positions.ML, Positions.MC, Positions.MC, Positions.MR]
        for i, pos in enumerate(positions * 2):  # 8 midfielders
            player = TestDataFactory.create_test_player(
                session,
                name=f"MID {i+1}",
                club=club,
                position=pos,
                overall=70 + random.randint(-5, 5),
            )
            players.append(player)

        # Create forwards
        for i in range(6):
            player = TestDataFactory.create_test_player(
                session,
                name=f"FWD {i+1}",
                club=club,
                position=Positions.FC,
                overall=75 + random.randint(-5, 5),
            )
            players.append(player)

        return club, players


class PerformanceTimer:
    """Context manager for timing test performance."""

    def __init__(self, name: str, max_duration: float = 1.0):
        self.name = name
        self.max_duration = max_duration
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()

        if duration > self.max_duration:
            pytest.fail(
                f"{self.name} took {duration:.2f}s, "
                f"exceeding max duration of {self.max_duration}s"
            )

        return False

    @property
    def duration(self) -> float:
        """Get the duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


def validate_formation(formation: Formation, players: List[Player]) -> bool:
    """Validate that players match the formation requirements."""
    if len(players) != 11:
        return False

    # Count players by position type
    position_counts = {
        "GK": 0,
        "D": 0,
        "M": 0,
        "F": 0,
    }

    for player in players:
        pos = Positions(player.position)
        if pos == Positions.GK:
            position_counts["GK"] += 1
        elif pos.name.startswith("D"):
            position_counts["D"] += 1
        elif pos.name.startswith("M"):
            position_counts["M"] += 1
        elif pos.name.startswith("F") or pos == Positions.FC:
            position_counts["F"] += 1

    # Parse formation string (e.g., "4-4-2")
    parts = formation.name.split("-")
    expected_counts = {
        "GK": 1,
        "D": int(parts[0]),
        "M": int(parts[1]),
        "F": int(parts[2]),
    }

    return position_counts == expected_counts


def create_mock_match_data() -> dict:
    """Create mock data for match testing."""
    return {
        "home_team": "Test Home FC",
        "away_team": "Test Away United",
        "home_score": 0,
        "away_score": 0,
        "minute": 0,
        "half": 1,
        "events": [],
        "home_possession": 50,
        "away_possession": 50,
        "home_shots": 0,
        "away_shots": 0,
        "home_shots_on_target": 0,
        "away_shots_on_target": 0,
    }


def assert_player_attributes_valid(player: Player) -> None:
    """Assert that all player attributes are within valid ranges."""
    # Check all numeric attributes are between 1 and 100
    attributes = [
        "overall",
        "potential",
        "pace",
        "acceleration",
        "sprint_speed",
        "stamina",
        "strength",
        "jumping",
        "passing",
        "vision",
        "crossing",
        "short_passing",
        "long_passing",
        "dribbling",
        "ball_control",
        "first_touch",
        "technique",
        "shooting",
        "long_shots",
        "finishing",
        "heading",
        "aggression",
        "anticipation",
        "bravery",
        "composure",
        "concentration",
        "creativity",
        "decisions",
        "determination",
        "flair",
        "leadership",
        "off_the_ball",
        "positioning",
        "teamwork",
        "work_rate",
    ]

    for attr in attributes:
        value = getattr(player, attr, None)
        if value is not None:
            assert 1 <= value <= 100, f"{attr} value {value} is out of range"

    # Check goalkeeper-specific attributes if player is a goalkeeper
    if Positions(player.position) == Positions.GK:
        gk_attributes = [
            "handling",
            "reflexes",
            "one_on_ones",
            "command_of_area",
            "communication",
            "kicking",
            "throwing",
        ]
        for attr in gk_attributes:
            value = getattr(player, attr, None)
            if value is not None:
                assert 1 <= value <= 100, f"GK {attr} value {value} is out of range"

    # Check age is reasonable
    assert 15 <= player.age <= 45, f"Player age {player.age} is unrealistic"

    # Check potential is at least equal to overall
    assert player.potential >= player.overall, "Potential should be >= overall"


def generate_random_minute() -> int:
    """Generate a random match minute with realistic distribution."""
    # More events happen in certain periods
    weights = [
        1,
        1,
        1,
        1,
        1,  # 0-5 mins
        2,
        2,
        2,
        2,
        2,  # 5-10 mins
        3,
        3,
        3,
        3,
        3,  # 10-15 mins (high activity)
        2,
        2,
        2,
        2,
        2,  # 15-20 mins
        2,
        2,
        2,
        2,
        2,  # 20-25 mins
        2,
        2,
        2,
        2,
        2,  # 25-30 mins
        2,
        2,
        2,
        2,
        2,  # 30-35 mins
        2,
        2,
        2,
        2,
        2,  # 35-40 mins
        3,
        3,
        3,
        3,
        3,  # 40-45 mins (end of half)
        # Second half
        3,
        3,
        3,
        3,
        3,  # 45-50 mins (start of second half)
        2,
        2,
        2,
        2,
        2,  # 50-55 mins
        2,
        2,
        2,
        2,
        2,  # 55-60 mins
        2,
        2,
        2,
        2,
        2,  # 60-65 mins
        2,
        2,
        2,
        2,
        2,  # 65-70 mins
        2,
        2,
        2,
        2,
        2,  # 70-75 mins
        3,
        3,
        3,
        3,
        3,  # 75-80 mins (crucial period)
        3,
        3,
        3,
        3,
        3,  # 80-85 mins
        4,
        4,
        4,
        4,
        4,  # 85-90 mins (end game)
    ]

    minutes = list(range(91))
    return random.choices(minutes, weights=weights[:91])[0]
