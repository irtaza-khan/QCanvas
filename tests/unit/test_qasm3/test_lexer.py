#!/usr/bin/env python3
"""Unit tests for OpenQASM 3.0 lexer."""

import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from quantum_converters.qasm3.lexer import QASMLexer, TokenType


class TestOpenQASM3Lexer(unittest.TestCase):
    """Test OpenQASM 3.0 lexer functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.lexer = QASMLexer()
    
    def test_version_control(self):
        """Test version string parsing."""
        source = "OPENQASM 3.0;"
        tokens = self.lexer.tokenize(source)
        
        # Check first few tokens
        self.assertEqual(tokens[0].type, TokenType.OPENQASM)
        self.assertEqual(tokens[1].type, TokenType.FLOAT)
        self.assertEqual(tokens[1].value, "3.0")
        self.assertEqual(tokens[2].type, TokenType.SEMICOLON)
    
    def test_comments(self):
        """Test comment parsing."""
        source = "// This is a comment\nOPENQASM 3.0;"
        tokens = self.lexer.tokenize(source)
        
        # Comments are tokenized but can be filtered out
        # Find the first non-comment token
        non_comment_tokens = [t for t in tokens if t.type != TokenType.COMMENT and t.type != TokenType.NEWLINE]
        self.assertEqual(non_comment_tokens[0].type, TokenType.OPENQASM)
        self.assertEqual(non_comment_tokens[1].type, TokenType.FLOAT)
    
    def test_include_statements(self):
        """Test include statement parsing."""
        source = 'include "stdgates.inc";'
        tokens = self.lexer.tokenize(source)
        
        self.assertEqual(tokens[0].type, TokenType.INCLUDE)
        self.assertEqual(tokens[1].type, TokenType.STRING)
        self.assertEqual(tokens[1].value, '"stdgates.inc"')
        self.assertEqual(tokens[2].type, TokenType.SEMICOLON)
    
    def test_literals(self):
        """Test literal parsing."""
        source = "42 3.14 true false"
        tokens = self.lexer.tokenize(source)
        
        self.assertEqual(tokens[0].type, TokenType.INTEGER)
        self.assertEqual(tokens[0].value, "42")
        self.assertEqual(tokens[1].type, TokenType.FLOAT)
        self.assertEqual(tokens[1].value, "3.14")
        # Note: true/false are handled as boolean literals in the lexer
        self.assertEqual(tokens[2].type, TokenType.BOOLEAN)
        self.assertEqual(tokens[3].type, TokenType.BOOLEAN)
    
    def test_types(self):
        """Test type keyword parsing."""
        source = "qubit bit int uint float angle bool"
        tokens = self.lexer.tokenize(source)
        
        expected_types = [
            TokenType.QUBIT, TokenType.BIT, TokenType.INT, 
            TokenType.UINT, TokenType.FLOAT_KW, TokenType.ANGLE, TokenType.BOOL
        ]
        
        for i, expected_type in enumerate(expected_types):
            self.assertEqual(tokens[i].type, expected_type)
    
    def test_operators(self):
        """Test operator parsing."""
        source = "+ - * / % ** == != < > <= >= && || !"
        tokens = self.lexer.tokenize(source)
        
        expected_operators = [
            TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE,
            TokenType.MODULO, TokenType.POWER, TokenType.EQUAL, TokenType.NOT_EQUAL,
            TokenType.LESS_THAN, TokenType.GREATER_THAN, TokenType.LESS_EQUAL,
            TokenType.GREATER_EQUAL, TokenType.AND, TokenType.OR, TokenType.NOT
        ]
        
        for i, expected_op in enumerate(expected_operators):
            self.assertEqual(tokens[i].type, expected_op)
    
    def test_gate_modifiers(self):
        """Test gate modifier parsing."""
        source = "ctrl @ inv @ pow(2) @"
        tokens = self.lexer.tokenize(source)
        
        self.assertEqual(tokens[0].type, TokenType.CTRL)
        self.assertEqual(tokens[1].type, TokenType.AT)
        self.assertEqual(tokens[2].type, TokenType.INV)
        self.assertEqual(tokens[3].type, TokenType.AT)
        self.assertEqual(tokens[4].type, TokenType.POW)
        self.assertEqual(tokens[5].type, TokenType.LPAREN)
        self.assertEqual(tokens[6].type, TokenType.INTEGER)
        self.assertEqual(tokens[7].type, TokenType.RPAREN)
        self.assertEqual(tokens[8].type, TokenType.AT)


if __name__ == '__main__':
    unittest.main()
