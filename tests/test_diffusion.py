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
    """Helper to build a standard multi-level model for tests (5 levels)."""
    return MultiLevelAutomationDiffusion(
        total_fleet=10000,
        initial_L1=450,
        initial_L2=450,
        initial_L3=0,
        initial_L4=0,
        initial_L5=0,
        M1=7000,
        M2=6000,
        M3=3000,
        M4=1200,
        M5=500,
        p1=0.035, q1=0.45,
        p2=0.030, q2=0.40,
        p3=0.020, q3=0.30,
        p4=0.012, q4=0.22,
        p5=0.008, q5=0.15,
        dt=1.0,
    )


def test_multilevel_never_exceeds_total_fleet_and_respects_hierarchy():
    """Each level should stay within fleet size and respect hierarchy: L5 <= L4 <= L3 <= L2 <= L1."""
    model = _build_multilevel_model()
    model.run(steps=100)

    L1 = np.array(model.history_L1)
    L2 = np.array(model.history_L2)
    L3 = np.array(model.history_L3)
    L4 = np.array(model.history_L4)
    L5 = np.array(model.history_L5)

    # Total at each level never exceeds total fleet
    assert np.all(L1 <= 10000 + 1e-9)
    assert np.all(L2 <= 10000 + 1e-9)
    assert np.all(L3 <= 10000 + 1e-9)
    assert np.all(L4 <= 10000 + 1e-9)
    assert np.all(L5 <= 10000 + 1e-9)

    # Hierarchy: L5 <= L4 <= L3 <= L2 <= L1
    assert np.all(L2 <= L1 + 1e-9)
    assert np.all(L3 <= L2 + 1e-9)
    assert np.all(L4 <= L3 + 1e-9)
    assert np.all(L5 <= L4 + 1e-9)


def test_multilevel_growth_is_non_negative_for_each_level():
    """Growth at each level should be non-negative (adoption cannot decrease)."""
    model = _build_multilevel_model()
    model.run(steps=100)

    L1 = np.array(model.history_L1)
    L2 = np.array(model.history_L2)
    L3 = np.array(model.history_L3)
    L4 = np.array(model.history_L4)
    L5 = np.array(model.history_L5)

    dL1 = np.diff(L1)
    dL2 = np.diff(L2)
    dL3 = np.diff(L3)
    dL4 = np.diff(L4)
    dL5 = np.diff(L5)

    # Growth per step per level is never negative
    assert np.all(dL1 >= -1e-12)
    assert np.all(dL2 >= -1e-12)
    assert np.all(dL3 >= -1e-12)
    assert np.all(dL4 >= -1e-12)
    assert np.all(dL5 >= -1e-12)


def test_multilevel_respects_market_potentials():
    """Each level should not exceed its own Bass market potential."""
    model = _build_multilevel_model()
    model.run(steps=200)

    L1 = np.array(model.history_L1)
    L2 = np.array(model.history_L2)
    L3 = np.array(model.history_L3)
    L4 = np.array(model.history_L4)
    L5 = np.array(model.history_L5)

    # These correspond to the M1-M5 used in _build_multilevel_model
    assert np.all(L1 <= 7000 + 1e-9)
    assert np.all(L2 <= 6000 + 1e-9)
    assert np.all(L3 <= 3000 + 1e-9)
    assert np.all(L4 <= 1200 + 1e-9)
    assert np.all(L5 <= 500 + 1e-9)


def test_multilevel_no_growth_if_all_pq_zero():
    """If all p and q are zero, adoption should stay at initial values."""
    model = MultiLevelAutomationDiffusion(
        total_fleet=10000,
        initial_L1=450,
        initial_L2=450,
        initial_L3=0,
        initial_L4=0,
        initial_L5=0,
        M1=7000,
        M2=6000,
        M3=3000,
        M4=1200,
        M5=500,
        p1=0.0, q1=0.0,
        p2=0.0, q2=0.0,
        p3=0.0, q3=0.0,
        p4=0.0, q4=0.0,
        p5=0.0, q5=0.0,
        dt=1.0,
    )

    model.run(steps=50)

    L1 = np.array(model.history_L1)
    L2 = np.array(model.history_L2)
    L3 = np.array(model.history_L3)
    L4 = np.array(model.history_L4)
    L5 = np.array(model.history_L5)

    assert np.allclose(L1, 450.0)
    assert np.allclose(L2, 450.0)
    assert np.allclose(L3, 0.0)
    assert np.allclose(L4, 0.0)
    assert np.allclose(L5, 0.0)


