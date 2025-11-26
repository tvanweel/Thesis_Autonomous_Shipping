"""
Unit tests for traffic behavior module.

Tests:
- EdgeTraffic: vessel tracking, density calculation, speed reduction
- CrossroadState: occupation, waiting queue, availability
- TrafficManager: initialization, vessel tracking, crossroad management
"""

import pytest
from src.models.traffic import (
    EdgeTraffic,
    CrossroadState,
    TrafficManager,
    VESSELS_PER_KM_CAPACITY,
    CONGESTION_IMPACT_FACTOR,
    CROSSROAD_TRANSIT_TIME,
    MIN_SPEED_RATIO
)
from src.models.network import Network, Node, Edge


class TestEdgeTraffic:
    """Tests for EdgeTraffic class."""

    def test_edge_creation(self):
        """Test EdgeTraffic initialization."""
        edge = EdgeTraffic(
            edge_id="A->B",
            distance_km=100.0,
            capacity=1200
        )
        assert edge.edge_id == "A->B"
        assert edge.distance_km == 100.0
        assert edge.capacity == 1200
        assert edge.vessel_count == 0
        assert len(edge.vessels) == 0

    def test_vessel_tracking(self):
        """Test adding and removing vessels from edge."""
        edge = EdgeTraffic("A->B", 100.0, 1200)

        # Add vessels
        edge.vessels.add("vessel_1")
        assert edge.vessel_count == 1

        edge.vessels.add("vessel_2")
        edge.vessels.add("vessel_3")
        assert edge.vessel_count == 3

        # Remove vessel
        edge.vessels.discard("vessel_1")
        assert edge.vessel_count == 2

        # Remove non-existent vessel (should not error)
        edge.vessels.discard("vessel_99")
        assert edge.vessel_count == 2

    def test_density_ratio(self):
        """Test density ratio calculation."""
        edge = EdgeTraffic("A->B", 100.0, 100)

        # Empty edge
        assert edge.density_ratio == 0.0

        # Half capacity
        for i in range(50):
            edge.vessels.add(f"vessel_{i}")
        assert edge.density_ratio == 0.5

        # Full capacity
        for i in range(50, 100):
            edge.vessels.add(f"vessel_{i}")
        assert edge.density_ratio == 1.0

        # Over capacity
        edge.vessels.add("vessel_100")
        assert edge.density_ratio > 1.0

    def test_density_ratio_zero_capacity(self):
        """Test density ratio with zero capacity."""
        edge = EdgeTraffic("A->B", 0.0, 0)
        edge.vessels.add("vessel_1")
        assert edge.density_ratio == 0.0

    def test_is_congested(self):
        """Test congestion detection."""
        edge = EdgeTraffic("A->B", 100.0, 100)

        # Not congested at 70% capacity
        for i in range(70):
            edge.vessels.add(f"vessel_{i}")
        assert not edge.is_congested

        # Congested at 80% capacity
        for i in range(70, 80):
            edge.vessels.add(f"vessel_{i}")
        assert edge.is_congested

        # Congested at over capacity
        for i in range(80, 120):
            edge.vessels.add(f"vessel_{i}")
        assert edge.is_congested

    def test_effective_speed_no_congestion(self):
        """Test speed calculation with no congestion."""
        edge = EdgeTraffic("A->B", 100.0, 100)
        base_speed = 15.0

        # No vessels -> full speed
        effective_speed = edge.calculate_effective_speed(base_speed)
        assert effective_speed == base_speed

    def test_effective_speed_with_congestion(self):
        """Test speed reduction due to congestion."""
        edge = EdgeTraffic("A->B", 100.0, 100)
        base_speed = 15.0

        # 50% capacity -> 65% speed (1 - 0.7*0.5 = 0.65)
        for i in range(50):
            edge.vessels.add(f"vessel_{i}")
        effective_speed = edge.calculate_effective_speed(base_speed)
        expected_speed = base_speed * 0.65
        assert abs(effective_speed - expected_speed) < 0.01

        # 100% capacity -> 30% speed (minimum)
        for i in range(50, 100):
            edge.vessels.add(f"vessel_{i}")
        effective_speed = edge.calculate_effective_speed(base_speed)
        expected_speed = base_speed * MIN_SPEED_RATIO
        assert abs(effective_speed - expected_speed) < 0.01

    def test_effective_speed_over_capacity(self):
        """Test speed at over-capacity (should not go below minimum)."""
        edge = EdgeTraffic("A->B", 100.0, 100)
        base_speed = 15.0

        # 150% capacity -> still 30% speed (minimum enforced)
        for i in range(150):
            edge.vessels.add(f"vessel_{i}")
        effective_speed = edge.calculate_effective_speed(base_speed)
        expected_speed = base_speed * MIN_SPEED_RATIO
        assert abs(effective_speed - expected_speed) < 0.01

        # Speed should never be less than 30% of base
        assert effective_speed >= base_speed * MIN_SPEED_RATIO


