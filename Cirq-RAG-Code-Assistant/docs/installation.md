# Installation Guide

This guide covers **Windows**, **Linux**, and **macOS**. Commands are shown for all platforms where they differ.

## 🚀 Quick Start

The fastest way to get started with Cirq-RAG-Code-Assistant is to install it using pip:

```bash
pip install cirq-rag-code-assistant
```

(On Windows you can use the same command in Command Prompt or PowerShell.)

## 📋 Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, Linux (Ubuntu 20.04+), or macOS 10.15+
- **Python**: 3.11 or higher
- **Memory**: 8GB RAM minimum, 16GB recommended
- **Storage**: 10GB free space
- **CPU**: Multi-core processor recommended
- **GPU**: NVIDIA GPU with CUDA support (optional; for PyTorch CUDA on Windows/Linux)

### Python Installation
If you don't have Python 3.11+ installed:

#### Windows
- Download the installer from [python.org/downloads](https://www.python.org/downloads/) and run it. Check **"Add Python to PATH"**.
- Or use the Microsoft Store: search for "Python 3.11" and install.

#### Linux (Ubuntu)
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip
```

#### macOS
```bash
# Using Homebrew (install from https://brew.sh if needed)
brew install python@3.11
```

### GPU Setup (Optional, Windows & Linux)
For PyTorch CUDA optimization (NVIDIA GPU):

- **Windows**: Install [NVIDIA drivers](https://www.nvidia.com/Download/index.aspx) and [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) if needed. Check GPU with `nvidia-smi` in Command Prompt or PowerShell.
- **Linux**: Install NVIDIA drivers (e.g. `sudo apt install nvidia-driver-525`), then check with `nvidia-smi`.

#### Install PyTorch with CUDA (Windows & Linux)
```bash
# Check your CUDA version: nvidia-smi

# For CUDA 11.8:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Verify installation:
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"
```

On **macOS** or if you don't need GPU, use the default pip install (CPU-only PyTorch is fine).

## 🔧 Installation Methods

### 1. Production Installation

#### From PyPI (Recommended)
```bash
pip install cirq-rag-code-assistant
```

#### From Source
```bash
git clone https://github.com/umerfarooq/cirq-rag-code-assistant.git
cd cirq-rag-code-assistant
pip install -e .
```

### 2. Development Installation

For development work, install with all development dependencies:

```bash
git clone https://github.com/umerfarooq/cirq-rag-code-assistant.git
cd cirq-rag-code-assistant
pip install -e ".[dev,gpu,quantum,qcanvas]"
```

### 3. Virtual Environment (Recommended)

#### Create Virtual Environment
```bash
# Create virtual environment
python -m venv cirq-rag-env

# Activate (Linux/macOS)
source cirq-rag-env/bin/activate

# Activate (Windows)
cirq-rag-env\Scripts\activate
```

#### Install in Virtual Environment
```bash
pip install cirq-rag-code-assistant
```

### 4. Using Poetry (Alternative)

If you prefer Poetry for dependency management:

**Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
poetry install
poetry shell
```

**Linux/macOS:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
poetry install
poetry shell
```

## 🎯 Installation Options

### Basic Installation
```bash
pip install cirq-rag-code-assistant
```

### With PyTorch CUDA GPU Support
```bash
# First install PyTorch with CUDA (choose based on your CUDA version)
# For CUDA 11.8:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Then install the package
pip install cirq-rag-code-assistant[gpu]
```

### With Quantum Computing Extensions
```bash
pip install cirq-rag-code-assistant[quantum]
```

### With QCanvas Integration
```bash
pip install cirq-rag-code-assistant[qcanvas]
```

### Complete Development Installation
```bash
pip install cirq-rag-code-assistant[dev,gpu,quantum,qcanvas]
```

## 🔍 Verification

### Check Installation
```bash
# Check version
cirq-rag --version

# Test CLI
cirq-rag --help

# Test Python import
python -c "import cirq_rag_code_assistant; print('Installation successful!')"
```

### Run Basic Test
```bash
# Test basic functionality
python -c "
from cirq_rag_code_assistant import DesignerAgent
agent = DesignerAgent()
print('Designer Agent initialized successfully!')
"
```

## 🔧 QCanvas Integration Setup

### Verify QCanvas Integration
```bash
# Test QCanvas integration
python -c "from cirq_rag_code_assistant.integration import QCanvasClient; print('QCanvas integration ready!')"
```

### Start Development Server for QCanvas
```bash
# Start server for QCanvas integration
cirq-rag server --host 0.0.0.0 --port 8000
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in your project directory:

```bash
# API Configuration
OPENAI_API_KEY=your_openai_api_key_here
CIRQ_RAG_LOG_LEVEL=INFO
CIRQ_RAG_DEBUG=false

# Database Configuration (SQLite for development)
DATABASE_URL=sqlite:///./cirq_rag.db

# Vector Database
VECTOR_DB_PATH=./vector_db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# QCanvas Integration
QCANVAS_HOST=localhost
QCANVAS_PORT=3000
QCANVAS_API_KEY=your_qcanvas_api_key

# GPU Configuration
TF_GPU_MEMORY_GROWTH=true
CUDA_VISIBLE_DEVICES=0

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### Configuration File
Create `config.yaml`:

```yaml
# Cirq-RAG-Code-Assistant Configuration
system:
  log_level: INFO
  debug: false
  workers: 4

api:
  host: "0.0.0.0"
  port: 8000
  cors_origins: ["*"]

agents:
  designer:
    max_retries: 3
    timeout: 30
  optimizer:
    optimization_level: "balanced"
  validator:
    simulation_timeout: 60
  educational:
    explanation_depth: "intermediate"

rag:
  vector_store:
    index_type: "hnsw"
    similarity_threshold: 0.7
  knowledge_base:
    update_interval: 3600

database:
  url: "sqlite:///./cirq_rag.db"
  echo: false

cache:
  redis_url: "redis://localhost:6379"
  ttl: 3600
```

## 🤖 Ollama Setup

This project can use Ollama for local LLM inference (optional if you use AWS Bedrock). If using Ollama, install it and create the custom agent models.

### Install Ollama

- **Windows**: Download the installer from [ollama.ai](https://ollama.ai) and run it. Ollama runs in the background; no separate `ollama serve` needed.
- **macOS**: Download from [ollama.ai](https://ollama.ai) or run `brew install ollama` and start the app.
- **Linux**: Download from [ollama.ai](https://ollama.ai) or run:
  ```bash
  curl -fsSL https://ollama.ai/install.sh | sh
  ollama serve
  ```

### Pull Base Models

Same on all platforms (run in Command Prompt, PowerShell, or terminal):

```bash
ollama pull qwen2.5-coder:14b-instruct-q4_K_M
ollama pull llama3.1:8b-instruct-q5_K_M
```

### Create Custom Agent Models

From the project root directory:

**Windows (Command Prompt or PowerShell):**
```cmd
cd config\ollama
ollama create cirq-designer-agent -f designer_agent.Modelfile
ollama create cirq-edu-agent -f educational_agent.Modelfile
cd ..\..
```

**Linux/macOS:**
```bash
cd config/ollama
ollama create cirq-designer-agent -f designer_agent.Modelfile
ollama create cirq-edu-agent -f educational_agent.Modelfile
cd ../..
```

### Verify Agent Models

```bash
ollama list
ollama run cirq-designer-agent "Create a Bell state circuit"
ollama run cirq-edu-agent "Explain superposition simply"
```

### Remove/Recreate Agent Models

**Windows:** `cd config\ollama` then run the `ollama rm` / `ollama create` commands below.  
**Linux/macOS:** `cd config/ollama` then:

```bash
ollama rm cirq-designer-agent
ollama create cirq-designer-agent -f designer_agent.Modelfile
```

## AWS Bedrock (optional)

You can use **AWS Bedrock** (Amazon Nova models) instead of Ollama for all agents and for RAG embeddings. This uses the same config and code; only credentials and provider settings change.

### 1. Credentials and env

1. Copy `.env.example` to `.env` in the project root. **On Windows:** use the same format in `.env` (no `set` prefix); the app loads it automatically. You can run `powershell -File scripts\set_aws_env.ps1 -CreateEnv` to create `.env` from the example.
2. Set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION` (e.g. `us-east-1`) in `.env`. Never commit `.env`.
3. Install dependencies: `pip install boto3` (included in `requirements.txt`).

### 2. Config

In `config/config.json`, the `aws` section and agent `model.provider` values can be set to use AWS. Defaults in config may already point to Nova model IDs and `provider: "aws"`. Each agent’s `model.provider` can be `"aws"` or `"ollama"` independently.

### 3. Re-build vector index when using AWS embeddings

If you set **RAG embeddings** to AWS (`models.embedding.provider` = `"aws"`), the embedding model and dimension (e.g. 1024) differ from the local sentence-transformers setup (e.g. 768). You **must re-build the vector index** after switching:

1. Remove or rename the existing vector index (e.g. delete or move the `data/models/vector_index` directory).
2. Run your usual flow that loads the knowledge base and builds the index (e.g. CLI init, or the notebooks that create the FAISS index from the knowledge base). The new index will use the AWS embedding dimension.

If you switch back to local embeddings, remove the index again and re-build so the dimension matches the local model.

## 🚀 First Run

### Initialize the System
```bash
# Initialize knowledge base
cirq-rag init

# Start the server
cirq-rag server

# Or use the CLI
cirq-rag generate "Create a simple VQE circuit"
```

### Web Interface
1. Start the server: `cirq-rag server`
2. Open browser: `http://localhost:8000`
3. Access API docs: `http://localhost:8000/docs`

## 🔧 Development Setup

### Clone Repository
```bash
git clone https://github.com/umerfarooq/cirq-rag-code-assistant.git
cd cirq-rag-code-assistant
```

### Install Development Dependencies
```bash
# Install with all development tools
pip install -e ".[dev,docs,gpu,quantum]"

# Install pre-commit hooks
pre-commit install
```

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cirq_rag_code_assistant

# Run specific test categories
pytest -m "not slow"
pytest -m "gpu"
pytest -m "quantum"
```

### Code Quality
```bash
# Format code
black src/ tests/
isort src/ tests/

# Run linting
flake8 src/ tests/
mypy src/

# Run all quality checks
pre-commit run --all-files
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Python Version Error
```
ERROR: Package requires Python >=3.11
```
**Solution**: Install Python 3.11 or higher

#### 2. Memory Issues
```
ERROR: Out of memory during installation
```
**Solution**: 
- Close other applications
- Use `--no-cache-dir` flag: `pip install --no-cache-dir cirq-rag-code-assistant`

#### 3. CUDA/GPU Issues
```
ERROR: CUDA not found
```
**Solution**: 
- Install CPU-only version: `pip install cirq-rag-code-assistant`
- Or install CUDA toolkit for GPU support

#### 4. Import Errors
```
ModuleNotFoundError: No module named 'cirq_rag_code_assistant'
```
**Solution**:
- Ensure virtual environment is activated
- Reinstall the package: `pip install -e .`

#### 5. Permission Errors
```
ERROR: Permission denied
```
**Solution**:
- Use virtual environment
- Or use `--user` flag: `pip install --user cirq-rag-code-assistant`

### Getting Help

#### Check Installation
```bash
python --version
python -c "import cirq_rag_code_assistant; print('OK')"
```

**Check if the package is installed:**  
- **Windows (PowerShell):** `pip list | Select-String cirq-rag`  
- **Linux/macOS:** `pip list | grep cirq-rag`

#### Debug Mode

**Windows (Command Prompt):**
```cmd
 set CIRQ_RAG_DEBUG=true
 set CIRQ_RAG_LOG_LEVEL=DEBUG
cirq-rag --verbose generate "test"
```

**Windows (PowerShell):**
```powershell
$env:CIRQ_RAG_DEBUG="true"; $env:CIRQ_RAG_LOG_LEVEL="DEBUG"
cirq-rag --verbose generate "test"
```

**Linux/macOS:**
```bash
export CIRQ_RAG_DEBUG=true
export CIRQ_RAG_LOG_LEVEL=DEBUG
cirq-rag --verbose generate "test"
```

#### Log Files
Check log files for detailed error information:

**Windows (PowerShell):** `Get-Content logs\app.log -Wait`  
**Linux/macOS:** `tail -f logs/app.log`

## 📚 Next Steps

After successful installation:

1. **Read the Documentation**: Start with [Quick Start Guide](quickstart.md)
2. **Explore Examples**: Check [Usage Examples](examples/README.md)
3. **API Reference**: See [API Documentation](api/README.md)
4. **Join Community**: Visit our [GitHub Discussions](https://github.com/umerfarooq/cirq-rag-code-assistant/discussions)

## 🔄 Updates

### Update Installation
```bash
# Update to latest version
pip install --upgrade cirq-rag-code-assistant

# Update from source
git pull origin main
pip install -e .
```

### Uninstall
```bash
pip uninstall cirq-rag-code-assistant
```

**Remove virtual environment:**  
- **Windows:** delete the folder `cirq-rag-env` or run `rmdir /s cirq-rag-env` in Command Prompt.  
- **Linux/macOS:** `rm -rf cirq-rag-env`

---

*For more detailed information, see the [Architecture Guide](architecture.md) and [API Documentation](api/README.md).*
