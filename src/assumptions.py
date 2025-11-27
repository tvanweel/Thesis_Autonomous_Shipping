"""
Model Assumptions Configuration

This module contains all configurable assumptions used by the simulation models.
Modify these values to run different scenarios and conduct sensitivity analysis.

All values in this file are actively used by the model code. Changing these
values will directly affect model behavior.

Categories:
- TRAFFIC: Traffic behavior model parameters (congestion, crossroads)
- AGENT: Agent/vessel characteristics (speed, RIS connectivity)
- NETWORK: Network distances between ports (Rhine corridor)

Citation Key:
- [EMPIRICAL]: Values from literature/data with citations
- [CALIBRATED]: Fitted to Rhine corridor data
- [ASSUMED]: Expert judgment or borrowed from adjacent domains
"""

# =============================================================================
# TRAFFIC BEHAVIOR MODEL
# =============================================================================
# Used in: src/models/traffic.py

TRAFFIC = {
    # Edge capacity model
    # [ASSUMED] Maximum vessels per km of waterway
    # Derived from: Rhine navigable width 200-400m, inland vessel length ~85-110m,
    # safe separation ~2 vessel lengths
    "vessels_per_km_capacity": 12,

    # Speed reduction model
    # [ASSUMED] Maximum speed reduction factor due to congestion (70% at capacity)
    # Linear model: effective_speed = base_speed × (1 - 0.7 × density_ratio)
    "congestion_impact_factor": 0.7,

    # [ASSUMED] Minimum speed ratio (vessels maintain 30% of base speed even at extreme congestion)
    "min_speed_ratio": 0.3,

    # Crossroad management
    # [ASSUMED] Transit time through crossroad in hours (30 minutes)
    # Crossroads defined as nodes with 3+ connections
    # Priority: First-Come-First-Served (FCFS)
    "crossroad_transit_time_hours": 0.5,
}

# =============================================================================
# AGENT/VESSEL CHARACTERISTICS
# =============================================================================
# Used in: src/models/agent.py, examples/agent_demo_random.py

AGENT = {
    # Speed characteristics
    # [ASSUMED] Default cruising speed for inland vessels (km/h)
    "default_vessel_speed_kmh": 14.0,

    # [ASSUMED] Speed range for vessel heterogeneity (min, max in km/h)
    "vessel_speed_range_kmh": (10.0, 18.0),

    # RIS (River Information Services) connectivity probabilities
    # [ASSUMED] Probability of RIS connectivity by automation level
    # Assumption: Higher automation correlates with better digital infrastructure
    "ris_connectivity_by_level": {
        # L0-L2: Manual to partial automation
        "L0_L2": 0.2,  # 20% RIS connectivity
        # L3-L4: Conditional to high automation
        "L3_L4": 0.6,  # 60% RIS connectivity
        # L5: Full automation
        "L5": 0.9,     # 90% RIS connectivity
    },
}

# =============================================================================
# NETWORK CONFIGURATION (Rhine Corridor)
# =============================================================================
# Used in: examples/agent_demo.py, examples/agent_demo_random.py

NETWORK = {
    # Port-to-port distances (km)
    # [CALIBRATED] From GIS/maritime data for Rhine river corridor
    "distances_km": {
        "rotterdam_dordrecht": 24,
        "dordrecht_nijmegen": 95,
        "nijmegen_duisburg": 111,
        "duisburg_cologne": 60,
        "cologne_mannheim": 143,
        "rotterdam_nijmegen_direct": 130,  # Alternative direct route
    },

    # Note: Current model uses straight-line distances
    # [ASSUMED] Actual river distances are ~10-20% longer due to meandering
    # This factor is NOT currently applied in the model
    "distance_meandering_factor": 1.15,
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_traffic_config():
    """
    Get traffic behavior configuration.

    Returns:
        dict: Traffic model parameters

    Example:
        >>> config = get_traffic_config()
        >>> capacity = config['vessels_per_km_capacity']
    """
    return TRAFFIC.copy()


def get_agent_config():
    """
    Get agent/vessel configuration.

    Returns:
        dict: Agent model parameters

    Example:
        >>> config = get_agent_config()
        >>> default_speed = config['default_vessel_speed_kmh']
    """
    return AGENT.copy()


def get_network_config():
    """
    Get network configuration.

    Returns:
        dict: Network distances and parameters

    Example:
        >>> config = get_network_config()
        >>> distances = config['distances_km']
    """
    return NETWORK.copy()


def get_all_assumptions():
    """
    Get all model assumptions as a single dictionary.

    Returns:
        dict: All assumptions organized by category

    Example:
        >>> assumptions = get_all_assumptions()
        >>> traffic_params = assumptions['traffic']
        >>> agent_params = assumptions['agent']
    """
    return {
        "traffic": TRAFFIC.copy(),
        "agent": AGENT.copy(),
        "network": NETWORK.copy(),
    }


# =============================================================================
# ASSUMPTIONS NOT CURRENTLY USED IN MODEL CODE
# =============================================================================
# The following assumptions were in the original file but are NOT used in
# the current model implementation. They are preserved here for reference
# but have been commented out.
#
# If you need to use these in future model versions, uncomment and integrate
# them into the appropriate model files.

# DIFFUSION_MODEL = {
#     # [EMPIRICAL] Bass model imitation parameter for maritime technology
#     # Source: Frank (2004), maritime technology diffusion
#     "bass_q_maritime": 0.38,
#
#     # [EMPIRICAL] Retrofit cost multiplier vs new build
#     # Source: AUTOSHIP D4.2, Table 7
#     "retrofit_cost_multiplier": 2.3,
# }

# SAFETY_RELIABILITY = {
#     # [ASSUMED] Remote operator center (ROC) takeover time
#     # Mean time in seconds; no maritime data available, based on automotive analogy
#     "roc_takeover_time_mean_seconds": 45,
#
#     # [ASSUMED] Platform failure correlation for cooperative vessels
#     # Vessels sharing ROC may have correlated failures
#     "platform_failure_correlation": 0.8,
# }

# PORT_INFRASTRUCTURE = {
#     # [CALIBRATED] Port capacities from port authority data (tons/year)
#     "port_capacity_tons_per_year": {
#         "rotterdam": 470_000_000,
#         "dordrecht": 50_000_000,
#         "nijmegen": 20_000_000,
#         "duisburg": 50_000_000,
#         "cologne": 30_000_000,
#         "mannheim": 25_000_000,
#     },
#
#     # [CALIBRATED] Narrow channel capacity reduction
#     # From Bingen AIS analysis
#     "narrow_channel_capacity_reduction": 0.65,
# }

# SCENARIO_PARAMETERS = {
#     # [SCENARIO] L3 adoption start year (varied in scenarios)
#     "l3_adoption_start_year_options": [2026, 2028, 2030],
#
#     # [SCENARIO] Infrastructure investment threshold (varied in scenarios)
#     "infrastructure_investment_threshold_options": [0.15, 0.25, 0.35],
#
#     # [SCENARIO] Automation level range
#     "automation_level_range": (0, 5),
#
#     # [SCENARIO] Number of vessels (for sensitivity analysis)
#     "num_vessels_options": [10, 20, 50, 100],
#
#     # [SCENARIO] Max simulation steps (for sensitivity analysis)
#     "max_simulation_steps_options": [100, 200, 500],
# }

# PHYSICAL_CHARACTERISTICS = {
#     # [EMPIRICAL] Rhine waterway characteristics
#     "rhine_navigable_width_m": (200, 400),
#     "inland_vessel_length_m": (85, 110),
#     "safe_separation_vessel_lengths": 2,
# }
