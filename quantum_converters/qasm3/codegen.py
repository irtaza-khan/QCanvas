"""
OpenQASM 3.0 Code Generator

This module provides code generation functionality to convert AST back to 
OpenQASM 3.0 source code. Useful for pretty-printing, optimization, and 
cross-framework conversion.

Author: QCanvas Team
Date: 2024
Version: 1.0.0
"""

from typing import List, Optional, Dict, Any
from .ast_nodes import *

class CodeGenerator(ASTVisitor):
    """Code generator that converts AST back to OpenQASM 3.0 source code."""
    
    def __init__(self, indent_size: int = 2):
        self.indent_size = indent_size
        self.indent_level = 0
        self.output: List[str] = []
        self.current_line = ""
    
    def generate(self, node: ASTNode) -> str:
        """
        Generate OpenQASM 3.0 source code from AST.
        
        Args:
            node: Root AST node
            
        Returns:
            Generated OpenQASM 3.0 source code
        """
        self.output = []
        self.current_line = ""
        self.indent_level = 0
        
        node.accept(self)
        self._flush_line()
        
        return "\n".join(self.output)
    
    def _write(self, text: str):
        """Write text to current line."""
        self.current_line += text
    
    def _writeln(self, text: str = ""):
        """Write text and start new line."""
        self.current_line += text
        self._flush_line()
    
    def _flush_line(self):
        """Flush current line to output."""
        if self.current_line.strip():
            self.output.append(self._indent() + self.current_line)
        elif self.current_line == "":
            self.output.append("")
        self.current_line = ""
    
    def _indent(self) -> str:
        """Get current indentation string."""
        return " " * (self.indent_level * self.indent_size)
    
    def _increase_indent(self):
        """Increase indentation level."""
        self.indent_level += 1
    
    def _decrease_indent(self):
        """Decrease indentation level."""
        self.indent_level = max(0, self.indent_level - 1)
    
    def visit_program(self, node: Program):
        """Generate program."""
        # Version declaration
        self._writeln(f"OPENQASM {node.version};")
        
        # Includes
        if node.includes:
            self._writeln()
            for include in node.includes:
                include.accept(self)
        
        # Statements
        if node.statements:
            self._writeln()
            for i, stmt in enumerate(node.statements):
                if i > 0:
                    self._writeln()
                stmt.accept(self)
    
    def visit_include_statement(self, node: IncludeStatement):
        """Generate include statement."""
        self._writeln(f'include "{node.filename}";')
    
    def visit_variable_declaration(self, node: VariableDeclaration):
        """Generate variable declaration."""
        if node.is_const:
            self._write("const ")
        
        # Type
        node.type_annotation.accept(self)
        self._write(f" {node.name}")
        
        # Initializer
        if node.initializer:
            self._write(" = ")
            node.initializer.accept(self)
        
        self._writeln(";")
    
    def visit_assignment(self, node: Assignment):
        """Generate assignment statement."""
        node.target.accept(self)
        self._write(f" {node.operator} ")
        node.value.accept(self)
        self._writeln(";")
    
    def visit_if_statement(self, node: IfStatement):
        """Generate if statement."""
        self._write("if (")
        node.condition.accept(self)
        self._write(") ")
        
        self._generate_block(node.then_body)
        
        if node.else_body:
            self._write(" else ")
            self._generate_block(node.else_body)
    
    def visit_for_statement(self, node: ForStatement):
        """Generate for statement."""
        self._write(f"for ({node.variable} in ")
        node.iterable.accept(self)
        self._write(") ")
        
        self._generate_block(node.body)
    
    def visit_expression_statement(self, node: ExpressionStatement):
        """Generate expression statement."""
        node.expression.accept(self)
        self._writeln(";")
    
    def visit_gate_definition(self, node: GateDefinition):
        """Generate gate definition."""
        self._write(f"gate {node.name}")
        
        # Parameters
        if node.parameters:
            self._write("(")
            for i, param in enumerate(node.parameters):
                if i > 0:
                    self._write(", ")
                self._write(param)
            self._write(")")
        
        # Qubits
        if node.qubits:
            self._write(" ")
            for i, qubit in enumerate(node.qubits):
                if i > 0:
                    self._write(", ")
                self._write(qubit)
        
        self._write(" ")
        self._generate_block(node.body)
    
    def visit_gate_call(self, node: GateCall):
        """Generate gate call."""
        # Modifiers
        if node.modifiers:
            for modifier in node.modifiers:
                modifier.accept(self)
                self._write(" ")
        
        # Gate name
        self._write(node.name)
        
        # Parameters
        if node.parameters:
            self._write("(")
            for i, param in enumerate(node.parameters):
                if i > 0:
                    self._write(", ")
                param.accept(self)
            self._write(")")
        
        # Qubits
        if node.qubits:
            self._write(" ")
            for i, qubit in enumerate(node.qubits):
                if i > 0:
                    self._write(", ")
                qubit.accept(self)
        
        self._writeln(";")
    
    def visit_gate_modifier(self, node: GateModifier):
        """Generate gate modifier."""
        self._write(f"{node.type}@")
        if node.parameter:
            self._write("(")
            node.parameter.accept(self)
            self._write(")")
    
    def visit_measurement_statement(self, node: MeasurementStatement):
        """Generate measurement statement."""
        self._write("measure ")
        node.qubit.accept(self)
        
        if node.target:
            self._write(" -> ")
            node.target.accept(self)
        
        self._writeln(";")
    
    def visit_reset_statement(self, node: ResetStatement):
        """Generate reset statement."""
        self._write("reset ")
        node.qubit.accept(self)
        self._writeln(";")
    
    def visit_barrier_statement(self, node: BarrierStatement):
        """Generate barrier statement."""
        self._write("barrier ")
        for i, qubit in enumerate(node.qubits):
            if i > 0:
                self._write(", ")
            qubit.accept(self)
        self._writeln(";")
    
    def visit_literal(self, node: Literal):
        """Generate literal."""
        if node.type_name == 'string':
            self._write(f'"{node.value}"')
        elif node.type_name == 'bool':
            self._write("true" if node.value else "false")
        else:
            self._write(str(node.value))
    
    def visit_identifier(self, node: Identifier):
        """Generate identifier."""
        self._write(node.name)
    
    def visit_binary_operation(self, node: BinaryOperation):
        """Generate binary operation."""
        # Add parentheses for clarity
        self._write("(")
        node.left.accept(self)
        self._write(f" {node.operator} ")
        node.right.accept(self)
        self._write(")")
    
    def visit_unary_operation(self, node: UnaryOperation):
        """Generate unary operation."""
        self._write(f"{node.operator}")
        if node.operator == "!":
            self._write(" ")
        node.operand.accept(self)
    
    def visit_array_access(self, node: ArrayAccess):
        """Generate array access."""
        node.array.accept(self)
        self._write("[")
        node.index.accept(self)
        self._write("]")
    
    def visit_array_slice(self, node: ArraySlice):
        """Generate array slice."""
        node.array.accept(self)
        self._write("[")
        
        if node.start:
            node.start.accept(self)
        
        self._write(":")
        
        if node.end:
            node.end.accept(self)
        
        self._write("]")
    
    def visit_function_call(self, node: FunctionCall):
        """Generate function call."""
        self._write(f"{node.name}(")
        for i, arg in enumerate(node.arguments):
            if i > 0:
                self._write(", ")
            arg.accept(self)
        self._write(")")
    
    def visit_type_annotation(self, node: TypeAnnotation):
        """Generate type annotation."""
        self._write(node.base_type)
        if node.size:
            self._write("[")
            node.size.accept(self)
            self._write("]")
    
    def visit_range_expression(self, node: RangeExpression):
        """Generate range expression."""
        self._write("range(")
        
        args = []
        if node.start is not None:
            args.append(node.start)
        if node.stop is not None:
            args.append(node.stop)
        if node.step is not None:
            args.append(node.step)
        
        for i, arg in enumerate(args):
            if i > 0:
                self._write(", ")
            arg.accept(self)
        
        self._write(")")
    
    def _generate_block(self, statements: List[Statement]):
        """Generate a block of statements."""
        if len(statements) == 1:
            # Single statement - no braces needed
            statements[0].accept(self)
        else:
            # Multiple statements - use braces
            self._writeln("{")
            self._increase_indent()
            
            for stmt in statements:
                stmt.accept(self)
            
            self._decrease_indent()
            self._write("}")


