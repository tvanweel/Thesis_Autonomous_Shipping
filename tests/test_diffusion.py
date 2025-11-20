import numpy as np
import pytest

from src.models.diffusion import BassDiffusionModel, MultiLevelAutomationDiffusion


# --------- BassDiffusionModel tests --------- #

def test_bass_total_never_exceeds_market_potential():
    """Bass model should never exceed market potential M."""
    M = 1000.0
    model = BassDiffusionModel(
        market_potential=M,
        p=0.03,
        q=0.38,
        dt=1.0,
        initial_adopters=100.0,
    )

    model.run(steps=300)

    N = np.array(model.history_N)
    # Total adopters never exceed market potential
    assert np.all(N <= M + 1e-9)
    # And for long runs we essentially saturate the market
    assert N[-1] == pytest.approx(M, rel=1e-6)


def test_bass_growth_is_non_negative_and_non_decreasing():
    """Bass model growth should be non-negative and cumulative adoption non-decreasing."""
    M = 500.0
    model = BassDiffusionModel(
        market_potential=M,
        p=0.02,
        q=0.30,
        dt=1.0,
        initial_adopters=0.0,
    )

    model.run(steps=100)

    N = np.array(model.history_N)
    growth = np.diff(N)

    # Growth per step is never negative
    assert np.all(growth >= -1e-12)
    # Cumulative adoption is non-decreasing
    assert np.all(N[1:] >= N[:-1] - 1e-12)


def test_bass_zero_p_and_q_produce_no_growth():
    """With zero innovation and imitation coefficients, there should be no growth."""
    M = 1000.0
    initial = 123.0

    model = BassDiffusionModel(
        market_potential=M,
        p=0.0,
        q=0.0,
        dt=1.0,
        initial_adopters=initial,
    )

    model.run(steps=50)

    N = np.array(model.history_N)

    # With p = q = 0, there should be no further adoption
    assert np.allclose(N, initial)


def test_bass_full_initial_saturation_stays_constant():
    """If the market is fully saturated at initialization, it should stay constant."""
    M = 1000.0
    model = BassDiffusionModel(
        market_potential=M,
        p=0.03,
        q=0.38,
        dt=1.0,
        initial_adopters=M,
    )

    model.run(steps=50)

    N = np.array(model.history_N)

    # Already saturated at t=0
    assert np.allclose(N, M)


def test_bass_with_different_timesteps():
    """Bass model should produce similar results with different timestep sizes."""
    M = 1000.0
    p = 0.03
    q = 0.38
    initial = 100.0

    # Large timestep
    model1 = BassDiffusionModel(
        market_potential=M,
        p=p,
        q=q,
        dt=1.0,
        initial_adopters=initial,
    )
    model1.run(steps=100)

    # Small timestep (10x more steps, 1/10 dt)
    model2 = BassDiffusionModel(
        market_potential=M,
        p=p,
        q=q,
        dt=0.1,
        initial_adopters=initial,
    )
    model2.run(steps=1000)

    # Final values should be similar
    assert model1.history_N[-1] == pytest.approx(model2.history_N[-1], rel=0.05)


def test_bass_initial_adopters_cannot_exceed_market_potential():
    """Initial adopters greater than M should be capped at M."""
    M = 1000.0
    model = BassDiffusionModel(
        market_potential=M,
        p=0.03,
        q=0.38,
        dt=1.0,
        initial_adopters=1500.0,  # Exceeds M
    )

    # The model should handle this gracefully
    assert model.N <= M + 1e-9


# --------- MultiLevelAutomationDiffusion tests --------- #

def _build_multilevel_model():
    """Helper to build a standard multi-level model for tests."""
    return MultiLevelAutomationDiffusion(
        total_fleet=8000,
        initial_L2=900,
        initial_L3=0,
        initial_L45=0,
        M2=6000,
        M3=2500,
        M45=800,
        p2=0.03, q2=0.4,
        p3=0.02, q3=0.3,
        p45=0.01, q45=0.2,
        dt=1.0,
    )


