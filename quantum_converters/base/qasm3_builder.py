"""
OpenQASM 3.0 Builder - Complete Iteration I Implementation

WHAT THIS FILE DOES:
    Provides a programmatic builder for generating OpenQASM 3.0 code. Implements
    comprehensive support for Iteration I features including types, gates, modifiers,
    control flow, and standard library. Converts CircuitAST or direct operation calls
    into syntactically correct OpenQASM 3.0 code strings.

HOW IT LINKS TO OTHER FILES:
    - Used by: All converter classes (qiskit_to_qasm.py, cirq_to_qasm.py, pennylane_to_qasm.py)
               use QASM3Builder to generate OpenQASM 3.0 code
    - Uses: circuit_ast.py (CircuitAST, GateNode, etc.) as input source
    - Uses: qasm3_gates.py (gate library and formatting utilities)
    - Uses: qasm3_expression.py (expression parsing and formatting)
    - Part of: Base module providing core code generation

INPUT:
    - CircuitAST: Unified circuit representation from parsers
    - Direct method calls: apply_gate(), add_measurement(), etc.
    - Configuration: Number of qubits, classical bits, include options
    - Used in: Converter._convert_ast_to_qasm3() methods

OUTPUT:
    - OpenQASM 3.0 code string: Complete, valid OpenQASM 3.0 program
    - Returned by: get_code() method
    - Format: Multi-line string with proper syntax and formatting

STAGE OF USE:
    - Code Generation Stage: Converts AST or operations to OpenQASM 3.0
    - Conversion Stage: Final step in converter pipeline
    - Used after: AST parsing and analysis
    - Used before: Validation and return to API

TOOLS USED:
    - re (regex): Identifier validation, slice parsing
    - numpy: Mathematical constant detection (pi, e, etc.)
    - typing: Type hints for parameters and return values
    - dataclasses: Internal data structures (QASMVariable, QASMGateDefinition, QASMAlias)

FEATURES IMPLEMENTED (Iteration I):
    - Comments and version control
    - All basic types (qubit, bit, int, uint, float, angle, bool)
    - Compile-time constants
    - Variables and global scope
    - Arrays and array operations
    - Aliasing, slicing, and concatenation
    - All gate types and modifiers (ctrl@, inv@)
    - Hierarchical gate definitions
    - Gate broadcasting
    - Built-in quantum instructions
    - Classical operations and control flow
    - Standard gate library
    - Built-in mathematical functions

ARCHITECTURE ROLE:
    Central code generation engine that produces OpenQASM 3.0 output. Handles
    all syntax generation, formatting, and feature support according to project
    scope (Iteration I features only, excluding pulse-level and timing features).

Author: QCanvas Team
Date: 2025-08-05
Version: 2.0.0 - Iteration I Complete
"""

import re
from typing import List, Dict, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
import numpy as np


@dataclass
class QASMVariable:
    """Represents a variable in OpenQASM 3.0"""
    name: str
    type: str  # qubit, bit, int, uint, float, angle, bool, complex (Iteration II)
    size: Optional[int] = None  # For arrays
    is_const: bool = False
    value: Optional[Any] = None


@dataclass
class QASMGateDefinition:
    """Represents a custom gate definition"""
    name: str
    parameters: List[str] = field(default_factory=list)
    qubits: List[str] = field(default_factory=list)
    body: List[str] = field(default_factory=list)


@dataclass
class QASMAlias:
    """Represents a register alias"""
    name: str
    target: str  # e.g., "q[0:2]"


@dataclass
class QASMSubroutine:
    """Represents a subroutine/function definition (Iteration II)"""
    name: str
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None  # None for void functions
    body: List[str] = field(default_factory=list)


