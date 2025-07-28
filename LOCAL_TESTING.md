# Local Testing Guide for OpenFootManager

This guide explains how to use the local testing infrastructure for OpenFootManager development. The testing setup is designed to make it easy to run tests locally without relying on GitHub Actions.

## Quick Start

The fastest way to run tests locally:

```bash
# Run all tests with linting
make test-local

# Run tests in watch mode (continuous testing)
make test-watch

# Run quick tests (fail fast on first error)
make test-quick

# Run thorough tests with coverage
make test-thorough

# Interactive test runner with menu
make test-interactive
```

## Testing Scripts

### 1. Shell Script (`scripts/local_test.sh`)

The main testing script provides comprehensive testing options:

```bash
# Basic usage
./scripts/local_test.sh

# Run specific test types
./scripts/local_test.sh -t unit        # Only unit tests
./scripts/local_test.sh -t integration # Only integration tests
./scripts/local_test.sh -t all         # All tests (default)

# Additional options
./scripts/local_test.sh -c  # Generate coverage reports
./scripts/local_test.sh -v  # Verbose output
./scripts/local_test.sh -q  # Quick mode (minimal tests)
./scripts/local_test.sh -w  # Watch mode (continuous)

# Combinations
./scripts/local_test.sh -c -v -t unit  # Unit tests with coverage and verbose output
./scripts/local_test.sh -w -t unit     # Watch mode for unit tests only
```

### 2. Python Test Runner (`scripts/test_runner.py`)

Interactive menu-driven test runner with advanced features:

```bash
# Run interactive menu
python scripts/test_runner.py

# Command line options
python scripts/test_runner.py --quick       # Quick test run
python scripts/test_runner.py --all         # Run all tests
python scripts/test_runner.py --unit        # Run unit tests
python scripts/test_runner.py --integration # Run integration tests
python scripts/test_runner.py --coverage    # Run with coverage
```

Features:
- Interactive menu for test selection
- Run specific test files or methods
- Test history tracking
- Colored output for better readability
- Watch mode support
- Coverage report generation

## Testing Modes

### 1. Quick Testing
Fast feedback during development:
```bash
make test-quick
```
- Fails fast on first error
- Minimal output
- No linting or type checking
- Ideal for rapid iteration

### 2. Standard Testing
Comprehensive test run:
```bash
make test-local
```
- Runs linting (Black, Flake8, ESLint)
- Type checking (MyPy, TypeScript)
- All unit and integration tests
- Clear pass/fail status

### 3. Thorough Testing
Complete validation with metrics:
```bash
make test-thorough
```
- Everything from standard testing
- Coverage report generation
- Detailed output
- Performance metrics

### 4. Watch Mode
Continuous testing during development:
```bash
make test-watch
```
- Automatically reruns tests on file changes
- Instant feedback
- Ideal for TDD (Test-Driven Development)
- Press Ctrl+C to exit

### 5. Interactive Testing
Menu-driven test selection:
```bash
make test-interactive
```
- Choose specific test files or methods
- View test history
- Multiple testing modes
- Colored output for clarity

## Test Organization

```
tests/
├── unit/              # Unit tests (fast, isolated)
│   ├── test_*.py     # Test files must start with test_
│   └── ...
├── integration/       # Integration tests (slower, dependencies)
│   ├── test_*.py
│   └── ...
└── conftest.py       # Shared fixtures and configuration
```

## Coverage Reports

Generate and view coverage reports:

```bash
# Generate coverage report
make test-thorough

# View coverage in terminal
# (automatically shown after test run)

# View HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Tips for Fast Testing

### 1. Use Test Markers
Mark tests for selective execution:

```python
import pytest

@pytest.mark.fast
def test_quick_function():
    assert True

@pytest.mark.slow
def test_complex_integration():
    # Time-consuming test
    pass
```

Run marked tests:
```bash
pytest -m fast   # Only fast tests
pytest -m "not slow"  # Exclude slow tests
```

### 2. Focus on Changed Files
Test only what you're working on:

```bash
# Using interactive runner
make test-interactive
# Then select option 4 or 5 for specific file/method

