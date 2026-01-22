# QCanvas: The Quantum Unified Simulator
## Final Year Project Presentation - Status & Roadmap

---

## Slide 1: Title Slide
**Title:** QCanvas: Bridging the Quantum Divide
**Subtitle:** A Unified Cloud-Based Quantum Simulation Platform
**Presenters:** 
- Umer Farooq (Project Lead)
- Hussan Waseem Syed
- Muhammad Irtaza Khan
**Supervisors:** Dr. Imran Ashraf, Dr. Muhammad Nouman Noor
**Context:** Final Year Project - Progress & Future Vision

---

## Slide 2: The Quantum Fragmentation Problem
**Header:** The "Tower of Babel" in Quantum Computing
**Core Message:** The quantum ecosystem is fragmented, creating barriers for learning and research.
**Key Points:**
- **Silos:** Qiskit (IBM), Cirq (Google), and PennyLane (Xanadu) use incompatible languages.
- **Complexity:** Researchers & students must learn multiple unique frameworks.
- **No Standardization:** Lack of a unified tool to compare and execute circuits across hardware.
- **The Gap:** Disconnect between high-level Python code and actual quantum execution.

---

## Slide 3: Our Solution - QCanvas
**Header:** One Platform, All Frameworks
**Core Message:** QCanvas is the "Universal Translator" for the quantum era.
**Key Features:**
- **Unified Interface:** First-of-its-kind Web IDE supporting Qiskit, Cirq, and PennyLane simultaneously.
- **Standardization:** Built on **OpenQASM 3.0** as the universal intermediate language.
- **Hybrid Execution:** Seamless bridging of Classical (CPU) and Quantum (Simulator) processing.
- **Educational:** Instant visualization and feedback to democratize quantum literacy.

---

## Slide 4: Project Timeline Overview (The 4 Sprints)
**Header:** The Development Roadmap
**Visual:** A timeline split into "Completed" and "Future" phases.
- **Sprint 1 (Done):** Foundation & Core Compilation
- **Sprint 2 (Done):** Advanced Features, Security & Persistence
- **Sprint 3 (Future):** Intelligence & Community
- **Sprint 4 (Future):** Production & Deep Integration

---

## Slide 5: Sprint 1 - The Foundation (Detailed Implementation)
**Header:** Laying the Quantum Bedrock
**Focus:** Establishing the conversion engine and IDE capabilities.

**1. Conversion Engine Capabilities:**
- **Supported Quantum Gates (20+):**
    - **Single-qubit:** X, Y, Z, H, S, T, RX, RY, RZ
    - **Two-qubit:** CNOT, CZ, SWAP, CRX, CRY, CRZ
    - **Multi-qubit:** Toffoli, Fredkin
    - **Special:** U (universal single-qubit), Phase gates
- **Core Logic:** Robust parsing and translation to OpenQASM 3.0.

**2. IDE Capabilities:**
- **Monaco Editor:** Industry-standard engine (same as VS Code) for robust editing.
- **Multi-Theme Support:** Fully functional Light and Dark modes.
- **Multi-File Workspace:** Manage complex projects with multiple files.
- **Real-Time Conversion:** Instant preview of generated OpenQASM code.

---

## Slide 6: Sprint 1 - Technical Challenges & Solutions
**Header:** Overcoming Early Hurdles
**Focus:** Resolving parsing and basic architecture issues.

- **Framework Syntax Variations:**
    - *Solution:* Built framework-specific AST parsers with a unified Intermediate Representation (IR) layer.
- **Gate Parameterization Differences:**
    - *Solution:* Created parameter normalization engine (degrees ↔ radians) to ensure consistency.
- **Qubit Indexing Inconsistencies:**
    - *Solution:* Implemented qubit mapping layer with strict validation logic.
- **Performance (Large Circuits):**
    - *Solution:* Optimized AST traversal and implemented incremental parsing strategies.
- **OpenQASM 3.0 Complexity:**
    - *Solution:* Focused on core subset for Iteration I, deferring advanced features to ensure stability.

---

## Slide 7: Sprint 2 - Overview
**Header:** Deepening the Architecture
**Deliverable:** A secure, scalable, and more powerful platform.
**Key Pillars:**
1.  **Security & Persistence:** CIA Compliance and Database Layer.
2.  **Advanced Quantum Features:** Extended Language Support.
3.  **Hybrid Architecture:** CPU/QPU Orchestration.
4.  **Refinement:** Benchmarking and UI Polish.

---

## Slide 8: Sprint 2 - Security & Persistence
**Header:** Building a Secure & Persistent Layer
**Focus:** Compliance with the CIA Triad (Confidentiality, Integrity, Availability).

- **Authentication & Authorization:**
    - **User Auth:** Secure login and registration.
    - **Hashing:** Bcrypt password hashing with per-user salts.
    - **RBAC:** Role-Based Access Control to manage permissions.
    - **CIA Compliance:** Ensuring data integrity and confidentiality.

- **Database Infrastructure:**
    - **PostgreSQL:** robust relational database for production-grade reliability.
    - **SQLAlchemy ORM:** Type-safe database interactions and schema management.
    - **Persistence:** Storing user accounts, projects, and conversion history.

---

## Slide 9: Sprint 2 - Advanced Quantum Capabilities
**Header:** Beyond Basic Circuits
**Focus:** Supporting complex quantum algorithms and advanced constructs.

