# Hybrid Execution Results API

## Overview

When executing quantum circuits in **Hybrid Execution Mode**, the `qsim.run()` function returns a `SimulationResult` object that provides comprehensive access to simulation data, performance metrics, and circuit information.

This document describes all available attributes and methods on the `result` object returned by `qsim.run()`.

## Basic Usage

```python
import cirq
from qcanvas import compile
import qsim

# Create and compile circuit
q = cirq.LineQubit.range(2)
circuit = cirq.Circuit([
    cirq.H(q[0]),
    cirq.CNOT(q[0], q[1]),
    cirq.measure(q[0], q[1], key='result')
])

qasm = compile(circuit, framework="cirq")

# Execute simulation
result = qsim.run(qasm, shots=1000, backend="cirq")

# Access result attributes
print(result.counts)
print(result.probabilities)
print(result.n_qubits)
```

## API Reference

### Available Functions

The hybrid execution environment provides the following functions:

#### `compile(circuit, framework=None)`

Compile a quantum circuit object to OpenQASM 3.0 format.

**Parameters:**
- `circuit` (Any): Circuit object from Cirq, Qiskit, or PennyLane
- `framework` (str, optional): Framework name (`"cirq"`, `"qiskit"`, `"pennylane"`). Auto-detected if not provided.

**Returns:**
- `str`: OpenQASM 3.0 code as a string

**Example:**
```python
import cirq
from qcanvas import compile

# Create circuit
q = cirq.LineQubit.range(2)
circuit = cirq.Circuit([
    cirq.H(q[0]),
    cirq.CNOT(q[0], q[1]),
    cirq.measure(q[0], q[1], key='result')
])

# Compile to QASM
qasm = compile(circuit, framework="cirq")
print(qasm)
```

#### `qsim.run(qasm_code, shots=1024, backend="cirq")`

Execute OpenQASM 3.0 code using QSim quantum simulator.

**Parameters:**
- `qasm_code` (str): OpenQASM 3.0 code to execute
- `shots` (int, optional): Number of measurement shots. Default: `1024`. Use `0` for exact statevector.
- `backend` (str, optional): Simulation backend. Options: `"cirq"`, `"qiskit"`, `"pennylane"`. Default: `"cirq"`

**Returns:**
- `SimulationResult`: Result object with counts, probabilities, and metadata

**Example:**
```python
import qsim

qasm = '''
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
h q[0];
cx q[0], q[1];
c[0] = measure q[0];
c[1] = measure q[1];
'''

# Execute with 1000 shots
result = qsim.run(qasm, shots=1000, backend="cirq")
print(result.counts)

# Get exact statevector (no measurement noise)
result_exact = qsim.run(qasm, shots=0, backend="cirq")
if result_exact.statevector:
    print(result_exact.statevector)
```

#### `compile_and_execute(circuit, framework=None, shots=1024, backend="cirq")`

Convenience function that compiles a circuit and executes it in a single call.

**Parameters:**
- `circuit` (Any): Circuit object from Cirq, Qiskit, or PennyLane
- `framework` (str, optional): Framework name. Auto-detected if not provided.
- `shots` (int, optional): Number of measurement shots. Default: `1024`
- `backend` (str, optional): Simulation backend. Default: `"cirq"`

**Returns:**
- `SimulationResult`: Result object with counts, probabilities, and metadata

**Example:**
```python
import cirq
from qcanvas import compile_and_execute

# Create circuit
q = cirq.LineQubit.range(2)
circuit = cirq.Circuit([
    cirq.H(q[0]),
    cirq.CNOT(q[0], q[1]),
    cirq.measure(q[0], q[1], key='result')
])

# Compile and execute in one call
result = compile_and_execute(circuit, framework="cirq", shots=1000)
print(result.counts)
print(result.probabilities)
```

### Printing Circuits

You can print circuit objects directly to see their structure:

#### Cirq Circuits

```python
import cirq

q = cirq.LineQubit.range(2)
circuit = cirq.Circuit([
    cirq.H(q[0]),
    cirq.CNOT(q[0], q[1]),
    cirq.measure(q[0], q[1], key='result')
])

# Print circuit representation
print(circuit)
# Output:
# 0: ───H───@───M('result')───
#           │
# 1: ───────X───M──────────────
```

#### Qiskit Circuits

