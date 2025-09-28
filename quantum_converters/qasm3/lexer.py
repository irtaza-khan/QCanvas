"""
OpenQASM 3.0 Lexer Module

This module provides tokenization for OpenQASM 3.0 source code.
Supports all Iteration I language features including comments, types, and operations.

Author: QCanvas Team
Date: 2024
Version: 1.0.0
"""

import re
from enum import Enum, auto
from typing import List, NamedTuple, Optional, Iterator
from dataclasses import dataclass

class TokenType(Enum):
    # Literals
    INTEGER = auto()
    FLOAT = auto()
    BOOLEAN = auto()
    STRING = auto()
    
    # Identifiers
    IDENTIFIER = auto()
    
    # Keywords
    OPENQASM = auto()
    INCLUDE = auto()
    CONST = auto()
    QUBIT = auto()
    BIT = auto()
    INT = auto()
    UINT = auto()
    FLOAT_KW = auto()
    ANGLE = auto()
    BOOL = auto()
    IF = auto()
    ELSE = auto()
    FOR = auto()
    IN = auto()
    RANGE = auto()
    GATE = auto()
    CTRL = auto()
    INV = auto()
    POW = auto()
    MEASURE = auto()
    RESET = auto()
    BARRIER = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    POWER = auto()
    
    # Comparison
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    
    # Logical
    AND = auto()
    OR = auto()
    NOT = auto()
    
    # Assignment
    ASSIGN = auto()
    PLUS_ASSIGN = auto()
    MINUS_ASSIGN = auto()
    
    # Punctuation
    SEMICOLON = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()
    
    # Brackets
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    
    # Special
    ARROW = auto()
    AT = auto()
    
    # Comments
    COMMENT = auto()
    
    # End of file
    EOF = auto()
    
    # Newline
    NEWLINE = auto()

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', {self.line}:{self.column})"

