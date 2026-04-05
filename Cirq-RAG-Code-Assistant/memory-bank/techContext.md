# Tech Context

## Languages & Frameworks
- Python 3.11+
- Cirq (quantum computing)
- PyTorch 2.1+ (primary ML framework)
- PyTorch CUDA for GPU optimization
- Sentence Transformers for embeddings
- FAISS (or equivalent) for vector search

## Agent Pipeline Architecture
- Sequential pipeline with conditional stages
- Orchestrator manages agent execution order
- Parameters control Validator/Optimizer enablement
- Educational Agent runs independently (parallel capable)

## Dev Setup
- Linux Ubuntu 20.04+ (recommended)
- pip + venv
- Pre-commit hooks (black, isort, flake8, mypy optional)
- CUDA support for PyTorch

## Constraints
- Reproducibility; deterministic seeds for simulation
- GPU memory management for PyTorch
- Agent pipeline order must be maintained

Future enhancement (post-project):
- FastAPI for QCanvas integration
- QCanvas integration requirements
