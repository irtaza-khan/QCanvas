# QCanvas Technical Explanation Document

## 1. Codebase Overview

**QCanvas** is a comprehensive quantum circuit editor and converter application that allows users to write quantum circuits in multiple frameworks (Qiskit, Cirq, PennyLane) and convert them to OpenQASM 3.0 format for execution and analysis.

### Architecture
- **Frontend**: Next.js/React application with TypeScript
- **Backend**: FastAPI-based REST API server
- **Quantum Converters**: Python modules for framework-to-QASM conversion
- **Simulator**: Quantum circuit execution engine

### Key Features
- Multi-framework quantum circuit editing
- Real-time conversion to OpenQASM 3.0
- Circuit execution and visualization
- File management system
- Results analysis and statistics

---

## 2. Frontend Analysis

### Technology Stack
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **UI Library**: React with custom components
- **Styling**: Tailwind CSS with custom quantum-themed design
- **State Management**: Zustand (useFileStore)
- **HTTP Client**: Native fetch API with custom wrapper

### Key Components

#### TopBar (`frontend/components/TopBar.tsx`)
Main action bar providing:
- **Compile to QASM**: Converts framework code to OpenQASM 3.0
- **Run**: Executes quantum circuits (conversion + simulation)
- **Save**: File persistence
- **Language Selection**: Input framework selection (QASM, Qiskit, Cirq, PennyLane)
- **Theme Toggle**: Dark/light mode switching
- **Keyboard Shortcuts**: Comprehensive shortcut system

**Key Functions**:
```typescript
handleConvertToQASM() // API call to /api/converter/convert
handleRun() // API calls to convert + execute
handleSave() // API call to /api/files/{id}
```

#### ResultsPane (`frontend/components/ResultsPane.tsx`)
Tabbed results display:
- **Console**: Execution logs and status messages
- **Output**: Raw simulation results (JSON)
- **Histogram**: Measurement result visualization (Chart.js)
- **OpenQASM**: Generated QASM code display
- **Errors**: Code analysis and validation errors
- **Stats**: Performance metrics and circuit analysis

**Key Features**:
- Real-time execution status updates
- Circuit statistics from backend conversion
- Interactive charts for measurement results
- Error highlighting with suggestions

#### File Management
- **Store**: Zustand-based state management (`useFileStore`)
- **API**: RESTful file operations (CRUD)
- **Features**: Multi-tab editing, auto-save, file switching

### API Integration (`frontend/lib/api.ts`)

#### Quantum API
```typescript
quantumApi.convertToQasm(code, framework, style) // POST /api/converter/convert
quantumApi.executeQasm(qasm_code, backend, shots) // POST /api/simulator/execute
quantumApi.validateCode(code, framework) // POST /api/converter/validate
quantumApi.getSupportedFrameworks() // GET /api/converter/frameworks
```

#### File API
```typescript
fileApi.getFiles() // GET /api/files
fileApi.createFile(data) // POST /api/files
fileApi.updateFile(id, data) // PUT /api/files/{id}
fileApi.deleteFile(id) // DELETE /api/files/{id}
```

---

## 3. Backend Analysis

### Technology Stack
- **Framework**: FastAPI (Python async web framework)
- **Language**: Python 3.8+
- **ASGI Server**: Uvicorn
- **CORS**: Configured for frontend integration
- **Validation**: Pydantic models

### Application Structure (`backend/app/main.py`)
```python
app = FastAPI(title="QCanvas Backend")

# Include routers
app.include_router(converter.router)  # /api/converter/*
app.include_router(simulator.router)  # /api/simulator/*
app.include_router(files.router)      # /api/files/*
```

### Key Routes

#### Converter Routes (`backend/app/api/routes/converter.py`)
- `POST /api/converter/convert`: Main conversion endpoint
- `GET /api/converter/frameworks`: Supported frameworks list
- `POST /api/converter/validate`: Code syntax validation
- `GET /api/converter/health`: Service health check

**Conversion Flow**:
1. Validate request (code, framework)
2. Call `ConversionService.convert_to_qasm()`
3. Return `ConversionResponse` with QASM code and statistics

