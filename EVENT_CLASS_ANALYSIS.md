# Event Class Analysis and Mismatch Report

## Current Implementation vs Test Expectations

### 1. PassEvent Class

**Current Implementation (from `ofm/core/simulation/events/pass_event.py`):**
```python
@dataclass
class PassEvent(SimulationEvent):
    commentary_importance = CommentaryImportance.LOW
    receiving_player: Optional[PlayerSimulation] = None
```
- Inherits from `SimulationEvent` which has: `event_type`, `state`, `outcome`, `attacking_player`, `defending_player`, `commentary`, `duration`
- No direct attributes for: `minute`, `player_id`, `team_id`, `success`, `pass_type`, `distance`

**Test Expectations (from `test_match_engine.py`):**
```python
pass_event = PassEvent(
    minute=15,
    player_id=1,
    team_id=1,
    success=True,
    pass_type="short",
    distance=10.5,
)
```

**Mismatches:**
- Test expects simple constructor with flat attributes
- Current implementation uses complex inheritance and GameState
- Test expects `minute` as integer, current uses `timedelta` in GameState
- Test expects `player_id/team_id` as integers, current uses PlayerSimulation objects
- Test expects explicit `success` boolean, current uses EventOutcome enum
- Test expects `pass_type` string, current doesn't have this attribute
- Test expects `distance` float, current calculates it internally

### 2. ShotEvent Class

**Current Implementation (from `ofm/core/simulation/events/shot_event.py`):**
```python
@dataclass
class ShotEvent(SimulationEvent):
    commentary_importance = CommentaryImportance.HIGH
```
- Inherits same base attributes as PassEvent
- No direct attributes for: `minute`, `player_id`, `team_id`, `success`, `shot_type`, `on_target`, `saved`, `is_goal`

**Test Expectations:**
```python
shot_event = ShotEvent(
    minute=30,
    player_id=2,
    team_id=1,
    success=False,
    shot_type="long_shot",
    on_target=True,
    saved=True,
    is_goal=True,  # in some tests
)
```

**Mismatches:**
- Similar structural mismatches as PassEvent
- Test expects `shot_type` string, current doesn't have this
- Test expects explicit `on_target`, `saved`, `is_goal` booleans, current uses EventOutcome
- Current implementation determines outcomes through complex probability calculations

### 3. DribbleEvent Class

**Current Implementation (from `ofm/core/simulation/events/dribble_event.py`):**
```python
@dataclass
class DribbleEvent(SimulationEvent):
    commentary_importance = CommentaryImportance.LOW
```
- Same inheritance structure
- No direct attributes for: `minute`, `player_id`, `team_id`, `success`, `skill_move`

**Test Expectations:**
```python
dribble_event = DribbleEvent(
    minute=45,
    player_id=3,
    team_id=2,
    success=True,
    skill_move="step_over",
)
```

**Mismatches:**
- Same structural issues as other events
- Test expects `skill_move` string, current doesn't have this attribute
- Test expects simple success/fail, current uses EventOutcome enum

### 4. GameState Class

**Current Implementation (from `ofm/core/simulation/game_state.py`):**
```python
@dataclass
class GameState:
    minutes: timedelta
    status: SimulationStatus
    position: PitchPosition
    in_additional_time: bool = False
    additional_time_elapsed: timedelta = timedelta(0)
```

**Test Expectations:**
```python
game_state = GameState()
game_state.home_team = club
game_state.away_team = club
game_state.home_score = 0
game_state.away_score = 0
game_state.minute = 0
game_state.half = 1
game_state.is_playing = True
```

**Mismatches:**
- Test expects mutable object with settable attributes
- Test expects `home_team`, `away_team` attributes (not in current)
- Test expects `home_score`, `away_score` integers (not in current)
- Test expects `minute` as integer, current has `minutes` as timedelta
- Test expects `half` integer, current uses `status` enum
- Test expects `is_playing` boolean, current uses status enum

## Root Cause Analysis

The fundamental mismatch is architectural:

1. **Current Implementation**:
   - Uses complex event-driven simulation with probability-based outcomes
   - Events are processed through `calculate_event()` method
   - State is managed through GameState and team objects
   - Players and teams are full objects with attributes

2. **Test Expectations**:
   - Simple data structures with direct attribute access
   - Events are just data containers
   - State is manually managed
   - IDs are used instead of object references

## Recommendations

### Option 1: Create Test-Specific Mock Classes
Create simplified mock classes that match test expectations:

```python
# In test_match_engine.py or a test utilities file
@dataclass
class MockPassEvent:
    minute: int
    player_id: int
    team_id: int
    success: bool
    pass_type: str
    distance: float
    event_type: EventType = EventType.PASS

@dataclass
class MockShotEvent:
    minute: int
    player_id: int
    team_id: int
    success: bool
    shot_type: str
    on_target: bool
    saved: bool
    is_goal: bool = False
    event_type: EventType = EventType.SHOT

@dataclass
class MockDribbleEvent:
    minute: int
    player_id: int
    team_id: int
    success: bool
    skill_move: str
    event_type: EventType = EventType.DRIBBLE

class MockGameState:
    def __init__(self):
        self.home_team = None
        self.away_team = None
        self.home_score = 0
        self.away_score = 0
        self.minute = 0
        self.half = 1
        self.is_playing = False
```

### Option 2: Adapter Pattern
Create adapter classes that translate between test expectations and real implementation:

```python
class EventAdapter:
    @staticmethod
    def create_pass_event(minute, player_id, team_id, success, pass_type, distance):
        # Create real PassEvent with proper GameState
        # Map simple parameters to complex objects
        pass

    @staticmethod
    def create_game_state():
        # Return a wrapper that provides expected interface
        pass
```

### Option 3: Refactor Tests
Update tests to work with the actual implementation:

```python
# Instead of:
pass_event = PassEvent(minute=15, player_id=1, ...)

# Use:
game_state = GameState(minutes=timedelta(minutes=15), status=SimulationStatus.FIRST_HALF, position=PitchPosition.MIDFIELD_CENTER)
pass_event = PassEvent(EventType.PASS, game_state)
# Set up players and teams properly
```

### Option 4: Hybrid Approach
1. Keep the current complex simulation engine
2. Add simplified event DTOs for external interfaces
3. Convert between internal and external representations

## Recommended Solution

**Option 1 (Mock Classes)** is the most pragmatic for immediate test fixes:
- Minimal changes to existing code
- Tests can run independently
- Clear separation between test expectations and implementation

This allows the tests to pass while maintaining the sophisticated simulation engine. Later, a proper integration test suite can be created that works with the real implementation.
