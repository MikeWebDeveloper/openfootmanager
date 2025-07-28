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
from dataclasses import dataclass
from uuid import UUID

from .player import PlayerTeam


class PlayerSubstitutionError(Exception):
    pass


@dataclass
class Club:
    club_id: UUID
    name: str
    country: str
    location: str
    default_formation: str
    # TODO: Implement a serializable stadium object
    squad: list[PlayerTeam]
    stadium: str
    stadium_capacity: int
    transfer_budget: float = 0.0
    wage_budget: float = 0.0
    reputation: int = 50  # 0-100 scale

    @classmethod
    def get_from_dict(cls, club: dict, players: list[PlayerTeam]):
        club_id = UUID(int=club["id"])
        return cls(
            club_id,
            club["name"],
            club["country"],
            club["location"],
            club["default_formation"],
            players,
            club["stadium"],
            club["stadium_capacity"],
            club.get("transfer_budget", 0.0),
            club.get("wage_budget", 0.0),
            club.get("reputation", 50),
        )

    def serialize(self) -> dict:
        return {
            "id": self.club_id.int,
            "name": self.name,
            "country": self.country,
            "location": self.location,
            "default_formation": self.default_formation,
            "squad": [player.details.player_id.int for player in self.squad],
            "stadium": self.stadium,
            "stadium_capacity": self.stadium_capacity,
            "transfer_budget": self.transfer_budget,
            "wage_budget": self.wage_budget,
            "reputation": self.reputation,
        }

    @property
    def players(self) -> list:
        """Get list of players (convenience property for transfer system)."""
        return [player.details for player in self.squad]
    
    @property
    def id(self) -> UUID:
        """Alias for club_id for consistency with database models."""
        return self.club_id
    
    def __repr__(self):
        return self.name.encode("utf-8").decode("unicode_escape")

    def __str__(self):
        return self.name.encode("utf-8").decode("unicode_escape")
