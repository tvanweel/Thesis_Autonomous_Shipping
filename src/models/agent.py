"""
Abstract Agent Model for Network-Based ABM

Defines generic agents that can navigate through networks, maintain state,
and track their journeys. The agent model is intentionally abstract and can
represent any mobile entity (vessels, vehicles, people, robots, etc.) in
agent-based simulations.

The model is domain-agnostic - all domain-specific properties (cargo, capacity,
speed, etc.) should be stored in the `properties` dictionary rather than as
explicit attributes.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from src.models.network import Network


class AgentState(Enum):
    """Agent operational states."""
    IDLE = "idle"
    TRAVELING = "traveling"
    AT_DESTINATION = "at_destination"
    STOPPED = "stopped"


@dataclass
class Agent:
    """
    Generic agent for network-based simulations.

    This is an abstract agent model that can represent any mobile entity
    in an agent-based simulation. The agent navigates through a network,
    maintains its state, and tracks journey metrics.

    The model is intentionally minimal and domain-agnostic. All domain-specific
    attributes (cargo capacity, speed, fuel, etc.) should be stored in the
    `properties` dictionary.

    Attributes:
        agent_id: Unique identifier for the agent
        agent_type: Type/category (e.g., "vessel", "vehicle", "person", "robot")
        current_node: Current node ID in the network
        origin: Starting node ID
        destination: Target node ID (optional, None if no destination set)
        route: Planned route as list of node IDs
        state: Current operational state (IDLE, TRAVELING, AT_DESTINATION, STOPPED)
        properties: Dictionary for domain-specific properties (capacity, speed, etc.)
        journey_distance: Cumulative distance traveled
        journey_time: Cumulative time elapsed
        route_index: Current position in route (0 = at origin)

    Example:
        >>> # Create a generic agent
        >>> agent = Agent(
        ...     agent_id="agent_1",
        ...     agent_type="vehicle",
        ...     current_node="A",
        ...     origin="A"
        ... )
        >>>
        >>> # Add domain-specific properties
        >>> agent.set_property("speed", 50)  # km/h
        >>> agent.set_property("capacity", 100)  # units
        >>> agent.set_property("fuel", 80.0)  # liters
    """
    agent_id: str
    agent_type: str
    current_node: str
    origin: str
    destination: Optional[str] = None
    route: List[str] = field(default_factory=list)
    state: AgentState = AgentState.IDLE
    properties: Dict[str, Any] = field(default_factory=dict)

    # Journey tracking
    journey_distance: float = 0.0
    journey_time: float = 0.0
    route_index: int = 0

    def __post_init__(self):
        """Initialize route if not provided."""
        if not self.route:
            self.route = [self.current_node]
        elif self.route and self.route[0] != self.current_node:
            # Only insert if current_node not already at start
            if self.current_node not in self.route or self.route[0] != self.current_node:
                pass  # Don't auto-insert, respect provided route

    def set_destination(self, destination: str, network: Network) -> None:
        """
        Set a destination and plan route through network.

        Args:
            destination: Target node ID
            network: Network to navigate

        Raises:
            ValueError: If no path exists to destination
        """
        self.destination = destination

        # Plan route using shortest path
        try:
            path, distance = network.get_shortest_path(
                self.current_node,
                destination
            )
            self.route = path
            self.route_index = 0
            self.state = AgentState.TRAVELING
        except ValueError as e:
            raise ValueError(f"Cannot plan route for agent {self.agent_id}: {e}")

    @property
    def next_node(self) -> Optional[str]:
        """Get the next node in the route."""
        if self.route_index + 1 < len(self.route):
            return self.route[self.route_index + 1]
        return None

    @property
    def is_at_destination(self) -> bool:
        """Check if agent has reached its destination."""
        return (
            self.destination is not None and
            self.current_node == self.destination and
            self.state == AgentState.AT_DESTINATION
        )

    @property
    def remaining_route(self) -> List[str]:
        """Get remaining nodes in route (including current)."""
        return self.route[self.route_index:]

    def advance_to_next_node(
        self,
        distance: float = 0.0,
        time: float = 0.0
    ) -> bool:
        """
        Move agent to the next node in its route.

        Args:
            distance: Distance traveled to next node
            time: Time taken to reach next node

        Returns:
            True if successfully moved, False if at end of route

        Raises:
            ValueError: If no next node available
        """
        if self.next_node is None:
            # Reached end of route
            if self.destination and self.current_node == self.destination:
                self.state = AgentState.AT_DESTINATION
            return False

        # Move to next node
        self.route_index += 1
        self.current_node = self.route[self.route_index]
        self.journey_distance += distance
        self.journey_time += time

        # Update state
        if self.current_node == self.destination:
            self.state = AgentState.AT_DESTINATION
        else:
            self.state = AgentState.TRAVELING

        return True

    def reset_journey(self) -> None:
        """Reset journey tracking to start fresh trip."""
        self.journey_distance = 0.0
        self.journey_time = 0.0
        self.route_index = 0
        self.current_node = self.origin
        self.route = [self.origin]
        self.destination = None
        self.state = AgentState.IDLE

    def stop(self) -> None:
        """Stop the agent at current location."""
        self.state = AgentState.STOPPED

    def resume(self) -> None:
        """Resume travel if agent was stopped."""
        if self.state == AgentState.STOPPED:
            if self.destination and self.current_node != self.destination:
                self.state = AgentState.TRAVELING
            elif self.destination and self.current_node == self.destination:
                self.state = AgentState.AT_DESTINATION
            else:
                self.state = AgentState.IDLE

    def get_property(self, key: str, default: Any = None) -> Any:
        """
        Get a custom property value.

        Args:
            key: Property key
            default: Default value if key not found

        Returns:
            Property value or default
        """
        return self.properties.get(key, default)

    def set_property(self, key: str, value: Any) -> None:
        """
        Set a custom property value.

        Args:
            key: Property key
            value: Property value
        """
        self.properties[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Export agent to dictionary format.

        Returns:
            Dictionary representation of agent
        """
        return {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type,
            'current_node': self.current_node,
            'origin': self.origin,
            'destination': self.destination,
            'route': self.route,
            'state': self.state.value,
            'properties': self.properties,
            'journey_distance': self.journey_distance,
            'journey_time': self.journey_time,
            'route_index': self.route_index
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """
        Create agent from dictionary format.

        Args:
            data: Dictionary representation

        Returns:
            Agent instance
        """
        state = AgentState(data.get('state', 'idle'))

        return cls(
            agent_id=data['agent_id'],
            agent_type=data['agent_type'],
            current_node=data['current_node'],
            origin=data['origin'],
            destination=data.get('destination'),
            route=data.get('route', []),
            state=state,
            properties=data.get('properties', {}),
            journey_distance=data.get('journey_distance', 0.0),
            journey_time=data.get('journey_time', 0.0),
            route_index=data.get('route_index', 0)
        )

    def __repr__(self) -> str:
        """String representation of agent."""
        dest_str = f" -> {self.destination}" if self.destination else ""
        return (f"Agent(id='{self.agent_id}', type='{self.agent_type}', "
                f"at='{self.current_node}'{dest_str}, state={self.state.value})")


# Global counter for automatic agent ID generation
_agent_id_counter = 0


def create_agent(
    agent_type: str,
    current_node: str,
    origin: str,
    agent_id: Optional[str] = None,
    **properties
) -> Agent:
    """
    Factory function to create agents with automatic ID generation.

    Creates a generic agent and populates its properties dictionary with
    any keyword arguments. This allows for flexible, domain-specific agent
    creation without modifying the base Agent class.

    Args:
        agent_type: Type of agent (e.g., "vessel", "vehicle", "person")
        current_node: Current location in network
        origin: Origin node ID
        agent_id: Optional custom ID (auto-generated as "type_N" if None)
        **properties: Domain-specific properties stored in agent.properties

    Returns:
        Agent instance with populated properties

    Example:
        >>> # Create agent with domain-specific properties
        >>> vessel = create_agent(
        ...     "vessel",
        ...     "Rotterdam",
        ...     "Rotterdam",
        ...     capacity=2500,
        ...     cargo_type="container",
        ...     speed=14.0
        ... )
        >>> vessel.get_property("capacity")  # 2500
        >>>
        >>> # Create minimal agent
        >>> agent = create_agent("robot", "A", "A")
        >>> agent.agent_id  # "robot_0"
    """
    global _agent_id_counter

    if agent_id is None:
        agent_id = f"{agent_type}_{_agent_id_counter}"
        _agent_id_counter += 1

    return Agent(
        agent_id=agent_id,
        agent_type=agent_type,
        current_node=current_node,
        origin=origin,
        properties=properties
    )


def reset_agent_id_counter() -> None:
    """Reset the global agent ID counter (useful for testing)."""
    global _agent_id_counter
    _agent_id_counter = 0
