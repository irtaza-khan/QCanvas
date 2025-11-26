"""
Qiskit AST Parser Module

WHAT THIS FILE DOES:
    Parses Qiskit quantum circuit source code using Python's AST module to extract
    circuit operations without executing the code. Provides secure, static analysis
    of Qiskit code to build a CircuitAST representation. Identifies QuantumCircuit
    creation, gate operations, measurements, resets, and barriers.

HOW IT LINKS TO OTHER FILES:
    - Used by: qiskit_to_qasm.py (QiskitToQASM3Converter uses QiskitASTParser)
    - Uses: circuit_ast.py (builds CircuitAST, GateNode, MeasurementNode, etc.)
    - Uses: config/config.py (VERBOSE flag for debugging output)
    - Part of: Parsers module providing framework-specific parsing logic

INPUT:
    - qiskit_source (str): Qiskit Python source code
    - Expected format: Code with QuantumCircuit() calls and gate operations (e.g., qc.h(0))
    - Used in: QiskitASTParser.parse() method

OUTPUT:
    - CircuitAST: Unified circuit representation with operations list
    - Returned by: QiskitASTParser.parse() method
    - Contains: Qubit count, classical bit count, operations (gates, measurements, etc.)

STAGE OF USE:
    - Parsing Stage: First step in AST-based conversion pipeline
    - Security Stage: Provides secure alternative to code execution
    - Used before: AST analysis and QASM code generation
    - Used by: QiskitToQASM3Converter.convert() method

TOOLS USED:
    - ast: Python's Abstract Syntax Tree module for parsing source code
    - logging: Debug logging (via config)
    - typing: Type hints for method signatures
    - re: Regular expressions for pattern matching (if needed)

PARSING STRATEGY:
    1. AST Visitor Pattern: Uses ast.NodeVisitor to traverse AST nodes
    2. Circuit Detection: Identifies QuantumCircuit() constructor calls
    3. Operation Extraction: Visits method calls on circuit variables (qc.h(), qc.cx(), etc.)
    4. Parameter Extraction: Extracts qubit indices, gate parameters, measurement mappings
    5. AST Building: Constructs CircuitAST with GateNode, MeasurementNode, etc.

ARCHITECTURE ROLE:
    Provides secure, static analysis of Qiskit code. Enables conversion without
    executing potentially unsafe user code. Part of the parsing layer that bridges
    framework-specific syntax and the unified CircuitAST representation.

Author: QCanvas Team
Date: 2025-08-10
Version: 1.0.0
"""

