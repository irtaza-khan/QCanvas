"""
Demo: Cirq Converter Output

Shows the actual OpenQASM 3.0 output from the integrated Cirq converter.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from quantum_converters.converters.cirq_to_qasm import CirqToQASM3Converter

# Example Cirq circuit
cirq_code = '''
import cirq
import numpy as np

def get_circuit():
    # Create qubits
    q0, q1, q2 = cirq.LineQubit.range(3)
    
    # Create circuit with Iteration I features
    circuit = cirq.Circuit(
        # Basic gates
        cirq.H(q0),
        cirq.X(q1),
        cirq.Y(q2),
        
        # Parameterized gates
        cirq.rx(np.pi/2)(q0),
        cirq.ry(np.pi/4)(q1),
        cirq.rz(np.pi)(q2),
        
        # Two-qubit gates
        cirq.CNOT(q0, q1),
        cirq.CZ(q1, q2),
        
        # Inverse gates (demonstrating inv@ modifier)
        cirq.S(q0)**-1,
        cirq.T(q1)**-1,
        
        # Measurements
        cirq.measure(q0, key='m0'),
        cirq.measure(q1, key='m1'),
        cirq.measure(q2, key='m2')
    )
    
    return circuit
'''

# Convert
converter = CirqToQASM3Converter()
result = converter.convert(cirq_code)

# Print results
print("=" * 80)
print("CIRQ CONVERTER OUTPUT - USING QASM3Builder")
print("=" * 80)
print()
print(result.qasm_code)
print()
print("=" * 80)
print("CONVERSION STATISTICS")
print("=" * 80)
print(f"Number of qubits: {result.stats.n_qubits}")
print(f"Circuit depth: {result.stats.depth}")
print(f"Gate counts: {result.stats.gate_counts}")
print(f"Has measurements: {result.stats.has_measurements}")
print("=" * 80)
