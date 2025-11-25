"""
Rhine River Network Visualization

Demonstrates the spatial network model of the Rhine river system,
including ports, segments, traffic flow, and navigation risks.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.network import create_rhine_network

# Create output directory
RESULTS_DIR = Path(__file__).parent.parent / "results" / "rhine_network"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("Rhine River Network Visualization")
print("=" * 80)
print()

# Create Rhine network
print("Initializing Rhine River network...")
rhine = create_rhine_network()
print(f"  Network created with {len(rhine.ports)} ports and {len(rhine.segments)} segments")
print()

# Display network statistics
print("Network Statistics:")
print("-" * 80)
stats = rhine.get_network_statistics()
for key, value in stats.items():
    if isinstance(value, float):
        print(f"  {key.replace('_', ' ').title()}: {value:.2f}")
    else:
        print(f"  {key.replace('_', ' ').title()}: {value}")
print()

# Display ports by country
print("Ports by Country:")
print("-" * 80)
for country in ["NL", "DE", "FR", "CH"]:
    country_ports = rhine.get_ports_by_country(country)
    country_names = {"NL": "Netherlands", "DE": "Germany", "FR": "France", "CH": "Switzerland"}
    print(f"  {country_names[country]}: {len(country_ports)} ports")
    for port in sorted(country_ports, key=lambda p: p.capacity, reverse=True)[:3]:
        print(f"    - {port.name}: {port.capacity/1000000:.1f}M tonnes capacity")
print()

# Analyze high-traffic segments
print("High-Traffic Segments (>100 vessels/day):")
print("-" * 80)
high_traffic = rhine.get_high_traffic_segments(threshold=100)
for seg in sorted(high_traffic, key=lambda s: s.traffic_density, reverse=True):
    print(f"  {seg.start} -> {seg.end}: {seg.traffic_density:.0f} vessels/day")
print()

# Analyze high-risk segments
print("High-Risk Navigation Segments (risk >= 3):")
print("-" * 80)
high_risk = rhine.get_high_risk_segments(min_risk=3)
for seg in sorted(high_risk, key=lambda s: s.risk_level, reverse=True):
    print(f"  {seg.start} -> {seg.end}: Risk level {seg.risk_level}")
    if seg.locks > 0:
        print(f"    ({seg.locks} locks, depth: {seg.depth}m)")
print()

# Calculate example routes
print("Example Routes:")
print("-" * 80)
routes = [
    ("Rotterdam", "Basel", "length"),
    ("Rotterdam", "Duisburg", "length"),
    ("Mannheim", "Rotterdam", "risk"),
]

for origin, dest, criterion in routes:
    route, cost = rhine.get_route(origin, dest, criterion=criterion)
    if route:
        print(f"  {origin} -> {dest} (optimized for {criterion}):")
        print(f"    Route: {' -> '.join(route)}")
        print(f"    Total {criterion}: {cost:.1f}")
    else:
        print(f"  {origin} -> {dest}: No route found")
print()

# Generate visualizations
print("Generating Visualizations:")
print("-" * 80)

# 1. Main network map
print("1. Creating spatial network map...")
fig1 = rhine.visualize_network(
    color_by="country",
    save_path=RESULTS_DIR / "rhine_network_spatial.png"
)
print(f"   Saved to: rhine_network_spatial.png")

# 2. Traffic flow visualization
print("2. Creating traffic flow analysis...")
fig2 = rhine.visualize_traffic_flow(
    save_path=RESULTS_DIR / "rhine_traffic_flow.png"
)
print(f"   Saved to: rhine_traffic_flow.png")

# 3. Risk profile
print("3. Creating navigation risk profile...")
fig3 = rhine.visualize_risk_profile(
    save_path=RESULTS_DIR / "rhine_risk_profile.png"
)
print(f"   Saved to: rhine_risk_profile.png")

# 4. Alternative visualizations with different color schemes
print("4. Creating capacity-based visualization...")
fig4 = rhine.visualize_network(
    color_by="capacity",
    save_path=RESULTS_DIR / "rhine_network_capacity.png"
)
print(f"   Saved to: rhine_network_capacity.png")

print()

# Analyze network connectivity
print("Network Connectivity Analysis:")
print("-" * 80)
major_ports = ["Rotterdam", "Duisburg", "Cologne", "Mannheim", "Strasbourg", "Basel"]
print("Downstream neighbors (towards North Sea):")
for port in major_ports:
    neighbors = rhine.get_neighbors(port, direction="downstream")
    if neighbors:
        print(f"  {port}: {', '.join(neighbors)}")

print()
print("Upstream neighbors (towards Basel):")
for port in major_ports:
    neighbors = rhine.get_neighbors(port, direction="upstream")
    if neighbors:
        print(f"  {port}: {', '.join(neighbors)}")

print()
print("=" * 80)
print("Rhine River Network Analysis Complete!")
print(f"All visualizations saved to: {RESULTS_DIR.absolute()}")
print("=" * 80)
