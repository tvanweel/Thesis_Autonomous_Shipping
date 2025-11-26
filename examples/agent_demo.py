"""
Agent Demo - Network-Based ABM

Demonstrates agents navigating through a network, planning routes,
and tracking their journeys.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.network import Network, Node, Edge
from src.models.agent import Agent, AgentState, create_agent, reset_agent_id_counter


def main():
    print("=" * 70)
    print("AGENT-BASED MODEL DEMONSTRATION")
    print("=" * 70)
    print()

    # Create a network
    print("Creating network...")
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
        print(f"  Added: {port.name}")

    # Add edges (shipping routes)
    routes = [
        Edge("Rotterdam", "Dordrecht", weight=24.0, properties={"distance_km": 24}),
        Edge("Dordrecht", "Nijmegen", weight=95.0, properties={"distance_km": 95}),
        Edge("Nijmegen", "Duisburg", weight=111.0, properties={"distance_km": 111}),
        Edge("Duisburg", "Cologne", weight=60.0, properties={"distance_km": 60}),
        Edge("Cologne", "Mannheim", weight=143.0, properties={"distance_km": 143}),
        # Alternative route
        Edge("Rotterdam", "Nijmegen", weight=130.0, properties={"distance_km": 130}),
    ]

    for route in routes:
        network.add_edge(route)

    print()
    print(f"Network created: {network}")
    print()

    # Create agents (vessels)
    print("=" * 70)
    print("CREATING AGENTS")
    print("=" * 70)
    print()

    reset_agent_id_counter()

    agents = [
        create_agent(
            "vessel",
            "Rotterdam",
            "Rotterdam",
            capacity=2500,
            cargo_type="container"
        ),
        create_agent(
            "vessel",
            "Dordrecht",
            "Dordrecht",
            capacity=3000,
            cargo_type="bulk"
        ),
        create_agent(
            "vessel",
            "Rotterdam",
            "Rotterdam",
            capacity=2000,
            cargo_type="tanker"
        ),
    ]

    for agent in agents:
        print(f"Created: {agent}")
        print(f"  Capacity: {agent.get_property('capacity')} tonnes")
        print(f"  Cargo type: {agent.get_property('cargo_type')}")
        print()

    # Set destinations and plan routes
    print("=" * 70)
    print("PLANNING ROUTES")
    print("=" * 70)
    print()

    destinations = ["Mannheim", "Duisburg", "Cologne"]

    for agent, dest in zip(agents, destinations):
        agent.set_destination(dest, network)
        path, distance = network.get_shortest_path(agent.origin, dest)

        print(f"{agent.agent_id}: {agent.origin} -> {dest}")
        print(f"  Route: {' -> '.join(path)}")
        print(f"  Total distance: {distance:.0f} km")
        print(f"  State: {agent.state.value}")
        print()

    # Simulate agent movement
    print("=" * 70)
    print("SIMULATING AGENT MOVEMENT")
    print("=" * 70)
    print()

    print("Starting simulation...")
    print()

    max_steps = 20
    step = 0

    while step < max_steps:
        # Check if all agents have reached destination
        all_arrived = all(agent.is_at_destination for agent in agents)
        if all_arrived:
            print("All agents have reached their destinations!")
            break

        step += 1
        print(f"Step {step}:")
        print("-" * 70)

        for agent in agents:
            if agent.is_at_destination:
                print(f"  {agent.agent_id}: AT DESTINATION ({agent.current_node})")
                continue

            if agent.state == AgentState.TRAVELING and agent.next_node:
                # Get edge distance
                next_node = agent.next_node
                current = agent.current_node

                # Find edge weight
                try:
                    # Get distance from network
                    path, distance = network.get_shortest_path(current, next_node)
                    if len(path) == 2:  # Direct edge
                        edge_distance = distance
                    else:
                        edge_distance = 10.0  # Default
                except:
                    edge_distance = 10.0

                # Calculate travel time (assume 14 km/h average speed)
                travel_time = edge_distance / 14.0

                # Move agent
                agent.advance_to_next_node(
                    distance=edge_distance,
                    time=travel_time
                )

                print(f"  {agent.agent_id}: {current} -> {agent.current_node} "
                      f"(+{edge_distance:.0f} km, +{travel_time:.2f} h)")

        print()

    # Final statistics
    print("=" * 70)
    print("JOURNEY STATISTICS")
    print("=" * 70)
    print()

    for agent in agents:
        print(f"{agent.agent_id}:")
        print(f"  Origin: {agent.origin}")
        print(f"  Destination: {agent.destination}")
        print(f"  Current location: {agent.current_node}")
        print(f"  Total distance: {agent.journey_distance:.0f} km")
        print(f"  Total time: {agent.journey_time:.2f} hours")
        print(f"  State: {agent.state.value}")

        if agent.is_at_destination:
            avg_speed = agent.journey_distance / agent.journey_time if agent.journey_time > 0 else 0
            print(f"  Average speed: {avg_speed:.1f} km/h")

        print()

    # Demonstrate agent serialization
    print("=" * 70)
    print("SERIALIZATION")
    print("=" * 70)
    print()

    print("Exporting first agent to dictionary...")
    agent_dict = agents[0].to_dict()
    print(f"Agent data: {len(agent_dict)} fields exported")
    print()

    print("Recreating agent from dictionary...")
    reconstructed = Agent.from_dict(agent_dict)
    print(f"Reconstructed: {reconstructed}")
    print(f"  Position matches: {reconstructed.current_node == agents[0].current_node}")
    print(f"  Distance matches: {reconstructed.journey_distance == agents[0].journey_distance}")
    print()

    # Demonstrate stop/resume
    print("=" * 70)
    print("STOP/RESUME FUNCTIONALITY")
    print("=" * 70)
    print()

    test_agent = create_agent("vessel", "Rotterdam", "Rotterdam")
    test_agent.set_destination("Cologne", network)

    print(f"Agent: {test_agent.agent_id}")
    print(f"  Initial state: {test_agent.state.value}")
    print()

    print("Stopping agent...")
    test_agent.stop()
    print(f"  State after stop: {test_agent.state.value}")
    print()

    print("Resuming agent...")
    test_agent.resume()
    print(f"  State after resume: {test_agent.state.value}")
    print()

    # Reset journey
    print("Resetting journey...")
    test_agent.reset_journey()
    print(f"  Current node: {test_agent.current_node}")
    print(f"  Distance: {test_agent.journey_distance} km")
    print(f"  State: {test_agent.state.value}")
    print()

    print("=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
