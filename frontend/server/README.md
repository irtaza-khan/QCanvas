# QCanvas Backend Integration

This directory contains the backend integration for the QCanvas Quantum Simulation Platform, including the quantum execution API and Python-based quantum circuit execution.

## Files

### `quantum_executor.py`
Python script that executes quantum circuits using Qiskit, Cirq, and other quantum frameworks. Based on the uploaded backend testing file.

**Features:**
- Direct OpenQASM 3.0 execution
- Qiskit circuit execution
- Cirq circuit execution
- Security sandboxing for user code
- JSON output for API integration

**Usage:**
```bash
python3 quantum_executor.py "<code>" <shots> "<backend>" "<framework>"
```

**Dependencies:**
```bash
pip install qiskit qiskit-aer cirq
```

### `routes/quantum.ts`
Express API route that handles quantum circuit execution requests from the frontend.

**Endpoint:** `POST /api/quantum/execute`

**Request body:**
```json
{
  "code": "# Quantum code here",
  "shots": 1024,
  "backend": "qasm_simulator",
  "framework": "qiskit"
}
```

**Response:**
```json
{
  "counts": {"00": 512, "11": 512},
  "shots": 1024,
  "backend": "qasm_simulator",
  "execution_time": "2.45",
  "success": true,
  "circuit_info": {
    "depth": 2,
    "qubits": 2
  }
}
```

## How It Works

1. **Frontend Request**: User clicks "Run Circuit" in the QCanvas interface
2. **API Call**: Frontend sends quantum code to `/api/quantum/execute`
3. **Python Execution**: Backend attempts to execute code using `quantum_executor.py`
4. **Fallback**: If Python execution fails, falls back to mock simulation
5. **Response**: Results are returned to frontend for visualization

## Security Features

- Code sanitization to remove dangerous imports
- Execution timeout (30 seconds)
- Sandboxed execution environment
- Input validation with Zod schemas

## Development Setup

1. Install Python dependencies:
   ```bash
   pip install qiskit qiskit-aer cirq
   ```

2. Test the Python executor:
   ```bash
   python3 server/quantum_executor.py
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## Production Deployment

For production deployment with actual quantum execution:

1. Ensure Python and quantum libraries are installed on the server
2. Configure proper security policies for code execution
3. Consider using Docker containers for better isolation
4. Set up monitoring for quantum execution processes

## Fallback Behavior

If Python/Qiskit is not available, the system automatically falls back to intelligent mock simulation that:
- Generates realistic quantum measurement results
- Recognizes common quantum algorithms (Bell states, Grover's, etc.)
- Provides appropriate statistical distributions
- Maintains the same API interface
