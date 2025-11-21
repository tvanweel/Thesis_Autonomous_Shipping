"""
Comprehensive visualization script for multi-level automation diffusion model.

Generates multiple visualizations:
1. Multi-level adoption curves (all 5 levels + L0 baseline)
2. Scenario comparison (baseline/optimistic/pessimistic)
3. Market share evolution (stacked area chart)
4. Uncertainty bands (range across scenarios)
5. Sensitivity analysis (varying key parameters)
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from src.models.diffusion import MultiLevelAutomationDiffusion
from src.config import DiffusionConfig


# Set up output directory
RESULTS_DIR = Path(__file__).parent.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Color scheme for automation levels
COLORS = {
    "L0": "#2C3E50",  # Dark gray (manual)
    "L1": "#3498DB",  # Blue (steering assistance)
    "L2": "#2ECC71",  # Green (partial automation)
    "L3": "#F39C12",  # Orange (conditional automation)
    "L4": "#E74C3C",  # Red (high automation)
    "L5": "#9B59B6",  # Purple (full automation)
}

SCENARIO_COLORS = {
    "baseline": "#3498DB",    # Blue
    "optimistic": "#2ECC71",  # Green
    "pessimistic": "#E74C3C", # Red
}


def run_model_from_config(config: DiffusionConfig) -> MultiLevelAutomationDiffusion:
    """Run simulation with given configuration."""
    model = MultiLevelAutomationDiffusion(**config.to_model_params())
    model.run(steps=config.time_horizon)
    return model


def calculate_L0(model: MultiLevelAutomationDiffusion) -> np.ndarray:
    """Calculate L0 (manual/non-adopters) vessels over time."""
    L1 = np.array(model.history_L1)
    return model.total_fleet - L1


def plot_1_multilevel_adoption_curves(config: DiffusionConfig, save_path: Path):
    """
    Visualization 1: Multi-level adoption curves over time.
    Shows all 5 automation levels plus L0 baseline on one plot.
    """
    print("Generating Visualization 1: Multi-level adoption curves...")

    model = run_model_from_config(config)

    t = np.array(model.history_time)
    L0 = calculate_L0(model)
    L1 = np.array(model.history_L1)
    L2 = np.array(model.history_L2)
    L3 = np.array(model.history_L3)
    L4 = np.array(model.history_L4)
    L5 = np.array(model.history_L5)

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(t, L0, label="L0 - Manual", color=COLORS["L0"], linewidth=2, linestyle="--")
    ax.plot(t, L1, label="L1 - Steering Assistance", color=COLORS["L1"], linewidth=2.5)
    ax.plot(t, L2, label="L2 - Partial Automation", color=COLORS["L2"], linewidth=2.5)
    ax.plot(t, L3, label="L3 - Conditional Automation", color=COLORS["L3"], linewidth=2.5)
    ax.plot(t, L4, label="L4 - High Automation", color=COLORS["L4"], linewidth=2.5)
    ax.plot(t, L5, label="L5 - Full Automation", color=COLORS["L5"], linewidth=2.5)

    ax.set_xlabel("Time (years)", fontsize=12)
    ax.set_ylabel("Number of Vessels", fontsize=12)
    ax.set_title(
        f"Automation Adoption in Inland Shipping ({config.scenario_name.capitalize()} Scenario)",
        fontsize=14,
        fontweight="bold",
    )
    ax.legend(loc="best", fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    print(f"  Saved to: {save_path}")
    plt.close()


def plot_2_scenario_comparison(scenarios: dict, save_path: Path):
    """
    Visualization 2: Scenario comparison.
    Overlays baseline/optimistic/pessimistic scenarios for each level.
    """
    print("Generating Visualization 2: Scenario comparison...")

    # Run all scenarios
    results = {}
    for name, config in scenarios.items():
        results[name] = run_model_from_config(config)

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()

    level_names = ["L0 - Manual", "L1 - Steering", "L2 - Partial",
                   "L3 - Conditional", "L4 - High", "L5 - Full"]

    for idx, (level_num, level_name) in enumerate(zip([0, 1, 2, 3, 4, 5], level_names)):
        ax = axes[idx]

        for scenario_name, model in results.items():
            t = np.array(model.history_time)

            if level_num == 0:
                data = calculate_L0(model)
            else:
                data = np.array(getattr(model, f"history_L{level_num}"))

            ax.plot(
                t,
                data,
                label=scenario_name.capitalize(),
                color=SCENARIO_COLORS[scenario_name],
                linewidth=2.5,
            )

        ax.set_xlabel("Time (years)", fontsize=10)
        ax.set_ylabel("Vessels", fontsize=10)
        ax.set_title(level_name, fontsize=11, fontweight="bold")
        ax.legend(loc="best", fontsize=9)
        ax.grid(True, alpha=0.3)

    fig.suptitle(
        "Scenario Comparison: Baseline vs. Optimistic vs. Pessimistic",
        fontsize=16,
        fontweight="bold",
    )
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    print(f"  Saved to: {save_path}")
    plt.close()


def plot_3_market_share_evolution(config: DiffusionConfig, save_path: Path):
    """
    Visualization 3: Market share evolution.
    Stacked area chart showing proportion of fleet at each automation level.
    """
    print("Generating Visualization 3: Market share evolution...")

    model = run_model_from_config(config)

    t = np.array(model.history_time)
    L0 = calculate_L0(model)
    L1 = np.array(model.history_L1)
    L2 = np.array(model.history_L2)
    L3 = np.array(model.history_L3)
    L4 = np.array(model.history_L4)
    L5 = np.array(model.history_L5)

    # Calculate market shares (percentage)
    total = model.total_fleet
    share_L0 = (L0 / total) * 100
    share_L1_only = ((L1 - L2) / total) * 100
    share_L2_only = ((L2 - L3) / total) * 100
    share_L3_only = ((L3 - L4) / total) * 100
    share_L4_only = ((L4 - L5) / total) * 100
    share_L5 = (L5 / total) * 100

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.fill_between(t, 0, share_L0, label="L0 - Manual", color=COLORS["L0"], alpha=0.8)
    ax.fill_between(
        t,
        share_L0,
        share_L0 + share_L1_only,
        label="L1 - Steering Assistance",
        color=COLORS["L1"],
        alpha=0.8,
    )
    ax.fill_between(
        t,
        share_L0 + share_L1_only,
        share_L0 + share_L1_only + share_L2_only,
        label="L2 - Partial Automation",
        color=COLORS["L2"],
        alpha=0.8,
    )
    ax.fill_between(
        t,
        share_L0 + share_L1_only + share_L2_only,
        share_L0 + share_L1_only + share_L2_only + share_L3_only,
        label="L3 - Conditional Automation",
        color=COLORS["L3"],
        alpha=0.8,
    )
    ax.fill_between(
        t,
        share_L0 + share_L1_only + share_L2_only + share_L3_only,
        share_L0 + share_L1_only + share_L2_only + share_L3_only + share_L4_only,
        label="L4 - High Automation",
        color=COLORS["L4"],
        alpha=0.8,
    )
    ax.fill_between(
        t,
        share_L0 + share_L1_only + share_L2_only + share_L3_only + share_L4_only,
        100,
        label="L5 - Full Automation",
        color=COLORS["L5"],
        alpha=0.8,
    )

    ax.set_xlabel("Time (years)", fontsize=12)
    ax.set_ylabel("Market Share (%)", fontsize=12)
    ax.set_title(
        f"Fleet Automation Market Share Evolution ({config.scenario_name.capitalize()} Scenario)",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_ylim(0, 100)
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5), fontsize=10)
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    print(f"  Saved to: {save_path}")
    plt.close()


def plot_4_uncertainty_bands(scenarios: dict, save_path: Path):
    """
    Visualization 4: Uncertainty bands.
    Shows range across scenarios for each automation level.
    """
    print("Generating Visualization 4: Uncertainty bands...")

    # Run all scenarios
    results = {}
    for name, config in scenarios.items():
        results[name] = run_model_from_config(config)

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()

    level_names = ["L0 - Manual", "L1 - Steering", "L2 - Partial",
                   "L3 - Conditional", "L4 - High", "L5 - Full"]

    for idx, (level_num, level_name) in enumerate(zip([0, 1, 2, 3, 4, 5], level_names)):
        ax = axes[idx]

        # Get baseline data
        baseline_model = results["baseline"]
        t = np.array(baseline_model.history_time)

        if level_num == 0:
            baseline_data = calculate_L0(baseline_model)
            optimistic_data = calculate_L0(results["optimistic"])
            pessimistic_data = calculate_L0(results["pessimistic"])
        else:
            baseline_data = np.array(getattr(baseline_model, f"history_L{level_num}"))
            optimistic_data = np.array(getattr(results["optimistic"], f"history_L{level_num}"))
            pessimistic_data = np.array(getattr(results["pessimistic"], f"history_L{level_num}"))

        # Plot baseline
        ax.plot(t, baseline_data, label="Baseline", color=SCENARIO_COLORS["baseline"], linewidth=2.5)

        # Fill uncertainty band
        ax.fill_between(
            t,
            pessimistic_data,
            optimistic_data,
            alpha=0.3,
            color=SCENARIO_COLORS["baseline"],
            label="Uncertainty Range",
        )

        ax.set_xlabel("Time (years)", fontsize=10)
        ax.set_ylabel("Vessels", fontsize=10)
        ax.set_title(level_name, fontsize=11, fontweight="bold")
        ax.legend(loc="best", fontsize=9)
        ax.grid(True, alpha=0.3)

    fig.suptitle(
        "Uncertainty Analysis: Baseline with Scenario Range",
        fontsize=16,
        fontweight="bold",
    )
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    print(f"  Saved to: {save_path}")
    plt.close()


def plot_5_sensitivity_analysis(base_config: DiffusionConfig, save_path: Path):
    """
    Visualization 5: Sensitivity analysis.
    Shows impact of varying key parameters (p, q, M) on L3 adoption.
    """
    print("Generating Visualization 5: Sensitivity analysis...")

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Base model
    base_model = run_model_from_config(base_config)
    t = np.array(base_model.history_time)
    base_L3 = np.array(base_model.history_L3)

    # Sensitivity to p3 (innovation coefficient)
    ax = axes[0]
    for factor, label in [(0.5, "50% lower"), (1.0, "baseline"), (1.5, "50% higher")]:
        config = DiffusionConfig.baseline()
        config.L3.innovation_coefficient *= factor
        model = run_model_from_config(config)
        L3 = np.array(model.history_L3)
        linestyle = "--" if factor != 1.0 else "-"
        linewidth = 2.0 if factor != 1.0 else 2.5
        ax.plot(t, L3, label=f"p3 {label}", linestyle=linestyle, linewidth=linewidth)

    ax.set_xlabel("Time (years)", fontsize=11)
    ax.set_ylabel("L3 Vessels", fontsize=11)
    ax.set_title("Sensitivity to Innovation Coefficient (p3)", fontsize=12, fontweight="bold")
    ax.legend(loc="best", fontsize=10)
    ax.grid(True, alpha=0.3)

    # Sensitivity to q3 (imitation coefficient)
    ax = axes[1]
    for factor, label in [(0.5, "50% lower"), (1.0, "baseline"), (1.5, "50% higher")]:
        config = DiffusionConfig.baseline()
        config.L3.imitation_coefficient *= factor
        model = run_model_from_config(config)
        L3 = np.array(model.history_L3)
        linestyle = "--" if factor != 1.0 else "-"
        linewidth = 2.0 if factor != 1.0 else 2.5
        ax.plot(t, L3, label=f"q3 {label}", linestyle=linestyle, linewidth=linewidth)

    ax.set_xlabel("Time (years)", fontsize=11)
    ax.set_ylabel("L3 Vessels", fontsize=11)
    ax.set_title("Sensitivity to Imitation Coefficient (q3)", fontsize=12, fontweight="bold")
    ax.legend(loc="best", fontsize=10)
    ax.grid(True, alpha=0.3)

    # Sensitivity to M3 (market potential)
    ax = axes[2]
    for factor, label in [(0.7, "30% lower"), (1.0, "baseline"), (1.3, "30% higher")]:
        config = DiffusionConfig.baseline()
        config.L3.market_potential *= factor
        model = run_model_from_config(config)
        L3 = np.array(model.history_L3)
        linestyle = "--" if factor != 1.0 else "-"
        linewidth = 2.0 if factor != 1.0 else 2.5
        ax.plot(t, L3, label=f"M3 {label}", linestyle=linestyle, linewidth=linewidth)

    ax.set_xlabel("Time (years)", fontsize=11)
    ax.set_ylabel("L3 Vessels", fontsize=11)
    ax.set_title("Sensitivity to Market Potential (M3)", fontsize=12, fontweight="bold")
    ax.legend(loc="best", fontsize=10)
    ax.grid(True, alpha=0.3)

    fig.suptitle(
        "Sensitivity Analysis: L3 (Conditional Automation) Adoption",
        fontsize=16,
        fontweight="bold",
    )
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    print(f"  Saved to: {save_path}")
    plt.close()


def main():
    """Generate all visualizations."""
    print("=" * 70)
    print("Multi-Level Automation Diffusion Model - Visualization Suite")
    print("=" * 70)
    print()

    # Load scenarios
    scenarios = DiffusionConfig.get_all_scenarios()
    baseline = scenarios["baseline"]

    # Print configuration summary
    print(baseline.summary())
    print()

    # Generate all visualizations
    print("Generating visualizations...")
    print("-" * 70)

    plot_1_multilevel_adoption_curves(
        baseline,
        RESULTS_DIR / "1_multilevel_adoption_curves.png"
    )

    plot_2_scenario_comparison(
        scenarios,
        RESULTS_DIR / "2_scenario_comparison.png"
    )

    plot_3_market_share_evolution(
        baseline,
        RESULTS_DIR / "3_market_share_evolution.png"
    )

    plot_4_uncertainty_bands(
        scenarios,
        RESULTS_DIR / "4_uncertainty_bands.png"
    )

    plot_5_sensitivity_analysis(
        baseline,
        RESULTS_DIR / "5_sensitivity_analysis.png"
    )

    print()
    print("=" * 70)
    print("All visualizations generated successfully!")
    print(f"Results saved to: {RESULTS_DIR.absolute()}")
    print("=" * 70)


if __name__ == "__main__":
    main()
