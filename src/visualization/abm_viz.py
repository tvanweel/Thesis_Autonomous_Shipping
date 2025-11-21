"""
Interactive visualization for the inland shipping ABM using Mesa's Solara-based visualization.

This module provides real-time visualization of vessel movements, showing:
- Vessel positions along the waterway
- Automation levels (color-coded)
- Direction of travel
- Real-time safety metrics
"""

import solara
from mesa.visualization import SolaraViz, make_plot_component
from src.models.simple_abm import WaterwayModel, Vessel


def vessel_portrayal(agent):
    """
    Define how to portray vessels in the visualization.

    Color coding by automation level:
    - L0 (Manual): Red
    - L1 (Steering assist): Orange
    - L2 (Partial automation): Yellow
    - L3 (Conditional automation): Green

    Shape indicates direction:
    - Triangle pointing right: Downstream (+1)
    - Triangle pointing left: Upstream (-1)
    """
    if not isinstance(agent, Vessel):
        return None

    # Color based on automation level
    color_map = {
        'L0': '#FF4444',  # Red
        'L1': '#FF8C00',  # Orange
        'L2': '#FFD700',  # Gold/Yellow
        'L3': '#00CC66'   # Green
    }

    # Size based on detection range (larger = better sensors)
    size_map = {
        'L0': 8,
        'L1': 10,
        'L2': 12,
        'L3': 14
    }

    portrayal = {
        "color": color_map.get(agent.automation_level, '#888888'),
        "size": size_map.get(agent.automation_level, 10),
        "filled": True,
        "shape": "circle",  # Using circles for simplicity
        "layer": 1,
        # Custom marker to show direction
        "marker": ">" if agent.direction > 0 else "<",
        # Tooltip info
        "tooltip": f"Vessel {agent.unique_id}\n"
                  f"Level: {agent.automation_level}\n"
                  f"Position: {agent.position:.0f}m\n"
                  f"Direction: {'Downstream' if agent.direction > 0 else 'Upstream'}\n"
                  f"Detection: {agent.detection_range}m"
    }

    return portrayal


def draw_waterway(agent):
    """
    Draw vessels on a 1D waterway represented in 2D space.

    X-axis: Position along waterway (0-5000m)
    Y-axis: Separated by direction (upstream/downstream) for clarity
    """
    if not isinstance(agent, Vessel):
        return None

    # Color based on automation level
    color_map = {
        'L0': 'red',
        'L1': 'orange',
        'L2': 'gold',
        'L3': 'green'
    }

    return {
        "x": agent.position,  # Position along waterway
        "y": 1 if agent.direction > 0 else -1,  # Separate by direction
        "color": color_map.get(agent.automation_level, 'gray'),
        "size": 15,
        "marker": "arrow-right" if agent.direction > 0 else "arrow-left"
    }


# Custom plot components for metrics
def make_collision_plot():
    """Create a plot showing collision count over time."""
    return make_plot_component(
        {
            "Collisions": {"color": "red", "type": "line"},
        }
    )


def make_encounter_plot():
    """Create a plot showing total encounters over time."""
    return make_plot_component(
        {
            "Total Encounters": {"color": "blue", "type": "line"},
            "Near Misses": {"color": "orange", "type": "line"},
            "Collisions": {"color": "red", "type": "line"},
        }
    )


def make_distance_plot():
    """Create a plot showing average encounter distance over time."""
    return make_plot_component(
        {
            "Average Distance": {"color": "green", "type": "line"},
        }
    )


# Model parameters for the interactive controls
model_params = {
    "n_vessels": {
        "type": "SliderInt",
        "value": 20,
        "label": "Number of Vessels",
        "min": 5,
        "max": 50,
        "step": 5,
    },
    "time_step": {
        "type": "SliderInt",
        "value": 5,
        "label": "Time Step (seconds)",
        "min": 1,
        "max": 10,
        "step": 1,
    },
    "fleet_composition": {
        "type": "Select",
        "value": {'L0': 0.4, 'L1': 0.3, 'L2': 0.2, 'L3': 0.1},
        "label": "Fleet Composition",
        "choices": {
            "Baseline": {'L0': 0.4, 'L1': 0.3, 'L2': 0.2, 'L3': 0.1},
            "All Manual": {'L0': 1.0},
            "High Automation": {'L0': 0.1, 'L1': 0.2, 'L2': 0.3, 'L3': 0.4},
            "Equal Mix": {'L0': 0.25, 'L1': 0.25, 'L2': 0.25, 'L3': 0.25},
        }
    }
}


