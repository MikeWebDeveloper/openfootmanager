#!/usr/bin/env python3
"""
Demo script showcasing the OpenFootManager Transfer System.

This demonstrates:
1. Player valuations with detailed breakdowns
2. Transfer market search and filtering
3. Transfer negotiations between clubs
4. Contract negotiations with players
5. AI transfer planning and execution
6. Transfer window simulation
"""

import sys
import os
from datetime import datetime, timedelta
from uuid import uuid4
import random

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from ofm.core.football.player import Player, PreferredFoot
from ofm.core.football.club import Club
from ofm.core.football.player_attributes import PlayerAttributes
from ofm.core.football.playercontract import PlayerContract
from ofm.core.football.positions import Positions
from ofm.core.football.detailed_positions import DetailedPosition

from ofm.core.transfer import (
    PlayerValuationEngine,
    TransferMarket,
    TransferSearchEngine,
    AITransferManager
)
from ofm.core.transfer.search import SearchCriteria
from ofm.core.db.models.transfer import TransferType, TransferWindow

# Mock database session for demo
class MockSession:
    def __init__(self):
        self.data = []
    
    def add(self, obj):
        self.data.append(obj)
    
    def commit(self):
        pass
    
    def query(self, model):
        return self
    
    def filter(self, *args):
        return self
    
    def all(self):
        return []
    
    def first(self):
        return None


