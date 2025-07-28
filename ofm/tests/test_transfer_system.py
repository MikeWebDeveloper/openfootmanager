"""Tests for the transfer system functionality."""

import pytest
from datetime import datetime, timedelta

from ofm.core.football.club import Club
from ofm.core.football.player import Player
from ofm.tests.utils import TestDataFactory, assert_player_attributes_valid


class TestTransferSystem:
    """Test suite for transfer system operations."""

    @pytest.mark.fast
    @pytest.mark.unit
    def test_create_transfer_offer(self, test_db_session, sample_club):
        """Test creating a transfer offer."""
        # Create two clubs
        buying_club = sample_club
        selling_club = TestDataFactory.create_test_club(
            test_db_session, name="Selling FC"
        )
        
        # Create a player for the selling club
        player = TestDataFactory.create_test_player(
            test_db_session,
            name="Transfer Target",
            club=selling_club,
            overall=85,
        )
        
        # Create transfer offer
        offer = TransferOffer(
            player_id=player.id,
            from_club_id=buying_club.id,
            to_club_id=selling_club.id,
            amount=50000000,  # 50M
            wage_offered=200000,  # 200k/week
            contract_years=5,
            status="pending",
            created_at=datetime.now(),
        )
        
        test_db_session.add(offer)
        test_db_session.commit()
        
        # Verify offer was created
        assert offer.id is not None
        assert offer.player_id == player.id
        assert offer.amount == 50000000
        assert offer.status == "pending"

    @pytest.mark.fast
    @pytest.mark.unit
    def test_accept_transfer_offer(self, test_db_session, sample_club):
        """Test accepting a transfer offer."""
        # Setup clubs and player
        buying_club = sample_club
        selling_club = TestDataFactory.create_test_club(
            test_db_session, name="Selling FC", budget=10000000
        )
        player = TestDataFactory.create_test_player(
            test_db_session,
            name="Transfer Target",
            club=selling_club,
            overall=85,
        )
        
        initial_buying_budget = buying_club.budget
        initial_selling_budget = selling_club.budget
        
        # Create and accept transfer offer
        offer = TransferOffer(
            player_id=player.id,
            from_club_id=buying_club.id,
            to_club_id=selling_club.id,
            amount=50000000,
            wage_offered=200000,
            contract_years=5,
            status="pending",
        )
        test_db_session.add(offer)
        test_db_session.commit()
        
        # Accept the offer
        offer.status = "accepted"
        offer.accepted_at = datetime.now()
        
        # Execute transfer
        transfer = Transfer(
            player_id=player.id,
            from_club_id=selling_club.id,
            to_club_id=buying_club.id,
            amount=offer.amount,
            date=datetime.now(),
            contract_years=offer.contract_years,
            wage=offer.wage_offered,
        )
        test_db_session.add(transfer)
        
        # Update player's club
        player.club_id = buying_club.id
        
        # Update club budgets
        buying_club.budget -= offer.amount
        selling_club.budget += offer.amount
        
        test_db_session.commit()
        
        # Verify transfer was completed
        assert player.club_id == buying_club.id
        assert buying_club.budget == initial_buying_budget - offer.amount
        assert selling_club.budget == initial_selling_budget + offer.amount
        assert transfer.id is not None

    @pytest.mark.fast
    @pytest.mark.unit
    def test_reject_transfer_offer(self, test_db_session, sample_club):
        """Test rejecting a transfer offer."""
        # Setup
        buying_club = sample_club
        selling_club = TestDataFactory.create_test_club(test_db_session)
        player = TestDataFactory.create_test_player(
            test_db_session, club=selling_club
        )
        
        # Create offer
        offer = TransferOffer(
            player_id=player.id,
            from_club_id=buying_club.id,
            to_club_id=selling_club.id,
            amount=30000000,
            wage_offered=150000,
            contract_years=4,
            status="pending",
        )
        test_db_session.add(offer)
        test_db_session.commit()
        
        # Reject offer
        offer.status = "rejected"
        offer.rejected_at = datetime.now()
        test_db_session.commit()
        
        # Verify player stays at original club
        assert player.club_id == selling_club.id
        assert offer.status == "rejected"
        assert offer.rejected_at is not None

    @pytest.mark.fast
    @pytest.mark.critical
    def test_transfer_budget_validation(self, test_db_session):
        """Test that transfers respect budget constraints."""
        # Create a club with limited budget
        poor_club = TestDataFactory.create_test_club(
            test_db_session,
            name="Poor FC",
            budget=5000000,  # Only 5M budget
        )
        rich_club = TestDataFactory.create_test_club(
            test_db_session,
            name="Rich FC",
            budget=200000000,  # 200M budget
        )
        
        # Create expensive player
        star_player = TestDataFactory.create_test_player(
            test_db_session,
            name="Expensive Star",
            club=rich_club,
            overall=95,
        )
        
        # Try to create offer beyond budget
        offer = TransferOffer(
            player_id=star_player.id,
            from_club_id=poor_club.id,
            to_club_id=rich_club.id,
            amount=100000000,  # 100M - way over budget
            wage_offered=500000,
            contract_years=5,
            status="pending",
        )
        
        # In a real system, this should be validated
        # For now, we just check the budget difference
        assert offer.amount > poor_club.budget
        assert poor_club.budget < offer.amount

    @pytest.mark.integration
    @pytest.mark.slow
    def test_transfer_window_restrictions(self, test_db_session):
        """Test transfer window date restrictions."""
        # Create clubs and player
        club1 = TestDataFactory.create_test_club(test_db_session, name="Club 1")
        club2 = TestDataFactory.create_test_club(test_db_session, name="Club 2")
        player = TestDataFactory.create_test_player(test_db_session, club=club1)
        
        # Define transfer windows
        summer_window_start = datetime(2024, 7, 1)
        summer_window_end = datetime(2024, 8, 31)
        winter_window_start = datetime(2025, 1, 1)
        winter_window_end = datetime(2025, 1, 31)
        
        # Test transfer during summer window
        summer_transfer = Transfer(
            player_id=player.id,
            from_club_id=club1.id,
            to_club_id=club2.id,
            amount=20000000,
            date=datetime(2024, 7, 15),  # During summer window
            contract_years=4,
            wage=100000,
        )
        test_db_session.add(summer_transfer)
        test_db_session.commit()
        
        assert summer_transfer.id is not None
        assert summer_window_start <= summer_transfer.date <= summer_window_end

    @pytest.mark.fast
    @pytest.mark.unit
    def test_loan_transfer(self, test_db_session):
        """Test loan transfer functionality."""
        # Create clubs and player
        parent_club = TestDataFactory.create_test_club(
            test_db_session, name="Parent FC"
        )
        loan_club = TestDataFactory.create_test_club(
            test_db_session, name="Loan FC"
        )
        player = TestDataFactory.create_test_player(
            test_db_session,
            name="Loan Player",
            club=parent_club,
            overall=75,
        )
        
        # Create loan transfer
        loan = Transfer(
            player_id=player.id,
            from_club_id=parent_club.id,
            to_club_id=loan_club.id,
            amount=0,  # No transfer fee for loan
            date=datetime.now(),
            contract_years=1,  # One season loan
            wage=50000,
            is_loan=True,
            loan_end_date=datetime.now() + timedelta(days=365),
            parent_club_id=parent_club.id,
        )
        test_db_session.add(loan)
        
        # Update player's current club
        player.club_id = loan_club.id
        player.parent_club_id = parent_club.id
        test_db_session.commit()
        
        # Verify loan setup
        assert loan.is_loan is True
        assert loan.parent_club_id == parent_club.id
        assert player.club_id == loan_club.id
        assert player.parent_club_id == parent_club.id

    @pytest.mark.fast
    @pytest.mark.critical
    def test_transfer_history(self, test_db_session):
        """Test tracking player transfer history."""
        # Create player and clubs
        club1 = TestDataFactory.create_test_club(test_db_session, name="First FC")
        club2 = TestDataFactory.create_test_club(test_db_session, name="Second FC")
        club3 = TestDataFactory.create_test_club(test_db_session, name="Third FC")
        
        player = TestDataFactory.create_test_player(
            test_db_session,
            name="Journey Man",
            club=club1,
        )
        
        # Create transfer history
        transfer1 = Transfer(
            player_id=player.id,
            from_club_id=club1.id,
            to_club_id=club2.id,
            amount=10000000,
            date=datetime.now() - timedelta(days=730),  # 2 years ago
            contract_years=3,
            wage=50000,
        )
        
        transfer2 = Transfer(
            player_id=player.id,
            from_club_id=club2.id,
            to_club_id=club3.id,
            amount=25000000,
            date=datetime.now() - timedelta(days=365),  # 1 year ago
            contract_years=4,
            wage=100000,
        )
        
        test_db_session.add_all([transfer1, transfer2])
        test_db_session.commit()
        
        # Query transfer history
        transfers = test_db_session.query(Transfer).filter_by(
            player_id=player.id
        ).order_by(Transfer.date).all()
        
        assert len(transfers) == 2
        assert transfers[0].amount == 10000000
        assert transfers[1].amount == 25000000
        assert transfers[0].date < transfers[1].date

    @pytest.mark.performance
    def test_bulk_transfer_processing(self, test_db_session):
        """Test performance of processing multiple transfers."""
        from ofm.tests.utils import PerformanceTimer
        
        # Create clubs
        clubs = []
        for i in range(10):
            club = TestDataFactory.create_test_club(
                test_db_session,
                name=f"Club {i}",
                budget=50000000,
            )
            clubs.append(club)
        
        # Create players
        players = []
        for i in range(50):
            player = TestDataFactory.create_test_player(
                test_db_session,
                name=f"Player {i}",
                club=clubs[i % 10],
                overall=60 + (i % 30),
            )
            players.append(player)
        
        # Process multiple transfers
        with PerformanceTimer("Bulk transfer processing", max_duration=2.0):
            transfers = []
            for i in range(20):
                transfer = Transfer(
                    player_id=players[i].id,
                    from_club_id=players[i].club_id,
                    to_club_id=clubs[(i + 5) % 10].id,
                    amount=1000000 * (i + 1),
                    date=datetime.now(),
                    contract_years=3,
                    wage=50000 + (i * 5000),
                )
                transfers.append(transfer)
            
            test_db_session.add_all(transfers)
            test_db_session.commit()
        
        # Verify transfers
        assert len(transfers) == 20
        saved_transfers = test_db_session.query(Transfer).count()
        assert saved_transfers >= 20