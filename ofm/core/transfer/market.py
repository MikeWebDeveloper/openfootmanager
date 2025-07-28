"""
Transfer market management system for OpenFootManager.

Central hub for all transfer market operations including:
- Transfer window management
- Market listings
- Transfer completion
- Financial transactions
- Market statistics
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from ..db.models.transfer import (
    ContractOffer,
    ContractStatus,
    TransferHistory,
    TransferListing,
    TransferNegotiation,
    TransferStatus,
    TransferType,
    TransferWindow,
)
from ..football.club import Club
from ..football.player import Player
from ..football.playercontract import PlayerContract
from .negotiation import ContractNegotiator, TransferNegotiator
from .search import SearchCriteria, TransferSearchEngine
from .valuation import PlayerValuationEngine


class TransferMarket:
    """Central transfer market management system."""

    def __init__(self, session: Session):
        self.session = session
        self.valuation_engine = PlayerValuationEngine()
        self.transfer_negotiator = TransferNegotiator(self.valuation_engine)
        self.contract_negotiator = ContractNegotiator(self.valuation_engine)
        self.search_engine = TransferSearchEngine(session, self.valuation_engine)
        self._active_window = None

    def get_active_window(self) -> Optional[TransferWindow]:
        """Get the currently active transfer window."""
        if self._active_window:
            return self._active_window

        current_date = datetime.utcnow()
        self._active_window = (
            self.session.query(TransferWindow)
            .filter(
                TransferWindow.start_date <= current_date,
                TransferWindow.end_date >= current_date,
                TransferWindow.is_active.is_(True),
            )
            .first()
        )

        return self._active_window

    def is_transfer_window_open(self) -> bool:
        """Check if transfer window is currently open."""
        return self.get_active_window() is not None

    def list_player(
        self,
        player: Player,
        club: Club,
        asking_price: Optional[float] = None,
        min_price: Optional[float] = None,
        transfer_type: TransferType = TransferType.PERMANENT,
    ) -> TransferListing:
        """
        List a player on the transfer market.

        Args:
            player: Player to list
            club: The selling club
            asking_price: Public asking price (auto-calculated if None)
            min_price: Minimum acceptable price
            transfer_type: Type of transfer offered

        Returns:
            Created TransferListing
        """
        if asking_price is None:
            asking_price = self.valuation_engine.calculate_value(player) * 1.2

        if min_price is None:
            min_price = asking_price * 0.8

        # Deactivate any existing listings
        existing = (
            self.session.query(TransferListing)
            .filter(
                TransferListing.player_id == player.id,
                TransferListing.is_active.is_(True),
            )
            .all()
        )

        for listing in existing:
            listing.is_active = False

        # Create new listing
        listing = TransferListing(
            player_id=player.id,
            club_id=club.id,
            asking_price=asking_price,
            min_price=min_price,
            transfer_type=transfer_type,
            is_active=True,
        )

        self.session.add(listing)
        self.session.commit()

        return listing

    def make_transfer_bid(
        self,
        player: Player,
        buying_club: Club,
        bid_amount: float,
        transfer_type: TransferType = TransferType.PERMANENT,
    ) -> Tuple[TransferNegotiation, str]:
        """
        Make a bid for a player.

        Args:
            player: Target player
            buying_club: The bidding club
            bid_amount: Bid amount
            transfer_type: Type of transfer

        Returns:
            Tuple of (negotiation, status_message)
        """
        if not self.is_transfer_window_open() and player.club_id is not None:
            return None, "Transfer window is closed"

        if bid_amount > buying_club.transfer_budget:
            return None, "Insufficient transfer budget"

        selling_club = player.club

        # Check for existing negotiations
        existing = (
            self.session.query(TransferNegotiation)
            .filter(
                TransferNegotiation.player_id == player.id,
                TransferNegotiation.buying_club_id == buying_club.id,
                TransferNegotiation.status == TransferStatus.NEGOTIATING,
            )
            .first()
        )

        if existing:
            return existing, "Negotiation already in progress"

        # Create new negotiation
        negotiation = self.transfer_negotiator.initiate_negotiation(
            player, buying_club, selling_club, transfer_type, bid_amount
        )

        self.session.add(negotiation)
        self.session.commit()

        # Check if selling club accepts immediately
        listing = (
            self.session.query(TransferListing)
            .filter(
                TransferListing.player_id == player.id,
                TransferListing.is_active.is_(True),
            )
            .first()
        )

        if listing and bid_amount >= listing.asking_price:
            negotiation.status = TransferStatus.AGREED
            negotiation.agreed_fee = bid_amount
            self.session.commit()
            return negotiation, "Bid accepted - asking price met"

        return negotiation, "Bid submitted - awaiting response"

    def negotiate_transfer(
        self,
        negotiation: TransferNegotiation,
        new_bid: Optional[float] = None,
        accept_current: bool = False,
    ) -> Tuple[bool, str]:
        """
        Continue transfer negotiations.

        Args:
            negotiation: Ongoing negotiation
            new_bid: New bid amount (if raising bid)
            accept_current: Accept the current terms

        Returns:
            Tuple of (completed, status_message)
        """
        if negotiation.status != TransferStatus.NEGOTIATING:
            return False, f"Negotiation status is {negotiation.status.value}"

        if accept_current:
            negotiation.status = TransferStatus.AGREED
            negotiation.agreed_fee = negotiation.current_offer
            self.session.commit()
            return True, "Transfer fee agreed"

        if new_bid:
            # Buying club raising bid
            if new_bid > negotiation.buying_club.transfer_budget:
                return False, "Insufficient transfer budget"

            negotiation.current_offer = new_bid
            negotiation.offer_history.append(
                {
                    "round": len(negotiation.offer_history),
                    "offer": new_bid,
                    "from": "buying_club",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            # Check if meets minimum requirements
            listing = (
                self.session.query(TransferListing)
                .filter(
                    TransferListing.player_id == negotiation.player_id,
                    TransferListing.is_active.is_(True),
                )
                .first()
            )

            if listing and new_bid >= listing.min_price:
                negotiation.status = TransferStatus.AGREED
                negotiation.agreed_fee = new_bid
                self.session.commit()
                return True, "Bid accepted"

        self.session.commit()
        return False, "Negotiation continues"

    def make_contract_offer(
        self,
        negotiation: TransferNegotiation,
        years: int = 4,
        weekly_wage: Optional[float] = None,
    ) -> Tuple[ContractOffer, str]:
        """
        Make contract offer to player after transfer fee agreed.

        Args:
            negotiation: Completed transfer negotiation
            years: Contract length
            weekly_wage: Wage offer

        Returns:
            Tuple of (contract_offer, status_message)
        """
        if negotiation.status != TransferStatus.AGREED:
            return None, "Transfer fee not yet agreed"

        player = negotiation.player
        buying_club = negotiation.buying_club

        # Check for existing contract offer
        existing = (
            self.session.query(ContractOffer)
            .filter(ContractOffer.negotiation_id == negotiation.id)
            .first()
        )

        if existing:
            return existing, "Contract offer already exists"

        # Create contract offer
        contract = self.contract_negotiator.create_contract_offer(
            player, buying_club, negotiation, years, weekly_wage
        )

        self.session.add(contract)
        self.session.commit()

        # Check if player accepts immediately
        if self.contract_negotiator._player_accepts_contract(contract):
            contract.status = ContractStatus.AGREED
            self.session.commit()
            return contract, "Contract terms agreed"

        return contract, "Contract offer made - awaiting response"

    def complete_transfer(self, negotiation: TransferNegotiation) -> Tuple[bool, str]:
        """
        Complete a transfer after all terms agreed.

        Args:
            negotiation: The negotiation to complete

        Returns:
            Tuple of (success, message)
        """
        # Verify all conditions met
        if negotiation.status != TransferStatus.AGREED:
            return False, "Transfer fee not agreed"

        contract = negotiation.contract_offer
        if not contract or contract.status != ContractStatus.AGREED:
            return False, "Contract terms not agreed"

        player = negotiation.player
        selling_club = negotiation.selling_club
        buying_club = negotiation.buying_club

        # Process financials
        if negotiation.transfer_type == TransferType.PERMANENT:
            if buying_club.transfer_budget < negotiation.agreed_fee:
                return False, "Insufficient funds"

            buying_club.transfer_budget -= negotiation.agreed_fee
            if selling_club:
                selling_club.transfer_budget += negotiation.agreed_fee

        # Update player's club
        player.club_id = buying_club.id

        # Create new contract
        new_contract = PlayerContract(
            player_id=player.id,
            club_id=buying_club.id,
            weekly_wage=contract.final_wage or contract.weekly_wage,
            years_remaining=contract.length_years,
            signing_bonus=contract.signing_bonus,
            release_clause=contract.release_clause,
        )

        # Remove old contract
        if player.contract:
            self.session.delete(player.contract)

        player.contract = new_contract

        # Record transfer history
        history = TransferHistory(
            player_id=player.id,
            from_club_id=selling_club.id if selling_club else None,
            to_club_id=buying_club.id,
            transfer_type=negotiation.transfer_type,
            transfer_fee=negotiation.agreed_fee,
            total_cost=negotiation.agreed_fee
            + contract.signing_bonus
            + contract.agent_fee,
            contract_length=contract.length_years,
            weekly_wage=contract.final_wage or contract.weekly_wage,
            agent_fee=contract.agent_fee,
            signing_bonus=contract.signing_bonus,
        )

        # Update negotiation status
        negotiation.status = TransferStatus.COMPLETED
        negotiation.completed_date = datetime.utcnow()
        contract.status = ContractStatus.SIGNED
        contract.signed_date = datetime.utcnow()

        # Deactivate transfer listing if exists
        listing = (
            self.session.query(TransferListing)
            .filter(
                TransferListing.player_id == player.id,
                TransferListing.is_active.is_(True),
            )
            .first()
        )

        if listing:
            listing.is_active = False

        # Save all changes
        self.session.add(new_contract)
        self.session.add(history)
        self.session.commit()

        return True, f"{player.name} has joined {buying_club.name}"

    def get_market_stats(self) -> Dict:
        """Get current transfer market statistics."""
        stats = {
            "total_listings": 0,
            "active_negotiations": 0,
            "completed_transfers": 0,
            "total_spending": 0,
            "average_fee": 0,
            "biggest_transfer": None,
            "most_active_club": None,
        }

        # Count active listings
        stats["total_listings"] = (
            self.session.query(TransferListing)
            .filter(TransferListing.is_active.is_(True))
            .count()
        )

        # Count active negotiations
        stats["active_negotiations"] = (
            self.session.query(TransferNegotiation)
            .filter(TransferNegotiation.status == TransferStatus.NEGOTIATING)
            .count()
        )

        # Get completed transfers this window
        if self.get_active_window():
            window_start = self.get_active_window().start_date

            completed = (
                self.session.query(TransferHistory)
                .filter(TransferHistory.transfer_date >= window_start)
                .all()
            )

            stats["completed_transfers"] = len(completed)

            if completed:
                total_fees = sum(t.transfer_fee for t in completed)
                stats["total_spending"] = total_fees
                stats["average_fee"] = total_fees / len(completed)

                # Find biggest transfer
                biggest = max(completed, key=lambda t: t.transfer_fee)
                stats["biggest_transfer"] = {
                    "player": biggest.player.name,
                    "fee": biggest.transfer_fee,
                    "to_club": biggest.to_club.name,
                }

        return stats

    def simulate_deadline_day(self) -> List[Dict]:
        """Simulate AI transfer activity on deadline day."""
        if not self.is_transfer_window_open():
            return []

        transfers = []

        # Get all clubs that might be active
        clubs = (
            self.session.query(Club)
            .filter(Club.transfer_budget > 1000000)  # At least 1M budget
            .all()
        )

        for club in clubs:
            # Determine if club needs players
            if self._club_needs_transfers(club):
                # Find suitable targets
                targets = self._find_ai_targets(club)

                for player, info in targets[:2]:  # Max 2 signings per club
                    # Attempt transfer
                    success = self._execute_ai_transfer(club, player, info)
                    if success:
                        transfers.append(
                            {
                                "player": player.name,
                                "from": (
                                    player.club.name if player.club else "Free Agent"
                                ),
                                "to": club.name,
                                "fee": info["value"],
                            }
                        )

        return transfers

    def _club_needs_transfers(self, club: Club) -> bool:
        """Determine if AI club needs to make transfers."""
        # TODO: Implement based on squad analysis
        return True  # Placeholder

    def _find_ai_targets(self, club: Club) -> List[Tuple[Player, Dict]]:
        """Find suitable transfer targets for AI club."""
        # Use search engine with smart criteria
        criteria = SearchCriteria(
            max_value=club.transfer_budget * 0.5,
            transfer_listed_only=True,
            sort_by="value_for_money",
        )

        return self.search_engine.search(criteria, club)

    def _execute_ai_transfer(self, club: Club, player: Player, info: Dict) -> bool:
        """Execute an AI-driven transfer."""
        # Make bid at asking price if listed
        if info["listing"]:
            negotiation, msg = self.make_transfer_bid(
                player, club, info["listing"].asking_price
            )

            if negotiation and negotiation.status == TransferStatus.AGREED:
                # Make contract offer
                contract, msg = self.make_contract_offer(negotiation)

                if contract and contract.status == ContractStatus.AGREED:
                    # Complete transfer
                    success, msg = self.complete_transfer(negotiation)
                    return success

        return False
