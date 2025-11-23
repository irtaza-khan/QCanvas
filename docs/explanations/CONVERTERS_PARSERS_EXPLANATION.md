# Backend Converters and Parsers: Line-by-Line Working Explanation

This document provides detailed line-by-line explanations of the backend converters and parsers in the QCanvas project, covering how they process quantum circuit code from different frameworks (Qiskit, Cirq, PennyLane) and convert them to OpenQASM 3.0 format.

---

## 1. Qiskit AST Parser (`quantum_converters/parsers/qiskit_parser.py`)

### QiskitASTVisitor Class

**Purpose**: AST visitor that traverses Qiskit source code to extract circuit operations without executing the code.

#### Key Methods:

**`visit_Assign` (lines 45-60)**:
```python
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
```

**Working**: Visits assignment nodes, detects `QuantumCircuit()` constructor calls, extracts qubit/clbit dimensions, and tracks circuit variable names.

**`_extract_circuit_dimensions` (lines 75-85)**:
```python
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
```

**Working**: Parses `QuantumCircuit(n, m)` arguments to extract qubit and classical bit counts.

**`visit_Expr` (lines 62-70)**:
```python
def visit_Expr(self, node: ast.Expr) -> None:
    """Handle expression statements, typically method calls."""
    if VERBOSE:
        vprint("[QiskitASTVisitor] visit_Expr: inspecting expression node")
    if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
        self._handle_circuit_method_call(node.value)
    self.generic_visit(node)
```

**Working**: Handles expression statements (method calls like `qc.h(0)`) and routes them to gate operation parsing.

**`_handle_circuit_method_call` (lines 105-125)**:
```python
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
```

**Working**: Checks if method calls are on tracked circuit variables, logs AST details for debugging, and routes to gate parsing.

**`_parse_gate_operation` (lines 127-180)**:
```python
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
```

**Working**: Routes different gate types to specialized handlers based on method name.

**`_handle_single_qubit_gate` (lines 182-190)**:
```python
def _handle_single_qubit_gate(self, method_name: str, args: List[ast.expr]) -> None:
    """Handle single-qubit gates without parameters."""
    if args:
        qubit = self._extract_qubit_index(args[0])
        self.operations.append(GateNode(name=method_name, qubits=[qubit]))
        if VERBOSE:
            vprint(f"[QiskitASTVisitor] Added single-qubit gate {method_name} on q[{qubit}]")
```

**Working**: Extracts qubit index from arguments and creates a `GateNode` for single-qubit gates.

**`_handle_parameterized_single_qubit_gate` (lines 200-212)**:
```python
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
```

**Working**: Extracts parameter and qubit index, creates `GateNode` with parameters for rotation gates.

**`_handle_measurement_qiskit` (lines 242-268)**:
```python
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
```

**Working**: Detects batch vs single measurements and routes accordingly.

**`_extract_qubit_index` (lines 320-340)**:
```python
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
```

**Working**: Extracts integer qubit indices from AST constant nodes.

**`_extract_parameter` (lines 350-375)**:
```python
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
    return 0
```

**Working**: Extracts parameter values, handles mathematical constants like `np.pi`, and tracks parameter names.

---

## 2. Cirq AST Parser (`quantum_converters/parsers/cirq_parser.py`)

### CirqASTVisitor Class

**Purpose**: AST visitor for Cirq source code, similar to Qiskit parser but adapted for Cirq syntax.

#### Key Methods:

**`visit_Assign` (lines 45-75)**:
```python
def visit_Assign(self, node: ast.Assign) -> None:
    """Handle variable assignments, particularly Circuit creation."""
    if VERBOSE:
        vprint("[CirqASTVisitor] visit_Assign: inspecting assignment node")
    # Check if assigning a Circuit
    if isinstance(node.value, ast.Call) and self._is_cirq_circuit_call(node.value):
        if VERBOSE:
            vprint("[CirqASTVisitor] Detected cirq.Circuit constructor; parsing args")
        # Track the variable name
        if isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id
            self.circuit_vars.add(var_name)
            self.current_circuit = var_name

        # Parse Circuit constructor arguments (operations)
        self._parse_circuit_constructor_args(node.value)
```

**Working**: Detects `cirq.Circuit()` calls and parses constructor arguments for operations.

**`_parse_circuit_constructor_args` (lines 135-150)**:
```python
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
```

**Working**: Parses operations passed to `cirq.Circuit()` constructor, handling both individual calls and lists.

