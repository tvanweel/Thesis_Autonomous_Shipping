"""
Simple Network Demo

Demonstrates basic usage of the Network, Node, and Edge classes
for agent-based modeling.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.network import Network, Node, Edge


def main():
    print("=" * 70)
    print("SIMPLE NETWORK DEMONSTRATION")
    print("=" * 70)
    print()

    # Create a new network
    print("Creating a directed network...")
    network = Network(directed=True)
    print(f"Network created: {network}")
    print()

    # Add nodes
    print("Adding nodes...")
    nodes = [
        Node(id="A", name="Port A", node_type="port",
             properties={"capacity": 1000}),
        Node(id="B", name="Port B", node_type="port",
             properties={"capacity": 800}),
        Node(id="C", name="Waypoint C", node_type="waypoint"),
        Node(id="D", name="Port D", node_type="port",
             properties={"capacity": 500}),
    ]

    for node in nodes:
        network.add_node(node)
        print(f"  Added: {node}")
    print()

    # Add edges
    print("Adding edges...")
    edges = [
        Edge(source="A", target="B", weight=10.0,
             properties={"distance_km": 100}),
        Edge(source="A", target="C", weight=8.0,
             properties={"distance_km": 80}),
        Edge(source="B", target="D", weight=15.0,
             properties={"distance_km": 150}),
        Edge(source="C", target="D", weight=12.0,
             properties={"distance_km": 120}),
        Edge(source="C", target="B", weight=5.0,
             properties={"distance_km": 50}),
    ]

    for edge in edges:
        network.add_edge(edge)
        print(f"  Added: {edge}")
    print()

    # Network statistics
    print("=" * 70)
    print("NETWORK STATISTICS")
    print("=" * 70)
    print(f"Number of nodes: {network.node_count}")
    print(f"Number of edges: {network.edge_count}")
    print(f"Directed: {network.directed}")
    print(f"Connected: {network.is_connected()}")
    print()

    # Node information
    print("=" * 70)
    print("NODE INFORMATION")
    print("=" * 70)
    for node_id, node in network.nodes.items():
        degree = network.get_degree(node_id)
        neighbors = network.get_neighbors(node_id)
        print(f"{node_id}: {node.name}")
        print(f"  Type: {node.node_type}")
        print(f"  Degree: {degree}")
        print(f"  Neighbors: {', '.join(neighbors)}")
        if node.properties:
            print(f"  Properties: {node.properties}")
        print()

    # Shortest paths
    print("=" * 70)
    print("SHORTEST PATHS")
    print("=" * 70)

    path_queries = [
        ("A", "D"),
        ("A", "B"),
        ("B", "C"),
    ]

    for source, target in path_queries:
        try:
            path, length = network.get_shortest_path(source, target)
            print(f"{source} -> {target}:")
            print(f"  Path: {' -> '.join(path)}")
            print(f"  Total weight: {length:.1f}")
        except ValueError as e:
            print(f"{source} -> {target}: {e}")
        print()

    # All paths
    print("=" * 70)
    print("ALL PATHS (A to D)")
    print("=" * 70)
    all_paths = network.get_all_paths("A", "D")
    for i, path in enumerate(all_paths, 1):
        print(f"Path {i}: {' -> '.join(path)}")
    print()

    # Subgraph
    print("=" * 70)
    print("SUBGRAPH EXTRACTION")
    print("=" * 70)
    print("Creating subgraph with nodes A, B, C...")
    subgraph = network.get_subgraph(["A", "B", "C"])
    print(f"Subgraph: {subgraph}")
    print(f"  Nodes: {list(subgraph.nodes.keys())}")
    print(f"  Edges: {len(subgraph.edges)}")
    print()

    # Dictionary export/import
    print("=" * 70)
    print("SERIALIZATION")
    print("=" * 70)
    print("Exporting network to dictionary...")
    network_dict = network.to_dict()
    print(f"Exported {len(network_dict['nodes'])} nodes and "
          f"{len(network_dict['edges'])} edges")
    print()

    print("Importing network from dictionary...")
    reconstructed = Network.from_dict(network_dict)
    print(f"Reconstructed: {reconstructed}")

    # Verify reconstruction
    path1, length1 = network.get_shortest_path("A", "D")
    path2, length2 = reconstructed.get_shortest_path("A", "D")
    print(f"Original path: {' -> '.join(path1)} (length: {length1:.1f})")
    print(f"Reconstructed path: {' -> '.join(path2)} (length: {length2:.1f})")
    print(f"Match: {path1 == path2 and length1 == length2}")
    print()

    print("=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
