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

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class CompetitionType(Enum):
    LEAGUE = "league"
    CUP = "cup"
    TOURNAMENT = "tournament"
    FRIENDLY = "friendly"


class Competition(Base):
    """Base competition model for all types of competitions"""

    __tablename__ = "competitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    short_name: Mapped[str] = mapped_column(String(20), nullable=False)
    type: Mapped[CompetitionType] = mapped_column(SQLEnum(CompetitionType), nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(3))  # ISO country code
    season: Mapped[int] = mapped_column(Integer, nullable=False)  # e.g., 2024
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    fixtures: Mapped[List["Fixture"]] = relationship("Fixture", back_populates="competition")

    def __repr__(self) -> str:
        return f"<Competition(id={self.id}, name='{self.name}', season={self.season})>"