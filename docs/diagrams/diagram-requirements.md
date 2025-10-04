# QCanvas Diagram Requirements

## Overview
This document outlines all the UML diagrams required for the QCanvas project based on the FYP UML Workshop requirements and the project's comprehensive scope. The diagrams will provide visual documentation of the system's architecture, functionality, and user interactions.

## Required Diagrams

### 1. Use Case Diagram
**Purpose**: Show the main functionalities and actors interacting with the QCanvas system.

**Key Elements**:
- **Primary Actors**:
  - Quantum Computing Researchers
  - Quantum Software Developers  
  - Students and Educators
  - Platform Administrators
  - Quantum Hardware Companies

- **Main Use Cases**:
  - Convert Quantum Circuits (Cirq ↔ Qiskit ↔ PennyLane)
  - Generate OpenQASM 3.0 Code
  - Simulate Quantum Circuits
  - Visualize Circuit Diagrams
  - Manage User Accounts
  - Share Circuits (GitHub-style)
  - Access Educational Content
  - Monitor System Performance

- **Secondary Use Cases**:
  - Authenticate Users
  - Validate Circuit Syntax
  - Optimize Circuit Performance
  - Export/Import Circuits
  - Track Learning Progress

**Diagram Details**: This diagram will show the system boundary, all external actors, and their relationships with the system's core functionalities. It will demonstrate how different user types interact with various features of the platform.

### 2. High-Level Use Cases (Textual)
**Purpose**: Provide detailed textual descriptions of the main use cases.

**Key Use Cases to Document**:
1. **Convert Quantum Circuit**
   - **Actor**: Quantum Developer
   - **Goal**: Convert circuit from one framework to another
   - **Main Success Scenario**: User inputs Cirq code → System validates → Converts to OpenQASM 3.0 → Converts to Qiskit → Returns converted code
   - **Extensions**: Handle conversion errors, provide optimization suggestions

2. **Simulate Quantum Circuit**
   - **Actor**: Researcher/Student
   - **Goal**: Execute quantum simulation
   - **Main Success Scenario**: User provides circuit → System validates → Executes simulation → Returns results with visualization
   - **Extensions**: Handle simulation errors, provide progress updates

3. **Share Quantum Circuit**
   - **Actor**: Developer/Educator
   - **Goal**: Share circuit with community
   - **Main Success Scenario**: User creates circuit → System validates → User shares publicly → Others can access and use
   - **Extensions**: Handle privacy settings, manage permissions

### 3. Expanded Use Cases (Detailed)
**Purpose**: Provide comprehensive step-by-step descriptions of complex use cases.

**Key Expanded Use Cases**:
1. **Multi-Framework Circuit Conversion**
   - **Preconditions**: User is authenticated, valid circuit code provided
   - **Main Success Scenario**: 
     1. User selects source framework (Cirq/Qiskit/PennyLane)
     2. User inputs circuit code
     3. System validates syntax and structure
     4. System converts to OpenQASM 3.0 intermediate representation
     5. System converts to target framework
     6. System returns converted code with metadata
   - **Alternative Flows**: Handle syntax errors, provide conversion statistics
   - **Postconditions**: Converted code available, conversion logged

2. **Real-time Quantum Simulation**
   - **Preconditions**: Valid OpenQASM 3.0 circuit, simulation parameters set
   - **Main Success Scenario**:
     1. User submits circuit for simulation
     2. System validates circuit and parameters
     3. System queues simulation job
     4. System provides real-time progress updates via WebSocket
     5. System executes simulation on selected backend
     6. System returns results with visualization
   - **Alternative Flows**: Handle simulation timeouts, provide partial results
   - **Postconditions**: Simulation results available, performance metrics logged

### 4. Domain Model (Conceptual Class Diagram)
**Purpose**: Show the key concepts and their relationships in the quantum computing domain.

