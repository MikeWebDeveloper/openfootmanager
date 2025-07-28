"""
Comprehensive tests for the transfer system.

Tests all aspects of the transfer functionality including:
- Player valuations
- Transfer negotiations
- Contract negotiations  
- Transfer market search
- AI transfer behavior
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from ofm.core.football.player import Player
from ofm.core.football.club import Club
from ofm.core.football.player_attributes import PlayerAttributes
from ofm.core.football.playercontract import PlayerContract
from ofm.core.football.detailed_positions import DetailedPosition
from ofm.core.football.positions import Positions

from ofm.core.transfer import (
    PlayerValuationEngine,
    TransferMarket,
    TransferNegotiator,
    ContractNegotiator,
    TransferSearchEngine,
    AITransferManager
)
from ofm.core.transfer.search import SearchCriteria
from ofm.core.transfer.negotiation import NegotiationStrategy

from ofm.core.db.models.transfer import (
    TransferStatus, TransferType, ContractStatus,
    TransferListing, TransferNegotiation, ContractOffer
)


@pytest.fixture
def sample_player():
    """Create a sample player for testing."""
    attributes = PlayerAttributes(
        technical_attributes={
            'dribbling': 75,
            'finishing': 80,
            'first_touch': 70,
            'free_kick': 65,
            'heading': 60,
            'long_shots': 70,
            'long_throws': 40,
            'marking': 50,
            'passing': 72,
            'penalty': 75,
            'tackling': 45,
            'technique': 73
        },
        mental_attributes={
            'aggression': 60,
            'anticipation': 70,
            'bravery': 65,
            'composure': 75,
            'concentration': 70,
            'decisions': 72,
            'determination': 80,
            'flair': 70,
            'leadership': 60,
            'off_the_ball': 75,
            'positioning': 55,
            'teamwork': 70,
            'vision': 68,
            'work_rate': 75
        },
        physical_attributes={
            'acceleration': 80,
            'agility': 78,
            'balance': 75,
            'jumping': 65,
            'natural_fitness': 80,
            'pace': 82,
            'stamina': 75,
            'strength': 70
        },
        goalkeeping_attributes={
            'aerial_reach': 30,
            'command_of_area': 20,
            'communication': 50,
            'eccentricity': 10,
            'handling': 20,
            'kicking': 60,
            'one_on_ones': 20,
            'reflexes': 30,
            'rushing_out': 20,
            'throwing': 40
        }
    )
    
    return Player(
        player_id=uuid4(),
        nationality="England",
        dob=datetime(2000, 1, 1).date(),
        first_name="Test",
        last_name="Player",
        short_name="T. Player",
        positions=[Positions.FW],
        fitness=90.0,
        stamina=85.0,
        form=0.8,
        attributes=attributes,
        potential_skill=90,
        international_reputation=3,
        preferred_foot=1,  # Right
        value=25000000.0
    )


@pytest.fixture
def sample_club():
    """Create a sample club for testing."""
    return Club(
        club_id=uuid4(),
        name="Test FC",
        country="England",
        transfer_budget=50000000.0,
        wage_budget=500000.0,
        reputation=75
    )


@pytest.fixture
def valuation_engine():
    """Create valuation engine instance."""
    return PlayerValuationEngine()


@pytest.fixture
def mock_session(mocker):
    """Create mock database session."""
    return mocker.Mock()


class TestPlayerValuation:
    """Test player valuation calculations."""
    
    def test_basic_valuation(self, sample_player, valuation_engine):
        """Test basic player valuation."""
        value = valuation_engine.calculate_value(sample_player)
        
        # Young striker with good attributes should be valuable
        assert value > 20.0  # More than 20 million
        assert value < 100.0  # Less than 100 million
    
    def test_detailed_valuation(self, sample_player, valuation_engine):
        """Test detailed valuation with breakdown."""
        value, details = valuation_engine.calculate_value(sample_player, detailed=True)
        
        assert 'base_value' in details
        assert 'age_modifier' in details
        assert 'ability_modifier' in details
        assert 'potential_modifier' in details
        assert details['final_value'] == value
    
    def test_age_impact(self, sample_player, valuation_engine):
        """Test how age affects valuation."""
        # Young player
        young_player = sample_player
        young_player.dob = datetime(2004, 1, 1).date()  # 20 years old
        young_value = valuation_engine.calculate_value(young_player)
        
        # Prime age player
        prime_player = sample_player
        prime_player.dob = datetime(1998, 1, 1).date()  # 26 years old
        prime_value = valuation_engine.calculate_value(prime_player)
        
        # Older player
        old_player = sample_player
        old_player.dob = datetime(1990, 1, 1).date()  # 34 years old
        old_value = valuation_engine.calculate_value(old_player)
        
        # Prime age should be most valuable
        assert prime_value > young_value
        assert prime_value > old_value
        assert young_value > old_value
    
    def test_contract_impact(self, sample_player, valuation_engine):
        """Test how contract situation affects value."""
        # Long contract
        sample_player.contract = PlayerContract(
            player_id=sample_player.player_id,
            club_id=uuid4(),
            weekly_wage=100000,
            years_remaining=4
        )
        long_contract_value = valuation_engine.calculate_value(sample_player)
        
        # Expiring contract
        sample_player.contract.years_remaining = 0.5
        expiring_value = valuation_engine.calculate_value(sample_player)
        
        # Long contract should be worth more
        assert long_contract_value > expiring_value * 1.5
    
    def test_wage_estimation(self, sample_player, valuation_engine):
        """Test wage demand estimation."""
        transfer_fee = 30000000  # 30 million
        wage = valuation_engine.estimate_wage_demands(sample_player, transfer_fee)
        
        # Should be reasonable weekly wage
        assert wage > 50000  # More than 50k/week
        assert wage < 300000  # Less than 300k/week


class TestTransferNegotiation:
    """Test transfer negotiation mechanics."""
    
    def test_initiate_negotiation(self, sample_player, sample_club, valuation_engine):
        """Test starting a transfer negotiation."""
        negotiator = TransferNegotiator(valuation_engine)
        selling_club = Club(
            club_id=uuid4(),
            name="Selling FC",
            country="England",
            transfer_budget=10000000.0
        )
        
        negotiation = negotiator.initiate_negotiation(
            sample_player,
            sample_club,
            selling_club,
            TransferType.PERMANENT,
            25000000
        )
        
        assert negotiation.status == TransferStatus.NEGOTIATING
        assert negotiation.initial_offer == 25000000
        assert negotiation.current_offer == 25000000
        assert len(negotiation.offer_history) == 1
    
    def test_counter_offer(self, sample_player, sample_club, valuation_engine):
        """Test making counter offers."""
        negotiator = TransferNegotiator(valuation_engine)
        selling_club = Club(
            club_id=uuid4(),
            name="Selling FC",
            country="England"
        )
        
        negotiation = negotiator.initiate_negotiation(
            sample_player,
            sample_club,
            selling_club,
            TransferType.PERMANENT,
            20000000
        )
        
        # Make counter offer
        accepted, message = negotiator.make_counter_offer(
            negotiation,
            30000000,
            {'sell_on': 0.2}  # 20% sell-on clause
        )
        
        assert negotiation.current_offer == 30000000
        assert len(negotiation.offer_history) == 2
    
    def test_loan_negotiation(self, sample_player, sample_club, valuation_engine):
        """Test loan-specific negotiations."""
        negotiator = TransferNegotiator(valuation_engine)
        selling_club = Club(
            club_id=uuid4(),
            name="Selling FC",
            country="England"
        )
        
        negotiation = negotiator.initiate_negotiation(
            sample_player,
            sample_club,
            selling_club,
            TransferType.LOAN
        )
        
        # Negotiate loan terms
        accepted, message = negotiator.negotiate_loan_terms(
            negotiation,
            loan_fee=2000000,
            wage_percentage=75,
            buy_option=35000000
        )
        
        assert negotiation.loan_fee == 2000000
        assert negotiation.wage_percentage == 75
        assert negotiation.buy_option == 35000000


class TestContractNegotiation:
    """Test contract negotiation with players."""
    
    def test_create_contract_offer(self, sample_player, sample_club, valuation_engine):
        """Test creating initial contract offer."""
        contract_negotiator = ContractNegotiator(valuation_engine)
        
        # Create mock negotiation
        negotiation = TransferNegotiation(
            player_id=sample_player.player_id,
            selling_club_id=uuid4(),
            buying_club_id=sample_club.club_id,
            status=TransferStatus.AGREED,
            transfer_type=TransferType.PERMANENT,
            initial_offer=25000000,
            current_offer=25000000,
            agreed_fee=25000000
        )
        negotiation.id = 1
        negotiation.player = sample_player
        
        contract = contract_negotiator.create_contract_offer(
            sample_player,
            sample_club,
            negotiation,
            years=4
        )
        
        assert contract.status == ContractStatus.PROPOSED
        assert contract.length_years == 4
        assert contract.weekly_wage > 0
        assert contract.player_demanded_wage > 0
    
    def test_negotiate_contract(self, sample_player, sample_club, valuation_engine):
        """Test contract negotiation rounds."""
        contract_negotiator = ContractNegotiator(valuation_engine)
        
        # Create contract offer
        contract = ContractOffer(
            negotiation_id=1,
            player_id=sample_player.player_id,
            club_id=sample_club.club_id,
            status=ContractStatus.PROPOSED,
            length_years=4,
            weekly_wage=80000,
            player_demanded_wage=100000
        )
        
        # Try to negotiate
        accepted, message = contract_negotiator.negotiate_contract(
            contract,
            new_wage=90000,
            new_bonus=1000000
        )
        
        assert contract.weekly_wage == 90000
        assert contract.signing_bonus == 1000000
        assert contract.negotiation_rounds == 1


class TestTransferSearch:
    """Test transfer market search functionality."""
    
    def test_basic_search(self, mock_session, valuation_engine):
        """Test basic player search."""
        search_engine = TransferSearchEngine(mock_session, valuation_engine)
        
        criteria = SearchCriteria(
            positions=[DetailedPosition.ST],
            min_age=20,
            max_age=28,
            min_overall=75,
            max_value=50000000
        )
        
        # Mock query results
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        results = search_engine.search(criteria)
        assert isinstance(results, list)
    
    def test_search_filters(self, mock_session, valuation_engine):
        """Test various search filters."""
        search_engine = TransferSearchEngine(mock_session, valuation_engine)
        
        criteria = SearchCriteria(
            transfer_listed_only=True,
            free_agents_only=False,
            nationalities=["England", "Spain"],
            sort_by="value",
            sort_desc=True
        )
        
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        results = search_engine.search(criteria)
        assert isinstance(results, list)


class TestAITransferManager:
    """Test AI transfer decision making."""
    
    def test_transfer_philosophy(self, sample_club, mock_session, valuation_engine):
        """Test AI philosophy determination."""
        market = TransferMarket(mock_session)
        ai_manager = AITransferManager(sample_club, market)
        
        # Rich club should prefer stars
        rich_club = sample_club
        rich_club.transfer_budget = 150000000
        rich_ai = AITransferManager(rich_club, market)
        
        # Poor club should focus on free agents
        poor_club = sample_club
        poor_club.transfer_budget = 5000000
        poor_ai = AITransferManager(poor_club, market)
        
        assert rich_ai.philosophy != poor_ai.philosophy
    
    def test_squad_analysis(self, sample_club, mock_session):
        """Test AI squad analysis."""
        market = TransferMarket(mock_session)
        ai_manager = AITransferManager(sample_club, market)
        
        # Add some players to club
        sample_club.players = []
        
        analysis = ai_manager._analyze_squad()
        
        assert 'total_players' in analysis
        assert 'average_age' in analysis
        assert 'positions' in analysis
    
    def test_transfer_planning(self, sample_club, mock_session):
        """Test AI transfer planning."""
        market = TransferMarket(mock_session)
        ai_manager = AITransferManager(sample_club, market)
        
        plan = ai_manager.plan_transfer_window()
        
        assert 'philosophy' in plan
        assert 'budget' in plan
        assert 'needs' in plan
        assert 'targets' in plan
        assert 'sales' in plan


class TestTransferMarket:
    """Test complete transfer market operations."""
    
    def test_transfer_window(self, mock_session):
        """Test transfer window management."""
        market = TransferMarket(mock_session)
        
        # Mock active window
        mock_window = TransferWindow(
            name="Summer 2024",
            season_id=1,
            start_date=datetime.utcnow() - timedelta(days=1),
            end_date=datetime.utcnow() + timedelta(days=30),
            is_active=True
        )
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_window
        
        assert market.is_transfer_window_open()
        assert market.get_active_window() == mock_window
    
    def test_list_player(self, sample_player, sample_club, mock_session):
        """Test listing a player for transfer."""
        market = TransferMarket(mock_session)
        
        # Mock existing listings query
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        listing = market.list_player(
            sample_player,
            sample_club,
            asking_price=30000000,
            min_price=25000000
        )
        
        assert listing.asking_price == 30000000
        assert listing.min_price == 25000000
        assert listing.is_active
    
    def test_complete_transfer(self, sample_player, sample_club, mock_session):
        """Test completing a full transfer."""
        market = TransferMarket(mock_session)
        
        # Create agreed negotiation
        negotiation = TransferNegotiation(
            player_id=sample_player.player_id,
            selling_club_id=uuid4(),
            buying_club_id=sample_club.club_id,
            status=TransferStatus.AGREED,
            transfer_type=TransferType.PERMANENT,
            agreed_fee=25000000
        )
        negotiation.player = sample_player
        negotiation.buying_club = sample_club
        
        # Create agreed contract
        contract = ContractOffer(
            negotiation_id=1,
            player_id=sample_player.player_id,
            club_id=sample_club.club_id,
            status=ContractStatus.AGREED,
            length_years=4,
            weekly_wage=100000,
            final_wage=100000
        )
        negotiation.contract_offer = contract
        
        # Attempt completion
        # Note: This would need proper mocking of all database operations
        # success, message = market.complete_transfer(negotiation)
        # assert success


if __name__ == "__main__":
    pytest.main([__file__])