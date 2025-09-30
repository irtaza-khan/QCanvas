# Integration Guide: Using New QASM3 Components

## 📋 Overview

This guide shows how to integrate the new OpenQASM 3.0 Iteration I components with existing converters.

## 🔧 New Components

### 1. QASM3Builder (`quantum_converters/base/qasm3_builder.py`)

Main code generation component with all Iteration I features.

### 2. QASM3ExpressionParser (`quantum_converters/base/qasm3_expression.py`)

Classical expression parsing and evaluation.

### 3. QASM3GateLibrary (`quantum_converters/base/qasm3_gates.py`)

Complete gate library with modifiers.

## 🚀 Quick Integration Examples

### Example 1: Basic Qiskit Integration

```python
from qiskit import QuantumCircuit
from quantum_converters.base.qasm3_builder import QASM3Builder
from quantum_converters.base.qasm3_gates import QASM3GateLibrary

def convert_qiskit_to_qasm3_enhanced(qc: QuantumCircuit) -> str:
    """Enhanced Qiskit to QASM3 conversion using new builder."""
    
    # Initialize builder
    builder = QASM3Builder()
    gate_lib = QASM3GateLibrary()
    
    # Build prelude
    builder.build_standard_prelude(
        num_qubits=qc.num_qubits,
        num_clbits=qc.num_clbits
    )
    
    builder.add_section_comment("Circuit operations")
    
    # Convert gates
    for instruction, qargs, cargs in qc.data:
        gate_name = instruction.name.lower()
        qubit_indices = [qc.qubits.index(q) for q in qargs]
        qubits = [f"q[{i}]" for i in qubit_indices]
        
        # Handle parameters
        params = None
        if instruction.params:
            params = [builder.format_parameter(p) for p in instruction.params]
        
        # Handle different gate types
        if gate_name == 'measure':
            clbit_indices = [qc.clbits.index(c) for c in cargs]
            builder.add_measurement(qubits[0], f"c[{clbit_indices[0]}]")
        elif gate_name == 'reset':
            builder.add_reset(qubits[0])
        elif gate_name == 'barrier':
            builder.add_barrier(qubits if qubits else None)
        else:
            # Check for gate modifiers
            modifiers = {}
            
            # Detect controlled gates
            if gate_name.startswith('c') and len(qubits) > 1:
                modifiers['ctrl'] = 1
                gate_name = gate_name[1:]  # Remove 'c' prefix
            
            # Apply gate
            builder.apply_gate(gate_name, qubits, parameters=params, modifiers=modifiers if modifiers else None)
    
    return builder.get_code()
```

### Example 2: Cirq Integration

```python
import cirq
from quantum_converters.base.qasm3_builder import QASM3Builder
from quantum_converters.base.qasm3_gates import QASM3GateLibrary, GateModifier

def convert_cirq_to_qasm3_enhanced(circuit: cirq.Circuit) -> str:
    """Enhanced Cirq to QASM3 conversion using new builder."""
    
    builder = QASM3Builder()
    gate_lib = QASM3GateLibrary()
    
    # Get qubits
    all_qubits = sorted(circuit.all_qubits(), key=str)
    num_qubits = len(all_qubits)
    qubit_map = {qubit: i for i, qubit in enumerate(all_qubits)}
    
    # Build prelude
    has_measurements = any(
        any(hasattr(op.gate, '_measurement_key') for op in moment)
        for moment in circuit
    )
    
    builder.build_standard_prelude(
        num_qubits=num_qubits,
        num_clbits=num_qubits if has_measurements else 0
    )
    
    builder.add_section_comment("Circuit operations")
    
    # Convert operations
    for moment in circuit:
        for operation in moment:
            gate = operation.gate
            qubits = [f"q[{qubit_map[q]}]" for q in operation.qubits]
            
            gate_name = type(gate).__name__
            
            # Handle inverse modifier
            modifiers = {}
            if hasattr(gate, 'exponent') and gate.exponent < 0:
                modifiers['inv'] = True
                gate.exponent = abs(gate.exponent)
            
            # Handle parameterized gates
            params = None
            if hasattr(gate, 'exponent') and gate.exponent != 1:
                import numpy as np
                angle = gate.exponent * np.pi
                params = [builder.format_parameter(angle)]
            
            # Map gate name
            gate_mapping = {
                'HPowGate': 'h',
                'XPowGate': 'x',
                'YPowGate': 'y',
                'ZPowGate': 'z',
                # Add more mappings...
            }
            
            qasm_gate = gate_mapping.get(gate_name, gate_name.lower())
            
            # Apply gate
            if qasm_gate == 'measure':
                builder.add_measurement(qubits[0], qubits[0].replace('q', 'c'))
            else:
                builder.apply_gate(qasm_gate, qubits, parameters=params, modifiers=modifiers if modifiers else None)
    
    return builder.get_code()
```

