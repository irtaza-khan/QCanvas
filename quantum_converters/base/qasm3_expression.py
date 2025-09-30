"""
OpenQASM 3.0 Expression Evaluator and Parser

Handles classical expressions, arithmetic, comparison, and logical operations
for OpenQASM 3.0 Iteration I features.

Author: QCanvas Team
Date: 2025-09-30
Version: 1.0.0
"""

import re
import ast
from typing import Any, Dict, Optional, Union, List
from enum import Enum


class ExpressionType(Enum):
    """Types of expressions in OpenQASM 3.0"""
    ARITHMETIC = "arithmetic"
    COMPARISON = "comparison"
    LOGICAL = "logical"
    BITWISE = "bitwise"
    LITERAL = "literal"
    VARIABLE = "variable"


class QASM3ExpressionParser:
    """
    Parser and evaluator for OpenQASM 3.0 classical expressions.
    
    Supports:
    - Arithmetic operations: +, -, *, /
    - Comparison operations: <, >, <=, >=, ==, !=
    - Logical operations: &&, ||, !
    - Mathematical functions: sin, cos, tan, sqrt, exp, log
    """
    
    # Operator precedence (higher number = higher precedence)
    PRECEDENCE = {
        '||': 1,
        '&&': 2,
        '==': 3, '!=': 3,
        '<': 4, '>': 4, '<=': 4, '>=': 4,
        '+': 5, '-': 5,
        '*': 6, '/': 6,  '%': 6,
        '!': 7,  # Unary not
    }
    
    # Supported mathematical functions (Iteration I)
    MATH_FUNCTIONS = {
        'sqrt', 'exp', 'log', 'ln',
        'sin', 'cos', 'tan',
        'arcsin', 'arccos', 'arctan',
        'floor', 'ceil', 'abs',
        'pow', 'mod',
    }
    
    def __init__(self):
        """Initialize the expression parser."""
        self.variables: Dict[str, Any] = {}
        
    def parse_literal(self, value_str: str) -> tuple[Any, str]:
        """
        Parse a literal value and determine its type.
        
        Args:
            value_str: String representation of literal
            
        Returns:
            Tuple of (value, type)  where type is 'int', 'float', 'bool', 'angle'
        """
        value_str = value_str.strip()
        
        # Boolean literals
        if value_str.lower() in ['true', '1']:
            return True, 'bool'
        if value_str.lower() in ['false', '0']:
            return False, 'bool'
            
        # Try integer
        try:
            val = int(value_str)
            return val, 'int'
        except ValueError:
            pass
            
        # Try float
        try:
            val = float(value_str)
            return val, 'float'
        except ValueError:
            pass
            
        # Check for mathematical constants
        constants = {
            'PI': (3.141592653589793, 'float'),
            'E': (2.718281828459045, 'float'),
            'PI_2': (1.5707963267948966, 'float'),
            'PI_4': (0.7853981633974483, 'float'),
            'TAU': (6.283185307179586, 'float'),
        }
        
        if value_str in constants:
            return constants[value_str]
            
        # Assume it's a variable reference
        return value_str, 'variable'
        
    def parse_expression(self, expr_str: str) -> str:
        """
        Parse and potentially simplify an expression.
        
        Args:
            expr_str: Expression string
            
        Returns:
            Parsed/simplified expression string
        """
        expr_str = expr_str.strip()
        
        # Handle parentheses
        if expr_str.startswith('(') and expr_str.endswith(')'):
            # Check if outer parentheses are balanced
            depth = 0
            for i, char in enumerate(expr_str):
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                if depth == 0 and i < len(expr_str) - 1:
                    break
            if depth == 0 and i == len(expr_str) - 1:
                # Outer parentheses are redundant
                return self.parse_expression(expr_str[1:-1])
                
        # Check for binary operators
        for op in ['||', '&&', '==', '!=', '<=', '>=', '<', '>', '+', '-', '*', '/']:
            if op in expr_str:
                parts = self._split_by_operator(expr_str, op)
                if len(parts) == 2:
                    left = self.parse_expression(parts[0])
                    right = self.parse_expression(parts[1])
                    
                    # Convert to OpenQASM operators
                    qasm_op = op
                    if op == '&&':
                        qasm_op = '&&'
                    elif op == '||':
                        qasm_op = '||'
                        
                    return f"{left} {qasm_op} {right}"
                    
        # Check for unary operators
        if expr_str.startswith('!'):
            operand = self.parse_expression(expr_str[1:])
            return f"!{operand}"
        if expr_str.startswith('-') and len(expr_str) > 1:
            operand = self.parse_expression(expr_str[1:])
            try:
                # Try to evaluate if it's a number
                float(operand)
                return f"-{operand}"
            except:
                return f"(-{operand})"
                
        # Check for function calls
        func_match = re.match(r'(\w+)\((.*)\)', expr_str)
        if func_match:
            func_name = func_match.group(1)
            args_str = func_match.group(2)
            
            if func_name in self.MATH_FUNCTIONS:
                # Parse arguments
                args = [self.parse_expression(arg.strip()) for arg in self._split_args(args_str)]
                args_formatted = ', '.join(args)
                return f"{func_name}({args_formatted})"
                
        # Otherwise, return as-is (literal or variable)
        return expr_str
        
    def _split_by_operator(self, expr: str, operator: str) -> List[str]:
        """
        Split an expression by an operator, respecting parentheses.
        
        Args:
            expr: Expression string
            operator: Operator to split by
            
        Returns:
            List of parts split by operator
        """
        parts = []
        current = []
        depth = 0
        i = 0
        
        while i < len(expr):
            char = expr[i]
            
            if char == '(':
                depth += 1
                current.append(char)
            elif char == ')':
                depth -= 1
                current.append(char)
            elif depth == 0 and expr[i:i+len(operator)] == operator:
                parts.append(''.join(current).strip())
                current = []
                i += len(operator) - 1
            else:
                current.append(char)
                
            i += 1
            
        if current:
            parts.append(''.join(current).strip())
            
        return parts
        
    def _split_args(self, args_str: str) -> List[str]:
        """
        Split function arguments, respecting parentheses and commas.
        
        Args:
            args_str: Arguments string
            
        Returns:
            List of individual arguments
        """
        if not args_str.strip():
            return []
            
        args = []
        current = []
        depth = 0
        
        for char in args_str:
            if char == '(':
                depth += 1
                current.append(char)
            elif char == ')':
                depth -= 1
                current.append(char)
            elif char == ',' and depth == 0:
                args.append(''.join(current).strip())
                current = []
            else:
                current.append(char)
                
        if current:
            args.append(''.join(current).strip())
            
        return args
        
    def validate_expression(self, expr_str: str) -> tuple[bool, Optional[str]]:
        """
        Validate an expression for syntactic correctness.
        
        Args:
            expr_str: Expression to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check balanced parentheses
            depth = 0
            for char in expr_str:
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                if depth < 0:
                    return False, "Unbalanced parentheses: too many closing parens"
                    
            if depth != 0:
                return False, "Unbalanced parentheses: unclosed opening parens"
                
            # Check for invalid character sequences
            if '..' in expr_str or ',,,' in expr_str:
                return False, "Invalid character sequence"
                
            return True, None
            
        except Exception as e:
            return False, str(e)
            
    def infer_type(self, expr_str: str) -> str:
        """
        Infer the type of an expression result.
        
        Args:
            expr_str: Expression string
            
        Returns:
            Inferred type: 'int', 'float', 'bool', 'angle', 'unknown'
        """
        expr_str = expr_str.strip()
        
        # Check for comparison/logical operators - these return bool
        for op in ['==', '!=', '<', '>', '<=', '>=', '&&', '||']:
            if op in expr_str:
                return 'bool'
                
        # Check for unary not
        if expr_str.startswith('!'):
            return 'bool'
            
        # Check for arithmetic - could be int or float
        for op in ['+', '-', '*', '/']:
            if op in expr_str:
                # If division, always float
                if '/' in expr_str:
                    return 'float'
                # Otherwise, check operands
                return 'float'  # Conservative: assume float
                
        # Check literals
        val, val_type = self.parse_literal(expr_str)
        return val_type
        
    def format_for_qasm(self, expr: Any) -> str:
        """
        Format a Python expression/value for OpenQASM output.
        
        Args:
            expr: Expression to format
            
        Returns:
            QASM-formatted string
        """
        if isinstance(expr, bool):
            return 'true' if expr else 'false'
        elif isinstance(expr, str):
            return expr
        elif isinstance(expr, (int, float)):
            return str(expr)
        else:
            return str(expr)