**Key Conceptual Classes**:
- **QuantumCircuit**: Core circuit representation
- **QuantumGate**: Individual quantum operations
- **Qubit**: Quantum bit representation
- **Measurement**: Quantum measurement operations
- **SimulationResult**: Results from quantum simulation
- **User**: Platform user
- **Framework**: Quantum computing framework (Cirq, Qiskit, PennyLane)
- **OpenQASMCode**: OpenQASM 3.0 representation
- **CircuitVisualization**: Visual representation of circuits
- **EducationalContent**: Learning materials and examples

**Relationships**:
- QuantumCircuit contains multiple QuantumGates
- QuantumCircuit operates on multiple Qubits
- QuantumCircuit can be converted to OpenQASMCode
- User creates and shares QuantumCircuits
- Framework provides specific implementations
- SimulationResult is generated from QuantumCircuit execution

### 5. System Sequence Diagram (SSD)
**Purpose**: Show the interaction between actors and the system for key use cases.

**Key SSDs to Create**:
1. **Circuit Conversion Process**
   - Actor: Quantum Developer
   - System: QCanvas Platform
   - External Systems: OpenQASM 3.0 Compiler
   - Flow: Input → Validation → Conversion → Output

2. **Quantum Simulation Process**
   - Actor: Researcher
   - System: QCanvas Platform
   - External Systems: Quantum Simulation Backend
   - Flow: Circuit Input → Validation → Simulation → Results

3. **User Authentication Process**
   - Actor: User
   - System: QCanvas Platform
   - External Systems: Authentication Service
   - Flow: Login → Validation → Session Creation → Access

### 6. Activity Diagram / Data Flow Diagram
**Purpose**: Show the detailed flow of activities and data through the system.

**Key Activity Diagrams**:
1. **Circuit Conversion Workflow**
   - Start: User inputs circuit code
   - Activities: Parse code, validate syntax, convert to OpenQASM 3.0, convert to target framework, validate output
   - Decision Points: Syntax valid?, Conversion successful?
   - End: Return converted code or error message

2. **Quantum Simulation Workflow**
   - Start: User submits circuit for simulation
   - Activities: Validate circuit, select backend, queue job, execute simulation, process results
   - Decision Points: Circuit valid?, Backend available?, Simulation successful?
   - End: Return simulation results or error

3. **User Registration Workflow**
   - Start: User requests account creation
   - Activities: Validate input, check uniqueness, create account, send confirmation
   - Decision Points: Input valid?, Email unique?, Account created?
   - End: Account created or error message

### 7. Operations Contracts
**Purpose**: Define the preconditions, postconditions, and responsibilities for key operations.

**Key Contracts**:
1. **ConvertCircuit Operation**
   - **Preconditions**: Valid source code, supported framework, user authenticated
   - **Postconditions**: OpenQASM 3.0 code generated, target framework code created, conversion logged
   - **Responsibilities**: Parse source, validate syntax, convert to intermediate representation, generate target code

2. **SimulateCircuit Operation**
   - **Preconditions**: Valid OpenQASM 3.0 circuit, simulation parameters set, backend available
   - **Postconditions**: Simulation results generated, performance metrics recorded, results stored
   - **Responsibilities**: Validate circuit, execute simulation, process results, update statistics

3. **AuthenticateUser Operation**
   - **Preconditions**: Valid credentials provided, authentication service available
   - **Postconditions**: User session created, access permissions set, login logged
   - **Responsibilities**: Validate credentials, create session, set permissions, log activity

### 8. Sequence Diagram
**Purpose**: Show detailed interactions between system components for specific scenarios.

**Key Sequence Diagrams**:
1. **Circuit Conversion Sequence**
   - Participants: User, Frontend, Backend API, Converter Service, OpenQASM Generator
   - Flow: User input → Frontend validation → API call → Backend processing → Conversion → Response

2. **Real-time Simulation Sequence**
   - Participants: User, Frontend, WebSocket Manager, Simulation Service, Backend
   - Flow: User request → WebSocket connection → Progress updates → Simulation execution → Results

3. **User Authentication Sequence**
   - Participants: User, Frontend, Authentication Service, Database, Session Manager
   - Flow: Login request → Credential validation → Session creation → Access granted

