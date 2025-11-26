# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
