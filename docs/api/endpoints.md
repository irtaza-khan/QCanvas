# QCanvas API Endpoints Documentation

## Overview

The QCanvas API provides comprehensive endpoints for quantum circuit conversion, simulation, and management. All endpoints are RESTful and return JSON responses.

**Base URL**: `http://localhost:8000/api`

## Authentication

Currently, the API does not require authentication for basic operations. Future versions will include JWT-based authentication.

## Response Format

All API responses follow this standard format:

```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed successfully",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

## Health Check Endpoints

### GET /api/health

Comprehensive health check of all system components.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T00:00:00Z",
  "version": "1.0.0",
  "uptime": 3600.5,
  "components": {
    "database": {
      "status": "healthy",
      "response_time": 15.2,
      "details": {
        "type": "postgresql",
        "pool_size": 10,
        "active_connections": 0
      }
    },
    "redis": {
      "status": "healthy",
      "response_time": 2.1,
      "details": {
        "type": "redis",
        "memory_usage": "2.5MB",
        "connected_clients": 1
      }
    },
    "quantum_simulator": {
      "status": "healthy",
      "response_time": 5.8,
      "details": {
        "available_backends": ["statevector", "density_matrix", "stabilizer"],
        "max_qubits": 32,
        "supported_frameworks": ["cirq", "qiskit", "pennylane"]
      }
    }
  }
}
```

### GET /api/health/simple

