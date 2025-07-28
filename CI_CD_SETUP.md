# CI/CD Setup Documentation

## Overview

This project uses GitHub Actions for continuous integration and deployment with comprehensive quality gates, automated testing, and security scanning.

## Workflow Features

### 🔄 Multi-Environment Testing
- **Python Versions**: 3.10, 3.11, 3.12
- **Operating System**: Ubuntu Latest
- **Dependency Caching**: Pip cache for faster builds

### 🧪 Quality Gates

#### Code Formatting & Style
- **Black**: Code formatting enforcement
- **isort**: Import sorting validation
- **flake8**: Comprehensive linting with custom configuration

#### Testing & Coverage
- **pytest**: Full test suite execution
- **Coverage**: Code coverage reporting with codecov integration
- **Hypothesis**: Property-based testing support

#### Security Scanning
- **Safety**: Dependency vulnerability scanning
- **Bandit**: Static security analysis for Python code

### 🚀 Build Pipeline
- **Package Building**: Automated package creation
- **Package Validation**: Twine package checking
- **Artifact Generation**: Build artifacts for releases

## Local Development Setup

### Quick Start
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run the complete CI verification locally
python3 test_ci_workflow.py
```

### Individual Commands

#### Install Dependencies
```bash
pip install -r requirements.txt          # Production dependencies
pip install -r requirements-dev.txt      # Development dependencies
```

#### Code Quality Checks
```bash
# Format code
black ofm/
isort ofm/

# Check formatting (CI mode)
black --check --diff ofm/
isort --check-only --diff ofm/

# Linting
flake8 ofm/ --config .flake8
```

#### Testing
```bash
# Run all tests
pytest ofm/tests/ -v

# Run with coverage
pytest ofm/tests/ -v --cov=ofm --cov-report=xml --cov-report=term-missing
```

#### Security Scanning
```bash
# Check dependencies for vulnerabilities
safety check

# Static security analysis
bandit -r ofm/
```

## Dependency Management

### Production Dependencies (`requirements.txt`)
- **ttkbootstrap**: GUI framework
- **pyyaml**: YAML configuration handling
- **sqlalchemy**: Database ORM

### Development Dependencies (`requirements-dev.txt`)
- **Testing**: pytest, pytest-cov, hypothesis
- **Code Quality**: black, isort, flake8, mypy
- **Security**: safety, bandit
- **Documentation**: sphinx, pygments, docutils
- **Build Tools**: build, twine
- **Pre-commit**: pre-commit hooks

## GitHub Actions Workflow

### Triggers
- **Push**: to `master`, `main`, `develop` branches
- **Pull Request**: to `master`, `main`, `develop` branches

### Jobs

#### 1. Test Job (`test`)
- **Matrix Strategy**: Python 3.10, 3.11, 3.12
- **Steps**:
  1. Checkout code
  2. Setup Python environment
  3. Cache dependencies
  4. Install dependencies
  5. Verify installations
  6. Code formatting check
  7. Import sorting check
  8. Linting (critical errors)
  9. Linting (full configuration)
  10. Type checking (if configured)
  11. Test execution with coverage
  12. Coverage upload

#### 2. Security Job (`security`)
- **Python Version**: 3.11
- **Steps**:
  1. Checkout code
  2. Setup Python environment
  3. Install dependencies
  4. Safety vulnerability check
  5. Bandit security analysis

#### 3. Build Job (`build`)
- **Trigger**: Only on `master`/`main` branch
- **Dependencies**: Requires `test` job success
- **Steps**:
  1. Checkout code
  2. Setup Python environment
  3. Install build tools
  4. Build package
  5. Validate package

## Configuration Files

### `.flake8`
```ini
[flake8]
ignore = E203, E266, E501, W503, F403, F401, F405, C901
max-line-length = 89
max-complexity = 18
select = B,C,E,F,W,T4,B9
```

### `pyproject.toml`
- Poetry configuration
- pytest configuration
- Build system configuration

## Troubleshooting

### Common Issues

#### 1. Import Errors
- **Problem**: `F821 undefined name` errors
- **Solution**: Add proper `TYPE_CHECKING` imports for forward references

#### 2. Formatting Issues
- **Problem**: Black or isort failures
- **Solution**: Run `black ofm/` and `isort ofm/` locally

#### 3. Test Failures
- **Problem**: Tests fail in CI but pass locally
- **Solution**: Check database setup and fixtures

#### 4. Dependency Issues
- **Problem**: Package installation failures
- **Solution**: Update version constraints in requirements files

### Local CI Verification

Use the provided `test_ci_workflow.py` script to verify your changes locally before pushing:

```bash
python3 test_ci_workflow.py
```

This script replicates the CI environment checks:
- ✅ Dependency installation
- ✅ Import verification
- ✅ Code formatting
- ✅ Import sorting
- ✅ Linting
- ✅ Test execution

## Phase 1.1 & 1.2 Features

The CI/CD pipeline properly handles our new Phase 1.1 and 1.2 features:

### Phase 1.1: League System & Season Management
- **Database Models**: Competition, League, LeagueSeason, Fixture, LeagueTableEntry
- **Season Management**: FixtureGenerator, SeasonManager
- **Promotion/Relegation**: PromotionRelegationManager

### Phase 1.2: Game Calendar & Save System
- **Calendar System**: GameCalendar, CalendarEvent
- **Save System**: SaveManager, SaveSerializer
- **Game State**: Comprehensive serialization and restoration

All features are:
- ✅ Properly tested with comprehensive test coverage
- ✅ Formatted according to project standards
- ✅ Linted for code quality
- ✅ Security scanned
- ✅ Type-safe with proper imports

## Best Practices

1. **Always run local verification** before pushing
2. **Fix formatting issues** locally with black and isort
3. **Add tests** for new features
4. **Update dependencies** carefully and test thoroughly
5. **Monitor security reports** and address vulnerabilities promptly
6. **Keep documentation updated** as features evolve

## Next Steps

- [ ] Add mypy configuration for strict type checking
- [ ] Add integration tests for full workflow scenarios
- [ ] Add performance benchmarking
- [ ] Add automatic dependency updates with Dependabot
- [ ] Add deployment pipeline for releases