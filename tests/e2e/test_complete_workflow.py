#!/usr/bin/env python3
"""End-to-end tests for complete QCanvas workflows."""

import unittest
import sys
import os
import requests
import time

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestCompleteWorkflow(unittest.TestCase):
    """Test complete QCanvas workflows."""

    def setUp(self):
        """Set up test fixtures."""
        # Test against the actual API
        self.api_base = "http://localhost:8000"  # Assuming backend is running
    
    def test_framework_to_qasm_conversion_workflow(self):
        """Test complete framework-to-OpenQASM conversion workflow."""
        # Step 1: Write Qiskit code
        qiskit_code = '''
from qiskit import QuantumCircuit

def get_circuit():
    qc = QuantumCircuit(3, 3)
    # Quantum Fourier Transform
    for i in range(3):
        qc.h(i)
        for j in range(i + 1, 3):
            angle = 3.14159 / (2 ** (j - i))
            qc.cp(angle, j, i)
    # Measure all qubits
    qc.measure_all()
    return qc
'''

        # Step 2: Convert via API
        try:
            response = requests.post(
                f"{self.api_base}/api/converter/convert",
                json={
                    "code": qiskit_code,
                    "framework": "qiskit",
                    "qasm_version": "3.0"
                },
                timeout=30
            )

            # Step 3: Check response
            self.assertEqual(response.status_code, 200)
            result = response.json()

            # Step 4: Validate conversion result
            self.assertTrue(result["success"])
            self.assertIn("qasm_code", result)
            self.assertIn("OPENQASM 3.0", result["qasm_code"])
            self.assertIn("qubit[3]", result["qasm_code"])
            self.assertIn("conversion_stats", result)

        except requests.exceptions.ConnectionError:
            self.skipTest("Backend API not available (not running)")
    
    def test_multiple_frameworks_conversion(self):
        """Test conversion across different frameworks."""
        frameworks_to_test = [
            ("qiskit", '''
from qiskit import QuantumCircuit
def get_circuit():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc
'''),
            ("cirq", '''
import cirq
def get_circuit():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.H(q0),
        cirq.CNOT(q0, q1)
    )
    return circuit
'''),
        ]

        for framework, code in frameworks_to_test:
            with self.subTest(framework=framework):
                try:
                    response = requests.post(
                        f"{self.api_base}/api/converter/convert",
                        json={
                            "code": code,
                            "framework": framework,
                            "qasm_version": "3.0"
                        },
                        timeout=30
                    )

                    self.assertEqual(response.status_code, 200)
                    result = response.json()
                    self.assertTrue(result["success"])
                    self.assertIn("OPENQASM 3.0", result["qasm_code"])

                except requests.exceptions.ConnectionError:
                    self.skipTest("Backend API not available (not running)")

    def test_error_handling_workflow(self):
        """Test error handling in conversion."""
        # Step 1: Send invalid framework code
        invalid_code = '''
def get_circuit():
    # Invalid - missing imports and wrong syntax
    return some_invalid_circuit
'''

        try:
            response = requests.post(
                f"{self.api_base}/api/converter/convert",
                json={
                    "code": invalid_code,
                    "framework": "qiskit",
                    "qasm_version": "3.0"
                },
                timeout=30
            )

            # Should still return a response (not crash)
            self.assertEqual(response.status_code, 200)
            result = response.json()
            # May succeed with fallback or fail gracefully
            self.assertIn("success", result)

        except requests.exceptions.ConnectionError:
            self.skipTest("Backend API not available (not running)")

    def test_performance_workflow(self):
        """Test performance with large circuits."""
        # Step 1: Create large Qiskit circuit
        large_circuit_code = '''
from qiskit import QuantumCircuit

def get_circuit():
    qc = QuantumCircuit(10, 10)
    # Add many operations
    for i in range(10):
        qc.h(i)

    for i in range(0, 10, 2):
        qc.cx(i, i+1)

    qc.measure_all()
    return qc
'''

        try:
            # Step 2: Measure conversion time
            start_time = time.time()
            response = requests.post(
                f"{self.api_base}/api/converter/convert",
                json={
                    "code": large_circuit_code,
                    "framework": "qiskit",
                    "qasm_version": "3.0"
                },
                timeout=60  # Allow more time for large circuits
            )
            end_time = time.time()

            # Step 3: Verify success and performance
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertTrue(result["success"])
            self.assertLess(end_time - start_time, 30.0)  # Should complete within 30 seconds

        except requests.exceptions.ConnectionError:
            self.skipTest("Backend API not available (not running)")


if __name__ == '__main__':
    unittest.main()