#### Simulator Routes (`backend/app/api/routes/simulator.py`)
- `POST /api/simulator/execute`: Execute QASM code
- `GET /api/simulator/backends`: Available backends
- `GET /api/simulator/health`: Service health check

**Execution Flow**:
1. Parse QASM code
2. Call `SimulationService.execute_qasm()`
3. Return simulation results (counts, statevector, etc.)

### Services Layer

#### ConversionService (`backend/app/services/conversion_service.py`)
**Core Methods**:
```python
convert_to_qasm(code, framework, style) -> Dict[str, Any]
validate_code(code, framework) -> Dict[str, Any]
get_supported_frameworks() -> List[str]
```

**Conversion Process**:
1. **Framework Detection**: Validate supported framework
2. **Converter Selection**: Choose appropriate converter (qiskit/cirq/pennylane)
3. **Execution**: Run converter function
4. **Result Processing**: Extract QASM code and statistics
5. **Styling**: Apply compact/classic formatting
6. **Response**: Return standardized response format

**Fallback Mechanisms**:
- AST-based parsing (primary)
- Runtime execution (fallback)
- Heuristic string conversion (last resort)

#### SimulationService (`backend/app/services/simulation_service.py`)
**Core Methods**:
```python
execute_qasm(qasm_code, backend, shots) -> Dict[str, Any]
get_available_backends() -> List[str]
```

**Supported Backends**:
- `statevector`: Full statevector simulation
- `density_matrix`: Density matrix simulation

**Current Implementation**: Basic placeholder simulation (Bell states, etc.)

---

## 4. Quantum Conversion System

### Converter Architecture

#### Base Classes

##### ConversionResult (`quantum_converters/base/ConversionResult.py`)
```python
@dataclass
class ConversionStats:
    n_qubits: int
    depth: Optional[int]
    gate_counts: Optional[Dict[str, int]]
    has_measurements: bool

@dataclass
class ConversionResult:
    qasm_code: str
    stats: ConversionStats
```

##### QASM3Builder (`quantum_converters/base/qasm3_builder.py`)
Comprehensive OpenQASM 3.0 code generator with:
- **Standard Prelude**: Headers, includes, register declarations
- **Gate Operations**: All standard gates with modifiers
- **Measurements**: Qubit measurement operations
- **Control Flow**: If statements, loops
- **Custom Gates**: Hierarchical gate definitions
- **Parameter Formatting**: Mathematical constants recognition

**Key Methods**:
```python
build_standard_prelude(num_qubits, num_clbits)
apply_gate(gate_name, qubits, parameters, modifiers)
add_measurement(qubit, bit)
format_parameter(param)  # Handles PI, E, etc.
```

##### CircuitAST (`quantum_converters/base/circuit_ast.py`)
Unified intermediate representation:
```python
@dataclass
class CircuitAST:
    qubits: int
    clbits: int
    operations: List[Union[GateNode, MeasurementNode, ResetNode, BarrierNode]]
    parameters: Dict[str, Any]
```

**Node Types**:
- `GateNode`: Quantum gates with parameters and modifiers
- `MeasurementNode`: Qubit measurements
- `ResetNode`: Qubit reset operations
- `BarrierNode`: Synchronization barriers

### Framework Converters

#### Qiskit Converter (`quantum_converters/converters/qiskit_to_qasm.py`)
**QiskitToQASM3Converter** class:
- **AST-based Conversion**: Primary method using `QiskitASTParser`
- **Runtime Execution**: Fallback using `exec()` on source code
- **Circuit Analysis**: Extract statistics from Qiskit circuits

**Conversion Methods**:
```python
convert(qiskit_source) -> ConversionResult
_execute_qiskit_source(source) -> QuantumCircuit
_analyze_qiskit_circuit(qc) -> ConversionStats
_convert_to_qasm3(qc) -> str
```

**Supported Qiskit Features**:
- All standard gates (H, X, Y, Z, CX, etc.)
- Parameterized gates (RX, RY, RZ, U, etc.)
- Custom gates and circuits
- Measurements and classical bits
- Circuit parameters

#### Cirq Converter (`quantum_converters/converters/cirq_to_qasm.py`)
Similar structure to Qiskit converter:
- AST parsing for Cirq circuits
- Runtime execution fallback
- Support for Cirq-specific operations

