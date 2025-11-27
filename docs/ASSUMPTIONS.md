# Model Assumptions Guide

This document explains how to use and modify the assumptions configuration system in the autonomous shipping simulation model.

---

## Overview

The `src/assumptions.py` file contains **all configurable parameters** used by the simulation models. This centralized configuration makes it easy to:

- **Run different scenarios** by changing parameter values
- **Conduct sensitivity analysis** by systematically varying assumptions
- **Document assumptions** with clear citations and justifications
- **Ensure consistency** across all model components

### Key Principle

**All values in `assumptions.py` are actively used by the model code.**

When you change a value in the assumptions file, it will **directly affect** how the model runs.

---

## Quick Start

### View Current Assumptions

```bash
python examples/test_assumptions.py
```

This displays all assumptions currently loaded by the model.

### Change an Assumption

1. Open `src/assumptions.py`
2. Find the parameter you want to change (e.g., `"default_vessel_speed_kmh": 14.0`)
3. Modify the value (e.g., change to `16.0`)
4. Save the file
5. Run your simulation - it will use the new value automatically

### Example: Change Traffic Congestion Behavior

Edit `src/assumptions.py`:

```python
TRAFFIC = {
    "vessels_per_km_capacity": 15,  # Changed from 12 to 15
    "congestion_impact_factor": 0.5,  # Changed from 0.7 to 0.5
    # ... other parameters
}
```

Now run a simulation:

```bash
python examples/agent_demo_random.py --ships 50
```

The model will now use:
- Higher edge capacity (15 vessels/km instead of 12)
- Lower congestion impact (50% speed reduction instead of 70%)

---

## Assumption Categories

### 1. Traffic Behavior Model

**Used in:** `src/models/traffic.py`

These assumptions control how vessel congestion and crossroads affect travel times.

```python
TRAFFIC = {
    "vessels_per_km_capacity": 12,
    "congestion_impact_factor": 0.7,
    "min_speed_ratio": 0.3,
    "crossroad_transit_time_hours": 0.5,
}
```

**Parameters:**

| Parameter | Default | Description | Citation |
|-----------|---------|-------------|----------|
| `vessels_per_km_capacity` | 12 | Maximum vessels per km of waterway | [ASSUMED] Based on Rhine width (200-400m), vessel length (~85-110m), safe separation (~2 vessel lengths) |
| `congestion_impact_factor` | 0.7 | Maximum speed reduction due to congestion (70% at capacity) | [ASSUMED] Linear model: `effective_speed = base_speed × (1 - 0.7 × density_ratio)` |
| `min_speed_ratio` | 0.3 | Minimum speed maintained even at extreme congestion (30% of base speed) | [ASSUMED] Expert judgment |
| `crossroad_transit_time_hours` | 0.5 | Time to navigate through intersection (30 minutes) | [ASSUMED] Crossroads defined as nodes with 3+ connections, FCFS priority |

### 2. Agent/Vessel Characteristics

**Used in:** `src/models/agent.py`, `examples/agent_demo_random.py`

These assumptions define default vessel properties and behavior.

```python
AGENT = {
    "default_vessel_speed_kmh": 14.0,
    "vessel_speed_range_kmh": (10.0, 18.0),
    "ris_connectivity_by_level": {
        "L0_L2": 0.2,
        "L3_L4": 0.6,
        "L5": 0.9,
    },
}
```

**Parameters:**

| Parameter | Default | Description | Citation |
|-----------|---------|-------------|----------|
| `default_vessel_speed_kmh` | 14.0 | Default cruising speed for inland vessels | [ASSUMED] Typical Rhine vessel speed |
| `vessel_speed_range_kmh` | (10.0, 18.0) | Speed range for vessel heterogeneity (min, max) | [ASSUMED] Observed range for inland shipping |
| `ris_connectivity_by_level` | L0-L2: 0.2<br>L3-L4: 0.6<br>L5: 0.9 | Probability of RIS connectivity by automation level | [ASSUMED] Higher automation correlates with better digital infrastructure |

### 3. Network Configuration

**Used in:** `examples/agent_demo.py`, `examples/agent_demo_random.py`

These assumptions define the Rhine corridor network distances.