class PrettyPrinter(CodeGenerator):
    """Pretty printer with additional formatting options."""
    
    def __init__(self, indent_size: int = 2, max_line_length: int = 80):
        super().__init__(indent_size)
        self.max_line_length = max_line_length
    
    def visit_gate_call(self, node: GateCall):
        """Generate gate call with better formatting."""
        # Calculate estimated line length
        estimated_length = len(node.name)
        if node.parameters:
            estimated_length += sum(len(str(p)) for p in node.parameters) + len(node.parameters) * 2
        if node.qubits:
            estimated_length += sum(len(str(q)) for q in node.qubits) + len(node.qubits) * 2
        
        # Use multi-line format for long gate calls
        if estimated_length > self.max_line_length // 2:
            self._generate_multiline_gate_call(node)
        else:
            super().visit_gate_call(node)
    
    def _generate_multiline_gate_call(self, node: GateCall):
        """Generate multi-line gate call for better readability."""
        # Modifiers
        if node.modifiers:
            for modifier in node.modifiers:
                modifier.accept(self)
                self._write(" ")
        
        # Gate name
        self._write(node.name)
        
        # Parameters
        if node.parameters:
            self._writeln("(")
            self._increase_indent()
            for i, param in enumerate(node.parameters):
                if i > 0:
                    self._writeln(",")
                param.accept(self)
            self._writeln()
            self._decrease_indent()
            self._write(")")
        
        # Qubits
        if node.qubits:
            if len(node.qubits) > 3:
                self._writeln()
                self._increase_indent()
                for i, qubit in enumerate(node.qubits):
                    if i > 0:
                        self._writeln(",")
                    qubit.accept(self)
                self._writeln()
                self._decrease_indent()
            else:
                self._write(" ")
                for i, qubit in enumerate(node.qubits):
                    if i > 0:
                        self._write(", ")
                    qubit.accept(self)
        
        self._writeln(";")


def test_codegen():
    """Test the code generator."""
    from .parser import QASMParser
    
    parser = QASMParser()
    generator = CodeGenerator()
    pretty_printer = PrettyPrinter()
    
    test_cases = [
        # Basic program
        '''OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
h q[0];
cx q[0], q[1];
measure q -> c;''',
        
        # Control flow
        '''OPENQASM 3.0;
int x = 5;
if (x > 0) {
    x = x + 1;
} else {
    x = x - 1;
}''',
        
        # Gate definition
        '''OPENQASM 3.0;
gate bell a, b {
    h a;
    cx a, b;
}''',
        
        # Complex expressions
        '''OPENQASM 3.0;
const float pi = 3.14159;
float angle = pi / 4;
if (angle > 0 && angle < pi) {
    ry(angle) q[0];
}'''
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n--- Code Generation Test {i+1} ---")
        print(f"Original:\n{test_case}")
        
        try:
            # Parse
            ast = parser.parse(test_case)
            
            # Generate standard format
            generated = generator.generate(ast)
            print(f"\nGenerated:\n{generated}")
            
            # Generate pretty format
            pretty = pretty_printer.generate(ast)
            print(f"\nPretty:\n{pretty}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_codegen()
