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
├── frontend/           # Next.js-based web interface (UI, routing, simple operations)
├── backend/           # FastAPI REST API and WebSocket server (complex simulations)
├── quantum_converters/ # Framework conversion modules
├── quantum_simulator/  # Quantum simulation engine
└── examples/          # Sample circuits and tutorials
```

### Core Components

1. **QCanvas (Compilation/Orchestration)**: AST parsing, QASM generation, validation, hybrid scheduling
2. **QSim (Execution)**: High-performance simulation backends and result aggregation
3. **Next.js Frontend**: UI components, routing, and simple operations
4. **FastAPI Backend**: API, WebSockets, and heavy computations
5. **Shared TypeScript Types**: Type safety across frontend and backend

### Hybrid Approach Benefits

- **Two Pillars**:
  - QCanvas orchestrates compilation, optimization, validation, and hybrid scheduling
  - QSim executes OpenQASM 3.0 circuits and aggregates results

- **Next.js Advantages**:
  - Server-side rendering (SSR) and static site generation (SSG)
  - Built-in routing and API routes
  - Excellent developer experience with hot reloading
  - Optimized performance with automatic code splitting
  - TypeScript support for type safety

- **FastAPI Advantages**:
  - High-performance async Python framework
  - Automatic API documentation
  - Built-in data validation with Pydantic
  - WebSocket support for real-time communication
  - Ideal for complex quantum computations

- **Shared TypeScript Types**:
  - Consistent data structures across services
  - Type safety between frontend and backend
  - Reduced development time and errors
  - Better developer experience

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Node.js 18+ (for Next.js)
- Docker (optional, for containerized deployment)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/qcanvas.git
   cd qcanvas
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

4. **Set up environment variables**
   ```bash
   cp environment.env.example environment.env
   # Edit environment.env with your configuration
   ```

5. **Start the development servers**
   ```bash
   # Terminal 1: Start FastAPI backend
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Terminal 2: Start Next.js frontend
   cd frontend
   npm run dev
   ```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 📖 Usage

### Web Interface

1. Open your browser to `http://localhost:3000`
2. Use the Circuit Converter to convert between frameworks
3. Use the Quantum Simulator to run and visualize circuits
4. Explore examples in the Documentation section

### API Usage

```python
import requests

# Convert a Cirq circuit to Qiskit
response = requests.post('http://localhost:8000/api/convert', json={
    'source_framework': 'cirq',
    'target_framework': 'qiskit',
    'source_code': 'your_cirq_code_here'
})

# Execute via QSim (simulation-first)
response = requests.post('http://localhost:8000/api/simulator/execute', json={
    'qasm_code': 'your_qasm_code_here',
    'backend': 'statevector',
    'shots': 1000
})
```

## 🔧 Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string for caching
- `SECRET_KEY`: Application secret key
- `DEBUG`: Enable debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `NEXT_PUBLIC_API_URL`: Frontend API endpoint for Next.js

### Backend Configuration (FastAPI)

The backend uses FastAPI with the following features:
- Automatic API documentation at `/docs`
- WebSocket support for real-time updates
- Database integration with SQLAlchemy
- Caching with Redis
- Shared TypeScript types with frontend

### Frontend Configuration (Next.js)

The frontend uses Next.js with the following features:
- App Router for modern routing
- Server-side rendering and static generation
- TypeScript for type safety
- API routes for simple operations
- WebSocket integration for real-time updates

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

### Test Structure

- `tests/unit/`: Unit tests for individual components
- `tests/integration/`: Integration tests for API endpoints
- `tests/e2e/`: End-to-end tests for user workflows
- `tests/fixtures/`: Test data and sample circuits

## 📚 Documentation

- [API Documentation](docs/api/)
- [User Guide](docs/user-guide/)
- [Developer Guide](docs/developer/)
- [Deployment Guide](docs/deployment/)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/developer/contributing.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Style

- Python: Black, Flake8, MyPy
- TypeScript/JavaScript: ESLint, Prettier
- Commit messages: Conventional Commits

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Cirq](https://github.com/quantumlib/Cirq) - Google's quantum computing framework
- [Qiskit](https://github.com/Qiskit/qiskit) - IBM's quantum computing framework
- [PennyLane](https://github.com/PennyLaneAI/pennylane) - Xanadu's quantum machine learning framework
- [OpenQASM](https://github.com/openqasm/openqasm) - Open quantum assembly language
- [Next.js](https://nextjs.org/) - React framework for production
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/qcanvas/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/qcanvas/discussions)
- **Email**: support@qcanvas.dev

## 🔮 Roadmap

- [ ] Support for additional quantum frameworks (Braket, Forest)
- [ ] Advanced noise models and error correction
- [ ] Quantum machine learning workflows
- [ ] Cloud deployment options
- [ ] Mobile application
- [ ] Collaborative circuit editing
- [ ] Quantum algorithm library
- [ ] Performance optimization and GPU acceleration
- [ ] Enhanced TypeScript type sharing
- [ ] Next.js App Router optimizations

---

**QCanvas** - Unifying Quantum Computing Frameworks with Next.js and FastAPI
