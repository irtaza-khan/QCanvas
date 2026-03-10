# QCanvas Architecture Documentation

## Overview

QCanvas is a modular, scalable quantum computing IDE platform with a clear separation of concerns and extensible architecture. It provides multi-framework quantum circuit compilation to OpenQASM 3.0, real-time simulation via QSim, hybrid CPU–QPU execution, user authentication, project/file management, gamification, and 3D circuit visualization. This document describes the system architecture, component interactions, and design decisions as implemented.

## System Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          Frontend (Next.js 14)                           │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐           │
│  │  Circuit    │ │  3D Circuit│ │  Results &  │ │Gamification│           │
│  │  Editor     │ │ Visualizer │ │ Histograms  │ │ & Profile  │           │
│  │ (Monaco)    │ │(Three.js)  │ │ (Chart.js)  │ │  (XP/Lvl)  │           │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘           │
│                                                                          │
│  - App Router & Page Routes (login, signup, app, examples, profile, …)  │
│  - Zustand State Management (auth, editor, gamification stores)          │
│  - TypeScript + Tailwind CSS                                             │
│  - REST API Client with local/remote fallback                            │
└──────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         Backend (FastAPI)                                 │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐           │
│  │  REST API   │ │  Auth &    │ │  Services   │ │ Middleware  │           │
│  │  Routes     │ │  JWT       │ │  Layer      │ │(Rate Limit, │           │
│  │             │ │            │ │             │ │ Audit, CSP) │           │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘           │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐           │
│  │  Database   │ │ QCanvas    │ │Gamification │ │  Project &  │           │
│  │  (Postgres) │ │ Runtime    │ │  Service    │ │File Mgmt    │           │
│  │  + Alembic  │ │ (Sandbox)  │ │ (XP/Levels) │ │             │           │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘           │
└──────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                     Quantum Processing Layer                             │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐           │
│  │ QCanvas     │ │  QSim      │ │  QASM3     │ │ Optimizers  │           │
│  │ (Converters,│ │ (Execution │ │ Builder &  │ │ & Validators│           │
│  │  Parsers)   │ │  Engine)   │ │ Gate Lib   │ │             │           │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘           │
└──────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                     Infrastructure                                       │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐                           │
│  │ PostgreSQL  │ │   Redis    │ │ SonarQube  │                           │
│  │  (Data)     │ │  (Cache)   │ │  (Quality) │                           │
│  └────────────┘ └────────────┘ └────────────┘                           │
└──────────────────────────────────────────────────────────────────────────┘
```

## Frontend Architecture

The frontend is built with Next.js 14 (App Router) and TypeScript. It uses Zustand for state management, Monaco Editor for code editing, Three.js for 3D circuit visualization, and Chart.js for result histograms.

### Directory Structure

```
frontend/
├── app/                         # Next.js App Router pages
│   ├── layout.tsx               # Root layout (Inter + JetBrains Mono fonts, Toaster)
│   ├── page.tsx                 # Landing / home page
│   ├── globals.css              # Global styles (Tailwind)
│   ├── app/page.tsx             # Main IDE workspace
│   ├── login/page.tsx           # Login page
│   ├── signup/page.tsx          # Registration page
│   ├── profile/page.tsx         # User profile & gamification stats
│   ├── achievements/page.tsx    # Achievements gallery
│   ├── examples/page.tsx        # Quantum example library
│   ├── docs/page.tsx            # Documentation page
│   ├── about/page.tsx           # About / team page
│   └── api/                     # Next.js API routes
│       ├── health/route.ts      # Frontend health check
│       ├── files/route.ts       # File proxy routes
│       ├── files/[id]/route.ts  # Single file operations
│       └── share/route.ts       # Share functionality
├── components/                  # React components
│   ├── TopBar.tsx               # Navigation, auth status, settings, shortcuts
│   ├── SimpleTopBar.tsx         # Simplified nav for non-IDE pages
│   ├── Sidebar.tsx              # File explorer, project tree, templates
│   ├── EditorPane.tsx           # Monaco editor, simulation controls
│   ├── ResultsPane.tsx          # Multi-tab results (Stats, Console, Errors, Histogram, Output)
│   ├── SimulationControls.tsx   # Backend/shots/framework selection
│   ├── CircuitVisualization.tsx # 2D circuit diagram (D3)
│   ├── CircuitVisualization3D.tsx # 3D circuit visualization (Three.js / R3F)
│   ├── ShareModal.tsx           # Circuit sharing modal
│   ├── ProfileDropdown.tsx      # User profile dropdown menu
│   ├── FindReplace.tsx          # Find & replace in editor
│   ├── AddNewLanguage.tsx       # Add new language support
│   ├── ThemeWatcher.tsx         # Dark/light mode watcher
│   ├── gamification/            # Gamification UI
│   │   ├── XPToast.tsx          # XP gain notification toast
│   │   ├── StatsOverview.tsx    # XP/level/streak overview card
│   │   └── AchievementCard.tsx  # Achievement display card
│   └── profile/                 # Profile page components
│       ├── ProfileHeader.tsx    # User info & avatar
│       ├── XPHistoryChart.tsx   # XP history over time
│       ├── RecentActivityList.tsx # Recent activities feed
│       └── AchievementsPreview.tsx # Achievements summary
├── lib/                         # Utilities, stores, API client
│   ├── api.ts                   # REST API client (local/remote fallback)
│   ├── auth.ts                  # Auth utility helpers
│   ├── authStore.ts             # Zustand auth store (user, token, JWT)
│   ├── store.ts                 # Zustand editor store (files, compile, simulate)
│   ├── gamificationStore.ts     # Zustand gamification store (XP, levels, achievements)
│   ├── config.ts                # Frontend configuration
│   ├── utils.ts                 # General utilities (generateId, cn, etc.)
│   ├── circuitParser.ts         # Client-side circuit parsing for visualization
│   └── XPEventProvider.tsx      # XP event context provider
├── types/                       # TypeScript type definitions
│   └── index.ts                 # All shared types (File, Project, Run, QuantumResults, etc.)
├── shared/                      # Shared API types
│   └── api.ts                   # Shared API interfaces
├── server/                      # Express server (Vite SSR integration)
│   ├── index.ts                 # Server entry point
│   ├── node-build.ts            # Build configuration
│   └── routes/
│       ├── quantum.ts           # Quantum execution proxy
│       └── demo.ts              # Demo endpoints
├── netlify/functions/           # Netlify serverless functions
│   └── api.ts                   # API function
├── package.json                 # Dependencies
├── tailwind.config.ts           # Tailwind CSS configuration
├── vite.config.ts               # Vite configuration
└── vite.config.server.ts        # Vite server configuration
```

### Key Frontend Design Decisions

- **Zustand** for state management instead of React Context — provides simpler API with persistence middleware for auth and gamification stores
- **Three.js / React Three Fiber** for interactive 3D circuit visualization
- **D3** for 2D circuit diagrams
- **Chart.js** via react-chartjs-2 for simulation result histograms
- **Local-first API routing**: the API client probes `127.0.0.1:8000` first, with an optional remote fallback to a Railway deployment
- **Zod** for runtime input validation on the frontend

### Core Frontend Components

| Component | Responsibility |
|---|---|
| `TopBar` | Navigation, auth status, settings dropdown, keyboard shortcuts |
| `Sidebar` | File explorer, project tree, new file/template modal |
| `EditorPane` | Monaco code editor, compile/execute buttons, framework selector |
| `ResultsPane` | Multi-tab output: Stats, Console, Errors, Histogram, Output |
| `SimulationControls` | Backend selection, shots, framework, execution mode |
| `CircuitVisualization3D` | Interactive 3D circuit rendering (Three.js) |
| `ProfileDropdown` | User menu, logout, navigate to profile/achievements |
| `XPToast` | Animated XP gain notification |

### State Management Stores

| Store | File | Purpose |
|---|---|---|
| Auth Store | `lib/authStore.ts` | User session, JWT token, login/logout with `persist` middleware |
| Editor Store | `lib/store.ts` | Files, active file, compile options, simulation results, hybrid results |
| Gamification Store | `lib/gamificationStore.ts` | XP, level, streak, achievements, activity history |

## Backend Architecture

The backend is a FastAPI application with JWT authentication, PostgreSQL via SQLAlchemy + Alembic, rate limiting via SlowAPI, security headers, and audit logging middleware.

### Directory Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app, lifespan, middleware, route registration
│   ├── api/
│   │   ├── dependencies.py      # Shared dependency injection
│   │   └── routes/
│   │       ├── health.py        # /api/health — health check
│   │       ├── auth.py          # /api/auth — register, login, profile, JWT
│   │       ├── converter.py     # /api/converter — compile to OpenQASM 3.0, parse gates
│   │       ├── simulator.py     # /api/simulator — execute QASM via QSim
│   │       ├── hybrid.py        # /api/hybrid — sandboxed Python + qcanvas/qsim
│   │       ├── projects.py      # /api/projects — CRUD for projects
│   │       ├── files.py         # /api/files — CRUD for files
│   │       └── gamification.py  # /api/gamification — XP, levels, achievements, leaderboard
│   ├── config/
│   │   ├── settings.py          # Pydantic Settings (DB, Redis, CORS, secrets)
│   │   └── database.py          # SQLAlchemy engine, SessionLocal, Base, get_db
│   ├── core/
│   │   ├── middleware.py         # SlowAPI limiter, SecurityHeadersMiddleware, AuditLogMiddleware
│   │   ├── quantum_simulator.py # Legacy quantum simulator bridge
│   │   └── websocket_manager.py # WebSocket connection manager
│   ├── models/
│   │   ├── database_models.py   # SQLAlchemy ORM models (User, Project, File, Job, Conversion, Simulation, Session, ApiActivity)
│   │   ├── gamification.py      # Gamification models (UserGamification, GamificationActivity, Achievement, UserAchievement)
│   │   └── schemas.py           # Pydantic request/response schemas
│   ├── services/
│   │   ├── conversion_service.py    # Framework parsing + QASM3 compilation
│   │   ├── simulation_service.py    # QSim execution wrapper
│   │   └── gamification_service.py  # XP calculation, level progression, streaks
│   └── utils/
│       ├── jwt_auth.py          # JWT token creation & verification
│       ├── security.py          # Bcrypt hashing, AES-256 API key encryption
│       ├── logging.py           # Structured logging
│       └── exceptions.py        # Custom exception hierarchy
├── qcanvas_runtime/             # Hybrid execution runtime
│   ├── __init__.py              # Exports: compile, compile_and_execute, SimulationResult
│   ├── core.py                  # compile() and compile_and_execute() functions
│   ├── sandbox.py               # Sandboxed Python executor with security restrictions
│   ├── qsim.py                  # qsim.run() wrapper for user code
│   └── result.py                # SimulationResult & HybridExecutionResult dataclasses
├── alembic/                     # Database migrations
│   ├── env.py
│   └── versions/                # Migration scripts
│       ├── 0ee5ac065b13_create_users_table_with_encryption.py
│       ├── 2b6207bf1c6e_add_projects_files_jobs.py
│       ├── 330e27ffebcd_add_demo_role_to_enum.py
│       ├── 4a1b2c3d4e5f_add_complete_schema.py
│       ├── 6f7e8d9c0b1a_decouple_files_from_projects.py
│       ├── 83149d586e8a_update_user_roles_to_user_admin_demo.py
│       └── a1b2c3d4e5f6_add_gamification_tables.py
├── start.py                     # Uvicorn entry point
└── (utility scripts)            # create_user.py, create_demo_account.py, reset_db.py, etc.
```

