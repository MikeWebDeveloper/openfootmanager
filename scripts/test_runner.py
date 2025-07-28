#!/usr/bin/env python3
"""
Interactive Test Runner for OpenFootManager
Provides a menu-driven interface for running tests with advanced features
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Color codes for terminal output
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


class TestRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_history_file = self.project_root / ".test_history.json"
        self.test_results_dir = self.project_root / "test_results"
        self.test_results_dir.mkdir(exist_ok=True)
        self.history = self.load_history()

    def load_history(self) -> List[Dict]:
        """Load test history from file"""
        if self.test_history_file.exists():
            try:
                with open(self.test_history_file, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_history(self):
        """Save test history to file"""
        # Keep only last 100 entries
        self.history = self.history[-100:]
        with open(self.test_history_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def add_to_history(self, test_type: str, result: bool, duration: float, details: str = ""):
        """Add test run to history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "test_type": test_type,
            "result": "passed" if result else "failed",
            "duration": duration,
            "details": details,
        }
        self.history.append(entry)
        self.save_history()

    def print_colored(self, text: str, color: str = Colors.RESET):
        """Print colored text"""
        print(f"{color}{text}{Colors.RESET}")

    def print_header(self, text: str):
        """Print a section header"""
        print()
        self.print_colored("=" * 60, Colors.BLUE)
        self.print_colored(text.center(60), Colors.BLUE)
        self.print_colored("=" * 60, Colors.BLUE)
        print()

    def get_test_files(self) -> Dict[str, List[Path]]:
        """Discover all test files"""
        test_files = {"unit": [], "integration": [], "all": []}

        # Find unit test files
        unit_dir = self.project_root / "tests" / "unit"
        if unit_dir.exists():
            test_files["unit"] = list(unit_dir.rglob("test_*.py"))

        # Find integration test files
        integration_dir = self.project_root / "tests" / "integration"
        if integration_dir.exists():
            test_files["integration"] = list(integration_dir.rglob("test_*.py"))

        # All test files
        test_files["all"] = test_files["unit"] + test_files["integration"]

        return test_files

    def get_test_methods(self, file_path: Path) -> List[str]:
        """Extract test methods from a test file"""
        methods = []
        try:
            with open(file_path, "r") as f:
                content = f.read()
                # Find all test methods
                pattern = r"def (test_\w+)\s*\("
                methods = re.findall(pattern, content)
        except:
            pass
        return methods

    def run_command(self, command: List[str], capture_output: bool = False) -> Tuple[bool, str]:
        """Run a command and return success status and output"""
        try:
            if capture_output:
                result = subprocess.run(
                    command, capture_output=True, text=True, cwd=self.project_root
                )
                return result.returncode == 0, result.stdout + result.stderr
            else:
                result = subprocess.run(command, cwd=self.project_root)
                return result.returncode == 0, ""
        except Exception as e:
            return False, str(e)

    def run_pytest(self, args: List[str], description: str = "tests") -> bool:
        """Run pytest with given arguments"""
        self.print_colored(f"Running {description}...", Colors.YELLOW)

        command = ["pytest"] + args
        start_time = time.time()

        success, output = self.run_command(command)
        duration = time.time() - start_time

        if success:
            self.print_colored(f"✓ {description} passed ({duration:.2f}s)", Colors.GREEN)
        else:
            self.print_colored(f"✗ {description} failed ({duration:.2f}s)", Colors.RED)

        self.add_to_history(description, success, duration)
        return success

    def run_specific_test_file(self):
        """Run a specific test file"""
        test_files = self.get_test_files()
        all_files = test_files["all"]

        if not all_files:
            self.print_colored("No test files found!", Colors.RED)
            return

        self.print_header("Select Test File")

        for idx, file_path in enumerate(all_files, 1):
            relative_path = file_path.relative_to(self.project_root)
            print(f"{idx}. {relative_path}")

        try:
            choice = int(input("\nEnter file number (0 to cancel): "))
            if choice == 0:
                return

            if 1 <= choice <= len(all_files):
                selected_file = all_files[choice - 1]
                self.run_pytest([str(selected_file)], f"tests in {selected_file.name}")
            else:
                self.print_colored("Invalid choice!", Colors.RED)
        except ValueError:
            self.print_colored("Invalid input!", Colors.RED)

    def run_specific_test_method(self):
        """Run a specific test method"""
        test_files = self.get_test_files()
        all_files = test_files["all"]

        if not all_files:
            self.print_colored("No test files found!", Colors.RED)
            return

        # First, select a file
        self.print_header("Select Test File")

        for idx, file_path in enumerate(all_files, 1):
            relative_path = file_path.relative_to(self.project_root)
            print(f"{idx}. {relative_path}")

        try:
            file_choice = int(input("\nEnter file number (0 to cancel): "))
            if file_choice == 0:
                return

            if 1 <= file_choice <= len(all_files):
                selected_file = all_files[file_choice - 1]
                methods = self.get_test_methods(selected_file)

                if not methods:
                    self.print_colored("No test methods found in file!", Colors.RED)
                    return

                # Then, select a method
                self.print_header("Select Test Method")

                for idx, method in enumerate(methods, 1):
                    print(f"{idx}. {method}")

                method_choice = int(input("\nEnter method number (0 to cancel): "))
                if method_choice == 0:
                    return

                if 1 <= method_choice <= len(methods):
                    selected_method = methods[method_choice - 1]
                    test_path = f"{selected_file}::{selected_method}"
                    self.run_pytest([test_path], f"method {selected_method}")
                else:
                    self.print_colored("Invalid choice!", Colors.RED)
            else:
                self.print_colored("Invalid choice!", Colors.RED)
        except ValueError:
            self.print_colored("Invalid input!", Colors.RED)

    def run_tests_with_coverage(self):
        """Run tests with coverage report"""
        self.print_header("Running Tests with Coverage")

        args = ["--cov=.", "--cov-report=html", "--cov-report=term-missing", "-v"]

        success = self.run_pytest(args, "all tests with coverage")

        if success:
            coverage_path = self.project_root / "htmlcov" / "index.html"
            if coverage_path.exists():
                self.print_colored(f"\nCoverage report: {coverage_path}", Colors.GREEN)
                self.print_colored("Open in browser to view detailed coverage", Colors.YELLOW)

    def run_watch_mode(self):
        """Run tests in watch mode"""
        self.print_header("Watch Mode")

        # Check if pytest-watch is installed
        try:
            subprocess.run(["pytest-watch", "--version"], capture_output=True, check=True)
        except:
            self.print_colored("pytest-watch not installed!", Colors.RED)
            self.print_colored("Install with: pip install pytest-watch", Colors.YELLOW)
            return

        self.print_colored("Starting watch mode... (Press Ctrl+C to stop)", Colors.YELLOW)

        try:
            subprocess.run(["pytest-watch", "-v"], cwd=self.project_root)
        except KeyboardInterrupt:
            self.print_colored("\nWatch mode stopped", Colors.YELLOW)

    def show_test_history(self):
        """Display test history"""
        self.print_header("Test History")

        if not self.history:
            self.print_colored("No test history found", Colors.YELLOW)
            return

        # Show last 10 entries
        recent_history = self.history[-10:]

        for entry in recent_history:
            timestamp = datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            result_color = Colors.GREEN if entry["result"] == "passed" else Colors.RED
            result_symbol = "✓" if entry["result"] == "passed" else "✗"

            print(f"{timestamp} - ", end="")
            self.print_colored(
                f"{result_symbol} {entry['test_type']} ({entry['duration']:.2f}s)", result_color
            )

            if entry.get("details"):
                print(f"  Details: {entry['details']}")

    def run_quick_test(self):
        """Run quick tests (fail fast)"""
        self.print_header("Quick Test Run")

        args = ["-x", "--tb=short", "-q"]
        self.run_pytest(args, "quick tests")

    def run_verbose_test(self):
        """Run tests with verbose output"""
        self.print_header("Verbose Test Run")

        args = ["-v", "-s", "--tb=long"]
        self.run_pytest(args, "verbose tests")

    def main_menu(self):
        """Display main menu and handle user choice"""
        while True:
            self.print_header("OpenFootManager Test Runner")

            menu_options = [
                "1. Run All Tests",
                "2. Run Unit Tests",
                "3. Run Integration Tests",
                "4. Run Specific Test File",
                "5. Run Specific Test Method",
                "6. Run Tests with Coverage",
                "7. Run Quick Test (fail fast)",
                "8. Run Verbose Test",
                "9. Watch Mode (continuous testing)",
                "10. Show Test History",
                "0. Exit",
            ]

            for option in menu_options:
                print(option)

            try:
                choice = input("\nEnter your choice: ").strip()

                if choice == "0":
                    self.print_colored("Goodbye!", Colors.GREEN)
                    break
                elif choice == "1":
                    self.run_pytest(["-v"], "all tests")
                elif choice == "2":
                    self.run_pytest(["tests/unit/", "-v"], "unit tests")
                elif choice == "3":
                    self.run_pytest(["tests/integration/", "-v"], "integration tests")
                elif choice == "4":
                    self.run_specific_test_file()
                elif choice == "5":
                    self.run_specific_test_method()
                elif choice == "6":
                    self.run_tests_with_coverage()
                elif choice == "7":
                    self.run_quick_test()
                elif choice == "8":
                    self.run_verbose_test()
                elif choice == "9":
                    self.run_watch_mode()
                elif choice == "10":
                    self.show_test_history()
                else:
                    self.print_colored("Invalid choice!", Colors.RED)

                if choice != "0":
                    input("\nPress Enter to continue...")

            except KeyboardInterrupt:
                self.print_colored("\n\nGoodbye!", Colors.GREEN)
                break
            except Exception as e:
                self.print_colored(f"Error: {e}", Colors.RED)
                input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Interactive Test Runner for OpenFootManager")
    parser.add_argument("--quick", action="store_true", help="Run quick test and exit")
    parser.add_argument("--all", action="store_true", help="Run all tests and exit")
    parser.add_argument("--unit", action="store_true", help="Run unit tests and exit")
    parser.add_argument("--integration", action="store_true", help="Run integration tests and exit")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage and exit")

    args = parser.parse_args()

    runner = TestRunner()

    # Handle command line arguments
    if args.quick:
        runner.run_quick_test()
    elif args.all:
        runner.run_pytest(["-v"], "all tests")
    elif args.unit:
        runner.run_pytest(["tests/unit/", "-v"], "unit tests")
    elif args.integration:
        runner.run_pytest(["tests/integration/", "-v"], "integration tests")
    elif args.coverage:
        runner.run_tests_with_coverage()
    else:
        # Run interactive menu
        runner.main_menu()


if __name__ == "__main__":
    main()