### Example 3: Custom Gate Definition

```python
from quantum_converters.base.qasm3_builder import QASM3Builder

def create_custom_gates():
    """Example of creating custom gate definitions."""
    
    builder = QASM3Builder()
    builder.initialize_header()
    
    # Define a Bell state preparation gate
    builder.define_gate("bell", [], ["a", "b"], [
        "h a;",
        "cx a, b;"
    ])
    
    # Define a parameterized rotation gate
    builder.define_gate("my_rot", ["theta", "phi"], ["q"], [
        "rz(phi) q;",
        "ry(theta) q;",
        "rz(-phi) q;"
    ])
    
    # Use the gates
    builder.declare_qubit_register("q", 4)
    builder.apply_gate("bell", ["q[0]", "q[1]"])
    builder.apply_gate("my_rot", ["q[2]"], parameters=["PI/2", "PI/4"])
    
    return builder.get_code()
```

### Example 4: Classical Control Flow Extraction

```python
from quantum_converters.base.qasm3_builder import QASM3Builder
from quantum_converters.base.qasm3_expression import QASM3ExpressionParser

def add_classical_control(builder: QASM3Builder, source_code: str):
    """Extract and add classical control flow from source code."""
    
    parser = QASM3ExpressionParser()
    
    # Example: Extract if statements
    import re
    if_matches = re.finditer(r'if\s+([^:]+):\s*\n\s+([^
]+)', source_code)
    
    for match in if_matches:
        condition = match.group(1)
        body = match.group(2)
        
        # Parse condition
        parsed_condition = parser.parse_expression(condition)
        
        # Add to QASM
        builder.add_if_statement(parsed_condition, [body])
    
    # Example: Extract for loops
    for_matches = re.finditer(r'for\s+(\w+)\s+in\s+range\((\d+)\):', source_code)
    
    for match in for_matches:
        var = match.group(1)
        end = match.group(2)
        
        # Add for loop to QASM
        builder.add_for_loop(var, f"[0:{end}]", [
            f"// Loop body for {var}"
        ])
```

### Example 5: Gate Broadcasting

```python
from quantum_converters.base.qasm3_builder import QASM3Builder

def demonstrate_broadcasting():
    """Example of gate broadcasting."""
    
    builder = QASM3Builder()
    builder.build_standard_prelude(num_qubits=10)
    
    builder.add_section_comment("Gate broadcasting examples")
    
    # Apply H to all qubits
    builder.apply_gate_broadcast("h", "q")
    
    # Apply to a subset
    builder.add_alias("first_five", "q[0:5]")
    builder.apply_gate_broadcast("x", "first_five")
    
    # Parameterized gate broadcasting
    builder.apply_gate_broadcast("rx", "q", parameters=["PI/2"])
    
    return builder.get_code()
```

## 🔄 Full Converter Update Pattern

### Step-by-Step Integration

1. **Import New Components**
```python
from quantum_converters.base.qasm3_builder import QASM3Builder
from quantum_converters.base.qasm3_gates import QASM3GateLibrary, GateModifier
from quantum_converters.base.qasm3_expression import QASM3ExpressionParser
```

2. **Replace Manual String Building**

**Old approach:**
```python
lines = []
lines.append("OPENQASM 3.0;")
lines.append('include "stdgates.inc";')
# ... manual string concatenation
qasm_code = '\n'.join(lines)
```

