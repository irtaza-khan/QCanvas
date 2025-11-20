# Use the python/pip from the active virtual environment
PYTHON = python3
PIP = pip

.PHONY: help install install-dev test-all test-qiskit test-cirq test-pennylane clean

help:
	@echo "----------------------------------------------------------------"
	@echo "  make install          - Install for USAGE only (no dev tools)"
	@echo "  make install-dev      - Install for DEVELOPMENT (includes pytest)"
	@echo "  make test-qiskit      - Run only Qiskit backend tests"
	@echo "  make test-cirq        - Run only Cirq backend tests"
	@echo "  make test-pennylane   - Run only PennyLane backend tests"
	@echo "  make clean            - Cleanup temp files"
	@echo "----------------------------------------------------------------"

# 1. USER INSTALLATION
# This installs dependencies + qsim, No pytest.
install:
	$(PIP) install -e .

# 2. DEVELOPER INSTALLATION
# This installs pytest and other dev tools defined in pyproject.toml
install-dev:
	$(PIP) install -e ".[dev]"

# 3. SEPARATE TESTING COMMANDS
test-qiskit:
	pytest tests/test_qiskit.py

test-cirq:
	pytest tests/test_cirq.py

test-pennylane:
	pytest tests/test_pennylane.py

# Run all tests
test-all:
	pytest tests/

# 4. CLEANING
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete