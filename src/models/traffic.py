"""
Traffic Behavior Module

Models realistic inland waterway traffic with:
- Dynamic speed adjustment based on vessel density
- Crossroad management with waiting times
- Congestion effects on travel time

Assumptions:
-----------
1. Edge Capacity:
   - Rhine waterway typical width: ~200-400m navigable channel
   - Inland vessel typical length: ~85-110m
   - Safe separation distance: ~2 vessel lengths
   - Capacity: ~12 vessels per kilometer per direction

2. Speed Model:
   - Base speed: Individual vessel cruising speed (10-18 km/h)
   - Speed reduction due to congestion: Linear model
   - Formula: effective_speed = base_speed * (1 - 0.7 * density_ratio)
   - density_ratio = vessels_on_edge / edge_capacity
   - Maximum slowdown: 70% when at capacity

3. Crossroads:
   - Major crossroads: Nodes with 3+ incoming/outgoing edges
   - Crossing time: 0.5 hours (30 minutes) to safely navigate intersection
   - Priority: First-come-first-served (FCFS)
   - Waiting: Vessels wait if crossroad occupied

4. Distances:
   - All distances are straight-line distances between ports
   - Actual river distances may be ~10-20% longer due to meandering
   - Distance values from network edges are used as-is
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict

from src.assumptions import get_traffic_config

# Load traffic model configuration from assumptions
_TRAFFIC_CONFIG = get_traffic_config()
VESSELS_PER_KM_CAPACITY = _TRAFFIC_CONFIG["vessels_per_km_capacity"]
CONGESTION_IMPACT_FACTOR = _TRAFFIC_CONFIG["congestion_impact_factor"]
CROSSROAD_TRANSIT_TIME = _TRAFFIC_CONFIG["crossroad_transit_time_hours"]
MIN_SPEED_RATIO = _TRAFFIC_CONFIG["min_speed_ratio"]


@dataclass
class EdgeTraffic:
    """Traffic state for a network edge."""
    edge_id: str  # "source->target"
    distance_km: float
    capacity: int  # Maximum vessels
    vessels: Set[str] = field(default_factory=set)  # Agent IDs currently on edge

    @property
    def vessel_count(self) -> int:
        """Number of vessels currently on this edge."""
        return len(self.vessels)

    @property
    def density_ratio(self) -> float:
        """Vessel density as ratio of capacity (0.0 to 1.0+)."""
        return self.vessel_count / self.capacity if self.capacity > 0 else 0.0

    @property
    def is_congested(self) -> bool:
        """True if edge is at or above 80% capacity."""
        return self.density_ratio >= 0.8

    def calculate_effective_speed(self, base_speed: float) -> float:
        """
        Calculate effective speed considering congestion.

        Args:
            base_speed: Vessel's cruising speed (km/h)

        Returns:
            Effective speed in km/h (never below MIN_SPEED_RATIO * base_speed)
        """
        # Linear congestion model: speed reduces with density
        speed_multiplier = 1.0 - (CONGESTION_IMPACT_FACTOR * min(1.0, self.density_ratio))
        speed_multiplier = max(MIN_SPEED_RATIO, speed_multiplier)

        return base_speed * speed_multiplier


@dataclass
class CrossroadState:
    """State for a crossroad node."""
    node_id: str
    occupied_by: Optional[str] = None  # Agent ID occupying crossroad
    occupation_end_time: float = 0.0  # When current vessel finishes crossing
    waiting_queue: List[Tuple[str, float]] = field(default_factory=list)  # (agent_id, arrival_time)

    def is_available(self, current_time: float) -> bool:
        """Check if crossroad is available for entry."""
        return self.occupied_by is None or current_time >= self.occupation_end_time

    def occupy(self, agent_id: str, current_time: float) -> float:
        """
        Occupy the crossroad.

        Args:
            agent_id: Agent occupying the crossroad
            current_time: Current simulation time

        Returns:
            Time when crossing will complete
        """
        self.occupied_by = agent_id
        self.occupation_end_time = current_time + CROSSROAD_TRANSIT_TIME
        return self.occupation_end_time

    def release(self):
        """Release the crossroad."""
        self.occupied_by = None
        self.occupation_end_time = 0.0

    def add_to_queue(self, agent_id: str, arrival_time: float):
        """Add vessel to waiting queue."""
        self.waiting_queue.append((agent_id, arrival_time))

    def remove_from_queue(self, agent_id: str):
        """Remove vessel from waiting queue."""
        self.waiting_queue = [(aid, t) for aid, t in self.waiting_queue if aid != agent_id]

    def get_wait_time(self, current_time: float) -> float:
        """Calculate wait time for next vessel in queue."""
        if self.is_available(current_time):
            return 0.0
        return max(0.0, self.occupation_end_time - current_time)


class TrafficManager:
    """
    Manages traffic behavior across the network.

    Tracks vessel positions on edges, manages crossroads, and calculates
    dynamic travel times based on congestion.
    """

    def __init__(self, network):
        """
        Initialize traffic manager.

        Args:
            network: Network object with nodes and edges
        """
        self.network = network
        self.edge_traffic: Dict[str, EdgeTraffic] = {}
        self.crossroads: Dict[str, CrossroadState] = {}
        self.current_time: float = 0.0

        # Initialize edge traffic
        self._initialize_edges()

        # Identify and initialize crossroads (nodes with 3+ connections)
        self._initialize_crossroads()

    def _initialize_edges(self):
        """Create EdgeTraffic for all network edges."""
        for edge in self.network.edges:
            edge_id = f"{edge.source}->{edge.target}"
            distance = edge.properties.get("distance_km", edge.weight)
            capacity = int(distance * VESSELS_PER_KM_CAPACITY)

            self.edge_traffic[edge_id] = EdgeTraffic(
                edge_id=edge_id,
                distance_km=distance,
                capacity=capacity
            )

    def _initialize_crossroads(self):
        """Identify nodes that are crossroads (3+ connections)."""
        for node_id, node in self.network.nodes.items():
            # Count incoming and outgoing edges
            incoming = sum(1 for e in self.network.edges if e.target == node_id)
            outgoing = sum(1 for e in self.network.edges if e.source == node_id)
            total_connections = incoming + outgoing

            # Crossroad if 3+ connections
            if total_connections >= 3:
                self.crossroads[node_id] = CrossroadState(node_id=node_id)

    def vessel_enter_edge(self, agent_id: str, source: str, target: str):
        """
        Register vessel entering an edge.

        Args:
            agent_id: Vessel identifier
            source: Source node
            target: Target node
        """
        edge_id = f"{source}->{target}"
        if edge_id in self.edge_traffic:
            self.edge_traffic[edge_id].vessels.add(agent_id)

    def vessel_exit_edge(self, agent_id: str, source: str, target: str):
        """
        Register vessel exiting an edge.

        Args:
            agent_id: Vessel identifier
            source: Source node
            target: Target node
        """
        edge_id = f"{source}->{target}"
        if edge_id in self.edge_traffic:
            self.edge_traffic[edge_id].vessels.discard(agent_id)

    def get_effective_speed(self, agent_id: str, base_speed: float,
                           source: str, target: str) -> float:
        """
        Calculate effective speed considering current traffic.

        Args:
            agent_id: Vessel identifier
            base_speed: Vessel's base cruising speed
            source: Source node
            target: Target node

        Returns:
            Effective speed in km/h
        """
        edge_id = f"{source}->{target}"
        if edge_id in self.edge_traffic:
            return self.edge_traffic[edge_id].calculate_effective_speed(base_speed)
        return base_speed

    def check_crossroad_entry(self, agent_id: str, node_id: str) -> Tuple[bool, float]:
        """
        Check if vessel can enter crossroad.

        Args:
            agent_id: Vessel identifier
            node_id: Crossroad node ID

        Returns:
            Tuple of (can_enter, wait_time_hours)
        """
        if node_id not in self.crossroads:
            return True, 0.0  # Not a crossroad, can proceed

        crossroad = self.crossroads[node_id]

        if crossroad.is_available(self.current_time):
            return True, 0.0

        # Must wait
        wait_time = crossroad.get_wait_time(self.current_time)
        return False, wait_time

    def occupy_crossroad(self, agent_id: str, node_id: str) -> float:
        """
        Occupy a crossroad.

        Args:
            agent_id: Vessel identifier
            node_id: Crossroad node ID

        Returns:
            Time when crossing completes (hours)
        """
        if node_id in self.crossroads:
            return self.crossroads[node_id].occupy(agent_id, self.current_time)
        return self.current_time

    def release_crossroad(self, agent_id: str, node_id: str):
        """
        Release a crossroad.

        Args:
            agent_id: Vessel identifier
            node_id: Crossroad node ID
        """
        if node_id in self.crossroads:
            crossroad = self.crossroads[node_id]
            if crossroad.occupied_by == agent_id:
                crossroad.release()

    def update_time(self, time: float):
        """
        Update simulation time.

        Args:
            time: Current simulation time (hours)
        """
        self.current_time = time

    def get_edge_stats(self) -> Dict[str, Dict]:
        """
        Get statistics for all edges.

        Returns:
            Dictionary of edge_id -> stats dict
        """
        stats = {}
        for edge_id, traffic in self.edge_traffic.items():
            stats[edge_id] = {
                "vessels": traffic.vessel_count,
                "capacity": traffic.capacity,
                "density_ratio": traffic.density_ratio,
                "is_congested": traffic.is_congested
            }
        return stats

    def get_crossroad_stats(self) -> Dict[str, Dict]:
        """
        Get statistics for all crossroads.

        Returns:
            Dictionary of node_id -> stats dict
        """
        stats = {}
        for node_id, crossroad in self.crossroads.items():
            stats[node_id] = {
                "occupied": crossroad.occupied_by is not None,
                "occupied_by": crossroad.occupied_by,
                "queue_length": len(crossroad.waiting_queue)
            }
        return stats
