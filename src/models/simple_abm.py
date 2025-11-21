"""
Simple Agent-Based Model for Inland Shipping Safety Assessment

This is a minimal viable ABM that simulates vessel movement in a 1D waterway
and detects collision risks based on automation levels.

Key simplifications:
- 1D movement (position along channel only)
- Constant vessel speeds
- Simple proximity-based encounter detection
- No active collision avoidance
"""

import random
from mesa import Agent, Model
from mesa.datacollection import DataCollector


class Vessel(Agent):
    """
    A vessel agent with automation level-dependent detection capabilities.

    Vessels move at constant speed in either upstream (+1) or downstream (-1) direction.
    Detection range increases with automation level.
    """

    # Detection ranges by automation level (in meters)
    DETECTION_RANGES = {
        'L0': 500,   # Manual operation
        'L1': 750,   # Steering assistance
        'L2': 1000,  # Partial automation
        'L3': 1200   # Conditional automation
    }

    def __init__(self, model, automation_level):
        """
        Initialize a vessel agent.

        Args:
            model: The WaterwayModel instance
            automation_level: String ('L0', 'L1', 'L2', or 'L3')
        """
        super().__init__(model)
        self.automation_level = automation_level

        # Random starting position along 5km waterway
        self.position = random.uniform(0, 5000)

        # Constant speed: 10 m/s (≈ 20 knots)
        self.speed = 10

        # Random direction: +1 (downstream) or -1 (upstream)
        self.direction = random.choice([1, -1])

        # Detection range based on automation level
        self.detection_range = self.DETECTION_RANGES[automation_level]

        # Track encounters this vessel has detected
        self.encounters_this_step = []

    def step(self):
        """
        Execute one time step for this vessel.

        1. Move vessel along waterway
        2. Check for nearby vessels within detection range
        3. Record encounters and calculate closest approach distances
        """
        # Move vessel
        self.position += self.speed * self.direction * self.model.time_step

        # Handle boundary conditions: vessels exit and re-enter waterway
        # (This keeps vessel count constant)
        if self.position > 5000:
            self.position = 0
        elif self.position < 0:
            self.position = 5000

        # Clear previous step's encounters
        self.encounters_this_step = []

        # Check for nearby vessels
        self._detect_nearby_vessels()

    def _detect_nearby_vessels(self):
        """
        Detect nearby vessels and classify encounters by severity.

        For each vessel within detection range heading toward us:
        - Calculate current distance
        - Classify as: collision (<50m), near-miss (50-100m), or encounter (>100m)
        - Record in model's safety metrics
        """
        for other in self.model.agents:
            if other.unique_id == self.unique_id:
                continue  # Skip self

            # Calculate distance
            distance = abs(self.position - other.position)

            # Check if within detection range
            if distance > self.detection_range:
                continue

            # Check if heading toward each other (opposite directions)
            heading_toward = self.direction != other.direction

            if heading_toward:
                # Record encounter (only count each pair once by using vessel ID ordering)
                if self.unique_id < other.unique_id:  # Prevent double-counting
                    encounter_info = {
                        'vessel_1': self.unique_id,
                        'vessel_2': other.unique_id,
                        'distance': distance,
                        'level_1': self.automation_level,
                        'level_2': other.automation_level,
                        'step': self.model.steps
                    }

                    # Classify encounter severity
                    if distance < 50:
                        self.model.collisions.append(encounter_info)
                    elif distance < 100:
                        self.model.near_misses.append(encounter_info)
                    else:
                        self.model.encounters.append(encounter_info)


class WaterwayModel(Model):
    """
    Simple waterway model with vessels moving in 1D space.

    Simulates vessel movement and tracks safety metrics based on
    proximity encounters between vessels.
    """

    def __init__(self, n_vessels=20, fleet_composition=None, time_step=5):
        """
        Initialize the waterway model.

        Args:
            n_vessels: Total number of vessels to simulate (default: 20)
            fleet_composition: Dictionary mapping automation levels to proportions
                              e.g., {'L0': 0.4, 'L1': 0.3, 'L2': 0.2, 'L3': 0.1}
                              If None, defaults to all L0
            time_step: Simulation time step in seconds (default: 5)
        """
        super().__init__()
        self.n_vessels = n_vessels
        self.time_step = time_step
        self.steps = 0  # Track simulation steps

        # Default to all manual vessels if no composition specified
        if fleet_composition is None:
            fleet_composition = {'L0': 1.0}

        self.fleet_composition = fleet_composition

        # Safety metrics storage
        self.encounters = []      # All encounters (>100m, <detection_range)
        self.near_misses = []     # 50-100m
        self.collisions = []      # <50m

        # Create vessels based on fleet composition
        self._create_vessels()

        # Set up data collection
        self.datacollector = DataCollector(
            model_reporters={
                "total_encounters": lambda m: len(m.encounters),
                "near_misses": lambda m: len(m.near_misses),
                "collisions": lambda m: len(m.collisions),
                "avg_encounter_distance": self._calculate_avg_encounter_distance
            }
        )

    def _create_vessels(self):
        """
        Create vessels according to specified fleet composition.

        Randomly assigns automation levels based on the proportions
        specified in fleet_composition.
        """
        # Build list of automation levels based on proportions
        levels = []
        for level, proportion in self.fleet_composition.items():
            count = int(self.n_vessels * proportion)
            levels.extend([level] * count)

        # Handle rounding issues - fill remaining slots with L0
        while len(levels) < self.n_vessels:
            levels.append('L0')

        # Shuffle to randomize vessel placement
        random.shuffle(levels)

        # Create vessel agents (Mesa 3.x automatically tracks agents)
        for i in range(self.n_vessels):
            vessel = Vessel(self, levels[i])
            # In Mesa 3.x, agents are automatically tracked when created with model reference

    def _calculate_avg_encounter_distance(self):
        """Calculate average distance across all encounters."""
        all_encounters = self.encounters + self.near_misses + self.collisions
        if len(all_encounters) == 0:
            return 0
        total_distance = sum(e['distance'] for e in all_encounters)
        return total_distance / len(all_encounters)

    def step(self):
        """Execute one time step of the simulation."""
        self.datacollector.collect(self)

        # In Mesa 3.x, manually call step() on each agent
        # Use list() to avoid modification during iteration
        for agent in list(self.agents):
            agent.step()

        self.steps += 1

    def get_summary_statistics(self):
        """
        Get summary statistics for the simulation run.

        Returns:
            Dictionary with safety metrics
        """
        all_encounters = self.encounters + self.near_misses + self.collisions

        avg_distance = 0
        if len(all_encounters) > 0:
            avg_distance = sum(e['distance'] for e in all_encounters) / len(all_encounters)

        return {
            'total_encounters': len(all_encounters),
            'encounters_safe': len(self.encounters),
            'near_misses': len(self.near_misses),
            'collisions': len(self.collisions),
            'avg_encounter_distance': avg_distance,
            'collision_rate': len(self.collisions) / len(all_encounters) if all_encounters else 0
        }
