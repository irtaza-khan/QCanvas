# Iteration II Feature Gap Report

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

The PennyLane → QASM registry only enumerates Iteration I gates:

```
57:86:quantum_converters/config/mappings.py
        "h": GateMap(...),
        ...
        "swap": GateMap(...),
        "ccx": GateMap(openqasm_gate="ccx", target_gate="Toffoli"),
```

The converter calls `builder.add_comment` for anything outside that list (`_add_pennylane_operation`), so all Iteration II gates (CY, CH, CR*, CP, CU, CSWAP, CCZ, GPHASE) are still missing exactly as the checklist states.

## Shared Infrastructure Gaps

### Gate Modifiers

`GateModifier` and `QASM3Builder._build_modifier_str` only know about `inv`, `ctrl`, and `pow`, but no code sets `pow` or multi-control counts, and there is no representation for `negctrl@`.

```
64:88:quantum_converters/base/qasm3_gates.py
class GateModifier:
    inverse: bool = False
    ctrl_qubits: Optional[int] = None
    power: Optional[float] = None
    ...
        if self.ctrl_qubits is not None:
            if self.ctrl_qubits == 1:
                parts.append("ctrl")
            else:
                parts.append(f"ctrl({self.ctrl_qubits})")
```

Converters never populate `GateModifier.ctrl_qubits` or `power`, so `ctrl(n)@` and `pow(k)@` remain theoretical.

### Language / Control-Flow Features

- `QASM3Builder` exposes `add_if_statement` and `add_for_loop` only; there are no helpers for `while`, `break`, or `continue`.
- No builder or parser support exists for declaring the Iteration II `complex` type or type casting.
- The expression parser (`quantum_converters/base/qasm3_expression.py`) stops at arithmetic/logical operators; bitwise (`& | ^ ~`) and shift (`<< >>`) operators from Iteration II are absent from `PRECEDENCE` and never emitted.
- There is no representation of subroutine/function AST nodes or builder methods for `def`/`return`, so Subroutines/Functions remain unimplemented.

These observations confirm the “Missing AST nodes / advanced language features” portion of the checklist.

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

See `docs/iteration-ii-implementation-summary.md` for detailed implementation documentation.


## Post-Iteration II Bug Fixes (Nov 26, 2025)

Several critical bugs were identified and fixed after the Iteration II release:

1.  **Cirq Multi-Qubit Measurement**: Fixed `CirqASTVisitor` to correctly handle multi-qubit measurements (e.g., `cirq.measure(q0, q1)`). Previously, only the first qubit was measured.
2.  **Qiskit Multi-Qubit Measurement**: Fixed `QiskitToQASM3Converter` to correctly iterate over all qubit-clbit pairs in a batch measurement.
3.  **Runtime QRNG Bug**: Fixed `_circuit_to_code` in `backend/qcanvas_runtime/core.py` to correctly generate single-qubit Cirq code (`q0 = cirq.LineQubit(0)` instead of `range(1)`), resolving a `NameError`.