```python
from qiskit import QuantumCircuit

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

# Print circuit representation
print(qc)
# Output:
#      ┌───┐     ┌─┐
# q_0: ┤ H ├──■──┤M├───
#      └───┘ │ ┌┴┐└╥┘
# q_1: ──────┼─┤M├─╫──
#            │ └╥┘ ║
# c: 2/══════╪══╬══╩═
#            └──╫───
#               ║
```

#### PennyLane Circuits

```python
import pennylane as qml

dev = qml.device('default.qubit', wires=2)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.expval(qml.PauliZ(0)), qml.expval(qml.PauliZ(1))

# Print circuit representation
print(qml.draw(circuit)())
# Output:
# 0: ──H──╭C──┤ ⟨Z⟩
# 1: ─────╰X──┤ ⟨Z⟩
```

### Complete Workflow Example

```python
import cirq
from qcanvas import compile, compile_and_execute
import qsim

# Step 1: Create circuit
q = cirq.LineQubit.range(2)
circuit = cirq.Circuit([
    cirq.H(q[0]),
    cirq.CNOT(q[0], q[1]),
    cirq.measure(q[0], q[1], key='result')
])

# Step 2: Print circuit (optional)
print("Circuit Structure:")
print(circuit)
print()

# Step 3: Compile to QASM
qasm = compile(circuit, framework="cirq")
print("Generated QASM:")
print(qasm)
print()

# Step 4: Execute simulation
result = qsim.run(qasm, shots=1000, backend="cirq")

# Step 5: Access results
print("Simulation Results:")
print(f"  Counts: {result.counts}")
print(f"  Probabilities: {result.probabilities}")
print(f"  Execution time: {result.execution_time}")

# Alternative: Compile and execute in one step
result2 = compile_and_execute(circuit, framework="cirq", shots=1000)
print(f"\nOne-step result: {result2.counts}")
```

## SimulationResult Attributes Reference

The `SimulationResult` object returned by `qsim.run()` and `compile_and_execute()` provides the following attributes:

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `counts` | `Dict[str, int]` | Measurement counts for each outcome | `{'00': 512, '11': 512}` |
| `probabilities` | `Dict[str, float]` | Probability of each measurement outcome | `{'00': 0.5, '11': 0.5}` |
| `statevector` | `List[complex]` | Full quantum statevector (only when `shots=0`) | `[0.707+0j, 0+0j, 0+0j, 0.707+0j]` |
| `n_qubits` | `int` | Number of qubits in the circuit | `2` |
| `shots` | `int` | Number of measurement shots executed | `1000` |
| `backend` | `str` | Backend used for simulation | `"cirq"` |
| `execution_time` | `str` | Total execution time (human-readable) | `"1.23ms"` |
| `simulation_time` | `str` | Time spent in quantum simulation | `"0.98ms"` |
| `memory_usage` | `str` | Memory consumed during simulation | `"45.2 MB"` |
| `cpu_usage` | `str` | CPU utilization during simulation | `"12.5%"` |
| `fidelity` | `float` | Simulation fidelity as percentage | `100.0` |
| `metadata` | `Dict[str, Any]` | Additional backend-specific metadata | `{'gate_count': 5}` |

### Quick Access Examples

```python
result = qsim.run(qasm, shots=1000, backend="cirq")

# Measurement data
print(result.counts)           # {'00': 498, '11': 502}
print(result.probabilities)    # {'00': 0.498, '11': 0.502}

# Circuit information
print(result.n_qubits)         # 2
print(result.shots)            # 1000
print(result.backend)          # "cirq"

# Performance metrics
print(result.execution_time)   # "1.23ms"
print(result.simulation_time)  # "0.98ms"
print(result.memory_usage)     # "45.2 MB"
print(result.cpu_usage)        # "12.5%"
print(result.fidelity)         # 100.0

# Additional data
print(result.metadata)         # {'gate_count': 5, ...}
```

## Result Object Attributes

### Measurement Data

#### `result.counts`
- **Type**: `Dict[str, int]`
- **Description**: Dictionary mapping measurement outcomes (binary strings) to their occurrence counts
- **Example**: `{'00': 512, '11': 512}`
- **Usage**:
  ```python
  result = qsim.run(qasm, shots=1000, backend="cirq")
  print(result.counts)  # {'00': 498, '11': 502}
  
  # Get count for specific state
  count_00 = result.counts.get('00', 0)
  
  # Get most likely state
  most_likely = max(result.counts, key=result.counts.get)
  ```