# Or directly with pytest
pytest tests/unit/test_specific_file.py
pytest tests/unit/test_file.py::test_specific_method
```

### 3. Use Watch Mode Effectively
Keep tests running while coding:

```bash
# Watch all tests
make test-watch

# Watch specific directory
pytest-watch tests/unit/

# Watch with specific options
pytest-watch -- -x --tb=short  # Fail fast with short traceback
```

### 4. Parallel Test Execution
Run tests in parallel for speed:

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto  # Auto-detect CPU cores
pytest -n 4     # Use 4 processes
```

## Interpreting Results

### Success Indicators
- ✓ Green checkmarks for passed tests
- All linting checks pass
- Coverage meets thresholds
- No type errors

### Failure Indicators
- ✗ Red X marks for failed tests
- Linting issues highlighted
- Coverage below thresholds
- Type errors reported

### Test Summary
At the end of each run:
- Total tests run
- Passed/Failed/Skipped counts
- Execution time
- Coverage percentage (if enabled)

## Troubleshooting

### Common Issues

1. **pytest-watch not installed**
   ```bash
   pip install pytest-watch
   ```

2. **Missing test dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Permission denied for scripts**
   ```bash
   chmod +x scripts/local_test.sh
   chmod +x scripts/test_runner.py
   ```

4. **Tests can't find modules**
   ```bash
   # Install package in development mode
   pip install -e .
   ```

### Performance Tips

1. **Skip slow tests during development**
   ```bash
   pytest -m "not slow"
   ```

2. **Use coverage only when needed**
   Coverage collection slows tests down

3. **Run unit tests first**
   They're faster and catch most issues

4. **Use quick mode for rapid feedback**
   ```bash
   make test-quick
   ```

## Integration with Development Workflow

### Pre-commit Testing
```bash
# Before committing, run quick tests
make test-quick

# If all pass, run full suite
make test-local
```

### Feature Development
```bash
# Start with watch mode
make test-watch

# Write tests and code iteratively
# Tests rerun automatically

# Final validation
make test-thorough
```

### Debugging Test Failures
```bash
# Use interactive runner to isolate failing test
make test-interactive

# Run with verbose output
./scripts/local_test.sh -v -t unit

# Debug specific test
pytest -vvs tests/unit/test_file.py::test_method --pdb
```

## Best Practices

1. **Run tests frequently** - Don't wait until PR time
2. **Use watch mode** - Get instant feedback while coding
3. **Start with unit tests** - They're fast and catch most bugs
4. **Check coverage** - Ensure new code is tested
5. **Fix linting issues immediately** - Don't let them accumulate
6. **Use markers** - Organize tests by speed/type
7. **Keep tests fast** - Mock external dependencies
8. **Run full suite before pushing** - Avoid CI failures

## Advanced Usage

### Custom Test Configuration
Create a `pytest.ini` file for project-specific settings:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    slow: marks tests as slow
    fast: marks tests as fast
    unit: marks tests as unit tests
    integration: marks tests as integration tests
```

### Test Data Management
Use fixtures for test data:

```python
# conftest.py
import pytest

@pytest.fixture
def sample_data():
    return {"test": "data"}

# In your test
def test_with_data(sample_data):
    assert sample_data["test"] == "data"
```

### Continuous Integration Locally
Simulate CI environment:

```bash
# Run exactly what CI runs
./scripts/local_test.sh -c -v

# Check all quality gates
make lint
make type-check
make test-thorough
make security
```

## Conclusion

The local testing infrastructure provides multiple ways to run tests efficiently during development. Choose the approach that best fits your current task:

- **Quick feedback**: `make test-quick` or `make test-watch`
- **Comprehensive testing**: `make test-local` or `make test-thorough`
- **Specific testing**: `make test-interactive` or direct pytest commands

Remember: The goal is to catch issues early and maintain high code quality without slowing down development.