### Middleware Stack

Requests flow through middleware in this order:

1. **SecurityHeadersMiddleware** — injects `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Strict-Transport-Security`, `Content-Security-Policy`
2. **AuditLogMiddleware** — logs every API call (endpoint, method, status, user, IP, response time) to the `api_activity` table
3. **CORSMiddleware** — handles cross-origin requests
4. **SlowAPI Rate Limiter** — per-endpoint rate limiting (e.g., 20/minute on converter and simulator)

### Route Registration

All routers are registered in `main.py`:

```python
app.include_router(health.router)       # /api/health
app.include_router(auth.router)         # /api/auth
app.include_router(converter.router)    # /api/converter
app.include_router(simulator.router)    # /api/simulator
app.include_router(hybrid.router)       # /api/hybrid
app.include_router(projects.router)     # /api/projects
app.include_router(files.router)        # /api/files
app.include_router(gamification.router) # /api/gamification
```

## Quantum Processing Architecture

### quantum_converters — Framework-to-QASM3 Compilation

```
quantum_converters/
├── base/
│   ├── abstract_converter.py    # ABC for all converters
│   ├── ConversionResult.py      # Structured conversion output
│   ├── circuit_ast.py           # Internal circuit AST representation
│   ├── qasm3_builder.py         # QASM3Builder — clean code generation API
│   ├── qasm3_gates.py           # QASM3GateLibrary — gate definitions & mappings
│   ├── qasm3_expression.py      # QASM3Expression — classical expression handling
│   └── openqasm_generator.py    # OpenQASM output formatter
├── parsers/
│   ├── cirq_parser.py           # CirqASTParser — Cirq code → AST
│   ├── qiskit_parser.py         # QiskitASTParser — Qiskit code → AST
│   ├── pennylane_parser.py      # PennyLaneASTParser — PennyLane code → AST
│   └── braket_parser.py         # BraketParser — Amazon Braket (experimental)
├── converters/
│   ├── cirq_to_qasm.py          # Cirq → OpenQASM 3.0
│   ├── qiskit_to_qasm.py        # Qiskit → OpenQASM 3.0
│   └── pennylane_to_qasm.py     # PennyLane → OpenQASM 3.0
├── optimizers/
│   ├── circuit_optimizer.py     # Multi-pass circuit optimization
│   └── gate_fusion.py           # Gate fusion passes
├── validators/
│   ├── syntax_validator.py      # QASM3 syntax validation
│   └── semantic_validator.py    # Semantic correctness checks
├── config/
│   ├── mappings.py              # Gate name and parameter mappings
│   └── schemas.py               # Configuration schemas
└── utils/
    ├── gate_mappings.py         # Framework-specific gate mappings
    ├── circuit_utils.py         # Circuit manipulation helpers
    └── qasm_formatter.py        # Output formatting utilities
```