class TestCrossroadState:
    """Tests for CrossroadState class."""

    def test_crossroad_creation(self):
        """Test CrossroadState initialization."""
        crossroad = CrossroadState(node_id="NodeA")
        assert crossroad.node_id == "NodeA"
        assert crossroad.occupied_by is None
        assert crossroad.occupation_end_time == 0.0
        assert len(crossroad.waiting_queue) == 0

    def test_is_available_empty(self):
        """Test availability when crossroad is empty."""
        crossroad = CrossroadState("NodeA")
        assert crossroad.is_available(0.0)
        assert crossroad.is_available(10.0)

    def test_occupy_crossroad(self):
        """Test occupying a crossroad."""
        crossroad = CrossroadState("NodeA")
        current_time = 5.0

        end_time = crossroad.occupy("vessel_1", current_time)

        assert crossroad.occupied_by == "vessel_1"
        assert crossroad.occupation_end_time == current_time + CROSSROAD_TRANSIT_TIME
        assert end_time == current_time + CROSSROAD_TRANSIT_TIME

    def test_is_available_occupied(self):
        """Test availability when crossroad is occupied."""
        crossroad = CrossroadState("NodeA")
        crossroad.occupy("vessel_1", 5.0)

        # Not available before occupation ends
        assert not crossroad.is_available(5.0)
        assert not crossroad.is_available(5.2)

        # Available after occupation ends
        assert crossroad.is_available(5.5)
        assert crossroad.is_available(6.0)

    def test_release_crossroad(self):
        """Test releasing a crossroad."""
        crossroad = CrossroadState("NodeA")
        crossroad.occupy("vessel_1", 5.0)

        crossroad.release()

        assert crossroad.occupied_by is None
        assert crossroad.occupation_end_time == 0.0
        assert crossroad.is_available(5.0)

    def test_waiting_queue(self):
        """Test waiting queue management."""
        crossroad = CrossroadState("NodeA")

        # Add to queue
        crossroad.add_to_queue("vessel_1", 5.0)
        crossroad.add_to_queue("vessel_2", 5.5)

        assert len(crossroad.waiting_queue) == 2
        assert crossroad.waiting_queue[0] == ("vessel_1", 5.0)
        assert crossroad.waiting_queue[1] == ("vessel_2", 5.5)

        # Remove from queue
        crossroad.remove_from_queue("vessel_1")
        assert len(crossroad.waiting_queue) == 1
        assert crossroad.waiting_queue[0] == ("vessel_2", 5.5)

    def test_get_wait_time(self):
        """Test wait time calculation."""
        crossroad = CrossroadState("NodeA")

        # No wait if available
        assert crossroad.get_wait_time(5.0) == 0.0

        # Wait time if occupied
        crossroad.occupy("vessel_1", 5.0)
        assert crossroad.get_wait_time(5.0) == CROSSROAD_TRANSIT_TIME
        assert abs(crossroad.get_wait_time(5.2) - 0.3) < 0.001

        # No wait after occupation ends
        assert crossroad.get_wait_time(5.5) == 0.0


