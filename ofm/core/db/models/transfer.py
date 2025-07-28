"""
Transfer system database models for OpenFootManager.

This module contains all transfer-related database models including:
- Transfer listings and market
- Transfer negotiations and bids
- Player valuations
- Transfer history
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class TransferStatus(Enum):
    """Status of a transfer negotiation."""

    LISTED = "listed"
    NEGOTIATING = "negotiating"
    AGREED = "agreed"
    MEDICAL = "medical"
    COMPLETED = "completed"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ContractStatus(Enum):
    """Status of contract negotiations."""

    PROPOSED = "proposed"
    NEGOTIATING = "negotiating"
    AGREED = "agreed"
    SIGNED = "signed"
    REJECTED = "rejected"


class TransferType(Enum):
    """Type of transfer."""

    PERMANENT = "permanent"
    LOAN = "loan"
    LOAN_TO_BUY = "loan_to_buy"
    FREE = "free"


class PlayerMarketValue(Base):
    """Tracks player market values over time."""

    __tablename__ = "player_market_values"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, nullable=False)  # Removed ForeignKey since Player is not a DB model
    value = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

    # Factors contributing to valuation
    base_value = Column(Float, nullable=False)
    age_modifier = Column(Float, default=1.0)
    ability_modifier = Column(Float, default=1.0)
    potential_modifier = Column(Float, default=1.0)
    form_modifier = Column(Float, default=1.0)
    contract_modifier = Column(Float, default=1.0)
    injury_modifier = Column(Float, default=1.0)

    # Additional metadata
    calculation_details = Column(JSON)  # Store detailed calculation breakdown

    # Relationships - commented out since Player/Club are not SQLAlchemy models
    # player = relationship("Player", back_populates="market_values")


class TransferListing(Base):
    """Players listed for transfer by their clubs."""

    __tablename__ = "transfer_listings"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, nullable=False)  # Removed ForeignKey since Player is not a DB model
    club_id = Column(Integer, nullable=False)  # Removed ForeignKey since Club is not a DB model

    # Listing details
    asking_price = Column(Float, nullable=False)
    min_price = Column(Float, nullable=False)  # Minimum acceptable price
    listed_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime)

    # Transfer preferences
    transfer_type = Column(SQLEnum(TransferType), default=TransferType.PERMANENT)
    loan_fee = Column(Float)  # For loan deals
    future_fee = Column(Float)  # For loan-to-buy deals
    wage_contribution = Column(Float)  # Percentage of wages to pay for loans

    # Status
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)  # Private listings for agent circulation

    # Relationships
    # player = relationship("Player", back_populates="transfer_listings")
    # Commented - not SQLAlchemy model
    # club = relationship("Club", back_populates="transfer_listings")
    # Commented - not SQLAlchemy model
    negotiations = relationship("TransferNegotiation", back_populates="listing")


class TransferNegotiation(Base):
    """Tracks transfer negotiations between clubs."""

    __tablename__ = "transfer_negotiations"

    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer, ForeignKey("transfer_listings.id"))
    player_id = Column(Integer, nullable=False)  # Removed ForeignKey since Player is not a DB model
    selling_club_id = Column(Integer, nullable=False)
    buying_club_id = Column(Integer, nullable=False)

    # Negotiation details
    status = Column(SQLEnum(TransferStatus), default=TransferStatus.NEGOTIATING)
    transfer_type = Column(SQLEnum(TransferType), nullable=False)

    # Financial terms
    initial_offer = Column(Float, nullable=False)
    current_offer = Column(Float, nullable=False)
    agreed_fee = Column(Float)

    # Additional fees
    agent_fee = Column(Float, default=0)
    signing_bonus = Column(Float, default=0)

    # Performance clauses
    performance_bonuses = Column(JSON)  # Structure: {"appearances": 1000000, "goals": 500000}
    sell_on_percentage = Column(Float, default=0)  # Future sale percentage

    # Loan specific
    loan_fee = Column(Float)
    wage_percentage = Column(Float)  # Percentage of wages paid by loaning club
    buy_option = Column(Float)  # Optional future purchase price
    buy_obligation = Column(Boolean, default=False)  # Mandatory future purchase

    # Timeline
    started_date = Column(DateTime, default=datetime.utcnow)
    deadline = Column(DateTime)
    completed_date = Column(DateTime)

    # Negotiation history
    offer_history = Column(JSON, default=list)  # List of offers and counter-offers

    # Relationships
    listing = relationship("TransferListing", back_populates="negotiations")
    # player = relationship("Player", back_populates="transfer_negotiations")
    # selling_club = relationship("Club", foreign_keys=[selling_club_id])
    # buying_club = relationship("Club", foreign_keys=[buying_club_id])
    contract_offer = relationship("ContractOffer", back_populates="negotiation", uselist=False)


class ContractOffer(Base):
    """Contract offers made to players during transfers."""

    __tablename__ = "contract_offers"

    id = Column(Integer, primary_key=True)
    negotiation_id = Column(Integer, ForeignKey("transfer_negotiations.id"), nullable=False)
    player_id = Column(Integer, nullable=False)
    club_id = Column(Integer, nullable=False)

    # Contract terms
    status = Column(SQLEnum(ContractStatus), default=ContractStatus.PROPOSED)
    length_years = Column(Integer, nullable=False)
    weekly_wage = Column(Float, nullable=False)

    # Bonuses
    signing_bonus = Column(Float, default=0)
    loyalty_bonus = Column(Float, default=0)
    appearance_fee = Column(Float, default=0)
    goal_bonus = Column(Float, default=0)
    clean_sheet_bonus = Column(Float, default=0)

    # Performance bonuses
    performance_bonuses = Column(JSON)  # Structured performance incentives

    # Clauses
    release_clause = Column(Float)
    wage_rise_percentage = Column(Float)  # Annual wage increase

    # Agent demands
    agent_fee = Column(Float, default=0)
    image_rights_percentage = Column(Float, default=0)

    # Negotiation tracking
    player_demanded_wage = Column(Float)
    final_wage = Column(Float)
    negotiation_rounds = Column(Integer, default=0)

    # Dates
    offered_date = Column(DateTime, default=datetime.utcnow)
    response_deadline = Column(DateTime)
    signed_date = Column(DateTime)

    # Relationships
    negotiation = relationship("TransferNegotiation", back_populates="contract_offer")
    # player = relationship("Player", back_populates="contract_offers")
    # club = relationship("Club", back_populates="contract_offers")


class TransferHistory(Base):
    """Historical record of completed transfers."""

    __tablename__ = "transfer_history"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, nullable=False)
    from_club_id = Column(Integer)
    to_club_id = Column(Integer, nullable=False)

    # Transfer details
    transfer_type = Column(SQLEnum(TransferType), nullable=False)
    transfer_fee = Column(Float, default=0)
    total_cost = Column(Float)  # Including all fees and bonuses

    # Contract details
    contract_length = Column(Integer)
    weekly_wage = Column(Float)

    # Additional details
    agent_fee = Column(Float, default=0)
    signing_bonus = Column(Float, default=0)
    sell_on_clause = Column(Float, default=0)

    # Dates
    transfer_date = Column(DateTime, default=datetime.utcnow)
    contract_end_date = Column(DateTime)

    # Performance tracking
    appearances_clause_triggered = Column(Boolean, default=False)
    goals_clause_triggered = Column(Boolean, default=False)

    # Relationships
    # player = relationship("Player", back_populates="transfer_history")
    # from_club = relationship("Club", foreign_keys=[from_club_id])
    # to_club = relationship("Club", foreign_keys=[to_club_id])


class TransferWindow(Base):
    """Transfer window periods for different leagues."""

    __tablename__ = "transfer_windows"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    season_id = Column(Integer, nullable=False)

    # Window periods
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    # Regional settings
    country = Column(String(3))  # ISO code, null for international
    is_active = Column(Boolean, default=True)

    # Special rules
    allows_loans = Column(Boolean, default=True)
    allows_free_agents = Column(Boolean, default=True)
    domestic_only = Column(Boolean, default=False)

    # Relationships
    # season = relationship("Season", back_populates="transfer_windows")
