#!/usr/bin/env python3
"""
Test script to verify Qiskit to OpenQASM 3.0 conversion
"""

from quantum_converters.converters.qiskit_to_qasm import convert_qiskit_to_qasm3

def test_qiskit_conversion():
    """Test the Qiskit to QASM conversion with the example code."""

    # Input Qiskit code
    qiskit_code = """
from qiskit import QuantumCircuit, execute, Aer

# Number of random bits you want
n_bits = 8

qc = QuantumCircuit(n_bits, n_bits)

# Put each qubit in superposition
for i in range(n_bits):
    qc.h(i)

# Measure all qubits
qc.measure(range(n_bits), range(n_bits))
"""

    # Expected OpenQASM 3.0 output
    expected_qasm = """OPENQASM 3.0;
include "stdgates.inc";

qubit[8] q;
bit[8] r;

// Apply Hadamard to each qubit
h q;

// Measure to get random bits
for uint i in [0:7] {
    r[i] = measure q[i];
}"""

    print("Testing Qiskit to QASM conversion...")
    print("=" * 50)
    print("Input Qiskit code:")
    print(qiskit_code)
    print("=" * 50)

    try:
        # Convert using the converter
        result = convert_qiskit_to_qasm3(qiskit_code)
        actual_qasm = result.qasm_code.strip()

        print("Actual QASM output:")
        print(actual_qasm)
        print("=" * 50)
        print("Expected QASM output:")
        print(expected_qasm)
        print("=" * 50)

        # Compare outputs (normalize whitespace)
        def normalize_qasm(qasm):
            return '\n'.join(line.strip() for line in qasm.split('\n') if line.strip())

        actual_normalized = normalize_qasm(actual_qasm)
        expected_normalized = normalize_qasm(expected_qasm)

        if actual_normalized == expected_normalized:
            print("✅ SUCCESS: Conversion matches expected output!")
            return True
        else:
            print("❌ FAILURE: Conversion does not match expected output.")
            print("\nDifferences:")
            actual_lines = actual_normalized.split('\n')
            expected_lines = expected_normalized.split('\n')

            for i, (a, e) in enumerate(zip(actual_lines, expected_lines)):
                if a != e:
                    print(f"Line {i+1}:")
                    print(f"  Actual:   '{a}'")
                    print(f"  Expected: '{e}'")
                    break

            # Show remaining lines if lengths differ
            if len(actual_lines) != len(expected_lines):
                print(f"Length mismatch: Actual has {len(actual_lines)} lines, Expected has {len(expected_lines)} lines")

            return False

    except Exception as e:
        print(f"❌ ERROR: Conversion failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_qiskit_conversion()
    exit(0 if success else 1)
