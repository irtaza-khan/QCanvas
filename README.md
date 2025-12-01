# Quantum Unified Simulator (QCanvas)

A comprehensive quantum computing platform that provides unified simulation, circuit conversion, and visualization capabilities across multiple quantum frameworks using a hybrid Next.js and FastAPI architecture.

## 🚀 Overview

QCanvas is a modern, web-based quantum computing platform that bridges the gap between different quantum computing frameworks. It provides a unified interface for simulating quantum circuits, converting between different quantum programming languages, and visualizing quantum states and operations.

### Key Features

- **Multi-Framework Support**: Convert circuits between Cirq, Qiskit, and PennyLane
- **Hybrid CPU–QPU Model**: QCanvas orchestrates; QSim executes (simulator-first, pluggable QPU later)
- **Real-Time Simulation**: Execute quantum circuits with statevector, density matrix, or stabilizer backends
- **OpenQASM 3.0 (Rosetta Stone)**: Universal intermediate representation across frameworks
- **Smart Conversion Engine**: AST-based parsing, intelligent gate mapping, built-in validation, instant analytics
- **Interactive Visualization**: Circuit rendering, histograms, and results analysis
- **Shared TypeScript Types**: Type safety across frontend and backend services
- **Extensible Architecture**: Plugin-based system for adding new frameworks

## 🏗️ Architecture

```
QCanvas/
├── frontend/             # Next.js-based web interface
│   ├── app/              # App Router pages and layouts
│   ├── components/       # Reusable UI components
│   ├── lib/              # Utility functions and state management
│   └── public/           # Static assets (images, icons)
│
├── backend/              # FastAPI REST API and WebSocket server
│   ├── app/              # Main application logic
│   │   ├── api/          # API routes and endpoints
│   │   ├── models/       # Database models and Pydantic schemas
│   │   └── services/     # Business logic services
│   └── alembic/          # Database migration scripts
│
├── quantum_converters/   # Framework conversion modules
│   ├── qiskit/           # Qiskit to OpenQASM converters
│   ├── cirq/             # Cirq to OpenQASM converters
│   └── pennylane/        # PennyLane to OpenQASM converters
│
├── quantum_simulator/    # Quantum simulation engine
│   ├── backends/         # Simulation backends (statevector, density matrix)
│   └── core/             # Core simulation logic
│
├── examples/             # Sample circuits and tutorials
│
├── docs/                 # Project documentation
│
├── tests/                # Comprehensive test suite
│
└── scripts/              # Helper scripts for setup and maintenance
```

### Core Components

1. **QCanvas (Compilation/Orchestration)**: AST parsing, QASM generation, validation, hybrid scheduling
2. **QSim (Execution)**: High-performance simulation backends and result aggregation
3. **Next.js Frontend**: UI components, routing, and simple operations
4. **FastAPI Backend**: API, WebSockets, and heavy computations
5. **Shared TypeScript Types**: Type safety across frontend and backend

## 🛠️ Installation

### Prerequisites

- Python 3.9+
- Node.js 18+ (for Next.js)
- Docker & Docker Compose (for PostgreSQL, Redis, SonarQube)
- Git

### Windows Setup (Recommended for Development)

#### 1. Clone Repository
```bash
git clone https://github.com/Umer-Farooq-CS/QCanvas.git
cd QCanvas
```

#### 2. Create Virtual Environment
```bash
python -m venv qcanvas_env
.\qcanvas_env\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Start Docker Services (PostgreSQL, Redis, SonarQube)
```bash
docker-compose up -d
```

Verify services are running:
```bash
docker-compose ps
```

You should see:
- **qcanvas_postgres** (port 5433)
- **qcanvas_redis** (port 6379)
- **qcanvas_sonarqube** (port 9000)

#### 5. Set Up Database Schema
```bash
# Set Python path
$env:PYTHONPATH="d:\path\to\QCanvas\backend"

