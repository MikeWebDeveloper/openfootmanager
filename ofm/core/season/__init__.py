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

from .calendar import CalendarEvent, CalendarEventType, GameCalendar
from .fixture_generator import FixtureGenerator
from .promotion_relegation import PromotionRelegationManager, PromotionRelegationResult
from .season_manager import SeasonManager

__all__ = [
    "FixtureGenerator",
    "SeasonManager",
    "GameCalendar",
    "CalendarEvent",
    "CalendarEventType",
    "PromotionRelegationManager",
    "PromotionRelegationResult",
]
