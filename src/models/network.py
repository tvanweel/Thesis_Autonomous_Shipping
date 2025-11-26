"""
Simple Network Model for ABM Simulation

A lightweight network structure consisting of nodes and edges for
agent-based modeling applications.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import networkx as nx


@dataclass
class Node:
    """
    Represents a node in the network.

    Attributes:
        id: Unique identifier for the node
        name: Human-readable name
        node_type: Type/category of the node
        properties: Additional node properties as key-value pairs
    """
    id: str
    name: str
    node_type: str = "default"
    properties: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.id == other.id
        return False

    def __repr__(self):
        return f"Node(id='{self.id}', name='{self.name}', type='{self.node_type}')"


@dataclass
class Edge:
    """
    Represents a directed edge between two nodes.

    Attributes:
        source: Source node ID
        target: Target node ID
        weight: Edge weight (default: 1.0)
        properties: Additional edge properties as key-value pairs
    """
    source: str
    target: str
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self):
        return f"Edge('{self.source}' -> '{self.target}', weight={self.weight})"


class Network:
    """
    Simple network structure for ABM modeling.

    Uses NetworkX for graph operations while providing a clean
    interface for agent-based models.
    """

    def __init__(self, directed: bool = True):
        """
        Initialize an empty network.

        Args:
            directed: Whether the network is directed (default: True)
        """
        self.directed = directed
        self._graph = nx.DiGraph() if directed else nx.Graph()
        self._nodes: Dict[str, Node] = {}
        self._edges: List[Edge] = []

    def add_node(self, node: Node) -> None:
        """
        Add a node to the network.

        Args:
            node: Node object to add

        Raises:
            ValueError: If node with same ID already exists
        """
        if node.id in self._nodes:
            raise ValueError(f"Node with id '{node.id}' already exists")

        self._nodes[node.id] = node
        self._graph.add_node(node.id, **node.properties)

    def add_edge(self, edge: Edge) -> None:
        """
        Add an edge to the network.

        Args:
            edge: Edge object to add

        Raises:
            ValueError: If source or target node doesn't exist
        """
        if edge.source not in self._nodes:
            raise ValueError(f"Source node '{edge.source}' does not exist")
        if edge.target not in self._nodes:
            raise ValueError(f"Target node '{edge.target}' does not exist")

        self._edges.append(edge)
        self._graph.add_edge(
            edge.source,
            edge.target,
            weight=edge.weight,
            **edge.properties
        )

    def get_node(self, node_id: str) -> Optional[Node]:
        """
        Get a node by its ID.

        Args:
            node_id: ID of the node to retrieve

        Returns:
            Node object or None if not found
        """
        return self._nodes.get(node_id)

    def get_neighbors(self, node_id: str) -> List[str]:
        """
        Get all neighbors of a node.

        Args:
            node_id: ID of the node

        Returns:
            List of neighbor node IDs

        Raises:
            ValueError: If node doesn't exist
        """
        if node_id not in self._nodes:
            raise ValueError(f"Node '{node_id}' does not exist")

        return list(self._graph.neighbors(node_id))

    def get_shortest_path(
        self,
        source: str,
        target: str,
        weight: str = "weight"
    ) -> Tuple[List[str], float]:
        """
        Find shortest path between two nodes.

        Args:
            source: Source node ID
            target: Target node ID
            weight: Edge attribute to use as weight (default: 'weight')

        Returns:
            Tuple of (path as list of node IDs, total path length)

        Raises:
            ValueError: If nodes don't exist or no path exists
        """
        if source not in self._nodes:
            raise ValueError(f"Source node '{source}' does not exist")
        if target not in self._nodes:
            raise ValueError(f"Target node '{target}' does not exist")

        try:
            path = nx.shortest_path(
                self._graph,
                source=source,
                target=target,
                weight=weight
            )
            length = nx.shortest_path_length(
                self._graph,
                source=source,
                target=target,
                weight=weight
            )
            return path, length
        except nx.NetworkXNoPath:
            raise ValueError(f"No path exists between '{source}' and '{target}'")

    def get_all_paths(
        self,
        source: str,
        target: str,
        cutoff: Optional[int] = None
    ) -> List[List[str]]:
        """
        Get all simple paths between two nodes.

        Args:
            source: Source node ID
            target: Target node ID
            cutoff: Maximum path length (default: None for no limit)

        Returns:
            List of paths, where each path is a list of node IDs
        """
        if source not in self._nodes:
            raise ValueError(f"Source node '{source}' does not exist")
        if target not in self._nodes:
            raise ValueError(f"Target node '{target}' does not exist")

        return list(nx.all_simple_paths(
            self._graph,
            source=source,
            target=target,
            cutoff=cutoff
        ))

    @property
    def nodes(self) -> Dict[str, Node]:
        """Get all nodes in the network."""
        return self._nodes.copy()

    @property
    def edges(self) -> List[Edge]:
        """Get all edges in the network."""
        return self._edges.copy()

    @property
    def node_count(self) -> int:
        """Get the number of nodes."""
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        """Get the number of edges."""
        return len(self._edges)

    def get_degree(self, node_id: str) -> int:
        """
        Get the degree (number of connections) of a node.

        Args:
            node_id: ID of the node

        Returns:
            Node degree
        """
        if node_id not in self._nodes:
            raise ValueError(f"Node '{node_id}' does not exist")
        return self._graph.degree(node_id)

    def is_connected(self) -> bool:
        """
        Check if the network is connected.

        For directed graphs, checks weak connectivity.

        Returns:
            True if network is connected, False otherwise
        """
        if self.directed:
            return nx.is_weakly_connected(self._graph)
        return nx.is_connected(self._graph)

    def get_subgraph(self, node_ids: List[str]) -> 'Network':
        """
        Create a subgraph containing only specified nodes.

        Args:
            node_ids: List of node IDs to include

        Returns:
            New Network object containing subgraph
        """
        subgraph = Network(directed=self.directed)

        # Add nodes
        for node_id in node_ids:
            if node_id in self._nodes:
                subgraph.add_node(self._nodes[node_id])

        # Add edges that connect nodes in subgraph
        for edge in self._edges:
            if edge.source in node_ids and edge.target in node_ids:
                subgraph.add_edge(edge)

        return subgraph

    def to_dict(self) -> Dict:
        """
        Export network to dictionary format.

        Returns:
            Dictionary representation of the network
        """
        return {
            'directed': self.directed,
            'nodes': [
                {
                    'id': node.id,
                    'name': node.name,
                    'type': node.node_type,
                    'properties': node.properties
                }
                for node in self._nodes.values()
            ],
            'edges': [
                {
                    'source': edge.source,
                    'target': edge.target,
                    'weight': edge.weight,
                    'properties': edge.properties
                }
                for edge in self._edges
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Network':
        """
        Create network from dictionary format.

        Args:
            data: Dictionary representation of network

        Returns:
            Network object
        """
        network = cls(directed=data.get('directed', True))

        # Add nodes
        for node_data in data.get('nodes', []):
            node = Node(
                id=node_data['id'],
                name=node_data['name'],
                node_type=node_data.get('type', 'default'),
                properties=node_data.get('properties', {})
            )
            network.add_node(node)

        # Add edges
        for edge_data in data.get('edges', []):
            edge = Edge(
                source=edge_data['source'],
                target=edge_data['target'],
                weight=edge_data.get('weight', 1.0),
                properties=edge_data.get('properties', {})
            )
            network.add_edge(edge)

        return network

    def __repr__(self):
        return f"Network(nodes={self.node_count}, edges={self.edge_count}, directed={self.directed})"