#### PennyLane Converter (`quantum_converters/converters/pennylane_to_qasm.py`)
PennyLane-specific conversion handling QNodes and quantum functions.

### Parser System

#### QiskitASTParser (`quantum_converters/parsers/qiskit_parser.py`)
Parses Qiskit source code to extract circuit operations without execution:
- **Function Detection**: Finds `get_circuit()` function
- **AST Analysis**: Uses Python AST to extract operations
- **Circuit Construction**: Builds `CircuitAST` representation

#### Cirq Parser (`quantum_converters/parsers/cirq_parser.py`)
Similar AST-based parsing for Cirq code.

### Gate Library (`quantum_converters/base/qasm3_gates.py`)

**QASM3GateLibrary** class provides:
- **Standard Gates**: Complete OpenQASM 3.0 gate set
- **Modifiers**: `ctrl@`, `inv@`, `pow@` support
- **Parameter Formatting**: Mathematical constant recognition
- **Validation**: Gate application validation

**Supported Gates**:
- Single-qubit: H, X, Y, Z, S, T, SX, RX, RY, RZ, P, U
- Two-qubit: CX, CY, CZ, SWAP, CP, CRX, CRY, CRZ
- Three-qubit: CCX, CSWAP, CCZ
- Special: GPHASE (global phase)

---

## 5. Process Flow (End-to-End)

### 1. User Code Input
User writes quantum circuit code in supported framework (Qiskit/Cirq/PennyLane)

### 2. Conversion Request
Frontend calls `POST /api/converter/convert` with:
```json
{
  "code": "from qiskit import QuantumCircuit\n\ndef get_circuit():\n    qc = QuantumCircuit(2)\n    qc.h(0)\n    qc.cx(0, 1)\n    return qc",
  "framework": "qiskit",
  "qasm_version": "3.0",
  "style": "classic"
}
```

### 3. Backend Processing
1. **Route Handler**: `converter.py` receives request
2. **Service Call**: `ConversionService.convert_to_qasm()`
3. **Framework Selection**: Choose appropriate converter
4. **Conversion Execution**:
   - Try AST-based parsing first
   - Fallback to runtime execution
   - Generate QASM code via `QASM3Builder`
5. **Statistics Extraction**: Analyze circuit properties
6. **Response Formation**: Return `ConversionResponse`

### 4. QASM Generation
```qasm
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;

h q[0];
cx q[0], q[1];
```

### 5. Execution (Optional)
If user clicks "Run":
1. **QASM Execution**: Call `POST /api/simulator/execute`
2. **Simulation**: Run on selected backend (statevector/density_matrix)
3. **Results**: Return measurement counts, statevector, etc.

### 6. Results Display
Frontend displays:
- Generated QASM code
- Circuit statistics (qubits, depth, gates)
- Execution results (if run)
- Performance metrics

---

## 6. Key Classes and Functions

### Frontend Classes

#### useFileStore (Zustand Store)
```typescript
interface FileStore {
  files: File[]
  activeFileId: string | null
  theme: 'light' | 'dark'
  compiledQasm: string
  conversionStats: ConversionStats | null
  
  // Actions
  addFile(name: string, content: string): void
  updateFileContent(id: string, content: string): void
  setActiveFile(id: string): void
  compileActiveToQasm(): Promise<void>
  setCompiledQasm(qasm: string): void
  setConversionStats(stats: ConversionStats): void
}
```

### Backend Classes

#### ConversionService
```python
class ConversionService:
    def __init__(self)
    def convert_to_qasm(self, code: str, framework: str, style: str) -> Dict[str, Any]
    def validate_code(self, code: str, framework: str) -> Dict[str, Any]
    def get_supported_frameworks(self) -> List[str]
```

#### QASM3Builder
```python
class QASM3Builder:
    def __init__(self)
    def build_standard_prelude(self, num_qubits: int, num_clbits: int = 0, ...)
    def apply_gate(self, gate_name: str, qubits: List[str], parameters: Optional[List[str]] = None, modifiers: Optional[Dict] = None)
    def add_measurement(self, qubit: str, bit: str)
    def get_code(self) -> str
```