### quantum_simulator (QSim) — Execution Engine

QSim is installed as an editable package (`-e ./quantum_simulator`) and provides multi-backend QASM execution:

```
quantum_simulator/
├── qsim/
│   ├── __init__.py              # Exports: run_qasm, RunArgs, SimResult
│   ├── core/
│   │   ├── api.py               # Public API: run_qasm()
│   │   ├── types.py             # RunArgs, SimResult dataclasses
│   │   └── exceptions.py        # QSim-specific exceptions
│   ├── qasm_parser/
│   │   ├── parser.py            # OpenQASM 3.0 parser (antlr4 + openqasm3)
│   │   ├── ast_utils.py         # AST traversal utilities
│   │   ├── scope.py             # Variable scoping for classical logic
│   │   └── allowed_nodes.py     # Whitelisted AST node types
│   ├── visitors/
│   │   ├── base_visitor.py      # Base AST visitor
│   │   ├── cirq_visitor.py      # QASM → Cirq circuit
│   │   ├── qiskit_visitor.py    # QASM → Qiskit circuit
│   │   ├── pennylane_visitor.py # QASM → PennyLane circuit
│   │   └── factory.py           # Visitor factory (select by backend name)
│   └── backends/
│       ├── base.py              # Backend ABC
│       ├── cirq.py              # Cirq simulation backend
│       ├── qiskit.py            # Qiskit Aer simulation backend
│       ├── pennylane.py         # PennyLane Lightning simulation backend
│       └── factory.py           # Backend factory
└── tests/
    ├── cirq_test.py
    ├── qiskit_test.py
    └── pennylane_test.py
```

