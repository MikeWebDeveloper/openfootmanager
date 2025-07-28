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
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ofm.core.db.models import (
    Base,
    Competition,
    CompetitionType,
    Fixture,
    FixtureStatus,
)
from ofm.core.season import CalendarEventType, GameCalendar


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
def sample_fixtures(db_session):
    """Create sample fixtures for testing"""
    competition = Competition(
        name="Test League",
        short_name="TL",
        type=CompetitionType.LEAGUE,
        country="ENG",
        season=2024,
        start_date=datetime(2024, 8, 1),
        end_date=datetime(2025, 5, 31),
        active=True,
    )
    db_session.add(competition)
    db_session.flush()

    fixtures = []
    # Create fixtures for different dates
    for i in range(5):
        fixture = Fixture(
            competition_id=competition.id,
            home_team_id=str(uuid.uuid4()),
            away_team_id=str(uuid.uuid4()),
            match_date=datetime(2024, 8, 10) + timedelta(days=i * 7),
            match_week=i + 1,
            status=FixtureStatus.SCHEDULED,
        )
        fixtures.append(fixture)
        db_session.add(fixture)

    db_session.commit()
    return fixtures


def test_calendar_initialization(db_session):
    """Test calendar initialization"""
    calendar = GameCalendar(db_session)
    assert calendar.current_date.date() == datetime.now().date()


def test_set_current_date(db_session):
    """Test setting current date"""
    calendar = GameCalendar(db_session)
    new_date = datetime(2024, 8, 1)
    calendar.set_current_date(new_date)
    assert calendar.current_date == new_date.replace(
        hour=0, minute=0, second=0, microsecond=0
    )


def test_advance_days(db_session):
    """Test advancing calendar days"""
    calendar = GameCalendar(db_session)
    start_date = datetime(2024, 8, 1)
    calendar.set_current_date(start_date)

    calendar.advance_days(5)
    assert calendar.current_date == datetime(2024, 8, 6)

    calendar.advance_days(10)
    assert calendar.current_date == datetime(2024, 8, 16)


def test_get_events_for_match_day(db_session, sample_fixtures):
    """Test getting events for a day with matches"""
    calendar = GameCalendar(db_session)

    # Get events for first match day
    events = calendar.get_events_for_date(datetime(2024, 8, 10))

    assert len(events) == 1
    assert events[0].event_type == CalendarEventType.MATCH
    assert "fixture_id" in events[0].data


def test_get_events_for_training_day(db_session):
    """Test getting events for a non-match day"""
    calendar = GameCalendar(db_session)

    # Monday with no matches should be training
    events = calendar.get_events_for_date(datetime(2024, 8, 5))

    assert len(events) == 1
    assert events[0].event_type == CalendarEventType.TRAINING


def test_get_events_for_sunday(db_session):
    """Test that Sunday has no training"""
    calendar = GameCalendar(db_session)

    # Sunday with no matches should have no events
    events = calendar.get_events_for_date(datetime(2024, 8, 4))

    assert len(events) == 0


def test_transfer_window_events(db_session):
    """Test transfer window events"""
    calendar = GameCalendar(db_session)

    # Summer window open
    events = calendar.get_events_for_date(datetime(2024, 7, 1))
    assert any(e.event_type == CalendarEventType.TRANSFER_WINDOW_OPEN for e in events)

    # Summer window close
    events = calendar.get_events_for_date(datetime(2024, 8, 31))
    assert any(e.event_type == CalendarEventType.TRANSFER_WINDOW_CLOSE for e in events)

    # Winter window open
    events = calendar.get_events_for_date(datetime(2025, 1, 1))
    assert any(e.event_type == CalendarEventType.TRANSFER_WINDOW_OPEN for e in events)

    # Winter window close
    events = calendar.get_events_for_date(datetime(2025, 1, 31))
    assert any(e.event_type == CalendarEventType.TRANSFER_WINDOW_CLOSE for e in events)


def test_is_transfer_window_open(db_session):
    """Test transfer window status check"""
    calendar = GameCalendar(db_session)

    # During summer window
    calendar.set_current_date(datetime(2024, 7, 15))
    assert calendar.is_transfer_window_open() is True

    # After summer window
    calendar.set_current_date(datetime(2024, 9, 15))
    assert calendar.is_transfer_window_open() is False

    # During winter window
    calendar.set_current_date(datetime(2025, 1, 15))
    assert calendar.is_transfer_window_open() is True


def test_get_next_match(db_session, sample_fixtures):
    """Test getting next match"""
    calendar = GameCalendar(db_session)
    calendar.set_current_date(datetime(2024, 8, 1))

    next_match = calendar.get_next_match()
    assert next_match is not None
    assert next_match.match_date == datetime(2024, 8, 10)


def test_get_fixtures_for_week(db_session, sample_fixtures):
    """Test getting fixtures for a week"""
    calendar = GameCalendar(db_session)

    # Week starting August 5, 2024 (Monday)
    week_fixtures = calendar.get_fixtures_for_week(datetime(2024, 8, 5))

    # Should include fixture on August 10 (Saturday)
    assert len(week_fixtures) == 1
    assert week_fixtures[0].match_date.date() == datetime(2024, 8, 10).date()


def test_get_season_progress(db_session, sample_fixtures):
    """Test getting season progress"""
    calendar = GameCalendar(db_session)

    # Initially all matches are scheduled
    competition_id = sample_fixtures[0].competition_id
    played, total = calendar.get_season_progress(competition_id)
    assert played == 0
    assert total == 5

    # Complete some matches
    sample_fixtures[0].status = FixtureStatus.COMPLETED
    sample_fixtures[0].home_score = 2
    sample_fixtures[0].away_score = 1
    sample_fixtures[1].status = FixtureStatus.COMPLETED
    sample_fixtures[1].home_score = 0
    sample_fixtures[1].away_score = 0
    db_session.commit()

    played, total = calendar.get_season_progress(competition_id)
    assert played == 2
    assert total == 5


def test_advance_to_next_event(db_session, sample_fixtures):
    """Test advancing to next event"""
    calendar = GameCalendar(db_session)
    calendar.set_current_date(datetime(2024, 8, 1))

    # Advance to next event (should be training or match)
    next_event = calendar.advance_to_next_event()
    assert next_event is not None
    assert calendar.current_date >= datetime(2024, 8, 2)


def test_cache_functionality(db_session, sample_fixtures):
    """Test that calendar caches events properly"""
    calendar = GameCalendar(db_session)

    # First call should cache
    events1 = calendar.get_events_for_date(datetime(2024, 8, 10))

    # Second call should use cache
    events2 = calendar.get_events_for_date(datetime(2024, 8, 10))

    assert events1 == events2
    assert len(calendar._events_cache) > 0

    # Clear cache
    calendar.clear_cache()
    assert len(calendar._events_cache) == 0