**`_parse_operation_call` (lines 152-165)**:
```python
def _parse_operation_call(self, call_node: ast.Call) -> None:
    """Parse a single operation call like cirq.H(q0) or cirq.measure(q0)."""
    method_name = self._extract_method_name(call_node)
    if method_name:
        if VERBOSE:
            self._log_operation_call(method_name, call_node)
        self._parse_gate_operation(method_name, call_node.args, call_node.keywords)
```

**Working**: Extracts method name from `cirq.H(q0)` style calls and routes to gate parsing.

**`_handle_qubit_creation` (lines 95-115)**:
```python
def _handle_qubit_creation(self, target, call_node):
    """Handle qubit creation and assignment."""
    if isinstance(target, ast.Tuple):
        self._handle_tuple_qubit_creation(target)
    elif isinstance(target, ast.Name):
        var_name = target.id
        self._handle_single_qubit_creation(var_name, call_node)
    # Other target types are ignored
```

**Working**: Handles Cirq qubit creation patterns like `q0, q1 = cirq.LineQubit.range(2)`.

---

## 3. Qiskit Converter (`quantum_converters/converters/qiskit_to_qasm.py`)

### QiskitToQASM3Converter Class

**Purpose**: Converts Qiskit circuits to OpenQASM 3.0 using both AST parsing and runtime execution.

#### Key Methods:

**`convert` (lines 540-600)**:
```python
def convert(self, qiskit_source: str) -> ConversionResult:
    """
    Convert Qiskit source code to OpenQASM 3.0 format using AST-based parsing.
    
    This method now uses AST parsing instead of dynamic execution for improved
    security and reliability. It parses the source code to extract circuit operations
    without executing potentially unsafe code.
    """
    # Try AST-based conversion first
    if VERBOSE:
        vprint("[QiskitToQASM3Converter] Attempt AST-based conversion")
    try:
        parser = QiskitASTParser()
        t_parse = time.time()
        circuit_ast = parser.parse(qiskit_source)
        if VERBOSE:
            vprint(f"[QiskitToQASM3Converter] AST parsed in {(time.time()-t_parse)*1000:.1f} ms")
        t_ana = time.time()
        stats = self._analyze_circuit_ast(circuit_ast)
        if VERBOSE:
            vprint(f"[QiskitToQASM3Converter] AST analyzed in {(time.time()-t_ana)*1000:.1f} ms")
        qasm3_program = self._convert_ast_to_qasm3(circuit_ast)
        return ConversionResult(qasm_code=qasm3_program, stats=stats)
    except Exception:
        pass

    # Fallback: execute and use runtime circuit to QASM
    if VERBOSE:
        vprint("[QiskitToQASM3Converter] AST failed, fallback to runtime execution path")
    qc = self._execute_qiskit_source(qiskit_source)
    stats = self._analyze_qiskit_circuit(qc)
    qasm3_program = self._convert_to_qasm3(qc)
    return ConversionResult(qasm_code=qasm3_program, stats=stats)
```

**Working**: Primary method that tries AST parsing first (secure), falls back to runtime execution if needed.

**`_execute_qiskit_source` (lines 35-85)**:
```python
def _execute_qiskit_source(self, source: str) -> 'QuantumCircuit':
    """
    Execute Qiskit source code and extract the quantum circuit.
    """
    self._ensure_qiskit_available()

    namespace = self._execute_source_code(source)

    # Try different strategies to extract the circuit
    circuit = (
        self._try_get_circuit_function(namespace) or
        self._try_find_circuit_instance(namespace) or
        self._try_factory_functions(namespace)
    )

    if circuit is None:
        raise ValueError(
            "Could not locate a QuantumCircuit. Define get_circuit() or assign the circuit to a variable."
        )

    return circuit
```

**Working**: Executes Qiskit source code in isolated namespace, tries multiple strategies to find the circuit.

**`_convert_ast_to_qasm3` (lines 420-440)**:
```python
def _convert_ast_to_qasm3(self, circuit_ast) -> str:
    t0 = time.time()
    builder = QASM3Builder()

    self._build_ast_prelude(builder, circuit_ast)
    self._convert_ast_operations(builder, circuit_ast)

    code = builder.get_code()
    self._log_ast_conversion_complete(t0)
    return code
```

**Working**: Converts AST representation to QASM using QASM3Builder.

