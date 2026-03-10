## Paper 4 – QCanvas IDE: A Web‑Based Quantum Computing Development Environment for Education and Research

### 1. Goal of the Paper

This paper introduces **QCanvas IDE**, a browser‑based quantum programming environment designed to:

- Make quantum computing **accessible for students and educators** with zero installation.
- Support **three major frameworks** (Qiskit, Cirq, PennyLane) in a single interface.
- Provide **real‑time compilation to OpenQASM 3.0** and multi‑backend simulation via QSim.
- Offer strong **educational scaffolding** (examples, visualizations, progressive disclosure) while still being useful for research and prototyping.

### 2. Motivation and Problems Addressed

The paper highlights several pain points in current quantum education:

- Difficult and fragile **local setup** of SDKs and dependencies.
- **Framework fragmentation**: students see only one ecosystem and struggle to transfer knowledge.
- Limited or clunky **interactivity and visualization** in command‑line or notebook workflows.
- Lack of integrated environments that combine **multi‑framework code editing, compilation, simulation, and visualization** in one tool.

QCanvas IDE is proposed as a **unified, web‑based IDE** that addresses these issues for both classroom and research settings.

### 3. Educational Design Principles

The design of QCanvas IDE is grounded in computing education and HCI principles:

#### Progressive Disclosure

- **Beginner view:** Clean interface; students can open a pre‑built example, click “Compile” and “Run,” and immediately see QASM output + histogram.
- **Intermediate view:** Access to framework selection, simulation configuration (backend, shots), and multi‑file editing.
- **Advanced view:** Keyboard shortcuts, statistics panel, detailed error logs, hybrid execution mode, and multi‑backend comparison.

#### Scaffolded Learning with Example Library

- 25+ curated examples, grouped into categories:
  - Basic Circuits: Bell, GHZ.
  - Quantum Algorithms: Teleportation, Deutsch–Jozsa, QRNG, Grover’s.
  - Variational Algorithms: VQE, QAOA.
  - Quantum Machine Learning: QML XOR classifier, QNN.
  - Error Correction and others.
- Many algorithms are provided in **all three frameworks**, letting students see how the same concept is written in Qiskit, Cirq, and PennyLane.

#### Immediate Feedback

- Real‑time syntax validation in the Monaco editor.
- Fast compile–run cycle with:
  - QASM panel,
  - histogram panel,
  - stats panel,
  - console log,
  - detailed error diagnostics.
- This supports **Constructionist** learning: students write code, run it, and immediately see the effect.

#### Multi‑Framework Literacy

- Position QCanvas IDE as a tool for **teaching concepts, not just one SDK**.
- Show that different framework syntaxes all compile to the same OpenQASM 3.0 representation.
- Reinforces that core ideas like superposition, entanglement, and algorithms (e.g., teleportation) are framework‑independent.

### 4. System Architecture (High‑Level)

The paper presents a three‑layer architecture:

1. **Frontend (Next.js 14 + React 18 + TypeScript)**
   - Monaco code editor with Python syntax highlighting.
   - Results pane with multiple tabs (Stats, Console, Errors, Histogram, Output).
   - Sidebar with framework and simulator controls.
   - Top bar with navigation, authentication, settings, and “Compile”/“Run” actions.

2. **Backend (FastAPI)**
   - REST endpoints for:
     - conversion (`/api/converter/convert`),
     - simulation (`/api/simulator/execute`),
     - health checks.
   - WebSocket endpoint (`/ws`) for real‑time progress updates.
   - Pydantic models for validation and automatic OpenAPI docs.

3. **Quantum Processing Layer**
   - Secure AST‑based parsers for Qiskit, Cirq, PennyLane.
   - Unified Circuit AST + QASM3Builder for OpenQASM 3.0.
   - QSim quantum simulator backends (Cirq, Qiskit, PennyLane) with configurable shots.

### 5. Key Features Described

#### Authentication and User Management

- User registration and login with persistent sessions (localStorage).
- Demo account (`demo@qcanvas.dev`) for instant access.
- Conditional UI (login/logout views, redirects) based on auth status.
- Prepared for role‑based access (e.g., future instructor vs. student features).

#### Keyboard Shortcuts

- 10+ shortcuts covering:
  - Save, new file, toggle sidebar, toggle results pane.
  - Find / find+replace.
  - Toggle theme.
  - Run/compile circuit.
  - Switch between file tabs.
