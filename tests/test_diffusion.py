"""
Test suite for Bass diffusion model.
These tests define the expected behavior BEFORE implementation.
"""

import pytest
import numpy as np
from src.models.diffusion import BassDiffusion


class TestBassDiffusionInitialization:
    """Test that Bass model initializes correctly."""
    
    def test_creates_with_valid_parameters(self):
        """Should create model with valid parameters."""
        model = BassDiffusion(
            market_potential=1000,
            p_innovation=0.03,
            q_imitation=0.38
        )
        assert model.market_potential == 1000
        assert model.p == 0.03
        assert model.q == 0.38
    
    def test_rejects_negative_market_potential(self):
        """Should raise error for negative market potential."""
        with pytest.raises(ValueError):
            BassDiffusion(market_potential=-100, p_innovation=0.03, q_imitation=0.38)
    
    def test_rejects_invalid_coefficients(self):
        """Should raise error for coefficients outside [0, 1]."""
        with pytest.raises(ValueError):
            BassDiffusion(market_potential=1000, p_innovation=-0.01, q_imitation=0.38)
        
        with pytest.raises(ValueError):
            BassDiffusion(market_potential=1000, p_innovation=0.03, q_imitation=1.5)


class TestBassDiffusionCalculations:
    """Test core diffusion calculations."""
    
    @pytest.fixture
    def standard_model(self):
        """Standard Bass model for testing."""
        return BassDiffusion(
            market_potential=1000,
            p_innovation=0.03,
            q_imitation=0.38
        )
    
    def test_cumulative_adoption_at_t0_is_zero(self, standard_model):
        """At time 0, no adoption should have occurred."""
        adoption = standard_model.cumulative_adoption(t=0)
        assert adoption == 0
    
    def test_cumulative_adoption_increases_over_time(self, standard_model):
        """Adoption should increase monotonically."""
        t1 = standard_model.cumulative_adoption(t=5)
        t2 = standard_model.cumulative_adoption(t=10)
        t3 = standard_model.cumulative_adoption(t=15)
        
        assert t1 < t2 < t3
    
    def test_cumulative_adoption_approaches_market_potential(self, standard_model):
        """At large t, adoption should approach market potential."""
        adoption = standard_model.cumulative_adoption(t=100)
        assert adoption > 0.95 * standard_model.market_potential
        assert adoption <= standard_model.market_potential
    
    def test_adoption_rate_peaks_then_declines(self, standard_model):
        """Adoption rate should follow inverted U-shape."""
        rates = [standard_model.adoption_rate(t) for t in range(0, 20, 2)]
        
        # Find peak
        peak_idx = rates.index(max(rates))
        
        # Rates before peak should be increasing
        assert all(rates[i] < rates[i+1] for i in range(peak_idx))
        
        # Rates after peak should be decreasing
        assert all(rates[i] > rates[i+1] for i in range(peak_idx, len(rates)-1))
    
    def test_penetration_rate_is_percentage(self, standard_model):
        """Penetration rate should be between 0 and 1."""
        for t in range(0, 20):
            penetration = standard_model.penetration_rate(t)
            assert 0 <= penetration <= 1


class TestBassDiffusionScenarios:
    """Test different adoption scenarios."""
    
    def test_high_innovation_fast_early_adoption(self):
        """High p should lead to faster early adoption."""
        high_p = BassDiffusion(market_potential=1000, p_innovation=0.08, q_imitation=0.38)
        low_p = BassDiffusion(market_potential=1000, p_innovation=0.01, q_imitation=0.38)
        
        # At t=2, high innovation should have more adoption
        assert high_p.cumulative_adoption(t=2) > low_p.cumulative_adoption(t=2)
    
    def test_high_imitation_steeper_growth(self):
        """High q should lead to steeper S-curve."""
        high_q = BassDiffusion(market_potential=1000, p_innovation=0.03, q_imitation=0.6)
        low_q = BassDiffusion(market_potential=1000, p_innovation=0.03, q_imitation=0.2)
        
        # Mid-period adoption should differ more
        t_mid = 8
        assert abs(high_q.cumulative_adoption(t_mid) - low_q.cumulative_adoption(t_mid)) > 100
    
    def test_time_to_peak_adoption_rate(self):
        """Should correctly calculate when adoption rate peaks."""
        model = BassDiffusion(market_potential=1000, p_innovation=0.03, q_imitation=0.38)
        
        t_peak = model.time_to_peak()
        
        # Peak should be where second derivative = 0
        rate_before = model.adoption_rate(t_peak - 0.5)
        rate_at = model.adoption_rate(t_peak)
        rate_after = model.adoption_rate(t_peak + 0.5)
        
        assert rate_at >= rate_before
        assert rate_at >= rate_after


