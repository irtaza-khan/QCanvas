# Algorithm Achievement Tracking — Options & Analysis

---

## ❓ Core Question: Is the Generated OpenQASM Identical for the Same Algorithm?

**Short answer: No. The same algorithm written in different ways will NOT always produce identical OpenQASM output.**

This is the most important thing to understand before picking a tracking strategy. Here is why:

### 1. Framework Differences (Qiskit vs Cirq vs PennyLane)

Each framework has its own internal gate set and its own QASM exporter. The same Bell state circuit produces fundamentally different QASM depending on which framework compiled it:

**Written in Qiskit:**
```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0], q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
```

**Written in Cirq (same logical circuit):**
```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
h q[1];          // ← Cirq uses big-endian qubit ordering — indices are flipped!
cx q[1], q[0];   // ← control/target swapped
measure q[1] -> c[0];
measure q[0] -> c[1];
```

Just choosing a different framework reverses the index order. The circuits are logically equivalent but the QASM text is different.

### 2. Gate Decomposition Differences

Not every framework supports every gate natively. When a gate is not natively supported, it gets **decomposed** into other gates — and each framework decomposes differently.

Example: A `SWAP` gate written manually in Qiskit stays as `swap q[0], q[1]`, but in Cirq or PennyLane it may be decomposed into three CNOT gates:
```qasm
cx q[0], q[1];
cx q[1], q[0];
cx q[0], q[1];  // Equivalent to swap, but looks completely different
```

Similarly, the Toffoli (CCX) gate in Grover's oracle might be decomposed into ~6 CNOT + T gates in frameworks that use a more primitive gate set.

### 3. The Oracle Problem (Grover, Deutsch-Jozsa)

For algorithms that contain a **problem-specific oracle**, the generated QASM will be completely different for every different problem instance, even if you use the same framework:

- Grover's searching for `|011⟩` vs `|101⟩` → completely different X-gate patterns before the CCX
- Deutsch-Jozsa with a constant function vs a balanced function → the oracle section is entirely different (empty vs CNOT gates)

The algorithm structure is the same but the QASM content changes.

### 4. Compiler Optimizations

Frameworks apply different circuit optimizations before generating QASM. Two users writing the "same" Grover's circuit might get:
- User A: 45 gates (unoptimized)
- User B: 31 gates (after transpile/optimization)

Completely different QASM, same algorithm.

### 5. Parameterized Circuits (VQE, QAOA)

VQE and QAOA circuits use **variable angles** (θ, γ, β) that change on every optimization iteration. The QASM will have different numeric values every single time:
```qasm
ry(0.3451) q[0];   // Iteration 1
ry(0.7823) q[0];   // Iteration 2 — same circuit structure, completely different numbers
```

---

## ✅ What DOES Stay Consistent Across All Implementations?

Even though the exact QASM text differs, certain **structural properties** are guaranteed to remain present regardless of framework, optimization, or problem instance:

| Algorithm | Guaranteed Structural Feature | Why it's always there |
|---|---|---|
| Entanglement | Always has `cx`, `cz`, or equivalent | Entanglement requires a 2-qubit gate by definition |
| Superposition | Always has Hadamard (`h`) | Superposition cannot be created without H (or equivalent Y-rotation) |
| Deutsch-Jozsa | Always has H gates on input qubits at start AND end | The H-Oracle-H structure is mathematically mandatory |
| Grover | Always has repeated oracle + diffusion iterations | The amplitude amplification structure cannot be removed |
| Shor | Always has a QFT section — recognizable by cascading phase rotations | QFT is a required subroutine regardless of implementation |
| VQE | Always has parameterized rotation gates (`ry`, `rx`, `rz` with variable angles) | The variational form requires parameterized gates |
| QAOA | Always alternates between ZZ-interaction (`cx-rz-cx`) and X-rotation (`rx`) layers | The cost/mixer structure is the definition of QAOA |

