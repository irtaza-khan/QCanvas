# Paper 5 – Cross-Framework Quantum Algorithm Benchmarking
## Step-by-Step Implementation Guide for QCanvas

> **Paper Title:** Cross-Framework Quantum Algorithm Benchmarking via Unified Compilation to OpenQASM 3.0  
> **Platform:** QCanvas  
> **Status:** Implementation Roadmap  
> **Target Venue:** IEEE QCE / ACM TQC  

---

## Overview

This guide lays out every concrete step needed to write and produce the results for Paper 5, using the QCanvas platform as the experimental engine. The paper's central claim is that QCanvas's unified AST-based compilation pipeline — which takes Qiskit, Cirq, and PennyLane code as input and generates a single OpenQASM 3.0 output — enables, for the first time, a *controlled and reproducible* cross-framework comparison of quantum algorithms.

**Quantum Volume (QV)** is added as a supplementary benchmarking dimension: for each algorithm and framework, we estimate the effective Quantum Volume achievable based on circuit depth and gate error assumptions, providing a hardware-readiness perspective on the compiled circuits.

---

## Phase 0 – Prerequisites & Environment Setup

### Step 0.1 – Confirm Core QCanvas Components Are Operational

Before collecting any data, verify that the three compilation pipelines work end-to-end.

```
QCanvas compilation chain for each framework:
  [Framework Source Code]
       ↓  (backend/app AST parsing via quantum_converters/parsers/*)
  [CircuitAST]
       ↓  (quantum_converters/converters/*_to_qasm.py → QASM3Builder)
  [OpenQASM 3.0 string]
       ↓  (quantum_simulator/qsim)
  [Measurement Results + Metrics]
```

Files to verify exist and are functional:
- `quantum_converters/parsers/qiskit_parser.py` – QiskitASTVisitor
- `quantum_converters/parsers/cirq_parser.py` – CirqASTVisitor
- `quantum_converters/parsers/pennylane_parser.py` – PennyLaneASTVisitor
- `quantum_converters/converters/qiskit_to_qasm.py` – QASM3Builder for Qiskit
- `quantum_converters/converters/cirq_to_qasm.py` – QASM3Builder for Cirq
- `quantum_converters/converters/pennylane_to_qasm.py` – QASM3Builder for PennyLane
- `quantum_simulator/qsim/` – QSim statevector simulation backend

**Action:** Run the existing test suite to confirm baseline correctness:
```bash
cd d:\University\Uni\FYP\QCanvas
python run_tests.py
```

### Step 0.2 – Set Up the Benchmarking Python Environment

Install all required scientific libraries for data collection and analysis:

```bash
pip install qiskit cirq pennylane
pip install numpy scipy pandas matplotlib seaborn
pip install psutil memory_profiler   # for CPU/RAM metrics
pip install statsmodels              # for chi-squared and KL divergence
pip install jupyter                  # for notebook-based analysis
```

Confirm all imports work:
```bash
python -c "import qiskit, cirq, pennylane, numpy, scipy, pandas, matplotlib, psutil; print('All OK')"
```

### Step 0.3 – Create the Benchmarking Directory Structure

Create a dedicated directory for all benchmark scripts, raw data, and figures:

```
QCanvas/
└── benchmarks/
    ├── algorithms/           # Step 1: idiomatic implementations per framework
    │   ├── qiskit/
    │   ├── cirq/
    │   └── pennylane/
    ├── qasm_outputs/         # Step 2: generated QASM 3.0 files (one per algo+framework)
    ├── metrics/              # Step 3: CSV files with structural and simulation metrics
    ├── results/              # Step 4: processed results tables and figures
    │   ├── structural/
    │   ├── simulation/
    │   └── scaling/
    ├── scripts/              # Step 5: automation and runner scripts
    └── notebooks/            # Step 6: Jupyter notebooks for analysis and paper figures
```

---

## Phase 1 – Algorithm Implementation (Idiomatic Versions)

### Step 1.1 – Understand "Idiomatic" Requirements

Each algorithm must be written the way an experienced user of that framework would naturally write it:

| Framework | Idiom Style |
|-----------|-------------|
| **Qiskit** | `QuantumCircuit` class, `.h()`, `.cx()`, `.barrier()`, `Transpiler` if needed, measurement at end |
| **Cirq** | `cirq.Circuit`, `cirq.H`, `cirq.CNOT`, moment-by-moment construction, `cirq.measure` |
| **PennyLane** | `@qml.qnode(dev)` decorator, `qml.Hadamard`, `qml.CNOT`, return `qml.probs()` or `qml.sample()` |

**Do not** translate one framework's code mechanically into another. This would artificially equalize results.

### Step 1.2 – Implement Algorithm Suite (12+ Algorithms)

For each algorithm below, create 3 files: one per framework.  
Example filename pattern: `benchmarks/algorithms/qiskit/bell_state.py`

---

#### Algorithm 1: Bell State (2 qubits)

**Purpose:** Simplest possible circuit. Sanity check. Expected output: `|00⟩: 50%, |11⟩: 50%`.

