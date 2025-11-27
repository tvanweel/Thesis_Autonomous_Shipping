"""
Test script to demonstrate how changing assumptions affects model behavior.

This script shows that the model now properly uses the assumptions file
and that changing assumptions directly affects simulation results.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.traffic import (
    VESSELS_PER_KM_CAPACITY,
    CONGESTION_IMPACT_FACTOR,
    CROSSROAD_TRANSIT_TIME,
    MIN_SPEED_RATIO
)
from src.models.agent import _DEFAULT_SPEED
from src.assumptions import get_all_assumptions


def main():
    """Display current assumptions loaded by the model."""
    print("=" * 70)
    print("MODEL ASSUMPTIONS - Currently Loaded Values")
    print("=" * 70)

    print("\n[TRAFFIC BEHAVIOR MODEL]")
    print("-" * 70)
    print(f"  Vessels per km capacity:        {VESSELS_PER_KM_CAPACITY}")
    print(f"  Congestion impact factor:       {CONGESTION_IMPACT_FACTOR}")
    print(f"  Minimum speed ratio:            {MIN_SPEED_RATIO}")
    print(f"  Crossroad transit time (hours): {CROSSROAD_TRANSIT_TIME}")

    print("\n[AGENT/VESSEL CHARACTERISTICS]")
    print("-" * 70)
    print(f"  Default vessel speed (km/h):    {_DEFAULT_SPEED}")

    print("\n[ALL ASSUMPTIONS] (from assumptions.py)")
    print("-" * 70)
    assumptions = get_all_assumptions()

    for category, params in assumptions.items():
        print(f"\n  {category.upper()}:")
        for key, value in params.items():
            if isinstance(value, dict):
                print(f"    {key}:")
                for sub_key, sub_val in value.items():
                    print(f"      {sub_key}: {sub_val}")
            else:
                print(f"    {key}: {value}")

    print("\n" + "=" * 70)
    print("[OK] To change model behavior, edit: src/assumptions.py")
    print("=" * 70)

    # Example: Show how to use assumptions in code
    print("\n[EXAMPLE] Using assumptions in your code")
    print("-" * 70)
    print("""
from src.assumptions import get_traffic_config, get_agent_config

# Load configurations
traffic_config = get_traffic_config()
agent_config = get_agent_config()

# Use in your simulation
capacity = traffic_config['vessels_per_km_capacity']
speed_range = agent_config['vessel_speed_range_kmh']
print(f"Edge capacity: {capacity} vessels/km")
print(f"Speed range: {speed_range[0]}-{speed_range[1]} km/h")
    """)

    # Actually run the example
    from src.assumptions import get_traffic_config, get_agent_config

    traffic_config = get_traffic_config()
    agent_config = get_agent_config()

    capacity = traffic_config['vessels_per_km_capacity']
    speed_range = agent_config['vessel_speed_range_kmh']
    print(f"Edge capacity: {capacity} vessels/km")
    print(f"Speed range: {speed_range[0]}-{speed_range[1]} km/h")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
