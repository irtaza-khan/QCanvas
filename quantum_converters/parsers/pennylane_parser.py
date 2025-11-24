"""
PennyLane AST Parser Module

WHAT THIS FILE DOES:
    Parses PennyLane quantum circuit source code using Python's AST module to extract
    circuit operations without executing the code. Provides secure, static analysis
    of PennyLane code to build a CircuitAST representation. Identifies qml.device()
    definitions, gate operations (qml.Hadamard(), qml.CNOT(), etc.), and measurements.
    Supports Iteration I features: basic gates, simple parameters, and measurements.

HOW IT LINKS TO OTHER FILES:
    - Used by: pennylane_to_qasm.py (PennyLaneToQASM3Converter uses PennyLaneASTParser)
    - Uses: circuit_ast.py (builds CircuitAST, GateNode, MeasurementNode, etc.)
    - Uses: config/mappings.py (gate name mappings via get_pl_inverse_qasm_map())
    - Uses: config/config.py (VERBOSE flag for debugging output)
    - Part of: Parsers module providing framework-specific parsing logic

INPUT:
    - pennylane_code (str): PennyLane Python source code
    - Expected format: Code with qml.device() and qml operations (e.g., qml.Hadamard(wires=0))
    - Used in: PennyLaneASTParser.parse() method

OUTPUT:
    - CircuitAST: Unified circuit representation with operations list
    - Returned by: PennyLaneASTParser.parse() method
    - Contains: Qubit count (from wires), operations (gates, measurements, etc.)

STAGE OF USE:
    - Parsing Stage: First step in AST-based conversion pipeline
    - Security Stage: Provides secure alternative to code execution
    - Used before: AST analysis and QASM code generation
    - Used by: PennyLaneToQASM3Converter.convert() method

TOOLS USED:
    - ast: Python's Abstract Syntax Tree module for parsing source code
    - logging: Debug logging (via config)
    - typing: Type hints for method signatures

PARSING STRATEGY:
    1. AST Visitor Pattern: Uses ast.NodeVisitor to traverse AST nodes
    2. Device Detection: Identifies qml.device() calls to extract wire count
    3. Operation Extraction: Visits qml.* function calls (qml.Hadamard(), qml.CNOT(), etc.)
    4. Wire Extraction: Extracts wire indices from keyword or positional arguments
    5. Parameter Extraction: Extracts gate parameters (angles, phases, etc.)
    6. Gate Mapping: Maps PennyLane gate names to OpenQASM mnemonics
    7. AST Building: Constructs CircuitAST with GateNode, MeasurementNode, etc.

ARCHITECTURE ROLE:
    Provides secure, static analysis of PennyLane code. Enables conversion without
    executing potentially unsafe user code. Part of the parsing layer that bridges
    framework-specific syntax and the unified CircuitAST representation.

Author: QCanvas Team
Date: 2025-08-14
Version: 1.0.0
"""

import ast
import logging
from config.config import VERBOSE, vprint
from quantum_converters.config import get_pl_inverse_qasm_map
from typing import List, Any, Set, Optional, Tuple, Dict

from quantum_converters.base.circuit_ast import (
    CircuitAST, GateNode, MeasurementNode, ResetNode, BarrierNode, ForLoopNode, IfStatementNode
)


# VERBOSE is imported from config.config


