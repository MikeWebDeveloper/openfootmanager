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
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .competition import Competition


class FixtureStatus(Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class Fixture(Base):
    """Represents a match fixture between two teams"""

    __tablename__ = "fixtures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    competition_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("competitions.id"), nullable=False
    )
    home_team_id: Mapped[str] = mapped_column(String(36), nullable=False)
    away_team_id: Mapped[str] = mapped_column(String(36), nullable=False)
    match_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    match_week: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[FixtureStatus] = mapped_column(
        SQLEnum(FixtureStatus), default=FixtureStatus.SCHEDULED
    )

    # Score fields (null until match is played)
    home_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    away_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Extra time and penalties (for cup competitions)
    home_score_aet: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    away_score_aet: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    home_score_pens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    away_score_pens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Stadium/venue
    stadium_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    attendance: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    competition: Mapped["Competition"] = relationship("Competition", back_populates="fixtures")

    def __repr__(self) -> str:
        return (
            f"<Fixture(id={self.id}, home={self.home_team_id}, "
            f"away={self.away_team_id}, date={self.match_date})>"
        )

    @property
    def is_completed(self) -> bool:
        return self.status == FixtureStatus.COMPLETED

    @property
    def is_draw(self) -> bool:
        if not self.is_completed:
            return False
        return self.home_score == self.away_score

    @property
    def winner_id(self) -> Optional[str]:
        """Returns the ID of the winning team, or None if draw/not completed"""
        if not self.is_completed or self.is_draw:
            return None

        # Check penalty shootout first
        if self.home_score_pens is not None and self.away_score_pens is not None:
            return (
                self.home_team_id
                if self.home_score_pens > self.away_score_pens
                else self.away_team_id
            )

        # Check after extra time
        if self.home_score_aet is not None and self.away_score_aet is not None:
            return (
                self.home_team_id
                if self.home_score_aet > self.away_score_aet
                else self.away_team_id
            )

        # Regular time
        return self.home_team_id if self.home_score > self.away_score else self.away_team_id
