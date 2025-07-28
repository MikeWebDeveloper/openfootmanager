# OpenFootManager Transfer System Documentation

## Overview

The Transfer System in OpenFootManager is a comprehensive module that handles all aspects of player transfers, including valuations, negotiations, contracts, and AI-driven transfer strategies. This document provides a complete guide to understanding and using the transfer system.

## Architecture

### Core Components

1. **Player Valuation Engine** (`valuation.py`)
   - Calculates player market values based on multiple factors
   - Estimates wage demands
   - Provides detailed valuation breakdowns

2. **Transfer Market** (`market.py`)
   - Central hub for all transfer operations
   - Manages transfer windows
   - Handles transfer completions and financial transactions

3. **Negotiation System** (`negotiation.py`)
   - Transfer fee negotiations between clubs
   - Contract negotiations with players
   - Support for various deal structures (permanent, loan, etc.)

4. **Search Engine** (`search.py`)
   - Advanced player search with multiple filters
   - AI recommendations
   - Similar player discovery

5. **AI Transfer Manager** (`ai_manager.py`)
   - Automated transfer planning for AI clubs
   - Squad analysis and needs assessment
   - Transfer strategy implementation

6. **Calendar Integration** (`calendar_integration.py`)
   - Transfer window management
   - Deadline day handling
   - Integration with season calendar

## Database Models

### Transfer-Related Tables

```python
# Player Market Values
PlayerMarketValue
├── player_id (FK)
├── value
├── date
├── base_value
├── age_modifier
├── ability_modifier
├── potential_modifier
├── form_modifier
├── contract_modifier
├── injury_modifier
└── calculation_details (JSON)

# Transfer Listings
TransferListing
├── player_id (FK)
├── club_id (FK)
├── asking_price
├── min_price
├── listed_date
├── expiry_date
├── transfer_type
├── loan_fee
├── future_fee
├── wage_contribution
├── is_active
└── is_public

# Transfer Negotiations
TransferNegotiation
├── listing_id (FK)
├── player_id (FK)
├── selling_club_id (FK)
├── buying_club_id (FK)
├── status
├── transfer_type
├── initial_offer
├── current_offer
├── agreed_fee
├── agent_fee
├── signing_bonus
├── performance_bonuses (JSON)
├── sell_on_percentage
├── loan_fee
├── wage_percentage
├── buy_option
├── buy_obligation
├── started_date
├── deadline
├── completed_date
└── offer_history (JSON)

# Contract Offers
ContractOffer
├── negotiation_id (FK)
├── player_id (FK)
├── club_id (FK)
├── status
├── length_years
├── weekly_wage
├── signing_bonus
├── loyalty_bonus
├── appearance_fee
├── goal_bonus
├── clean_sheet_bonus
├── performance_bonuses (JSON)
├── release_clause
├── wage_rise_percentage
├── agent_fee
├── image_rights_percentage
├── player_demanded_wage
├── final_wage
├── negotiation_rounds
├── offered_date
├── response_deadline
└── signed_date

# Transfer History
TransferHistory
├── player_id (FK)
├── from_club_id (FK)
├── to_club_id (FK)
├── transfer_type
├── transfer_fee
├── total_cost
├── contract_length
├── weekly_wage
├── agent_fee
├── signing_bonus
├── sell_on_clause
├── transfer_date
├── contract_end_date
├── appearances_clause_triggered
└── goals_clause_triggered

# Transfer Windows
TransferWindow
├── name
├── season_id (FK)
├── start_date
├── end_date
├── country
├── is_active
├── allows_loans
├── allows_free_agents
└── domestic_only
```

## Player Valuation

### Valuation Algorithm

The player valuation system considers multiple factors:

1. **Base Value**: Position-specific base values
   - Strikers/CF: £30M base
   - Attacking Midfielders: £25M base
   - Central Midfielders: £20M base
   - Defenders: £12-15M base
   - Goalkeepers: £10M base

2. **Age Multiplier**: Peak value at 25-26
   - 16-20: 0.3x to 0.9x
   - 21-27: 1.0x to 1.4x
   - 28-35: 1.2x to 0.15x

3. **Ability Multiplier**: Based on overall rating
   - 90+: 4.0x (World class)
   - 85-89: 3.0x (Elite)
   - 80-84: 2.2x (Very good)
   - 75-79: 1.6x (Good)
   - 70-74: 1.2x (Decent)
   - Below 70: 0.3x to 0.8x

4. **Other Factors**:
   - Potential vs Current ability
   - Contract situation
   - Injury status
   - International reputation
   - Positional versatility
   - Recent form

### Example Calculation

```python
# Young striker with high potential
Base Value: £30M
Age (21): 1.0x
Ability (75): 1.6x
Potential Gap (15): 1.5x
Contract (4 years): 1.0x
No injuries: 1.0x

Final Value = 30 * 1.0 * 1.6 * 1.5 * 1.0 * 1.0 = £72M
```

## Transfer Negotiations

### Negotiation Flow

1. **Initial Contact**
   - Buying club identifies target
   - Makes initial bid (usually 70-110% of value)
   - Selling club evaluates offer

2. **Counter-Offers**
   - Maximum 10 rounds of negotiation
   - Each side can adjust demands
   - Additional terms (sell-on clauses, bonuses)

3. **Agreement**
   - Transfer fee agreed
   - Move to contract negotiations
   - Or negotiations break down

### Negotiation Strategies

