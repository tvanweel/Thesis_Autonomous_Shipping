# Multi-Level Automation Diffusion Model

## Overview

This project implements a **Bass diffusion model** for analyzing the adoption of maritime automation technologies in European inland shipping. The model tracks adoption across five distinct automation levels (L1-L5) based on CCNR (Central Commission for the Navigation of the Rhine) definitions.

## Model Architecture

### Core Concept: Mutually Exclusive Levels

The model treats automation levels as **mutually exclusive categories** where each vessel belongs to exactly ONE level at any given time:

```
L0 + L1 + L2 + L3 + L4 + L5 = total_fleet (always)
```

- **L0**: Manual operation (no automation) - baseline
- **L1**: Steering assistance (track pilot with basic automation features)
- **L2**: Partial automation (track pilot + propulsion control)
- **L3**: Conditional automation (with collision avoidance, still in development)
- **L4**: High automation (advanced autonomous capabilities)
- **L5**: Full automation (fully autonomous vessels)

### Key Characteristics

1. **Independent Growth**: Each level evolves according to its own Bass diffusion dynamics
2. **Distinct Technologies**: L5 does NOT necessarily incorporate L1-L4 functionalities
3. **Competition**: Levels compete for adoption from the same vessel population
4. **Fleet Constraint**: Total adoption across all levels cannot exceed fleet size

## Implementation

### File Structure

```
src/
├── models/
│   └── diffusion.py              # Core Bass diffusion implementation
├── config/
│   ├── __init__.py
│   └── diffusion_config.py       # Scenario configurations
tests/
└── test_diffusion.py             # Comprehensive test suite (21 tests)
visualizations/
└── show_diffusion.py             # Visualization generation
results/
├── 1_multilevel_adoption_curves.png
├── 2_scenario_comparison.png
├── 3_market_share_evolution.png
├── 4_uncertainty_bands.png
└── 5_sensitivity_analysis.png
```

### Core Components

#### 1. BassDiffusionModel ([src/models/diffusion.py](src/models/diffusion.py))

Implements the basic Bass diffusion equation for a single technology:

```python
dN/dt = (p + q * N/M) * (M - N)
```

**Parameters:**
- `M`: Market potential (maximum adopters)
- `p`: Innovation coefficient (external influence)
- `q`: Imitation coefficient (word-of-mouth)
- `dt`: Time step size

#### 2. MultiLevelAutomationDiffusion ([src/models/diffusion.py](src/models/diffusion.py))

Manages five independent Bass diffusion models with fleet constraint enforcement:

```python
model = MultiLevelAutomationDiffusion(
    total_fleet=10000,
    initial_L1=450, M1=3000, p1=0.035, q1=0.45,
    initial_L2=450, M2=3500, p2=0.030, q2=0.40,
    initial_L3=0,   M3=2000, p3=0.020, q3=0.30,
    initial_L4=0,   M4=1000, p4=0.012, q4=0.22,
    initial_L5=0,   M5=500,  p5=0.008, q5=0.15,
    dt=1.0
)
model.run(steps=30)
```

**Fleet Constraint Logic:**
1. Each level's Bass model advances independently
2. Apply individual market potential caps: `N_i ≤ M_i`
3. If total adoption exceeds fleet, proportionally scale all levels:
   ```python
   if N1 + N2 + N3 + N4 + N5 > total_fleet:
       scale_factor = total_fleet / (N1 + N2 + N3 + N4 + N5)
       N_i *= scale_factor  # for all i
   ```

#### 3. DiffusionConfig ([src/config/diffusion_config.py](src/config/diffusion_config.py))

Provides three predefined scenarios with validated parameters:

**Baseline Scenario** (moderate adoption):
```python
config = DiffusionConfig.baseline()
# Market potentials: L1=3000, L2=3500, L3=2000, L4=1000, L5=500
# Sum = 10,000 (100% of fleet)
```

**Optimistic Scenario** (faster adoption, shift to higher levels):
```python
config = DiffusionConfig.optimistic()
# Market potentials: L1=2000, L2=2500, L3=3000, L4=1500, L5=1000
# Sum = 10,000 (100% of fleet)
# Higher p/q coefficients (+29% to +88%)
```

**Pessimistic Scenario** (slower adoption, concentration at lower levels):
```python
config = DiffusionConfig.pessimistic()
# Market potentials: L1=4000, L2=4000, L3=1500, L4=400, L5=100
# Sum = 10,000 (100% of fleet)
# Lower p/q coefficients (-29% to -50%)
```

### Validation Rules

The configuration class enforces realistic constraints:

1. **Individual Level Cap**: `M_i ≤ total_fleet` for all levels
2. **Sum Constraint**: `∑M_i ≤ 2 × total_fleet` (allows some competition)

## Usage Examples

### Basic Simulation

```python
from src.config import DiffusionConfig
from src.models.diffusion import MultiLevelAutomationDiffusion

# Use predefined scenario
config = DiffusionConfig.baseline()
model = MultiLevelAutomationDiffusion(**config.to_model_params())
model.run(steps=30)

# Access results
print(f"L1 adoption at year 30: {model.history_L1[-1]:.0f} vessels")
print(f"L5 adoption at year 30: {model.history_L5[-1]:.0f} vessels")
```

