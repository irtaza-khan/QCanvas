# API Documentation

## 🌐 REST API Reference

The Cirq-RAG-Code-Assistant provides a comprehensive REST API for programmatic access to all system capabilities.

## 🚀 Getting Started

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
Currently, the API uses API key authentication:

```bash
# Set your API key
export CIRQ_RAG_API_KEY=your_api_key_here

# Or include in requests
curl -H "Authorization: Bearer your_api_key_here" \
  http://localhost:8000/api/v1/health
```

### Content Type
All requests and responses use JSON:
```bash
Content-Type: application/json
Accept: application/json
```

## 📋 API Endpoints

### 1. Health Check

#### GET /health
Check if the API is running and healthy.

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-XX T10:30:00Z",
  "version": "0.1.0",
  "services": {
    "rag": "healthy",
    "agents": "healthy",
    "database": "healthy"
  }
}
```

### 2. Code Generation

#### POST /generate
Generate Cirq code from natural language description.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Create a VQE circuit for H2 molecule",
    "algorithm": "vqe",
    "parameters": {
      "qubits": 4,
      "layers": 2,
      "optimizer": "COBYLA"
    },
    "options": {
      "include_explanation": true,
      "optimize": true,
      "validate": true
    }
  }'
```

**Request Schema:**
```json
{
  "description": "string (required)",
  "algorithm": "string (optional)",
  "parameters": {
    "qubits": "integer",
    "layers": "integer",
    "optimizer": "string",
    "molecule": "string",
    "p": "integer"
  },
  "options": {
    "include_explanation": "boolean (default: true)",
    "optimize": "boolean (default: true)",
    "validate": "boolean (default: true)",
    "optimization_level": "string (default: balanced)",
    "explanation_depth": "string (default: intermediate)"
  }
}
```

**Response:**
```json
{
  "success": true,
  "request_id": "req_123456789",
  "result": {
    "code": "import cirq\nimport numpy as np\n...",
    "explanation": {
      "overview": "This VQE circuit implements...",
      "steps": [
        {
          "number": 1,
          "title": "Initialize qubits",
          "description": "Create 4 qubits for the H2 molecule",
          "code": "qubits = range(4)"
        }
      ],
      "concepts": ["VQE", "Variational circuits", "Quantum chemistry"]
    },
    "metrics": {
      "depth": 8,
      "gate_count": 24,
      "two_qubit_gates": 6,
      "estimated_time": "2.5ms"
    },
    "optimization": {
      "original_depth": 12,
      "optimized_depth": 8,
      "improvement_percentage": 33.3,
      "optimization_time": "0.15s"
    },
    "validation": {
      "syntax_valid": true,
      "simulation_success": true,
      "tests_passed": 3,
      "total_tests": 3,
      "execution_time": "0.05s"
    }
  },
  "processing_time": "2.3s",
  "timestamp": "2025-01-XX T10:30:00Z"
}
```

### 3. Code Optimization

#### POST /optimize
Optimize an existing quantum circuit.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import cirq\nqubits = cirq.LineQubit.range(4)\n...",
    "target_metrics": ["depth", "gate_count"],
    "optimization_level": "aggressive",
    "hardware_constraints": {
      "max_depth": 20,
      "connectivity": "linear"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "original_metrics": {
    "depth": 15,
    "gate_count": 45,
    "two_qubit_gates": 12
  },
  "optimized_metrics": {
    "depth": 10,
    "gate_count": 32,
    "two_qubit_gates": 8
  },
  "improvements": {
    "depth_improvement": 33.3,
    "gate_count_improvement": 28.9,
    "two_qubit_improvement": 33.3
  },
  "optimized_code": "import cirq\n# Optimized version...",
  "optimization_time": "0.8s"
}
```

### 4. Code Validation

#### POST /validate
Validate quantum circuit code.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import cirq\nqubits = cirq.LineQubit.range(4)\n...",
    "validation_level": "comprehensive",
    "include_simulation": true
  }'
```

