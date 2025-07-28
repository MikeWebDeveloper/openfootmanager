"""
Calendar integration for the transfer system.

Integrates transfer windows with the season calendar,
managing transfer window dates and deadlines.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from ..db.models.league_season import LeagueSeason
from ..db.models.transfer import TransferWindow
from ..season.calendar import Calendar, CalendarEvent
from ..season.calendar import CalendarEventType as EventType


class TransferCalendarIntegration:
    """Manages transfer window integration with season calendar."""

    def __init__(self, calendar: Calendar):
        self.calendar = calendar

    def add_transfer_windows(self, season: LeagueSeason) -> List[TransferWindow]:
        """
        Add standard transfer windows to a season.

        Args:
            season: The league season

        Returns:
            List of created transfer windows
        """
        windows = []

        # Summer transfer window (June 1 - August 31)
        summer_window = self._create_summer_window(season)
        windows.append(summer_window)

        # Winter transfer window (January 1-31)
        winter_window = self._create_winter_window(season)
        windows.append(winter_window)

        # Add to calendar
        self._add_window_to_calendar(summer_window)
        self._add_window_to_calendar(winter_window)

        return windows

    def _create_summer_window(self, season: LeagueSeason) -> TransferWindow:
        """Create summer transfer window."""
        # Typically runs from June 1 to August 31
        year = season.start_date.year

        start_date = datetime(year, 6, 1)
        end_date = datetime(year, 8, 31, 23, 59, 59)

        return TransferWindow(
            name=f"Summer Transfer Window {year}",
            season_id=season.id,
            start_date=start_date,
            end_date=end_date,
            country=season.league.country,
            is_active=True,
            allows_loans=True,
            allows_free_agents=True,
        )

    def _create_winter_window(self, season: LeagueSeason) -> TransferWindow:
        """Create winter transfer window."""
        # Runs in January of the following year
        year = season.start_date.year + 1

        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 1, 31, 23, 59, 59)

        return TransferWindow(
            name=f"Winter Transfer Window {year}",
            season_id=season.id,
            start_date=start_date,
            end_date=end_date,
            country=season.league.country,
            is_active=True,
            allows_loans=True,
            allows_free_agents=True,
        )

    def _add_window_to_calendar(self, window: TransferWindow):
        """Add transfer window events to calendar."""
        # Window opening event
        open_event = CalendarEvent(
            date=window.start_date,
            event_type=EventType.TRANSFER_WINDOW_OPEN,
            description=f"{window.name} Opens",
            metadata={"window_id": window.id, "window_name": window.name},
        )
        self.calendar.add_event(open_event)

        # Deadline day warning (1 week before close)
        warning_date = window.end_date - timedelta(days=7)
        warning_event = CalendarEvent(
            date=warning_date,
            event_type=EventType.TRANSFER_DEADLINE_WARNING,
            description=f"{window.name} - 1 Week Remaining",
            metadata={"window_id": window.id, "days_remaining": 7},
        )
        self.calendar.add_event(warning_event)

        # Deadline day event
        deadline_event = CalendarEvent(
            date=window.end_date.replace(hour=0, minute=0, second=0),
            event_type=EventType.TRANSFER_DEADLINE_DAY,
            description=f"{window.name} Deadline Day",
            metadata={"window_id": window.id, "closes_at": window.end_date.isoformat()},
        )
        self.calendar.add_event(deadline_event)

        # Window closing event
        close_event = CalendarEvent(
            date=window.end_date,
            event_type=EventType.TRANSFER_WINDOW_CLOSE,
            description=f"{window.name} Closes",
            metadata={"window_id": window.id, "window_name": window.name},
        )
        self.calendar.add_event(close_event)

    def get_current_window(self, date: datetime) -> Optional[TransferWindow]:
        """
        Get the active transfer window for a given date.

        Args:
            date: The date to check

        Returns:
            Active transfer window or None
        """
        # This would query the database in real implementation
        # For now, return None
        return None

    def days_until_deadline(self, window: TransferWindow) -> int:
        """
        Calculate days until transfer deadline.

        Args:
            window: The transfer window

        Returns:
            Days remaining (negative if past deadline)
        """
        now = datetime.now()
        delta = window.end_date - now
        return delta.days

    def is_deadline_day(self, date: datetime, window: TransferWindow) -> bool:
        """
        Check if given date is deadline day.

        Args:
            date: Date to check
            window: Transfer window

        Returns:
            True if deadline day
        """
        return date.date() == window.end_date.date()

    def get_regional_windows(self, country: str) -> List[TransferWindow]:
        """
        Get transfer windows for a specific country.

        Some countries have different transfer window dates.

        Args:
            country: ISO country code

        Returns:
            List of transfer windows for that country
        """
        # Different windows for different regions
        # TODO: Implement regional windows
        # Examples:
        # - Russia: February (summer), July-August (winter)
        # - Brazil: January-April (summer), July-August (winter)
        # - USA/MLS: February-May (primary), July-August (secondary)

        # Return standard windows for now
        return []

    def schedule_transfer_meetings(self, window: TransferWindow):
        """
        Schedule important transfer-related meetings.

        Args:
            window: The transfer window
        """
        # Pre-window planning meeting (1 week before)
        planning_date = window.start_date - timedelta(days=7)
        planning_event = CalendarEvent(
            date=planning_date,
            event_type=EventType.BOARD_MEETING,
            description="Transfer Planning Meeting",
            metadata={"meeting_type": "transfer_planning", "window_id": window.id},
        )
        self.calendar.add_event(planning_event)

        # Mid-window review (halfway through)
        duration = window.end_date - window.start_date
        midpoint = window.start_date + (duration / 2)
        review_event = CalendarEvent(
            date=midpoint,
            event_type=EventType.BOARD_MEETING,
            description="Transfer Window Review",
            metadata={"meeting_type": "transfer_review", "window_id": window.id},
        )
        self.calendar.add_event(review_event)

    def get_transfer_timeline(self, season: LeagueSeason) -> List[Tuple[datetime, str]]:
        """
        Get complete transfer timeline for a season.

        Args:
            season: The league season

        Returns:
            List of (date, description) tuples
        """
        timeline = []

        # Get all transfer-related events
        transfer_events = [
            event
            for event in self.calendar.events
            if event.event_type
            in [
                EventType.TRANSFER_WINDOW_OPEN,
                EventType.TRANSFER_WINDOW_CLOSE,
                EventType.TRANSFER_DEADLINE_DAY,
                EventType.TRANSFER_DEADLINE_WARNING,
            ]
        ]

        # Sort by date
        transfer_events.sort(key=lambda e: e.date)

        # Build timeline
        for event in transfer_events:
            timeline.append((event.date, event.description))

        return timeline
