"""
OpenQASM 3.0 Type System and Semantic Analyzer

This module provides type checking and semantic analysis for OpenQASM 3.0.
Implements the type system defined in the OpenQASM 3.0 specification.

Author: QCanvas Team
Date: 2024
Version: 1.0.0
"""

from typing import Dict, List, Optional, Union, Any, Set
from dataclasses import dataclass
from enum import Enum
from .ast_nodes import *

class QASMType(Enum):
    """OpenQASM 3.0 built-in types."""
    QUBIT = "qubit"
    BIT = "bit"
    INT = "int"
    UINT = "uint"
    FLOAT = "float"
    ANGLE = "angle"
    BOOL = "bool"
    STRING = "string"
    VOID = "void"

@dataclass
class TypeInfo:
    """Type information for variables and expressions."""
    base_type: QASMType
    size: Optional[int] = None  # For array types
    is_const: bool = False
    is_array: bool = False
    
    def __str__(self):
        if self.is_array and self.size is not None:
            return f"{self.base_type.value}[{self.size}]"
        elif self.is_array:
            return f"{self.base_type.value}[]"
        else:
            return self.base_type.value
    
    def is_compatible_with(self, other: 'TypeInfo') -> bool:
        """Check if this type is compatible with another type."""
        # Same base type
        if self.base_type != other.base_type:
            # Allow numeric type promotions
            if self._is_numeric() and other._is_numeric():
                return True
            return False
        
        # Array compatibility
        if self.is_array != other.is_array:
            return False
        
        if self.is_array and self.size != other.size:
            # Allow compatible array sizes
            return self.size is None or other.size is None
        
        return True
    
    def _is_numeric(self) -> bool:
        """Check if type is numeric."""
        return self.base_type in [QASMType.INT, QASMType.UINT, QASMType.FLOAT, QASMType.ANGLE]
    
    def _is_quantum(self) -> bool:
        """Check if type is quantum."""
        return self.base_type == QASMType.QUBIT
    
    def _is_classical(self) -> bool:
        """Check if type is classical."""
        return not self._is_quantum()

class SemanticError(Exception):
    """Exception raised for semantic analysis errors."""
    
    def __init__(self, message: str, node: ASTNode):
        self.message = message
        self.node = node
        super().__init__(f"Semantic error at line {node.line}, column {node.column}: {message}")

class Symbol:
    """Symbol table entry."""
    
    def __init__(self, name: str, type_info: TypeInfo, value: Any = None, node: ASTNode = None):
        self.name = name
        self.type_info = type_info
        self.value = value
        self.node = node
        self.is_defined = value is not None