class QASMLexer:
    """OpenQASM 3.0 Lexer for tokenizing source code."""
    
    def __init__(self):
        # Keywords mapping
        self.keywords = {
            'OPENQASM': TokenType.OPENQASM,
            'include': TokenType.INCLUDE,
            'const': TokenType.CONST,
            'qubit': TokenType.QUBIT,
            'bit': TokenType.BIT,
            'int': TokenType.INT,
            'uint': TokenType.UINT,
            'float': TokenType.FLOAT_KW,
            'angle': TokenType.ANGLE,
            'bool': TokenType.BOOL,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'for': TokenType.FOR,
            'in': TokenType.IN,
            'range': TokenType.RANGE,
            'gate': TokenType.GATE,
            'ctrl': TokenType.CTRL,
            'inv': TokenType.INV,
            'pow': TokenType.POW,
            'measure': TokenType.MEASURE,
            'reset': TokenType.RESET,
            'barrier': TokenType.BARRIER,
            'true': TokenType.BOOLEAN,
            'false': TokenType.BOOLEAN,
        }
        
        # Token patterns
        self.token_patterns = [
            # Comments (must be first to catch before other patterns)
            (r'//[^\n]*', TokenType.COMMENT),
            (r'/\*[\s\S]*?\*/', TokenType.COMMENT),
            
            # Numbers (must come before identifiers to prevent invalid identifiers like "123abc")
            (r'\d+\.\d+([eE][+-]?\d+)?', TokenType.FLOAT),
            (r'\d+[eE][+-]?\d+', TokenType.FLOAT),
            (r'\d+', TokenType.INTEGER),
            
            # Strings
            (r'"[^"]*"', TokenType.STRING),
            (r"'[^']*'", TokenType.STRING),
            
            # Identifiers and keywords
            (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER),
            
            # Two-character operators
            (r'==', TokenType.EQUAL),
            (r'!=', TokenType.NOT_EQUAL),
            (r'<=', TokenType.LESS_EQUAL),
            (r'>=', TokenType.GREATER_EQUAL),
            (r'&&', TokenType.AND),
            (r'\|\|', TokenType.OR),
            (r'\+=', TokenType.PLUS_ASSIGN),
            (r'-=', TokenType.MINUS_ASSIGN),
            (r'->', TokenType.ARROW),
            (r'\*\*', TokenType.POWER),
            
            # Single-character operators
            (r'\+', TokenType.PLUS),
            (r'-', TokenType.MINUS),
            (r'\*', TokenType.MULTIPLY),
            (r'/', TokenType.DIVIDE),
            (r'%', TokenType.MODULO),
            (r'<', TokenType.LESS_THAN),
            (r'>', TokenType.GREATER_THAN),
            (r'!', TokenType.NOT),
            (r'=', TokenType.ASSIGN),
            
            # Punctuation
            (r';', TokenType.SEMICOLON),
            (r',', TokenType.COMMA),
            (r'\.', TokenType.DOT),
            (r':', TokenType.COLON),
            (r'@', TokenType.AT),
            
            # Brackets
            (r'\(', TokenType.LPAREN),
            (r'\)', TokenType.RPAREN),
            (r'\[', TokenType.LBRACKET),
            (r'\]', TokenType.RBRACKET),
            (r'\{', TokenType.LBRACE),
            (r'\}', TokenType.RBRACE),
            
            # Newlines
            (r'\n', TokenType.NEWLINE),
        ]
        
        # Compile patterns
        self.compiled_patterns = [(re.compile(pattern), token_type) 
                                 for pattern, token_type in self.token_patterns]
    
    def tokenize(self, source: str) -> List[Token]:
        """
        Tokenize OpenQASM 3.0 source code.
        
        Args:
            source: OpenQASM 3.0 source code string
            
        Returns:
            List of tokens
        """
        tokens = []
        lines = source.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            column = 1
            pos = 0
            
            while pos < len(line):
                # Skip whitespace (except newlines)
                if line[pos].isspace() and line[pos] != '\n':
                    pos += 1
                    column += 1
                    continue
                
                # Try to match patterns
                matched = False
                for pattern, token_type in self.compiled_patterns:
                    match = pattern.match(line, pos)
                    if match:
                        value = match.group()
                        
                        # Handle keywords vs identifiers
                        if token_type == TokenType.IDENTIFIER and value in self.keywords:
                            token_type = self.keywords[value]
                        
                        # Skip whitespace tokens but keep meaningful ones
                        if token_type != TokenType.NEWLINE or value == '\n':
                            tokens.append(Token(token_type, value, line_num, column))
                        
                        pos = match.end()
                        column += len(value)
                        matched = True
                        break
                
                if not matched:
                    # Unknown character, skip it
                    pos += 1
                    column += 1
            
            # Add newline token at end of each line (except last empty line)
            if line_num < len(lines) or line.strip():
                tokens.append(Token(TokenType.NEWLINE, '\n', line_num, len(line) + 1))
        
        # Add EOF token
        tokens.append(Token(TokenType.EOF, '', len(lines), 1))
        
        return tokens
    
    def tokenize_iterator(self, source: str) -> Iterator[Token]:
        """
        Tokenize source code and return iterator for memory efficiency.
        
        Args:
            source: OpenQASM 3.0 source code string
            
        Yields:
            Token objects
        """
        for token in self.tokenize(source):
            yield token


def test_lexer():
    """Test the OpenQASM 3.0 lexer with various inputs."""
    lexer = QASMLexer()
    
    # Test cases
    test_cases = [
        # Basic structure
        '''OPENQASM 3.0;
include "stdgates.inc";''',
        
        # Types and variables
        '''qubit[5] q;
bit[5] c;
int x = 42;
float y = 3.14;
bool flag = true;''',
        
        # Comments
        '''// Single line comment
/* Multi-line
   comment */
qubit q;''',
        
        # Gates and operations
        '''gate h q { }
ctrl @ x q[0], q[1];
inv @ h q[2];''',
        
        # Classical operations
        '''if (x > 0) {
    y += 1;
} else {
    y -= 1;
}'''
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test Case {i+1} ---")
        print(f"Input:\n{test_case}")
        print(f"\nTokens:")
        
        tokens = lexer.tokenize(test_case)
        for token in tokens:
            if token.type not in [TokenType.NEWLINE, TokenType.EOF]:
                print(f"  {token}")

if __name__ == "__main__":
    test_lexer()
