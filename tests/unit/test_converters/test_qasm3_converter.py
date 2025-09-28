#!/usr/bin/env python3
"""Unit tests for OpenQASM 3.0 converter integration."""

import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from quantum_converters.qasm3 import OpenQASM3Compiler


class TestOpenQASM3Converter(unittest.TestCase):
    """Test OpenQASM 3.0 converter functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.compiler = OpenQASM3Compiler()
    
    def test_basic_compilation(self):
        """Test basic OpenQASM 3.0 compilation."""
        source = '''OPENQASM 3.0;
qubit q;
h q;'''
        
        result = self.compiler.compile(source)
        self.assertTrue(result.success)
        self.assertEqual(len(result.errors), 0)
        self.assertIsNotNone(result.ast)
    
    def test_compilation_with_errors(self):
        """Test compilation with errors."""
        source = '''OPENQASM 3.0;
int x = true;  // Type error'''
        
        result = self.compiler.compile(source)
        self.assertFalse(result.success)
        self.assertGreater(len(result.errors), 0)
    
    def test_ast_generation(self):
        """Test AST generation."""
        source = '''OPENQASM 3.0;
qubit[2] q;
h q[0];
cx q[0], q[1];'''
        
        ast = self.compiler.get_ast(source)
        self.assertIsNotNone(ast)
        self.assertEqual(len(ast.statements), 3)
    
    def test_code_generation(self):
        """Test code generation."""
        source = '''OPENQASM 3.0;
qubit q;
h q;'''
        
        generated = self.compiler.generate(source)
        self.assertIn("OPENQASM 3.0", generated)
        self.assertIn("qubit q", generated)
        self.assertIn("h q", generated)
    
    def test_token_generation(self):
        """Test token generation."""
        source = '''OPENQASM 3.0;
qubit q;'''
        
        tokens = self.compiler.get_tokens(source)
        self.assertGreater(len(tokens), 0)
        self.assertEqual(tokens[0].type.name, 'OPENQASM')
        self.assertEqual(tokens[1].type.name, 'FLOAT')
    
    def test_roundtrip_compilation(self):
        """Test roundtrip compilation."""
        original = '''OPENQASM 3.0;
qubit[3] q;
for (int i in range(3)) {
    h q[i];
}'''
        
        # Parse -> Generate -> Parse
        ast1 = self.compiler.get_ast(original)
        generated = self.compiler.generate(original)
        ast2 = self.compiler.get_ast(generated)
        
        self.assertIsNotNone(ast1)
        self.assertIsNotNone(ast2)
        self.assertEqual(len(ast1.statements), len(ast2.statements))
    
    def test_complex_program(self):
        """Test complex program compilation."""
        source = '''OPENQASM 3.0;
qubit[4] q;
bit[4] c;

// Quantum Fourier Transform
for (int i in range(4)) {
    h q[i];
    for (int j in range(i + 1, 4)) {
        float angle = pi / (2 ** (j - i));
        cp(angle) q[j], q[i];
    }
}

// Measure all qubits
for (int i in range(4)) {
    measure q[i] -> c[i];
}'''
        
        result = self.compiler.compile(source)
        self.assertTrue(result.success)
        self.assertEqual(len(result.errors), 0)
    
    def test_error_recovery(self):
        """Test error recovery in compilation."""
        source = '''OPENQASM 3.0;
qubit q;
h q;
// This line has a syntax error
int x = 5  // Missing semicolon
h q;'''
        
        result = self.compiler.compile(source)
        self.assertFalse(result.success)
        self.assertGreater(len(result.errors), 0)
    
    def test_performance_large_program(self):
        """Test performance with large programs."""
        # Generate a large program
        source = "OPENQASM 3.0;\n"
        source += "qubit[50] q;\n"
        source += "bit[50] c;\n"
        
        # Add many operations
        for i in range(50):
            source += f"h q[{i}];\n"
        
        for i in range(0, 50, 2):
            source += f"cx q[{i}], q[{i+1}];\n"
        
        for i in range(50):
            source += f"measure q[{i}] -> c[{i}];\n"
        
        result = self.compiler.compile(source)
        self.assertTrue(result.success)
        self.assertEqual(len(result.errors), 0)


if __name__ == '__main__':
    unittest.main()
