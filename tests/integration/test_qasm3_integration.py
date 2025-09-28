#!/usr/bin/env python3
"""Integration tests for OpenQASM 3.0 compiler."""

import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from quantum_converters.qasm3 import OpenQASM3Compiler


class TestOpenQASM3Integration(unittest.TestCase):
    """Integration tests for OpenQASM 3.0 compiler."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.compiler = OpenQASM3Compiler()
    
    def test_full_compilation_workflow(self):
        """Test complete compilation workflow."""
        source = '''OPENQASM 3.0;
qubit[3] q;
bit[3] c;

// Initialize qubits
h q[0];
cx q[0], q[1];
cx q[1], q[2];

// Measure all qubits
for (int i in range(3)) {
    measure q[i] -> c[i];
}'''
        
        # Test compilation
        result = self.compiler.compile(source)
        self.assertTrue(result.success)
        self.assertEqual(len(result.errors), 0)
        
        # Test AST generation
        ast = self.compiler.get_ast(source)
        self.assertIsNotNone(ast)
        self.assertEqual(len(ast.statements), 4)  # 1 qubit decl + 3 gate calls + 1 for loop
        
        # Test code generation
        generated = self.compiler.generate(source)
        self.assertIn("OPENQASM 3.0", generated)
        self.assertIn("qubit[3] q", generated)
        self.assertIn("h q[0]", generated)
        self.assertIn("for (int i in range(3))", generated)
    
    def test_complex_quantum_algorithm(self):
        """Test compilation of complex quantum algorithm."""
        source = '''OPENQASM 3.0;
qubit[4] q;
bit[4] c;
int n = 4;

// Quantum Fourier Transform
for (int i in range(n)) {
    h q[i];
    for (int j in range(i + 1, n)) {
        float angle = pi / (2 ** (j - i));
        cp(angle) q[j], q[i];
    }
}

// Measure
for (int i in range(n)) {
    measure q[i] -> c[i];
}'''
        
        result = self.compiler.compile(source)
        self.assertTrue(result.success)
        self.assertEqual(len(result.errors), 0)
    
    def test_gate_definition_and_usage(self):
        """Test gate definition and usage."""
        source = '''OPENQASM 3.0;
gate bell a, b {
    h a;
    cx a, b;
}

qubit[2] q;
bell q[0], q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];'''
        
        result = self.compiler.compile(source)
        self.assertTrue(result.success)
        self.assertEqual(len(result.errors), 0)
    
    def test_parameterized_gates(self):
        """Test parameterized gate definitions and usage."""
        source = '''OPENQASM 3.0;
gate rx(angle theta) q {
    // Rotation around X axis
}

gate ry(angle theta) q {
    // Rotation around Y axis
}

qubit q;
rx(pi/2) q;
ry(pi/4) q;'''
        
        result = self.compiler.compile(source)
        self.assertTrue(result.success)
        self.assertEqual(len(result.errors), 0)
    
    def test_control_flow_with_quantum_operations(self):
        """Test control flow with quantum operations."""
        source = '''OPENQASM 3.0;
qubit[3] q;
bit[3] c;
int i = 0;

// Conditional quantum operations
if (i == 0) {
    h q[0];
    cx q[0], q[1];
} else {
    x q[0];
    y q[1];
}

// Loop with quantum operations
for (int j in range(3)) {
    if (j < 2) {
        h q[j];
    }
    measure q[j] -> c[j];
}'''
        
        result = self.compiler.compile(source)
        self.assertTrue(result.success)
        self.assertEqual(len(result.errors), 0)
    
    def test_error_handling_and_recovery(self):
        """Test error handling and recovery."""
        # Test with syntax errors
        source_with_errors = '''OPENQASM 3.0;
qubit q;
h q  // Missing semicolon
x q;'''
        
        result = self.compiler.compile(source_with_errors)
        self.assertFalse(result.success)
        self.assertGreater(len(result.errors), 0)
        
        # Test with semantic errors
        source_semantic_errors = '''OPENQASM 3.0;
int x = 5;
h x;  // Wrong type for gate argument'''
        
        result = self.compiler.compile(source_semantic_errors)
        self.assertFalse(result.success)
        self.assertGreater(len(result.errors), 0)
    
    def test_large_program_performance(self):
        """Test performance with large programs."""
        # Generate a large program
        source = "OPENQASM 3.0;\n"
        source += "qubit[20] q;\n"
        source += "bit[20] c;\n"
        
        # Add many operations
        for i in range(20):
            source += f"h q[{i}];\n"
        
        for i in range(0, 20, 2):
            source += f"cx q[{i}], q[{i+1}];\n"
        
        for i in range(20):
            source += f"measure q[{i}] -> c[{i}];\n"
        
        result = self.compiler.compile(source)
        self.assertTrue(result.success)
        self.assertEqual(len(result.errors), 0)
    
    def test_roundtrip_compilation(self):
        """Test roundtrip compilation (parse -> generate -> parse)."""
        original = '''OPENQASM 3.0;
qubit[3] q;
bit[3] c;

for (int i in range(3)) {
    h q[i];
    if (i < 2) {
        cx q[i], q[i+1];
    }
    measure q[i] -> c[i];
}'''
        
        # Parse original
        ast1 = self.compiler.get_ast(original)
        self.assertIsNotNone(ast1)
        
        # Generate code
        generated = self.compiler.generate(original)
        self.assertIsNotNone(generated)
        
        # Parse generated code
        ast2 = self.compiler.get_ast(generated)
        self.assertIsNotNone(ast2)
        
        # Both should have the same number of statements
        self.assertEqual(len(ast1.statements), len(ast2.statements))


if __name__ == '__main__':
    unittest.main()
