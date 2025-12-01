# QCanvas Setup Guide

This guide will help you set up and run the complete QCanvas system with the frontend connected to the FastAPI backend and quantum converters.

## Prerequisites

- Python 3.9+ 
- Node.js 18+
- npm or yarn
- Virtual environment tools (venv or conda)

## Installation Steps

### 1. Install Python Dependencies

Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv qcanvas_env

# Activate (Windows)
qcanvas_env\Scripts\activate

# Activate (macOS/Linux)
source qasm_env/bin/activate
```

Install Python packages:

```bash
# Install backend dependencies
pip install -r requirements.txt

# Install quantum computing frameworks
pip install qiskit cirq pennylane numpy
```

### 2. Install Frontend Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Return to project root
cd ..
```

### 3. Environment Configuration

Set up environment variables for proper Python path:

```bash
# Windows
set PYTHONPATH=%CD%

# macOS/Linux
export PYTHONPATH=$(pwd)
```

Or create a `.env` file in the project root:
```
PYTHONPATH=.
```

### 4. Configure Frontend API Base URL

Create `frontend/.env.local` (if it doesn't exist):
```
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

## Running the System

### Method 1: Run Both Services Separately

#### Terminal 1 - Backend (FastAPI)
```bash
# Activate Python environment
# Windows: qcanvas_env\Scripts\activate
# macOS/Linux: source qcanvas_env/bin/activate

# Navigate to backend directory
cd backend

# Start the FastAPI server
python -m app.main

# Or alternatively:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 2 - Frontend (Next.js)
```bash
# Navigate to frontend directory
cd frontend

# Start the development server
npm run dev

# Or with yarn:
yarn dev
```

### Method 2: Using Docker (if docker-compose.yml is configured)
```bash
docker-compose up
```

## Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Testing the Integration

### 1. Test Conversion Features

1. Open the frontend at http://localhost:3000
2. Create a new file with a quantum framework code:

**Qiskit Example:**
```python
from qiskit import QuantumCircuit

def get_circuit():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc
```

**Cirq Example:**
```python
import cirq

def get_circuit():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.H(q0),
        cirq.CNOT(q0, q1)
    )
    return circuit
```

**PennyLane Example:**
```python
import pennylane as qml

def get_circuit():
    dev = qml.device('default.qubit', wires=2)
    
    @qml.qnode(dev)
    def circuit():
        qml.Hadamard(wires=0)
        qml.CNOT(wires=[0, 1])
        return qml.expval(qml.PauliZ(0))
    
    return circuit
```

3. Click "Compile to QASM" to convert the code to OpenQASM 3.0
4. Click "Run" to execute the circuit

### 2. Test QASM Execution

1. Create a new file with `.qasm` extension
2. Add OpenQASM code:
```qasm
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;

h q[0];
cx q[0], q[1];
```

3. Click "Run" to execute the QASM code directly

## API Endpoints

The FastAPI backend provides these endpoints:

- `POST /api/converter/convert` - Convert framework code to QASM
- `GET /api/converter/frameworks` - Get supported frameworks
- `POST /api/converter/validate` - Validate framework code
- `POST /api/simulator/execute` - Execute QASM code
- `GET /api/simulator/backends` - Get available simulation backends
- `GET /api/health` - Health check

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure PYTHONPATH is set correctly
2. **Connection Refused**: Check that both frontend and backend are running
3. **CORS Errors**: Verify the API base URL in frontend configuration
4. **Module Not Found**: Install missing Python packages with pip

### Debug Mode

Start the backend with debug logging:
```bash
cd backend
python -c "
import sys
print('Python path:', sys.path)
try:
    from quantum_converters.converters.qiskit_to_qasm import convert_qiskit_to_qasm3
    print('✓ Quantum converters imported successfully')
except Exception as e:
    print('✗ Import error:', e)
"
```

### Logs

- Backend logs: Check console output where FastAPI is running
- Frontend logs: Check browser developer console (F12)

## Example Workflow

1. Start both backend and frontend servers
2. Open http://localhost:3000 in your browser
3. Create a new file with Qiskit/Cirq/PennyLane code
4. Use "Compile to QASM" to convert to OpenQASM 3.0
5. Use "Run" to execute the circuit and see results
6. View execution results in the console or results panel

## Next Steps

- Enhance the results panel to display simulation results
- Add more sophisticated quantum algorithms
- Implement additional backends and noise models
- Add circuit visualization features

For more help, check the documentation at `/docs` or the examples at `/examples`.
