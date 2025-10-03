"""
Cirq AST Parser Module

This module provides AST-based parsing for Cirq quantum circuit source code.
It parses Python source code using the ast module to extract circuit operations
without executing the code, providing a secure alternative to dynamic execution.

Author: QCanvas Team
Date: 2025-01-15
Version: 1.0.0
"""

import ast
import logging
from typing import List, Set, Any, Optional, Dict
from quantum_converters.base.circuit_ast import (
    CircuitAST, GateNode, MeasurementNode, ResetNode, BarrierNode
)

VERBOSE = True


class CirqASTVisitor(ast.NodeVisitor):
    """
    AST visitor that traverses Cirq source code to extract circuit operations.

    This visitor identifies:
    - QuantumCircuit instantiation and configuration
    - Gate operations (h, x, cx, etc.)
    - Measurement operations
    - Reset operations
    - Barrier operations
    - Parameter usage
    """

    def __init__(self):
        self.circuit_vars: Set[str] = set()  # Variables holding Circuit instances
        self.operations: List[Any] = []  # Circuit operations in order
        self.parameters: Set[str] = set()  # Parameter names used
        self.qubits: int = 0  # Number of qubits (estimated)
        self.clbits: int = 0  # Number of classical bits (estimated)
        self.current_circuit: Optional[str] = None  # Current circuit variable being operated on
        self.qubit_vars: Dict[str, int] = {}  # Map variable names to qubit indices
        self.qubit_counter: int = 0  # Counter for qubit indices

    def visit_Assign(self, node: ast.Assign) -> None:
        """Handle variable assignments, particularly Circuit creation."""
        # Check if assigning a Circuit
        if isinstance(node.value, ast.Call) and self._is_cirq_circuit_call(node.value):
            # Track the variable name
            if isinstance(node.targets[0], ast.Name):
                var_name = node.targets[0].id
                self.circuit_vars.add(var_name)
                self.current_circuit = var_name

            # Parse Circuit constructor arguments (operations)
            self._parse_circuit_constructor_args(node.value)

        # Check for qubit assignments (LineQubit.range, etc.)
        elif isinstance(node.value, ast.Call) and self._is_qubit_creation(node.value):
            self._handle_qubit_creation(node.targets[0], node.value)

        # Check for method calls on circuit variables
        elif isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
            self._handle_circuit_method_call(node.value)

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Handle function definitions, particularly get_circuit()."""
        # Parse the function body for circuit operations
        for stmt in node.body:
            self.visit(stmt)
        # Don't call generic_visit to avoid double processing

    def visit_Expr(self, node: ast.Expr) -> None:
        """Handle expression statements, typically method calls."""
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
            self._handle_circuit_method_call(node.value)
        self.generic_visit(node)

    def _is_cirq_circuit_call(self, node: ast.Call) -> bool:
        """Check if a call creates a Cirq Circuit."""
        if isinstance(node.func, ast.Name) and node.func.id == 'Circuit':
            return True
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'Circuit':
            return True
        return False

    def _is_qubit_creation(self, node: ast.Call) -> bool:
        """Check if a call creates qubits."""
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ['range', 'LineQubit', 'GridQubit', 'NamedQubit']:
                return True
        return False

    def _handle_qubit_creation(self, target, call_node):
        """Handle qubit creation and assignment."""
        if isinstance(target, ast.Name):
            var_name = target.id
        elif isinstance(target, ast.Tuple):
            # Handle tuple unpacking like q0, q1 = cirq.LineQubit.range(2)
            for i, elt in enumerate(target.elts):
                if isinstance(elt, ast.Name):
                    self.qubit_vars[elt.id] = self.qubit_counter
                    self.qubit_counter += 1
            return
        else:
            return

        # For single variable assignments
        if isinstance(call_node.func, ast.Attribute) and call_node.func.attr == 'range':
            # cirq.LineQubit.range(n)
            if call_node.args and isinstance(call_node.args[0], ast.Num):
                count = call_node.args[0].n
                for i in range(count):
                    self.qubit_vars[f"{var_name}[{i}]"] = self.qubit_counter
                    self.qubit_counter += 1

    def _parse_circuit_constructor_args(self, circuit_call: ast.Call) -> None:
        """Parse arguments passed to Circuit constructor (operations)."""
        # Circuit constructor arguments are the operations to add
        for arg in circuit_call.args:
            if isinstance(arg, ast.Call):
                # This is a function call like cirq.H(q0) or cirq.measure(q0)
                self._parse_operation_call(arg)
            elif isinstance(arg, ast.List):
                # Handle list of operations
                for item in arg.elts:
                    if isinstance(item, ast.Call):
                        self._parse_operation_call(item)

    def _parse_operation_call(self, call_node: ast.Call) -> None:
        """Parse a single operation call like cirq.H(q0) or cirq.measure(q0)."""
        if isinstance(call_node.func, ast.Attribute):
            # cirq.H(q0), cirq.measure(q0), etc.
            if isinstance(call_node.func.value, ast.Name) and call_node.func.value.id == 'cirq':
                method_name = call_node.func.attr
                self._parse_gate_operation(method_name, call_node.args, call_node.keywords)
        elif isinstance(call_node.func, ast.Name):
            # Direct function calls (less common in Cirq)
            method_name = call_node.func.id
            self._parse_gate_operation(method_name, call_node.args, call_node.keywords)

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
        if method_name in ['H', 'X', 'Y', 'Z', 'S', 'T', 'SX', 'I']:
            # Single-qubit gates
            if args:
                qubit = self._extract_qubit_index(args[0])
                gate_name = method_name.lower()
                self.operations.append(GateNode(name=gate_name, qubits=[qubit]))

        elif method_name in ['CNOT', 'CX', 'CZ', 'CY', 'CH', 'SWAP']:
            # Two-qubit gates
            if len(args) >= 2:
                qubit1 = self._extract_qubit_index(args[0])
                qubit2 = self._extract_qubit_index(args[1])
                gate_name = 'cx' if method_name in ['CNOT', 'CX'] else method_name.lower()
                self.operations.append(GateNode(name=gate_name, qubits=[qubit1, qubit2]))

        elif method_name in ['Rx', 'Ry', 'Rz']:
            # Parameterized rotation gates
            if len(args) >= 2:
                qubit = self._extract_qubit_index(args[0])
                param = self._extract_parameter(args[1])
                gate_name = method_name.lower()
                self.operations.append(GateNode(
                    name=gate_name,
                    qubits=[qubit],
                    parameters=[param]
                ))

        elif method_name == 'measure':
            # Measurement operation
            if len(args) >= 1:
                qubit = self._extract_qubit_index(args[0])
                # Extract key if present
                key = None
                for kw in keywords:
                    if kw.arg == 'key' and isinstance(kw.value, ast.Str):
                        key = kw.value.s
                self.operations.append(MeasurementNode(qubit=qubit, clbit=qubit))  # Simplified: use qubit index as clbit

        elif method_name == 'reset':
            # Reset operation
            if args:
                qubit = self._extract_qubit_index(args[0])
                self.operations.append(ResetNode(qubit=qubit))

        # Add more gate types as needed

    def _extract_qubit_index(self, node: ast.expr) -> int:
        """Extract qubit index from AST node."""
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.Name):
            # Check if it's a known qubit variable
            if node.id in self.qubit_vars:
                return self.qubit_vars[node.id]
            # Could be a parameter or variable, for now return 0
            return 0
        elif isinstance(node, ast.Subscript):
            # Handle array access like qubits[0]
            if isinstance(node.value, ast.Name) and isinstance(node.slice, ast.Index):
                base_name = node.value.id
                if isinstance(node.slice.value, ast.Num):
                    index = node.slice.value.n
                    key = f"{base_name}[{index}]"
                    if key in self.qubit_vars:
                        return self.qubit_vars[key]
            return 0
        return 0

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


class CirqASTParser:
    """
    Parser for Cirq quantum circuit source code using AST parsing.

    This parser provides a secure alternative to dynamic code execution by
    analyzing the abstract syntax tree of Python source code to extract
    circuit operations.
    """

    def __init__(self):
        self.visitor = CirqASTVisitor()

    def parse(self, source_code: str) -> CircuitAST:
        """
        Parse Cirq source code and return CircuitAST representation.

        Args:
            source_code: Python source code containing Cirq circuit definition

        Returns:
            CircuitAST: Parsed circuit representation

        Raises:
            ValueError: If source code cannot be parsed or doesn't contain valid circuit
        """
        # Log that AST parsing is being used
        logging.info("Using AST parsing for secure Cirq code analysis")

        if VERBOSE:
            logging.info("VERBOSE: Starting AST parsing of Cirq source code")
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
        self.visitor = CirqASTVisitor()

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
            qubits=self.visitor.qubit_counter,  # Use the counter as estimated qubits
            clbits=self.visitor.qubit_counter,  # Assume same number for measurements
            operations=self.visitor.operations,
            parameters=list(self.visitor.parameters)
        )

        if VERBOSE:
            logging.info("VERBOSE: Successfully created CircuitAST representation")

        return circuit_ast

    def get_supported_gates(self) -> List[str]:
        """Get list of supported gate operations."""
        return [
            'h', 'x', 'y', 'z', 's', 't', 'sx', 'i',  # Single qubit
            'cx', 'cnot', 'cz', 'cy', 'ch', 'swap',  # Two qubit
            'rx', 'ry', 'rz',  # Parameterized
            'measure', 'reset'  # Special operations
        ]
