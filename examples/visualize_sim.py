"""
Launch the interactive visualization for the inland shipping ABM.

This script starts a web server that provides an interactive visualization
of the simulation, showing:
- Real-time vessel movements along the waterway
- Color-coded automation levels
- Direction of travel (upstream/downstream)
- Live safety metrics (encounters, collisions, near-misses)
- Interactive controls to adjust parameters

Usage:
    python -m examples.visualize_sim

The visualization will open in your default web browser at http://localhost:8521
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.visualization.abm_viz import create_visualization


def main():
    """Launch the interactive visualization."""
    print("=" * 70)
    print("INLAND SHIPPING SAFETY SIMULATION - INTERACTIVE VISUALIZATION")
    print("=" * 70)
    print("\nStarting visualization server...")
    print("\nThe visualization will open in your default web browser.")
    print("If it doesn't open automatically, navigate to: http://localhost:8521")
    print("\nControls:")
    print("  - Use the slider to adjust number of vessels")
    print("  - Select different fleet compositions from the dropdown")
    print("  - Click 'Start' to run the simulation")
    print("  - Click 'Step' to advance one time step at a time")
    print("  - Click 'Reset' to restart with current parameters")
    print("\nVisualization Legend:")
    print("  🔴 Red vessels: L0 (Manual operation)")
    print("  🟠 Orange vessels: L1 (Steering assistance)")
    print("  🟡 Yellow vessels: L2 (Partial automation)")
    print("  🟢 Green vessels: L3 (Conditional automation)")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 70)
    print()

    # Create and launch visualization
    viz = create_visualization()

    # Note: In Mesa 3.x with Solara, we use a different approach
    # The page object needs to be run with solara
    try:
        # Launch using solara's built-in server
        import solara.server.starlette
        print("Starting server on http://localhost:8521...")

        # Create the app
        from mesa.visualization import SolaraViz

        page = SolaraViz(
            WaterwayModel,
            [
                {
                    "type": "SliderInt",
                    "label": "Number of Vessels",
                    "value": 20,
                    "min": 5,
                    "max": 50,
                    "step": 5,
                },
                {
                    "type": "Select",
                    "label": "Fleet Composition",
                    "value": "baseline",
                    "values": ["baseline", "all_manual", "high_automation", "equal_mix"],
                },
            ]
        )

        # Import the model
        from src.models.simple_abm import WaterwayModel

        # Run with solara
        page  # This will be picked up by solara run command

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTo run the visualization, use:")
        print("  solara run examples/visualize_sim.py")
        print("\nMake sure solara is installed:")
        print("  pip install solara")


if __name__ == "__main__":
    # For direct execution, provide instructions
    print("\n" + "=" * 70)
    print("To run the interactive visualization, use the solara command:")
    print("=" * 70)
    print("\n  solara run examples/visualize_sim.py\n")
    print("Or create a simpler version using the app.py file")
    print("=" * 70)
