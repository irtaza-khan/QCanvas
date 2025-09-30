"""
Demo Script: PennyLane to OpenQASM 3.0 Conversion

This script demonstrates the updated PennyLane converter using QASM3Builder.
It creates sample circuits and shows the generated OpenQASM 3.0 code.

Author: QCanvas Team
Date: 2025-09-30
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from quantum_converters.converters.pennylane_to_qasm import PennyLaneToQASM3Converter


def main():
    """Run the demo"""
    print("=" * 80)
    print("PennyLane to OpenQASM 3.0 Conversion Demo")
    print("Using QASM3Builder Integration")
    print("=" * 80)
    print()
    
    # Example 1: Simple Quantum Teleportation Circuit
    print("Example 1: Simple Quantum Teleportation Setup")
    print("-" * 80)
    source1 = '''
import pennylane as qml

dev = qml.device('default.qubit', wires=3)

@qml.qnode(dev)
def circuit():
    # Create entangled pair
    qml.Hadamard(wires=1)
    qml.CNOT(wires=[1, 2])
    
    # Bell measurement
    qml.CNOT(wires=[0, 1])
    qml.Hadamard(wires=0)
    
    return qml.state()

def get_circuit():
    return circuit
'''
    
    converter = PennyLaneToQASM3Converter()
    result1 = converter.convert(source1)
    
    print("Generated OpenQASM 3.0:")
    print(result1.qasm_code)
    print()
    
    # Example 2: Parameterized Rotation Circuit
    print("=" * 80)
    print("Example 2: Parameterized Rotations")
    print("-" * 80)
    source2 = '''
import pennylane as qml
import numpy as np

dev = qml.device('default.qubit', wires=2)

@qml.qnode(dev)
def circuit():
    qml.RX(np.pi/2, wires=0)
    qml.RY(np.pi/4, wires=1)
    qml.CNOT(wires=[0, 1])
    qml.RZ(np.pi, wires=0)
    return qml.state()

def get_circuit():
    return circuit
'''
    
    result2 = converter.convert(source2)
    
    print("Generated OpenQASM 3.0:")
    print(result2.qasm_code)
    print()
    
    # Example 3: Multi-Qubit Gates
    print("=" * 80)
    print("Example 3: Multi-Qubit Gates (Toffoli, CZ, SWAP)")
    print("-" * 80)
    source3 = '''
import pennylane as qml

dev = qml.device('default.qubit', wires=3)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    qml.CZ(wires=[0, 1])
    qml.SWAP(wires=[1, 2])
    qml.Toffoli(wires=[0, 1, 2])
    return qml.state()

def get_circuit():
    return circuit
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