# Run database migrations
python -m alembic upgrade head
```

#### 6. Create Admin User (Optional)
```bash
python backend/create_user.py
```

Follow prompts to create an admin account.

#### 7. Create Demo Account (Optional)
```bash
python backend/create_demo_account.py
```

This creates a demo account (`demo@qcanvas.dev` / `demo123`) for testing. Demo data is cleared on logout.

#### 8. Verify Database
```bash
python backend/verify_database.py
```

📚 **For detailed information about database architecture, security (CIA principles), and troubleshooting, see [docs/db_setup.md](docs/db_setup.md)**

#### 9. Start Backend Server
```bash
$env:PYTHONPATH="d:\path\to\QCanvas\backend"
python backend/start.py
```

Backend will run on `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

#### 10. Start Frontend (New Terminal)
```bash
cd frontend
npm install
npm run dev
```

Frontend will run on `http://localhost:3000`

### Linux Quick Setup (Recommended)

For a fresh Linux machine, you can install all requirements and start QCanvas using the provided scripts:

1. **Clone the repository**
   ```bash
   git clone https://github.com/Umer-Farooq-CS/QCanvas.git
   cd QCanvas
   ```

2. **Run first‑time setup**
   ```bash
   # Installs system packages, creates venv, installs backend + frontend deps
   bash setup.sh
   ```

3. **Configure environment**
   ```bash
   cp environment.env.example environment.env
   # Edit environment.env with your configuration
   ```

4. **Start/stop QCanvas in the background**
   ```bash
   # Start Next.js frontend and FastAPI backend in background
   ./run.sh start

   # Stop all QCanvas services (kills node/next/uvicorn and clears PID files)
   ./run.sh stop
   ```

   - Background logs are written to `logs/frontend.log` and `logs/backend.log`.
   - PID files `frontend.pid` and `backend.pid` are used to avoid double‑starting services.

## 📡 API Usage

### Conversion API

**Endpoint:** `POST /api/converter/convert`

Convert quantum circuit code from a specific framework to OpenQASM 3.0.

```json
{
  "source_code": "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)",
  "source_framework": "qiskit",
  "conversion_type": "classic"
}
```

**Response:**
```json
{
    "success": true,
    "qasm_code": "OPENQASM 3.0;...",
    "framework": "qiskit",
    "conversion_stats": { ... }
}
```

### Simulation API (QSim)

**Endpoint:** `POST /api/simulator/execute`

Execute OpenQASM 3.0 code using the QSim engine with various backends.

```json
{
  "qasm_code": "OPENQASM 3.0; include \"stdgates.inc\"; qubit[2] q; bit[2] c; h q[0]; cx q[0], q[1]; c = measure q;",
  "backend": "cirq",  // Options: "cirq", "qiskit", "pennylane"
  "shots": 1024
}
```

**Response:**
```json
{
    "success": true,
    "counts": { "00": 512, "11": 512 },
    "metadata": { ... }
}
```

## 🔧 Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string for caching
- `SECRET_KEY`: Application secret key
- `DEBUG`: Enable debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `NEXT_PUBLIC_API_URL`: Frontend API endpoint for Next.js

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run frontend tests
cd frontend
npm test

# Run with coverage
pytest --cov=quantum_converters --cov=quantum_simulator --cov=backend
```

## 📚 Documentation

- [API Documentation](docs/api/)
- [User Guide](docs/user-guide/)
- [Developer Guide](docs/developer/)
- [Deployment Guide](docs/deployment/)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/developer/contributing.md) for details.

## 📄 License

This project is licensed under the **Open Quantum Workbench Proprietary License**. See the [LICENSE](LICENSE) file for details.

## 👥 Teams

### QCanvas Team
- Umer Farooq
- Hussan Waseem Syed
- Muhammad Irtaza Khan

### QSim Team
- Aneeq Ahmed Malik
- Abeer Noor
- Abdullah Mehmood

### Supervisors
- Dr. Imran Ashraf (Project Supervisor)
- Dr. Muhammad Nouman Noor (Co-Supervisor)

**Built under Open Quantum Workbench: A FAST University Initiative**
