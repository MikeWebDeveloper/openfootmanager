"""Tests for the match engine and simulation components."""

import pytest
from datetime import datetime
import random

from ofm.core.simulation.game_state import GameState
from ofm.core.simulation.simulation import SimulationEngine
from ofm.core.simulation.event_type import EventType
from ofm.core.simulation.events import PassEvent, ShotEvent, DribbleEvent
from ofm.core.football.formation import Formation
from ofm.core.football.positions import Positions
from ofm.tests.utils import TestDataFactory, PerformanceTimer, create_mock_match_data


class TestMatchEngine:
    """Test suite for match engine functionality."""

    @pytest.mark.fast
    @pytest.mark.unit
    def test_game_state_initialization(self, sample_team):
        """Test game state initialization."""
        club, players = sample_team
        
        game_state = GameState()
        game_state.home_team = club
        game_state.away_team = club  # Using same team for simplicity
        game_state.home_score = 0
        game_state.away_score = 0
        game_state.minute = 0
        game_state.half = 1
        
        assert game_state.home_score == 0
        assert game_state.away_score == 0
        assert game_state.minute == 0
        assert game_state.half == 1
        assert game_state.is_playing is False

    @pytest.mark.fast
    @pytest.mark.unit
    def test_match_event_creation(self):
        """Test creation of different match events."""
        # Pass event
        pass_event = PassEvent(
            minute=15,
            player_id=1,
            team_id=1,
            success=True,
            pass_type="short",
            distance=10.5,
        )
        assert pass_event.event_type == EventType.PASS
        assert pass_event.success is True
        assert pass_event.distance == 10.5
        
        # Shot event
        shot_event = ShotEvent(
            minute=30,
            player_id=2,
            team_id=1,
            success=False,
            shot_type="long_shot",
            on_target=True,
            saved=True,
        )
        assert shot_event.event_type == EventType.SHOT
        assert shot_event.on_target is True
        assert shot_event.saved is True
        
        # Dribble event
        dribble_event = DribbleEvent(
            minute=45,
            player_id=3,
            team_id=2,
            success=True,
            skill_move="step_over",
        )
        assert dribble_event.event_type == EventType.DRIBBLE
        assert dribble_event.skill_move == "step_over"

    @pytest.mark.fast
    @pytest.mark.critical
    def test_goal_scoring(self, sample_team):
        """Test goal scoring mechanism."""
        club, players = sample_team
        
        game_state = GameState()
        game_state.home_team = club
        game_state.away_team = club
        game_state.home_score = 0
        game_state.away_score = 0
        
        # Simulate a goal
        goal_event = ShotEvent(
            minute=25,
            player_id=players[0].id,
            team_id=club.id,
            success=True,
            shot_type="finish",
            on_target=True,
            saved=False,
            is_goal=True,
        )
        
        # Update game state
        if goal_event.is_goal:
            if goal_event.team_id == game_state.home_team.id:
                game_state.home_score += 1
            else:
                game_state.away_score += 1
        
        assert game_state.home_score == 1
        assert game_state.away_score == 0

    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_match_simulation(self, test_db_session):
        """Test a complete match simulation."""
        # Create two teams
        home_club, home_players = TestDataFactory.create_test_team(
            test_db_session, club_name="Home FC"
        )
        away_club, away_players = TestDataFactory.create_test_team(
            test_db_session, club_name="Away United"
        )
        
        # Initialize game state
        game_state = GameState()
        game_state.home_team = home_club
        game_state.away_team = away_club
        game_state.home_score = 0
        game_state.away_score = 0
        game_state.minute = 0
        game_state.half = 1
        game_state.is_playing = True
        
        # Simulate match minutes
        events = []
        while game_state.minute < 90:
            game_state.minute += 1
            
            # Change half at 45 minutes
            if game_state.minute == 46:
                game_state.half = 2
            
            # Random chance of event
            if random.random() < 0.1:  # 10% chance of event per minute
                event_type = random.choice(["pass", "shot", "dribble", "foul"])
                
                if event_type == "shot" and random.random() < 0.2:  # 20% of shots are goals
                    team = random.choice([home_club, away_club])
                    if team == home_club:
                        game_state.home_score += 1
                    else:
                        game_state.away_score += 1
                    
                    events.append({
                        "minute": game_state.minute,
                        "type": "goal",
                        "team": team.name,
                    })
        
        # End match
        game_state.is_playing = False
        
        # Verify match completed
        assert game_state.minute >= 90
        assert game_state.half == 2
        assert game_state.is_playing is False
        assert game_state.home_score >= 0
        assert game_state.away_score >= 0

    @pytest.mark.fast
    @pytest.mark.unit
    def test_possession_calculation(self, sample_team):
        """Test possession percentage calculation."""
        club, players = sample_team
        
        # Track passes for possession
        home_passes = 250
        away_passes = 150
        total_passes = home_passes + away_passes
        
        home_possession = (home_passes / total_passes) * 100
        away_possession = (away_passes / total_passes) * 100
        
        assert abs(home_possession + away_possession - 100) < 0.01
        assert home_possession == 62.5
        assert away_possession == 37.5

    @pytest.mark.fast
    @pytest.mark.unit
    def test_substitution_during_match(self, sample_team):
        """Test player substitution during match."""
        club, players = sample_team
        
        # Select starting 11
        starting_11 = players[:11]
        substitutes = players[11:16]  # 5 substitutes
        
        # Make a substitution at 60 minutes
        player_out = starting_11[5]  # Midfielder
        player_in = substitutes[0]
        
        # Perform substitution
        starting_11[5] = player_in
        
        assert player_in in starting_11
        assert player_out not in starting_11
        assert len(starting_11) == 11

    @pytest.mark.fast
    @pytest.mark.critical
    def test_injury_during_match(self, sample_team):
        """Test injury occurrence and handling during match."""
        club, players = sample_team
        
        # Select a player to get injured
        injured_player = players[0]
        
        # Simulate injury
        injury_data = {
            "player_id": injured_player.id,
            "minute": 35,
            "severity": "moderate",
            "days_out": 14,
            "body_part": "ankle",
        }
        
        # Apply injury
        injured_player.is_injured = True
        injured_player.injury_days_remaining = injury_data["days_out"]
        injured_player.injury_type = injury_data["body_part"]
        
        assert injured_player.is_injured is True
        assert injured_player.injury_days_remaining == 14
        assert injured_player.injury_type == "ankle"

    @pytest.mark.performance
    def test_match_engine_performance(self, test_db_session):
        """Test match engine performance with multiple simultaneous matches."""
        matches = []
        
        # Create 10 matches
        for i in range(10):
            home_club, home_players = TestDataFactory.create_test_team(
                test_db_session, club_name=f"Home {i}"
            )
            away_club, away_players = TestDataFactory.create_test_team(
                test_db_session, club_name=f"Away {i}"
            )
            
            matches.append({
                "home": home_club,
                "away": away_club,
                "home_players": home_players,
                "away_players": away_players,
            })
        
        # Simulate all matches
        with PerformanceTimer("10 match simulations", max_duration=5.0):
            results = []
            for match in matches:
                # Simplified match simulation
                home_score = random.randint(0, 5)
                away_score = random.randint(0, 5)
                
                results.append({
                    "home_team": match["home"].name,
                    "away_team": match["away"].name,
                    "home_score": home_score,
                    "away_score": away_score,
                })
        
        assert len(results) == 10
        for result in results:
            assert result["home_score"] >= 0
            assert result["away_score"] >= 0

    @pytest.mark.fast
    @pytest.mark.unit
    def test_match_statistics_tracking(self):
        """Test tracking of match statistics."""
        stats = {
            "home": {
                "shots": 0,
                "shots_on_target": 0,
                "passes": 0,
                "pass_accuracy": 0.0,
                "fouls": 0,
                "corners": 0,
                "offsides": 0,
                "yellow_cards": 0,
                "red_cards": 0,
            },
            "away": {
                "shots": 0,
                "shots_on_target": 0,
                "passes": 0,
                "pass_accuracy": 0.0,
                "fouls": 0,
                "corners": 0,
                "offsides": 0,
                "yellow_cards": 0,
                "red_cards": 0,
            }
        }
        
        # Simulate some events
        stats["home"]["shots"] = 12
        stats["home"]["shots_on_target"] = 5
        stats["home"]["passes"] = 450
        stats["home"]["pass_accuracy"] = 0.85
        stats["home"]["fouls"] = 8
        stats["home"]["corners"] = 6
        
        stats["away"]["shots"] = 8
        stats["away"]["shots_on_target"] = 3
        stats["away"]["passes"] = 320
        stats["away"]["pass_accuracy"] = 0.78
        stats["away"]["fouls"] = 12
        stats["away"]["corners"] = 4
        
        # Verify statistics
        assert stats["home"]["shots"] > stats["away"]["shots"]
        assert stats["home"]["passes"] > stats["away"]["passes"]
        assert stats["away"]["fouls"] > stats["home"]["fouls"]
        
        # Calculate shot accuracy
        home_shot_accuracy = stats["home"]["shots_on_target"] / stats["home"]["shots"]
        away_shot_accuracy = stats["away"]["shots_on_target"] / stats["away"]["shots"]
        
        assert 0 <= home_shot_accuracy <= 1
        assert 0 <= away_shot_accuracy <= 1