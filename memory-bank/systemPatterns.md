# QCanvas System Patterns

## System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │   Circuit   │ │  Quantum    │ │   Real-time │ │   Results   │ │
│  │   Editor    │ │ Simulator   │ │  Updates    │ │Display & Viz│ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│                                                                 │
│  - UI Components & Routing                                      │
│  - Simple Operations & SSR/SSG                                  │
│  - TypeScript Frontend                                          │
│  - App Router & API Routes                                      │
└─────────────────────────────────────────────────────────────────┘
```

See `docs/project-scope.md` for authoritative scope and exclusions.

## Key Technical Decisions

### Hybrid Architecture Choice
**Decision**: Use Next.js for frontend and FastAPI for backend
**Rationale**: 
- Next.js provides excellent SSR/SSG, routing, and developer experience
- FastAPI excels at complex computations and API development
- TypeScript enables shared types across both services
- Each framework handles what it does best

### OpenQASM 3.0 as Intermediate Representation
**Decision**: Use OpenQASM 3.0 as universal intermediate format
**Rationale**:
- Industry standard for quantum circuit representation
- Enables framework-agnostic processing
- Supports major quantum gates and operations needed for our scope
- Provides clear conversion path between frameworks

### WebSocket for Real-time Updates
**Decision**: Implement WebSocket for long-running operations
**Rationale**:
- Quantum simulations can take significant time
- Users need progress feedback during operations
- Enables real-time collaboration features
- Provides better user experience than polling

### Shared TypeScript Types
**Decision**: Maintain type definitions shared between frontend and backend
**Rationale**:
- Ensures consistency across services
- Reduces development time and errors
- Enables better IDE support and validation
- Simplifies API contract management

## Design Patterns in Use

### Converter Pattern
```python
class AbstractConverter:
    def convert(self, source_code: str) -> ConversionResult:
        # Parse source framework
        # Convert to OpenQASM 3.0
        # Convert to target framework
        # Return structured result
```

### Strategy Pattern for Simulation Backends
```python
class SimulationBackend:
    def simulate(self, circuit: str, params: SimulationParams) -> SimulationResult:
        pass

class StatevectorBackend(SimulationBackend):
    def simulate(self, circuit: str, params: SimulationParams) -> SimulationResult:
        # Statevector simulation implementation
```

### Observer Pattern for WebSocket Updates
```python
class WebSocketManager:
    def __init__(self):
        self.connections: List[WebSocket] = []
    
    async def broadcast_progress(self, task_id: str, progress: float):
        for connection in self.connections:
            await connection.send_json({
                "task_id": task_id,
                "progress": progress,
                "type": "progress_update"
            })
```

### Factory Pattern for Framework Detection
```python
class ConverterFactory:
    @staticmethod
    def create_converter(source: str, target: str) -> AbstractConverter:
        if source == "cirq" and target == "qiskit":
            return CirqToQiskitConverter()
        elif source == "qiskit" and target == "cirq":
            return QiskitToCirqConverter()
        # ... other combinations
```

## Component Relationships

### Frontend Components
- **EditorPane**: Circuit code input and editing
- **ResultsPane**: Display conversion and simulation results
- **Sidebar**: Framework selection and options
- **TopBar**: Navigation and user controls
- **ThemeWatcher**: Dark/light mode management

### Backend Services
- **ConverterService**: Handles circuit conversion logic
- **SimulationService**: Manages quantum simulations
- **WebSocketService**: Real-time communication
- **ValidationService**: Input validation and error handling

### Quantum Processing Modules
- **Parsers**: Framework-specific code parsing
- **Converters**: Framework-to-framework conversion
- **Generators**: OpenQASM 3.0 code generation
- **Validators**: Circuit validation and optimization

## Data Flow Patterns

### Circuit Conversion Flow
```
User Input → Frontend Validation → API Request → Backend Processing → 
OpenQASM Generation → Target Framework Conversion → Response → 
Frontend Display
```

### Simulation Flow
```
QASM Input → Validation → Backend Selection → Simulation Execution → 
Progress Updates (WebSocket) → Results Processing → Response → 
Visualization
```

### Real-time Update Flow
```
Long Operation Start → WebSocket Connection → Progress Broadcast → 
Frontend Update → Operation Complete → Final Results → 
Connection Cleanup
```

## Error Handling Patterns

### Structured Exception Hierarchy
```python
class QCanvasException(Exception):
    """Base exception for all QCanvas errors"""
    pass

class ConversionError(QCanvasException):
    """Circuit conversion specific errors"""
    pass

class SimulationError(QCanvasException):
    """Quantum simulation specific errors"""
    pass

class ValidationError(QCanvasException):
    """Input validation errors"""
    pass
```

### Graceful Degradation
- Fallback to simpler backends if complex ones fail
- Provide partial results when full conversion isn't possible
- Clear error messages with suggested fixes
- Maintain system stability even with invalid inputs

## Performance Patterns

### Caching Strategy
- Cache conversion results for identical inputs
- Cache simulation results for common circuits
- Use Redis for distributed caching
- Implement cache invalidation strategies

### Async Processing
- Use async/await for I/O operations
- Implement background tasks for long simulations
- Provide progress updates via WebSocket
- Handle timeouts and resource limits

### Resource Management
- Implement circuit size limits
- Set simulation timeout limits
- Monitor memory usage during simulations
- Provide resource usage feedback to users

## Security Patterns

### Input Validation
- Validate all user inputs on both frontend and backend
- Sanitize circuit code before processing
- Implement rate limiting for API endpoints
- Use parameterized queries for database operations

### Authentication & Authorization
- JWT-based authentication for user sessions
- Role-based access control for different features
- API key management for programmatic access
- Secure WebSocket connections

## Testing Patterns

### Test Structure
- Unit tests for individual components
- Integration tests for API endpoints
- End-to-end tests for user workflows
- Mock external dependencies and quantum backends

### Test Data Management
- Use fixtures for common test circuits
- Implement test data factories
- Maintain test circuit examples for each framework
- Use parameterized tests for multiple scenarios

## Out-of-Scope (per project scope)
- Pulse-level control/OpenPulse and calibration blocks
- Circuit timing constructs (delay, duration, box)
- Hardware-specific extensions and extern functions
- Memory management and quantum error correction
