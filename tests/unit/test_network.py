"""
Unit tests for the simple network module.
"""

import pytest
from src.models.network import Node, Edge, Network


class TestNode:
    """Tests for the Node class."""

    def test_node_creation(self):
        """Test basic node creation."""
        node = Node(id="n1", name="Node 1", node_type="test")
        assert node.id == "n1"
        assert node.name == "Node 1"
        assert node.node_type == "test"
        assert node.properties == {}

    def test_node_with_properties(self):
        """Test node creation with custom properties."""
        props = {"capacity": 100, "location": "A"}
        node = Node(id="n1", name="Node 1", properties=props)
        assert node.properties["capacity"] == 100
        assert node.properties["location"] == "A"

    def test_node_equality(self):
        """Test node equality based on ID."""
        node1 = Node(id="n1", name="Node 1")
        node2 = Node(id="n1", name="Different Name")
        node3 = Node(id="n2", name="Node 1")

        assert node1 == node2  # Same ID
        assert node1 != node3  # Different ID

    def test_node_hashable(self):
        """Test that nodes can be used in sets and dicts."""
        node1 = Node(id="n1", name="Node 1")
        node2 = Node(id="n2", name="Node 2")

        node_set = {node1, node2}
        assert len(node_set) == 2
        assert node1 in node_set

    def test_node_repr(self):
        """Test node string representation."""
        node = Node(id="n1", name="Test Node", node_type="port")
        repr_str = repr(node)
        assert "n1" in repr_str
        assert "Test Node" in repr_str
        assert "port" in repr_str


class TestEdge:
    """Tests for the Edge class."""

    def test_edge_creation(self):
        """Test basic edge creation."""
        edge = Edge(source="n1", target="n2")
        assert edge.source == "n1"
        assert edge.target == "n2"
        assert edge.weight == 1.0
        assert edge.properties == {}

    def test_edge_with_weight(self):
        """Test edge creation with custom weight."""
        edge = Edge(source="n1", target="n2", weight=5.5)
        assert edge.weight == 5.5

    def test_edge_with_properties(self):
        """Test edge creation with custom properties."""
        props = {"distance": 10.5, "type": "highway"}
        edge = Edge(source="n1", target="n2", properties=props)
        assert edge.properties["distance"] == 10.5
        assert edge.properties["type"] == "highway"

    def test_edge_repr(self):
        """Test edge string representation."""
        edge = Edge(source="n1", target="n2", weight=2.0)
        repr_str = repr(edge)
        assert "n1" in repr_str
        assert "n2" in repr_str
        assert "2.0" in repr_str


