"""
Agent Demo - Random Ships With Traffic Behavior

Demonstrates a simulation with:
- Randomly generated ships with random start/destination
- Random automation levels (0-5)
- Realistic traffic behavior (congestion, crossroads)
- Dynamic speed adjustment based on vessel density
- Performance metrics (travel time, system time, waiting time)
- CSV export of all ship data

Usage:
    Command line: python agent_demo_random.py --ships 20 --seed 42 --non-interactive
    IPython/Jupyter: Run the file directly, or call main(num_ships=20, seed=42, interactive=False)
"""

import sys
import random
import csv
from pathlib import Path
from typing import List, Tuple
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.network import Network, Node, Edge
from src.models.agent import Agent, AgentState, create_agent, reset_agent_id_counter
from src.models.traffic import TrafficManager
from src.assumptions import get_agent_config


def create_rhine_network() -> Network:
    """Create a network representing Rhine river ports."""
    network = Network(directed=True)

    # Add nodes representing ports
    ports = [
        Node(id="Rotterdam", name="Rotterdam Port", node_type="port",
             properties={"capacity": 470000000}),
        Node(id="Dordrecht", name="Dordrecht Port", node_type="port",
             properties={"capacity": 50000000}),
        Node(id="Nijmegen", name="Nijmegen Port", node_type="port",
             properties={"capacity": 20000000}),
        Node(id="Duisburg", name="Duisburg Port", node_type="port",
             properties={"capacity": 50000000}),
        Node(id="Cologne", name="Cologne Port", node_type="port",
             properties={"capacity": 30000000}),
        Node(id="Mannheim", name="Mannheim Port", node_type="port",
             properties={"capacity": 25000000}),
    ]

    for port in ports:
        network.add_node(port)

    # Add edges (shipping routes with distances in km)
    routes = [
        Edge("Rotterdam", "Dordrecht", weight=24.0, properties={"distance_km": 24}),
        Edge("Dordrecht", "Nijmegen", weight=95.0, properties={"distance_km": 95}),
        Edge("Nijmegen", "Duisburg", weight=111.0, properties={"distance_km": 111}),
        Edge("Duisburg", "Cologne", weight=60.0, properties={"distance_km": 60}),
        Edge("Cologne", "Mannheim", weight=143.0, properties={"distance_km": 143}),
        # Alternative route
        Edge("Rotterdam", "Nijmegen", weight=130.0, properties={"distance_km": 130}),
        # Reverse routes for bidirectional travel
        Edge("Dordrecht", "Rotterdam", weight=24.0, properties={"distance_km": 24}),
        Edge("Nijmegen", "Dordrecht", weight=95.0, properties={"distance_km": 95}),
        Edge("Duisburg", "Nijmegen", weight=111.0, properties={"distance_km": 111}),
        Edge("Cologne", "Duisburg", weight=60.0, properties={"distance_km": 60}),
        Edge("Mannheim", "Cologne", weight=143.0, properties={"distance_km": 143}),
        Edge("Nijmegen", "Rotterdam", weight=130.0, properties={"distance_km": 130}),
    ]

    for route in routes:
        network.add_edge(route)

    return network


def create_random_ships(
    num_ships: int,
    port_ids: List[str],
    network: Network
) -> List[Agent]:
    """
    Create random ships with random start/destination and automation levels.

    Args:
        num_ships: Number of ships to create
        port_ids: List of available port IDs
        network: Network for route planning

    Returns:
        List of Agent objects
    """
    reset_agent_id_counter()

    # Load agent configuration from assumptions
    agent_config = get_agent_config()
    speed_min, speed_max = agent_config["vessel_speed_range_kmh"]
    ris_probs = agent_config["ris_connectivity_by_level"]

    ships = []

    for i in range(num_ships):
        # Random start location
        start = random.choice(port_ids)

        # Random destination (different from start)
        available_destinations = [p for p in port_ids if p != start]
        destination = random.choice(available_destinations)

        # Random automation level (0-5)
        automation_level = random.randint(0, 5)

        # Random speed from configured range
        speed = random.uniform(speed_min, speed_max)

        # RIS connectivity based on automation level (from assumptions)
        if automation_level <= 2:
            ris_connected = random.random() < ris_probs["L0_L2"]
        elif automation_level <= 4:
            ris_connected = random.random() < ris_probs["L3_L4"]
        else:
            ris_connected = random.random() < ris_probs["L5"]

        # Create agent
        ship = create_agent(
            "vessel",
            start,
            start,
            automation_level=automation_level,
            speed=speed,
            ris_connected=ris_connected
        )

        # Set destination
        try:
            ship.set_destination(destination, network)
            ships.append(ship)
        except ValueError:
            # Skip if no path exists
            pass

    return ships