**Conclusion: We cannot match exact QASM strings or hashes. But we CAN reliably detect structural patterns (specific gate types, gate ordering patterns, gate count relationships) that every correct implementation of an algorithm must contain.**

---

## ⚙️ What This Means For Our Tracking Strategy

Since exact QASM matching is impossible, our tracking options rank as follows:

| Approach | Works given QASM variability? | Recommended? |
|---|---|---|
| Exact QASM hash/string match | ❌ Never — QASM varies too much | No |
| Structural pattern / regex on QASM | ✅ Yes — gate presence is stable | Yes (for simple algorithms) |
| `algorithm_hint` metadata tag | ✅ Yes — bypasses QASM entirely | Yes (best for complex algorithms) |
| Template-context tracking | ✅ Yes — bypasses QASM entirely | Yes (cleanest solution) |
| Python AST inspection | ✅ Yes — framework imports are stable | Yes (for Python/hybrid execution) |

---



> **Purpose:** This document analyses how the QCanvas backend can detect and track the 7 algorithm-based achievements. It covers what the circuit diagram approach can offer, what its limitations are, and what the recommended implementation strategy is.

---

## The 7 Algorithm Achievements

| Achievement | Activity Logged | Rarity | XP |
|---|---|---|---|
| Entanglement Expert | `entangled_circuit` | Rare | 200 |
| Superposition Savant | `superposition_circuit` | Rare | 150 |
| Deutsch Detective | `algorithm_deutsch` | Epic | 300 |
| Grover's Guardian | `algorithm_grover` | Epic | 400 |
| Shor's Scholar | `algorithm_shor` | Legendary | 500 |
| VQE Virtuoso | `algorithm_vqe` | Epic | 400 |
| QAOA Champion | `algorithm_qaoa` | Epic | 450 |

None of these activity types are currently being logged anywhere in the backend. This document proposes how to fix this.

---

## Option 1: Circuit Diagram / QASM Pattern Recognition (Structural Analysis)

### Can we identify algorithms from their circuit diagrams?

**Yes — with varying degrees of confidence.** Every quantum algorithm has a mathematically-defined circuit structure, and that structure translates into a predictable sequence of gates in the generated QASM code. This means we can parse the raw QASM string to detect algorithm fingerprints.

Here is how each algorithm's circuit looks and what makes it structurally unique:

---

### Entanglement (Bell State / CNOT chains)

**Circuit signature:**
```
h q[0];
cx q[0], q[1];   ← CNOT gate between two qubits
```

**OpenQASM keywords to match:**
- `cx` (CNOT gate) — the defining gate of entanglement between two qubits
- `cz` (Controlled-Z), `swap` — also create entanglement

**Detection regex:**
```python
re.search(r'\bcx\b|\bcz\b|\bccx\b|\bswap\b', qasm_code, re.IGNORECASE)
```

**Confidence:** ✅ Very High. Any circuit with `cx` or `cz` is genuinely entangled. False positives are nearly impossible.

---

### Superposition (Hadamard Gate)

**Circuit signature:**
```
h q[0];   ← Hadamard gate puts qubit into superposition
```

**OpenQASM keywords to match:**
- `h q[` — the Hadamard gate applied to any qubit

**Detection regex:**
```python
re.search(r'\bh\s+q\[', qasm_code, re.IGNORECASE)
```

**Confidence:** ✅ Very High. Superposition is exclusively created by Hadamard (H) gates in standard circuits.

---

### Deutsch-Jozsa Algorithm

**Circuit signature:**
```
// Phase 1: Initialize — H on all n input qubits, X + H on ancilla qubit
h q[0]; h q[1]; ... h q[n-1];
x q[n];   ← ancilla
h q[n];   ← ancilla

// Phase 2: Oracle — problem-specific (constant or balanced function)
// For constant oracle: nothing or I gate
// For balanced oracle: cx gates linking input qubits to ancilla

// Phase 3: Interference — H on all input qubits again
h q[0]; h q[1]; ... h q[n-1];

// Phase 4: Measure
measure q[0] -> c[0]; measure q[1] -> c[1]; ...
```