class TestNetwork:
    """Tests for the Network class."""

    @pytest.fixture
    def empty_network(self):
        """Create an empty network."""
        return Network()

    @pytest.fixture
    def sample_network(self):
        """Create a sample network with nodes and edges."""
        network = Network()

        # Add nodes
        network.add_node(Node(id="A", name="Node A", node_type="port"))
        network.add_node(Node(id="B", name="Node B", node_type="port"))
        network.add_node(Node(id="C", name="Node C", node_type="waypoint"))

        # Add edges
        network.add_edge(Edge(source="A", target="B", weight=10.0))
        network.add_edge(Edge(source="B", target="C", weight=15.0))
        network.add_edge(Edge(source="A", target="C", weight=30.0))

        return network

    def test_network_creation(self, empty_network):
        """Test network initialization."""
        assert empty_network.node_count == 0
        assert empty_network.edge_count == 0
        assert empty_network.directed is True

    def test_undirected_network(self):
        """Test creation of undirected network."""
        network = Network(directed=False)
        assert network.directed is False

    def test_add_node(self, empty_network):
        """Test adding nodes to network."""
        node = Node(id="n1", name="Node 1")
        empty_network.add_node(node)

        assert empty_network.node_count == 1
        assert empty_network.get_node("n1") == node

    def test_add_duplicate_node_raises_error(self, empty_network):
        """Test that adding duplicate node raises error."""
        node1 = Node(id="n1", name="Node 1")
        node2 = Node(id="n1", name="Node 2")

        empty_network.add_node(node1)

        with pytest.raises(ValueError, match="already exists"):
            empty_network.add_node(node2)

    def test_add_edge(self, sample_network):
        """Test adding edges to network."""
        assert sample_network.edge_count == 3

    def test_add_edge_without_nodes_raises_error(self, empty_network):
        """Test that adding edge without nodes raises error."""
        edge = Edge(source="n1", target="n2")

        with pytest.raises(ValueError, match="does not exist"):
            empty_network.add_edge(edge)

    def test_get_node(self, sample_network):
        """Test retrieving nodes."""
        node = sample_network.get_node("A")
        assert node is not None
        assert node.id == "A"
        assert node.name == "Node A"

    def test_get_nonexistent_node(self, sample_network):
        """Test getting nonexistent node returns None."""
        node = sample_network.get_node("Z")
        assert node is None

    def test_get_neighbors(self, sample_network):
        """Test getting neighbors of a node."""
        neighbors = sample_network.get_neighbors("A")
        assert len(neighbors) == 2
        assert "B" in neighbors
        assert "C" in neighbors

    def test_get_neighbors_nonexistent_node_raises_error(self, sample_network):
        """Test that getting neighbors of nonexistent node raises error."""
        with pytest.raises(ValueError, match="does not exist"):
            sample_network.get_neighbors("Z")

    def test_shortest_path(self, sample_network):
        """Test shortest path calculation."""
        path, length = sample_network.get_shortest_path("A", "C")
        assert path == ["A", "B", "C"]
        assert length == 25.0  # 10 + 15

    def test_shortest_path_direct(self, sample_network):
        """Test shortest path when direct path is shorter."""
        # Add a shorter direct path
        sample_network.add_node(Node(id="D", name="Node D"))
        sample_network.add_edge(Edge(source="A", target="D", weight=5.0))
        sample_network.add_edge(Edge(source="D", target="C", weight=5.0))

        path, length = sample_network.get_shortest_path("A", "C")
        assert length == 10.0  # 5 + 5, shorter than 25

    def test_shortest_path_nonexistent_node_raises_error(self, sample_network):
        """Test that shortest path with nonexistent node raises error."""
        with pytest.raises(ValueError, match="does not exist"):
            sample_network.get_shortest_path("A", "Z")

    def test_shortest_path_no_path_raises_error(self):
        """Test that shortest path with no connection raises error."""
        network = Network()
        network.add_node(Node(id="A", name="Node A"))
        network.add_node(Node(id="B", name="Node B"))
        # No edge connecting them

        with pytest.raises(ValueError, match="No path exists"):
            network.get_shortest_path("A", "B")

    def test_get_all_paths(self, sample_network):
        """Test getting all simple paths."""
        paths = sample_network.get_all_paths("A", "C")
        assert len(paths) == 2  # Direct and via B
        assert ["A", "C"] in paths
        assert ["A", "B", "C"] in paths

    def test_get_all_paths_with_cutoff(self, sample_network):
        """Test getting all paths with length cutoff."""
        paths = sample_network.get_all_paths("A", "C", cutoff=2)
        # Only paths with max 2 hops
        assert len(paths) == 2

    def test_nodes_property(self, sample_network):
        """Test nodes property returns all nodes."""
        nodes = sample_network.nodes
        assert len(nodes) == 3
        assert "A" in nodes
        assert "B" in nodes
        assert "C" in nodes

    def test_edges_property(self, sample_network):
        """Test edges property returns all edges."""
        edges = sample_network.edges
        assert len(edges) == 3

    def test_get_degree(self, sample_network):
        """Test getting node degree."""
        degree_a = sample_network.get_degree("A")
        assert degree_a == 2  # Connected to B and C

    def test_get_degree_nonexistent_node_raises_error(self, sample_network):
        """Test that getting degree of nonexistent node raises error."""
        with pytest.raises(ValueError, match="does not exist"):
            sample_network.get_degree("Z")

    def test_is_connected_true(self, sample_network):
        """Test connectivity check on connected network."""
        assert sample_network.is_connected() is True

    def test_is_connected_false(self):
        """Test connectivity check on disconnected network."""
        network = Network()
        network.add_node(Node(id="A", name="Node A"))
        network.add_node(Node(id="B", name="Node B"))
        network.add_node(Node(id="C", name="Node C"))
        network.add_edge(Edge(source="A", target="B"))
        # C is disconnected

        assert network.is_connected() is False

    def test_get_subgraph(self, sample_network):
        """Test subgraph extraction."""
        subgraph = sample_network.get_subgraph(["A", "B"])

        assert subgraph.node_count == 2
        assert subgraph.edge_count == 1  # Only A->B edge
        assert subgraph.get_node("A") is not None
        assert subgraph.get_node("B") is not None
        assert subgraph.get_node("C") is None

    def test_to_dict(self, sample_network):
        """Test network export to dictionary."""
        data = sample_network.to_dict()

        assert data["directed"] is True
        assert len(data["nodes"]) == 3
        assert len(data["edges"]) == 3

        # Check node data
        node_a = next(n for n in data["nodes"] if n["id"] == "A")
        assert node_a["name"] == "Node A"
        assert node_a["type"] == "port"

        # Check edge data
        edge_ab = next(e for e in data["edges"]
                      if e["source"] == "A" and e["target"] == "B")
        assert edge_ab["weight"] == 10.0

    def test_from_dict(self):
        """Test network creation from dictionary."""
        data = {
            "directed": True,
            "nodes": [
                {"id": "A", "name": "Node A", "type": "port", "properties": {}},
                {"id": "B", "name": "Node B", "type": "port", "properties": {}}
            ],
            "edges": [
                {"source": "A", "target": "B", "weight": 10.0, "properties": {}}
            ]
        }

        network = Network.from_dict(data)

        assert network.node_count == 2
        assert network.edge_count == 1
        assert network.directed is True
        assert network.get_node("A").name == "Node A"

    def test_round_trip_dict_conversion(self, sample_network):
        """Test that network can be exported and imported without data loss."""
        data = sample_network.to_dict()
        reconstructed = Network.from_dict(data)

        assert reconstructed.node_count == sample_network.node_count
        assert reconstructed.edge_count == sample_network.edge_count
        assert reconstructed.directed == sample_network.directed

        # Check a path to verify structure
        path1, length1 = sample_network.get_shortest_path("A", "C")
        path2, length2 = reconstructed.get_shortest_path("A", "C")
        assert path1 == path2
        assert length1 == length2

    def test_network_repr(self, sample_network):
        """Test network string representation."""
        repr_str = repr(sample_network)
        assert "3" in repr_str  # 3 nodes
        assert "3" in repr_str  # 3 edges
        assert "directed" in repr_str.lower()


