"""
AI Transfer Manager for OpenFootManager.

Handles transfer strategies and decisions for AI-controlled clubs including:
- Squad analysis and needs assessment
- Transfer target identification
- Negotiation strategies
- Budget management
- Squad building philosophy
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from ..db.models.transfer import ContractStatus, TransferStatus
from ..football.club import Club
from ..football.detailed_positions import DetailedPosition
from ..football.player import Player
from .market import TransferMarket
from .search import SearchCriteria


class TransferPhilosophy(Enum):
    """AI club transfer philosophies."""

    YOUTH_DEVELOPMENT = "youth"  # Focus on young players with potential
    ESTABLISHED_STARS = "stars"  # Buy proven quality
    MONEYBALL = "moneyball"  # Value for money, analytics-driven
    DOMESTIC_FOCUS = "domestic"  # Prefer local players
    LOAN_ARMY = "loans"  # Build through loans
    FREE_AGENTS = "free"  # Focus on free transfers


class SquadRole(Enum):
    """Player roles in squad planning."""

    STARTER = "starter"
    ROTATION = "rotation"
    BACKUP = "backup"
    PROSPECT = "prospect"
    SURPLUS = "surplus"


@dataclass
class SquadNeed:
    """Represents a squad need."""

    position: DetailedPosition
    priority: int  # 1-10, 10 being critical
    role: SquadRole
    max_age: Optional[int] = None
    min_ability: Optional[int] = None


class AITransferManager:
    """AI manager for automated transfer decisions."""

    def __init__(self, club: Club, market: TransferMarket):
        self.club = club
        self.market = market
        self.philosophy = self._determine_philosophy()
        self.squad_needs = []
        self.transfer_targets = []
        self.outgoing_players = []

    def plan_transfer_window(self) -> Dict:
        """
        Create comprehensive transfer plan for the window.

        Returns:
            Transfer plan with targets, sales, and priorities
        """
        # Analyze current squad
        squad_analysis = self._analyze_squad()

        # Identify needs
        self.squad_needs = self._identify_squad_needs(squad_analysis)

        # Identify surplus players
        self.outgoing_players = self._identify_surplus_players(squad_analysis)

        # Calculate available budget
        budget = self._calculate_transfer_budget()

        # Find transfer targets
        self.transfer_targets = self._identify_transfer_targets(budget)

        # Create action plan
        plan = {
            "philosophy": self.philosophy.value,
            "budget": budget,
            "needs": [
                {
                    "position": need.position.value,
                    "priority": need.priority,
                    "role": need.role.value,
                }
                for need in self.squad_needs
            ],
            "targets": [
                {
                    "player": target["player"].name,
                    "position": target["player"].get_best_position().value,
                    "value": target["value"],
                    "priority": target["priority"],
                }
                for target in self.transfer_targets[:10]
            ],
            "sales": [
                {
                    "player": player.name,
                    "reason": reason,
                    "asking_price": self.market.valuation_engine.calculate_value(
                        player
                    ),
                }
                for player, reason in self.outgoing_players
            ],
        }

        return plan

    def execute_transfer_plan(self) -> List[Dict]:
        """
        Execute the transfer plan, making actual bids and sales.

        Returns:
            List of completed transactions
        """
        transactions = []

        # List surplus players first
        for player, reason in self.outgoing_players:
            listing = self.market.list_player(player, self.club)
            transactions.append(
                {
                    "type": "listed",
                    "player": player.name,
                    "asking_price": listing.asking_price,
                }
            )

        # Make bids for targets
        for target in self.transfer_targets:
            if self._should_bid_for_target(target):
                transaction = self._attempt_signing(target)
                if transaction:
                    transactions.append(transaction)

        return transactions

    def respond_to_bid(
        self, player: Player, bid_amount: float, buying_club: Club
    ) -> Tuple[bool, Optional[float]]:
        """
        Respond to incoming transfer bid.

        Args:
            player: Player being bid for
            bid_amount: Offer amount
            buying_club: Club making the bid

        Returns:
            Tuple of (accept, counter_offer)
        """
        # Check if player is listed
        is_listed = any(p[0].id == player.id for p in self.outgoing_players)

        # Get player value
        player_value = self.market.valuation_engine.calculate_value(player)

        # Determine importance to squad
        importance = self._assess_player_importance(player)

        if is_listed:
            # More willing to sell
            if bid_amount >= player_value * 0.8:
                return True, None
            else:
                return False, player_value * 0.9

        if importance == SquadRole.SURPLUS:
            # Willing to sell at market value
            if bid_amount >= player_value:
                return True, None
            else:
                return False, player_value * 1.1

        if importance == SquadRole.STARTER:
            # Only sell for premium
            if bid_amount >= player_value * 1.5:
                return True, None
            else:
                return False, player_value * 2.0

        # Default: slightly above value
        if bid_amount >= player_value * 1.2:
            return True, None
        else:
            return False, player_value * 1.3

    def _determine_philosophy(self) -> TransferPhilosophy:
        """Determine club's transfer philosophy based on various factors."""
        # TODO: Base on club traditions, finances, league position
        # For now, assign based on budget
        if self.club.transfer_budget > 100000000:
            return TransferPhilosophy.ESTABLISHED_STARS
        elif self.club.transfer_budget > 50000000:
            return TransferPhilosophy.MONEYBALL
        elif self.club.transfer_budget > 20000000:
            return TransferPhilosophy.YOUTH_DEVELOPMENT
        else:
            return TransferPhilosophy.FREE_AGENTS

    def _analyze_squad(self) -> Dict:
        """Comprehensive squad analysis."""
        analysis = {
            "total_players": len(self.club.players),
            "average_age": 0,
            "average_ability": 0,
            "positions": {},
            "age_profile": {"U21": 0, "21-25": 0, "26-30": 0, "Over30": 0},
            "contract_situations": {"Expiring": 0, "Long": 0},
            "injury_prone": [],
        }

        if not self.club.players:
            return analysis

        total_age = 0
        total_ability = 0

        for player in self.club.players:
            # Age analysis
            total_age += player.age
            if player.age < 21:
                analysis["age_profile"]["U21"] += 1
            elif player.age <= 25:
                analysis["age_profile"]["21-25"] += 1
            elif player.age <= 30:
                analysis["age_profile"]["26-30"] += 1
            else:
                analysis["age_profile"]["Over30"] += 1

            # Ability analysis
            total_ability += player.attributes.get_overall()

            # Position depth
            best_pos = player.get_best_position()
            if best_pos not in analysis["positions"]:
                analysis["positions"][best_pos] = []
            analysis["positions"][best_pos].append(player)

            # Contract analysis
            if player.contract:
                if player.contract.years_remaining < 1:
                    analysis["contract_situations"]["Expiring"] += 1
                elif player.contract.years_remaining > 3:
                    analysis["contract_situations"]["Long"] += 1

        analysis["average_age"] = total_age / len(self.club.players)
        analysis["average_ability"] = total_ability / len(self.club.players)

        return analysis

    def _identify_squad_needs(self, analysis: Dict) -> List[SquadNeed]:
        """Identify positions that need strengthening."""
        needs = []

        # Define minimum players per position
        position_requirements = {
            DetailedPosition.GK: 3,
            DetailedPosition.CB: 4,
            DetailedPosition.LB: 2,
            DetailedPosition.RB: 2,
            DetailedPosition.CDM: 2,
            DetailedPosition.CM: 4,
            DetailedPosition.CAM: 2,
            DetailedPosition.LW: 2,
            DetailedPosition.RW: 2,
            DetailedPosition.ST: 3,
        }

        # Check each position
        for position, min_required in position_requirements.items():
            current_players = analysis["positions"].get(position, [])

            if len(current_players) < min_required:
                # Critical need
                priority = 10 if len(current_players) == 0 else 8
                needs.append(
                    SquadNeed(
                        position=position,
                        priority=priority,
                        role=(
                            SquadRole.STARTER
                            if len(current_players) == 0
                            else SquadRole.ROTATION
                        ),
                    )
                )
            elif len(current_players) == min_required:
                # Could use depth
                quality_players = [
                    p for p in current_players if p.attributes.get_overall() >= 70
                ]
                if len(quality_players) < min_required:
                    needs.append(
                        SquadNeed(
                            position=position,
                            priority=5,
                            role=SquadRole.ROTATION,
                            min_ability=70,
                        )
                    )

        # Sort by priority
        needs.sort(key=lambda x: x.priority, reverse=True)

        return needs

    def _identify_surplus_players(self, analysis: Dict) -> List[Tuple[Player, str]]:
        """Identify players who could be sold."""
        surplus = []

        for position, players in analysis["positions"].items():
            if len(players) > 4:  # Too many in one position
                # Sort by ability
                players.sort(key=lambda p: p.attributes.get_overall())

                # Mark worst as surplus
                for player in players[: len(players) - 4]:
                    surplus.append((player, "Surplus to requirements"))

        # Add aging players on high wages
        for player in self.club.players:
            if (
                player.age > 32
                and player.contract
                and player.contract.weekly_wage > 100000
            ):
                if not any(p[0].id == player.id for p in surplus):
                    surplus.append((player, "High wages for age"))

        # Add unhappy players (when morale system exists)
        # TODO: Check player morale

        return surplus

    def _calculate_transfer_budget(self) -> float:
        """Calculate available transfer budget including potential sales."""
        base_budget = self.club.transfer_budget

        # Add potential income from sales
        for player, _ in self.outgoing_players:
            estimated_fee = self.market.valuation_engine.calculate_value(player) * 0.8
            base_budget += estimated_fee

        # Reserve some for wages
        wage_reserve = base_budget * 0.2

        return base_budget - wage_reserve

    def _identify_transfer_targets(self, budget: float) -> List[Dict]:
        """Find suitable transfer targets within budget."""
        targets = []

        for need in self.squad_needs[:5]:  # Focus on top 5 needs
            # Build search criteria based on philosophy
            criteria = self._build_search_criteria(need, budget)

            # Search for players
            results = self.market.search_engine.search(criteria, self.club)

            # Score and rank results
            for player, info in results[:5]:  # Top 5 per position
                score = self._score_transfer_target(player, info, need)
                targets.append(
                    {
                        "player": player,
                        "value": info["value"],
                        "info": info,
                        "need": need,
                        "score": score,
                        "priority": need.priority,
                    }
                )

        # Sort by score
        targets.sort(key=lambda x: x["score"], reverse=True)

        return targets

    def _build_search_criteria(self, need: SquadNeed, budget: float) -> SearchCriteria:
        """Build search criteria based on need and philosophy."""
        criteria = SearchCriteria(
            positions=[need.position],
            max_value=budget * 0.4,  # Don't spend more than 40% on one player
            exclude_own_players=True,
        )

        # Apply philosophy-specific filters
        if self.philosophy == TransferPhilosophy.YOUTH_DEVELOPMENT:
            criteria.max_age = 23
            criteria.min_potential = 75
        elif self.philosophy == TransferPhilosophy.ESTABLISHED_STARS:
            criteria.min_overall = 80
            criteria.min_age = 24
        elif self.philosophy == TransferPhilosophy.FREE_AGENTS:
            criteria.free_agents_only = True
        elif self.philosophy == TransferPhilosophy.DOMESTIC_FOCUS:
            criteria.nationalities = [self.club.country]

        # Apply need-specific filters
        if need.min_ability:
            criteria.min_overall = need.min_ability
        if need.max_age:
            criteria.max_age = need.max_age

        return criteria

    def _score_transfer_target(
        self, player: Player, info: Dict, need: SquadNeed
    ) -> float:
        """Score a potential transfer target."""
        score = 0.0

        # Base score from ability
        score += player.attributes.get_overall()

        # Position suitability
        position_rating = player.positions.get(need.position, 0)
        score += position_rating * 2

        # Value for money
        if info["value"] > 0:
            value_ratio = player.attributes.get_overall() / info["value"]
            score += value_ratio * 20

        # Philosophy alignment
        if self.philosophy == TransferPhilosophy.YOUTH_DEVELOPMENT:
            if player.age <= 21:
                score += 30
            potential_gap = player.potential_ability - player.attributes.get_overall()
            score += potential_gap

        # Availability bonus
        if info["status"] == "transfer_listed":
            score += 20
        elif info["status"] == "free_agent":
            score += 40

        # Need priority
        score += need.priority * 5

        return score

    def _should_bid_for_target(self, target: Dict) -> bool:
        """Determine if should bid for a target."""
        # Check budget
        if target["value"] > self.club.transfer_budget:
            return False

        # Check if still needed
        current_need = self._assess_current_need(target["need"])
        if current_need < 5:
            return False

        # Check if good value
        if target["score"] < 100:
            return False

        return True

    def _attempt_signing(self, target: Dict) -> Optional[Dict]:
        """Attempt to sign a transfer target."""
        player = target["player"]

        # Determine bid amount
        if target["info"]["status"] == "transfer_listed":
            bid_amount = target["info"]["listing"].asking_price
        else:
            bid_amount = target["value"] * 0.9  # Start below value

        # Make bid
        negotiation, msg = self.market.make_transfer_bid(player, self.club, bid_amount)

        if not negotiation:
            return None

        # If not immediately accepted, negotiate
        rounds = 0
        while negotiation.status == TransferStatus.NEGOTIATING and rounds < 3:
            # Increase bid
            new_bid = negotiation.current_offer * 1.1
            if new_bid > target["value"] * 1.3:
                # Too expensive, withdraw
                break

            success, msg = self.market.negotiate_transfer(negotiation, new_bid=new_bid)
            rounds += 1

        if negotiation.status == TransferStatus.AGREED:
            # Make contract offer
            contract, msg = self.market.make_contract_offer(negotiation)

            if contract and contract.status == ContractStatus.AGREED:
                # Complete transfer
                success, msg = self.market.complete_transfer(negotiation)
                if success:
                    return {
                        "type": "signed",
                        "player": player.name,
                        "fee": negotiation.agreed_fee,
                        "position": player.get_best_position().value,
                    }

        return None

    def _assess_current_need(self, need: SquadNeed) -> int:
        """Re-assess a squad need (may have changed after signings)."""
        current_players = [
            p for p in self.club.players if p.positions.get(need.position, 0) >= 15
        ]

        if len(current_players) >= 3:
            return 0  # No longer needed
        elif len(current_players) == 2:
            return 5  # Nice to have
        elif len(current_players) == 1:
            return 8  # Important
        else:
            return 10  # Critical

    def _assess_player_importance(self, player: Player) -> SquadRole:
        """Assess how important a player is to the squad."""
        position = player.get_best_position()

        # Get all players in same position
        position_players = [
            p for p in self.club.players if p.get_best_position() == position
        ]

        # Sort by ability
        position_players.sort(key=lambda p: p.attributes.get_overall(), reverse=True)

        # Determine role based on ranking
        player_rank = position_players.index(player) + 1

        if player_rank <= 2:
            return SquadRole.STARTER
        elif player_rank <= 3:
            return SquadRole.ROTATION
        elif player_rank <= 4:
            return SquadRole.BACKUP
        else:
            return SquadRole.SURPLUS
