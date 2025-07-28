#!/bin/bash

# Local Testing Script for OpenFootManager
# Provides comprehensive testing options for local development

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="all"
COVERAGE=false
VERBOSE=false
QUICK=false
WATCH=false

# Function to print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to print section headers
print_header() {
    echo
    print_color "$BLUE" "========================================="
    print_color "$BLUE" "$1"
    print_color "$BLUE" "========================================="
    echo
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Help function
show_help() {
    cat << EOF
Usage: ./scripts/local_test.sh [OPTIONS]

OPTIONS:
    -t, --type TYPE     Type of tests to run (unit|integration|all) [default: all]
    -c, --coverage      Generate coverage reports
    -v, --verbose       Verbose output
    -q, --quick         Quick mode (minimal tests)
    -w, --watch         Watch mode (continuous testing)
    -h, --help          Show this help message

EXAMPLES:
    ./scripts/local_test.sh                     # Run all tests
    ./scripts/local_test.sh -t unit            # Run only unit tests
    ./scripts/local_test.sh -c                 # Run with coverage
    ./scripts/local_test.sh -q                 # Quick test run
    ./scripts/local_test.sh -w -t unit         # Watch mode for unit tests

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -q|--quick)
            QUICK=true
            shift
            ;;
        -w|--watch)
            WATCH=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_color "$RED" "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate test type
if [[ ! "$TEST_TYPE" =~ ^(unit|integration|all)$ ]]; then
    print_color "$RED" "Invalid test type: $TEST_TYPE"
    show_help
    exit 1
fi

# Check required tools
print_header "Checking Environment"

if ! command_exists python3; then
    print_color "$RED" "Error: Python 3 is not installed"
    exit 1
fi

if ! command_exists npm; then
    print_color "$RED" "Error: npm is not installed"
    exit 1
fi

print_color "$GREEN" "✓ Environment checks passed"

# Function to run Python linting
run_python_lint() {
    print_header "Running Python Linting (Black & Flake8)"

    if command_exists black; then
        print_color "$YELLOW" "Running Black..."
        if black --check .; then
            print_color "$GREEN" "✓ Black formatting check passed"
        else
            print_color "$RED" "✗ Black formatting issues found"
            if [[ "$QUICK" != true ]]; then
                print_color "$YELLOW" "Run 'black .' to fix formatting"
            fi
            return 1
        fi
    else
        print_color "$YELLOW" "⚠ Black not installed, skipping"
    fi

    if command_exists flake8; then
        print_color "$YELLOW" "Running Flake8..."
        if flake8 .; then
            print_color "$GREEN" "✓ Flake8 check passed"
        else
            print_color "$RED" "✗ Flake8 issues found"
            return 1
        fi
    else
        print_color "$YELLOW" "⚠ Flake8 not installed, skipping"
    fi

    return 0
}

# Function to run TypeScript/JavaScript linting
run_js_lint() {
    print_header "Running TypeScript/JavaScript Linting"

    if [[ -f "package.json" ]]; then
        if npm run lint 2>/dev/null; then
            print_color "$GREEN" "✓ ESLint check passed"
        else
            print_color "$YELLOW" "⚠ No lint script found or linting failed"
        fi
    else
        print_color "$YELLOW" "⚠ No package.json found, skipping JS linting"
    fi
}

# Function to run type checking
run_type_check() {
    print_header "Running Type Checking"

    # Python type checking
    if command_exists mypy; then
        print_color "$YELLOW" "Running MyPy..."
        if mypy . 2>/dev/null; then
            print_color "$GREEN" "✓ MyPy type check passed"
        else
            print_color "$YELLOW" "⚠ MyPy issues found or not configured"
        fi
    else
        print_color "$YELLOW" "⚠ MyPy not installed, skipping Python type checking"
    fi

    # TypeScript type checking
    if [[ -f "tsconfig.json" ]]; then
        print_color "$YELLOW" "Running TypeScript compiler..."
        if npx tsc --noEmit; then
            print_color "$GREEN" "✓ TypeScript type check passed"
        else
            print_color "$RED" "✗ TypeScript type errors found"
            return 1
        fi
    fi
}

