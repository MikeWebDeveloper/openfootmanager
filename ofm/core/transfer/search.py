"""
Transfer market search and filtering system for OpenFootManager.

Provides sophisticated search capabilities for finding players including:
- Position-based searches
- Attribute filtering
- Age and potential ranges
- Financial constraints
- Availability status
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from ..db.models.transfer import TransferListing, TransferStatus, TransferType
from ..football.club import Club
from ..football.detailed_positions import DetailedPosition
from ..football.player import Player
from .valuation import PlayerValuationEngine


class SearchFilter(Enum):
    """Types of search filters available."""

    POSITION = "position"
    AGE = "age"
    OVERALL = "overall"
    POTENTIAL = "potential"
    VALUE = "value"
    WAGE = "wage"
    CONTRACT = "contract"
    NATIONALITY = "nationality"
    AVAILABILITY = "availability"


@dataclass
class SearchCriteria:
    """Encapsulates all search criteria for transfer market."""

    # Basic filters
    positions: Optional[List[DetailedPosition]] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None

    # Ability filters
    min_overall: Optional[int] = None
    max_overall: Optional[int] = None
    min_potential: Optional[int] = None

    # Financial filters
    max_value: Optional[float] = None
    max_wage: Optional[float] = None

    # Availability filters
    transfer_listed_only: bool = False
    free_agents_only: bool = False
    loan_available: bool = False

    # Other filters
    nationalities: Optional[List[str]] = None
    exclude_own_players: bool = True

    # Sorting
    sort_by: str = "value"  # value, age, overall, potential
    sort_desc: bool = True

    # Pagination
    limit: int = 50
    offset: int = 0


class TransferSearchEngine:
    """Advanced search engine for transfer market."""

    def __init__(self, session: Session, valuation_engine: PlayerValuationEngine = None):
        self.session = session
        self.valuation_engine = valuation_engine or PlayerValuationEngine()

    def search(
        self, criteria: SearchCriteria, searching_club: Optional[Club] = None
    ) -> List[Tuple[Player, Dict]]:
        """
        Search for players matching criteria.

        Args:
            criteria: Search criteria
            searching_club: The club doing the search (for filtering own players)

        Returns:
            List of (Player, info_dict) tuples where info_dict contains:
            - value: Current market value
            - status: Availability status
            - listing: TransferListing if listed
        """
        query = self.session.query(Player)

        # Apply filters
        query = self._apply_basic_filters(query, criteria)
        query = self._apply_ability_filters(query, criteria)
        query = self._apply_availability_filters(query, criteria)

        # Exclude own players if requested
        if criteria.exclude_own_players and searching_club:
            query = query.filter(Player.club_id != searching_club.id)

        # Get initial results
        players = query.all()

        # Apply value-based filters (requires calculation)
        if criteria.max_value or criteria.max_wage:
            players = self._apply_financial_filters(players, criteria)

        # Calculate additional info for each player
        results = []
        for player in players:
            info = self._get_player_info(player)
            results.append((player, info))

        # Sort results
        results = self._sort_results(results, criteria)

        # Apply pagination
        start = criteria.offset
        end = criteria.offset + criteria.limit

        return results[start:end]

    def get_recommendations(
        self, club: Club, position: DetailedPosition, max_results: int = 10
    ) -> List[Tuple[Player, Dict]]:
        """
        Get AI-recommended players for a position.

        Args:
            club: The searching club
            position: DetailedPosition to fill
            max_results: Maximum recommendations

        Returns:
            List of recommended players with info
        """
        # Analyze club's needs
        budget = club.transfer_budget
        wage_budget = self._estimate_wage_budget(club)
        squad_level = self._analyze_squad_level(club)

        # Build smart criteria
        criteria = SearchCriteria(
            positions=[position],
            min_overall=max(50, squad_level - 10),
            max_overall=min(99, squad_level + 15),
            max_value=budget * 0.8,  # Don't spend entire budget
            max_wage=wage_budget,
            sort_by="value_for_money",  # Custom sort
        )

        # Get initial results
        results = self.search(criteria, club)

        # Score and filter recommendations
        scored_results = []
        for player, info in results:
            score = self._calculate_recommendation_score(player, info, club, position)
            scored_results.append((player, info, score))

        # Sort by score and return top results
        scored_results.sort(key=lambda x: x[2], reverse=True)

        return [(p, i) for p, i, _ in scored_results[:max_results]]

    def find_similar_players(
        self, player: Player, max_results: int = 10
    ) -> List[Tuple[Player, Dict]]:
        """
        Find players similar to a given player.

        Args:
            player: Reference player
            max_results: Maximum similar players to return

        Returns:
            List of similar players with info
        """
        # Build criteria based on player attributes
        criteria = SearchCriteria(
            positions=[player.get_best_position()],
            min_age=player.age - 3,
            max_age=player.age + 3,
            min_overall=player.attributes.get_overall() - 5,
            max_overall=player.attributes.get_overall() + 5,
            exclude_own_players=False,
        )

        # Search for candidates
        results = self.search(criteria)

        # Calculate similarity scores
        scored_results = []
        for candidate, info in results:
            if candidate.id == player.id:
                continue
            score = self._calculate_similarity_score(player, candidate)
            scored_results.append((candidate, info, score))

        # Sort by similarity
        scored_results.sort(key=lambda x: x[2], reverse=True)

        return [(p, i) for p, i, _ in scored_results[:max_results]]

    def _apply_basic_filters(self, query, criteria: SearchCriteria):
        """Apply basic filters to query."""
        if criteria.positions:
            # Filter by any of the positions
            position_filters = []
            for position in criteria.positions:
                position_filters.append(Player.positions[position] >= 10)
            query = query.filter(or_(*position_filters))

        if criteria.min_age is not None:
            query = query.filter(Player.age >= criteria.min_age)
        if criteria.max_age is not None:
            query = query.filter(Player.age <= criteria.max_age)

        if criteria.nationalities:
            query = query.filter(Player.nationality.in_(criteria.nationalities))

        return query

    def _apply_ability_filters(self, query, criteria: SearchCriteria):
        """Apply ability-based filters."""
        # Note: These would need to be calculated attributes or stored values
        # For now, we'll do post-filtering
        return query

    def _apply_availability_filters(self, query, criteria: SearchCriteria):
        """Apply availability filters."""
        if criteria.transfer_listed_only:
            query = query.join(TransferListing).filter(TransferListing.is_active.is_(True))

        if criteria.free_agents_only:
            query = query.filter(Player.club_id.is_(None))

        return query

    def _apply_financial_filters(
        self, players: List[Player], criteria: SearchCriteria
    ) -> List[Player]:
        """Filter players by financial constraints."""
        filtered = []

        for player in players:
            # Check value constraint
            if criteria.max_value:
                value = self.valuation_engine.calculate_value(player)
                if value > criteria.max_value:
                    continue

            # Check wage constraint
            if criteria.max_wage:
                # Estimate wage based on value
                value = self.valuation_engine.calculate_value(player)
                wage = self.valuation_engine.estimate_wage_demands(player, value)
                if wage > criteria.max_wage:
                    continue

            filtered.append(player)

        return filtered

    def _get_player_info(self, player: Player) -> Dict:
        """Get additional info about a player."""
        value = self.valuation_engine.calculate_value(player)

        # Check if transfer listed
        listing = (
            self.session.query(TransferListing)
            .filter(
                TransferListing.player_id == player.id,
                TransferListing.is_active.is_(True),
            )
            .first()
        )

        # Determine availability status
        if not player.club_id:
            status = "free_agent"
        elif listing:
            status = "transfer_listed"
        elif player.contract and player.contract.years_remaining < 1:
            status = "expiring_contract"
        else:
            status = "not_listed"

        return {
            "value": value,
            "status": status,
            "listing": listing,
            "wage_estimate": self.valuation_engine.estimate_wage_demands(player, value),
        }

    def _sort_results(
        self, results: List[Tuple[Player, Dict]], criteria: SearchCriteria
    ) -> List[Tuple[Player, Dict]]:
        """Sort search results."""
        if criteria.sort_by == "value":
            results.sort(key=lambda x: x[1]["value"], reverse=criteria.sort_desc)
        elif criteria.sort_by == "age":
            results.sort(key=lambda x: x[0].age, reverse=not criteria.sort_desc)
        elif criteria.sort_by == "overall":
            results.sort(key=lambda x: x[0].attributes.get_overall(), reverse=criteria.sort_desc)
        elif criteria.sort_by == "potential":
            results.sort(key=lambda x: x[0].potential_ability, reverse=criteria.sort_desc)
        elif criteria.sort_by == "value_for_money":
            # Custom sort for recommendations
            results.sort(
                key=lambda x: x[0].attributes.get_overall() / max(x[1]["value"], 0.1),
                reverse=criteria.sort_desc,
            )

        return results

    def _estimate_wage_budget(self, club: Club) -> float:
        """Estimate available wage budget for new signings."""
        # TODO: Implement based on club finances
        return 100000  # Placeholder

    def _analyze_squad_level(self, club: Club) -> int:
        """Analyze average squad ability level."""
        # TODO: Calculate from actual squad
        return 70  # Placeholder

    def _calculate_recommendation_score(
        self, player: Player, info: Dict, club: Club, position: DetailedPosition
    ) -> float:
        """Calculate how well a player fits club's needs."""
        score = 0.0

        # Position suitability
        position_rating = player.positions.get(position, 0)
        score += position_rating * 2

        # Value for money
        if info["value"] > 0:
            ability_per_million = player.attributes.get_overall() / info["value"]
            score += ability_per_million * 10

        # Age profile
        if 21 <= player.age <= 27:
            score += 20  # Prime age
        elif player.age < 21:
            score += 15  # Young talent

        # Availability
        if info["status"] == "transfer_listed":
            score += 10
        elif info["status"] == "free_agent":
            score += 15

        return score

    def _calculate_similarity_score(self, player1: Player, player2: Player) -> float:
        """Calculate similarity between two players."""
        score = 100.0

        # Age difference
        age_diff = abs(player1.age - player2.age)
        score -= age_diff * 2

        # Overall ability difference
        ability_diff = abs(player1.attributes.get_overall() - player2.attributes.get_overall())
        score -= ability_diff

        # Position match
        pos1 = player1.get_best_position()
        pos2 = player2.get_best_position()
        if pos1 == pos2:
            score += 20

        # Nationality match
        if player1.nationality == player2.nationality:
            score += 5

        return max(0, score)
