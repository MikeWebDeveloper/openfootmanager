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

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .league_season import LeagueSeason


class League(Base):
    """League configuration model"""

    __tablename__ = "leagues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(3), nullable=False)  # ISO country code
    level: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 = top division
    num_teams: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    promotion_places: Mapped[int] = mapped_column(Integer, default=0)
    playoff_places: Mapped[int] = mapped_column(Integer, default=0)
    relegation_places: Mapped[int] = mapped_column(Integer, default=0)

    # League above and below for promotion/relegation
    league_above_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("leagues.id"), nullable=True
    )
    league_below_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("leagues.id"), nullable=True
    )

    # Whether the league uses a split system (like Scottish Premiership)
    has_split: Mapped[bool] = mapped_column(Boolean, default=False)
    split_after_rounds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    seasons: Mapped[List["LeagueSeason"]] = relationship("LeagueSeason", back_populates="league")

    def __repr__(self) -> str:
        return f"<League(id={self.id}, name='{self.name}', level={self.level})>"
