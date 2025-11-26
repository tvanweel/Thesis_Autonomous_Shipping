"""
Autonomous Shipping Thesis - Agent-Based Modeling Framework

A simulation framework for analyzing autonomous shipping technology adoption
and its impact on inland waterway transportation.
"""

__version__ = "0.3.0"
__author__ = "Tijn van Weel"
__description__ = "ABM framework for autonomous shipping research"

# Version history
__changelog__ = {
    "0.3.0": "Added agent model for network-based ABM simulations",
    "0.2.0": "Added simple network module for ABM modeling",
    "0.1.0": "Initial diffusion model implementation",
    "0.0.1": "Project setup"
}

# Public API
from src.models.diffusion import (
    BassDiffusionModel,
    MultiLevelAutomationDiffusion
)

from src.models.network import (
    Node,
    Edge,
    Network
)

from src.models.agent import (
    Agent,
    AgentState,
    create_agent,
    reset_agent_id_counter
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__description__",

    # Diffusion models
    "BassDiffusionModel",
    "MultiLevelAutomationDiffusion",

    # Network models
    "Node",
    "Edge",
    "Network",

    # Agent models
    "Agent",
    "AgentState",
    "create_agent",
    "reset_agent_id_counter",
]
