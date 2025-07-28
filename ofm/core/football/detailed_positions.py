"""
Detailed position system for OpenFootManager.

Extends the basic position system with specific positional roles
needed for the transfer market and tactical systems.
"""

from enum import IntEnum, auto
from typing import Dict, List

from .positions import Positions


class DetailedPosition(IntEnum):
    """Detailed player positions for tactical and transfer systems."""

    # Goalkeeper
    GK = auto()

    # Defenders
    CB = auto()  # Center Back
    LB = auto()  # Left Back
    RB = auto()  # Right Back
    LWB = auto()  # Left Wing Back
    RWB = auto()  # Right Wing Back

    # Midfielders
    CDM = auto()  # Central Defensive Midfielder
    CM = auto()  # Central Midfielder
    CAM = auto()  # Central Attacking Midfielder
    LM = auto()  # Left Midfielder
    RM = auto()  # Right Midfielder

    # Forwards/Wingers
    LW = auto()  # Left Winger
    RW = auto()  # Right Winger
    CF = auto()  # Center Forward
    ST = auto()  # Striker


# Mapping from detailed positions to basic positions
DETAILED_TO_BASIC: Dict[DetailedPosition, Positions] = {
    DetailedPosition.GK: Positions.GK,
    # Defenders
    DetailedPosition.CB: Positions.DF,
    DetailedPosition.LB: Positions.DF,
    DetailedPosition.RB: Positions.DF,
    DetailedPosition.LWB: Positions.DF,
    DetailedPosition.RWB: Positions.DF,
    # Midfielders
    DetailedPosition.CDM: Positions.MF,
    DetailedPosition.CM: Positions.MF,
    DetailedPosition.CAM: Positions.MF,
    DetailedPosition.LM: Positions.MF,
    DetailedPosition.RM: Positions.MF,
    # Forwards
    DetailedPosition.LW: Positions.FW,
    DetailedPosition.RW: Positions.FW,
    DetailedPosition.CF: Positions.FW,
    DetailedPosition.ST: Positions.FW,
}


# Position families for similar positions
POSITION_FAMILIES: Dict[str, List[DetailedPosition]] = {
    "central_defenders": [DetailedPosition.CB],
    "fullbacks": [DetailedPosition.LB, DetailedPosition.RB],
    "wingbacks": [DetailedPosition.LWB, DetailedPosition.RWB],
    "defensive_midfielders": [DetailedPosition.CDM],
    "central_midfielders": [DetailedPosition.CM, DetailedPosition.CAM],
    "wide_midfielders": [DetailedPosition.LM, DetailedPosition.RM],
    "wingers": [DetailedPosition.LW, DetailedPosition.RW],
    "forwards": [DetailedPosition.CF, DetailedPosition.ST],
}


def get_basic_position(detailed: DetailedPosition) -> Positions:
    """Convert detailed position to basic position."""
    return DETAILED_TO_BASIC.get(detailed, Positions.MF)


def get_similar_positions(position: DetailedPosition) -> List[DetailedPosition]:
    """Get positions similar to the given position."""
    similar = []

    for family, positions in POSITION_FAMILIES.items():
        if position in positions:
            similar.extend(positions)

    # Remove the original position
    similar = [p for p in similar if p != position]

    return similar


def can_play_position(
    player_positions: Dict[DetailedPosition, int],
    target_position: DetailedPosition,
    min_rating: int = 10,
) -> bool:
    """
    Check if a player can play a specific position.

    Args:
        player_positions: Dict of player's position ratings
        target_position: The position to check
        min_rating: Minimum rating required (default 10)

    Returns:
        True if player can play the position
    """
    # Direct position check
    if player_positions.get(target_position, 0) >= min_rating:
        return True

    # Check similar positions with penalty
    similar = get_similar_positions(target_position)
    for pos in similar:
        if player_positions.get(pos, 0) >= min_rating + 5:
            return True

    return False
