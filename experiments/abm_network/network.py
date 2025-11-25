"""
Rhine River Network Model

This module represents the spatial network of the Rhine river system,
including major ports, river segments, locks, and navigational characteristics.

The Rhine is Europe's most important inland waterway, stretching from
Switzerland through Germany and the Netherlands to the North Sea.
"""

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class RhinePort:
    """
    Represents a port or important location on the Rhine.

    Attributes:
        name: Port name
        country: Country code (CH, DE, NL, FR)
        river_km: Distance from Rhine mouth (km)
        coordinates: (latitude, longitude)
        port_type: Type of port (seaport, inland_port, terminal, lock)
        capacity: Annual throughput capacity (tonnes)
        automation_level: Current automation level (L0-L5)
    """
    name: str
    country: str
    river_km: float
    coordinates: Tuple[float, float]
    port_type: str
    capacity: float = 0.0
    automation_level: int = 0
    traffic_volume: float = 0.0
    vessel_count: int = 0

    def __hash__(self):
        return hash(self.name)


@dataclass
class RhineSegment:
    """
    Represents a segment of the Rhine river between two locations.

    Attributes:
        start: Starting port/location name
        end: Ending port/location name
        length: Segment length (km)
        depth: Minimum depth (meters)
        width: Average width (meters)
        locks: Number of locks in segment
        traffic_density: Vessels per day
        risk_level: Navigation risk level (1-5)
    """
    start: str
    end: str
    length: float
    depth: float = 3.0
    width: float = 200.0
    locks: int = 0
    traffic_density: float = 0.0
    risk_level: int = 1


