# Models Module

This module contains core models for the ABM simulation framework.

## Available Models

### Network Model (`network.py`)

A simple, lightweight network structure for agent-based modeling.

**Classes:**
- `Node`: Represents a network node with ID, name, type, and properties
- `Edge`: Represents a directed edge between nodes with weight and properties
- `Network`: Main network class with graph operations

**Key Features:**
- Directed and undirected network support
- Shortest path finding (weighted)
- All paths enumeration
- Network connectivity checks
- Subgraph extraction
- Dictionary serialization/deserialization

**Example Usage:**
```python
from src.models.network import Network, Node, Edge

# Create network
network = Network(directed=True)

# Add nodes
network.add_node(Node(id="A", name="Port A", node_type="port"))
network.add_node(Node(id="B", name="Port B", node_type="port"))

# Add edge
network.add_edge(Edge(source="A", target="B", weight=10.0))

# Find shortest path
path, length = network.get_shortest_path("A", "B")
```

See [examples/simple_network_demo.py](../../examples/simple_network_demo.py) for complete examples.

### Diffusion Model (`diffusion.py`)

Bass diffusion model for technology adoption analysis.

**Classes:**
- `BassDiffusionModel`: Classic Bass diffusion for single technology
- `MultiLevelAutomationDiffusion`: Multi-level adoption model (L0-L5)

**Key Features:**
- Innovation and imitation coefficients
- Market potential constraints
- Fleet size constraints
- History tracking

**Example Usage:**
```python
from src.models.diffusion import MultiLevelAutomationDiffusion

# Create diffusion model
diffusion = MultiLevelAutomationDiffusion(
    total_fleet=1000,
    initial_L1=50,
    M1=400, M2=300, M3=200,
    p1=0.02, q1=0.38,
    p2=0.01, q2=0.40,
    # ... other parameters
)

# Run simulation
for _ in range(50):
    diffusion.step()

# Access results
print(f"L1 adoption: {diffusion.history_L1[-1]}")
```

See [visualizations/show_diffusion.py](../../visualizations/show_diffusion.py) for visualization examples.

## Testing

Run tests for all models:
```bash
python -m pytest tests/unit/ -v
```

Run specific model tests:
```bash
python -m pytest tests/unit/test_network.py -v
python -m pytest tests/unit/test_diffusion.py -v
```

## Version History

See [CHANGELOG.md](../../CHANGELOG.md) for version history and updates.
