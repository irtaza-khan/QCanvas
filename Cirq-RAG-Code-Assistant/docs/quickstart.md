# Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide will help you get up and running with Cirq-RAG-Code-Assistant quickly.

## 📦 Installation

### Option 1: Quick Install
```bash
pip install cirq-rag-code-assistant
```

### Option 2: Development Install
```bash
git clone https://github.com/umerfarooq/cirq-rag-code-assistant.git
cd cirq-rag-code-assistant
pip install -e ".[dev]"
```

## 🎯 Basic Usage

### 1. Command Line Interface

#### Generate Quantum Code
```bash
# Generate a simple VQE circuit
cirq-rag generate "Create a VQE circuit for H2 molecule with 4 qubits"

# Generate QAOA for MaxCut
cirq-rag generate "Create a QAOA circuit for MaxCut problem on 3 qubits"

# Generate Grover's algorithm
cirq-rag generate "Implement Grover's search algorithm for 2 qubits"
```

#### Interactive Mode
```bash
# Start interactive session
cirq-rag interactive

# In interactive mode:
> Create a quantum teleportation circuit
> Optimize the circuit for depth
> Explain how quantum teleportation works
```

### 2. Python API

#### Basic Code Generation
```python
from cirq_rag_code_assistant import DesignerAgent, Orchestrator

# Initialize the system
orchestrator = Orchestrator()

# Generate code
result = orchestrator.generate_code(
    description="Create a VQE circuit for H2 molecule",
    algorithm="vqe",
    qubits=4,
    layers=2
)

print("Generated Code:")
print(result.code)
print("\nExplanation:")
print(result.explanation)
```

#### Advanced Usage
```python
from cirq_rag_code_assistant import (
    DesignerAgent, 
    OptimizerAgent, 
    ValidatorAgent,
    EducationalAgent
)

# Initialize agents
designer = DesignerAgent()
optimizer = OptimizerAgent()
validator = ValidatorAgent()
educational = EducationalAgent()

# Generate initial code
code = designer.generate_code("VQE for H2 molecule, 4 qubits")

# Optimize the circuit
optimized_code = optimizer.optimize(code)

# Validate the code
validation_result = validator.validate(optimized_code)

# Get educational explanation
explanation = educational.explain(optimized_code, "VQE algorithm")

print(f"Original depth: {code.depth}")
print(f"Optimized depth: {optimized_code.depth}")
print(f"Validation: {'PASSED' if validation_result.success else 'FAILED'}")
```

### 3. Web API

#### Start the Server
```bash
# Start development server
cirq-rag server

# Or with custom settings
cirq-rag server --host 0.0.0.0 --port 8080
```

#### API Usage
```bash
# Generate code via API
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Create a VQE circuit for H2 molecule",
    "algorithm": "vqe",
    "parameters": {
      "qubits": 4,
      "layers": 2
    }
  }'
```

#### Python Requests
```python
import requests

# API endpoint
url = "http://localhost:8000/api/v1/generate"

# Request payload
payload = {
    "description": "Create a QAOA circuit for MaxCut",
    "algorithm": "qaoa",
    "parameters": {
        "qubits": 3,
        "p": 1
    }
}

# Make request
response = requests.post(url, json=payload)
result = response.json()

print("Generated Code:")
print(result["code"])
print("\nOptimization Results:")
print(result["optimization"])
```

## 🧪 Examples

### Example 1: VQE Circuit
```python
from cirq_rag_code_assistant import Orchestrator

orchestrator = Orchestrator()

# Generate VQE circuit
result = orchestrator.generate_code(
    description="VQE circuit for H2 molecule optimization",
    algorithm="vqe",
    qubits=4,
    layers=2,
    optimizer="COBYLA"
)

# The result contains:
# - result.code: Generated Cirq code
# - result.explanation: Educational explanation
# - result.optimization: Performance metrics
# - result.validation: Test results
```

### Example 2: QAOA Optimization
```python
# Generate QAOA circuit
result = orchestrator.generate_code(
    description="QAOA for MaxCut problem",
    algorithm="qaoa",
    qubits=4,
    p=2,
    graph_type="random"
)

# Optimize further
optimized = orchestrator.optimize_circuit(
    circuit=result.code,
    target_metrics=["depth", "gate_count"],
    optimization_level="aggressive"
)
```

### Example 3: Educational Content
```python
# Get detailed explanation
explanation = orchestrator.explain_algorithm(
    algorithm="grover",
    level="intermediate",
    include_visualization=True
)

print("Algorithm Overview:")
print(explanation.overview)
print("\nStep-by-step Process:")
for step in explanation.steps:
    print(f"{step.number}. {step.description}")
    print(f"   Code: {step.code}")
```

