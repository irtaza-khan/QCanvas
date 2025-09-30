"""
Demo Script: Qiskit to OpenQASM 3.0 Conversion

This script demonstrates the updated Qiskit converter using QASM3Builder.
It creates a sample circuit and shows the generated OpenQASM 3.0 code.

Author: QCanvas Team
Date: 2025-09-30
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from quantum_converters.converters.qiskit_to_qasm import QiskitToQASM3Converter


def main():
    """Run the demo"""
    print("=" * 80)
    print("Qiskit to OpenQASM 3.0 Conversion Demo")
    print("Using QASM3Builder Integration")
    print("=" * 80)
    print()
    
    # Example 1: Simple Bell State
    print("Example 1: Simple Bell State")
    print("-" * 80)
    source1 = '''
from qiskit import QuantumCircuit

def get_circuit():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc
'''
    
    converter = QiskitToQASM3Converter()
    result1 = converter.convert(source1)
    
    print("Generated OpenQASM 3.0:")
    print(result1.qasm_code)
    print()
    
    # Example 2: Parameterized Rotation Circuit
    print("=" * 80)
    print("Example 2: Parameterized Rotations with Inverse Gates")
    print("-" * 80)
    source2 = '''
from qiskit import QuantumCircuit
import numpy as np

def get_circuit():
    qc = QuantumCircuit(2)
    qc.rx(np.pi/2, 0)
    qc.ry(np.pi/4, 1)
    qc.cx(0, 1)
    qc.sdg(0)  # Inverse S
    qc.tdg(1)  # Inverse T
    return qc
'''
    
    result2 = converter.convert(source2)
    
    print("Generated OpenQASM 3.0:")
    print(result2.qasm_code)
    print()
    
    # Example 3: Multi-qubit Gates
    print("=" * 80)
    print("Example 3: Multi-Qubit Gates (Toffoli, CZ, SWAP)")
    print("-" * 80)
    source3 = '''
from qiskit import QuantumCircuit

def get_circuit():
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cz(0, 1)
    qc.swap(1, 2)
    qc.ccx(0, 1, 2)  # Toffoli
    return qc
'''
    
    result3 = converter.convert(source3)
    
    print("Generated OpenQASM 3.0:")
    print(result3.qasm_code)
    print()
    
    print("=" * 80)
    print("Conversion Statistics for Example 3:")
    print(f"  Qubits: {result3.stats.n_qubits}")
    print(f"  Depth: {result3.stats.depth}")
    print(f"  Gate Counts: {result3.stats.gate_counts}")
    print("=" * 80)


if __name__ == "__main__":
    main()