class TestTrafficManager:
    """Tests for TrafficManager class."""

    @pytest.fixture
    def simple_network(self):
        """Create a simple test network."""
        network = Network(directed=True)

        # Add nodes
        network.add_node(Node("A", "Node A", "port"))
        network.add_node(Node("B", "Node B", "port"))
        network.add_node(Node("C", "Node C", "port"))
        network.add_node(Node("D", "Node D", "port"))

        # Add edges
        network.add_edge(Edge("A", "B", 100.0, properties={"distance_km": 100}))
        network.add_edge(Edge("B", "C", 50.0, properties={"distance_km": 50}))
        network.add_edge(Edge("C", "D", 75.0, properties={"distance_km": 75}))
        network.add_edge(Edge("B", "D", 120.0, properties={"distance_km": 120}))

        return network

    @pytest.fixture
    def crossroad_network(self):
        """Create a network with a crossroad."""
        network = Network(directed=True)

        # Add nodes
        network.add_node(Node("A", "Node A", "port"))
        network.add_node(Node("B", "Node B", "port"))  # This will be a crossroad
        network.add_node(Node("C", "Node C", "port"))
        network.add_node(Node("D", "Node D", "port"))

        # Add edges - B is a crossroad with 4 connections
        network.add_edge(Edge("A", "B", 100.0, properties={"distance_km": 100}))
        network.add_edge(Edge("B", "C", 50.0, properties={"distance_km": 50}))
        network.add_edge(Edge("B", "D", 75.0, properties={"distance_km": 75}))
        network.add_edge(Edge("C", "B", 50.0, properties={"distance_km": 50}))

        return network

    def test_initialization(self, simple_network):
        """Test TrafficManager initialization."""
        traffic_mgr = TrafficManager(simple_network)

        assert traffic_mgr.network == simple_network
        assert traffic_mgr.current_time == 0.0
        assert len(traffic_mgr.edge_traffic) == 4

        # Check edge traffic created correctly
        assert "A->B" in traffic_mgr.edge_traffic
        edge_ab = traffic_mgr.edge_traffic["A->B"]
        assert edge_ab.distance_km == 100.0
        assert edge_ab.capacity == 100 * VESSELS_PER_KM_CAPACITY

    def test_crossroad_identification(self, crossroad_network):
        """Test automatic crossroad identification."""
        traffic_mgr = TrafficManager(crossroad_network)

        # B should be identified as a crossroad (4 connections)
        assert "B" in traffic_mgr.crossroads

        # A, C, D should not be crossroads
        assert "A" not in traffic_mgr.crossroads
        assert "C" not in traffic_mgr.crossroads
        assert "D" not in traffic_mgr.crossroads

    def test_vessel_enter_exit_edge(self, simple_network):
        """Test vessel entering and exiting edges."""
        traffic_mgr = TrafficManager(simple_network)

        # Vessel enters edge
        traffic_mgr.vessel_enter_edge("vessel_1", "A", "B")
        edge = traffic_mgr.edge_traffic["A->B"]
        assert "vessel_1" in edge.vessels
        assert edge.vessel_count == 1

        # Another vessel enters
        traffic_mgr.vessel_enter_edge("vessel_2", "A", "B")
        assert edge.vessel_count == 2

        # Vessel exits edge
        traffic_mgr.vessel_exit_edge("vessel_1", "A", "B")
        assert "vessel_1" not in edge.vessels
        assert edge.vessel_count == 1

    def test_get_effective_speed(self, simple_network):
        """Test effective speed calculation through TrafficManager."""
        traffic_mgr = TrafficManager(simple_network)
        base_speed = 15.0

        # No congestion
        speed = traffic_mgr.get_effective_speed("vessel_1", base_speed, "A", "B")
        assert speed == base_speed

        # Add vessels to create congestion
        edge = traffic_mgr.edge_traffic["A->B"]
        capacity = edge.capacity

        # Fill to 50% capacity
        for i in range(capacity // 2):
            edge.vessels.add(f"vessel_{i}")

        speed = traffic_mgr.get_effective_speed("vessel_test", base_speed, "A", "B")
        expected = base_speed * 0.65  # 1 - 0.7 * 0.5
        assert abs(speed - expected) < 0.01

    def test_get_effective_speed_nonexistent_edge(self, simple_network):
        """Test effective speed for non-existent edge (should return base speed)."""
        traffic_mgr = TrafficManager(simple_network)
        base_speed = 15.0

        # Non-existent edge
        speed = traffic_mgr.get_effective_speed("vessel_1", base_speed, "X", "Y")
        assert speed == base_speed

    def test_check_crossroad_entry_no_crossroad(self, simple_network):
        """Test crossroad entry check for non-crossroad node."""
        traffic_mgr = TrafficManager(simple_network)

        # Node A is not a crossroad
        can_enter, wait_time = traffic_mgr.check_crossroad_entry("vessel_1", "A")
        assert can_enter is True
        assert wait_time == 0.0

    def test_check_crossroad_entry_available(self, crossroad_network):
        """Test crossroad entry check when crossroad is available."""
        traffic_mgr = TrafficManager(crossroad_network)

        # B is a crossroad and is available
        can_enter, wait_time = traffic_mgr.check_crossroad_entry("vessel_1", "B")
        assert can_enter is True
        assert wait_time == 0.0

    def test_check_crossroad_entry_occupied(self, crossroad_network):
        """Test crossroad entry check when crossroad is occupied."""
        traffic_mgr = TrafficManager(crossroad_network)
        traffic_mgr.update_time(5.0)

        # Occupy the crossroad
        traffic_mgr.occupy_crossroad("vessel_1", "B")

        # Another vessel tries to enter
        can_enter, wait_time = traffic_mgr.check_crossroad_entry("vessel_2", "B")
        assert can_enter is False
        assert wait_time == CROSSROAD_TRANSIT_TIME

    def test_occupy_and_release_crossroad(self, crossroad_network):
        """Test occupying and releasing a crossroad."""
        traffic_mgr = TrafficManager(crossroad_network)
        traffic_mgr.update_time(5.0)

        # Occupy crossroad
        end_time = traffic_mgr.occupy_crossroad("vessel_1", "B")
        assert end_time == 5.0 + CROSSROAD_TRANSIT_TIME

        crossroad = traffic_mgr.crossroads["B"]
        assert crossroad.occupied_by == "vessel_1"

        # Release crossroad
        traffic_mgr.release_crossroad("vessel_1", "B")
        assert crossroad.occupied_by is None

    def test_occupy_non_crossroad(self, simple_network):
        """Test occupying a non-crossroad node (should return current time)."""
        traffic_mgr = TrafficManager(simple_network)
        traffic_mgr.update_time(5.0)

        # A is not a crossroad
        end_time = traffic_mgr.occupy_crossroad("vessel_1", "A")
        assert end_time == 5.0  # Should return current time unchanged

    def test_update_time(self, simple_network):
        """Test updating simulation time."""
        traffic_mgr = TrafficManager(simple_network)

        assert traffic_mgr.current_time == 0.0

        traffic_mgr.update_time(10.5)
        assert traffic_mgr.current_time == 10.5

        traffic_mgr.update_time(15.0)
        assert traffic_mgr.current_time == 15.0

    def test_get_edge_stats(self, simple_network):
        """Test getting edge statistics."""
        traffic_mgr = TrafficManager(simple_network)

        # Add some vessels
        traffic_mgr.vessel_enter_edge("vessel_1", "A", "B")
        traffic_mgr.vessel_enter_edge("vessel_2", "A", "B")

        stats = traffic_mgr.get_edge_stats()

        assert "A->B" in stats
        ab_stats = stats["A->B"]
        assert ab_stats["vessels"] == 2
        assert ab_stats["capacity"] == 100 * VESSELS_PER_KM_CAPACITY
        assert ab_stats["density_ratio"] > 0
        assert "is_congested" in ab_stats

    def test_get_crossroad_stats(self, crossroad_network):
        """Test getting crossroad statistics."""
        traffic_mgr = TrafficManager(crossroad_network)
        traffic_mgr.update_time(5.0)

        # Occupy crossroad
        traffic_mgr.occupy_crossroad("vessel_1", "B")

        stats = traffic_mgr.get_crossroad_stats()

        assert "B" in stats
        b_stats = stats["B"]
        assert b_stats["occupied"] is True
        assert b_stats["occupied_by"] == "vessel_1"
        assert b_stats["queue_length"] == 0

    def test_edge_traffic_persistence(self, simple_network):
        """Test that edge traffic persists across multiple operations."""
        traffic_mgr = TrafficManager(simple_network)

        # Add vessels to multiple edges
        traffic_mgr.vessel_enter_edge("vessel_1", "A", "B")
        traffic_mgr.vessel_enter_edge("vessel_2", "B", "C")
        traffic_mgr.vessel_enter_edge("vessel_3", "A", "B")

        # Check state persists
        assert traffic_mgr.edge_traffic["A->B"].vessel_count == 2
        assert traffic_mgr.edge_traffic["B->C"].vessel_count == 1

        # Exit one vessel
        traffic_mgr.vessel_exit_edge("vessel_1", "A", "B")

        # State should update correctly
        assert traffic_mgr.edge_traffic["A->B"].vessel_count == 1
        assert traffic_mgr.edge_traffic["B->C"].vessel_count == 1


class TestTrafficConstants:
    """Tests for traffic model constants."""

    def test_constants_defined(self):
        """Test that all constants are properly defined."""
        assert VESSELS_PER_KM_CAPACITY == 12
        assert CONGESTION_IMPACT_FACTOR == 0.7
        assert CROSSROAD_TRANSIT_TIME == 0.5
        assert MIN_SPEED_RATIO == 0.3

    def test_constants_reasonable_values(self):
        """Test that constants have reasonable values."""
        assert 10 <= VESSELS_PER_KM_CAPACITY <= 20
        assert 0 < CONGESTION_IMPACT_FACTOR <= 1.0
        assert 0 < CROSSROAD_TRANSIT_TIME <= 1.0
        assert 0 < MIN_SPEED_RATIO < 1.0


class TestIntegrationScenarios:
    """Integration tests for realistic traffic scenarios."""

    @pytest.fixture
    def rhine_network(self):
        """Create a Rhine-like network."""
        network = Network(directed=True)

        # Create nodes
        nodes = [
            Node("Rotterdam", "Rotterdam Port", "port"),
            Node("Dordrecht", "Dordrecht Port", "port"),
            Node("Nijmegen", "Nijmegen Port", "port"),
            Node("Duisburg", "Duisburg Port", "port"),
        ]
        for node in nodes:
            network.add_node(node)

        # Create edges
        edges = [
            Edge("Rotterdam", "Dordrecht", 24.0, properties={"distance_km": 24}),
            Edge("Dordrecht", "Nijmegen", 95.0, properties={"distance_km": 95}),
            Edge("Nijmegen", "Duisburg", 111.0, properties={"distance_km": 111}),
        ]
        for edge in edges:
            network.add_edge(edge)

        return network

    def test_multi_vessel_journey(self, rhine_network):
        """Test multiple vessels traveling through the network."""
        traffic_mgr = TrafficManager(rhine_network)

        # Three vessels traveling along the same route
        vessels = ["vessel_1", "vessel_2", "vessel_3"]

        # All enter Rotterdam->Dordrecht
        for vessel in vessels:
            traffic_mgr.vessel_enter_edge(vessel, "Rotterdam", "Dordrecht")

        edge = traffic_mgr.edge_traffic["Rotterdam->Dordrecht"]
        assert edge.vessel_count == 3

        # Check congestion effect
        base_speed = 15.0
        effective_speed = traffic_mgr.get_effective_speed("test", base_speed, "Rotterdam", "Dordrecht")
        assert effective_speed < base_speed  # Should be slower due to congestion

    def test_crossroad_scenario(self, rhine_network):
        """Test crossroad behavior with multiple vessels."""
        # Add edges to make Nijmegen a crossroad
        rhine_network.add_edge(Edge("Rotterdam", "Nijmegen", 130.0, properties={"distance_km": 130}))
        rhine_network.add_edge(Edge("Nijmegen", "Rotterdam", 130.0, properties={"distance_km": 130}))

        traffic_mgr = TrafficManager(rhine_network)
        traffic_mgr.update_time(0.0)

        # Nijmegen should be a crossroad now
        assert "Nijmegen" in traffic_mgr.crossroads

        # First vessel occupies crossroad
        traffic_mgr.occupy_crossroad("vessel_1", "Nijmegen")

        # Second vessel must wait
        can_enter, wait_time = traffic_mgr.check_crossroad_entry("vessel_2", "Nijmegen")
        assert not can_enter
        assert wait_time == CROSSROAD_TRANSIT_TIME

        # After transit time, crossroad becomes available
        traffic_mgr.update_time(CROSSROAD_TRANSIT_TIME)
        can_enter, wait_time = traffic_mgr.check_crossroad_entry("vessel_2", "Nijmegen")
        assert can_enter
        assert wait_time == 0.0