**Qiskit version:**
```python
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def bell_state_qiskit():
    qr = QuantumRegister(2, 'q')
    cr = ClassicalRegister(2, 'c')
    qc = QuantumCircuit(qr, cr)
    qc.h(qr[0])
    qc.cx(qr[0], qr[1])
    qc.measure(qr, cr)
    return qc
```

**Cirq version:**
```python
import cirq

def bell_state_cirq():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit([
        cirq.H(q0),
        cirq.CNOT(q0, q1),
        cirq.measure(q0, q1, key='result')
    ])
    return circuit
```

**PennyLane version:**
```python
import pennylane as qml

dev = qml.device('default.qubit', wires=2)

@qml.qnode(dev)
def bell_state_pennylane():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.probs(wires=[0, 1])
```

---

#### Algorithm 2: GHZ State (variable: 3–8 qubits)

**Purpose:** Entanglement scaling test. Used for scaling analysis (RQ4).

Write version for n qubits. In Qiskit:
```python
def ghz_state_qiskit(n):
    qc = QuantumCircuit(n, n)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    qc.measure_all()
    return qc
```
Write equivalent versions in Cirq and PennyLane for the same `n`.

---

#### Algorithm 3: Quantum Teleportation (3 qubits)

**Purpose:** Demonstrates multi-step protocol. Tests mid-circuit measurement handling differences.

Implement Alice-Bob teleportation protocol. Key structural differences to watch:
- Qiskit: can use `c_if` for classically-controlled gates
- Cirq: uses `ClassicallyControlledOperation`
- PennyLane: mid-circuit measurements via `qml.measure` (newer API)

---

#### Algorithm 4: Deutsch–Jozsa (variable: 3–8 qubits)

**Purpose:** Oracle-based. Tests how each framework encodes constant vs. balanced oracles.

Implement with a **constant oracle** and a **balanced oracle** separately. Note: oracle encoding is the main source of gate count divergence across frameworks.

---

#### Algorithm 5: Bernstein–Vazirani (variable: 3–8 qubits)

**Purpose:** Hidden string oracle. Simple oracle structure makes gate count differences visible.

Use a fixed secret string (e.g., `s = "101"` for 3-qubit version) for reproducibility.

---

#### Algorithm 6: Grover's Algorithm (variable: 2–6 qubits)

**Purpose:** Main case study. Tests oracle + diffusion operator decomposition.

Implement for a **specific marked state** (e.g., `|11⟩` for 2 qubits, `|101⟩` for 3 qubits).

**Critical:** The diffusion operator (`2|s⟩⟨s| - I`) can be decomposed differently:
- Qiskit typically uses `H⊗n → X⊗n → multi-controlled-Z → X⊗n → H⊗n`
- Cirq may use custom gate construction
- PennyLane provides `qml.GroverOperator` template (may have different gate count)

This is the algorithm with the **highest expected gate-count divergence**.

---

#### Algorithm 7: Quantum Random Number Generator / QRNG (variable: 4–8 qubits)

**Purpose:** Purely Hadamard-based. Minimal oracle. Used to isolate pure gate-translation overhead.

Simple: apply H to all qubits, measure. Expected output: uniform distribution over all 2^n states.

---

#### Algorithm 8: VQE – Variational Quantum Eigensolver (variable: 2–6 qubits)

**Purpose:** Variational algorithm. Tests ansatz construction and parameter handling.

Use **same Hamiltonian** (e.g., H₂ molecule Hamiltonian or simple Z⊗Z + X⊗I) across all frameworks.

Key differences in ansatz:
- Qiskit: `EfficientSU2` ansatz from `qiskit.circuit.library`
- Cirq: Manual CNOT + Rz rotation layers
- PennyLane: `qml.StronglyEntanglingLayers`

**Important:** Fix the ansatz parameters to the same values (e.g., all zeros or a previously optimized set) to make QASM output deterministic and comparable.

---

#### Algorithm 9: QAOA – Quantum Approximate Optimization Algorithm (variable: 2–6 qubits)

**Purpose:** Combinatorial optimization. Tests cost Hamiltonian encoding.

Use **MaxCut on a simple graph** (e.g., 3-node triangle graph). Fix `p=1` layer. Fix gamma and beta parameters across all frameworks.

---

#### Algorithm 10: QML XOR Classifier (2–4 qubits)

**Purpose:** Quantum ML. Tests data encoding circuits and variational layers.

Implement angle encoding of classical data (XOR inputs) + variational layer. Compare how each framework encodes classical data into quantum states.

---

#### Algorithm 11: Bit-Flip Error Correcting Code (3 qubits → 9 qubits)

**Purpose:** Error correction circuits. Tests syndrome measurement and ancilla qubit handling.

Implement standard 3-qubit bit-flip code (encode → add noise → decode → measure syndrome).

---

#### Algorithm 12: Phase-Flip Error Correcting Code (3 qubits → 9 qubits)

**Purpose:** Complementary to bit-flip. Tests Hadamard basis error correction encoding.

---

### Step 1.3 – Cross-Verify Algorithm Correctness Before Benchmarking