def create_sample_player(name, age, position, overall, potential, nationality="England"):
    """Create a sample player with given attributes."""
    # Generate attributes based on overall rating
    attr_value = lambda base: max(1, min(99, base + random.randint(-10, 10)))
    
    attributes = PlayerAttributes(
        technical_attributes={
            'dribbling': attr_value(overall),
            'finishing': attr_value(overall),
            'first_touch': attr_value(overall),
            'free_kick': attr_value(overall - 10),
            'heading': attr_value(overall - 5),
            'long_shots': attr_value(overall - 5),
            'long_throws': attr_value(40),
            'marking': attr_value(overall - 20),
            'passing': attr_value(overall),
            'penalty': attr_value(overall),
            'tackling': attr_value(overall - 30),
            'technique': attr_value(overall)
        },
        mental_attributes={
            'aggression': attr_value(60),
            'anticipation': attr_value(overall),
            'bravery': attr_value(65),
            'composure': attr_value(overall),
            'concentration': attr_value(overall),
            'decisions': attr_value(overall),
            'determination': attr_value(75),
            'flair': attr_value(overall - 5),
            'leadership': attr_value(60),
            'off_the_ball': attr_value(overall),
            'positioning': attr_value(overall - 10),
            'teamwork': attr_value(70),
            'vision': attr_value(overall),
            'work_rate': attr_value(70)
        },
        physical_attributes={
            'acceleration': attr_value(overall - 5),
            'agility': attr_value(overall - 5),
            'balance': attr_value(overall - 5),
            'jumping': attr_value(65),
            'natural_fitness': attr_value(75),
            'pace': attr_value(overall - 5),
            'stamina': attr_value(75),
            'strength': attr_value(70)
        },
        goalkeeping_attributes={
            'aerial_reach': attr_value(30),
            'command_of_area': attr_value(20),
            'communication': attr_value(50),
            'eccentricity': attr_value(10),
            'handling': attr_value(20),
            'kicking': attr_value(60),
            'one_on_ones': attr_value(20),
            'reflexes': attr_value(30),
            'rushing_out': attr_value(20),
            'throwing': attr_value(40)
        }
    )
    
    birth_year = datetime.now().year - age
    
    return Player(
        player_id=uuid4(),
        nationality=nationality,
        dob=datetime(birth_year, random.randint(1, 12), random.randint(1, 28)).date(),
        first_name=name.split()[0],
        last_name=name.split()[1] if len(name.split()) > 1 else "Player",
        short_name=name,
        positions=[position],
        fitness=random.uniform(80, 95),
        stamina=random.uniform(80, 90),
        form=random.uniform(0.6, 0.9),
        attributes=attributes,
        potential_skill=potential,
        international_reputation=min(5, overall // 18),
        preferred_foot=PreferredFoot.RIGHT,
        value=0  # Will be calculated
    )


def create_sample_club(name, country, budget):
    """Create a sample club."""
    return Club(
        club_id=uuid4(),
        name=name,
        country=country,
        transfer_budget=budget,
        wage_budget=budget / 100,  # 1% of transfer budget
        reputation=random.randint(60, 90)
    )


def demo_valuation_system():
    """Demonstrate player valuation system."""
    print("\n" + "="*60)
    print("PLAYER VALUATION SYSTEM DEMO")
    print("="*60)
    
    valuation_engine = PlayerValuationEngine()
    
    # Create players of different profiles
    players = [
        ("Young Wonderkid", create_sample_player("Marcus Young", 19, Positions.FW, 75, 92)),
        ("Prime Striker", create_sample_player("Roberto Carlos", 26, Positions.FW, 88, 88)),
        ("Aging Veteran", create_sample_player("Frank Old", 33, Positions.MF, 82, 82)),
        ("Average Player", create_sample_player("John Average", 24, Positions.DF, 70, 75)),
    ]
    
    for label, player in players:
        value, details = valuation_engine.calculate_value(player, detailed=True)
        print(f"\n{label}: {player.short_name}")
        print(f"  Age: {datetime.now().year - player.dob.year}")
        print(f"  Overall: {player.attributes.get_overall()}")
        print(f"  Potential: {player.potential_skill}")
        print(f"  Market Value: £{value:,.1f}M")
        print(f"  Breakdown:")
        print(f"    - Base Value: £{details['base_value']:,.1f}M")
        print(f"    - Age Modifier: {details['age_modifier']:.2f}x")
        print(f"    - Ability Modifier: {details['ability_modifier']:.2f}x")
        print(f"    - Potential Modifier: {details['potential_modifier']:.2f}x")
        
        # Add contract and show impact
        player.contract = PlayerContract(
            player_id=player.player_id,
            club_id=uuid4(),
            weekly_wage=50000,
            years_remaining=1
        )
        
        new_value = valuation_engine.calculate_value(player)
        print(f"  With 1 year left on contract: £{new_value:,.1f}M")
        
        wage = valuation_engine.estimate_wage_demands(player, value)
        print(f"  Estimated wage demands: £{wage:,.0f}/week")


def demo_transfer_search():
    """Demonstrate transfer market search."""
    print("\n" + "="*60)
    print("TRANSFER MARKET SEARCH DEMO")
    print("="*60)
    
    # In real implementation, these would be used:
    # session = MockSession()
    # valuation_engine = PlayerValuationEngine()
    
    # Create a searching club
    club = create_sample_club("Manchester Blue", "England", 100000000)
    
    print(f"\n{club.name} Transfer Budget: £{club.transfer_budget:,.0f}")
    print("\nSearching for a striker...")
    
    # Create search criteria (demonstration only)
    # In real implementation, this would be used with TransferSearchEngine
    SearchCriteria(
        positions=[DetailedPosition.ST],
        min_age=21,
        max_age=28,
        min_overall=80,
        max_value=50000000,
        sort_by="value"
    )
    
    print("\nSearch Criteria:")
    print(f"  - Position: Striker")
    print(f"  - Age: 21-28")
    print(f"  - Minimum Overall: 80")
    print(f"  - Maximum Value: £50M")
    
    # Note: In real implementation, this would search actual database
    print("\n(In real implementation, this would return matching players from database)")


def demo_transfer_negotiation():
    """Demonstrate transfer negotiation process."""
    print("\n" + "="*60)
    print("TRANSFER NEGOTIATION DEMO")
    print("="*60)
    
    session = MockSession()
    market = TransferMarket(session)
    
    # Create clubs and player
    buying_club = create_sample_club("Real Barcelona", "Spain", 150000000)
    selling_club = create_sample_club("Ajax", "Netherlands", 50000000)
    player = create_sample_player("Johan Stars", 23, Positions.MF, 82, 90, "Netherlands")
    player.club_id = selling_club.club_id
    player.club = selling_club
    
    # Add contract
    player.contract = PlayerContract(
        player_id=player.player_id,
        club_id=selling_club.club_id,
        weekly_wage=60000,
        years_remaining=3
    )
    
    # Calculate player value
    value = market.valuation_engine.calculate_value(player)
    print(f"\nPlayer: {player.short_name}")
    print(f"Current Club: {selling_club.name}")
    print(f"Market Value: £{value:,.1f}M")
    print(f"Contract: {player.contract.years_remaining} years remaining")
    
    # List player
    print(f"\n{selling_club.name} lists {player.short_name} for transfer")
    listing = market.list_player(player, selling_club, asking_price=value * 1.2)
    print(f"Asking Price: £{listing.asking_price:,.1f}M")
    print(f"Minimum Price: £{listing.min_price:,.1f}M")
    
    # Make bid
    print(f"\n{buying_club.name} makes initial bid")
    bid_amount = value * 0.9
    print(f"Bid Amount: £{bid_amount:,.1f}M")
    
    # Simulate negotiation rounds
    print("\nNegotiation Progress:")
    print(f"Round 1: {buying_club.name} bids £{bid_amount:,.1f}M - Too low")
    
    bid_amount = value * 1.05
    print(f"Round 2: {buying_club.name} raises to £{bid_amount:,.1f}M - Getting closer")
    
    bid_amount = value * 1.15
    print(f"Round 3: {buying_club.name} final offer £{bid_amount:,.1f}M - ACCEPTED")
    
    # Contract negotiation
    print(f"\n{player.short_name} negotiating personal terms with {buying_club.name}")
    wage_demand = market.valuation_engine.estimate_wage_demands(player, bid_amount)
    print(f"Player wage demands: £{wage_demand:,.0f}/week")
    print(f"Club offers: £{wage_demand * 0.9:,.0f}/week")
    print(f"Agreement reached at: £{wage_demand * 0.95:,.0f}/week")
    
    print(f"\nTransfer Complete!")
    print(f"{player.short_name} joins {buying_club.name} for £{bid_amount:,.1f}M")
    print(f"Contract: 4 years, £{wage_demand * 0.95:,.0f}/week")


def demo_ai_transfer_planning():
    """Demonstrate AI transfer planning."""
    print("\n" + "="*60)
    print("AI TRANSFER PLANNING DEMO")
    print("="*60)
    
    session = MockSession()
    market = TransferMarket(session)
    
    # Create AI-controlled club
    club = create_sample_club("Atletico Milan", "Italy", 80000000)
    
    # Add some existing players
    club.players = [
        create_sample_player("Giuseppe Keeper", 28, Positions.GK, 78, 78, "Italy"),
        create_sample_player("Marco Defender", 26, Positions.DF, 76, 76, "Italy"),
        create_sample_player("Luigi Midfielder", 24, Positions.MF, 77, 80, "Italy"),
        create_sample_player("Paolo Striker", 31, Positions.FW, 79, 79, "Italy"),
    ]
    
    ai_manager = AITransferManager(club, market)
    
    print(f"\n{club.name} Transfer Planning")
    print(f"Budget: £{club.transfer_budget:,.0f}")
    print(f"Current Squad Size: {len(club.players)}")
    
    # Get transfer plan
    plan = ai_manager.plan_transfer_window()
    
    print(f"\nTransfer Philosophy: {plan['philosophy']}")
    print(f"\nSquad Needs (Top 3):")
    for i, need in enumerate(plan['needs'][:3], 1):
        print(f"  {i}. {need['position']} - Priority: {need['priority']}/10")
    
    print(f"\nTransfer Targets:")
    if not plan['targets']:
        print("  (Would show recommended players from database)")
    else:
        for i, target in enumerate(plan['targets'][:3], 1):
            print(f"  {i}. {target['player']} ({target['position']}) - £{target['value']:,.1f}M")
    
    print(f"\nPlayers to Sell:")
    if not plan['sales']:
        print("  None identified")
    else:
        for sale in plan['sales']:
            print(f"  - {sale['player']}: {sale['reason']} (£{sale['asking_price']:,.1f}M)")


def demo_transfer_window_simulation():
    """Demonstrate transfer window activity."""
    print("\n" + "="*60)
    print("TRANSFER WINDOW SIMULATION")
    print("="*60)
    
    # In real implementation, session would be used
    # session = MockSession()
    
    # Create transfer window
    window = TransferWindow(
        name="Summer 2024",
        season_id=1,
        start_date=datetime.now() - timedelta(days=1),
        end_date=datetime.now() + timedelta(days=30),
        is_active=True
    )
    
    print(f"\nTransfer Window: {window.name}")
    print(f"Opens: {window.start_date.strftime('%Y-%m-%d')}")
    print(f"Closes: {window.end_date.strftime('%Y-%m-%d')}")
    print(f"Days Remaining: {(window.end_date - datetime.now()).days}")
    
    # Simulate some transfer activity
    print("\nRecent Transfer Activity:")
    transfers = [
        ("Kylian Stars", "PSG", "Real Madrid", 180.0),
        ("Harry Striker", "Tottenham", "Bayern Munich", 100.0),
        ("Bruno Creator", "Sporting", "Manchester United", 65.0),
        ("Jadon Winger", "Dortmund", "Manchester United", 73.0),
    ]
    
    total_spending = 0
    for player, from_club, to_club, fee in transfers:
        print(f"  - {player}: {from_club} → {to_club} (£{fee:.1f}M)")
        total_spending += fee
    
    print(f"\nTotal Window Spending: £{total_spending:.1f}M")
    print(f"Average Transfer Fee: £{total_spending/len(transfers):.1f}M")
    
    # Show deadline day activity
    print("\nDeadline Day Activity:")
    print("  - 3 hours remaining: 15 transfers completed")
    print("  - 2 hours remaining: 8 transfers in negotiation")
    print("  - 1 hour remaining: 5 last-minute deals")
    print("  - Window closes: 28 total transfers today")


def main():
    """Run all demonstrations."""
    print("\n" + "#"*60)
    print("#" + " "*18 + "OPENFOOTMANAGER" + " "*18 + "#")
    print("#" + " "*13 + "TRANSFER SYSTEM DEMO" + " "*13 + "#")
    print("#"*60)
    
    demos = [
        ("Player Valuation System", demo_valuation_system),
        ("Transfer Market Search", demo_transfer_search),
        ("Transfer Negotiation Process", demo_transfer_negotiation),
        ("AI Transfer Planning", demo_ai_transfer_planning),
        ("Transfer Window Simulation", demo_transfer_window_simulation),
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        input(f"\nPress Enter to continue to demo {i}/{len(demos)}: {name}")
        demo_func()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\nThe Transfer System includes:")
    print("  ✓ Sophisticated player valuation algorithm")
    print("  ✓ Transfer market search with filters")
    print("  ✓ Multi-round transfer negotiations")
    print("  ✓ Contract negotiations with players")
    print("  ✓ AI transfer planning and strategy")
    print("  ✓ Transfer window management")
    print("  ✓ Loan deals with options/obligations")
    print("  ✓ Performance-based clauses")
    print("  ✓ Agent fees and bonuses")
    print("  ✓ Transfer history tracking")


if __name__ == "__main__":
    main()