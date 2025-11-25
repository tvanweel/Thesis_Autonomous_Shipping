"""
Network graph visualization for multi-level automation diffusion model.

This module creates network-based visualizations to show:
1. Relationships between automation levels
2. Adoption flows and transitions
3. Market potential distribution
4. Hierarchical structure of automation levels
"""

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Tuple

from src.models.diffusion import MultiLevelAutomationDiffusion
from src.config import DiffusionConfig


class DiffusionNetworkGraph:
    """
    Creates network graph visualizations for the diffusion model.

    The network represents:
    - Nodes: Automation levels (L0-L5)
    - Node size: Number of vessels at each level
    - Node color: Automation level category
    - Edges: Potential transitions between levels
    - Edge weight: Strength of transition/influence
    """

    def __init__(self, model: MultiLevelAutomationDiffusion, timestep: Optional[int] = None):
        """
        Initialize network graph from diffusion model.

        Args:
            model: MultiLevelAutomationDiffusion instance (after running simulation)
            timestep: Which timestep to visualize (default: last timestep)
        """
        self.model = model
        self.timestep = timestep if timestep is not None else len(model.history_time) - 1

        if self.timestep >= len(model.history_time):
            raise ValueError(f"Timestep {self.timestep} exceeds simulation length {len(model.history_time)}")

        self.graph = nx.DiGraph()
        self._build_graph()

    def _calculate_L0(self) -> float:
        """Calculate L0 (manual vessels) at current timestep."""
        L1 = self.model.history_L1[self.timestep]
        L2 = self.model.history_L2[self.timestep]
        L3 = self.model.history_L3[self.timestep]
        L4 = self.model.history_L4[self.timestep]
        L5 = self.model.history_L5[self.timestep]
        return self.model.total_fleet - (L1 + L2 + L3 + L4 + L5)

    def _build_graph(self):
        """Build the network graph structure."""
        # Get vessel counts at current timestep
        vessel_counts = {
            "L0": self._calculate_L0(),
            "L1": self.model.history_L1[self.timestep],
            "L2": self.model.history_L2[self.timestep],
            "L3": self.model.history_L3[self.timestep],
            "L4": self.model.history_L4[self.timestep],
            "L5": self.model.history_L5[self.timestep],
        }

        # Market potentials
        market_potentials = {
            "L0": self.model.total_fleet,  # All vessels can be manual
            "L1": self.model.M1,
            "L2": self.model.M2,
            "L3": self.model.M3,
            "L4": self.model.M4,
            "L5": self.model.M5,
        }

        # Add nodes with attributes
        level_descriptions = {
            "L0": "Manual",
            "L1": "Steering Assistance",
            "L2": "Partial Automation",
            "L3": "Conditional Automation",
            "L4": "High Automation",
            "L5": "Full Automation",
        }

        for level, count in vessel_counts.items():
            self.graph.add_node(
                level,
                vessels=count,
                market_potential=market_potentials[level],
                description=level_descriptions[level],
                adoption_rate=count / self.model.total_fleet if self.model.total_fleet > 0 else 0
            )

        # Add edges representing potential transitions
        # Hierarchical progression: L0 -> L1 -> L2 -> L3 -> L4 -> L5
        transitions = [
            ("L0", "L1"),
            ("L1", "L2"),
            ("L2", "L3"),
            ("L3", "L4"),
            ("L4", "L5"),
        ]

        for source, target in transitions:
            # Calculate transition strength based on adoption rates
            source_vessels = vessel_counts[source]
            target_vessels = vessel_counts[target]

            # Weight represents potential for transition
            if source_vessels > 0:
                weight = target_vessels / source_vessels
            else:
                weight = 0.0

            self.graph.add_edge(source, target, weight=weight, transition_type="progressive")

        # Add competitive edges (vessels can also jump levels or compete)
        competitive_edges = [
            ("L0", "L2"),  # Direct to partial automation
            ("L0", "L3"),  # Direct to conditional
            ("L1", "L3"),  # Skip L2
            ("L2", "L4"),  # Skip L3
        ]

        for source, target in competitive_edges:
            if vessel_counts[target] > 0:
                weight = vessel_counts[target] / self.model.total_fleet
                self.graph.add_edge(source, target, weight=weight, transition_type="competitive")

    def get_node_sizes(self, scale: float = 50.0) -> list:
        """
        Get node sizes based on vessel counts.

        Args:
            scale: Scaling factor for node sizes

        Returns:
            List of node sizes
        """
        sizes = []
        for node in self.graph.nodes():
            vessels = self.graph.nodes[node]["vessels"]
            # Ensure minimum visible size
            size = max(vessels * scale, 100)
            sizes.append(size)
        return sizes

    def get_node_colors(self) -> list:
        """Get node colors based on automation level."""
        color_map = {
            "L0": "#2C3E50",  # Dark gray (manual)
            "L1": "#3498DB",  # Blue (steering assistance)
            "L2": "#2ECC71",  # Green (partial automation)
            "L3": "#F39C12",  # Orange (conditional automation)
            "L4": "#E74C3C",  # Red (high automation)
            "L5": "#9B59B6",  # Purple (full automation)
        }
        return [color_map[node] for node in self.graph.nodes()]

    def get_edge_weights(self) -> list:
        """Get edge weights for visualization."""
        return [self.graph[u][v]["weight"] for u, v in self.graph.edges()]

    def plot(
        self,
        figsize: Tuple[int, int] = (14, 10),
        layout: str = "hierarchical",
        show_labels: bool = True,
        show_edge_labels: bool = True,
        save_path: Optional[Path] = None
    ) -> plt.Figure:
        """
        Create network graph visualization.

        Args:
            figsize: Figure size (width, height)
            layout: Layout algorithm ('hierarchical', 'spring', 'circular')
            show_labels: Whether to show node labels
            show_edge_labels: Whether to show edge weights
            save_path: Path to save figure (optional)

        Returns:
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Choose layout
        if layout == "hierarchical":
            pos = self._hierarchical_layout()
        elif layout == "spring":
            pos = nx.spring_layout(self.graph, k=2, iterations=50)
        elif layout == "circular":
            pos = nx.circular_layout(self.graph)
        else:
            raise ValueError(f"Unknown layout: {layout}")

        # Get visual properties
        node_sizes = self.get_node_sizes()
        node_colors = self.get_node_colors()
        edge_weights = self.get_edge_weights()

        # Separate progressive and competitive edges
        progressive_edges = [(u, v) for u, v, d in self.graph.edges(data=True)
                            if d.get("transition_type") == "progressive"]
        competitive_edges = [(u, v) for u, v, d in self.graph.edges(data=True)
                            if d.get("transition_type") == "competitive"]

        # Draw progressive edges (solid lines)
        nx.draw_networkx_edges(
            self.graph,
            pos,
            edgelist=progressive_edges,
            edge_color="#34495E",
            width=2.5,
            alpha=0.7,
            arrows=True,
            arrowsize=20,
            arrowstyle="->",
            connectionstyle="arc3,rad=0.1",
            ax=ax
        )

        # Draw competitive edges (dashed lines)
        nx.draw_networkx_edges(
            self.graph,
            pos,
            edgelist=competitive_edges,
            edge_color="#7F8C8D",
            width=1.5,
            alpha=0.4,
            style="dashed",
            arrows=True,
            arrowsize=15,
            arrowstyle="->",
            connectionstyle="arc3,rad=0.3",
            ax=ax
        )

        # Draw nodes
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

        # Draw node labels
        if show_labels:
            labels = {}
            for node in self.graph.nodes():
                vessels = self.graph.nodes[node]["vessels"]
                desc = self.graph.nodes[node]["description"]
                labels[node] = f"{node}\n{desc}\n{vessels:.0f} vessels"

            nx.draw_networkx_labels(
                self.graph,
                pos,
                labels,
                font_size=9,
                font_weight="bold",
                font_color="white",
                ax=ax
            )

        # Draw edge labels
        if show_edge_labels:
            edge_labels = {}
            for u, v, d in self.graph.edges(data=True):
                weight = d["weight"]
                if weight > 0.01:  # Only show significant weights
                    edge_labels[(u, v)] = f"{weight:.2f}"

            nx.draw_networkx_edge_labels(
                self.graph,
                pos,
                edge_labels,
                font_size=8,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7),
                ax=ax
            )

        # Title and styling
        timestep_label = f"t={self.model.history_time[self.timestep]:.1f}"
        ax.set_title(
            f"Automation Level Network Graph ({timestep_label})\n"
            f"Total Fleet: {self.model.total_fleet:.0f} vessels",
            fontsize=14,
            fontweight="bold",
            pad=20
        )

        ax.axis("off")
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        return fig

    def _hierarchical_layout(self) -> Dict[str, Tuple[float, float]]:
        """Create hierarchical layout for automation levels."""
        levels = ["L0", "L1", "L2", "L3", "L4", "L5"]
        pos = {}

        # Vertical spacing
        for i, level in enumerate(levels):
            x = i * 2.0  # Horizontal spacing
            y = 0.0  # Keep on same level or vary slightly

            # Add some vertical variation based on adoption rate
            if level in self.graph.nodes():
                adoption_rate = self.graph.nodes[level]["adoption_rate"]
                y = adoption_rate * 2.0  # Vary height based on adoption

            pos[level] = (x, y)

        return pos

    def get_network_metrics(self) -> Dict[str, float]:
        """
        Calculate network metrics.

        Returns:
            Dictionary of network metrics
        """
        metrics = {
            "num_nodes": self.graph.number_of_nodes(),
            "num_edges": self.graph.number_of_edges(),
            "density": nx.density(self.graph),
            "avg_degree": sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes(),
        }

        # Calculate centrality measures
        try:
            metrics["avg_betweenness"] = np.mean(list(nx.betweenness_centrality(self.graph).values()))
            metrics["avg_closeness"] = np.mean(list(nx.closeness_centrality(self.graph).values()))
        except:
            metrics["avg_betweenness"] = 0.0
            metrics["avg_closeness"] = 0.0

        return metrics


def create_temporal_network_visualization(
    model: MultiLevelAutomationDiffusion,
    timesteps: list,
    save_dir: Path,
    layout: str = "hierarchical"
) -> None:
    """
    Create multiple network graphs at different timesteps.

    Args:
        model: Diffusion model instance
        timesteps: List of timestep indices to visualize
        save_dir: Directory to save visualizations
        layout: Layout algorithm to use
    """
    save_dir.mkdir(parents=True, exist_ok=True)

    print(f"Creating temporal network visualizations for {len(timesteps)} timesteps...")

    for timestep in timesteps:
        graph = DiffusionNetworkGraph(model, timestep=timestep)
        time_value = model.history_time[timestep]

        save_path = save_dir / f"network_graph_t{time_value:.0f}.png"
        graph.plot(layout=layout, save_path=save_path)

        print(f"  Created graph for t={time_value:.1f} -> {save_path.name}")

    print(f"All temporal visualizations saved to: {save_dir}")


def create_network_summary(config: DiffusionConfig, save_path: Path) -> None:
    """
    Create a comprehensive network visualization summary.

    Args:
        config: Diffusion configuration
        save_path: Path to save the summary visualization
    """
    print("Creating network summary visualization...")

    # Run model
    model = MultiLevelAutomationDiffusion(**config.to_model_params())
    model.run(steps=config.time_horizon)

    # Create figure with multiple network snapshots
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    axes = axes.flatten()

    # Select timesteps to visualize (beginning, middle, end)
    total_steps = len(model.history_time)
    timesteps = [0, total_steps // 5, 2 * total_steps // 5,
                 3 * total_steps // 5, 4 * total_steps // 5, total_steps - 1]

    for idx, timestep in enumerate(timesteps):
        ax = axes[idx]

        # Create network graph
        graph = DiffusionNetworkGraph(model, timestep=timestep)

        # Get layout
        pos = graph._hierarchical_layout()

        # Visual properties
        node_sizes = [s / 10 for s in graph.get_node_sizes()]  # Scale down for subplot
        node_colors = graph.get_node_colors()

        # Draw
        nx.draw_networkx_nodes(
            graph.graph,
            pos,
            node_size=node_sizes,
            node_color=node_colors,
            alpha=0.9,
            edgecolors="black",
            linewidths=1,
            ax=ax
        )

        nx.draw_networkx_edges(
            graph.graph,
            pos,
            edge_color="#34495E",
            width=1.5,
            alpha=0.5,
            arrows=True,
            arrowsize=10,
            ax=ax
        )

        # Simplified labels
        labels = {node: f"{node}\n{graph.graph.nodes[node]['vessels']:.0f}"
                 for node in graph.graph.nodes()}
        nx.draw_networkx_labels(
            graph.graph,
            pos,
            labels,
            font_size=7,
            font_weight="bold",
            ax=ax
        )

        time_value = model.history_time[timestep]
        ax.set_title(f"t = {time_value:.0f} years", fontsize=11, fontweight="bold")
        ax.axis("off")

    fig.suptitle(
        f"Network Evolution Over Time ({config.scenario_name.capitalize()} Scenario)",
        fontsize=16,
        fontweight="bold"
    )

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    print(f"Network summary saved to: {save_path}")
    plt.close()