Basic health check for load balancers.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T00:00:00Z",
  "version": "1.0.0",
  "uptime": 3600.5
}
```

### GET /api/health/ready

Kubernetes readiness probe.

**Response**:
```json
{
  "status": "ready",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### GET /api/health/live

Kubernetes liveness probe.

**Response**:
```json
{
  "status": "alive",
  "timestamp": "2025-01-01T00:00:00Z",
  "version": "1.0.0",
  "uptime": 3600.5
}
```

### GET /api/health/info

Detailed system information.

**Response**:
```json
{
  "application": {
    "name": "QCanvas",
    "version": "1.0.0",
    "environment": "production",
    "debug": false,
    "uptime": 3600.5
  },
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "workers": 4
  },
  "quantum": {
    "max_qubits": 32,
    "max_shots": 10000,
    "default_backend": "statevector",
    "enable_noise_models": true
  },
  "components": {...},
  "timestamp": "2025-01-01T00:00:00Z"
}
```

## Circuit Conversion Endpoints

### POST /api/convert

Convert a quantum circuit between different frameworks.

**Request Body**:
```json
{
  "source_framework": "cirq",
  "target_framework": "qiskit",
  "source_code": "import cirq\n\nq0, q1 = cirq.LineQubit.range(2)\ncircuit = cirq.Circuit(\n    cirq.H(q0),\n    cirq.CNOT(q0, q1),\n    cirq.measure(q0, q1)\n)",
  "optimization_level": 1,
  "include_comments": false,
  "validate_circuit": true
}
```

**Response**:
```json
{
  "success": true,
  "source_framework": "cirq",
  "target_framework": "qiskit",
  "converted_code": "from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister\n\nqr = QuantumRegister(2, 'q')\ncr = ClassicalRegister(2, 'c')\nqc = QuantumCircuit(qr, cr)\n\nqc.h(qr[0])\nqc.cx(qr[0], qr[1])\nqc.measure(qr, cr)\n",
  "qasm_code": "OPENQASM 3.0;\ninclude \"stdgates.inc\";\n\nqubit[2] q;\nbit[2] c;\n\nh q[0];\ncx q[0], q[1];\nc[0] = measure q[0];\nc[1] = measure q[1];",
  "stats": {
    "execution_time": 0.125,
    "gate_count": 3,
    "qubit_count": 2,
    "depth": 2
  },
  "warnings": [],
  "errors": [],
  "execution_time": 0.125,
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### POST /api/convert/batch

Convert multiple circuits in batch.

**Request Body**:
```json
[
  {
    "source_framework": "cirq",
    "target_framework": "qiskit",
    "source_code": "..."
  },
  {
    "source_framework": "qiskit",
    "target_framework": "pennylane",
    "source_code": "..."
  }
]
```

**Response**:
```json
[
  {
    "success": true,
    "source_framework": "cirq",
    "target_framework": "qiskit",
    "converted_code": "...",
    "execution_time": 0.125,
    "timestamp": "2025-01-01T00:00:00Z"
  },
  {
    "success": true,
    "source_framework": "qiskit",
    "target_framework": "pennylane",
    "converted_code": "...",
    "execution_time": 0.098,
    "timestamp": "2025-01-01T00:00:00Z"
  }
]
```

### GET /api/convert/frameworks

Get information about supported frameworks.

**Response**:
```json
[
  {
    "name": "cirq",
    "version": "1.2.0",
    "supported_gates": ["H", "X", "Y", "Z", "CNOT", "CZ", "SWAP", "T", "S"],
    "features": ["Near-term devices", "Noise models", "Circuit optimization"],
    "limitations": ["Limited to Google's quantum devices"]
  },
  {
    "name": "qiskit",
    "version": "0.45.0",
    "supported_gates": ["H", "X", "Y", "Z", "CNOT", "CZ", "SWAP", "T", "S", "U1", "U2", "U3"],
    "features": ["IBM Quantum devices", "Aer simulator", "Quantum machine learning"],
    "limitations": ["IBM-specific optimizations"]
  },
  {
    "name": "pennylane",
    "version": "0.32.0",
    "supported_gates": ["H", "X", "Y", "Z", "CNOT", "CZ", "SWAP", "RX", "RY", "RZ"],
    "features": ["Quantum machine learning", "Gradient computation", "Hybrid classical-quantum"],
    "limitations": ["Focused on variational circuits"]
  }
]
```

### GET /api/convert/stats

Get conversion statistics.

**Response**:
```json
{
  "total_conversions": 1250,
  "successful_conversions": 1180,
  "failed_conversions": 70,
  "average_execution_time": 0.145,
  "framework_stats": {
    "cirq": {
      "total": 450,
      "successful": 425,
      "failed": 25
    },
    "qiskit": {
      "total": 400,
      "successful": 380,
      "failed": 20
    },
    "pennylane": {
      "total": 400,
      "successful": 375,
      "failed": 25
    }
  }
}
```

### POST /api/convert/validate

Validate a quantum circuit without converting.

**Request Body**:
```json
{
  "source_framework": "cirq",
  "source_code": "import cirq\n\nq0, q1 = cirq.LineQubit.range(2)\ncircuit = cirq.Circuit(\n    cirq.H(q0),\n    cirq.CNOT(q0, q1)\n)"
}
```

**Response**:
```json
{
  "valid": true,
  "framework": "cirq",
  "warnings": [],
  "errors": [],
  "stats": {
    "gate_count": 2,
    "qubit_count": 2,
    "depth": 2
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### GET /api/convert/optimize

Get optimization options.

**Response**:
```json
{
  "optimization_levels": {
    0: {
      "name": "No Optimization",
      "description": "Direct conversion without any optimizations",
      "use_cases": ["Debugging", "Exact representation", "Educational purposes"]
    },
    1: {
      "name": "Basic Optimization",
      "description": "Basic gate fusion and simplification",
      "use_cases": ["General use", "Balanced performance", "Most conversions"]
    },
    2: {
      "name": "Advanced Optimization",
      "description": "Advanced optimizations including circuit restructuring",
      "use_cases": ["Performance critical", "Large circuits", "Production use"]
    },
    3: {
      "name": "Maximum Optimization",
      "description": "Maximum possible optimizations, may change circuit structure",
      "use_cases": ["Ultra-performance", "Research", "Experimental"]
    }
  },
  "optimization_techniques": [
    "Gate fusion",
    "Circuit simplification",
    "Dead code elimination",
    "Constant folding",
    "Circuit restructuring",
    "Noise-aware optimization"
  ]
}
```

### POST /api/convert/compare

Compare circuits before and after conversion.

**Request Body**:
```json
{
  "source_framework": "cirq",
  "target_framework": "qiskit",
  "source_code": "...",
  "optimization_level": 1
}
```

**Response**:
```json
{
  "source_stats": {
    "gate_count": 5,
    "qubit_count": 2,
    "depth": 3,
    "total_operations": 5
  },
  "target_stats": {
    "gate_count": 4,
    "qubit_count": 2,
    "depth": 2,
    "total_operations": 4
  },
  "equivalence": true,
  "differences": {
    "gate_reduction": 1,
    "depth_reduction": 1,
    "optimization_applied": true
  },
  "optimization_impact": {
    "gate_fusion": 1,
    "simplification": 0,
    "restructuring": 0
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### GET /api/convert/examples/{framework}

Get example circuits for a specific framework.

**Response**:
```json
[
  {
    "name": "Bell State",
    "description": "Creates a Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2",
    "code": "import cirq\n\nq0, q1 = cirq.LineQubit.range(2)\ncircuit = cirq.Circuit(\n    cirq.H(q0),\n    cirq.CNOT(q0, q1),\n    cirq.measure(q0, q1)\n)",
    "category": "basic",
    "tags": ["entanglement", "superposition", "measurement"]
  },
  {
    "name": "GHZ State",
    "description": "Creates a GHZ state for 3 qubits",
    "code": "...",
    "category": "advanced",
    "tags": ["multi-qubit", "entanglement", "quantum_algorithms"]
  }
]
```

## Quantum Simulation Endpoints

### POST /api/simulate

Simulate a quantum circuit.

**Request Body**:
```json
{
  "qasm_code": "OPENQASM 3.0;\ninclude \"stdgates.inc\";\n\nqubit[2] q;\nbit[2] c;\n\nh q[0];\ncx q[0], q[1];\nc[0] = measure q[0];\nc[1] = measure q[1];",
  "backend": "statevector",
  "shots": 1000,
  "noise_model": null,
  "optimization_level": 1,
  "seed": 42,
  "return_statevector": false,
  "return_density_matrix": false
}
```

**Response**:
```json
{
  "success": true,
  "backend": "statevector",
  "shots": 1000,
  "execution_time": 0.045,
  "results": {
    "counts": {
      "00": 498,
      "11": 502
    },
    "probabilities": {
      "00": 0.498,
      "11": 0.502
    }
  },
  "statevector": null,
  "density_matrix": null,
  "circuit_stats": {
    "gate_count": 3,
    "qubit_count": 2,
    "depth": 2,
    "total_operations": 3
  },
  "warnings": [],
  "errors": [],
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### POST /api/simulate/batch

Simulate multiple circuits in batch.

**Request Body**:
```json
[
  {
    "qasm_code": "...",
    "backend": "statevector",
    "shots": 1000
  },
  {
    "qasm_code": "...",
    "backend": "density_matrix",
    "shots": 500
  }
]
```

**Response**:
```json
[
  {
    "success": true,
    "backend": "statevector",
    "shots": 1000,
    "execution_time": 0.045,
    "results": {...},
    "timestamp": "2025-01-01T00:00:00Z"
  },
  {
    "success": true,
    "backend": "density_matrix",
    "shots": 500,
    "execution_time": 0.032,
    "results": {...},
    "timestamp": "2025-01-01T00:00:00Z"
  }
]
```

### GET /api/simulate/backends

Get available simulation backends.

**Response**:
```json
[
  {
    "name": "statevector",
    "type": "exact",
    "max_qubits": 32,
    "supported_gates": ["H", "X", "Y", "Z", "CNOT", "CZ", "SWAP", "T", "S", "RX", "RY", "RZ"],
    "noise_models": ["depolarizing", "bit_flip", "phase_flip"],
    "features": ["Exact simulation", "State vector access", "Fast for small circuits"],
    "limitations": ["Memory intensive for large circuits"]
  },
  {
    "name": "density_matrix",
    "type": "mixed_state",
    "max_qubits": 16,
    "supported_gates": ["H", "X", "Y", "Z", "CNOT", "CZ", "SWAP"],
    "noise_models": ["depolarizing", "bit_flip", "phase_flip", "amplitude_damping"],
    "features": ["Noise simulation", "Mixed states", "Realistic quantum devices"],
    "limitations": ["Slower than statevector", "Limited qubit count"]
  },
  {
    "name": "stabilizer",
    "type": "stabilizer",
    "max_qubits": 64,
    "supported_gates": ["H", "X", "Y", "Z", "CNOT", "CZ", "S"],
    "noise_models": ["depolarizing"],
    "features": ["Fast for Clifford circuits", "Large qubit support", "Error correction"],
    "limitations": ["Limited to Clifford gates", "No T gates"]
  }
]
```

### GET /api/simulate/noise-models

Get available noise models.

**Response**:
```json
{
  "depolarizing": {
    "description": "Depolarizing noise channel",
    "parameters": {
      "p": {
        "type": "float",
        "range": [0.0, 1.0],
        "default": 0.01,
        "description": "Depolarizing probability"
      }
    },
    "supported_backends": ["statevector", "density_matrix", "stabilizer"]
  },
  "bit_flip": {
    "description": "Bit flip noise channel",
    "parameters": {
      "p": {
        "type": "float",
        "range": [0.0, 1.0],
        "default": 0.01,
        "description": "Bit flip probability"
      }
    },
    "supported_backends": ["statevector", "density_matrix"]
  },
  "phase_flip": {
    "description": "Phase flip noise channel",
    "parameters": {
      "p": {
        "type": "float",
        "range": [0.0, 1.0],
        "default": 0.01,
        "description": "Phase flip probability"
      }
    },
    "supported_backends": ["statevector", "density_matrix"]
  },
  "amplitude_damping": {
    "description": "Amplitude damping noise channel",
    "parameters": {
      "gamma": {
        "type": "float",
        "range": [0.0, 1.0],
        "default": 0.01,
        "description": "Damping rate"
      }
    },
    "supported_backends": ["density_matrix"]
  }
}
```

### GET /api/simulate/stats

Get simulation statistics.

**Response**:
```json
{
  "total_simulations": 850,
  "successful_simulations": 820,
  "failed_simulations": 30,
  "average_execution_time": 0.078,
  "backend_stats": {
    "statevector": {
      "total": 500,
      "successful": 485,
      "failed": 15,
      "average_time": 0.045
    },
    "density_matrix": {
      "total": 250,
      "successful": 240,
      "failed": 10,
      "average_time": 0.098
    },
    "stabilizer": {
      "total": 100,
      "successful": 95,
      "failed": 5,
      "average_time": 0.023
    }
  }
}
```

### POST /api/simulate/analyze

Analyze a quantum circuit without executing.

**Request Body**:
```json
{
  "qasm_code": "OPENQASM 3.0;\ninclude \"stdgates.inc\";\n\nqubit[2] q;\nbit[2] c;\n\nh q[0];\ncx q[0], q[1];\nc[0] = measure q[0];\nc[1] = measure q[1];",
  "optimization_level": 1
}
```

**Response**:
```json
{
  "circuit_info": {
    "qubit_count": 2,
    "gate_count": 3,
    "depth": 2,
    "total_operations": 3
  },
  "gate_distribution": {
    "H": 1,
    "CNOT": 1,
    "measure": 1
  },
  "complexity_metrics": {
    "entanglement_entropy": 1.0,
    "circuit_volume": 6,
    "connectivity": 0.5
  },
  "potential_issues": [],
  "optimization_suggestions": [
    "Circuit is already optimal",
    "No further optimizations possible"
  ],
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### POST /api/simulate/compare-backends

Compare simulation results across different backends.

**Request Body**:
```json
{
  "qasm_code": "OPENQASM 3.0;\ninclude \"stdgates.inc\";\n\nqubit[2] q;\nbit[2] c;\n\nh q[0];\ncx q[0], q[1];\nc[0] = measure q[0];\nc[1] = measure q[1];",
  "shots": 1000,
  "noise_model": null,
  "optimization_level": 1,
  "seed": 42
}
```

**Response**:
```json
{
  "backend_results": {
    "statevector": {
      "success": true,
      "execution_time": 0.045,
      "results": {...},
      "accuracy": 1.0
    },
    "density_matrix": {
      "success": true,
      "execution_time": 0.098,
      "results": {...},
      "accuracy": 1.0
    },
    "stabilizer": {
      "success": true,
      "execution_time": 0.023,
      "results": {...},
      "accuracy": 1.0
    }
  },
  "performance_comparison": {
    "fastest": "stabilizer",
    "slowest": "density_matrix",
    "speedup": {
      "stabilizer_vs_statevector": 1.96,
      "stabilizer_vs_density_matrix": 4.26
    }
  },
  "accuracy_comparison": {
    "all_backends_equivalent": true,
    "max_difference": 0.0
  },
  "recommendations": [
    "Use stabilizer backend for best performance",
    "All backends provide equivalent results for this circuit"
  ],
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### POST /api/simulate/optimize

Optimize a quantum circuit for simulation.

**Request Body**:
```json
{
  "qasm_code": "OPENQASM 3.0;\ninclude \"stdgates.inc\";\n\nqubit[2] q;\nbit[2] c;\n\nh q[0];\nh q[0];\ncx q[0], q[1];\nc[0] = measure q[0];\nc[1] = measure q[1];",
  "optimization_level": 2,
  "backend": "statevector"
}
```

**Response**:
```json
{
  "original_circuit": {
    "gate_count": 4,
    "qubit_count": 2,
    "depth": 3,
    "total_operations": 4
  },
  "optimized_circuit": {
    "gate_count": 3,
    "qubit_count": 2,
    "depth": 2,
    "total_operations": 3,
    "qasm_code": "OPENQASM 3.0;\ninclude \"stdgates.inc\";\n\nqubit[2] q;\nbit[2] c;\n\ncx q[0], q[1];\nc[0] = measure q[0];\nc[1] = measure q[1];"
  },
  "optimization_metrics": {
    "gate_reduction": 1,
    "depth_reduction": 1,
    "operation_reduction": 1,
    "optimization_time": 0.012
  },
  "gate_reduction": {
    "H_gates_removed": 2,
    "reason": "H^2 = I, so consecutive H gates cancel out"
  },
  "depth_reduction": {
    "layers_removed": 1,
    "reason": "Gate fusion and cancellation"
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### GET /api/simulate/examples

Get example circuits for simulation testing.

**Response**:
```json
[
  {
    "name": "Bell State",
    "description": "Creates a Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2",
    "qasm_code": "OPENQASM 3.0;\ninclude \"stdgates.inc\";\n\nqubit[2] q;\nbit[2] c;\n\nh q[0];\ncx q[0], q[1];\nc[0] = measure q[0];\nc[1] = measure q[1];",
    "category": "basic",
    "expected_result": {
      "00": 0.5,
      "11": 0.5
    },
    "tags": ["entanglement", "superposition", "measurement"]
  },
  {
    "name": "GHZ State",
    "description": "Creates a GHZ state for 3 qubits",
    "qasm_code": "...",
    "category": "advanced",
    "expected_result": {
      "000": 0.5,
      "111": 0.5
    },
    "tags": ["multi-qubit", "entanglement", "quantum_algorithms"]
  }
]
```

### POST /api/simulate/validate

Validate simulation parameters.

**Request Body**:
```json
{
  "qasm_code": "OPENQASM 3.0;\ninclude \"stdgates.inc\";\n\nqubit[2] q;\nbit[2] c;\n\nh q[0];\ncx q[0], q[1];\nc[0] = measure q[0];\nc[1] = measure q[1];",
  "backend": "statevector",
  "shots": 1000,
  "noise_model": null,
  "optimization_level": 1
}
```

**Response**:
```json
{
  "valid": true,
  "warnings": [],
  "errors": [],
  "recommendations": [
    "Consider using stabilizer backend for better performance",
    "Circuit is suitable for all available backends"
  ],
  "estimated_resources": {
    "memory_usage": "16 KB",
    "execution_time": "0.05 seconds",
    "cpu_usage": "low"
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

## WebSocket Endpoints

### WebSocket /ws

Real-time communication endpoint for live updates.

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

**Message Format**:
```json
{
  "type": "message_type",
  "data": {...},
  "timestamp": "2025-01-01T00:00:00Z",
  "session_id": "unique_session_id"
}
```

**Supported Message Types**:
- `ping`: Keep-alive ping
- `pong`: Keep-alive response
- `subscribe`: Subscribe to updates
- `unsubscribe`: Unsubscribe from updates
- `simulation_update`: Real-time simulation progress
- `conversion_progress`: Real-time conversion progress

## Error Responses

### 400 Bad Request
```json
{
  "error": "ValidationError",
  "message": "Invalid framework specified",
  "details": {
    "field": "source_framework",
    "value": "invalid_framework",
    "supported_frameworks": ["cirq", "qiskit", "pennylane"]
  }
}
```

### 404 Not Found
```json
{
  "error": "NotFoundError",
  "message": "Framework not found",
  "details": {
    "requested_framework": "invalid_framework"
  }
}
```

### 500 Internal Server Error
```json
{
  "error": "InternalServerError",
  "message": "An unexpected error occurred",
  "details": "Internal server error"
}
```

### 429 Too Many Requests
```json
{
  "error": "RateLimitError",
  "message": "Rate limit exceeded",
  "details": {
    "retry_after": 60
  }
}
```

## Rate Limiting

- **Per minute**: 100 requests
- **Per hour**: 1000 requests
- **Per day**: 10000 requests

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset time

## CORS Configuration

The API supports CORS for web applications:

- **Allowed Origins**: `http://localhost:3000`, `http://127.0.0.1:3000`
- **Allowed Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Allowed Headers**: Content-Type, Authorization
- **Credentials**: Supported

## Versioning

API versioning is handled through URL paths:
- Current version: `/api/`
- Future versions: `/api/v2/`, `/api/v3/`, etc.

## Deprecation Policy

- Deprecated endpoints will be marked with `deprecated: true` in responses
- Deprecated endpoints will be supported for at least 6 months
- Migration guides will be provided for deprecated functionality

## Support

For API support:
- **Documentation**: `/docs` (Swagger UI)
- **Issues**: GitHub Issues
- **Email**: api-support@qcanvas.dev
