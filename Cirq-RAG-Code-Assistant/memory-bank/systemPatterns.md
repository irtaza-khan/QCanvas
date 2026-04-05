# System Patterns

## Agent Pipeline Architecture
- **Sequential Pipeline**: Designer → [Validator] → [Optimizer ⟷ Validator Loop] → Final Validator
- **Always Running**: Designer Agent (first), Final Validator Agent (last)
- **Conditional Stages**: Validator and Optimizer agents can be enabled/disabled via parameters
- **Optimization Loop**: Optimizer can loop back to Validator for iterative improvement

## Agent Roles
- **Designer Agent**: Generates initial Cirq code from natural language (always runs first)
- **Validator Agent**: Validates code syntax, compilation, simulation (conditional)
- **Optimizer Agent**: Reduces gate count/depth, improves circuit efficiency (conditional, can loop)
- **Final Validator**: Quality assurance before output (always runs last)
- **Educational Agent**: Provides explanations focused on user prompt (independent, runs parallel)

## Core System Patterns
- Hybrid RAG + Multi-Agent orchestration
- Tool-augmented reasoning with compile/simulate tools in-loop
- Knowledge base: curated Cirq snippets, NL descriptions, explanations
- PyTorch CUDA GPU optimization for neural network operations
- Evaluation: syntax correctness, execution success, educational ratings

Future enhancement (post-project):
- QCanvas integration: real-time circuit visualization and execution