#### QiskitToQASM3Converter
```python
class QiskitToQASM3Converter:
    def convert(self, qiskit_source: str) -> ConversionResult
    def _execute_qiskit_source(self, source: str) -> QuantumCircuit
    def _convert_to_qasm3(self, qc: QuantumCircuit) -> str
    def _analyze_qiskit_circuit(self, qc: QuantumCircuit) -> ConversionStats
```

### Utility Functions

#### Parameter Formatting
```python
def format_parameter(self, param: Any) -> str:
    # Handles mathematical constants
    if abs(value - np.pi) < 1e-10:
        return "PI"
    # ... other constants
```

#### Gate Application
```python
def apply_gate(self, gate_name: str, qubits: List[str], parameters=None, modifiers=None):
    # Build modifier string (ctrl@, inv@, etc.)
    # Format parameters
    # Generate QASM statement
```

---

## 7. Configuration and Dependencies

### Backend Dependencies (`backend/requirements.txt`)
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
qiskit>=0.44.0
cirq>=1.0.0
pennylane>=0.33.0
numpy>=1.21.0
python-multipart==0.0.6
```

### Frontend Dependencies (`frontend/package.json`)
```json
{
  "dependencies": {
    "next": "14.0.4",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.3.0",
    "zustand": "^4.4.0",
    "react-hot-toast": "^2.4.0",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0",
    "lucide-react": "^0.294.0"
  }
}
```

### Configuration Files
- `config/config.py`: Logging, verbose output, constants
- `config/logging.yml`: Logging configuration
- `quantum_converters/config.py`: Converter-specific settings

### Environment Variables
- `NEXT_PUBLIC_API_BASE`: Frontend API base URL (default: http://localhost:8000)

---

## 8. Error Handling and Validation

### Frontend Validation
- **Framework Detection**: Automatic framework detection from imports
- **Code Validation**: Syntax checking before conversion
- **File Type Validation**: QASM vs framework code detection

### Backend Validation
- **Request Validation**: Pydantic models for API requests
- **Framework Support**: Check against supported frameworks list
- **Code Validation**: AST parsing and syntax validation
- **Converter Availability**: Check if required converter is available

### Error Response Format
```json
{
  "success": false,
  "error": "Detailed error message",
  "framework": "qiskit",
  "qasm_version": "3.0"
}
```

---

## 9. Performance Considerations

### Conversion Optimization
- **AST-based Parsing**: Avoids runtime execution for security and speed
- **Lazy Loading**: Converters loaded only when needed
- **Caching**: Potential for QASM code caching (not implemented)

### Execution Optimization
- **Backend Selection**: Choose appropriate simulator backend
- **Shot Optimization**: Efficient measurement shot allocation
- **Memory Management**: Large circuit handling

### Frontend Optimization
- **Code Splitting**: Dynamic imports for heavy components
- **State Management**: Efficient Zustand store updates
- **API Batching**: Combined requests where possible

---

## 10. Testing and Quality Assurance

### Current Testing
- **Unit Tests**: Individual converter testing
- **Integration Tests**: API endpoint testing
- **Manual Testing**: UI/UX validation

### Test Files
- `test_cirq_conversion_fixed.py`: Cirq converter tests
- `temp_compare_gates.py`: Gate comparison utilities
- Various test files in quantum_converters directory

### CI/CD
- **GitHub Actions**: Automated testing workflow (`.github/workflows/ci.yml`)
- **Linting**: Code quality checks
- **Dependency Updates**: Automated dependency management

---

## 11. Future Enhancements

### Planned Features
- **Advanced Simulator**: Full quantum simulator integration
- **Circuit Optimization**: Gate optimization passes
- **Visualization**: Circuit diagram rendering
- **Collaboration**: Multi-user editing
- **Plugin System**: Extensible converter architecture

### Technical Debt
- **Simulator Integration**: Complete quantum simulator backend
- **Error Handling**: Comprehensive error reporting
- **Performance**: Optimization for large circuits
- **Documentation**: API documentation generation

---

This document provides a comprehensive technical overview of the QCanvas quantum circuit editor and converter application. The system demonstrates a well-architected approach to quantum computing tool development with clear separation of concerns, robust error handling, and extensible design patterns.
