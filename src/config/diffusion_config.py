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

        # Validate that market potentials respect hierarchical constraints
        self._validate_market_potentials()

    def _validate_market_potentials(self):
        """
        Validate that market potentials respect fleet constraints.

        Since automation levels are mutually exclusive (each vessel belongs to ONE level),
        the sum of all market potentials should not significantly exceed the total fleet.
        Some overlap is allowed as market potentials represent maximum potential adoption,
        but excessive overlap would be unrealistic.

        Raises:
            ValueError: If market potential constraints are violated.
        """
        # Check that each individual level doesn't exceed total fleet
        for level_num, level_params in [(1, self.L1), (2, self.L2), (3, self.L3), (4, self.L4), (5, self.L5)]:
            if level_params.market_potential > self.total_fleet:
                raise ValueError(
                    f"L{level_num} market potential ({level_params.market_potential}) cannot exceed "
                    f"total fleet ({self.total_fleet}). "
                    f"A single level cannot have more potential adopters than the entire fleet."
                )

        # Check that sum of market potentials is reasonable
        # Allow up to 2x fleet size (some competition between levels is realistic)
        total_market_potential = (
            self.L1.market_potential +
            self.L2.market_potential +
            self.L3.market_potential +
            self.L4.market_potential +
            self.L5.market_potential
        )

        if total_market_potential > 2 * self.total_fleet:
            raise ValueError(
                f"Sum of market potentials ({total_market_potential}) is unrealistically high "
                f"({total_market_potential/self.total_fleet:.1f}x fleet size). "
                f"Since levels are mutually exclusive, the sum should not exceed ~2x the fleet size. "
                f"Consider reducing market potentials to reflect realistic adoption scenarios."
            )

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

        Assumptions (Mutually Exclusive Levels):
        - Total fleet: 10,000 vessels (fixed)
        - Each vessel adopts EXACTLY ONE automation level
        - L0 (manual): Majority of fleet starts here
        - L1+L2: ~900 initial adopters (existing track pilot systems)
        - L3-L5: 0 initial adopters (technologies still in development)
        - Market potentials represent maximum vessels that could adopt each specific level
        - Sum of market potentials ≈ fleet size (levels compete for same vessels)
        """
        return cls(
            total_fleet=10000,
            L1=LevelParameters(
                initial_adopters=450,  # Basic automation (track pilot)
                market_potential=3000,  # 30% could adopt basic level
                innovation_coefficient=0.035,  # Moderate early adoption
                imitation_coefficient=0.45,  # Strong word-of-mouth for proven tech
            ),
            L2=LevelParameters(
                initial_adopters=450,  # Partial automation
                market_potential=3500,  # 35% could adopt partial automation
                innovation_coefficient=0.030,  # Slightly lower than L1
                imitation_coefficient=0.40,  # Still strong imitation
            ),
            L3=LevelParameters(
                initial_adopters=0,  # Conditional automation (still in development)
                market_potential=2000,  # 20% for conditional automation
                innovation_coefficient=0.020,  # Lower (more complex, expensive)
                imitation_coefficient=0.30,  # Moderate imitation
            ),
            L4=LevelParameters(
                initial_adopters=0,  # High automation (not yet available)
                market_potential=1000,  # 10% for high automation
                innovation_coefficient=0.012,  # Low early adoption
                imitation_coefficient=0.22,  # Lower imitation (niche use cases)
            ),
            L5=LevelParameters(
                initial_adopters=0,  # Full automation (future technology)
                market_potential=500,  # 5% for full autonomy
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
        Optimistic scenario with faster adoption and shift toward higher automation levels.

        Assumptions (Mutually Exclusive Levels):
        - Total fleet: 10,000 vessels (fixed)
        - Favorable regulatory environment
        - Rapid technological development
        - Strong economic incentives for automation
        - Higher market acceptance, especially for advanced levels
        - Faster technology diffusion
        - Market shifts toward L3-L5 (higher automation preferred)
        """
        return cls(
            total_fleet=10000,
            L1=LevelParameters(
                initial_adopters=450,
                market_potential=2000,  # 20% stay at basic level (lower than baseline)
                innovation_coefficient=0.045,  # +29% vs baseline
                imitation_coefficient=0.55,  # +22% vs baseline
            ),
            L2=LevelParameters(
                initial_adopters=450,
                market_potential=2500,  # 25% at partial automation
                innovation_coefficient=0.040,  # +33% vs baseline
                imitation_coefficient=0.50,  # +25% vs baseline
            ),
            L3=LevelParameters(
                initial_adopters=0,
                market_potential=3000,  # 30% for conditional automation (higher than baseline)
                innovation_coefficient=0.030,  # +50% vs baseline
                imitation_coefficient=0.42,  # +40% vs baseline
            ),
            L4=LevelParameters(
                initial_adopters=0,
                market_potential=1500,  # 15% for high automation
                innovation_coefficient=0.020,  # +67% vs baseline
                imitation_coefficient=0.32,  # +45% vs baseline
            ),
            L5=LevelParameters(
                initial_adopters=0,
                market_potential=1000,  # 10% for full autonomy (2x baseline)
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
        Pessimistic scenario with slower adoption and concentration at lower automation levels.

        Assumptions (Mutually Exclusive Levels):
        - Total fleet: 10,000 vessels (fixed)
        - Regulatory barriers and uncertainty
        - Slower technological development
        - Economic challenges (high costs, unclear ROI)
        - Market resistance and safety concerns
        - Slower technology diffusion
        - Most fleet remains at L0-L2 (basic/manual operation)
        """
        return cls(
            total_fleet=10000,
            L1=LevelParameters(
                initial_adopters=450,
                market_potential=4000,  # 40% at basic level (higher than baseline)
                innovation_coefficient=0.025,  # -29% vs baseline
                imitation_coefficient=0.35,  # -22% vs baseline
            ),
            L2=LevelParameters(
                initial_adopters=450,
                market_potential=4000,  # 40% at partial automation
                innovation_coefficient=0.022,  # -27% vs baseline
                imitation_coefficient=0.30,  # -25% vs baseline
            ),
            L3=LevelParameters(
                initial_adopters=0,
                market_potential=1500,  # 15% for conditional automation (lower than baseline)
                innovation_coefficient=0.012,  # -40% vs baseline
                imitation_coefficient=0.20,  # -33% vs baseline
            ),
            L4=LevelParameters(
                initial_adopters=0,
                market_potential=400,  # 4% for high automation
                innovation_coefficient=0.007,  # -42% vs baseline
                imitation_coefficient=0.14,  # -36% vs baseline
            ),
            L5=LevelParameters(
                initial_adopters=0,
                market_potential=100,  # 1% for full autonomy (very limited)
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
            f"Fleet Size: {self.total_fleet} vessels (fixed)",
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