## 🔧 Configuration

### Basic Configuration
Create a `config.yaml` file:

```yaml
# Basic configuration
system:
  log_level: INFO
  workers: 4

agents:
  designer:
    max_retries: 3
    timeout: 30
  optimizer:
    optimization_level: "balanced"
  validator:
    simulation_timeout: 60

rag:
  vector_store:
    similarity_threshold: 0.7
  knowledge_base:
    update_interval: 3600
```

### Environment Variables
```bash
# Set environment variables
export CIRQ_RAG_LOG_LEVEL=INFO
export CIRQ_RAG_DEBUG=false
export OPENAI_API_KEY=your_api_key_here
```

## 📊 Understanding Results

### Code Generation Result
```python
result = orchestrator.generate_code("VQE for H2")

# Access different parts of the result
print("Generated Code:")
print(result.code)

print("\nEducational Explanation:")
print(result.explanation)

print("\nPerformance Metrics:")
print(f"Circuit Depth: {result.metrics.depth}")
print(f"Gate Count: {result.metrics.gate_count}")
print(f"Two-qubit Gates: {result.metrics.two_qubit_gates}")

print("\nValidation Results:")
print(f"Syntax Check: {result.validation.syntax_valid}")
print(f"Simulation: {result.validation.simulation_success}")
print(f"Tests Passed: {result.validation.tests_passed}")
```

### Optimization Results
```python
optimized = orchestrator.optimize_circuit(result.code)

print("Optimization Results:")
print(f"Original Depth: {optimized.original_metrics.depth}")
print(f"Optimized Depth: {optimized.optimized_metrics.depth}")
print(f"Improvement: {optimized.improvement_percentage:.1f}%")
print(f"Optimization Time: {optimized.optimization_time:.2f}s")
```

## 🎓 Learning Resources

### Built-in Tutorials
```bash
# List available tutorials
cirq-rag tutorials list

# Run a tutorial
cirq-rag tutorials run vqe-basics

# Interactive tutorial
cirq-rag tutorials interactive grover-algorithm
```

### Educational Content
```python
# Get learning materials
materials = orchestrator.get_learning_materials(
    topic="quantum_algorithms",
    level="beginner"
)

for material in materials:
    print(f"Title: {material.title}")
    print(f"Type: {material.type}")
    print(f"Description: {material.description}")
    print("---")
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Import Error
```python
# If you get import errors
try:
    from cirq_rag_code_assistant import Orchestrator
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure the package is installed: pip install cirq-rag-code-assistant")
```

#### 2. API Key Missing
```python
# Check if API key is set
import os
if not os.getenv("OPENAI_API_KEY"):
    print("Please set OPENAI_API_KEY environment variable")
```

#### 3. Server Not Starting
```bash
# Check if port is available
netstat -an | grep 8000

# Try different port
cirq-rag server --port 8080
```

### Debug Mode
```bash
# Enable debug logging
export CIRQ_RAG_DEBUG=true
cirq-rag generate "test circuit" --verbose
```

## 📚 Next Steps

### 1. Explore Algorithms
- Try different quantum algorithms (VQE, QAOA, Grover, QFT)
- Experiment with different parameters
- Compare optimization results

### 2. Learn the API
- Read the [API Documentation](api/README.md)
- Try the [Examples](examples/README.md)
- Explore the [Agent System](agents/README.md)

### 3. Advanced Usage
- Customize the knowledge base
- Add your own algorithms
- Integrate with your workflow

### 4. Contribute
- Check out the [Contributing Guide](contributing.md)
- Report issues on [GitHub](https://github.com/umerfarooq/cirq-rag-code-assistant/issues)
- Join the community discussions

## 🆘 Getting Help

### Documentation
- [Installation Guide](installation.md)
- [Architecture Guide](architecture.md)
- [API Reference](api/README.md)
- [Examples](examples/README.md)

### Community
- [GitHub Issues](https://github.com/umerfarooq/cirq-rag-code-assistant/issues)
- [GitHub Discussions](https://github.com/umerfarooq/cirq-rag-code-assistant/discussions)
- [Discord Community](https://discord.gg/cirq-rag)

### Support
- Email: umerfarooqcs0891@gmail.com
- Documentation: [cirq-rag-code-assistant.readthedocs.io](https://cirq-rag-code-assistant.readthedocs.io)

---

*Ready to dive deeper? Check out the [Architecture Guide](architecture.md) to understand how the system works, or explore [Usage Examples](examples/README.md) for more complex scenarios.*