**`_convert_ast_operations` (lines 450-470)**:
```python
def _convert_ast_operations(self, builder: QASM3Builder, circuit_ast) -> None:
    """Convert AST operations to QASM."""
    builder.add_section_comment("Circuit operations")

    for idx, op in enumerate(circuit_ast.operations):
        if isinstance(op, GateNode):
            self._convert_gate_node(builder, idx, op)
        elif isinstance(op, MeasurementNode):
            self._convert_measurement_node(builder, idx, op)
        elif isinstance(op, ResetNode):
            self._convert_reset_node(builder, idx, op)
        elif isinstance(op, BarrierNode):
            self._convert_barrier_node(builder, idx, op)
        else:
            builder.add_comment("Unsupported AST operation")
```

**Working**: Iterates through AST operations and converts each type to QASM.

---

## 4. Cirq Converter (`quantum_converters/converters/cirq_to_qasm.py`)

### CirqToQASM3Converter Class

**Purpose**: Converts Cirq circuits to OpenQASM 3.0.

#### Key Methods:

**`convert` (lines 650-680)**:
```python
def convert(self, cirq_source: str) -> ConversionResult:
    """
    Convert Cirq source code to OpenQASM 3.0 format.
    """
    # Try AST-based path first (secure, no execution)
    try:
        if VERBOSE:
            vprint("[CirqToQASM3Converter] Attempt AST-based conversion")
        parser = CirqASTParser()
        circuit_ast = parser.parse(cirq_source)
        stats = self._analyze_circuit_ast(circuit_ast)
        qasm3_program = self._convert_ast_to_qasm3(circuit_ast)
        return ConversionResult(qasm_code=qasm3_program, stats=stats)
    except Exception:
        pass

    # Fallback: execute source to obtain cirq.Circuit
    if VERBOSE:
        vprint("[CirqToQASM3Converter] AST failed, fallback to runtime execution path")
    circuit = self._execute_cirq_source(cirq_source)
    stats = self._analyze_cirq_circuit(circuit)
    qasm3_program = self._convert_to_qasm3(circuit)
    return ConversionResult(qasm_code=qasm3_program, stats=stats)
```

**Working**: Similar to Qiskit converter, tries AST parsing first, falls back to execution.

**`_convert_to_qasm3` (lines 200-240)**:
```python
def _convert_to_qasm3(self, circuit: 'Circuit') -> str:
    """
    Convert Cirq Circuit to enhanced OpenQASM 3.0 string with advanced features.
    Now uses QASM3Builder for proper code generation.
    """
    self._ensure_dependencies_available()

    if VERBOSE:
        vprint("[CirqToQASM3Converter] Building prelude")
    t0 = time.time()

    builder = QASM3Builder()
    qubit_map = self._create_qubit_mapping(circuit)
    has_measurements = self._detect_measurements(circuit)

    self._build_prelude(builder, len(qubit_map), has_measurements)
    self._add_custom_gates(builder, circuit)
    self._convert_operations(builder, circuit, qubit_map)

    code = builder.get_code()
    self._log_conversion_complete(code, t0)
    return code
```

**Working**: Creates qubit mapping, builds prelude, converts operations using QASM3Builder.

---

## 5. PennyLane Converter (`quantum_converters/converters/pennylane_to_qasm.py`)

### PennyLaneToQASM3Converter Class

**Purpose**: Converts PennyLane circuits to OpenQASM 3.0.

#### Key Methods:

**`convert` (lines 400-420)**:
```python
def convert(self, pennylane_code: str) -> ConversionResult:
    """
    Convert PennyLane quantum circuit code to OpenQASM 3.0 format with statistics.
    """
    # First try AST-based conversion (preferred)
    ast_result = self._try_ast_conversion(pennylane_code)
    if ast_result is not None:
        return ast_result

    # Fall back to legacy conversion
    return self._convert_legacy(pennylane_code)
```

**Working**: Tries AST conversion first, falls back to legacy string parsing.

**`_try_ast_conversion` (lines 580-600)**:
```python
def _try_ast_conversion(self, pennylane_code: str) -> Optional[ConversionResult]:
    """Try AST-based conversion, return None if it fails."""
    try:
        if VERBOSE:
            vprint("[PennyLaneToQASM3Converter] Attempt AST-based conversion")
        parser = PennyLaneASTParser()
        t_parse = time.time()
        circuit_ast = parser.parse(pennylane_code)
        if VERBOSE:
            vprint(f"[PennyLaneToQASM3Converter] AST parsed in {(time.time()-t_parse)*1000:.1f} ms; analyzing AST")
        t_ana = time.time()
        stats = self._analyze_circuit_ast(circuit_ast)
        if VERBOSE:
            vprint(f"[PennyLaneToQASM3Converter] AST analyzed in {(time.time()-t_ana)*1000:.1f} ms")
        qasm = self._convert_ast_to_qasm3(circuit_ast)
        return ConversionResult(qasm_code=qasm, stats=stats)
    except Exception:
        return None
```

