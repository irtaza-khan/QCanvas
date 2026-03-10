## Paper 6 – Towards Reproducible Quantum Computing Research: A Standardized Compilation and Artifact Framework Using OpenQASM 3.0

### 1. Problem and Motivation

- **Reproducibility crisis in quantum computing**: Quantum computing research papers frequently report simulation or hardware results without providing portable, executable artifacts. Replicating published results often requires:
  - The exact same framework version (Qiskit 0.x, Cirq 1.x, etc.).
  - Undocumented configuration choices (transpiler settings, noise models, shot counts).
  - Manual reimplementation when the original code targets a different framework than the reader uses.
- **Framework lock‑in hinders verification**: A Cirq user who wants to verify a result published with Qiskit code must either install and learn Qiskit or manually port the circuit — both are error‑prone and time‑consuming.
- **No standard artifact format**: Classical computing has standardized artifact evaluation (e.g., ACM badges, Docker containers, Jupyter notebooks). Quantum computing lacks an equivalent: there is no agreed‑upon, framework‑neutral format for sharing quantum circuits alongside papers.
- **OpenQASM 3.0 as a solution**: OpenQASM 3.0 is expressive enough to represent the vast majority of gate‑based quantum circuits, is human‑readable, and is increasingly supported by tools and platforms. It can serve as a **universal reproducibility artifact** — but this idea has not been formalized or evaluated.
- **QCanvas as the enabling platform**: QCanvas can convert programs written in any of the three major frameworks into standardized OpenQASM 3.0, simulate them on multiple backends, and provide rich metadata (gate counts, depth, performance metrics). This makes it a natural platform for generating and validating reproducibility artifacts.

The paper proposes a **framework for reproducible quantum computing research** centered on OpenQASM 3.0 artifacts, with QCanvas as the reference implementation for artifact generation, validation, and cross‑framework verification.

### 2. Research Questions

1. **RQ1 (Artifact Sufficiency):** Is OpenQASM 3.0 expressive enough to serve as a standalone reproducibility artifact for the majority of published gate‑based quantum algorithms?
2. **RQ2 (Cross‑Framework Reproduction):** Can results originally produced in one framework be reproduced by compiling the source to QASM 3.0 and simulating on a different framework's backend?
3. **RQ3 (Metadata Completeness):** What metadata (beyond the circuit itself) must accompany a QASM 3.0 artifact to enable full reproduction — shot count, backend type, noise model, random seed, framework version?
4. **RQ4 (Tooling Gap):** What tooling is currently missing from the ecosystem to support a QASM 3.0‑based reproducibility workflow, and how does QCanvas address part of that gap?

### 3. Background and Related Work

#### 3.1 Reproducibility in Classical Computing

- ACM artifact evaluation badges (Available, Functional, Reproduced).
- Docker/container‑based reproducibility.
- Jupyter notebooks as computational narratives.
- Language‑independent IRs (LLVM IR, WebAssembly) that enable cross‑platform verification.

#### 3.2 Reproducibility in Quantum Computing

- **Current state**: Most quantum papers share code as GitHub repositories with framework‑specific Python scripts. No standard format, no metadata schema, no cross‑framework validation.
- **Existing efforts**:
  - QASMBench (Li et al., 2022): a benchmark suite in QASM 2.0 — a step towards standard artifacts, but limited to QASM 2.0's simple feature set.
  - Qiskit's `.qpy` format: binary circuit serialization — framework‑specific, not human‑readable, not portable.
  - PennyLane's `qml.specs()`: circuit metadata — framework‑specific, not a standalone artifact.
- **Gap**: No work has proposed a comprehensive reproducibility framework using OpenQASM 3.0 as the artifact format, with tooling for generation, validation, and cross‑framework verification.

#### 3.3 OpenQASM 3.0 as an Artifact Format