```python
NETWORK = {
    "distances_km": {
        "rotterdam_dordrecht": 24,
        "dordrecht_nijmegen": 95,
        "nijmegen_duisburg": 111,
        "duisburg_cologne": 60,
        "cologne_mannheim": 143,
        "rotterdam_nijmegen_direct": 130,
    },
    "distance_meandering_factor": 1.15,
}
```

**Parameters:**

| Parameter | Default | Description | Citation |
|-----------|---------|-------------|----------|
| `distances_km` | (various) | Port-to-port distances in Rhine corridor | [CALIBRATED] From GIS/maritime data |
| `distance_meandering_factor` | 1.15 | Actual river distance vs straight-line (10-20% longer) | [ASSUMED] Note: NOT currently applied in model |

---

## Using Assumptions in Code

### Method 1: Direct Import (Simple)

```python
from src.assumptions import TRAFFIC, AGENT

# Access values directly
capacity = TRAFFIC["vessels_per_km_capacity"]
default_speed = AGENT["default_vessel_speed_kmh"]
```

### Method 2: Helper Functions (Recommended)

```python
from src.assumptions import get_traffic_config, get_agent_config

# Get configuration dictionaries (returns copies)
traffic_config = get_traffic_config()
agent_config = get_agent_config()

# Use in simulation
capacity = traffic_config["vessels_per_km_capacity"]
speed_range = agent_config["vessel_speed_range_kmh"]
```

### Method 3: Get All Assumptions

```python
from src.assumptions import get_all_assumptions

# Get all assumptions organized by category
assumptions = get_all_assumptions()

traffic_params = assumptions["traffic"]
agent_params = assumptions["agent"]
network_params = assumptions["network"]
```

---

## How Models Use Assumptions

### Traffic Model (`src/models/traffic.py`)

The traffic model loads assumptions at import time:

```python
from src.assumptions import get_traffic_config

_TRAFFIC_CONFIG = get_traffic_config()
VESSELS_PER_KM_CAPACITY = _TRAFFIC_CONFIG["vessels_per_km_capacity"]
CONGESTION_IMPACT_FACTOR = _TRAFFIC_CONFIG["congestion_impact_factor"]
# ... etc
```

These constants are then used throughout the module:

```python
def _initialize_edges(self):
    for edge in self.network.edges:
        distance = edge.properties.get("distance_km", edge.weight)
        capacity = int(distance * VESSELS_PER_KM_CAPACITY)  # Uses assumption
        # ...
```

### Agent Model (`src/models/agent.py`)

The agent model uses assumptions for default values:

```python
from src.assumptions import get_agent_config

_AGENT_CONFIG = get_agent_config()
_DEFAULT_SPEED = _AGENT_CONFIG["default_vessel_speed_kmh"]

@dataclass
class Agent:
    # ... other fields
    speed: float = _DEFAULT_SPEED  # Uses assumption as default
```

### Example Scripts (`examples/agent_demo_random.py`)

Example scripts load assumptions for random generation:

```python
from src.assumptions import get_agent_config

agent_config = get_agent_config()
speed_min, speed_max = agent_config["vessel_speed_range_kmh"]
ris_probs = agent_config["ris_connectivity_by_level"]

# Generate random vessel with speeds from assumption range
speed = random.uniform(speed_min, speed_max)

# Assign RIS connectivity based on automation level probabilities
if automation_level <= 2:
    ris_connected = random.random() < ris_probs["L0_L2"]
```

---

## Scenario Analysis Workflow

### 1. Baseline Scenario

Run with default assumptions:

```bash
python examples/agent_demo_random.py --ships 50 --seed 42
```

Record results (travel times, congestion, etc.)

### 2. Create Scenario Variant

Edit `src/assumptions.py` for a "high capacity" scenario:

```python
TRAFFIC = {
    "vessels_per_km_capacity": 18,  # Increased from 12
    "congestion_impact_factor": 0.5,  # Reduced from 0.7
    # ... other parameters unchanged
}
```

### 3. Run Variant

```bash
python examples/agent_demo_random.py --ships 50 --seed 42
```

Use same seed for reproducibility.

### 4. Compare Results

Compare travel times, congestion levels, and system metrics between baseline and variant.

### 5. Document Changes

Keep track of which assumptions were changed and why:

```python
# Scenario: High Capacity Waterway
# Rationale: Simulate effects of widened navigation channels
TRAFFIC = {
    "vessels_per_km_capacity": 18,  # +50% capacity (widened channels)
    "congestion_impact_factor": 0.5,  # Reduced congestion (better flow management)
}
```