### Hybrid CPU-QPU Runtime

The `qcanvas_runtime` package enables users to write Python scripts that mix classical logic with quantum compilation and simulation:

```python
import cirq
from qcanvas import compile
import qsim

circuit = cirq.Circuit(...)
qasm = compile(circuit, framework="cirq")

for i in range(3):
    result = qsim.run(qasm, shots=100, backend="cirq")
    print(f"Run {i+1}: {result.counts}")
```

The runtime executes inside a configurable sandbox (`qcanvas_runtime/sandbox.py`) with these security controls (all set in `config/config.py`):

| Setting | Default | Description |
|---|---|---|
| `HYBRID_BLOCK_DANGEROUS_IMPORTS` | `False` | Block os, subprocess, sys, etc. |
| `HYBRID_BLOCK_FILE_ACCESS` | `True` | Block open(), pathlib, io |
| `HYBRID_BLOCK_NETWORK` | `True` | Block socket, urllib, requests |
| `HYBRID_BLOCK_SHELL` | `True` | Block subprocess, os.system |
| `HYBRID_RESTRICT_BUILTINS` | `True` | Only safe builtins |
| `HYBRID_MAX_EXECUTION_TIME` | `30s` | Execution timeout |
| `HYBRID_MAX_MEMORY_MB` | `512` | Memory limit |
| `HYBRID_MAX_OUTPUT_SIZE` | `100000` | Max print output chars |

Three execution modes are supported:
1. **Compile Only** — generate QASM without execution
2. **Full Execute** — compile + run on QSim
3. **Execute Hybrid** — run user Python with `qcanvas`/`qsim` APIs in sandbox

## Data Flow Architecture

### Circuit Compilation Flow

```
1. User writes framework code (Qiskit/Cirq/PennyLane) in Monaco Editor
   ↓
2. Frontend sends POST /api/converter/convert { code, framework }
   ↓
3. ConversionService selects the appropriate AST parser
   ↓
4. Parser extracts circuit AST (gates, measurements, control flow)
   ↓
5. QASM3Builder generates OpenQASM 3.0 from the AST
   ↓
6. Response returns { qasm_code, conversion_stats }
   ↓
7. Frontend displays QASM in Results pane, updates stats
```

### Simulation Flow

```
1. User has compiled QASM code (or writes QASM directly)
   ↓
2. Frontend sends POST /api/simulator/simulate { qasm_code, backend, shots }
   ↓
3. SimulationService calls QSim: run_qasm(qasm_code, RunArgs(backend, shots))
   ↓
4. QSim parses QASM → visits AST → builds framework circuit → executes
   ↓
5. Results (counts, probabilities, metadata) returned
   ↓
6. Frontend renders histogram (Chart.js), stats cards, output
```

### Hybrid Execution Flow

