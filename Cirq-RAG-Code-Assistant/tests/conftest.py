"""Pytest configuration and shared fixtures."""

import pytest
import sys
import os
from pathlib import Path

# Add src to Python path
PROJECT_ROOT = Path(__file__).parent.parent
SRC_PATH = PROJECT_ROOT / "src"
# Project root enables `from src.xxx import ...` (matches how uvicorn loads it);
# src path is retained for tests written against bare module names.
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SRC_PATH))

@pytest.fixture
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent

@pytest.fixture
def src_path():
    """Return the src directory path."""
    return PROJECT_ROOT / "src"

@pytest.fixture
def test_data_path():
    """Return the test data directory path."""
    return Path(__file__).parent / "data"

@pytest.fixture
def temp_output_path(tmp_path):
    """Return a temporary output directory."""
    return tmp_path / "outputs"

@pytest.fixture(scope="session")
def test_config():
    """Return test configuration."""
    return {
        "test_mode": True,
        "log_level": "DEBUG",
        "max_iterations": 5,
        "timeout_seconds": 30,
    }

@pytest.fixture
def mock_cirq_circuit():
    """Return a mock Cirq circuit for testing."""
    import cirq

    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(cirq.H(q0), cirq.CNOT(q0, q1), cirq.measure(q0, q1, key="m"))
    return circuit

@pytest.fixture
def mock_quantum_algorithm():
    """Return mock quantum algorithm data."""
    return {
        "name": "test_algorithm",
        "description": "A test quantum algorithm",
        "qubits": 2,
        "gates": ["H", "CNOT", "M"],
        "expected_output": "00 or 11 with equal probability"
    }

# Markers for different test types
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "gpu: marks tests that require GPU")
    config.addinivalue_line("markers", "quantum: marks tests that require quantum simulators")
