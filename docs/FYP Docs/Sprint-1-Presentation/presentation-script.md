## Slide 1 — Title
- One‑liner: “QCanvas unifies Qiskit, Cirq, and PennyLane into OpenQASM 3.0 for portable, testable quantum circuits.”
- Context: “This is our Sprint‑1 presentation (post‑proposal). We’ll show what we built, how we addressed the council’s feedback, and what’s next.”

## Slide 2 — Quantum Simulator Architecture (Two Pillars)
- Hook: “Think ‘compile’ vs ‘execute’.”
- Point: “QCanvas compiles multi‑framework code to OpenQASM 3.0; QSim executes on simulators.”
- Assurance: “Our compiler stands alone—OpenQASM runs on third‑party simulators even if QSim isn’t present.”

## Slide 3 — Overview of FYP Goals
- Frame: “Five goals guide Sprint‑1.”
- Bullets: “Translate to OpenQASM 3.0; unified IDE; hybrid path; education‑first; standards‑aligned.”
- Transition: “Now the council’s feedback—and the resolutions we delivered.”

## Slide 4 — Feedback: Why build this if big tech hasn’t?
- Core: “Vendors optimize for their own stacks; no neutral, cross‑framework pipeline exists.”
- Value: “We fill the interoperability gap for education/research with OpenQASM 3.0 at the center.”
- Proof: “Sprint‑1 delivers working converters and tests—feasibility demonstrated.”

## Slide 5 — Feedback: If QSim fails, how do you validate and what’s the value?
- Lead: “Standard IR → run anywhere.”
- Explain: “We export OpenQASM 3.0 and validate on existing simulators (Qiskit Aer, Cirq, PennyLane, cloud).”
- Outcome: “Compiler value stands on its own: conversion, QASM export, IDE, and reproducible learning—even without QSim.”

## Slide 6 — Feedback: Scope clarity (what’s included/excluded)
- Reference: “Complete scope lives in docs/project‑scope.md (also in Mid‑I Report).”
- Include: “Iteration‑I gates, ctrl@/inv@, measure/reset/barrier, core types, if/for, arithmetic/comparison, arrays/slices, I/O.”
- Exclude: “Pulse/timing, extern/hardware‑specific, memory/QEC, physical qubits ($i).”

## Slide 7 — Feedback: Domain‑specific challenges (per framework)
- Qiskit: “U/CX basis vs rotations; classical regs vs QASM bits; Pulse exists but out‑of‑scope.”
- Cirq: “Moments → linear order; device/qubit ordering; no classical regs; timing excluded.”
- PennyLane: “High‑level ops → decomposed; measurement handling differs; autodiff excluded.”
- Tie‑in: “Our compiler normalizes these differences into OpenQASM 3.0.”

## Slide 8 — Feedback: Accuracy and translator correctness
- Method: “Differential checks vs native simulators with fixed seeds.”
- Round‑trip: “Source ↔ QASM ↔ Source; assert thresholds.”
- Unit/grammar: “Per‑construct tests + static QASM validation.”
- Note: “Reports include gate counts, depth, qubits, and deltas.”

## Slide 9 — Metrics & Benchmarks (Compilation)
- Correctness: “L2<1e‑8; TVD<1e‑3; fidelity>0.999999 (small n).”
- Conformance: “100% Iteration‑I; reject excluded with clear diagnostics.”
- Performance: “p95<2s for ≤500 ops; p99<5s.”
- Stability: “Round‑trip ≥99%; deterministic formatting.”
- Coverage: “≥80%; property‑based fuzz within scope.”

## Slide 10 — Progress Since Proposal (Process)
- Theme: “Agile, modular, user‑centric; MVP each iteration; test every step.”
- Rhythm: “Foundation → Strength/Security → Intelligence/Extensibility → Integration/Insight.”
- Bridge: “Here’s what we actually shipped in Sprint‑1.”

## Slide 11 — Sprint‑1: The Foundation (Done)
- Delivered: “Web IDE + Backend API foundation.”
- Engine: “Dual‑path parsing (AST‑first, safe runtime fallback), gate mapping (20+ gates), multi‑framework support.”
- Usability: “Code highlighting, themes, multi‑file, real‑time conversion preview.”
- Summary: “Working, unified compiler and interface.”

