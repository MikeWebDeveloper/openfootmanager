# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OpenFoot Manager is a free and open source football/soccer manager simulation game written in Python. It's inspired by Football Manager and built upon the source code of Bygfoot. The project uses a Tkinter-based GUI with ttkbootstrap for theming.

## Development Commands

### Using Poetry (Recommended)
```bash
# Install dependencies
poetry install

# Install without dev dependencies
poetry install --without dev

# Run the game
poetry run python run.py

# Run tests
poetry run pytest

# Run a single test
poetry run pytest path/to/test_file.py::test_function_name

# Install pre-commit hooks
poetry run pre-commit install

# Run linting manually
poetry run black .
poetry run isort . --profile black
poetry run flake8
```

### Using Pipenv
```bash
# Install dependencies
pipenv install --dev

# Run the game
pipenv run python run.py

# Run tests
pipenv run pytest

# Install pre-commit hooks
pipenv run python -m pre-commit install
```

## Architecture Overview

### Core Structure
The application follows an MVC pattern with clear separation of concerns:

1. **Entry Point**: `run.py` → `OFM` class → `OFMController`
2. **Core Components**:
   - `ofm/core/db/`: Database layer with generators for creating game data
   - `ofm/core/football/`: Domain models (Player, Club, Manager, Formation, etc.)
   - `ofm/core/simulation/`: Match simulation engine with event system
   - `ofm/ui/`: GUI layer using ttkbootstrap

### Key Architectural Patterns

1. **Simulation Engine**: Event-driven architecture in `ofm/core/simulation/`
   - `LiveGame` class orchestrates matches
   - Events (pass, shot, foul, etc.) in `events/` directory
   - `GameState` tracks match progress
   - `TeamSimulation` handles team-specific logic

2. **UI Architecture**: Controller-based navigation in `ofm/ui/`
   - Controllers in `controllers/` manage page transitions
   - Pages in `pages/` define UI layouts
   - Custom themes defined in `gui.py`

3. **Data Generation**: Procedural generation in `ofm/core/db/generators.py`
   - Creates realistic player names, attributes, and teams
   - Uses JSON resources in `ofm/res/` for names and configurations

### Important Design Decisions

1. **No External Game Database**: Uses procedurally generated fictitious players
2. **Event-Based Match Simulation**: Each match action is an event object
3. **Settings Management**: Centralized in `Settings` class
4. **Resource Files**: JSON data in `ofm/res/` for names, clubs, and countries

## Testing Approach

Tests are organized by module in `ofm/tests/`:
- Unit tests for individual components
- Integration tests for simulation engine
- Uses pytest with fixtures defined in `conftest.py`

## Code Standards

- Python 3.10+ required
- Black for formatting
- isort for import sorting
- flake8 for linting
- Pre-commit hooks enforce standards
- Follow existing patterns in neighboring files

## Development Status & Roadmap

### Current Status
The project is in active development, transitioning from a debug-ready state to a fully playable game. Core systems like match simulation and player models are implemented, but gameplay features are still being built.

### Development Roadmap
See [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) for the complete development plan, including:
- **Phase 1**: Core Gameplay Loop (Season Structure, Save/Load, Transfers, Finances, AI)
- **Phase 2**: Management Features (Training, Tactics, Youth Academy, Contracts)
- **Phase 3**: Polish & Content (Leagues, Press, Achievements)
- **Phase 4**: Advanced Features (3D Visualization, Mods, Multiplayer)

### Quick Links
- [Current Phase Progress](DEVELOPMENT_ROADMAP.md#progress-tracking)
- [Technical Architecture](DEVELOPMENT_ROADMAP.md#technical-architecture)
- [Testing Strategy](DEVELOPMENT_ROADMAP.md#testing-strategy)
- [Agent Orchestration](DEVELOPMENT_ROADMAP.md#agent-orchestration-plan)

### Key Development Decisions
1. **Database Migration**: Moving from JSON to SQLAlchemy for persistence
2. **AI Architecture**: Decision tree-based AI for tactical and transfer decisions
3. **Save System**: Versioned saves with migration support for compatibility
4. **Transfer Market**: Dynamic valuation based on multiple factors
5. **Season Structure**: Event-driven calendar system with fixture generation

### Completed Implementation Steps
1. ✅ Set up SQLAlchemy database schema
2. ✅ Implement basic season/league structure  
3. ✅ Create fixture generation algorithm
4. ✅ Build save/load system foundation

### Next Implementation Steps
1. Develop transfer negotiation mechanics
2. Implement financial system
3. Create AI manager system
4. Build training and tactics systems

### Development Guidelines
- Always write tests for new features
- Use type hints for better code clarity
- Document complex algorithms and game mechanics
- Keep performance in mind (target: simulate season in <30 seconds)
- Maintain backwards compatibility for save files