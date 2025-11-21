"""
Configuration class for Bass diffusion model parameters.

Defines scenarios for automation adoption in inland shipping with uncertainty.
Based on CCNR automation level definitions:
- L0: Manual operation (baseline, not explicitly modeled)
- L1: Steering assistance (track pilot with basic automation features)
- L2: Partial automation (track pilot + propulsion control)
- L3: Conditional automation (with collision avoidance, still in development)
- L4: High automation (advanced systems, low initial adoption)
- L5: Full automation (autonomous vessels, minimal initial adoption)
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class LevelParameters:
    """Parameters for a single automation level."""

    initial_adopters: float
    market_potential: float  # M - maximum potential adopters
    innovation_coefficient: float  # p - external influence
    imitation_coefficient: float  # q - internal influence (word-of-mouth)

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for easy unpacking."""
        return {
            "initial": self.initial_adopters,
            "M": self.market_potential,
            "p": self.innovation_coefficient,
            "q": self.imitation_coefficient,
        }


class DiffusionConfig:
    """
    Configuration class for multi-level automation diffusion model.

    Provides three scenario definitions:
    - Baseline: Moderate adoption rates based on current trends
    - Optimistic: Faster adoption with higher market potentials
    - Pessimistic: Slower adoption with lower market potentials

    Usage:
        config = DiffusionConfig.baseline()
        model = MultiLevelAutomationDiffusion(**config.to_model_params())
    """

    def __init__(
        self,
        total_fleet: int,
        L1: LevelParameters,
        L2: LevelParameters,
        L3: LevelParameters,
        L4: LevelParameters,
        L5: LevelParameters,
        time_horizon: int = 30,
        dt: float = 1.0,
        scenario_name: str = "custom",
    ):
        """
        Initialize diffusion configuration.

        Args:
            total_fleet: Total number of vessels in the fleet (~10,000 for European inland shipping)
            L1-L5: Parameters for each automation level
            time_horizon: Number of years to simulate (default: 30)
            dt: Time step size in years (default: 1.0)
            scenario_name: Name of the scenario (baseline/optimistic/pessimistic/custom)
        """
        self.total_fleet = total_fleet
        self.L1 = L1
        self.L2 = L2
        self.L3 = L3
        self.L4 = L4
        self.L5 = L5
        self.time_horizon = time_horizon
        self.dt = dt
        self.scenario_name = scenario_name

    def to_model_params(self) -> Dict[str, Any]:
        """
        Convert configuration to parameters for MultiLevelAutomationDiffusion.

        Returns:
            Dictionary of parameters that can be unpacked into model constructor.
        """
        return {
            "total_fleet": self.total_fleet,
            "initial_L1": self.L1.initial_adopters,
            "initial_L2": self.L2.initial_adopters,
            "initial_L3": self.L3.initial_adopters,
            "initial_L4": self.L4.initial_adopters,
            "initial_L5": self.L5.initial_adopters,
            "M1": self.L1.market_potential,
            "M2": self.L2.market_potential,
            "M3": self.L3.market_potential,
            "M4": self.L4.market_potential,
            "M5": self.L5.market_potential,
            "p1": self.L1.innovation_coefficient,
            "q1": self.L1.imitation_coefficient,
            "p2": self.L2.innovation_coefficient,
            "q2": self.L2.imitation_coefficient,
            "p3": self.L3.innovation_coefficient,
            "q3": self.L3.imitation_coefficient,
            "p4": self.L4.innovation_coefficient,
            "q4": self.L4.imitation_coefficient,
            "p5": self.L5.innovation_coefficient,
            "q5": self.L5.imitation_coefficient,
            "dt": self.dt,
        }

    @classmethod
    def baseline(cls) -> "DiffusionConfig":
        """
        Baseline scenario with moderate adoption rates.

        Assumptions:
        - Total fleet: 10,000 vessels
        - L1+L2 combined have ~900 initial adopters (existing track pilot systems)
        - L3-L5 start at 0 (technologies still in development)
        - Market potentials reflect realistic adoption constraints
        - Innovation coefficients (p) decrease for higher levels (more barriers)
        - Imitation coefficients (q) vary based on observable benefits
        """
        return cls(
            total_fleet=10000,
            L1=LevelParameters(
                initial_adopters=450,  # Half of existing track pilot systems
                market_potential=7000,  # Most vessels could adopt basic automation
                innovation_coefficient=0.035,  # Moderate early adoption
                imitation_coefficient=0.45,  # Strong word-of-mouth for proven tech
            ),
            L2=LevelParameters(
                initial_adopters=450,  # Other half of existing systems
                market_potential=6000,  # Slightly lower (more requirements)
                innovation_coefficient=0.030,  # Slightly lower than L1
                imitation_coefficient=0.40,  # Still strong imitation
            ),
            L3=LevelParameters(
                initial_adopters=0,  # Still in development
                market_potential=3000,  # Significant barrier (collision avoidance)
                innovation_coefficient=0.020,  # Lower (more complex, expensive)
                imitation_coefficient=0.30,  # Moderate imitation
            ),
            L4=LevelParameters(
                initial_adopters=0,  # Not yet available
                market_potential=1200,  # High barriers (technical, regulatory)
                innovation_coefficient=0.012,  # Low early adoption
                imitation_coefficient=0.22,  # Lower imitation (niche use cases)
            ),
            L5=LevelParameters(
                initial_adopters=0,  # Future technology
                market_potential=500,  # Very limited (full autonomy challenges)
                innovation_coefficient=0.008,  # Very low early adoption
                imitation_coefficient=0.15,  # Limited imitation (high risk perception)
            ),
            time_horizon=30,
            dt=1.0,
            scenario_name="baseline",
        )

    @classmethod
    def optimistic(cls) -> "DiffusionConfig":
        """
        Optimistic scenario with faster adoption and higher market potentials.

        Assumptions:
        - Favorable regulatory environment
        - Rapid technological development
        - Strong economic incentives for automation
        - Higher market acceptance
        - Faster technology diffusion
        """
        return cls(
            total_fleet=10000,
            L1=LevelParameters(
                initial_adopters=450,
                market_potential=8500,  # +21% vs baseline
                innovation_coefficient=0.045,  # +29% vs baseline
                imitation_coefficient=0.55,  # +22% vs baseline
            ),
            L2=LevelParameters(
                initial_adopters=450,
                market_potential=7500,  # +25% vs baseline
                innovation_coefficient=0.040,  # +33% vs baseline
                imitation_coefficient=0.50,  # +25% vs baseline
            ),
            L3=LevelParameters(
                initial_adopters=0,
                market_potential=4500,  # +50% vs baseline
                innovation_coefficient=0.030,  # +50% vs baseline
                imitation_coefficient=0.42,  # +40% vs baseline
            ),
            L4=LevelParameters(
                initial_adopters=0,
                market_potential=2000,  # +67% vs baseline
                innovation_coefficient=0.020,  # +67% vs baseline
                imitation_coefficient=0.32,  # +45% vs baseline
            ),
            L5=LevelParameters(
                initial_adopters=0,
                market_potential=1000,  # +100% vs baseline
                innovation_coefficient=0.015,  # +88% vs baseline
                imitation_coefficient=0.25,  # +67% vs baseline
            ),
            time_horizon=30,
            dt=1.0,
            scenario_name="optimistic",
        )

    @classmethod
    def pessimistic(cls) -> "DiffusionConfig":
        """
        Pessimistic scenario with slower adoption and lower market potentials.

        Assumptions:
        - Regulatory barriers and uncertainty
        - Slower technological development
        - Economic challenges (high costs, unclear ROI)
        - Market resistance and safety concerns
        - Slower technology diffusion
        """
        return cls(
            total_fleet=10000,
            L1=LevelParameters(
                initial_adopters=450,
                market_potential=5500,  # -21% vs baseline
                innovation_coefficient=0.025,  # -29% vs baseline
                imitation_coefficient=0.35,  # -22% vs baseline
            ),
            L2=LevelParameters(
                initial_adopters=450,
                market_potential=4500,  # -25% vs baseline
                innovation_coefficient=0.022,  # -27% vs baseline
                imitation_coefficient=0.30,  # -25% vs baseline
            ),
            L3=LevelParameters(
                initial_adopters=0,
                market_potential=1800,  # -40% vs baseline
                innovation_coefficient=0.012,  # -40% vs baseline
                imitation_coefficient=0.20,  # -33% vs baseline
            ),
            L4=LevelParameters(
                initial_adopters=0,
                market_potential=600,  # -50% vs baseline
                innovation_coefficient=0.007,  # -42% vs baseline
                imitation_coefficient=0.14,  # -36% vs baseline
            ),
            L5=LevelParameters(
                initial_adopters=0,
                market_potential=200,  # -60% vs baseline
                innovation_coefficient=0.004,  # -50% vs baseline
                imitation_coefficient=0.08,  # -47% vs baseline
            ),
            time_horizon=30,
            dt=1.0,
            scenario_name="pessimistic",
        )

    @classmethod
    def get_all_scenarios(cls) -> Dict[str, "DiffusionConfig"]:
        """
        Get all predefined scenarios as a dictionary.

        Returns:
            Dictionary mapping scenario names to DiffusionConfig instances.
        """
        return {
            "baseline": cls.baseline(),
            "optimistic": cls.optimistic(),
            "pessimistic": cls.pessimistic(),
        }

    def __repr__(self) -> str:
        """String representation of configuration."""
        return (
            f"DiffusionConfig(scenario='{self.scenario_name}', "
            f"total_fleet={self.total_fleet}, time_horizon={self.time_horizon})"
        )

    def summary(self) -> str:
        """
        Generate a human-readable summary of the configuration.

        Returns:
            Multi-line string describing the configuration parameters.
        """
        lines = [
            f"Diffusion Model Configuration - {self.scenario_name.upper()} Scenario",
            "=" * 70,
            f"Total Fleet: {self.total_fleet} vessels",
            f"Time Horizon: {self.time_horizon} years (dt={self.dt})",
            "",
            "Automation Levels (CCNR Definitions):",
            "-" * 70,
        ]

        for level_num, level_name, level_params in [
            (1, "Steering Assistance", self.L1),
            (2, "Partial Automation", self.L2),
            (3, "Conditional Automation", self.L3),
            (4, "High Automation", self.L4),
            (5, "Full Automation", self.L5),
        ]:
            lines.extend(
                [
                    f"Level {level_num}: {level_name}",
                    f"  Initial Adopters: {level_params.initial_adopters:.0f} vessels",
                    f"  Market Potential: {level_params.market_potential:.0f} vessels "
                    f"({level_params.market_potential/self.total_fleet*100:.1f}% of fleet)",
                    f"  Innovation Coeff (p): {level_params.innovation_coefficient:.4f}",
                    f"  Imitation Coeff (q): {level_params.imitation_coefficient:.4f}",
                    "",
                ]
            )

        return "\n".join(lines)
