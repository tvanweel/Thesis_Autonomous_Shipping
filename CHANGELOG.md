# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2024-11-26

### Added
- Traffic behavior module for realistic inland waterway simulations
- Dynamic speed adjustment based on vessel density on edges
- Crossroad management with waiting times and priority rules
- TrafficManager class to coordinate traffic across the network
- EdgeTraffic class to track vessel positions and calculate congestion
- CrossroadState class for crossroad occupation and queuing
- Agent waiting_time tracking attribute
- Traffic-aware simulation in agent_demo_random.py

### Changed
- Agent model: Added `waiting_time` field for tracking delays
- CSV exports now include:
  - `waiting_time_hours` column in ship summary
  - `effective_speed_kmh` column in time series (shows congestion impact)
  - `total_time_hours` column (travel + waiting time)
- Simulation metrics now include total and average waiting times
- agent_demo_random.py updated to use TrafficManager for realistic behavior

### Assumptions Documented
- Edge capacity: 12 vessels per km based on Rhine waterway dimensions
- Speed reduction model: Linear (70% max slowdown at capacity)
- Crossroad transit time: 30 minutes per vessel
- Minimum speed: 30% of base speed even at full capacity
- Crossroad priority: First-come-first-served (FCFS)

### Infrastructure
- Updated CHANGELOG.md to version 0.4.0
- Created feature/traffic-behavior branch

## [0.3.0] - 2024-11-26

### Added
- Agent model for network-based ABM simulations
- Agent class with network navigation capabilities
- AgentState enum for agent operational states (IDLE, TRAVELING, AT_DESTINATION, STOPPED)
- Agent features:
  - Set destination and plan routes through networks
  - Travel along routes with distance/time tracking
  - Stop/resume functionality
  - Custom properties for agent specialization
  - Journey tracking (distance, time, route progress)
  - Dictionary serialization/deserialization
- `create_agent()` factory function with automatic ID generation
- Agent state management (IDLE, TRAVELING, AT_DESTINATION, STOPPED)

### Infrastructure
- Updated src/__init__.py to version 0.3.0
- Extended models module with agent capabilities

## [0.2.0] - 2024-11-26

### Added
- Simple network implementation for ABM modeling
- Node class with ID, name, type, and properties
- Edge class with source, target, weight, and properties
- Network class with comprehensive graph operations:
  - Add/get nodes and edges
  - Get neighbors of nodes
  - Find shortest paths
  - Find all paths between nodes
  - Calculate node degrees
  - Check network connectivity
  - Create subgraphs
  - Export/import to dictionary format

### Infrastructure
- Created feature branch workflow
- Established CHANGELOG.md for version tracking
- Updated src/__init__.py with version information

## [0.1.0] - 2024-11-25

### Added
- Bass diffusion model implementation
- Multi-level automation diffusion model (L0-L5)
- Diffusion visualization script
- Unit tests for diffusion models

### Changed
- Cleaned up previous network and vessel simulation code
- Restructured project to focus on core diffusion model

### Removed
- Previous Rhine network implementation
- Vessel and ship simulator modules
- ABM network experiments
- Ship simulation experiments

## [0.0.1] - 2024-11-19

### Added
- Initial project setup
- Basic project structure
- Package configuration