```
1. User writes Python with qcanvas.compile() and qsim.run() calls
   ↓
2. Frontend sends POST /api/hybrid/execute { code, mode }
   ↓
3. Sandbox validates code, restricts imports/builtins
   ↓
4. Code executes with injected qcanvas and qsim modules
   ↓
5. Print output captured; simulation results collected
   ↓
6. Response: { stdout, simulation_results[], qasm_generated, execution_time }
   ↓
7. Frontend displays output in Console tab, results in Histogram tab
```

## API Reference

### Health

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/health/` | No | Health check with timestamp and version |

### Authentication (`/api/auth`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register` | No | Register new user |
| POST | `/api/auth/login` | No | Login, returns JWT + user |
| GET | `/api/auth/me` | JWT | Get current user profile |
| POST | `/api/auth/demo` | No | Create/login demo account |

### Converter (`/api/converter`)

| Method | Endpoint | Auth | Rate Limit | Description |
|---|---|---|---|---|
| POST | `/api/converter/convert` | Optional | 20/min | Compile framework code → OpenQASM 3.0 |
| POST | `/api/converter/parse` | Optional | — | Parse circuit into gate list for visualization |
| GET | `/api/converter/frameworks` | No | — | List supported frameworks |
| GET | `/api/converter/stats` | Optional | — | Get conversion statistics |

### Simulator (`/api/simulator`)

| Method | Endpoint | Auth | Rate Limit | Description |
|---|---|---|---|---|
| POST | `/api/simulator/execute` | Optional | 20/min | Execute QASM (legacy) |
| POST | `/api/simulator/simulate` | Optional | 20/min | Execute QASM via QSim |
| GET | `/api/simulator/backends` | No | — | List available simulation backends |

### Hybrid Execution (`/api/hybrid`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/hybrid/execute` | No | Execute Python with qcanvas/qsim in sandbox |
| POST | `/api/hybrid/validate` | No | Validate code before execution |
| GET | `/api/hybrid/status` | No | Check if hybrid execution is enabled |

### Projects (`/api/projects`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/projects/` | JWT | Create project |
| GET | `/api/projects/` | JWT | List user's and public projects |
| GET | `/api/projects/{id}` | JWT | Get project with files |
| PUT | `/api/projects/{id}` | JWT | Update project |
| DELETE | `/api/projects/{id}` | JWT | Delete project |

### Files (`/api/files`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/files/` | JWT | Create file (root or within project) |
| GET | `/api/files/` | JWT | List user's files |
| GET | `/api/files/{id}` | JWT | Get single file |
| PUT | `/api/files/{id}` | JWT | Update file content/metadata |
| DELETE | `/api/files/{id}` | JWT | Delete file |

### Gamification (`/api/gamification`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/gamification/stats` | JWT | Get user XP, level, streak, progression |
| POST | `/api/gamification/activity` | JWT | Log activity and award XP |
| GET | `/api/gamification/activities` | JWT | Get activity history (paginated) |
| GET | `/api/gamification/achievements` | JWT | Get all achievements with unlock status |
| GET | `/api/gamification/leaderboard` | JWT | Get top users by XP |
| POST | `/api/gamification/reset` | JWT | Reset gamification data (dev) |

## Database Architecture

### PostgreSQL with SQLAlchemy + Alembic

The database uses PostgreSQL 15 with SQLAlchemy 2.0 ORM and Alembic for schema migrations. UUIDs are used as primary keys for security-sensitive tables (users, conversions, simulations).

### Entity Relationship Overview

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │──┬──│ Project  │──┬──│  File    │
│ (UUID PK)│  │  │(int PK)  │  │  │(int PK)  │
└──────────┘  │  └──────────┘  │  └──────────┘
     │        │       │         │       ▲
     │        │       └─────────┘       │
     │        │                         │
     │        ├──── Job (int PK)        │
     │        ├──── Conversion (UUID) ──┤── ConversionStats (UUID)
     │        ├──── Simulation (UUID)   │
     │        ├──── Session (UUID)      │
     │        ├──── ApiActivity (UUID)  │
     │        │                         │
     │        │  Gamification Tables     │
     │        ├──── UserGamification    │
     │        ├──── GamificationActivity│
     │        └──── UserAchievement ────┤── Achievement
```

### Core Data Models

```python
# User — authentication and authorization
class User(Base):
    id          = Column(UUID, primary_key=True)
    email       = Column(String(255), unique=True, index=True)
    username    = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))  # Bcrypt
    full_name   = Column(String(255))
    role        = Column(Enum(UserRole))  # user | admin | demo
    is_active   = Column(Boolean)
    api_key_encrypted = Column(String(255))  # AES-256
    deleted_at  = Column(TIMESTAMP)  # Soft delete

# Project — file container
class Project(Base):
    id          = Column(Integer, primary_key=True)
    user_id     = Column(UUID, ForeignKey("users.id"))
    name        = Column(String(255))
    is_public   = Column(Boolean)