class PennyLaneASTVisitor(ast.NodeVisitor):
    """
    AST visitor to extract PennyLane circuit operations.

    Assumptions (Iteration I):
    - Device declared via qml.device(..., wires=N)
    - Gates are called as qml.<Gate>(..., wires=...)
    - Measurements via qml.measure(wires=i) are mapped to classical bits
    - We support a core set of gates consistent with Iteration I
    """

    def __init__(self):
        self.operations: List[Any] = []
        self.parameters: Set[str] = set()
        self.qubits: int = 0
        self.clbits: int = 0
        self.variables: Dict[str, Any] = {}  # Track variable assignments

    # Detect qml.device(..., wires=N) and track variable assignments
    def visit_Assign(self, node: ast.Assign) -> None:
        try:
            # Track simple variable assignments like n_bits = 8
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                var_name = node.targets[0].id
                # Handle ast.Constant (Python 3.8+)
                if isinstance(node.value, ast.Constant):
                    self.variables[var_name] = node.value.value
                    if VERBOSE:
                        vprint(f"[PennyLaneASTVisitor] Tracked variable: {var_name} = {node.value.value}")
                # Handle ast.Num (deprecated, for older Python)
                elif isinstance(node.value, ast.Num):
                    self.variables[var_name] = node.value.n
                    if VERBOSE:
                        vprint(f"[PennyLaneASTVisitor] Tracked variable (Num): {var_name} = {node.value.n}")
            
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

    def visit_For(self, node: ast.For) -> None:
        """Handle for loops in PennyLane code."""
        if VERBOSE:
            vprint("[PennyLaneASTVisitor] visit_For: inspecting for loop")
        
        # Extract loop variable
        if not isinstance(node.target, ast.Name):
            self.generic_visit(node)
            return
        
        loop_var = node.target.id
        
        # Extract range information
        range_start, range_end = self._extract_range(node.iter)
        if range_start is None or range_end is None:
            # Not a simple range() call, skip for now
            self.generic_visit(node)
            return
        
        # Collect operations in the loop body
        loop_body = []
        saved_operations = self.operations
        self.operations = loop_body
        
        # Visit all statements in the loop body
        for stmt in node.body:
            self.visit(stmt)
        
        # Restore operations list
        self.operations = saved_operations
        
        # Create ForLoopNode
        for_loop = ForLoopNode(
            variable=loop_var,
            range_start=range_start,
            range_end=range_end,
            body=loop_body
        )
        self.operations.append(for_loop)
        
        if VERBOSE:
            vprint(f"[PennyLaneASTVisitor] Added for loop: {loop_var} in range({range_start}, {range_end})")

    def visit_If(self, node: ast.If) -> None:
        """Handle if statements in PennyLane code."""
        if VERBOSE:
            vprint("[PennyLaneASTVisitor] visit_If: inspecting if statement")
        
        # Extract condition
        condition = self._extract_condition(node.test)
        
        # Collect operations in the if body
        if_body = []
        saved_operations = self.operations
        self.operations = if_body
        
        # Visit all statements in the if body
        for stmt in node.body:
            self.visit(stmt)
        
        # Collect operations in the else body (if present)
        else_body = None
        if node.orelse:
            else_body = []
            self.operations = else_body
            for stmt in node.orelse:
                self.visit(stmt)
        
        # Restore operations list
        self.operations = saved_operations
        
        # Create IfStatementNode
        if_stmt = IfStatementNode(
            condition=condition,
            body=if_body,
            else_body=else_body
        )
        self.operations.append(if_stmt)
        
        if VERBOSE:
            vprint(f"[PennyLaneASTVisitor] Added if statement: {condition}")

    def _extract_range(self, node: ast.expr) -> Tuple[Optional[int], Optional[int]]:
        """Extract range start and end from a range() call."""
        if not isinstance(node, ast.Call):
            return None, None
        
        if not isinstance(node.func, ast.Name) or node.func.id != 'range':
            return None, None
        
        # Handle range(n) -> [0:n]
        if len(node.args) == 1:
            end = self._extract_constant_value(node.args[0])
            if end is not None:
                return 0, end
        
        # Handle range(start, end) -> [start:end]
        if len(node.args) == 2:
            start = self._extract_constant_value(node.args[0])
            end = self._extract_constant_value(node.args[1])
            if start is not None and end is not None:
                return start, end
        
        return None, None

    def _extract_constant_value(self, node: ast.expr) -> Optional[int]:
        """Extract a constant integer value from an AST node."""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, int):
                return node.value
        elif isinstance(node, ast.Name):
            # Look up variable in tracked variables
            var_name = node.id
            if var_name in self.variables:
                val = self.variables[var_name]
                if isinstance(val, int):
                    if VERBOSE:
                        vprint(f"[PennyLaneASTVisitor] Resolved range variable: {var_name} = {val}")
                    return val
            return None
        return None

    def _extract_condition(self, node: ast.expr) -> str:
        """
        Extract condition expression as a string representation.
        Supports OpenQASM 3.0 condition syntax including:
        - Comparisons (==, !=, <, >, <=, >=)
        - Boolean operators (and, or, not)
        - Classical register access (c[i], m[i])
        - Variable references
        """
        # Handle boolean operators (and, or, not) - OpenQASM 3.0 supports &&, ||, !
        if isinstance(node, ast.BoolOp):
            op_str = "&&" if isinstance(node.op, ast.And) else "||"
            values = [self._extract_condition(value) for value in node.values]
            return f"({f' {op_str} '.join(values)})"
        
        # Handle unary not operator
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            operand = self._extract_condition(node.operand)
            return f"!{operand}" if not operand.startswith("(") else f"!({operand})"
        
        # Handle comparisons
        if isinstance(node, ast.Compare):
            left = self._extract_condition_operand(node.left)
            ops = [self._extract_comparison_op(op) for op in node.ops]
            comparators = [self._extract_condition_operand(comp) for comp in node.comparators]
            
            if len(ops) == 1 and len(comparators) == 1:
                return f"{left} {ops[0]} {comparators[0]}"
            # Handle chained comparisons (a < b < c) - not standard in OpenQASM but handle gracefully
            elif len(ops) > 1:
                parts = [left]
                for i, (op, comp) in enumerate(zip(ops, comparators)):
                    parts.append(f"{op} {comp}")
                return " && ".join(parts)
        
        # Handle boolean constants
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                return "true" if node.value else "false"
            return str(node.value)
        
        # Handle name references (variables, classical registers)
        if isinstance(node, ast.Name):
            # Map common Python boolean names to OpenQASM
            if node.id == "True":
                return "true"
            elif node.id == "False":
                return "false"
            return node.id
        
        # Fallback: return a string representation
        try:
            return ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
        except:
            return str(node)

    def _extract_condition_operand(self, node: ast.expr) -> str:
        """
        Extract an operand from a condition.
        Handles constants, variables, array indexing, and classical register access.
        """
        if isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.Name):
            # Check if it's a known variable that maps to a classical register
            # In PennyLane, measurement results are accessed via wires
            var_name = node.id
            # Map common classical register variable names to OpenQASM format
            if var_name.startswith('c') and len(var_name) > 1 and var_name[1:].isdigit():
                # Handle c0, c1, etc. -> c[0], c[1]
                return f"c[{var_name[1:]}]"
            return var_name
        elif isinstance(node, ast.Subscript):
            # Handle array indexing like c[i], m[i]
            value = self._extract_condition_operand(node.value)
            if isinstance(node.slice, ast.Index):  # Python < 3.9
                index = self._extract_condition_operand(node.slice.value)
            elif isinstance(node.slice, ast.Constant):  # Python 3.9+
                index = str(node.slice.value)
            elif isinstance(node.slice, ast.Name):
                # Handle variable indices like c[i]
                index = node.slice.id
            else:
                index = self._extract_condition_operand(node.slice)
            return f"{value}[{index}]"
        elif isinstance(node, ast.Attribute):
            # Handle attribute access like measurements[key]
            # For conditions, we typically want just the register name
            if isinstance(node.value, ast.Name):
                # Map common patterns: creg -> c, mreg -> m
                attr_name = node.attr
                if attr_name in ['creg', 'c']:
                    return 'c'
                elif attr_name in ['mreg', 'm']:
                    return 'm'
            return f"{self._extract_condition_operand(node.value)}.{node.attr}"
        return str(node)

    def _extract_comparison_op(self, op: ast.cmpop) -> str:
        """Extract comparison operator as string."""
        op_map = {
            ast.Eq: "==",
            ast.NotEq: "!=",
            ast.Lt: "<",
            ast.LtE: "<=",
            ast.Gt: ">",
            ast.GtE: ">=",
        }
        return op_map.get(type(op), "==")

    def _is_qml_call(self, call: ast.Call, attr_name: str) -> bool:
        func = call.func
        return isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) \
            and func.value.id == 'qml' and func.attr == attr_name

    def _extract_wires_from_device(self, call: ast.Call) -> None:
        for kw in call.keywords:
            if kw.arg == 'wires':
                if isinstance(kw.value, ast.Constant):
                    self.qubits = int(kw.value.value)
                elif isinstance(kw.value, ast.Name):
                    # Handle variable reference like wires=n_bits
                    var_name = kw.value.id
                    if var_name in self.variables:
                        self.qubits = int(self.variables[var_name])
                        if VERBOSE:
                            vprint(f"[PennyLaneASTVisitor] Resolved wires from variable: {var_name} = {self.qubits}")
                return

    def _handle_qml_call(self, call: ast.Call) -> None:
        if not self._is_qml_call(call):
            return

        method_name = call.func.attr

        # Handle measurements - qml.measure(wires=i)
        if method_name == 'measure':
            self._handle_measurement_pennylane(call)
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

    def _handle_measurement_pennylane(self, call: ast.Call) -> None:
        """
        Handle qml.measure() calls and create MeasurementNode.
        
        PennyLane measurements: qml.measure(wires=i)
        Maps to OpenQASM: c[clbit_index] = measure q[qubit_index];
        """
        wires = self._extract_wires(call)
        if not wires:
            if VERBOSE:
                vprint("[PennyLaneASTVisitor] qml.measure() with no wires found")
            return
        
        for wire in wires:
            # If wire is a variable (string), use same variable for clbit
            # This handles for loop cases like: for i in range(n): qml.measure(wires=i)
            if isinstance(wire, str):
                # Variable wire - clbit should use same variable
                clbit = wire
            else:
                # Constant wire - use sequential clbit index
                clbit = self.clbits
                self.clbits += 1
            self.operations.append(MeasurementNode(qubit=wire, clbit=clbit))
            if VERBOSE:
                vprint(f"[PennyLaneASTVisitor] Added measurement q[{wire}] -> c[{clbit}]")

    def _get_gate_mapping(self) -> dict:
        """Get mapping of PennyLane gate names to OpenQASM mnemonics."""
        # Centralized registry: invert once and reuse
        return dict(get_pl_inverse_qasm_map())

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

    def _extract_wires(self, call: ast.Call) -> List[Any]:
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

    def _parse_wires_value(self, node: ast.AST) -> List[Any]:
        if VERBOSE:
            try:
                vprint(f"[PennyLaneASTVisitor]     _parse_wires_value node={ast.dump(node, include_attributes=False)}")
            except Exception:
                vprint("[PennyLaneASTVisitor]     _parse_wires_value node=<dump failed>")
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return [int(node.value)]
        if isinstance(node, ast.Name):
            # Variable wire index (e.g., wires=i in a for loop)
            return [node.id]
        if isinstance(node, ast.List):
            result: List[Any] = []
            for elt in node.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, int):
                    result.append(int(elt.value))
                elif isinstance(elt, ast.Name):
                    result.append(elt.id)
            return result
        # Unsupported dynamic wires
        return []

    def _extract_params(self, call: ast.Call, method_name: str) -> List[Any]:
        params: List[Any] = []
        # Parameterized gates: RX/RY/RZ/PhaseShift and their controlled versions
        # Also includes GlobalPhase
        parameterized_gates = [
            'RX', 'RY', 'RZ', 'PhaseShift', 
            'CRX', 'CRY', 'CRZ', 'ControlledPhaseShift',
            'GlobalPhase'
        ]
        if method_name in parameterized_gates and call.args:
            angle = call.args[0]
            params.append(self._extract_parameter(angle))
        if VERBOSE:
            vprint(f"[PennyLaneASTVisitor]   _extract_params method={method_name} -> {params}")
        return params

    def _extract_parameter(self, node: ast.AST):
        if VERBOSE:
            self._log_parameter_extraction(node)

        # Route to appropriate handler based on node type
        if isinstance(node, ast.Constant):
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

    # Removed deprecated ast.Num handler; ast.Constant path covers ints

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
            return 'pi'
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
        """Format division operations, preferring pi/n style when possible."""
        if left == 'pi' and isinstance(right, (int, float)):
            if isinstance(right, int) or float(right).is_integer():
                return f"pi/{int(right)}"
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

        # Determine qubit count: prefer device wires; else infer from max wire index
        if self.visitor.qubits <= 0:
            self.visitor.qubits = self._infer_qubit_count()

        # Determine classical bit count: use clbits if set, else infer from qubits
        clbit_count = self.visitor.clbits if self.visitor.clbits > 0 else self.visitor.qubits

        circuit_ast = CircuitAST(
            qubits=self.visitor.qubits,
            clbits=clbit_count,
            operations=self.visitor.operations,
            parameters=list(self.visitor.parameters)
        )

        vprint("[PennyLaneASTParser] Built CircuitAST")
        return circuit_ast

    def _infer_qubit_count(self) -> int:
        """Infer qubit count from operations, for loop ranges, and variables."""
        max_qubit = 0
        
        for op in self.visitor.operations:
            # Check ForLoopNode ranges
            if isinstance(op, ForLoopNode):
                if op.range_end is not None:
                    max_qubit = max(max_qubit, op.range_end)
            # Check GateNode qubits
            elif isinstance(op, GateNode):
                for q in op.qubits:
                    if isinstance(q, int):
                        max_qubit = max(max_qubit, q + 1)
            # Check MeasurementNode qubits
            elif isinstance(op, MeasurementNode):
                if isinstance(op.qubit, int):
                    max_qubit = max(max_qubit, op.qubit + 1)
        
        # Also check variables for common patterns like n_bits
        for var_name, value in self.visitor.variables.items():
            if isinstance(value, int) and var_name in ['n_bits', 'n_qubits', 'num_qubits', 'wires']:
                max_qubit = max(max_qubit, value)
        
        return max_qubit if max_qubit > 0 else 1

    def get_supported_gates(self) -> List[str]:
        return [
            'PauliX', 'PauliY', 'PauliZ', 'Hadamard', 'S', 'T', 'Identity',
            'RX', 'RY', 'RZ', 'PhaseShift', 'CNOT', 'CZ', 'SWAP', 'Toffoli'
        ]

