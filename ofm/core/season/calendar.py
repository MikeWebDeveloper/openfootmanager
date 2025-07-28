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
from enum import Enum
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from ..db.models import Competition, Fixture, FixtureStatus


class CalendarEventType(Enum):
    """Types of calendar events"""

    MATCH = "match"
    TRANSFER_WINDOW_OPEN = "transfer_window_open"
    TRANSFER_WINDOW_CLOSE = "transfer_window_close"
    TRANSFER_DEADLINE_DAY = "transfer_deadline_day"
    TRANSFER_DEADLINE_WARNING = "transfer_deadline_warning"
    TRAINING = "training"
    REST_DAY = "rest_day"
    INTERNATIONAL_BREAK = "international_break"
    SEASON_START = "season_start"
    SEASON_END = "season_end"
    PRE_SEASON = "pre_season"
    BOARD_MEETING = "board_meeting"


class CalendarEvent:
    """Represents a single calendar event"""

    def __init__(
        self,
        date: datetime,
        event_type: CalendarEventType,
        description: str,
        data: Optional[Dict] = None,
    ):
        self.date = date
        self.event_type = event_type
        self.description = description
        self.data = data or {}

    def __repr__(self) -> str:
        return f"<CalendarEvent({self.date.date()}, {self.event_type.value}, {self.description})>"


class GameCalendar:
    """Manages the game calendar and scheduling"""

    def __init__(self, session: Session):
        self.session = session
        self.current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self._events_cache: Dict[datetime, List[CalendarEvent]] = {}

    def set_current_date(self, date: datetime) -> None:
        """Set the current game date"""
        self.current_date = date.replace(hour=0, minute=0, second=0, microsecond=0)

    def advance_days(self, days: int) -> datetime:
        """Advance the calendar by specified days"""
        self.current_date += timedelta(days=days)
        return self.current_date

    def advance_to_next_event(self) -> Optional[CalendarEvent]:
        """Advance to the next calendar event"""
        next_event = self.get_next_event()
        if next_event:
            self.current_date = next_event.date
        return next_event

    def get_events_for_date(self, date: datetime) -> List[CalendarEvent]:
        """Get all events for a specific date"""
        date_only = date.replace(hour=0, minute=0, second=0, microsecond=0)

        # Check cache first
        if date_only in self._events_cache:
            return self._events_cache[date_only]

        events = []

        # Check for matches
        fixtures = (
            self.session.query(Fixture)
            .filter(
                Fixture.match_date >= date_only,
                Fixture.match_date < date_only + timedelta(days=1),
            )
            .all()
        )

        for fixture in fixtures:
            event = CalendarEvent(
                date=fixture.match_date,
                event_type=CalendarEventType.MATCH,
                description=f"Match: {fixture.home_team_id} vs {fixture.away_team_id}",
                data={"fixture_id": fixture.id},
            )
            events.append(event)

        # Check for transfer windows (hardcoded for now, should be configurable)
        if self._is_transfer_window_date(date_only):
            window_type = self._get_transfer_window_type(date_only)
            if window_type:
                events.append(window_type)

        # Add training days (non-match days)
        if not fixtures and date_only.weekday() not in [6]:  # Not Sunday
            events.append(
                CalendarEvent(
                    date=date_only,
                    event_type=CalendarEventType.TRAINING,
                    description="Team training session",
                )
            )

        # Cache the results
        self._events_cache[date_only] = events
        return events

    def get_events_range(self, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        """Get all events in a date range"""
        events = []
        current = start_date

        while current <= end_date:
            events.extend(self.get_events_for_date(current))
            current += timedelta(days=1)

        return sorted(events, key=lambda e: e.date)

    def get_next_event(
        self, event_type: Optional[CalendarEventType] = None
    ) -> Optional[CalendarEvent]:
        """Get the next event of specified type (or any type if None)"""
        search_date = self.current_date + timedelta(days=1)
        max_search_days = 365  # Don't search forever

        for _ in range(max_search_days):
            events = self.get_events_for_date(search_date)

            if event_type:
                filtered_events = [e for e in events if e.event_type == event_type]
                if filtered_events:
                    return filtered_events[0]
            elif events:
                return events[0]

            search_date += timedelta(days=1)

        return None

    def get_next_match(self, team_id: Optional[str] = None) -> Optional[Fixture]:
        """Get the next match for a specific team or any team"""
        query = self.session.query(Fixture).filter(
            Fixture.match_date > self.current_date,
            Fixture.status == FixtureStatus.SCHEDULED,
        )

        if team_id:
            query = query.filter(
                (Fixture.home_team_id == team_id) | (Fixture.away_team_id == team_id)
            )

        return query.order_by(Fixture.match_date).first()

    def get_fixtures_for_week(self, week_start: Optional[datetime] = None) -> List[Fixture]:
        """Get all fixtures for the week starting from given date"""
        if week_start is None:
            # Find Monday of current week
            days_since_monday = self.current_date.weekday()
            week_start = self.current_date - timedelta(days=days_since_monday)

        week_end = week_start + timedelta(days=7)

        return (
            self.session.query(Fixture)
            .filter(Fixture.match_date >= week_start, Fixture.match_date < week_end)
            .order_by(Fixture.match_date)
            .all()
        )

    def _is_transfer_window_date(self, date: datetime) -> bool:
        """Check if date is related to transfer window"""
        # Summer window: July 1 - August 31
        # Winter window: January 1 - January 31

        if date.month == 7 and date.day == 1:
            return True
        elif date.month == 8 and date.day == 31:
            return True
        elif date.month == 1 and date.day == 1:
            return True
        elif date.month == 1 and date.day == 31:
            return True

        return False

    def _get_transfer_window_type(self, date: datetime) -> Optional[CalendarEvent]:
        """Get transfer window event for date"""
        if date.month == 7 and date.day == 1:
            return CalendarEvent(
                date=date,
                event_type=CalendarEventType.TRANSFER_WINDOW_OPEN,
                description="Summer transfer window opens",
            )
        elif date.month == 8 and date.day == 31:
            return CalendarEvent(
                date=date,
                event_type=CalendarEventType.TRANSFER_WINDOW_CLOSE,
                description="Summer transfer window closes",
            )
        elif date.month == 1 and date.day == 1:
            return CalendarEvent(
                date=date,
                event_type=CalendarEventType.TRANSFER_WINDOW_OPEN,
                description="Winter transfer window opens",
            )
        elif date.month == 1 and date.day == 31:
            return CalendarEvent(
                date=date,
                event_type=CalendarEventType.TRANSFER_WINDOW_CLOSE,
                description="Winter transfer window closes",
            )

        return None

    def is_transfer_window_open(self) -> bool:
        """Check if transfer window is currently open"""
        month = self.current_date.month
        day = self.current_date.day

        # Summer window: July 1 - August 31
        if month == 7 or (month == 8 and day <= 31):
            return True

        # Winter window: January 1 - January 31
        if month == 1:
            return True

        return False

    def get_season_progress(self, competition_id: int) -> Tuple[int, int]:
        """Get season progress as (matches_played, total_matches)"""
        competition = self.session.get(Competition, competition_id)
        if not competition:
            return 0, 0

        total_fixtures = (
            self.session.query(Fixture).filter_by(competition_id=competition_id).count()
        )

        completed_fixtures = (
            self.session.query(Fixture)
            .filter_by(competition_id=competition_id, status=FixtureStatus.COMPLETED)
            .count()
        )

        return completed_fixtures, total_fixtures

    def clear_cache(self) -> None:
        """Clear the events cache"""
        self._events_cache.clear()