#### `result.probabilities`
- **Type**: `Dict[str, float]`
- **Description**: Dictionary mapping measurement outcomes to their probabilities (0.0 to 1.0)
- **Example**: `{'00': 0.5, '11': 0.5}`
- **Usage**:
  ```python
  result = qsim.run(qasm, shots=1000, backend="cirq")
  print(result.probabilities)  # {'00': 0.498, '11': 0.502}
  
  # Get probability for specific state
  prob_00 = result.probabilities.get('00', 0.0)
  
  # Calculate entropy or other statistics
  for state, prob in result.probabilities.items():
      print(f"P({state}) = {prob:.4f}")
  ```

#### `result.statevector`
- **Type**: `Optional[List[complex]]`
- **Description**: Full quantum statevector (only available when `shots=0` for exact state simulation)
- **Example**: `[0.7071067811865476+0j, 0+0j, 0+0j, 0.7071067811865476+0j]`
- **Usage**:
  ```python
  # Get exact statevector (no measurement noise)
  result = qsim.run(qasm, shots=0, backend="cirq")
  
  if result.statevector:
      print(f"Statevector has {len(result.statevector)} amplitudes")
      for i, amplitude in enumerate(result.statevector):
          prob = abs(amplitude)**2
          if prob > 0.001:
              state_binary = format(i, f'0{result.n_qubits}b')
              print(f"|{state_binary}⟩: {amplitude:.4f} (prob: {prob:.4f})")
  ```

### Circuit Information

#### `result.n_qubits`
- **Type**: `int`
- **Description**: Number of qubits in the simulated circuit
- **Example**: `2`
- **Usage**:
  ```python
  result = qsim.run(qasm, shots=1000, backend="cirq")
  print(f"Circuit has {result.n_qubits} qubits")
  ```

#### `result.shots`
- **Type**: `int`
- **Description**: Number of measurement shots executed
- **Example**: `1000`
- **Usage**:
  ```python
  result = qsim.run(qasm, shots=1000, backend="cirq")
  print(f"Executed {result.shots} shots")
  
  # Verify total counts match shots
  total_counts = sum(result.counts.values())
  assert total_counts == result.shots
  ```

### Backend Information

#### `result.backend`
- **Type**: `str`
- **Description**: Name of the backend used for simulation
- **Possible Values**: `"cirq"`, `"qiskit"`, `"pennylane"`
- **Example**: `"cirq"`
- **Usage**:
  ```python
  result = qsim.run(qasm, shots=1000, backend="cirq")
  print(f"Simulated using {result.backend} backend")
  
  # Backend-specific processing
  if result.backend == "cirq":
      # Cirq-specific analysis
      pass
  ```

### Performance Metrics

#### `result.execution_time`
- **Type**: `str`
- **Description**: Total execution time including compilation, simulation, and post-processing
- **Format**: Human-readable string (e.g., `"1.23ms"`, `"0.45s"`)
- **Example**: `"1.23ms"`
- **Usage**:
  ```python
  result = qsim.run(qasm, shots=1000, backend="cirq")
  print(f"Execution took {result.execution_time}")
  
  # Parse for numerical analysis
  time_str = result.execution_time.replace('ms', '').replace('s', '')
  time_ms = float(time_str) * (1000 if 's' in result.execution_time else 1)
  ```

#### `result.simulation_time`
- **Type**: `str`
- **Description**: Time spent in the actual quantum simulation (excluding compilation and post-processing)
- **Format**: Human-readable string (e.g., `"0.98ms"`, `"0.32s"`)
- **Example**: `"0.98ms"`
- **Usage**:
  ```python
  result = qsim.run(qasm, shots=1000, backend="cirq")
  print(f"Simulation took {result.simulation_time}")
  print(f"Total execution: {result.execution_time}")
  ```

#### `result.memory_usage`
- **Type**: `str`
- **Description**: Memory consumed during simulation
- **Format**: Human-readable string (e.g., `"45.2 MB"`, `"1.2 GB"`)
- **Example**: `"45.2 MB"`
- **Usage**:
  ```python
  result = qsim.run(qasm, shots=1000, backend="cirq")
  print(f"Memory used: {result.memory_usage}")
  ```

