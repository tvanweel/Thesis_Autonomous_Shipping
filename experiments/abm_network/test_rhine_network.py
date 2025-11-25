"""
Tests for Rhine River Network Model

Tests cover:
1. Network initialization and structure
2. Port and segment properties
3. Route finding and navigation
4. Network statistics and analysis
5. Visualization generation
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for tests

import pytest
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
import tempfile
import shutil

from src.models.network import (
    RhineNetwork,
    RhinePort,
    RhineSegment,
    create_rhine_network,
)


# --------- Fixtures --------- #

@pytest.fixture
def rhine_network():
    """Create Rhine network for testing."""
    return create_rhine_network()


@pytest.fixture
def temp_dir():
    """Create temporary directory for test outputs."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    if temp_path.exists():
        shutil.rmtree(temp_path)


# --------- Initialization Tests --------- #

def test_network_initialization(rhine_network):
    """Test that Rhine network initializes correctly."""
    assert rhine_network is not None
    assert isinstance(rhine_network.graph, nx.DiGraph)
    assert len(rhine_network.ports) > 0
    assert len(rhine_network.segments) > 0


def test_factory_function():
    """Test factory function creates network."""
    network = create_rhine_network()
    assert isinstance(network, RhineNetwork)
    assert network.graph.number_of_nodes() > 0


def test_major_ports_exist(rhine_network):
    """Test that major Rhine ports are included."""
    major_ports = ["Rotterdam", "Duisburg", "Cologne", "Mannheim", "Basel"]
    for port in major_ports:
        assert port in rhine_network.ports
        assert port in rhine_network.graph.nodes()


def test_all_ports_have_required_attributes(rhine_network):
    """Test that all ports have required attributes."""
    required_attrs = ["name", "country", "river_km", "coordinates",
                     "port_type", "capacity"]

    for port in rhine_network.ports.values():
        for attr in required_attrs:
            assert hasattr(port, attr)


def test_all_segments_have_required_attributes(rhine_network):
    """Test that all segments have required attributes."""
    required_attrs = ["start", "end", "length", "depth", "width",
                     "locks", "traffic_density", "risk_level"]

    for segment in rhine_network.segments:
        for attr in required_attrs:
            assert hasattr(segment, attr)


# --------- Port Tests --------- #

def test_port_dataclass():
    """Test RhinePort dataclass."""
    port = RhinePort(
        name="Test Port",
        country="DE",
        river_km=500.0,
        coordinates=(50.0, 7.0),
        port_type="inland_port",
        capacity=1000000.0
    )

    assert port.name == "Test Port"
    assert port.country == "DE"
    assert port.river_km == 500.0
    assert port.coordinates == (50.0, 7.0)


def test_ports_have_valid_countries(rhine_network):
    """Test that all ports have valid country codes."""
    valid_countries = {"NL", "DE", "FR", "CH"}

    for port in rhine_network.ports.values():
        assert port.country in valid_countries


def test_ports_have_positive_river_km(rhine_network):
    """Test that all ports have positive river_km values."""
    for port in rhine_network.ports.values():
        assert port.river_km > 0


def test_rotterdam_is_largest_port(rhine_network):
    """Test that Rotterdam has the highest capacity."""
    rotterdam = rhine_network.ports["Rotterdam"]
    other_ports = [p for p in rhine_network.ports.values() if p.name != "Rotterdam"]

    assert all(rotterdam.capacity > p.capacity for p in other_ports)


def test_get_ports_by_country(rhine_network):
    """Test filtering ports by country."""
    nl_ports = rhine_network.get_ports_by_country("NL")
    de_ports = rhine_network.get_ports_by_country("DE")

    assert len(nl_ports) > 0
    assert len(de_ports) > 0
    assert all(p.country == "NL" for p in nl_ports)
    assert all(p.country == "DE" for p in de_ports)


# --------- Segment Tests --------- #

def test_segment_dataclass():
    """Test RhineSegment dataclass."""
    segment = RhineSegment(
        start="PortA",
        end="PortB",
        length=50.0,
        depth=4.0,
        width=200.0,
        locks=1,
        traffic_density=100.0,
        risk_level=2
    )

    assert segment.start == "PortA"
    assert segment.end == "PortB"
    assert segment.length == 50.0


def test_segments_have_positive_length(rhine_network):
    """Test that all segments have positive length."""
    for segment in rhine_network.segments:
        assert segment.length > 0


def test_segments_have_valid_risk_levels(rhine_network):
    """Test that risk levels are in valid range."""
    for segment in rhine_network.segments:
        assert 1 <= segment.risk_level <= 5


