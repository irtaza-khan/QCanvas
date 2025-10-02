"""
Qiskit AST Parser Module

This module provides AST-based parsing for Qiskit quantum circuit source code.
It parses Python source code using the ast module to extract circuit operations
without executing the code, providing a secure alternative to dynamic execution.

Author: QCanvas Team
Date: 2025-01-15
Version: 1.0.0
"""

import ast
import re
import logging
from typing import List, Dict, Any, Optional, Set
from quantum_converters.base.circuit_ast import (
    CircuitAST, GateNode, MeasurementNode, ResetNode, BarrierNode
)

# VERBOSE flag for debugging AST parsing
VERBOSE = True


class QiskitASTVisitor(ast.NodeVisitor):
    """
    AST visitor that traverses Qiskit source code to extract circuit operations.

    This visitor identifies:
    - QuantumCircuit instantiation and configuration
    - Gate operations (h, x, cx, etc.)
    - Measurement operations
    - Reset operations
    - Barrier operations
    - Parameter usage
    """

    def __init__(self):
        self.circuit_vars: Set[str] = set()  # Variables holding QuantumCircuit instances
        self.operations: List[Any] = []  # Circuit operations in order
        self.parameters: Set[str] = set()  # Parameter names used
        self.qubits: int = 0  # Number of qubits
        self.clbits: int = 0  # Number of classical bits
        self.current_circuit: Optional[str] = None  # Current circuit variable being operated on

    def visit_Assign(self, node: ast.Assign) -> None:
        """Handle variable assignments, particularly QuantumCircuit creation."""
        # Check if assigning a QuantumCircuit
        if isinstance(node.value, ast.Call) and self._is_quantum_circuit_call(node.value):
            # Extract circuit dimensions from arguments
            self._extract_circuit_dimensions(node.value)
            # Track the variable name
            if isinstance(node.targets[0], ast.Name):
                var_name = node.targets[0].id
                self.circuit_vars.add(var_name)
                self.current_circuit = var_name

        # Check for method calls on circuit variables
        elif isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
            self._handle_circuit_method_call(node.value)

        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> None:
        """Handle expression statements, typically method calls."""
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
            self._handle_circuit_method_call(node.value)
        self.generic_visit(node)

    def _is_quantum_circuit_call(self, node: ast.Call) -> bool:
        """Check if a call creates a QuantumCircuit."""
        if isinstance(node.func, ast.Name) and node.func.id == 'QuantumCircuit':
            return True
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'QuantumCircuit':
            return True
        return False

    def _extract_circuit_dimensions(self, node: ast.Call) -> None:
        """Extract qubits and clbits from QuantumCircuit constructor."""
        args = node.args
        if len(args) >= 1:
            # First argument is typically number of qubits
            if isinstance(args[0], ast.Num):
                self.qubits = args[0].n
            elif isinstance(args[0], ast.Constant):  # Python 3.8+
                self.qubits = args[0].value

        if len(args) >= 2:
            # Second argument is number of classical bits
            if isinstance(args[1], ast.Num):
                self.clbits = args[1].n
            elif isinstance(args[1], ast.Constant):
                self.clbits = args[1].value

    def _handle_circuit_method_call(self, node: ast.Call) -> None:
        """Handle method calls on circuit variables."""
        if not isinstance(node.func, ast.Attribute):
            return

        # Check if the method is called on a circuit variable
        if isinstance(node.func.value, ast.Name) and node.func.value.id in self.circuit_vars:
            method_name = node.func.attr
            self._parse_gate_operation(method_name, node.args, node.keywords)

    def _parse_gate_operation(self, method_name: str, args: List[ast.expr], keywords: List[ast.keyword]) -> None:
        """Parse a gate operation and add it to operations list."""
        # Handle different gate types
        if method_name in ['h', 'x', 'y', 'z', 's', 't', 'sx', 'id', 'i']:
            # Single-qubit gates
            if args:
                qubit = self._extract_qubit_index(args[0])
                self.operations.append(GateNode(name=method_name, qubits=[qubit]))

        elif method_name in ['cx', 'cnot', 'cz', 'cy', 'ch', 'swap']:
            # Two-qubit gates
            if len(args) >= 2:
                qubit1 = self._extract_qubit_index(args[0])
                qubit2 = self._extract_qubit_index(args[1])
                gate_name = 'cx' if method_name == 'cnot' else method_name
                self.operations.append(GateNode(name=gate_name, qubits=[qubit1, qubit2]))

        elif method_name in ['rx', 'ry', 'rz', 'p']:
            # Parameterized single-qubit gates
            if len(args) >= 2:
                qubit = self._extract_qubit_index(args[0])
                param = self._extract_parameter(args[1])
                self.operations.append(GateNode(
                    name=method_name,
                    qubits=[qubit],
                    parameters=[param]
                ))

        elif method_name == 'u':
            # Universal gate
            if len(args) >= 4:
                qubit = self._extract_qubit_index(args[0])
                params = [self._extract_parameter(arg) for arg in args[1:4]]
                self.operations.append(GateNode(
                    name='u',
                    qubits=[qubit],
                    parameters=params
                ))

        elif method_name == 'measure':
            # Measurement operation
            if len(args) >= 2:
                qubit = self._extract_qubit_index(args[0])
                clbit = self._extract_clbit_index(args[1])
                self.operations.append(MeasurementNode(qubit=qubit, clbit=clbit))

        elif method_name == 'reset':
            # Reset operation
            if args:
                qubit = self._extract_qubit_index(args[0])
                self.operations.append(ResetNode(qubit=qubit))

        elif method_name == 'barrier':
            # Barrier operation
            qubits = []
            if args:
                if isinstance(args[0], ast.List):
                    qubits = [self._extract_qubit_index(item) for item in args[0].elts]
                else:
                    qubits = [self._extract_qubit_index(args[0])]
            self.operations.append(BarrierNode(qubits=qubits))

    def _extract_qubit_index(self, node: ast.expr) -> int:
        """Extract qubit index from AST node."""
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.Name):
            # Could be a parameter or variable, for now return 0
            return 0
        return 0

    def _extract_clbit_index(self, node: ast.expr) -> int:
        """Extract classical bit index from AST node."""
        return self._extract_qubit_index(node)  # Same logic

    def _extract_parameter(self, node: ast.expr) -> Any:
        """Extract parameter value or name from AST node."""
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            # Parameter name
            param_name = node.id
            self.parameters.add(param_name)
            return param_name
        elif isinstance(node, ast.BinOp):
            # Mathematical expression
            return self._extract_expression(node)
        return 0

    def _extract_expression(self, node: ast.expr) -> str:
        """Extract mathematical expression as string."""
        # For simplicity, return a placeholder
        # In a full implementation, you'd parse the expression
        return "expr"