def test_multilevel_never_exceeds_total_fleet_and_respects_hierarchy():
    """Each level should stay within fleet size and respect hierarchy: L45 <= L3 <= L2."""
    model = _build_multilevel_model()
    model.run(steps=100)

    L2 = np.array(model.history_L2)
    L3 = np.array(model.history_L3)
    L45 = np.array(model.history_L45)

    # Total at each level never exceeds total fleet
    assert np.all(L2 <= 8000 + 1e-9)
    assert np.all(L3 <= 8000 + 1e-9)
    assert np.all(L45 <= 8000 + 1e-9)

    # Hierarchy: L45 <= L3 <= L2
    assert np.all(L3 <= L2 + 1e-9)
    assert np.all(L45 <= L3 + 1e-9)


def test_multilevel_growth_is_non_negative_for_each_level():
    """Growth at each level should be non-negative (adoption cannot decrease)."""
    model = _build_multilevel_model()
    model.run(steps=100)

    L2 = np.array(model.history_L2)
    L3 = np.array(model.history_L3)
    L45 = np.array(model.history_L45)

    dL2 = np.diff(L2)
    dL3 = np.diff(L3)
    dL45 = np.diff(L45)

    # Growth per step per level is never negative
    assert np.all(dL2 >= -1e-12)
    assert np.all(dL3 >= -1e-12)
    assert np.all(dL45 >= -1e-12)


def test_multilevel_respects_market_potentials():
    """Each level should not exceed its own Bass market potential."""
    model = _build_multilevel_model()
    model.run(steps=200)

    L2 = np.array(model.history_L2)
    L3 = np.array(model.history_L3)
    L45 = np.array(model.history_L45)

    # These correspond to the M2, M3, M45 used in _build_multilevel_model
    assert np.all(L2 <= 6000 + 1e-9)
    assert np.all(L3 <= 2500 + 1e-9)
    assert np.all(L45 <= 800 + 1e-9)


def test_multilevel_no_growth_if_all_pq_zero():
    """If all p and q are zero, adoption should stay at initial values."""
    model = MultiLevelAutomationDiffusion(
        total_fleet=8000,
        initial_L2=900,
        initial_L3=0,
        initial_L45=0,
        M2=6000,
        M3=2500,
        M45=800,
        p2=0.0, q2=0.0,
        p3=0.0, q3=0.0,
        p45=0.0, q45=0.0,
        dt=1.0,
    )

    model.run(steps=50)

    L2 = np.array(model.history_L2)
    L3 = np.array(model.history_L3)
    L45 = np.array(model.history_L45)

    assert np.allclose(L2, 900.0)
    assert np.allclose(L3, 0.0)
    assert np.allclose(L45, 0.0)


def test_multilevel_hierarchy_constraint_enforced_during_growth():
    """
    Test that hierarchy constraints are enforced even when higher levels
    have stronger growth parameters than lower levels.
    """
    model = MultiLevelAutomationDiffusion(
        total_fleet=1000,
        initial_L2=100,
        initial_L3=50,
        initial_L45=10,
        M2=500,
        M3=400,
        M45=300,
        # Give higher levels stronger growth (counterintuitive scenario)
        p2=0.01, q2=0.1,
        p3=0.05, q3=0.4,
        p45=0.1, q45=0.5,
        dt=1.0,
    )

    model.run(steps=50)

    L2 = np.array(model.history_L2)
    L3 = np.array(model.history_L3)
    L45 = np.array(model.history_L45)

    # Despite L45 having stronger growth parameters, it should never exceed L3
    assert np.all(L45 <= L3 + 1e-9)
    # And L3 should never exceed L2
    assert np.all(L3 <= L2 + 1e-9)


def test_multilevel_initial_values_respect_hierarchy():
    """Initial values that violate hierarchy should be corrected."""
    # Try to initialize with L3 > L2 (violates hierarchy)
    model = MultiLevelAutomationDiffusion(
        total_fleet=1000,
        initial_L2=100,
        initial_L3=200,  # Violates L3 <= L2
        initial_L45=50,
        M2=500,
        M3=400,
        M45=300,
        p2=0.01, q2=0.1,
        p3=0.01, q3=0.1,
        p45=0.01, q45=0.1,
        dt=1.0,
    )

    # Initial L3 should be capped at L2
    assert model.history_L3[0] <= model.history_L2[0] + 1e-9


