## Literature Review: Model-Driven Quantum Code Generation and LLM-Augmented Forward Engineering

### Scope and Alignment
This review focuses on forward engineering for hybrid classical–quantum software using model-driven engineering (MDE) and large language models (LLMs), aligned to QCanvas priorities: OpenQASM 3.0 as IR, framework unification (Cirq, Qiskit, PennyLane), simulation-first, and education-friendly UX.

### Core Papers

#### Code generation for classical–quantum systems modeled in UML (Springer, 2025)
- **What**: Proposes forward engineering from extended UML models to hybrid source code.
- **How**: Model-to-Text (M2T) transformations using Epsilon Generation Language (EGL) generating Python (classical) + Qiskit (quantum). Uses UML extensions to encode classical–quantum interactions.
- **Results**: Multi-case study (7 systems). Effectiveness measured via precision/recall/F1 and CodeBLEU; efficiency also reported. Concludes MDE can complete modernization by covering forward engineering.
- **Relevance to QCanvas**: Confirms viability of rules-based generation; informs metrics and validation; emphasizes hybrid orchestration constructs.
- **Link**: [Springer article](https://link.springer.com/article/10.1007/s10270-024-01259-w)

#### Model-Driven Quantum Code Generation Using LLMs and Retrieval-Augmented Generation (arXiv, 2025)
- **What**: Uses LLM + RAG to transform UML instances into Qiskit Python code.
- **How**: Curates Qiskit exemplars from public repos into retrieval index; prompt engineering references UML instance; LLM synthesizes target code.
- **Results**: Reports substantial CodeBLEU gains (up to ~4×) with engineered prompts + retrieval; improved consistency of generated code.
- **Relevance to QCanvas**: Motivates LLM+RAG companion to rules-based M2T; suggests retrieval quality and prompt structure as key levers.
- **Link**: [arXiv:2508.21097](https://arxiv.org/abs/2508.21097)

### Adjacent and Supporting References
- **IBM classical feedforward & control flow in Qiskit**: Patterns for hybrid control useful in emitted code. [Docs](https://docs.quantum.ibm.com/build/classical-feedforward-and-control-flow)
- **EGL Python templates**: Practical M2T examples akin to the Springer approach. [GitHub](https://github.com/ivyncm/PythonGenerator/tree/main/EGLtemplates)
- **QuAntiL Circuit Transformer**: Lifecycle tooling for circuit transformation, informs integration patterns. [Guide](https://quantil.readthedocs.io/en/latest/user-guide/circuit-transformer/)
- **Microsoft QIR overview**: Alternative IR perspective; reinforces IR-centric pipelines analogous to QCanvas with OpenQASM 3.0. [Post](https://devblogs.microsoft.com/qsharp/introducing-quantum-intermediate-representation-qir/)

### Comparative Synthesis
- **Specification source**: Both assume structured models (UML). Springer formalizes with EGL; arXiv leverages LLMs with retrieval.
- **Target artifacts**: Python + Qiskit; QCanvas should emphasize OpenQASM 3.0 as primary IR and then generate per framework.
- **Validation**: Springer employs precision/recall/F1 + CodeBLEU; arXiv emphasizes CodeBLEU gains. For QCanvas, add semantic validation via OpenQASM 3.0 simulation equivalence.
- **Scalability**: M2T is deterministic and maintainable; LLM+RAG offers breadth with curation and guardrails.

### Metrics and Evaluation (Recommended)
- **Syntactic/semantic quality**: CodeBLEU for synthesis; static checks for imports/API usage.
- **Element coverage**: Precision/recall/F1 for required constructs (gates, measures, control flow).
- **Functional equivalence**: Simulate OpenQASM 3.0 on statevector backend; compare distributions/state overlaps.
- **Efficiency**: Wall-clock latency, token/cost (LLM), and throughput for batch generation.

### Risks and Mitigations
- **Scope creep**: Exclude pulse/timing/hardware-specific constructs; constrain prompts and templates accordingly.
- **LLM hallucinations**: Require retrieval-grounded prompts; post-generate verification via OpenQASM 3.0 round-trip and simulation.
- **Template brittleness**: Keep M2T small and modular; validate with integration tests per construct.

### Takeaways for QCanvas
- Adopt a dual-path strategy: rules-based M2T for core coverage; LLM+RAG for rapid expansion and examples.
- Make OpenQASM 3.0 the verification backbone: all generated framework code must compile or transpile to QASM3 and pass semantic checks.
- Provide educational transparency: show UML → code → QASM → simulate, with provenance of retrieved snippets and prompts.


