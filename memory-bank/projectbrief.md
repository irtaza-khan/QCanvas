# QCanvas Project Brief

## Project Vision
QCanvas is a Quantum Unified Simulator - a comprehensive platform that bridges the gap between different quantum computing frameworks, providing a unified interface for circuit conversion, simulation, and visualization.

> Authoritative scope: see `docs/project-scope.md` for the latest official scope and exclusions.

## Core Requirements

### Primary Goals
1. **Framework Unification**: Enable seamless conversion between Cirq, Qiskit, and PennyLane
2. **Real-time Simulation**: Provide instant quantum circuit execution and visualization
3. **Educational Platform**: Create an accessible learning environment for quantum computing
4. **Production Ready**: Build a scalable, monitored, and secure platform

### Key Features
- Multi-framework circuit conversion (Cirq ↔ Qiskit ↔ PennyLane)
- Real-time quantum simulation with multiple backends
- Interactive visualization of quantum states and circuits
- WebSocket-based real-time updates
- Comprehensive API with automatic documentation
- Docker-based deployment with monitoring

### Target Users
- **Researchers**: Comparing algorithms across frameworks
- **Students**: Learning quantum computing concepts
- **Developers**: Building quantum applications
- **Educators**: Teaching quantum computing principles

## Technical Scope

### Architecture
- **Hybrid Approach**: Next.js frontend + FastAPI backend
- **Shared TypeScript Types**: Type safety across services
- **OpenQASM 3.0**: Universal intermediate representation
- **Microservices**: Modular quantum processing components

### Supported Frameworks
- **Cirq** (Google): Near-term quantum devices
- **Qiskit** (IBM): Comprehensive quantum computing
- **PennyLane** (Xanadu): Quantum machine learning

### Simulation Backends
- Statevector: Exact quantum state simulation
- Density Matrix: Mixed states and noise handling
- Stabilizer: Efficient Clifford circuit simulation

## Success Criteria
1. Successful conversion between all supported frameworks
2. Real-time simulation with <5 second response time
3. Comprehensive test coverage (>80%)
4. Production deployment with monitoring
5. User-friendly interface for quantum computing beginners

## Constraints
- Must support OpenQASM 3.0 standard
- Must be educational and accessible
- Must handle quantum computing complexity gracefully
- Must be deployable in containerized environments
- Must maintain type safety across the entire stack

## Project Boundaries
- Focus on circuit conversion and simulation (not quantum hardware)
- Support for 3 major frameworks initially
- Web-based interface (no mobile app initially)
- Educational and research focus (not commercial quantum computing)
- Explicitly excluded: Pulse-level/OpenPulse, hardware-specific extensions, extern functions, memory mgmt, QEC, circuit timing features (delay, duration, box).
