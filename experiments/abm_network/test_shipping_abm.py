"""
Tests for Rhine Shipping ABM

Tests cover:
1. Model initialization
2. Vessel agent creation and behavior
3. Automation adoption
4. Collision risk calculation
5. Data collection
"""

import matplotlib
matplotlib.use('Agg')

import pytest
import numpy as np

from src.models.shipping_abm import RhineShippingModel, create_shipping_model
from src.agents.vessel_agent import VesselAgent, create_vessel_characteristics


# --------- Model Initialization Tests --------- #

def test_model_initialization():
    """Test basic model initialization."""
    model = RhineShippingModel(num_vessels=10, seed=42)

    assert model is not None
    assert model.num_vessels == 10
    assert len(model.vessel_list) == 10
    assert model.network is not None


def test_model_with_different_vessel_counts():
    """Test model creation with different vessel counts."""
    for num_vessels in [5, 20, 50]:
        model = RhineShippingModel(num_vessels=num_vessels, seed=42)
        assert len(model.vessel_list) == num_vessels


def test_factory_function():
    """Test factory function creates model."""
    model = create_shipping_model(num_vessels=10, scenario="baseline", seed=42)

    assert isinstance(model, RhineShippingModel)
    assert len(model.vessel_list) == 10


def test_factory_with_scenarios():
    """Test factory with different scenarios."""
    for scenario in ["baseline", "optimistic", "pessimistic"]:
        model = create_shipping_model(num_vessels=10, scenario=scenario, seed=42)
        assert model is not None


# --------- Vessel Agent Tests --------- #

def test_vessel_characteristics():
    """Test vessel characteristics creation."""
    for vessel_type in ["cargo", "tanker", "container", "passenger"]:
        char = create_vessel_characteristics(vessel_type)
        assert char.vessel_type == vessel_type
        assert char.length > 0
        assert char.max_speed > 0


def test_vessel_agent_creation():
    """Test vessel agent initialization."""
    model = RhineShippingModel(num_vessels=5, seed=42)
    vessel = model.vessel_list[0]

    assert isinstance(vessel, VesselAgent)
    assert vessel.automation_level >= 0
    assert vessel.automation_level <= 5
    assert vessel.origin in model.network.ports
    assert vessel.destination in model.network.ports


def test_vessel_route_planning():
    """Test that vessels plan routes."""
    model = RhineShippingModel(num_vessels=5, seed=42)

    for vessel in model.vessel_list:
        assert len(vessel.route) > 0
        assert vessel.route[0] == vessel.origin


def test_vessel_automation_adoption():
    """Test vessel automation level upgrade."""
    model = RhineShippingModel(num_vessels=5, seed=42)
    vessel = model.vessel_list[0]

    initial_level = vessel.automation_level
    vessel.adopt_automation_level(min(initial_level + 1, 5))

    if initial_level < 5:
        assert vessel.automation_level > initial_level


# --------- Model Step Tests --------- #

def test_model_step():
    """Test model can execute a step."""
    model = RhineShippingModel(num_vessels=10, seed=42)
    initial_steps = model.steps

    model.step()

    assert model.steps == initial_steps + 1


def test_model_run():
    """Test model can run multiple steps."""
    model = RhineShippingModel(num_vessels=10, seed=42)

    model.run_model(5)

    assert model.steps == 5


def test_vessels_move():
    """Test that vessels move over time."""
    model = RhineShippingModel(num_vessels=10, seed=42)

    # Record initial positions
    initial_positions = {v.unique_id: v.route_position for v in model.vessel_list}

    # Run simulation for longer to allow loading/unloading cycles
    model.run_model(200)

    # Check that at least some vessels moved
    moved_count = sum(1 for v in model.vessel_list
                     if v.route_position != initial_positions[v.unique_id])

    assert moved_count > 0


# --------- Data Collection Tests --------- #

def test_data_collection():
    """Test that data is collected."""
    model = RhineShippingModel(num_vessels=10, seed=42)

    model.run_model(5)

    model_data = model.datacollector.get_model_vars_dataframe()
    assert len(model_data) == 6  # Initial + 5 steps


def test_model_reporters():
    """Test model-level data reporters."""
    model = RhineShippingModel(num_vessels=10, seed=42)

    model.run_model(3)

    model_data = model.datacollector.get_model_vars_dataframe()

    required_columns = [
        "Total_Vessels", "Sailing_Vessels", "Total_Incidents",
        "L0_Vessels", "L1_Vessels"
    ]

    for col in required_columns:
        assert col in model_data.columns


