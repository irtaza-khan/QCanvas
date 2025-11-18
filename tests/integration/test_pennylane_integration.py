"""
Integration Tests for PennyLane to OpenQASM 3.0 Converter

Tests the updated PennyLane converter with QASM3Builder integration.

Author: QCanvas Team
Date: 2025-09-30
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from quantum_converters.converters.pennylane_to_qasm import PennyLaneToQASM3Converter


class TestPennyLaneIntegration:
    """Test PennyLane converter with QASM3Builder integration"""
    
    def test_simple_circuit(self):
        """Test a simple PennyLane circuit conversion"""
        source = '''
import pennylane as qml

dev = qml.device('default.qubit', wires=2)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.state()

def get_circuit():
    return circuit
'''
        converter = PennyLaneToQASM3Converter()
        result = converter.convert(source)
        
        # Check that conversion was successful
        assert result is not None
        assert result.qasm_code is not None
        
        # Check for expected QASM 3 elements
        qasm = result.qasm_code
        assert "OPENQASM 3;" in qasm
        assert 'include "stdgates.inc";' in qasm
        assert "qubit[2] q;" in qasm
        assert "h q[0];" in qasm
        assert "cx q[0], q[1];" in qasm
        
        # Constants are emitted only when required by expressions
        
    def test_parameterized_gates(self):
        """Test PennyLane circuit with parameterized gates"""
        source = '''
import pennylane as qml
import numpy as np

dev = qml.device('default.qubit', wires=1)

@qml.qnode(dev)
def circuit():
    qml.RX(np.pi/2, wires=0)
    qml.RY(np.pi/4, wires=0)
    qml.RZ(np.pi, wires=0)
    return qml.state()

def get_circuit():
    return circuit
'''
        converter = PennyLaneToQASM3Converter()
        result = converter.convert(source)
        
        qasm = result.qasm_code
        # Should have rotation gates with parameters
        assert "rx(" in qasm
        assert "ry(" in qasm
        assert "rz(" in qasm
        assert "q[0];" in qasm
        
    def test_pauli_gates(self):
        """Test PennyLane Pauli gates"""
        source = '''
import pennylane as qml

dev = qml.device('default.qubit', wires=3)

@qml.qnode(dev)
def circuit():
    qml.PauliX(wires=0)
    qml.PauliY(wires=1)
    qml.PauliZ(wires=2)
    return qml.state()

def get_circuit():
    return circuit
'''
        converter = PennyLaneToQASM3Converter()
        result = converter.convert(source)
        
        qasm = result.qasm_code
        assert "x q[0];" in qasm
        assert "y q[1];" in qasm
        assert "z q[2];" in qasm
        
    def test_statistics(self):
        """Test that conversion statistics are calculated"""
        source = '''
import pennylane as qml

dev = qml.device('default.qubit', wires=3)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    qml.Hadamard(wires=1)
    qml.Hadamard(wires=2)
    qml.CNOT(wires=[0, 1])
    qml.CNOT(wires=[1, 2])
    return qml.state()

def get_circuit():
    return circuit
'''
        converter = PennyLaneToQASM3Converter()
        result = converter.convert(source)
        
        # Check statistics
        assert result.stats is not None
        assert result.stats.n_qubits == 3
        assert result.stats.depth is not None
        assert result.stats.gate_counts is not None
        
    def test_multiple_qubit_gates(self):
        """Test two-qubit and three-qubit gates"""
        source = '''
import pennylane as qml

dev = qml.device('default.qubit', wires=3)

@qml.qnode(dev)
def circuit():
    qml.CZ(wires=[0, 1])
    qml.SWAP(wires=[0, 1])
    qml.Toffoli(wires=[0, 1, 2])
    return qml.state()

def get_circuit():
    return circuit
'''
        converter = PennyLaneToQASM3Converter()
        result = converter.convert(source)
        
        qasm = result.qasm_code
        assert "cz q[0], q[1];" in qasm
        assert "swap q[0], q[1];" in qasm
        assert "ccx q[0], q[1], q[2];" in qasm
        
    def test_s_and_t_gates(self):
        """Test S and T gates"""
        source = '''
import pennylane as qml

dev = qml.device('default.qubit', wires=2)

@qml.qnode(dev)
def circuit():
    qml.S(wires=0)
    qml.T(wires=1)
    return qml.state()

def get_circuit():
    return circuit
'''
        converter = PennyLaneToQASM3Converter()
        result = converter.convert(source)
        
        qasm = result.qasm_code
        assert "s q[0];" in qasm
        assert "t q[1];" in qasm
        
    def test_phase_shift_gate(self):
        """Test PhaseShift gate"""
        source = '''
import pennylane as qml
import numpy as np

dev = qml.device('default.qubit', wires=1)

@qml.qnode(dev)
def circuit():
    qml.PhaseShift(np.pi/2, wires=0)
    return qml.state()

def get_circuit():
    return circuit
'''
        converter = PennyLaneToQASM3Converter()
        result = converter.convert(source)
        
        qasm = result.qasm_code
        assert "p(" in qasm
        assert "q[0];" in qasm


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