### 9. Architecture Diagram
**Purpose**: Show the high-level system architecture and component relationships.

**Key Architectural Components**:
- **Frontend Layer**: Next.js application with React components
- **API Gateway**: FastAPI backend with REST endpoints
- **Conversion Engine**: Quantum framework converters
- **Simulation Engine**: Quantum simulation backends
- **Database Layer**: PostgreSQL for persistence
- **Cache Layer**: Redis for performance
- **WebSocket Service**: Real-time communication
- **Authentication Service**: User management and security

**Architecture Patterns**:
- **Microservices Architecture**: Separate services for different functionalities
- **API Gateway Pattern**: Centralized API management
- **Event-Driven Architecture**: WebSocket-based real-time updates
- **CQRS Pattern**: Separate read and write operations
- **Repository Pattern**: Data access abstraction

### 10. Component Diagram
**Purpose**: Show the internal structure and relationships of system components.

**Key Components**:
- **Frontend Components**: Editor, Visualizer, Results Display, User Interface
- **Backend Services**: API Gateway, Conversion Service, Simulation Service, Authentication Service
- **Quantum Processing**: Framework Parsers, OpenQASM Generator, Circuit Validators
- **Data Layer**: Database Models, Cache Managers, File Storage
- **External Integrations**: Quantum Frameworks, Simulation Backends, Authentication Providers

### 11. Deployment Diagram
**Purpose**: Show the physical deployment architecture and infrastructure.

**Key Deployment Elements**:
- **Web Server**: Nginx reverse proxy
- **Application Servers**: Multiple FastAPI instances
- **Database Servers**: PostgreSQL primary and replicas
- **Cache Servers**: Redis cluster
- **Load Balancers**: Traffic distribution
- **Monitoring**: Prometheus and Grafana
- **Container Orchestration**: Docker and Docker Compose

### 12. State Diagram
**Purpose**: Show the state transitions for key system entities.

**Key State Diagrams**:
1. **User Session States**
   - States: Anonymous, Authenticating, Authenticated, Active, Inactive, Expired
   - Transitions: Login, Logout, Timeout, Activity

2. **Circuit Conversion States**
   - States: Pending, Validating, Converting, Completed, Failed
   - Transitions: Start conversion, Validation success/failure, Conversion success/failure

3. **Simulation Job States**
   - States: Queued, Running, Completed, Failed, Cancelled
   - Transitions: Start simulation, Progress updates, Completion, Error handling

## Diagram Implementation Guidelines

### Visual Standards
- **Consistency**: Use consistent notation and styling across all diagrams
- **Clarity**: Ensure diagrams are readable and self-explanatory
- **Completeness**: Include all necessary elements and relationships
- **Accuracy**: Reflect the actual system architecture and behavior

### Documentation Requirements
- **Descriptions**: Provide detailed descriptions for each diagram
- **Legends**: Include legends for symbols and notations
- **Context**: Explain the purpose and scope of each diagram
- **Relationships**: Show how diagrams relate to each other

### Tools and Software
- **UML Tools**: Rational Software Architect, Enterprise Architect, or similar
- **Diagramming Tools**: Lucidchart, Draw.io, or Visio
- **Version Control**: Track diagram changes in Git
- **Documentation**: Maintain comprehensive documentation for each diagram

## Success Criteria

### Completeness
- All required diagram types are created
- Each diagram includes all necessary elements
- Relationships between diagrams are clearly defined
- Documentation is comprehensive and accurate

### Quality
- Diagrams are professionally formatted and readable
- Notation follows UML standards
- Content accurately reflects the system design
- Diagrams are maintainable and updatable

### Usability
- Diagrams serve their intended purpose
- Stakeholders can understand the system from the diagrams
- Diagrams support development and maintenance activities
- Documentation is accessible and well-organized

## Conclusion

These diagrams will provide comprehensive visual documentation of the QCanvas system, supporting development, maintenance, and stakeholder communication. The diagrams will evolve with the system, ensuring they remain accurate and useful throughout the project lifecycle.
