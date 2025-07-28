#!/usr/bin/env python3
"""
OpenFoot Manager - Simple GUI Demo
==================================

A simplified GUI demo that showcases working components without the problematic ones.
This demonstrates that the basic GUI infrastructure works.
"""

import os
import sys
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from ofm.core.db.models.base import Base, engine, SessionLocal
from ofm.core.db.models import League, Competition, Fixture, FixtureStatus
from ofm.core.season.season_manager import SeasonManager
from ofm.core.season.calendar import GameCalendar
from ofm.core.save.save_manager import SaveManager
from ofm.core.settings import Settings


class SimpleOFMApp:
    """A simplified version of the OFM app for testing"""

    def __init__(self):
        # Initialize window (use standard theme)
        self.window = ttk.Window(title="OpenFoot Manager - Demo", themename="darkly")
        self.window.geometry("800x600")
        
        # Initialize core systems
        self.setup_database()
        self.setup_ui()
        
    def setup_database(self):
        """Initialize database and core systems"""
        # Create database
        Base.metadata.create_all(bind=engine)
        self.session = SessionLocal()
        
        # Initialize managers
        self.season_manager = SeasonManager(self.session)
        self.calendar = GameCalendar(self.session)
        self.save_manager = SaveManager(self.session)
        
        # Create demo data
        self.create_demo_data()
        
    def create_demo_data(self):
        """Create some demo data to display"""
        # Create league if not exists
        existing_league = self.session.query(League).first()
        if not existing_league:
            self.league = League(
                name="Premier League Demo",
                country="ENG",
                level=1,
                num_teams=4,
                promotion_places=0,
                relegation_places=1
            )
            self.session.add(self.league)
            self.session.flush()
            
            # Create demo teams
            self.team_ids = [
                "team_arsenal",
                "team_chelsea", 
                "team_liverpool",
                "team_manchester_united"
            ]
            
            # Create season
            self.league_season = self.season_manager.create_season(
                league=self.league,
                teams=self.team_ids,
                season_year=2024,
                start_date=datetime(2024, 8, 15),
                end_date=datetime(2025, 5, 25)
            )
            
            # Simulate some matches
            fixtures = self.session.query(Fixture).filter_by(
                competition_id=self.league_season.competition.id
            ).limit(3).all()
            
            for i, fixture in enumerate(fixtures):
                fixture.home_score = i + 1
                fixture.away_score = i
                fixture.status = FixtureStatus.COMPLETED
                self.season_manager.update_table_after_fixture(fixture)
                
            self.session.commit()
        else:
            self.league = existing_league
            self.league_season = self.session.query(League).first().seasons[0] if existing_league.seasons else None
            
    def setup_ui(self):
        """Create the user interface"""
        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="OpenFoot Manager - Phase 1 Demo",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=BOTH, expand=True)
        
        # Add tabs
        self.create_league_tab()
        self.create_calendar_tab()
        self.create_saves_tab()
        self.create_status_tab()
        
    def create_league_tab(self):
        """Create league information tab"""
        league_frame = ttk.Frame(self.notebook)
        self.notebook.add(league_frame, text="League")
        
        # League info
        info_frame = ttk.LabelFrame(league_frame, text="League Information")
        info_frame.pack(fill=X, padx=10, pady=10)
        
        if self.league:
            ttk.Label(info_frame, text=f"Name: {self.league.name}").pack(anchor=W, padx=10, pady=2)
            ttk.Label(info_frame, text=f"Country: {self.league.country}").pack(anchor=W, padx=10, pady=2)
            ttk.Label(info_frame, text=f"Level: {self.league.level}").pack(anchor=W, padx=10, pady=2)
            ttk.Label(info_frame, text=f"Teams: {self.league.num_teams}").pack(anchor=W, padx=10, pady=2)
        
        # League table
        table_frame = ttk.LabelFrame(league_frame, text="League Table")
        table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        if self.league_season:
            # Create simple table display
            headers = ["Pos", "Team", "P", "W", "D", "L", "GF", "GA", "GD", "Pts"]
            
            # Headers
            header_frame = ttk.Frame(table_frame)
            header_frame.pack(fill=X, padx=5, pady=5)
            
            for i, header in enumerate(headers):
                ttk.Label(header_frame, text=header, font=("Arial", 9, "bold")).grid(
                    row=0, column=i, padx=5, sticky=W
                )
            
            # Table entries
            entries = self.season_manager.get_league_table(self.league_season.id)
            
            for row, entry in enumerate(entries, 1):
                entry_frame = ttk.Frame(table_frame)
                entry_frame.pack(fill=X, padx=5, pady=1)
                
                data = [
                    str(entry.position),
                    entry.team_id.replace("team_", "").title(),
                    str(entry.played),
                    str(entry.won),
                    str(entry.drawn),
                    str(entry.lost),
                    str(entry.goals_for),
                    str(entry.goals_against),
                    f"{entry.goal_difference:+d}",
                    str(entry.points)
                ]
                
                for i, value in enumerate(data):
                    ttk.Label(entry_frame, text=value).grid(row=0, column=i, padx=5, sticky=W)
        
    def create_calendar_tab(self):
        """Create calendar tab"""
        calendar_frame = ttk.Frame(self.notebook)
        self.notebook.add(calendar_frame, text="Calendar")
        
        # Current date
        date_frame = ttk.LabelFrame(calendar_frame, text="Current Date")
        date_frame.pack(fill=X, padx=10, pady=10)
        
        current_date = self.calendar.current_date
        ttk.Label(date_frame, text=f"Game Date: {current_date.strftime('%Y-%m-%d')}").pack(
            anchor=W, padx=10, pady=5
        )
        
        # Calendar controls
        controls_frame = ttk.Frame(date_frame)
        controls_frame.pack(fill=X, padx=10, pady=5)
        
        ttk.Button(
            controls_frame, 
            text="Advance 1 Day",
            command=self.advance_day
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            controls_frame,
            text="Advance 1 Week", 
            command=self.advance_week
        ).pack(side=LEFT, padx=5)
        
        # Upcoming events
        events_frame = ttk.LabelFrame(calendar_frame, text="Upcoming Events")
        events_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Create text widget for events
        self.events_text = ttk.Text(events_frame, height=15, wrap=WORD)
        scrollbar = ttk.Scrollbar(events_frame, orient=VERTICAL, command=self.events_text.yview)
        self.events_text.configure(yscrollcommand=scrollbar.set)
        
        self.events_text.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=RIGHT, fill=Y, pady=5)
        
        self.update_events_display()
        
    def create_saves_tab(self):
        """Create saves management tab"""
        saves_frame = ttk.Frame(self.notebook)
        self.notebook.add(saves_frame, text="Saves")
        
        # Save controls
        controls_frame = ttk.LabelFrame(saves_frame, text="Save Management")
        controls_frame.pack(fill=X, padx=10, pady=10)
        
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill=X, padx=10, pady=10)
        
        ttk.Button(
            button_frame,
            text="Create Manual Save",
            command=self.create_manual_save
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Create Autosave",
            command=self.create_autosave
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Refresh List",
            command=self.update_saves_display
        ).pack(side=LEFT, padx=5)
        
        # Saves list
        saves_list_frame = ttk.LabelFrame(saves_frame, text="Available Saves")
        saves_list_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        self.saves_text = ttk.Text(saves_list_frame, height=15, wrap=WORD)
        saves_scrollbar = ttk.Scrollbar(saves_list_frame, orient=VERTICAL, command=self.saves_text.yview)
        self.saves_text.configure(yscrollcommand=saves_scrollbar.set)
        
        self.saves_text.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        saves_scrollbar.pack(side=RIGHT, fill=Y, pady=5)
        
        self.update_saves_display()
        
    def create_status_tab(self):
        """Create status information tab"""
        status_frame = ttk.Frame(self.notebook)
        self.notebook.add(status_frame, text="Status")
        
        # System status
        system_frame = ttk.LabelFrame(status_frame, text="System Status")
        system_frame.pack(fill=X, padx=10, pady=10)
        
        ttk.Label(system_frame, text="✅ Season Management: Working").pack(anchor=W, padx=10, pady=2)
        ttk.Label(system_frame, text="✅ Calendar System: Working").pack(anchor=W, padx=10, pady=2)
        ttk.Label(system_frame, text="✅ Save/Load System: Working").pack(anchor=W, padx=10, pady=2)
        ttk.Label(system_frame, text="✅ Database Models: Working").pack(anchor=W, padx=10, pady=2)
        ttk.Label(system_frame, text="⚠️ Full GUI: Partial (complex components have issues)").pack(anchor=W, padx=10, pady=2)
        
        # Statistics
        stats_frame = ttk.LabelFrame(status_frame, text="Game Statistics")
        stats_frame.pack(fill=X, padx=10, pady=10)
        
        if self.league_season:
            total_fixtures = self.session.query(Fixture).filter_by(
                competition_id=self.league_season.competition.id
            ).count()
            
            completed_fixtures = self.session.query(Fixture).filter_by(
                competition_id=self.league_season.competition.id,
                status=FixtureStatus.COMPLETED
            ).count()
            
            ttk.Label(stats_frame, text=f"Total Fixtures: {total_fixtures}").pack(anchor=W, padx=10, pady=2)
            ttk.Label(stats_frame, text=f"Completed Fixtures: {completed_fixtures}").pack(anchor=W, padx=10, pady=2)
            ttk.Label(stats_frame, text=f"Progress: {completed_fixtures/total_fixtures*100:.1f}%").pack(anchor=W, padx=10, pady=2)
        
        # Transfer window
        window_frame = ttk.LabelFrame(status_frame, text="Transfer Window")
        window_frame.pack(fill=X, padx=10, pady=10)
        
        is_open = self.calendar.is_transfer_window_open()
        status_text = "OPEN" if is_open else "CLOSED"
        ttk.Label(window_frame, text=f"Status: {status_text}").pack(anchor=W, padx=10, pady=2)
        
    def advance_day(self):
        """Advance calendar by one day"""
        self.calendar.advance_days(1)
        self.update_events_display()
        self.refresh_current_date()
        
    def advance_week(self):
        """Advance calendar by one week"""
        self.calendar.advance_days(7)
        self.update_events_display()
        self.refresh_current_date()
        
    def refresh_current_date(self):
        """Refresh the current date display"""
        # Update the calendar tab
        for child in self.notebook.nametowidget(self.notebook.tabs()[1]).winfo_children():
            if isinstance(child, ttk.LabelFrame) and child.cget("text") == "Current Date":
                for label in child.winfo_children():
                    if isinstance(label, ttk.Label) and "Game Date:" in label.cget("text"):
                        label.config(text=f"Game Date: {self.calendar.current_date.strftime('%Y-%m-%d')}")
                        break
                break
        
    def update_events_display(self):
        """Update the events display"""
        self.events_text.delete(1.0, END)
        
        # Get upcoming events
        from datetime import timedelta
        events = self.calendar.get_events_range(
            self.calendar.current_date,
            self.calendar.current_date + timedelta(days=14)
        )
        
        for event in events[:20]:  # Show first 20 events
            event_text = f"{event.date.strftime('%Y-%m-%d')}: {event.event_type.value} - {event.description}\n"
            self.events_text.insert(END, event_text)
            
    def create_manual_save(self):
        """Create a manual save"""
        try:
            save_name = f"Manual Save {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            save_game = self.save_manager.create_save(
                name=save_name,
                manager_name="Demo Manager",
                club_id="demo_club",
                current_date=self.calendar.current_date,
                play_time=7200,  # 2 hours
                metadata={"created_via": "demo_gui"}
            )
            self.update_saves_display()
            ttk.dialogs.Messagebox.show_info(
                title="Save Created",
                message=f"Save '{save_name}' created successfully!"
            )
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                title="Save Failed", 
                message=f"Failed to create save: {str(e)}"
            )
            
    def create_autosave(self):
        """Create an autosave"""
        try:
            save_game = self.save_manager.create_autosave(
                manager_name="Demo Manager",
                club_id="demo_club", 
                current_date=self.calendar.current_date,
                play_time=7200,
                metadata={"created_via": "demo_gui"}
            )
            self.update_saves_display()
            ttk.dialogs.Messagebox.show_info(
                title="Autosave Created",
                message=f"Autosave '{save_game.name}' created successfully!"
            )
        except Exception as e:
            ttk.dialogs.Messagebox.show_error(
                title="Autosave Failed",
                message=f"Failed to create autosave: {str(e)}"
            )
            
    def update_saves_display(self):
        """Update the saves display"""
        self.saves_text.delete(1.0, END)
        
        saves = self.save_manager.list_saves()
        
        if not saves:
            self.saves_text.insert(END, "No saves found.")
            return
            
        for save in saves:
            save_type_icon = "💾" if save.save_type.value == "manual" else "🔄"
            save_text = f"{save_type_icon} {save.name}\n"
            save_text += f"   Manager: {save.manager_name}\n"
            save_text += f"   Date: {save.current_date.strftime('%Y-%m-%d')}\n"
            save_text += f"   Created: {save.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            save_text += f"   Play time: {save.play_time // 60}m\n"
            save_text += f"   Size: {len(save.game_state)} bytes\n\n"
            
            self.saves_text.insert(END, save_text)
            
    def run(self):
        """Run the application"""
        self.window.mainloop()
        
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'session'):
            self.session.close()


def main():
    """Main function"""
    print("Starting OpenFoot Manager - Simple GUI Demo")
    print("This demonstrates the working core features with a simplified GUI.")
    print("=" * 60)
    
    try:
        app = SimpleOFMApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'app' in locals():
            app.cleanup()


if __name__ == "__main__":
    main()