# Q-CANVAS Project Scope and Proposal

## Project Teams

### QCanvas Team
- Umer Farooq
- Hussan Waseem Syed
- Muhammad Irtaza Khan

### QSim Team
- Aneeq Ahmed Malik
- Abeer Noor
- Abdullah Mehmood

## Supervised by
- Dr. Imran Ashraf (Project Supervisor)
- Dr. Muhammad Nouman Noor (Co-Supervisor)

Built under **Open Quantum Workbench**: A FAST University Initiative

## Abstract
This document presents the completed Q-CANVAS platform, a unified quantum simulation platform that successfully addresses the critical standardization gap in multi-framework quantum programming. The platform serves as a universal intermediary, translating quantum circuits written in popular frameworks (Qiskit, Cirq, PennyLane) into the standardized OpenQASM 3.0 intermediate representation. Q-CANVAS features a sophisticated web-based IDE with real-time circuit visualization, persistent user authentication, keyboard shortcuts, and an interactive example system. The platform integrates with the QSim quantum simulation backend via API to enable hybrid quantum-classical algorithm execution. This implementation unifies the quantum programming experience, accelerating development and learning while fostering collaboration in the quantum computing ecosystem.

## 1. Introduction

This document presents the completed Q-CANVAS platform, a unified quantum simulation platform that successfully addresses the critical standardization gap in multi-framework quantum programming. It outlines the implemented features of the platform, detailing the comprehensive solution that unifies quantum programming across multiple frameworks. The document covers the architectural design, implemented features, and the successful integration of all planned components.

### Key Implemented Features:
- ✅ **Multi-Framework Compilation**: Qiskit, Cirq, PennyLane to OpenQASM 3.0 conversion
- ✅ **Advanced Web IDE**: Monaco Editor with syntax highlighting, multi-file workspace
- ✅ **Real-time Simulation**: QSim backend integration with multiple simulators
- ✅ **Authentication System**: Persistent login, demo accounts, conditional UI
- ✅ **Keyboard Shortcuts**: Comprehensive shortcut system (Ctrl+S, Ctrl+N, Ctrl+B, etc.)
- ✅ **Example System**: Pre-built quantum examples with smart loading
- ✅ **Settings & Preferences**: Theme selection, auto-save, format-on-save
- ✅ **Responsive Design**: Mobile-first approach with adaptive layouts
- ✅ **File Management**: Automatic naming, export, multi-file support