def export_ships_to_csv(ships: List[Agent], metrics: dict, filename: str = None) -> str:
    """
    Export ship data to CSV file.

    Args:
        ships: List of Agent objects
        metrics: Simulation metrics dictionary
        filename: Optional filename (auto-generated if None)

    Returns:
        Path to created CSV file
    """
    # Create results directory if it doesn't exist
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ship_simulation_{timestamp}.csv"

    filepath = results_dir / filename

    # Write CSV
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'ship_id',
            'automation_level',
            'base_speed_kmh',
            'ris_connected',
            'origin',
            'destination',
            'distance_km',
            'travel_time_hours',
            'waiting_time_hours',
            'total_time_hours',
            'state',
            'route'
        ])

        # Ship data
        for ship in ships:
            total_time = ship.journey_time + ship.waiting_time
            writer.writerow([
                ship.agent_id,
                ship.automation_level,
                f"{ship.speed:.2f}",
                ship.ris_connected,
                ship.origin,
                ship.destination,
                f"{ship.journey_distance:.2f}",
                f"{ship.journey_time:.2f}",
                f"{ship.waiting_time:.2f}",
                f"{total_time:.2f}",
                ship.state.value,
                ' -> '.join(ship.route)
            ])

    return str(filepath)


def export_timeseries_to_csv(history: List[dict], filename: str = None) -> str:
    """
    Export simulation time series data to CSV file.

    Args:
        history: List of step snapshots with ship states
        filename: Optional filename (auto-generated if None)

    Returns:
        Path to created CSV file
    """
    # Create results directory if it doesn't exist
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ship_timeseries_{timestamp}.csv"

    filepath = results_dir / filename

    # Write CSV
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'step',
            'ship_id',
            'automation_level',
            'base_speed_kmh',
            'effective_speed_kmh',
            'ris_connected',
            'current_node',
            'destination',
            'state',
            'distance_traveled_km',
            'time_elapsed_hours',
            'waiting_time_hours',
            'next_node'
        ])

        # Time series data
        for step_data in history:
            step = step_data['step']
            for ship_state in step_data['ships']:
                writer.writerow([
                    step,
                    ship_state['ship_id'],
                    ship_state['automation_level'],
                    f"{ship_state['base_speed']:.2f}",
                    f"{ship_state['effective_speed']:.2f}",
                    ship_state['ris_connected'],
                    ship_state['current_node'],
                    ship_state['destination'],
                    ship_state['state'],
                    f"{ship_state['distance_traveled']:.2f}",
                    f"{ship_state['time_elapsed']:.2f}",
                    f"{ship_state['waiting_time']:.2f}",
                    ship_state['next_node'] or ''
                ])

    return str(filepath)