## Slide 12 — Conversion Engine Details
- Gates: “Single‑qubit (X…RZ); Two‑qubit (CNOT, CZ, SWAP, CRX/CRY/CRZ); Multi‑qubit (Toffoli, Fredkin); U, phase.”
- Mapping: “Consistent parameter order; controlled/inverse semantics; broadcast and slicing handled.”
- Result: “Deterministic OpenQASM 3.0 output with stats.”

## Slide 13 — IDE Details
- Editor: “Monaco (VS Code engine), multi‑theme, multi‑file.”
- Feedback: “Live conversion preview; precise diagnostics.”
- Ready: “Built for examples, labs, and quick iteration.”

## Slide 14 — What’s Next (Sprint‑2 Preview)
- Depth: “Expand Iteration‑II where valuable; tighten error messages and docs.”
- Validation: “Broaden differential tests; add more golden circuits.”
- UX: “Improve examples, onboarding, and results panels.”
- Close: “We’re on track—compiler solid, scope clear, and validation measurable.”

## Optional Handoffs (if multi‑speaker)
- Umer: intro, architecture, scope.
- Hussain: IDE, UX, demo narrative.
- Irtaza: compiler internals, metrics, validation.

## 10‑Second Wrap (if asked to summarize)
- “We built a neutral, standards‑aligned compiler that turns diverse framework code into OpenQASM 3.0 and validates it using existing simulators. Sprint‑1 delivers a working IDE and translation engine with measurable correctness and clear scope.”

---

## 3‑Minute Timed Script (Slide‑by‑Slide)

### Slide 1 — Title (10s)
“This is Sprint‑1. We’re QCanvas: a compiler that unifies Qiskit, Cirq, and PennyLane into OpenQASM 3.0, with a working IDE and measurable validation.”

### Slide 2 — Architecture: Two Pillars (15s)
“Our system has two pillars: QCanvas compiles to OpenQASM; QSim executes. Even without QSim, our OpenQASM runs on existing simulators, so the compiler stands alone.”

### Slide 3 — Goals (10s)
“Goals: standards‑aligned translation, a unified IDE, hybrid pathway, and an education‑first experience grounded in OpenQASM 3.0.”

### Slide 4 — Why this platform? (15s)
“Vendors optimize for their own stacks. There’s no neutral, cross‑framework pipeline. We fill that interoperability gap for education and research.”

### Slide 5 — If QSim isn’t present (15s)
“We export OpenQASM and validate on Qiskit Aer, Cirq, and PennyLane. Value remains: conversion, standard export, IDE, and reproducible labs.”

### Slide 6 — Scope (15s)
“Scope is formalized: Iteration‑I gates, ctrl@/inv@, measure/reset, core types, arrays, if/for. Excluded: pulse, timing, extern/hardware‑specific, memory/QEC, physical qubits.”

### Slide 7 — Domain challenges (15s)
“We normalize differences: Qiskit’s U/CX vs rotations, Cirq’s moments and ordering, PennyLane’s high‑level ops and measurements—into a consistent OpenQASM output.”

### Slide 8 — Accuracy & correctness (15s)
“We do differential checks vs native simulators, round‑trip source↔QASM↔source, and static QASM validation to guarantee translator correctness.”

### Slide 9 — Metrics (15s)
“Targets: L2<1e‑8; TVD<1e‑3; fidelity>0.999999; 100% Iteration‑I conformance; p95<2s conversion; round‑trip≥99%; ≥80% coverage with property‑based fuzz.”

### Slide 10 — Process (10s)
“We work in short iterations: Foundation → Strength → Intelligence → Integration, testing continuously.”

### Slide 11 — Sprint‑1 shipped (20s)
“Delivered: IDE + backend foundation, dual‑path parsing, 20+ gate mappings, multi‑framework support, live conversion, and actionable diagnostics.”

### Slide 12 — Engine details (15s)
“Single‑ and two‑qubit gates plus multi‑qubit like Toffoli/Fredkin; consistent parameters, broadcast/slicing, and deterministic QASM with stats.”

### Slide 13 — IDE details (10s)
“Monaco editor, themes, multi‑file projects, real‑time preview—ready for examples and labs.”

### Slide 14 — What’s next (15s)
“Sprint‑2: broader differential tests and golden circuits, sharper diagnostics and docs, and UX improvements. The compiler is solid; we’re scaling validation.”

### Closing (5s)
“QCanvas makes quantum code portable, testable, and teachable. Thank you.”

