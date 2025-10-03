"""
PennyLane AST Parser Module

Parses PennyLane-style quantum circuit source code into the unified CircuitAST
without executing user code. This mirrors the approach in `qiskit_parser.py`
for Iteration I features: basic gates, simple parameters, and measurements.
"""

import ast
import logging
from config.config import VERBOSE, vprint
from typing import List, Any, Set

from quantum_converters.base.circuit_ast import (
    CircuitAST, GateNode, MeasurementNode, ResetNode, BarrierNode
)


# VERBOSE is imported from config.config


class PennyLaneASTVisitor(ast.NodeVisitor):
    """
    AST visitor to extract PennyLane circuit operations.

    Assumptions (Iteration I):
    - Device declared via qml.device(..., wires=N)
    - Gates are called as qml.<Gate>(..., wires=...)
    - Measurements via qml.measure or return qml.state()/qml.expval are ignored (no classical mapping yet)
    - We support a core set of gates consistent with Iteration I
    """

    def __init__(self):
        self.operations: List[Any] = []
        self.parameters: Set[str] = set()
        self.qubits: int = 0
        self.clbits: int = 0

    # Detect qml.device(..., wires=N)
    def visit_Assign(self, node: ast.Assign) -> None:
        try:
            if isinstance(node.value, ast.Call) and self._is_qml_call(node.value, 'device'):
                self._extract_wires_from_device(node.value)
        except Exception:
            pass
        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> None:
        # Capture qml gate/measurement expressions
        try:
            if isinstance(node.value, ast.Call):
                if VERBOSE:
                    try:
                        vprint(f"[PennyLaneASTVisitor] visit_Expr: call={ast.dump(node.value, include_attributes=False)}")
                    except Exception:
                        vprint("[PennyLaneASTVisitor] visit_Expr: call=<dump failed>")
                self._handle_qml_call(node.value)
        except Exception:
            pass
        self.generic_visit(node)

    def _is_qml_call(self, call: ast.Call, attr_name: str) -> bool:
        func = call.func
        return isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) \
            and func.value.id == 'qml' and func.attr == attr_name

    def _extract_wires_from_device(self, call: ast.Call) -> None:
        for kw in call.keywords:
            if kw.arg == 'wires':
                if isinstance(kw.value, ast.Num):
                    self.qubits = int(kw.value.n)
                elif isinstance(kw.value, ast.Constant):
                    self.qubits = int(kw.value.value)
                return

    def _handle_qml_call(self, call: ast.Call) -> None:
        if not self._is_qml_call(call):
            return

        method_name = call.func.attr

        # Measurements are not mapped to classical bits in Iteration I
        if method_name in ['measure']:
            return

        gate_map = self._get_gate_mapping()

        if method_name in gate_map:
            self._log_qml_call(method_name, call)
            qubits = self._extract_wires(call)
            params = self._extract_params(call, method_name)

            if not qubits:
                return  # If no wires were resolvable, skip

            self.operations.append(GateNode(name=gate_map[method_name], qubits=qubits, parameters=params))
            if VERBOSE:
                vprint(f"[PennyLaneASTVisitor] Added op {method_name} wires={qubits} params={params}")

        # Ignore unsupported qml constructs in Iteration I (no-op)

    def _is_qml_call(self, call: ast.Call) -> bool:
        """Check if this is a qml function call."""
        return (isinstance(call.func, ast.Attribute) and
                isinstance(call.func.value, ast.Name) and
                call.func.value.id == 'qml')

    def _get_gate_mapping(self) -> dict:
        """Get mapping of PennyLane gate names to OpenQASM mnemonics."""
        return {
            'PauliX': 'x', 'PauliY': 'y', 'PauliZ': 'z',
            'Hadamard': 'h', 'S': 's', 'T': 't', 'Identity': 'id',
            'RX': 'rx', 'RY': 'ry', 'RZ': 'rz', 'PhaseShift': 'p',
            'CNOT': 'cx', 'CZ': 'cz', 'SWAP': 'swap', 'Toffoli': 'ccx'
        }

    def _log_qml_call(self, method_name: str, call: ast.Call) -> None:
        """Log detailed information about qml call if verbose."""
        if not VERBOSE:
            return

        try:
            args_dump = [ast.dump(a, include_attributes=False) for a in call.args]
        except Exception:
            args_dump = [str(a) for a in call.args]

        kw_dump = {}
        for kw in call.keywords:
            try:
                kw_dump[kw.arg] = ast.dump(kw.value, include_attributes=False)
            except Exception:
                kw_dump[kw.arg] = str(kw.value)

        vprint(f"[PennyLaneASTVisitor] qml.{method_name} raw.args={args_dump}")
        vprint(f"[PennyLaneASTVisitor] qml.{method_name} raw.keywords={kw_dump}")

    def _extract_wires(self, call: ast.Call) -> List[int]:
        # wires may appear as keyword or positional last arg
        # Prefer keyword 'wires'
        if VERBOSE:
            vprint("[PennyLaneASTVisitor]   _extract_wires")
        for kw in call.keywords:
            if kw.arg == 'wires':
                return self._parse_wires_value(kw.value)
        # Fallback: try last positional if reasonable
        if call.args:
            last = call.args[-1]
            parsed = self._parse_wires_value(last)
            if parsed:
                return parsed
        return []

    def _parse_wires_value(self, node: ast.AST) -> List[int]:
        if VERBOSE:
            try:
                vprint(f"[PennyLaneASTVisitor]     _parse_wires_value node={ast.dump(node, include_attributes=False)}")
            except Exception:
                vprint("[PennyLaneASTVisitor]     _parse_wires_value node=<dump failed>")
        if isinstance(node, ast.Num):
            return [int(node.n)]
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return [int(node.value)]
        if isinstance(node, ast.List):
            result: List[int] = []
            for elt in node.elts:
                if isinstance(elt, ast.Num):
                    result.append(int(elt.n))
                elif isinstance(elt, ast.Constant) and isinstance(elt.value, int):
                    result.append(int(elt.value))
            return result
        # Unsupported dynamic wires
        return []

    def _extract_params(self, call: ast.Call, method_name: str) -> List[Any]:
        params: List[Any] = []
        # Parameterized for RX/RY/RZ/PhaseShift: first arg is angle
        if method_name in ['RX', 'RY', 'RZ', 'PhaseShift'] and call.args:
            angle = call.args[0]
            params.append(self._extract_parameter(angle))
        if VERBOSE:
            vprint(f"[PennyLaneASTVisitor]   _extract_params method={method_name} -> {params}")
        return params

    def _extract_parameter(self, node: ast.AST):
        if VERBOSE:
            self._log_parameter_extraction(node)

        # Route to appropriate handler based on node type
        if isinstance(node, ast.Num):
            return self._handle_num_parameter(node)
        elif isinstance(node, ast.Constant):
            return self._handle_constant_parameter(node)
        elif isinstance(node, ast.Name):
            return self._handle_name_parameter(node)
        elif isinstance(node, ast.UnaryOp):
            return self._handle_unary_op_parameter(node)
        elif isinstance(node, ast.Attribute):
            return self._handle_attribute_parameter(node)
        elif isinstance(node, ast.BinOp):
            return self._handle_binary_op_parameter(node)
        else:
            return 'expr'  # Fallback

    def _log_parameter_extraction(self, node: ast.AST) -> None:
        """Log parameter extraction details if verbose."""
        if not VERBOSE:
            return
        try:
            vprint(f"[PennyLaneASTVisitor]   _extract_parameter node={ast.dump(node, include_attributes=False)}")
        except Exception:
            vprint("[PennyLaneASTVisitor]   _extract_parameter node=<dump failed>")

    def _handle_num_parameter(self, node: ast.Num):
        """Handle numeric literal parameters."""
        return node.n

    def _handle_constant_parameter(self, node: ast.Constant):
        """Handle constant parameters (Python 3.8+)."""
        return node.value

    def _handle_name_parameter(self, node: ast.Name):
        """Handle named/symbolic parameters."""
        self.parameters.add(node.id)
        return node.id

    def _handle_unary_op_parameter(self, node: ast.UnaryOp):
        """Handle unary operations (like negation)."""
        if isinstance(node.op, ast.USub):
            inner = self._extract_parameter(node.operand)
            return f"-{inner}" if isinstance(inner, (str, int, float)) else inner
        return 'expr'

    def _handle_attribute_parameter(self, node: ast.Attribute):
        """Handle attribute access (like np.pi)."""
        if (isinstance(node.value, ast.Name) and
            node.value.id in ('np', 'numpy') and
            node.attr == 'pi'):
            return 'PI'
        return 'expr'

    def _handle_binary_op_parameter(self, node: ast.BinOp):
        """Handle binary operations (+, -, *, /)."""
        left = self._extract_parameter(node.left)
        right = self._extract_parameter(node.right)

        if isinstance(node.op, ast.Add):
            return f"{left} + {right}"
        elif isinstance(node.op, ast.Sub):
            return f"{left} - {right}"
        elif isinstance(node.op, ast.Mult):
            return f"{left}*{right}"
        elif isinstance(node.op, ast.Div):
            return self._format_division(left, right)
        else:
            return 'expr'

    def _format_division(self, left, right):
        """Format division operations, preferring PI/n style when possible."""
        if left == 'PI' and isinstance(right, (int, float)):
            if isinstance(right, int) or float(right).is_integer():
                return f"PI/{int(right)}"
        return f"{left}/{right}"


