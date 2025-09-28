"""
OpenQASM 3.0 Abstract Syntax Tree (AST) Node Definitions

This module defines all AST node types for OpenQASM 3.0 Iteration I features.
Provides a clean, modular representation of the parsed syntax.

Author: QCanvas Team
Date: 2024
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Union, Any, Dict
from dataclasses import dataclass

# Base AST Node
@dataclass
class ASTNode(ABC):
    """Base class for all AST nodes."""
    line: int
    column: int
    
    @abstractmethod
    def accept(self, visitor):
        """Accept a visitor for the visitor pattern."""
        pass

# Expressions
@dataclass
class Expression(ASTNode):
    """Base class for all expressions."""
    pass

@dataclass
class Literal(Expression):
    """Literal values (integers, floats, booleans, strings)."""
    value: Union[int, float, bool, str]
    type_name: str  # 'int', 'float', 'bool', 'string'
    
    def accept(self, visitor):
        return visitor.visit_literal(self)

@dataclass
class Identifier(Expression):
    """Variable or function identifiers."""
    name: str
    
    def accept(self, visitor):
        return visitor.visit_identifier(self)

@dataclass
class BinaryOperation(Expression):
    """Binary operations (+, -, *, /, ==, !=, etc.)."""
    left: Expression
    operator: str
    right: Expression
    
    def accept(self, visitor):
        return visitor.visit_binary_operation(self)

@dataclass
class UnaryOperation(Expression):
    """Unary operations (!, -, +)."""
    operator: str
    operand: Expression
    
    def accept(self, visitor):
        return visitor.visit_unary_operation(self)

@dataclass
class ArrayAccess(Expression):
    """Array element access (arr[index])."""
    array: Expression
    index: Expression
    
    def accept(self, visitor):
        return visitor.visit_array_access(self)

@dataclass
class ArraySlice(Expression):
    """Array slice access (arr[start:end])."""
    array: Expression
    start: Optional[Expression]
    end: Optional[Expression]
    
    def accept(self, visitor):
        return visitor.visit_array_slice(self)

@dataclass
class FunctionCall(Expression):
    """Function call expression."""
    name: str
    arguments: List[Expression]
    
    def accept(self, visitor):
        return visitor.visit_function_call(self)

# Types
@dataclass
class TypeAnnotation(ASTNode):
    """Type annotations for variables."""
    base_type: str  # 'qubit', 'bit', 'int', 'uint', 'float', 'angle', 'bool'
    size: Optional[Expression] = None  # For array types
    
    def accept(self, visitor):
        return visitor.visit_type_annotation(self)

# Statements
@dataclass
class Statement(ASTNode):
    """Base class for all statements."""
    pass

@dataclass
class Program(ASTNode):
    """Root node representing the entire program."""
    version: str
    includes: List['IncludeStatement']
    statements: List[Statement]
    
    def accept(self, visitor):
        return visitor.visit_program(self)

@dataclass
class IncludeStatement(Statement):
    """Include statement for external files."""
    filename: str
    
    def accept(self, visitor):
        return visitor.visit_include_statement(self)

@dataclass
class VariableDeclaration(Statement):
    """Variable declaration with optional initialization."""
    type_annotation: TypeAnnotation
    name: str
    initializer: Optional[Expression] = None
    is_const: bool = False
    
    def accept(self, visitor):
        return visitor.visit_variable_declaration(self)

@dataclass
class Assignment(Statement):
    """Assignment statement."""
    target: Expression  # Can be identifier or array access
    operator: str  # '=', '+=', '-='
    value: Expression
    
    def accept(self, visitor):
        return visitor.visit_assignment(self)

@dataclass
class IfStatement(Statement):
    """If-else conditional statement."""
    condition: Expression
    then_body: List[Statement]
    else_body: Optional[List[Statement]] = None
    
    def accept(self, visitor):
        return visitor.visit_if_statement(self)

@dataclass
class ForStatement(Statement):
    """For loop statement."""
    variable: str
    iterable: Expression  # range() or array
    body: List[Statement]
    
    def accept(self, visitor):
        return visitor.visit_for_statement(self)

@dataclass
class ExpressionStatement(Statement):
    """Statement that wraps an expression."""
    expression: Expression
    
    def accept(self, visitor):
        return visitor.visit_expression_statement(self)

# Quantum-specific statements
@dataclass
class GateDefinition(Statement):
    """Quantum gate definition."""
    name: str
    parameters: List[str]  # Parameter names
    qubits: List[str]     # Qubit parameter names
    body: List[Statement]
    
    def accept(self, visitor):
        return visitor.visit_gate_definition(self)

@dataclass
class GateCall(Statement):
    """Quantum gate application."""
    name: str
    parameters: List[Expression]  # Actual parameter values
    qubits: List[Expression]     # Target qubits
    modifiers: List['GateModifier'] = None
    
    def accept(self, visitor):
        return visitor.visit_gate_call(self)

@dataclass
class GateModifier(ASTNode):
    """Gate modifiers (ctrl@, inv@, pow@)."""
    type: str  # 'ctrl', 'inv', 'pow'
    parameter: Optional[Expression] = None  # For ctrl@(n) or pow@(k)
    
    def accept(self, visitor):
        return visitor.visit_gate_modifier(self)

@dataclass
class MeasurementStatement(Statement):
    """Measurement operation."""
    qubit: Expression
    target: Optional[Expression] = None  # Classical bit to store result
    
    def accept(self, visitor):
        return visitor.visit_measurement_statement(self)

@dataclass
class ResetStatement(Statement):
    """Reset operation."""
    qubit: Expression
    
    def accept(self, visitor):
        return visitor.visit_reset_statement(self)

@dataclass
class BarrierStatement(Statement):
    """Barrier operation."""
    qubits: List[Expression]
    
    def accept(self, visitor):
        return visitor.visit_barrier_statement(self)

# Range expression for for loops
@dataclass
class RangeExpression(Expression):
    """Range expression for iteration."""
    start: Optional[Expression] = None
    stop: Expression = None
    step: Optional[Expression] = None
    
    def accept(self, visitor):
        return visitor.visit_range_expression(self)

# Visitor interface
class ASTVisitor(ABC):
    """Visitor interface for traversing AST nodes."""
    
    @abstractmethod
    def visit_program(self, node: Program): pass
    
    @abstractmethod
    def visit_include_statement(self, node: IncludeStatement): pass
    
    @abstractmethod
    def visit_variable_declaration(self, node: VariableDeclaration): pass
    
    @abstractmethod
    def visit_assignment(self, node: Assignment): pass
    
    @abstractmethod
    def visit_if_statement(self, node: IfStatement): pass
    
    @abstractmethod
    def visit_for_statement(self, node: ForStatement): pass
    
    @abstractmethod
    def visit_expression_statement(self, node: ExpressionStatement): pass
    
    @abstractmethod
    def visit_gate_definition(self, node: GateDefinition): pass
    
    @abstractmethod
    def visit_gate_call(self, node: GateCall): pass
    
    @abstractmethod
    def visit_gate_modifier(self, node: GateModifier): pass
    
    @abstractmethod
    def visit_measurement_statement(self, node: MeasurementStatement): pass
    
    @abstractmethod
    def visit_reset_statement(self, node: ResetStatement): pass
    
    @abstractmethod
    def visit_barrier_statement(self, node: BarrierStatement): pass
    
    @abstractmethod
    def visit_literal(self, node: Literal): pass
    
    @abstractmethod
    def visit_identifier(self, node: Identifier): pass
    
    @abstractmethod
    def visit_binary_operation(self, node: BinaryOperation): pass
    
    @abstractmethod
    def visit_unary_operation(self, node: UnaryOperation): pass
    
    @abstractmethod
    def visit_array_access(self, node: ArrayAccess): pass
    
    @abstractmethod
    def visit_array_slice(self, node: ArraySlice): pass
    
    @abstractmethod
    def visit_function_call(self, node: FunctionCall): pass
    
    @abstractmethod
    def visit_type_annotation(self, node: TypeAnnotation): pass
    
    @abstractmethod
    def visit_range_expression(self, node: RangeExpression): pass


# AST utilities
class ASTPrinter(ASTVisitor):
    """Pretty printer for AST nodes."""
    
    def __init__(self):
        self.indent_level = 0
        self.output = []
    
    def _indent(self):
        return "  " * self.indent_level
    
    def _print(self, text):
        self.output.append(self._indent() + text)
    
    def print_ast(self, node: ASTNode) -> str:
        """Print AST as a formatted string."""
        self.output = []
        self.indent_level = 0
        node.accept(self)
        return "\n".join(self.output)
    
    def visit_program(self, node: Program):
        self._print(f"Program(version={node.version})")
        self.indent_level += 1
        
        if node.includes:
            self._print("Includes:")
            self.indent_level += 1
            for include in node.includes:
                include.accept(self)
            self.indent_level -= 1
        
        if node.statements:
            self._print("Statements:")
            self.indent_level += 1
            for stmt in node.statements:
                stmt.accept(self)
            self.indent_level -= 1
        
        self.indent_level -= 1
    
    def visit_include_statement(self, node: IncludeStatement):
        self._print(f"Include({node.filename})")
    
    def visit_variable_declaration(self, node: VariableDeclaration):
        const_str = "const " if node.is_const else ""
        self._print(f"VariableDeclaration({const_str}{node.name})")
        self.indent_level += 1
        self._print("Type:")
        self.indent_level += 1
        node.type_annotation.accept(self)
        self.indent_level -= 1
        if node.initializer:
            self._print("Initializer:")
            self.indent_level += 1
            node.initializer.accept(self)
            self.indent_level -= 1
        self.indent_level -= 1
    
    def visit_assignment(self, node: Assignment):
        self._print(f"Assignment({node.operator})")
        self.indent_level += 1
        self._print("Target:")
        self.indent_level += 1
        node.target.accept(self)
        self.indent_level -= 1
        self._print("Value:")
        self.indent_level += 1
        node.value.accept(self)
        self.indent_level -= 1
        self.indent_level -= 1
    
    def visit_if_statement(self, node: IfStatement):
        self._print("IfStatement")
        self.indent_level += 1
        self._print("Condition:")
        self.indent_level += 1
        node.condition.accept(self)
        self.indent_level -= 1
        self._print("Then:")
        self.indent_level += 1
        for stmt in node.then_body:
            stmt.accept(self)
        self.indent_level -= 1
        if node.else_body:
            self._print("Else:")
            self.indent_level += 1
            for stmt in node.else_body:
                stmt.accept(self)
            self.indent_level -= 1
        self.indent_level -= 1
    
    def visit_for_statement(self, node: ForStatement):
        self._print(f"ForStatement(var={node.variable})")
        self.indent_level += 1
        self._print("Iterable:")
        self.indent_level += 1
        node.iterable.accept(self)
        self.indent_level -= 1
        self._print("Body:")
        self.indent_level += 1
        for stmt in node.body:
            stmt.accept(self)
        self.indent_level -= 1
        self.indent_level -= 1
    
    def visit_expression_statement(self, node: ExpressionStatement):
        self._print("ExpressionStatement")
        self.indent_level += 1
        node.expression.accept(self)
        self.indent_level -= 1
    
    def visit_gate_definition(self, node: GateDefinition):
        self._print(f"GateDefinition({node.name})")
        self.indent_level += 1
        if node.parameters:
            self._print(f"Parameters: {', '.join(node.parameters)}")
        if node.qubits:
            self._print(f"Qubits: {', '.join(node.qubits)}")
        self._print("Body:")
        self.indent_level += 1
        for stmt in node.body:
            stmt.accept(self)
        self.indent_level -= 1
        self.indent_level -= 1
    
    def visit_gate_call(self, node: GateCall):
        self._print(f"GateCall({node.name})")
        self.indent_level += 1
        if node.modifiers:
            self._print("Modifiers:")
            self.indent_level += 1
            for mod in node.modifiers:
                mod.accept(self)
            self.indent_level -= 1
        if node.parameters:
            self._print("Parameters:")
            self.indent_level += 1
            for param in node.parameters:
                param.accept(self)
            self.indent_level -= 1
        self._print("Qubits:")
        self.indent_level += 1
        for qubit in node.qubits:
            qubit.accept(self)
        self.indent_level -= 1
        self.indent_level -= 1
    
    def visit_gate_modifier(self, node: GateModifier):
        if node.parameter:
            self._print(f"GateModifier({node.type})")
            self.indent_level += 1
            self._print("Parameter:")
            self.indent_level += 1
            node.parameter.accept(self)
            self.indent_level -= 1
            self.indent_level -= 1
        else:
            self._print(f"GateModifier({node.type})")
    
    def visit_measurement_statement(self, node: MeasurementStatement):
        self._print("MeasurementStatement")
        self.indent_level += 1
        self._print("Qubit:")
        self.indent_level += 1
        node.qubit.accept(self)
        self.indent_level -= 1
        if node.target:
            self._print("Target:")
            self.indent_level += 1
            node.target.accept(self)
            self.indent_level -= 1
        self.indent_level -= 1
    
    def visit_reset_statement(self, node: ResetStatement):
        self._print("ResetStatement")
        self.indent_level += 1
        node.qubit.accept(self)
        self.indent_level -= 1
    
    def visit_barrier_statement(self, node: BarrierStatement):
        self._print("BarrierStatement")
        self.indent_level += 1
        for qubit in node.qubits:
            qubit.accept(self)
        self.indent_level -= 1
    
    def visit_literal(self, node: Literal):
        self._print(f"Literal({node.type_name}: {node.value})")
    
    def visit_identifier(self, node: Identifier):
        self._print(f"Identifier({node.name})")
    
    def visit_binary_operation(self, node: BinaryOperation):
        self._print(f"BinaryOperation({node.operator})")
        self.indent_level += 1
        self._print("Left:")
        self.indent_level += 1
        node.left.accept(self)
        self.indent_level -= 1
        self._print("Right:")
        self.indent_level += 1
        node.right.accept(self)
        self.indent_level -= 1
        self.indent_level -= 1
    
    def visit_unary_operation(self, node: UnaryOperation):
        self._print(f"UnaryOperation({node.operator})")
        self.indent_level += 1
        node.operand.accept(self)
        self.indent_level -= 1
    
    def visit_array_access(self, node: ArrayAccess):
        self._print("ArrayAccess")
        self.indent_level += 1
        self._print("Array:")
        self.indent_level += 1
        node.array.accept(self)
        self.indent_level -= 1
        self._print("Index:")
        self.indent_level += 1
        node.index.accept(self)
        self.indent_level -= 1
        self.indent_level -= 1
    
    def visit_array_slice(self, node: ArraySlice):
        self._print("ArraySlice")
        self.indent_level += 1
        self._print("Array:")
        self.indent_level += 1
        node.array.accept(self)
        self.indent_level -= 1
        if node.start:
            self._print("Start:")
            self.indent_level += 1
            node.start.accept(self)
            self.indent_level -= 1
        if node.end:
            self._print("End:")
            self.indent_level += 1
            node.end.accept(self)
            self.indent_level -= 1
        self.indent_level -= 1
    
    def visit_function_call(self, node: FunctionCall):
        self._print(f"FunctionCall({node.name})")
        self.indent_level += 1
        for arg in node.arguments:
            arg.accept(self)
        self.indent_level -= 1
    
    def visit_type_annotation(self, node: TypeAnnotation):
        if node.size:
            self._print(f"Type({node.base_type})")
            self.indent_level += 1
            self._print("Size:")
            self.indent_level += 1
            node.size.accept(self)
            self.indent_level -= 1
            self.indent_level -= 1
        else:
            self._print(f"Type({node.base_type})")
    
    def visit_range_expression(self, node: RangeExpression):
        self._print("Range")
        self.indent_level += 1
        if node.start:
            self._print("Start:")
            self.indent_level += 1
            node.start.accept(self)
            self.indent_level -= 1
        if node.stop:
            self._print("Stop:")
            self.indent_level += 1
            node.stop.accept(self)
            self.indent_level -= 1
        if node.step:
            self._print("Step:")
            self.indent_level += 1
            node.step.accept(self)
            self.indent_level -= 1
        self.indent_level -= 1
