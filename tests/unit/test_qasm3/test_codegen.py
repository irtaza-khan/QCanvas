#!/usr/bin/env python3
"""Unit tests for OpenQASM 3.0 code generator."""

import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from quantum_converters.qasm3.parser import QASMParser
from quantum_converters.qasm3.codegen import QASMCodeGenerator


class TestOpenQASM3CodeGen(unittest.TestCase):
    """Test OpenQASM 3.0 code generator functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = QASMParser()
        self.codegen = QASMCodeGenerator()
    
    def test_pretty_printing(self):
        """Test pretty printing."""
        source = '''OPENQASM 3.0;
qubit q;
h q;'''
        
        ast = self.parser.parse(source)
        generated = self.codegen.generate(ast)
        
        self.assertIn("OPENQASM 3.0", generated)
        self.assertIn("qubit q", generated)
        self.assertIn("h q", generated)
    
    def test_roundtrip(self):
        """Test parse -> generate roundtrip."""
        original = '''OPENQASM 3.0;
qubit[2] q;
h q[0];
cx q[0], q[1];
measure q[0] -> c;'''
        
        ast = self.parser.parse(original)
        generated = self.codegen.generate(ast)
        
        # Parse the generated code again
        ast2 = self.parser.parse(generated)
        
        # Should parse without errors
        self.assertIsNotNone(ast2)
        self.assertEqual(len(ast.statements), len(ast2.statements))
    
    def test_complex_program(self):
        """Test code generation for complex programs."""
        source = '''OPENQASM 3.0;
qubit[3] q;
bit[3] c;
int i = 0;
for (int j in range(3)) {
    h q[j];
    measure q[j] -> c[j];
}'''
        
        ast = self.parser.parse(source)
        generated = self.codegen.generate(ast)
        
        self.assertIn("OPENQASM 3.0", generated)
        self.assertIn("qubit[3] q", generated)
        self.assertIn("bit[3] c", generated)
        self.assertIn("for (int j in range(3))", generated)
        self.assertIn("h q[j]", generated)
        self.assertIn("measure q[j] -> c[j]", generated)
    
    def test_gate_definitions(self):
        """Test code generation for gate definitions."""
        source = '''OPENQASM 3.0;
gate h q { }
gate rx(angle theta) q { }
gate bell a, b {
    h a;
    cx a, b;
}'''
        
        ast = self.parser.parse(source)
        generated = self.codegen.generate(ast)
        
        self.assertIn("gate h q", generated)
        self.assertIn("gate rx(angle theta) q", generated)
        self.assertIn("gate bell a, b", generated)
        self.assertIn("h a", generated)
        self.assertIn("cx a, b", generated)
    
    def test_expressions(self):
        """Test code generation for complex expressions."""
        source = '''OPENQASM 3.0;
int x = 5;
int y = x + 1;
bool flag = (x > 0) && (y < 10);
float arr[5];
float val = arr[x];'''
        
        ast = self.parser.parse(source)
        generated = self.codegen.generate(ast)
        
        self.assertIn("int x = 5", generated)
        self.assertIn("int y = x + 1", generated)
        self.assertIn("bool flag = (x > 0) && (y < 10)", generated)
        self.assertIn("float arr[5]", generated)
        self.assertIn("float val = arr[x]", generated)
    
    def test_control_flow(self):
        """Test code generation for control flow."""
        source = '''OPENQASM 3.0;
qubit q;
bit c;
if (c) {
    h q;
} else {
    x q;
}
for (int i in range(5)) {
    h q;
}'''
        
        ast = self.parser.parse(source)
        generated = self.codegen.generate(ast)
        
        self.assertIn("if (c)", generated)
        self.assertIn("h q", generated)
        self.assertIn("x q", generated)
        self.assertIn("for (int i in range(5))", generated)


if __name__ == '__main__':
    unittest.main()
