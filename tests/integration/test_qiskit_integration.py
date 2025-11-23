"""
Integration Tests for Qiskit to OpenQASM 3.0 Converter

Tests the updated Qiskit converter with QASM3Builder integration.

Author: QCanvas Team
Date: 2025-09-30
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from quantum_converters.converters.qiskit_to_qasm import QiskitToQASM3Converter


class TestQiskitIntegration:
    """Test Qiskit converter with QASM3Builder integration"""
    
    def test_simple_circuit(self):
        """Test a simple Qiskit circuit conversion"""
        source = '''
from qiskit import QuantumCircuit

def get_circuit():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    return qc
'''
        converter = QiskitToQASM3Converter()
        result = converter.convert(source)
        
        # Check that conversion was successful
        assert result is not None
        assert result.qasm_code is not None
        
        # Check for expected QASM 3 elements
        qasm = result.qasm_code
        assert "OPENQASM 3.0;" in qasm
        assert 'include "stdgates.inc";' in qasm
        assert "qubit[2] q;" in qasm
        assert "h q[0];" in qasm
        assert "cx q[0], q[1];" in qasm
        
        # Basic circuits no longer inject mathematical constants automatically
        
    def test_parameterized_gates(self):
        """Test Qiskit circuit with parameterized gates"""
        source = '''
from qiskit import QuantumCircuit
import numpy as np

def get_circuit():
    qc = QuantumCircuit(1)
    qc.rx(np.pi/2, 0)
    qc.ry(np.pi/4, 0)
    qc.rz(np.pi, 0)
    return qc
'''
        converter = QiskitToQASM3Converter()
        result = converter.convert(source)
        
        qasm = result.qasm_code
        assert "rx(pi_2) q[0];" in qasm or "rx(pi/2) q[0];" in qasm
        assert "ry(pi_4) q[0];" in qasm or "ry(pi/4) q[0];" in qasm
        assert "rz(pi) q[0];" in qasm
        
    def test_measurements(self):
        """Test Qiskit circuit with measurements"""
        source = '''
from qiskit import QuantumCircuit

def get_circuit():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc
'''
        converter = QiskitToQASM3Converter()
        result = converter.convert(source)
        
        qasm = result.qasm_code
        assert "bit[2] c;" in qasm
        assert "measure q[0] -> c[0];" in qasm
        assert "measure q[1] -> c[1];" in qasm
        
    def test_inverse_modifier(self):
        """Test inverse gate modifier"""
        source = '''
from qiskit import QuantumCircuit

def get_circuit():
    qc = QuantumCircuit(1)
    qc.sdg(0)  # Inverse S gate
    qc.tdg(0)  # Inverse T gate
    return qc
'''
        converter = QiskitToQASM3Converter()
        result = converter.convert(source)
        
        qasm = result.qasm_code
        # Should use inv@ modifier
        assert "inv @" in qasm
        assert "s q[0];" in qasm
        assert "t q[0];" in qasm
        
    def test_statistics(self):
        """Test that conversion statistics are calculated"""
        source = '''
from qiskit import QuantumCircuit

def get_circuit():
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.h(1)
    qc.h(2)
    qc.cx(0, 1)
    qc.cx(1, 2)
    return qc
'''
        converter = QiskitToQASM3Converter()
        result = converter.convert(source)
        
        # Check statistics
        assert result.stats is not None
        assert result.stats.n_qubits == 3
        assert result.stats.depth is not None
        assert result.stats.gate_counts is not None
        
    def test_reset_instruction(self):
        """Test reset instruction"""
        source = '''
from qiskit import QuantumCircuit

def get_circuit():
    qc = QuantumCircuit(1)
    qc.h(0)
    qc.reset(0)
    return qc
'''
        converter = QiskitToQASM3Converter()
        result = converter.convert(source)
        
        qasm = result.qasm_code
        assert "reset q[0];" in qasm
        
    def test_multiple_qubit_gates(self):
        """Test two-qubit and three-qubit gates"""
        source = '''
from qiskit import QuantumCircuit

def get_circuit():
    qc = QuantumCircuit(3)
    qc.cz(0, 1)
    qc.swap(0, 1)
    qc.ccx(0, 1, 2)  # Toffoli
    return qc
'''
        converter = QiskitToQASM3Converter()
        result = converter.convert(source)
        
        qasm = result.qasm_code
        assert "cz q[0], q[1];" in qasm
        assert "swap q[0], q[1];" in qasm
        assert "ccx q[0], q[1], q[2];" in qasm
        
    def test_u_gate(self):
        """Test universal U gate"""
        source = '''
from qiskit import QuantumCircuit
import numpy as np

def get_circuit():
    qc = QuantumCircuit(1)
    qc.u(np.pi/2, 0, np.pi, 0)
    return qc
'''
        converter = QiskitToQASM3Converter()
        result = converter.convert(source)
        
        qasm = result.qasm_code
        assert "u(" in qasm
        assert "q[0];" in qasm

    def test_controlled_parameterized_gates(self):
        """Test controlled parameterized gates including CU"""
        source = '''
from qiskit import QuantumCircuit
import numpy as np

def get_circuit():
    qc = QuantumCircuit(2)
    qc.cp(np.pi/4, 0, 1)
    qc.crx(np.pi/3, 0, 1)
    qc.cry(np.pi/5, 0, 1)
    qc.crz(np.pi/6, 0, 1)
    qc.cu(1.0, 0.5, 0.25, 0.1, 0, 1)
    return qc
'''
        converter = QiskitToQASM3Converter()
        result = converter.convert(source)

        qasm = result.qasm_code
        assert "cp(" in qasm
        assert "crx(" in qasm
        assert "cry(" in qasm
        assert "crz(" in qasm
        assert "cu(" in qasm


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