def run_simulation(
    num_ships: int = 10,
    max_steps: int = 100,
    seed: int = None
) -> Tuple[List[Agent], dict, List[dict]]:
    """
    Run the complete simulation with realistic traffic behavior.

    Args:
        num_ships: Number of ships to simulate
        max_steps: Maximum simulation steps
        seed: Random seed for reproducibility

    Returns:
        Tuple of (agents list, metrics dict, history list)
    """
    if seed is not None:
        random.seed(seed)

    # Create network
    network = create_rhine_network()
    port_ids = list(network.nodes.keys())

    # Create ships
    ships = create_random_ships(num_ships, port_ids, network)

    # Initialize traffic manager
    traffic_mgr = TrafficManager(network)

    # Simulation metrics
    total_system_time = 0.0  # Total time all ships spend in system
    total_travel_time = 0.0  # Actual travel time
    total_waiting_time = 0.0  # Total waiting time

    # Track when ships enter/exit
    ship_exit_step = {}

    # Track history for time series export
    history = []

    # Track effective speeds for each ship at each step
    ship_effective_speeds = {}

    # Run simulation
    step = 0
    active_ships = set(ship.agent_id for ship in ships)

    while step < max_steps and active_ships:
        step += 1

        # Move all active ships
        for ship in ships:
            if ship.agent_id not in active_ships:
                continue

            # Move ship if traveling
            if ship.state == AgentState.TRAVELING and ship.next_node:
                current = ship.current_node
                next_node = ship.next_node

                # Check crossroad entry (if arriving at next node)
                can_enter, wait_time = traffic_mgr.check_crossroad_entry(ship.agent_id, next_node)

                if not can_enter:
                    # Must wait at crossroad
                    ship.waiting_time += wait_time
                    traffic_mgr.update_time(ship.journey_time + ship.waiting_time)
                    ship_effective_speeds[ship.agent_id] = 0.0
                    continue

                # Get edge distance
                try:
                    path, distance = network.get_shortest_path(current, next_node)
                    if len(path) == 2:
                        edge_distance = distance
                    else:
                        edge_distance = 10.0
                except:
                    edge_distance = 10.0

                # Register vessel entering edge
                traffic_mgr.vessel_enter_edge(ship.agent_id, current, next_node)

                # Calculate effective speed based on congestion
                effective_speed = traffic_mgr.get_effective_speed(
                    ship.agent_id, ship.speed, current, next_node
                )
                ship_effective_speeds[ship.agent_id] = effective_speed

                # Calculate travel time using effective speed
                travel_time = edge_distance / effective_speed

                # Move agent
                ship.advance_to_next_node(
                    distance=edge_distance,
                    time=travel_time
                )

                # Register vessel exiting previous edge
                traffic_mgr.vessel_exit_edge(ship.agent_id, current, next_node)

                # Occupy crossroad if arriving at one
                if next_node in traffic_mgr.crossroads:
                    traffic_mgr.occupy_crossroad(ship.agent_id, next_node)

                # Release previous crossroad if leaving one
                if current in traffic_mgr.crossroads:
                    traffic_mgr.release_crossroad(ship.agent_id, current)

            # Check if ship reached destination
            if ship.is_at_destination and ship.agent_id in active_ships:
                ship_exit_step[ship.agent_id] = step
                active_ships.remove(ship.agent_id)

                # Release crossroad if at one
                if ship.current_node in traffic_mgr.crossroads:
                    traffic_mgr.release_crossroad(ship.agent_id, ship.current_node)

        # Update traffic manager time
        if ships:
            avg_time = sum(s.journey_time + s.waiting_time for s in ships) / len(ships)
            traffic_mgr.update_time(avg_time)

        # Capture state after all movements for this step
        step_snapshot = {
            'step': step,
            'ships': []
        }

        for ship in ships:
            eff_speed = ship_effective_speeds.get(ship.agent_id, ship.speed)
            step_snapshot['ships'].append({
                'ship_id': ship.agent_id,
                'automation_level': ship.automation_level,
                'base_speed': ship.speed,
                'effective_speed': eff_speed,
                'ris_connected': ship.ris_connected,
                'current_node': ship.current_node,
                'destination': ship.destination,
                'state': ship.state.value,
                'distance_traveled': ship.journey_distance,
                'time_elapsed': ship.journey_time,
                'waiting_time': ship.waiting_time,
                'next_node': ship.next_node
            })

        # Save step snapshot to history
        history.append(step_snapshot)

    # Calculate metrics
    for ship in ships:
        total_travel_time += ship.journey_time
        total_waiting_time += ship.waiting_time

        # System time = travel time + waiting time
        if ship.agent_id in ship_exit_step:
            total_system_time += (ship.journey_time + ship.waiting_time)

    metrics = {
        'num_ships': num_ships,
        'completed_journeys': len(ship_exit_step),
        'total_system_time': total_system_time,
        'total_travel_time': total_travel_time,
        'total_waiting_time': total_waiting_time,
        'avg_system_time': total_system_time / len(ship_exit_step) if ship_exit_step else 0,
        'avg_travel_time': total_travel_time / len(ship_exit_step) if ship_exit_step else 0,
        'avg_waiting_time': total_waiting_time / len(ship_exit_step) if ship_exit_step else 0,
        'simulation_steps': step,
    }

    return ships, metrics, history


