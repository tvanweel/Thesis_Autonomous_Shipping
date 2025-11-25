"""
Rhine Shipping ABM Demonstration

Runs the agent-based model simulation and creates comprehensive visualizations
of vessel movements, automation adoption, and collision risks.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.models.shipping_abm import create_shipping_model

# Create output directory
RESULTS_DIR = Path(__file__).parent.parent / "results" / "abm_simulation"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("Rhine Shipping Agent-Based Model Simulation")
print("=" * 80)
print()

# Model parameters
NUM_VESSELS = 100
SIMULATION_STEPS = 200
SCENARIO = "baseline"
SEED = 42

print(f"Configuration:")
print(f"  Number of Vessels: {NUM_VESSELS}")
print(f"  Simulation Steps: {SIMULATION_STEPS}")
print(f"  Scenario: {SCENARIO}")
print(f"  Random Seed: {SEED}")
print()

# Create and run model
print("Initializing model...")
model = create_shipping_model(
    num_vessels=NUM_VESSELS,
    scenario=SCENARIO,
    seed=SEED
)
print(f"  Model created with {len(model.vessel_list)} vessels")
print(f"  Network: {len(model.network.ports)} ports, {len(model.network.segments)} segments")
print()

# Print initial state
print("Initial Vessel Distribution:")
initial_dist = model.get_automation_distribution()
for level, count in sorted(initial_dist.items()):
    print(f"  Level {level}: {count} vessels ({count/NUM_VESSELS*100:.1f}%)")
print()

# Run simulation
print(f"Running simulation for {SIMULATION_STEPS} steps...")
model.run_model(SIMULATION_STEPS)
print("  Simulation complete!")
print()

# Get results
print("Collecting results...")
model_data = model.datacollector.get_model_vars_dataframe()
agent_data = model.datacollector.get_agent_vars_dataframe()
print(f"  Collected {len(model_data)} model observations")
print(f"  Collected {len(agent_data)} agent observations")
print()

# Summary statistics
print("Simulation Summary:")
print("-" * 80)
stats = model.get_summary_statistics()
for key, value in stats.items():
    if isinstance(value, dict):
        print(f"  {key}:")
        for k, v in value.items():
            print(f"    L{k}: {v}")
    elif isinstance(value, float):
        print(f"  {key}: {value:.2f}")
    else:
        print(f"  {key}: {value}")
print()

# Generate visualizations
print("Generating Visualizations:")
print("-" * 80)

# 1. Automation adoption over time
print("1. Creating automation adoption timeline...")
fig1, ax1 = plt.subplots(figsize=(12, 6))

for level in range(6):
    col_name = f"L{level}_Vessels"
    if col_name in model_data.columns:
        ax1.plot(model_data.index, model_data[col_name],
                label=f"Level {level}", linewidth=2.5)

ax1.set_xlabel("Simulation Step", fontsize=12)
ax1.set_ylabel("Number of Vessels", fontsize=12)
ax1.set_title("Automation Technology Adoption Over Time", fontsize=14, fontweight="bold")
ax1.legend(loc="best", fontsize=10)
ax1.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(RESULTS_DIR / "automation_adoption_timeline.png", dpi=300)
plt.close()
print(f"   Saved to: automation_adoption_timeline.png")

# 2. Collision risk over time
print("2. Creating collision risk analysis...")
fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(14, 5))

# Risk over time
ax2a.plot(model_data.index, model_data["Avg_Collision_Risk"],
         color='#E63946', linewidth=2.5)
ax2a.fill_between(model_data.index, 0, model_data["Avg_Collision_Risk"],
                 alpha=0.3, color='#E63946')
ax2a.set_xlabel("Simulation Step", fontsize=11)
ax2a.set_ylabel("Average Collision Risk", fontsize=11)
ax2a.set_title("Average Collision Risk Over Time", fontsize=12, fontweight="bold")
ax2a.grid(True, alpha=0.3)

# Incidents over time
ax2b.plot(model_data.index, model_data["Total_Incidents"],
         color='#E63946', linewidth=2.5, label="Incidents")
ax2b.plot(model_data.index, model_data["Total_Near_Misses"],
         color='#F77F00', linewidth=2.5, label="Near Misses")
ax2b.set_xlabel("Simulation Step", fontsize=11)
ax2b.set_ylabel("Cumulative Count", fontsize=11)
ax2b.set_title("Incidents and Near Misses", fontsize=12, fontweight="bold")
ax2b.legend(loc="best", fontsize=10)
ax2b.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(RESULTS_DIR / "collision_risk_analysis.png", dpi=300)
plt.close()
print(f"   Saved to: collision_risk_analysis.png")

# 3. Vessel activity over time
print("3. Creating vessel activity visualization...")
fig3, ax3 = plt.subplots(figsize=(12, 6))

ax3.plot(model_data.index, model_data["Sailing_Vessels"],
        label="Sailing", color='#06AED5', linewidth=2.5)
ax3.plot(model_data.index, model_data["Total_Vessels"] - model_data["Sailing_Vessels"],
        label="Moored/Loading", color='#004E89', linewidth=2.5)

ax3.set_xlabel("Simulation Step", fontsize=12)
ax3.set_ylabel("Number of Vessels", fontsize=12)
ax3.set_title("Vessel Activity Over Time", fontsize=14, fontweight="bold")
ax3.legend(loc="best", fontsize=11)
ax3.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(RESULTS_DIR / "vessel_activity.png", dpi=300)
plt.close()
print(f"   Saved to: vessel_activity.png")

# 4. Distance traveled analysis
print("4. Creating distance traveled analysis...")
fig4, ax4 = plt.subplots(figsize=(12, 6))

ax4.plot(model_data.index, model_data["Total_Distance_Traveled"],
        color='#2ECC71', linewidth=2.5)
ax4.fill_between(model_data.index, 0, model_data["Total_Distance_Traveled"],
                alpha=0.3, color='#2ECC71')

ax4.set_xlabel("Simulation Step", fontsize=12)
ax4.set_ylabel("Total Distance (km)", fontsize=12)
ax4.set_title("Cumulative Distance Traveled by Fleet", fontsize=14, fontweight="bold")
ax4.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(RESULTS_DIR / "distance_traveled.png", dpi=300)
plt.close()
print(f"   Saved to: distance_traveled.png")

# 5. Comprehensive dashboard
print("5. Creating comprehensive dashboard...")
fig5 = plt.figure(figsize=(16, 12))
gs = fig5.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

# Top left: Automation levels
ax5a = fig5.add_subplot(gs[0, 0])
for level in range(6):
    col_name = f"L{level}_Vessels"
    if col_name in model_data.columns:
        ax5a.plot(model_data.index, model_data[col_name], label=f"L{level}", linewidth=2)
ax5a.set_xlabel("Step", fontsize=10)
ax5a.set_ylabel("Vessels", fontsize=10)
ax5a.set_title("Automation Adoption", fontsize=11, fontweight="bold")
ax5a.legend(fontsize=8, ncol=2)
ax5a.grid(True, alpha=0.3)

# Top right: Risk and incidents
ax5b = fig5.add_subplot(gs[0, 1])
ax5b_twin = ax5b.twinx()
ax5b.plot(model_data.index, model_data["Avg_Collision_Risk"],
         color='#E63946', linewidth=2, label="Avg Risk")
ax5b_twin.plot(model_data.index, model_data["Total_Incidents"],
              color='#004E89', linewidth=2, linestyle='--', label="Incidents")
ax5b.set_xlabel("Step", fontsize=10)
ax5b.set_ylabel("Collision Risk", fontsize=10, color='#E63946')
ax5b_twin.set_ylabel("Incidents", fontsize=10, color='#004E89')
ax5b.set_title("Risk vs Incidents", fontsize=11, fontweight="bold")
ax5b.tick_params(axis='y', labelcolor='#E63946')
ax5b_twin.tick_params(axis='y', labelcolor='#004E89')
ax5b.grid(True, alpha=0.3)

# Middle left: Vessel states
ax5c = fig5.add_subplot(gs[1, 0])
ax5c.plot(model_data.index, model_data["Sailing_Vessels"],
         label="Sailing", color='#06AED5', linewidth=2)
ax5c.plot(model_data.index, NUM_VESSELS - model_data["Sailing_Vessels"],
         label="At Port", color='#004E89', linewidth=2)
ax5c.set_xlabel("Step", fontsize=10)
ax5c.set_ylabel("Vessels", fontsize=10)
ax5c.set_title("Vessel States", fontsize=11, fontweight="bold")
ax5c.legend(fontsize=9)
ax5c.grid(True, alpha=0.3)

# Middle right: Distance
ax5d = fig5.add_subplot(gs[1, 1])
ax5d.plot(model_data.index, model_data["Total_Distance_Traveled"],
         color='#2ECC71', linewidth=2)
ax5d.fill_between(model_data.index, 0, model_data["Total_Distance_Traveled"],
                 alpha=0.3, color='#2ECC71')
ax5d.set_xlabel("Step", fontsize=10)
ax5d.set_ylabel("Distance (km)", fontsize=10)
ax5d.set_title("Total Distance Traveled", fontsize=11, fontweight="bold")
ax5d.grid(True, alpha=0.3)

# Bottom: Final distribution comparison
ax5e = fig5.add_subplot(gs[2, :])
final_dist = model.get_automation_distribution()
initial_dist_list = [initial_dist[i] for i in range(6)]
final_dist_list = [final_dist[i] for i in range(6)]

x = np.arange(6)
width = 0.35
ax5e.bar(x - width/2, initial_dist_list, width, label='Initial', alpha=0.8, color='#004E89')
ax5e.bar(x + width/2, final_dist_list, width, label='Final', alpha=0.8, color='#2ECC71')
ax5e.set_xlabel("Automation Level", fontsize=10)
ax5e.set_ylabel("Number of Vessels", fontsize=10)
ax5e.set_title("Automation Distribution: Initial vs Final", fontsize=11, fontweight="bold")
ax5e.set_xticks(x)
ax5e.set_xticklabels([f"L{i}" for i in range(6)])
ax5e.legend(fontsize=9)
ax5e.grid(True, alpha=0.3, axis='y')

fig5.suptitle(f"Rhine Shipping ABM Dashboard ({SCENARIO.capitalize()} Scenario)",
             fontsize=16, fontweight="bold", y=0.995)
plt.savefig(RESULTS_DIR / "abm_dashboard.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"   Saved to: abm_dashboard.png")

print()

# Export data to CSV
print("Exporting data...")
model_data.to_csv(RESULTS_DIR / "model_data.csv")
agent_data.to_csv(RESULTS_DIR / "agent_data.csv")
print(f"  Model data: model_data.csv")
print(f"  Agent data: agent_data.csv")
print()

# Vessel statistics
print("Top 5 Vessels by Distance Traveled:")
print("-" * 80)
vessel_distances = {}
for agent in model.vessel_list:
    vessel_distances[agent.unique_id] = {
        'distance': agent.distance_traveled,
        'automation_level': agent.automation_level,
        'incidents': agent.incident_count,
        'near_misses': agent.near_misses,
    }

sorted_vessels = sorted(vessel_distances.items(),
                       key=lambda x: x[1]['distance'], reverse=True)[:5]

for vessel_id, data in sorted_vessels:
    print(f"  Vessel {vessel_id}:")
    print(f"    Distance: {data['distance']:.1f} km")
    print(f"    Automation: Level {data['automation_level']}")
    print(f"    Incidents: {data['incidents']}, Near Misses: {data['near_misses']}")

print()
print("=" * 80)
print("Simulation Complete!")
print(f"All results saved to: {RESULTS_DIR.absolute()}")
print("=" * 80)
