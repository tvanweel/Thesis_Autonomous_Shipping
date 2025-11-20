"""
Bass Diffusion Model for Technology Adoption.

Implements the Bass (1969) diffusion model for modeling autonomous shipping
technology penetration in the Dutch inland waterway fleet.

References:
    Bass, F. M. (1969). A new product growth for model consumer durables.
    Management Science, 15(5), 215-227.
"""

import numpy as np
from typing import Dict, Union, Optional


class BassDiffusion:
    """
    Bass diffusion model for technology adoption.
    
    The model calculates cumulative adoption over time using:
        F(t) = (1 - e^(-(p+q)t)) / (1 + (q/p)e^(-(p+q)t))
    
    where:
        F(t) = cumulative adoption fraction at time t
        p = coefficient of innovation (external influence)
        q = coefficient of imitation (internal influence / word-of-mouth)
    
    Parameters
    ----------
    market_potential : float
        Total market size (maximum possible adopters)
    p_innovation : float
        Coefficient of innovation (0 < p < 1)
    q_imitation : float
        Coefficient of imitation (0 < q < 1)
        
    Raises
    ------
    ValueError
        If parameters are outside valid ranges
        
    Examples
    --------
    >>> model = BassDiffusion(market_potential=1000, p_innovation=0.03, q_imitation=0.38)
    >>> adoption_at_year_5 = model.cumulative_adoption(t=5)
    >>> penetration_rate = model.penetration_rate(t=5)
    """
    
    def __init__(
        self,
        market_potential: float,
        p_innovation: float,
        q_imitation: float
    ):
        # Validate parameters
        if market_potential <= 0:
            raise ValueError("Market potential must be positive")
        
        if not (0 <= p_innovation <= 1):
            raise ValueError("Innovation coefficient p must be in [0, 1]")
        
        if not (0 <= q_imitation <= 1):
            raise ValueError("Imitation coefficient q must be in [0, 1]")
        
        self.market_potential = market_potential
        self.p = p_innovation
        self.q = q_imitation
    
    def cumulative_adoption(self, t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Calculate cumulative number of adopters at time t.
        
        Parameters
        ----------
        t : float or array-like
            Time point(s) to evaluate
            
        Returns
        -------
        float or ndarray
            Number of cumulative adopters
        """
        t = np.asarray(t)
        
        # Handle t=0 case
        if np.any(t == 0):
            result = np.zeros_like(t, dtype=float)
            mask = t > 0
            if np.any(mask):
                result[mask] = self._calculate_adoption(t[mask])
            return float(result) if t.ndim == 0 else result
        
        return self._calculate_adoption(t)
    
    def _calculate_adoption(self, t: np.ndarray) -> np.ndarray:
        """Internal calculation avoiding division by zero."""
        # Bass formula: F(t) = (1 - e^(-(p+q)t)) / (1 + (q/p)e^(-(p+q)t))
        p_plus_q = self.p + self.q
        
        # Handle edge case where p + q = 0
        if p_plus_q == 0:
            return np.zeros_like(t, dtype=float)
        
        exp_term = np.exp(-p_plus_q * t)
        
        # Handle case where p is very small (avoid division by zero)
        if self.p < 1e-10:
            # If p ≈ 0, formula simplifies
            fraction = 1 - exp_term
        else:
            fraction = (1 - exp_term) / (1 + (self.q / self.p) * exp_term)
        
        adoption = self.market_potential * fraction
        
        # Ensure we don't exceed market potential due to numerical errors
        adoption = np.minimum(adoption, self.market_potential)
        
        return float(adoption) if adoption.ndim == 0 else adoption
    
    def adoption_rate(self, t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Calculate instantaneous adoption rate (derivative) at time t.
        
        This is dF/dt, the rate of new adoptions per time unit.
        
        Parameters
        ----------
        t : float or array-like
            Time point(s) to evaluate
            
        Returns
        -------
        float or ndarray
            Adoption rate at time t
        """
        t = np.asarray(t)
        
        p_plus_q = self.p + self.q
        
        if p_plus_q == 0:
            return 0.0 if t.ndim == 0 else np.zeros_like(t, dtype=float)
        
        # Derivative of Bass formula
        exp_term = np.exp(-(p_plus_q) * t)
        
        if self.p < 1e-10:
            # Simplified for p ≈ 0
            rate = self.market_potential * p_plus_q * exp_term
        else:
            denominator = (1 + (self.q / self.p) * exp_term) ** 2
            numerator = (p_plus_q ** 2 / self.p) * exp_term
            rate = self.market_potential * numerator / denominator
        
        return float(rate) if rate.ndim == 0 else rate
    
    def penetration_rate(self, t: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Calculate market penetration rate (fraction of market adopted).
        
        Parameters
        ----------
        t : float or array-like
            Time point(s) to evaluate
            
        Returns
        -------
        float or ndarray
            Penetration rate between 0 and 1
        """
        return self.cumulative_adoption(t) / self.market_potential
    
    def time_to_peak(self) -> float:
        """
        Calculate time when adoption rate reaches its maximum.
        
        Returns
        -------
        float
            Time of peak adoption rate
        """
        if self.p + self.q == 0:
            return np.inf
        
        if self.p < 1e-10:
            return 0.0
        
        # Peak occurs at t* = ln(q/p) / (p+q)
        t_peak = np.log(self.q / self.p) / (self.p + self.q)
        return max(0, t_peak)


class MultiLevelDiffusion:
    """
    Multi-level Bass diffusion for sequential technology adoption.
    
    Models adoption of multiple automation levels (L0-L5) with different
    diffusion parameters and start times.
    
    Parameters
    ----------
    market_potential : float
        Total fleet size
    levels_config : dict
        Configuration for each automation level:
        {
            'L1': {'p': 0.03, 'q': 0.38, 'start_time': 0},
            'L2': {'p': 0.025, 'q': 0.35, 'start_time': 5},
            ...
        }
        
    Examples
    --------
    >>> config = {
    ...     'L1': {'p': 0.03, 'q': 0.38, 'start_time': 0},
    ...     'L2': {'p': 0.025, 'q': 0.35, 'start_time': 5}
    ... }
    >>> model = MultiLevelDiffusion(market_potential=1000, levels_config=config)
    >>> composition = model.fleet_composition(t=10)
    """
    
    def __init__(
        self,
        market_potential: float,
        levels_config: Dict[str, Dict[str, float]]
    ):
        self.market_potential = market_potential
        self.levels_config = levels_config
        
        # Create Bass models for each level
        self.levels = {}
        for level_name, config in levels_config.items():
            self.levels[level_name] = {
                'model': BassDiffusion(
                    market_potential=market_potential,
                    p_innovation=config['p'],
                    q_imitation=config['q']
                ),
                'start_time': config['start_time']
            }
    
    def level_adoption(self, level: str, t: float) -> float:
        """
        Get cumulative adoption for a specific level at time t.
        
        Parameters
        ----------
        level : str
            Automation level (e.g., 'L1', 'L2')
        t : float
            Time point
            
        Returns
        -------
        float
            Number of vessels at this automation level
        """
        if level not in self.levels:
            raise ValueError(f"Unknown level: {level}")
        
        level_data = self.levels[level]
        start_time = level_data['start_time']
        
        # Before start time, no adoption
        if t < start_time:
            return 0.0
        
        # Calculate adoption since start
        time_since_start = t - start_time
        return level_data['model'].cumulative_adoption(time_since_start)
    
    def fleet_composition(self, t: float) -> Dict[str, float]:
        """
        Get complete fleet composition at time t.
        
        Distributes fleet across levels. Vessels transition from lower to higher
        automation levels (L0 -> L1 -> L2 -> ...), so adoption is cumulative
        replacement rather than additive.
        
        Parameters
        ----------
        t : float
            Time point
            
        Returns
        -------
        dict
            Fleet distribution: {'L0': 500, 'L1': 300, 'L2': 200, ...}
        """
        composition = {}
        
        # Get raw adoption for each level
        level_adoptions = {}
        for level in self.levels.keys():
            level_adoptions[level] = self.level_adoption(level, t)
        
        # For sequential adoption: higher levels "take" from lower levels
        # Sort levels to process in order (L0, L1, L2, ...)
        sorted_levels = sorted(level_adoptions.keys())
        
        remaining_fleet = self.market_potential
        
        # Start from highest level and work down
        # (vessels upgrade to highest available level)
        for level in reversed(sorted_levels):
            if level == 'L0':
                # L0 is whatever remains
                composition['L0'] = remaining_fleet
            else:
                # Higher levels take from available fleet
                adoption = min(level_adoptions[level], remaining_fleet)
                composition[level] = adoption
                remaining_fleet -= adoption
        
        return composition
    
    def penetration_by_level(self, t: float) -> Dict[str, float]:
        """
        Get penetration rate (0-1) for each level at time t.
        
        Parameters
        ----------
        t : float
            Time point
            
        Returns
        -------
        dict
            Penetration rates: {'L0': 0.5, 'L1': 0.3, 'L2': 0.2, ...}
        """
        composition = self.fleet_composition(t)
        return {
            level: count / self.market_potential
            for level, count in composition.items()
        }


def apply_policy_effects(
    base_model: BassDiffusion,
    policy: Dict[str, float]
) -> BassDiffusion:
    """
    Apply policy interventions to modify diffusion parameters.
    
    Policy effects:
    - subsidy: increases q (imitation coefficient)
    - strict_standards: decreases p (innovation coefficient)
    - infrastructure_investment: increases market_potential
    
    Parameters
    ----------
    base_model : BassDiffusion
        Base diffusion model
    policy : dict
        Policy parameters, e.g.:
        {
            'subsidy_factor': 1.2,  # 20% increase in q
            'standards_factor': 0.8,  # 20% decrease in p
            'infrastructure_factor': 1.1  # 10% increase in M
        }
        
    Returns
    -------
    BassDiffusion
        New model with policy effects applied
    """
    # Apply factors (default to 1.0 if not specified)
    new_p = base_model.p * policy.get('standards_factor', 1.0)
    new_q = base_model.q * policy.get('subsidy_factor', 1.0)
    new_M = base_model.market_potential * policy.get('infrastructure_factor', 1.0)
    
    # Ensure parameters stay in valid range
    new_p = np.clip(new_p, 0, 1)
    new_q = np.clip(new_q, 0, 1)
    
    return BassDiffusion(
        market_potential=new_M,
        p_innovation=new_p,
        q_imitation=new_q
    )
