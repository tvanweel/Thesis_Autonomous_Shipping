"""
Rhine River Network Model

Models the main Rhine corridor from Rotterdam to Basel with nodes representing:
- Major ports and transshipment points
- Lock complexes
- River confluences and intersections
- Important navigational waypoints

Uses real-world distances and infrastructure locations.
"""

import networkx as nx
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


@dataclass
class RhineNode:
    """Represents a node in the Rhine network."""
    name: str
    node_type: str  # 'port', 'lock', 'confluence', 'waypoint'
    river_km: float  # Distance from North Sea in km
    coordinates: Tuple[float, float]  # (latitude, longitude)
    country: str
    description: str
    capacity: Optional[float] = None  # Annual capacity in tonnes (for ports)


class RhineNetwork:
    """
    Network model of the Rhine River corridor.

    The Rhine flows from Basel (Switzerland) at km 170 through Germany,
    France, and the Netherlands to the North Sea at km 1036.

    River kilometers are measured from the North Sea upstream.
    """

    def __init__(self):
        """Initialize the Rhine network with real infrastructure."""
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, RhineNode] = {}

        # Build the network
        self._initialize_nodes()
        self._initialize_edges()

    def _initialize_nodes(self):
        """Initialize all nodes with real Rhine infrastructure."""

        nodes_data = [
            # Netherlands - Lower Rhine Delta
            RhineNode(
                name="Rotterdam_Port",
                node_type="port",
                river_km=1004,
                coordinates=(51.9244, 4.4777),
                country="NL",
                description="Europe's largest port, Rotterdam Europoort",
                capacity=469000000
            ),
            RhineNode(
                name="Botlek_Locks",
                node_type="lock",
                river_km=1000,
                coordinates=(51.9089, 4.3167),
                country="NL",
                description="Botlek lock complex, tide barrier"
            ),
            RhineNode(
                name="Dordrecht",
                node_type="port",
                river_km=980,
                coordinates=(51.8133, 4.6739),
                country="NL",
                description="Major inland port, historical trading city"
            ),
            RhineNode(
                name="Nijmegen",
                node_type="port",
                river_km=885,
                coordinates=(51.8426, 5.8550),
                country="NL",
                description="Oldest city in Netherlands, Waal crossing"
            ),
            RhineNode(
                name="Lobith_Border",
                node_type="waypoint",
                river_km=859,
                coordinates=(51.8592, 6.1089),
                country="NL",
                description="Dutch-German border crossing point"
            ),

            # Germany - Lower Rhine (Niederrhein)
            RhineNode(
                name="Emmerich",
                node_type="port",
                river_km=852,
                coordinates=(51.8319, 6.2475),
                country="DE",
                description="First German port, border town"
            ),
            RhineNode(
                name="Wesel",
                node_type="port",
                river_km=814,
                coordinates=(51.6589, 6.6289),
                country="DE",
                description="Lippe River confluence, industrial port"
            ),
            RhineNode(
                name="Rheinberg_Orsoy",
                node_type="lock",
                river_km=795,
                coordinates=(51.5439, 6.6833),
                country="DE",
                description="Double lock complex"
            ),
            RhineNode(
                name="Duisburg_Port",
                node_type="port",
                river_km=774,
                coordinates=(51.4344, 6.7623),
                country="DE",
                description="World's largest inland port, Ruhr confluence",
                capacity=50000000
            ),
            RhineNode(
                name="Krefeld_Uerdingen",
                node_type="port",
                river_km=762,
                coordinates=(51.3586, 6.6833),
                country="DE",
                description="Chemical industry port"
            ),
            RhineNode(
                name="Dusseldorf",
                node_type="port",
                river_km=744,
                coordinates=(51.2277, 6.7735),
                country="DE",
                description="State capital, major business center"
            ),
            RhineNode(
                name="Neuss",
                node_type="port",
                river_km=740,
                coordinates=(51.2028, 6.6922),
                country="DE",
                description="Erft River mouth, industrial port"
            ),
            RhineNode(
                name="Dormagen",
                node_type="waypoint",
                river_km=720,
                coordinates=(51.0958, 6.8406),
                country="DE",
                description="Chemical industry complex"
            ),
            RhineNode(
                name="Cologne_Port",
                node_type="port",
                river_km=688,
                coordinates=(50.9375, 6.9603),
                country="DE",
                description="Major city, Cologne Cathedral, trading hub"
            ),
            RhineNode(
                name="Bonn",
                node_type="port",
                river_km=655,
                coordinates=(50.7374, 7.0982),
                country="DE",
                description="Former capital, government district"
            ),

            # Germany - Middle Rhine (Mittelrhein) - UNESCO World Heritage
            RhineNode(
                name="Andernach",
                node_type="waypoint",
                river_km=612,
                coordinates=(50.4394, 7.4014),
                country="DE",
                description="Volcanic Eifel region entrance"
            ),
            RhineNode(
                name="Koblenz",
                node_type="confluence",
                river_km=593,
                coordinates=(50.3569, 7.5889),
                country="DE",
                description="Deutsche Eck - Rhine-Moselle confluence",
                capacity=5000000
            ),
            RhineNode(
                name="Bingen",
                node_type="waypoint",
                river_km=526,
                coordinates=(49.9672, 7.8994),
                country="DE",
                description="Nahe River confluence, Bingen Hole narrows"
            ),
            RhineNode(
                name="Mainz",
                node_type="confluence",
                river_km=498,
                coordinates=(50.0000, 8.2711),
                country="DE",
                description="Main River confluence, state capital"
            ),

            # Germany - Upper Rhine (Oberrhein)
            RhineNode(
                name="Wiesbaden_Schierstein",
                node_type="lock",
                river_km=489,
                coordinates=(50.0333, 8.2347),
                country="DE",
                description="Schierstein lock and harbor"
            ),
            RhineNode(
                name="Mainz_Kostheim",
                node_type="lock",
                river_km=493,
                coordinates=(50.0044, 8.3119),
                country="DE",
                description="Kostheim lock complex"
            ),
            RhineNode(
                name="Gernsheim",
                node_type="waypoint",
                river_km=460,
                coordinates=(49.7547, 8.4900),
                country="DE",
                description="Upper Rhine navigation waypoint"
            ),
            RhineNode(
                name="Mannheim_Port",
                node_type="port",
                river_km=424,
                coordinates=(49.4875, 8.4660),
                country="DE",
                description="Major port, Neckar confluence",
                capacity=7500000
            ),
            RhineNode(
                name="Ludwigshafen",
                node_type="port",
                river_km=420,
                coordinates=(49.4814, 8.4353),
                country="DE",
                description="BASF chemical complex, opposite Mannheim"
            ),
            RhineNode(
                name="Speyer",
                node_type="waypoint",
                river_km=400,
                coordinates=(49.3197, 8.4317),
                country="DE",
                description="Historical cathedral city"
            ),
            RhineNode(
                name="Karlsruhe_Port",
                node_type="port",
                river_km=360,
                coordinates=(49.0094, 8.4044),
                country="DE",
                description="Baden region port, oil refinery"
            ),

            # Germany-France Border Region
            RhineNode(
                name="Iffezheim_Locks",
                node_type="lock",
                river_km=334,
                coordinates=(48.8253, 8.1542),
                country="DE",
                description="Major lock complex, hydroelectric plant"
            ),
            RhineNode(
                name="Kehl",
                node_type="port",
                river_km=296,
                coordinates=(48.5708, 7.8156),
                country="DE",
                description="Border city opposite Strasbourg"
            ),
            RhineNode(
                name="Strasbourg_Port",
                node_type="port",
                river_km=292,
                coordinates=(48.5734, 7.7521),
                country="FR",
                description="Major French Rhine port, EU Parliament",
                capacity=9000000
            ),
            RhineNode(
                name="Gambsheim_Locks",
                node_type="lock",
                river_km=283,
                coordinates=(48.6631, 7.8289),
                country="FR",
                description="French-German lock complex"
            ),
            RhineNode(
                name="Breisach",
                node_type="waypoint",
                river_km=226,
                coordinates=(48.0278, 7.5806),
                country="DE",
                description="Border town, tourist gateway"
            ),

            # Switzerland - High Rhine
            RhineNode(
                name="Basel_Port",
                node_type="port",
                river_km=170,
                coordinates=(47.5596, 7.5886),
                country="CH",
                description="Tri-border area (CH-DE-FR), Rhine knee",
                capacity=6000000
            ),
            RhineNode(
                name="Basel_Rheinhalle",
                node_type="port",
                river_km=167,
                coordinates=(47.5650, 7.5983),
                country="CH",
                description="Basel container terminal, end of navigation"
            ),
        ]

        # Add all nodes to the network
        for node in nodes_data:
            self.nodes[node.name] = node
            self.graph.add_node(
                node.name,
                type=node.node_type,
                river_km=node.river_km,
                coordinates=node.coordinates,
                country=node.country,
                description=node.description,
                capacity=node.capacity
            )

    def _initialize_edges(self):
        """Initialize edges with real distances between consecutive nodes."""

        # Create ordered list of nodes by river kilometer (descending - from sea to source)
        ordered_nodes = sorted(self.nodes.items(), key=lambda x: x[1].river_km, reverse=True)

        # Connect consecutive nodes in both directions
        for i in range(len(ordered_nodes) - 1):
            upstream_name = ordered_nodes[i][0]
            downstream_name = ordered_nodes[i + 1][0]

            upstream_node = ordered_nodes[i][1]
            downstream_node = ordered_nodes[i + 1][1]

            # Calculate distance
            distance = upstream_node.river_km - downstream_node.river_km

            # Add bidirectional edges
            # Downstream (with current)
            self.graph.add_edge(
                upstream_name,
                downstream_name,
                distance=distance,
                direction="downstream"
            )

            # Upstream (against current - typically slower)
            self.graph.add_edge(
                downstream_name,
                upstream_name,
                distance=distance,
                direction="upstream"
            )

    def get_route(
        self,
        origin: str,
        destination: str,
        weight: str = "distance"
    ) -> Tuple[List[str], float]:
        """
        Find route between two nodes.

        Args:
            origin: Starting node name
            destination: Ending node name
            weight: Edge attribute to minimize (default: distance)

        Returns:
            Tuple of (route as list of node names, total distance/weight)
        """
        try:
            route = nx.shortest_path(self.graph, origin, destination, weight=weight)
            total_distance = nx.shortest_path_length(self.graph, origin, destination, weight=weight)
            return route, total_distance
        except nx.NetworkXNoPath:
            return [], 0.0

    def get_node_info(self, node_name: str) -> Optional[RhineNode]:
        """Get detailed information about a node."""
        return self.nodes.get(node_name)

    def get_nodes_by_type(self, node_type: str) -> List[RhineNode]:
        """Get all nodes of a specific type."""
        return [node for node in self.nodes.values() if node.node_type == node_type]

    def get_network_statistics(self) -> Dict:
        """Get overall network statistics."""
        node_counts = {}
        for node in self.nodes.values():
            node_counts[node.node_type] = node_counts.get(node.node_type, 0) + 1

        total_length = max(n.river_km for n in self.nodes.values()) - min(n.river_km for n in self.nodes.values())

        return {
            "total_nodes": len(self.nodes),
            "node_types": node_counts,
            "total_length_km": total_length,
            "countries": len(set(n.country for n in self.nodes.values())),
            "navigable_range": f"km {min(n.river_km for n in self.nodes.values())} to {max(n.river_km for n in self.nodes.values())}"
        }

    def visualize(self, save_path: Optional[str] = None, figsize: Tuple[int, int] = (16, 12)):
        """
        Visualize the Rhine network with geographic layout.

        Args:
            save_path: Optional path to save figure
            figsize: Figure size
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

        # Layout 1: Geographic coordinates
        pos_geo = {name: (node.coordinates[1], node.coordinates[0])
                   for name, node in self.nodes.items()}

        # Layout 2: River kilometer linear layout
        pos_linear = {}
        y_offset = {
            'NL': 0, 'DE': 0.3, 'FR': -0.3, 'CH': 0
        }
        for name, node in self.nodes.items():
            # X-axis: river km, Y-axis: country offset for visibility
            pos_linear[name] = (node.river_km, y_offset.get(node.country, 0))

        # Color nodes by type
        color_map = {
            'port': '#2E86AB',
            'lock': '#A23B72',
            'confluence': '#F18F01',
            'waypoint': '#C73E1D'
        }
        node_colors = [color_map.get(self.nodes[name].node_type, '#666666')
                      for name in self.graph.nodes()]

        # Size nodes by importance
        node_sizes = []
        for name in self.graph.nodes():
            node = self.nodes[name]
            if node.node_type == 'port' and node.capacity:
                size = min(3000, 300 + node.capacity / 10000000)
            elif node.node_type == 'port':
                size = 500
            elif node.node_type == 'lock':
                size = 400
            elif node.node_type == 'confluence':
                size = 600
            else:
                size = 200
            node_sizes.append(size)

        # Plot 1: Geographic view
        nx.draw_networkx_nodes(
            self.graph, pos_geo, ax=ax1,
            node_color=node_colors,
            node_size=node_sizes,
            alpha=0.8
        )
        nx.draw_networkx_edges(
            self.graph, pos_geo, ax=ax1,
            edge_color='#cccccc',
            arrows=False,
            width=1.5
        )

        # Add labels for major ports only (to avoid clutter)
        major_port_names = [name for name, node in self.nodes.items()
                           if node.node_type == 'port' and node.capacity and node.capacity > 5000000]

        labels_to_draw = {name: name for name in major_port_names}
        pos_to_use = {name: pos_geo[name] for name in major_port_names}

        if labels_to_draw:
            nx.draw_networkx_labels(
                self.graph, pos_to_use,
                labels=labels_to_draw,
                ax=ax1,
                font_size=8,
                font_weight='bold'
            )

        ax1.set_title("Rhine Corridor - Geographic View", fontsize=14, fontweight='bold')
        ax1.set_xlabel("Longitude", fontsize=11)
        ax1.set_ylabel("Latitude", fontsize=11)
        ax1.grid(True, alpha=0.3)

        # Plot 2: Linear river kilometer view
        nx.draw_networkx_nodes(
            self.graph, pos_linear, ax=ax2,
            node_color=node_colors,
            node_size=node_sizes,
            alpha=0.8
        )
        nx.draw_networkx_edges(
            self.graph, pos_linear, ax=ax2,
            edge_color='#cccccc',
            arrows=False,
            width=1.5
        )

        # Add selective labels in linear view (avoid clutter)
        sorted_names = sorted(self.graph.nodes(), key=lambda x: self.nodes[x].river_km, reverse=True)
        labels_linear = {}
        pos_linear_subset = {}

        for i, name in enumerate(sorted_names):
            # Label every 3rd node or major infrastructure
            node = self.nodes[name]
            if i % 3 == 0 or node.node_type in ['port', 'lock', 'confluence']:
                labels_linear[name] = name
                pos_linear_subset[name] = pos_linear[name]

        nx.draw_networkx_labels(
            self.graph, pos_linear_subset,
            labels=labels_linear,
            ax=ax2,
            font_size=7,
            font_weight='bold'
        )

        ax2.set_title("Rhine Corridor - River Kilometer View", fontsize=14, fontweight='bold')
        ax2.set_xlabel("River Kilometer (from North Sea)", fontsize=11)
        ax2.set_ylabel("Country Offset", fontsize=11)
        ax2.grid(True, alpha=0.3, axis='x')
        ax2.set_xlim(150, 1020)

        # Add legend
        legend_elements = [
            mpatches.Patch(color=color_map['port'], label='Major Port'),
            mpatches.Patch(color=color_map['lock'], label='Lock Complex'),
            mpatches.Patch(color=color_map['confluence'], label='River Confluence'),
            mpatches.Patch(color=color_map['waypoint'], label='Waypoint')
        ]
        fig.legend(handles=legend_elements, loc='upper center',
                  bbox_to_anchor=(0.5, 0.98), ncol=4, fontsize=10)

        plt.tight_layout(rect=[0, 0, 1, 0.96])

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Network visualization saved to {save_path}")

        return fig

    def print_network_summary(self):
        """Print a detailed summary of the Rhine network."""
        print("=" * 80)
        print("RHINE RIVER CORRIDOR NETWORK")
        print("=" * 80)
        print()

        stats = self.get_network_statistics()
        print("Network Statistics:")
        print(f"  Total nodes: {stats['total_nodes']}")
        print(f"  Total navigable length: {stats['total_length_km']:.1f} km")
        print(f"  Range: {stats['navigable_range']}")
        print(f"  Countries: {stats['countries']}")
        print()

        print("Nodes by Type:")
        for node_type, count in stats['node_types'].items():
            print(f"  {node_type.capitalize()}: {count}")
        print()

        print("=" * 80)
        print("MAJOR INFRASTRUCTURE (Upstream order - Rotterdam to Basel)")
        print("=" * 80)
        print()

        # Print nodes grouped by country
        for country, country_name in [('NL', 'Netherlands'), ('DE', 'Germany'),
                                       ('FR', 'France'), ('CH', 'Switzerland')]:
            country_nodes = [n for n in self.nodes.values() if n.country == country]
            if country_nodes:
                print(f"{country_name}:")
                print("-" * 80)

                # Sort by river km descending (upstream order)
                for node in sorted(country_nodes, key=lambda x: x.river_km, reverse=True):
                    capacity_str = f" | Capacity: {node.capacity/1000000:.1f}M tonnes/year" if node.capacity else ""
                    print(f"  [{node.node_type.upper():10s}] km {node.river_km:5.0f} - {node.name:25s}")
                    print(f"                    {node.description}{capacity_str}")
                print()


def create_rhine_network() -> RhineNetwork:
    """Factory function to create Rhine network."""
    return RhineNetwork()


if __name__ == "__main__":
    # Create and display the network
    rhine = create_rhine_network()
    rhine.print_network_summary()

    # Example: Find route from Rotterdam to Basel
    print("\n" + "=" * 80)
    print("EXAMPLE ROUTE: Rotterdam to Basel")
    print("=" * 80)
    route, distance = rhine.get_route("Rotterdam_Port", "Basel_Port")
    print(f"Total distance: {distance:.1f} km")
    print(f"Route ({len(route)} nodes):")
    for i, node_name in enumerate(route, 1):
        node = rhine.get_node_info(node_name)
        print(f"  {i:2d}. {node_name:25s} (km {node.river_km:5.0f}) - {node.description}")
