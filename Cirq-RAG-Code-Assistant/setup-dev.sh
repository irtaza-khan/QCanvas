#!/bin/bash

# Cirq-RAG-Code-Assistant Development Environment Setup Script
# For Linux Ubuntu with PyTorch CUDA support

set -e  # Exit on any error

echo "🚀 Setting up Cirq-RAG-Code-Assistant development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Ubuntu
if ! grep -q "Ubuntu" /etc/os-release; then
    print_warning "This script is optimized for Ubuntu. You may need to adjust package manager commands."
fi

# Check Python version
print_status "Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    print_error "Python 3.11+ is required. Found: $python_version"
    print_status "Please install Python 3.11+ and try again."
    exit 1
fi

print_success "Python version check passed: $python_version"

# Check for NVIDIA GPU and CUDA
print_status "Checking for NVIDIA GPU and CUDA..."
if command -v nvidia-smi &> /dev/null; then
    print_success "NVIDIA GPU detected:"
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader,nounits
else
    print_warning "NVIDIA GPU not detected. PyTorch will run on CPU."
fi

# Create virtual environment
print_status "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install development dependencies
print_status "Installing development dependencies..."
pip install -e ".[dev,gpu,quantum]"

# Install pre-commit hooks
print_status "Installing pre-commit hooks..."
pre-commit install
pre-commit install --hook-type pre-push

# Create necessary directories
print_status "Creating project directories..."
mkdir -p data/{knowledge_base,datasets,models}
mkdir -p outputs/{logs,reports,artifacts}
mkdir -p tests/{unit,integration,e2e}
mkdir -p src/{rag,agents,orchestration,evaluation,cli}

# Create initial configuration files
print_status "Creating initial configuration files..."

# Create .env template
cat > .env.template << EOF
# Cirq-RAG-Code-Assistant Environment Configuration

# API Keys (if needed)
# OPENAI_API_KEY=your_openai_api_key_here
# HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///data/braket_rag.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=outputs/logs/braket_rag.log

# PyTorch Configuration
CUDA_VISIBLE_DEVICES=0
TORCH_DEVICE=auto
TORCH_DETERMINISTIC=false
TORCH_BENCHMARK=true
TORCH_MEMORY_FRACTION=0.8

# Development Settings
DEBUG=True
ENVIRONMENT=development

# Model Configuration
DEFAULT_MODEL_NAME=BAAI/bge-base-en-v1.5
VECTOR_DB_TYPE=faiss
MAX_RETRIEVAL_RESULTS=5

# Agent Configuration
MAX_ITERATIONS=10
TIMEOUT_SECONDS=300
EOF

# Create local .env file
if [ ! -f ".env" ]; then
    cp .env.template .env
    print_success "Created .env file from template"
else
    print_warning ".env file already exists"
fi

# Test PyTorch CUDA installation
print_status "Testing PyTorch CUDA installation..."
python3 -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'✅ CUDA device: {torch.cuda.get_device_name(0)}')
else:
    print('⚠️  CUDA device not available - running on CPU')
"

# Run initial tests
print_status "Running initial tests..."
if [ -f "tests/test_basic.py" ]; then
    python -m pytest tests/test_basic.py -v
else
    print_warning "No basic tests found. Creating test structure..."
fi

# Create basic test file
cat > tests/test_basic.py << 'EOF'
"""Basic tests for Cirq-RAG-Code-Assistant."""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_python_version():
    """Test that we're using Python 3.11+."""
    assert sys.version_info >= (3, 11)

def test_imports():
    """Test that basic imports work."""
    try:
        import torch
        import cirq
        import numpy as np
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import required packages: {e}")

def test_pytorch_cuda():
    """Test PyTorch CUDA availability."""
    import torch
    assert isinstance(torch.cuda.is_available(), bool)

if __name__ == "__main__":
    pytest.main([__file__])
EOF

print_success "Created basic test file"

# Run the basic tests
python -m pytest tests/test_basic.py -v

# Final setup summary
print_success "🎉 Development environment setup complete!"
echo ""
print_status "Next steps:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Review and update .env file with your configuration"
echo "  3. Start implementing the RAG system: make dev-start"
echo "  4. Run tests: make test"
echo "  5. Check code quality: make lint"
echo ""
print_status "Useful commands:"
echo "  - make help          # Show all available commands"
echo "  - make test          # Run all tests"
echo "  - make lint          # Run linting"
echo "  - make format        # Format code"
echo "  - make clean         # Clean build artifacts"
echo ""
print_success "Happy coding! 🚀"