### 1.1 Problem Statement
The field of quantum computing is nascent and rapidly evolving, leading to a significant lack of standardization. Major technology companies, including IBM, Google, Xanadu, Rigetti, Amazon, and Microsoft, have developed their own proprietary software frameworks and languages (e.g., Qiskit, Cirq, PennyLane, PyQuil, Braket, Q#). This fragmentation creates a high barrier to entry for new developers and researchers, who must learn multiple complex ecosystems to work across different quantum hardware platforms. There is currently no universal platform that allows for the seamless integration, comparison, and execution of quantum circuits written in these diverse frameworks, even as pulse-level programming becomes more prevalent. This project aims to develop a software system that solves this interoperability problem, enabling a more efficient and collaborative quantum research and development environment.

### 1.2 Motivation
The motivation for selecting this problem is multi-faceted. Firstly, the current state of fragmentation is inefficient and slows down progress in the field, particularly as variational algorithms show promise on near-term devices. Secondly, drawing inspiration from classical computing, where ecosystems converge on standard languages (e.g., JavaScript for web development, Python for data science), a unified platform is a necessary evolution for quantum computing. Finally, different quantum frameworks have unique strengths, and a platform that leverages all of them would empower developers to create more powerful and sophisticated quantum applications without being locked into a single vendor's ecosystem.

### 1.3 Problem Solution
The application being specified is Q-CANVAS: A Quantum Simulation Platform for Multi-Framework Quantum Programming. It is a software platform designed to serve as a universal intermediary, translating and executing code from major quantum frameworks through a common intermediate representation based on OpenQASM 3.0. The primary goal is to unify the quantum programming experience, thereby accelerating development and learning by building upon fundamental quantum gates and established compilation principles.

The core objectives of the Q-CANVAS platform are:
- To provide robust multi-framework support for Qiskit, Cirq, PennyLane, and others.
- To implement a universal quantum code conversion engine using OpenQASM 3.0 as the intermediate representation, supporting Unicode character properties for comprehensive parsing.
- To develop a smart compilation system featuring AST-based parsing, intelligent gate mapping, and built-in validation.
- To enable seamless hybrid CPU and Quantum Processing Unit (QPU) integration for efficient execution of hybrid quantum-classical algorithms.
- To create an extensible architecture that allows for community-powered, plug-and-play language integration.
- To foster educational innovation through pre-built examples, gamified learning, and advanced circuit visualization.
- To build a community-oriented platform with GitHub-style circuit sharing and detailed user analytics, following modern typesetting principles.

### 1.4 Stakeholders
The key stakeholders for the Q-CANVAS project are:
- Quantum Computing Researchers & Academics: Who require a standardized tool for comparing algorithms across frameworks.
- Quantum Software Developers: Who need an efficient, multi-framework development environment to build applications.
- Students and Educators: Who will use the platform as an educational tool to learn quantum programming concepts without framework-specific barriers.
- Platform Administrators: Who will curate and manage the integrated language support and community content.
- Quantum Hardware Companies: Who may benefit from increased accessibility and a larger developer ecosystem.

## 2. Project Description

This chapter provides a comprehensive overview of the Q-CANVAS project. It details the project's scope, defining its core functionalities and boundaries. The architectural modules are broken down with their specific features, followed by the complete technology stack required for implementation. The chapter concludes with the work division among team members and a high-level project timeline.

### 2.1 Scope
The scope of the Q-CANVAS project encompasses the development of a unified cloud-based quantum simulation platform that serves as a multi-framework compiler and intermediary. The core functionality is the translation of quantum circuits written in popular high-level frameworks (Qiskit, Cirq, PennyLane) into the standardized OpenQASM 3.0 intermediate representation. This involves implementing a significant portion of the OpenQASM 3.0 language specification, including core types, gates, classical instructions, and scoping rules, while explicitly excluding specialized features like pulse-level control and hardware-specific extensions. The platform will feature a sophisticated web-based IDE with syntax highlighting, IntelliSense, and real-time circuit visualization. It will manage user authentication, role-based access, and provide a GitHub-style repository for circuit sharing. Furthermore, the platform will integrate with a separate quantum simulation backend (QSim) via a well-defined API to enable the execution of hybrid quantum-classical algorithms, splitting code between classical CPU and quantum QPU resources for optimal performance. The project is strictly a software solution and does not include the development of underlying quantum hardware or the QSim execution engine itself.

### 2.2 Modules
The system is architected into several key modules, primarily focused on a web application.

#### 2.2.1 Compilation Engine Core
The central module responsible for parsing, validating, and converting quantum code from supported frameworks into OpenQASM 3.0.
1. Multi-Framework Parser Support for Qiskit, Cirq, and PennyLane.
2. AST-Based Parsing and Intelligent Gate Mapping.
3. OpenQASM 3.0 Code Generation and Validation.
4. Syntax and Semantic Error Checking.

#### 2.2.2 Hybrid Execution Orchestrator
Manages the seamless integration and execution flow between classical and quantum processing units.
1. Hybrid Code File Segmentation (CPU vs. QPU blocks).
2. API Integration Layer for QSim Backend Communication.
3. Intelligent Job Queuing and Resource Management.

#### 2.2.3 Web IDE (Frontend)
The user-facing interface built with Next.js, providing a full-featured development environment.
1. Monaco Editor Integration with Quantum Language IntelliSense.
2. Real-Time, Interactive Quantum Circuit Rendering.
3. Multi-Theme Support and Multi-File Workspace.
4. Results Visualization with Histograms and Charts.
5. Advanced Keyboard Shortcuts System (Ctrl+S, Ctrl+N, Ctrl+B, etc.).
6. Simulation Controls (Backend Selection, Shots Configuration).
7. Responsive Design with Mobile-First Approach.

#### 2.2.4 User & Community Platform
Handles user management, social features, and educational content.
1. User Registration, Authentication, and Role Management.
2. Persistent Login with Session Management.
3. GitHub-Style Circuit Sharing and Repository System.
4. Gamified Learning Paths and Achievement System.
5. Pre-Built Example Circuit Library with Interactive Loading.
6. Smart Example Flow (Authentication-aware example loading).

#### 2.2.5 Backend API & Services
The server-side infrastructure that powers the application logic and data persistence.
1. RESTful API with FastAPI for all frontend operations.
2. PostgreSQL Database with SQLAlchemy ORM for data storage.
3. Redis-based Intelligent Caching for improved performance.
4. Usage Analytics and Monitoring System.

### 2.3 Tools and Technologies
- Version Control & Project Management: Git, GitHub, Trello
- Frontend: Next.js 14, React 18, TypeScript, Tailwind CSS, Monaco Editor, Chart.js, Lucide React Icons
- Backend: Python, FastAPI, Uvicorn, Pydantic, QSim Integration
- Quantum Frameworks: Qiskit, Cirq, PennyLane, OpenQASM 3.0, QSim Backend
- Database & Cache: PostgreSQL, SQLAlchemy, Alembic, Redis
- UI/UX: Responsive Design, Keyboard Shortcuts, Toast Notifications
- DevOps & Deployment: Docker, CI/CD (to be determined)
- Communication: Discord

### 2.4 Work Division
Responsibility for modules and features is assigned based on team member roles and expertise.

| Name | Registration | Responsibility/Module/Feature |
|------|-------------|------------------------------|
| Umer Farooq | 22I-0891 | Project Lead: Overall Architecture, Quantum Compilation Core (Module 1), Database & Security Schema, API Design, Final Integration |
| Hussan Waseem Syed | 22I-0893 | Frontend Specialist: Web IDE Module (Module 3) - Next.js App, Monaco Editor, Themes, Circuit Visualizations (D3.js) |
| Muhammad Irtaza Khan | 22I-0911 | Backend Specialist: Backend API & Services (Module 5) - FastAPI Server, Authentication, QSim API Integration, Caching (Redis) |

### 2.5 Current Implementation Status

As of November 2025, Q-CANVAS has been successfully implemented with the following completed features:

#### ✅ Completed Features
- **Multi-Framework Compilation Engine**: Full support for Qiskit, Cirq, and PennyLane conversion to OpenQASM 3.0
- **Web IDE**: Advanced Monaco Editor with syntax highlighting, multi-file workspace, and responsive design
- **Authentication System**: Persistent login, demo accounts, and role-based access
- **Simulation Integration**: QSim backend integration for real-time quantum execution
- **Keyboard Shortcuts**: Comprehensive shortcut system (Ctrl+S, Ctrl+N, Ctrl+B, etc.)
- **Example System**: Pre-built quantum examples with smart loading
- **Settings & Preferences**: Theme selection, auto-save, format-on-save options
- **User Experience**: Conditional UI based on auth status, smooth navigation flows

#### 🔄 Implementation Highlights
- **Simulation Controls**: Backend selection (Cirq, Qiskit, PennyLane), shots configuration
- **File Management**: Automatic naming, multi-file support, export functionality
- **Real-time Feedback**: Toast notifications, progress indicators, error handling
- **Responsive Design**: Mobile-first approach with adaptive layouts
- **Performance**: Optimized rendering, efficient state management
- **Expanded Example Library (November 2025)**: 25+ pre-built quantum examples
  - Quantum Teleportation (all 3 frameworks)
  - Deutsch-Jozsa Algorithm (all 3 frameworks)
  - Quantum Random Number Generator (all 3 frameworks)
  - Grover's Search (all 3 frameworks)
  - XOR Demonstration (PennyLane)
  - QML XOR Classifier (PennyLane) - Quantum Machine Learning
  - Bell State, GHZ, QFT, VQE, QAOA, QNN, Error Correction
- **File Templates System**: Separate initial files and templates for variety
- **Parser Enhancements**: If-else support across all frameworks, variable tracking, loop variable handling

### 2.6 Updated Timeline
The project execution has been completed with iterative development:

| Phase | Status | Key Deliverables |
|-------|--------|------------------|
| Foundation | ✅ Complete | Core compilation engine, basic web IDE, multi-framework support |
| Integration | ✅ Complete | QSim backend integration, authentication, user management |
| Enhancement | ✅ Complete | Advanced UI/UX, keyboard shortcuts, example system, settings |
| Production | ✅ Complete | Full-featured quantum IDE with simulation capabilities |

## 3. Language Constructs Reference

This chapter defines the precise technical boundaries of the Q-CANVAS compiler. The core functionality is the accurate translation of high-level quantum frameworks into the OpenQASM 3.0 intermediate representation. To manage this complex undertaking, the implementation of OpenQASM 3.0 language features will be divided into distinct phases. The following tables provide a detailed breakdown of all language constructs and their scheduled implementation phase, clearly delineating what is included within the project's scope for the initial release and what is planned for future iterations or explicitly excluded.

### 3.1 Implementation Phases Legend
- **Iteration I**: Essential core features for basic quantum programming and MVP release.
- **Iteration II**: Advanced features for extended functionality and production release.
- **Excluded**: Specialized features deferred to future releases or considered out of scope for this project.

### 3.2 Language Constructs Implementation Plan

#### 3.2.1 Comments and Version Control

| Feature | Phase |
|---------|-------|
| Single-line Comments (//) | Iteration I |
| Multi-line Comments (/* */) | Iteration I |
| Version String (OPENQASM 3.0) | Iteration I |
| Include Statements | Iteration I |

#### 3.2.2 Types and Casting

| Feature | Phase |
|---------|-------|
| Identifiers | Iteration I |
| Variables | Iteration I |
| Quantum Types (qubit) | Iteration I |
| Physical Qubits ($0, $1, ...) | Excluded |
| Boolean Type (bool) | Iteration I |
| Bit Type (bit) | Iteration I |
| Integer Type (int) | Iteration I |
| Unsigned Integer Type (uint) | Iteration I |
| Float Type (float) | Iteration I |
| Angle Type (angle) | Iteration I |
| Complex Type (complex) | Iteration II |
| Compile-time Constants (const) | Iteration I |
| Literals (Integer, Float, Boolean) | Iteration I |
| Arrays | Iteration I |
| Duration Type (duration) | Excluded |
| Stretch Type (stretch) | Excluded |
| Aliasing | Iteration I |
| Index Sets and Slicing | Iteration I |
| Register Concatenation | Iteration I |
| Classical Value Bit Slicing | Excluded |
| Array Concatenation | Iteration I |
| Type Casting | Iteration II |

#### 3.2.3 Gates

| Feature | Phase |
|---------|-------|
| Applying Gates | Iteration I |
| Gate Broadcasting | Iteration I |
| Parameterized Gates | Iteration I |
| Hierarchical Gate Definitions | Iteration I |
| Control Modifier (ctrl@) | Iteration I |
| Negative Control Modifier (negctrl@) | Iteration II |
| Multi-Control (ctrl(n)@) | Iteration II |
| Inverse Modifier (inv@) | Iteration I |
| Power Modifier (pow(k)@) | Iteration II |
| Built-in U Gate | Iteration I |
| Global Phase Gate (gphase) | Iteration I |

#### 3.2.4 Built-in Quantum Instructions

| Instruction | Phase |
|-------------|-------|
| Reset Instruction | Iteration I |
| Measurement Instruction | Iteration I |
| Barrier Instruction | Iteration I |
| Delay Instruction | Excluded |

#### 3.2.5 Classical Instructions

| Instruction | Phase |
|-------------|-------|
| Assignment Statements | Iteration I |
| Arithmetic Operations (+, -, *, /) | Iteration I |
| Comparison Operations (<, >, ==, !=) | Iteration I |
| Logical Operations (&&, \|\|, !) | Iteration I |
| Bitwise Operations (&, \|, ^, ~) | Iteration II |
| Shift Operations (<<, >>) | Iteration II |
| If Statements | Iteration I |
| If-Else Statements | Iteration I |
| While Loops | Iteration II |
| For Loops | Iteration I |
| Break Statement | Iteration II |
| Continue Statement | Iteration II |
| Mathematical Functions | Iteration II |

#### 3.2.6 Subroutines

| Feature | Phase |
|---------|-------|
| Function Definitions | Iteration II |
| Function Calls | Iteration II |
| Return Statements | Iteration II |
| Parameter Passing | Iteration II |
| Local Variables | Iteration II |

#### 3.2.7 Scoping of Variables

| Scope | Phase |
|-------|-------|
| Global Scope | Iteration I |
| Function Scope | Iteration II |
| Block Scope | Iteration II |
| Variable Shadowing | Iteration II |

#### 3.2.8 Directives

| Directive | Phase |
|----------|-------|
| Pragma Directives | Excluded |
| Input/Output Directives | Iteration I |
| Annotation Directives | Excluded |

#### 3.2.9 Standard Library and Built-ins

| Item | Phase |
|------|-------|
| Standard Gate Library | Iteration I |
| Built-in Functions | Iteration I |
| Mathematical Constants | Iteration I |
| Trigonometric Functions | Iteration II |
| Exponential Functions | Iteration II |

### 3.3 Explicitly Excluded Features
The following broad categories of OpenQASM 3.0 are explicitly excluded from the scope of this project and are deferred to future work:
- **Circuit Timing**: Delay Instructions, Duration Literals, Box Statement
- **Pulse-level Descriptions**: Calibration Blocks, Pulse Gates, Waveforms, Frames, Ports
- **OpenPulse Grammar**: Complete pulse-level control specifications
- **Advanced Features**: Extern Functions, Memory Management, Hardware-specific Extensions, Quantum Error Correction

Complete specifications are available at: https://openqasm.com/versions/3.0/

## 4. Conclusions and Future Work

### 4.1 Conclusions
The Q-CANVAS project proposes a critical solution to a significant and growing problem within the quantum computing ecosystem: framework fragmentation. By developing a unified simulation platform that acts as a multi-framework compiler, this project addresses the standardization gap that currently hinders developer productivity, educational accessibility, and cross-platform research. The proposed architecture, centered on OpenQASM 3.0 as a universal intermediate representation, demonstrates a viable and technically sound approach to integrating disparate quantum programming languages like Qiskit, Cirq, and PennyLane.

The conclusion of this proposal is that such a platform is not only feasible but necessary for the continued maturation of the quantum software field. Q-CANVAS is designed to be more than just a tool; it is conceived as the foundational bridge between today's learners and tomorrow's quantum breakthroughs. By lowering the barrier to entry and providing a consistent, powerful development environment, this project aims to accelerate innovation and collaboration. In a world that is increasingly quantum, it is imperative that our development tools evolve beyond classical paradigms and vendor-specific silos to reflect this new reality.

### 4.2 Future Work
The development of Q-CANVAS, as outlined in this proposal, establishes a strong foundation. However, the roadmap for the platform extends far beyond the initial scope. Future work will focus on expansion, deepening integration, and exploring new frontiers in quantum tooling:

- **Expansion of Language Support**: A primary future goal is the integration of new quantum programming languages such as Q# (Microsoft) and Braket (Amazon). Furthermore, achieving deeper language support within existing frameworks will be crucial. This involves implementing more advanced syntax trees, supporting domain-specific library functions, and handling framework-specific optimizations that are currently beyond the initial scope.

- **Pulse-Level Control and Calibration**: Extending the platform to support OpenPulse and pulse-level descriptions would allow researchers to work with quantum hardware at a lower, more precise level, enabling calibration, error mitigation, and advanced control techniques.

- **Advanced Error Correction and Mitigation**: Integrating built-in support for quantum error correction codes and error mitigation strategies would provide immense value for users running algorithms on noisy intermediate-scale quantum (NISQ) simulators and future hardware.

- **Native Hardware Integration**: While initially focused on simulation, the platform's architecture is designed to be extended. Future work would involve building direct APIs to various quantum processing units (QPUs) from IBM, Google, IonQ, Rigetti, and others, making Q-CANVAS a true cloud-agnostic portal for quantum execution.

- **Advanced Collaboration Features**: Building upon the GitHub-style sharing, features like real-time collaborative editing, code review tools specifically for quantum circuits, and version control for quantum experiments could be developed.

- **Enhanced Visual Debugger**: Creating a sophisticated visual debugger that allows developers to step through quantum circuit execution, view the statevector or density matrix at any point, and visualize the impact of each gate would be a powerful educational and professional tool.

The successful implementation of this proposal will create a powerful and extensible platform ready to incorporate these advanced features, solidifying its role as a standard-setting tool in the quantum computing landscape.

## References

[1] Thomas Alexander, Naoki Kanazawa, Daniel J. Egger, Lauren Capelluto, Christopher J. Wood, Ali Javadi-Abhari, and David C. McKay. Qiskit pulse: Programming quantum computers through the cloud with pulses. Quantum Science and Technology, 5(4):044006, aug 2020.

[2] Adriano Barenco, Charles H. Bennett, Richard Cleve, David P. DiVincenzo, Norman Margolus, Peter Shor, Tycho Sleator, John A. Smolin, and Harald Weinfurter. Elementary gates for quantum computation. Physical Review A, 52(5):3457–3467, nov 1995.

[3] Wikipedia contributors. Unicode character property, general category — Wikipedia, the free encyclopedia, 2022. [Online; accessed 14-December-2022].

[4] DiCarloLab-Delft. Dicarlolab-delft/pycqed_py3. https://github.com/DiCarloLab-Delft/PycQED_py3, May 2021.

[5] Xiang Fu, Leon Riesebos, M. A. Rol, J. van Straten, J. van Someren, N. Khammassi, Imran Ashraf, R. F. L. Vermeulen, V. Newsum, K. K. L. Loh, J. C. de Sterke, W. J. Vlothuizen, R. N. Schouten, L. DiCarlo, and K. L. M. Bertels. An experimental microarchitecture for a superconducting quantum processor. In Proceedings of the 50th Annual IEEE/ACM International Symposium on Microarchitecture, pages 813–825, oct 2017.

[6] Donald E. Knuth and Duane Bibby. The TeXbook, volume 3. Addison-Wesley, Reading, 1984.

[7] A Kolyshkin and S Nazarovs. Stability of slowly diverging flows in shallow water. Mathematical Modeling and Analysis, 2007.

[8] David C. McKay, Thomas Alexander, Luciano Bello, Michael J. Biercuk, Lev Bishop, Jiayin Chen, Jerry M. Chow, Antonio D. Córcoles, Daniel Egger, Stefan Filipp, Juan Gomez, Michael Hush, Ali Javadi-Abhari, Diego Moreda, Paul Nation, Brent Paulovicks, Erick Winston, Christopher J. Wood, James Wootton, and Jay M. Gambetta. Qiskit backend specifications for openqasm and openpulse experiments. arXiv:1809.03452 [quant-ph], 2018.

[9] Thien Nguyen and Alexander McCaskey. Enabling pulse-level programming, compilation, and execution in XACC. arXiv:2003.11971 [physics.quant-ph], mar 2020.

[10] Alberto Peruzzo, Jarrod McClean, Peter Shadbolt, Man-Hong Yung, Xiao-Qi Zhou, Peter J. Love, Alán Aspuru-Guzik, and Jeremy L. O'Brien. A variational eigenvalue solver on a photonic quantum processor. Nature Communications, 5(1):4213, jul 2014.

[11] Quil-lang. quil-lang/quil. https://github.com/quil-lang/quil, June 2021.

[12] M. V. Wilkes. The best way to design an automatic calculating machine. In The Early British Computer Conferences, pages 182–184, Cambridge, MA, USA, May 1989. MIT Press.
