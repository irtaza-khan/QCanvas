# Product Context

## Why
Lower the barrier to Cirq quantum programming by pairing generation with education and validation through a sequential agent pipeline.

## Users
- Students learning Cirq and quantum algorithms
- Researchers prototyping circuits with correctness checks

## Experience
- Ask in natural language; receive Cirq code via sequential agent pipeline
- **Designer** generates code, optional **Validator** checks it, optional **Optimizer** improves it
- **Final Validator** ensures quality before output
- **Educational Agent** (optional, independent) provides explanations focused on user's prompt
- Templates for VQE, QAOA, teleportation, Grover, QFT
- GPU-accelerated processing with PyTorch CUDA

## Agent Flow Options
Users can configure:
- Validation enabled/disabled (conditional Validator)
- Optimization enabled/disabled (conditional Optimizer)
- Educational explanations enabled/disabled (independent Educational Agent)

Future enhancement (post-project):
- QCanvas users integrating with existing quantum simulator
- Real-time integration with QCanvas for circuit visualization