def main(
    num_ships: int = 10,
    seed: int = None,
    interactive: bool = True
):
    """
    Run simulation with parameters.

    Args:
        num_ships: Number of ships to simulate
        seed: Random seed for reproducibility
        interactive: Whether to prompt for user input
    """
    print("=" * 80)
    print("AUTONOMOUS SHIPPING SIMULATION - WITH TRAFFIC BEHAVIOR")
    print("=" * 80)
    print()

    # Get user input if interactive
    if interactive:
        print("SIMULATION PARAMETERS")
        print("-" * 80)

        try:
            num_ships = int(input("Number of ships to simulate [default: 10]: ") or "10")
        except (ValueError, EOFError):
            num_ships = 10

        try:
            seed_input = input("\nRandom seed (for reproducibility) [default: random]: ")
            seed = int(seed_input) if seed_input else None
        except (ValueError, EOFError):
            seed = None

        print()

    # Display parameters
    print("=" * 80)
    print("CONFIGURATION")
    print("=" * 80)
    print(f"Ships: {num_ships}")
    print(f"Random seed: {seed if seed is not None else 'random'}")
    print()

    print("=" * 80)
    print("RUNNING SIMULATION")
    print("=" * 80)
    print()

    # Run simulation
    ships, metrics, history = run_simulation(
        num_ships=num_ships,
        max_steps=200,
        seed=seed
    )

    # Display results
    print("=" * 80)
    print("SHIP CONFIGURATION")
    print("=" * 80)
    print()

    # Group by automation level
    by_automation = {}
    for ship in ships:
        level = ship.automation_level
        by_automation[level] = by_automation.get(level, 0) + 1

    for level in sorted(by_automation.keys()):
        print(f"  Level {level}: {by_automation[level]} ships")

    print()

    # Display performance metrics
    print("=" * 80)
    print("PERFORMANCE METRICS")
    print("=" * 80)
    print()

    print(f"Ships simulated: {metrics['num_ships']}")
    print(f"Completed journeys: {metrics['completed_journeys']}")
    print(f"Simulation steps: {metrics['simulation_steps']}")
    print()

    print(f"Total travel time: {metrics['total_travel_time']:.2f} hours")
    print(f"Total waiting time: {metrics['total_waiting_time']:.2f} hours")
    print(f"Total system time: {metrics['total_system_time']:.2f} hours")
    print()

    if metrics['completed_journeys'] > 0:
        print(f"Average travel time per ship: {metrics['avg_travel_time']:.2f} hours")
        print(f"Average waiting time per ship: {metrics['avg_waiting_time']:.2f} hours")
        print(f"Average system time per ship: {metrics['avg_system_time']:.2f} hours")

    print()

    # Sample ship details
    print("=" * 80)
    print("SAMPLE SHIP DETAILS (first 5)")
    print("=" * 80)
    print()

    for ship in ships[:5]:
        total_time = ship.journey_time + ship.waiting_time
        print(f"{ship.agent_id}:")
        print(f"  Route: {ship.origin} -> {ship.destination}")
        print(f"  Automation Level: L{ship.automation_level}")
        print(f"  Distance: {ship.journey_distance:.0f} km")
        print(f"  Travel time: {ship.journey_time:.2f} hours")
        print(f"  Waiting time: {ship.waiting_time:.2f} hours")
        print(f"  Total time: {total_time:.2f} hours")
        print(f"  State: {ship.state.value}")
        print()

    # Export to CSV
    print("=" * 80)
    print("EXPORTING RESULTS")
    print("=" * 80)
    print()

    csv_path = export_ships_to_csv(ships, metrics)
    print(f"Ship summary exported to: {csv_path}")

    timeseries_path = export_timeseries_to_csv(history)
    print(f"Time series data exported to: {timeseries_path}")
    print()

    print("=" * 80)
    print("SIMULATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    import argparse

    # Check if running in IPython/Jupyter
    try:
        get_ipython()  # type: ignore # This function only exists in IPython/Jupyter
        in_ipython = True
    except NameError:
        in_ipython = False

    if in_ipython:
        # Running in IPython/Jupyter - use default interactive mode
        # Users can call main() directly with parameters if needed
        print("Running in interactive environment (Jupyter/IPython)")
        print("You can run with parameters by calling main() directly:")
        print("  main(num_ships=20, seed=42, interactive=False)")
        print()
        main()
    else:
        # Running as script - use argparse
        parser = argparse.ArgumentParser(description='Autonomous Shipping Simulation (No Disruptions)')
        parser.add_argument('--ships', type=int, default=10, help='Number of ships (default: 10)')
        parser.add_argument('--seed', type=int, default=None,
                           help='Random seed for reproducibility')
        parser.add_argument('--non-interactive', action='store_true',
                           help='Run without user prompts')

        args = parser.parse_args()

        main(
            num_ships=args.ships,
            seed=args.seed,
            interactive=not args.non_interactive
        )