Before running the full benchmark pipeline, manually verify each implementation is semantically correct:

1. Run each framework's native simulator (not QCanvas yet)
2. Check measurement distributions match theoretical expectations
3. Document any subtle differences (e.g., qubit ordering conventions — Qiskit uses little-endian bitstring ordering, Cirq uses natural order)

**Qubit ordering note:** Qiskit outputs bitstrings in **reversed order** relative to Cirq and PennyLane. All post-processing must account for this. Create a normalisation function:

```python
def normalize_bitstring(bitstring: str, source_framework: str) -> str:
    """Reverses bitstring if framework is Qiskit (little-endian convention)."""
    if source_framework == 'qiskit':
        return bitstring[::-1]
    return bitstring
```

---

## Phase 2 – QCanvas Compilation Pipeline

### Step 2.1 – Build the Automated Compilation Runner

Create `benchmarks/scripts/compile_all.py`. This script:

1. For each (algorithm, framework) pair:
   - Loads the algorithm function from `benchmarks/algorithms/<framework>/<algo>.py`
   - Calls the appropriate QCanvas parser (`qiskit_parser.py`, `cirq_parser.py`, `pennylane_parser.py`)
   - Builds the `CircuitAST`
   - Calls the corresponding QASM3Builder (`qiskit_to_qasm.py`, etc.)
   - Saves the output QASM string to `benchmarks/qasm_outputs/<algo>_<framework>.qasm`

```python
# benchmarks/scripts/compile_all.py (pseudocode structure)
import time, os
from quantum_converters.parsers.qiskit_parser import QiskitASTVisitor
from quantum_converters.parsers.cirq_parser import CirqASTVisitor
from quantum_converters.parsers.pennylane_parser import PennyLaneASTVisitor
from quantum_converters.converters.qiskit_to_qasm import qiskit_to_qasm3
from quantum_converters.converters.cirq_to_qasm import cirq_to_qasm3
from quantum_converters.converters.pennylane_to_qasm import pennylane_to_qasm3

COMPILE_REGISTRY = {
    'qiskit': (get_qiskit_circuit_fn, qiskit_to_qasm3),
    'cirq':   (get_cirq_circuit_fn,   cirq_to_qasm3),
    'pennylane': (get_pennylane_circuit_fn, pennylane_to_qasm3),
}

results = []
for algo_name in ALGORITHM_LIST:
    for framework, (circuit_fn, converter_fn) in COMPILE_REGISTRY.items():
        circuit = circuit_fn(algo_name)
        start_t = time.perf_counter()
        qasm_str = converter_fn(circuit)
        end_t = time.perf_counter()
        
        compilation_time_ms = (end_t - start_t) * 1000
        
        # Save QASM
        with open(f"qasm_outputs/{algo_name}_{framework}.qasm", "w") as f:
            f.write(qasm_str)
        
        results.append({
            'algorithm': algo_name,
            'framework': framework,
            'compilation_time_ms': compilation_time_ms,
            'qasm_path': f"qasm_outputs/{algo_name}_{framework}.qasm"
        })
```

**Run this script 10 times** and record mean ± std of `compilation_time_ms` for each pair.

### Step 2.2 – Static QASM Analysis

Create `benchmarks/scripts/analyze_qasm.py`. This script parses each `.qasm` file and extracts structural metrics **without running any simulation**.

For each `.qasm` file, extract:

```python
import re

def analyze_qasm_file(qasm_path: str) -> dict:
    with open(qasm_path) as f:
        content = f.read()
    
    # Gate count: count gate invocation lines (excluding declarations and comments)
    gate_lines = [l.strip() for l in content.split('\n') 
                  if l.strip() and not l.strip().startswith(('//', 'OPENQASM', 'include', 'qubit', 'bit', 'gate ', '#'))]
    
    # Gate type breakdown
    gate_types = {}
    for line in gate_lines:
        gate_name = line.split('(')[0].split(' ')[0]  # first token
        gate_types[gate_name] = gate_types.get(gate_name, 0) + 1
    
    total_gates = sum(gate_types.values())
    
    # Circuit depth: requires topological sort (implement or use a QASM parser library)
    # Use simple approximation: max number of non-parallel gates on any qubit
    depth = compute_circuit_depth_from_qasm(content)  # implement this function
    
    # Multi-qubit gates: CNOT, CX, CCX, CZ, SWAP, etc.
    multi_qubit_count = sum(v for k, v in gate_types.items() 
                            if k.lower() in ['cx', 'cnot', 'cz', 'ccx', 'swap', 'ctrl'])
    
    # Measurements
    measurement_count = gate_types.get('measure', 0)
    
    # Modifier usage (QASM 3.0 specific)
    ctrl_modifier_count = len(re.findall(r'ctrl\s*@', content))
    inv_modifier_count = len(re.findall(r'inv\s*@', content))
    pow_modifier_count = len(re.findall(r'pow\s*\(', content))
    
    return {
        'total_gates': total_gates,
        'gate_types': gate_types,
        'circuit_depth': depth,
        'multi_qubit_gates': multi_qubit_count,
        'multi_qubit_ratio': multi_qubit_count / total_gates if total_gates > 0 else 0,
        'measurement_count': measurement_count,
        'ctrl_modifier_count': ctrl_modifier_count,
        'inv_modifier_count': inv_modifier_count,
        'pow_modifier_count': pow_modifier_count,
    }
```

