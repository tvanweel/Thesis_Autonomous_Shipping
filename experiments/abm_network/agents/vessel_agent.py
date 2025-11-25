"""
Vessel Agent for Rhine Shipping ABM

Represents individual vessels navigating the Rhine river with varying
levels of automation technology (L0-L5 according to CCNR classification).
"""

import numpy as np
from mesa import Agent
from typing import Optional, List, Tuple
from dataclasses import dataclass


@dataclass
class VesselCharacteristics:
    """Physical and operational characteristics of a vessel."""
    length: float  # meters
    width: float  # meters
    draft: float  # meters (how deep vessel sits in water)
    max_speed: float  # km/h
    cargo_capacity: float  # tonnes
    vessel_type: str  # "cargo", "tanker", "container", "passenger"


class VesselAgent(Agent):
    """
    Agent representing a vessel navigating the Rhine.

    Attributes:
        unique_id: Unique identifier for the agent
        model: Reference to the ShippingModel
        automation_level: Current automation level (0-5)
        characteristics: Physical vessel characteristics
        current_port: Current port location
        destination_port: Target destination
        route: List of ports to traverse
        position: Current position on route (index)
        speed: Current speed (km/h)
        cargo: Current cargo load (tonnes)
        state: Vessel state (sailing, moored, loading, unloading)
    """

    def __init__(
        self,
        model,
        unique_id: int,
        automation_level: int,
        characteristics: VesselCharacteristics,
        origin: str,
        destination: str,
    ):
        """
        Initialize vessel agent.

        Args:
            model: ShippingModel instance
            unique_id: Unique identifier
            automation_level: Automation level (0-5)
            characteristics: Vessel physical characteristics
            origin: Starting port name
            destination: Destination port name
        """
        super().__init__(model)
        self.unique_id = unique_id

        # Automation and characteristics
        self.automation_level = automation_level
        self.characteristics = characteristics

        # Journey information
        self.origin = origin
        self.destination = destination
        self.current_port = origin
        self.route: List[str] = []
        self.route_position = 0  # Index in route

        # Movement state
        self.state = "moored"  # moored, sailing, loading, unloading
        self.speed = 0.0
        self.cargo = 0.0

        # Journey tracking
        self.distance_traveled = 0.0
        self.journey_time = 0
        self.waiting_time = 0

        # Risk and incidents
        self.collision_risk = 0.0
        self.incident_count = 0
        self.near_misses = 0

        # Calculate initial route
        self._plan_route()

    def _plan_route(self):
        """Plan route from origin to destination using network."""
        if self.origin == self.destination:
            self.route = [self.origin]
            return

        # Use network to find optimal route
        route, distance = self.model.network.get_route(
            self.origin,
            self.destination,
            criterion="length"
        )

        if route:
            self.route = route
            self.route_position = 0
        else:
            # Fallback: stay at origin
            self.route = [self.origin]
            self.state = "moored"

    def _calculate_automation_speed_factor(self) -> float:
        """
        Calculate speed adjustment factor based on automation level.

        Higher automation allows more consistent optimal speeds.
        """
        # Automation provides more efficient operation
        base_efficiency = 1.0
        automation_bonus = {
            0: 0.0,   # Manual - baseline
            1: 0.02,  # Basic assistance - 2% improvement
            2: 0.05,  # Partial automation - 5% improvement
            3: 0.08,  # Conditional automation - 8% improvement
            4: 0.12,  # High automation - 12% improvement
            5: 0.15,  # Full automation - 15% improvement
        }
        return base_efficiency + automation_bonus.get(self.automation_level, 0)

    def _calculate_base_collision_risk(self) -> float:
        """
        Calculate base collision risk based on current conditions.

        Factors:
        - Traffic density in current segment
        - Navigation risk level of segment
        - Weather/visibility (simplified as random factor)
        - Vessel automation level
        """
        if self.state != "sailing" or self.route_position >= len(self.route) - 1:
            return 0.0

        # Get current segment
        current = self.route[self.route_position]
        next_port = self.route[self.route_position + 1]

        # Find segment in network
        segment = None
        for seg in self.model.network.segments:
            if seg.start == current and seg.end == next_port:
                segment = seg
                break

        if not segment:
            return 0.0

        # Base risk from segment characteristics
        traffic_risk = segment.traffic_density / 300.0  # Normalize (max ~200)
        navigation_risk = segment.risk_level / 5.0  # Normalize (1-5 scale)

        # Environmental factor (random, representing weather/visibility)
        environmental_factor = self.random.uniform(0.5, 1.5)

        # Automation reduces risk
        automation_reduction = {
            0: 1.0,   # Manual - baseline risk
            1: 0.92,  # 8% reduction
            2: 0.82,  # 18% reduction
            3: 0.70,  # 30% reduction
            4: 0.55,  # 45% reduction
            5: 0.40,  # 60% reduction
        }

        base_risk = (traffic_risk * 0.4 + navigation_risk * 0.6) * environmental_factor
        adjusted_risk = base_risk * automation_reduction.get(self.automation_level, 1.0)

        return min(adjusted_risk, 1.0)

    def _check_for_incidents(self):
        """Check if incident occurs based on collision risk."""
        if self.collision_risk > 0:
            # Incident probability is a function of risk
            incident_threshold = 0.001  # 0.1% base probability at risk=1.0
            incident_prob = self.collision_risk * incident_threshold

            if self.random.random() < incident_prob:
                self.incident_count += 1
                self.model.total_incidents += 1
                self.speed *= 0.5  # Reduce speed after incident

            # Near miss probability (higher than actual incident)
            near_miss_prob = self.collision_risk * 0.01  # 1% at risk=1.0
            if self.random.random() < near_miss_prob:
                self.near_misses += 1
                self.model.total_near_misses += 1

    def _move_along_route(self):
        """Move vessel along planned route."""
        if self.route_position >= len(self.route) - 1:
            # Reached destination
            self.state = "moored"
            self.speed = 0
            self.current_port = self.destination
            return

        # Set sailing state
        self.state = "sailing"

        # Calculate speed based on vessel characteristics and automation
        speed_factor = self._calculate_automation_speed_factor()
        self.speed = self.characteristics.max_speed * speed_factor

        # Add some randomness for realism
        self.speed *= self.random.uniform(0.85, 1.0)

        # Calculate collision risk for current segment
        self.collision_risk = self._calculate_base_collision_risk()

        # Check for incidents
        self._check_for_incidents()

        # Simulate movement (simplified: one segment per step)
        # In reality, this would be more granular
        movement_prob = self.speed / 100.0  # Faster vessels move between ports quicker

        if self.random.random() < movement_prob:
            self.route_position += 1
            if self.route_position < len(self.route):
                self.current_port = self.route[self.route_position]

                # Get segment distance for tracking
                if self.route_position < len(self.route) - 1:
                    prev = self.route[self.route_position - 1]
                    curr = self.route[self.route_position]

                    for seg in self.model.network.segments:
                        if seg.start == prev and seg.end == curr:
                            self.distance_traveled += seg.length
                            break

    def _load_unload_cargo(self):
        """Simulate cargo loading/unloading at port."""
        if self.state == "loading":
            # Loading takes time
            self.waiting_time += 1
            if self.random.random() < 0.2:  # 20% chance per step
                self.cargo = self.characteristics.cargo_capacity * self.random.uniform(0.6, 1.0)
                self.state = "sailing"  # Start sailing after loading

        elif self.state == "unloading":
            # Unloading takes time
            self.waiting_time += 1
            if self.random.random() < 0.2:  # 20% chance per step
                self.cargo = 0
                self.state = "moored"  # Stay moored after unloading

    def _decide_next_action(self):
        """Decide what to do next based on current state."""
        if self.state == "moored":
            # At port, decide whether to start journey or wait
            if self.current_port == self.origin and self.route_position == 0:
                # Just starting, load cargo
                self.state = "loading"
            elif self.current_port == self.destination:
                # At destination, unload cargo
                if self.cargo > 0:
                    self.state = "unloading"
                else:
                    # Journey complete, could start new journey
                    # For now, vessel stays moored
                    pass
            else:
                # At intermediate port, continue journey
                self.state = "sailing"

    def step(self):
        """Execute one step of vessel behavior."""
        self.journey_time += 1

        # Main behavior logic based on state
        if self.state in ["loading", "unloading"]:
            self._load_unload_cargo()

        elif self.state == "sailing":
            self._move_along_route()

        elif self.state == "moored":
            self._decide_next_action()

        # Record data
        self.model.datacollector.add_table_row(
            "Vessel_States",
            {
                "Step": self.model.steps,
                "VesselID": self.unique_id,
                "AutomationLevel": self.automation_level,
                "State": self.state,
                "CurrentPort": self.current_port,
                "Speed": self.speed,
                "CollisionRisk": self.collision_risk,
                "DistanceTraveled": self.distance_traveled,
            }
        )

    def adopt_automation_level(self, new_level: int):
        """
        Adopt a new automation level (technology upgrade).

        Args:
            new_level: New automation level (should be higher than current)
        """
        if new_level > self.automation_level:
            old_level = self.automation_level
            self.automation_level = new_level

            # Record technology adoption event
            self.model.automation_adoptions += 1

            # Notify model for statistics
            if hasattr(self.model, 'vessels_by_automation'):
                if old_level in self.model.vessels_by_automation:
                    self.model.vessels_by_automation[old_level].discard(self.unique_id)
                if new_level not in self.model.vessels_by_automation:
                    self.model.vessels_by_automation[new_level] = set()
                self.model.vessels_by_automation[new_level].add(self.unique_id)

    def get_state_summary(self) -> dict:
        """Get summary of vessel state for reporting."""
        return {
            "id": self.unique_id,
            "automation_level": self.automation_level,
            "state": self.state,
            "current_port": self.current_port,
            "destination": self.destination,
            "progress": f"{self.route_position}/{len(self.route)}",
            "distance_traveled": self.distance_traveled,
            "journey_time": self.journey_time,
            "incidents": self.incident_count,
            "near_misses": self.near_misses,
            "avg_risk": self.collision_risk,
        }


def create_vessel_characteristics(vessel_type: str) -> VesselCharacteristics:
    """
    Factory function to create typical vessel characteristics by type.

    Args:
        vessel_type: Type of vessel (cargo, tanker, container, passenger)

    Returns:
        VesselCharacteristics instance
    """
    characteristics = {
        "cargo": VesselCharacteristics(
            length=110.0,
            width=11.4,
            draft=3.5,
            max_speed=15.0,
            cargo_capacity=2500.0,
            vessel_type="cargo"
        ),
        "tanker": VesselCharacteristics(
            length=135.0,
            width=11.4,
            draft=3.8,
            max_speed=13.0,
            cargo_capacity=3000.0,
            vessel_type="tanker"
        ),
        "container": VesselCharacteristics(
            length=110.0,
            width=11.4,
            draft=3.2,
            max_speed=16.0,
            cargo_capacity=2000.0,
            vessel_type="container"
        ),
        "passenger": VesselCharacteristics(
            length=135.0,
            width=15.0,
            draft=1.8,
            max_speed=25.0,
            cargo_capacity=200.0,  # passengers
            vessel_type="passenger"
        ),
    }

    return characteristics.get(vessel_type, characteristics["cargo"])
