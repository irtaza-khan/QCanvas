
# Iteration I Frontend Test Codes

This folder contains comprehensive test circuits for validating all OpenQASM 3.0 **Iteration I** features in the QCanvas platform.

## 📋 Overview

These test files demonstrate **ALL** features from Iteration I as defined in `docs/project-scope.md`. Use these to test the conversion accuracy of the QCanvas frontend.

## 🧪 Test Files

### 1. **qiskit_iteration_i_complete.py**
Complete Qiskit circuit testing all Iteration I features.

**How to use:**
1. Open QCanvas frontend
2. Select "Qiskit" as the framework
3. Copy and paste the entire file content
4. Click "Convert" or "Run"
5. Verify OpenQASM 3.0 output contains all expected features

### 2. **cirq_iteration_i_complete.py**
Complete Cirq circuit testing all Iteration I features.

**How to use:**
1. Open QCanvas frontend
2. Select "Cirq" as the framework
3. Copy and paste the entire file content
4. Click "Convert" or "Run"
5. Verify OpenQASM 3.0 output contains all expected features

### 3. **pennylane_iteration_i_complete.py**
Complete PennyLane circuit testing all Iteration I features.

**How to use:**
1. Open QCanvas frontend
2. Select "PennyLane" as the framework
3. Copy and paste the entire file content
4. Click "Convert" or "Run"
5. Verify OpenQASM 3.0 output contains all expected features

## ✅ Expected Features in Output

All test files should produce OpenQASM 3.0 code containing:

### 1. **Comments and Version Control**
```qasm
OPENQASM 3.0;
include "stdgates.inc";
// Single-line comment
/* Multi-line comment */
```

### 2. **Types and Declarations**
```qasm
// Quantum types
qubit[5] q;
bit[5] c;

// Classical types
int loop_index;
uint counter;
float temp_angle;
angle theta;
bool condition_result;

// Constants
const float PI = 3.141592653589793;
const float E = 2.718281828459045;
const float PI_2 = 1.5707963267948966;
const float PI_4 = 0.7853981633974483;
```

### 3. **Arrays and Aliasing**
```qasm
int[10] my_array;
let first_two = q[0:2];  // Aliasing
```

### 4. **Gates - Basic**
```qasm
h q[0];     // Hadamard
x q[1];     // Pauli-X
y q[2];     // Pauli-Y
z q[3];     // Pauli-Z
s q[0];     // S gate
t q[1];     // T gate
sdg q[2];   // S dagger (inverse)
tdg q[3];   // T dagger (inverse)
sx q[0];    // Sqrt(X)
sxdg q[1];  // Inverse Sqrt(X)
id q[4];    // Identity
```

### 5. **Gates - Parameterized**
```qasm
rx(PI/2) q[0];           // Rotation-X
ry(PI/4) q[1];           // Rotation-Y
rz(PI) q[2];             // Rotation-Z
p(PI/3) q[3];            // Phase
u(PI/2, 0, PI) q[4];     // Universal gate
```

### 6. **Gates - Two-Qubit**
```qasm
cx q[0], q[1];    // CNOT
cz q[1], q[2];    // Controlled-Z
cy q[2], q[3];    // Controlled-Y
swap q[0], q[2];  // SWAP
ch q[1], q[3];    // Controlled-H
```

### 7. **Gates - Three-Qubit**
```qasm
ccx q[0], q[1], q[2];    // Toffoli
cswap q[0], q[1], q[2];  // Fredkin
ccz q[0], q[1], q[2];    // Controlled-Controlled-Z
```

### 8. **Gates - Special**
```qasm
gphase(PI/4);  // Global phase
```

### 9. **Gate Modifiers**
```qasm
// Control modifier (ctrl@)
ctrl @ x q[0], q[1];           // Same as cx
ctrl(2) @ x q[0], q[1], q[2];  // Same as ccx

// Inverse modifier (inv@)
inv @ s q[0];     // Same as sdg
inv @ t q[1];     // Same as tdg

// Combined modifiers
inv @ ctrl @ h q[0], q[1];
```

### 10. **Gate Broadcasting**
```qasm
h q;  // Apply H to all qubits in register q
```

### 11. **Hierarchical Gate Definitions**
```qasm
gate my_gate(theta) a, b {
    rx(theta) a;
    cx a, b;
    ry(theta) b;
}

// Use the custom gate
my_gate(PI/2) q[0], q[1];
```

### 12. **Built-in Quantum Instructions**
```qasm
reset q[0];            // Reset
measure q[0] -> c[0];  // Measurement
barrier q[0], q[1];    // Barrier
```

### 13. **Classical Operations**
```qasm
// Assignment
temp_angle = PI/2;
loop_index = 0;
counter = 10;

// Arithmetic operations
result = a + b;
result = a * b;

// Comparison operations
condition_result = (c[0] == 1);
condition_result = (counter > 5);

// Logical operations
condition_result = (a && b);
condition_result = !flag;
```

### 14. **Control Flow - If/Else**
```qasm
if (c[0] == 1) {
    x q[1];
}

if (c[0] == 1) {
    x q[1];
} else {
    y q[1];
}
```

### 15. **Control Flow - For Loops**
```qasm
for loop_index in [0:5] {
    h q[loop_index];
}

for i in {0, 2, 4} {
    rx(temp_angle) q[i];
}
```