def test_multilevel_initial_values_respect_market_potentials():
    """Initial values that exceed market potentials should be capped."""
    model = MultiLevelAutomationDiffusion(
        total_fleet=10000,
        initial_L2=5000,  # Exceeds M2
        initial_L3=0,
        initial_L45=0,
        M2=3000,  # Market potential smaller than initial
        M3=2000,
        M45=1000,
        p2=0.01, q2=0.1,
        p3=0.01, q3=0.1,
        p45=0.01, q45=0.1,
        dt=1.0,
    )

    # Initial L2 should be capped at M2
    assert model.history_L2[0] <= model.M2 + 1e-9


def test_multilevel_saturation_behavior():
    """Test that levels saturate at their market potentials over long runs."""
    model = MultiLevelAutomationDiffusion(
        total_fleet=10000,
        initial_L2=100,
        initial_L3=50,
        initial_L45=10,
        M2=1000,
        M3=500,
        M45=200,
        p2=0.05, q2=0.5,
        p3=0.05, q3=0.5,
        p45=0.05, q45=0.5,
        dt=1.0,
    )

    model.run(steps=500)

    L2 = np.array(model.history_L2)
    L3 = np.array(model.history_L3)
    L45 = np.array(model.history_L45)

    # After long run, levels should saturate near their market potentials
    # L2 should reach M2
    assert L2[-1] == pytest.approx(1000, rel=0.01)
    # L3 should reach M3 (500, which is less than L2)
    assert L3[-1] == pytest.approx(500, rel=0.01)
    # L45 should reach M45 (200, which is less than L3)
    assert L45[-1] == pytest.approx(200, rel=0.01)


def test_multilevel_constrained_by_lower_level():
    """
    Test scenario where L3 wants to grow beyond L2's current value but is constrained.
    """
    model = MultiLevelAutomationDiffusion(
        total_fleet=1000,
        initial_L2=100,
        initial_L3=90,
        initial_L45=0,
        M2=150,  # L2 can only grow to 150
        M3=500,  # L3 has high potential but constrained by L2
        M45=100,
        p2=0.01, q2=0.1,  # Slow growth for L2
        p3=0.1, q3=0.5,   # Fast growth for L3
        p45=0.01, q45=0.1,
        dt=1.0,
    )

    model.run(steps=100)

    L2 = np.array(model.history_L2)
    L3 = np.array(model.history_L3)

    # L3 should never exceed L2 despite having higher growth potential
    assert np.all(L3 <= L2 + 1e-9)
    # L3 should be close to L2 if it's being constrained
    final_gap = L2[-1] - L3[-1]
    assert final_gap >= -1e-9  # L3 can't exceed L2


def test_multilevel_different_timesteps():
    """Multi-level model should produce similar results with different timesteps."""
    # Coarse timestep
    model1 = MultiLevelAutomationDiffusion(
        total_fleet=8000,
        initial_L2=900,
        initial_L3=0,
        initial_L45=0,
        M2=6000,
        M3=2500,
        M45=800,
        p2=0.03, q2=0.4,
        p3=0.02, q3=0.3,
        p45=0.01, q45=0.2,
        dt=1.0,
    )
    model1.run(steps=100)

    # Fine timestep
    model2 = MultiLevelAutomationDiffusion(
        total_fleet=8000,
        initial_L2=900,
        initial_L3=0,
        initial_L45=0,
        M2=6000,
        M3=2500,
        M45=800,
        p2=0.03, q2=0.4,
        p3=0.02, q3=0.3,
        p45=0.01, q45=0.2,
        dt=0.1,
    )
    model2.run(steps=1000)

    # Final values should be similar
    assert model1.history_L2[-1] == pytest.approx(model2.history_L2[-1], rel=0.05)
    assert model1.history_L3[-1] == pytest.approx(model2.history_L3[-1], rel=0.05)
    assert model1.history_L45[-1] == pytest.approx(model2.history_L45[-1], rel=0.05)


def test_multilevel_time_tracking():
    """Test that time is tracked correctly in the multi-level model."""
    dt = 0.5
    steps = 100
    model = _build_multilevel_model()
    model.dt = dt

    model.run(steps=steps)

    expected_final_time = steps * dt
    assert model.t == pytest.approx(expected_final_time)
    assert len(model.history_time) == steps + 1  # Initial + steps
    assert model.history_time[-1] == pytest.approx(expected_final_time)