### Custom Scenario

```python
from src.config.diffusion_config import DiffusionConfig, LevelParameters

config = DiffusionConfig(
    total_fleet=10000,
    L1=LevelParameters(
        initial_adopters=500,
        market_potential=4000,
        innovation_coefficient=0.04,
        imitation_coefficient=0.50
    ),
    # ... define L2-L5 similarly
    time_horizon=50,
    scenario_name="custom"
)

model = MultiLevelAutomationDiffusion(**config.to_model_params())
model.run(steps=config.time_horizon)
```

### Generate Visualizations

```python
# From project root:
python -m visualizations.show_diffusion
```

This generates 5 visualizations in `results/`:
1. **Multi-level adoption curves**: All levels + L0 over time
2. **Scenario comparison**: Baseline vs Optimistic vs Pessimistic
3. **Market share evolution**: Stacked area chart showing fleet composition
4. **Uncertainty bands**: Range across scenarios for each level
5. **Sensitivity analysis**: Impact of varying p, q, and M parameters

## Testing

The test suite includes 21 tests covering:

- **Bass model fundamentals** (6 tests)
- **Multi-level behavior** (11 tests)
- **Configuration validation** (4 tests)

Run tests:
```bash
pytest tests/test_diffusion.py -v
```

### Key Test Coverage

1. **Fleet constraints**: Total adoption never exceeds fleet size
2. **Market potentials**: Each level respects its maximum
3. **Independent growth**: Levels can grow independently in mutually exclusive model
4. **Non-decreasing adoption**: Adoption cannot go backwards
5. **Numerical stability**: Consistent results across different timesteps
6. **Scenario validation**: All predefined scenarios pass validation

## Real-World Context

**European Inland Shipping Fleet** (~10,000 vessels):
- **Current state** (2024):
  - L0 (manual): ~9,100 vessels (91%)
  - L1+L2 (track pilot): ~900 vessels (9%)
  - L3-L5: 0 vessels (technologies in development)

**Baseline Projection** (30-year horizon):
- L1: 450 → ~2,950 vessels
- L2: 450 → ~3,450 vessels
- L3: 0 → ~1,950 vessels
- L4: 0 → ~850 vessels
- L5: 0 → ~350 vessels
- L0 remains: ~450 vessels

## Model Assumptions

1. **Fixed fleet size**: 10,000 vessels throughout simulation period
2. **Mutually exclusive adoption**: Each vessel adopts exactly ONE level
3. **No downgrades**: Vessels don't revert to lower automation levels
4. **Independent diffusion**: Each level follows its own Bass dynamics
5. **Proportional scaling**: When total demand exceeds fleet, all levels scale proportionally

## Parameter Interpretation

### Innovation Coefficient (p)
- **Range**: 0.004 - 0.045 in predefined scenarios
- **Meaning**: Rate of adoption by innovators (independent of others)
- **Higher values**: Faster early adoption

### Imitation Coefficient (q)
- **Range**: 0.08 - 0.55 in predefined scenarios
- **Meaning**: Rate of adoption due to word-of-mouth/peer influence
- **Higher values**: Steeper S-curve, faster mid-stage growth

### Market Potential (M)
- **Range**: 100 - 4,000 vessels per level
- **Meaning**: Maximum vessels that could adopt this specific level
- **Constraint**: Sum ≤ 2× fleet size (allows realistic competition)

## Recent Changes

### Version History

**Current Version**: Mutually Exclusive Model
- Changed from hierarchical (L5 ⊆ L4 ⊆ L3 ⊆ L2 ⊆ L1) to mutually exclusive categories
- Each level represents distinct technology with unique challenges
- Removed hierarchical constraints from step() method
- Updated validation: sum of market potentials ≤ 2× fleet
- Reconfigured all scenarios to realistic market potentials
- L0 calculation: `total_fleet - (L1 + L2 + L3 + L4 + L5)`

**Previous Version**: Fixed Fleet Model
- Removed fleet growth feature for simplicity
- Fleet size fixed at 10,000 vessels

## References

- **Bass Diffusion Model**: Bass, F. M. (1969). "A New Product Growth for Model Consumer Durables"
- **CCNR Automation Levels**: Central Commission for the Navigation of the Rhine standards
- **European Inland Shipping**: ~10,000 vessel fleet estimate

## Contributing

When modifying the model:

1. **Update tests**: Ensure all 21 tests pass after changes
2. **Regenerate visualizations**: Run `python -m visualizations.show_diffusion`
3. **Update documentation**: Keep this file synchronized with code changes
4. **Validate scenarios**: Ensure predefined scenarios remain realistic

## Contact

For questions about model implementation or parameter calibration, refer to:
- Model documentation: [src/models/diffusion.py](src/models/diffusion.py)
- Configuration: [src/config/diffusion_config.py](src/config/diffusion_config.py)
- Tests: [tests/test_diffusion.py](tests/test_diffusion.py)