class SymbolTable:
    """Symbol table for variables and functions."""
    
    def __init__(self, parent: Optional['SymbolTable'] = None):
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
        self.scopes: List['SymbolTable'] = []
    
    def define(self, name: str, type_info: TypeInfo, value: Any = None, node: ASTNode = None) -> Symbol:
        """Define a new symbol."""
        if name in self.symbols:
            raise SemanticError(f"Symbol '{name}' already defined in this scope", node)
        
        symbol = Symbol(name, type_info, value, node)
        self.symbols[name] = symbol
        return symbol
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in this scope or parent scopes."""
        if name in self.symbols:
            return self.symbols[name]
        
        if self.parent:
            return self.parent.lookup(name)
        
        return None
    
    def get(self, name: str, node: ASTNode = None) -> Symbol:
        """Get a symbol or raise error if not found."""
        symbol = self.lookup(name)
        if symbol is None:
            raise SemanticError(f"Undefined symbol '{name}'", node)
        return symbol
    
    def enter_scope(self) -> 'SymbolTable':
        """Enter a new scope."""
        new_scope = SymbolTable(self)
        self.scopes.append(new_scope)
        return new_scope
    
    def exit_scope(self) -> Optional['SymbolTable']:
        """Exit current scope and return parent."""
        return self.parent
    
    def debug_print(self, indent=0):
        """Debug print the symbol table."""
        prefix = "  " * indent
        print(f"{prefix}Scope: {len(self.symbols)} symbols")
        for name, symbol in self.symbols.items():
            print(f"{prefix}  {name}: {symbol.type_info}")
        if self.parent:
            print(f"{prefix}Parent:")
            self.parent.debug_print(indent + 1)

class SemanticAnalyzer(ASTVisitor):
    """Semantic analyzer for OpenQASM 3.0."""
    
    def __init__(self):
        self.global_scope = SymbolTable()
        self.current_scope = self.global_scope
        self.errors: List[SemanticError] = []
        self.warnings: List[str] = []
        
        # Initialize built-in functions and constants
        self._init_builtins()
    
    def _init_builtins(self):
        """Initialize built-in functions and constants."""
        # Built-in constants
        try:
            self.global_scope.define("pi", TypeInfo(QASMType.FLOAT, is_const=True), 3.141592653589793)
            self.global_scope.define("euler", TypeInfo(QASMType.FLOAT, is_const=True), 2.718281828459045)
        except:
            pass  # Constants may already be defined
        
        # Built-in functions (simplified)
        # Note: In a full implementation, these would be function types
        # Avoid common variable names like 'x', 'y' to prevent conflicts
        builtin_gates = ["h", "z", "s", "t", "cx", "cy", "cz", "swap", "ccx", "ry", "rx", "rz"]
        for gate in builtin_gates:
            try:
                self.global_scope.define(gate, TypeInfo(QASMType.VOID))
            except:
                pass  # Gate may already be defined
    
    def analyze(self, program: Program) -> bool:
        """
        Analyze a program for semantic correctness.
        
        Args:
            program: Program AST node
            
        Returns:
            True if analysis succeeded, False if errors found
        """
        # Reset state for new analysis
        self.global_scope = SymbolTable()
        self.current_scope = self.global_scope
        self.errors = []
        self.warnings = []
        
        # Re-initialize built-ins for each analysis
        self._init_builtins()
        
        try:
            program.accept(self)
            return len(self.errors) == 0
        except Exception as e:
            self.errors.append(SemanticError(f"Internal error: {str(e)}", program))
            return False
    
    def get_errors(self) -> List[SemanticError]:
        """Get list of semantic errors."""
        return self.errors
    
    def get_warnings(self) -> List[str]:
        """Get list of warnings."""
        return self.warnings
    
    def _error(self, message: str, node: ASTNode):
        """Record a semantic error."""
        self.errors.append(SemanticError(message, node))
    
    def _warning(self, message: str, node: ASTNode):
        """Record a warning."""
        self.warnings.append(f"Warning at line {node.line}: {message}")
    
    def _enter_scope(self):
        """Enter a new scope."""
        self.current_scope = self.current_scope.enter_scope()
    
    def _exit_scope(self):
        """Exit current scope."""
        parent = self.current_scope.exit_scope()
        if parent:
            self.current_scope = parent
    
    def visit_program(self, node: Program):
        """Visit program node."""
        # Process includes
        for include in node.includes:
            include.accept(self)
        
        # Process statements
        for stmt in node.statements:
            stmt.accept(self)
        
        return TypeInfo(QASMType.VOID)
    
    def visit_include_statement(self, node: IncludeStatement):
        """Visit include statement."""
        # In a full implementation, this would load and process the included file
        return TypeInfo(QASMType.VOID)
    
    def visit_variable_declaration(self, node: VariableDeclaration):
        """Visit variable declaration."""
        # Get type information
        type_info = node.type_annotation.accept(self)
        type_info.is_const = node.is_const
        
        # Check initializer if present
        if node.initializer:
            init_type = node.initializer.accept(self)
            if not type_info.is_compatible_with(init_type):
                self._error(f"Cannot initialize variable of type {type_info} with value of type {init_type}", node)
        elif node.is_const:
            self._error("Const variables must be initialized", node)
        
        # Define symbol
        try:
            self.current_scope.define(node.name, type_info, node=node)
        except SemanticError as e:
            self._error(e.message, node)
        
        return TypeInfo(QASMType.VOID)
    
    def visit_assignment(self, node: Assignment):
        """Visit assignment statement."""
        target_type = node.target.accept(self)
        value_type = node.value.accept(self)
        
        # Check if target is assignable
        if isinstance(node.target, Identifier):
            symbol = self.current_scope.lookup(node.target.name)
            if symbol and symbol.type_info.is_const:
                self._error(f"Cannot assign to const variable '{node.target.name}'", node)
        
        # Check type compatibility
        if not target_type.is_compatible_with(value_type):
            self._error(f"Cannot assign value of type {value_type} to variable of type {target_type}", node)
        
        # Check assignment operator
        if node.operator in ["+=", "-="]:
            if not target_type._is_numeric():
                self._error(f"Operator '{node.operator}' can only be used with numeric types", node)
        
        return TypeInfo(QASMType.VOID)
    
    def visit_if_statement(self, node: IfStatement):
        """Visit if statement."""
        condition_type = node.condition.accept(self)
        
        # Condition must be boolean
        if condition_type.base_type != QASMType.BOOL:
            self._error("If condition must be boolean", node)
        
        # Analyze then body
        self._enter_scope()
        for stmt in node.then_body:
            stmt.accept(self)
        self._exit_scope()
        
        # Analyze else body if present
        if node.else_body:
            self._enter_scope()
            for stmt in node.else_body:
                stmt.accept(self)
            self._exit_scope()
        
        return TypeInfo(QASMType.VOID)
    
    def visit_for_statement(self, node: ForStatement):
        """Visit for statement."""
        iterable_type = node.iterable.accept(self)
        
        # Check iterable type
        if isinstance(node.iterable, RangeExpression):
            # Range iteration - loop variable is int
            loop_var_type = TypeInfo(QASMType.INT)
        elif iterable_type.is_array:
            # Array iteration - loop variable is element type
            loop_var_type = TypeInfo(iterable_type.base_type)
        else:
            self._error("For loop iterable must be an array or range", node)
            loop_var_type = TypeInfo(QASMType.INT)  # Fallback
        
        # Enter new scope for loop body
        self._enter_scope()
        
        # Define loop variable in the new scope
        self.current_scope.define(node.variable, loop_var_type, node=node)
        
        # Analyze body
        for stmt in node.body:
            stmt.accept(self)
        
        self._exit_scope()
        
        return TypeInfo(QASMType.VOID)
    
    def visit_expression_statement(self, node: ExpressionStatement):
        """Visit expression statement."""
        node.expression.accept(self)
        return TypeInfo(QASMType.VOID)
    
    def visit_gate_definition(self, node: GateDefinition):
        """Visit gate definition."""
        # Define gate in symbol table
        gate_type = TypeInfo(QASMType.VOID)  # Gates return void
        try:
            self.current_scope.define(node.name, gate_type, node=node)
        except SemanticError as e:
            self._error(e.message, node)
        
        # Enter new scope for gate body
        self._enter_scope()
        
        # Define parameters
        for param in node.parameters:
            param_type = TypeInfo(QASMType.FLOAT)  # Parameters are typically angles
            self.current_scope.define(param, param_type)
        
        # Define qubit parameters
        for qubit in node.qubits:
            qubit_type = TypeInfo(QASMType.QUBIT)
            self.current_scope.define(qubit, qubit_type)
        
        # Analyze body
        for stmt in node.body:
            stmt.accept(self)
        
        self._exit_scope()
        
        return TypeInfo(QASMType.VOID)
    
    def visit_gate_call(self, node: GateCall):
        """Visit gate call."""
        # Check if gate is defined
        try:
            gate_symbol = self.current_scope.get(node.name, node)
        except SemanticError as e:
            self._error(e.message, node)
            return TypeInfo(QASMType.VOID)
        
        # Check parameters
        for param in node.parameters:
            param_type = param.accept(self)
            if not param_type._is_numeric():
                self._error("Gate parameters must be numeric", node)
        
        # Check qubits
        for qubit in node.qubits:
            qubit_type = qubit.accept(self)
            if qubit_type.base_type != QASMType.QUBIT:
                self._error("Gate arguments must be qubits", node)
        
        # Check modifiers
        if node.modifiers:
            for modifier in node.modifiers:
                modifier.accept(self)
        
        return TypeInfo(QASMType.VOID)
    
    def visit_gate_modifier(self, node: GateModifier):
        """Visit gate modifier."""
        if node.parameter:
            param_type = node.parameter.accept(self)
            if not param_type._is_numeric() or param_type.base_type != QASMType.INT:
                self._error("Gate modifier parameters must be integers", node)
        
        return TypeInfo(QASMType.VOID)
    
    def visit_measurement_statement(self, node: MeasurementStatement):
        """Visit measurement statement."""
        qubit_type = node.qubit.accept(self)
        if qubit_type.base_type != QASMType.QUBIT:
            self._error("Can only measure qubits", node)
        
        if node.target:
            target_type = node.target.accept(self)
            if target_type.base_type != QASMType.BIT:
                self._error("Measurement target must be a bit", node)
        
        return TypeInfo(QASMType.VOID)
    
    def visit_reset_statement(self, node: ResetStatement):
        """Visit reset statement."""
        qubit_type = node.qubit.accept(self)
        if qubit_type.base_type != QASMType.QUBIT:
            self._error("Can only reset qubits", node)
        
        return TypeInfo(QASMType.VOID)
    
    def visit_barrier_statement(self, node: BarrierStatement):
        """Visit barrier statement."""
        for qubit in node.qubits:
            qubit_type = qubit.accept(self)
            if qubit_type.base_type != QASMType.QUBIT:
                self._error("Barrier can only be applied to qubits", node)
        
        return TypeInfo(QASMType.VOID)
    
    def visit_literal(self, node: Literal):
        """Visit literal."""
        type_map = {
            'int': QASMType.INT,
            'float': QASMType.FLOAT,
            'bool': QASMType.BOOL,
            'string': QASMType.STRING
        }
        
        base_type = type_map.get(node.type_name, QASMType.STRING)
        return TypeInfo(base_type)
    
    def visit_identifier(self, node: Identifier):
        """Visit identifier."""
        try:
            symbol = self.current_scope.get(node.name, node)
            return symbol.type_info
        except SemanticError as e:
            self._error(e.message, node)
            return TypeInfo(QASMType.INT)  # Fallback
    
    def visit_binary_operation(self, node: BinaryOperation):
        """Visit binary operation."""
        left_type = node.left.accept(self)
        right_type = node.right.accept(self)
        
        # Arithmetic operations
        if node.operator in ['+', '-', '*', '/', '%', '**']:
            if not (left_type._is_numeric() and right_type._is_numeric()):
                self._error(f"Arithmetic operator '{node.operator}' requires numeric operands", node)
            
            # Return type promotion
            if left_type.base_type == QASMType.FLOAT or right_type.base_type == QASMType.FLOAT:
                return TypeInfo(QASMType.FLOAT)
            else:
                return TypeInfo(QASMType.INT)
        
        # Comparison operations
        elif node.operator in ['<', '>', '<=', '>=']:
            if not (left_type._is_numeric() and right_type._is_numeric()):
                self._error(f"Comparison operator '{node.operator}' requires numeric operands", node)
            return TypeInfo(QASMType.BOOL)
        
        # Equality operations
        elif node.operator in ['==', '!=']:
            if not left_type.is_compatible_with(right_type):
                self._error(f"Cannot compare values of types {left_type} and {right_type}", node)
            return TypeInfo(QASMType.BOOL)
        
        # Logical operations
        elif node.operator in ['&&', '||']:
            if left_type.base_type != QASMType.BOOL or right_type.base_type != QASMType.BOOL:
                self._error(f"Logical operator '{node.operator}' requires boolean operands", node)
            return TypeInfo(QASMType.BOOL)
        
        else:
            self._error(f"Unknown binary operator '{node.operator}'", node)
            return TypeInfo(QASMType.BOOL)
    
    def visit_unary_operation(self, node: UnaryOperation):
        """Visit unary operation."""
        operand_type = node.operand.accept(self)
        
        if node.operator == '!':
            if operand_type.base_type != QASMType.BOOL:
                self._error("Logical NOT requires boolean operand", node)
            return TypeInfo(QASMType.BOOL)
        
        elif node.operator in ['+', '-']:
            if not operand_type._is_numeric():
                self._error(f"Unary operator '{node.operator}' requires numeric operand", node)
            return operand_type
        
        else:
            self._error(f"Unknown unary operator '{node.operator}'", node)
            return operand_type
    
    def visit_array_access(self, node: ArrayAccess):
        """Visit array access."""
        array_type = node.array.accept(self)
        index_type = node.index.accept(self)
        
        if not array_type.is_array:
            self._error("Cannot index non-array type", node)
            return TypeInfo(QASMType.INT)  # Fallback
        
        if index_type.base_type != QASMType.INT:
            self._error("Array index must be integer", node)
        
        # Return element type (not array)
        return TypeInfo(array_type.base_type, is_array=False)
    
    def visit_array_slice(self, node: ArraySlice):
        """Visit array slice."""
        array_type = node.array.accept(self)
        
        if not array_type.is_array:
            self._error("Cannot slice non-array type", node)
            return TypeInfo(QASMType.INT)  # Fallback
        
        if node.start:
            start_type = node.start.accept(self)
            if start_type.base_type != QASMType.INT:
                self._error("Array slice start must be integer", node)
        
        if node.end:
            end_type = node.end.accept(self)
            if end_type.base_type != QASMType.INT:
                self._error("Array slice end must be integer", node)
        
        # Return array type with unknown size
        return TypeInfo(array_type.base_type, is_array=True)
    
    def visit_function_call(self, node: FunctionCall):
        """Visit function call."""
        # In a full implementation, this would check function signatures
        # For now, assume all function calls return appropriate types
        
        # Check if function is defined
        try:
            symbol = self.current_scope.get(node.name, node)
        except SemanticError as e:
            self._error(e.message, node)
        
        # Check arguments
        for arg in node.arguments:
            arg.accept(self)
        
        # Return type depends on function
        if node.name in ["sin", "cos", "tan", "exp", "log", "sqrt"]:
            return TypeInfo(QASMType.FLOAT)
        elif node.name in ["abs", "floor", "ceil"]:
            return TypeInfo(QASMType.INT)
        else:
            return TypeInfo(QASMType.VOID)
    
    def visit_type_annotation(self, node: TypeAnnotation):
        """Visit type annotation."""
        type_map = {
            'qubit': QASMType.QUBIT,
            'bit': QASMType.BIT,
            'int': QASMType.INT,
            'uint': QASMType.UINT,
            'float': QASMType.FLOAT,
            'angle': QASMType.ANGLE,
            'bool': QASMType.BOOL
        }
        
        base_type = type_map.get(node.base_type, QASMType.INT)
        
        if node.size:
            size_type = node.size.accept(self)
            if size_type.base_type != QASMType.INT:
                self._error("Array size must be integer", node)
            
            # Try to get constant value for validation
            size = None
            if isinstance(node.size, Literal) and isinstance(node.size.value, int):
                size = node.size.value
                if size <= 0:
                    self._error("Array size must be positive", node)
            elif isinstance(node.size, Identifier):
                # Check if it's a const variable
                symbol = self.current_scope.lookup(node.size.name)
                if symbol and symbol.type_info.is_const and symbol.value is not None:
                    if isinstance(symbol.value, int):
                        size = symbol.value
                        if size <= 0:
                            self._error("Array size must be positive", node)
            
            return TypeInfo(base_type, size=size, is_array=True)
        else:
            return TypeInfo(base_type)
    
    def visit_range_expression(self, node: RangeExpression):
        """Visit range expression."""
        if node.start:
            start_type = node.start.accept(self)
            if start_type.base_type not in [QASMType.INT, QASMType.UINT]:
                self._error("Range start must be integer", node)
        
        if node.stop:
            stop_type = node.stop.accept(self)
            if stop_type.base_type not in [QASMType.INT, QASMType.UINT]:
                self._error("Range stop must be integer", node)
        
        if node.step:
            step_type = node.step.accept(self)
            if step_type.base_type not in [QASMType.INT, QASMType.UINT]:
                self._error("Range step must be integer", node)
        
        # Range is an iterable of integers
        return TypeInfo(QASMType.INT, is_array=True)


def test_semantic_analyzer():
    """Test the semantic analyzer."""
    from .parser import QASMParser
    
    parser = QASMParser()
    analyzer = SemanticAnalyzer()
    
    test_cases = [
        # Valid program
        '''OPENQASM 3.0;
qubit[2] q;
bit[2] c;
h q[0];
cx q[0], q[1];
measure q -> c;''',
        
        # Type error
        '''OPENQASM 3.0;
int x = true;''',  # Cannot assign bool to int
        
        # Undefined variable
        '''OPENQASM 3.0;
h undefined_qubit;''',
        
        # Array access
        '''OPENQASM 3.0;
qubit[5] q;
int i = 2;
h q[i];'''
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n--- Semantic Analysis Test {i+1} ---")
        print(f"Input:\n{test_case}")
        
        try:
            ast = parser.parse(test_case)
            success = analyzer.analyze(ast)
            
            if success:
                print("✓ Semantic analysis passed")
            else:
                print("✗ Semantic analysis failed")
                for error in analyzer.get_errors():
                    print(f"  Error: {error}")
            
            if analyzer.get_warnings():
                for warning in analyzer.get_warnings():
                    print(f"  {warning}")
                    
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_semantic_analyzer()
