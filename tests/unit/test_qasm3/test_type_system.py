#!/usr/bin/env python3
"""Unit tests for OpenQASM 3.0 type system and semantic analysis."""

import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from quantum_converters.qasm3.parser import QASMParser
from quantum_converters.qasm3.type_system import SemanticAnalyzer


class TestOpenQASM3TypeSystem(unittest.TestCase):
    """Test OpenQASM 3.0 type system and semantic analysis."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = QASMParser()
        self.analyzer = SemanticAnalyzer()
    
    def test_type_checking(self):
        """Test basic type checking."""
        source = '''OPENQASM 3.0;
int x = 42;
float y = 3.14;
bool flag = true;
qubit q;
bit c;'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertTrue(success)
        self.assertEqual(len(self.analyzer.get_errors()), 0)
    
    def test_array_types(self):
        """Test array type checking."""
        source = '''OPENQASM 3.0;
qubit[5] q;
bit[3] c;
int[10] arr;
float val = arr[0];'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertTrue(success)
        self.assertEqual(len(self.analyzer.get_errors()), 0)
    
    def test_control_flow_types(self):
        """Test control flow type checking."""
        source = '''OPENQASM 3.0;
qubit q;
bit c;
if (c) {
    h q;
}
for (int i in range(5)) {
    h q;
}'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertTrue(success)
        self.assertEqual(len(self.analyzer.get_errors()), 0)
    
    def test_gate_type_checking(self):
        """Test gate call type checking."""
        source = '''OPENQASM 3.0;
qubit[2] q;
h q[0];
cx q[0], q[1];
rx(3.14) q[0];'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertTrue(success)
        self.assertEqual(len(self.analyzer.get_errors()), 0)
    
    def test_type_errors(self):
        """Test type error detection."""
        # Wrong type assignment
        source = '''OPENQASM 3.0;
int x = true;'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertFalse(success)
        errors = self.analyzer.get_errors()
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("Cannot initialize variable" in str(error) for error in errors))
    
    def test_array_errors(self):
        """Test array type errors."""
        # Array access on non-array
        source = '''OPENQASM 3.0;
int x = 5;
int y = x[0];'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertFalse(success)
        errors = self.analyzer.get_errors()
        self.assertTrue(any("Cannot index non-array" in str(error) for error in errors))
    
    def test_undefined_variables(self):
        """Test undefined variable detection."""
        source = '''OPENQASM 3.0;
int x = undefined_var;'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertFalse(success)
        errors = self.analyzer.get_errors()
        self.assertTrue(any("Undefined symbol" in str(error) for error in errors))
    
    def test_const_reassignment(self):
        """Test const variable reassignment error."""
        source = '''OPENQASM 3.0;
const int x = 42;
x = 10;'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertFalse(success)
        errors = self.analyzer.get_errors()
        self.assertTrue(any("Cannot assign to const" in str(error) for error in errors))
    
    def test_scope_management(self):
        """Test variable scope management."""
        source = '''OPENQASM 3.0;
int x = 5;
if (true) {
    int y = x + 1;  // Should access outer x
    int x = 10;     // Should shadow outer x
}
// y should not be accessible here'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertTrue(success)
        self.assertEqual(len(self.analyzer.get_errors()), 0)


if __name__ == '__main__':
    unittest.main()