---

## Sensitivity Analysis Example

To test sensitivity to `congestion_impact_factor`:

```python
# sensitivity_analysis.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import and temporarily modify assumptions
import src.assumptions as assumptions

# Test different congestion impact factors
test_values = [0.3, 0.5, 0.7, 0.9]
results = []

for impact_factor in test_values:
    # Modify assumption
    assumptions.TRAFFIC["congestion_impact_factor"] = impact_factor

    # Reload traffic module to pick up new value
    import importlib
    import src.models.traffic
    importlib.reload(src.models.traffic)

    # Run simulation
    # ... your simulation code here ...

    results.append({
        'impact_factor': impact_factor,
        'avg_travel_time': avg_time,
        # ... other metrics
    })

# Analyze results
print(results)
```

---

## Assumptions Not Currently Used

The assumptions file includes commented-out sections for parameters that are **not yet used** in the model:

```python
# DIFFUSION_MODEL = {
#     "bass_q_maritime": 0.38,
#     "retrofit_cost_multiplier": 2.3,
# }
```

These are preserved for:
- **Documentation**: Show what was considered
- **Future use**: Easy to uncomment and integrate later
- **Transparency**: Clear about what is and isn't used

---

## Best Practices

### 1. Always Document Changes

When you change an assumption, add a comment:

```python
TRAFFIC = {
    # CHANGED 2024-11-27: Increased for Rhine widening scenario
    "vessels_per_km_capacity": 18,  # Was: 12
}
```

### 2. Use Version Control

Commit `assumptions.py` changes with clear messages:

```bash
git commit -m "Increase vessel capacity to 18 for widening scenario"
```

### 3. Keep Backups

Before major changes, save a copy:

```bash
cp src/assumptions.py src/assumptions_baseline.py
```

### 4. Run Tests After Changes

Ensure model still works:

```bash
python -m pytest tests/ -v
```

### 5. Document Rationale

Include citations or reasoning in comments:

```python
# [ASSUMED] Based on Rhine Engineering Report (2023)
# Narrow channels: 200m width → 12 vessels/km
# Wide channels: 400m width → 18 vessels/km
"vessels_per_km_capacity": 18,
```

---

## Citation Types

Assumptions are categorized by their source:

- **[EMPIRICAL]**: Values from literature/data with citations
  - Example: `bass_q_maritime: 0.38` from Frank (2004)

- **[CALIBRATED]**: Fitted to Rhine corridor data
  - Example: `rotterdam_dordrecht_km: 24` from GIS data

- **[ASSUMED]**: Expert judgment or borrowed from adjacent domains
  - Example: `vessels_per_km_capacity: 12` derived from physical constraints

- **[SCENARIO]**: Systematically varied in analysis
  - Example: Different adoption start years (2026, 2028, 2030)

---

## Troubleshooting

### Problem: Changes Don't Affect Model

**Solution:** Make sure you're editing `src/assumptions.py` and not a copy. Check that the file is in the correct location.

### Problem: Model Uses Old Values

**Solution:** Restart Python or your notebook kernel. The assumptions are loaded at import time.

### Problem: Tests Fail After Changing Assumptions

**Solution:** Some tests may expect specific default values. Either:
1. Revert assumptions to baseline for testing
2. Update tests to work with new values
3. Use test-specific assumption overrides

### Problem: Import Errors

**Solution:** Ensure `src/assumptions.py` has no syntax errors. Check:

```bash
python -c "from src.assumptions import get_all_assumptions; print('OK')"
```

---

## Related Documentation

- **Model Code**: `src/models/` - See how assumptions are used
- **Examples**: `examples/` - See assumptions in practice
- **Tests**: `tests/unit/` - See assumption validation
- **Version Control**: `CLAUDE.md` - See workflow documentation

---

## Summary

✅ **Centralized**: All configurable parameters in one place
✅ **Documented**: Clear citations and justifications
✅ **Active**: Changes directly affect model behavior
✅ **Traceable**: Version control tracks all changes
✅ **Testable**: All assumptions validated by tests

**To change model behavior:** Edit `src/assumptions.py` → Save → Run simulation

---

*Last Updated: 2024-11-27*
