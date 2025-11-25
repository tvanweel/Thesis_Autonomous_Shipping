"""
Rhine River Network Visualization

Demonstrates the Rhine corridor network with infrastructure details.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.network import create_rhine_network

# Create output directory
RESULTS_DIR = Path(__file__).parent.parent / "results" / "rhine_network"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("Rhine River Corridor Network Visualization")
print("=" * 80)
print()

# Create network
print("Loading Rhine network...")
rhine = create_rhine_network()
print(f"  Loaded {len(rhine.nodes)} infrastructure nodes")
print(f"  {len(rhine.graph.edges())} connections")
print()

# Print detailed summary
rhine.print_network_summary()

# Show examples of different node types
print("\n" + "=" * 80)
print("INFRASTRUCTURE BY TYPE")
print("=" * 80)
print()

print("Major Ports (with capacity):")
print("-" * 80)
ports = rhine.get_nodes_by_type("port")
ports_with_capacity = [p for p in ports if p.capacity]
for port in sorted(ports_with_capacity, key=lambda x: x.capacity, reverse=True):
    print(f"  {port.name:25s} - {port.capacity/1000000:6.1f}M tonnes/year  ({port.country})")
print()

print("Lock Complexes:")
print("-" * 80)
locks = rhine.get_nodes_by_type("lock")
for lock in sorted(locks, key=lambda x: x.river_km, reverse=True):
    print(f"  km {lock.river_km:5.0f} - {lock.name:25s} - {lock.description}")
print()

print("River Confluences:")
print("-" * 80)
confluences = rhine.get_nodes_by_type("confluence")
for conf in sorted(confluences, key=lambda x: x.river_km, reverse=True):
    print(f"  km {conf.river_km:5.0f} - {conf.name:25s} - {conf.description}")
print()

# Example routes
print("=" * 80)
print("EXAMPLE ROUTES")
print("=" * 80)
print()

routes_to_test = [
    ("Rotterdam_Port", "Basel_Port", "Full corridor"),
    ("Duisburg_Port", "Mannheim_Port", "German industrial route"),
    ("Cologne_Port", "Strasbourg_Port", "Middle Rhine to Alsace"),
    ("Rotterdam_Port", "Duisburg_Port", "Netherlands to Ruhr area"),
]

for origin, dest, description in routes_to_test:
    route, distance = rhine.get_route(origin, dest)
    if route:
        print(f"{description}:")
        print(f"  {origin} -> {dest}")
        print(f"  Distance: {distance:.1f} km")
        print(f"  Via {len(route)} nodes")

        # Show key waypoints (first, locks, last)
        key_points = []
        for node_name in route:
            node = rhine.get_node_info(node_name)
            if node.node_type in ['lock', 'confluence'] or node_name == origin or node_name == dest:
                key_points.append(f"{node_name} (km {node.river_km:.0f})")
        print(f"  Key points: {' -> '.join(key_points)}")
        print()

# Generate visualization
print("=" * 80)
print("GENERATING VISUALIZATIONS")
print("=" * 80)
print()

print("Creating network visualization...")
fig = rhine.visualize(save_path=RESULTS_DIR / "rhine_corridor_network.png")
print(f"  Saved to: {RESULTS_DIR / 'rhine_corridor_network.png'}")
print()

# Network statistics
print("=" * 80)
print("NETWORK ANALYSIS")
print("=" * 80)
print()

stats = rhine.get_network_statistics()
print("Network Characteristics:")
for key, value in stats.items():
    if isinstance(value, dict):
        print(f"  {key}:")
        for k, v in value.items():
            print(f"    {k}: {v}")
    else:
        print(f"  {key}: {value}")
print()

print("=" * 80)
print("Rhine Network Analysis Complete!")
print(f"Results saved to: {RESULTS_DIR.absolute()}")
print("=" * 80)