- **Advantages**:
  - Human‑readable (can be inspected, understood, and included in papers).
  - Rich enough for complex circuits (control flow, subroutines, gate modifiers, types).
  - Hardware‑agnostic (not tied to any vendor's backend).
  - Increasingly supported (Qiskit, Amazon Braket, QCanvas).
- **Limitations**:
  - Does not capture noise models or hardware topology.
  - Does not encode simulation configuration (shots, seed, backend type).
  - Some framework‑specific features (PennyLane's automatic differentiation, Qiskit's transpiler passes) are not representable.

### 4. Proposed Reproducibility Framework

The paper proposes a three‑layer reproducibility framework:

#### 4.1 Layer 1: Circuit Artifact (OpenQASM 3.0)

The core artifact is a standards‑compliant OpenQASM 3.0 file that captures:

- The complete quantum circuit (gates, measurements, control flow, subroutines).
- All gate modifiers (`ctrl@`, `inv@`, `negctrl@`, `pow@`).
- Classical logic interleaved with quantum operations.
- Parameterized circuits with concrete parameter values bound.

**Generation via QCanvas**: The AST‑based parser accepts Qiskit, Cirq, or PennyLane source code and produces QASM 3.0 without executing user code — ensuring the artifact is derived securely and deterministically from the source.

#### 4.2 Layer 2: Metadata Schema (JSON Sidecar)

A JSON metadata file accompanies each QASM 3.0 artifact:

```json
{
  "artifact_version": "1.0",
  "algorithm": "Grover's Search",
  "source_framework": "qiskit",
  "source_framework_version": "1.2.0",
  "qcanvas_version": "1.0.0",
  "compilation": {
    "method": "ast_based",
    "compilation_time_ms": 16.4,
    "fallback_used": false
  },
  "circuit_metrics": {
    "qubit_count": 4,
    "classical_bit_count": 4,
    "gate_count": 28,
    "circuit_depth": 12,
    "gate_breakdown": {
      "h": 8, "x": 4, "cx": 8, "ccx": 2, "measure": 4, "barrier": 2
    }
  },
  "simulation_config": {
    "backend": "cirq_statevector",
    "shots": 4096,
    "random_seed": 42
  },
  "expected_results": {
    "dominant_bitstring": "1010",
    "dominant_probability": 0.96,
    "full_distribution": { "1010": 3932, "0101": 82, "...": "..." }
  },
  "reproduction_instructions": "Compile with QCanvas or execute QASM directly on any QASM 3.0-compatible simulator."
}
```

This metadata schema is designed to be:
- **Machine‑readable**: Tools can automatically validate reproduction.
- **Human‑readable**: Researchers can inspect and understand the configuration.
- **Extensible**: Additional fields (noise model, hardware topology, transpiler passes) can be added as the ecosystem matures.

#### 4.3 Layer 3: Validation Protocol

A standardized validation protocol for checking whether a result has been reproduced:

1. **Syntactic validation**: Parse the QASM 3.0 artifact and verify it is well‑formed.
2. **Structural validation**: Extract circuit metrics and compare against the metadata sidecar.
3. **Simulation validation**: Execute the QASM on a specified backend with the specified shots and seed.
4. **Statistical validation**: Compare the simulation output against `expected_results` using:
   - Chi‑squared test (p > 0.05 for equivalence).
   - Jensen–Shannon divergence (JSD < 0.01 for strong equivalence).
   - Top‑k bitstring match (the dominant outcome matches).
5. **Cross‑framework validation**: Optionally, reverse‑compile the QASM back into a different framework and simulate there, verifying framework independence.

### 5. Experimental Evaluation

#### 5.1 Experiment 1: Artifact Generation Coverage

**Goal**: Determine what fraction of published quantum algorithms can be captured as QASM 3.0 artifacts via QCanvas.

**Method**:
- Curate a corpus of 30–50 quantum algorithms from recent publications (2022–2025) and textbooks.
- Attempt to implement each in Qiskit, Cirq, and PennyLane and compile via QCanvas.
- Categorize results:
  - **Full support**: QASM 3.0 artifact captures the complete circuit.
  - **Partial support**: Core circuit captured, but some features (noise, hardware mapping) are not represented.
  - **Unsupported**: Algorithm uses features outside QCanvas/QASM 3.0 scope (pulse‑level, continuous‑variable, etc.).

**Expected result**: >85% of standard gate‑based algorithms in full or partial support, with unsupported cases clearly identified and documented.

#### 5.2 Experiment 2: Cross‑Framework Reproduction

**Goal**: Demonstrate that results produced in one framework can be reproduced via the QASM 3.0 artifact on a different framework's backend.

**Method**:
- Select 10 representative algorithms (from QCanvas's example library).
- For each algorithm:
  1. Implement in Framework A (e.g., Qiskit), compile to QASM 3.0, simulate on Backend A, record results.
  2. Take the QASM 3.0 artifact and simulate on Backend B (e.g., Cirq backend) and Backend C (e.g., PennyLane backend).
  3. Compare results across all three backends using the validation protocol.
- Record:
  - Pass/fail for each (algorithm, source framework, target backend) triple.
  - Statistical divergence metrics.
  - Any cases where reproduction fails, with root cause analysis.

**Expected result**: >95% reproduction success for standard algorithms. Failures, if any, will be attributable to known framework‑specific simulation differences (e.g., qubit ordering conventions, measurement collapse behavior).

#### 5.3 Experiment 3: Reproducing Published Results

**Goal**: Take actual results from published quantum computing papers and attempt to reproduce them using QCanvas and the QASM 3.0 artifact framework.

**Method**:
- Select 5–8 recent papers that include quantum circuits and simulation results.
- Reimplement the circuits in QCanvas (in the original paper's framework).
- Compile to QASM 3.0, simulate, and compare against published results.
- Document:
  - Whether reproduction succeeded.
  - What information was missing from the original paper (shot count, seed, backend, version).
  - How much effort the reproduction required.
  - Whether the QASM 3.0 artifact would have simplified the process.

**Expected result**: Reproduction will succeed for papers with well‑documented configurations but fail for papers with incomplete methodology sections — demonstrating the value of standardized artifacts.

#### 5.4 Experiment 4: Metadata Necessity Analysis

**Goal**: Determine which metadata fields are essential for successful reproduction.

**Method**:
- Take 10 algorithms with full artifacts (QASM + metadata).
- Systematically ablate metadata fields (remove shot count, remove seed, remove backend specification, etc.).
- Attempt reproduction after each ablation.
- Record which ablations cause reproduction failure and by how much.

**Expected result**: Shot count and backend type are critical; random seed matters for small shot counts; framework version is important for parameterized circuits. This informs the "minimum viable metadata" for reproducibility.

### 6. The QASM Artifact Workflow in Practice

The paper walks through a concrete end‑to‑end scenario:

#### Scenario: A Researcher Publishing a VQE Result

1. **Development**: Researcher writes VQE circuit in PennyLane using QCanvas IDE.
2. **Compilation**: QCanvas compiles to OpenQASM 3.0, generating the circuit artifact.
3. **Simulation**: QSim executes the QASM with 4096 shots; results displayed in the histogram panel.
4. **Artifact Generation**: QCanvas exports:
   - `vqe_h2.qasm` — the OpenQASM 3.0 circuit.
   - `vqe_h2_meta.json` — the metadata sidecar with all configuration and expected results.
5. **Publication**: Researcher includes both files as supplementary material.
6. **Verification**: A reviewer (who uses Qiskit, not PennyLane):
   - Loads `vqe_h2.qasm` into QCanvas or any QASM 3.0‑compatible tool.
   - Simulates with the parameters from `vqe_h2_meta.json`.
   - Runs the validation protocol and confirms the results match.
   - No need to install PennyLane or understand its API.

### 7. Discussion

#### 7.1 Why OpenQASM 3.0 and Not Other Formats?

| Format | Human‑Readable | Framework‑Neutral | Rich Enough | Adoption |
|--------|:-:|:-:|:-:|:-:|
| OpenQASM 3.0 | Yes | Yes | Yes (gate‑level) | Growing |
| OpenQASM 2.0 | Yes | Yes | No (too limited) | Wide |
| Qiskit QPY | No | No | Yes | Qiskit only |
| Quil | Yes | Rigetti‑centric | Moderate | Low |
| QIR (LLVM) | No | Yes | Yes | Early |

OpenQASM 3.0 is the only format that is simultaneously human‑readable, framework‑neutral, and rich enough for modern quantum circuits.

#### 7.2 What QASM 3.0 Cannot Capture

The paper honestly discusses limitations:

- **Noise models**: QASM 3.0 does not encode noise channels. The metadata sidecar must specify noise separately.
- **Transpiler/optimization passes**: Framework‑specific optimizations are lost in the QASM output. The artifact represents the *logical* circuit, not the *physical* circuit.
- **Automatic differentiation**: PennyLane's gradient computation is not representable in QASM.
- **Pulse‑level control**: QASM 3.0 has pulse features, but they are underspecified and not yet widely supported.
- **Classical pre/post‑processing**: The Python code around the quantum circuit (data loading, result analysis) is not captured.

For each limitation, the paper discusses whether the metadata sidecar can compensate or whether additional artifact types are needed.

#### 7.3 Comparison with Classical Reproducibility

- **Docker analogy**: QASM 3.0 + metadata is to quantum computing what a Docker image is to classical computing — a portable, self‑contained execution artifact.
- **Jupyter analogy**: QASM 3.0 is more like a compiled binary than a notebook; it captures the circuit but not the development narrative. The metadata sidecar partially addresses this.
- **LLVM IR analogy**: Just as LLVM IR enables cross‑platform compilation and verification, QASM 3.0 enables cross‑framework quantum circuit portability.

#### 7.4 Path to Adoption

The paper proposes a realistic adoption path:

1. **Immediate**: Researchers voluntarily include QASM 3.0 artifacts with submissions. QCanvas makes this easy.
2. **Short term**: Conferences and journals adopt optional artifact evaluation for quantum papers (similar to ACM badges).
3. **Medium term**: Artifact submission becomes standard practice; review processes include reproduction checks.
4. **Long term**: QASM 3.0 artifacts are required for quantum computing publications, with automated validation pipelines.

#### 7.5 Limitations of This Work

- **Simulation‑only validation**: Reproduction is tested via simulation, not hardware. Hardware reproducibility introduces additional variables (calibration drift, queue effects, noise).
- **Algorithm coverage**: The evaluation covers gate‑based algorithms only; continuous‑variable, measurement‑based, and topological approaches are excluded.
- **Metadata schema is preliminary**: The proposed schema is a starting point; community input is needed to mature it.
- **Single tool dependency**: The current workflow relies on QCanvas for artifact generation; broader tool support is needed for ecosystem‑wide adoption.

### 8. Contributions Claimed by the Paper

1. A **reproducibility framework** for quantum computing research centered on OpenQASM 3.0 artifacts with a structured metadata sidecar.
2. A **validation protocol** with concrete statistical criteria for determining whether a quantum result has been successfully reproduced.
3. **Empirical evidence** from four experiments showing that:
   - QASM 3.0 can capture >85% of standard gate‑based algorithms.
   - Cross‑framework reproduction succeeds >95% of the time.
   - Published results can be reproduced when sufficient metadata is provided.
   - Specific metadata fields (shots, backend, seed) are critical for reproduction.
4. A **concrete workflow** demonstrating end‑to‑end artifact generation, publication, and verification using QCanvas.
5. A **comparison** of QASM 3.0 against alternative artifact formats, arguing for its suitability as the community standard.
6. A **roadmap** for community adoption of quantum reproducibility practices, from voluntary artifacts to mandatory evaluation.

### 9. Proposed Paper Structure

| Section | Content | Estimated Pages |
|---------|---------|-----------------|
| 1. Introduction | Reproducibility crisis, QASM 3.0 opportunity, contributions | 1.5 |
| 2. Background | Reproducibility in CS, quantum frameworks, QASM 3.0, QCanvas | 2 |
| 3. Reproducibility Framework | Three layers: artifact, metadata, validation protocol | 3 |
| 4. Experimental Evaluation | Four experiments with methodology and results | 3.5 |
| 5. End‑to‑End Workflow | VQE scenario walkthrough | 1 |
| 6. Discussion | Limitations, comparisons, adoption path | 2 |
| 7. Related Work | Classical reproducibility, quantum benchmarks, existing tools | 1 |
| 8. Conclusion | Summary, call to action, future work | 0.5 |
| **Total** | | **~14–15 pages** |

### 10. Target Venues

- **ACM/IEEE International Conference on Quantum Computing and Engineering (QCE)** — strong fit for tools and methodology papers.
- **Nature Quantum Information** — high‑impact journal; reproducibility is a recurring editorial concern.
- **IEEE Transactions on Quantum Engineering** — journal with software/tools scope.
- **ACM SIGSOFT / FSE (Reproducibility Track)** — if framed as a software engineering contribution.
- **arXiv preprint** — for early community feedback and visibility.

