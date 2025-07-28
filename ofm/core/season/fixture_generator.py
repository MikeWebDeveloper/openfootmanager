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

import random
from datetime import datetime, timedelta
from typing import List, Tuple
from uuid import UUID

from ..db.models import Fixture, FixtureStatus


class FixtureGenerator:
    """Generates fixtures for a round-robin league competition"""

    def __init__(
        self,
        start_date: datetime,
        match_days: List[int],
        winter_break: Tuple[datetime, datetime] = None,
    ):
        """
        Initialize fixture generator

        Args:
            start_date: First match date of the season
            match_days: Days of week when matches are played (0=Monday, 6=Sunday)
            winter_break: Optional tuple of (start, end) dates for winter break
        """
        self.start_date = start_date
        self.match_days = match_days
        self.winter_break = winter_break

    def generate_fixtures(
        self, teams: List[UUID], competition_id: int, double_round_robin: bool = True
    ) -> List[Fixture]:
        """
        Generate fixtures using the circle method algorithm

        Args:
            teams: List of team IDs
            competition_id: Competition ID for the fixtures
            double_round_robin: If True, each team plays home and away

        Returns:
            List of Fixture objects
        """
        # Work with a copy to avoid modifying the input
        teams_copy = teams.copy()
        if len(teams_copy) % 2 != 0:
            teams_copy.append(None)  # Add dummy team for odd number

        fixtures = []

        # Generate first round robin
        rounds = self._generate_round_robin(teams_copy)

        # Calculate dates for matches
        current_date = self.start_date
        match_week = 1

        for round_num, round_fixtures in enumerate(rounds):
            # Skip to next valid match day
            while current_date.weekday() not in self.match_days:
                current_date += timedelta(days=1)

            # Check for winter break
            if self.winter_break and self.winter_break[0] <= current_date <= self.winter_break[1]:
                current_date = self.winter_break[1] + timedelta(days=1)
                while current_date.weekday() not in self.match_days:
                    current_date += timedelta(days=1)

            for home, away in round_fixtures:
                if home is not None and away is not None:  # Skip dummy team fixtures
                    fixture = Fixture(
                        competition_id=competition_id,
                        home_team_id=str(home),
                        away_team_id=str(away),
                        match_date=current_date,
                        match_week=match_week,
                        status=FixtureStatus.SCHEDULED,
                    )
                    fixtures.append(fixture)

            current_date += timedelta(days=7)  # Move to next week
            match_week += 1

        # Generate second round robin (reverse fixtures)
        if double_round_robin:
            for round_num, round_fixtures in enumerate(rounds):
                # Skip to next valid match day
                while current_date.weekday() not in self.match_days:
                    current_date += timedelta(days=1)

                # Check for winter break
                if (
                    self.winter_break
                    and self.winter_break[0] <= current_date <= self.winter_break[1]
                ):
                    current_date = self.winter_break[1] + timedelta(days=1)
                    while current_date.weekday() not in self.match_days:
                        current_date += timedelta(days=1)

                for home, away in round_fixtures:
                    if home is not None and away is not None:
                        # Reverse home and away
                        fixture = Fixture(
                            competition_id=competition_id,
                            home_team_id=str(away),
                            away_team_id=str(home),
                            match_date=current_date,
                            match_week=match_week,
                            status=FixtureStatus.SCHEDULED,
                        )
                        fixtures.append(fixture)

                current_date += timedelta(days=7)
                match_week += 1

        return fixtures

    def _generate_round_robin(self, teams: List[UUID]) -> List[List[Tuple[UUID, UUID]]]:
        """
        Generate round-robin fixtures using the circle method

        Returns:
            List of rounds, each containing list of (home, away) tuples
        """
        n_teams = len(teams)
        rounds = []

        # Create a copy to manipulate
        team_list = teams.copy()

        for round_num in range(n_teams - 1):
            round_fixtures = []

            # Pair teams
            for i in range(n_teams // 2):
                home = team_list[i]
                away = team_list[n_teams - 1 - i]

                # Alternate home/away for fairness (except first team which is fixed)
                if i == 0 and round_num % 2 == 1:
                    home, away = away, home

                round_fixtures.append((home, away))

            rounds.append(round_fixtures)

            # Rotate teams (keep first team fixed)
            team_list = [team_list[0]] + [team_list[-1]] + team_list[1:-1]

        return rounds

    def randomize_fixture_times(
        self, fixtures: List[Fixture], kick_off_times: List[Tuple[int, int]]
    ) -> None:
        """
        Randomize kick-off times for fixtures on the same day

        Args:
            fixtures: List of fixtures to update
            kick_off_times: List of (hour, minute) tuples for possible kick-off times
        """
        # Group fixtures by date
        fixtures_by_date = {}
        for fixture in fixtures:
            date = fixture.match_date.date()
            if date not in fixtures_by_date:
                fixtures_by_date[date] = []
            fixtures_by_date[date].append(fixture)

        # Assign random kick-off times
        for date, day_fixtures in fixtures_by_date.items():
            # Shuffle fixtures for this day
            random.shuffle(day_fixtures)

            # Assign kick-off times
            for i, fixture in enumerate(day_fixtures):
                if i < len(kick_off_times):
                    hour, minute = kick_off_times[i]
                else:
                    # Default time if more fixtures than time slots
                    hour, minute = kick_off_times[0]

                fixture.match_date = fixture.match_date.replace(hour=hour, minute=minute)