Save all metrics to `benchmarks/metrics/structural_metrics.csv`.

**Expected CSV schema:**
```
algorithm, framework, n_qubits, total_gates, circuit_depth, multi_qubit_gates,
multi_qubit_ratio, measurement_count, ctrl_count, inv_count, pow_count,
gate_H, gate_CX, gate_RZ, gate_RX, gate_RY, gate_X, gate_Z, gate_S, gate_T
```

---

## Phase 3 – Simulation & Dynamic Metrics Collection

### Step 3.1 – QSim Simulation Runner

Create `benchmarks/scripts/simulate_all.py`. For each `(algorithm, framework, shot_count)` triple:

1. Load the pre-generated QASM file from `qasm_outputs/`
2. Submit to QSim backend (Cirq statevector simulator)
3. Record measurement distribution and performance metrics

```python
import psutil, time, tracemalloc

def run_simulation_trial(qasm_path: str, shots: int) -> dict:
    with open(qasm_path) as f:
        qasm_str = f.read()
    
    # Memory tracking
    tracemalloc.start()
    
    # CPU baseline
    cpu_before = psutil.cpu_percent(interval=None)
    
    start_t = time.perf_counter()
    
    # Run QSim backend
    from quantum_simulator.qsim import QSimBackend
    backend = QSimBackend()
    result = backend.run_qasm(qasm_str, shots=shots)
    
    end_t = time.perf_counter()
    
    _, peak_memory_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    cpu_after = psutil.cpu_percent(interval=None)
    
    return {
        'simulation_time_ms': (end_t - start_t) * 1000,
        'peak_memory_mb': peak_memory_bytes / (1024 * 1024),
        'cpu_utilization_pct': (cpu_before + cpu_after) / 2,  # approximate
        'measurement_distribution': result.counts,  # dict: bitstring → count
        'fidelity': result.fidelity if hasattr(result, 'fidelity') else None,
    }
```

**Repeat each trial 10 times.** Collect mean and standard deviation.

**Shot counts to use:** 1024, 4096, 8192 (as specified in the paper).

**Save results to:** `benchmarks/metrics/simulation_metrics.csv`

**Expected CSV schema:**
```
algorithm, framework, n_qubits, shots, trial,
sim_time_ms, peak_memory_mb, cpu_pct,
dist_json_path, fidelity
```

### Step 3.2 – Quantum Volume Estimation per Circuit

**Quantum Volume (QV)** is the key additional benchmarking stat this guide adds beyond the original paper outline.

**Definition:** QV = 2^n where n is the largest square circuit (n_qubits × n_depth) that can be executed with ≥ 2/3 heavy output probability. For simulation purposes (no noise), we compute the **circuit-structure-implied QV** as a hardware-readiness metric.

**How to compute circuit-structural QV estimate:**

For each compiled QASM circuit, calculate the effective QV based on circuit properties:

```python
import numpy as np

def estimate_quantum_volume(
    n_qubits: int,
    circuit_depth: int,
    gate_error_rate: float = 0.001,    # typical superconducting qubit 2-qubit gate error
    t1_time_us: float = 100.0,         # T1 relaxation time (μs)
    gate_time_ns: float = 50.0         # 2-qubit gate time (ns)
) -> dict:
    """
    Estimates the effective Quantum Volume achievable given circuit structure.
    
    QV = 2^m where m is the largest n such that a square circuit (n x n) has
    expected fidelity > 0.5 (i.e., heavy output probability > 2/3).
    
    For our benchmarking purposes, we compute:
      1. Circuit fidelity estimate under depolarizing noise
      2. The equivalent QV-scale (log2 of effective fidelity area)
    """
    # Number of two-qubit gate layers ≈ circuit_depth / 2 (rough estimate)
    n_2q_layers = circuit_depth // 2
    
    # Fidelity decay due to gate errors (depolarizing approximation)
    # Each 2-qubit gate introduces (1 - epsilon) fidelity factor
    gate_fidelity = (1 - gate_error_rate) ** (n_2q_layers * n_qubits)
    
    # Fidelity decay due to T1 decoherence
    total_time_ns = circuit_depth * gate_time_ns
    t1_fidelity = np.exp(-total_time_ns / (t1_time_us * 1000))
    
    # Combined estimated fidelity
    estimated_fidelity = gate_fidelity * t1_fidelity
    
    # Effective QV: largest m such that m x m circuit has fidelity > 0.5
    # Solve: (1 - eps)^(m*m/2) * exp(-m*gate_time/(t1)) > 0.5
    # Numerically find m:
    m = 1
    while True:
        f_gate = (1 - gate_error_rate) ** (m * m // 2)
        f_t1 = np.exp(-(m * gate_time_ns) / (t1_time_us * 1000))
        if f_gate * f_t1 < 0.5 or m > 30:
            break
        m += 1
    effective_qv = 2 ** (m - 1)
    
    return {
        'n_qubits': n_qubits,
        'circuit_depth': circuit_depth,
        'estimated_fidelity': estimated_fidelity,
        'effective_qv_log2': m - 1,
        'effective_qv': effective_qv,
        'gate_fidelity_component': gate_fidelity,
        't1_fidelity_component': t1_fidelity,
    }
```

