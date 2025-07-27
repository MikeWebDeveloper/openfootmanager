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

from typing import List

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class LeagueSeason(Base):
    """Represents a specific season instance of a league"""

    __tablename__ = "league_seasons"
    __table_args__ = (UniqueConstraint("league_id", "competition_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    league_id: Mapped[int] = mapped_column(Integer, ForeignKey("leagues.id"), nullable=False)
    competition_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("competitions.id"), nullable=False
    )

    # Relationships
    league: Mapped["League"] = relationship("League", back_populates="seasons")
    competition: Mapped["Competition"] = relationship("Competition")
    table_entries: Mapped[List["LeagueTableEntry"]] = relationship(
        "LeagueTableEntry", back_populates="league_season"
    )
    
    # Teams participating in this season
    team_ids: Mapped[List[int]] = mapped_column(Integer, nullable=False)  # Will be JSON array

    def __repr__(self) -> str:
        return f"<LeagueSeason(id={self.id}, league_id={self.league_id})>"