class PennyLaneASTParser:
    """
    Parse PennyLane source into CircuitAST using static AST analysis.
    """

    def __init__(self):
        self.visitor = PennyLaneASTVisitor()

    def parse(self, source_code: str) -> CircuitAST:
        vprint("[PennyLaneASTParser] Using AST parsing for secure PennyLane code analysis")
        if VERBOSE:
            vprint("[PennyLaneASTParser] Starting AST parsing of PennyLane source code")
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            vprint(f"[PennyLaneASTParser] Syntax error during AST parsing: {e}")
            raise ValueError(f"Invalid Python syntax in source code: {e}")

        # Reset visitor
        self.visitor = PennyLaneASTVisitor()
        self.visitor.visit(tree)

        # Basic validation
        if self.visitor.qubits <= 0:
            # Default to 1 qubit if device not found, to keep builder happy
            self.visitor.qubits = 1

        circuit_ast = CircuitAST(
            qubits=self.visitor.qubits,
            clbits=self.visitor.clbits,
            operations=self.visitor.operations,
            parameters=list(self.visitor.parameters)
        )

        vprint("[PennyLaneASTParser] Built CircuitAST")
        return circuit_ast

    def get_supported_gates(self) -> List[str]:
        return [
            'PauliX', 'PauliY', 'PauliZ', 'Hadamard', 'S', 'T', 'Identity',
            'RX', 'RY', 'RZ', 'PhaseShift', 'CNOT', 'CZ', 'SWAP', 'Toffoli'
        ]

