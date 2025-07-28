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

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .league_season import LeagueSeason


class LeagueTableEntry(Base):
    """Represents a team's position in a league table"""

    __tablename__ = "league_table_entries"
    __table_args__ = (UniqueConstraint("league_season_id", "team_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    league_season_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("league_seasons.id"), nullable=False
    )
    team_id: Mapped[str] = mapped_column(String(36), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    # Match statistics
    played: Mapped[int] = mapped_column(Integer, default=0)
    won: Mapped[int] = mapped_column(Integer, default=0)
    drawn: Mapped[int] = mapped_column(Integer, default=0)
    lost: Mapped[int] = mapped_column(Integer, default=0)
    goals_for: Mapped[int] = mapped_column(Integer, default=0)
    goals_against: Mapped[int] = mapped_column(Integer, default=0)

    # Form (last 5 matches: W/D/L)
    form: Mapped[str] = mapped_column(String(5), default="")

    # Relationships
    league_season: Mapped["LeagueSeason"] = relationship(
        "LeagueSeason", back_populates="table_entries"
    )

    @property
    def points(self) -> int:
        """Calculate points (3 for win, 1 for draw)"""
        return (self.won * 3) + self.drawn

    @property
    def goal_difference(self) -> int:
        """Calculate goal difference"""
        return self.goals_for - self.goals_against

    def update_after_match(self, goals_scored: int, goals_conceded: int, result: str) -> None:
        """Update table entry after a match"""
        self.played += 1
        self.goals_for += goals_scored
        self.goals_against += goals_conceded

        if result == "W":
            self.won += 1
        elif result == "D":
            self.drawn += 1
        else:  # "L"
            self.lost += 1

        # Update form (keep last 5 results)
        self.form = (self.form + result)[-5:]

    def __repr__(self) -> str:
        return (
            f"<LeagueTableEntry(position={self.position}, team={self.team_id}, "
            f"points={self.points}, gd={self.goal_difference})>"
        )