**Structural fingerprint:**
1. Hadamard gates appear **twice on the input qubits** (before and after the oracle)
2. One qubit (ancilla) gets `x` then `h` at the start
3. Final measurement on all input qubits

**Detection strategy (heuristic):**
- Count distinct qubit Hadamard applications — if the same qubit index appears in H gates at both the beginning AND near the end, that is the Deutsch-Jozsa sandwich pattern

**Confidence:** ⚠️ Medium. The H-Oracle-H pattern is distinctive, but a user could accidentally write a circuit with the same structure without intending to implement Deutsch-Jozsa.

---

### Grover's Search Algorithm

**Circuit signature:**
```
// Step 1: Initialize — H on all n qubits
h q[0]; h q[1]; ... h q[n-1];

// Step 2: Oracle — marks the target state (problem-specific)
// Typically a pattern of X gates + CCX (Toffoli) + X gates
x q[0]; x q[1]; ccx q[0], q[1], q[2]; x q[0]; x q[1];

// Step 3: Diffusion operator — H, X, multi-controlled-Z, X, H (repeated)
h q[0]; h q[1]; x q[0]; x q[1]; cz q[0], q[1]; x q[0]; x q[1]; h q[0]; h q[1];

// Repeat Steps 2 & 3 for ~sqrt(N) iterations
```

**Structural fingerprint:**
1. Initial H on all qubits
2. CCX (Toffoli) gates — identifying the oracle
3. A Diffusion block: H → X → multi-controlled-phase → X → H (the "Grover diffusion" pattern)
4. The above is **repeated** (Grover iterations)

**Detection strategy (heuristic):**
- Look for `ccx` (Toffoli) gates — very Grover-specific
- Look for the alternating `h ... x ... ccx/cz ... x ... h` pattern
- Count repetitions — Grover circuits repeat the oracle + diffusion block

