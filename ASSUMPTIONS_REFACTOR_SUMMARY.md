# Assumptions Refactor Summary

## Overview

The assumptions file has been **refactored to serve as the single source of truth** for all model parameters. Now, when you change values in `src/assumptions.py`, the model will automatically use those new values.

---

## What Changed

### Before

- `src/assumptions.py` was a **documentation file** with many unused values
- Model code had **hardcoded constants** (e.g., `VESSELS_PER_KM_CAPACITY = 12`)
- Changing assumptions required editing multiple files
- Unused/commented assumptions were mixed with active ones

### After

- `src/assumptions.py` is now a **configuration file** that models import from
- Only contains **assumptions actually used** in the model
- Changing assumptions is **centralized** in one file
- Unused assumptions are **clearly documented** at the bottom (commented out)
- Helper functions make it easy to load configurations

---

## Files Modified

### Core Model Files

1. **`src/assumptions.py`** - Complete rewrite
   - Organized into 3 active categories: TRAFFIC, AGENT, NETWORK
   - Added helper functions: `get_traffic_config()`, `get_agent_config()`, `get_network_config()`, `get_all_assumptions()`
   - Moved unused assumptions to commented section at bottom
   - Added clear documentation of where each assumption is used

2. **`src/models/traffic.py`**
   - Now imports from `src.assumptions`
   - Loads constants from assumptions: `VESSELS_PER_KM_CAPACITY`, `CONGESTION_IMPACT_FACTOR`, etc.
   - Constants are set at module load time from assumptions file

3. **`src/models/agent.py`**
   - Now imports from `src.assumptions`
   - Uses `_DEFAULT_SPEED` from assumptions as default value
   - `create_agent()` function updated to use None as default (meaning: use assumptions)

4. **`examples/agent_demo_random.py`**
   - Now imports from `src.assumptions`
   - Loads `vessel_speed_range_kmh` and `ris_connectivity_by_level` from assumptions
   - Random generation now respects configured ranges

### Test Files

5. **`tests/unit/test_agent.py`**
   - Updated `test_create_agent_with_properties()` to reflect that `speed` is now an explicit agent attribute (not a property)

### Documentation

6. **`docs/ASSUMPTIONS.md`** - New comprehensive guide
   - How to use assumptions system
   - How to run scenarios
   - Example code snippets
   - Troubleshooting guide

7. **`examples/test_assumptions.py`** - New demo script
   - Shows currently loaded assumption values
   - Demonstrates how to use assumptions in code

---

## Active Assumptions (Used by Model)

### Traffic Behavior (`src/models/traffic.py`)
```python
TRAFFIC = {
    "vessels_per_km_capacity": 12,
    "congestion_impact_factor": 0.7,
    "min_speed_ratio": 0.3,
    "crossroad_transit_time_hours": 0.5,
}
```

### Agent/Vessel Characteristics (`src/models/agent.py`, `examples/`)
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

### Network Configuration (`examples/`)
```python
NETWORK = {
    "distances_km": {
        "rotterdam_dordrecht": 24,
        "dordrecht_nijmegen": 95,
        # ... other distances
    },
    "distance_meandering_factor": 1.15,
}
```

---

## Inactive Assumptions (Preserved for Future Use)

The following were in the original file but are **NOT used** in current model code. They remain in `assumptions.py` as comments for documentation:

- `bass_q_maritime`, `retrofit_cost_multiplier` - Diffusion model parameters
- `roc_takeover_time_mean_seconds`, `platform_failure_correlation` - Safety/reliability
- Port capacities, narrow channel reduction - Port infrastructure
- Scenario parameters - L3 adoption years, investment thresholds
- Physical characteristics - Rhine width, vessel length, safe separation

These can be uncommented and integrated when needed.

---

## How to Use

### View Current Assumptions

```bash
python examples/test_assumptions.py
```

### Change an Assumption

1. Edit `src/assumptions.py`
2. Change the value (e.g., `"default_vessel_speed_kmh": 16.0`)
3. Save
4. Run your simulation - it uses the new value automatically!

### Example: Run High-Capacity Scenario

Edit `src/assumptions.py`:
```python
TRAFFIC = {
    "vessels_per_km_capacity": 18,  # Changed from 12
    "congestion_impact_factor": 0.5,  # Changed from 0.7
}
```

Run simulation:
```bash
python examples/agent_demo_random.py --ships 50
```

The model will now use higher capacity and lower congestion impact.

---

## Testing

All 127 tests pass after refactoring:

```bash
python -m pytest tests/ -v
# ===== 127 passed in 1.15s =====
```

Tests confirm that:
- Models load assumptions correctly
- Default values work as expected
- Traffic calculations use configured constants
- Agent creation respects speed defaults

---

## Benefits

✅ **Centralized Configuration**: One file to rule them all
✅ **Easy Scenarios**: Change values → run simulation → compare results
✅ **Clear Documentation**: Each assumption has citation type and usage location
✅ **Backward Compatible**: All existing code still works
✅ **Type Safe**: Helper functions return proper types
✅ **Testable**: Assumption changes can be validated

---

## Migration Guide (For Future Assumptions)

To add a new assumption that's actually used in the model:

1. **Add to assumptions.py**:
   ```python
   TRAFFIC = {
       "new_parameter": 42,  # [ASSUMED] Description and citation
   }
   ```

2. **Use in model code**:
   ```python
   from src.assumptions import get_traffic_config

   config = get_traffic_config()
   value = config["new_parameter"]
   ```

3. **Document in ASSUMPTIONS.md**:
   - Add to relevant table
   - Explain what it affects
   - Show example usage

4. **Test**:
   - Add test to verify parameter is used
   - Test with different values

---

## Next Steps

1. ✅ Refactor assumptions file (DONE)
2. ✅ Update model code to use assumptions (DONE)
3. ✅ Create documentation (DONE)
4. ✅ Test everything (DONE)
5. 📝 Commit changes with clear message
6. 🔄 Consider adding scenario management system
7. 📊 Run sensitivity analysis using new system

---

## Questions?

See:
- **`docs/ASSUMPTIONS.md`** - Comprehensive guide
- **`src/assumptions.py`** - The assumptions themselves
- **`examples/test_assumptions.py`** - Demo of usage
- **Model code** in `src/models/` - Examples of how assumptions are used

---

*Created: 2024-11-27*
*Author: Claude Code*