**Response:**
```json
{
  "success": true,
  "validation_results": {
    "syntax_check": {
      "passed": true,
      "errors": [],
      "warnings": []
    },
    "compilation": {
      "passed": true,
      "imports_resolved": true,
      "dependencies_ok": true
    },
    "simulation": {
      "passed": true,
      "execution_time": "0.05s",
      "memory_usage": "2.1MB",
      "results": {
        "final_state": [0.707, 0.0, 0.0, 0.707],
        "measurements": {"00": 0.5, "11": 0.5}
      }
    },
    "performance": {
      "depth": 8,
      "gate_count": 24,
      "estimated_time": "2.5ms"
    }
  },
  "overall_score": 0.95,
  "validation_time": "0.12s"
}
```

### 5. Educational Content

#### POST /explain
Get educational explanations for quantum algorithms.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/explain \
  -H "Content-Type: application/json" \
  -d '{
    "algorithm": "vqe",
    "level": "intermediate",
    "include_visualization": true,
    "include_examples": true
  }'
```

**Response:**
```json
{
  "success": true,
  "explanation": {
    "overview": "The Variational Quantum Eigensolver (VQE) is...",
    "algorithm_steps": [
      {
        "step": 1,
        "title": "Problem Setup",
        "description": "Define the Hamiltonian and initial state",
        "mathematical_formulation": "H = Σᵢ hᵢσᵢ + Σᵢⱼ Jᵢⱼσᵢσⱼ"
      }
    ],
    "visualizations": [
      {
        "type": "circuit_diagram",
        "url": "/api/v1/visualizations/circuit_123.png"
      }
    ],
    "examples": [
      {
        "title": "H2 Molecule",
        "description": "Simple 2-qubit VQE example",
        "code": "import cirq\n# H2 VQE example..."
      }
    ],
    "learning_resources": [
      {
        "type": "paper",
        "title": "A variational eigenvalue solver on a quantum processor",
        "url": "https://arxiv.org/abs/1304.3061"
      }
    ]
  }
}
```

### 6. Knowledge Base

#### GET /knowledge-base/algorithms
Get list of supported algorithms.

**Response:**
```json
{
  "success": true,
  "algorithms": [
    {
      "name": "vqe",
      "full_name": "Variational Quantum Eigensolver",
      "description": "Finds ground state energy of quantum systems",
      "complexity": "intermediate",
      "supported_molecules": ["H2", "LiH", "BeH2"],
      "example_parameters": {
        "qubits": 4,
        "layers": 2,
        "optimizer": "COBYLA"
      }
    }
  ]
}
```

#### GET /knowledge-base/templates
Get available code templates.

**Response:**
```json
{
  "success": true,
  "templates": [
    {
      "id": "vqe_h2_basic",
      "name": "VQE for H2 Molecule",
      "algorithm": "vqe",
      "complexity": "beginner",
      "description": "Basic VQE implementation for H2 molecule",
      "parameters": ["qubits", "layers"],
      "estimated_time": "2s"
    }
  ]
}
```

### 7. System Status

#### GET /status
Get detailed system status.

**Response:**
```json
{
  "success": true,
  "system": {
    "status": "healthy",
    "uptime": "2h 15m 30s",
    "version": "0.1.0",
    "memory_usage": "1.2GB",
    "cpu_usage": "15%"
  },
  "services": {
    "rag": {
      "status": "healthy",
      "knowledge_base_size": 1250,
      "vector_index_size": "45MB"
    },
    "agents": {
      "designer": {"status": "healthy", "queue_size": 0},
      "optimizer": {"status": "healthy", "queue_size": 0},
      "validator": {"status": "healthy", "queue_size": 0},
      "educational": {"status": "healthy", "queue_size": 0}
    },
    "database": {
      "status": "healthy",
      "connections": 5,
      "size": "12MB"
    }
  }
}
```

## 🔧 Python SDK

### Installation
```bash
pip install cirq-rag-code-assistant
```

### Basic Usage
```python
from cirq_rag_code_assistant import CirqRAGClient