class TestMultiLevelDiffusion:
    """Test sequential diffusion across automation levels."""
    
    def test_multi_level_diffusion_initialization(self):
        """Should create multi-level diffusion with different parameters per level."""
        levels_config = {
            'L1': {'p': 0.03, 'q': 0.38, 'start_time': 0},
            'L2': {'p': 0.025, 'q': 0.35, 'start_time': 5},
            'L3': {'p': 0.02, 'q': 0.30, 'start_time': 10},
        }
        
        from src.models.diffusion import MultiLevelDiffusion
        model = MultiLevelDiffusion(
            market_potential=1000,
            levels_config=levels_config
        )
        
        assert len(model.levels) == 3
        assert 'L1' in model.levels
    
    def test_sequential_adoption(self):
        """Later levels should not adopt before their start time."""
        from src.models.diffusion import MultiLevelDiffusion
        
        levels_config = {
            'L1': {'p': 0.03, 'q': 0.38, 'start_time': 0},
            'L2': {'p': 0.025, 'q': 0.35, 'start_time': 5},
        }
        
        model = MultiLevelDiffusion(market_potential=1000, levels_config=levels_config)
        
        # At t=3, L2 should have 0 adoption
        fleet_comp = model.fleet_composition(t=3)
        assert fleet_comp['L2'] == 0
        
        # At t=7, L2 should have some adoption
        fleet_comp = model.fleet_composition(t=7)
        assert fleet_comp['L2'] > 0
    
    def test_fleet_composition_sums_to_market_potential(self):
        """Total fleet should always equal market potential."""
        from src.models.diffusion import MultiLevelDiffusion
        
        levels_config = {
            'L0': {'p': 0, 'q': 0, 'start_time': 0},  # Manual (no adoption)
            'L1': {'p': 0.03, 'q': 0.38, 'start_time': 0},
            'L2': {'p': 0.025, 'q': 0.35, 'start_time': 3},
        }
        
        model = MultiLevelDiffusion(market_potential=1000, levels_config=levels_config)
        
        for t in range(0, 20):
            composition = model.fleet_composition(t)
            total = sum(composition.values())
            assert abs(total - 1000) < 0.01  # Allow small floating point error


class TestPolicyInfluenceOnDiffusion:
    """Test how policy interventions affect diffusion parameters."""
    
    def test_subsidy_increases_imitation_coefficient(self):
        """Policy subsidy should increase q (word-of-mouth effect)."""
        from src.models.diffusion import BassDiffusion
        
        base_model = BassDiffusion(market_potential=1000, p_innovation=0.03, q_imitation=0.38)
        
        # Apply policy effect
        subsidy_factor = 1.2
        subsidized_q = base_model.q * subsidy_factor
        policy_model = BassDiffusion(market_potential=1000, p_innovation=0.03, q_imitation=subsidized_q)
        
        # With subsidy, adoption should be faster mid-period
        t_mid = 8
        assert policy_model.cumulative_adoption(t_mid) > base_model.cumulative_adoption(t_mid)
    
    def test_strict_standards_slow_early_adoption(self):
        """Strict standards should reduce p (innovation coefficient)."""
        base_model = BassDiffusion(market_potential=1000, p_innovation=0.03, q_imitation=0.38)
        
        standards_factor = 0.7
        restricted_p = base_model.p * standards_factor
        policy_model = BassDiffusion(market_potential=1000, p_innovation=restricted_p, q_imitation=0.38)
        
        # With strict standards, early adoption should be slower
        t_early = 3
        assert policy_model.cumulative_adoption(t_early) < base_model.cumulative_adoption(t_early)


class TestDiffusionEdgeCases:
    """Test edge cases and error handling."""
    
    def test_handles_zero_time(self):
        """Should handle t=0 without errors."""
        model = BassDiffusion(market_potential=1000, p_innovation=0.03, q_imitation=0.38)
        assert model.cumulative_adoption(0) == 0
        assert model.adoption_rate(0) >= 0
    
    def test_handles_large_time(self):
        """Should handle very large t without overflow."""
        model = BassDiffusion(market_potential=1000, p_innovation=0.03, q_imitation=0.38)
        adoption = model.cumulative_adoption(t=1000)
        assert np.isfinite(adoption)
        assert adoption <= model.market_potential
    
    def test_vectorized_calculation(self):
        """Should efficiently calculate for multiple time points."""
        model = BassDiffusion(market_potential=1000, p_innovation=0.03, q_imitation=0.38)
        
        time_points = np.arange(0, 20, 0.5)
        adoptions = model.cumulative_adoption(time_points)
        
        assert len(adoptions) == len(time_points)
        assert all(np.isfinite(adoptions))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