class QiskitASTParser:
    """
    Parser for Qiskit quantum circuit source code using AST parsing.

    This parser provides a secure alternative to dynamic code execution by
    analyzing the abstract syntax tree of Python source code to extract
    circuit operations.
    """

    def __init__(self):
        self.visitor = QiskitASTVisitor()

    def parse(self, source_code: str) -> CircuitAST:
        """
        Parse Qiskit source code and return CircuitAST representation.

        Args:
            source_code: Python source code containing Qiskit circuit definition

        Returns:
            CircuitAST: Parsed circuit representation

        Raises:
            ValueError: If source code cannot be parsed or doesn't contain valid circuit
        """
        # Log that AST parsing is being used
        logging.info("Using AST parsing for secure Qiskit code analysis")

        if VERBOSE:
            logging.info("VERBOSE: Starting AST parsing of Qiskit source code")
            logging.info(f"VERBOSE: Source code length: {len(source_code)} characters")

        try:
            # Parse the source code into AST
            tree = ast.parse(source_code)
            if VERBOSE:
                logging.info("VERBOSE: Successfully parsed source code into AST")
        except SyntaxError as e:
            if VERBOSE:
                logging.info(f"VERBOSE: Syntax error during AST parsing: {e}")
            raise ValueError(f"Invalid Python syntax in source code: {e}")

        # Reset visitor state
        self.visitor = QiskitASTVisitor()

        # Visit all nodes
        self.visitor.visit(tree)

        if VERBOSE:
            logging.info(f"VERBOSE: Found {len(self.visitor.operations)} operations")
            logging.info(f"VERBOSE: Circuit has {self.visitor.qubits} qubits and {self.visitor.clbits} clbits")
            logging.info(f"VERBOSE: Parameters found: {list(self.visitor.parameters)}")

        # Validate that we found a circuit
        if not self.visitor.operations:
            raise ValueError("No circuit operations found in source code. Make sure to define a get_circuit() function or circuit operations.")

        # Create CircuitAST
        circuit_ast = CircuitAST(
            qubits=self.visitor.qubits,
            clbits=self.visitor.clbits,
            operations=self.visitor.operations,
            parameters=list(self.visitor.parameters)
        )

        if VERBOSE:
            logging.info("VERBOSE: Successfully created CircuitAST representation")

        return circuit_ast

    def get_supported_gates(self) -> List[str]:
        """Get list of supported gate operations."""
        return [
            'h', 'x', 'y', 'z', 's', 't', 'sx', 'id', 'i',  # Single qubit
            'cx', 'cnot', 'cz', 'cy', 'ch', 'swap',  # Two qubit
            'rx', 'ry', 'rz', 'p', 'u',  # Parameterized
            'ccx', 'ccz', 'cswap',  # Multi-qubit
            'measure', 'reset', 'barrier'  # Special operations
        ]
