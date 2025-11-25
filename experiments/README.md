# Experiments

This folder contains experimental code that was developed but is not currently part of the main codebase.

## ABM Network (`abm_network/`)

Complete Agent-Based Model implementation integrating Rhine river spatial network with automation diffusion model.

**Contents:**
- `network.py` - Rhine River spatial network (18 ports, 17 segments, NetworkX-based)
- `shipping_abm.py` - Main ABM model with Mesa 3.0+ compatibility
- `agents/vessel_agent.py` - Individual vessel agents with automation levels
- `visualization/network_graph.py` - Network graph visualization for diffusion
- `test_rhine_network.py` - 43 tests for Rhine network (98% coverage)
- `test_shipping_abm.py` - 26 tests for ABM (all passing)
- `show_rhine_network.py` - Demo script for Rhine network visualization
- `show_shipping_abm.py` - Demo script for ABM simulation

**Features:**
- Realistic Rhine geography from Rotterdam to Basel
- Multi-level automation diffusion (L0-L5)
- Vessel movement with collision risk calculation
- Port congestion and route optimization
- Comprehensive data collection with Mesa DataCollector

**Status:** Fully functional and tested. Archived for potential future use.

**Branch:** `feature/network-graph` (preserved)
