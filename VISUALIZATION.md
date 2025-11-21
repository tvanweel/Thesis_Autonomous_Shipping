# ABM Visualization Guide

## Quick Start

### Windows
Double-click `run_visualization.bat` or run in terminal:
```bash
solara run app.py
```

### Mac/Linux
```bash
solara run app.py
```

The visualization will automatically open in your browser at **http://localhost:8765**

## What You'll See

### Main Visualization Components

1. **Waterway Canvas** (Top Panel)
   - Horizontal axis: Position along 5km waterway (0-5000 meters)
   - Vessels shown as colored arrows
   - Upper lane: Downstream traffic (→)
   - Lower lane: Upstream traffic (←)
   - Hover over vessels to see details

2. **Safety Metrics Card** (Right Panel)
   - Current simulation step
   - Total encounters
   - Near misses (50-100m)
   - Collisions (<50m)
   - Average encounter distance
   - Collision rate percentage

3. **Time-Series Plots** (Bottom Panel)
   - Total encounters over time (blue)
   - Near misses over time (orange)
   - Collisions over time (red)
   - Average encounter distance over time (green)

4. **Control Panel** (Left Panel)
   - **Number of Vessels**: Slider (5-50 vessels)
   - **Fleet Composition**: Dropdown menu
     - Baseline (40% L0, 30% L1, 20% L2, 10% L3)
     - All Manual (100% L0)
     - High Automation (40% L3, 30% L2, 20% L1, 10% L0)
     - Equal Mix (25% each level)
   - **Time Step**: Slider (1-10 seconds)
   - **Start/Pause**: Begin or pause simulation
   - **Step**: Advance one step at a time
   - **Reset**: Restart with current parameters

## Color Legend

| Color | Automation Level | Detection Range |
|-------|------------------|-----------------|
| 🔴 Red | L0 - Manual | 500m |
| 🟠 Orange | L1 - Steering Assist | 750m |
| 🟡 Yellow | L2 - Partial Automation | 1000m |
| 🟢 Green | L3 - Conditional Automation | 1200m |

## How to Use

### Running a Basic Simulation

1. **Start the server**: `solara run app.py`
2. **Browser opens** automatically to http://localhost:8765
3. **Click "Start"** to begin the simulation
4. **Watch** vessels move along the waterway
5. **Observe** safety metrics update in real-time

### Comparing Fleet Compositions

1. **Select "All Manual"** from fleet composition dropdown
2. **Click "Reset"** to restart with new parameters
3. **Click "Start"** and run for ~100 steps
4. **Note the collision rate**
5. **Select "High Automation"**
6. **Click "Reset"** and run again
7. **Compare collision rates** between scenarios

**Expected Result**: High automation scenarios should show:
- ✓ Lower collision rates
- ✓ Higher average encounter distances
- ✓ Fewer near-misses

### Investigating Vessel Density

1. **Set vessels to 10** using slider
2. **Run simulation** and observe metrics
3. **Reset and set vessels to 50**
4. **Run simulation** again
5. **Compare encounter rates**

**Expected Result**: More vessels = more encounters (but collision rate per encounter should remain similar)

### Step-by-Step Analysis

1. **Click "Step"** instead of "Start"
2. **Advance one time step** at a time
3. **Watch individual vessel movements**
4. **See exactly when encounters occur**
5. **Useful for understanding collision scenarios**

## Understanding the Metrics

### Total Encounters
- Count of all vessel pairs that came within detection range
- Heading toward each other (opposite directions)
- Detection range varies by automation level

### Near Misses
- Vessel pairs that came within 50-100 meters
- Potentially dangerous situations
- Should decrease with higher automation

### Collisions
- Vessel pairs that came within <50 meters
- Critical safety failures
- Primary metric for safety assessment

### Average Encounter Distance
- Mean distance across all encounters
- Higher is better (more separation)
- Should increase with better detection systems

### Collision Rate
- Percentage: (Collisions / Total Encounters) × 100
- Normalized metric for comparison
- Accounts for different encounter frequencies

## Typical Results

Based on 720 steps (1 hour simulation):

| Scenario | Collision Rate | Avg Distance | Collisions |
|----------|----------------|--------------|------------|
| All Manual (L0) | ~5.6% | ~255m | ~700-800 |
| Baseline Mix | ~3.9% | ~400m | ~700-850 |
| High Automation | ~3.1% | ~500m | ~700-850 |

*Note: Absolute collision counts may vary due to different total encounters, but collision rate shows the safety improvement*

## Troubleshooting

### Visualization won't start
```bash
# Make sure solara is installed
pip install solara

# Check if port 8765 is already in use
# Close other applications using that port or specify different port:
solara run app.py --port 8888
```

### Browser doesn't open automatically
Manually navigate to: **http://localhost:8765**

### Simulation runs too fast/slow
- Adjust the **play interval** in the code (app.py line 211)
- Default: 500ms between steps
- Increase for slower: `play_interval=1000`
- Decrease for faster: `play_interval=200`

### Vessels overlap/hard to see
- Reduce number of vessels (use slider)
- Zoom in on the waterway plot (use plotly controls)
- Click and drag to pan the view

## Advanced Usage

### Modifying Detection Ranges

Edit [src/models/simple_abm.py](src/models/simple_abm.py:29-34):

```python
DETECTION_RANGES = {
    'L0': 500,   # Change these values
    'L1': 750,
    'L2': 1000,
    'L3': 1200
}
```

### Changing Waterway Length

Edit [src/models/simple_abm.py](src/models/simple_abm.py:48):

```python
self.position = random.uniform(0, 5000)  # Change 5000 to desired length
```

Also update boundary conditions in `step()` method.

### Adding More Automation Levels

1. Add L4/L5 to detection ranges
2. Update color maps in [app.py](app.py:33-38)
3. Add to fleet composition choices
4. Test with new scenarios

## Files Overview

- **app.py** - Main visualization application (run this!)
- **src/models/simple_abm.py** - Core ABM model
- **src/visualization/abm_viz.py** - Visualization components (alternative implementation)
- **examples/run_basic_sim.py** - Command-line simulation (no visualization)
- **run_visualization.bat** - Windows quick-start script

## Next Steps

After understanding the basic visualization:

1. **Extend to 2D movement** - Add lateral position
2. **Implement COLREGS** - Add maritime traffic rules
3. **Add collision avoidance** - Vessels actively avoid each other
4. **Integrate with diffusion model** - Use diffusion outputs as fleet composition inputs
5. **Add environmental factors** - Weather, visibility, current

## Support

For questions or issues:
1. Check the code comments in [app.py](app.py) and [simple_abm.py](src/models/simple_abm.py)
2. Review Mesa documentation: https://mesa.readthedocs.io/
3. Solara docs: https://solara.dev/

## Performance Tips

- **Start small**: Begin with 20 vessels to ensure smooth performance
- **Increase gradually**: Test with 30, 40, 50 vessels if performance allows
- **Lower time step**: Larger time steps (5-10s) run faster than 1s steps
- **Close unused browser tabs**: Free up memory for smooth visualization
- **Monitor CPU usage**: If laggy, reduce vessel count or increase play interval

Enjoy exploring your inland shipping safety simulation! 🚢
