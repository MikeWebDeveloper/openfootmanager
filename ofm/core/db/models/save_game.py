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

import enum
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Enum, Integer, String, Text

from .base import Base


class SaveType(enum.Enum):
    """Type of save game"""

    MANUAL = "manual"
    AUTOSAVE = "autosave"
    CHECKPOINT = "checkpoint"


class SaveGame(Base):
    """Represents a saved game state"""

    __tablename__ = "save_games"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    save_type = Column(Enum(SaveType), nullable=False, default=SaveType.MANUAL)

    # Version information for compatibility
    game_version = Column(String(20), nullable=False)
    save_version = Column(Integer, nullable=False, default=1)

    # Game state
    current_date = Column(DateTime, nullable=False)
    manager_name = Column(String(100), nullable=False)
    club_id = Column(String(36), nullable=False)  # UUID as string

    # Save metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_modified = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    play_time = Column(Integer, default=0)  # Total playtime in seconds

    # Compressed game state
    game_state = Column(Text, nullable=False)  # JSON compressed string

    # Additional metadata
    save_metadata = Column(
        JSON, default=dict
    )  # Extra info like league position, finances, etc.

    def __repr__(self):
        return f"<SaveGame(name='{self.name}', manager='{self.manager_name}', date='{self.current_date}')>"
