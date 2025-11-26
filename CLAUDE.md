# Version Control & Development Workflow

This document describes the version control structure, branching strategy, and development workflow for this project.

---

## Version Control Structure

### Branching Strategy

This project follows a **feature branch workflow** with semantic versioning:

```
main
├── feature/simple-network (v0.2.0)
├── feature/agent-model (v0.3.0)
└── feature/traffic-behavior (v0.4.0)
```

#### Main Branch
- **Branch**: `main`
- **Purpose**: Stable, production-ready code
- **Protection**: Only updated via pull requests from feature branches
- **Current Version**: v0.1.0 (after cleanup)

#### Feature Branches
- **Naming Convention**: `feature/<descriptive-name>`
- **Purpose**: Develop new features or significant changes
- **Lifecycle**: Created → Developed → Tested → PR → Merged → Deleted
- **Examples**:
  - `feature/simple-network` - Network implementation (v0.2.0)
  - `feature/agent-model` - Agent implementation (v0.3.0)
  - `feature/traffic-behavior` - Traffic behavior with congestion (v0.4.0)

---

## Semantic Versioning

This project follows [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH
  |     |     |
  |     |     └─ Bug fixes, minor improvements
  |     └─────── New features (backward compatible)
  └───────────── Breaking changes
```

### Version History

| Version | Date | Description | Branch |
|---------|------|-------------|--------|
| 0.4.0 | 2024-11-26 | Traffic behavior with congestion & crossroads | `feature/traffic-behavior` |
| 0.3.0 | 2024-11-26 | Agent model for network-based ABM | `feature/agent-model` |
| 0.2.0 | 2024-11-26 | Simple network module | `feature/simple-network` |
| 0.1.0 | 2024-11-25 | Diffusion model implementation | `main` |
| 0.0.1 | 2024-11-19 | Initial project setup | `main` |

### When to Bump Versions

**PATCH (0.0.x)**:
- Bug fixes
- Documentation updates
- Minor refactoring
- Performance improvements

**MINOR (0.x.0)**:
- New features
- New models or components
- Backward-compatible API additions
- Significant enhancements

**MAJOR (x.0.0)**:
- Breaking API changes
- Major architectural changes
- Removal of deprecated features
- Complete rewrites

---

## Development Workflow

### 1. Starting a New Feature

```bash
# Ensure you're on main and up to date
git checkout main
git pull origin main

# Create a new feature branch
git checkout -b feature/<feature-name>
```

### 2. Development Process

1. **Implement the feature**
   - Write code in appropriate modules
   - Follow existing code structure

2. **Update version tracking**
   - Update `CHANGELOG.md`:
     ```markdown
     ## [X.Y.Z] - YYYY-MM-DD

     ### Added
     - New feature description

     ### Changed
     - Modified features

     ### Fixed
     - Bug fixes
     ```

   - Update `src/__init__.py`:
     ```python
     __version__ = "X.Y.Z"

     __changelog__ = {
         "X.Y.Z": "Brief description",
         # ... previous versions
     }
     ```

3. **Write tests**
   - Create test file in `tests/unit/`
   - Aim for comprehensive coverage
   - Run tests: `python -m pytest tests/unit/test_<module>.py -v`

4. **Create examples**
   - Add demo script in `examples/`
   - Show practical usage

### 3. Committing Changes

```bash
# Stage all changes
git add -A

# Commit with descriptive message
git commit -m "Add <feature> (<version>)

<Detailed description>

Features:
- Feature 1
- Feature 2

Infrastructure:
- Version updates
- Test additions

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 4. Pushing and Creating PR

```bash
# Push feature branch
git push -u origin feature/<feature-name>
```

Then create a Pull Request on GitHub:
- Compare: `feature/<feature-name>` → `main`
- Include version number in title
- Link to relevant issues

### 5. Merging to Main

After review and approval:

```bash
# Switch to main
git checkout main

# Merge feature branch
git merge feature/<feature-name>

# Push to remote
git push origin main

# Delete feature branch (optional)
git branch -d feature/<feature-name>
git push origin --delete feature/<feature-name>
```

---

## File Structure for Version Management

```
Thesis_Autonomous_Shipping/
├── CHANGELOG.md                 # Version history and changes
├── CLAUDE.md                    # This file - workflow documentation
├── src/
│   ├── __init__.py             # Version number and public API
│   └── models/
│       ├── agent.py
│       ├── network.py
│       └── diffusion.py
├── tests/
│   └── unit/
│       ├── test_agent.py
│       ├── test_network.py
│       └── test_diffusion.py
└── examples/
    ├── agent_demo.py
    └── simple_network_demo.py
```

---

## Version Update Checklist

When creating a new version, ensure all of these are updated:

- [ ] **CHANGELOG.md**
  - Add new version section
  - Document all changes (Added/Changed/Fixed/Removed)
  - Include date

- [ ] **src/__init__.py**
  - Update `__version__`
  - Add entry to `__changelog__` dict
  - Export new public API elements in `__all__`

- [ ] **Tests**
  - Create test file for new features
  - Ensure all tests pass
  - Document test count in commit

- [ ] **Examples/Demos**
  - Create demo script showing usage
  - Test demo runs successfully

- [ ] **Documentation**
  - Update README if needed
  - Add docstrings to new code
  - Update module README if applicable

---

## CHANGELOG Format

Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format:

```markdown
## [Version] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing features

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security fixes
```

---

## Git Commit Message Format

### Structure
```
<Type>: <Short description> (<version>)

<Detailed description>

<Bullet points for:>
- Features
- Infrastructure
- Tests
- Documentation

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only
- **style**: Code style/formatting
- **refactor**: Code restructuring
- **test**: Adding tests
- **chore**: Maintenance tasks

### Example
```
Add agent model for network-based ABM (v0.3.0)

Added comprehensive agent implementation with network navigation.

Features:
- Agent class with network travel capabilities
- AgentState enum (IDLE, TRAVELING, AT_DESTINATION, STOPPED)
- Route planning and navigation
- Journey tracking (distance, time, progress)

Infrastructure:
- Updated CHANGELOG.md to v0.3.0
- Updated src/__init__.py to v0.3.0
- Added 32 unit tests (all passing)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Testing Requirements

All features must include tests before merging:

### Test File Location
```
tests/unit/test_<module_name>.py
```

### Test Structure
```python
class Test<ClassName>:
    """Tests for <ClassName>."""

    @pytest.fixture
    def sample_instance(self):
        """Create sample instance for testing."""
        return ClassName(...)

    def test_basic_functionality(self, sample_instance):
        """Test basic use case."""
        assert sample_instance.method() == expected
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/unit/ -v

# Run specific test file
python -m pytest tests/unit/test_agent.py -v

# Run with coverage
python -m pytest tests/unit/ --cov=src --cov-report=html
```

### Test Coverage Goals
- **Minimum**: 70% coverage
- **Target**: 85%+ coverage
- **Critical modules**: 95%+ coverage

---

## Example: Creating a New Feature

Let's walk through creating a hypothetical `Scheduler` feature:

### Step 1: Create Branch
```bash
git checkout -b feature/scheduler
```

### Step 2: Implement Feature
Create `src/models/scheduler.py`:
```python
"""
Scheduler for managing agent simulation steps.
"""

class Scheduler:
    """Manages simulation time and agent scheduling."""

    def __init__(self):
        self.current_time = 0
        self.agents = []

    def add_agent(self, agent):
        """Add agent to scheduler."""
        self.agents.append(agent)

    def step(self):
        """Advance simulation by one time step."""
        self.current_time += 1
        # ... schedule agent actions
```

### Step 3: Update Version Files

**CHANGELOG.md**:
```markdown
## [0.4.0] - 2024-11-27

### Added
- Scheduler module for managing agent simulations
- Time-based event scheduling
- Agent action coordination
```

**src/__init__.py**:
```python
__version__ = "0.4.0"

__changelog__ = {
    "0.4.0": "Added scheduler for agent simulation management",
    "0.3.0": "Added agent model for network-based ABM simulations",
    # ...
}

from src.models.scheduler import Scheduler

__all__ = [
    # ... existing exports
    "Scheduler",
]
```

### Step 4: Write Tests
Create `tests/unit/test_scheduler.py`:
```python
import pytest
from src.models.scheduler import Scheduler
from src.models.agent import create_agent

class TestScheduler:
    def test_scheduler_creation(self):
        scheduler = Scheduler()
        assert scheduler.current_time == 0

    def test_add_agent(self):
        scheduler = Scheduler()
        agent = create_agent("vessel", "A", "A")
        scheduler.add_agent(agent)
        assert len(scheduler.agents) == 1
```

### Step 5: Create Demo
Create `examples/scheduler_demo.py`:
```python
"""Demonstration of scheduler functionality."""

from src.models.scheduler import Scheduler
from src.models.agent import create_agent
from src.models.network import Network, Node, Edge

# ... demo implementation
```

### Step 6: Commit and Push
```bash
git add -A
git commit -m "Add scheduler module (v0.4.0)

..."
git push -u origin feature/scheduler
```

### Step 7: Create Pull Request
On GitHub, create PR: `feature/scheduler` → `main`

---

## Quick Reference

### Common Commands

```bash
# Check current branch
git branch

# Check status
git status

# View version
python -c "import src; print(src.__version__)"

# Run all tests
python -m pytest tests/unit/ -v

# Run specific demo
python examples/agent_demo.py

# View changelog
cat CHANGELOG.md
```

### Version Locations

- `src/__init__.py` - `__version__` variable
- `CHANGELOG.md` - Detailed version history
- Git tags - `git tag` (if using tags)

---

## Best Practices

### 1. Branch Management
- ✅ Create feature branches from up-to-date `main`
- ✅ Keep feature branches focused and short-lived
- ✅ Delete merged feature branches
- ❌ Don't commit directly to `main`
- ❌ Don't create long-lived feature branches

### 2. Version Updates
- ✅ Update all version files together
- ✅ Use semantic versioning correctly
- ✅ Document all changes in CHANGELOG
- ❌ Don't skip version numbers
- ❌ Don't forget to update `__changelog__`

### 3. Commits
- ✅ Write descriptive commit messages
- ✅ Include version number in feature commits
- ✅ Commit working, tested code
- ❌ Don't commit broken code
- ❌ Don't make commits too large

### 4. Testing
- ✅ Write tests before merging
- ✅ Run all tests before pushing
- ✅ Aim for high coverage
- ❌ Don't merge without tests
- ❌ Don't ignore failing tests

---

## Troubleshooting

### "I forgot to update the version"
```bash
# If not yet pushed
git reset --soft HEAD~1
# Update version files
git add .
git commit -m "..."
```

### "I need to change my last commit"
```bash
# If not yet pushed
git commit --amend
```

### "My branch is behind main"
```bash
git checkout feature/my-feature
git merge main
# Resolve conflicts if any
git push
```

### "I want to see what changed between versions"
```bash
git diff v0.2.0..v0.3.0
# or
git log v0.2.0..v0.3.0
```

---

## Future Considerations

### Potential Additions

1. **Git Tags for Releases**
   ```bash
   git tag -a v0.3.0 -m "Version 0.3.0: Agent model"
   git push origin v0.3.0
   ```

2. **Automated Version Bumping**
   - Use `bump2version` or similar tool
   - Automate CHANGELOG generation

3. **CI/CD Pipeline**
   - Automated testing on PR
   - Version validation
   - Automatic deployment

4. **Release Notes**
   - Generate from CHANGELOG
   - Include in GitHub releases

---

## Resources

- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Git Feature Branch Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## Feature Documentation

### Traffic Behavior Module (v0.4.0)

The traffic behavior module introduces realistic inland waterway simulation with dynamic speed adjustments and crossroad management.

#### Key Components

**1. TrafficManager** (`src/models/traffic.py`)
- Coordinates traffic behavior across the entire network
- Tracks vessel positions on edges
- Manages crossroad occupation and queuing
- Calculates dynamic travel times based on congestion

**2. EdgeTraffic**
- Tracks vessel density on each edge
- Calculates effective speed based on congestion
- Edge capacity: 12 vessels per kilometer

**3. CrossroadState**
- Manages crossroad occupation (First-Come-First-Served)
- Maintains waiting queues
- 30-minute transit time per vessel

#### Modeling Assumptions

All assumptions are clearly documented in the module docstring:

1. **Edge Capacity**
   - Rhine waterway width: 200-400m navigable channel
   - Inland vessel length: ~85-110m
   - Safe separation: ~2 vessel lengths
   - **Result**: 12 vessels per km per direction

2. **Speed Reduction Model**
   - Formula: `effective_speed = base_speed × (1 - 0.7 × density_ratio)`
   - Maximum slowdown: 70% at full capacity
   - Minimum speed: 30% of base speed

3. **Crossroads**
   - Identified as nodes with 3+ connections
   - Transit time: 30 minutes
   - Priority: First-come-first-served (FCFS)

4. **Distances**
   - Straight-line distances between ports
   - Actual river distances ~10-20% longer (not modeled)

#### Usage Example

```python
from src.models.traffic import TrafficManager
from src.models.network import Network

# Create network
network = create_rhine_network()

# Initialize traffic manager
traffic_mgr = TrafficManager(network)

# Get effective speed considering congestion
effective_speed = traffic_mgr.get_effective_speed(
    agent_id="vessel_1",
    base_speed=15.0,
    source="Rotterdam",
    target="Dordrecht"
)

# Check crossroad availability
can_enter, wait_time = traffic_mgr.check_crossroad_entry(
    agent_id="vessel_1",
    node_id="Nijmegen"
)
```

#### Enhanced Agent Tracking

**New Agent Attribute:**
- `waiting_time`: Tracks time spent waiting (traffic, crossroads)

**Updated CSV Exports:**
- Ship summary: `waiting_time_hours`, `total_time_hours`, `base_speed_kmh`
- Time series: `effective_speed_kmh`, `waiting_time_hours`

**Enhanced Metrics:**
- Total/average waiting time
- Total system time = travel time + waiting time

#### Testing

Run traffic behavior simulation:
```bash
# With 10 ships, seed 42
python examples/agent_demo_random.py --non-interactive --ships 10 --seed 42

# With 50 ships for higher congestion
python examples/agent_demo_random.py --non-interactive --ships 50 --seed 123
```

Expected behavior:
- Higher ship density → lower effective speeds
- Crossroad waiting times appear in metrics
- Time series shows speed variations due to congestion

---

*Last Updated: 2024-11-26 (v0.4.0)*