def test_get_high_traffic_segments(rhine_network):
    """Test filtering high-traffic segments."""
    high_traffic = rhine_network.get_high_traffic_segments(threshold=100)

    assert len(high_traffic) > 0
    assert all(seg.traffic_density >= 100 for seg in high_traffic)


def test_get_high_risk_segments(rhine_network):
    """Test filtering high-risk segments."""
    high_risk = rhine_network.get_high_risk_segments(min_risk=3)

    assert len(high_risk) > 0
    assert all(seg.risk_level >= 3 for seg in high_risk)


# --------- Graph Structure Tests --------- #

def test_graph_is_directed(rhine_network):
    """Test that graph is a directed graph."""
    assert isinstance(rhine_network.graph, nx.DiGraph)


def test_graph_is_connected(rhine_network):
    """Test that graph is connected (ignoring direction)."""
    undirected = rhine_network.graph.to_undirected()
    assert nx.is_connected(undirected)


def test_bidirectional_edges(rhine_network):
    """Test that river segments are bidirectional."""
    # For each segment, both directions should exist
    for segment in rhine_network.segments:
        assert rhine_network.graph.has_edge(segment.start, segment.end)
        assert rhine_network.graph.has_edge(segment.end, segment.start)


def test_edge_attributes(rhine_network):
    """Test that edges have required attributes."""
    required_attrs = ["length", "depth", "width", "locks",
                     "traffic_density", "risk_level", "direction"]

    for u, v, data in rhine_network.graph.edges(data=True):
        for attr in required_attrs:
            assert attr in data


def test_node_attributes(rhine_network):
    """Test that nodes have required attributes."""
    required_attrs = ["country", "river_km", "coordinates", "port_type",
                     "capacity", "automation_level"]

    for node, data in rhine_network.graph.nodes(data=True):
        for attr in required_attrs:
            assert attr in data


# --------- Route Finding Tests --------- #

def test_route_rotterdam_to_basel(rhine_network):
    """Test finding route from Rotterdam to Basel."""
    route, cost = rhine_network.get_route("Rotterdam", "Basel", criterion="length")

    assert len(route) > 0
    assert route[0] == "Rotterdam"
    assert route[-1] == "Basel"
    assert cost > 0


def test_route_with_different_criteria(rhine_network):
    """Test route finding with different optimization criteria."""
    origin, dest = "Rotterdam", "Mannheim"

    route_length, cost_length = rhine_network.get_route(origin, dest, "length")
    route_risk, cost_risk = rhine_network.get_route(origin, dest, "risk")

    assert len(route_length) > 0
    assert len(route_risk) > 0
    # Routes may differ based on optimization criterion


def test_route_invalid_ports(rhine_network):
    """Test route finding with invalid ports."""
    # NetworkX raises NodeNotFound for invalid nodes
    with pytest.raises((nx.NodeNotFound, Exception)):
        route, cost = rhine_network.get_route("InvalidPort1", "InvalidPort2")


def test_route_same_origin_destination(rhine_network):
    """Test route from port to itself."""
    route, cost = rhine_network.get_route("Cologne", "Cologne", "length")

    assert route == ["Cologne"]
    assert cost == 0


# --------- Neighbor Tests --------- #

def test_get_neighbors_both_directions(rhine_network):
    """Test getting neighbors in both directions."""
    neighbors = rhine_network.get_neighbors("Cologne", direction="both")
    assert len(neighbors) > 0


def test_get_neighbors_downstream(rhine_network):
    """Test getting downstream neighbors."""
    # Basel should have no downstream neighbors (it's upstream end)
    basel_downstream = rhine_network.get_neighbors("Basel", direction="downstream")
    assert len(basel_downstream) == 0

    # Rotterdam should have downstream neighbors
    rotterdam_downstream = rhine_network.get_neighbors("Rotterdam", direction="downstream")
    assert len(rotterdam_downstream) > 0


def test_get_neighbors_upstream(rhine_network):
    """Test getting upstream neighbors."""
    # Rotterdam is at the downstream end, so it has neighbors going upstream
    # But in the direction filtering, "upstream" means edges going towards Basel
    # Duisburg is further inland and should have upstream neighbors
    duisburg_upstream = rhine_network.get_neighbors("Duisburg", direction="upstream")
    assert len(duisburg_upstream) > 0


# --------- Statistics Tests --------- #

def test_network_statistics(rhine_network):
    """Test network statistics calculation."""
    stats = rhine_network.get_network_statistics()

    required_stats = ["total_ports", "total_segments", "total_distance_km",
                     "countries", "total_locks", "avg_segment_length",
                     "avg_traffic_density", "total_capacity", "avg_risk_level"]

    for stat in required_stats:
        assert stat in stats
        assert isinstance(stats[stat], (int, float))
        assert stats[stat] >= 0


