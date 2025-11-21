"""
Interactive visualization app for the inland shipping ABM.

Run with:
    solara run app.py

Or:
    python app.py  (will provide instructions)
"""

import solara
from mesa.visualization import SolaraViz, make_space_component
from src.models.simple_abm import WaterwayModel, Vessel


def agent_portrayal(agent):
    """
    Define how vessels appear in the visualization.

    Color coding:
    - L0: Red (manual)
    - L1: Orange (steering assist)
    - L2: Gold (partial automation)
    - L3: Green (conditional automation)
    """
    if not isinstance(agent, Vessel):
        return {}

    color_map = {
        'L0': 'red',
        'L1': 'orange',
        'L2': 'gold',
        'L3': 'green'
    }

    # Position vessels vertically based on direction
    # Downstream (+1) at y=1, Upstream (-1) at y=-1
    y_position = 1 if agent.direction > 0 else -1

    return {
        "color": color_map.get(agent.automation_level, 'gray'),
        "size": 50,
        "marker": "arrow-right" if agent.direction > 0 else "arrow-left",
        "x": agent.position,
        "y": y_position,
    }


# Model parameters for interactive controls
model_params = {
    "n_vessels": {
        "type": "SliderInt",
        "value": 20,
        "label": "Number of Vessels",
        "min": 5,
        "max": 50,
        "step": 5,
    },
    "fleet_composition": {
        "type": "Select",
        "value": {'L0': 0.4, 'L1': 0.3, 'L2': 0.2, 'L3': 0.1},
        "label": "Fleet Composition",
        "choices": [
            {'L0': 0.4, 'L1': 0.3, 'L2': 0.2, 'L3': 0.1},  # Baseline
            {'L0': 1.0},  # All manual
            {'L0': 0.1, 'L1': 0.2, 'L2': 0.3, 'L3': 0.4},  # High automation
            {'L0': 0.25, 'L1': 0.25, 'L2': 0.25, 'L3': 0.25},  # Equal mix
        ],
    },
    "time_step": {
        "type": "SliderInt",
        "value": 5,
        "label": "Time Step (seconds)",
        "min": 1,
        "max": 10,
        "step": 1,
    },
}


