"""
Transfer and contract negotiation system for OpenFootManager.

Handles the complex negotiation mechanics between clubs and players including:
- Transfer fee negotiations
- Contract terms negotiations
- Agent involvement
- Negotiation strategies
- Deal structures (loans, options, etc.)
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple

from ..db.models.transfer import (
    ContractOffer,
    ContractStatus,
    TransferNegotiation,
    TransferStatus,
    TransferType,
)
from ..football.club import Club
from ..football.player import Player
from .valuation import PlayerValuationEngine


class NegotiationStrategy(Enum):
    """AI negotiation strategies."""

    AGGRESSIVE = "aggressive"  # Start low, increase slowly
    FAIR = "fair"  # Start near valuation
    DESPERATE = "desperate"  # Will overpay to get player
    HARDBALL = "hardball"  # Won't budge much from initial position


class TransferNegotiator:
    """Handles transfer fee negotiations between clubs."""

    def __init__(self, valuation_engine: PlayerValuationEngine = None):
        self.valuation_engine = valuation_engine or PlayerValuationEngine()
        self.negotiation_rounds = 0
        self.max_rounds = 10  # Maximum back-and-forth

    def initiate_negotiation(
        self,
        player: Player,
        buying_club: Club,
        selling_club: Club,
        transfer_type: TransferType = TransferType.PERMANENT,
        initial_offer: Optional[float] = None,
    ) -> TransferNegotiation:
        """
        Start a new transfer negotiation.

        Args:
            player: The player being transferred
            buying_club: The club making the offer
            selling_club: The player's current club
            transfer_type: Type of transfer (permanent, loan, etc.)
            initial_offer: Initial offer amount (auto-calculated if None)

        Returns:
            New TransferNegotiation instance
        """
        player_value = self.valuation_engine.calculate_value(player)

        if initial_offer is None:
            # Calculate initial offer based on buying club's strategy
            initial_offer = self._calculate_initial_offer(
                player_value, buying_club, player
            )

        negotiation = TransferNegotiation(
            player_id=player.id,
            selling_club_id=selling_club.id,
            buying_club_id=buying_club.id,
            status=TransferStatus.NEGOTIATING,
            transfer_type=transfer_type,
            initial_offer=initial_offer,
            current_offer=initial_offer,
            offer_history=[
                {
                    "round": 0,
                    "offer": initial_offer,
                    "from": "buying_club",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ],
        )

        return negotiation

    def make_counter_offer(
        self,
        negotiation: TransferNegotiation,
        amount: float,
        additional_terms: Optional[Dict] = None,
    ) -> Tuple[bool, str]:
        """
        Make a counter-offer in ongoing negotiation.

        Args:
            negotiation: The ongoing negotiation
            amount: New offer amount
            additional_terms: Additional terms (sell-on clause, bonuses, etc.)

        Returns:
            Tuple of (accepted, message)
        """
        self.negotiation_rounds += 1

        if self.negotiation_rounds >= self.max_rounds:
            negotiation.status = TransferStatus.REJECTED
            return False, "Negotiations have broken down after too many rounds"

        # Update offer history
        negotiation.offer_history.append(
            {
                "round": self.negotiation_rounds,
                "offer": amount,
                "from": "selling_club",
                "terms": additional_terms,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        negotiation.current_offer = amount

        # Check if buying club will accept
        accepted = self._evaluate_counter_offer(negotiation, amount)

        if accepted:
            negotiation.status = TransferStatus.AGREED
            negotiation.agreed_fee = amount
            if additional_terms:
                negotiation.sell_on_percentage = additional_terms.get("sell_on", 0)
                negotiation.performance_bonuses = additional_terms.get("bonuses", {})
            return True, "Transfer fee agreed"

        return False, "Counter-offer made, awaiting response"

    def negotiate_loan_terms(
        self,
        negotiation: TransferNegotiation,
        loan_fee: float,
        wage_percentage: float,
        buy_option: Optional[float] = None,
        buy_obligation: bool = False,
    ) -> Tuple[bool, str]:
        """
        Negotiate loan-specific terms.

        Args:
            negotiation: The ongoing negotiation
            loan_fee: Fee for the loan
            wage_percentage: Percentage of wages paid by loaning club
            buy_option: Optional future purchase price
            buy_obligation: Whether purchase is mandatory

        Returns:
            Tuple of (accepted, message)
        """
        if negotiation.transfer_type not in [
            TransferType.LOAN,
            TransferType.LOAN_TO_BUY,
        ]:
            return False, "Not a loan negotiation"

        negotiation.loan_fee = loan_fee
        negotiation.wage_percentage = wage_percentage
        negotiation.buy_option = buy_option
        negotiation.buy_obligation = buy_obligation

        # Evaluate loan terms
        player = negotiation.player
        acceptable = self._evaluate_loan_terms(negotiation, player)

        if acceptable:
            negotiation.status = TransferStatus.AGREED
            return True, "Loan terms agreed"

        return False, "Loan terms under negotiation"

    def _calculate_initial_offer(
        self, player_value: float, buying_club: Club, player: Player
    ) -> float:
        """Calculate initial offer based on club strategy and finances."""
        strategy = self._determine_club_strategy(buying_club, player)

        offer_multipliers = {
            NegotiationStrategy.AGGRESSIVE: 0.7,
            NegotiationStrategy.FAIR: 0.9,
            NegotiationStrategy.DESPERATE: 1.1,
            NegotiationStrategy.HARDBALL: 0.6,
        }

        base_offer = player_value * offer_multipliers[strategy]

        # Adjust for club finances
        if buying_club.transfer_budget < base_offer:
            base_offer = buying_club.transfer_budget * 0.8  # Leave some budget

        return round(base_offer, 1)

    def _determine_club_strategy(
        self, club: Club, player: Player
    ) -> NegotiationStrategy:
        """Determine negotiation strategy based on club situation."""
        # TODO: Implement based on club AI personality, needs, finances
        # For now, return fair strategy
        return NegotiationStrategy.FAIR

    def _evaluate_counter_offer(
        self, negotiation: TransferNegotiation, amount: float
    ) -> bool:
        """Evaluate if buying club will accept counter-offer."""
        buying_club = negotiation.buying_club
        player = negotiation.player
        player_value = self.valuation_engine.calculate_value(player)

        # Check if within budget
        if amount > buying_club.transfer_budget:
            return False

        # Check if reasonable compared to valuation
        if amount > player_value * 1.5:
            return False  # Too expensive

        # Check negotiation progress
        current_gap = negotiation.current_offer - amount

        # Accept if gap is closing reasonably
        if abs(current_gap) < player_value * 0.1:
            return True

        return False

    def _evaluate_loan_terms(
        self, negotiation: TransferNegotiation, player: Player
    ) -> bool:
        """Evaluate if loan terms are acceptable."""
        # Check wage coverage
        if negotiation.wage_percentage < 50:
            return False  # Want at least half wages covered

        # Check loan fee is reasonable
        player_value = self.valuation_engine.calculate_value(player)
        if negotiation.loan_fee < player_value * 0.05:
            return False  # Too low

        return True


class ContractNegotiator:
    """Handles contract negotiations with players."""

    def __init__(self, valuation_engine: PlayerValuationEngine = None):
        self.valuation_engine = valuation_engine or PlayerValuationEngine()

    def create_contract_offer(
        self,
        player: Player,
        club: Club,
        negotiation: TransferNegotiation,
        years: int = 4,
        wage_offer: Optional[float] = None,
    ) -> ContractOffer:
        """
        Create initial contract offer to a player.

        Args:
            player: The player
            club: The offering club
            negotiation: Associated transfer negotiation
            years: Contract length in years
            wage_offer: Weekly wage offer (auto-calculated if None)

        Returns:
            New ContractOffer instance
        """
        if wage_offer is None:
            wage_offer = self._calculate_wage_offer(
                player, negotiation.agreed_fee or negotiation.current_offer
            )

        # Calculate player's wage demands
        wage_demand = self.valuation_engine.estimate_wage_demands(
            player, negotiation.agreed_fee or negotiation.current_offer
        )

        contract = ContractOffer(
            negotiation_id=negotiation.id,
            player_id=player.id,
            club_id=club.id,
            status=ContractStatus.PROPOSED,
            length_years=years,
            weekly_wage=wage_offer,
            player_demanded_wage=wage_demand,
            signing_bonus=self._calculate_signing_bonus(player, wage_offer),
            agent_fee=self._calculate_agent_fee(
                negotiation.agreed_fee or negotiation.current_offer
            ),
        )

        return contract

    def negotiate_contract(
        self,
        contract: ContractOffer,
        new_wage: Optional[float] = None,
        new_bonus: Optional[float] = None,
        new_clauses: Optional[Dict] = None,
    ) -> Tuple[bool, str]:
        """
        Negotiate contract terms with player.

        Args:
            contract: The contract offer
            new_wage: New wage offer
            new_bonus: New signing bonus
            new_clauses: Additional clauses

        Returns:
            Tuple of (accepted, message)
        """
        contract.negotiation_rounds += 1

        if contract.negotiation_rounds > 5:
            contract.status = ContractStatus.REJECTED
            return False, "Player has ended negotiations"

        if new_wage:
            contract.weekly_wage = new_wage
        if new_bonus:
            contract.signing_bonus = new_bonus
        if new_clauses:
            contract.release_clause = new_clauses.get("release_clause")
            contract.wage_rise_percentage = new_clauses.get("wage_rise", 0)

        # Check if player accepts
        if self._player_accepts_contract(contract):
            contract.status = ContractStatus.AGREED
            contract.final_wage = contract.weekly_wage
            return True, "Contract terms agreed"

        # Generate counter-demand
        counter_wage = self._calculate_counter_demand(contract)
        return False, f"Player demands {counter_wage:,.0f} per week"

    def _calculate_wage_offer(self, player: Player, transfer_fee: float) -> float:
        """Calculate initial wage offer based on various factors."""
        base_wage = self.valuation_engine.estimate_wage_demands(player, transfer_fee)

        # Start slightly below expected demands
        return base_wage * 0.85

    def _calculate_signing_bonus(self, player: Player, wage: float) -> float:
        """Calculate appropriate signing bonus."""
        # Typically 10-20 weeks of wages
        weeks = 10
        if player.attributes.get_overall() >= 80:
            weeks = 20
        elif player.attributes.get_overall() >= 75:
            weeks = 15

        return wage * weeks

    def _calculate_agent_fee(self, transfer_fee: float) -> float:
        """Calculate agent fee (typically 5-10% of transfer)."""
        if transfer_fee == 0:
            return 50000  # Minimum agent fee

        percentage = 0.07  # 7% average
        return transfer_fee * percentage

    def _player_accepts_contract(self, contract: ContractOffer) -> bool:
        """Determine if player accepts current contract terms."""
        wage_ratio = contract.weekly_wage / contract.player_demanded_wage

        # Accept if close to demands
        if wage_ratio >= 0.95:
            return True

        # Consider other factors
        if wage_ratio >= 0.85:
            # Might accept with good bonuses/clauses
            if contract.signing_bonus > contract.player_demanded_wage * 15:
                return True
            if (
                contract.release_clause
                and contract.release_clause < contract.player_demanded_wage * 1000
            ):
                return True

        return False

    def _calculate_counter_demand(self, contract: ContractOffer) -> float:
        """Calculate player's counter wage demand."""
        current_ratio = contract.weekly_wage / contract.player_demanded_wage

        if current_ratio < 0.7:
            # Far too low, stick to original demand
            return contract.player_demanded_wage
        elif current_ratio < 0.85:
            # Getting closer, reduce demand slightly
            return contract.player_demanded_wage * 0.95
        else:
            # Very close, meet in middle
            return (contract.weekly_wage + contract.player_demanded_wage) / 2
