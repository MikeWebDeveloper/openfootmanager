"""
Player valuation engine for OpenFootManager.

Calculates player market values based on multiple factors including:
- Age and potential
- Current ability and form
- Position and versatility
- Contract situation
- Injury history
- International caps
- Market conditions
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from ..db.models.transfer import PlayerMarketValue
from ..football.detailed_positions import DetailedPosition
from ..football.player import Player
from ..football.positions import Positions


class PlayerValuationEngine:
    """Sophisticated player valuation system."""

    # Base values by position (in millions)
    BASE_VALUES_DETAILED = {
        DetailedPosition.GK: 10.0,
        DetailedPosition.CB: 15.0,
        DetailedPosition.LB: 12.0,
        DetailedPosition.RB: 12.0,
        DetailedPosition.CDM: 18.0,
        DetailedPosition.CM: 20.0,
        DetailedPosition.CAM: 25.0,
        DetailedPosition.LM: 18.0,
        DetailedPosition.RM: 18.0,
        DetailedPosition.LW: 22.0,
        DetailedPosition.RW: 22.0,
        DetailedPosition.CF: 30.0,
        DetailedPosition.ST: 30.0,
    }

    # Base values by general position (in millions)
    BASE_VALUES = {
        Positions.GK: 10.0,
        Positions.DF: 15.0,
        Positions.MF: 20.0,
        Positions.FW: 25.0,
    }

    # Age value curves
    AGE_MULTIPLIERS = {
        16: 0.3,
        17: 0.4,
        18: 0.6,
        19: 0.8,
        20: 0.9,
        21: 1.0,
        22: 1.1,
        23: 1.2,
        24: 1.3,
        25: 1.4,
        26: 1.4,
        27: 1.3,
        28: 1.2,
        29: 1.0,
        30: 0.8,
        31: 0.6,
        32: 0.4,
        33: 0.3,
        34: 0.2,
        35: 0.15,
    }

    def __init__(self):
        self.market_inflation = 1.0  # Can be adjusted based on game year
        self.transfer_activity_modifier = 1.0  # Based on recent market activity

    def calculate_value(self, player: Player, detailed: bool = False) -> float | Tuple[float, Dict]:
        """
        Calculate a player's market value.

        Args:
            player: The player to value
            detailed: If True, return breakdown of calculation

        Returns:
            Market value in millions, optionally with calculation details
        """
        # Get base value for position
        base_value = self.BASE_VALUES.get(player.get_best_position(), 15.0)

        # Calculate modifiers
        age_modifier = self._calculate_age_modifier(player.age)
        ability_modifier = self._calculate_ability_modifier(player)
        potential_modifier = self._calculate_potential_modifier(player)
        form_modifier = self._calculate_form_modifier(player)
        contract_modifier = self._calculate_contract_modifier(player)
        injury_modifier = self._calculate_injury_modifier(player)
        international_modifier = self._calculate_international_modifier(player)
        versatility_modifier = self._calculate_versatility_modifier(player)

        # Calculate final value
        value = (
            base_value
            * age_modifier
            * ability_modifier
            * potential_modifier
            * form_modifier
            * contract_modifier
            * injury_modifier
            * international_modifier
            * versatility_modifier
            * self.market_inflation
            * self.transfer_activity_modifier
        )

        # Apply minimum and maximum caps
        value = max(0.1, min(value, 300.0))  # Between 100k and 300m

        if detailed:
            details = {
                "base_value": base_value,
                "age_modifier": age_modifier,
                "ability_modifier": ability_modifier,
                "potential_modifier": potential_modifier,
                "form_modifier": form_modifier,
                "contract_modifier": contract_modifier,
                "injury_modifier": injury_modifier,
                "international_modifier": international_modifier,
                "versatility_modifier": versatility_modifier,
                "market_inflation": self.market_inflation,
                "final_value": value,
            }
            return value, details

        return value

    def _calculate_age_modifier(self, age: int) -> float:
        """Calculate value modifier based on age."""
        if age < 16:
            return 0.2
        elif age > 35:
            return 0.1
        return self.AGE_MULTIPLIERS.get(age, 0.5)

    def _calculate_ability_modifier(self, player: Player) -> float:
        """Calculate modifier based on current ability."""
        # Use the player's primary position for overall calculation
        position = player.positions[0] if player.positions else Positions.MF
        overall = player.attributes.get_overall(position)

        if overall >= 90:
            return 4.0  # World class
        elif overall >= 85:
            return 3.0  # Elite
        elif overall >= 80:
            return 2.2  # Very good
        elif overall >= 75:
            return 1.6  # Good
        elif overall >= 70:
            return 1.2  # Decent
        elif overall >= 65:
            return 0.8  # Average
        elif overall >= 60:
            return 0.5  # Below average
        else:
            return 0.3  # Poor

    def _calculate_potential_modifier(self, player: Player) -> float:
        """Calculate modifier based on potential vs current ability."""
        position = player.positions[0] if player.positions else Positions.MF
        current = player.attributes.get_overall(position)
        potential = player.potential_ability

        if player.age <= 23:
            # Young players get significant boost from high potential
            potential_gap = potential - current
            if potential_gap > 20:
                return 1.8
            elif potential_gap > 15:
                return 1.5
            elif potential_gap > 10:
                return 1.3
            elif potential_gap > 5:
                return 1.15

        return 1.0

    def _calculate_form_modifier(self, player: Player) -> float:
        """Calculate modifier based on recent form."""
        # TODO: Implement when match history is available
        # For now, use fitness as proxy
        if player.fitness >= 95:
            return 1.1
        elif player.fitness >= 85:
            return 1.05
        elif player.fitness >= 70:
            return 1.0
        elif player.fitness >= 50:
            return 0.9
        else:
            return 0.8

    def _calculate_contract_modifier(self, player: Player) -> float:
        """Calculate modifier based on contract situation."""
        if not player.contract:
            return 0.1  # Free agent

        years_remaining = player.contract.years_remaining

        if years_remaining >= 4:
            return 1.0
        elif years_remaining >= 3:
            return 0.9
        elif years_remaining >= 2:
            return 0.7
        elif years_remaining >= 1:
            return 0.4
        else:
            return 0.15  # Less than a year

    def _calculate_injury_modifier(self, player: Player) -> float:
        """Calculate modifier based on injury history."""
        if player.injury and player.injury.is_active():
            severity = player.injury.severity
            if severity >= 8:
                return 0.5  # Serious injury
            elif severity >= 5:
                return 0.7  # Moderate injury
            else:
                return 0.9  # Minor injury

        # TODO: Check injury history when available
        return 1.0

    def _calculate_international_modifier(self, player: Player) -> float:
        """Calculate modifier based on international status."""
        # TODO: Implement when international data is available
        # For now, use nationality as proxy
        if player.nationality in ["England", "Spain", "Germany", "Italy", "France"]:
            return 1.1  # Major football nation
        return 1.0

    def _calculate_versatility_modifier(self, player: Player) -> float:
        """Calculate modifier based on positional versatility."""
        # Currently positions is a list, not a dict with ratings
        # So we'll use the number of positions as a simple versatility measure
        num_positions = len(player.positions)

        if num_positions >= 3:
            return 1.15
        elif num_positions >= 2:
            return 1.08
        elif num_positions >= 1:
            return 1.0

        return 0.9  # No positions defined

    def estimate_wage_demands(self, player: Player, transfer_fee: float) -> float:
        """
        Estimate weekly wage demands based on value and transfer fee.

        Args:
            player: The player
            transfer_fee: The agreed transfer fee

        Returns:
            Estimated weekly wage demand
        """
        base_value = self.calculate_value(player)  # This is in millions

        # Higher transfer fees often mean higher wages
        # Convert transfer_fee to millions for comparison
        transfer_fee_millions = transfer_fee / 1_000_000
        fee_factor = 1.0 + (transfer_fee_millions / base_value - 1.0) * 0.3

        # Base wage calculation
        # A player worth 25M might earn 100-200k per week
        # So roughly 20-40% of value annually
        base_wage = base_value * 1_000_000 * 0.25 / 52  # 25% of value annually, divided by 52 weeks

        # Apply modifiers
        age_factor = 1.0
        if player.age >= 28:
            age_factor = 1.2  # Older players want security
        elif player.age <= 21:
            age_factor = 0.8  # Young players accept lower wages

        position = player.positions[0] if player.positions else Positions.MF
        ability_factor = player.attributes.get_overall(position) / 70  # Normalized around 70

        return base_wage * fee_factor * age_factor * ability_factor

    def calculate_release_clause(self, player: Player, multiplier: float = 1.5) -> float:
        """
        Calculate a reasonable release clause for a player.

        Args:
            player: The player
            multiplier: Multiple of market value (default 1.5x)

        Returns:
            Suggested release clause amount
        """
        market_value = self.calculate_value(player)

        # Young players with high potential get higher multipliers
        position = player.positions[0] if player.positions else Positions.MF
        if (
            player.age <= 23
            and player.potential_ability - player.attributes.get_overall(position) > 10
        ):
            multiplier *= 1.3

        return market_value * multiplier

    def save_valuation(self, player: Player, session) -> PlayerMarketValue:
        """Save current valuation to database."""
        value, details = self.calculate_value(player, detailed=True)

        market_value = PlayerMarketValue(
            player_id=player.id,
            value=value,
            base_value=details["base_value"],
            age_modifier=details["age_modifier"],
            ability_modifier=details["ability_modifier"],
            potential_modifier=details["potential_modifier"],
            form_modifier=details["form_modifier"],
            contract_modifier=details["contract_modifier"],
            injury_modifier=details["injury_modifier"],
            calculation_details=details,
        )

        session.add(market_value)
        session.commit()

        return market_value