# File — quantum code files (can be standalone or in a project)
class File(Base):
    id          = Column(Integer, primary_key=True)
    user_id     = Column(UUID, ForeignKey("users.id"))
    project_id  = Column(Integer, ForeignKey("projects.id"), nullable=True)
    filename    = Column(String(255))
    content     = Column(Text)
    is_main     = Column(Boolean)
    is_shared   = Column(Boolean)

# Conversion — tracks each compilation
class Conversion(Base):
    id               = Column(UUID, primary_key=True)
    user_id          = Column(UUID, ForeignKey("users.id"))
    source_framework = Column(Enum(QuantumFramework))  # cirq | qiskit | pennylane
    source_code      = Column(Text)
    qasm_code        = Column(Text)
    status           = Column(Enum(ExecutionStatus))  # success | failed | pending | running
    execution_time_ms = Column(Integer)

# Simulation — tracks each simulation run
class Simulation(Base):
    id               = Column(UUID, primary_key=True)
    user_id          = Column(UUID, ForeignKey("users.id"))
    qasm_code        = Column(Text)
    backend          = Column(Enum(SimulationBackend))  # statevector | density_matrix | stabilizer
    shots            = Column(Integer)
    results_json     = Column(JSON)
    status           = Column(Enum(ExecutionStatus))

# Job — async job tracking
class Job(Base):
    id               = Column(Integer, primary_key=True)
    user_id          = Column(UUID, ForeignKey("users.id"))
    project_id       = Column(Integer, ForeignKey("projects.id"))
    status           = Column(Enum(JobStatus))  # pending | running | completed | failed
    backend          = Column(String(50))
    shots            = Column(Integer)
    result_data      = Column(JSON)

# Session — tracks user sessions
class Session(Base):
    id             = Column(UUID, primary_key=True)
    user_id        = Column(UUID, ForeignKey("users.id"))
    session_token  = Column(String(255), unique=True)
    session_type   = Column(Enum(SessionType))  # websocket | api | web
    ip_address     = Column(String(45))
    expires_at     = Column(TIMESTAMP)

# ApiActivity — audit log
class ApiActivity(Base):
    id             = Column(UUID, primary_key=True)
    user_id        = Column(UUID, ForeignKey("users.id"))
    endpoint       = Column(String(255))
    method         = Column(String(10))
    status_code    = Column(Integer)
    ip_address     = Column(String(45))
    response_time_ms = Column(Integer)
```

### Gamification Models

```python
# UserGamification — per-user XP and level tracking
class UserGamification(Base):
    user_id           = Column(UUID, ForeignKey("users.id"), primary_key=True)
    total_xp          = Column(Integer, default=0)
    level             = Column(Integer, default=1)
    current_streak    = Column(Integer, default=0)
    longest_streak    = Column(Integer, default=0)
    last_activity_date = Column(Date)

# GamificationActivity — XP-earning event log
class GamificationActivity(Base):
    id              = Column(UUID, primary_key=True)
    user_id         = Column(UUID, ForeignKey("users.id"))
    activity_type   = Column(String(50))  # simulation_run, conversion, etc.
    xp_awarded      = Column(Integer)
    activity_metadata = Column(JSON)

# Achievement — catalog of all achievements
class Achievement(Base):
    id          = Column(UUID, primary_key=True)
    name        = Column(String(100), unique=True)
    description = Column(String(255))
    category    = Column(String(50))  # getting_started, mastery, progression
    criteria    = Column(JSON)
    reward_xp   = Column(Integer)
    rarity      = Column(String(20))  # common, uncommon, rare, epic, legendary

# UserAchievement — per-user achievement progress/unlock
class UserAchievement(Base):
    id             = Column(UUID, primary_key=True)
    user_id        = Column(UUID, ForeignKey("users.id"))
    achievement_id = Column(UUID, ForeignKey("achievements.id"))
    progress       = Column(JSON)
    unlocked_at    = Column(TIMESTAMP)
```

## Security Architecture

### Authentication

- **JWT tokens** via `python-jose` with HS256 signing
- Tokens issued on login/register, verified via `HTTPBearer` dependency
- `get_current_user` dependency enforces auth on protected routes
- `get_optional_user` allows unauthenticated access with optional user context

### Password & Key Security

- **Bcrypt** for password hashing (via `passlib`)
- **AES-256** encryption for API keys (via `cryptography`)
- Soft delete support on user accounts

### Middleware Security

- **Rate Limiting**: SlowAPI with `get_remote_address` key function (e.g., 20/minute on converter/simulator)
- **Security Headers**: X-Frame-Options, X-Content-Type-Options, HSTS, CSP
- **Audit Logging**: All API calls logged to `api_activity` table with user, endpoint, response time, IP

### CORS

Configured for development with `allow_origins=["*"]`; production should restrict to the frontend domain.

### Input Validation

All API inputs validated via Pydantic models:

```python
class ConversionRequest(BaseModel):
    code: str
    framework: Literal["qiskit", "cirq", "pennylane"]
    qasm_version: str = "3.0"
    style: Literal["classic", "compact"] = "classic"