@solara.component
def SpaceComponent(model):
    """
    Custom visualization of the waterway with vessels.
    """
    import plotly.graph_objects as go

    # Separate vessels by direction and level
    vessel_data = {'downstream': {}, 'upstream': {}}

    for level in ['L0', 'L1', 'L2', 'L3']:
        vessel_data['downstream'][level] = []
        vessel_data['upstream'][level] = []

    for agent in model.agents:
        direction_key = 'downstream' if agent.direction > 0 else 'upstream'
        vessel_data[direction_key][agent.automation_level].append({
            'position': agent.position,
            'id': agent.unique_id
        })

    # Color mapping
    color_map = {
        'L0': 'red',
        'L1': 'orange',
        'L2': 'gold',
        'L3': 'green'
    }

    # Create traces
    traces = []

    for level in ['L0', 'L1', 'L2', 'L3']:
        # Downstream vessels
        if vessel_data['downstream'][level]:
            traces.append(go.Scatter(
                x=[v['position'] for v in vessel_data['downstream'][level]],
                y=[1.0] * len(vessel_data['downstream'][level]),
                mode='markers',
                name=f'{level} ↓',
                marker=dict(
                    size=15,
                    color=color_map[level],
                    symbol='arrow-right',
                    line=dict(width=2, color='darkblue')
                ),
                text=[f"V{v['id']}" for v in vessel_data['downstream'][level]],
                hovertemplate='<b>%{text}</b><br>Pos: %{x:.0f}m<br>Level: ' + level + '<extra></extra>'
            ))

        # Upstream vessels
        if vessel_data['upstream'][level]:
            traces.append(go.Scatter(
                x=[v['position'] for v in vessel_data['upstream'][level]],
                y=[-1.0] * len(vessel_data['upstream'][level]),
                mode='markers',
                name=f'{level} ↑',
                marker=dict(
                    size=15,
                    color=color_map[level],
                    symbol='arrow-left',
                    line=dict(width=2, color='darkblue')
                ),
                text=[f"V{v['id']}" for v in vessel_data['upstream'][level]],
                hovertemplate='<b>%{text}</b><br>Pos: %{x:.0f}m<br>Level: ' + level + '<extra></extra>'
            ))

    # Create figure
    fig = go.Figure(data=traces)

    fig.update_layout(
        title={
            'text': f'<b>Waterway (Step {model.steps})</b>',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis=dict(
            title='Position along waterway (meters)',
            range=[0, 5000],
            showgrid=True,
            gridcolor='lightblue',
            zeroline=False
        ),
        yaxis=dict(
            title='Lane',
            range=[-1.5, 1.5],
            tickvals=[-1, 0, 1],
            ticktext=['← Upstream', 'Center', 'Downstream →'],
            showgrid=False,
            zeroline=True,
            zerolinecolor='blue',
            zerolinewidth=2
        ),
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        hovermode='closest',
        plot_bgcolor='#e6f3ff'
    )

    return solara.FigurePlotly(fig)


@solara.component
def MetricsCard(model):
    """Display real-time safety metrics."""
    stats = model.get_summary_statistics()

    with solara.Card(title="📊 Safety Metrics", elevation=2):
        with solara.Column(gap="10px"):
            solara.Markdown(f"**Simulation Step:** {model.steps}")
            solara.Markdown(f"**Total Encounters:** {stats['total_encounters']}")

            with solara.Row():
                with solara.Column():
                    solara.Markdown(f"**Near Misses:** {stats['near_misses']}")
                with solara.Column():
                    solara.Markdown(f"**Collisions:** :red[{stats['collisions']}]")

            solara.Markdown(f"**Avg Distance:** {stats['avg_encounter_distance']:.1f} m")

            if stats['total_encounters'] > 0:
                collision_rate = stats['collision_rate'] * 100
                color = "red" if collision_rate > 5 else "orange" if collision_rate > 3 else "green"
                solara.Markdown(f"**Collision Rate:** :{color}[{collision_rate:.2f}%]")


# Create the main visualization page
page = SolaraViz(
    model_class=WaterwayModel,
    model_params=model_params,
    measures=[
        {"name": "total_encounters", "label": "Total Encounters", "color": "blue"},
        {"name": "near_misses", "label": "Near Misses", "color": "orange"},
        {"name": "collisions", "label": "Collisions", "color": "red"},
        {"name": "avg_encounter_distance", "label": "Avg Distance (m)", "color": "green"},
    ],
    name="Inland Shipping Safety Simulation",
    space_drawer=SpaceComponent,
    play_interval=500,  # 500ms between steps for smooth animation
)


if __name__ == "__main__":
    import sys

    print("\n" + "=" * 80)
    print("INLAND SHIPPING ABM VISUALIZATION")
    print("=" * 80)
    print("\nTo run this visualization, use one of these commands:")
    print("\n  Option 1 (Recommended):")
    print("    solara run app.py")
    print("\n  Option 2:")
    print("    mesa runserver")
    print("\n" + "=" * 80)
    print("\nVisualization Features:")
    print("  - Real-time vessel tracking on waterway")
    print("  - Color-coded automation levels (Red=L0, Orange=L1, Yellow=L2, Green=L3)")
    print("  - Direction indicators (arrows)")
    print("  - Live safety metrics (collisions, near-misses, encounters)")
    print("  - Interactive controls (vessel count, fleet composition)")
    print("  - Time-series plots of safety metrics")
    print("=" * 80)
    print()

    # Check if solara is available
    try:
        import solara.server
        print("[OK] Solara is installed")
        print("\nRun: solara run app.py")
    except ImportError:
        print("[ERROR] Solara is not installed")
        print("\nInstall with: pip install solara")

    sys.exit(0)
