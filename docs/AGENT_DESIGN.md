# Agent Model Design Philosophy

## Abstract Agent-Based Modeling

The Agent model in this framework is intentionally **abstract and domain-agnostic**. It provides core navigation and state management capabilities while remaining flexible enough to represent any mobile entity in agent-based simulations.

---

## Design Principles

### 1. **Minimal Core Attributes**

The Agent class includes only essential attributes needed for network navigation:

```python
@dataclass
class Agent:
    agent_id: str              # Unique identifier
    agent_type: str            # Category/type
    current_node: str          # Current location
    origin: str                # Starting point
    destination: Optional[str] # Target (if any)
    route: List[str]           # Planned path
    state: AgentState          # Operational state
    properties: Dict[str, Any] # Domain-specific data

    # Journey tracking
    journey_distance: float
    journey_time: float
    route_index: int
```

### 2. **Domain-Agnostic**

The agent does **NOT** include domain-specific attributes like:
- ❌ `cargo_type`
- ❌ `capacity`
- ❌ `speed`
- ❌ `fuel_level`
- ❌ `load_weight`

Instead, these are stored in the `properties` dictionary.

### 3. **Properties Dictionary Pattern**

All domain-specific attributes use the flexible `properties` dictionary:

```python
# Maritime shipping example
vessel = create_agent(
    "vessel",
    "Rotterdam",
    "Rotterdam",
    capacity=2500,           # → properties["capacity"]
    cargo_type="container",  # → properties["cargo_type"]
    speed=14.0               # → properties["speed"]
)

# Urban traffic example
vehicle = create_agent(
    "car",
    "intersection_1",
    "intersection_1",
    max_speed=50,            # → properties["max_speed"]
    fuel_type="electric",    # → properties["fuel_type"]
    battery=85.0             # → properties["battery"]
)

# Pedestrian simulation example
person = create_agent(
    "pedestrian",
    "station_A",
    "station_A",
    walking_speed=5.0,       # → properties["walking_speed"]
    destination_purpose="work" # → properties["destination_purpose"]
)

# Robot warehouse example
robot = create_agent(
    "forklift",
    "dock_1",
    "dock_1",
    max_load=500,            # → properties["max_load"]
    battery_level=100.0,     # → properties["battery_level"]
    autonomy_level=3         # → properties["autonomy_level"]
)
```

---

## Usage Patterns

### Creating Domain-Specific Agents

#### Option 1: Direct Property Access

```python
from src.models.agent import create_agent

# Create agent
agent = create_agent("vessel", "A", "A")

# Set properties after creation
agent.set_property("capacity", 1000)
agent.set_property("cargo_type", "bulk")
agent.set_property("speed", 15.0)

# Get properties
capacity = agent.get_property("capacity")
speed = agent.get_property("speed", default=14.0)  # with default
```

#### Option 2: Factory Function with Keywords

```python
# Create agent with properties in one call
agent = create_agent(
    "vessel",
    "Rotterdam",
    "Rotterdam",
    capacity=1000,
    cargo_type="bulk",
    speed=15.0,
    flag_state="NL"
)

# All keyword arguments go into properties dict
assert agent.properties["capacity"] == 1000
assert agent.get_property("cargo_type") == "bulk"
```

#### Option 3: Custom Subclass (Advanced)

For complex domain models, you can subclass Agent:

```python
from src.models.agent import Agent, AgentState
from dataclasses import dataclass

@dataclass
class Vessel(Agent):
    """Domain-specific vessel agent."""

    def __post_init__(self):
        super().__post_init__()
        # Validate vessel-specific properties
        if "capacity" not in self.properties:
            raise ValueError("Vessels must have capacity")

    @property
    def capacity(self) -> float:
        """Convenience accessor for capacity."""
        return self.properties.get("capacity", 0.0)

    @capacity.setter
    def capacity(self, value: float):
        """Convenience setter for capacity."""
        self.properties["capacity"] = value

    def load_cargo(self, amount: float):
        """Domain-specific method."""
        current_load = self.get_property("current_load", 0.0)
        if current_load + amount > self.capacity:
            raise ValueError("Exceeds capacity")
        self.set_property("current_load", current_load + amount)
```