- **Advanced OpenQASM Features:**
    - **Control Flow:** `If/Else` statements, `For` and `While` loops.
    - **Classical Logic:** Bitwise operations (&, |, ^, ~, <<, >>) and arithmetic.
    - **Subroutines:** Reusable quantum functions with return values.
    - **Complex Types:** Support for complex numbers and angle types.

- **Expanded Framework Support:**
    - **PennyLane Integration:** Advanced gates (CSWAP, GlobalPhase) and state modifiers (`negctrl`, `pow`, `inv`).
    - **Qiskit/Cirq Compatibility:** Parity with advanced language features.

---

## Slide 10: Sprint 2 - Hybrid Architecture (CPU/QPU)
**Header:** Orchestrating Classical & Quantum Compute
**Focus:** Seamless separation of concerns for optimal performance.

- **API for QSim Compilation:**
    - **Hybrid Execution:** Distinct pipeline for splitting CPU-bound compilation from Quantum simulation.
    - **`/compile` Endpoint:** Offloads complex circuit logic and AST parsing.
    - **`/simulate` Endpoint:** Dedicated interface for the QSim backend.
    - **Job Isolation:** Ensures heavy conversions don't block simulation resources.

- **Frontend Integration (QCanvas SDK):**
    - **Usage:** Seamless integration via `from qcanvas import compile` to interface with the backend.
    - **Signature:** `compile(circuit, framework=None)` -> `str` (OpenQASM 3.0)

    ```python
    from qcanvas import compile
    import cirq

    # ... circuit definition ...
    qasm = compile(circuit, framework="cirq")
    ```

---

## Slide 11: Sprint 2 - Technical Challenges & Solutions
**Header:** Scaling for Complexity
**Focus:** Solving security, orchestration, and advanced logic challenges.

- **Hybrid Resource Management (CPU starvation):**
    - *Solution:* Implemented Asynchronous Job Isolation, decoupling CPU-heavy compilation from I/O-bound simulation.
- **Complex Control Flow Translation:**
    - *Solution:* Developed state-aware AST transformers to map recursive Python loops and conditional logic to OpenQASM.
- **Secure Persistence & Integrity:**
    - *Solution:* Integrated **PostgreSQL** with **SQLAlchemy** to manage ACID transactions and **Bcrypt** for secure credential storage.
- **Cross-Framework Feature Parity:**
    - *Solution:* Extended the IR to support advanced gate modifiers (`ctrl`, `pow`, `inv`) particularly for PennyLane integration.

---

## Slide 12: Sprint 2 - Refinement & Evaluation
**Header:** Polishing the User Experience
**Focus:** Proving the system works and making it usable.

- **Evaluation & Benchmarking:**
    - **Performance:** Measured conversion latencies (sub-150ms for standard circuits).
    - **Accuracy:** Validated gate fidelities against theoretical models.
    - **Scalability:** Stress-tested API endpoints.

- **Frontend Refinement:**
    - **Documentation:** Comprehensive User Guides and API Docs.
    - **Landing Page:** Professional onboarding experience.
    - **Responsiveness:** Mobile-first layout adjustments.
    - **Login Flow:** Smooth, secure authentication UI.

---

## Slide 13: Current Status Summary
**Header:** Where We Are Today
**Status:** **Features Verified & Architecture Stabilized**
- **Test Coverage:** 100% pass rate on 300+ unit and integration tests.
- **Performance:** Robust handling of 20+ qubit simulations.
- **Usability:** A production-ready environment for developers and students.
- **Ready for Next Phase:** Building Intelligence (Sprint 3) and Production Scale (Sprint 4).

---

## Slide 14: Sprint 3 - Intelligence & Extensibility (Future Work)
**Header:** Making QCanvas "Smart"
**Focus:** Enhancing education and community collaboration.
**Planned Deliverables:**
- 🚀 **"Quantum Explain It" Mode:** AI-driven explanations of circuit behavior and gate logic.
- 🚀 **Gamified Learning:** Interactive challenges, badges, and "Learning Paths".
- 🚀 **Circuit Repository:** GitHub-style sharing platform (Public/Private circuits, Forking).
- 🚀 **Plug-n-Play Plugins:** Community contributions for new languages (e.g., Q#, Braket).

---

## Slide 15: Sprint 4 - Integration & Production (Future Work)
**Header:** Enterprise-Grade Simulation
**Focus:** Deep integration with execution backends and advanced analytics.
**Planned Deliverables:**
- 🔮 **Deep QSim Integration:** Switching to gRPC for high-performance streaming.
- 🔮 **Advanced Visualization:** 3D Bloch spheres, Entanglement graphs, Probability heatmaps.
- 🔮 **User Analytics:** Detailed metrics on circuit complexity and usage.
- 🔮 **Public API:** Opening the QCanvas API for external developers.

---

## Slide 16: Conclusion
**Header:** Defining the Future of Quantum Tooling

- **Mission Accomplished (Sprints 1-2):**
    - solved the **"Interoperability"** problem.
    - Delivered a **Secure, Scalable, & Powerful** platform.
    - Verified functionality with 100% test coverage.

- **The Path Forward (Sprints 3-4):**
    - Solving **"Accessibility"** & **"Community"**.
    - Transforming QCanvas from a tool into an **Ecosystem**.

- **Final Word:**
    - Bridging the gap today to power the quantum breakthroughs of tomorrow.

**Thank You!**

---