**Confidence:** ⚠️ Medium. `ccx` is a strong signal (it's used in phase-kickback oracles), but not exclusive to Grover's.

---

### Shor's Factoring Algorithm

**Circuit signature:**
```
// Quantum Phase Estimation (QPE) subroutine:
// Phase 1: H on all query register qubits
h q[0]; h q[1]; h q[2]; ...

// Phase 2: Controlled unitary (modular exponentiation)
// This is the most complex part — a deep circuit of controlled-phase and swap gates
cp(pi/2) q[0], q[1];   ← controlled-phase rotation
swap q[0], q[1];         ← swap gate
cu q[0], q[1], q[2], q[3]; ← controlled-U operations

// Phase 3: Inverse QFT (Quantum Fourier Transform)
h q[0]; cp(-pi/2) q[1], q[0]; swap q[0], q[1];
```

**Structural fingerprint:**
1. Controlled-phase gates: `cp(` or `p(` with angle values that are fractions of π
2. `swap` gates (part of the QFT)
3. A cascade of controlled-phase rotations with angles π/2, π/4, π/8... (QFT pattern)
4. Very large circuit depth — Shor's is by far the deepest circuit in the set

**Detection strategy (heuristic):**
- Look for `cp(` or `p(` angle rotations in arithmetic progressions (π, π/2, π/4...)
- Look for swap gates combined with controlled phases — this is the QFT fingerprint
- Look for overall gate count > threshold (Shor's is always a large circuit)

**Confidence:** ⚠️ Medium-Low. QFT-based circuits are distinctive but the pattern can appear in other phase estimation algorithms too.

---

### VQE — Variational Quantum Eigensolver

**Circuit signature:**
```
// Parameterized ansatz (variational form)
// Typically: RY rotations with variable parameters + entanglement layers
ry(theta[0]) q[0];   ← parameterized rotation
ry(theta[1]) q[1];
cx q[0], q[1];       ← entanglement layer
ry(theta[2]) q[0];
ry(theta[3]) q[1];
```

**Structural fingerprint:**
1. `ry(...)` or `rx(`, `rz(` — **parameterized** rotation gates with named parameters
2. Layered structure: rotation block → entanglement block → rotation block (repeated)
3. No measurement in the middle (VQE circuits are usually shot-based measurement at the end)

**Detection strategy (heuristic):**
- Look for parameterized rotation gates: `ry(`, `rx(`, `rz(` with variable angles
- Look for alternating rotation-entanglement layers
- If the code uses Python (hybrid execution), look for `from qiskit.circuit.library import EfficientSU2` or `import pennylane; qml.BasicEntanglerLayers`

**Confidence:** ⚠️ Medium. Parameterized gates are the distinguishing feature, but any parametric circuit could trigger this.

---

### QAOA — Quantum Approximate Optimization Algorithm

**Circuit signature:**
```
// Alternating gamma and beta layers
// Cost unitary (problem Hamiltonian)
cx q[0], q[1];
rz(2*gamma) q[1];   ← gamma = cost parameter
cx q[0], q[1];

// Mixer unitary
rx(2*beta) q[0];    ← beta = mixer parameter
rx(2*beta) q[1];
```

**Structural fingerprint:**
1. Alternating `rz(...)` layers (cost layer) and `rx(...)` layers (mixer layer)
2. The `rz` gates are flanked by `cx` gates (ZZ interaction pattern)
3. Multiple repetitions (p layers) of the same cost-mixer pattern

**Detection strategy (heuristic):**
- Look for repeating blocks of `cx ... rz(...) ... cx` followed by `rx(...)`
- This cost-mixer alternation is uniquely QAOA

**Confidence:** ⚠️ Medium. The `cx-rz-cx` + `rx` pattern is quite specific to QAOA.

---

## Option 2: Code Comment / Metadata Tag (Explicit Declaration)

The simplest approach. The user or a tutorial template includes a special comment in their code:

```python
# @algorithm: grover
# or
// Algorithm: Deutsch-Jozsa
```

Or: the **frontend sends an optional field** with the execution request:

```json
{
  "qasm_input": "...",
  "algorithm_hint": "grover"
}
```

The backend reads this tag and logs the corresponding activity type directly.

**Confidence:** ✅ Highest possible (user is explicitly declaring intent)  
**Reliability:** ⚠️ Depends on user discipline — users can cheat by adding the wrong tag. Fine for a gamified educational context.

---

## Option 3: Tutorial / Template Tracking (Context-Aware)

The frontend already has tutorial or example templates. When a user runs a circuit from a named template (e.g., "Grover's Search Tutorial"), the frontend can include the template's name or ID in the execution request. The backend maps template IDs → achievement activity types:

```python
TEMPLATE_TO_ACTIVITY = {
    "grover_tutorial": "algorithm_grover",
    "deutsch_tutorial": "algorithm_deutsch",
    "vqe_tutorial": "algorithm_vqe",
    ...
}
```

**Confidence:** ✅ Very High  
**Reliability:** ✅ No cheating possible since the template tag is server-resolved

---

## Option 4: Python Code Inspection (Hybrid Execution Route)

When users run Python code via `/api/hybrid/execute`, we can inspect the Python AST (Abstract Syntax Tree) for imports and function calls that are unique to each algorithm:

| Algorithm | Python Import / Function Call Signature |
|---|---|
| VQE | `from qiskit.algorithms import VQE`, `qml.VQECost`, `EstimatedExpValue` |
| QAOA | `from qiskit.algorithms import QAOA`, `qml.qaoa.cost`, `qml.qaoa.mixer` |
| Grover | `from qiskit.algorithms import Grover`, `cirq.GroverAlgorithm` |
| Shor | `from qiskit.algorithms import Shor`, `algorithms.Shor` |
| Deutsch-Jozsa | `from qiskit.algorithms import DeutschJozsa`, `deutsch_jozsa` |

**Implementation:**
```python
import ast
tree = ast.parse(user_code)
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        # Check for algorithm-specific imports
```

**Confidence:** ✅ High  
**Reliability:** ✅ Very reliable for Python code path

---

## Comparison & Recommendation

| Option | Confidence | Complexity | Cheat-proof | Works with QASM | Works with Python |
|---|---|---|---|---|---|
| 1 — QASM Pattern Matching | Medium | Medium | Mostly | ✅ | ✅ (after compile) |
| 2 — Comment / Metadata Tag | Exact | Low | ❌ No | ✅ | ✅ |
| 3 — Template Context | Exact | Low | ✅ Yes | ✅ | ✅ |
| 4 — Python AST Inspection | High | Medium | ✅ Yes | ❌ No | ✅ |

### Recommended: **Layered Approach**

Combine all options in a priority order:

```
1. Is this a template run? → Template tracking (highest confidence, no effort from user)
2. Is there an algorithm_hint field in the request? → Metadata tag
3. Is this a Python code run? → AST inspection
4. Fall through: → QASM pattern matching as best-effort heuristic
```

For **Entanglement Expert** and **Superposition Savant** specifically:
- Use QASM Pattern Matching only (Option 1) — these are structurally trivial to detect with 99%+ accuracy
- These are NOT named algorithms — they are just circuit properties (does the circuit contain `cx`? does it contain `h`?)

For **Deutsch, Grover, Shor, VQE, QAOA**:
- Start with template context (Option 3) — requires frontend to pass template ID
- Add Python AST inspection (Option 4) for the hybrid execution route
- Add QASM heuristics (Option 1) as fallback

---

## Implementation Plan (Priority Order)

### Phase 1: Implement immediately (trivial, high-confidence)
1. **Entanglement Expert**: In `simulator.py` after successful execution — scan QASM for `cx`, `cz`, `ccx`, `swap` gates → log `entangled_circuit`
2. **Superposition Savant**: Scan QASM for `h q[` → log `superposition_circuit`

### Phase 2: Short-term (1-2 days)
3. Add `algorithm_hint` optional field to `/api/simulator/execute-qsim` request schema
4. Backend maps `algorithm_hint` → the correct `algorithm_*` activity type
5. Frontend tutorial templates automatically populate the `algorithm_hint` field

### Phase 3: Medium-term (optional polish)
6. Add Python AST inspection in `/api/hybrid/execute` for VQE and QAOA Python library calls
7. Add QASM structural heuristics for Grover (CCX detection), Deutsch (H-Oracle-H), Shor (QFT pattern)

---

## Summary: Does Each Algorithm Have a Unique Circuit Diagram?

| Algorithm | Unique QASM Fingerprint? | Key Distinguishing Gates |
|---|---|---|
| Entanglement | ✅ Yes — very unique | `cx`, `cz` |
| Superposition | ✅ Yes — very unique | `h` |
| Deutsch-Jozsa | ✅ Yes — moderately unique | H-Oracle-H sandwich, ancilla X+H |
| Grover | ✅ Yes — fairly unique | `ccx` Toffoli + H-X diffusion layers |
| Shor | ✅ Yes — highly unique | QFT cascade (`cp(pi/N)`) + `swap` |
| VQE | ⚠️ Partially unique | Parameterized `ry(θ)` + entanglement layers |
| QAOA | ⚠️ Partially unique | `cx-rz-cx` (cost) + `rx` (mixer) alternation |

**Conclusion:** Yes, every algorithm has structurally unique circuit patterns that can be detected via QASM regex/heuristics. The detection confidence ranges from very high (entanglement, superposition, Shor's QFT) to medium (VQE, QAOA, which share parameterized gate patterns with other variational algorithms). For the QCanvas educational context, the combination of template-context tracking and QASM pattern matching is the most practical and reliable solution.
