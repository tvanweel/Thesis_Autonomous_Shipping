"""
Basic simulation runner for the minimal inland shipping ABM.

This script demonstrates how to:
1. Set up a simulation with a specific fleet composition
2. Run the simulation for 1 hour (720 steps at 5 seconds each)
3. Extract and display safety metrics

Usage:
    python -m examples.run_basic_sim
"""

import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.simple_abm import WaterwayModel


def run_simulation(fleet_composition, n_vessels=20, duration_hours=1, time_step=5):
    """
    Run a single simulation with specified parameters.

    Args:
        fleet_composition: Dictionary mapping automation levels to proportions
        n_vessels: Number of vessels to simulate
        duration_hours: Simulation duration in hours
        time_step: Time step in seconds

    Returns:
        Dictionary with simulation results
    """
    print("=" * 60)
    print("INLAND SHIPPING SAFETY SIMULATION")
    print("=" * 60)
    print(f"\nSimulation Parameters:")
    print(f"  - Number of vessels: {n_vessels}")
    print(f"  - Duration: {duration_hours} hour(s)")
    print(f"  - Time step: {time_step} seconds")
    print(f"  - Waterway: 5 km straight channel")
    print(f"\nFleet Composition:")
    for level, proportion in sorted(fleet_composition.items()):
        count = int(n_vessels * proportion)
        print(f"  - {level}: {proportion*100:.0f}% ({count} vessels)")

    # Initialize model
    model = WaterwayModel(
        n_vessels=n_vessels,
        fleet_composition=fleet_composition,
        time_step=time_step
    )

    # Calculate number of steps
    steps = int((duration_hours * 3600) / time_step)

    print(f"\nRunning simulation for {steps} steps...")

    # Run simulation
    for i in range(steps):
        model.step()
        # Progress indicator every 100 steps
        if (i + 1) % 100 == 0:
            print(f"  Progress: {i + 1}/{steps} steps ({(i+1)/steps*100:.1f}%)")

    print("\n" + "=" * 60)
    print("SIMULATION RESULTS")
    print("=" * 60)

    # Get summary statistics
    stats = model.get_summary_statistics()

    print(f"\nSafety Metrics:")
    print(f"  - Total encounters: {stats['total_encounters']}")
    print(f"  - Safe encounters (>100m): {stats['encounters_safe']}")
    print(f"  - Near misses (50-100m): {stats['near_misses']}")
    print(f"  - Collisions (<50m): {stats['collisions']}")
    print(f"  - Average encounter distance: {stats['avg_encounter_distance']:.1f} m")
    print(f"  - Collision rate: {stats['collision_rate']*100:.2f}%")

    print("\n" + "=" * 60)

    return stats


def compare_scenarios():
    """
    Compare safety outcomes across different fleet compositions.
    """
    print("\n" + "=" * 60)
    print("SCENARIO COMPARISON")
    print("=" * 60)

    scenarios = {
        "All Manual (L0)": {
            'L0': 1.0
        },
        "Mixed Fleet - Baseline": {
            'L0': 0.4,
            'L1': 0.3,
            'L2': 0.2,
            'L3': 0.1
        },
        "High Automation": {
            'L0': 0.1,
            'L1': 0.2,
            'L2': 0.3,
            'L3': 0.4
        }
    }

    results = {}

    for scenario_name, fleet_comp in scenarios.items():
        print(f"\n{'='*60}")
        print(f"Scenario: {scenario_name}")
        print(f"{'='*60}")

        stats = run_simulation(fleet_comp, n_vessels=20, duration_hours=1)
        results[scenario_name] = stats

    # Summary comparison
    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)
    print(f"\n{'Scenario':<30} {'Collisions':<12} {'Near Misses':<12} {'Avg Distance':<12}")
    print("-" * 66)

    for scenario_name, stats in results.items():
        print(f"{scenario_name:<30} {stats['collisions']:<12} {stats['near_misses']:<12} {stats['avg_encounter_distance']:<12.1f}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Run single simulation with baseline fleet composition
    fleet_comp = {
        'L0': 0.4,  # 40% manual
        'L1': 0.3,  # 30% steering assistance
        'L2': 0.2,  # 20% partial automation
        'L3': 0.1   # 10% conditional automation
    }

    print("\n" + "=" * 60)
    print("SINGLE SIMULATION RUN")
    print("=" * 60)

    run_simulation(fleet_comp)

    # Run scenario comparison to demonstrate automation impact:
    compare_scenarios()