class RhineNetwork:
    """
    Spatial network model of the Rhine river system.

    This class creates and manages a directed graph representing the Rhine river,
    with nodes as ports/locations and edges as navigable river segments.
    """

    def __init__(self):
        """Initialize Rhine network with major ports and segments."""
        self.graph = nx.DiGraph()
        self.ports: Dict[str, RhinePort] = {}
        self.segments: List[RhineSegment] = []

        self._initialize_ports()
        self._initialize_segments()
        self._build_graph()

    def _initialize_ports(self):
        """Initialize major Rhine ports and locations."""
        # Major ports from Rhine mouth (km 0) to Basel (km 832)
        # River km measured from Hoek van Holland (North Sea)

        ports_data = [
            # Netherlands
            RhinePort("Rotterdam", "NL", 1025, (51.92, 4.48), "seaport",
                     capacity=140000000, traffic_volume=35000, vessel_count=6000),
            RhinePort("Dordrecht", "NL", 982, (51.81, 4.67), "inland_port",
                     capacity=15000000, traffic_volume=8000, vessel_count=800),
            RhinePort("Nijmegen", "NL", 885, (51.85, 5.87), "inland_port",
                     capacity=5000000, traffic_volume=5000, vessel_count=500),
            RhinePort("Arnhem", "NL", 890, (51.98, 5.91), "inland_port",
                     capacity=3000000, traffic_volume=3000, vessel_count=300),

            # Germany - Lower Rhine
            RhinePort("Emmerich", "DE", 852, (51.83, 6.25), "inland_port",
                     capacity=2000000, traffic_volume=4000, vessel_count=400),
            RhinePort("Wesel", "DE", 814, (51.67, 6.62), "inland_port",
                     capacity=4000000, traffic_volume=3500, vessel_count=350),
            RhinePort("Duisburg", "DE", 774, (51.43, 6.76), "inland_port",
                     capacity=50000000, traffic_volume=20000, vessel_count=2500),
            RhinePort("Dusseldorf", "DE", 744, (51.23, 6.77), "inland_port",
                     capacity=8000000, traffic_volume=5000, vessel_count=600),
            RhinePort("Cologne", "DE", 688, (50.94, 6.96), "inland_port",
                     capacity=10000000, traffic_volume=7000, vessel_count=800),
            RhinePort("Bonn", "DE", 655, (50.73, 7.10), "inland_port",
                     capacity=2000000, traffic_volume=2000, vessel_count=200),

            # Germany - Middle Rhine
            RhinePort("Koblenz", "DE", 593, (50.36, 7.60), "inland_port",
                     capacity=3000000, traffic_volume=3000, vessel_count=350),
            RhinePort("Mainz", "DE", 498, (50.00, 8.27), "inland_port",
                     capacity=5000000, traffic_volume=4000, vessel_count=450),

            # Germany - Upper Rhine
            RhinePort("Mannheim", "DE", 424, (49.49, 8.47), "inland_port",
                     capacity=8000000, traffic_volume=6000, vessel_count=700),
            RhinePort("Ludwigshafen", "DE", 420, (49.48, 8.43), "inland_port",
                     capacity=6000000, traffic_volume=5000, vessel_count=600),
            RhinePort("Karlsruhe", "DE", 360, (49.01, 8.40), "inland_port",
                     capacity=7000000, traffic_volume=5500, vessel_count=650),
            RhinePort("Kehl", "DE", 292, (48.57, 7.81), "inland_port",
                     capacity=3000000, traffic_volume=3000, vessel_count=300),

            # France
            RhinePort("Strasbourg", "FR", 296, (48.58, 7.75), "inland_port",
                     capacity=9000000, traffic_volume=6000, vessel_count=700),

            # Switzerland
            RhinePort("Basel", "CH", 170, (47.56, 7.59), "inland_port",
                     capacity=6000000, traffic_volume=4000, vessel_count=500),
        ]

        for port in ports_data:
            self.ports[port.name] = port

    def _initialize_segments(self):
        """Initialize Rhine river segments between ports."""
        # Define segments with navigational characteristics
        # Segments listed from downstream (North Sea) to upstream (Basel)

        segments_data = [
            # Netherlands - Lower Rhine Delta
            RhineSegment("Rotterdam", "Dordrecht", 43, depth=11.0, width=500, locks=0,
                        traffic_density=200, risk_level=3),
            RhineSegment("Dordrecht", "Nijmegen", 97, depth=6.5, width=400, locks=0,
                        traffic_density=150, risk_level=2),
            RhineSegment("Nijmegen", "Arnhem", 5, depth=5.5, width=350, locks=0,
                        traffic_density=120, risk_level=2),

            # Germany - Lower Rhine
            RhineSegment("Arnhem", "Emmerich", 38, depth=5.0, width=300, locks=0,
                        traffic_density=110, risk_level=2),
            RhineSegment("Emmerich", "Wesel", 38, depth=4.5, width=280, locks=0,
                        traffic_density=100, risk_level=2),
            RhineSegment("Wesel", "Duisburg", 40, depth=4.2, width=250, locks=0,
                        traffic_density=140, risk_level=3),
            RhineSegment("Duisburg", "Dusseldorf", 30, depth=4.0, width=240, locks=0,
                        traffic_density=130, risk_level=3),
            RhineSegment("Dusseldorf", "Cologne", 56, depth=3.8, width=230, locks=0,
                        traffic_density=120, risk_level=2),
            RhineSegment("Cologne", "Bonn", 33, depth=3.5, width=220, locks=0,
                        traffic_density=100, risk_level=2),

            # Germany - Middle Rhine (narrow valleys, more difficult navigation)
            RhineSegment("Bonn", "Koblenz", 62, depth=3.2, width=180, locks=0,
                        traffic_density=90, risk_level=4),
            RhineSegment("Koblenz", "Mainz", 95, depth=3.0, width=160, locks=0,
                        traffic_density=80, risk_level=4),

            # Germany - Upper Rhine (canalized)
            RhineSegment("Mainz", "Mannheim", 74, depth=4.0, width=200, locks=2,
                        traffic_density=85, risk_level=3),
            RhineSegment("Mannheim", "Ludwigshafen", 4, depth=4.0, width=200, locks=0,
                        traffic_density=85, risk_level=2),
            RhineSegment("Ludwigshafen", "Karlsruhe", 60, depth=3.8, width=190, locks=2,
                        traffic_density=75, risk_level=3),
            RhineSegment("Karlsruhe", "Kehl", 68, depth=3.5, width=180, locks=3,
                        traffic_density=65, risk_level=3),
            RhineSegment("Kehl", "Strasbourg", 4, depth=3.5, width=180, locks=0,
                        traffic_density=60, risk_level=2),
            RhineSegment("Strasbourg", "Basel", 126, depth=3.0, width=150, locks=4,
                        traffic_density=50, risk_level=4),
        ]

        self.segments = segments_data

    def _build_graph(self):
        """Build NetworkX graph from ports and segments."""
        # Add nodes with port attributes
        for port_name, port in self.ports.items():
            self.graph.add_node(
                port_name,
                country=port.country,
                river_km=port.river_km,
                coordinates=port.coordinates,
                port_type=port.port_type,
                capacity=port.capacity,
                automation_level=port.automation_level,
                traffic_volume=port.traffic_volume,
                vessel_count=port.vessel_count,
            )

        # Add edges (bidirectional for river segments)
        for segment in self.segments:
            # Downstream direction (towards North Sea)
            self.graph.add_edge(
                segment.start,
                segment.end,
                length=segment.length,
                depth=segment.depth,
                width=segment.width,
                locks=segment.locks,
                traffic_density=segment.traffic_density,
                risk_level=segment.risk_level,
                direction="downstream"
            )

            # Upstream direction (towards Basel)
            self.graph.add_edge(
                segment.end,
                segment.start,
                length=segment.length,
                depth=segment.depth,
                width=segment.width,
                locks=segment.locks,
                traffic_density=segment.traffic_density,
                risk_level=segment.risk_level,
                direction="upstream"
            )

    def get_route(self, origin: str, destination: str,
                  criterion: str = "length") -> Tuple[List[str], float]:
        """
        Find optimal route between two ports.

        Args:
            origin: Starting port name
            destination: Destination port name
            criterion: Optimization criterion ('length', 'risk', 'locks')

        Returns:
            Tuple of (route as list of port names, total cost)
        """
        if criterion == "length":
            weight = "length"
        elif criterion == "risk":
            weight = "risk_level"
        elif criterion == "locks":
            weight = "locks"
        else:
            raise ValueError(f"Unknown criterion: {criterion}")

        try:
            route = nx.shortest_path(self.graph, origin, destination, weight=weight)
            cost = nx.shortest_path_length(self.graph, origin, destination, weight=weight)
            return route, cost
        except nx.NetworkXNoPath:
            return [], float('inf')

    def get_neighbors(self, port: str, direction: str = "both") -> List[str]:
        """
        Get neighboring ports.

        Args:
            port: Port name
            direction: 'upstream', 'downstream', or 'both'

        Returns:
            List of neighboring port names
        """
        if direction == "both":
            return list(self.graph.neighbors(port))

        neighbors = []
        for neighbor in self.graph.neighbors(port):
            edge_data = self.graph[port][neighbor]
            if edge_data["direction"] == direction:
                neighbors.append(neighbor)

        return neighbors

    def get_ports_by_country(self, country: str) -> List[RhinePort]:
        """Get all ports in a specific country."""
        return [port for port in self.ports.values() if port.country == country]

    def get_high_traffic_segments(self, threshold: float = 100) -> List[RhineSegment]:
        """Get segments with traffic density above threshold."""
        return [seg for seg in self.segments if seg.traffic_density >= threshold]

    def get_high_risk_segments(self, min_risk: int = 3) -> List[RhineSegment]:
        """Get segments with risk level at or above threshold."""
        return [seg for seg in self.segments if seg.risk_level >= min_risk]

    def calculate_total_distance(self) -> float:
        """Calculate total navigable distance in network."""
        return sum(seg.length for seg in self.segments)

    def get_network_statistics(self) -> Dict[str, any]:
        """Calculate network statistics."""
        stats = {
            "total_ports": len(self.ports),
            "total_segments": len(self.segments),
            "total_distance_km": self.calculate_total_distance(),
            "countries": len(set(p.country for p in self.ports.values())),
            "total_locks": sum(seg.locks for seg in self.segments),
            "avg_segment_length": np.mean([seg.length for seg in self.segments]),
            "avg_traffic_density": np.mean([seg.traffic_density for seg in self.segments]),
            "total_capacity": sum(p.capacity for p in self.ports.values()),
            "avg_risk_level": np.mean([seg.risk_level for seg in self.segments]),
            "graph_density": nx.density(self.graph),
            "avg_degree": sum(dict(self.graph.degree()).values()) / len(self.graph.nodes()),
        }
        return stats

    def visualize_network(self,
                         figsize: Tuple[int, int] = (16, 12),
                         show_labels: bool = True,
                         color_by: str = "country",
                         save_path: Optional[Path] = None) -> plt.Figure:
        """
        Visualize Rhine network as a spatial graph.

        Args:
            figsize: Figure size
            show_labels: Whether to show port labels
            color_by: Node coloring scheme ('country', 'capacity', 'automation')
            save_path: Path to save figure

        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Use geographical coordinates for positioning
        pos = {name: port.coordinates for name, port in self.ports.items()}

        # Flip coordinates for proper map orientation (lat, lon -> x, y)
        pos = {name: (coord[1], coord[0]) for name, coord in pos.items()}

        # Node colors based on criterion
        if color_by == "country":
            country_colors = {"NL": "#FF6B35", "DE": "#004E89", "FR": "#1A659E", "CH": "#C1292E"}
            node_colors = [country_colors.get(self.ports[node].country, "#808080")
                          for node in self.graph.nodes()]
        elif color_by == "capacity":
            capacities = [self.ports[node].capacity for node in self.graph.nodes()]
            node_colors = capacities
        elif color_by == "automation":
            node_colors = [self.ports[node].automation_level for node in self.graph.nodes()]
        else:
            node_colors = "#004E89"

        # Node sizes based on traffic volume
        node_sizes = [self.ports[node].traffic_volume / 50 for node in self.graph.nodes()]
        node_sizes = [max(size, 100) for size in node_sizes]  # Minimum size

        # Draw edges (only downstream to avoid duplication)
        downstream_edges = [(u, v) for u, v, d in self.graph.edges(data=True)
                           if d["direction"] == "downstream"]

        # Edge colors based on risk level
        edge_colors = []
        for u, v in downstream_edges:
            risk = self.graph[u][v]["risk_level"]
            if risk >= 4:
                edge_colors.append("#E63946")  # High risk - red
            elif risk == 3:
                edge_colors.append("#F77F00")  # Medium risk - orange
            else:
                edge_colors.append("#06AED5")  # Low risk - blue

        # Edge widths based on traffic density
        edge_widths = [self.graph[u][v]["traffic_density"] / 30 for u, v in downstream_edges]
        edge_widths = [max(width, 0.5) for width in edge_widths]

        # Draw network
        nx.draw_networkx_edges(
            self.graph,
            pos,
            edgelist=downstream_edges,
            edge_color=edge_colors,
            width=edge_widths,
            alpha=0.6,
            arrows=False,
            ax=ax
        )

        nx.draw_networkx_nodes(
            self.graph,
            pos,
            node_size=node_sizes,
            node_color=node_colors,
            alpha=0.9,
            edgecolors="black",
            linewidths=2,
            ax=ax
        )

        if show_labels:
            # Only label major ports
            major_ports = {name: name for name in self.graph.nodes()
                          if self.ports[name].capacity > 5000000}
            nx.draw_networkx_labels(
                self.graph,
                pos,
                labels=major_ports,
                font_size=9,
                font_weight="bold",
                font_color="white",
                ax=ax
            )

        # Add legend
        if color_by == "country":
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='#FF6B35', label='Netherlands'),
                Patch(facecolor='#004E89', label='Germany'),
                Patch(facecolor='#1A659E', label='France'),
                Patch(facecolor='#C1292E', label='Switzerland'),
            ]
            ax.legend(handles=legend_elements, loc='upper left', fontsize=10)

        ax.set_title("Rhine River Network: Spatial Structure",
                    fontsize=16, fontweight="bold", pad=20)
        ax.set_xlabel("Longitude", fontsize=12)
        ax.set_ylabel("Latitude", fontsize=12)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        return fig

    def visualize_traffic_flow(self,
                               figsize: Tuple[int, int] = (14, 10),
                               save_path: Optional[Path] = None) -> plt.Figure:
        """Visualize traffic flow and density along the Rhine."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

        # Left plot: Traffic density by segment
        segment_names = [f"{seg.start[:3]}-{seg.end[:3]}" for seg in self.segments]
        traffic_densities = [seg.traffic_density for seg in self.segments]
        colors = ['#E63946' if td > 100 else '#F77F00' if td > 60 else '#06AED5'
                 for td in traffic_densities]

        ax1.barh(segment_names, traffic_densities, color=colors, alpha=0.7, edgecolor='black')
        ax1.set_xlabel("Traffic Density (vessels/day)", fontsize=11)
        ax1.set_ylabel("River Segment", fontsize=11)
        ax1.set_title("Traffic Density by Segment", fontsize=12, fontweight="bold")
        ax1.grid(True, alpha=0.3, axis='x')

        # Right plot: Port capacity
        port_names = [port.name for port in sorted(self.ports.values(),
                     key=lambda p: p.capacity, reverse=True)[:12]]
        capacities = [self.ports[name].capacity / 1000000 for name in port_names]  # In millions

        ax2.barh(port_names, capacities, color='#004E89', alpha=0.7, edgecolor='black')
        ax2.set_xlabel("Annual Capacity (million tonnes)", fontsize=11)
        ax2.set_ylabel("Port", fontsize=11)
        ax2.set_title("Top 12 Ports by Capacity", fontsize=12, fontweight="bold")
        ax2.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        return fig

    def visualize_risk_profile(self,
                              figsize: Tuple[int, int] = (14, 8),
                              save_path: Optional[Path] = None) -> plt.Figure:
        """Visualize navigation risk profile along the Rhine."""
        fig, ax = plt.subplots(figsize=figsize)

        # Calculate cumulative distance and plot risk by location
        cumulative_dist = 0
        distances = []
        risk_levels = []
        segment_labels = []

        for seg in self.segments:
            distances.append(cumulative_dist)
            risk_levels.append(seg.risk_level)
            segment_labels.append(seg.start)
            cumulative_dist += seg.length

        # Add final point
        distances.append(cumulative_dist)
        risk_levels.append(self.segments[-1].risk_level)

        # Create step plot
        ax.step(distances, risk_levels, where='post', linewidth=2.5, color='#004E89')
        ax.fill_between(distances, risk_levels, step='post', alpha=0.3, color='#004E89')

        # Add risk zones
        ax.axhline(y=3, color='#F77F00', linestyle='--', alpha=0.5, label='Medium Risk Threshold')
        ax.axhline(y=4, color='#E63946', linestyle='--', alpha=0.5, label='High Risk Threshold')

        # Annotate major ports
        major_ports_dist = {}
        cumulative = 0
        for seg in self.segments:
            if self.ports[seg.start].capacity > 8000000:
                major_ports_dist[seg.start] = cumulative
            cumulative += seg.length

        for port, dist in major_ports_dist.items():
            ax.axvline(x=dist, color='gray', linestyle=':', alpha=0.3)
            ax.text(dist, 4.5, port, rotation=90, va='bottom', fontsize=8)

        ax.set_xlabel("Distance from Rotterdam (km)", fontsize=12)
        ax.set_ylabel("Risk Level", fontsize=12)
        ax.set_title("Navigation Risk Profile Along the Rhine", fontsize=14, fontweight="bold")
        ax.set_ylim(0, 5)
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        return fig


def create_rhine_network() -> RhineNetwork:
    """
    Factory function to create a Rhine network instance.

    Returns:
        Configured RhineNetwork object
    """
    return RhineNetwork()
