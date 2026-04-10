# Iteration II Feature Gap Report

> **How to read this document**  
> **Current truth** for Iteration II delivery is the [High-Level Findings](#high-level-findings) table, the [Outstanding Items Checklist](#outstanding-items-checklist) (all complete), [iteration-ii-implementation-summary.md](iteration-ii-implementation-summary.md), and [Post-Iteration II Bug Fixes](#post-iteration-ii-bug-fixes-nov-26-2025).  
> The [Methodology](#methodology) and framework notes under [Framework-Specific Details](#framework-specific-details) describe how the audit was done. The short [Historical gap analysis (superseded)](#historical-gap-analysis-superseded) section replaces an older mid-document write-up that stated pre-shipment gaps; it is kept only for traceability, not as a description of today’s code.

## Methodology

- Read all Memory Bank files and `docs/project-scope.md` to refresh authoritative scope.
- Reviewed the current converter implementations (`quantum_converters/converters/*`) together with their AST parsers and gate registries.
- Inspected the shared OpenQASM builder, gate library, and expression utilities to verify modifier/data-type/control-flow coverage.
- Cross-referenced the findings against the “Left Behind” checklist supplied by the user.

## High-Level Findings

| Area | Status | Notes |
| --- | --- | --- |
| Cirq controlled/parameterized gates | **✅ Shipped** | Runtime + AST now lower `cirq.ControlledGate` instances into `cy/ch/crx/cry/crz/cp` and tests pass. |
| Cirq CCZ | **✅ Shipped** | Nested controls are flattened and emitted as `ccz` in both AST and runtime paths. |
| Qiskit controlled-U | **✅ Shipped** | AST/runtime emit `cp/crx/cry/crz/cu` with correct parameter order; integration tests green. |
| PennyLane Iteration II gates | **✅ Shipped (2025-11-18)** | All Iteration II gates implemented: CY, CH, CRX, CRY, CRZ, CP, CSWAP, CCZ, GlobalPhase. 8 new tests passing. |
| Gate modifiers (`negctrl@`, `ctrl(n)@`, `pow(k)@`) | **✅ Shipped (2025-11-18)** | Full support for `negctrl@`, `ctrl(n)@`, and `pow(k)@` modifiers. 7 new tests passing. |
| Iteration II data types (`complex`, casting) | **✅ Shipped (2025-11-18)** | Complex type support added to QASM3Builder. |
| Advanced control flow (while/break/continue) | **✅ Shipped (2025-11-18)** | `add_while_loop`, `add_break_statement`, `add_continue_statement` implemented. |
| Classical bitwise & shift ops | **✅ Shipped (2025-11-18)** | All bitwise (`&`, `|`, `^`, `~`) and shift (`<<`, `>>`) operators implemented in expression parser. |
| Subroutines/functions | **✅ Shipped (2025-11-18)** | `define_subroutine` and `add_return_statement` with full parameter/return type support. |

## Framework-Specific Details

### Cirq Converter

- **Controlled gates**: Both the runtime path and AST parser now flatten `cirq.ControlledGate(...)` recursively. The converter maps the base gate + total control count into the OpenQASM mnemonics (`cy`, `ch`, `crx`, `cry`, `crz`, `cp`, `ccz`). See `quantum_converters/converters/cirq_to_qasm.py` `_handle_controlled_gate`.
- **AST emission**: `CirqASTVisitor`’s `_handle_controlled_gate_cirq` builds `GateNode`s with the QASM-ready gate names/parameters, so the AST pipeline produces the same QASM strings as the runtime fallback.
- **Tests**: `tests/integration/test_cirq_integration.py::test_controlled_parameterized_gates` now passes inside `qasm_env`, confirming the feature end-to-end.

### Qiskit Converter

- **Registries**: `quantum_converters/config/mappings.py` now includes the Iteration II controlled gates plus `cu(θ, φ, λ, γ)` with proper parameter order.
- **AST parser**: `_handle_controlled_two_qubit_gate` in `quantum_converters/parsers/qiskit_parser.py` extracts parameters + control/target indices for `cp`, `crx`, `cry`, `crz`, and `cu`, so AST conversion no longer drops them.
- **Converter**: `_convert_gate_node` and `_add_qiskit_operation` emit those gates through `QASM3Builder.apply_gate`, producing standard OpenQASM 3 statements. Full integration suite (`tests/integration/test_qiskit_integration.py`) passes in the venv.

### PennyLane Converter

- **Registry**: `quantum_converters/config/mappings.py` includes Iteration II gates (CY, CH, CRX, CRY, CRZ, CP, CSWAP, CCZ, GlobalPhase) with OpenQASM mapping and parameter handling aligned to the other frameworks.
- **Converter/parser**: Iteration II operations are emitted through the shared QASM3 builder path (not left as comments-only fallbacks for that gate set). Implementation details and test pointers: [iteration-ii-implementation-summary.md](iteration-ii-implementation-summary.md).
- **Tests**: `tests/integration/test_pennylane_iteration_ii.py` (8 tests) covers Iteration II gate coverage; `tests/integration/test_pennylane_integration.py` covers Iteration I parity.

## Historical gap analysis (superseded)

*Before **2025-11-18**, a prior revision of this report documented concrete gaps: PennyLane registry stopped at Iteration I gates; `GateModifier` / builder did not yet cover `negctrl@`, `ctrl(n)@`, and `pow(k)@` end-to-end; `QASM3Builder` lacked `while` / `break` / `continue`, `complex`, bitwise and shift operators in the expression layer, and subroutine/`return` support. That analysis drove the implementation. **Those gaps are closed** for Iteration II scope—see the High-Level Findings table and Outstanding Items Checklist above. The obsolete code excerpts and “still missing” wording were removed to avoid contradicting the shipped state.*

## Outstanding Items Checklist

**UPDATE (2025-11-18): All items completed! ✅**

All previously outstanding items have been implemented and tested:

1. ✅ **PennyLane Iteration II gates**: Registry extended with CY, CH, CRX, CRY, CRZ, CP, CSWAP, CCZ, GlobalPhase. Parameter extraction updated for controlled gates. 8 new integration tests passing.

2. ✅ **Gate modifiers**: Full implementation of `negctrl@`, `ctrl(n)@`, and `pow(k)@` modifiers in both `GateModifier` dataclass and `QASM3Builder._build_modifier_str`. 7 new integration tests passing.

3. ✅ **Language features**: Complete Iteration II classical features implemented:
   - Complex type support
   - While loops, break, continue statements
   - Bitwise operators (`&`, `|`, `^`, `~`)
   - Shift operators (`<<`, `>>`)
   - Subroutines/functions with return statements
   - 15 new integration tests passing

**Total new tests**: 30 tests  
**Test status**: All passing (54/54 integration tests)  
**Implementation date**: November 18, 2025

See [iteration-ii-implementation-summary.md](iteration-ii-implementation-summary.md) for a concise implementation summary (shipped areas, key paths, tests).


## Post-Iteration II Bug Fixes (Nov 26, 2025)

Several critical bugs were identified and fixed after the Iteration II release:

1.  **Cirq Multi-Qubit Measurement**: Fixed `CirqASTVisitor` to correctly handle multi-qubit measurements (e.g., `cirq.measure(q0, q1)`). Previously, only the first qubit was measured.
2.  **Qiskit Multi-Qubit Measurement**: Fixed `QiskitToQASM3Converter` to correctly iterate over all qubit-clbit pairs in a batch measurement.
3.  **Runtime QRNG Bug**: Fixed `_circuit_to_code` in `backend/qcanvas_runtime/core.py` to correctly generate single-qubit Cirq code (`q0 = cirq.LineQubit(0)` instead of `range(1)`), resolving a `NameError`.
