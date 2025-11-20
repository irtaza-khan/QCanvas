# qsim: Quantum Simulation Framework

**Status:** Active Development

This project is currently in the development phase. APIs and internal logic are subject to change.

qsim is a Python backend framework designed to bridge the gap between OpenQASM 3 and major quantum simulation libraries. It parses OpenQASM 3 code and translates it into executable circuits for Qiskit, Cirq, and PennyLane.

## Features

- **OpenQASM 3 Support:** Parses modern QASM 3 syntax including standard gates and measurements.
- **Multi-Backend:** Seamlessly switch simulation backends without changing your quantum code.
- **Unified API:** Provides specific RunArgs and SimResult classes for consistent inputs and outputs.
- **Type-Safe:** Built with Python type hints for better development experience.

## Installation

Since this project is not yet published to PyPI, follow these steps to set it up locally.

### 1. Clone the Repository

```bash
git clone https://github.com/Aneeq-Ahmed-Malik/QSim.git
cd qsim
```

### 2. Set up a Virtual Environment

It is highly recommended to work inside a virtual environment.

**Mac / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install the Package

Use the provided Makefile to install the project and its dependencies in editable mode.

```bash
make install
```

**Windows Users (No make installed?):** If the command above fails, use the standard pip command:

```bash
pip install -e .
```

## Usage

qsim uses a structured API. You define your configuration in RunArgs and receive a SimResult object.

### Running a Simulation

Create a file (e.g., main.py) and run the following code:

```python
from qsim import RunArgs, SimResult, run_qasm

# 1. Define OpenQASM 3.0 code
qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[2] q;
    bit[2] c;
    h q[0];
    cx q[0], q[1];
    c[0] = measure q[0];
    c[1] = measure q[1];
"""

# 2. Configure arguments
# Backends: "qiskit", "cirq", "pennylane"
args = RunArgs(
    qasm_input=qasm_code,
    backend="cirq",
    shots=1024
)

print(f"Running simulation on backend: {args.backend}...")

# 3. Execute
try:
    result: SimResult = run_qasm(args)

    # 4. Inspect Results
    print("\n--- Counts ---")
    print(result.counts)
    
    print("\n--- Metadata ---")
    print(result.metadata)

    # 5. Access the native circuit object (for drawing/advanced usage)
    print("\n--- Circuit Diagram ---")
    print(result.circuit)

except Exception as e:
    print(f"Simulation failed: {e}")
```

### Visualizing Circuits

The SimResult.circuit attribute contains the native circuit object (e.g., a qiskit.QuantumCircuit or cirq.Circuit).

## Development and Testing

This project includes a test suite to validate translations against all supported backends.

### Running Tests

We use pytest via the Makefile.

**Run All Tests:**

```bash
make test-all
```

**Test Specific Backends:**

```bash
make test-qiskit
make test-cirq
make test-pennylane
```


## License

Distributed under the MIT License. See LICENSE for more information.