### 16. **Index Sets and Slicing**
```qasm
// Slicing
let subset = q[0:3];

// Index sets
for i in [0:2:10] {  // Start:Step:End
    h q[i];
}
```

### 17. **Built-in Mathematical Functions** (If used in parameters)
```qasm
temp_angle = sqrt(2.0);
result = sin(PI/4);
value = cos(angle);
```

## 🔍 Validation Checklist

When testing each file, verify the converted OpenQASM 3.0 code includes:

- [ ] Correct version header (`OPENQASM 3.0;`)
- [ ] Include statement (`include "stdgates.inc";`)
- [ ] Mathematical constants (PI, E, etc.)
- [ ] Proper register declarations (qubit[], bit[])
- [ ] Classical variable declarations (int, uint, float, angle, bool)
- [ ] All basic gates correctly converted
- [ ] Parameterized gates with proper angle formatting
- [ ] Two-qubit and three-qubit gates
- [ ] Gate modifiers (ctrl@, inv@) where applicable
- [ ] Custom gate definitions (if any)
- [ ] Reset and measurement instructions
- [ ] Barrier instructions
- [ ] Classical operations and assignments
- [ ] If/else statements
- [ ] For loop structures
- [ ] Proper qubit/bit indexing
- [ ] Array operations where used

## 🐛 Reporting Issues

If any expected features are missing or incorrectly converted:

1. Note the specific feature that failed
2. Compare with the expected output above
3. Check the test file in `tests/iteration_1/test_iteration_i_features.py`
4. Report the issue with:
   - Framework used (Qiskit/Cirq/PennyLane)
   - Feature that failed
   - Expected vs. Actual output

## 📚 Reference

For complete Iteration I feature specification, see:
- `docs/project-scope.md` - Official scope document
- `tests/iteration_1/test_iteration_i_features.py` - Automated test suite

## 🚀 Quick Test Commands

### Automated Testing
```bash
# Activate virtual environment
cd D:\University\Uni\FYP\QCanvas
.\qasm_env\Scripts\Activate.ps1

# Run all Iteration I tests
pytest tests/iteration_1/test_iteration_i_features.py -v

# Run specific test category
pytest tests/iteration_1/test_iteration_i_features.py::TestGatesAndModifiers -v

# Run with detailed output
pytest tests/iteration_1/test_iteration_i_features.py -vv --tb=short

# Run with line-by-line output
pytest tests/iteration_1/test_iteration_i_features.py -v --tb=line
```

### Integration Testing
```bash
# Run all converter integration tests
pytest tests/integration/ -v

# Run specific converter tests
pytest tests/integration/test_cirq_integration.py -v
pytest tests/integration/test_qiskit_integration.py -v
pytest tests/integration/test_pennylane_integration.py -v
```

### Demo Scripts
```bash
# See actual OpenQASM 3.0 output from each converter
python tests/integration/demo_cirq_output.py
python tests/integration/demo_qiskit_output.py
python tests/integration/demo_pennylane_output.py
```

### Complete Test Suite
```bash
# Run everything (Iteration I + Integration)
pytest tests/iteration_1/ tests/integration/ -v

# Run with summary
pytest tests/iteration_1/ tests/integration/ -v --tb=line -q

# Run and stop on first failure
pytest tests/iteration_1/ tests/integration/ -v -x
```

### What Each Test Shows

**Iteration I Tests** (`pytest tests/iteration_1/test_iteration_i_features.py -v`):
- ✅ **42 PASSED**: All implemented features working correctly
- 🟡 **2 SKIPPED**: Concatenation features (deferred to later)
- ❌ **4 XFAIL**: Excluded features (expected to fail)
- **Total**: 48 tests, 100% success rate for implemented features

**Integration Tests** (`pytest tests/integration/ -v`):
- ✅ **Cirq**: 7/7 tests passing (simple circuits, parameters, measurements, modifiers, statistics, reset, multi-qubit)
- ✅ **Qiskit**: 8/8 tests passing (simple circuits, parameters, measurements, modifiers, statistics, reset, multi-qubit, U gate)
- ✅ **PennyLane**: 7/7 tests passing (simple circuits, parameters, Pauli gates, statistics, multi-qubit, S/T gates, PhaseShift)
- **Total**: 22 tests, 100% success rate

**Demo Scripts** (shows actual OpenQASM 3.0 output):
- **Cirq Demo**: Bell state, parameterized rotations, inverse gates, multi-qubit gates
- **Qiskit Demo**: Bell state with measurements, parameterized rotations, multi-qubit gates (Toffoli, CZ, SWAP)
- **PennyLane Demo**: Quantum teleportation setup, parameterized rotations, multi-qubit gates

## 📝 Notes

- **Physical Qubits** ($0, $1, etc.) are **EXCLUDED** from Iteration I
- **Duration** and **Stretch** types are **EXCLUDED**
- **Delay** instructions are **EXCLUDED**
- **Complex** type is **Iteration II** (not I)
- **While** loops are **Iteration II** (not I)
- **Break/Continue** statements are **Iteration II** (not I)
- **Bitwise operations** are **Iteration II** (not I)

---

**Happy Testing! 🎉**
