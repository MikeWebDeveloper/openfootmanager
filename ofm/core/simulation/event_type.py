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
from enum import Enum, auto


class FoulType(Enum):
    OFFENSIVE_FOUL = auto()
    DEFENSIVE_FOUL = auto()


class FoulStrength(Enum):
    LIGHT = auto()
    MEDIUM = auto()
    HIGH = auto()


class FreeKickType(Enum):
    DIRECT_SHOT = auto()
    CROSS = auto()
    PASS = auto()


class EventType(Enum):
    PASS = 0
    DRIBBLE = auto()
    SHOT = auto()
    CROSS = auto()
    FOUL = auto()
    FREE_KICK = auto()
    CORNER_KICK = auto()
    GOAL_KICK = auto()
    PENALTY_KICK = auto()
