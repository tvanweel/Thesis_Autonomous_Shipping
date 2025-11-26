# Examples Directory

This directory contains demonstration scripts for the autonomous shipping simulation models.

## Available Demos

### 1. Agent Demo (Manual Configuration)
**File:** `agent_demo.py`

A detailed walkthrough demonstration with manually configured ships:
- 3 pre-configured ships with specific routes
- Step-by-step simulation showing agent movement
- Demonstrates all agent features (serialization, stop/resume, etc.)
- Good for understanding the agent model in detail

**Usage:**
```bash
python examples/agent_demo.py
```

### 2. Agent Demo (Random Configuration)
**File:** `agent_demo_random.py`

Simulation with randomly generated ships:
- Configurable number of ships
- Random start/destination assignments
- Random automation levels (0-5)
- Random capacities and cargo types
- Performance metrics output
- **CSV export of all ship data to `results/` directory**
- Command-line and interactive modes

**Usage:**
```bash
# Interactive mode
python examples/agent_demo_random.py

# Command-line mode
python examples/agent_demo_random.py --non-interactive --ships 20 --seed 42

# In VSCode Interactive Window / Jupyter
main(num_ships=20, seed=42, interactive=False)
```

**Arguments:**
- `--ships N`: Number of ships (default: 10)
- `--seed S`: Random seed for reproducibility
- `--non-interactive`: Skip user prompts

**Output:**
- Console output with metrics and ship details
- CSV file saved to `results/ship_simulation_YYYYMMDD_HHMMSS.csv` with columns:
  - ship_id
  - automation_level
  - origin
  - destination
  - distance_km
  - travel_time_hours
  - state
  - route (full path)

### 3. Simple Network Demo
**File:** `simple_network_demo.py`

Demonstrates the network model functionality:
- Creating nodes and edges
- Network connectivity
- Shortest path algorithms
- Network serialization

**Usage:**
```bash
python examples/simple_network_demo.py
```

## When to Use Each Demo

- **agent_demo.py**: Learn about agent features and see detailed step-by-step simulation
- **agent_demo_random.py**: Run experiments with many ships, test scenarios, generate metrics
- **simple_network_demo.py**: Understand the network model and routing algorithms

## Output Metrics

All agent demos provide:
- Total travel time
- Total system time
- Average times per ship
- Ship configuration by automation level
- Individual ship details (route, distance, time, etc.)

## Network Structure

All demos use a Rhine River port network with 6 ports:
- Rotterdam
- Dordrecht
- Nijmegen
- Duisburg
- Cologne
- Mannheim

Connected by shipping routes with realistic distances in kilometers.
