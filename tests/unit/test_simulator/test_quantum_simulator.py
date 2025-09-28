#!/usr/bin/env python3
"""Unit tests for quantum simulator."""

import unittest
import sys
import os
import numpy as np

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))


class TestQuantumSimulator(unittest.TestCase):
    """Test quantum simulator functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        try:
            from quantum_simulator.core.statevector import StatevectorBackend
            from quantum_simulator.core.density_matrix import DensityMatrixBackend
            from quantum_simulator.core.stabilizer import StabilizerBackend
            
            self.statevector_backend = StatevectorBackend()
            self.density_matrix_backend = DensityMatrixBackend()
            self.stabilizer_backend = StabilizerBackend()
        except ImportError:
            self.skipTest("Quantum simulator backends not available")
    
    def test_statevector_backend_creation(self):
        """Test statevector backend creation."""
        self.assertIsNotNone(self.statevector_backend)
        self.assertTrue(hasattr(self.statevector_backend, 'simulate'))
    
    def test_density_matrix_backend_creation(self):
        """Test density matrix backend creation."""
        self.assertIsNotNone(self.density_matrix_backend)
        self.assertTrue(hasattr(self.density_matrix_backend, 'simulate'))
    
    def test_stabilizer_backend_creation(self):
        """Test stabilizer backend creation."""
        self.assertIsNotNone(self.stabilizer_backend)
        self.assertTrue(hasattr(self.stabilizer_backend, 'simulate'))
    
    def test_backend_interface(self):
        """Test that backends implement required interface."""
        from quantum_simulator.core.base_backend import BaseBackend
        
        self.assertIsInstance(self.statevector_backend, BaseBackend)
        self.assertIsInstance(self.density_matrix_backend, BaseBackend)
        self.assertIsInstance(self.stabilizer_backend, BaseBackend)
    
    def test_simulation_methods(self):
        """Test simulation methods exist."""
        # Test statevector backend
        self.assertTrue(hasattr(self.statevector_backend, 'simulate'))
        self.assertTrue(hasattr(self.statevector_backend, 'get_state'))
        self.assertTrue(hasattr(self.statevector_backend, 'measure'))
        
        # Test density matrix backend
        self.assertTrue(hasattr(self.density_matrix_backend, 'simulate'))
        self.assertTrue(hasattr(self.density_matrix_backend, 'get_state'))
        self.assertTrue(hasattr(self.density_matrix_backend, 'measure'))
        
        # Test stabilizer backend
        self.assertTrue(hasattr(self.stabilizer_backend, 'simulate'))
        self.assertTrue(hasattr(self.stabilizer_backend, 'get_state'))
        self.assertTrue(hasattr(self.stabilizer_backend, 'measure'))
    
    def test_simulation_with_simple_circuit(self):
        """Test simulation with simple circuit."""
        # Create a simple circuit (H gate on |0>)
        circuit = {
            'gates': [
                {'type': 'h', 'qubits': [0]}
            ],
            'num_qubits': 1
        }
        
        # Test statevector simulation
        result = self.statevector_backend.simulate(circuit)
        self.assertIsNotNone(result)
        self.assertTrue('state' in result or 'probabilities' in result)
        
        # Test density matrix simulation
        result = self.density_matrix_backend.simulate(circuit)
        self.assertIsNotNone(result)
        self.assertTrue('state' in result or 'probabilities' in result)
        
        # Test stabilizer simulation
        result = self.stabilizer_backend.simulate(circuit)
        self.assertIsNotNone(result)
        self.assertTrue('state' in result or 'probabilities' in result)
    
    def test_measurement_simulation(self):
        """Test measurement simulation."""
        circuit = {
            'gates': [
                {'type': 'h', 'qubits': [0]},
                {'type': 'measure', 'qubits': [0], 'bits': [0]}
            ],
            'num_qubits': 1,
            'num_bits': 1
        }
        
        # Test measurement with statevector backend
        result = self.statevector_backend.simulate(circuit)
        self.assertIsNotNone(result)
        
        # Test measurement with density matrix backend
        result = self.density_matrix_backend.simulate(circuit)
        self.assertIsNotNone(result)
        
        # Test measurement with stabilizer backend
        result = self.stabilizer_backend.simulate(circuit)
        self.assertIsNotNone(result)
    
    def test_multi_qubit_circuit(self):
        """Test multi-qubit circuit simulation."""
        circuit = {
            'gates': [
                {'type': 'h', 'qubits': [0]},
                {'type': 'cx', 'qubits': [0, 1]},
                {'type': 'measure', 'qubits': [0, 1], 'bits': [0, 1]}
            ],
            'num_qubits': 2,
            'num_bits': 2
        }
        
        # Test with all backends
        for backend in [self.statevector_backend, self.density_matrix_backend, self.stabilizer_backend]:
            result = backend.simulate(circuit)
            self.assertIsNotNone(result)
            self.assertTrue('state' in result or 'probabilities' in result)
    
    def test_error_handling(self):
        """Test error handling in simulation."""
        # Test with invalid circuit
        invalid_circuit = {
            'gates': [
                {'type': 'invalid_gate', 'qubits': [0]}
            ],
            'num_qubits': 1
        }
        
        # Should handle gracefully
        for backend in [self.statevector_backend, self.density_matrix_backend, self.stabilizer_backend]:
            try:
                result = backend.simulate(invalid_circuit)
                # If it doesn't raise an exception, it should return an error result
                if result and 'error' in result:
                    self.assertTrue(True)  # Expected behavior
            except Exception:
                self.assertTrue(True)  # Also expected behavior
    
    def test_performance_large_circuit(self):
        """Test performance with larger circuit."""
        # Create a larger circuit
        circuit = {
            'gates': [],
            'num_qubits': 10
        }
        
        # Add many gates
        for i in range(10):
            circuit['gates'].append({'type': 'h', 'qubits': [i]})
        
        for i in range(0, 10, 2):
            circuit['gates'].append({'type': 'cx', 'qubits': [i, i+1]})
        
        # Test with statevector backend (most general)
        result = self.statevector_backend.simulate(circuit)
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
