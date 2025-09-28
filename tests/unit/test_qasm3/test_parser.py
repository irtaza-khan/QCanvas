#!/usr/bin/env python3
"""Unit tests for OpenQASM 3.0 parser."""

import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from quantum_converters.qasm3.parser import QASMParser
from quantum_converters.qasm3.ast_nodes import *


class TestOpenQASM3Parser(unittest.TestCase):
    """Test OpenQASM 3.0 parser functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = QASMParser()
    
    def test_basic_program(self):
        """Test basic program parsing."""
        source = '''OPENQASM 3.0;
qubit q;
h q;'''
        
        ast = self.parser.parse(source)
        self.assertEqual(len(ast.statements), 2)
        self.assertIsInstance(ast.statements[0], VariableDeclaration)
        self.assertIsInstance(ast.statements[1], GateCall)
    
    def test_variable_declarations(self):
        """Test variable declaration parsing."""
        source = '''OPENQASM 3.0;
const int x = 42;
float y = 3.14;
qubit[5] q;
bit[5] c;'''
        
        ast = self.parser.parse(source)
        statements = ast.statements
        
        # Const declaration
        self.assertIsInstance(statements[0], VariableDeclaration)
        self.assertTrue(statements[0].is_const)
        self.assertEqual(statements[0].name, "x")
        
        # Float declaration with initializer
        self.assertIsInstance(statements[1], VariableDeclaration)
        self.assertFalse(statements[1].is_const)
        self.assertIsNotNone(statements[1].initializer)
        
        # Array declarations
        self.assertIsInstance(statements[2], VariableDeclaration)
        self.assertIsNotNone(statements[2].type_annotation.size)
    
    def test_control_flow(self):
        """Test control flow parsing."""
        source = '''OPENQASM 3.0;
if (true) {
    h q;
} else {
    x q;
}
for (int i in range(5)) {
    h q[i];
}'''
        
        ast = self.parser.parse(source)
        statements = ast.statements
        
        # If statement
        self.assertIsInstance(statements[0], IfStatement)
        self.assertIsInstance(statements[0].condition, Literal)
        self.assertEqual(len(statements[0].then_branch), 1)
        self.assertEqual(len(statements[0].else_branch), 1)
        
        # For statement
        self.assertIsInstance(statements[1], ForStatement)
        self.assertEqual(statements[1].variable, "i")
        self.assertIsInstance(statements[1].iterable, RangeExpression)
    
    def test_expressions(self):
        """Test expression parsing."""
        source = '''OPENQASM 3.0;
int x = 5;
int y = x + 1;
bool flag = (x > 0) && (y < 10);
float arr[5];
float val = arr[x];'''
        
        ast = self.parser.parse(source)
        statements = ast.statements
        
        # Binary operation
        init_expr = statements[1].initializer
        self.assertIsInstance(init_expr, BinaryOperation)
        self.assertEqual(init_expr.operator, "+")
        
        # Complex boolean expression
        bool_expr = statements[2].initializer
        self.assertIsInstance(bool_expr, BinaryOperation)
        self.assertEqual(bool_expr.operator, "&&")
        
        # Array access
        access_expr = statements[4].initializer
        self.assertIsInstance(access_expr, ArrayAccess)
    
    def test_gate_calls(self):
        """Test gate call parsing."""
        source = '''OPENQASM 3.0;
qubit[3] q;
h q[0];
cx q[0], q[1];
ctrl @ x q[0], q[1];
inv @ h q[2];
rx(3.14) q[0];'''
        
        ast = self.parser.parse(source)
        statements = ast.statements[1:]  # Skip qubit declaration
        
        # Simple gate call
        self.assertIsInstance(statements[0], GateCall)
        self.assertEqual(statements[0].name, "h")
        
        # Two-qubit gate
        self.assertIsInstance(statements[1], GateCall)
        self.assertEqual(len(statements[1].qubits), 2)
        
        # Modified gate calls
        self.assertIsInstance(statements[2], GateCall)
        self.assertEqual(len(statements[2].modifiers), 1)
        self.assertEqual(statements[2].modifiers[0].type, "ctrl")
        
        # Parameterized gate call
        self.assertIsInstance(statements[4], GateCall)
        self.assertEqual(len(statements[4].parameters), 1)
    
    def test_gate_definitions(self):
        """Test gate definition parsing."""
        source = '''OPENQASM 3.0;
gate h q { }
gate rx(angle theta) q { }
gate bell a, b {
    h a;
    cx a, b;
}'''
        
        ast = self.parser.parse(source)
        statements = ast.statements
        
        # Simple gate
        self.assertIsInstance(statements[0], GateDefinition)
        self.assertEqual(statements[0].name, "h")
        self.assertEqual(len(statements[0].parameters), 0)
        self.assertEqual(len(statements[0].qubits), 1)
        
        # Parameterized gate
        self.assertIsInstance(statements[1], GateDefinition)
        self.assertEqual(statements[1].name, "rx")
        self.assertEqual(len(statements[1].parameters), 1)
        self.assertEqual(statements[1].parameters[0], "theta")
        
        # Multi-qubit gate with body
        self.assertIsInstance(statements[2], GateDefinition)
        self.assertEqual(len(statements[2].qubits), 2)
        self.assertEqual(len(statements[2].body), 2)
    
    def test_measurements(self):
        """Test measurement parsing."""
        source = '''OPENQASM 3.0;
qubit q;
bit c;
measure q -> c;
reset q;'''
        
        ast = self.parser.parse(source)
        statements = ast.statements[2:]  # Skip declarations
        
        # Measurement
        self.assertIsInstance(statements[0], MeasurementStatement)
        self.assertIsInstance(statements[0].qubit, Identifier)
        self.assertIsInstance(statements[0].target, Identifier)
        
        # Reset
        self.assertIsInstance(statements[1], ResetStatement)
        self.assertIsInstance(statements[1].qubit, Identifier)
    
    def test_parse_errors(self):
        """Test parse error handling."""
        # Missing semicolon
        source = '''OPENQASM 3.0;
int x = 5
h q;'''
        
        with self.assertRaises(Exception):
            self.parser.parse(source)
        
        # Invalid syntax
        source = '''OPENQASM 3.0;
int x = 5;
if (x) {  // Missing semicolon
    h q;
}'''
        
        with self.assertRaises(Exception):
            self.parser.parse(source)


if __name__ == '__main__':
    unittest.main()
