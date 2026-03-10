## Paper 5 – Cross‑Framework Quantum Algorithm Benchmarking via Unified Compilation to OpenQASM 3.0

### 1. Problem and Motivation

- **No apples‑to‑apples comparison exists**: Researchers routinely implement quantum algorithms in a single framework (Qiskit, Cirq, or PennyLane) and report performance metrics, but there is no systematic study comparing *the same algorithm* across all three major frameworks under identical conditions.
- **Framework choice introduces hidden variation**: Each framework makes different internal decisions about gate decomposition, parameter conventions, qubit ordering, and measurement handling. These choices silently affect circuit depth, gate count, and even simulation results — yet they are rarely quantified.
- **Lack of a neutral compilation target**: Without a common intermediate representation, comparing "Grover's in Qiskit" with "Grover's in Cirq" is meaningless because the circuits are expressed in incompatible formats. OpenQASM 3.0 can serve as this neutral target, but no study has used it systematically for benchmarking.
- **QCanvas as an enabling tool**: QCanvas provides a unique capability — it can take the *same algorithm* written idiomatically in each framework, compile all three to OpenQASM 3.0 via its secure AST‑based pipeline, and simulate them on the same backend. This creates a controlled experimental environment that did not previously exist.

The paper proposes a **systematic cross‑framework benchmarking methodology** using QCanvas and OpenQASM 3.0 as the unifying layer.

### 2. Research Questions

The paper addresses four core research questions:

1. **RQ1 (Structural Divergence):** For the same quantum algorithm, how do the generated OpenQASM 3.0 circuits differ across Qiskit, Cirq, and PennyLane in terms of gate count, circuit depth, qubit usage, and gate composition?
2. **RQ2 (Simulation Equivalence):** Do the three framework implementations produce statistically equivalent measurement distributions when compiled to QASM 3.0 and simulated on the same backend?
3. **RQ3 (Performance Variation):** How do compilation time, simulation time, memory consumption, and CPU utilization vary across framework origins for the same algorithm?
4. **RQ4 (Complexity Scaling):** As algorithm complexity increases (more qubits, deeper circuits, variational parameters), do the cross‑framework differences grow, shrink, or remain constant?

### 3. Benchmarking Methodology

#### 3.1 Algorithm Selection

The benchmark suite consists of algorithms spanning multiple categories and difficulty levels, drawn from QCanvas's built‑in example library and extended where needed:

| Category | Algorithms | Qubit Range |
|----------|-----------|-------------|
| Foundational | Bell State, GHZ State | 2–8 |
| Quantum Communication | Quantum Teleportation | 3 |
| Oracle‑Based | Deutsch–Jozsa, Bernstein–Vazirani | 3–8 |
| Search | Grover's Algorithm | 2–6 |
| Randomness | Quantum Random Number Generator (QRNG) | 4–8 |
| Variational | VQE, QAOA | 2–6 |
| Quantum ML | QML XOR Classifier, Simple QNN | 2–4 |
| Error Correction | Bit‑Flip Code, Phase‑Flip Code | 3–9 |

Each algorithm is implemented **idiomatically** in Qiskit, Cirq, and PennyLane — following each framework's conventions and best practices rather than forcing a uniform coding style.

#### 3.2 Experimental Pipeline

For each (algorithm, framework) pair, the following pipeline is executed:

1. **AST Parsing** → QCanvas parses the framework source code into a `CircuitAST` using the appropriate visitor (`QiskitASTVisitor`, `CirqASTVisitor`, `PennyLaneASTVisitor`).
2. **QASM 3.0 Generation** → The `QASM3Builder` converts the `CircuitAST` into standards‑compliant OpenQASM 3.0.
3. **Static Analysis** → Extract structural metrics from the generated QASM:
   - Total gate count (by gate type)
   - Circuit depth
   - Number of single‑qubit vs. multi‑qubit gates
   - Number of measurements
   - Use of gate modifiers (`ctrl@`, `inv@`, `pow@`)
4. **Simulation** → Execute the generated QASM on QSim backends with configurable shots (1024, 4096, 8192) and collect:
   - Measurement distributions (bitstring → count)
   - Execution time
   - Memory usage
   - CPU utilization
5. **Comparison** → For each algorithm, compare all three frameworks on every metric.

#### 3.3 Controlled Variables

To ensure fair comparison:

- **Same QASM backend**: All simulations use the same QSim backend (default: Cirq statevector simulator).
- **Same shot count**: Identical number of measurement shots per run.
- **Same hardware**: All experiments run on the same machine (specified in the paper).
- **Multiple runs**: Each experiment is repeated 10 times; results report mean and standard deviation.
- **Identical algorithm logic**: Each implementation encodes the same oracle, ansatz, or circuit structure — only the framework syntax differs.