---

## Core Agent Capabilities

### Navigation

Agents can navigate through networks:

```python
# Set destination and plan route
agent.set_destination("Basel", network)

# Check next node
next_node = agent.next_node

# Advance along route
agent.advance_to_next_node(distance=50.0, time=3.5)

# Check if arrived
if agent.is_at_destination:
    print(f"Agent reached {agent.destination}")
```

### State Management

Agents maintain operational state:

```python
# States: IDLE, TRAVELING, AT_DESTINATION, STOPPED
print(agent.state)  # AgentState.IDLE

# Set destination → becomes TRAVELING
agent.set_destination("B", network)

# Control states
agent.stop()    # → STOPPED
agent.resume()  # → TRAVELING (or AT_DESTINATION if at dest)
```

### Journey Tracking

Agents automatically track their journey:

```python
# Distance and time accumulate
print(agent.journey_distance)  # km traveled
print(agent.journey_time)      # hours elapsed

# Route progress
print(agent.route_index)       # current position in route
print(agent.remaining_route)   # nodes left to visit

# Reset for new journey
agent.reset_journey()
```

### Serialization

Agents can be saved and loaded:

```python
# Export to dictionary
data = agent.to_dict()

# Save to JSON/database/etc
import json
json.dump(data, file)

# Recreate agent
loaded_agent = Agent.from_dict(data)
```

---

## Why This Design?

### ✅ Advantages

1. **Flexibility**: Same agent model for any domain
2. **Extensibility**: Add new properties without changing code
3. **Simplicity**: Minimal core, easy to understand
4. **Reusability**: Use across different projects
5. **Serialization**: Easy to save/load with dynamic properties

### ❌ Trade-offs

1. **No Type Safety**: Properties are untyped (can use TypedDict if needed)
2. **Runtime Validation**: Property validation happens at runtime
3. **No IDE Autocomplete**: IDE can't suggest property names

### When to Subclass

Consider subclassing Agent when:
- You need type safety for domain properties
- You have complex domain-specific methods
- You want IDE autocomplete for attributes
- You need validation logic

For simple cases, use the properties dictionary directly.

---

## Example: Maritime Shipping

Here's a complete example for maritime vessel simulation:

```python
from src.models.network import Network, Node, Edge
from src.models.agent import create_agent, reset_agent_id_counter

# Create Rhine river network
network = Network()
network.add_node(Node(id="Rotterdam", name="Rotterdam Port"))
network.add_node(Node(id="Duisburg", name="Duisburg Port"))
network.add_edge(Edge("Rotterdam", "Duisburg", weight=230.0))

# Create vessel agents with shipping-specific properties
reset_agent_id_counter()

container_ship = create_agent(
    "vessel",
    "Rotterdam",
    "Rotterdam",
    capacity=2500,
    cargo_type="container",
    speed=14.0,
    flag_state="NL",
    imo_number="IMO1234567"
)

bulk_carrier = create_agent(
    "vessel",
    "Rotterdam",
    "Rotterdam",
    capacity=3500,
    cargo_type="bulk",
    speed=12.0,
    flag_state="DE",
    draft=8.5  # meters
)

# Set destinations
container_ship.set_destination("Duisburg", network)
bulk_carrier.set_destination("Duisburg", network)

# Simulate movement
for vessel in [container_ship, bulk_carrier]:
    if vessel.next_node:
        # Get vessel-specific speed
        speed = vessel.get_property("speed", 14.0)
        distance = 230.0  # km
        time = distance / speed

        vessel.advance_to_next_node(distance, time)

        print(f"{vessel.agent_id}:")
        print(f"  Type: {vessel.get_property('cargo_type')}")
        print(f"  Position: {vessel.current_node}")
        print(f"  Journey: {vessel.journey_distance:.0f} km "
              f"in {vessel.journey_time:.1f} hours")
```

---

## Example: Urban Traffic

Same agent model for different domain:

```python
from src.models.network import Network, Node, Edge
from src.models.agent import create_agent

# Create road network
network = Network()
network.add_node(Node(id="int_1", name="Main & 1st"))
network.add_node(Node(id="int_2", name="Main & 2nd"))
network.add_edge(Edge("int_1", "int_2", weight=0.5))  # 500m

# Create vehicles with traffic-specific properties
car = create_agent(
    "car",
    "int_1",
    "int_1",
    max_speed=50,      # km/h
    fuel_type="petrol",
    passengers=2,
    license_plate="ABC-123"
)

bus = create_agent(
    "bus",
    "int_1",
    "int_1",
    max_speed=40,
    capacity=80,
    current_passengers=35,
    route_number="15"
)

# Same navigation methods work
car.set_destination("int_2", network)
bus.set_destination("int_2", network)
```

---

## Best Practices

### 1. Document Your Properties

Create a constant or enum for property names:

```python
# At module level
class VesselProperties:
    """Standard property names for vessel agents."""
    CAPACITY = "capacity"
    CARGO_TYPE = "cargo_type"
    SPEED = "speed"
    FLAG_STATE = "flag_state"
    IMO_NUMBER = "imo_number"

# Use in code
vessel.set_property(VesselProperties.CAPACITY, 2500)
```

### 2. Provide Defaults

Always use defaults when getting properties:

```python
# Good: provides fallback
speed = agent.get_property("speed", default=14.0)

# Bad: could fail if property not set
speed = agent.properties["speed"]  # KeyError if not set
```

### 3. Validate Early

Validate domain properties right after creation:

```python
def create_vessel(origin: str, **props) -> Agent:
    """Create and validate vessel agent."""
    vessel = create_agent("vessel", origin, origin, **props)

    # Validate required properties
    if vessel.get_property("capacity") is None:
        raise ValueError("Vessels must have capacity")
    if vessel.get_property("capacity") <= 0:
        raise ValueError("Capacity must be positive")

    return vessel
```

### 4. Use Type Hints in Wrappers

Create typed wrapper functions:

```python
from typing import Optional

def create_vessel(
    origin: str,
    capacity: float,
    cargo_type: str,
    speed: float = 14.0,
    agent_id: Optional[str] = None
) -> Agent:
    """
    Create a vessel agent with type-safe properties.

    Args:
        origin: Starting port
        capacity: Cargo capacity in tonnes
        cargo_type: Type of cargo (container, bulk, tanker)
        speed: Average speed in km/h
        agent_id: Optional custom ID

    Returns:
        Agent configured as vessel
    """
    return create_agent(
        "vessel",
        origin,
        origin,
        agent_id=agent_id,
        capacity=capacity,
        cargo_type=cargo_type,
        speed=speed
    )
```

---

## Comparison with Alternative Designs

### Alternative 1: Explicit Subclassing

```python
# More rigid, domain-specific
class Vessel(Agent):
    capacity: float
    cargo_type: str
    speed: float

# ❌ Can't reuse for other domains
# ✅ Type-safe
# ❌ Requires code changes for new attributes
```

### Alternative 2: Component System

```python
# Entity-Component-System pattern
agent = Agent(...)
agent.add_component(CapacityComponent(2500))
agent.add_component(SpeedComponent(14.0))

# ✅ Very flexible
# ❌ More complex
# ❌ Overkill for simple ABM
```

### Our Approach: Properties Dictionary

```python
agent = create_agent("vessel", "A", "A",
                    capacity=2500, speed=14.0)

# ✅ Simple and flexible
# ✅ No code changes needed
# ❌ No compile-time type checking
# ✅ Easy serialization
```

---

## Summary

The Agent model is designed to be:

- **Abstract**: No domain-specific assumptions
- **Flexible**: Properties dictionary for any attribute
- **Reusable**: Works across different ABM applications
- **Simple**: Minimal core, easy to understand
- **Extensible**: Subclass if needed, use as-is if not

This design makes the framework suitable for any agent-based modeling application where entities navigate through networks, not just maritime shipping.

---

*Last Updated: 2024-11-26 (v0.3.0)*