**Run this for every (algorithm, framework) pair.** This produces a QV estimate for each compiled circuit, allowing comparison like:

> *"Grover's (4 qubits) compiled from Qiskit generates a circuit with effective QV = 32, while PennyLane generates a circuit with effective QV = 16, because PennyLane's decomposition is 23% deeper."*

**Add QV columns to `structural_metrics.csv`:**
```
... , estimated_fidelity, effective_qv_log2, effective_qv
```

---

## Phase 4 – Statistical Analysis

### Step 4.1 – Distribution Equivalence Testing

For each algorithm, compare the measurement distributions from all three frameworks.

**Test 1: Chi-Squared Goodness-of-Fit**

For each framework's output, compare against the **theoretical ideal distribution**:

```python
from scipy.stats import chisquare
import numpy as np

def chi_squared_test(
    observed_counts: dict,   # e.g., {'00': 512, '11': 512}
    expected_probs: dict,    # e.g., {'00': 0.5, '11': 0.5}
    shots: int
) -> dict:
    states = sorted(expected_probs.keys())
    observed = np.array([observed_counts.get(s, 0) for s in states])
    expected = np.array([expected_probs[s] * shots for s in states])
    
    chi2_stat, p_value = chisquare(f_obs=observed, f_exp=expected)
    return {
        'chi2_statistic': chi2_stat,
        'p_value': p_value,
        'significant_divergence': p_value < 0.05
    }
```

**Test 2: Jensen-Shannon Divergence (Pairwise)**

```python
from scipy.spatial.distance import jensenshannon
import numpy as np

def js_divergence(dist_a: dict, dist_b: dict, all_states: list) -> float:
    """
    Compute Jensen-Shannon divergence between two measurement distributions.
    JSD < 0.01 → effectively identical
    JSD > 0.05 → significant divergence (investigate)
    """
    p = np.array([dist_a.get(s, 0) for s in all_states], dtype=float)
    q = np.array([dist_b.get(s, 0) for s in all_states], dtype=float)
    
    # Normalize to probabilities
    p /= p.sum()
    q /= q.sum()
    
    return float(jensenshannon(p, q))

def pairwise_jsd(distributions: dict) -> dict:
    """distributions = {'qiskit': {...}, 'cirq': {...}, 'pennylane': {...}}"""
    frameworks = list(distributions.keys())
    all_states = sorted(set().union(*[d.keys() for d in distributions.values()]))
    
    result = {}
    for i in range(len(frameworks)):
        for j in range(i + 1, len(frameworks)):
            fa, fb = frameworks[i], frameworks[j]
            jsd = js_divergence(distributions[fa], distributions[fb], all_states)
            key = f"{fa}_vs_{fb}"
            result[key] = {
                'jsd': jsd,
                'equivalent': jsd < 0.01,
                'divergent': jsd > 0.05
            }
    return result
```

**Aggregate per algorithm across all 10 trials**, reporting mean JSD ± std.

### Step 4.2 – Structural Comparison Analysis

For each algorithm, produce a **comparison table** comparing all three frameworks on every structural metric:

```
ALGORITHM: Grover's Algorithm (4 qubits)
┌──────────────┬─────────┬───────┬───────────────┐
│ Metric       │ Qiskit  │ Cirq  │ PennyLane     │
├──────────────┼─────────┼───────┼───────────────┤
│ Total Gates  │  42     │  38   │  51           │
│ Circuit Depth│  18     │  16   │  22           │
│ 2-Qubit Gates│  14     │  12   │  17           │
│ Multi-Q Ratio│  33%    │  32%  │  33%          │
│ Estimated QV │  64     │  128  │  32           │
│ QV Log₂      │  6      │  7    │  5            │
└──────────────┴─────────┴───────┴───────────────┘
```

Automate table generation in `benchmarks/scripts/generate_tables.py`.

### Step 4.3 – Scaling Analysis

