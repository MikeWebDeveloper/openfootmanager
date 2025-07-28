#!/usr/bin/env python3
"""
OpenFoot Manager - GUI Test Runner
==================================

This script tests GUI components individually to identify and fix issues.
"""

import os
import sys
import traceback

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Test if all imports work correctly"""
    print("Testing basic imports...")

    try:
        import tkinter
        print("✓ tkinter imported")
    except ImportError as e:
        print(f"❌ tkinter import failed: {e}")
        return False

    try:
        import ttkbootstrap
        print("✓ ttkbootstrap imported")
    except ImportError as e:
        print(f"❌ ttkbootstrap import failed: {e}")
        return False

    try:
        from ofm.core.settings import Settings
        print("✓ Settings imported")
    except ImportError as e:
        print(f"❌ Settings import failed: {e}")
        return False

    try:
        from ofm.core.db.database import DB
        print("✓ DB imported")
    except ImportError as e:
        print(f"❌ DB import failed: {e}")
        return False

    try:
        from ofm.ui.gui import GUI
        print("✓ GUI imported")
    except ImportError as e:
        print(f"❌ GUI import failed: {e}")
        return False

    return True

def test_settings_initialization():
    """Test settings initialization"""
    print("\nTesting settings initialization...")

    try:
        from ofm.core.settings import Settings
        settings = Settings()
        settings.get_settings()
        print("✓ Settings initialized successfully")

        # Check if required paths exist
        print(f"  - Root dir: {settings.root_dir}")
        print(f"  - Images dir: {settings.images}")
        print(f"  - Res dir: {settings.res}")

        return True
    except Exception as e:
        print(f"❌ Settings initialization failed: {e}")
        traceback.print_exc()
        return False

def test_database_initialization():
    """Test database initialization"""
    print("\nTesting database initialization...")

    try:
        from ofm.core.settings import Settings
        from ofm.core.db.database import DB

        settings = Settings()
        settings.get_settings()

        # Test DB initialization
        DB(settings)
        print("✓ DB initialized successfully")

        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        traceback.print_exc()
        return False

def test_gui_creation():
    """Test GUI creation without mainloop"""
    print("\nTesting GUI creation...")

    try:
        from ofm.ui.gui import GUI
        gui = GUI()
        print("✓ GUI created successfully")

        # Check if window was created
        if gui.window:
            print("✓ Window object exists")
            print(f"  - Title: {gui.window.title()}")
            print(f"  - Geometry: {gui.window.geometry()}")

        # Check if pages were created
        if gui.pages:
            print(f"✓ {len(gui.pages)} pages created")
            for page_name in gui.pages.keys():
                print(f"  - {page_name}")

        # Clean up - destroy window without mainloop
        gui.window.destroy()
        print("✓ GUI cleaned up successfully")

        return True
    except Exception as e:
        print(f"❌ GUI creation failed: {e}")
        traceback.print_exc()
        return False

def test_controller_imports():
    """Test controller imports"""
    print("\nTesting controller imports...")

    try:
        from ofm.ui.controllers import OFMController
        print("✓ OFMController imported")

        from ofm.ui.controllers.home_controller import HomePageController
        print("✓ HomePageController imported")

        # Check other controllers
        controller_modules = [
            'debug_controller',
            'debug_match_controller',
            'team_selection_controller',
            'settings_controller',
            'player_profile_controller',
            'team_explorer_controller'
        ]

        for module in controller_modules:
            try:
                __import__(f'ofm.ui.controllers.{module}')
                print(f"✓ {module} imported")
            except ImportError as e:
                print(f"⚠ {module} import failed: {e}")

        return True
    except Exception as e:
        print(f"❌ Controller imports failed: {e}")
        traceback.print_exc()
        return False

def test_minimal_app():
    """Test minimal app creation without running mainloop"""
    print("\nTesting minimal app creation...")

    try:
        from ofm.core.settings import Settings
        from ofm.core.db.database import DB
        from ofm.ui.controllers import OFMController

        # Initialize components
        settings = Settings()
        settings.get_settings()
        print("✓ Settings initialized")

        db = DB(settings)
        print("✓ Database initialized")

        controller = OFMController(settings, db)
        print("✓ Controller initialized")

        # Check if GUI was created
        if controller.gui:
            print("✓ GUI created through controller")

            # Check controllers
            if controller.controllers:
                print(f"✓ {len(controller.controllers)} page controllers created")
                for name in controller.controllers.keys():
                    print(f"  - {name}")

        # Clean up
        controller.gui.window.destroy()
        print("✓ App cleaned up successfully")

        return True
    except Exception as e:
        print(f"❌ Minimal app creation failed: {e}")
        traceback.print_exc()
        return False

def test_image_resources():
    """Test if image resources exist"""
    print("\nTesting image resources...")

    try:
        from ofm.core.settings import Settings
        import os

        settings = Settings()
        settings.get_settings()

        # Check for logo image
        logo_path = os.path.join(settings.root_dir, "res", "images", "openfoot.png")
        if os.path.exists(logo_path):
            print(f"✓ Logo found: {logo_path}")
        else:
            print(f"⚠ Logo missing: {logo_path}")

            # Check alternative locations
            alt_paths = [
                os.path.join(settings.images, "openfoot.png"),
                os.path.join(os.path.dirname(settings.root_dir), "images", "openfoot.png")
            ]

            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    print(f"✓ Logo found at alternative location: {alt_path}")
                    break
            else:
                print("❌ Logo not found in any location")
                return False

        return True
    except Exception as e:
        print(f"❌ Image resource test failed: {e}")
        traceback.print_exc()
        return False

def run_gui_diagnostics():
    """Run a GUI without starting mainloop to check for issues"""
    print("\nRunning GUI diagnostics...")

    try:
        import ttkbootstrap as ttk

        # Create minimal window
        window = ttk.Window(title="OFM GUI Test", themename="darkfootball")
        print("✓ Window created with theme")

        # Test basic widgets
        frame = ttk.Frame(window)
        frame.pack(fill="both", expand=True)
        print("✓ Frame created")

        label = ttk.Label(frame, text="GUI Test")
        label.pack(pady=20)
        print("✓ Label created")

        button = ttk.Button(frame, text="Test Button")
        button.pack(pady=10)
        print("✓ Button created")

        # Update window once to ensure everything renders
        window.update()
        print("✓ Window updated successfully")

        # Clean up
        window.destroy()
        print("✓ Test window cleaned up")

        return True
    except Exception as e:
        print(f"❌ GUI diagnostics failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print(" OPENFOOT MANAGER - GUI TEST RUNNER")
    print("=" * 60)

    tests = [
        ("Basic Imports", test_basic_imports),
        ("Settings Initialization", test_settings_initialization),
        ("Database Initialization", test_database_initialization),
        ("Image Resources", test_image_resources),
        ("GUI Diagnostics", run_gui_diagnostics),
        ("GUI Creation", test_gui_creation),
        ("Controller Imports", test_controller_imports),
        ("Minimal App", test_minimal_app),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n{'=' * 60}")
        print(f" {test_name}")
        print(f"{'=' * 60}")

        try:
            if test_func():
                print(f"\n✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"\n❌ {test_name} FAILED")
                failed += 1
        except Exception as e:
            print(f"\n❌ {test_name} FAILED with exception: {e}")
            failed += 1

    print(f"\n{'=' * 60}")
    print(" TEST SUMMARY")
    print(f"{'=' * 60}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")

    if failed == 0:
        print("\n🎉 All tests passed! GUI should work correctly.")
        print("\nYou can now try: python3 run.py")
    else:
        print(f"\n⚠ {failed} test(s) failed. Fix these issues before running the GUI.")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