import ast
import re
import logging
from config.config import VERBOSE, vprint
from typing import List, Dict, Any, Optional, Set, Tuple, Union
from quantum_converters.base.circuit_ast import (
    CircuitAST, GateNode, MeasurementNode, ResetNode, BarrierNode, ForLoopNode, IfStatementNode
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
        self.variables: Dict[str, Any] = {}  # Track variable values
        self.classical_registers: Set[str] = set()  # Track classical register variable names (from measurements)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Handle variable assignments, particularly QuantumCircuit creation."""
        if VERBOSE:
            vprint("[QiskitASTVisitor] visit_Assign: inspecting assignment node")

        # First, handle variable assignments (store values)
        # BUT: Don't overwrite classical register names - they should refer to measurement results
        if isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id
            # Don't store Python variable assignments for classical register names
            # (e.g., c = [0, 0, 0] should not overwrite that c is a classical register)
            if var_name in self.classical_registers:
                if VERBOSE:
                    vprint(f"[QiskitASTVisitor] Ignoring Python assignment to classical register '{var_name}'")
                # Still continue to check for QuantumCircuit creation, but don't store the variable
            elif isinstance(node.value, ast.Constant):
                self.variables[var_name] = node.value.value
            elif isinstance(node.value, ast.Name) and node.value.id in self.variables:
                self.variables[var_name] = self.variables[node.value.id]

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

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        """Handle augmented assignments like qc.global_phase += value."""
        if VERBOSE:
            vprint("[QiskitASTVisitor] visit_AugAssign: inspecting augmented assignment node")
        # Check for qc.global_phase += value
        if isinstance(node.target, ast.Attribute) and isinstance(node.target.value, ast.Name) and node.target.value.id in self.circuit_vars and node.target.attr == 'global_phase':
            if VERBOSE:
                vprint("[QiskitASTVisitor] Detected global_phase assignment")
            param = self._extract_parameter(node.value)
            self.operations.append(GateNode(name='gphase', qubits=[], parameters=[param]))
            if VERBOSE:
                vprint(f"[QiskitASTVisitor] Added global phase gphase({param})")

        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> None:
        """Handle expression statements, typically method calls."""
        if VERBOSE:
            vprint("[QiskitASTVisitor] visit_Expr: inspecting expression node")
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
            self._handle_circuit_method_call(node.value)
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        """Handle for loops in Qiskit code."""
        if VERBOSE:
            vprint("[QiskitASTVisitor] visit_For: inspecting for loop")
        
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
            vprint(f"[QiskitASTVisitor] Added for loop: {loop_var} in range({range_start}, {range_end})")

    def visit_If(self, node: ast.If) -> None:
        """Handle if statements in Qiskit code."""
        if VERBOSE:
            vprint("[QiskitASTVisitor] visit_If: inspecting if statement")
        
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
            vprint(f"[QiskitASTVisitor] Added if statement: {condition}")

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
            # Check if it's a variable we know about
            if node.id in self.variables:
                return self.variables[node.id]
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
            # Check if it's a known classical register name (from measurements)
            var_name = node.id
            if var_name in self.classical_registers:
                # This is a classical register, return as-is (will be used in subscript like c[i])
                return var_name
            # Map common classical register variable names to OpenQASM format
            if var_name.startswith('c') and len(var_name) > 1 and var_name[1:].isdigit():
                # Handle c0, c1, etc. -> c[0], c[1]
                return f"c[{var_name[1:]}]"
            return var_name
        elif isinstance(node, ast.Subscript):
            # Handle array indexing like c[i], creg[0], m[i]
            value = self._extract_condition_operand(node.value)
            # Check if the base value is a classical register
            if isinstance(node.value, ast.Name) and node.value.id in self.classical_registers:
                # This is a classical register access (e.g., c[1]), use it directly
                if isinstance(node.slice, ast.Index):  # Python < 3.9
                    index = self._extract_condition_operand(node.slice.value)
                elif isinstance(node.slice, ast.Constant):  # Python 3.9+
                    index = str(node.slice.value)
                elif isinstance(node.slice, ast.Name):
                    index = node.slice.id
                else:
                    index = self._extract_condition_operand(node.slice)
                return f"{value}[{index}]"
            
            # Regular array indexing
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
            # Handle attribute access like creg[i] or circuit.creg[i]
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
            elif isinstance(args[0], ast.Name) and args[0].id in self.variables:
                self.qubits = self.variables[args[0].id]

        if len(args) >= 2:
            # Second argument is number of classical bits
            if isinstance(args[1], ast.Constant):
                self.clbits = int(args[1].value)
            elif isinstance(args[1], ast.Name) and args[1].id in self.variables:
                self.clbits = self.variables[args[1].id]

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
        elif method_name in ['ccx', 'ccz', 'cswap']:
            self._handle_three_qubit_gate(method_name, args)
        elif method_name == 'gphase':
            self._handle_global_phase(args)
        elif method_name in ['cp', 'crx', 'cry', 'crz', 'cu']:
            self._handle_controlled_two_qubit_gate(method_name, args)
        elif method_name == 'u':
            self._handle_universal_gate(args)
        elif method_name == 'measure':
            self._handle_measurement_qiskit(args)
        elif method_name == 'reset':
            self._handle_reset_qiskit(args)
        elif method_name == 'barrier':
            self._handle_barrier_qiskit(args)
        elif method_name == 'if_else':
            # Qiskit 2.1+ if_else method: qc.if_else(condition, true_body, false_body=None)
            self._handle_if_else_qiskit(args)

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

    def _handle_controlled_two_qubit_gate(self, method_name: str, args: List[ast.expr]) -> None:
        """Handle controlled parameterized two-qubit gates like cp, crx, cry, crz, cu."""
        param_counts = {
            'cp': 1,
            'crx': 1,
            'cry': 1,
            'crz': 1,
            'cu': 4,
        }
        required_params = param_counts.get(method_name, 0)
        total_required = required_params + 2  # parameters + two qubit indices
        if len(args) < total_required:
            return

        params = [self._extract_parameter(arg) for arg in args[:required_params]]
        control = self._extract_qubit_index(args[required_params])
        target = self._extract_qubit_index(args[required_params + 1])
        self.operations.append(GateNode(
            name=method_name,
            qubits=[control, target],
            parameters=params
        ))
        if VERBOSE:
            vprint(f"[QiskitASTVisitor] Added {method_name} gate with params {params} on q[{control}], q[{target}]")

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
        """Handle three-qubit gates like ccx, ccz, cswap."""
        if len(args) >= 3:
            q0 = self._extract_qubit_index(args[0])
            q1 = self._extract_qubit_index(args[1])
            q2 = self._extract_qubit_index(args[2])
            self.operations.append(GateNode(name=method_name, qubits=[q0, q1, q2]))
            if VERBOSE:
                vprint(f"[QiskitASTVisitor] Added three-qubit gate {method_name} on q[{q0}], q[{q1}], q[{q2}]")

    def _handle_global_phase(self, args: List[ast.expr]) -> None:
        """Handle global phase gate."""
        if args:
            param = self._extract_parameter(args[0])
            self.operations.append(GateNode(name='gphase', qubits=[], parameters=[param]))
            if VERBOSE:
                vprint(f"[QiskitASTVisitor] Added global phase gphase({param})")

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
                vprint("[QiskitASTVisitor]   rule=u_gate -> extract parameters args[0:3]; extract_qubit_index(args[3])")
            params = [self._extract_parameter(arg) for arg in args[0:3]]
            qubit = self._extract_qubit_index(args[3])
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
        elif self._is_range_call(args):
            self._handle_range_call_measurement(args)
        else:
            self._handle_single_measurement(args)

    def _is_batch_measurement(self, args: List[ast.expr]) -> bool:
        """Check if this is a batch measurement with lists of qubits and clbits."""
        return (isinstance(args[0], ast.List) and isinstance(args[1], ast.List))

    def _is_range_call(self, args: List[ast.expr]) -> bool:
        """Check if this is a range call for measurement."""
        return (isinstance(args[0], ast.Call) and isinstance(args[0].func, ast.Name) and args[0].func.id == 'range' and
                isinstance(args[1], ast.Call) and isinstance(args[1].func, ast.Name) and args[1].func.id == 'range')

    def _handle_range_call_measurement(self, args: List[ast.expr]) -> None:
        """Handle measurement of range(n) to range(n)."""
        end_q = self._extract_constant_value(args[0].args[0])
        end_c = self._extract_constant_value(args[1].args[0])
        if end_q is not None and end_c is not None and end_q == end_c:
            body = [MeasurementNode(qubit='i', clbit='i')]
            for_loop = ForLoopNode(variable='i', range_start=0, range_end=end_q, body=body)
            self.operations.append(for_loop)

    def _handle_batch_measurement(self, args: List[ast.expr]) -> None:
        """Handle measurement of multiple qubits to multiple clbits."""
        qubits = [self._extract_qubit_index(item) for item in args[0].elts]
        clbits = [self._extract_clbit_index(item) for item in args[1].elts]

        for q, c in zip(qubits, clbits):
            self.operations.append(MeasurementNode(qubit=q, clbit=c))
            if VERBOSE:
                vprint(f"[QiskitASTVisitor] Added measure q[{q}] -> c[{c}]")
        
        # Track that 'c' is a classical register (common Qiskit convention)
        self.classical_registers.add('c')

    def _handle_single_measurement(self, args: List[ast.expr]) -> None:
        """Handle measurement of a single qubit to a single clbit."""
        qubit = self._extract_qubit_index(args[0])
        clbit = self._extract_clbit_index(args[1])
        self.operations.append(MeasurementNode(qubit=qubit, clbit=clbit))
        
        # Track that 'c' is a classical register (common Qiskit convention)
        # This helps identify c[i] references in if statements as classical register access
        self.classical_registers.add('c')

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

    def _handle_if_else_qiskit(self, args: List[ast.expr]) -> None:
        """
        Handle Qiskit 2.1+ if_else method: qc.if_else(condition, true_body, false_body=None)
        
        According to Qiskit 2.1 API (https://quantum.cloud.ibm.com/docs/en/api/qiskit/2.1/qiskit.circuit.IfElseOp):
        - condition: (ClassicalRegister, int) | (Clbit, int/bool) | expr.Expr
        - true_body: QuantumCircuit
        - false_body: QuantumCircuit | None
        """
        if len(args) < 2:
            if VERBOSE:
                vprint("[QiskitASTVisitor] if_else requires at least 2 arguments (condition, true_body)")
            return
        
        # Extract condition from first argument
        condition = self._extract_qiskit_condition(args[0])
        
        # Extract true_body operations from second argument
        true_body_ops = []
        saved_operations = self.operations
        self.operations = true_body_ops
        
        # Try to extract operations from true_body (could be a variable or QuantumCircuit call)
        self._extract_circuit_body_operations(args[1])
        true_body_ops = self.operations
        
        # Extract false_body operations if present
        false_body_ops = None
        if len(args) >= 3:
            false_body_ops = []
            self.operations = false_body_ops
            self._extract_circuit_body_operations(args[2])
            false_body_ops = self.operations
        
        # Restore operations list
        self.operations = saved_operations
        
        # Create IfStatementNode
        if_stmt = IfStatementNode(
            condition=condition,
            body=true_body_ops,
            else_body=false_body_ops
        )
        self.operations.append(if_stmt)
        
        if VERBOSE:
            vprint(f"[QiskitASTVisitor] Added Qiskit if_else: {condition}")

    def _extract_qiskit_condition(self, node: ast.expr) -> str:
        """
        Extract condition from Qiskit if_else format.
        Supports: (ClassicalRegister, int), (Clbit, int/bool), or expr.Expr
        """
        # Handle tuple condition: (creg, value) or (cbit, value)
        if isinstance(node, ast.Tuple) and len(node.elts) == 2:
            register_or_bit = node.elts[0]
            value = node.elts[1]
            
            # Extract register/bit name
            reg_name = self._extract_register_or_bit_name(register_or_bit)
            
            # Extract value
            if isinstance(value, ast.Constant):
                val = str(value.value)
            elif isinstance(value, ast.Name):
                val = value.id
            else:
                val = self._extract_condition_operand(value)
            
            # Format as OpenQASM condition: c[i] == value
            # For now, assume single bit access - could be enhanced for full register comparison
            if reg_name:
                return f"{reg_name} == {val}"
        
        # Handle expression condition (fallback to general condition extraction)
        return self._extract_condition(node)

    def _extract_register_or_bit_name(self, node: ast.expr) -> str:
        """Extract classical register or bit name from AST node."""
        # Handle direct name: creg
        if isinstance(node, ast.Name):
            return node.id
        
        # Handle attribute access: circuit.creg
        if isinstance(node, ast.Attribute):
            return node.attr
        
        # Handle subscript: creg[0] -> creg[0]
        if isinstance(node, ast.Subscript):
            value = self._extract_register_or_bit_name(node.value)
            if isinstance(node.slice, ast.Index):  # Python < 3.9
                index = self._extract_condition_operand(node.slice.value)
            elif isinstance(node.slice, ast.Constant):  # Python 3.9+
                index = str(node.slice.value)
            else:
                index = self._extract_condition_operand(node.slice)
            return f"{value}[{index}]"
        
        return str(node)

    def _extract_circuit_body_operations(self, node: ast.expr) -> None:
        """
        Extract operations from a circuit body (true_body or false_body).
        Handles both variable references and QuantumCircuit constructor calls.
        Note: This is limited for AST parsing - we can't execute code to get circuit objects.
        """
        # If it's a variable name, we can't extract operations statically
        # This is a limitation of AST parsing - we'd need execution to get the circuit
        if isinstance(node, ast.Name):
            if VERBOSE:
                vprint(f"[QiskitASTVisitor] if_else body is a variable '{node.id}' - cannot extract operations statically")
            # For now, we'll skip this - in a full implementation, you might want to
            # track circuit variables and their operations
            return
        
        # If it's a QuantumCircuit constructor call, we could parse it
        # but typically bodies are passed as variables, not inline
        if isinstance(node, ast.Call):
            if self._is_quantum_circuit_call(node):
                if VERBOSE:
                    vprint("[QiskitASTVisitor] if_else body is QuantumCircuit() - parsing inline circuit")
                # Could parse the circuit constructor, but this is uncommon
                # Usually bodies are pre-created variables
                return
        
        # For other cases, try to visit the node to see if it contains operations
        # This handles cases where the body might be a more complex expression
        try:
            self.visit(node)
        except Exception:
            if VERBOSE:
                vprint(f"[QiskitASTVisitor] Could not extract operations from if_else body: {type(node).__name__}")

    def _extract_qubit_index(self, node: ast.expr) -> Union[int, str]:
        """Extract qubit index from AST node."""
        if VERBOSE:
            try:
                vprint(f"[QiskitASTVisitor]   _extract_qubit_index node={ast.dump(node, include_attributes=False)}")
            except Exception:
                vprint("[QiskitASTVisitor]   _extract_qubit_index node=<dump failed>")
        if isinstance(node, ast.Constant):  # Python 3.8+
            return node.value if isinstance(node.value, int) else 0
        elif isinstance(node, ast.Name):
            # Could be a parameter or variable, return the name
            return node.id
        return 0

    def _extract_clbit_index(self, node: ast.expr) -> Union[int, str]:
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
            return 'pi'
        return self._extract_parameter_value(node)

    def _extract_expression(self, node: ast.expr) -> str:
        """Extract simple numpy pi expressions into OpenQASM constants."""
        text = self._extract_pi_constant(node)
        if text:
            return text
        text = self._extract_pi_fraction(node)
        if text:
            return text
        text = self._extract_pi_multiplication(node)
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
            return 'pi'
        return None

    def _extract_pi_fraction(self, node: ast.expr) -> Optional[str]:
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            left, right = node.left, node.right
            if isinstance(left, ast.Attribute) and isinstance(left.value, ast.Name) and left.attr == 'pi' and left.value.id in ('np','numpy'):
                if isinstance(right, ast.Constant) and isinstance(right.value, int) and right.value in (2, 3, 4, 6, 8):
                    return f"pi/{int(right.value)}"
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