For algorithms with variable qubit counts (GHZ, Deutsch-Jozsa, Grover's, QRNG), generate scaling plots:

```python
# For each variable-qubit algorithm:
# X-axis: n_qubits (e.g., 2, 3, 4, 5, 6)
# Y-axis: total_gates, circuit_depth, compilation_time_ms, effective_qv

# Fit trend lines to identify:
# - Constant offset (additive framework overhead)
# - Linear scaling (proportional)
# - Super-linear/exponential (diverging at scale)

from numpy.polynomial import polynomial as P
import numpy as np

def fit_scaling(qubits: list, values: list):
    coeffs_linear = np.polyfit(qubits, values, 1)    # linear fit
    coeffs_quad   = np.polyfit(qubits, values, 2)    # quadratic fit
    
    # Choose better fit by R²
    ...
    return {'slope': coeffs_linear[0], 'intercept': coeffs_linear[1]}
```

This answers **RQ4 (Complexity Scaling)**.

---

## Phase 5 – Case Study Deep Dives

### Step 5.1 – Case Study 1: Bell State

Write a narrative section for the paper with:

1. **Three-column code listing:** Qiskit, Cirq, PennyLane source code side-by-side
2. **Three QASM 3.0 listings:** The actual generated QASM output from QCanvas for each
3. **Key observation table:** Point out exactly which QASM lines differ:
   - Does Qiskit generate `cx q[0], q[1];` while Cirq generates `ctrl @ x q[1];` ?
   - Are qubit register declarations different?
   - Does PennyLane add any extra ancilla gates?
4. **Measurement histogram comparison:** Bar chart showing `|00⟩ ~50%, |11⟩ ~50%` for all three (they should be identical)
5. **JSD values:** All should be < 0.001
6. **QV comparison:** Likely identical since this is a minimal 2-gate circuit

### Step 5.2 – Case Study 2: Grover's Algorithm

1. **Oracle encoding comparison:**
   - Show how the phase oracle for `|11⟩` is expressed in each framework
   - Count how many gates differ in the oracle section specifically
2. **Diffusion operator comparison:**
   - Show the QASM for the reflection operator `2|s⟩⟨s| - I` in each framework
   - Identify which framework produces the most efficient decomposition
3. **4-qubit scaling results table:**
   - Report gate count, depth, QV estimate for n = 2, 3, 4, 5
   - Plot showing how gate count grows with n across frameworks
4. **Measurement distribution at each qubit size:**
   - For a 2-qubit marked state `|11⟩`: should show ~80% probability on `|11⟩`
   - Check all frameworks give the same marked state boost

### Step 5.3 – Case Study 3: VQE / QAOA

1. **Ansatz structure comparison:**
   - Show one layer of EfficientSU2 (Qiskit) vs. manual Rz+CNOT (Cirq) vs. StronglyEntanglingLayers (PennyLane)
   - Count gates per layer for each
2. **Parameter handling in QASM:**
   - Show how `theta[0]`, `theta[1]` parameters appear in the generated QASM 3.0
   - Examine if any framework introduces extra parameter binding gates
3. **Distribution comparison at zero-parameter initialization:**
   - All three should produce similar near-uniform output since parameters are zero
   - Report JSD values (expect small but non-zero due to ansatz structure differences)
4. **Discussion of implications:**
   - Which framework's VQE QASM is most hardware-efficient (lowest effective QV requirement)?

### Step 5.4 – Case Study 4: QML XOR Classifier

1. **Data encoding comparison:**
   - Angle encoding in Qiskit (RX gates)
   - Angle encoding in Cirq (rx gates)
   - Angle encoding in PennyLane (qml.AngleEmbedding)
   - Was any extra layer added by any framework for encoding?
2. **Variational layer comparison:**
   - Count of parametric gates per framework for one variational layer
3. **Discuss design philosophy:**
   - PennyLane has `qml.AngleEmbedding` as a built-in; does this produce fewer or more gates?
   - Which framework's QML circuits are most naturally expressed at the QASM level?

---

## Phase 6 – Figure Generation

Create all figures in `benchmarks/notebooks/paper5_figures.ipynb`.

### Step 6.1 – Figure List

| Figure | Content | Type |
|--------|---------|------|
| Fig. 1 | QCanvas compilation pipeline diagram | Architecture diagram |
| Fig. 2 | Gate count per algorithm per framework (all 12 algorithms) | Grouped bar chart |
| Fig. 3 | Circuit depth per algorithm per framework | Grouped bar chart |
| Fig. 4 | Gate composition breakdown (H, CNOT, Rz, etc.) by framework | Stacked bar chart |
| Fig. 5 | Gate count scaling with qubit count (GHZ, Grover's, QRNG) | Multi-line plot |
| Fig. 6 | Compilation time per framework (mean ± std over 10 runs) | Box plot |
| Fig. 7 | Simulation time per framework (should be approximately equal) | Box plot |
| Fig. 8 | Memory usage per algorithm (mean ± std) | Bar chart |
| Fig. 9 | Pairwise JSD heatmap across all algorithms | Heatmap |
| Fig. 10 | Chi-squared p-values across all algorithms | Heatmap / Table |
| **Fig. 11** | **Quantum Volume estimate per algorithm per framework** | **Grouped bar chart** |
| **Fig. 12** | **QV vs. Circuit Depth scatter plot (framework coloring)** | **Scatter plot** |
| Fig. 13 | Bell state measurement histograms (3 frameworks) | Side-by-side histograms |
| Fig. 14 | Grover's gate count scaling plot (2–5 qubits, 3 frameworks) | Multi-line plot |

### Step 6.2 – Figure Style Requirements

All figures must use consistent styling for publication quality:

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Color palette (framework-specific, consistent throughout paper)
FRAMEWORK_COLORS = {
    'qiskit':    '#6929C4',  # IBM purple (Qiskit brand color)
    'cirq':      '#009D9A',  # Google teal (Cirq / Google Quantum)
    'pennylane': '#FF7F50',  # PennyLane orange (Xanadu brand)
}

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'figure.dpi': 300,       # publication quality
    'figure.figsize': (8, 5),
    'axes.spines.top': False,
    'axes.spines.right': False,
})
```

---

## Phase 7 – Results Tables for Paper Sections

### Step 7.1 – Main Results Table (Section 4)

Create a comprehensive summary table for the paper (to be placed in Section 4):

```
Table 1: Structural Metrics Summary — Mean values across all 12 algorithms

