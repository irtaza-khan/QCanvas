"""
Pytest configuration and fixtures for QCanvas tests.
"""

import pytest
import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def project_root_path():
    """Return the project root path."""
    return project_root


@pytest.fixture(scope="session")
def test_data_dir():
    """Return the test data directory."""
    return project_root / "tests" / "fixtures"


@pytest.fixture(scope="session")
def sample_circuits_dir():
    """Return the sample circuits directory."""
    return project_root / "tests" / "fixtures" / "sample_circuits"


@pytest.fixture(scope="session")
def expected_outputs_dir():
    """Return the expected outputs directory."""
    return project_root / "tests" / "fixtures" / "expected_outputs"


@pytest.fixture
def quantum_simulator():
    """Provide quantum simulator instance."""
    try:
        from quantum_simulator.core.statevector import StatevectorBackend
        return StatevectorBackend()
    except ImportError:
        pytest.skip("Quantum simulator not available")


@pytest.fixture
def api_client():
    """Provide API test client."""
    try:
        from backend.app.main import app
        from fastapi.testclient import TestClient
        return TestClient(app)
    except ImportError:
        pytest.skip("FastAPI not available")


@pytest.fixture
def sample_qasm_programs():
    """Provide sample OpenQASM programs for testing."""
    return {
        "simple": '''OPENQASM 3;
qubit q;
h q;''',
        
        "bell_state": '''OPENQASM 3;
qubit[2] q;
h q[0];
cx q[0], q[1];
c[0] = measure q[0];
c[1] = measure q[1];''',
        
        "qft": '''OPENQASM 3;
qubit[3] q;
bit[3] c;

// Quantum Fourier Transform
for (int i in range(3)) {
    h q[i];
    for (int j in range(i + 1, 3)) {
        float angle = pi / (2 ** (j - i));
        cp(angle) q[j], q[i];
    }
}

// Measure all qubits
for (int i in range(3)) {
    c[i] = measure q[i];
}''',
        
        "grover": '''OPENQASM 3;
qubit[3] q;
bit[3] c;
int n = 3;

// Grover's algorithm
for (int iteration in range(int(sqrt(2**n)))) {
    // Oracle
    for (int i in range(n)) {
        if (i == 0) {
            x q[i];
        }
    }
    
    // Diffusion operator
    for (int i in range(n)) {
        h q[i];
    }
    for (int i in range(n)) {
        x q[i];
    }
    h q[n-1];
    cx q[0], q[n-1];
    h q[n-1];
    for (int i in range(n)) {
        x q[i];
    }
    for (int i in range(n)) {
        h q[i];
    }
}

// Measure
for (int i in range(n)) {
    c[i] = measure q[i];
}'''
    }


@pytest.fixture
def sample_circuits():
    """Provide sample quantum circuits for testing."""
    return {
        "simple_h": {
            "gates": [{"type": "h", "qubits": [0]}],
            "num_qubits": 1
        },
        
        "bell_state": {
            "gates": [
                {"type": "h", "qubits": [0]},
                {"type": "cx", "qubits": [0, 1]},
                {"type": "measure", "qubits": [0, 1], "bits": [0, 1]}
            ],
            "num_qubits": 2,
            "num_bits": 2
        },
        
        "ghz_state": {
            "gates": [
                {"type": "h", "qubits": [0]},
                {"type": "cx", "qubits": [0, 1]},
                {"type": "cx", "qubits": [1, 2]},
                {"type": "measure", "qubits": [0, 1, 2], "bits": [0, 1, 2]}
            ],
            "num_qubits": 3,
            "num_bits": 3
        }
    }


@pytest.fixture
def test_errors():
    """Provide test error cases."""
    return {
        "syntax_error": '''OPENQASM 3;
qubit q;
h q  // Missing semicolon''',
        
        "type_error": '''OPENQASM 3;
int x = true;  // Type mismatch''',
        
        "undefined_variable": '''OPENQASM 3;
int x = undefined_var;''',
        
        "missing_version": '''include "stdgates.inc";
qubit q;
h q;''',
        
        "invalid_gate": '''OPENQASM 3.0;
qubit q;
invalid_gate q;'''
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    # Add markers based on test file location
    for item in items:
        test_path = Path(item.fspath)
        
        if "unit" in str(test_path):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(test_path):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(test_path):
            item.add_marker(pytest.mark.e2e)
        
        # Mark slow tests
        if "performance" in str(test_path) or "large" in str(test_path):
            item.add_marker(pytest.mark.slow)