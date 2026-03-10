## Paper 2 – Secure AST-Based Transpilation of Multi‑Framework Quantum Programs to OpenQASM 3.0

### 1. Problem and Motivation

- **Framework fragmentation**: Qiskit, Cirq, and PennyLane all use different Python APIs and conventions, making it hard to share or reuse quantum programs across ecosystems.
- **Unsafe transpilation approaches**: Existing converters typically *execute* user Python code to obtain a circuit object, which is unacceptable in a cloud/multi‑tenant setting because arbitrary code execution is a major security risk.
- **Need for a secure, standard IR**: OpenQASM 3.0 is a rich, hardware‑agnostic intermediate representation, but there is little tooling that safely converts real framework code into standards‑compliant QASM 3.

The paper proposes a **secure, AST‑based transpilation pipeline** that converts source code from Qiskit, Cirq, and PennyLane into OpenQASM 3.0 **without executing the user’s code**.

### 2. High‑Level Approach

The pipeline has three main stages:

1. **Framework‑specific AST parsing**
   - Use Python’s `ast` module to parse the user’s Python source into an abstract syntax tree.
   - Implement dedicated `NodeVisitor` classes for:
     - `QiskitASTVisitor` (method‑based construction like `qc.h(0)`)
     - `CirqASTVisitor` (function‑based construction like `cirq.H(q0)`)
     - `PennyLaneASTVisitor` (decorator‑based @`qml.qnode` pattern)
   - Visitors identify:
     - Circuit declarations
     - Qubit/bit counts
     - Gate applications
     - Measurements, resets, barriers
     - Simple control flow structures in the Python code that affect circuit construction.

2. **Unified Circuit AST (intermediate representation)**
   - All frameworks map to a **framework‑agnostic IR**:
     - `CircuitAST` – stores global qubit/bit counts, parameters, and a list of operations.
     - `GateNode` – gate name, target qubit indices, parameters, modifiers (e.g. ctrl, inv, pow).
     - `MeasurementNode`, `ResetNode`, `BarrierNode`, and optional `ControlFlowNode`.
   - This IR decouples framework parsing from QASM code generation and makes the system extensible to new frameworks later.

3. **OpenQASM 3.0 code generation**
   - Use a dedicated **`QASM3Builder`** plus helper modules:
     - `QASM3GateLibrary` – maps framework gate names to standard QASM gate names.
     - `QASM3Expression` – formats classical expressions, recognizes constants (`np.pi → pi`, etc.).
   - The builder:
     - Emits the prelude: `OPENQASM 3.0;`, `include "stdgates.inc";`, and register declarations.
     - Walks the `CircuitAST` and emits gate calls, measurements, resets, and barriers.
     - Handles **gate modifiers** such as `ctrl@`, `inv@`, `negctrl@`, and `pow(k)@`.

### 3. Key Technical Ideas

- **Secure static analysis instead of execution**
  - The default path never executes user code; it statically inspects the AST to recover the circuit.
  - This removes most security risks associated with arbitrary Python execution in hosted environments.

- **Variable and loop tracking**
  - The visitors maintain a `variables: Dict[str, Any]` map to:
    - Infer qubit counts from patterns like `n_bits = 8`, `QuantumCircuit(n_bits, n_bits)`.
    - Resolve loop bounds (`for i in range(n_bits):`) so indices like `q[i]` become correct in the IR.
    - Count classical bits based on actual measurements instead of just constructor arguments.

- **Framework‑specific patterns**
  - Qiskit: detect `QuantumCircuit` assignments, then parse `qc.method(...)` calls.
  - Cirq: detect `cirq.Circuit(...)` constructor arguments and `circuit.append(...)` calls; map `cirq.H(q)` style.
  - PennyLane: detect `@qml.qnode(dev)` functions, traverse the function body, and extract `qml.Op(wires=...)` calls and returned observables/measurements.

- **Gate modifier and advanced OpenQASM 3 support**
  - The IR and builder handle:
    - Standard gates and parameterized gates.
    - Advanced gate modifiers:
      - `ctrl@`, `ctrl(n)@`
      - `inv@`
      - `negctrl@`
      - `pow(k)@`
    - Iteration I and II language features: rich type system, while/break/continue, subroutines, bitwise and shift operators.

- **Sandboxed runtime fallback**
  - For rare cases where AST analysis cannot recover the circuit (heavy metaprogramming, dynamic imports), there is a **fallback path**:
    - Execute the code in a tightly restricted sandbox (no `os`, no `subprocess`, no file or network access, strict timeouts).
    - Extract a framework circuit object and then convert to QASM using the same builder.
    - This keeps compatibility for complex programs while preserving strong security guarantees.

### 4. Implementation Details

- Implemented in the `quantum_converters` package:
  - `parsers/` – Qiskit, Cirq, PennyLane AST visitors.
  - `base/` – `circuit_ast.py`, `qasm3_builder.py`, `qasm3_gates.py`, `qasm3_expression.py`.
  - `converters/` – high‑level converter classes orchestrating parse → IR → QASM.
- Supports **full Iteration I** and **full Iteration II** feature sets of OpenQASM 3.0 for gate‑based circuits (excluding timing, pulse‑level and hardware‑specific features).

### 5. Evaluation Summary

- **Test suite:** 105 tests total:
  - 48 Iteration I unit tests (types, gates, control flow, I/O).
  - 54 integration tests across:
    - Qiskit, Cirq, PennyLane (Iteration I and II),
    - gate modifiers,
    - language features.
  - 4 expected‑failure tests for known corner cases.
- **Results:**
  - 100% pass rate for all relevant tests; AST‑based parsing succeeded on all integration tests (no fallback needed for those).
  - Average transpilation time:
    - ~15–18 ms total per circuit (AST parse + analysis + QASM generation).
  - Correctness validated by:
    - syntax checking of generated QASM 3,
    - simulating original framework circuits and generated QASM on QSim backends and comparing measurement distributions.

### 6. Contributions Claimed by the Paper

1. A secure, AST‑based transpilation architecture that avoids executing user code while converting Qiskit, Cirq, and PennyLane programs to OpenQASM 3.0.\n2. A unified `CircuitAST` intermediate representation and QASM 3 generation infrastructure with full Iteration I and II support for gate‑based features.\n3. Techniques for variable tracking and loop‑pattern analysis that handle realistic quantum code (dynamic qubit counts, `q[i]` indexing, derived measurement counts).\n4. A comprehensive evaluation showing 100% success on a large test suite with sub‑20 ms compile times.\n5. A discussion of security, limitations, and extensibility (adding new frameworks) based on real implementation experience in QCanvas.