Framework  | Avg Gate Count | Avg Depth | Avg Multi-Q Ratio | Avg Compile Time | Avg QV Est.
-----------|---------------|-----------|-------------------|-----------------|------------
Qiskit     |     XX ± XX   |  XX ± XX  |     XX% ± XX%     |   XX ± XX ms    |  2^XX ± XX
Cirq       |     XX ± XX   |  XX ± XX  |     XX% ± XX%     |   XX ± XX ms    |  2^XX ± XX
PennyLane  |     XX ± XX   |  XX ± XX  |     XX% ± XX%     |   XX ± XX ms    |  2^XX ± XX
```

### Step 7.2 – Equivalence Testing Table (Section 4)

```
Table 2: JSD and Chi-Squared Results — Statistical Equivalence of Simulation Outputs

Algorithm          | JSD (Qiskit vs Cirq) | JSD (Qiskit vs PL) | JSD (Cirq vs PL) | All Equivalent?
-------------------|---------------------|-------------------|-------------------|-----------------
Bell State         |       0.000X        |       0.000X      |       0.000X      |       ✓
GHZ State          |       0.000X        |       0.000X      |       0.000X      |       ✓
Grover's (2q)      |       0.000X        |       0.000X      |       0.000X      |       ✓
...
```

### Step 7.3 – Quantum Volume Comparison Table

```
Table 3: Estimated Quantum Volume by Algorithm and Framework
(Assumes: 2-qubit gate error = 0.001, T1 = 100μs, gate time = 50ns)

