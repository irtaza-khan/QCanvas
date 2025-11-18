"""
Integration Tests for Iteration II Gate Modifiers

Tests gate modifier support including:
- negctrl@ (negative control)
- ctrl(n)@ (multi-control)
- pow(k)@ (power modifier)

Author: QCanvas Team
Date: 2025-11-18
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from quantum_converters.base.qasm3_builder import QASM3Builder
from quantum_converters.base.qasm3_gates import GateModifier


class TestGateModifiers:
    """Test Iteration II gate modifiers"""
    
    def test_negctrl_modifier_single(self):
        """Test negctrl@ modifier for single negative control"""
        builder = QASM3Builder()
        builder.initialize_header()
        builder.declare_qubit_register("q", 3)
        
        # Negative control: gate triggers when control is |0>
        builder.apply_gate("x", ["q[1]", "q[2]"], modifiers={'negctrl': 1})
        
        code = builder.get_code()
        assert "negctrl @" in code
        
    def test_negctrl_modifier_multiple(self):
        """Test negctrl(n)@ modifier for multiple negative controls"""
        builder = QASM3Builder()
        builder.initialize_header()
        builder.declare_qubit_register("q", 4)
        
        # Two negative controls
        builder.apply_gate("x", ["q[2]", "q[3]"], modifiers={'negctrl': 2})
        
        code = builder.get_code()
        assert "negctrl(2) @" in code
        
    def test_ctrl_multiple(self):
        """Test ctrl(n)@ modifier for multiple controls"""
        builder = QASM3Builder()
        builder.initialize_header()
        builder.declare_qubit_register("q", 4)
        
        # Three controls (for C3X gate)
        builder.apply_gate("x", ["q[0]", "q[1]", "q[2]", "q[3]"], modifiers={'ctrl': 3})
        
        code = builder.get_code()
        assert "ctrl(3) @" in code
        
    def test_pow_modifier(self):
        """Test pow(k)@ modifier"""
        builder = QASM3Builder()
        builder.initialize_header()
        builder.declare_qubit_register("q", 1)
        
        # Square root of X gate (pow(0.5))
        builder.apply_gate("x", ["q[0]"], modifiers={'pow': 0.5})
        
        code = builder.get_code()
        assert "pow(0.5) @" in code
        
    def test_combined_modifiers(self):
        """Test combining multiple modifiers"""
        builder = QASM3Builder()
        builder.initialize_header()
        builder.declare_qubit_register("q", 3)
        
        # Inverse controlled gate
        builder.apply_gate("x", ["q[0]", "q[1]"], modifiers={'inv': True, 'ctrl': 1})
        
        code = builder.get_code()
        assert "inv @ ctrl @" in code or "ctrl @ inv @" in code  # Order may vary
        
    def test_gate_modifier_dataclass(self):
        """Test GateModifier dataclass"""
        # Test with negctrl
        mod1 = GateModifier(negctrl_qubits=1)
        assert "negctrl @" in mod1.to_string()
        
        # Test with multiple negctrl
        mod2 = GateModifier(negctrl_qubits=2)
        assert "negctrl(2) @" in mod2.to_string()
        
        # Test with power
        mod3 = GateModifier(power=0.25)
        assert "pow(0.25) @" in mod3.to_string()
        
        # Test combined
        mod4 = GateModifier(inverse=True, ctrl_qubits=2, power=2)
        result = mod4.to_string()
        assert "inv @" in result
        assert "ctrl(2) @" in result
        assert "pow(2) @" in result
        
    def test_mixed_control_types(self):
        """Test combining ctrl and negctrl"""
        builder = QASM3Builder()
        builder.initialize_header()
        builder.declare_qubit_register("q", 4)
        
        # Both positive and negative controls
        builder.apply_gate("x", ["q[2]", "q[3]"], modifiers={'ctrl': 1, 'negctrl': 1})
        
        code = builder.get_code()
        assert "ctrl @" in code
        assert "negctrl @" in code


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

