"""
Agent-Based Model for Rhine River Shipping

Simulates vessel movements, automation technology adoption, and collision risks
on the Rhine river network.
"""

import numpy as np
from mesa import Model, DataCollector
from mesa.agent import AgentSet
from typing import Dict, List, Optional, Tuple
import random

from src.models.network import RhineNetwork, create_rhine_network
from src.models.diffusion import MultiLevelAutomationDiffusion
from src.agents.vessel_agent import VesselAgent, create_vessel_characteristics


class RhineShippingModel(Model):
    """
    Agent-based model of Rhine river shipping with automation diffusion.

    Integrates:
    - Rhine spatial network for realistic geography
    - Multi-level automation diffusion model
    - Individual vessel agents with varying automation levels
    - Collision risk calculation and incident tracking
    """

    def __init__(
        self,
        num_vessels: int = 100,
        diffusion_config: Optional[dict] = None,
        automation_adoption_rate: float = 0.01,
        seed: Optional[int] = None,
    ):
        """
        Initialize Rhine shipping ABM.

        Args:
            num_vessels: Number of vessel agents to create
            diffusion_config: Configuration for automation diffusion model
            automation_adoption_rate: Probability per step that a vessel adopts new tech
            seed: Random seed for reproducibility
        """
        super().__init__()

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        # Model parameters
        self.num_vessels = num_vessels
        self.automation_adoption_rate = automation_adoption_rate

        # Initialize Rhine network
        self.network = create_rhine_network()

        # Initialize diffusion model
        if diffusion_config:
            self.diffusion_model = MultiLevelAutomationDiffusion(**diffusion_config)
        else:
            # Default configuration
            self.diffusion_model = MultiLevelAutomationDiffusion(
                total_fleet=num_vessels,
                initial_L1=int(num_vessels * 0.1),
                initial_L2=int(num_vessels * 0.05),
                initial_L3=0,
                initial_L4=0,
                initial_L5=0,
                M1=int(num_vessels * 0.4),
                M2=int(num_vessels * 0.35),
                M3=int(num_vessels * 0.25),
                M4=int(num_vessels * 0.15),
                M5=int(num_vessels * 0.10),
                p1=0.03, q1=0.4,
                p2=0.02, q2=0.3,
                p3=0.01, q3=0.2,
                p4=0.01, q4=0.15,
                p5=0.005, q5=0.1,
                dt=1.0,
            )

        # Custom agent collection (Mesa 3.0+ reserves 'agents' attribute)
        self.vessel_list = []

        # Tracking variables
        self.vessels_by_automation: Dict[int, set] = {i: set() for i in range(6)}
        self.total_incidents = 0
        self.total_near_misses = 0
        self.automation_adoptions = 0

        # Data collection
        self.datacollector = DataCollector(
            model_reporters={
                "Total_Vessels": lambda m: len(m.vessel_list),
                "Sailing_Vessels": lambda m: sum(1 for a in m.vessel_list if a.state == "sailing"),
                "Total_Incidents": lambda m: m.total_incidents,
                "Total_Near_Misses": lambda m: m.total_near_misses,
                "Avg_Collision_Risk": lambda m: np.mean([a.collision_risk for a in m.vessel_list if a.state == "sailing"]) if any(a.state == "sailing" for a in m.vessel_list) else 0,
                "L0_Vessels": lambda m: len(m.vessels_by_automation.get(0, set())),
                "L1_Vessels": lambda m: len(m.vessels_by_automation.get(1, set())),
                "L2_Vessels": lambda m: len(m.vessels_by_automation.get(2, set())),
                "L3_Vessels": lambda m: len(m.vessels_by_automation.get(3, set())),
                "L4_Vessels": lambda m: len(m.vessels_by_automation.get(4, set())),
                "L5_Vessels": lambda m: len(m.vessels_by_automation.get(5, set())),
                "Total_Distance_Traveled": lambda m: sum(a.distance_traveled for a in m.vessel_list),
            },
            agent_reporters={
                "AutomationLevel": "automation_level",
                "State": "state",
                "CollisionRisk": "collision_risk",
                "Incidents": "incident_count",
                "NearMisses": "near_misses",
            },
            tables={
                "Vessel_States": ["Step", "VesselID", "AutomationLevel", "State",
                                 "CurrentPort", "Speed", "CollisionRisk", "DistanceTraveled"]
            }
        )

        # Create initial vessel population
        self._create_vessels()

        # Initialize data collection
        self.datacollector.collect(self)

    def _create_vessels(self):
        """Create initial population of vessel agents."""
        # Get list of major ports for origin/destination assignment
        major_ports = [p.name for p in self.network.ports.values()
                      if p.capacity > 5000000]  # Major ports only

        # Determine initial automation distribution from diffusion model
        L0_count = self.num_vessels - (
            int(self.diffusion_model.history_L1[0]) +
            int(self.diffusion_model.history_L2[0])
        )

        automation_levels = (
            [0] * L0_count +
            [1] * int(self.diffusion_model.history_L1[0]) +
            [2] * int(self.diffusion_model.history_L2[0])
        )

        # Ensure we have exactly num_vessels
        while len(automation_levels) < self.num_vessels:
            automation_levels.append(0)
        automation_levels = automation_levels[:self.num_vessels]

        # Shuffle to randomize assignment
        self.random.shuffle(automation_levels)

        # Vessel types distribution (realistic mix)
        vessel_types = ["cargo"] * 60 + ["tanker"] * 20 + ["container"] * 15 + ["passenger"] * 5
        while len(vessel_types) < self.num_vessels:
            vessel_types.append(self.random.choice(["cargo", "tanker", "container"]))
        self.random.shuffle(vessel_types)

        # Create vessels
        for i in range(self.num_vessels):
            # Assign automation level
            auto_level = automation_levels[i]

            # Create vessel characteristics
            vessel_type = vessel_types[i]
            characteristics = create_vessel_characteristics(vessel_type)

            # Assign origin and destination (avoid same port)
            origin = self.random.choice(major_ports)
            destination = self.random.choice([p for p in major_ports if p != origin])

            # Create vessel agent
            vessel = VesselAgent(
                model=self,
                unique_id=i,
                automation_level=auto_level,
                characteristics=characteristics,
                origin=origin,
                destination=destination,
            )

            # Add to vessel list and tracking
            self.vessel_list.append(vessel)
            self.vessels_by_automation[auto_level].add(i)

    def _update_diffusion_model(self):
        """Advance diffusion model and update vessel automation levels."""
        # Step the diffusion model
        self.diffusion_model.step()

        # Get target counts for each automation level
        target_counts = {
            0: self.num_vessels - sum([
                int(self.diffusion_model.history_L1[-1]),
                int(self.diffusion_model.history_L2[-1]),
                int(self.diffusion_model.history_L3[-1]),
                int(self.diffusion_model.history_L4[-1]),
                int(self.diffusion_model.history_L5[-1]),
            ]),
            1: int(self.diffusion_model.history_L1[-1]),
            2: int(self.diffusion_model.history_L2[-1]),
            3: int(self.diffusion_model.history_L3[-1]),
            4: int(self.diffusion_model.history_L4[-1]),
            5: int(self.diffusion_model.history_L5[-1]),
        }

        # Upgrade vessels based on diffusion model predictions
        for target_level in range(1, 6):
            current_count = len(self.vessels_by_automation.get(target_level, set()))
            target_count = target_counts[target_level]

            if target_count > current_count:
                # Need to upgrade some vessels
                vessels_to_upgrade = target_count - current_count

                # Find vessels at lower levels that can upgrade
                for source_level in range(target_level):
                    if vessels_to_upgrade <= 0:
                        break

                    available_vessels = list(self.vessels_by_automation.get(source_level, set()))
                    if not available_vessels:
                        continue

                    # Randomly select vessels to upgrade
                    n_to_upgrade = min(vessels_to_upgrade, len(available_vessels))
                    vessels_to_upgrade_ids = self.random.sample(available_vessels, n_to_upgrade)

                    for vessel_id in vessels_to_upgrade_ids:
                        # Find vessel by ID
                        vessel = next((a for a in self.vessel_list if a.unique_id == vessel_id), None)
                        if vessel:
                            vessel.adopt_automation_level(target_level)
                            vessels_to_upgrade -= 1

    def _calculate_network_congestion(self) -> Dict[str, float]:
        """Calculate congestion levels at each port."""
        congestion = {port: 0 for port in self.network.ports.keys()}

        for agent in self.vessel_list:
            if agent.current_port in congestion:
                congestion[agent.current_port] += 1

        # Normalize by port capacity (simplified)
        for port, count in congestion.items():
            port_obj = self.network.ports[port]
            # Higher capacity ports can handle more vessels
            capacity_factor = port_obj.capacity / 10000000  # Normalize
            congestion[port] = count / max(capacity_factor, 1.0)

        return congestion

    def step(self):
        """Execute one step of the model."""
        # Update diffusion model (technology adoption)
        if self.steps % 10 == 0:  # Update every 10 steps
            self._update_diffusion_model()

        # Step all agents in random order
        agents_list = self.vessel_list.copy()
        self.random.shuffle(agents_list)
        for agent in agents_list:
            agent.step()

        # Calculate network-level metrics
        congestion = self._calculate_network_congestion()

        # Collect data
        self.datacollector.collect(self)

        # Call parent step to increment counter
        super().step()

    def run_model(self, steps: int):
        """
        Run model for specified number of steps.

        Args:
            steps: Number of time steps to simulate
        """
        for _ in range(steps):
            self.step()

    def get_summary_statistics(self) -> dict:
        """Get summary statistics of the simulation."""
        model_data = self.datacollector.get_model_vars_dataframe()

        agents_list = self.vessel_list
        sailing_vessels = [a for a in agents_list if a.state == "sailing"]
        moored_vessels = [a for a in agents_list if a.state == "moored"]

        stats = {
            "total_steps": self.steps,
            "total_vessels": len(agents_list),
            "sailing_vessels": len(sailing_vessels),
            "moored_vessels": len(moored_vessels),
            "total_incidents": self.total_incidents,
            "total_near_misses": self.total_near_misses,
            "automation_adoptions": self.automation_adoptions,
            "vessels_by_automation": {
                level: len(vessels) for level, vessels in self.vessels_by_automation.items()
            },
            "avg_distance_traveled": np.mean([a.distance_traveled for a in agents_list]),
            "avg_collision_risk": np.mean([a.collision_risk for a in sailing_vessels]) if sailing_vessels else 0,
            "total_distance": sum(a.distance_traveled for a in agents_list),
        }

        return stats

    def get_automation_distribution(self) -> Dict[int, int]:
        """Get current distribution of vessels by automation level."""
        return {
            level: len(vessels)
            for level, vessels in self.vessels_by_automation.items()
        }

    def get_vessels_at_port(self, port_name: str) -> List[VesselAgent]:
        """Get list of vessels currently at a specific port."""
        return [
            agent for agent in self.vessel_list
            if agent.current_port == port_name
        ]

    def get_sailing_vessels(self) -> List[VesselAgent]:
        """Get list of vessels currently sailing."""
        return [agent for agent in self.vessel_list if agent.state == "sailing"]