Algorithm          | Qubits | Qiskit QV | Cirq QV | PennyLane QV | Winner
-------------------|--------|-----------|---------|--------------|--------
Bell State         |   2    |   2^10    |  2^10   |    2^10      |  Tie
GHZ (5q)           |   5    |   2^6     |  2^7    |    2^5       |  Cirq
Grover's (4q)      |   4    |   2^6     |  2^7    |    2^5       |  Cirq
VQE (4q, 1-layer)  |   4    |   2^5     |  2^5    |    2^4       |  Tie
...
```

---

## Phase 8 – Paper Writing (Section-by-Section)

### Step 8.1 – Section 1: Introduction (1.5 pages)

**Write in order:**
1. Opening paragraph: The growing fragmentation of quantum software frameworks
2. The "hidden variable" problem: Framework choice silently shapes results
3. Research gap: No systematic cross-framework comparison at the QASM level
4. QCanvas as the enabling platform: Unique AST-based compilation
5. List of contributions (points 1–6 from paper outline)
6. Paper structure overview

### Step 8.2 – Section 2: Background (2 pages)

**Sub-sections:**
1. **2.1 Quantum Frameworks Overview:** Qiskit (IBM), Cirq (Google), PennyLane (Xanadu) — key design philosophies, gate sets, and conventions
2. **2.2 OpenQASM 3.0:** Why it's the right neutral IR — gate modifiers, parameterized circuits, classical control
3. **2.3 QCanvas Architecture:** AST-based compilation pipeline — describe visitors, QASM3Builder, QSim backend
4. **2.4 Quantum Volume:** Definition, formula, and why it's used here as an additional benchmark

### Step 8.3 – Section 3: Methodology (2.5 pages)

Cover all points from Phase 1–4 of this guide, including:
- Algorithm selection rationale and table (12 algorithms × 3 frameworks = 36 circuits)
- Experimental pipeline diagram (Fig. 1)
- Controlled variable list
- All metrics with formulas
- Statistical tests (JSD, Chi-squared) with thresholds
- Quantum Volume estimation method and assumptions

### Step 8.4 – Section 4: Results (3 pages)

**Structure:**
1. **4.1 Structural Divergence (RQ1):** Main gate count/depth table + bar charts (Figs. 2–4)
2. **4.2 Simulation Equivalence (RQ2):** JSD table + heatmap (Figs. 9–10). Key finding: all standard algorithms produce equivalent distributions
3. **4.3 Performance Variation (RQ3):** Compilation time and simulation time box plots (Figs. 6–8). Key finding: simulation time is framework-independent
4. **4.4 Complexity Scaling (RQ4):** Scaling plots (Fig. 5). Identify linear vs. constant offsets
5. **4.5 Quantum Volume Analysis:** QV table and plots (Figs. 11–12). Key finding: deeper circuits from verbose frameworks lose QV headroom faster

### Step 8.5 – Section 5: Case Studies (2.5 pages)

Four detailed case studies as described in Phase 5. Each includes:
- Source code (3-framework comparison)
- QASM output (3-framework comparison)
- Structural metrics table
- Statistical equivalence result
- QV comparison
- Narrative analysis

### Step 8.6 – Section 6: Discussion (1.5 pages)

Cover three stakeholder groups:
1. **Researchers:** Report framework + version; publish QASM artifacts alongside papers
2. **Framework developers:** Standardize decompositions; native QASM 3.0 export matters
3. **Educators:** Use cross-framework comparison as a teaching paradigm

**Limitations subsection:** Simulation only; idiomatic subjectivity; AST coverage limits; shot noise

### Step 8.7 – Section 7: Related Work (1 page)

Cite and differentiate from:
- QASMBench (Li et al., 2022)
- SupermarQ (Tomesh et al., 2022)
- MQTBench (Quetschlich et al., 2023)
- LaRose (2019) framework survey
- Fingerhuth et al. (2018) comparison
- IBM QV paper (Cross et al., 2019) — for QV methodology

### Step 8.8 – Section 8: Conclusion (0.5 pages)

Summarize the three main contributions:
1. The benchmarking methodology (QCanvas + QASM 3.0 as the unified layer)
2. Quantitative evidence of structural divergence (with QV implications)
3. Statistical proof of simulation equivalence

**Future work:** Hardware benchmarking on real QPUs; adding more frameworks (Amazon Braket, Q#); optimizing QASM before simulation (gate-level optimization pass)

---

## Phase 9 – Validation Checklist

Before submitting, verify each of the following:

### Correctness Checks
- [ ] All 36 QASM files (12 algorithms × 3 frameworks) are generated and syntactically valid
- [ ] All QASM files are OPENQASM 3.0 (not 2.0 — check header `OPENQASM 3.0;`)
- [ ] Bell state measurement histogram shows ≈50/50 for all three frameworks (simulated)
- [ ] Grover's algorithm shows correct marked state amplification for all frameworks
- [ ] VQE energy expectation converges similarly across frameworks at same parameters

### Statistical Checks
- [ ] All JSD values for standard algorithms (Bell, GHZ, Teleportation) are < 0.01
- [ ] chi-squared p-values > 0.05 for all standard algorithms (no significant divergence)
- [ ] Any JSD > 0.05 outlier has been investigated and explained in the paper

### QV Checks
- [ ] QV estimates are computed with stated assumptions (documented in paper)
- [ ] QV table shows intuitive ordering (deeper circuits → lower QV)
- [ ] QV comparison is presented as supplementary/estimate (not as a definitive hardware measurement)

### Reproducibility Checks
- [ ] All random seeds are fixed (`np.random.seed(42)`, `cirq.ops.random_unitary(seed=42)`, etc.)
- [ ] All benchmark scripts are committed to the repo under `benchmarks/`
- [ ] All generated QASM files are committed for artifact archiving
- [ ] Machine specs are documented (CPU, RAM, OS, Python version, all framework versions)

---

## Appendix A – Expected Hypotheses Summary

| Hypothesis | Expected Finding |
|------------|-----------------|
| H1: Gate count varies 5–20% across frameworks | Verified by structural metrics (RQ1) |
| H2: Distributions are statistically equivalent for standard algorithms | Verified by JSD < 0.01 for Bell, GHZ, etc. (RQ2) |
| H3: Compilation time differs across frameworks | Cirq fastest, PennyLane slowest (RQ3) |
| H4: Simulation time is framework-independent | Verified: all QASM runs on same QSim backend (RQ3) |
| H5: Scaling behavior similar, constant gate overhead varies | Verified by scaling plots (RQ4) |
| H6 (NEW): Circuits with more gates = lower effective QV estimate | Verified by QV table (added contribution) |

---

## Appendix B – Framework Version Pinning

For full reproducibility, pin and document exact versions in the paper:

```
qiskit==1.x.x
cirq==1.x.x  
pennylane==0.3x.x
numpy==1.x.x
scipy==1.x.x
python==3.10.x
QCanvas==<git commit hash>
```

---

## Appendix C – Related QCanvas Files

| What | Where in QCanvas |
|------|-----------------|
| Qiskit parser | `quantum_converters/parsers/qiskit_parser.py` |
| Cirq parser | `quantum_converters/parsers/cirq_parser.py` |
| PennyLane parser | `quantum_converters/parsers/pennylane_parser.py` |
| Qiskit→QASM converter | `quantum_converters/converters/qiskit_to_qasm.py` |
| Cirq→QASM converter | `quantum_converters/converters/cirq_to_qasm.py` |
| PennyLane→QASM converter | `quantum_converters/converters/pennylane_to_qasm.py` |
| QSim simulation backend | `quantum_simulator/qsim/` |
| Existing Qiskit examples | `examples/qiskit_examples/` |
| Existing Cirq examples | `examples/cirq_examples/` |
| Existing PennyLane examples | `examples/pennylane_examples/` |

---

*Last updated: March 2026 | QCanvas Paper 5 Implementation Guide*
