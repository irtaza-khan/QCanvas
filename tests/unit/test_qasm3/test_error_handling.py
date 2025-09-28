#!/usr/bin/env python3
"""Unit tests for OpenQASM 3.0 error handling and validation."""

import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from quantum_converters.qasm3.parser import QASMParser
from quantum_converters.qasm3.type_system import SemanticAnalyzer


class TestOpenQASM3ErrorHandling(unittest.TestCase):
    """Test OpenQASM 3.0 error handling and validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = QASMParser()
        self.analyzer = SemanticAnalyzer()
    
    def test_wrong_type_assignment(self):
        """Test wrong type assignment error."""
        source = '''OPENQASM 3.0;
int x = true;'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertFalse(success)
        errors = self.analyzer.get_errors()
        self.assertTrue(any("Cannot initialize variable" in str(error) for error in errors))
    
    def test_const_without_initializer(self):
        """Test const variable without initializer error."""
        source = '''OPENQASM 3.0;
const int x;'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertFalse(success)
        errors = self.analyzer.get_errors()
        self.assertTrue(any("Const variables must be initialized" in str(error) for error in errors))
    
    def test_undefined_variable(self):
        """Test undefined variable error."""
        source = '''OPENQASM 3.0;
int x = undefined_variable;'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertFalse(success)
        errors = self.analyzer.get_errors()
        self.assertTrue(any("Undefined symbol" in str(error) for error in errors))
    
    def test_type_mismatch_in_operations(self):
        """Test type mismatch in operations."""
        source = '''OPENQASM 3.0;
int x = 5;
bool flag = true;
int y = x + flag;'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertFalse(success)
        errors = self.analyzer.get_errors()
        self.assertTrue(any("Arithmetic operator" in str(error) for error in errors))
    
    def test_array_index_type_mismatch(self):
        """Test array index type mismatch."""
        source = '''OPENQASM 3.0;
qubit[5] q;
bit c;
h q[c];'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertFalse(success)
        errors = self.analyzer.get_errors()
        self.assertTrue(any("Array index must be integer" in str(error) for error in errors))
    
    def test_non_boolean_if_condition(self):
        """Test non-boolean if condition."""
        source = '''OPENQASM 3.0;
int x = 5;
if (x) {
    h q;
}'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertFalse(success)
        errors = self.analyzer.get_errors()
        self.assertTrue(any("If condition must be boolean" in str(error) for error in errors))
    
    def test_wrong_gate_argument_type(self):
        """Test wrong gate argument type."""
        source = '''OPENQASM 3.0;
int x = 5;
h x;'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertFalse(success)
        errors = self.analyzer.get_errors()
        self.assertTrue(any("Gate arguments must be qubits" in str(error) for error in errors))
    
    def test_measure_wrong_types(self):
        """Test measure with wrong types."""
        source = '''OPENQASM 3.0;
int x = 5;
bit c;
measure x -> c;'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertFalse(success)
        errors = self.analyzer.get_errors()
        self.assertTrue(any("Can only measure qubits" in str(error) for error in errors))
    
    def test_invalid_range_arguments(self):
        """Test invalid range arguments."""
        source = '''OPENQASM 3.0;
for (int i in range(5.5)) {
    h q;
}'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertFalse(success)
        errors = self.analyzer.get_errors()
        self.assertTrue(any("Range" in str(error) and "must be integer" in str(error) for error in errors))
    
    def test_redefinition(self):
        """Test variable redefinition error."""
        source = '''OPENQASM 3.0;
int x = 5;
int x = 10;'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertFalse(success)
        errors = self.analyzer.get_errors()
        self.assertTrue(any("already defined in this scope" in str(error) for error in errors))
    
    def test_const_reassignment(self):
        """Test const variable reassignment error."""
        source = '''OPENQASM 3.0;
const int x = 5;
x = 10;'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertFalse(success)
        errors = self.analyzer.get_errors()
        self.assertTrue(any("Cannot assign to const" in str(error) for error in errors))
    
    def test_array_access_on_non_array(self):
        """Test array access on non-array type."""
        source = '''OPENQASM 3.0;
int x = 5;
int y = x[0];'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        self.assertFalse(success)
        errors = self.analyzer.get_errors()
        self.assertTrue(any("Cannot index non-array" in str(error) for error in errors))
    
    def test_missing_version(self):
        """Test missing version string."""
        source = '''include "stdgates.inc";
qubit q;
h q;'''
        
        with self.assertRaises(Exception):
            self.parser.parse(source)
    
    def test_invalid_version(self):
        """Test invalid version string."""
        source = '''OPENQASM 2.0;
qubit q;
h q;'''
        
        # This should parse but might generate warnings
        ast = self.parser.parse(source)
        self.assertIsNotNone(ast)
    
    def test_unclosed_comment(self):
        """Test unclosed comment."""
        source = '''OPENQASM 3.0;
/* This is an unclosed comment
qubit q;
h q;'''
        
        # This should parse but might generate warnings
        ast = self.parser.parse(source)
        self.assertIsNotNone(ast)
    
    def test_division_by_zero(self):
        """Test division by zero (should be allowed in OpenQASM)."""
        source = '''OPENQASM 3.0;
int x = 5 / 0;
int y = 10;'''
        
        ast = self.parser.parse(source)
        success = self.analyzer.analyze(ast)
        
        # Division by zero should be allowed in OpenQASM
        self.assertTrue(success)
    
    def test_unmatched_braces(self):
        """Test unmatched braces."""
        source = '''OPENQASM 3.0;
if (true) {
    h q;
// Missing closing brace'''
        
        with self.assertRaises(Exception):
            self.parser.parse(source)
    
    def test_unmatched_parentheses(self):
        """Test unmatched parentheses."""
        source = '''OPENQASM 3.0;
int x = (5 + 3;
int y = 10;'''
        
        with self.assertRaises(Exception):
            self.parser.parse(source)
    
    def test_invalid_identifier(self):
        """Test invalid identifier."""
        source = '''OPENQASM 3.0;
int 123invalid = 5;'''
        
        with self.assertRaises(Exception):
            self.parser.parse(source)
    
    def test_reserved_keyword_as_identifier(self):
        """Test reserved keyword as identifier."""
        source = '''OPENQASM 3.0;
int if = 5;'''
        
        with self.assertRaises(Exception):
            self.parser.parse(source)


if __name__ == '__main__':
    unittest.main()
