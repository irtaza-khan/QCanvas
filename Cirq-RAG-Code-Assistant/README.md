# Cirq-RAG-Code-Assistant

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1+-orange.svg)](https://pytorch.org)
[![Cirq](https://img.shields.io/badge/Cirq_SDK-1.3+-green.svg)](https://quantumai.google/cirq)
[![License](https://img.shields.io/badge/License-Academic%20Use-red.svg)](LICENSE)

**A research-grade system for generating, optimizing, explaining, and validating Cirq quantum computing code using hybrid RAG + Multi-Agent architecture with PyTorch CUDA GPU optimization.**

</div>

## 🎯 Overview

The Cirq-RAG-Code-Assistant is a cutting-edge research project that combines **Retrieval-Augmented Generation (RAG)** with **Multi-Agent Systems** to provide intelligent assistance for Google's Cirq quantum computing framework. Our system generates syntactically correct, executable Cirq code from natural language descriptions while providing comprehensive educational explanations.

### 🚀 Key Features

- **🧠 Hybrid RAG + Multi-Agent Architecture** - Combines knowledge retrieval with specialized agents
- **⚡ PyTorch CUDA GPU Optimization** - Leverages GPU acceleration for performance
- **🎓 Educational Focus** - Provides step-by-step explanations alongside generated code
- **🔧 Tool-Augmented Reasoning** - Uses compile/simulate loops for code validation
- **🤖 Agentic Reinforcement Learning** - Iterative refinement using RL techniques
- **📊 Comprehensive Evaluation** - Rigorous testing and benchmarking framework

### 🏗️ System Architecture

Our system employs four specialized agents working in coordination:

- **🎨 Designer Agent** - Creates quantum circuits from natural language descriptions
- **⚡ Optimizer Agent** - Optimizes circuits for depth, gate count, and performance
- **✅ Validator Agent** - Validates code syntax, logic, and quantum principles
- **📚 Educational Agent** - Provides explanations and learning content

## 🛠️ Technology Stack

### Core Technologies
- **Python 3.11+** - Primary development language
- **PyTorch 2.1+** - Deep learning and GPU optimization with CUDA
- **Google Cirq SDK 1.3+** - Quantum computing framework
- **Sentence Transformers** - Text embeddings and similarity search
- **FAISS/ChromaDB** - Vector database for knowledge retrieval

### Development Tools
- **pytest** - Testing framework
- **Black + isort** - Code formatting
- **mypy** - Type checking
- **pre-commit** - Code quality hooks
- **Make** - Development automation

## 📁 Repository Structure

```
.
├─ config/                                  # Configuration files
│  ├─ config.json                          # Main configuration
│  └─ ollama/                              # Ollama Modelfiles
│     ├─ designer_agent.Modelfile          # Designer agent model
│     └─ educational_agent.Modelfile       # Educational agent model
│
├─ data/                                    # Data storage (git-ignored)
│  ├─ datasets/                            # Training and evaluation datasets
│  ├─ knowledge_base/                      # Curated Cirq code snippets
│  └─ models/                              # Pre-trained models and embeddings
│
├─ docs/                                   # Project documentation
│  ├─ agents/                              # Agent documentation
│  │  ├─ designer.md                       # Designer agent details
│  │  └─ README.md                         # Agent system overview
│  ├─ api/                                 # API documentation
│  │  └─ README.md                         # REST API reference
│  ├─ Proposal/                            # Research proposal
│  │  └─ LaTeX Files/                      # LaTeX source files
│  ├─ Research Paper/                      # Final research paper
│  │  └─ LaTeX Files/                      # LaTeX source and figures
│  │     ├─ main.tex                       # Main paper (Springer LNCS format)
│  │     ├─ references.bib                 # Bibliography
│  │     └─ figs/                          # Figures and visualizations
│  ├─ architecture.md                      # System architecture
│  ├─ installation.md                      # Setup instructions
│  ├─ integration.md                       # QCanvas integration guide
│  ├─ overview.md                          # Project overview
│  ├─ quickstart.md                        # Quick start guide
│  ├─ README.md                            # Documentation index
│  ├─ rubric.md                            # Project evaluation rubric
│  └─ tech-stack.md                        # Technology details
│
├─ memory-bank/                            # Project memory system
│  ├─ activeContext.md                     # Current focus and next steps
│  ├─ productContext.md                    # Product vision and UX goals
│  ├─ progress.md                          # Status and known issues
│  ├─ projectbrief.md                      # Scope and objectives
│  ├─ systemPatterns.md                    # Architecture patterns
│  └─ techContext.md                       # Technical context
│
├─ outputs/                                # Generated outputs (git-ignored)
│  ├─ artifacts/                           # Generated code and visualizations
│  ├─ logs/                                # System and application logs
│  └─ reports/                             # Evaluation reports and metrics
│
├─ src/                                    # Python source code
│  ├─ agents/                              # Multi-agent system
│  ├─ cirq_rag_code_assistant/               # Main package
│  │  └─ config/                           # Configuration modules
│  ├─ cli/                                 # Command-line interface
│  ├─ evaluation/                          # Evaluation framework
│  ├─ orchestration/                       # Agent coordination
│  └─ rag/                                 # RAG system implementation
│
├─ tests/                                  # Test suite
│  ├─ e2e/                                 # End-to-end tests
│  ├─ integration/                         # Integration tests
│  └─ unit/                                # Unit tests
│
├─ .cursorrules                            # Project intelligence
├─ .dockerignore                           # Docker ignore patterns
├─ .gitignore                              # Git ignore patterns
├─ .pre-commit-config.yaml                 # Pre-commit hooks
├─ CHANGELOG.md                            # Project changelog
├─ Dockerfile                              # Docker containerization
├─ LICENSE                                 # Academic Use License
├─ Makefile                                # Development automation
├─ README.md                               # This file
├─ env.template                            # Environment variables template
├─ pyproject.toml                          # Modern Python packaging
├─ requirements.txt                        # Python dependencies
├─ setup-dev.bat                           # Windows batch setup script
├─ setup-dev.ps1                           # Windows PowerShell setup script
├─ setup-dev.sh                            # Linux setup script
└─ setup.py                                # Python package setup
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (Linux Ubuntu recommended for PyTorch CUDA GPU)
- **NVIDIA GPU** (optional, for PyTorch CUDA acceleration)
- **CUDA 12.0+** (if using GPU)

### Installation

#### Option 1: Automated Setup (Recommended)

**Windows PowerShell:**
```powershell
.\setup-dev.ps1
```

**Windows Command Prompt:**
```cmd
setup-dev.bat
```

**Linux/Unix:**
```bash
chmod +x setup-dev.sh
./setup-dev.sh
```

#### Option 2: Manual Setup

1. **Create virtual environment:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies:**
   ```bash
   # Basic installation
   pip install -e .
   
   # Development installation with PyTorch CUDA GPU
   pip install -e ".[dev,gpu,quantum]"
   ```

3. **Setup pre-commit hooks:**
   ```bash
   pre-commit install
   pre-commit install --hook-type pre-push
   ```

4. **Run tests:**
   ```bash
   pytest -q
   ```

### Environment Configuration

1. **Copy environment template:**
   ```bash
   cp env.template .env
   ```

2. **Edit `.env` file** with your configuration:
   ```env
   DEBUG=true
   ENVIRONMENT=development
   LOG_LEVEL=INFO
   DATABASE_URL=sqlite:///data/cirq_rag.db
   ```

### 🤖 Ollama Custom Models

This project uses custom Ollama Modelfiles with optimized parameters for each agent. You must create these models before running the notebooks.

#### Create Agent Models

From the project root directory:

```bash
# Create Designer Agent (for code generation)
cd config/ollama
ollama create cirq-designer-agent -f designer_agent.Modelfile

# Create Educational Agent (for explanations)
ollama create cirq-edu-agent -f educational_agent.Modelfile

# Return to project root
cd ../..
```

#### Remove Agent Models

```bash
# Remove a specific agent model
ollama rm cirq-designer-agent
ollama rm cirq-edu-agent
```

#### List Available Models

```bash
# See all installed models
ollama list
```

#### Test Agent Models

```bash
# Test Designer Agent (expects JSON output)
ollama run cirq-designer-agent "Create a simple Bell state circuit"

# Test Educational Agent (expects markdown output)
ollama run cirq-edu-agent "Explain what a Hadamard gate does"
```

#### Modelfile Configuration

The Modelfiles in `config/ollama/` contain:
- **Base model** - The underlying LLM (e.g., `qwen2.5-coder:14b`)
- **System prompt** - Agent-specific instructions and output format
- **Parameters** - Temperature, context size, GPU layers, etc.

See [config/README.md](config/README.md) for detailed Modelfile documentation.

## 🧪 Development

### Available Commands

```bash
# Development automation
make help              # Show all available commands
make test              # Run all tests
make lint              # Run linting and formatting
make format            # Format code with Black and isort
make clean             # Clean build artifacts

# Installation options
make install           # Basic installation
make install-dev       # Development installation
make install-gpu       # With PyTorch CUDA support
make install-quantum   # With quantum computing extensions
```

### Testing

```bash
# Run all tests
pytest

# Run specific test types
pytest tests/unit/                    # Unit tests only
pytest tests/integration/             # Integration tests only
pytest tests/e2e/                     # End-to-end tests only

# Run with coverage
pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/

# Security checks
bandit -r src/
safety check
```

## 📊 Research Results

### Achieved Objectives

1. **Code Generation Accuracy** - ✅ Achieved 92% success rate on standard benchmarks
2. **Educational Value** - ✅ Multi-level explanations with 4 depth levels (low to very_high)
3. **Performance Optimization** - ✅ 33% reduction in gate count, 38% reduction in two-qubit gates
4. **Validation & Testing** - ✅ 90% validation rate with self-correction loops
5. **Reproducible Evaluation** - ✅ Complete benchmark suite with ablation studies

### Research Paper

The complete research paper is available in `docs/Research Paper/LaTeX Files/main.tex` (Springer LNCS format). The paper includes:
- Comprehensive methodology and system architecture
- Experimental setup with ablation studies
- Detailed results and analysis (92% success rate, optimization metrics)
- Limitations and future work discussion

### Target Algorithms

- **VQE (Variational Quantum Eigensolver)** - Quantum chemistry applications
- **QAOA (Quantum Approximate Optimization Algorithm)** - Combinatorial optimization
- **Quantum Teleportation** - Quantum communication protocols
- **Grover's Algorithm** - Quantum search algorithms
- **Quantum Fourier Transform** - Quantum signal processing

## 🐳 Docker Deployment

The project includes a `Dockerfile` for containerized deployment:

```bash
# Build the Docker image
docker build -t cirq-rag-code-assistant .

# Run the container
docker run -it cirq-rag-code-assistant
```

See the `Dockerfile` for details on the containerization setup.

## 🔮 Future Enhancements

### Post-Project Development

- **Knowledge Base Scaling** - Expand from 140+ to 2,500+ curated entries
- **RL Optimization** - Production deployment of reinforcement learning-based optimization
- **QCanvas Integration** - Real-time circuit visualization and hardware-aware optimization
- **User Studies** - Educational effectiveness evaluation with human participants
- **Multi-Framework Support** - Extend to Qiskit, PennyLane, and other frameworks
- **Cloud Deployment** - Scalable cloud-based quantum computing assistance

## 📚 Documentation

- **[Project Overview](docs/overview.md)** - Detailed project description and goals
- **[Architecture Guide](docs/architecture.md)** - System design and components
- **[Installation Guide](docs/installation.md)** - Comprehensive setup instructions
- **[Quick Start](docs/quickstart.md)** - Get up and running quickly
- **[Technology Stack](docs/tech-stack.md)** - Complete technology overview
- **[API Documentation](docs/api/README.md)** - REST API reference
- **[Agent Documentation](docs/agents/README.md)** - Multi-agent system details
- **[Research Paper](docs/Research%20Paper/LaTeX%20Files/main.tex)** - Complete research paper (Springer LNCS format)
- **[Evaluation Rubric](docs/rubric.md)** - Project evaluation criteria and self-assessment

## 🤝 Contributing

We welcome contributions! Please see our development guidelines:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** and ensure tests pass
4. **Commit your changes** (`git commit -m 'Add amazing feature'`)
5. **Push to the branch** (`git push origin feature/amazing-feature`)
6. **Open a Pull Request**

### Development Standards

- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for any changes
- Ensure all pre-commit hooks pass
- Use conventional commit messages

## 📄 License

This project is licensed under the **Academic Use License** - see the [LICENSE](LICENSE) file for details.

**Key Points:**
- ✅ **Academic use** - Free for educational and research purposes
- ✅ **Open source** - Source code available for study and modification
- ❌ **Commercial use** - Requires explicit written permission
- 📧 **Contact** - umerfarooqcs0891@gmail.com for licensing inquiries

## 👥 Authors

- **Umer Farooq** (Team Lead) - umerfarooqcs0891@gmail.com
- **Hussain Waseem Syed** - i220893@nu.edu.pk  
- **Muhammad Irtaza Khan** - i220911@nu.edu.pk

## 📞 Support

- **Issues** - [GitHub Issues](https://github.com/Umer-Farooq-CS/Cirq-RAG-Code-Assistant/issues)
- **Email** - umerfarooqcs0891@gmail.com
- **Documentation** - [docs/](docs/) directory

## 🙏 Acknowledgments

- **Google Cirq Team** - For the excellent quantum computing framework
- **PyTorch Team** - For GPU optimization capabilities
- **Open Source Community** - For the tools and libraries that made this possible

---

<div align="center">

**Made with ❤️ for the quantum computing community**

[⭐ Star this repo](https://github.com/Umer-Farooq-CS/Cirq-RAG-Code-Assistant) | [🐛 Report Bug](https://github.com/Umer-Farooq-CS/Cirq-RAG-Code-Assistant/issues) | [💡 Request Feature](https://github.com/Umer-Farooq-CS/Cirq-RAG-Code-Assistant/issues)

</div>