## QCanvas Action Plan: Forward Engineering from UML with M2T and LLM+RAG

### Objectives
- Integrate a forward-engineering path that converts UML instances to OpenQASM 3.0 and framework code (Qiskit first), aligned to QCanvas scope.
- Establish an LLM+RAG companion pipeline for code synthesis with automated verification via OpenQASM 3.0 simulation.

### Deliverables (Milestone 1–2 weeks)
1. Minimal UML → OpenQASM 3.0 emitter (template- or codegen-based) for Bell, GHZ, and QAOA depth-1.
2. RAG pipeline using `Generative AI Model Files/rag/` to ingest curated Qiskit/OpenQASM exemplars and generate Qiskit code from UML JSON instances.
3. Evaluation harness: CodeBLEU, precision/recall/F1 on expected constructs, and semantic simulation checks.
4. Demo notebook: end-to-end run UML → code → QASM → simulate.

### Architecture Integration
```
UML Instance → (Path A) M2T Templates → Qiskit & OpenQASM 3.0
           ↘ (Path B) LLM+RAG Synthesis → Qiskit → QASM3 export
                                 ↓
                  QCanvas Validation & Simulation (OpenQASM 3.0)
```

### Implementation Steps
1) Modeling Input
- Define a minimal JSON schema for UML instances (class names, operations, quantum steps), or parse from UML XMI with a small adapter.
- Constrain features to Iteration I/II OpenQASM constructs (exclude timing, pulse, hardware-specific).

2) Rules-based M2T Baseline
- Implement a small emitter (Python + Jinja2) mapping UML JSON → OpenQASM 3.0 (Bell, GHZ, QAOA depth-1) and Qiskit code.
- Keep templates granular: gates, measurement, simple classical control.
- Add unit tests per construct; integration tests per circuit.

3) LLM+RAG Synthesis
- Use `rag/ingest.py` to index curated exemplars (Qiskit, OpenQASM 3.0) with metadata tags (algorithm, gates, measurement, control).
- Implement a generation command in `rag/cli.py` that:
  - Retrieves top-k exemplars
  - Constructs a structured prompt with UML JSON and constraints
  - Generates Qiskit code
  - Exports to OpenQASM 3.0 via Qiskit transpiler

4) Automated Verification
- Static checks: import/API usage; parsable OpenQASM 3.0.
- Semantic checks: run statevector simulation and compare to expected distributions/state overlaps.
- Report metrics: CodeBLEU; precision/recall/F1 for required constructs; latency/cost.

5) Frontend/UX Hook
- Add a prototype panel in the IDE to show: UML JSON → Qiskit code → OpenQASM 3.0 → simulation results.
- Stream generation/verification steps via WebSocket for transparency.

### Evaluation Protocol
- Benchmarks: Bell, GHZ, QFT-3 (optional), QAOA (p=1), VQE (toy Hamiltonian) with small qubit counts.
- Metrics: CodeBLEU; precision/recall/F1 on constructs; equivalence under statevector; wall-clock/token costs.
- Ablations: RAG on/off; prompt variants; template-only vs LLM+RAG.

### Guardrails
- Filtering: exclude pulse-level/timing/hardware APIs during retrieval and prompt construction.
- Limits: qubits ≤ 8 for demo; shots/timeouts aligned with `techContext.md`.
- Fallbacks: if LLM output fails verification, revert to M2T baseline.

### References
- Springer paper (EGL M2T): [link.springer.com](https://link.springer.com/article/10.1007/s10270-024-01259-w)
- LLM+RAG model-driven generation: [arXiv:2508.21097](https://arxiv.org/abs/2508.21097)
- IBM classical feedforward: [docs.quantum.ibm.com](https://docs.quantum.ibm.com/build/classical-feedforward-and-control-flow)
- EGL templates: [github.com/ivyncm/PythonGenerator](https://github.com/ivyncm/PythonGenerator/tree/main/EGLtemplates)
- QuAntiL Circuit Transformer: [quantil.readthedocs.io](https://quantil.readthedocs.io/en/latest/user-guide/circuit-transformer/)