#### `result.cpu_usage`
- **Type**: `str`
- **Description**: CPU utilization during simulation
- **Format**: Human-readable string (e.g., `"12.5%"`, `"45.2%"`)
- **Example**: `"12.5%"`
- **Usage**:
  ```python
  result = qsim.run(qasm, shots=1000, backend="cirq")
  print(f"CPU usage: {result.cpu_usage}")
  ```

### Quality Metrics

#### `result.fidelity`
- **Type**: `float`
- **Description**: Simulation fidelity as a percentage (100.0 = perfect simulation)
- **Range**: `0.0` to `100.0`
- **Example**: `100.0`
- **Usage**:
  ```python
  result = qsim.run(qasm, shots=1000, backend="cirq")
  print(f"Simulation fidelity: {result.fidelity}%")
  
  if result.fidelity < 99.0:
      print("Warning: Low fidelity detected")
  ```

### Additional Data

#### `result.metadata`
- **Type**: `Dict[str, Any]`
- **Description**: Additional metadata from the simulation (backend-specific information)
- **Example**: `{'gate_count': 5, 'depth': 3, 'circuit_name': 'bell_state'}`
- **Usage**:
  ```python
  result = qsim.run(qasm, shots=1000, backend="cirq")
  
  # Access specific metadata
  if 'gate_count' in result.metadata:
      print(f"Circuit has {result.metadata['gate_count']} gates")
  
  # Print all metadata
  print("Metadata:", result.metadata)
  
  # Iterate over metadata
  for key, value in result.metadata.items():
      print(f"{key}: {value}")
  ```

## Result Object Methods

### `result.__repr__()`
- **Description**: String representation for debugging
- **Returns**: `str` - Compact representation with key stats
- **Example**: `"SimulationResult(counts={'00': 512, '11': 512}, shots=1000, backend='cirq', n_qubits=2)"`
- **Usage**:
  ```python
  result = qsim.run(qasm, shots=1000, backend="cirq")
  print(repr(result))
  ```

### `result.__str__()`
- **Description**: Human-readable string representation
- **Returns**: `str` - Formatted multi-line string with all key information
- **Usage**:
  ```python
  result = qsim.run(qasm, shots=1000, backend="cirq")
  print(str(result))
  # Output:
  # Simulation Result:
  #   Backend: cirq
  #   Qubits: 2
  #   Shots: 1000
  #   Counts: {'00': 512, '11': 512}
  #   Probabilities: {'00': 0.512, '11': 0.488}
  #   Execution Time: 1.23ms
  #   Fidelity: 100.0%
  ```

### `result.to_dict()`
- **Description**: Convert result to dictionary for JSON serialization
- **Returns**: `Dict[str, Any]` - Dictionary containing all result data
- **Usage**:
  ```python
  result = qsim.run(qasm, shots=1000, backend="cirq")
  result_dict = result.to_dict()
  
  # Can be serialized to JSON
  import json
  json_str = json.dumps(result_dict, indent=2)
  ```

## Complete Example

```python
import cirq
from qcanvas import compile
import qsim

# Create Bell state circuit
q = cirq.LineQubit.range(2)
circuit = cirq.Circuit([
    cirq.H(q[0]),
    cirq.CNOT(q[0], q[1]),
    cirq.measure(q[0], q[1], key='result')
])

# Compile to QASM
qasm = compile(circuit, framework="cirq")
print(f"Generated QASM:\n{qasm}\n")

# Execute simulation
result = qsim.run(qasm, shots=1000, backend="cirq")

# Complete analysis
print("=" * 60)
print("COMPLETE SIMULATION RESULT ANALYSIS")
print("=" * 60)

print(f"\n📊 Circuit Information:")
print(f"  • Qubits: {result.n_qubits}")
print(f"  • Backend: {result.backend}")
print(f"  • Shots: {result.shots}")

print(f"\n⚡ Performance Metrics:")
print(f"  • Execution time: {result.execution_time}")
print(f"  • Simulation time: {result.simulation_time}")
print(f"  • Memory usage: {result.memory_usage}")
print(f"  • CPU usage: {result.cpu_usage}")
print(f"  • Fidelity: {result.fidelity}%")

print(f"\n📈 Measurement Results:")
for state in sorted(result.counts.keys()):
    count = result.counts[state]
    prob = result.probabilities.get(state, 0.0)
    percentage = prob * 100
    print(f"  • |{state}⟩: {count} occurrences ({percentage:.2f}%)")

print(f"\n🔍 Additional Metadata:")
if result.metadata:
    for key, value in result.metadata.items():
        print(f"  • {key}: {value}")
else:
    print("  • No additional metadata")

print("=" * 60)
```

