#!/usr/bin/env python3
"""End-to-end tests for complete QCanvas workflows."""

import unittest
import sys
import os
import time

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestCompleteWorkflow(unittest.TestCase):
    """Test complete QCanvas workflows."""
    
    def setUp(self):
        """Set up test fixtures."""
        try:
            from quantum_converters.qasm3 import OpenQASM3Compiler
            self.compiler = OpenQASM3Compiler()
        except ImportError:
            self.skipTest("OpenQASM 3.0 compiler not available")
    
    def test_quantum_algorithm_workflow(self):
        """Test complete quantum algorithm workflow."""
        # Step 1: Write OpenQASM 3.0 code
        source = '''OPENQASM 3.0;
qubit[3] q;
bit[3] c;

// Quantum Fourier Transform
for (int i in range(3)) {
    h q[i];
    for (int j in range(i + 1, 3)) {
        float angle = pi / (2 ** (j - i));
        cp(angle) q[j], q[i];
    }
}

// Measure all qubits
for (int i in range(3)) {
    measure q[i] -> c[i];
}'''
        
        # Step 2: Compile and validate
        result = self.compiler.compile(source)
        self.assertTrue(result.success)
        self.assertEqual(len(result.errors), 0)
        
        # Step 3: Generate AST
        ast = self.compiler.get_ast(source)
        self.assertIsNotNone(ast)
        self.assertGreater(len(ast.statements), 0)
        
        # Step 4: Generate code (roundtrip)
        generated = self.compiler.generate(source)
        self.assertIn("OPENQASM 3.0", generated)
        self.assertIn("qubit[3] q", generated)
        
        # Step 5: Validate generated code
        ast2 = self.compiler.get_ast(generated)
        self.assertIsNotNone(ast2)
        self.assertEqual(len(ast.statements), len(ast2.statements))
    
    def test_circuit_conversion_workflow(self):
        """Test circuit conversion workflow."""
        # Step 1: Start with OpenQASM 3.0
        source = '''OPENQASM 3.0;
qubit[2] q;
h q[0];
cx q[0], q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];'''
        
        # Step 2: Compile to AST
        ast = self.compiler.get_ast(source)
        self.assertIsNotNone(ast)
        
        # Step 3: Generate OpenQASM 3.0 code
        generated = self.compiler.generate(source)
        self.assertIsNotNone(generated)
        
        # Step 4: Validate the generated code
        result = self.compiler.compile(generated)
        self.assertTrue(result.success)
    
    def test_error_handling_workflow(self):
        """Test error handling workflow."""
        # Step 1: Write code with errors
        source_with_errors = '''OPENQASM 3.0;
qubit q;
int x = true;  // Type error
h q;'''
        
        # Step 2: Attempt compilation
        result = self.compiler.compile(source_with_errors)
        self.assertFalse(result.success)
        self.assertGreater(len(result.errors), 0)
        
        # Step 3: Fix errors
        fixed_source = '''OPENQASM 3.0;
qubit q;
int x = 1;  // Fixed
h q;'''
        
        # Step 4: Recompile
        result = self.compiler.compile(fixed_source)
        self.assertTrue(result.success)
        self.assertEqual(len(result.errors), 0)
    
    def test_performance_workflow(self):
        """Test performance with large programs."""
        # Step 1: Generate large program
        source = "OPENQASM 3.0;\n"
        source += "qubit[10] q;\n"
        source += "bit[10] c;\n"
        
        # Add many operations
        for i in range(10):
            source += f"h q[{i}];\n"
        
        for i in range(0, 10, 2):
            source += f"cx q[{i}], q[{i+1}];\n"
        
        for i in range(10):
            source += f"measure q[{i}] -> c[{i}];\n"
        
        # Step 2: Measure compilation time
        start_time = time.time()
        result = self.compiler.compile(source)
        end_time = time.time()
        
        # Step 3: Verify success and performance
        self.assertTrue(result.success)
        self.assertLess(end_time - start_time, 5.0)  # Should complete within 5 seconds
        
        # Step 4: Test AST generation
        start_time = time.time()
        ast = self.compiler.get_ast(source)
        end_time = time.time()
        
        self.assertIsNotNone(ast)
        self.assertLess(end_time - start_time, 2.0)  # Should complete within 2 seconds
        
        # Step 5: Test code generation
        start_time = time.time()
        generated = self.compiler.generate(source)
        end_time = time.time()
        
        self.assertIsNotNone(generated)
        self.assertLess(end_time - start_time, 1.0)  # Should complete within 1 second
    
    def test_complex_quantum_circuit_workflow(self):
        """Test complex quantum circuit workflow."""
        # Step 1: Define complex quantum circuit
        source = '''OPENQASM 3.0;
qubit[4] q;
bit[4] c;

// Quantum teleportation protocol
h q[0];
cx q[0], q[1];
cx q[1], q[2];
h q[0];
measure q[0] -> c[0];
measure q[1] -> c[1];

// Conditional operations based on measurement
if (c[0]) {
    z q[2];
}
if (c[1]) {
    x q[2];
}

measure q[2] -> c[2];'''
        
        # Step 2: Compile and validate
        result = self.compiler.compile(source)
        self.assertTrue(result.success)
        
        # Step 3: Generate AST
        ast = self.compiler.get_ast(source)
        self.assertIsNotNone(ast)
        
        # Step 4: Verify circuit structure
        statements = ast.statements
        self.assertGreater(len(statements), 5)  # Should have multiple statements
        
        # Step 5: Generate and validate code
        generated = self.compiler.generate(source)
        self.assertIn("qubit[4] q", generated)
        self.assertIn("if (c[0])", generated)
        self.assertIn("if (c[1])", generated)
    
    def test_educational_workflow(self):
        """Test educational workflow for learning quantum computing."""
        # Step 1: Start with simple circuit
        simple_source = '''OPENQASM 3.0;
qubit q;
h q;
measure q -> c;'''
        
        result = self.compiler.compile(simple_source)
        self.assertTrue(result.success)
        
        # Step 2: Add complexity gradually
        intermediate_source = '''OPENQASM 3.0;
qubit[2] q;
bit[2] c;
h q[0];
cx q[0], q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];'''
        
        result = self.compiler.compile(intermediate_source)
        self.assertTrue(result.success)
        
        # Step 3: Add control flow
        advanced_source = '''OPENQASM 3.0;
qubit[3] q;
bit[3] c;
for (int i in range(3)) {
    h q[i];
    if (i < 2) {
        cx q[i], q[i+1];
    }
    measure q[i] -> c[i];
}'''
        
        result = self.compiler.compile(advanced_source)
        self.assertTrue(result.success)
    
    def test_research_workflow(self):
        """Test research workflow for quantum algorithm development."""
        # Step 1: Define research algorithm
        research_source = '''OPENQASM 3.0;
qubit[5] q;
bit[5] c;
int n = 5;

// Grover's algorithm
for (int iteration in range(int(sqrt(2**n)))) {
    // Oracle
    for (int i in range(n)) {
        if (i == 0) {
            x q[i];
        }
    }
    
    // Diffusion operator
    for (int i in range(n)) {
        h q[i];
    }
    for (int i in range(n)) {
        x q[i];
    }
    h q[n-1];
    cx q[0], q[n-1];
    h q[n-1];
    for (int i in range(n)) {
        x q[i];
    }
    for (int i in range(n)) {
        h q[i];
    }
}

// Measure
for (int i in range(n)) {
    measure q[i] -> c[i];
}'''
        
        # Step 2: Compile and validate
        result = self.compiler.compile(research_source)
        self.assertTrue(result.success)
        
        # Step 3: Generate AST for analysis
        ast = self.compiler.get_ast(research_source)
        self.assertIsNotNone(ast)
        
        # Step 4: Generate code for documentation
        generated = self.compiler.generate(research_source)
        self.assertIn("Grover's algorithm", generated)
        self.assertIn("for (int iteration in range", generated)


if __name__ == '__main__':
    unittest.main()