**Working**: Uses PennyLaneASTParser to parse code, analyzes AST, converts to QASM.

---

## 6. QASM3Builder (`quantum_converters/base/qasm3_builder.py`)

### QASM3Builder Class

**Purpose**: Builds OpenQASM 3.0 code programmatically.

#### Key Methods:

**`build_standard_prelude` (lines 50-80)**:
```python
def build_standard_prelude(self, num_qubits: int, num_clbits: int = 0, include_vars: bool = True, include_constants: bool = True):
    """Build the standard OpenQASM 3.0 prelude with qubit and classical bit declarations."""
    self.add_line("OPENQASM 3.0;")
    self.add_line("include \"stdgates.inc\";")
    self.add_blank_line()

    # Declare qubits
    if num_qubits > 0:
        self.add_line(f"qubit[{num_qubits}] q;")
    if num_clbits > 0:
        self.add_line(f"bit[{num_clbits}] c;")
    self.add_blank_line()
```

**Working**: Creates the standard QASM header with qubit and classical bit declarations.

**`apply_gate` (lines 120-150)**:
```python
def apply_gate(self, gate_name: str, qubits: List[str], parameters: Optional[List[str]] = None, modifiers: Optional[Dict] = None):
    """Apply a quantum gate with optional parameters and modifiers."""
    # Build modifier string (ctrl@, inv@, etc.)
    modifier_str = ""
    if modifiers:
        modifier_parts = []
        if modifiers.get('ctrl'):
            modifier_parts.append("ctrl")
        if modifiers.get('inv'):
            modifier_parts.append("inv")
        if modifiers.get('pow'):
            modifier_parts.append(f"pow({modifiers['pow']})")
        if modifier_parts:
            modifier_str = "@".join(modifier_parts) + "@"

    # Format parameters
    param_str = ""
    if parameters:
        param_str = "(" + ", ".join(str(p) for p in parameters) + ")"

    # Build gate instruction
    gate_instruction = f"{modifier_str}{gate_name}{param_str} {', '.join(qubits)};"

    self.add_line(gate_instruction)
```

**Working**: Formats gate instructions with modifiers, parameters, and qubit arguments.

**`format_parameter` (lines 200-230)**:
```python
def format_parameter(self, param: Any) -> str:
    """Format a parameter value, recognizing mathematical constants."""
    if isinstance(param, str):
        # Check for mathematical constants
        if param.lower() == 'pi':
            return 'pi'
        elif param.upper() == 'E':
            return 'E'
        return param
    elif isinstance(param, (int, float)):
        # Check for common constants
        if abs(param - np.pi) < 1e-10:
            return "pi"
        elif abs(param - np.pi/2) < 1e-10:
            return "pi_2"
        elif abs(param - np.pi/4) < 1e-10:
            return "pi_4"
        elif abs(param - np.e) < 1e-10:
            return "E"
        else:
            return f"{param:.6f}"
    else:
        return str(param)
```

**Working**: Formats parameters, converting numerical constants to symbolic QASM constants.

---

## 7. Circuit AST (`quantum_converters/base/circuit_ast.py`)

### CircuitAST Class

**Purpose**: Unified intermediate representation for quantum circuits.

#### Key Classes:

**`CircuitAST` (lines 20-35)**:
```python
@dataclass
class CircuitAST:
    qubits: int
    clbits: int
    operations: List[Union[GateNode, MeasurementNode, ResetNode, BarrierNode]]
    parameters: List[str]
```

**Working**: Holds circuit structure with qubits, classical bits, operations list, and parameters.

**`GateNode` (lines 40-50)**:
```python
@dataclass
class GateNode:
    name: str
    qubits: List[int]
    parameters: Optional[List[Any]] = None
    modifiers: Optional[Dict[str, Any]] = None
```

**Working**: Represents quantum gates with name, target qubits, parameters, and modifiers.

---

## Summary of Conversion Flow

1. **Input**: Framework-specific quantum circuit code
2. **Parsing**: AST parser extracts operations without execution (secure)
3. **AST Building**: Creates `CircuitAST` with operations list
4. **Analysis**: Extracts statistics (qubits, depth, gate counts)
5. **QASM Generation**: `QASM3Builder` converts AST to OpenQASM 3.0
6. **Output**: Returns `ConversionResult` with QASM code and statistics

The system prioritizes security by using AST parsing first, falling back to controlled execution only when necessary. Each converter handles framework-specific syntax while producing standardized OpenQASM 3.0 output.
