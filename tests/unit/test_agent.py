"""
Unit tests for the Agent model.
"""

import pytest
from src.models.agent import (
    Agent,
    AgentState,
    create_agent,
    reset_agent_id_counter
)
from src.models.network import Network, Node, Edge


class TestAgentState:
    """Tests for AgentState enum."""

    def test_agent_states(self):
        """Test all agent states are available."""
        assert AgentState.IDLE.value == "idle"
        assert AgentState.TRAVELING.value == "traveling"
        assert AgentState.AT_DESTINATION.value == "at_destination"
        assert AgentState.STOPPED.value == "stopped"


class TestAgent:
    """Tests for the Agent class."""

    @pytest.fixture
    def sample_network(self):
        """Create a sample network for testing."""
        network = Network()

        # Add nodes
        network.add_node(Node(id="A", name="Node A"))
        network.add_node(Node(id="B", name="Node B"))
        network.add_node(Node(id="C", name="Node C"))
        network.add_node(Node(id="D", name="Node D"))

        # Add edges
        network.add_edge(Edge(source="A", target="B", weight=10.0))
        network.add_edge(Edge(source="B", target="C", weight=15.0))
        network.add_edge(Edge(source="A", target="C", weight=30.0))
        network.add_edge(Edge(source="C", target="D", weight=5.0))

        return network

    def test_agent_creation(self):
        """Test basic agent creation."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="A",
            origin="A"
        )

        assert agent.agent_id == "agent1"
        assert agent.agent_type == "vessel"
        assert agent.current_node == "A"
        assert agent.origin == "A"
        assert agent.state == AgentState.IDLE
        assert agent.destination is None

    def test_agent_with_properties(self):
        """Test agent creation with custom properties."""
        props = {"capacity": 1000, "speed": 20}
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="A",
            origin="A",
            properties=props
        )

        assert agent.properties["capacity"] == 1000
        assert agent.properties["speed"] == 20

    def test_agent_route_initialization(self):
        """Test that route is initialized with current node."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="A",
            origin="A"
        )

        assert agent.route == ["A"]
        assert agent.route_index == 0

    def test_set_destination(self, sample_network):
        """Test setting destination and planning route."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="A",
            origin="A"
        )

        agent.set_destination("C", sample_network)

        assert agent.destination == "C"
        assert agent.route == ["A", "B", "C"]  # Shortest path
        assert agent.state == AgentState.TRAVELING

    def test_set_destination_no_path_raises_error(self):
        """Test that setting unreachable destination raises error."""
        network = Network()
        network.add_node(Node(id="A", name="Node A"))
        network.add_node(Node(id="B", name="Node B"))
        # No edge between them

        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="A",
            origin="A"
        )

        with pytest.raises(ValueError, match="Cannot plan route"):
            agent.set_destination("B", network)

    def test_next_node_property(self, sample_network):
        """Test next_node property."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="A",
            origin="A"
        )

        agent.set_destination("C", sample_network)

        assert agent.next_node == "B"  # Next in route A -> B -> C

    def test_next_node_at_end_of_route(self):
        """Test next_node returns None at end of route."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="C",
            origin="A",
            route=["A", "B", "C"]
        )
        agent.route_index = 2  # At end

        assert agent.next_node is None

    def test_is_at_destination(self):
        """Test is_at_destination property."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="C",
            origin="A",
            destination="C",
            state=AgentState.AT_DESTINATION
        )

        assert agent.is_at_destination is True

    def test_is_at_destination_false_when_not_at_dest(self):
        """Test is_at_destination is False when traveling."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="B",
            origin="A",
            destination="C",
            state=AgentState.TRAVELING
        )

        assert agent.is_at_destination is False

    def test_remaining_route(self, sample_network):
        """Test remaining_route property."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="A",
            origin="A"
        )

        agent.set_destination("C", sample_network)
        # Route: A -> B -> C

        assert agent.remaining_route == ["A", "B", "C"]

        # After advancing
        agent.advance_to_next_node(10.0, 1.0)
        assert agent.remaining_route == ["B", "C"]

    def test_advance_to_next_node(self, sample_network):
        """Test advancing agent to next node."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="A",
            origin="A"
        )

        agent.set_destination("C", sample_network)
        # Route: A -> B -> C

        # Advance to B
        result = agent.advance_to_next_node(distance=10.0, time=1.0)

        assert result is True
        assert agent.current_node == "B"
        assert agent.route_index == 1
        assert agent.journey_distance == 10.0
        assert agent.journey_time == 1.0
        assert agent.state == AgentState.TRAVELING

    def test_advance_to_destination(self, sample_network):
        """Test advancing agent to final destination."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="B",
            origin="A",
            destination="C",
            route=["A", "B", "C"]
        )
        agent.route_index = 1  # At B

        # Advance to C (destination)
        result = agent.advance_to_next_node(distance=15.0, time=1.5)

        assert result is True
        assert agent.current_node == "C"
        assert agent.state == AgentState.AT_DESTINATION

    def test_advance_at_end_of_route(self):
        """Test advancing when already at end returns False."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="C",
            origin="A",
            destination="C",
            route=["A", "B", "C"]
        )
        agent.route_index = 2  # At end

        result = agent.advance_to_next_node()

        assert result is False
        assert agent.state == AgentState.AT_DESTINATION

    def test_journey_tracking(self, sample_network):
        """Test that journey distance and time are tracked."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="A",
            origin="A"
        )

        agent.set_destination("C", sample_network)

        # Move A -> B
        agent.advance_to_next_node(distance=10.0, time=1.0)
        assert agent.journey_distance == 10.0
        assert agent.journey_time == 1.0

        # Move B -> C
        agent.advance_to_next_node(distance=15.0, time=1.5)
        assert agent.journey_distance == 25.0
        assert agent.journey_time == 2.5

    def test_reset_journey(self, sample_network):
        """Test resetting journey tracking."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="C",
            origin="A",
            destination="C"
        )
        agent.journey_distance = 25.0
        agent.journey_time = 2.5
        agent.route_index = 2

        agent.reset_journey()

        assert agent.current_node == "A"
        assert agent.journey_distance == 0.0
        assert agent.journey_time == 0.0
        assert agent.route_index == 0
        assert agent.destination is None
        assert agent.state == AgentState.IDLE

    def test_stop_agent(self):
        """Test stopping agent."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="B",
            origin="A",
            state=AgentState.TRAVELING
        )

        agent.stop()
        assert agent.state == AgentState.STOPPED

    def test_resume_agent_while_traveling(self):
        """Test resuming agent that was traveling."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="B",
            origin="A",
            destination="C",
            state=AgentState.STOPPED
        )

        agent.resume()
        assert agent.state == AgentState.TRAVELING

    def test_resume_agent_at_destination(self):
        """Test resuming agent already at destination."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="C",
            origin="A",
            destination="C",
            state=AgentState.STOPPED
        )

        agent.resume()
        assert agent.state == AgentState.AT_DESTINATION

    def test_resume_agent_without_destination(self):
        """Test resuming agent without destination."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="A",
            origin="A",
            state=AgentState.STOPPED
        )

        agent.resume()
        assert agent.state == AgentState.IDLE

    def test_get_property(self):
        """Test getting agent property."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="A",
            origin="A",
            properties={"capacity": 1000}
        )

        assert agent.get_property("capacity") == 1000
        assert agent.get_property("speed", default=20) == 20

    def test_set_property(self):
        """Test setting agent property."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="A",
            origin="A"
        )

        agent.set_property("capacity", 1000)
        assert agent.properties["capacity"] == 1000

    def test_to_dict(self):
        """Test exporting agent to dictionary."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="B",
            origin="A",
            destination="C",
            route=["A", "B", "C"],
            state=AgentState.TRAVELING,
            properties={"capacity": 1000}
        )
        agent.journey_distance = 10.0
        agent.journey_time = 1.0
        agent.route_index = 1

        data = agent.to_dict()

        assert data["agent_id"] == "agent1"
        assert data["agent_type"] == "vessel"
        assert data["current_node"] == "B"
        assert data["origin"] == "A"
        assert data["destination"] == "C"
        assert data["route"] == ["A", "B", "C"]
        assert data["state"] == "traveling"
        assert data["properties"]["capacity"] == 1000
        assert data["journey_distance"] == 10.0
        assert data["journey_time"] == 1.0
        assert data["route_index"] == 1

    def test_from_dict(self):
        """Test creating agent from dictionary."""
        data = {
            "agent_id": "agent1",
            "agent_type": "vessel",
            "current_node": "B",
            "origin": "A",
            "destination": "C",
            "route": ["A", "B", "C"],
            "state": "traveling",
            "properties": {"capacity": 1000},
            "journey_distance": 10.0,
            "journey_time": 1.0,
            "route_index": 1
        }

        agent = Agent.from_dict(data)

        assert agent.agent_id == "agent1"
        assert agent.agent_type == "vessel"
        assert agent.current_node == "B"
        assert agent.origin == "A"
        assert agent.destination == "C"
        assert agent.route == ["A", "B", "C"]
        assert agent.state == AgentState.TRAVELING
        assert agent.properties["capacity"] == 1000
        assert agent.journey_distance == 10.0
        assert agent.journey_time == 1.0
        assert agent.route_index == 1

    def test_round_trip_dict_conversion(self):
        """Test that agent can be exported and imported without data loss."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="B",
            origin="A",
            destination="C",
            properties={"capacity": 1000}
        )
        agent.journey_distance = 10.0

        data = agent.to_dict()
        reconstructed = Agent.from_dict(data)

        assert reconstructed.agent_id == agent.agent_id
        assert reconstructed.current_node == agent.current_node
        assert reconstructed.journey_distance == agent.journey_distance

    def test_agent_repr(self):
        """Test agent string representation."""
        agent = Agent(
            agent_id="agent1",
            agent_type="vessel",
            current_node="B",
            origin="A",
            destination="C",
            state=AgentState.TRAVELING
        )

        repr_str = repr(agent)
        assert "agent1" in repr_str
        assert "vessel" in repr_str
        assert "B" in repr_str
        assert "C" in repr_str
        assert "traveling" in repr_str


class TestCreateAgent:
    """Tests for the create_agent factory function."""

    def test_create_agent_with_auto_id(self):
        """Test creating agent with automatic ID generation."""
        reset_agent_id_counter()

        agent1 = create_agent("vessel", "A", "A")
        agent2 = create_agent("vessel", "B", "B")

        assert agent1.agent_id == "vessel_0"
        assert agent2.agent_id == "vessel_1"

    def test_create_agent_with_custom_id(self):
        """Test creating agent with custom ID."""
        agent = create_agent("vessel", "A", "A", agent_id="custom_id")
        assert agent.agent_id == "custom_id"

    def test_create_agent_with_properties(self):
        """Test creating agent with properties."""
        agent = create_agent(
            "vessel",
            "A",
            "A",
            capacity=1000,
            speed=20
        )

        assert agent.properties["capacity"] == 1000
        assert agent.properties["speed"] == 20

    def test_reset_agent_id_counter(self):
        """Test resetting the agent ID counter."""
        reset_agent_id_counter()
        agent1 = create_agent("vessel", "A", "A")
        assert agent1.agent_id == "vessel_0"

        reset_agent_id_counter()
        agent2 = create_agent("vessel", "A", "A")
        assert agent2.agent_id == "vessel_0"  # Counter was reset


class TestAgentIntegration:
    """Integration tests with network."""

    @pytest.fixture
    def complex_network(self):
        """Create a more complex network."""
        network = Network()

        # Create a diamond network
        for node_id in ["A", "B", "C", "D", "E"]:
            network.add_node(Node(id=node_id, name=f"Node {node_id}"))

        network.add_edge(Edge(source="A", target="B", weight=5.0))
        network.add_edge(Edge(source="A", target="C", weight=10.0))
        network.add_edge(Edge(source="B", target="D", weight=5.0))
        network.add_edge(Edge(source="C", target="D", weight=5.0))
        network.add_edge(Edge(source="D", target="E", weight=5.0))

        return network

    def test_agent_complete_journey(self, complex_network):
        """Test agent completing a full journey."""
        agent = create_agent("vessel", "A", "A")
        agent.set_destination("E", complex_network)

        # Agent should take shortest path: A -> B -> D -> E
        assert agent.route == ["A", "B", "D", "E"]

        # Travel the route
        steps = 0
        while not agent.is_at_destination and steps < 10:
            agent.advance_to_next_node(distance=5.0, time=0.5)
            steps += 1

        assert agent.is_at_destination
        assert agent.current_node == "E"
        assert agent.journey_distance == 15.0  # 5+5+5
        assert agent.journey_time == 1.5  # 0.5+0.5+0.5

    def test_multiple_agents_on_network(self, complex_network):
        """Test multiple agents traveling simultaneously."""
        reset_agent_id_counter()

        agent1 = create_agent("vessel", "A", "A")
        agent2 = create_agent("vessel", "C", "C")

        agent1.set_destination("E", complex_network)
        agent2.set_destination("E", complex_network)

        # Both agents should have valid routes
        assert len(agent1.route) > 0
        assert len(agent2.route) > 0

        # Different starting points
        assert agent1.current_node == "A"
        assert agent2.current_node == "C"
