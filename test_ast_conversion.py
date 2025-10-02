#!/usr/bin/env python3
"""
Test script to verify AST-based Qiskit to QASM3 conversion.
"""

import logging
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging to see the AST parsing message
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Import the converter
from quantum_converters.converters import convert_qiskit_to_qasm3

# Test Qiskit source code
qiskit_source = """
from qiskit import QuantumCircuit
def get_circuit():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc
"""

def main():
    print("Testing AST-based Qiskit to QASM3 conversion...")
    print("=" * 50)

    try:
        # Perform the conversion
        result = convert_qiskit_to_qasm3(qiskit_source)

        print("Conversion successful!")
        print(f"Circuit stats: {result.stats.n_qubits} qubits, depth {result.stats.depth}")
        print("\nGenerated QASM3 code:")
        print("-" * 30)
        print(result.qasm_code)
        print("-" * 30)

        # Verify AST usage by checking for expected log message
        print("\nCheck the logs above for 'Using AST parsing for secure Qiskit code analysis'")
        print("and VERBOSE debug output if enabled.")

    except Exception as e:
        print(f"Conversion failed: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
