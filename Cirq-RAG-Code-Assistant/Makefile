# Makefile for Cirq-RAG-Code-Assistant
# =====================================

.PHONY: help install install-dev test lint format clean docs serve-docs build dist upload

# Default target
help: ## Show this help message
	@echo "Cirq-RAG-Code-Assistant Makefile"
	@echo "================================"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation
install: ## Install the package in production mode
	pip install -e .

install-dev: ## Install the package in development mode with all dev dependencies
	pip install -e ".[dev,gpu,quantum,qcanvas]"
	pre-commit install

install-gpu: ## Install with GPU support
	pip install -e ".[gpu]"

install-quantum: ## Install with quantum computing extensions
	pip install -e ".[quantum]"

install-qcanvas: ## Install with QCanvas integration support (future enhancement)
	@echo "QCanvas integration is planned as a future enhancement"
	@echo "This will be implemented after the core research project is completed"

# Development
test: ## Run tests
	pytest tests/ -v --cov=cirq_rag_code_assistant --cov-report=html --cov-report=term-missing

test-unit: ## Run unit tests only
	pytest tests/unit/ -v

test-integration: ## Run integration tests only
	pytest tests/integration/ -v

test-fast: ## Run fast tests (skip slow tests)
	pytest tests/ -v -m "not slow"

test-gpu: ## Run GPU tests (requires GPU)
	pytest tests/ -v -m "gpu"

test-quantum: ## Run quantum tests (requires quantum simulators)
	pytest tests/ -v -m "quantum"

# Code Quality
lint: ## Run all linting tools
	flake8 src/ tests/
	mypy src/
	black --check src/ tests/
	isort --check-only src/ tests/

format: ## Format code with black and isort
	black src/ tests/
	isort src/ tests/

format-check: ## Check code formatting
	black --check src/ tests/
	isort --check-only src/ tests/

# Pre-commit
pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

pre-commit-install: ## Install pre-commit hooks
	pre-commit install

# Documentation
docs: ## Build documentation
	cd docs && make html

docs-clean: ## Clean documentation build
	cd docs && make clean

serve-docs: ## Serve documentation locally
	cd docs/_build/html && python -m http.server 8000

docs-api: ## Generate API documentation
	sphinx-apidoc -o docs/api src/cirq_rag_code_assistant

# Building (for development)
build: ## Build the package for development
	python -m build

# Installation from source
install-from-source: ## Install from source
	pip install -e .

# Cleaning
clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .tox/
	rm -rf .nox/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete

clean-docs: ## Clean documentation
	cd docs && make clean

clean-data: ## Clean data files
	rm -rf data/
	rm -rf datasets/
	rm -rf models/
	rm -rf vector_db/
	rm -rf knowledge_base/
	rm -rf logs/
	rm -rf tmp/
	rm -rf cache/

clean-all: clean clean-docs clean-data ## Clean everything

# Development Server (for QCanvas integration)
dev-server: ## Start development server for QCanvas integration (future enhancement)
	@echo "QCanvas integration is planned as a future enhancement"
	@echo "This will be implemented after the core research project is completed"

dev-server-debug: ## Start development server with debug mode (future enhancement)
	@echo "QCanvas integration is planned as a future enhancement"
	@echo "This will be implemented after the core research project is completed"

# CLI
cli-help: ## Show CLI help
	python -m cirq_rag_code_assistant.cli.main --help

cli-test: ## Test CLI functionality
	python -m cirq_rag_code_assistant.cli.main --version

# Database
db-init: ## Initialize database
	python -m cirq_rag_code_assistant.db.init

db-migrate: ## Run database migrations
	python -m cirq_rag_code_assistant.db.migrate

db-reset: ## Reset database
	python -m cirq_rag_code_assistant.db.reset

# Knowledge Base
kb-init: ## Initialize knowledge base
	python -m cirq_rag_code_assistant.rag.init_kb

kb-update: ## Update knowledge base
	python -m cirq_rag_code_assistant.rag.update_kb

kb-rebuild: ## Rebuild knowledge base from scratch
	python -m cirq_rag_code_assistant.rag.rebuild_kb

# Agents
agent-test: ## Test all agents
	python -m cirq_rag_code_assistant.agents.test_all

agent-designer: ## Test designer agent
	python -m cirq_rag_code_assistant.agents.test_designer

agent-optimizer: ## Test optimizer agent
	python -m cirq_rag_code_assistant.agents.test_optimizer

agent-validator: ## Test validator agent
	python -m cirq_rag_code_assistant.agents.test_validator

agent-educational: ## Test educational agent
	python -m cirq_rag_code_assistant.agents.test_educational

# Performance
benchmark: ## Run performance benchmarks
	python -m cirq_rag_code_assistant.evaluation.benchmark

profile: ## Run performance profiling
	python -m cirq_rag_code_assistant.evaluation.profile

# Security
security-check: ## Run security checks
	bandit -r src/
	safety check

# QCanvas Integration (Future Enhancement)
qcanvas-test: ## Test QCanvas integration (future enhancement)
	@echo "QCanvas integration is planned as a future enhancement"
	@echo "This will be implemented after the core research project is completed"

qcanvas-demo: ## Run QCanvas integration demo (future enhancement)
	@echo "QCanvas integration is planned as a future enhancement"
	@echo "This will be implemented after the core research project is completed"

# Environment
env-create: ## Create virtual environment
	python -m venv venv

env-activate: ## Activate virtual environment (Linux/Mac)
	source venv/bin/activate

env-activate-win: ## Activate virtual environment (Windows)
	venv\Scripts\activate

env-install: ## Install dependencies in virtual environment
	pip install -r requirements.txt

# Git
git-hooks: ## Install git hooks
	pre-commit install

git-hooks-update: ## Update git hooks
	pre-commit autoupdate

# Development Testing
dev-test: ## Run development tests
	pytest tests/ --cov=cirq_rag_code_assistant --cov-report=xml --junitxml=test-results.xml

dev-lint: ## Run development linting
	flake8 src/ tests/
	mypy src/
	black --check src/ tests/
	isort --check-only src/ tests/

dev-security: ## Run development security checks
	bandit -r src/
	safety check

# Development Monitoring
dev-logs: ## View development logs
	tail -f logs/app.log

dev-logs-error: ## View error logs
	tail -f logs/error.log

# Development Backup
dev-backup: ## Backup important development files
	tar -czf backup-$(shell date +%Y%m%d-%H%M%S).tar.gz src/ docs/ tests/ requirements.txt pyproject.toml

# Help
help-install: ## Show installation help
	@echo "Installation Options:"
	@echo "  make install        - Basic installation"
	@echo "  make install-dev    - Development installation with all tools"
	@echo "  make install-gpu    - With PyTorch CUDA support"
	@echo "  make install-quantum - With quantum computing extensions"
	@echo "  make install-qcanvas - With QCanvas integration support (future enhancement)"

help-dev: ## Show development help
	@echo "Development Commands:"
	@echo "  make test           - Run all tests"
	@echo "  make lint           - Run linting"
	@echo "  make format         - Format code"
	@echo "  make dev-server     - Start development server for QCanvas (future enhancement)"
	@echo "  make qcanvas-test   - Test QCanvas integration (future enhancement)"

# Default target when no argument is provided
.DEFAULT_GOAL := help