- Cross‑platform (Ctrl on Windows/Linux, Cmd on macOS) with proper event cleanup.

#### Example System with Smart Loading

- Example cards on the home page show title, framework, difficulty, and description.
- **Auth‑aware flow**:
  - If logged in: example is loaded directly into the editor.
  - If not: example code is stored in session, user is redirected to login, then code auto‑loads after login.
- Examples span all three frameworks for several algorithms, enabling comparative learning.

#### File Management and Templates

- Multi‑file workspace (tabs).
- Auto‑loaded **initial files**:
  - Bell State (Cirq),
  - Deutsch–Jozsa (Qiskit),
  - Grover’s (PennyLane).
- Additional **templates** via modal:
  - Teleportation (Qiskit),
  - QRNG (Cirq),
  - XOR Demo (PennyLane),
  - QML XOR (PennyLane).
- Auto naming for new files, custom delete confirmation modals, click‑outside‑to‑close behavior.

#### Settings and Preferences

- Persistent user preferences:
  - Dark/light theme.
  - Auto‑save.
  - Format‑on‑save.
- Stored in localStorage, loaded on each session.

#### Results Visualization and Analysis

- **Stats tab**:
  - Gate count, circuit depth, qubit count.
  - Execution time, memory, CPU utilization, estimated fidelity.
  - Color‑coded cards (green/yellow/red) for quick status insight.
- **Histogram tab**:
  - Chart.js bar charts for measurement outcomes with percentages and progress bars.
- **Console tab**:
  - Detailed logs: framework detection, parsing, analysis, QASM generation, simulation.
- **Errors tab**:
  - Human‑readable messages plus code snippets, line numbers, and suggested fixes.
- **Output tab**:
  - Raw QASM and raw simulation results (counts, metadata).

### 6. Hybrid Execution Model

The paper explains three execution modes:

1. **Compile Only**
   - Convert code to OpenQASM 3.0 without running.
   - Ideal for teaching QASM syntax and understanding compilation.

2. **Full Execute**
   - Compile to QASM and simulate via QSim.
   - Supports multiple backends and shot counts; results appear in the histogram and stats.

3. **Hybrid Execute**
   - Runs user Python code in a sandbox, with access to:
     - `qcanvas.compile()` for framework → QASM,
     - `qsim.run()` for QASM → simulation.
   - Captures `print()` output into the IDE’s Output tab.
   - Enforces strict security: blocked dangerous imports, no file/network access, time and memory limits.

### 7. Educational Use Cases Highlighted

The paper walks through four main teaching scenarios:

1. **Introductory quantum computing course**
   - Students open Bell state, compile and run, view QASM and histogram, and then modify the circuit to see direct effects.

2. **Cross‑framework comparison lab**
   - Students load teleportation in Qiskit, Cirq, and PennyLane and compare:
     - framework code,
     - generated QASM,
     - simulation results.

3. **Research algorithm development**
   - Researchers iterate on VQE/QAOA circuits, using hybrid execution, measurement statistics, and QASM exports.

4. **Quantum ML workshop**
   - Participants use QML XOR and other QML examples to explore variational quantum models with PennyLane, backed by QCanvas compile/execute pipeline.

### 8. Evaluation and Deployment

- **Testing:** Describes a 100‑test suite (unit + integration) with 100% pass rate on implemented features (44 Iteration I features, all Iteration II features, 105 passing tests total in QCanvas).
- **Performance:** Documents sub‑50 ms compilation times, sub‑2s simulation for 1024‑shot circuits, $<$3 s initial page load, and low WebSocket latency.
- **Deployment:** Shows how to deploy via Docker Compose (backend, frontend, DB, Redis, Nginx, Prometheus, Grafana) and describes easy classroom setup.

### 9. Main Contributions Claimed by the Paper

1. A **feature‑complete, web‑based quantum IDE** that combines multi‑framework support, QASM 3 compilation, and multi‑backend simulation.\n2. A **carefully designed educational UX** (progressive disclosure, example scaffolding, multi‑framework comparison, rich feedback) tailored to learners while still supporting research workflows.\n3. An integrated **hybrid execution and visualization stack** that provides immediate, interpretable feedback (QASM, histograms, stats, detailed errors).\n4. An initial **evaluation of correctness and performance**, plus a roadmap for future user studies and pedagogical assessment.