```

### Sandbox Security (Hybrid Execution)

User Python code runs in a restricted sandbox with configurable import blocking, builtin restrictions, file/network/shell access control, execution timeout, and memory limits — all managed via `config/config.py`.

## Configuration

### Global Configuration (`config/config.py`)

Centralizes runtime flags:
- `VERBOSE` — enable console logging for parsers
- `INCLUDE_VARS` / `INCLUDE_CONSTANTS` — QASM3 prelude control
- `DISABLE_REMOTE_API_FALLBACK` — force local-only backend
- `HYBRID_*` — all sandbox security settings
- Per-run log files under `logs/YYYY/Mon/`

### Backend Settings (`backend/app/config/settings.py`)

Pydantic Settings with environment variable support:

```python
class Settings(BaseSettings):
    PROJECT_NAME: str = "QCanvas"
    VERSION: str = "1.0.0"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_SERVER: str = "127.0.0.1"
    POSTGRES_PORT: str = "5433"
    POSTGRES_DB: str = "qcanvas_db"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    SECRET_KEY: str = "development_secret_key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
```

## Infrastructure & Deployment

### Docker Compose (Development)

The development stack runs PostgreSQL 15, Redis, and SonarQube:

```yaml
services:
  postgres:
    image: postgres:15-alpine
    ports: ["5433:5432"]
    environment:
      POSTGRES_DB: qcanvas_db
    volumes: [postgres_data:/var/lib/postgresql/data]
    healthcheck: pg_isready

  redis:
    image: redis:alpine
    ports: ["6379:6379"]
    volumes: [redis_data:/data]
    healthcheck: redis-cli ping

  sonarqube:
    image: sonarqube:community
    ports: ["9000:9000"]
```

### Production Docker (`config/docker/`)

Separate Dockerfiles for frontend and backend with a production Docker Compose configuration:

```
config/
├── docker/
│   ├── Dockerfile.frontend      # Next.js multi-stage build
│   ├── Dockerfile.backend       # Python multi-stage build
│   └── docker-compose.prod.yml  # Production orchestration
├── nginx.conf                   # Reverse proxy configuration
├── supervisor.conf              # Process management
└── logging.yml                  # Structured logging configuration
```

### Linux Helper Scripts

```bash
# First-time setup: system packages, Python venv, backend + frontend deps
bash setup.sh

# Start/stop services in background with log files and PID tracking
./run.sh start   # starts backend + frontend, writes logs/
./run.sh stop    # stops all processes, clears PID files
```

## Testing Architecture

### Test Structure

```
tests/
├── conftest.py                  # Shared fixtures
├── run_all_tests.py             # Test runner
├── test_security.py             # Security-specific tests
├── iteration_1/
│   ├── test_iteration_i_features.py    # 44 Iteration I feature tests
│   └── frontend_test_codes/            # Framework-specific test circuits
│       ├── cirq_iteration_i_complete.py
│       ├── qiskit_iteration_i_complete.py
│       └── pennylane_iteration_i_complete.py
├── integration/
│   ├── test_cirq_integration.py        # Cirq converter integration (7 tests)
│   ├── test_qiskit_integration.py      # Qiskit converter integration (8 tests)
│   ├── test_pennylane_integration.py   # PennyLane Iteration I (7 tests)
│   ├── test_pennylane_iteration_ii.py  # PennyLane Iteration II (8 tests)
│   ├── test_gate_modifiers.py          # Gate modifier tests (7 tests)
│   ├── test_iteration_ii_language_features.py  # Language features (15 tests)
│   ├── test_control_flow.py            # Control flow tests
│   ├── test_full_conversion.py         # End-to-end conversion tests
│   ├── test_api_integration.py         # API integration tests
│   └── demo_*_output.py               # Demo output scripts
├── unit/
│   ├── test_api/
│   │   ├── test_api_routes.py          # Route unit tests
│   │   ├── test_routes.py              # Additional route tests
│   │   └── test_services.py            # Service unit tests
│   ├── test_converters/
│   │   ├── test_framework_converters.py
│   │   ├── test_cirq_converter.py
│   │   ├── test_qiskit_converter.py
│   │   └── test_pennylane_converter.py
│   ├── test_simulator/
│   │   ├── test_quantum_simulator.py
│   │   ├── test_quantum_gates.py
│   │   └── test_backends.py
│   └── test_config_registries.py
├── e2e/
│   ├── test_complete_workflow.py
│   ├── test_user_workflows.py
│   └── test_frontend_integration.py
└── fixtures/
    └── sample_circuits/
        ├── cirq_examples/
        ├── qiskit_examples/
        └── pennylane_examples/
