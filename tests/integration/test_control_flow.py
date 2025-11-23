"""
Integration Tests for Control Flow (For Loops and If Statements)

Tests the for loop and if statement support in Qiskit, Cirq, and PennyLane converters.

Author: QCanvas Team
Date: 2025-11-18
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Try to import converters, skip tests if dependencies are missing
try:
    from quantum_converters.converters.qiskit_to_qasm import QiskitToQASM3Converter
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    QiskitToQASM3Converter = None

try:
    from quantum_converters.converters.cirq_to_qasm import CirqToQASM3Converter
    CIRQ_AVAILABLE = True
except ImportError:
    CIRQ_AVAILABLE = False
    CirqToQASM3Converter = None

try:
    from quantum_converters.converters.pennylane_to_qasm import PennyLaneToQASM3Converter
    PENNYLANE_AVAILABLE = True
except ImportError:
    PENNYLANE_AVAILABLE = False
    PennyLaneToQASM3Converter = None


@pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not available")
class TestControlFlowQiskit:
    """Test for loops and if statements in Qiskit converter"""
    
    def test_for_loop_with_hadamard(self):
        """Test for loop applying Hadamard gates"""
        source = '''from qiskit import QuantumCircuit

n_bits = 8
qc = QuantumCircuit(n_bits, n_bits)

# Put each qubit in superposition
for i in range(n_bits):
    qc.h(i)

# Measure all qubits
qc.measure(range(n_bits), range(n_bits))
'''
        converter = QiskitToQASM3Converter()
        result = converter.convert(source)
        
        assert result is not None
        assert result.qasm_code is not None
        
        qasm = result.qasm_code
        assert "OPENQASM 3.0;" in qasm
        assert "for" in qasm
        assert "uint i" in qasm or "i in" in qasm
        assert "[0:7]" in qasm  # range(8) -> [0:7]
        assert "h q[i];" in qasm or "h q[0];" in qasm  # Gate inside loop
    
    def test_for_loop_with_measurements(self):
        """Test for loop with measurements inside"""
        source = '''from qiskit import QuantumCircuit

n_bits = 8
qc = QuantumCircuit(n_bits, n_bits)

# Put each qubit in superposition
for i in range(n_bits):
    qc.h(i)

# Measure each qubit in a loop
for i in range(n_bits):
    qc.measure(i, i)
'''
        converter = QiskitToQASM3Converter()
        result = converter.convert(source)
        
        assert result is not None
        qasm = result.qasm_code
        assert "for" in qasm
        assert "measure" in qasm
    
    def test_if_statement(self):
        """Test if statement"""
        source = '''from qiskit import QuantumCircuit

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.measure(0, 0)
if True:
    qc.x(1)
'''
        converter = QiskitToQASM3Converter()
        result = converter.convert(source)
        
        assert result is not None
        qasm = result.qasm_code
        assert "if" in qasm
        assert "x q[1];" in qasm
    
    def test_nested_for_loops(self):
        """Test nested for loops"""
        source = '''from qiskit import QuantumCircuit

qc = QuantumCircuit(4, 4)
for i in range(2):
    for j in range(2):
        qc.cx(i, j + 2)
'''
        converter = QiskitToQASM3Converter()
        result = converter.convert(source)
        
        assert result is not None
        qasm = result.qasm_code
        assert "for" in qasm
        assert "cx" in qasm
    
    def test_for_loop_with_range_start_end(self):
        """Test for loop with explicit range start and end"""
        source = '''from qiskit import QuantumCircuit

qc = QuantumCircuit(5, 5)
for i in range(1, 4):
    qc.h(i)
'''
        converter = QiskitToQASM3Converter()
        result = converter.convert(source)
        
        assert result is not None
        qasm = result.qasm_code
        assert "for" in qasm
        assert "[1:3]" in qasm  # range(1, 4) -> [1:3]


@pytest.mark.skipif(not CIRQ_AVAILABLE, reason="Cirq not available")
class TestControlFlowCirq:
    """Test for loops and if statements in Cirq converter"""
    
    def test_for_loop_with_hadamard(self):
        """Test for loop applying Hadamard gates in Cirq"""
        source = '''import cirq

n_bits = 8
qubits = cirq.LineQubit.range(n_bits)
circuit = cirq.Circuit()

# Put each qubit in superposition
for i in range(n_bits):
    circuit.append(cirq.H(qubits[i]))
'''
        converter = CirqToQASM3Converter()
        result = converter.convert(source)
        
        assert result is not None
        assert result.qasm_code is not None
        
        qasm = result.qasm_code
        assert "OPENQASM 3.0;" in qasm
        # Note: Cirq parser may unroll loops or preserve them depending on implementation
        # For now, just check that conversion succeeds and produces valid QASM
        assert "h q[" in qasm or "for" in qasm
    
    def test_if_statement_cirq(self):
        """Test if statement in Cirq"""
        source = '''import cirq

qubits = cirq.LineQubit.range(2)
circuit = cirq.Circuit()
circuit.append(cirq.H(qubits[0]))
if True:
    circuit.append(cirq.X(qubits[1]))
'''
        converter = CirqToQASM3Converter()
        result = converter.convert(source)
        
        assert result is not None
        qasm = result.qasm_code
        # Note: Cirq parser may unroll if statements or preserve them depending on implementation
        # For now, just check that conversion succeeds and produces valid QASM
        assert "x q[1];" in qasm or "if" in qasm


@pytest.mark.skipif(not PENNYLANE_AVAILABLE, reason="PennyLane not available")
class TestControlFlowPennyLane:
    """Test for loops and if statements in PennyLane converter"""
    
    def test_for_loop_with_hadamard(self):
        """Test for loop applying Hadamard gates in PennyLane"""
        source = '''import pennylane as qml

dev = qml.device('default.qubit', wires=8)

@qml.qnode(dev)
def circuit():
    for i in range(8):
        qml.Hadamard(wires=i)
    return qml.state()
'''
        converter = PennyLaneToQASM3Converter()
        result = converter.convert(source)
        
        assert result is not None
        assert result.qasm_code is not None
        
        qasm = result.qasm_code
        assert "OPENQASM 3.0;" in qasm
        assert "for" in qasm
    
    def test_if_statement_pennylane(self):
        """Test if statement in PennyLane"""
        source = '''import pennylane as qml

dev = qml.device('default.qubit', wires=2)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    if True:
        qml.PauliX(wires=1)
    return qml.state()
'''
        converter = PennyLaneToQASM3Converter()
        result = converter.convert(source)
        
        assert result is not None
        qasm = result.qasm_code
        assert "if" in qasm


@pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not available")
class TestControlFlowEdgeCases:
    """Test edge cases for control flow"""
    
    def test_empty_for_loop(self):
        """Test empty for loop"""
        source = '''from qiskit import QuantumCircuit

qc = QuantumCircuit(2, 2)
for i in range(0):
    qc.h(i)
'''
        converter = QiskitToQASM3Converter()
        result = converter.convert(source)
        
        assert result is not None
        qasm = result.qasm_code
        assert "for" in qasm or "OPENQASM 3.0;" in qasm
    
    def test_if_else_statement(self):
        """Test if-else statement"""
        source = '''from qiskit import QuantumCircuit

qc = QuantumCircuit(2, 2)
qc.measure(0, 0)
if True:
    qc.x(1)
else:
    qc.y(1)
'''
        converter = QiskitToQASM3Converter()
        result = converter.convert(source)
        
        assert result is not None
        qasm = result.qasm_code
        assert "if" in qasm
        assert "else" in qasm
    
    def test_for_loop_with_parameterized_gates(self):
        """Test for loop with parameterized gates"""
        source = '''from qiskit import QuantumCircuit
import numpy as np

qc = QuantumCircuit(4, 4)
for i in range(4):
    qc.ry(np.pi / 4, i)
'''
        converter = QiskitToQASM3Converter()
        result = converter.convert(source)
        
        assert result is not None
        qasm = result.qasm_code
        assert "for" in qasm
        assert "ry" in qasm


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