### 4. Metrics and Analysis

#### 4.1 Structural Metrics (Static)

| Metric | Description | Comparison Method |
|--------|-------------|-------------------|
| Gate count | Total gates in generated QASM | Direct numerical comparison |
| Gate composition | Breakdown by gate type (H, CNOT, Rz, etc.) | Stacked bar chart per framework |
| Circuit depth | Longest path from input to measurement | Direct comparison |
| Multi‑qubit ratio | Fraction of gates that are 2+ qubit | Percentage comparison |
| Modifier usage | Count of `ctrl@`, `inv@`, `pow@` modifiers | Presence/absence and count |
| Measurement count | Number of `measure` operations | Direct comparison |

These metrics reveal how each framework's conventions and QCanvas's parsing translate into different QASM structures for the same algorithm.

#### 4.2 Simulation Metrics (Dynamic)

| Metric | Description | Comparison Method |
|--------|-------------|-------------------|
| Measurement distribution | Bitstring → probability | Chi‑squared test or KL divergence |
| Compilation time | AST parse + QASM generation (ms) | Mean ± std over 10 runs |
| Simulation time | QSim execution (ms) | Mean ± std over 10 runs |
| Memory usage | Peak memory during simulation (MB) | Mean ± std over 10 runs |
| CPU utilization | % CPU during simulation | Mean ± std over 10 runs |
| Estimated fidelity | QSim‑reported fidelity metric | Direct comparison |

#### 4.3 Statistical Equivalence Testing

For each algorithm, test whether the three frameworks produce **statistically equivalent** measurement distributions:

- **Chi‑squared goodness‑of‑fit test**: Compare each framework's distribution against the theoretical/expected distribution.
- **Pairwise KL divergence**: Measure information‑theoretic distance between each pair of framework outputs.
- **Jensen–Shannon divergence**: Symmetric version of KL for cleaner pairwise comparison.
- **Threshold**: Define equivalence as JSD < 0.01 (effectively identical) and flag any pair exceeding JSD > 0.05 for investigation.

#### 4.4 Scaling Analysis