def test_multilevel_hierarchy_constraint_enforced_during_growth():
    """
    Test that hierarchy constraints are enforced even when higher levels
    have stronger growth parameters than lower levels.
    """
    model = MultiLevelAutomationDiffusion(
        total_fleet=1000,
        initial_L1=100,
        initial_L2=80,
        initial_L3=50,
        initial_L4=20,
        initial_L5=10,
        M1=500,
        M2=450,
        M3=400,
        M4=350,
        M5=300,
        # Give higher levels stronger growth (counterintuitive scenario)
        p1=0.01, q1=0.1,
        p2=0.02, q2=0.2,
        p3=0.05, q3=0.4,
        p4=0.08, q4=0.5,
        p5=0.1, q5=0.6,
        dt=1.0,
    )

    model.run(steps=50)

    L1 = np.array(model.history_L1)
    L2 = np.array(model.history_L2)
    L3 = np.array(model.history_L3)
    L4 = np.array(model.history_L4)
    L5 = np.array(model.history_L5)

    # Despite higher levels having stronger growth parameters, hierarchy should be enforced
    assert np.all(L2 <= L1 + 1e-9)
    assert np.all(L3 <= L2 + 1e-9)
    assert np.all(L4 <= L3 + 1e-9)
    assert np.all(L5 <= L4 + 1e-9)


def test_multilevel_initial_values_respect_hierarchy():
    """Initial values that violate hierarchy should be corrected."""
    # Try to initialize with values that violate hierarchy
    model = MultiLevelAutomationDiffusion(
        total_fleet=1000,
        initial_L1=100,
        initial_L2=150,  # Violates L2 <= L1
        initial_L3=200,  # Violates L3 <= L2
        initial_L4=180,  # Violates L4 <= L3
        initial_L5=250,  # Violates L5 <= L4
        M1=500,
        M2=450,
        M3=400,
        M4=350,
        M5=300,
        p1=0.01, q1=0.1,
        p2=0.01, q2=0.1,
        p3=0.01, q3=0.1,
        p4=0.01, q4=0.1,
        p5=0.01, q5=0.1,
        dt=1.0,
    )

    # Initial values should be capped to respect hierarchy
    assert model.history_L2[0] <= model.history_L1[0] + 1e-9
    assert model.history_L3[0] <= model.history_L2[0] + 1e-9
    assert model.history_L4[0] <= model.history_L3[0] + 1e-9
    assert model.history_L5[0] <= model.history_L4[0] + 1e-9


def test_multilevel_initial_values_respect_market_potentials():
    """Initial values that exceed market potentials should be capped."""
    model = MultiLevelAutomationDiffusion(
        total_fleet=10000,
        initial_L1=6000,  # Exceeds M1
        initial_L2=5000,  # Exceeds M2
        initial_L3=4000,  # Exceeds M3
        initial_L4=2000,  # Exceeds M4
        initial_L5=1000,  # Exceeds M5
        M1=5000,  # Market potentials smaller than initial
        M2=3000,
        M3=2000,
        M4=1000,
        M5=500,
        p1=0.01, q1=0.1,
        p2=0.01, q2=0.1,
        p3=0.01, q3=0.1,
        p4=0.01, q4=0.1,
        p5=0.01, q5=0.1,
        dt=1.0,
    )

    # Initial values should be capped at their respective market potentials
    assert model.history_L1[0] <= model.M1 + 1e-9
    assert model.history_L2[0] <= model.M2 + 1e-9
    assert model.history_L3[0] <= model.M3 + 1e-9
    assert model.history_L4[0] <= model.M4 + 1e-9
    assert model.history_L5[0] <= model.M5 + 1e-9


