# QCanvas Backend

This is the backend API for QCanvas, a quantum circuit framework converter that converts code from various quantum computing frameworks to OpenQASM 3.0.

## Features

- **Framework Support**: Convert code from Qiskit, Cirq, and PennyLane to OpenQASM 3.0
- **RESTful API**: Clean REST endpoints for conversion operations
- **Code Validation**: Syntax validation for supported frameworks
- **Health Monitoring**: Health check endpoints for system monitoring
- **CORS Support**: Configured for frontend integration

## API Endpoints

### Health Check
- `GET /api/health` - Backend health status

### Converter
- `POST /api/converter/convert` - Convert code to OpenQASM
- `GET /api/converter/frameworks` - Get supported frameworks
- `POST /api/converter/validate` - Validate code syntax
- `GET /api/converter/health` - Converter service health

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Backend**:
   ```bash
   python start.py
   ```
   
   Or directly with uvicorn:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Access API Documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Usage Examples

### Convert Qiskit Code to OpenQASM

```bash
curl -X POST "http://localhost:8000/api/converter/convert" \
     -H "Content-Type: application/json" \
     -d '{
       "code": "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0,1)",
       "framework": "qiskit",
       "style": "classic"
     }'
```

### Get Supported Frameworks

```bash
curl "http://localhost:8000/api/converter/frameworks"
```

### Validate Code

```bash
curl -X POST "http://localhost:8000/api/converter/validate" \
     -H "Content-Type: application/json" \
     -d '{
       "code": "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)",
       "framework": "qiskit"
     }'
```

## Configuration

The backend is configured to:
- Run on port 8000
- Accept CORS requests from any origin (configurable for production)
- Use the quantum converters from the `quantum_converters` package

## Frontend Integration

The frontend can connect to this backend by:
1. Setting `NEXT_PUBLIC_API_BASE=http://localhost:8000` in the frontend environment
2. Using the conversion API endpoints through the `conversionApi` functions

## Error Handling

The API provides detailed error messages for:
- Invalid framework specifications
- Code syntax errors
- Conversion failures
- Server errors

## Development

- **Hot Reload**: The backend automatically reloads on code changes when using `--reload`
- **Logging**: Comprehensive logging for debugging
- **Exception Handling**: Global exception handler for consistent error responses