For algorithms that support variable qubit counts (e.g., GHZ, Deutsch–Jozsa, Grover's, QRNG):

- Plot gate count, depth, and compilation time as a function of qubit count for each framework.
- Identify whether cross‑framework differences are **constant** (additive overhead), **linear** (proportional), or **super‑linear** (diverging).
- Determine at what scale framework choice starts to matter significantly.

### 5. Expected Results and Hypotheses

Based on preliminary observations during QCanvas development:

1. **Gate count will vary by 5–20%** across frameworks for the same algorithm, because:
   - Different default decompositions (e.g., Cirq may decompose `SWAP` differently than Qiskit).
   - PennyLane's template‑based approach may introduce extra or fewer gates depending on the algorithm.
2. **Measurement distributions will be statistically equivalent** for well‑known algorithms (Bell, GHZ, Teleportation) but may show **small divergences** for variational algorithms where parameterization and initialization differ.
3. **Compilation time will be fastest for Cirq** (simpler AST patterns, function‑based) and **slowest for PennyLane** (decorator pattern, more complex AST traversal).
4. **Simulation time will be independent of source framework** (since all run the same QASM), confirming that the compilation layer, not the framework, determines runtime.
5. **Scaling behavior will be similar** across frameworks, but the constant factor (gate overhead) will vary.

### 6. Case Studies (Detailed Walkthroughs)

The paper includes 3–4 detailed case studies with full QASM listings:

#### Case Study 1: Bell State (Simplest Case)

- Show Qiskit, Cirq, PennyLane source code side by side.
- Show generated QASM 3.0 for each.
- Highlight differences: e.g., Qiskit may produce `cx` while Cirq produces `ctrl @ x` via modifier syntax.
- Compare measurement histograms (expect `|00⟩: 50%, |11⟩: 50%` for all three).

#### Case Study 2: Grover's Algorithm (Moderate Complexity)

- Show how oracle encoding differs across frameworks.
- Compare generated QASM depth and gate counts.
- Analyze whether the diffusion operator is decomposed identically.
- Compare simulation results at 2, 3, 4, and 5 qubits.

#### Case Study 3: VQE / QAOA (Variational)

- Show how ansatz construction differs (Qiskit's `EfficientSU2`, Cirq's manual construction, PennyLane's `StronglyEntanglingLayers`).
- Compare generated QASM for one variational layer.
- Analyze whether parameter handling introduces structural differences.
- Discuss implications for variational algorithm benchmarking in the literature.

#### Case Study 4: QML XOR Classifier (Quantum ML)

- Compare PennyLane's native QML approach with equivalent Qiskit and Cirq implementations.
- Analyze circuit structure differences for data encoding and variational layers.
- Discuss how framework design philosophy affects QML circuit structure.

### 7. Discussion

#### 7.1 Implications for Researchers

- **Framework choice is not neutral**: The same algorithm, written in different frameworks, produces measurably different QASM circuits. Researchers should report framework and version alongside results.
- **OpenQASM 3.0 as a benchmark artifact**: Publishing QASM 3.0 alongside papers would allow direct comparison and reproduction, independent of framework.
- **QCanvas as a benchmarking platform**: The unified compilation pipeline enables controlled cross‑framework experiments that were previously impractical.

#### 7.2 Implications for Framework Developers

- **Gate decomposition transparency**: Frameworks should document their default decomposition strategies so users can understand and control circuit structure.
- **Standardized naming and parameter conventions**: The benchmarking results quantify the cost of naming and convention fragmentation.
- **QASM 3.0 export as a priority**: Frameworks that support native QASM 3.0 export enable users to verify and compare their circuits against a standard.

#### 7.3 Implications for Educators

- **Teaching framework independence**: The benchmark results show students that quantum concepts are framework‑independent, even if the generated circuits differ in details.
- **Using QCanvas for comparative labs**: Educators can use the benchmark methodology as a classroom exercise to teach about compilation, optimization, and framework trade‑offs.

#### 7.4 Limitations

- **Simulation only**: Results are based on simulation, not hardware execution. Hardware‑level differences (noise, connectivity) are not captured.
- **Idiomatic implementations**: "Idiomatic" is subjective; different developers might write different Qiskit code for the same algorithm. The paper uses QCanvas's built‑in examples as a consistent baseline.
- **AST coverage**: QCanvas's AST parsers support a specific subset of each framework's features. Algorithms using unsupported features are excluded.
- **Shot noise**: Finite shot counts introduce statistical variation; the paper uses multiple runs and statistical tests to account for this.

### 8. Related Work

- **Quantum algorithm benchmarks**: QASMBench (Li et al., 2022), SupermarQ (Tomesh et al., 2022), and MQTBench (Quetschlich et al., 2023) provide benchmark suites but focus on single‑framework circuits or hardware performance, not cross‑framework comparison.
- **Framework comparison surveys**: Existing surveys (LaRose, 2019; Fingerhuth et al., 2018) compare frameworks at the API/feature level but do not compile to a common IR and compare output structure.
- **Compiler benchmarks**: t|ket⟩ benchmarks focus on optimization performance, not framework‑of‑origin effects.
- **This paper's novelty**: The first systematic study that compiles the same algorithms from three frameworks into OpenQASM 3.0 and compares structural and simulation metrics under controlled conditions, using QCanvas as the enabling platform.

### 9. Contributions Claimed by the Paper

1. A **cross‑framework benchmarking methodology** that uses OpenQASM 3.0 as a neutral comparison target and QCanvas as the unified compilation platform.
2. A **benchmark suite** of 12+ quantum algorithms implemented idiomatically in Qiskit, Cirq, and PennyLane, with full QASM 3.0 outputs.
3. **Quantitative evidence** that framework choice introduces measurable variation in circuit structure (gate count, depth, composition) even for semantically identical algorithms.
4. **Statistical analysis** showing that simulation results are equivalent across frameworks for standard algorithms, validating the compilation pipeline's correctness.
5. **Scaling analysis** revealing how cross‑framework differences behave as circuit complexity increases.
6. **Practical recommendations** for researchers (report framework details, publish QASM artifacts), framework developers (standardize decompositions), and educators (use cross‑framework comparison as a teaching tool).

### 10. Proposed Paper Structure

| Section | Content | Estimated Pages |
|---------|---------|-----------------|
| 1. Introduction | Motivation, research questions, contributions | 1.5 |
| 2. Background | Quantum frameworks, OpenQASM 3.0, QCanvas overview | 2 |
| 3. Benchmarking Methodology | Algorithm selection, pipeline, metrics, statistical tests | 2.5 |
| 4. Results | Structural comparison, simulation comparison, scaling | 3 |
| 5. Case Studies | Detailed walkthroughs of 3–4 algorithms | 2.5 |
| 6. Discussion | Implications, limitations, threats to validity | 1.5 |
| 7. Related Work | Existing benchmarks and surveys | 1 |
| 8. Conclusion | Summary, future work (hardware extension, more frameworks) | 0.5 |
| **Total** | | **~14–15 pages** |

### 11. Target Venues

- **IEEE International Conference on Quantum Computing and Engineering (QCE / Quantum Week)** — primary target; accepts benchmarking and tools papers.
- **ACM Transactions on Quantum Computing (TQC)** — journal option for extended version.
- **Quantum Science and Technology (IOP)** — journal with broad quantum computing scope.
- **arXiv preprint** — for early visibility and community feedback.

