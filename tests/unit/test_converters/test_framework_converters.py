#!/usr/bin/env python3
"""Unit tests for framework converters (Qiskit, Cirq, PennyLane)."""

import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))


class TestFrameworkConverters(unittest.TestCase):
    """Test framework converter functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Note: These tests will be skipped if the frameworks are not installed
        self.skip_if_framework_missing()
    
    def skip_if_framework_missing(self):
        """Skip test if required frameworks are not installed."""
        try:
            import qiskit
            import cirq
            import pennylane
        except ImportError:
            self.skipTest("Required quantum frameworks not installed")
    
    def test_qiskit_converter_import(self):
        """Test Qiskit converter can be imported."""
        try:
            from quantum_converters.converters.qiskit_to_qasm import QiskitToQASMConverter
            converter = QiskitToQASMConverter()
            self.assertIsNotNone(converter)
        except ImportError:
            self.skipTest("Qiskit converter not available")
    
    def test_cirq_converter_import(self):
        """Test Cirq converter can be imported."""
        try:
            from quantum_converters.converters.cirq_to_qasm import CirqToQASMConverter
            converter = CirqToQASMConverter()
            self.assertIsNotNone(converter)
        except ImportError:
            self.skipTest("Cirq converter not available")
    
    def test_pennylane_converter_import(self):
        """Test PennyLane converter can be imported."""
        try:
            from quantum_converters.converters.pennylane_to_qasm import PennyLaneToQASMConverter
            converter = PennyLaneToQASMConverter()
            self.assertIsNotNone(converter)
        except ImportError:
            self.skipTest("PennyLane converter not available")
    
    def test_converter_interface(self):
        """Test that all converters implement the required interface."""
        from quantum_converters.base.abstract_converter import AbstractConverter
        
        # Test that converters can be instantiated
        try:
            from quantum_converters.converters.qiskit_to_qasm import QiskitToQASMConverter
            qiskit_converter = QiskitToQASMConverter()
            self.assertIsInstance(qiskit_converter, AbstractConverter)
        except ImportError:
            pass
        
        try:
            from quantum_converters.converters.cirq_to_qasm import CirqToQASMConverter
            cirq_converter = CirqToQASMConverter()
            self.assertIsInstance(cirq_converter, AbstractConverter)
        except ImportError:
            pass
        
        try:
            from quantum_converters.converters.pennylane_to_qasm import PennyLaneToQASMConverter
            pennylane_converter = PennyLaneToQASMConverter()
            self.assertIsInstance(pennylane_converter, AbstractConverter)
        except ImportError:
            pass
    
    def test_converter_methods(self):
        """Test that converters have required methods."""
        try:
            from quantum_converters.converters.qiskit_to_qasm import QiskitToQASMConverter
            converter = QiskitToQASMConverter()
            
            # Check required methods exist
            self.assertTrue(hasattr(converter, 'convert'))
            self.assertTrue(hasattr(converter, 'validate'))
            self.assertTrue(hasattr(converter, 'get_supported_gates'))
        except ImportError:
            self.skipTest("Qiskit converter not available")
    
    def test_converter_error_handling(self):
        """Test converter error handling."""
        try:
            from quantum_converters.converters.qiskit_to_qasm import QiskitToQASMConverter
            converter = QiskitToQASMConverter()
            
            # Test with invalid input
            result = converter.convert(None)
            self.assertFalse(result.success)
            self.assertGreater(len(result.errors), 0)
        except ImportError:
            self.skipTest("Qiskit converter not available")
    
    def test_converter_validation(self):
        """Test converter validation."""
        try:
            from quantum_converters.converters.qiskit_to_qasm import QiskitToQASMConverter
            converter = QiskitToQASMConverter()
            
            # Test validation with valid input
            # Note: This would require actual Qiskit circuit objects
            # For now, just test that the method exists
            self.assertTrue(hasattr(converter, 'validate'))
        except ImportError:
            self.skipTest("Qiskit converter not available")


if __name__ == '__main__':
    unittest.main()