def create_shipping_model(
    num_vessels: int = 100,
    scenario: str = "baseline",
    seed: Optional[int] = None
) -> RhineShippingModel:
    """
    Factory function to create Rhine shipping model with preset scenarios.

    Args:
        num_vessels: Number of vessels in simulation
        scenario: Scenario name (baseline, optimistic, pessimistic)
        seed: Random seed

    Returns:
        Configured RhineShippingModel instance
    """
    from src.config import DiffusionConfig

    # Get diffusion configuration for scenario
    if scenario == "baseline":
        config_obj = DiffusionConfig.baseline()
    elif scenario == "optimistic":
        config_obj = DiffusionConfig.optimistic()
    elif scenario == "pessimistic":
        config_obj = DiffusionConfig.pessimistic()
    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    # Adjust for fleet size
    config_dict = config_obj.to_model_params()
    config_dict["total_fleet"] = num_vessels

    # Scale market potentials proportionally
    scale_factor = num_vessels / 10000
    config_dict["M1"] = int(config_obj.L1.market_potential * scale_factor)
    config_dict["M2"] = int(config_obj.L2.market_potential * scale_factor)
    config_dict["M3"] = int(config_obj.L3.market_potential * scale_factor)
    config_dict["M4"] = int(config_obj.L4.market_potential * scale_factor)
    config_dict["M5"] = int(config_obj.L5.market_potential * scale_factor)

    # Scale initial adopters
    config_dict["initial_L1"] = int(config_obj.L1.initial_adopters * scale_factor)
    config_dict["initial_L2"] = int(config_obj.L2.initial_adopters * scale_factor)

    return RhineShippingModel(
        num_vessels=num_vessels,
        diffusion_config=config_dict,
        seed=seed
    )
