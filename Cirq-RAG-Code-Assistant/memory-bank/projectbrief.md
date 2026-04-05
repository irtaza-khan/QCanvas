# Project Brief

Cirq-RAG-Code-Assistant is a research-grade system to generate and explain Google Cirq quantum computing code using a hybrid Retrieval-Augmented Generation (RAG) + Multi-Agent architecture, with tool augmentation and agentic reinforcement learning.

## Agent Pipeline
```
Designer (Always) → [Validator] → [Optimizer ⟷ Validator Loop] → Final Validator (Always)
Educational Agent: Independent, runs in parallel when requested
```

## Core Goals
- Generate syntactically correct, executable Cirq code from natural language
- Provide step-by-step educational explanations (via independent Educational Agent)
- Optimize circuits (depth, two-qubit gates) via conditional Optimizer Agent
- Validate via simulation and tests (Validator Agent + Final Validator)
- Establish datasets, metrics, and benchmarks
- Leverage PyTorch CUDA GPU for performance optimization

## Key Features
- **Designer Agent**: Always runs first, generates initial code
- **Validator/Optimizer**: Conditional stages, can be enabled/disabled
- **Final Validator**: Always runs last, ensures quality
- **Educational Agent**: Independent, focused on user prompt explanations

Future enhancement (post-project):
- QCanvas integration for real-time circuit visualization and execution