def test_multilevel_saturation_behavior():
    """Test that levels saturate at their market potentials over long runs."""
    model = MultiLevelAutomationDiffusion(
        total_fleet=10000,
        initial_L1=100,
        initial_L2=80,
        initial_L3=50,
        initial_L4=20,
        initial_L5=10,
        M1=1500,
        M2=1000,
        M3=600,
        M4=300,
        M5=150,
        p1=0.05, q1=0.5,
        p2=0.05, q2=0.5,
        p3=0.05, q3=0.5,
        p4=0.05, q4=0.5,
        p5=0.05, q5=0.5,
        dt=1.0,
    )

    model.run(steps=500)

    L1 = np.array(model.history_L1)
    L2 = np.array(model.history_L2)
    L3 = np.array(model.history_L3)
    L4 = np.array(model.history_L4)
    L5 = np.array(model.history_L5)

    # After long run, levels should saturate near their market potentials
    assert L1[-1] == pytest.approx(1500, rel=0.01)
    assert L2[-1] == pytest.approx(1000, rel=0.01)
    assert L3[-1] == pytest.approx(600, rel=0.01)
    assert L4[-1] == pytest.approx(300, rel=0.01)
    assert L5[-1] == pytest.approx(150, rel=0.01)


def test_multilevel_constrained_by_lower_level():
    """
    Test scenario where higher levels want to grow beyond lower levels but are constrained.
    """
    model = MultiLevelAutomationDiffusion(
        total_fleet=1000,
        initial_L1=100,
        initial_L2=95,
        initial_L3=90,
        initial_L4=85,
        initial_L5=80,
        M1=150,  # L1 can only grow to 150
        M2=200,  # L2 has potential but constrained by L1
        M3=500,  # L3 has high potential but constrained by L2
        M4=400,  # L4 has potential but constrained by L3
        M5=300,  # L5 has potential but constrained by L4
        p1=0.01, q1=0.1,   # Slow growth for L1
        p2=0.03, q2=0.2,   # Faster growth for L2
        p3=0.1, q3=0.5,    # Fast growth for L3
        p4=0.08, q4=0.4,   # Fast growth for L4
        p5=0.06, q5=0.3,   # Fast growth for L5
        dt=1.0,
    )

    model.run(steps=100)

    L1 = np.array(model.history_L1)
    L2 = np.array(model.history_L2)
    L3 = np.array(model.history_L3)
    L4 = np.array(model.history_L4)
    L5 = np.array(model.history_L5)

    # Higher levels should never exceed lower levels despite having higher growth potential
    assert np.all(L2 <= L1 + 1e-9)
    assert np.all(L3 <= L2 + 1e-9)
    assert np.all(L4 <= L3 + 1e-9)
    assert np.all(L5 <= L4 + 1e-9)


def test_multilevel_different_timesteps():
    """Multi-level model should produce similar results with different timesteps."""
    # Coarse timestep
    model1 = MultiLevelAutomationDiffusion(
        total_fleet=10000,
        initial_L1=450,
        initial_L2=450,
        initial_L3=0,
        initial_L4=0,
        initial_L5=0,
        M1=7000,
        M2=6000,
        M3=3000,
        M4=1200,
        M5=500,
        p1=0.035, q1=0.45,
        p2=0.030, q2=0.40,
        p3=0.020, q3=0.30,
        p4=0.012, q4=0.22,
        p5=0.008, q5=0.15,
        dt=1.0,
    )
    model1.run(steps=100)

    # Fine timestep
    model2 = MultiLevelAutomationDiffusion(
        total_fleet=10000,
        initial_L1=450,
        initial_L2=450,
        initial_L3=0,
        initial_L4=0,
        initial_L5=0,
        M1=7000,
        M2=6000,
        M3=3000,
        M4=1200,
        M5=500,
        p1=0.035, q1=0.45,
        p2=0.030, q2=0.40,
        p3=0.020, q3=0.30,
        p4=0.012, q4=0.22,
        p5=0.008, q5=0.15,
        dt=0.1,
    )
    model2.run(steps=1000)

    # Final values should be similar
    assert model1.history_L1[-1] == pytest.approx(model2.history_L1[-1], rel=0.05)
    assert model1.history_L2[-1] == pytest.approx(model2.history_L2[-1], rel=0.05)
    assert model1.history_L3[-1] == pytest.approx(model2.history_L3[-1], rel=0.05)
    assert model1.history_L4[-1] == pytest.approx(model2.history_L4[-1], rel=0.05)
    assert model1.history_L5[-1] == pytest.approx(model2.history_L5[-1], rel=0.05)


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
