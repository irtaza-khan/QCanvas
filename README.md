# Quantum Unified Simulator (QCanvas)

A comprehensive quantum computing platform that provides unified simulation, circuit conversion, and visualization capabilities across multiple quantum frameworks.

## 🚀 Overview

QCanvas is a modern, web-based quantum computing platform that bridges the gap between different quantum computing frameworks. It provides a unified interface for simulating quantum circuits, converting between different quantum programming languages, and visualizing quantum states and operations.

### Key Features

- **Multi-Framework Support**: Convert circuits between Cirq, Qiskit, and PennyLane
- **Real-Time Simulation**: Execute quantum circuits with multiple backend options
- **Interactive Visualization**: Visualize quantum states, circuits, and measurement results
- **Web-Based Interface**: Modern, responsive web application with real-time updates
- **OpenQASM 3.0 Integration**: Standardized intermediate representation
- **Extensible Architecture**: Plugin-based system for adding new frameworks

> **Note**: The frontend React application is currently marked as TODO and needs to be implemented. The backend API and quantum processing components are fully functional and documented.

## 🏗️ Architecture

```
QCanvas/
├── frontend/          # React-based web interface
├── backend/           # FastAPI REST API and WebSocket server
├── quantum_converters/ # Framework conversion modules
├── quantum_simulator/  # Quantum simulation engine
└── examples/          # Sample circuits and tutorials
```

### Core Components

1. **Quantum Converters**: Convert between Cirq, Qiskit, and PennyLane
2. **Quantum Simulator**: Multi-backend simulation engine
3. **Web Interface**: Real-time circuit editing and visualization
4. **API Layer**: RESTful API for programmatic access

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Node.js 16+
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
   # Terminal 1: Start backend
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Terminal 2: Start frontend
   cd frontend
   npm start
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

# Simulate a quantum circuit
response = requests.post('http://localhost:8000/api/simulate', json={
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

### Backend Configuration

The backend uses FastAPI with the following features:
- Automatic API documentation at `/docs`
- WebSocket support for real-time updates
- Database integration with SQLAlchemy
- Caching with Redis

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

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
- JavaScript: ESLint, Prettier
- Commit messages: Conventional Commits

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Cirq](https://github.com/quantumlib/Cirq) - Google's quantum computing framework
- [Qiskit](https://github.com/Qiskit/qiskit) - IBM's quantum computing framework
- [PennyLane](https://github.com/PennyLaneAI/pennylane) - Xanadu's quantum machine learning framework
- [OpenQASM](https://github.com/openqasm/openqasm) - Open quantum assembly language

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

---

**QCanvas** - Unifying Quantum Computing Frameworks
