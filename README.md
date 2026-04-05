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
- Docker Engine with **Compose V2** (`docker compose` CLI)
- Git

## Docker and Docker Compose

The repo includes [`docker-compose.yml`](docker-compose.yml) for **PostgreSQL**, **Redis**, **QCanvas FastAPI backend**, **Cirq-RAG-Code-Assistant** (Cirq AI / Bedrock), and optionally **SonarQube** (metrics profile).

The **Next.js frontend is not in Compose**; run it locally with `npm run dev` in `frontend/` (see below).

### Service overview

| Service | Container name | Host port | Notes |
|--------|----------------|-----------|--------|
| PostgreSQL | `qcanvas_postgres` | **5433** → 5432 | Database for QCanvas |
| Redis | `qcanvas_redis` | **6379** | Caching |
| Cirq AI | `qcanvas_cirq_agent` | **8001** → 8000 | Bedrock/RAG; internal URL `http://cirq_agent:8000` |
| QCanvas API | `qcanvas_backend` | **8000** | Sets `CIRQ_AGENT_URL=http://cirq_agent:8000` |
| SonarQube | `qcanvas_sonarqube` | **9000** | Only with `--profile metrics` |

Each container can use port **8000 internally** without conflict; they are isolated. Only **host** ports must be unique (**8000** vs **8001**).

### Environment file (project root)

Create a **`.env`** in the repository root (Compose loads it automatically). Minimum for the database:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=qcanvas_db
```

For **Cirq AI** inside Docker, add the same variables you use for Bedrock (see [`Cirq-RAG-Code-Assistant/.env.example`](Cirq-RAG-Code-Assistant/.env.example)):

```env
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
BEDROCK_INFERENCE_PROFILE_ARN_DESIGNER=...
BEDROCK_INFERENCE_PROFILE_ARN_OPTIMIZER=...
BEDROCK_INFERENCE_PROFILE_ARN_VALIDATOR=...
BEDROCK_INFERENCE_PROFILE_ARN_EDUCATIONAL=...
```

Put AWS keys in **`Cirq-RAG-Code-Assistant/.env`** when using Docker: that file is bind-mounted into the `cirq_agent` container as `/app/.env`. The Compose file does **not** set `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` to empty defaults anymore—empty values used to block `python-dotenv` from applying the mounted file.

### Commands (run from the repo root)

**Build images and start the default stack** (postgres, redis, cirq_agent, backend):

```bash
docker compose up -d --build
```

**Start or restart without rebuilding images:**

```bash
docker compose up -d
```

**Include SonarQube** (metrics profile):

```bash
docker compose --profile metrics up -d --build
```

**Rebuild only specific services** (e.g. after changing a `Dockerfile`):

```bash
docker compose build cirq_agent backend
docker compose up -d
```

**Force a clean rebuild** (slower; use when dependencies change):

```bash
docker compose build --no-cache cirq_agent backend
docker compose up -d
```

**View running services:**

```bash
docker compose ps
```

**Follow logs** (all services or one):

```bash
docker compose logs -f
docker compose logs -f backend
docker compose logs -f cirq_agent
```

**Stop containers** (keeps named volumes such as database data):

```bash
docker compose stop
```

**Stop and remove containers** (keeps volumes unless you add `-v`):

```bash
docker compose down
```

**Stop and remove containers and volumes** (⚠️ deletes Postgres/Redis/SonarQube data):

```bash
docker compose down -v
```

**Run a one-off command in the backend container** (example: open a shell):

```bash
docker compose exec backend bash
```

### After Docker is up

- **API:** http://localhost:8000 — docs: http://localhost:8000/docs  
- **Health:** http://localhost:8000/api/health  
- **Cirq AI (direct):** http://localhost:8001/docs  

Run **database migrations** against the Dockerized Postgres (from host, with venv and `PYTHONPATH` set, or `exec` into `backend`):

```bash
# Example from host (Windows PowerShell); adjust path and venv
$env:PYTHONPATH = "D:\path\to\QCanvas\backend"
$env:DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5433/qcanvas_db"
python -m alembic -c backend/alembic.ini upgrade head
```

Then start the **frontend**:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

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

#### 4. Start Docker Services

Use **Docker Compose** as described in [Docker and Docker Compose](#docker-and-docker-compose) (e.g. `docker compose up -d --build`). For SonarQube, add `--profile metrics`.

#### 5. Set Up Database Schema
```powershell
# From repo root; set path to your clone
$env:PYTHONPATH = "D:\path\to\QCanvas\backend"
# If Postgres is the Docker Compose service (mapped to host 5433):
$env:DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5433/qcanvas_db"

python -m alembic -c backend/alembic.ini upgrade head
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

If you already use **Docker Compose** for the API, **skip this step** (backend is on http://localhost:8000).

```powershell
$env:PYTHONPATH="d:\path\to\QCanvas\backend"
python backend/start.py
```

Backend will run on `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

**Cirq AI assistant (optional):** The IDE can proxy to [Cirq-RAG-Code-Assistant](Cirq-RAG-Code-Assistant/QCANVAS_INTEGRATION_GUIDE.md). Run the Cirq service on **port 8001** (QCanvas already uses **8000**). Set `CIRQ_AGENT_URL` in the QCanvas backend environment (defaults to `http://127.0.0.1:8001`). The frontend calls `{QCanvas API}/api/cirq-agent/api/v1/...`. For local UI-only testing without the QCanvas API proxy, set `NEXT_PUBLIC_CIRQ_USE_NEXT_REWRITE=true` and optionally `CIRQ_REWRITE_TARGET` (Next.js rewrites `/cirq-api/*` to the Cirq server).

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
- `NEXT_PUBLIC_API_URL` / `NEXT_PUBLIC_API_BASE`: Frontend API endpoint for Next.js
- `CIRQ_AGENT_URL`: QCanvas backend proxy target for Cirq AI (Compose sets `http://cirq_agent:8000` inside Docker; locally often `http://127.0.0.1:8001`)

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