```

### Test Results Summary

- **Iteration I**: 44 passed, 4 xfailed (100% success)
- **Integration**: 54 passed (Cirq 7/7, Qiskit 8/8, PennyLane 15/15, Gate Modifiers 7/7, Language Features 15/15)
- **Total**: 105+ passed, 29 skipped, 4 xfailed (100% pass rate)

## Technology Stack Summary

### Backend

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.8+ | Core language |
| FastAPI | ≥0.104.0 | Web framework |
| Uvicorn | ≥0.24.0 | ASGI server |
| SQLAlchemy | ≥2.0.0 | ORM |
| Alembic | ≥1.13.0 | Database migrations |
| PostgreSQL | 15 | Primary database |
| Redis | ≥5.0.0 | Caching |
| Pydantic | ≥2.5.0 | Data validation |
| SlowAPI | ≥0.1.9 | Rate limiting |
| python-jose | ≥3.3.0 | JWT tokens |
| bcrypt | ≥4.0.0 | Password hashing |
| cryptography | ≥42.0.0 | AES-256 encryption |
| psutil | ≥5.9.0 | System metrics |

### Quantum

| Technology | Version | Purpose |
|---|---|---|
| Cirq | ≥1.5.0 | Google quantum framework |
| Qiskit | ≥2.1.2 | IBM quantum framework |
| Qiskit Aer | ≥0.17.2 | Qiskit simulation backend |
| PennyLane | ≥0.42.3 | Xanadu quantum ML framework |
| PennyLane Lightning | ≥0.42.0 | Fast PennyLane simulator |
| OpenQASM 3 | ≥1.0.1 | QASM parser library |
| pyqasm | ≥0.5.0 | QASM utilities |
| antlr4 | ≥4.13.2 | Parser generator runtime |
| NumPy | ≥1.24.0 | Numerical computing |
| SciPy | ≥1.11.0 | Scientific computing |

### Frontend

| Technology | Version | Purpose |
|---|---|---|
| Next.js | ≥14.2 | React framework (App Router) |
| React | ≥18.3 | UI library |
| TypeScript | ≥5.5 | Type-safe JavaScript |
| Zustand | ≥4.5 | State management |
| Tailwind CSS | ≥3.4 | Utility-first styling |
| Monaco Editor | ≥4.6 | Code editor |
| Chart.js | ≥4.5 | Histogram visualization |
| Three.js | ≥0.160 | 3D rendering |
| React Three Fiber | ≥8.18 | React Three.js bindings |
| D3 | ≥7.9 | 2D circuit visualization |
| Lucide React | ≥0.400 | Icon library |
| React Hot Toast | ≥2.4 | Toast notifications |
| Zod | ≥3.22 | Runtime validation |

### DevOps

| Technology | Purpose |
|---|---|
| Docker / Docker Compose | Container orchestration |
| Nginx | Reverse proxy (production) |
| SonarQube | Code quality analysis |
| Alembic | Database migration management |
| GitHub Actions | CI/CD pipelines |
| pytest | Python test framework |

## Extensibility

### Adding a New Quantum Framework

1. Create a parser in `quantum_converters/parsers/` (extend the AST extraction pattern)
2. Create a converter in `quantum_converters/converters/` (use `QASM3Builder`)
3. Add gate mappings in `quantum_converters/config/mappings.py`
4. Register in `ConversionService` (`backend/app/services/conversion_service.py`)
5. Add a QSim visitor in `quantum_simulator/qsim/visitors/`
6. Add a QSim backend in `quantum_simulator/qsim/backends/`

### Adding a New API Feature

1. Create route file in `backend/app/api/routes/`
2. Add Pydantic schemas in `backend/app/models/schemas.py`
3. Add service logic in `backend/app/services/`
4. Register router in `backend/app/main.py`
5. Add migration if new database tables needed (`alembic revision --autogenerate`)

## Conclusion

QCanvas is built with a modular architecture that supports:

- **Full-stack IDE**: Monaco editor + 3D visualization + multi-tab results
- **Multi-framework**: Cirq, Qiskit, PennyLane compilation to OpenQASM 3.0
- **Hybrid execution**: Sandboxed Python with quantum compilation and simulation
- **Authentication**: JWT-based auth with bcrypt passwords and demo accounts
- **Gamification**: XP, levels, streaks, achievements, leaderboards
- **Project management**: User projects and files with sharing
- **Security**: Rate limiting, audit logging, security headers, sandbox restrictions
- **Extensibility**: Plugin-like patterns for frameworks, backends, and features
- **Infrastructure**: Docker Compose dev stack, Alembic migrations, SonarQube quality gates