- **Aggressive**: Start low (70%), increase slowly
- **Fair**: Start near valuation (90%)
- **Desperate**: Will overpay (110%+)
- **Hardball**: Won't budge much (60% start)

## Contract Negotiations

### Contract Components

1. **Basic Terms**
   - Length (1-5 years typically)
   - Weekly wage
   - Signing bonus

2. **Bonuses**
   - Appearance fees
   - Goal/clean sheet bonuses
   - Performance incentives

3. **Clauses**
   - Release clause
   - Annual wage rises
   - Image rights

### Wage Calculation

Wages are estimated based on:
- Transfer fee paid
- Player ability
- Age (older players want security)
- Market conditions

Typical range: 0.5-2% of market value annually

## Transfer Search

### Search Criteria

```python
SearchCriteria(
    positions=[DetailedPosition.ST],      # Positions to search
    min_age=21,                          # Minimum age
    max_age=28,                          # Maximum age
    min_overall=75,                      # Minimum ability
    max_overall=85,                      # Maximum ability
    min_potential=80,                    # Minimum potential
    max_value=50000000,                  # Maximum price
    max_wage=100000,                     # Maximum weekly wage
    transfer_listed_only=False,          # Only listed players
    free_agents_only=False,              # Only free agents
    loan_available=False,                # Available for loan
    nationalities=["England", "Spain"],  # Specific nationalities
    exclude_own_players=True,            # Exclude own squad
    sort_by="value",                     # Sort field
    sort_desc=True,                      # Sort order
    limit=50,                            # Results per page
    offset=0                             # Pagination offset
)
```

### AI Recommendations

The system can recommend players based on:
- Club's squad needs
- Budget constraints
- Playing style
- League level

## AI Transfer Behavior

### Transfer Philosophies

1. **Youth Development**: Focus on young players with potential
2. **Established Stars**: Buy proven quality
3. **Moneyball**: Value for money, analytics-driven
4. **Domestic Focus**: Prefer local players
5. **Loan Army**: Build through loans
6. **Free Agents**: Focus on free transfers

### Squad Analysis

AI managers analyze:
- Position depth (minimum players per position)
- Age profile
- Contract situations
- Squad quality vs league level

### Transfer Planning

1. **Identify Needs**: Which positions need strengthening
2. **Set Priorities**: Critical vs nice-to-have signings
3. **Find Targets**: Search for suitable players
4. **Execute Plan**: Make bids and complete transfers

## Transfer Windows

### Standard Windows

- **Summer Window**: June 1 - August 31
- **Winter Window**: January 1-31

### Regional Variations

Different countries have different windows:
- Russia: February-February, July-August
- Brazil: January-April, July-August
- MLS: February-May, July-August

### Window Events

- Window opens
- One week warning
- Deadline day
- Window closes

## Usage Examples

### Listing a Player

```python
# List a player for transfer
listing = market.list_player(
    player=player,
    club=selling_club,
    asking_price=30000000,  # £30M
    min_price=25000000,     # Will accept £25M+
    transfer_type=TransferType.PERMANENT
)
```

### Making a Transfer Bid

```python
# Make initial bid
negotiation, message = market.make_transfer_bid(
    player=target_player,
    buying_club=my_club,
    bid_amount=25000000,
    transfer_type=TransferType.PERMANENT
)

# Negotiate if needed
if negotiation.status == TransferStatus.NEGOTIATING:
    accepted, message = market.negotiate_transfer(
        negotiation=negotiation,
        new_bid=28000000
    )
```

### Completing a Transfer

```python
# After fee agreed, make contract offer
contract, message = market.make_contract_offer(
    negotiation=negotiation,
    years=4,
    weekly_wage=100000
)

# If contract agreed, complete transfer
if contract.status == ContractStatus.AGREED:
    success, message = market.complete_transfer(negotiation)
```

### AI Transfer Planning

```python
# Create AI manager for a club
ai_manager = AITransferManager(club, market)

# Get transfer plan
plan = ai_manager.plan_transfer_window()

# Execute plan
transactions = ai_manager.execute_transfer_plan()
```

## Performance Considerations

1. **Caching**: Player valuations are cached to avoid recalculation
2. **Batch Operations**: Multiple transfers can be processed together
3. **Async Support**: Long operations support async execution
4. **Database Optimization**: Indexes on frequently searched fields

## Future Enhancements

1. **Agent System**: Individual agents with relationships
2. **Third-Party Ownership**: Complex ownership structures
3. **Work Permits**: International transfer restrictions
4. **Financial Fair Play**: Budget constraints based on revenue
5. **Player Preferences**: Players preferring certain clubs/leagues
6. **Media Speculation**: Transfer rumors and reliability
7. **Loan Recall Options**: Ability to recall loaned players
8. **Swap Deals**: Player + cash exchanges
9. **Tribunal Fees**: For young player compensation
10. **Pre-Contracts**: Signing players on expiring contracts

## Testing

The transfer system includes comprehensive tests covering:
- Valuation calculations
- Negotiation mechanics
- Contract terms
- Search functionality
- AI behavior
- Edge cases and error handling

Run tests with:
```bash
pytest ofm/tests/test_transfer_system.py -v
```

## Integration Points

The transfer system integrates with:
- **Calendar System**: Transfer windows and deadlines
- **Financial System**: Budget management
- **Save/Load System**: Persistence of transfer data
- **UI System**: Transfer market interface
- **Match System**: Player availability after transfers
- **Season System**: Window timing and rules