# Initialize client
client = CirqRAGClient(
    base_url="http://localhost:8000/api/v1",
    api_key="your_api_key_here"
)

# Generate code
result = client.generate_code(
    description="Create a VQE circuit for H2 molecule",
    algorithm="vqe",
    parameters={"qubits": 4, "layers": 2}
)

print("Generated Code:")
print(result.code)
print("\nExplanation:")
print(result.explanation.overview)
```

### Advanced Usage
```python
# Optimize existing code
optimized = client.optimize_code(
    code=result.code,
    target_metrics=["depth", "gate_count"],
    optimization_level="aggressive"
)

# Validate code
validation = client.validate_code(
    code=optimized.code,
    validation_level="comprehensive"
)

# Get educational content
explanation = client.explain_algorithm(
    algorithm="vqe",
    level="intermediate",
    include_visualization=True
)
```

## 📊 WebSocket API

### Real-time Updates
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

// Listen for updates
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Update:', data);
};

// Send generation request
ws.send(JSON.stringify({
    type: 'generate',
    data: {
        description: 'Create a VQE circuit',
        algorithm: 'vqe'
    }
}));
```

## 🚨 Error Handling

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid algorithm specified",
    "details": {
      "field": "algorithm",
      "value": "invalid_algorithm",
      "allowed_values": ["vqe", "qaoa", "grover", "qft"]
    }
  },
  "request_id": "req_123456789",
  "timestamp": "2025-01-XX T10:30:00Z"
}
```

### Common Error Codes
- `VALIDATION_ERROR`: Invalid request parameters
- `ALGORITHM_NOT_SUPPORTED`: Algorithm not implemented
- `GENERATION_FAILED`: Code generation failed
- `OPTIMIZATION_FAILED`: Circuit optimization failed
- `VALIDATION_FAILED`: Code validation failed
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server error

## 📈 Rate Limiting

### Limits
- **Free Tier**: 100 requests/hour
- **Pro Tier**: 1000 requests/hour
- **Enterprise**: Custom limits

### Headers
```bash
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## 🔐 Authentication

### API Key Authentication
```bash
# Set API key in header
curl -H "Authorization: Bearer your_api_key_here" \
  http://localhost:8000/api/v1/generate
```

### Python SDK
```python
client = CirqRAGClient(
    base_url="http://localhost:8000/api/v1",
    api_key="your_api_key_here"
)
```

## 📚 SDK Examples

### JavaScript/Node.js
```javascript
const axios = require('axios');

const client = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Authorization': 'Bearer your_api_key_here',
    'Content-Type': 'application/json'
  }
});

// Generate code
const result = await client.post('/generate', {
  description: 'Create a VQE circuit for H2 molecule',
  algorithm: 'vqe',
  parameters: { qubits: 4, layers: 2 }
});

console.log(result.data.result.code);
```

### Go
```go
package main

import (
    "bytes"
    "encoding/json"
    "net/http"
)

type GenerateRequest struct {
    Description string                 `json:"description"`
    Algorithm   string                 `json:"algorithm"`
    Parameters  map[string]interface{} `json:"parameters"`
}

func main() {
    req := GenerateRequest{
        Description: "Create a VQE circuit for H2 molecule",
        Algorithm:   "vqe",
        Parameters:  map[string]interface{}{"qubits": 4, "layers": 2},
    }
    
    jsonData, _ := json.Marshal(req)
    
    resp, err := http.Post(
        "http://localhost:8000/api/v1/generate",
        "application/json",
        bytes.NewBuffer(jsonData),
    )
    // Handle response...
}
```

---

*For more examples and detailed usage, see the [Usage Examples](examples/README.md) and [Integration Guide](integration.md).*