# Create custom space drawer for the waterway
@solara.component
def WaterwayCanvas(model):
    """
    Custom canvas component to draw the waterway and vessels.

    Shows vessels as colored markers along a horizontal line representing
    the 5km waterway, with upstream/downstream separated vertically.
    """
    import plotly.graph_objects as go

    # Collect vessel data
    downstream_vessels = []
    upstream_vessels = []

    for agent in model.agents:
        vessel_data = {
            'position': agent.position,
            'level': agent.automation_level,
            'id': agent.unique_id,
            'detection': agent.detection_range
        }

        if agent.direction > 0:
            downstream_vessels.append(vessel_data)
        else:
            upstream_vessels.append(vessel_data)

    # Color mapping
    color_map = {
        'L0': 'red',
        'L1': 'orange',
        'L2': 'gold',
        'L3': 'green'
    }

    # Create traces
    traces = []

    # Downstream vessels
    if downstream_vessels:
        for level in ['L0', 'L1', 'L2', 'L3']:
            level_vessels = [v for v in downstream_vessels if v['level'] == level]
            if level_vessels:
                traces.append(go.Scatter(
                    x=[v['position'] for v in level_vessels],
                    y=[1] * len(level_vessels),
                    mode='markers',
                    name=f'{level} Downstream',
                    marker=dict(
                        size=12,
                        color=color_map[level],
                        symbol='arrow-right',
                        line=dict(width=1, color='black')
                    ),
                    hovertemplate='<b>%{text}</b><br>Position: %{x:.0f}m<extra></extra>',
                    text=[f"Vessel {v['id']} ({v['level']})" for v in level_vessels]
                ))

    # Upstream vessels
    if upstream_vessels:
        for level in ['L0', 'L1', 'L2', 'L3']:
            level_vessels = [v for v in upstream_vessels if v['level'] == level]
            if level_vessels:
                traces.append(go.Scatter(
                    x=[v['position'] for v in level_vessels],
                    y=[-1] * len(level_vessels),
                    mode='markers',
                    name=f'{level} Upstream',
                    marker=dict(
                        size=12,
                        color=color_map[level],
                        symbol='arrow-left',
                        line=dict(width=1, color='black')
                    ),
                    hovertemplate='<b>%{text}</b><br>Position: %{x:.0f}m<extra></extra>',
                    text=[f"Vessel {v['id']} ({v['level']})" for v in level_vessels]
                ))

    # Create figure
    fig = go.Figure(data=traces)

    # Update layout
    fig.update_layout(
        title='Waterway Vessel Positions',
        xaxis=dict(
            title='Position along waterway (meters)',
            range=[0, 5000],
            showgrid=True,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title='Lane',
            range=[-2, 2],
            tickvals=[-1, 1],
            ticktext=['Upstream ←', 'Downstream →'],
            showgrid=False
        ),
        height=300,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='closest'
    )

    # Add waterway reference line
    fig.add_shape(
        type="line",
        x0=0, x1=5000, y0=0, y1=0,
        line=dict(color="blue", width=2, dash="dash")
    )

    return solara.FigurePlotly(fig)


@solara.component
def MetricsDisplay(model):
    """Display current safety metrics."""
    stats = model.get_summary_statistics()

    with solara.Column():
        solara.Text(f"🚢 Simulation Step: {model.steps}", style={"font-size": "16px", "font-weight": "bold"})
        solara.Text(f"⚠️ Total Encounters: {stats['total_encounters']}", style={"font-size": "14px"})
        solara.Text(f"🟡 Near Misses: {stats['near_misses']}", style={"color": "orange", "font-size": "14px"})
        solara.Text(f"🔴 Collisions: {stats['collisions']}", style={"color": "red", "font-size": "14px", "font-weight": "bold"})
        solara.Text(f"📏 Avg Distance: {stats['avg_encounter_distance']:.1f}m", style={"font-size": "14px"})
        if stats['total_encounters'] > 0:
            solara.Text(f"📊 Collision Rate: {stats['collision_rate']*100:.2f}%", style={"font-size": "14px"})


def create_visualization():
    """
    Create and return the complete SolaraViz visualization.

    Returns:
        SolaraViz: Interactive visualization object ready to launch
    """
    # Create the visualization with custom components
    page = SolaraViz(
        model_class=WaterwayModel,
        model_params=model_params,
        measures=[
            "total_encounters",
            "near_misses",
            "collisions",
            "avg_encounter_distance"
        ],
        name="Inland Shipping Safety Simulation",
        # Custom agent portrayal
        agent_portrayal=draw_waterway,
        space_drawer=WaterwayCanvas,
        play_interval=500,  # milliseconds between steps
    )

    return page


# Standalone function to launch the visualization
def launch_visualization(port=8521):
    """
    Launch the interactive visualization server.

    Args:
        port: Port number for the web server (default: 8521)
    """
    viz = create_visualization()
    viz.launch(port=port, open_browser=True)