**New approach:**
```python
builder = QASM3Builder()
builder.initialize_header()
builder.build_standard_prelude(num_qubits, num_clbits)
# ... use builder methods
qasm_code = builder.get_code()
```

3. **Use Gate Library for Validation**

```python
gate_lib = QASM3GateLibrary()

# Validate before applying
is_valid, error = gate_lib.validate_gate_application(
    gate_name, num_qubits, num_params
)

if is_valid:
    builder.apply_gate(gate_name, qubits, parameters)
else:
    print(f"Error: {error}")
```

4. **Handle Gate Modifiers**

```python
# Detect controlled gates
if is_controlled_gate(gate):
    modifiers = {'ctrl': get_num_controls(gate)}
    base_gate = get_base_gate(gate)
    builder.apply_gate(base_gate, qubits, modifiers=modifiers)

# Detect inverse gates
if is_inverse_gate(gate):
    modifiers = {'inv': True}
    base_gate = get_base_gate(gate)
    builder.apply_gate(base_gate, qubits, modifiers=modifiers)
```

5. **Parse Classical Expressions**

```python
expr_parser = QASM3ExpressionParser()

# Parse and validate
is_valid, error = expr_parser.validate_expression(expression)
if is_valid:
    parsed_expr = expr_parser.parse_expression(expression)
    builder.add_assignment(variable, parsed_expr)
```

## 📝 Migration Checklist

When updating a converter:

- [ ] Import new components
- [ ] Replace header generation with `builder.initialize_header()`
- [ ] Replace register declarations with `builder.declare_*_register()`
- [ ] Use `builder.build_standard_prelude()` for common setup
- [ ] Replace gate string building with `builder.apply_gate()`
- [ ] Implement gate modifier detection and application
- [ ] Use `gate_lib` for validation
- [ ] Parse classical expressions with `expr_parser`
- [ ] Add control flow with `builder.add_if_statement()` and `builder.add_for_loop()`
- [ ] Replace manual parameter formatting with `builder.format_parameter()`
- [ ] Test with Iteration I test suite

## 🧪 Testing Your Integration

After integration, test with:

```bash
# Run automated tests
pytest tests/iteration_1/test_iteration_i_features.py -v

# Test specific converter
python -c "
from quantum_converters.converters.qiskit_to_qasm import QiskitToQASM3Converter
# ... test code
"

# Test with frontend examples
# Copy code from tests/iteration_1/frontend_test_codes/
```

## 🐛 Common Integration Issues

### Issue 1: Parameter Formatting

**Problem**: Parameters not formatted correctly
```python
# Wrong
qasm = f"rx({param}) q[0];"

# Correct
param_str = builder.format_parameter(param)
builder.apply_gate("rx", ["q[0]"], parameters=[param_str])
```

### Issue 2: Gate Modifier Detection

**Problem**: Not detecting controlled/inverse gates
```python
# Add detection logic
def detect_modifiers(gate_name, gate_obj):
    modifiers = {}
    
    if gate_name.startswith('c'):
        modifiers['ctrl'] = gate_name.count('c')
        gate_name = gate_name.lstrip('c')
    
    if hasattr(gate_obj, 'is_inverse') and gate_obj.is_inverse:
        modifiers['inv'] = True
    
    return gate_name, modifiers
```

### Issue 3: Qubit Indexing

**Problem**: Incorrect qubit indices
```python
# Ensure consistent qubit mapping
qubit_map = {qubit: i for i, qubit in enumerate(sorted(all_qubits, key=str))}
qubits = [f"q[{qubit_map[q]}]" for q in gate_qubits]
```

## 📚 Additional Resources

- **API Documentation**: See docstrings in each module
- **Examples**: `tests/iteration_1/frontend_test_codes/`
- **Tests**: `tests/iteration_1/test_iteration_i_features.py`
- **Status**: `tests/iteration_1/IMPLEMENTATION_STATUS.md`

## 🎯 Next Steps

1. Update one converter completely (recommend starting with Qiskit)
2. Test thoroughly with automated and frontend tests
3. Apply same pattern to other converters
4. Document any converter-specific edge cases
5. Update converter documentation

---

*Last Updated: 2025-09-30*
