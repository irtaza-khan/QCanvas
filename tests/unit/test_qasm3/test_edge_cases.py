#!/usr/bin/env python3
"""Unit tests for OpenQASM 3.0 edge cases and tricky scenarios."""

import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from quantum_converters.qasm3.parser import QASMParser
from quantum_converters.qasm3.type_system import SemanticAnalyzer


class TestOpenQASM3EdgeCases(unittest.TestCase):
    """Test OpenQASM 3.0 edge cases and tricky scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = QASMParser()
        self.analyzer = SemanticAnalyzer()
    
    def test_nested_expressions(self):
        """Test deeply nested expressions."""
        source = '''OPENQASM 3.0;
int x = (((1 + 2) * 3) - 4) / 5;
bool flag = ((x > 0) && (x < 10)) || ((x == 5) && (x != 3));'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertTrue(success)
        self.assertEqual(len(self.analyzer.get_errors()), 0)
    
    def test_complex_gate_definitions(self):
        """Test complex gate definitions with multiple parameters."""
        source = '''OPENQASM 3.0;
gate u3(theta, phi, lambda) q {
    // Complex gate implementation would go here
}
gate cphase(angle) a, b {
    // Controlled phase gate
}'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertTrue(success)
        
        # Check gate definitions
        gate1 = ast.statements[0]
        self.assertEqual(len(gate1.parameters), 3)
        self.assertEqual(len(gate1.qubits), 1)
        
        gate2 = ast.statements[1]
        self.assertEqual(len(gate2.parameters), 1)
        self.assertEqual(len(gate2.qubits), 2)
    
    def test_const_expressions(self):
        """Test constant expressions and compile-time evaluation."""
        source = '''OPENQASM 3.0;
const int x = 5;
const int y = x * 2;
const float pi = 3.14159;
const float area = pi * x * x;'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertTrue(success)
        self.assertEqual(len(self.analyzer.get_errors()), 0)
    
    def test_control_modifiers_with_parameters(self):
        """Test control modifiers with parameters."""
        source = '''OPENQASM 3.0;
qubit[3] q;
ctrl(2) @ x q[0], q[1], q[2];
pow(3) @ h q[0];'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertTrue(success)
        self.assertEqual(len(self.analyzer.get_errors()), 0)
    
    def test_for_loops_with_ranges(self):
        """Test for loops with different range expressions."""
        source = '''OPENQASM 3.0;
qubit[5] q;
for (int i in range(5)) {
    h q[i];
}
for (int j in range(2, 5)) {
    x q[j];
}
for (int k in range(0, 5, 2)) {
    y q[k];
}'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertTrue(success)
        self.assertEqual(len(self.analyzer.get_errors()), 0)
    
    def test_array_slicing(self):
        """Test array slicing operations."""
        source = '''OPENQASM 3.0;
qubit[10] q;
bit[10] c;
for (int i in range(5)) {
    h q[i];
    measure q[i] -> c[i];
}'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertTrue(success)
        self.assertEqual(len(self.analyzer.get_errors()), 0)
    
    def test_unicode_and_special_characters(self):
        """Test handling of special characters in strings and comments."""
        source = '''OPENQASM 3.0;
// This is a comment with special chars: àáâãäåæçèéêë
qubit q;
h q;  // Another comment with symbols: ∑∏∫∂∇'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertTrue(success)
        self.assertEqual(len(self.analyzer.get_errors()), 0)
    
    def test_long_identifiers(self):
        """Test long identifier names."""
        source = '''OPENQASM 3.0;
qubit very_long_quantum_register_name;
bit another_very_long_classical_register_name;
h very_long_quantum_register_name;'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertTrue(success)
        self.assertEqual(len(self.analyzer.get_errors()), 0)
    
    def test_assignment_operators(self):
        """Test assignment operators."""
        source = '''OPENQASM 3.0;
int x = 5;
x += 3;
x -= 2;
x *= 4;
x /= 2;'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertTrue(success)
        self.assertEqual(len(self.analyzer.get_errors()), 0)
    
    def test_error_recovery(self):
        """Test parser error recovery."""
        source = '''OPENQASM 3.0;
int x = 5;
// Missing semicolon on next line
int y = 10
int z = 15;'''
        
        # This should raise a parse error
        with self.assertRaises(Exception):
            self.parser.parse(source)
    
    def test_nested_control_flow(self):
        """Test nested control flow structures."""
        source = '''OPENQASM 3.0;
qubit[3] q;
bit[3] c;
for (int i in range(3)) {
    if (i == 0) {
        h q[i];
    } else if (i == 1) {
        x q[i];
    } else {
        y q[i];
    }
    measure q[i] -> c[i];
}'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertTrue(success)
        self.assertEqual(len(self.analyzer.get_errors()), 0)


if __name__ == '__main__':
    unittest.main()
