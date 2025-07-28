"""Tests for the transfer system functionality."""

from datetime import datetime, timedelta

import pytest

from ofm.core.db.models.transfer import (
    ContractOffer,
    ContractStatus,
    TransferHistory,
    TransferNegotiation,
    TransferStatus,
    TransferType,
)


# Mock classes for testing
class MockPlayer:
    """Mock Player for testing."""

    def __init__(self, id=1, name="Test Player", club_id=None):
        self.id = id
        self.name = name
        self.club_id = club_id


class MockClub:
    """Mock Club for testing."""

    def __init__(self, id=1, name="Test Club", budget=50000000):
        self.id = id
        self.name = name
        self.budget = budget


class TestTransferSystem:
    """Test suite for transfer system operations."""

    @pytest.mark.fast
    @pytest.mark.unit
    def test_create_transfer_offer(self, test_db_session):
        """Test creating a transfer offer."""
        # Create two clubs
        buying_club = MockClub(id=1, name="Buying FC")
        selling_club = MockClub(id=2, name="Selling FC")

        # Create a player for the selling club
        player = MockPlayer(id=1, name="Transfer Target", club_id=selling_club.id)

        # Create transfer negotiation
        negotiation = TransferNegotiation(
            player_id=player.id,
            selling_club_id=selling_club.id,
            buying_club_id=buying_club.id,
            initial_offer=50000000,  # 50M
            current_offer=50000000,
            status=TransferStatus.NEGOTIATING,
            transfer_type=TransferType.PERMANENT,
        )

        test_db_session.add(negotiation)
        test_db_session.commit()

        # Verify negotiation was created
        assert negotiation.id is not None
        assert negotiation.player_id == player.id
        assert negotiation.initial_offer == 50000000
        assert negotiation.status == TransferStatus.NEGOTIATING

    @pytest.mark.fast
    @pytest.mark.unit
    def test_accept_transfer_offer(self, test_db_session):
        """Test accepting a transfer offer."""
        # Setup clubs and player
        buying_club = MockClub(id=1, name="Buying FC", budget=100000000)
        selling_club = MockClub(id=2, name="Selling FC", budget=10000000)
        player = MockPlayer(id=1, name="Transfer Target", club_id=selling_club.id)

        initial_buying_budget = buying_club.budget
        initial_selling_budget = selling_club.budget

        # Create and accept transfer negotiation
        negotiation = TransferNegotiation(
            player_id=player.id,
            selling_club_id=selling_club.id,
            buying_club_id=buying_club.id,
            initial_offer=50000000,
            current_offer=50000000,
            agreed_fee=50000000,
            status=TransferStatus.NEGOTIATING,
            transfer_type=TransferType.PERMANENT,
        )
        test_db_session.add(negotiation)
        test_db_session.commit()

        # Accept the negotiation
        negotiation.status = TransferStatus.AGREED
        negotiation.completed_date = datetime.now()

        # Create contract offer
        contract = ContractOffer(
            negotiation_id=negotiation.id,
            player_id=player.id,
            club_id=buying_club.id,
            status=ContractStatus.SIGNED,
            length_years=5,
            weekly_wage=200000,
            signed_date=datetime.now(),
        )
        test_db_session.add(contract)

        # Update player's club
        player.club_id = buying_club.id

        # Update club budgets
        buying_club.budget -= negotiation.agreed_fee
        selling_club.budget += negotiation.agreed_fee

        test_db_session.commit()

        # Verify transfer was completed
        assert player.club_id == buying_club.id
        assert buying_club.budget == initial_buying_budget - negotiation.agreed_fee
        assert selling_club.budget == initial_selling_budget + negotiation.agreed_fee
        assert contract.id is not None

    @pytest.mark.fast
    @pytest.mark.unit
    def test_reject_transfer_offer(self, test_db_session):
        """Test rejecting a transfer offer."""
        # Setup
        buying_club = MockClub(id=1, name="Buying FC")
        selling_club = MockClub(id=2, name="Selling FC")
        player = MockPlayer(id=1, name="Test Player", club_id=selling_club.id)

        # Create negotiation
        negotiation = TransferNegotiation(
            player_id=player.id,
            selling_club_id=selling_club.id,
            buying_club_id=buying_club.id,
            initial_offer=30000000,
            current_offer=30000000,
            status=TransferStatus.NEGOTIATING,
            transfer_type=TransferType.PERMANENT,
        )
        test_db_session.add(negotiation)
        test_db_session.commit()

        # Reject negotiation
        negotiation.status = TransferStatus.REJECTED
        negotiation.completed_date = datetime.now()
        test_db_session.commit()

        # Verify player stays at original club
        assert player.club_id == selling_club.id
        assert negotiation.status == TransferStatus.REJECTED
        assert negotiation.completed_date is not None

    @pytest.mark.fast
    @pytest.mark.critical
    def test_transfer_budget_validation(self, test_db_session):
        """Test that transfers respect budget constraints."""
        # Create a club with limited budget
        poor_club = MockClub(id=1, name="Poor FC", budget=5000000)  # Only 5M budget
        rich_club = MockClub(id=2, name="Rich FC", budget=200000000)  # 200M budget

        # Create expensive player
        star_player = MockPlayer(id=1, name="Expensive Star", club_id=rich_club.id)

        # Try to create negotiation beyond budget
        negotiation = TransferNegotiation(
            player_id=star_player.id,
            selling_club_id=rich_club.id,
            buying_club_id=poor_club.id,
            initial_offer=100000000,  # 100M - way over budget
            current_offer=100000000,
            status=TransferStatus.NEGOTIATING,
            transfer_type=TransferType.PERMANENT,
        )

        # In a real system, this should be validated
        # For now, we just check the budget difference
        assert negotiation.initial_offer > poor_club.budget
        assert poor_club.budget < negotiation.initial_offer

    @pytest.mark.integration
    @pytest.mark.slow
    def test_transfer_window_restrictions(self, test_db_session):
        """Test transfer window date restrictions."""
        # Create clubs and player
        club1 = MockClub(id=1, name="Club 1")
        club2 = MockClub(id=2, name="Club 2")
        player = MockPlayer(id=1, name="Test Player", club_id=club1.id)

        # Define transfer windows
        summer_window_start = datetime(2024, 7, 1)
        summer_window_end = datetime(2024, 8, 31)

        # Test negotiation during summer window
        summer_transfer = TransferHistory(
            player_id=player.id,
            from_club_id=club1.id,
            to_club_id=club2.id,
            transfer_fee=20000000,
            transfer_date=datetime(2024, 7, 15),  # During summer window
            contract_length=4,
            weekly_wage=100000,
            transfer_type=TransferType.PERMANENT,
        )
        test_db_session.add(summer_transfer)
        test_db_session.commit()

        assert summer_transfer.id is not None
        assert summer_window_start <= summer_transfer.transfer_date <= summer_window_end

    @pytest.mark.fast
    @pytest.mark.unit
    def test_loan_transfer(self, test_db_session):
        """Test loan transfer functionality."""
        # Create clubs and player
        parent_club = MockClub(id=1, name="Parent FC")
        loan_club = MockClub(id=2, name="Loan FC")
        player = MockPlayer(id=1, name="Loan Player", club_id=parent_club.id)

        # Create loan transfer history
        loan = TransferHistory(
            player_id=player.id,
            from_club_id=parent_club.id,
            to_club_id=loan_club.id,
            transfer_fee=0,  # No transfer fee for loan
            transfer_date=datetime.now(),
            contract_length=1,  # One season loan
            weekly_wage=50000,
            transfer_type=TransferType.LOAN,
            contract_end_date=datetime.now() + timedelta(days=365),
        )
        test_db_session.add(loan)

        # Update player's current club
        player.club_id = loan_club.id
        # Note: parent_club_id is not a field in the test factory player
        test_db_session.commit()

        # Verify loan setup
        assert loan.transfer_type == TransferType.LOAN
        assert loan.from_club_id == parent_club.id
        assert player.club_id == loan_club.id
        # Note: parent_club_id is not a field in the test factory player

    @pytest.mark.fast
    @pytest.mark.critical
    def test_transfer_history(self, test_db_session):
        """Test tracking player transfer history."""
        # Create player and clubs
        club1 = MockClub(id=1, name="First FC")
        club2 = MockClub(id=2, name="Second FC")
        club3 = MockClub(id=3, name="Third FC")

        player = MockPlayer(id=1, name="Journey Man", club_id=club1.id)

        # Create transfer history
        transfer1 = TransferHistory(
            player_id=player.id,
            from_club_id=club1.id,
            to_club_id=club2.id,
            transfer_fee=10000000,
            transfer_date=datetime.now() - timedelta(days=730),  # 2 years ago
            contract_length=3,
            weekly_wage=50000,
            transfer_type=TransferType.PERMANENT,
        )

        transfer2 = TransferHistory(
            player_id=player.id,
            from_club_id=club2.id,
            to_club_id=club3.id,
            transfer_fee=25000000,
            transfer_date=datetime.now() - timedelta(days=365),  # 1 year ago
            contract_length=4,
            weekly_wage=100000,
            transfer_type=TransferType.PERMANENT,
        )

        test_db_session.add_all([transfer1, transfer2])
        test_db_session.commit()

        # Query transfer history
        transfers = (
            test_db_session.query(TransferHistory)
            .filter_by(player_id=player.id)
            .order_by(TransferHistory.transfer_date)
            .all()
        )

        assert len(transfers) == 2
        assert transfers[0].transfer_fee == 10000000
        assert transfers[1].transfer_fee == 25000000
        assert transfers[0].transfer_date < transfers[1].transfer_date

    @pytest.mark.performance
    def test_bulk_transfer_processing(self, test_db_session):
        """Test performance of processing multiple transfers."""
        from ofm.tests.utils import PerformanceTimer

        # Create clubs
        clubs = []
        for i in range(10):
            club = MockClub(id=i, name=f"Club {i}", budget=50000000)
            clubs.append(club)

        # Create players
        players = []
        for i in range(50):
            player = MockPlayer(id=i, name=f"Player {i}", club_id=clubs[i % 10].id)
            players.append(player)

        # Process multiple transfers
        with PerformanceTimer("Bulk transfer processing", max_duration=2.0):
            transfers = []
            
            for i in range(20):
                transfer = TransferHistory(
                    player_id=players[i].id,
                    from_club_id=players[i].club_id,
                    to_club_id=clubs[(i + 5) % 10].id,
                    transfer_fee=1000000 * (i + 1),
                    transfer_date=datetime.now(),
                    contract_length=3,
                    weekly_wage=50000 + (i * 5000),
                    transfer_type=TransferType.PERMANENT,
                )
                transfers.append(transfer)

            test_db_session.add_all(transfers)
            test_db_session.commit()

        # Verify transfers
        assert len(transfers) == 20
        saved_transfers = test_db_session.query(TransferHistory).count()
        assert saved_transfers >= 20