class TestNetworkAdvanced:
    """Advanced network tests."""

    def test_complex_network(self):
        """Test creation and operations on more complex network."""
        network = Network()

        # Create a diamond-shaped network
        #    A
        #   / \
        #  B   C
        #   \ /
        #    D

        for node_id in ["A", "B", "C", "D"]:
            network.add_node(Node(id=node_id, name=f"Node {node_id}"))

        network.add_edge(Edge(source="A", target="B", weight=1.0))
        network.add_edge(Edge(source="A", target="C", weight=2.0))
        network.add_edge(Edge(source="B", target="D", weight=1.0))
        network.add_edge(Edge(source="C", target="D", weight=1.0))

        # Test shortest path (should go A->B->D)
        path, length = network.get_shortest_path("A", "D")
        assert path == ["A", "B", "D"]
        assert length == 2.0

        # Test all paths
        all_paths = network.get_all_paths("A", "D")
        assert len(all_paths) == 2

    def test_network_with_properties(self):
        """Test network with nodes and edges containing properties."""
        network = Network()

        # Add nodes with properties
        network.add_node(Node(
            id="port1",
            name="Rotterdam",
            node_type="port",
            properties={"capacity": 1000, "country": "NL"}
        ))
        network.add_node(Node(
            id="port2",
            name="Duisburg",
            node_type="port",
            properties={"capacity": 800, "country": "DE"}
        ))

        # Add edge with properties
        network.add_edge(Edge(
            source="port1",
            target="port2",
            weight=250.0,
            properties={"distance_km": 250, "river": "Rhine"}
        ))

        # Verify properties preserved
        node = network.get_node("port1")
        assert node.properties["capacity"] == 1000
        assert node.properties["country"] == "NL"

        # Check via dictionary export/import
        data = network.to_dict()
        reconstructed = Network.from_dict(data)
        recon_node = reconstructed.get_node("port1")
        assert recon_node.properties["capacity"] == 1000
