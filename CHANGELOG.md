# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Simple network module with Node and Edge classes
- Network class with graph operations using NetworkX
- Support for directed and undirected networks
- Shortest path calculation between nodes
- All simple paths enumeration
- Network connectivity checks
- Subgraph extraction
- Dictionary serialization/deserialization

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
