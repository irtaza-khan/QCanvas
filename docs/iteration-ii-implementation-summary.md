# Iteration II Implementation Summary

**Status:** Shipped (November 18, 2025)  
**Related:** [Iteration II Feature Gap Report](feature-gap-report.md) (methodology, framework notes, post-release fixes)

This document summarizes what was delivered for OpenQASM 3.0 **Iteration II** scope in QCanvas: PennyLane gates, gate modifiers, classical language extensions, and shared builder/parser support.

## Delivered capabilities

### PennyLane → OpenQASM (Iteration II gates)

Registry and conversion paths extended for: **CY, CH, CRX, CRY, CRZ, CP, CSWAP, CCZ, GlobalPhase**, with parameter extraction aligned to OpenQASM mnemonics.

**Primary touchpoints:** `quantum_converters/config/mappings.py`, PennyLane converter and parser under `quantum_converters/converters/` and `quantum_converters/parsers/`.

### Gate modifiers

Support for **negctrl@**, **ctrl(n)@**, and **pow(k)@** in the shared gate/modifier pipeline and QASM emission.

**Primary touchpoints:** `quantum_converters/base/qasm3_gates.py` (`GateModifier`, builder modifier strings), `QASM3Builder` application paths.

### Classical language features

- **Types:** `complex` and casting aligned with Iteration II scope.
- **Control flow:** `while`, `break`, `continue` (builder and emission).
- **Expressions:** Bitwise (`&`, `|`, `^`, `~`) and shift (`<<`, `>>`).
- **Subroutines:** Function definitions, calls, returns, parameter/return typing as scoped in project Iteration II.

**Primary touchpoints:** `quantum_converters/base/` (builder, expression parser), relevant parser visitors per framework.

### Cirq / Qiskit alignment

Controlled and multi-control gates, **CCZ**, and Qiskit **controlled-U** parameter ordering were brought in line with the same QASM3Builder outputs (see feature-gap report for file-level notes).

## Tests added (integration)

| Area | Test module | Count (approx.) |
|------|-------------|-----------------|
| PennyLane Iteration II gates | `tests/integration/test_pennylane_iteration_ii.py` | 8 |
| Gate modifiers | `tests/integration/test_gate_modifiers.py` | 7 |
| Language features | `tests/integration/test_iteration_ii_language_features.py` | 15 |

**Total new integration tests for Iteration II tranche:** 30 (all passing at release; see `feature-gap-report.md` for current status).

## Post-release fixes

Multi-qubit measurement fixes (Cirq AST visitor, Qiskit batch measurement) and a hybrid-runtime QRNG code-generation fix are documented under **Post-Iteration II Bug Fixes** in [feature-gap-report.md](feature-gap-report.md).

## Out of scope (unchanged)

Per `docs/project-scope.md`: pulse-level OpenPulse, timing/box, extern/memory/QEC, and hardware-specific extensions remain excluded.
