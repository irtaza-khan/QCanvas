"""
Integration Tests for PennyLane Iteration II Features

Tests the PennyLane converter for Iteration II gates including:
- Controlled gates (CY, CH, CRX, CRY, CRZ, CP)
- Three-qubit gates (CSWAP, CCZ)
- Global phase gate

Author: QCanvas Team
Date: 2025-11-18
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from quantum_converters.converters.pennylane_to_qasm import PennyLaneToQASM3Converter


class TestPennyLaneIterationII:
    """Test PennyLane converter with Iteration II gates"""
    
    def test_controlled_y_gate(self):
        """Test CY (Controlled-Y) gate"""
        source = '''
import pennylane as qml

dev = qml.device('default.qubit', wires=2)

@qml.qnode(dev)
def circuit():
    qml.CY(wires=[0, 1])
    return qml.state()

def get_circuit():
    return circuit
'''
        converter = PennyLaneToQASM3Converter()
        result = converter.convert(source)
        
        qasm = result.qasm_code
        assert "cy q[0], q[1];" in qasm
        
    def test_controlled_hadamard_gate(self):
        """Test CH (Controlled-Hadamard) gate"""
        source = '''
import pennylane as qml

dev = qml.device('default.qubit', wires=2)

@qml.qnode(dev)
def circuit():
    qml.ControlledHadamard(wires=[0, 1])
    return qml.state()

def get_circuit():
    return circuit
'''
        converter = PennyLaneToQASM3Converter()
        result = converter.convert(source)
        
        qasm = result.qasm_code
        assert "ch q[0], q[1];" in qasm
        
    def test_controlled_rotation_gates(self):
        """Test controlled rotation gates (CRX, CRY, CRZ)"""
        source = '''
import pennylane as qml
import numpy as np

dev = qml.device('default.qubit', wires=2)

@qml.qnode(dev)
def circuit():
    qml.CRX(np.pi/3, wires=[0, 1])
    qml.CRY(np.pi/4, wires=[0, 1])
    qml.CRZ(np.pi/6, wires=[0, 1])
    return qml.state()

def get_circuit():
    return circuit
'''
        converter = PennyLaneToQASM3Converter()
        result = converter.convert(source)
        
        qasm = result.qasm_code
        assert "crx(" in qasm
        assert "cry(" in qasm
        assert "crz(" in qasm
        
    def test_controlled_phase_shift(self):
        """Test CP (Controlled-PhaseShift) gate"""
        source = '''
import pennylane as qml
import numpy as np

dev = qml.device('default.qubit', wires=2)

@qml.qnode(dev)
def circuit():
    qml.ControlledPhaseShift(np.pi/8, wires=[0, 1])
    return qml.state()

def get_circuit():
    return circuit
'''
        converter = PennyLaneToQASM3Converter()
        result = converter.convert(source)
        
        qasm = result.qasm_code
        assert "cp(" in qasm
        
    def test_cswap_gate(self):
        """Test CSWAP (Fredkin) gate"""
        source = '''
import pennylane as qml

dev = qml.device('default.qubit', wires=3)

@qml.qnode(dev)
def circuit():
    qml.CSWAP(wires=[0, 1, 2])
    return qml.state()

def get_circuit():
    return circuit
'''
        converter = PennyLaneToQASM3Converter()
        result = converter.convert(source)
        
        qasm = result.qasm_code
        assert "cswap q[0], q[1], q[2];" in qasm
        
    def test_ccz_gate(self):
        """Test CCZ (Double-Controlled-Z) gate"""
        source = '''
import pennylane as qml

dev = qml.device('default.qubit', wires=3)

@qml.qnode(dev)
def circuit():
    qml.CCZ(wires=[0, 1, 2])
    return qml.state()

def get_circuit():
    return circuit
'''
        converter = PennyLaneToQASM3Converter()
        result = converter.convert(source)
        
        qasm = result.qasm_code
        assert "ccz q[0], q[1], q[2];" in qasm
        
    def test_global_phase_gate(self):
        """Test GlobalPhase gate"""
        source = '''
import pennylane as qml
import numpy as np

dev = qml.device('default.qubit', wires=1)

@qml.qnode(dev)
def circuit():
    qml.GlobalPhase(np.pi/4, wires=0)
    return qml.state()

def get_circuit():
    return circuit
'''
        converter = PennyLaneToQASM3Converter()
        result = converter.convert(source)
        
        qasm = result.qasm_code
        assert "gphase(" in qasm
        
    def test_combined_iteration_ii_gates(self):
        """Test multiple Iteration II gates in one circuit"""
        source = '''
import pennylane as qml
import numpy as np

dev = qml.device('default.qubit', wires=4)

@qml.qnode(dev)
def circuit():
    # Controlled gates
    qml.CY(wires=[0, 1])
    qml.ControlledHadamard(wires=[1, 2])
    qml.CRX(np.pi/3, wires=[0, 1])
    
    # Three-qubit gates
    qml.CSWAP(wires=[0, 1, 2])
    qml.CCZ(wires=[1, 2, 3])
    
    # Global phase
    qml.GlobalPhase(np.pi/8, wires=0)
    
    return qml.state()

def get_circuit():
    return circuit
'''
        converter = PennyLaneToQASM3Converter()
        result = converter.convert(source)
        
        qasm = result.qasm_code
        # Check all gates are present
        assert "cy q[0], q[1];" in qasm
        assert "ch q[1], q[2];" in qasm
        assert "crx(" in qasm
        assert "cswap q[0], q[1], q[2];" in qasm
        assert "ccz q[1], q[2], q[3];" in qasm
        assert "gphase(" in qasm
        
        # Check statistics
        assert result.stats is not None
        assert result.stats.n_qubits == 4


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