def test_total_distance_calculation(rhine_network):
    """Test total distance calculation."""
    total_distance = rhine_network.calculate_total_distance()

    assert total_distance > 0
    # Rhine navigable distance should be around 800-900 km
    assert 700 < total_distance < 1000


def test_country_count(rhine_network):
    """Test that network spans 4 countries."""
    stats = rhine_network.get_network_statistics()
    assert stats["countries"] == 4


# --------- Visualization Tests --------- #

def test_visualize_network_creates_figure(rhine_network):
    """Test that network visualization creates a figure."""
    fig = rhine_network.visualize_network()
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_visualize_network_with_different_colors(rhine_network):
    """Test visualization with different color schemes."""
    color_schemes = ["country", "capacity", "automation"]

    for color_by in color_schemes:
        fig = rhine_network.visualize_network(color_by=color_by)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


def test_visualize_network_saves_file(rhine_network, temp_dir):
    """Test that visualization can be saved."""
    save_path = temp_dir / "rhine_network.png"
    fig = rhine_network.visualize_network(save_path=save_path)

    assert save_path.exists()
    assert save_path.stat().st_size > 0
    plt.close(fig)


def test_visualize_traffic_flow_creates_figure(rhine_network):
    """Test that traffic flow visualization creates a figure."""
    fig = rhine_network.visualize_traffic_flow()
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_visualize_traffic_flow_saves_file(rhine_network, temp_dir):
    """Test that traffic flow visualization can be saved."""
    save_path = temp_dir / "traffic_flow.png"
    fig = rhine_network.visualize_traffic_flow(save_path=save_path)

    assert save_path.exists()
    assert save_path.stat().st_size > 0
    plt.close(fig)


def test_visualize_risk_profile_creates_figure(rhine_network):
    """Test that risk profile visualization creates a figure."""
    fig = rhine_network.visualize_risk_profile()
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_visualize_risk_profile_saves_file(rhine_network, temp_dir):
    """Test that risk profile visualization can be saved."""
    save_path = temp_dir / "risk_profile.png"
    fig = rhine_network.visualize_risk_profile(save_path=save_path)

    assert save_path.exists()
    assert save_path.stat().st_size > 0
    plt.close(fig)


# --------- Integration Tests --------- #

def test_full_journey_rotterdam_to_basel(rhine_network):
    """Test complete journey from Rotterdam to Basel."""
    route, distance = rhine_network.get_route("Rotterdam", "Basel", "length")

    assert route[0] == "Rotterdam"
    assert route[-1] == "Basel"
    assert len(route) >= 10  # Should pass through many ports

    # Verify all ports in route exist
    for port_name in route:
        assert port_name in rhine_network.ports


def test_network_traversal_preserves_connectivity(rhine_network):
    """Test that network remains connected through all ports."""
    # Every port should be reachable from Rotterdam
    for port_name in rhine_network.ports.keys():
        if port_name != "Rotterdam":
            route, _ = rhine_network.get_route("Rotterdam", port_name, "length")
            assert len(route) > 0, f"Cannot reach {port_name} from Rotterdam"


def test_bidirectional_routes_consistent(rhine_network):
    """Test that bidirectional routes are consistent."""
    origin, dest = "Cologne", "Mannheim"

    route_forward, dist_forward = rhine_network.get_route(origin, dest, "length")
    route_backward, dist_backward = rhine_network.get_route(dest, origin, "length")

    # Routes should exist in both directions
    assert len(route_forward) > 0
    assert len(route_backward) > 0

    # Distances should be the same (undirected length)
    assert abs(dist_forward - dist_backward) < 0.1


def test_high_capacity_ports_are_well_connected(rhine_network):
    """Test that high-capacity ports have good connectivity."""
    high_capacity_ports = [p.name for p in rhine_network.ports.values()
                          if p.capacity > 10000000]

    for port in high_capacity_ports:
        neighbors = rhine_network.get_neighbors(port, direction="both")
        # High-capacity ports should have at least one neighbor
        assert len(neighbors) >= 1


# --------- Edge Case Tests --------- #

def test_port_hash_consistency():
    """Test that RhinePort hashing works correctly."""
    port1 = RhinePort("Test", "DE", 500, (50.0, 7.0), "inland_port")
    port2 = RhinePort("Test", "DE", 500, (50.0, 7.0), "inland_port")

    # Same name should produce same hash
    assert hash(port1) == hash(port2)

    # Can be used in sets
    port_set = {port1, port2}
    assert len(port_set) == 1


def test_empty_route_handling(rhine_network):
    """Test handling of routes with no path."""
    # Try to find route with invalid criterion
    with pytest.raises(ValueError, match="Unknown criterion"):
        rhine_network.get_route("Rotterdam", "Basel", "invalid_criterion")
