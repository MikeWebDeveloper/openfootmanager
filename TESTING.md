# OpenFootManager Testing Guide

## Overview

This guide explains the comprehensive testing strategy implemented for OpenFootManager, including pre-commit hooks, test organization, and CI/CD integration.

## Quick Start

```bash
# Install development dependencies
make install

# Set up pre-commit hooks
make setup-dev

# Run all tests
make test

# Run fast tests only (pre-commit)
make test-fast

# Run specific test categories
make test-unit
make test-integration
make test-critical
```

## Pre-commit Hooks

Pre-commit hooks run automatically before each commit to ensure code quality. They include:

1. **Code Formatting** (black, isort)
2. **Linting** (flake8)
3. **Fast Tests** (pytest -m fast)
4. **Type Checking** (mypy)
5. **Security Checks** (bandit)

To run pre-commit hooks manually:
```bash
pre-commit run --all-files
```

## Test Categories

Tests are organized with pytest markers:

- `@pytest.mark.fast` - Tests that complete in under 1 second (run on pre-commit)
- `@pytest.mark.slow` - Tests that take more than 1 second
- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests for multiple components
- `@pytest.mark.critical` - Critical functionality that must always pass
- `@pytest.mark.db` - Database-related tests
- `@pytest.mark.simulation` - Game simulation tests
- `@pytest.mark.save` - Save/load functionality tests
- `@pytest.mark.performance` - Performance benchmark tests

## Test Structure

```
ofm/tests/
├── conftest.py              # Shared fixtures and configuration
├── utils.py                 # Test utilities and helpers
├── test_*.py               # Test files for different modules
├── test_transfer_system.py  # Transfer system tests
├── test_match_engine.py    # Match engine tests
└── ...
```

## Writing Tests

### Example Unit Test

```python
@pytest.mark.fast
@pytest.mark.unit
def test_player_creation(test_db_session):
    """Test creating a new player."""
    player = TestDataFactory.create_test_player(
        test_db_session,
        name="Test Player",
        overall=75
    )

    assert player.id is not None
    assert player.name == "Test Player"
    assert player.overall == 75
```

### Example Integration Test

```python
@pytest.mark.integration
@pytest.mark.slow
def test_full_match_simulation(test_db_session):
    """Test complete match simulation."""
    home_team, home_players = TestDataFactory.create_test_team(test_db_session)
    away_team, away_players = TestDataFactory.create_test_team(test_db_session)

    # Run match simulation
    result = simulate_match(home_team, away_team)

    assert result.home_score >= 0
    assert result.away_score >= 0
```

### Performance Testing

```python
@pytest.mark.performance
def test_bulk_operations(test_db_session):
    """Test performance of bulk operations."""
    with PerformanceTimer("Bulk insert", max_duration=2.0):
        # Perform bulk operations
        players = [create_player(i) for i in range(1000)]
        test_db_session.add_all(players)
        test_db_session.commit()
```

## Coverage Requirements

- Minimum coverage: 70%
- Critical paths: 90%+ coverage
- New features must include tests

View coverage report:
```bash
make coverage
# Open htmlcov/index.html in browser
```

## CI/CD Pipeline

The GitHub Actions workflow includes:

1. **Fast Tests** - Run on every push/PR
2. **Full Test Suite** - Matrix testing (Python 3.10, 3.11, 3.12)
3. **Security Scanning** - Bandit, Safety, Semgrep
4. **Performance Benchmarks** - On pull requests
5. **Coverage Reporting** - Upload to Codecov

## Development Workflow

1. Write code following TDD principles
2. Add appropriate test markers
3. Run tests locally: `make test-fast`
4. Commit (pre-commit hooks run automatically)
5. Push to GitHub (CI/CD runs full suite)

## Test Data Management

Use the `TestDataFactory` for consistent test data:

```python
# Create test league
league = TestDataFactory.create_test_league(session)

# Create test club with players
club, players = TestDataFactory.create_test_team(session)

# Create individual player
player = TestDataFactory.create_test_player(
    session,
    position=Position.FC,
    overall=85
)
```

## Debugging Tests

```bash
# Run tests with verbose output
pytest -vv

# Run specific test file
pytest ofm/tests/test_transfer_system.py

# Run specific test
pytest ofm/tests/test_transfer_system.py::TestTransferSystem::test_create_transfer_offer

# Debug with pdb
pytest --pdb

# Show local variables on failure
pytest -l
```

## Security Testing

Security tests are run automatically in CI/CD:

- **Bandit** - Identifies common security issues
- **Safety** - Checks dependencies for vulnerabilities
- **Semgrep** - Static analysis for security patterns

Run security checks locally:
```bash
make security
```

## Best Practices

1. **Fast Tests First**: Mark unit tests as `@pytest.mark.fast`
2. **Isolated Tests**: Each test should be independent
3. **Clear Names**: Test names should describe what they test
4. **Use Fixtures**: Leverage pytest fixtures for setup
5. **Assert Messages**: Include helpful messages in assertions
6. **Mock External Dependencies**: Don't make real API calls
7. **Test Edge Cases**: Include boundary conditions
8. **Performance Awareness**: Monitor test execution time

## Troubleshooting

### Pre-commit hooks are slow
- Ensure only fast tests are marked with `@pytest.mark.fast`
- Check if black/isort are processing too many files

### Tests fail in CI but pass locally
- Check Python version differences
- Verify all dependencies are in requirements.txt
- Look for hardcoded paths or OS-specific code

### Coverage is below threshold
- Run `make coverage` to identify uncovered lines
- Add tests for critical paths first
- Use `# pragma: no cover` sparingly for untestable code

## Contributing

When adding new features:

1. Write tests first (TDD)
2. Ensure all tests pass
3. Add appropriate markers
4. Update this documentation if needed
5. Check coverage remains above threshold

For questions or issues, please open a GitHub issue.