class QASM3Builder:
    """
    Comprehensive OpenQASM 3.0 code builder with full Iteration I support.
    
    This class manages the generation of syntactically and semantically correct
    OpenQASM 3.0 code including all Iteration I features.
    """
    
    def __init__(self):
        """Initialize the QASM 3.0 builder."""
        self.variables: Dict[str, QASMVariable] = {}
        self.gate_definitions: Dict[str, QASMGateDefinition] = {}
        self.subroutines: Dict[str, QASMSubroutine] = {}  # Iteration II
        self.aliases: Dict[str, QASMAlias] = {}
        self.lines: List[str] = []
        self.included_files: Set[str] = set()
        self.used_math_constants: Set[str] = set()
        self._emit_math_constants: bool = True
        
        # Standard mathematical constants
        self.math_constants = {
            'pi': '3.141592653589793',
            'e': '2.718281828459045',
            'pi_2': '1.5707963267948966',  # pi/2
            'pi_4': '0.7853981633974483',  # pi/4
            'tau': '6.283185307179586',     # 2*pi
            'sqrt2': '1.4142135623730951',
            'sqrt1_2': '0.7071067811865476',  # 1/sqrt(2)
        }
        
        # Standard gate library
        self.standard_gates = {
            # Single-qubit gates
            'h', 'x', 'y', 'z', 's', 't', 'sdg', 'tdg', 'sx', 'sxdg', 'id',
            # Parameterized single-qubit gates
            'rx', 'ry', 'rz', 'p', 'u', 'u1', 'u2', 'u3',
            # Two-qubit gates
            'cx', 'cy', 'cz', 'ch', 'swap', 'crx', 'cry', 'crz', 'cp', 'cu',
            # Three-qubit gates
            'ccx', 'cswap', 'ccz',
            # Special gates
            'gphase',
        }
        
    def initialize_header(self, include_stdgates: bool = True):
        """
        Initialize OpenQASM 3 header with version and includes.
        
        Args:
            include_stdgates: Whether to include standard gate library
        """
        # OpenQASM 3.0 specification uses `OPENQASM 3.0;`
        self.lines.append("OPENQASM 3.0;")
        
        if include_stdgates:
            self.add_include("stdgates.inc")
        
        self.lines.append("")
        
    def add_include(self, filename: str):
        """Add an include statement."""
        if filename not in self.included_files:
            self.lines.append(f'include "{filename}";')
            self.included_files.add(filename)
            
    def add_comment(self, text: str, multiline: bool = False):
        """
        Add a comment to the code.
        
        Args:
            text: Comment text
            multiline: If True, use /* */ style, else //
        """
        if multiline:
            self.lines.append(f"/* {text} */")
        else:
            self.lines.append(f"// {text}")
            
    def add_mathematical_constants(self):
        """
        Add mathematical constants.

        QCanvas behavior: emit only constants that are actually referenced in the
        program. (This avoids repeating the entire constants block for every output.)
        """
        self.add_mathematical_constants_used_only()

    def add_mathematical_constants_used_only(self):
        """Add only those mathematical constants that were actually referenced."""
        ordered_used = [k for k in self.math_constants.keys() if k in self.used_math_constants]
        if not ordered_used:
            return

        self.add_comment("Mathematical constants")
        for name in ordered_used:
            # Avoid duplicating if already present.
            prefix = f"const float {name} ="
            if any(line.strip().startswith(prefix) for line in self.lines):
                continue
            self.add_constant(name, 'float', self.math_constants[name])
        self.lines.append("")
        
    def add_constant(self, name: str, type_: str, value: str):
        """
        Add a compile-time constant.
        
        Args:
            name: Constant name
            type_: Data type (int, uint, float, angle, bool)
            value: Constant value
        """
        self.variables[name] = QASMVariable(name, type_, is_const=True, value=value)
        self.lines.append(f"const {type_} {name} = {value};")
        
    def declare_qubit_register(self, name: str, size: int):
        """
        Declare a qubit register.
        
        Args:
            name: Register name
            size: Number of qubits
        """
        self.variables[name] = QASMVariable(name, 'qubit', size=size)
        self.lines.append(f"qubit[{size}] {name};")
        
    def declare_bit_register(self, name: str, size: int):
        """
        Declare a classical bit register.
        
        Args:
            name: Register name
            size: Number of bits
        """
        self.variables[name] = QASMVariable(name, 'bit', size=size)
        self.lines.append(f"bit[{size}] {name};")
        
    def declare_variable(self, name: str, type_: str, size: Optional[Union[int, List[int]]] = None, 
                        value: Optional[str] = None):
        """
        Declare a variable.
        
        Args:
            name: Variable name
            type_: Data type (int, uint, float, angle, bool)
            size: Array size (optional)
            value: Initial value (optional)
        """
        self.variables[name] = QASMVariable(name, type_, size=size, value=value)
        
        if size:
            if isinstance(size, list):
                size_str = ", ".join(str(s) for s in size)
                decl = f"{type_}[{size_str}] {name}"
            else:
                decl = f"{type_}[{size}] {name}"
        else:
            decl = f"{type_} {name}"
            
        if value is not None:
            decl += f" = {value}"
            
        self.lines.append(f"{decl};")
        
    def add_alias(self, alias_name: str, target: str):
        """
        Add a register alias.
        
        Args:
            alias_name: Name of the alias
            target: Target register/slice (e.g., "q[0:2]")
        """
        self.aliases[alias_name] = QASMAlias(alias_name, target)
        self.lines.append(f"let {alias_name} = {target};")
        
    def define_gate(self, name: str, parameters: List[str], qubits: List[str], 
                   body: List[str]):
        """
        Define a custom hierarchical gate.
        
        Args:
            name: Gate name
            parameters: List of parameter names
            qubits: List of qubit argument names
            body: List of gate operations in the body
        """
        gate_def = QASMGateDefinition(name, parameters, qubits, body)
        self.gate_definitions[name] = gate_def
        
        # Build gate definition
        param_str = f"({', '.join(parameters)})" if parameters else ""
        qubit_str = ', '.join(qubits)
        
        self.lines.append(f"gate {name}{param_str} {qubit_str} {{")
        for op in body:
            self.lines.append(f"    {op}")
        self.lines.append("}")
        
    def define_subroutine(self, name: str, parameters: List[str], return_type: Optional[str],
                         body: List[str]):
        """
        Define a subroutine/function (Iteration II).
        
        Args:
            name: Subroutine name
            parameters: List of parameter declarations (e.g., "int x", "float theta")
            return_type: Return type (None for void)
            body: List of statements in the subroutine body
        """
        subroutine = QASMSubroutine(name, parameters, return_type, body)
        self.subroutines[name] = subroutine
        
        # Build subroutine definition
        param_str = f"({', '.join(parameters)})" if parameters else "()"
        return_str = f" -> {return_type}" if return_type else ""
        
        self.lines.append(f"def {name}{param_str}{return_str} {{")
        for stmt in body:
            self.lines.append(f"    {stmt}")
        self.lines.append("}")
        
    def add_return_statement(self, expression: Optional[str] = None):
        """
        Add a return statement (Iteration II).
        
        Args:
            expression: Optional return value expression
        """
        if expression:
            self.lines.append(f"return {expression};")
        else:
            self.lines.append("return;")
        
    def apply_gate(self, gate_name: str, qubits: List[str], 
                   parameters: Optional[List[str]] = None,
                   modifiers: Optional[Dict[str, Any]] = None):
        """
        Apply a gate with optional modifiers.
        
        Args:
            gate_name: Name of the gate
            qubits: List of qubit arguments
            parameters: Optional gate parameters
            modifiers: Optional modifiers dict with keys:
                - ctrl: Number of control qubits or list of control qubits
                - inv: Boolean, whether to apply inverse
                - pow: Power to raise gate to
        """
        # Build modifier string
        modifier_str = self._build_modifier_str(modifiers)
                
        # Build parameter string
        param_str = ""
        if parameters:
            param_str = f"({', '.join(str(p) for p in parameters)})"
            
        # Build qubit string
        qubit_str = ', '.join(qubits)
        
        # Complete gate application
        gate_app = f"{modifier_str}{gate_name}{param_str} {qubit_str};"
        self.lines.append(gate_app)

    def _build_modifier_str(self, modifiers: Optional[Dict[str, Any]]) -> str:
        """
        Build the OpenQASM modifier prefix string from a modifiers dict.
        
        Supports Iteration II modifiers:
        - inv: Inverse modifier
        - ctrl: Control modifier (single int or list)
        - negctrl: Negative control modifier (Iteration II)
        - pow: Power modifier (Iteration II)
        """
        if not modifiers:
            return ""
        parts: List[str] = []
        if modifiers.get('inv'):
            parts.append("inv")
        if 'ctrl' in modifiers:
            ctrl = modifiers['ctrl']
            if isinstance(ctrl, int):
                parts.append("ctrl" if ctrl == 1 else f"ctrl({ctrl})")
            elif isinstance(ctrl, list):
                parts.append(f"ctrl({len(ctrl)})")
        if 'negctrl' in modifiers:
            negctrl = modifiers['negctrl']
            if isinstance(negctrl, int):
                parts.append("negctrl" if negctrl == 1 else f"negctrl({negctrl})")
            elif isinstance(negctrl, list):
                parts.append(f"negctrl({len(negctrl)})")
        if 'pow' in modifiers:
            parts.append(f"pow({modifiers['pow']})")
        return (" @ ".join(parts) + " @ ") if parts else ""
        
    def apply_gate_broadcast(self, gate_name: str, qubit_array: str,
                            parameters: Optional[List[str]] = None):
        """
        Apply a gate to all qubits in an array (broadcasting).
        
        Args:
            gate_name: Name of the gate
            qubit_array: Qubit array reference (e.g., "q" or "q[0:3]")
            parameters: Optional gate parameters
        """
        param_str = ""
        if parameters:
            param_str = f"({', '.join(str(p) for p in parameters)})"
            
        self.lines.append(f"{gate_name}{param_str} {qubit_array};")
        
    def add_measurement(self, qubit: str, bit: str):
        """
        Add a measurement operation.
        """
        # Keep arrow syntax for backward compatibility with existing tests and
        # downstream consumers that expect OpenQASM-style measure statements.
        self.lines.append(f"measure {qubit} -> {bit};")
        
    def add_reset(self, qubit: str):
        """
        Add a reset operation.
        
        Args:
            qubit: Qubit to reset
        """
        self.lines.append(f"reset {qubit};")
        
    def add_barrier(self, qubits: Optional[List[str]] = None):
        """
        Add a barrier operation.
        
        Args:
            qubits: Optional list of qubits (None for all qubits)
        """
        if qubits:
            qubit_str = ', '.join(qubits)
            self.lines.append(f"barrier {qubit_str};")
        else:
            self.lines.append("barrier;")
            
    def add_assignment(self, variable: str, expression: str):
        """
        Add an assignment statement.
        
        Args:
            variable: Variable name
            expression: Value expression
        """
        self.lines.append(f"{variable} = {expression};")
        
    def add_if_statement(self, condition: str, body: List[str], 
                        else_body: Optional[List[str]] = None):
        """
        Add an if statement (or if-else).
        
        Args:
            condition: Boolean condition
            body: List of statements in if block
            else_body: Optional list of statements in else block
        """
        self.lines.append(f"if ({condition}) {{")
        for stmt in body:
            self.lines.append(f"    {stmt}")
        
        if else_body:
            self.lines.append("} else {")
            for stmt in else_body:
                self.lines.append(f"    {stmt}")
                
        self.lines.append("}")
        
    def add_for_loop(self, variable: str, range_spec: str, body: List[str]):
        """
        Add a for loop.
        
        Args:
            variable: Loop variable name (can include type, e.g., "uint i")
            range_spec: Range specification (e.g., "[0:10]", "[0:n-1]" or "{0, 2, 4, 6}")
            body: List of statements in loop body
        """
        self.lines.append(f"for {variable} in {range_spec} {{")
        for stmt in body:
            # Add indentation
            if not stmt.startswith("    "):
                self.lines.append(f"    {stmt}")
            else:
                self.lines.append(stmt)
        self.lines.append("}")
        
    def add_while_loop(self, condition: str, body: List[str]):
        """
        Add a while loop (Iteration II).
        
        Args:
            condition: Loop condition expression
            body: List of statements in loop body
        """
        self.lines.append(f"while ({condition}) {{")
        for stmt in body:
            self.lines.append(f"    {stmt}")
        self.lines.append("}")
        
    def add_break_statement(self):
        """Add a break statement (Iteration II)."""
        self.lines.append("break;")
        
    def add_continue_statement(self):
        """Add a continue statement (Iteration II)."""
        self.lines.append("continue;")
        
    def _format_float_constant(self, value: float) -> Optional[str]:
        """
        Return a symbolic name if the float matches a well-known constant, else None.
        """
        if abs(value - np.pi) < 1e-10:
            return "pi"
        if abs(value - np.pi/2) < 1e-10:
            return "pi_2"
        if abs(value - np.pi/4) < 1e-10:
            return "pi_4"
        if abs(value - 2*np.pi) < 1e-10:
            return "tau"
        if abs(value - np.e) < 1e-10:
            return "e"
        if abs(value - np.sqrt(2)) < 1e-10:
            return "sqrt2"
        if abs(value - 1/np.sqrt(2)) < 1e-10:
            return "sqrt1_2"
        return None

    def format_parameter(self, param: Any) -> str:
        """
        Format a parameter value for OpenQASM output.

        Args:
            param: Parameter value (can be numeric or symbolic)

        Returns:
            Formatted parameter string
        """
        if isinstance(param, str):
            return param

        if isinstance(param, (int, float)):
            return self._format_numeric_parameter(param)

        return str(param)

    def _format_numeric_parameter(self, param: Union[int, float]) -> str:
        """Format numeric parameters, handling numpy types and constants."""
        # Handle numpy scalar types
        if hasattr(param, 'item'):
            param = param.item()

        if isinstance(param, float):
            return self._format_float_parameter(param)
        else:
            return str(param)

    def _format_float_parameter(self, param: float) -> str:
        """Format float parameters, checking for common mathematical constants."""
        constant_name = self._identify_mathematical_constant(param)
        if constant_name:
            return constant_name

        return f"{param:.10g}"

    def _identify_mathematical_constant(self, value: float) -> Optional[str]:
        """Identify common mathematical constants and return their QASM names."""
        constants = [
            (np.pi, "pi"),
            (np.pi/2, "pi_2"),
            (np.pi/3, "pi/3"),
            (np.pi/4, "pi_4"),
            (np.pi/6, "pi/6"),
            (np.pi/8, "pi/8"),
            (2*np.pi, "tau"),
            (np.e, "e"),
            (np.sqrt(2), "sqrt2"),
            (1/np.sqrt(2), "sqrt1_2"),
        ]

        for constant_value, constant_name in constants:
            if abs(value - constant_value) < 1e-10:
                if constant_name in self.math_constants:
                    self.used_math_constants.add(constant_name)
                return constant_name

        return None
        
    def add_blank_line(self):
        """Add a blank line for readability."""
        self.lines.append("")
        
    def add_section_comment(self, title: str):
        """Add a section header comment."""
        self.lines.append("")
        self.lines.append(f"// {title}")
        
    def get_code(self) -> str:
        """
        Get the complete OpenQASM 3.0 code.
        
        Returns:
            Complete QASM code as string
        """
        lines = list(self.lines)

        # Detect constant usage even when symbols appear directly in expressions.
        # (e.g., code contains `rz(pi/2)` as a string, not a numeric float.)
        used_by_scan: Set[str] = set()
        const_names = list(self.math_constants.keys())
        patterns = {name: re.compile(rf"\b{re.escape(name)}\b") for name in const_names}

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("/*"):
                continue
            # Don't treat the declarations themselves as "usage"
            if stripped.startswith("const "):
                continue
            for name, pat in patterns.items():
                if pat.search(stripped):
                    used_by_scan.add(name)

        self.used_math_constants |= used_by_scan

        # Remove any previously emitted constant block / declarations for our known constants.
        filtered: List[str] = []
        for raw in lines:
            s = raw.strip()
            if s == "// Mathematical constants":
                continue
            if s.startswith("const float "):
                m = re.match(r"^const\s+float\s+([A-Za-z_]\w*)\s*=", s)
                if m and m.group(1) in self.math_constants:
                    continue
            filtered.append(raw)
        lines = filtered

        # Inject only referenced math constants after the header/includes section.
        if self._emit_math_constants and self.used_math_constants:
            insert_at = None
            for i, line in enumerate(lines):
                if line.strip() == "":
                    insert_at = i
                    break
            if insert_at is None:
                insert_at = len(lines)

            tmp = QASM3Builder()
            tmp.lines = []
            tmp.used_math_constants = set(self.used_math_constants)
            tmp.math_constants = dict(self.math_constants)
            tmp.add_mathematical_constants_used_only()
            const_block = tmp.lines

            if const_block:
                lines = lines[:insert_at] + const_block + lines[insert_at:]

        # Whitespace normalization: remove trailing spaces + collapse blank runs.
        normalized: List[str] = []
        blank_run = 0
        for raw in lines:
            s = raw.rstrip()
            if s == "":
                blank_run += 1
                if blank_run > 1:
                    continue
                normalized.append("")
            else:
                blank_run = 0
                normalized.append(s)

        # Trim leading/trailing blank lines.
        while normalized and normalized[0] == "":
            normalized.pop(0)
        while normalized and normalized[-1] == "":
            normalized.pop()

        return "\n".join(normalized) + "\n"
        
    def validate_identifier(self, name: str) -> bool:
        """
        Validate an OpenQASM identifier.
        
        Args:
            name: Identifier to validate
            
        Returns:
            True if valid, False otherwise
        """
        # OpenQASM identifiers must start with letter or underscore
        # and contain only letters, digits, and underscores
        pattern = r'^[A-Za-z_]\w*$'
        return bool(re.match(pattern, name))
        
    def parse_slice(self, slice_str: str) -> Tuple[Optional[int], Optional[int]]:
        """
        Parse a slice expression.
        
        Args:
            slice_str: Slice string like "[0:5]" or "[3:10]"
            
        Returns:
            Tuple of (start, end) indices
        """
        match = re.match(r'\[(\d+):(\d+)\]', slice_str)
        if match:
            return int(match.group(1)), int(match.group(2))
        return None, None
        
    def concatenate_registers(self, target_name: str, parts: List[str]):
        """
        Concatenate qubit or bit register slices into an alias using ++.

        Example: concatenate_registers("q_all", ["q1", "q2[0:2]"]) ->
        let q_all = (q1 ++ q2[0:2]);
        """
        if not parts:
            return
        concat_expr = " ++ ".join(parts)
        self.lines.append(f"let {target_name} = ({concat_expr});")

    def concatenate_arrays(self, target_name: str, arrays: List[str]):
        """
        Concatenate classical arrays into a new array alias using ++.
        """
        if not arrays:
            return
        concat_expr = " ++ ".join(arrays)
        self.lines.append(f"let {target_name} = ({concat_expr});")
        
    def build_standard_prelude(self, num_qubits: int, num_clbits: int = 0,
                               include_vars: bool = True,
                               include_constants: bool = True):
        """
        Build a standard OpenQASM 3.0 prelude with common setup.
        
        Args:
            num_qubits: Number of qubits
            num_clbits: Number of classical bits
            include_vars: Whether to include common variable declarations
        """
        # Header
        self.initialize_header()
        self._emit_math_constants = bool(include_constants)
        
        # Quantum registers
        self.add_section_comment("Quantum and classical registers")
        self.declare_qubit_register('q', num_qubits)
        
        if num_clbits > 0:
            self.declare_bit_register('c', num_clbits)
        
        # Common variables
        if include_vars:
            self.add_blank_line()
            self.add_section_comment("Classical variables")
            self.declare_variable('loop_index', 'int')
            self.declare_variable('temp_angle', 'angle')
            self.declare_variable('condition_result', 'bool')
            self.declare_variable('counter', 'uint')
            self.add_blank_line()

    def add_input_directive(self, name: str, type_: str, size: Optional[Union[int, List[int]]] = None):
        """
        Add an input directive.

        Args:
            name: Identifier name
            type_: Data type (bit, int, uint, float, angle, bool)
            size: Optional array size or shape (for bit[n], int[m], array[float, n, m], etc.)
        """
        if size is not None:
            if isinstance(size, list):
                size_str = ", ".join(str(s) for s in size)
                decl = f"{type_}[{size_str}] {name}"
            else:
                decl = f"{type_}[{size}] {name}"
        else:
            decl = f"{type_} {name}"
        self.lines.append(f"input {decl};")

    def add_output_directive(self, name: str, type_: str, size: Optional[Union[int, List[int]]] = None):
        """
        Add an output directive.

        Args:
            name: Identifier name
            type_: Data type (bit, int, uint, float, angle, bool)
            size: Optional array size (for bit[n], int[m], etc.)
        """
        decl = f"{type_}[{size}] {name}" if size is not None else f"{type_} {name}"
        self.lines.append(f"output {decl};")