## Quick Reference Table

Complete reference of all `SimulationResult` attributes:

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `counts` | `Dict[str, int]` | Measurement counts for each outcome | `{'00': 512, '11': 512}` |
| `probabilities` | `Dict[str, float]` | Probability of each measurement outcome | `{'00': 0.5, '11': 0.5}` |
| `statevector` | `List[complex]` | Full quantum statevector (only when `shots=0`) | `[0.707+0j, 0+0j, 0+0j, 0.707+0j]` |
| `n_qubits` | `int` | Number of qubits in the circuit | `2` |
| `shots` | `int` | Number of measurement shots executed | `1000` |
| `backend` | `str` | Backend used for simulation | `"cirq"` |
| `execution_time` | `str` | Total execution time (human-readable) | `"1.23ms"` |
| `simulation_time` | `str` | Time spent in quantum simulation | `"0.98ms"` |
| `memory_usage` | `str` | Memory consumed during simulation | `"45.2 MB"` |
| `cpu_usage` | `str` | CPU utilization during simulation | `"12.5%"` |
| `fidelity` | `float` | Simulation fidelity as percentage | `100.0` |
| `metadata` | `Dict[str, Any]` | Additional backend-specific metadata | `{'gate_count': 5}` |

## Common Patterns

### Pattern 1: Statistical Analysis

```python
result = qsim.run(qasm, shots=1000, backend="cirq")

# Calculate statistics
total = sum(result.counts.values())
mean_count = total / len(result.counts)
max_count = max(result.counts.values())
min_count = min(result.counts.values())

print(f"Total measurements: {total}")
print(f"Average count per state: {mean_count:.2f}")
print(f"Max count: {max_count}, Min count: {min_count}")
```

### Pattern 2: State Probability Analysis

```python
result = qsim.run(qasm, shots=1000, backend="cirq")

# Find states with probability > threshold
threshold = 0.1
significant_states = {
    state: prob 
    for state, prob in result.probabilities.items() 
    if prob > threshold
}

print(f"States with probability > {threshold}:")
for state, prob in sorted(significant_states.items(), key=lambda x: x[1], reverse=True):
    print(f"  |{state}⟩: {prob:.4f} ({prob*100:.2f}%)")
```

### Pattern 3: Performance Benchmarking

```python
results = []
for i in range(10):
    result = qsim.run(qasm, shots=1000, backend="cirq")
    results.append(result)
    print(f"Run {i+1}: {result.execution_time}")

# Calculate average
times = [float(r.execution_time.replace('ms', '')) for r in results]
avg_time = sum(times) / len(times)
print(f"\nAverage execution time: {avg_time:.2f}ms")
```

### Pattern 4: Multiple Backend Comparison

```python
backends = ["cirq", "qiskit", "pennylane"]
comparison = {}

for backend in backends:
    result = qsim.run(qasm, shots=1000, backend=backend)
    comparison[backend] = {
        'execution_time': result.execution_time,
        'memory_usage': result.memory_usage,
        'fidelity': result.fidelity,
        'counts': result.counts
    }

print("Backend Comparison:")
for backend, data in comparison.items():
    print(f"\n{backend.upper()}:")
    print(f"  Time: {data['execution_time']}")
    print(f"  Memory: {data['memory_usage']}")
    print(f"  Fidelity: {data['fidelity']}%")
```

## Notes

- All attributes are read-only after the result is created
- The `statevector` attribute is only populated when `shots=0` (exact state simulation)
- Performance metrics may vary based on system load and circuit complexity
- Metadata contents depend on the backend used and may vary between frameworks
- Counts and probabilities are normalized to sum to 1.0 (within floating-point precision)

## Related Documentation

- [API Endpoints](./endpoints.md) - Complete API reference
- [Hybrid Execution Guide](../guides/hybrid-execution.md) - Guide to hybrid CPU-QPU execution
- [QASM Conversion](../guides/qasm-conversion.md) - OpenQASM 3.0 conversion documentation

