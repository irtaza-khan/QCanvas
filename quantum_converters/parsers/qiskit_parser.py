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
from config.config import VERBOSE, vprint
from typing import List, Dict, Any, Optional, Set
from quantum_converters.base.circuit_ast import (
    CircuitAST, GateNode, MeasurementNode, ResetNode, BarrierNode
)

# VERBOSE is imported from config.config


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
        if VERBOSE:
            vprint("[QiskitASTVisitor] visit_Assign: inspecting assignment node")
        # Check if assigning a QuantumCircuit
        if isinstance(node.value, ast.Call) and self._is_quantum_circuit_call(node.value):
            if VERBOSE:
                vprint("[QiskitASTVisitor] Detected QuantumCircuit constructor")
            # Extract circuit dimensions from arguments
            self._extract_circuit_dimensions(node.value)
            # Track the variable name
            if isinstance(node.targets[0], ast.Name):
                var_name = node.targets[0].id
                self.circuit_vars.add(var_name)
                self.current_circuit = var_name

        # Check for method calls on circuit variables
        elif isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
            if VERBOSE:
                vprint("[QiskitASTVisitor] Assignment invokes method; treating as circuit operation if applicable")
            self._handle_circuit_method_call(node.value)

        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> None:
        """Handle expression statements, typically method calls."""
        if VERBOSE:
            vprint("[QiskitASTVisitor] visit_Expr: inspecting expression node")
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
            if isinstance(args[0], ast.Constant):  # Python 3.8+
                self.qubits = int(args[0].value)

        if len(args) >= 2:
            # Second argument is number of classical bits
            if isinstance(args[1], ast.Constant):
                self.clbits = int(args[1].value)

    def _handle_circuit_method_call(self, node: ast.Call) -> None:
        """Handle method calls on circuit variables."""
        if not isinstance(node.func, ast.Attribute):
            return

        # Check if the method is called on a circuit variable
        if isinstance(node.func.value, ast.Name) and node.func.value.id in self.circuit_vars:
            method_name = node.func.attr
            if VERBOSE:
                vprint(f"[QiskitASTVisitor] Circuit method call detected: {method_name}")
                # Raw AST dumps for traceability
                try:
                    args_dump = [ast.dump(a, include_attributes=False) for a in node.args]
                except Exception:
                    args_dump = [str(a) for a in node.args]
                kw_dump = {}
                for kw in node.keywords:
                    try:
                        kw_dump[kw.arg] = ast.dump(kw.value, include_attributes=False)
                    except Exception:
                        kw_dump[kw.arg] = str(kw.value)
                vprint(f"[QiskitASTVisitor]   raw.args={args_dump}")
                vprint(f"[QiskitASTVisitor]   raw.keywords={kw_dump}")
            self._parse_gate_operation(method_name, node.args, node.keywords)

    def _parse_gate_operation(self, method_name: str, args: List[ast.expr], keywords: List[ast.keyword]) -> None:
        """Parse a gate operation and add it to operations list."""
        # Handle different gate types
        if VERBOSE:
            vprint(f"[QiskitASTVisitor] Parsing operation: {method_name}")
            vprint(f"[QiskitASTVisitor]   args_count={len(args)} kw_count={len(keywords)}")

        # Route to appropriate handler
        if method_name in ['h', 'x', 'y', 'z', 's', 't', 'sx', 'id', 'i']:
            self._handle_single_qubit_gate(method_name, args)
        elif method_name in ['cx', 'cnot', 'cz', 'cy', 'ch', 'swap']:
            self._handle_two_qubit_gate(method_name, args)
        elif method_name in ['rx', 'ry', 'rz', 'p']:
            self._handle_parameterized_single_qubit_gate(method_name, args)
        elif method_name in ['sdg', 'tdg']:
            self._handle_inverse_gate(method_name, args)
        elif method_name in ['ccx']:
            self._handle_three_qubit_gate(method_name, args)
        elif method_name == 'u':
            self._handle_universal_gate(args)
        elif method_name == 'measure':
            self._handle_measurement_qiskit(args)
        elif method_name == 'reset':
            self._handle_reset_qiskit(args)
        elif method_name == 'barrier':
            self._handle_barrier_qiskit(args)

    def _handle_single_qubit_gate(self, method_name: str, args: List[ast.expr]) -> None:
        """Handle single-qubit gates without parameters."""
        if args:
            qubit = self._extract_qubit_index(args[0])
            self.operations.append(GateNode(name=method_name, qubits=[qubit]))
            if VERBOSE:
                vprint(f"[QiskitASTVisitor] Added single-qubit gate {method_name} on q[{qubit}]")

    def _handle_two_qubit_gate(self, method_name: str, args: List[ast.expr]) -> None:
        """Handle two-qubit gates."""
        if len(args) >= 2:
            if VERBOSE:
                vprint("[QiskitASTVisitor]   rule=two_qubit_gate -> extract_qubit_index(args[0,1])")
            qubit1 = self._extract_qubit_index(args[0])
            qubit2 = self._extract_qubit_index(args[1])
            gate_name = 'cx' if method_name == 'cnot' else method_name
            self.operations.append(GateNode(name=gate_name, qubits=[qubit1, qubit2]))
            if VERBOSE:
                vprint(f"[QiskitASTVisitor] Added two-qubit gate {gate_name} on q[{qubit1}], q[{qubit2}]")

    def _handle_parameterized_single_qubit_gate(self, method_name: str, args: List[ast.expr]) -> None:
        """Handle parameterized single-qubit gates."""
        if len(args) >= 2:
            if VERBOSE:
                vprint("[QiskitASTVisitor]   rule=rotation_gate -> extract_parameter(args[0]); extract_qubit_index(args[1])")
            param = self._extract_parameter(args[0])
            qubit = self._extract_qubit_index(args[1])
            self.operations.append(GateNode(
                name=method_name,
                qubits=[qubit],
                parameters=[param]
            ))
            if VERBOSE:
                vprint(f"[QiskitASTVisitor] Added rotation {method_name}({param}) on q[{qubit}]")

    def _handle_three_qubit_gate(self, method_name: str, args: List[ast.expr]) -> None:
        """Handle three-qubit gates like ccx."""
        if len(args) >= 3:
            q0 = self._extract_qubit_index(args[0])
            q1 = self._extract_qubit_index(args[1])
            q2 = self._extract_qubit_index(args[2])
            self.operations.append(GateNode(name=method_name, qubits=[q0, q1, q2]))

    def _handle_inverse_gate(self, method_name: str, args: List[ast.expr]) -> None:
        """Handle inverse named gates like sdg/tdg by emitting inv modifier on s/t."""
        if len(args) >= 1:
            qubit = self._extract_qubit_index(args[0])
            base = 's' if method_name == 'sdg' else 't'
            # Represent as GateNode with modifier in metadata
            node = GateNode(name=base, qubits=[qubit], parameters=[])
            # attach a simple modifiers dict
            setattr(node, 'modifiers', {'inv': True})
            self.operations.append(node)

    def _handle_universal_gate(self, args: List[ast.expr]) -> None:
        """Handle universal U gate."""
        if len(args) >= 4:
            if VERBOSE:
                vprint("[QiskitASTVisitor]   rule=u_gate -> extract_qubit_index(args[0]); extract parameters args[1:4]")
            qubit = self._extract_qubit_index(args[0])
            params = [self._extract_parameter(arg) for arg in args[1:4]]
            self.operations.append(GateNode(
                name='u',
                qubits=[qubit],
                parameters=params
            ))
            if VERBOSE:
                vprint(f"[QiskitASTVisitor] Added u gate{tuple(params)} on q[{qubit}]")

    def _handle_measurement_qiskit(self, args: List[ast.expr]) -> None:
        """Handle measurement operations in Qiskit."""
        if len(args) < 2:
            return

        if VERBOSE:
            vprint("[QiskitASTVisitor]   rule=measure -> support list and single indices")

        if self._is_batch_measurement(args):
            self._handle_batch_measurement(args)
        else:
            self._handle_single_measurement(args)

    def _is_batch_measurement(self, args: List[ast.expr]) -> bool:
        """Check if this is a batch measurement with lists of qubits and clbits."""
        return (isinstance(args[0], ast.List) and isinstance(args[1], ast.List))

    def _handle_batch_measurement(self, args: List[ast.expr]) -> None:
        """Handle measurement of multiple qubits to multiple clbits."""
        qubits = [self._extract_qubit_index(item) for item in args[0].elts]
        clbits = [self._extract_clbit_index(item) for item in args[1].elts]

        for q, c in zip(qubits, clbits):
            self.operations.append(MeasurementNode(qubit=q, clbit=c))
            if VERBOSE:
                vprint(f"[QiskitASTVisitor] Added measure q[{q}] -> c[{c}]")

    def _handle_single_measurement(self, args: List[ast.expr]) -> None:
        """Handle measurement of a single qubit to a single clbit."""
        qubit = self._extract_qubit_index(args[0])
        clbit = self._extract_clbit_index(args[1])
        self.operations.append(MeasurementNode(qubit=qubit, clbit=clbit))

        if VERBOSE:
            vprint(f"[QiskitASTVisitor] Added measure q[{qubit}] -> c[{clbit}]")

    def _handle_reset_qiskit(self, args: List[ast.expr]) -> None:
        """Handle reset operations in Qiskit."""
        if args:
            if VERBOSE:
                vprint("[QiskitASTVisitor]   rule=reset -> extract_qubit_index(args[0])")
            qubit = self._extract_qubit_index(args[0])
            self.operations.append(ResetNode(qubit=qubit))
            if VERBOSE:
                vprint(f"[QiskitASTVisitor] Added reset q[{qubit}]")

    def _handle_barrier_qiskit(self, args: List[ast.expr]) -> None:
        """Handle barrier operations in Qiskit."""
        qubits = []
        if args:
            if isinstance(args[0], ast.List):
                qubits = [self._extract_qubit_index(item) for item in args[0].elts]
            else:
                qubits = [self._extract_qubit_index(args[0])]
        self.operations.append(BarrierNode(qubits=qubits))
        if VERBOSE:
            vprint(f"[QiskitASTVisitor] Added barrier on {qubits if qubits else 'all qubits'}")

    def _extract_qubit_index(self, node: ast.expr) -> int:
        """Extract qubit index from AST node."""
        if VERBOSE:
            try:
                vprint(f"[QiskitASTVisitor]   _extract_qubit_index node={ast.dump(node, include_attributes=False)}")
            except Exception:
                vprint("[QiskitASTVisitor]   _extract_qubit_index node=<dump failed>")
        if isinstance(node, ast.Constant):  # Python 3.8+
            return node.value if isinstance(node.value, int) else 0
        elif isinstance(node, ast.Name):
            # Could be a parameter or variable, for now return 0
            return 0
        return 0

    def _extract_clbit_index(self, node: ast.expr) -> int:
        """Extract classical bit index from AST node."""
        if VERBOSE:
            try:
                vprint(f"[QiskitASTVisitor]   _extract_clbit_index node={ast.dump(node, include_attributes=False)}")
            except Exception:
                vprint("[QiskitASTVisitor]   _extract_clbit_index node=<dump failed>")
        return self._extract_qubit_index(node)  # Same logic

    def _extract_parameter(self, node: ast.expr) -> Any:
        """Extract parameter value or name from AST node."""
        if VERBOSE:
            try:
                vprint(f"[QiskitASTVisitor]   _extract_parameter node={ast.dump(node, include_attributes=False)}")
            except Exception:
                vprint("[QiskitASTVisitor]   _extract_parameter node=<dump failed>")
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            # Parameter name
            param_name = node.id
            self.parameters.add(param_name)
            return param_name
        elif isinstance(node, ast.BinOp):
            # Mathematical expression
            return self._extract_expression(node)
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.attr == 'pi' and node.value.id in ('np','numpy'):
            return 'PI'
        return 0

    def _extract_expression(self, node: ast.expr) -> str:
        """Extract simple numpy pi expressions into OpenQASM constants."""
        text = self._extract_pi_constant(node)
        if text:
            return text
        text = self._extract_pi_fraction(node)
        if text:
            return text
        if VERBOSE:
            try:
                vprint(f"[QiskitASTVisitor]   _extract_expression node={ast.dump(node, include_attributes=False)}")
            except Exception:
                vprint("[QiskitASTVisitor]   _extract_expression node=<dump failed>")
        return "expr"

    def _extract_pi_constant(self, node: ast.expr) -> Optional[str]:
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.attr == 'pi' and node.value.id in ('np', 'numpy'):
            return 'PI'
        return None

    def _extract_pi_fraction(self, node: ast.expr) -> Optional[str]:
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            left, right = node.left, node.right
            if isinstance(left, ast.Attribute) and isinstance(left.value, ast.Name) and left.attr == 'pi' and left.value.id in ('np','numpy'):
                if isinstance(right, ast.Constant) and isinstance(right.value, int) and right.value in (2, 4, 8):
                    return f"PI/{int(right.value)}"
        return None


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
                vprint("[QiskitASTParser] Parsed source code into AST")
        except SyntaxError as e:
            if VERBOSE:
                vprint(f"[QiskitASTParser] Syntax error during AST parsing: {e}")
            raise ValueError(f"Invalid Python syntax in source code: {e}")

        # Reset visitor state
        self.visitor = QiskitASTVisitor()

        # Visit all nodes
        self.visitor.visit(tree)

        if VERBOSE:
            vprint(f"[QiskitASTParser] Found operations: {len(self.visitor.operations)}")
            vprint(f"[QiskitASTParser] Qubits: {self.visitor.qubits}, Clbits: {self.visitor.clbits}")
            vprint(f"[QiskitASTParser] Parameters: {list(self.visitor.parameters)}")

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
            vprint("[QiskitASTParser] Built CircuitAST")

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
