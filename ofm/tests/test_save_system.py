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

import json
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

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
    SaveGame,
    SaveType,
)
from ofm.core.save import SaveManager, SaveSerializer
from ofm.core.season import SeasonManager


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
def temp_save_dir():
    """Create a temporary directory for saves"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_game_state(db_session):
    """Create a sample game state with some data"""
    # Create a league
    league = League(
        name="Test League",
        country="ENG",
        level=1,
        num_teams=4,
        promotion_places=1,
        playoff_places=0,
        relegation_places=1
    )
    db_session.add(league)
    db_session.flush()
    
    # Create a competition
    competition = Competition(
        name="Test Competition 2024/25",
        short_name="TC",
        type=CompetitionType.LEAGUE,
        country="ENG",
        season=2024,
        start_date=datetime(2024, 8, 1),
        end_date=datetime(2025, 5, 31),
        active=True
    )
    db_session.add(competition)
    db_session.flush()
    
    # Create league season
    season = LeagueSeason(
        league_id=league.id,
        competition_id=competition.id,
        _team_ids_json=""
    )
    teams = [uuid.uuid4() for _ in range(4)]
    season.team_ids = teams
    db_session.add(season)
    db_session.flush()
    
    # Create some fixtures
    fixture = Fixture(
        competition_id=competition.id,
        home_team_id=str(teams[0]),
        away_team_id=str(teams[1]),
        match_date=datetime(2024, 8, 10),
        match_week=1,
        status=FixtureStatus.COMPLETED,
        home_score=2,
        away_score=1
    )
    db_session.add(fixture)
    
    # Create table entries
    for i, team in enumerate(teams):
        entry = LeagueTableEntry(
            league_season_id=season.id,
            team_id=str(team),
            position=i + 1,
            played=1,
            won=1 if i == 0 else 0,
            drawn=0,
            lost=0 if i == 0 else 1,
            goals_for=2 if i == 0 else 1,
            goals_against=1 if i == 0 else 2
        )
        db_session.add(entry)
    
    db_session.commit()
    
    return {
        'league': league,
        'competition': competition,
        'season': season,
        'teams': teams,
        'fixture': fixture
    }


def test_serializer_game_state_extraction(db_session, sample_game_state):
    """Test extracting game state"""
    serializer = SaveSerializer(db_session)
    
    state = serializer.extract_current_game_state()
    
    assert 'save_version' in state
    assert 'saved_at' in state
    assert 'competitions' in state
    assert 'leagues' in state
    assert 'league_seasons' in state
    assert 'fixtures' in state
    assert 'table_entries' in state
    
    # Check data was extracted
    assert len(state['leagues']) == 1
    assert len(state['competitions']) == 1
    assert len(state['league_seasons']) == 1
    assert len(state['fixtures']) == 1
    assert len(state['table_entries']) == 4


def test_serializer_compression(db_session, sample_game_state):
    """Test game state serialization and compression"""
    serializer = SaveSerializer(db_session)
    
    # Extract state
    state = serializer.extract_current_game_state()
    
    # Serialize
    compressed = serializer.serialize_game_state(state)
    
    # Should be a base64 string
    assert isinstance(compressed, str)
    
    # Deserialize
    restored = serializer.deserialize_game_state(compressed)
    
    # Check key data is restored
    assert restored['save_version'] == state['save_version']
    assert len(restored['leagues']) == len(state['leagues'])
    assert len(restored['competitions']) == len(state['competitions'])


def test_save_manager_create_save(db_session, temp_save_dir, sample_game_state):
    """Test creating a save game"""
    manager = SaveManager(db_session, temp_save_dir)
    
    save = manager.create_save(
        name="Test Save",
        manager_name="John Doe",
        club_id=str(sample_game_state['teams'][0]),
        current_date=datetime(2024, 8, 15),
        save_type=SaveType.MANUAL,
        play_time=3600,
        metadata={'league_position': 1, 'balance': 1000000}
    )
    
    assert save.id is not None
    assert save.name == "Test Save"
    assert save.manager_name == "John Doe"
    assert save.save_type == SaveType.MANUAL
    assert save.play_time == 3600
    assert save.save_metadata['league_position'] == 1


def test_save_manager_list_saves(db_session, temp_save_dir, sample_game_state):
    """Test listing saves"""
    manager = SaveManager(db_session, temp_save_dir)
    
    # Create multiple saves
    for i in range(3):
        manager.create_save(
            name=f"Save {i}",
            manager_name="Test Manager",
            club_id=str(sample_game_state['teams'][0]),
            current_date=datetime(2024, 8, 15),
            save_type=SaveType.MANUAL if i < 2 else SaveType.AUTOSAVE
        )
    
    # List all saves
    all_saves = manager.list_saves()
    assert len(all_saves) == 3
    
    # List manual saves only
    manual_saves = manager.list_saves(SaveType.MANUAL)
    assert len(manual_saves) == 2
    
    # List autosaves only
    autosaves = manager.list_saves(SaveType.AUTOSAVE)
    assert len(autosaves) == 1


def test_save_manager_delete_save(db_session, temp_save_dir, sample_game_state):
    """Test deleting a save"""
    manager = SaveManager(db_session, temp_save_dir)
    
    save = manager.create_save(
        name="To Delete",
        manager_name="Test Manager",
        club_id=str(sample_game_state['teams'][0]),
        current_date=datetime(2024, 8, 15)
    )
    
    save_id = save.id
    
    # Delete the save
    manager.delete_save(save_id)
    
    # Verify it's gone
    saves = manager.list_saves()
    assert len(saves) == 0


def test_save_manager_update_save(db_session, temp_save_dir, sample_game_state):
    """Test updating an existing save"""
    manager = SaveManager(db_session, temp_save_dir)
    
    # Create initial save
    save = manager.create_save(
        name="Original Save",
        manager_name="Test Manager",
        club_id=str(sample_game_state['teams'][0]),
        current_date=datetime(2024, 8, 15),
        play_time=1000
    )
    
    save_id = save.id
    
    # Update the save
    updated = manager.update_save(
        save_id=save_id,
        current_date=datetime(2024, 8, 20),
        play_time=2000,
        metadata={'new_data': 'value'}
    )
    
    assert updated.current_date == datetime(2024, 8, 20)
    assert updated.play_time == 2000
    assert updated.save_metadata['new_data'] == 'value'


def test_autosave_cleanup(db_session, temp_save_dir, sample_game_state):
    """Test autosave cleanup mechanism"""
    manager = SaveManager(db_session, temp_save_dir)
    
    # Create more autosaves than the limit
    for i in range(8):
        manager.create_autosave(
            manager_name="Test Manager",
            club_id=str(sample_game_state['teams'][0]),
            current_date=datetime(2024, 8, 15),
            play_time=i * 1000
        )
    
    # Check only MAX_AUTOSAVES remain
    autosaves = manager.list_saves(SaveType.AUTOSAVE)
    assert len(autosaves) == SaveManager.MAX_AUTOSAVES


def test_save_export_import(db_session, temp_save_dir, sample_game_state):
    """Test exporting and importing saves"""
    manager = SaveManager(db_session, temp_save_dir)
    
    # Create a save
    original = manager.create_save(
        name="Export Test",
        manager_name="Test Manager",
        club_id=str(sample_game_state['teams'][0]),
        current_date=datetime(2024, 8, 15),
        play_time=5000,
        metadata={'test': 'data'}
    )
    
    # Export the save
    export_path = Path(temp_save_dir) / "exported_save.json"
    manager.export_save(original.id, str(export_path))
    
    # Verify export file exists
    assert export_path.exists()
    
    # Import the save with a new name
    imported = manager.import_save(str(export_path), name="Imported Save")
    
    assert imported.name == "Imported Save"
    assert imported.manager_name == original.manager_name
    assert imported.club_id == original.club_id
    assert imported.play_time == original.play_time


def test_save_load_integration(db_session, temp_save_dir, sample_game_state):
    """Test full save/load cycle"""
    manager = SaveManager(db_session, temp_save_dir)
    
    # Create a save
    save = manager.create_save(
        name="Integration Test",
        manager_name="Test Manager",
        club_id=str(sample_game_state['teams'][0]),
        current_date=datetime(2024, 8, 15),
        play_time=7200
    )
    
    save_id = save.id
    
    # Clear the database (simulate loading into fresh game)
    db_session.query(LeagueTableEntry).delete()
    db_session.query(Fixture).delete()
    db_session.query(LeagueSeason).delete()
    db_session.query(Competition).delete()
    db_session.query(League).delete()
    db_session.commit()
    
    # Verify database is empty
    assert db_session.query(League).count() == 0
    assert db_session.query(Competition).count() == 0
    
    # Load the save
    manager_info = manager.load_save(save_id)
    
    # Verify data was restored
    assert db_session.query(League).count() == 1
    assert db_session.query(Competition).count() == 1
    assert db_session.query(LeagueSeason).count() == 1
    assert db_session.query(Fixture).count() == 1
    assert db_session.query(LeagueTableEntry).count() == 4
    
    # Check manager info
    assert manager_info['name'] == "Test Manager"
    assert manager_info['club_id'] == str(sample_game_state['teams'][0])
    assert manager_info['play_time'] == 7200


def test_save_version_compatibility(db_session, temp_save_dir):
    """Test save version compatibility check"""
    manager = SaveManager(db_session, temp_save_dir)
    
    # Create a save with future version
    save = SaveGame(
        name="Future Save",
        save_type=SaveType.MANUAL,
        game_version="999.0.0",
        save_version=999,  # Future version
        current_date=datetime(2024, 8, 15),
        manager_name="Test Manager",
        club_id=str(uuid.uuid4()),
        game_state="dummy"
    )
    db_session.add(save)
    db_session.commit()
    
    # Try to load it
    with pytest.raises(ValueError, match="Save file version"):
        manager.load_save(save.id)


def test_get_save_info(db_session, temp_save_dir, sample_game_state):
    """Test getting save info without loading"""
    manager = SaveManager(db_session, temp_save_dir)
    
    save = manager.create_save(
        name="Info Test",
        manager_name="Test Manager",
        club_id=str(sample_game_state['teams'][0]),
        current_date=datetime(2024, 8, 15),
        play_time=3000,
        metadata={'position': 1}
    )
    
    info = manager.get_save_info(save.id)
    
    assert info['name'] == "Info Test"
    assert info['manager_name'] == "Test Manager"
    assert info['play_time'] == 3000
    assert info['metadata']['position'] == 1
    assert 'game_state' not in info  # Should not include actual game data