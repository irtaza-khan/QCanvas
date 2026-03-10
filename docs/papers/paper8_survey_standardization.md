## Paper 8 – Towards Standardization in Quantum Programming: A Survey of Frameworks, IRs, and Interoperability Tools

### 1. What This Paper Is About

This paper is a **survey and position paper** about the current state of quantum programming and the path towards **standardization**. It:

- Catalogues the major **quantum programming frameworks** (Qiskit, Cirq, PennyLane, PyQuil, Amazon Braket, Q#, Strawberry Fields).
- Reviews key **intermediate representations (IRs)** (OpenQASM 2.0/3.0, Quil, QIR, XACC IR).
- Describes prominent **interoperability tools** (t$|$ket$\\rangle$, Mitiq, QCanvas, Orquestra, Strangeworks).
- Analyzes **OpenQASM 3.0** as the leading candidate for a universal standard.
- Uses **QCanvas** as a case study to expose concrete cross‑framework issues.
- Proposes a **roadmap** for standardization over the short, medium, and long term.

The focus is on **portability, reproducibility, educational accessibility, and vendor‑agnostic development**.

### 2. Motivation and Problem Statement

- The ecosystem is **fragmented**:
  - Each major vendor ships its own SDK and toolchain.
  - Code written in one framework is not executable in another without manual porting.
- This fragmentation leads to:
  - Poor **code portability** and **tool lock‑in**.
  - Difficult **reproducibility** for research papers.
  - Higher **barriers to entry** for students and educators.
  - Repeated **duplication of effort** (same algorithm in many incompatible forms).
- The paper argues that, just as classical computing moved toward standardized ISAs and IRs (e.g., LLVM), **quantum computing must converge on shared standards** to scale.

### 3. Survey Methodology (Scope and Dimensions)

The survey includes tools that:

- Are actively maintained (recent releases/commits).
- Support **gate‑based** quantum programming.
- Provide either:
  - a **framework**, or
  - an **intermediate representation**, or
  - an **interoperability tool**.

Each system is evaluated on 12 dimensions:

1. Programming paradigm (imperative, functional, declarative, standalone language, visual).
2. Primary language/API design (Python, Q#, instruction‑based, etc.).
3. Gate library coverage (single/multi‑qubit, parameterized, custom gates).
4. Gate modifiers (control, inverse, power, negative control).
5. Classical control flow (conditionals, loops, functions).
6. Type system richness (classical types, complex types, arrays).
7. Measurement model (mid‑circuit, terminal, observable‑based).
8. Simulation capabilities (statevector, density matrix, noise, QML support).
9. Hardware access and vendor coverage.
10. QASM/IR import/export support.
11. Community ecosystem (usage, contributors, docs).
12. Educational resources and documentation quality.

### 4. Survey of Programming Frameworks

For each major framework, the paper summarizes:

#### Qiskit (IBM)
- Imperative, object‑oriented Python SDK (`QuantumCircuit`).
- Broad gate library, transpiler stack, and Aer simulators.
- Native OpenQASM 2.0 export; partial OpenQASM 3.0 support.
- Tight integration with IBM Quantum hardware; large community and educational materials.

#### Cirq (Google)
- Functional‑declarative style with explicit qubits (`LineQubit`, `GridQubit`).
- Strong focus on NISQ circuits and device‑level topology.
- QASM 2.0 export via `QasmOutput`; no native QASM 3.0 support.
- Integration with Google hardware via Google Cloud.

#### PennyLane (Xanadu)
- Quantum machine learning‑oriented, decorator (@`qml.qnode`) style.
- Extensive template library for variational circuits and QML models.
- Integrates with ML frameworks (PyTorch, TensorFlow, JAX).
- QASM 2.0 **import**, but no QASM 3.0 export.

#### Other Frameworks
- **PyQuil** (Rigetti) built around **Quil** as the native IR and Rigetti hardware.
- **Amazon Braket**: vendor‑neutral cloud service, Python SDK, early OpenQASM 3.0 input support.
- **Q#** (Microsoft): standalone, strongly‑typed quantum language built around **QIR** (LLVM‑based IR).
- **Strawberry Fields** (Xanadu): continuous‑variable photonic platform; included as a different paradigm.

The paper provides a **framework comparison table** summarizing language, paradigm, gate naming, parameter conventions, QASM support, IR, mid‑circuit measurement support, and community metrics.

### 5. Survey of Intermediate Representations

The paper analyzes 4 main IR families:

#### OpenQASM 2.0
- Simple, instruction‑style quantum assembly language (gates, qubits, bits, simple conditionals).
- Widely supported for basic circuit interchange, but lacks a rich type system, control flow, and subroutines.

#### OpenQASM 3.0
- A major evolution: full type system, control flow, subroutines, gate modifiers, timing, and pulse‑level features.
- Intended as a **universal IR** for both high‑level logic and low‑level scheduling.
- Human‑readable and suitable for debugging and education.

#### Quil
- Rigetti’s instruction language; hardware‑oriented with `DECLARE` for classical memory and `DEFGATE` for custom gates.
- Emphasizes low‑level control and compiler pragmas.
- Not as general or high‑level as QASM 3.0.

#### QIR (LLVM‑based) and XACC IR
- **QIR**: quantum integrated into LLVM IR with runtime calls; excellent for classical computation and optimization, but not human‑friendly.
- **XACC IR**: graphs/IR nodes representing circuits across platforms; plugin‑based, hardware‑agnostic, but with lower adoption.

A comparison table contrasts these IRs on capabilities, human readability, and adoption.

### 6. Interoperability Tools

The survey covers:

#### t$|$ket$\\rangle$ (Quantinuum)
- Retargetable compiler and optimizer.
- Accepts circuit objects from various frameworks (Qiskit, Cirq, PennyLane, etc.).
- Focuses on **optimization and hardware mapping**, not source‑level transpilation.

#### Mitiq
- Framework‑agnostic **error mitigation** toolkit.
- Works at circuit level, wrapping circuits to insert error‑mitigation strategies; not an IR converter.

#### QCanvas (Your System)
- Accepts framework‑specific **source code** (not just circuit objects).
- Uses **secure AST‑based parsing** (no code execution) to produce a unified Circuit AST.
- Generates standards‑compliant OpenQASM 3.0 (Iteration I and II) and supports multi‑backend simulation.
- Bundled with a web IDE (QCanvas IDE) to make this process interactive and educational.

#### Orquestra, Strangeworks
- Provide workflow/orchestration or cloud aggregation instead of code‑level transpilation, but relevant for the interoperability landscape.

The paper includes a table comparing these tools on whether they accept source code, perform AST analysis, do optimization, generate QASM 3.0, and/or provide a web IDE.

### 7. Deep Dive: OpenQASM 3.0 as a Standard

The paper then focuses on **OpenQASM 3.0**:

- Categorizes features as **core**, **intermediate**, **advanced**, and **specialized** based on implementation difficulty:
  - Core: registers, standard gates, measurement/reset/barrier, simple control flow.
  - Intermediate: full type system, arrays, aliasing, input/output, math functions.
  - Advanced: `negctrl@`, `pow(k)@`, subroutines, while/break/continue, complex types, bitwise/shift operators.
  - Specialized: timing, pulse‑level control, externs, physical qubits, hardware extensions.
- Discusses **adoption status**:
  - Qiskit: partial QASM 3 support.
  - Braket: supports QASM 3 as an input format.
  - Other frameworks: mostly stuck at QASM 2 or lacking support.
  - QCanvas: demonstrates full Iteration I/II gate‑based QASM 3 generation.
- Highlights **implementation challenges** discovered during QCanvas development:
  - Measurement formatting consistency (QASM 2 vs. 3 syntax).
  - Type choice for loop variables (`int` vs. `uint`).
  - Semantics and ordering of composed gate modifiers.
  - Proper classical bit counting based on actual measurement usage.
  - Standard library (`stdgates.inc`) not fully standardized across tools.

### 8. QCanvas Case Study: Concrete Cross‑Framework Issues

Using QCanvas as a case study, the paper identifies real interoperability problems:

1. **Naming discrepancies** – same gate, many names (e.g., H vs. `Hadamard`; `cx` vs. `CNOT` vs. `CNOT`).
2. **Parameter convention incompatibilities** – angle ordering, keyword vs. positional arguments, power syntax (`**0.5`), etc.\n3. **Different circuit construction patterns** – method‑based (Qiskit), function‑based (Cirq), decorator‑based (PennyLane) requiring completely different parsing strategies.\n4. **Qubit addressing** – integer indices vs. qubit objects vs. wire keywords; mapping `GridQubit` to linear indices.\n5. **Measurement model differences** – classical registers vs. key‑based vs. observable‑based measurements.\n6. **Inverse and modifier semantics** – `sdg/tdg` vs. exponentiation vs. `adjoint()`; mapping all to QASM 3’s `inv@` and `ctrl@` system.

These concrete examples show that **just having a standard (OpenQASM 3.0) is not enough**—we also need consistent gate semantics, parameter conventions, and measurement models across frameworks.

### 9. Standardization Roadmap Proposed

The paper proposes a **three‑phase roadmap**:

#### Short Term (1–2 years)

- Standardize **gate semantics** and mapping tables (names, parameters, decompositions).
- Publish an official, versioned **`stdgates.inc`** library for QASM 3.0.
- Create an **OpenQASM 3.0 compliance test suite** for parsers and generators.
- Encourage framework maintainers to ship **native QASM 3.0 export APIs**.

#### Medium Term (2–4 years)

- Define a **unified circuit metadata standard** (gate counts, depth, connectivity, qubit topology).
- Build a **cross‑framework benchmark suite** (canonical algorithm set with implementations in each major framework plus reference QASM 3).
- Establish an **interoperability certification process** using this suite.
- Mature and standardize **pulse‑level** parts of QASM 3 and their mapping to hardware.

#### Long Term (4+ years)

- Develop a **universal quantum compiler infrastructure** (quantum analogue of LLVM) where:
  - frontends are various frameworks,
  - IRs include QASM 3 and/or QIR,
  - backends are concrete quantum devices and simulators.\n- Support **“compile once, run anywhere”** deployment across hardware vendors.\n- Define **quantum software engineering standards** (testing, documentation, code quality) analogous to classical SE.

### 10. Discussion and Position

The paper’s stance:

- **OpenQASM 3.0 is the most promising standard**: rich, human‑readable, backed by IBM, and already influencing tools and platforms.
- But **barriers remain**:
  - Commercial incentives to keep ecosystems proprietary.
  - Fast‑moving research can outpace the standard.
  - Diverse qubit technologies make low‑level standardization harder.
  - Some parts of the spec (timing, pulse‑level) are under‑implemented in practice.
- Tools like **QCanvas**, **t$|$ket$\\rangle$**, and **Mitiq** are essential bridging solutions:
  - They prove interoperability is feasible.
  - They expose real friction points in the spec and ecosystem.
  - They can help drive community consensus through concrete implementations.

### 11. Main Takeaways

- The quantum programming ecosystem is currently **highly fragmented**, and this is starting to hurt scalability in research, industry, and education.\n- OpenQASM 3.0 provides a solid basis for a **universal quantum IR**, but adoption and implementation details are uneven.\n- **Cross‑framework tools**—especially those that operate on source code and generate OpenQASM 3.0 (like QCanvas)—reveal the exact gaps that standards must address.\n- The paper lays out a **practical, staged roadmap** the community can follow to move from today’s fragmented landscape toward a more unified, interoperable quantum software stack.

