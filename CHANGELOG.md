# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-08

### Added
- **Initial public SDK release**: `qcanvas-sdk` distribution with `compile()` and `compile_and_execute()` API
- Support for **Cirq** circuits → OpenQASM 3.0 via `convert_cirq_to_qasm3()`
- Support for **Qiskit** circuits → OpenQASM 3.0 via `convert_qiskit_to_qasm3()`
- Support for **PennyLane** QNodes → OpenQASM 3.0 via `convert_pennylane_to_qasm3()`
- Framework auto-detection: `compile(circuit)` infers framework from object type
- Result types: `SimulationResult` and `HybridExecutionResult` dataclasses
- Graceful fallbacks: imports work with or without optional framework dependencies
- Package distributed via PyPI with optional extras: `[cirq]`, `[qiskit]`, `[pennylane]`, `[all]`
- GitHub Actions CI workflow for build/test and automated publish to TestPyPI and PyPI on tags
- Basic smoke tests for import and API validation

### Notes
- Backend runtime (`qcanvas_runtime`) and FastAPI server are separate distributions
- The wheel includes `quantum_converters` but does not require moving repo files
- Backward compatibility shim: if `quantum_converters` is not available, falls back to bundled runtime

## [0.1.2] - 2026-05-08

### Changed
- Bumped package version again to avoid TestPyPI file-name reuse during upload