def test_agent_reporters():
    """Test agent-level data reporters."""
    model = RhineShippingModel(num_vessels=10, seed=42)

    model.run_model(3)

    agent_data = model.datacollector.get_agent_vars_dataframe()
    assert len(agent_data) > 0


# --------- Collision Risk Tests --------- #

def test_collision_risk_calculation():
    """Test collision risk is calculated."""
    model = RhineShippingModel(num_vessels=20, seed=42)

    model.run_model(20)

    # Check that some vessels have non-zero risk
    risks = [v.collision_risk for v in model.vessel_list if v.state == "sailing"]

    if risks:  # If any vessels are sailing
        assert any(r > 0 for r in risks)


def test_incident_tracking():
    """Test incidents are tracked."""
    model = RhineShippingModel(num_vessels=50, seed=42)

    model.run_model(100)

    # Model should track total incidents
    assert hasattr(model, 'total_incidents')
    assert hasattr(model, 'total_near_misses')
    assert model.total_incidents >= 0
    assert model.total_near_misses >= 0


# --------- Automation Diffusion Tests --------- #

def test_automation_tracking():
    """Test automation levels are tracked."""
    model = RhineShippingModel(num_vessels=20, seed=42)

    dist = model.get_automation_distribution()

    assert len(dist) == 6  # L0-L5
    assert sum(dist.values()) == 20


def test_automation_adoption_over_time():
    """Test automation adoption increases over time."""
    model = RhineShippingModel(num_vessels=50, seed=42)

    initial_dist = model.get_automation_distribution()
    initial_advanced = sum(initial_dist.get(i, 0) for i in range(3, 6))

    model.run_model(100)

    final_dist = model.get_automation_distribution()
    final_advanced = sum(final_dist.get(i, 0) for i in range(3, 6))

    # More vessels should have advanced automation
    assert final_advanced >= initial_advanced


# --------- Network Integration Tests --------- #

def test_model_uses_network():
    """Test model integrates with Rhine network."""
    model = RhineShippingModel(num_vessels=10, seed=42)

    assert model.network is not None
    assert len(model.network.ports) > 0


def test_vessels_at_port():
    """Test querying vessels at specific port."""
    model = RhineShippingModel(num_vessels=20, seed=42)

    # Get vessels at major port
    vessels = model.get_vessels_at_port("Rotterdam")
    assert isinstance(vessels, list)


def test_sailing_vessels_query():
    """Test querying sailing vessels."""
    model = RhineShippingModel(num_vessels=20, seed=42)

    model.run_model(10)

    sailing = model.get_sailing_vessels()
    assert isinstance(sailing, list)


# --------- Summary Statistics Tests --------- #

def test_summary_statistics():
    """Test summary statistics generation."""
    model = RhineShippingModel(num_vessels=20, seed=42)

    model.run_model(10)

    stats = model.get_summary_statistics()

    assert "total_steps" in stats
    assert "total_vessels" in stats
    assert "total_incidents" in stats
    assert "vessels_by_automation" in stats


def test_statistics_consistency():
    """Test statistics are consistent."""
    model = RhineShippingModel(num_vessels=20, seed=42)

    model.run_model(10)

    stats = model.get_summary_statistics()

    # Total vessels should match
    assert stats["total_vessels"] == 20

    # Count vessels by all states (sailing, moored, loading, unloading)
    state_counts = {}
    for v in model.vessel_list:
        state_counts[v.state] = state_counts.get(v.state, 0) + 1

    # All vessels should be in some state
    assert sum(state_counts.values()) == 20


# --------- Edge Cases --------- #

def test_single_vessel():
    """Test model with single vessel."""
    model = RhineShippingModel(num_vessels=1, seed=42)

    model.run_model(5)

    assert len(model.vessel_list) == 1


def test_same_origin_destination():
    """Test vessel with same origin and destination."""
    model = RhineShippingModel(num_vessels=5, seed=42)

    # Manually set a vessel's destination to its origin
    vessel = model.vessel_list[0]
    vessel.destination = vessel.origin
    vessel._plan_route()

    assert len(vessel.route) == 1


def test_reproducibility_with_seed():
    """Test that same seed produces same results."""
    model1 = RhineShippingModel(num_vessels=10, seed=42)
    model1.run_model(10)
    stats1 = model1.get_summary_statistics()

    model2 = RhineShippingModel(num_vessels=10, seed=42)
    model2.run_model(10)
    stats2 = model2.get_summary_statistics()

    # Should have same number of incidents
    assert stats1["total_incidents"] == stats2["total_incidents"]