# Function to run unit tests
run_unit_tests() {
    print_header "Running Unit Tests"

    local pytest_args="-v"

    if [[ "$COVERAGE" == true ]]; then
        pytest_args="$pytest_args --cov=. --cov-report=html --cov-report=term"
    fi

    if [[ "$VERBOSE" == true ]]; then
        pytest_args="$pytest_args -s"
    fi

    if [[ "$QUICK" == true ]]; then
        pytest_args="$pytest_args -x --tb=short"
    fi

    if command_exists pytest; then
        if pytest $pytest_args ofm/tests/; then
            print_color "$GREEN" "✓ Unit tests passed"
        else
            print_color "$RED" "✗ Unit tests failed"
            return 1
        fi
    else
        print_color "$YELLOW" "⚠ pytest not installed, skipping unit tests"
    fi
}

# Function to run integration tests
run_integration_tests() {
    print_header "Running Integration Tests"

    local pytest_args="-v"

    if [[ "$COVERAGE" == true ]]; then
        pytest_args="$pytest_args --cov=. --cov-report=html --cov-report=term"
    fi

    if [[ "$VERBOSE" == true ]]; then
        pytest_args="$pytest_args -s"
    fi

    if command_exists pytest; then
        if pytest $pytest_args -m integration ofm/tests/; then
            print_color "$GREEN" "✓ Integration tests passed"
        else
            print_color "$RED" "✗ Integration tests failed"
            return 1
        fi
    else
        print_color "$YELLOW" "⚠ pytest not installed, skipping integration tests"
    fi
}

# Function to generate coverage report
generate_coverage_report() {
    if [[ "$COVERAGE" == true ]]; then
        print_header "Coverage Report"

        if [[ -d "htmlcov" ]]; then
            print_color "$GREEN" "Coverage report generated in htmlcov/"
            print_color "$YELLOW" "Open htmlcov/index.html in your browser to view the report"
        fi
    fi
}

# Function to run all tests
run_all_tests() {
    local failed=false

    # Linting
    if [[ "$QUICK" != true ]]; then
        run_python_lint || failed=true
        run_js_lint || failed=true
        run_type_check || failed=true
    fi

    # Tests
    case "$TEST_TYPE" in
        unit)
            run_unit_tests || failed=true
            ;;
        integration)
            run_integration_tests || failed=true
            ;;
        all)
            run_unit_tests || failed=true
            run_integration_tests || failed=true
            ;;
    esac

    # Coverage report
    generate_coverage_report

    # Final status
    print_header "Test Summary"

    if [[ "$failed" == true ]]; then
        print_color "$RED" "✗ TESTS FAILED"
        return 1
    else
        print_color "$GREEN" "✓ ALL TESTS PASSED"
        return 0
    fi
}

# Function to run tests in watch mode
run_watch_mode() {
    print_header "Watch Mode Activated"
    print_color "$YELLOW" "Press Ctrl+C to exit watch mode"
    echo

    if command_exists pytest-watch; then
        local watch_args=""

        if [[ "$VERBOSE" == true ]]; then
            watch_args="$watch_args -- -v -s"
        fi

        case "$TEST_TYPE" in
            unit)
                pytest-watch ofm/tests/ $watch_args
                ;;
            integration)
                pytest-watch -m integration ofm/tests/ $watch_args
                ;;
            all)
                pytest-watch $watch_args
                ;;
        esac
    else
        print_color "$RED" "Error: pytest-watch not installed"
        print_color "$YELLOW" "Install with: pip install pytest-watch"
        exit 1
    fi
}

# Main execution
main() {
    print_color "$BLUE" "OpenFootManager Local Testing"
    print_color "$BLUE" "============================="
    echo

    if [[ "$WATCH" == true ]]; then
        run_watch_mode
    else
        if run_all_tests; then
            exit 0
        else
            exit 1
        fi
    fi
}

# Run main function
main
