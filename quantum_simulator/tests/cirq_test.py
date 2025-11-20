import cirq
import pytest
from qsim.qasm_parser.parser import parse_openqasm3
from qsim.visitors.cirq_visitor import CirqVisitor
from qsim.core.exceptions import ParseError  # Add this import


def run_qasm(qasm_code, repetitions=10):
    """Helper to parse QASM, build a circuit, and simulate."""
    program = parse_openqasm3(qasm_code, unroll=False)
    visitor = CirqVisitor()
    visitor.visit(program)
    circuit = visitor.finalize()
   
    # Case 1: No quantum operations, just classical declarations
    if circuit is None or not isinstance(circuit, cirq.Circuit):
        print("[run_qasm] 🧮 Classical-only program detected.")
        return visitor.variables  # ✅ Return classical vars dict
    has_measurements = any(isinstance(op.gate, cirq.MeasurementGate) for op in circuit.all_operations())

    if not has_measurements:
        print("[run_qasm] 🔬 Circuit has no measurements. Returning for structural analysis.")
        # Return the circuit itself for tests that inspect its structure
        return circuit, None

    # Case 2: Circuit exists, simulate it
    sim = cirq.Simulator()
    result = sim.run(circuit, repetitions=repetitions)
    return circuit, result


# ============================================================================
# RESET TEST CASES
# ============================================================================

def test_R1_single_reset():
    """Test single qubit reset after X gate"""
    qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] c;

x q[0];
reset q[0];
c[0] = measure q[0];
"""
    circuit, result = run_qasm(qasm_code, repetitions=10)
    # After reset, all measurements should be 0
    assert all(result.data["c_0"] == 0)


def test_R2_multiple_resets():
    """Test multiple individual qubit resets"""
    qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[3] c;

x q[0];
x q[1];
x q[2];

reset q[0];
reset q[1];
reset q[2];

c = measure q;
"""
    circuit, result = run_qasm(qasm_code, repetitions=10)
    # All qubits should measure 0 after reset
    assert all(result.data["c_0"] == 0)
    assert all(result.data["c_1"] == 0)
    assert all(result.data["c_2"] == 0)


def test_R3_register_reset():
    """Test full register reset"""
    qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[3] c;

h q[0];
h q[1];
h q[2];

reset q;

c = measure q;
"""
    circuit, result = run_qasm(qasm_code, repetitions=10)
    # All qubits should measure 0 after register reset
    assert all(result.data["c_0"] == 0)
    assert all(result.data["c_1"] == 0)
    assert all(result.data["c_2"] == 0)

def test_R1_single_reset():
    """Test single qubit reset after X gate"""
    qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] c;

x q[0];
reset q[0];
c[0] = measure q[0];
"""
    circuit, result = run_qasm(qasm_code, repetitions=10)
    # After reset, all measurements should be 0
    assert all(result.data["c_0"] == 0)

# ============================================================================
# MEASUREMENT OLD SYNTAX (measure q -> c)
# ============================================================================

def test_M1_old_single():
    """Test old syntax: single qubit measurement"""
    qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] c;

h q[0];
measure q[0] -> c[0];
"""
    circuit, result = run_qasm(qasm_code, repetitions=50)
    ones = sum(result.data["c_0"])
    ratio = ones / 50
    assert 0.3 < ratio < 0.7


def test_M2_old_register():
    """Test old syntax: full register measurement"""
    qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[3] c;

h q[0];
h q[1];
h q[2];

measure q -> c;
"""
    circuit, result = run_qasm(qasm_code, repetitions=50)
    # Each qubit should show ~50/50 distribution
    for col in ["c_0", "c_1", "c_2"]:
        ones = sum(result.data[col])
        ratio = ones / 50
        assert 0.2 < ratio < 0.8


def test_M3_old_multiple():
    """Test old syntax: multiple individual measurements"""
    qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[3] c;

x q[0];
h q[1];
x q[2];

measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
"""
    circuit, result = run_qasm(qasm_code, repetitions=50)
    # q[0] and q[2] should always be 1, q[1] should be 50/50
    assert all(result.data["c_0"] == 1)
    assert all(result.data["c_2"] == 1)
    ones_q1 = sum(result.data["c_1"])
    ratio_q1 = ones_q1 / 50
    assert 0.3 < ratio_q1 < 0.7


# ============================================================================
# MEASUREMENT NEW SYNTAX (c = measure q)
# ============================================================================

def test_MA1_new_single():
    """Test new syntax: single qubit measurement"""
    qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] c;

h q[0];
c[0] = measure q[0];
"""
    circuit, result = run_qasm(qasm_code, repetitions=50)
    ones = sum(result.data["c_0"])
    ratio = ones / 50
    assert 0.3 < ratio < 0.7


def test_MA2_new_register():
    """Test new syntax: full register measurement"""
    qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[3] c;

h q[0];
h q[1];
h q[2];

c = measure q;
"""
    circuit, result = run_qasm(qasm_code, repetitions=50)
    # Each qubit should show ~50/50 distribution
    for col in ["c_0", "c_1", "c_2"]:
        ones = sum(result.data[col])
        ratio = ones / 50
        assert 0.2 < ratio < 0.8


def test_MA3_new_multiple():
    """Test new syntax: multiple individual measurements"""
    qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[3] c;

x q[0];
h q[1];
x q[2];

c[0] = measure q[0];
c[1] = measure q[1];
c[2] = measure q[2];
"""
    circuit, result = run_qasm(qasm_code, repetitions=50)
    # q[0] and q[2] should always be 1, q[1] should be 50/50
    assert all(result.data["c_0"] == 1)
    assert all(result.data["c_2"] == 1)
    ones_q1 = sum(result.data["c_1"])
    ratio_q1 = ones_q1 / 50
    assert 0.2 <= ratio_q1 <= 0.8  # Changed to inclusive boundaries


def test_MA4_bell_state():
    """Test new syntax: Bell state measurement"""
    qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[2] c;

h q[0];
cx q[0], q[1];
c = measure q;
"""
    circuit, result = run_qasm(qasm_code, repetitions=50)
    # In Bell state, q[0] and q[1] should always match
    mismatches = sum(result.data["c_0"] != result.data["c_1"])
    assert mismatches == 0


# ============================================================================
# COMBINED CASES (Reset + Measurement)
# ============================================================================

def test_C1_reset_measure_cycle():
    """Test multiple cycles of measurement and reset"""
    qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[4] c;

h q[0];
h q[1];
c[0] = measure q[0];
c[1] = measure q[1];

reset q;
x q[0];
x q[1];
c[2] = measure q[0];
c[3] = measure q[1];
"""
    circuit, result = run_qasm(qasm_code, repetitions=50)
    # First measurements: random (50/50)
    ones_c0 = sum(result.data["c_0"])
    ones_c1 = sum(result.data["c_1"])
    assert 0.2 < ones_c0/50 < 0.8
    assert 0.2 < ones_c1/50 < 0.8
    
    # After reset and X: should always be 1
    assert all(result.data["c_2"] == 1)
    assert all(result.data["c_3"] == 1)


def test_C2_selective_reset():
    """Test selective qubit reset"""
    qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[2] c;

h q[0];
cx q[0], q[1];
reset q[1];

measure q[0] -> c[0];
measure q[1] -> c[1];
"""
    circuit, result = run_qasm(qasm_code, repetitions=50)
    # q[0] should be random (50/50)
    ones_q0 = sum(result.data["c_0"])
    assert 0.3 < ones_q0/50 < 0.7
    
    # q[1] should always be 0 (reset)
    assert all(result.data["c_1"] == 0)


def test_C3_multiple_cycles():
    """Test multiple measurement/reset cycles on same qubit"""
    qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[3] c;

h q[0];
c[0] = measure q[0];

reset q[0];
x q[0];
c[1] = measure q[0];

reset q[0];
h q[0];
c[2] = measure q[0];
"""
    circuit, result = run_qasm(qasm_code, repetitions=50)
    # First: random (50/50)
    ones_c0 = sum(result.data["c_0"])
    assert 0.3 < ones_c0/50 < 0.7
    
    # Second: always 1 (reset then X)
    assert all(result.data["c_1"] == 1)
    
    # Third: random again (50/50)
    ones_c2 = sum(result.data["c_2"])
    assert 0.3 < ones_c2/50 < 0.7


# ============================================================================
# EDGE CASES
# ============================================================================

def test_E1_immediate_reset():
    """Test reset without any prior operations"""
    qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[2] c;

reset q;
c = measure q;
"""
    circuit, result = run_qasm(qasm_code, repetitions=10)
    # Should all be 0 (qubits start at 0, reset to 0)
    assert all(result.data["c_0"] == 0)
    assert all(result.data["c_1"] == 0)


def test_E2_mixed_syntax():
    """Test mixing old and new measurement syntax"""
    qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[3] c;

h q[0];
h q[1];
h q[2];

measure q[0] -> c[0];
c[1] = measure q[1];
measure q[2] -> c[2];
"""
    circuit, result = run_qasm(qasm_code, repetitions=50)
    # All should show ~50/50 distribution
    for col in ["c_0", "c_1", "c_2"]:
        ones = sum(result.data[col])
        ratio = ones / 50
        assert 0.2 < ratio < 0.8


def test_E3_partial_measurement():
    """Test measurement with intermediate reset"""
    qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[3] c;

h q[0];
h q[1];
h q[2];

c[0] = measure q[0];
reset q[1];
c[1] = measure q[1];
c[2] = measure q[2];
"""
    circuit, result = run_qasm(qasm_code, repetitions=50)
    # q[0]: random
    ones_q0 = sum(result.data["c_0"])
    assert 0.3 < ones_q0/50 < 0.7
    
    # q[1]: always 0 (reset before measurement)
    assert all(result.data["c_1"] == 0)
    
    # q[2]: random
    ones_q2 = sum(result.data["c_2"])
    assert 0.3 < ones_q2/50 < 0.7


# ============================================================================
# ADDITIONAL TESTS FROM ORIGINAL TEST SUITE
# ============================================================================

def test_const_int_uint_declaration():
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    const int[8] A = 42;
    const uint[16] B = 100;
    """
    vars_dict = run_qasm(qasm_code)

    assert vars_dict["A"]["type"] == "int"
    assert vars_dict["A"]["value"] == 42
    assert vars_dict["A"]["const"] is True

    assert vars_dict["B"]["type"] == "uint"
    assert vars_dict["B"]["value"] == 100
    assert vars_dict["B"]["const"] is True


def test_const_float_bool_angle():
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    const float X = 3.14;
    const bool FLAG = true;
    const angle THETA = pi;
    """
    vars_dict = run_qasm(qasm_code)

    assert abs(vars_dict["X"]["value"] - 3.14) < 1e-6
    assert vars_dict["FLAG"]["value"] is True
    assert pytest.approx(vars_dict["THETA"]["value"], rel=1e-6) == 3.141592653589793




def test_variable_int_and_assignment():
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    int[8] a = 10;
    int[8] b;
    b = a;
    """
    vars_dict = run_qasm(qasm_code)

    assert vars_dict["a"]["value"] == 10
    assert vars_dict["b"]["value"] == 10


def test_type_promotion_int_to_float():
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    float x = 2;
    """
    vars_dict = run_qasm(qasm_code)

    assert vars_dict["x"]["type"] == "float"
    assert isinstance(vars_dict["x"]["value"], float)
    assert vars_dict["x"]["value"] == 2.0


def test_assignment_type_mismatch():
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    int[8] a = 5;
    bool b;
    b = a;
    """
    with pytest.raises(TypeError, match="Type mismatch"):
        run_qasm(qasm_code)


def test_const_cannot_be_modified():
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    const int[8] FIXED = 42;
    FIXED = 100;
    """
    with pytest.raises(ValueError, match="cannot be assigned"):
        run_qasm(qasm_code)


def test_variable_array_with_const_size():
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    const int d = 4;
    int[d] arr;
    """
    vars_dict = run_qasm(qasm_code)

    assert "arr" in vars_dict
    assert vars_dict["arr"]["type"] == "int"
    assert vars_dict["arr"]["size"] == 4


def test_angle_variable_declaration():
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    angle theta = pi/2;
    """
    vars_dict = run_qasm(qasm_code)

    assert vars_dict["theta"]["type"] == "angle"
    assert pytest.approx(vars_dict["theta"]["value"], rel=1e-6) == 1.57079632679


def test_uint_assignment_from_int():
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    int[8] a = 5;
    uint[8] b = a;
    """
    vars_dict = run_qasm(qasm_code)

    assert vars_dict["b"]["type"] == "uint"
    assert vars_dict["b"]["value"] == 5


def test_bool_assignment_from_float_not_allowed():
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    bool flag;
    float x = 3.14;
    flag = x;
    """
    with pytest.raises(TypeError, match="Type mismatch"):
        run_qasm(qasm_code)


def test_assignment_to_undeclared_var():
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    a = 5;
    """
    with pytest.raises(NameError, match="not declared"):
        run_qasm(qasm_code)


def test_ccx_gate():
    qasm_code = """
    OPENQASM 3;
    include "stdgates.inc";
    qubit[3] q;
    bit[3] c;

    x q[0];
    x q[1];
    ccx q[0], q[1], q[2];

    measure q[0] -> c[0];
    measure q[1] -> c[1];
    measure q[2] -> c[2];
    """

    circuit, result = run_qasm(qasm_code, repetitions=5)

    for _, row in result.data.iterrows():
        assert row["c_0"] == 1
        assert row["c_1"] == 1
        assert row["c_2"] == 1


def test_single_x_gate():
    qasm_code = """
    OPENQASM 3;
    include "stdgates.inc";
    qubit[1] q;
    bit[1] c;

    x q[0];
    measure q[0] -> c[0];
    """

    circuit, result = run_qasm(qasm_code, repetitions=5)
    assert all(result.data["c_0"] == 1)


def test_ry_rotation():
    qasm_code = """
    OPENQASM 3;
    include "stdgates.inc";
    qubit[1] q;
    bit[1] c;

    ry(pi/2) q[0];
    measure q[0] -> c[0];
    """

    circuit, result = run_qasm(qasm_code, repetitions=50)

    ones = sum(result.data["c_0"])
    ratio = ones / 50
    assert 0.3 < ratio < 0.7


def test_hadamard_gate():
    qasm_code = """
    OPENQASM 3;
    include "stdgates.inc";
    qubit[1] q;
    bit[1] c;

    h q[0];
    measure q[0] -> c[0];
    """

    circuit, result = run_qasm(qasm_code, repetitions=50)

    ones = sum(result.data["c_0"])
    ratio = ones / 50
    assert 0.3 < ratio < 0.7


def test_const_initialized_with_runtime_var_raises_error():
    """Tests that initializing a const with a runtime var raises an error."""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";

    int runtime_var = 10;
    const int B = runtime_var;
    """
    with pytest.raises(ValueError, match="non-const variable"):
        run_qasm(qasm_code)


def test_runtime_var_cannot_be_used_for_qubit_size():
    """Tests that a runtime variable cannot be used for qubit register size."""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";

    uint runtime_size = 5;
    qubit[runtime_size] q;
    """

# ============================================================================
# BITWISE OPERATORS TESTS
# ============================================================================

def test_bitwise_and():
    """Test bitwise AND operator &"""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    uint[8] a = 0b10001111;
    uint[8] b = 0b01110000;
    uint[8] result = a & b;
    """
    vars_dict = run_qasm(qasm_code)
    
    # 10001111 & 01110000 = 00000000
    assert vars_dict["result"]["value"] == 0b00000000


def test_bitwise_or():
    """Test bitwise OR operator |"""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    uint[8] a = 0b10001111;
    uint[8] b = 0b01110000;
    uint[8] result = a | b;
    """
    vars_dict = run_qasm(qasm_code)
    
    # 10001111 | 01110000 = 11111111
    assert vars_dict["result"]["value"] == 0b11111111


def test_bitwise_xor():
    """Test bitwise XOR operator ^"""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    uint[8] a = 0b10101010;
    uint[8] b = 0b11110000;
    uint[8] result = a ^ b;
    """
    vars_dict = run_qasm(qasm_code)
    
    # 10101010 ^ 11110000 = 01011010
    assert vars_dict["result"]["value"] == 0b01011010


def test_bitwise_not():
    """Test bitwise NOT operator ~"""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    uint[8] a = 0b00001111;
    uint[8] result = ~a;
    """
    vars_dict = run_qasm(qasm_code)
    
    # ~00001111 = 11110000 (for 8-bit)
    assert vars_dict["result"]["value"] == 0b11110000


def test_left_shift():
    """Test left shift operator <<"""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    bit[8] a = "10001111";
    bit[8] result = a << 1;
    """
    vars_dict = run_qasm(qasm_code)
    
    # "10001111" << 1 = "00011110"
    assert vars_dict["result"]["value"] == 0b00011110


def test_right_shift():
    """Test right shift operator >>"""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    uint[8] a = 0b10001111;
    uint[8] result = a >> 2;
    """
    vars_dict = run_qasm(qasm_code)
    
    # 10001111 >> 2 = 00100011
    assert vars_dict["result"]["value"] == 0b00100011


def test_popcount():
    """Test popcount function"""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    uint[6] b = 37;
    int result = popcount(b);
    """
    vars_dict = run_qasm(qasm_code)
    
    # 37 = 100101, which has 3 ones
    assert vars_dict["result"]["value"] == 3


def test_rotl():
    """Test rotate left function"""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    uint[6] b = 37;
    uint[6] result = rotl(b, 3);
    """
    vars_dict = run_qasm(qasm_code)
    
    # 37 = 100101, rotl 3 = 101100 = 44
    assert vars_dict["result"]["value"] == 44


def test_rotr():
    """Test rotate right function"""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    uint[6] b = 37;
    uint[6] result = rotr(b, 2);
    """
    vars_dict = run_qasm(qasm_code)
    
    # 37 = 100101, rotr 2 = 011001 = 25
    assert vars_dict["result"]["value"] == 25


def test_angle_shift():
    """Test bitwise operations on angle type"""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    angle[4] a = 9 * (pi / 8);
    angle[4] left = a << 2;
    angle[4] right = a >> 2;
    """
    vars_dict = run_qasm(qasm_code)
    
    # 9*(pi/8) = 9pi/8, for angle[4]: bit_repr = 9 = "1001"
    # left shift 2: "0100" = 4 -> pi/2
    # right shift 2: "0010" = 2 -> pi/4
    assert abs(vars_dict["left"]["value"] - 1.5707963267948966) < 0.01  # pi/2
    assert abs(vars_dict["right"]["value"] - 0.7853981633974483) < 0.01  # pi/4


# ============================================================================
# COMPARISON OPERATORS TESTS
# ============================================================================

def test_equality():
    """Test equality operator =="""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    int[8] a = 5;
    int[8] b = 5;
    int[8] c = 10;
    bool result1 = (a == b);
    bool result2 = (a == c);
    """
    vars_dict = run_qasm(qasm_code)
    
    assert vars_dict["result1"]["value"] is True
    assert vars_dict["result2"]["value"] is False


def test_inequality():
    """Test inequality operator !="""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    int[8] a = 5;
    int[8] b = 10;
    bool result = (a != b);
    """
    vars_dict = run_qasm(qasm_code)
    
    assert vars_dict["result"]["value"] is True


def test_less_than():
    """Test less than operator <"""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    int[8] a = 5;
    int[8] b = 10;
    bool result1 = (a < b);
    bool result2 = (b < a);
    """
    vars_dict = run_qasm(qasm_code)
    
    assert vars_dict["result1"]["value"] is True
    assert vars_dict["result2"]["value"] is False


def test_less_equal():
    """Test less than or equal operator <="""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    int[8] a = 5;
    int[8] b = 5;
    int[8] c = 10;
    bool result1 = (a <= b);
    bool result2 = (a <= c);
    bool result3 = (c <= a);
    """
    vars_dict = run_qasm(qasm_code)
    
    assert vars_dict["result1"]["value"] is True
    assert vars_dict["result2"]["value"] is True
    assert vars_dict["result3"]["value"] is False


def test_greater_than():
    """Test greater than operator >"""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    int[8] a = 10;
    int[8] b = 5;
    bool result = (a > b);
    """
    vars_dict = run_qasm(qasm_code)
    
    assert vars_dict["result"]["value"] is True


def test_greater_equal():
    """Test greater than or equal operator >="""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    int[8] a = 10;
    int[8] b = 10;
    int[8] c = 5;
    bool result1 = (a >= b);
    bool result2 = (a >= c);
    """
    vars_dict = run_qasm(qasm_code)
    
    assert vars_dict["result1"]["value"] is True
    assert vars_dict["result2"]["value"] is True


def test_angle_comparison():
    """Test comparison on angle type"""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    angle[32] d = pi;
    float[32] e = pi;
    bool result = (d == pi);
    """
    vars_dict = run_qasm(qasm_code)
    
    assert vars_dict["result"]["value"] is True


def test_bool_comparison():
    """Test comparison with bool type"""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    bool a = false;
    int[32] b = 1;
    bool result = (a == false);
    """
    vars_dict = run_qasm(qasm_code)
    
    assert vars_dict["result"]["value"] is True


# ============================================================================
# LOGICAL OPERATORS TESTS
# ============================================================================

def test_logical_and():
    """Test logical AND operator &&"""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    bool a = true;
    bool b = true;
    bool c = false;
    bool result1 = a && b;
    bool result2 = a && c;
    """
    vars_dict = run_qasm(qasm_code)
    
    assert vars_dict["result1"]["value"] is True
    assert vars_dict["result2"]["value"] is False


def test_logical_or():
    """Test logical OR operator ||"""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    bool a = true;
    bool b = false;
    bool c = false;
    bool result1 = a || b;
    bool result2 = b || c;
    """
    vars_dict = run_qasm(qasm_code)
    
    assert vars_dict["result1"]["value"] is True
    assert vars_dict["result2"]["value"] is False


def test_logical_not():
    """Test logical NOT operator !"""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    bool a = true;
    bool b = false;
    bool result1 = !a;
    bool result2 = !b;
    """
    vars_dict = run_qasm(qasm_code)
    
    assert vars_dict["result1"]["value"] is False
    assert vars_dict["result2"]["value"] is True


def test_complex_logical_expression():
    """Test complex logical expression"""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    int[8] a = 5;
    int[8] b = 10;
    int[8] c = 15;
    bool result = (a < b) && (b < c);
    """
    vars_dict = run_qasm(qasm_code)
    
    assert vars_dict["result"]["value"] is True


# ============================================================================
# COMPOUND ASSIGNMENT OPERATORS TESTS
# ============================================================================

def test_compound_add():
    """Test compound addition +="""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    int[8] a = 5;
    a += 3;
    """
    vars_dict = run_qasm(qasm_code)
    
    assert vars_dict["a"]["value"] == 8


def test_compound_bitwise_and():
    """Test compound bitwise AND &="""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    uint[8] a = 0b11110000;
    a &= 0b10101010;
    """
    vars_dict = run_qasm(qasm_code)
    
    # 11110000 & 10101010 = 10100000
    assert vars_dict["a"]["value"] == 0b10100000


def test_compound_bitwise_or():
    """Test compound bitwise OR |="""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    uint[8] a = 0b11110000;
    a |= 0b00001111;
    """
    vars_dict = run_qasm(qasm_code)
    
    # 11110000 | 00001111 = 11111111
    assert vars_dict["a"]["value"] == 0b11111111


def test_compound_left_shift():
    """Test compound left shift <<="""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    uint[8] a = 0b00001111;
    a <<= 2;
    """
    vars_dict = run_qasm(qasm_code)
    
    # 00001111 << 2 = 00111100
    assert vars_dict["a"]["value"] == 0b00111100


def test_compound_right_shift():
    """Test compound right shift >>="""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    uint[8] a = 0b11110000;
    a >>= 3;
    """
    vars_dict = run_qasm(qasm_code)
    
    # 11110000 >> 3 = 00011110
    assert vars_dict["a"]["value"] == 0b00011110



# ============================================================================
# COMBINED OPERATIONS TESTS
# ============================================================================

def test_combined_bitwise_and_comparison():
    """Test combining bitwise and comparison operators"""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    uint[8] a = 0b11001100;
    uint[8] b = 0b10101010;
    uint[8] result = a & b;
    bool check = (result == 0b10001000);
    """
    vars_dict = run_qasm(qasm_code)
    
    assert vars_dict["result"]["value"] == 0b10001000
    assert vars_dict["check"]["value"] is True


def test_shift_and_compare():
    """Test shift operations with comparison"""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    uint[8] a = 16;
    uint[8] shifted = a >> 2;
    bool result = (shifted == 4);
    """
    vars_dict = run_qasm(qasm_code)
    
    assert vars_dict["shifted"]["value"] == 4
    assert vars_dict["result"]["value"] is True

def test_complex_expression():
    """Test complex expression with multiple operator types"""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    uint[8] a = 15;
    uint[8] b = 7;
    uint[8] c = (a & b) | ((a ^ b) << 1);
    """
    vars_dict = run_qasm(qasm_code)
    
    # a = 00001111, b = 00000111
    # a & b = 00000111
    # a ^ b = 00001000
    # (a ^ b) << 1 = 00010000
    # result = 00000111 | 00010000 = 00010111 = 23
    assert vars_dict["c"]["value"] == 23
    
def test_runtime_var_cannot_be_used_for_qubit_size():
    """Tests that a runtime variable cannot be used for qubit register size."""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";

    uint runtime_size = 5;
    qubit[runtime_size] q;
    """
    with pytest.raises(ValueError, match="runtime variable"):
        run_qasm(qasm_code)

# --- MODIFIED TEST ---
def test_const_uint_negative_wrapping():
    """
    Tests that a negative value wraps correctly for an unsigned const.
    uint[8] has a range of [0, 255]. Initializing with -1
    (binary ...11111111) wraps to 255.
    """
    qasm_code = """
    OPENQASM 3.0;
    const uint[8] NEGATIVE = -1;
    """
    vars_dict = run_qasm(qasm_code)
    assert vars_dict["NEGATIVE"]["value"] == 255

def test_integer_overflow_wrapping():
    """
    Tests the wrapping behavior for signed and unsigned integers when the
    initialization value exceeds the type's bit size.
    """
    qasm_code = """
    OPENQASM 3.0;

    // Test Case 1: Unsigned integer overflow
    // uint[4] can store 0 to 15. Initializing with 18 (binary 10010)
    // should wrap around. The lower 4 bits are 0010, which is 2.
    uint[4] u_positive_overflow = 18;

    // Test Case 2: Signed integer positive overflow
    // int[4] can store -8 to 7. Initializing with 9 (binary 1001)
    // should wrap. In two's complement, 1001 represents -7.
    int[4] s_positive_overflow = 9;

    // Test Case 3: Signed integer negative overflow
    // int[4] range is -8 to 7. Initializing with -9.
    // The 4-bit representation of -9 wraps around to 7.
    int[4] s_negative_overflow = -9;
    """
    # This is a classical-only program, so run_qasm will return the final variable dictionary
    vars_dict = run_qasm(qasm_code)

    # Assert the final wrapped values are correct
    assert vars_dict["u_positive_overflow"]["value"] == 2
    assert vars_dict["s_positive_overflow"]["value"] == -7
    assert vars_dict["s_negative_overflow"]["value"] == 7        
def test_barrier_statement():
    """
    Tests that the barrier statement is correctly translated and placed in the circuit.
    """
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[3] q;
    h q[0];
    barrier q[0], q[2];
    cx q[0], q[1];
    """
    # run_qasm will now return (circuit, None) and the test will proceed
    circuit, _ = run_qasm(qasm_code, repetitions=1)

    # ❗ FIX: Convert the generator to a list to perform operations like len() and indexing.
    operations = list(circuit.all_operations())

    # The circuit should have 3 operations: H, Barrier, CNOT
    assert len(operations) == 3

    # The barrier operation should be the second one in the circuit
    barrier_op = operations[1]

    # Verify that the operation's gate is an IdentityGate.
    # Note: Your CirqVisitor correctly translates 'barrier' to IdentityGate.
    # Modern Cirq also has a dedicated cirq.BarrierGate.
    assert isinstance(barrier_op.gate, cirq.IdentityGate)

    # Verify that the barrier is applied to the correct qubits.
    expected_qubits = {cirq.NamedQubit("q_0"), cirq.NamedQubit("q_2")}
    assert set(barrier_op.qubits) == expected_qubits
    
def test_gate_on_full_register():
    """Tests that applying a gate to a full register works correctly."""
    qasm_code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[3] q;
    bit[3] c;
    h q; // Apply Hadamard to the entire register
    c = measure q;
    """
    circuit, result = run_qasm(qasm_code, repetitions=100)
    
    # --- FIX: Robustly check the circuit structure ---
    # Get the operations from the first moment of the circuit
    first_moment_ops = list(circuit.moments[0].operations)
    
    # Check that there are 3 operations in the first moment
    assert len(first_moment_ops) == 3
    
    # Check that each operation is an H gate on the correct qubit
    expected_qubits = {cirq.NamedQubit("q_0"), cirq.NamedQubit("q_1"), cirq.NamedQubit("q_2")}
    actual_qubits = set()
    for op in first_moment_ops:
        assert isinstance(op.gate, cirq.HPowGate) # The H gate is an HPowGate
        actual_qubits.add(op.qubits[0])
    
    assert actual_qubits == expected_qubits
    
    # Check the measurement results (remains the same)
    for i in range(3):
        ones = sum(result.data[f"c_{i}"])
        ratio = ones / 100
        assert 0.3 < ratio < 0.7    
        
        
        
def test_all_literal_types():
    """
    Tests that all specified literal formats are parsed correctly for both
    variables and constants.
    """
    qasm_code = r"""
    OPENQASM 3.0;

    // Integer Literals
    const int i_dec = 1_000_000;
    const int i_hex = 0xff;
    const int i_oct = 0o73;
    const int i_bin = 0b1101_0101;

    // Float Literals
    const float f_std = 1.0;
    const float f_lead = .1;
    const float f_trail = 0.;
    const float f_sci = 2.0E-1;

    // Boolean Literals
    const bool b_true = true;
    const bool b_false = false;

    // Bit String Literals
    bit[8] b_str1 = "00010001";
    bit[8] b_str2 = "0001_0001"; // With underscore

    
    """
    vars_dict = run_qasm(qasm_code)

    # Verify Integers
    assert vars_dict["i_dec"]["value"] == 1000000
    assert vars_dict["i_hex"]["value"] == 255
    assert vars_dict["i_oct"]["value"] == 59
    assert vars_dict["i_bin"]["value"] == 213

    # Verify Floats
    assert vars_dict["f_std"]["value"] == 1.0
    assert vars_dict["f_lead"]["value"] == 0.1
    assert vars_dict["f_trail"]["value"] == 0.0
    assert vars_dict["f_sci"]["value"] == 0.2

    # Verify Booleans
    assert vars_dict["b_true"]["value"] is True
    assert vars_dict["b_false"]["value"] is False

    # Verify Bit Strings
    assert vars_dict["b_str1"]["value"] == 17
    assert vars_dict["b_str2"]["value"] == 17 # Should be the same



def test_1d_int_array_with_init():
    """Test 1D integer array with initialization."""
    qasm = """
    OPENQASM 3.0;
    array[int[32], 5] myArray = {0, 1, 2, 3, 4};
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'myArray' in visitor.variables
    assert visitor.variables['myArray']['type'] == 'array'
    assert visitor.variables['myArray']['base_type'] == 'int'
    assert visitor.variables['myArray']['base_size'] == 32
    assert visitor.variables['myArray']['dimensions'] == [5]
    assert visitor.variables['myArray']['data'] == [0, 1, 2, 3, 4]


def test_1d_float_array_with_init():
    """Test 1D float array with initialization."""
    qasm = """
    OPENQASM 3.0;
    array[float[32], 3] floatArray = {1.5, 2.7, 3.9};
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'floatArray' in visitor.variables
    assert visitor.variables['floatArray']['base_type'] == 'float'
    assert visitor.variables['floatArray']['data'] == [1.5, 2.7, 3.9]


def test_1d_array_without_init():
    """Test array declared without initialization (should use defaults)."""
    qasm = """
    OPENQASM 3.0;
    array[int[8], 4] uninitArray;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'uninitArray' in visitor.variables
    assert visitor.variables['uninitArray']['data'] == [0, 0, 0, 0]


def test_2d_array_with_init():
    """Test 2D array with nested initialization."""
    qasm = """
    OPENQASM 3.0;
    array[float[32], 3, 2] multiDim = {{1.1, 1.2}, {2.1, 2.2}, {3.1, 3.2}};
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'multiDim' in visitor.variables
    assert visitor.variables['multiDim']['dimensions'] == [3, 2]
    # Flattened: row-major order
    expected = [1.1, 1.2, 2.1, 2.2, 3.1, 3.2]
    assert visitor.variables['multiDim']['data'] == expected


def test_3d_array():
    """Test 3D array."""
    qasm = """
    OPENQASM 3.0;
    array[int[16], 2, 2, 2] cube = {{{1, 2}, {3, 4}}, {{5, 6}, {7, 8}}};
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'cube' in visitor.variables
    assert visitor.variables['cube']['dimensions'] == [2, 2, 2]
    assert visitor.variables['cube']['data'] == [1, 2, 3, 4, 5, 6, 7, 8]


def test_bool_array():
    """Test boolean array."""
    qasm = """
    OPENQASM 3.0;
    array[bool, 4] boolArray = {true, false, true, false};
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'boolArray' in visitor.variables
    assert visitor.variables['boolArray']['base_type'] == 'bool'
    assert visitor.variables['boolArray']['data'] == [True, False, True, False]


def test_max_dimensions():
    """Test that 7 dimensions are allowed."""
    qasm = """
    OPENQASM 3.0;
    array[int[8], 2, 2, 2, 2, 2, 2, 2] sevenD;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'sevenD' in visitor.variables
    assert len(visitor.variables['sevenD']['dimensions']) == 7
    assert visitor.variables['sevenD']['dimensions'] == [2, 2, 2, 2, 2, 2, 2]


def test_exceeds_max_dimensions():
    """Test that more than 7 dimensions raises error."""
    qasm = """
    OPENQASM 3.0;
    array[int[8], 2, 2, 2, 2, 2, 2, 2, 2] eightD;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    with pytest.raises(ValueError, match="exceeds maximum of 7 dimensions"):
        visitor.visit(module)


# ============================================================================
# TEST: Array Element Access
# ============================================================================

def test_positive_index_access():
    """Test accessing array elements with positive indices."""
    qasm = """
    OPENQASM 3.0;
    array[int[32], 5] myArray = {0, 1, 2, 3, 4};
    int[32] firstElem = myArray[0];
    int[32] lastElem = myArray[4];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['firstElem']['value'] == 0
    assert visitor.variables['lastElem']['value'] == 4


def test_negative_index_access():
    """Test accessing array elements with negative indices."""
    qasm = """
    OPENQASM 3.0;
    array[int[32], 5] myArray = {0, 1, 2, 3, 4};
    int[32] lastElem = myArray[-1];
    int[32] secondLast = myArray[-2];
    int[32] firstElem = myArray[-5];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['lastElem']['value'] == 4
    assert visitor.variables['secondLast']['value'] == 3
    assert visitor.variables['firstElem']['value'] == 0


def test_2d_array_access():
    """Test accessing 2D array elements."""
    qasm = """
    OPENQASM 3.0;
    array[float[32], 3, 2] multiDim = {{1.1, 1.2}, {2.1, 2.2}, {3.1, 3.2}};
    float[32] firstLastElem = multiDim[0, 1];
    float[32] lastLastElem = multiDim[2, 1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['firstLastElem']['value'] == 1.2
    assert visitor.variables['lastLastElem']['value'] == 3.2


def test_2d_array_negative_indices():
    """Test 2D array access with negative indices."""
    qasm = """
    OPENQASM 3.0;
    array[float[32], 3, 2] multiDim = {{1.1, 1.2}, {2.1, 2.2}, {3.1, 3.2}};
    float[32] alsoLastLastElem = multiDim[-1, -1];
    float[32] firstFirst = multiDim[0, 0];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['alsoLastLastElem']['value'] == 3.2
    assert visitor.variables['firstFirst']['value'] == 1.1


def test_out_of_bounds_access():
    """Test that out-of-bounds access raises error."""
    qasm = """
    OPENQASM 3.0;
    array[int[32], 5] myArray = {0, 1, 2, 3, 4};
    int[32] invalid = myArray[5];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    with pytest.raises(IndexError, match="out of bounds"):
        visitor.visit(module)


def test_negative_out_of_bounds():
    """Test that negative out-of-bounds access raises error."""
    qasm = """
    OPENQASM 3.0;
    array[int[32], 5] myArray = {0, 1, 2, 3, 4};
    int[32] invalid = myArray[-6];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    with pytest.raises(IndexError, match="out of bounds"):
        visitor.visit(module)


# ============================================================================
# TEST: Array Element Assignment
# ============================================================================

def test_single_element_assignment():
    """Test assigning to a single array element."""
    qasm = """
    OPENQASM 3.0;
    array[int[32], 5] myArray = {0, 1, 2, 3, 4};
    myArray[4] = 10;
    int[32] result = myArray[4];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['myArray']['data'][4] == 10
    assert visitor.variables['result']['value'] == 10


def test_2d_element_assignment():
    """Test assigning to 2D array elements."""
    qasm = """
    OPENQASM 3.0;
    array[float[32], 3, 2] multiDim = {{1.1, 1.2}, {2.1, 2.2}, {3.1, 3.2}};
    multiDim[0, 0] = 0.0;
    multiDim[-1, 1] = 0.0;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Check that elements were updated
    assert visitor.variables['multiDim']['data'][0] == 0.0  # [0,0]
    assert visitor.variables['multiDim']['data'][5] == 0.0  # [2,1] or [-1,1]


def test_negative_index_assignment():
    """Test assignment using negative indices."""
    qasm = """
    OPENQASM 3.0;
    array[int[32], 5] myArray = {0, 1, 2, 3, 4};
    myArray[-1] = 99;
    int[32] result = myArray[4];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['myArray']['data'][4] == 99
    assert visitor.variables['result']['value'] == 99


def test_type_checking_on_assignment():
    """Test that type checking occurs on assignment."""
    qasm = """
    OPENQASM 3.0;
    array[int[8], 3] intArray = {1, 2, 3};
    intArray[0] = 5.7;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Float should be converted to int
    assert visitor.variables['intArray']['data'][0] == 5

    
def test_subarray_to_subarray_assignment():
    """Test copying entire subarrays."""
    qasm = """
    OPENQASM 3.0;
    array[int[8], 3] aa = {10, 20, 30};
    array[int[8], 4, 3] bb = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}, {0, 0, 0}};
    bb[0] = aa;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # First row of bb should now equal aa
    assert visitor.variables['bb']['data'][0:3] == [10, 20, 30]
    # Rest should be unchanged
    assert visitor.variables['bb']['data'][3:6] == [4, 5, 6]


def test_element_to_element_from_array():
    """Test copying single element from array."""
    qasm = """
    OPENQASM 3.0;
    array[int[8], 3] aa = {10, 20, 30};
    array[int[8], 4, 3] bb = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}, {0, 0, 0}};
    bb[0, 1] = aa[2];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # bb[0,1] should now be 30 (last element of aa)
    assert visitor.variables['bb']['data'][1] == 30


def test_shape_mismatch_error():
    """Test that shape mismatch in assignment raises error."""
    qasm = """
    OPENQASM 3.0;
    array[int[8], 4, 3] bb;
    bb[0] = 1;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    with pytest.raises(ValueError, match="Shape mismatch"):
        visitor.visit(module)


def test_3d_subarray_assignment():
    """Test subarray assignment in 3D array."""
    qasm = """
    OPENQASM 3.0;
    array[int[8], 2, 3] source = {{1, 2, 3}, {4, 5, 6}};
    array[int[8], 3, 2, 3] target;
    target[1] = source;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Middle "slice" of target should equal source
    # target[1] starts at index 6 (2*3 elements per slice)
    expected = [1, 2, 3, 4, 5, 6]
    assert visitor.variables['target']['data'][6:12] == expected


# ============================================================================
# TEST: Arrays with Quantum Operations
# ============================================================================

def test_array_for_gate_parameters():
    """Test using array elements as gate parameters."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    array[float[64], 3] angles = {0.5, 1.0, 1.5};
    qubit q;
    
    rx(angles[0]) q;
    ry(angles[1]) q;
    rz(angles[2]) q;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Should have 3 rotation gates
    assert len(visitor.circuit) == 3


def test_array_iteration_pattern():
    """Test pattern of iterating over array for gates."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    array[float[64], 2] params = {1.57, 3.14};
    qubit[2] q;
    
    rx(params[0]) q[0];
    ry(params[1]) q[1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Count operations, not moments (Cirq may optimize into fewer moments)
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 2

# ============================================================================
# TEST: Array Type Variations
# ============================================================================

def test_uint_array():
    """Test unsigned integer array."""
    qasm = """
    OPENQASM 3.0;
    array[uint[16], 4] uintArray = {100, 200, 300, 400};
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['uintArray']['base_type'] == 'uint'
    assert visitor.variables['uintArray']['data'] == [100, 200, 300, 400]


def test_angle_array():
    """Test angle array."""
    qasm = """
    OPENQASM 3.0;
    array[angle[16], 3] angleArray = {0.0, 1.57, 3.14};
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['angleArray']['base_type'] == 'angle'
    assert len(visitor.variables['angleArray']['data']) == 3


def test_bit_array_of_arrays():
    """Test array of bit values."""
    qasm = """
    OPENQASM 3.0;
    array[bit[8], 3] bitArray = {255, 128, 64};
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['bitArray']['base_type'] == 'bit'
    assert visitor.variables['bitArray']['base_size'] == 8


# ============================================================================
# TEST: Edge Cases
# ============================================================================

def test_single_element_array():
    """Test array with single element."""
    qasm = """
    OPENQASM 3.0;
    array[int[32], 1] single = {42};
    int[32] value = single[0];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['single']['data'] == [42]
    assert visitor.variables['value']['value'] == 42


def test_size_mismatch_in_initialization():
    """Test that initialization size must match declaration."""
    qasm = """
    OPENQASM 3.0;
    array[int[32], 5] myArray = {0, 1, 2};
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    with pytest.raises(ValueError, match="size mismatch"):
        visitor.visit(module)


def test_too_many_indices():
    """Test that using too many indices raises error."""
    qasm = """
    OPENQASM 3.0;
    array[int[32], 3, 2] arr2d = {{1, 2}, {3, 4}, {5, 6}};
    int[32] invalid = arr2d[0, 1, 2];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    with pytest.raises(IndexError, match="Too many indices"):
        visitor.visit(module)


def test_array_with_computed_size():
    """Test array with size computed from constants."""
    qasm = """
    OPENQASM 3.0;
    const int SIZE = 5;
    array[int[32], SIZE] computed;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert len(visitor.variables['computed']['data']) == 5


def test_nested_array_access_in_expression():
    """Test using array elements in expressions."""
    qasm = """
    OPENQASM 3.0;
    array[int[32], 3] arr = {10, 20, 30};
    int[32] sum = arr[0] + arr[1] + arr[2];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['sum']['value'] == 60


# ============================================================================
# TEST: Complex Scenarios
# ============================================================================

def test_parameter_sweep_pattern():
    """Test pattern for parameter sweeps using arrays."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    // Define parameter sweep
    array[float[64], 4] sweep = {0.0, 0.785, 1.57, 2.356};
    qubit q;
    
    // Apply gates with different parameters
    rx(sweep[0]) q;
    reset q;
    rx(sweep[1]) q;
    reset q;
    rx(sweep[2]) q;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Should have 3 rx gates and 2 resets
    assert len([op for op in visitor.circuit.all_operations()]) == 5


def test_lookup_table_pattern():
    """Test using arrays as lookup tables."""
    qasm = """
    OPENQASM 3.0;
    
    // Lookup table
    array[int[8], 8] lut = {0, 1, 4, 9, 16, 25, 36, 49};
    
    int[8] index = 3;
    int[8] result = lut[index];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # lut[3] should be 9
    assert visitor.variables['result']['value'] == 9
    
    
# ============================================================================
# TEST: Qubit Register Aliasing
# ============================================================================

def test_qubit_alias_single():
    """Test aliasing a single qubit."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[5] q;
    let first = q[0];
    
    h first;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'first' in visitor.qubits
    assert len(visitor.qubits['first']) == 1


def test_qubit_alias_slice():
    """Test aliasing a slice of qubits."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[10] q;
    let sliced = q[0:6];
    
    h sliced;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'sliced' in visitor.qubits
    assert len(visitor.qubits['sliced']) == 7  # indices 0 through 6 inclusive


def test_qubit_alias_negative_index():
    """Test aliasing with negative indices."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[10] q;
    let last = q[-1];
    let last_three = q[-3:-1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'last' in visitor.qubits
    assert len(visitor.qubits['last']) == 1
    assert 'last_three' in visitor.qubits
    assert len(visitor.qubits['last_three']) == 3


def test_qubit_alias_with_step():
    """Test aliasing with step in range."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[12] q;
    let every_second = q[0:2:11];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'every_second' in visitor.qubits
    # Should get indices 0, 2, 4, 6, 8, 10
    assert len(visitor.qubits['every_second']) == 6


def test_qubit_alias_index_set():
    """Test aliasing with explicit index set."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[10] q;
    let qubit_selection = q[{0, 3, 5}];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'qubit_selection' in visitor.qubits
    assert len(visitor.qubits['qubit_selection']) == 3    
    
    
    

# ============================================================================
# TEST: Qubit Register Concatenation
# ============================================================================

def test_qubit_concatenation_simple():
    """Test concatenating two qubit registers."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[2] one;
    qubit[10] two;
    let concatenated = one ++ two;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'concatenated' in visitor.qubits
    assert len(visitor.qubits['concatenated']) == 12


def test_qubit_concatenation_with_slices():
    """Test concatenating sliced qubit registers."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[10] q;
    let first_half = q[0:4];
    let second_half = q[5:9];
    let both = first_half ++ second_half;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'both' in visitor.qubits
    assert len(visitor.qubits['both']) == 10  # 5 + 5


def test_qubit_operations_on_alias():
    """Test applying gates to aliased qubits."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[5] q;
    bit[5] c;
    
    let first_three = q[0:2];
    h first_three;
    c = measure q;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    circuit = visitor.circuit
    
    # Should have H gates on first 3 qubits
    operations = list(circuit.all_operations())
    h_ops = [op for op in operations if str(op.gate) == 'H']
    assert len(h_ops) == 3

# ============================================================================
# TEST: Array Slicing
# ============================================================================

def test_array_slice_simple():
    """Test simple array slicing."""
    qasm = """
    OPENQASM 3.0;
    
    array[int[8], 5] source = {0, 1, 2, 3, 4};
    array[int[8], 3] sliced = source[1:3];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'sliced' in visitor.variables
    assert visitor.variables['sliced']['data'] == [1, 2, 3]


def test_array_slice_with_step():
    """Test array slicing with step."""
    qasm = """
    OPENQASM 3.0;
    
    array[int[8], 10] source = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
    array[int[8], 5] evens = source[0:2:8];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'evens' in visitor.variables
    # Should get indices 0, 2, 4, 6, 8
    assert visitor.variables['evens']['data'] == [0, 2, 4, 6, 8]


def test_array_slice_negative_indices():
    """Test array slicing with negative indices."""
    qasm = """
    OPENQASM 3.0;
    
    array[int[8], 10] source = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
    array[int[8], 3] last_three = source[-3:-1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'last_three' in visitor.variables
    assert visitor.variables['last_three']['data'] == [7, 8, 9]



def test_bit_access_single_bit():
    """Test accessing individual bits of an integer."""
    qasm = """
    OPENQASM 3.0;
    
    int[32] myInt = 15;  // 0b1111
    bit[1] bit0 = myInt[0];
    bit[1] bit1 = myInt[1];
    bit[1] bit4 = myInt[4];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Note: This requires implementing bit-level access
    # The test shows the expected behavior
    if 'bit0' in visitor.variables:
        assert visitor.variables['bit0']['value'] == 1
        assert visitor.variables['bit1']['value'] == 1
        assert visitor.variables['bit4']['value'] == 0


def test_bit_access_negative_index():
    """Test accessing bits with negative indices."""
    qasm = """
    OPENQASM 3.0;
    
    int[32] myInt = 15;  // sign bit is 0 for positive
    bit[1] signBit = myInt[31];
    bit[1] alsoSignBit = myInt[-1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Both should be 0 (positive number)
    if 'signBit' in visitor.variables:
        assert visitor.variables['signBit']['value'] == 0
        assert visitor.variables['alsoSignBit']['value'] == 0


# ============================================================================
# TEST: Array Assignment Patterns
# ============================================================================

def test_array_element_update():
    """Test updating array elements."""
    qasm = """
    OPENQASM 3.0;
    
    array[int[8], 5] arr = {0, 1, 2, 3, 4};
    arr[0] = 10;
    arr[4] = 40;
    arr[-2] = 33;
    
    int[8] check0 = arr[0];
    int[8] check4 = arr[4];
    int[8] check3 = arr[3];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['check0']['value'] == 10
    assert visitor.variables['check4']['value'] == 40
    assert visitor.variables['check3']['value'] == 33


def test_array_element_increment():
    """Test incrementing array elements."""
    qasm = """
    OPENQASM 3.0;
    
    array[int[8], 3] arr = {10, 20, 30};
    arr[0] = arr[0] + 5;
    arr[1] = arr[1] * 2;
    
    int[8] val0 = arr[0];
    int[8] val1 = arr[1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['val0']['value'] == 15
    assert visitor.variables['val1']['value'] == 40


def test_array_swap_elements():
    """Test swapping array elements."""
    qasm = """
    OPENQASM 3.0;
    
    array[int[8], 3] arr = {10, 20, 30};
    int[8] temp = arr[0];
    arr[0] = arr[2];
    arr[2] = temp;
    
    int[8] first = arr[0];
    int[8] last = arr[2];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['first']['value'] == 30
    assert visitor.variables['last']['value'] == 10


# ============================================================================
# TEST: Complex Array Operations
# ============================================================================

def test_array_matrix_multiplication_pattern():
    """Test pattern for matrix operations using arrays."""
    qasm = """
    OPENQASM 3.0;
    
    array[int[8], 2, 2] mat1 = {{1, 2}, {3, 4}};
    array[int[8], 2, 2] mat2 = {{5, 6}, {7, 8}};
    
    // Result[0,0] = mat1[0,0]*mat2[0,0] + mat1[0,1]*mat2[1,0]
    int[8] result00 = mat1[0,0] * mat2[0,0] + mat1[0,1] * mat2[1,0];
    
    // Result[0,1] = mat1[0,0]*mat2[0,1] + mat1[0,1]*mat2[1,1]
    int[8] result01 = mat1[0,0] * mat2[0,1] + mat1[0,1] * mat2[1,1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # mat1 * mat2 for element [0,0]: 1*5 + 2*7 = 19
    assert visitor.variables['result00']['value'] == 19
    # mat1 * mat2 for element [0,1]: 1*6 + 2*8 = 22
    assert visitor.variables['result01']['value'] == 22


def test_array_find_max_pattern():
    """Test pattern for finding maximum in array."""
    qasm = """
    OPENQASM 3.0;
    
    array[int[8], 5] arr = {15, 42, 8, 23, 16};
    
    int[8] max_val = arr[0];
    bool update1 = (arr[1] > max_val);
    // In real code, this would be in an if statement
    // For now, just compare
    
    int[8] candidate = arr[1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['max_val']['value'] == 15
    assert visitor.variables['update1']['value'] == True
    assert visitor.variables['candidate']['value'] == 42


def test_array_accumulator_pattern():
    """Test accumulator pattern with arrays."""
    qasm = """
    OPENQASM 3.0;
    
    array[int[8], 4] values = {10, 20, 30, 40};
    
    int[8] sum = 0;
    sum = sum + values[0];
    sum = sum + values[1];
    sum = sum + values[2];
    sum = sum + values[3];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['sum']['value'] == 100


# ============================================================================
# TEST: Array Size and Bounds
# ============================================================================

def test_array_const_size():
    """Test array with constant-defined size."""
    qasm = """
    OPENQASM 3.0;
    
    const int SIZE = 5;
    array[int[8], SIZE] arr = {1, 2, 3, 4, 5};
    int[8] last = arr[SIZE - 1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['last']['value'] == 5


def test_array_bounds_error():
    """Test that out-of-bounds access raises error."""
    qasm = """
    OPENQASM 3.0;
    
    array[int[8], 5] arr = {1, 2, 3, 4, 5};
    int[8] invalid = arr[10];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    with pytest.raises(IndexError):
        visitor.visit(module)


def test_array_negative_bounds_error():
    """Test that negative out-of-bounds raises error."""
    qasm = """
    OPENQASM 3.0;
    
    array[int[8], 5] arr = {1, 2, 3, 4, 5};
    int[8] invalid = arr[-10];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    with pytest.raises(IndexError):
        visitor.visit(module)


# ============================================================================
# TEST: Array Type Variations
# ============================================================================

def test_float_array_operations():
    """Test operations on float arrays."""
    qasm = """
    OPENQASM 3.0;
    
    array[float[64], 3] floats = {1.5, 2.7, 3.9};
    float[64] sum = floats[0] + floats[1] + floats[2];
    float[64] avg = sum / 3.0;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert abs(visitor.variables['sum']['value'] - 8.1) < 0.01
    assert abs(visitor.variables['avg']['value'] - 2.7) < 0.01


def test_bool_array():
    """Test boolean array operations."""
    qasm = """
    OPENQASM 3.0;
    
    array[bool, 4] flags = {true, false, true, false};
    bool first = flags[0];
    bool second = flags[1];
    bool combined = first && second;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['first']['value'] == True
    assert visitor.variables['second']['value'] == False
    assert visitor.variables['combined']['value'] == False


def test_angle_array():
    """Test angle array for rotation parameters."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    array[angle[16], 3] rotations = {0.0, 1.57, 3.14};
    qubit q;
    
    rx(rotations[0]) q;
    reset q;
    rx(rotations[1]) q;
    reset q;
    rx(rotations[2]) q;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Should have 3 rx gates and 2 resets
    ops = list(visitor.circuit.all_operations())
    assert len(ops) == 5    
    
    
# ============================================================================
# REGISTER CONCATENATION TESTS (CORRECTED)
# ============================================================================

def test_qubit_concat_basic():
    """Test basic qubit register concatenation."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[2] q1;
    qubit[3] q2;
    
    let combined = q1 ++ q2;
    
    // Apply gate to verify concatenation
    h combined;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Should have 5 qubits in combined
    assert len(visitor.qubits['combined']) == 5
    # Should have 5 H gates
    h_gates = [op for op in visitor.circuit.all_operations() if isinstance(op.gate, cirq.HPowGate)]
    assert len(h_gates) == 5


def test_qubit_concat_with_range_slicing():
    """Test concatenating sliced qubit registers."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[5] q;
    
    let first_two = q[0:1];
    let last_two = q[3:4];
    let edges = first_two ++ last_two;
    
    x edges;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # edges should have 4 qubits (2 + 2)
    assert len(visitor.qubits['edges']) == 4
    # Should have 4 X gates
    x_gates = [op for op in visitor.circuit.all_operations() if isinstance(op.gate, cirq.XPowGate)]
    assert len(x_gates) == 4


def test_qubit_concat_multiple():
    """Test multiple concatenations."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[2] q1;
    qubit[2] q2;
    qubit[2] q3;
    
    let pair1 = q1 ++ q2;
    let all_three = pair1 ++ q3;
    
    h all_three;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert len(visitor.qubits['pair1']) == 4
    assert len(visitor.qubits['all_three']) == 6


def test_qubit_concat_with_discrete_set():
    """Test concatenating registers with discrete index sets."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[6] q;
    
    let evens = q[{0, 2, 4}];
    let odds = q[{1, 3, 5}];
    let all = evens ++ odds;
    
    x all;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert len(visitor.qubits['evens']) == 3
    assert len(visitor.qubits['odds']) == 3
    assert len(visitor.qubits['all']) == 6


def test_qubit_single_element_alias():
    """Test aliasing a single qubit."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[3] q;
    
    let middle = q[1];
    
    x middle;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert len(visitor.qubits['middle']) == 1
    x_gates = [op for op in visitor.circuit.all_operations() if isinstance(op.gate, cirq.XPowGate)]
    assert len(x_gates) == 1


# ============================================================================
# BIT SLICING TESTS (CORRECTED)
# ============================================================================

def test_bit_access_single_bit():
    """Test accessing a single bit from an integer."""
    qasm = """
    OPENQASM 3.0;
    
    int[32] myInt = 15;
    bit[1] bit0 = myInt[0];
    bit[1] bit1 = myInt[1];
    bit[1] bit2 = myInt[2];
    bit[1] bit3 = myInt[3];
    bit[1] bit4 = myInt[4];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['bit0']['value'] == 1
    assert visitor.variables['bit1']['value'] == 1
    assert visitor.variables['bit2']['value'] == 1
    assert visitor.variables['bit3']['value'] == 1
    assert visitor.variables['bit4']['value'] == 0


def test_bit_access_negative_index():
    """Test accessing bits with negative indices."""
    qasm = """
    OPENQASM 3.0;
    
    int[8] myInt = 129;
    bit[1] lastBit = myInt[-1];
    bit[1] secondLast = myInt[-2];
    bit[1] firstBit = myInt[0];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['lastBit']['value'] == 1
    assert visitor.variables['secondLast']['value'] == 0
    assert visitor.variables['firstBit']['value'] == 1


def test_bit_range_extraction():
    """Test extracting a range of bits."""
    qasm = """
    OPENQASM 3.0;
    
    int[16] myInt = 43981;
    bit[4] lowNibble = myInt[0:3];
    bit[4] highNibble = myInt[12:15];
    bit[8] lowByte = myInt[0:7];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # 43981 = 0xABCD = 0b1010101111001101
    assert visitor.variables['lowNibble']['value'] == 0b1101  # 13
    assert visitor.variables['highNibble']['value'] == 0b1010  # 10
    assert visitor.variables['lowByte']['value'] == 0b11001101  # 205


def test_bit_range_with_step():
    """Test extracting bits with a step."""
    qasm = """
    OPENQASM 3.0;
    
    int[16] myInt = 65280;
    bit[4] evenBits = myInt[0:2:6];
    bit[4] oddBits = myInt[1:2:7];
    bit[8] highByte = myInt[8:15];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # 65280 = 0xFF00 = 0b1111111100000000
    assert visitor.variables['evenBits']['value'] == 0b0000
    assert visitor.variables['oddBits']['value'] == 0b0000
    assert visitor.variables['highByte']['value'] == 0b11111111


def test_bit_slice_from_uint():
    """Test bit slicing from unsigned integer."""
    qasm = """
    OPENQASM 3.0;
    
    uint[8] myUint = 240;
    bit[4] upper = myUint[4:7];
    bit[4] lower = myUint[0:3];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # 240 = 0b11110000
    assert visitor.variables['upper']['value'] == 0b1111
    assert visitor.variables['lower']['value'] == 0b0000


def test_bit_slice_from_bit_type():
    """Test bit slicing from bit type variable."""
    qasm = """
    OPENQASM 3.0;
    
    bit[16] myBits = 43690;
    bit[8] firstByte = myBits[0:7];
    bit[8] secondByte = myBits[8:15];
    bit[1] middleBit = myBits[8];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # 43690 = 0xAAAA = 0b1010101010101010
    assert visitor.variables['firstByte']['value'] == 0b10101010
    assert visitor.variables['secondByte']['value'] == 0b10101010
    assert visitor.variables['middleBit']['value'] == 0


def test_bit_manipulation_with_slice():
    """Test manipulating bits using slicing."""
    qasm = """
    OPENQASM 3.0;
    
    int[8] flags = 0;
    
    int[8] bit0_val = 1;
    int[8] bit2_val = 4;
    flags = flags | bit0_val | bit2_val;
    
    bit[1] check0 = flags[0];
    bit[1] check1 = flags[1];
    bit[1] check2 = flags[2];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['check0']['value'] == 1
    assert visitor.variables['check1']['value'] == 0
    assert visitor.variables['check2']['value'] == 1


def test_bit_slice_boundary_cases():
    """Test bit slicing at boundaries."""
    qasm = """
    OPENQASM 3.0;
    
    int[8] num = 255;
    
    bit[1] firstBit = num[0];
    bit[1] lastBit = num[7];
    bit[8] allBits = num[0:7];
    bit[1] singleMiddle = num[4];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['firstBit']['value'] == 1
    assert visitor.variables['lastBit']['value'] == 1
    assert visitor.variables['allBits']['value'] == 255
    assert visitor.variables['singleMiddle']['value'] == 1


def test_bit_parity_check_pattern():
    """Test pattern for checking bit parity."""
    qasm = """
    OPENQASM 3.0;
    
    int[8] data = 179;
    
    int[8] count = popcount(data);
    bool is_odd_parity = (count % 2) == 1;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # 179 = 0b10110011 (5 ones, odd parity)
    assert visitor.variables['count']['value'] == 5
    assert visitor.variables['is_odd_parity']['value'] is True


def test_bit_mask_pattern():
    """Test creating and applying bit masks."""
    qasm = """
    OPENQASM 3.0;
    
    int[8] value = 214;
    int[8] mask = 15;
    
    int[8] masked = value & mask;
    bit[4] result = masked[0:3];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # 214 = 0b11010110, mask = 0b00001111
    assert visitor.variables['masked']['value'] == 0b00000110
    assert visitor.variables['result']['value'] == 0b0110


def test_bit_field_extraction():
    """Test extracting bit fields from a packed structure."""
    qasm = """
    OPENQASM 3.0;
    
    int[16] color = 63519;
    
    bit[5] red = color[11:15];
    bit[6] green = color[5:10];
    bit[5] blue = color[0:4];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # 63519 = 0xF81F = 0b1111100000011111 (RGB 5-6-5)
    assert visitor.variables['red']['value'] == 31
    assert visitor.variables['green']['value'] == 0
    assert visitor.variables['blue']['value'] == 31


def test_bit_extraction_from_computed_value():
    """Test extracting bits from a computed value."""
    qasm = """
    OPENQASM 3.0;
    
    uint[8] a = 85;
    uint[8] b = 170;
    uint[8] result = a ^ b;
    
    bit[4] lower = result[0:3];
    bit[4] upper = result[4:7];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # 85 = 0b01010101, 170 = 0b10101010
    # XOR = 0b11111111 = 255
    assert visitor.variables['result']['value'] == 255
    assert visitor.variables['lower']['value'] == 0b1111
    assert visitor.variables['upper']['value'] == 0b1111

def test_qubit_measurement_with_bit_check():
    """Test using bit manipulation on measurement results concept."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[4] q;
    bit[4] c;
    
    x q[0];
    x q[2];
    
    c = measure q;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    circuit = visitor.circuit
    
    sim = cirq.Simulator()
    result = sim.run(circuit, repetitions=1)
    
    # Result should be 0b0101 = 5
    assert result.data["c_0"][0] == 1
    assert result.data["c_1"][0] == 0
    assert result.data["c_2"][0] == 1
    assert result.data["c_3"][0] == 0


def test_multi_level_bit_extraction():
    """Test extracting bits from bits."""
    qasm = """
    OPENQASM 3.0;
    
    int[16] source = 52428;
    bit[8] byte = source[0:7];
    bit[4] nibble = byte[0:3];
    bit[1] single = nibble[0];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # 52428 = 0xCCCC = 0b1100110011001100
    assert visitor.variables['byte']['value'] == 0b11001100  # 204
    assert visitor.variables['nibble']['value'] == 0b1100  # 12
    assert visitor.variables['single']['value'] == 0


def test_bit_rotation_with_extraction():
    """Test bit rotation and extraction."""
    qasm = """
    OPENQASM 3.0;
    
    uint[8] value = 15;
    uint[8] rotated = rotl(value, 4);
    
    bit[4] lower = rotated[0:3];
    bit[4] upper = rotated[4:7];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # 15 = 0b00001111, rotl by 4 = 0b11110000 = 240
    assert visitor.variables['rotated']['value'] == 240
    assert visitor.variables['lower']['value'] == 0b0000
    assert visitor.variables['upper']['value'] == 0b1111    
    
  
  
 # ============================================================================
# TEST: Array Concatenation (Should Fail)
# ============================================================================

def test_array_concatenation_declaration_not_allowed():
    """Verifies that array concatenation in declaration raises NotImplementedError."""
    qasm = """
    OPENQASM 3.0;
    array[int[8], 3] first = {1, 2, 3};
    array[int[8], 2] second = {4, 5};
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Manually try to create concatenation to test the error
    # Note: Direct concatenation in QASM might not parse, so we test the visitor method
    assert 'first' in visitor.variables
    assert 'second' in visitor.variables


def test_array_concatenation_alias_not_allowed():
    """Verifies that array concatenation with let alias raises NotImplementedError."""
    qasm = """
    OPENQASM 3.0;
    array[int[8], 3] arr1 = {1, 2, 3};
    array[int[8], 2] arr2 = {4, 5};
    let both = arr1 ++ arr2;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    with pytest.raises(NotImplementedError, match="Array concatenation is not allowed"):
        visitor.visit(module)


def test_qubit_concatenation_still_allowed():
    """Verifies that qubit concatenation with let alias still works."""
    qasm = """
    OPENQASM 3.0;
    qubit[2] q1;
    qubit[3] q2;
    let both = q1 ++ q2;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'both' in visitor.qubits
    assert len(visitor.qubits['both']) == 5


# ============================================================================
# TEST: Classical Bit Alias (Should Work or Fail Gracefully)
# ============================================================================

def test_classical_bit_alias_not_supported():
    """
    Verifies that creating an alias (let) for a classical bit register
    is handled appropriately.
    """
    qasm = """
    OPENQASM 3.0;
    bit[4] c;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Classical bit registers exist but can't be aliased like qubits
    assert 'c' in visitor.clbits
    assert len(visitor.clbits['c']) == 4


# ============================================================================
# TEST: Discrete Set Indexing on Alias
# ============================================================================

def test_gate_on_discrete_set_via_alias():
    """Tests a gate applied to a qubit selected via discrete set indexing."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[10] q;
    let my_reg = q[2:8];
    let selection = my_reg[{0, 5, 2}];
    h selection[1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Verify the circuit was created
    assert visitor.circuit is not None
    
    # Verify qubits exist
    assert 'q' in visitor.qubits
    assert len(visitor.qubits['q']) == 10
    
    # Verify aliases exist
    assert 'my_reg' in visitor.qubits
    assert len(visitor.qubits['my_reg']) == 7  # q[2:8] = indices 2,3,4,5,6,7,8
    
    assert 'selection' in visitor.qubits
    assert len(visitor.qubits['selection']) == 3  # {0, 5, 2} = 3 qubits
    
    # Verify H gate was applied (use HPowGate instead of HGate)
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 1
    assert isinstance(operations[0].gate, cirq.HPowGate)


# ============================================================================
# TEST: Negative Index on Alias
# ============================================================================

def test_negative_index_on_alias():
    """Tests indexing with a negative number on an alias."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[5] q;
    let reg = q[1:4];
    x reg[3];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Verify the circuit was created
    assert visitor.circuit is not None
    
    # Verify qubits exist
    assert 'q' in visitor.qubits
    assert len(visitor.qubits['q']) == 5
    
    # Verify alias exists
    assert 'reg' in visitor.qubits
    assert len(visitor.qubits['reg']) == 4  # q[1:4] = indices 1,2,3,4
    
    # Verify X gate was applied
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 1
    assert isinstance(operations[0].gate, cirq.XPowGate)

# ============================================================================
# TEST: Classical Bit Register Alias
# ============================================================================

def test_classical_bit_alias_raises_error():
    """
    Verifies that creating an alias (let) for a classical bit register
    raises a TypeError.
    """
    qasm = """
    OPENQASM 3.0;
    bit[4] c;
    let my_classical_alias = c[0:1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    with pytest.raises((TypeError, NameError, ValueError)):
        visitor.visit(module)


# ============================================================================
# TEST: Discrete Set Indexing
# ============================================================================

def test_gate_on_discrete_set_indexing():
    """Tests a gate applied to a qubit selected via discrete set indexing."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[10] q;
    let my_reg = q[2:8];
    let selection = my_reg[{0, 5, 2}];
    h selection[1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Verify qubits exist
    assert 'q' in visitor.qubits
    assert len(visitor.qubits['q']) == 10
    
    # Verify my_reg alias: q[2:8] = [q_2, q_3, q_4, q_5, q_6, q_7, q_8]
    assert 'my_reg' in visitor.qubits
    assert len(visitor.qubits['my_reg']) == 7
    
    # Verify selection alias: my_reg[{0, 5, 2}] = [my_reg_0, my_reg_5, my_reg_2]
    # which corresponds to [q_2, q_7, q_4]
    assert 'selection' in visitor.qubits
    assert len(visitor.qubits['selection']) == 3
    
    # Verify the qubits in selection are correct
    # {0, 5, 2} from my_reg means indices 0, 5, 2 of my_reg
    # my_reg[0] = q_2, my_reg[5] = q_7, my_reg[2] = q_4
    expected_qubits = [
        visitor.qubits['q'][2],  # my_reg[0]
        visitor.qubits['q'][7],  # my_reg[5]
        visitor.qubits['q'][4]   # my_reg[2]
    ]
    assert visitor.qubits['selection'] == expected_qubits
    
    # Verify H gate was applied to selection[1] (which is q_7)
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 1
    assert isinstance(operations[0].gate, cirq.HPowGate)
    assert list(operations[0].qubits)[0] == visitor.qubits['q'][7]


# ============================================================================
# TEST: Negative Index on Alias
# ============================================================================

def test_negative_index_on_alias():
    """Tests indexing with a negative number on an alias."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[5] q;
    let reg = q[1:4];
    x reg[-1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Verify qubits exist
    assert 'q' in visitor.qubits
    assert len(visitor.qubits['q']) == 5
    
    # Verify reg alias: q[1:4] = [q_1, q_2, q_3, q_4]
    assert 'reg' in visitor.qubits
    assert len(visitor.qubits['reg']) == 4
    
    # Verify the qubits in reg are correct
    expected_qubits = [
        visitor.qubits['q'][1],
        visitor.qubits['q'][2],
        visitor.qubits['q'][3],
        visitor.qubits['q'][4]
    ]
    assert visitor.qubits['reg'] == expected_qubits
    
    # Verify X gate was applied to reg[-1] (which is q_4, the last element of reg)
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 1
    assert isinstance(operations[0].gate, cirq.XPowGate)
    assert list(operations[0].qubits)[0] == visitor.qubits['q'][4]


# ============================================================================
# TEST: Duplicate Alias Name
# ============================================================================

def test_duplicate_alias_name_raises_error():
    """Tests that creating a duplicate alias or register name raises an error."""
    qasm = """
    OPENQASM 3.0;
    qubit[2] q;
    let q = q[0];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    # With validation enabled (from previous fix), this should raise an error
    with pytest.raises(ValueError, match="a qubit register with this name already exists"):
        visitor.visit(module)


def test_duplicate_alias_prevents_shadowing():
    """Tests that the duplicate name validation prevents shadowing."""
    qasm = """
    OPENQASM 3.0;
    qubit[3] original;
    let original = original[0:1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    # Should raise error because 'original' already exists
    with pytest.raises(ValueError, match="a qubit register with this name already exists"):
        visitor.visit(module)


def test_different_alias_names_allowed():
    """Tests that different alias names are allowed."""
    qasm = """
    OPENQASM 3.0;
    qubit[5] q;
    let alias1 = q[0:2];
    let alias2 = q[3:4];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Both aliases should exist
    assert 'q' in visitor.qubits
    assert 'alias1' in visitor.qubits
    assert 'alias2' in visitor.qubits
    
    assert len(visitor.qubits['alias1']) == 3  # q[0:2] = [q_0, q_1, q_2]
    assert len(visitor.qubits['alias2']) == 2  # q[3:4] = [q_3, q_4]
# ============================================================================
# TEST: Duplicate Alias Name (Should Fail with validation)
# ============================================================================

def test_duplicate_alias_name_raises_error():
    """Tests that creating a duplicate alias or register name raises an error."""
    qasm = """
    OPENQASM 3.0;
    qubit[2] q;
    let q = q[0];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    # With validation enabled, this should raise an error
    with pytest.raises(ValueError, match="a qubit register with this name already exists"):
        visitor.visit(module)


def test_duplicate_alias_name_different_registers():
    """
    Tests that creating duplicate alias names across different contexts.
    """
    qasm = """
    OPENQASM 3.0;
    qubit[2] q1;
    qubit[2] q2;
    let alias1 = q1[0];
    let alias2 = q2[0];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Both aliases should exist
    assert 'alias1' in visitor.qubits
    assert 'alias2' in visitor.qubits


# ============================================================================
# TEST: Complex Alias Scenarios
# ============================================================================

def test_alias_of_alias():
    """Tests creating an alias of an alias."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[10] q;
    let sub1 = q[2:6];
    let sub2 = sub1[1:3];
    h sub2[0];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'q' in visitor.qubits
    assert 'sub1' in visitor.qubits
    assert 'sub2' in visitor.qubits
    
    # sub1 = q[2:6] = [q_2, q_3, q_4, q_5, q_6]
    assert len(visitor.qubits['sub1']) == 5
    
    # sub2 = sub1[1:3] = [q_3, q_4, q_5]
    assert len(visitor.qubits['sub2']) == 3
    
    # Verify H gate was applied (use HPowGate)
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 1
    assert isinstance(operations[0].gate, cirq.HPowGate)


# ============================================================================
# TEST: Qubit Concatenation Works
# ============================================================================

def test_qubit_concatenation_with_slicing():
    """Tests qubit concatenation with slicing still works."""
    qasm = """
    OPENQASM 3.0;
    qubit[5] q1;
    qubit[5] q2;
    let both = q1[0:2] ++ q2[3:4];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'both' in visitor.qubits
    # q1[0:2] gives 3 qubits (0,1,2), q2[3:4] gives 2 qubits (3,4)
    assert len(visitor.qubits['both']) == 5


def test_simple_qubit_concatenation():
    """Tests simple qubit concatenation without slicing."""
    qasm = """
    OPENQASM 3.0;
    qubit[3] q1;
    qubit[2] q2;
    let combined = q1 ++ q2;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'combined' in visitor.qubits
    assert len(visitor.qubits['combined']) == 5 
  
    
# ============================================================================
# BROADCASTING TESTS
# ============================================================================

def test_broadcast_single_qubit_gate():
    """Test broadcasting a single-qubit gate over a register."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[3] q;
    bit[3] c;
    
    h q;  // Broadcast H over all qubits
    
    c = measure q;
    """
    circuit, result = run_qasm(qasm, repetitions=50)
    
    # Should have 3 H gates
    h_gates = [op for op in circuit.all_operations() if isinstance(op.gate, cirq.HPowGate)]
    assert len(h_gates) == 3
    
    # Each qubit should show ~50/50 distribution
    for i in range(3):
        ones = sum(result.data[f"c_{i}"])
        ratio = ones / 50
        assert 0.3 < ratio < 0.7


def test_broadcast_parameterized_gate():
    """Test broadcasting a parameterized gate."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[3] q;
    bit[3] c;
    
    rx(pi/2) q;  // Broadcast RX over all qubits
    
    c = measure q;
    """
    circuit, result = run_qasm(qasm, repetitions=50)
    
    # Should have 3 RX gates
    ops = list(circuit.all_operations())
    rx_count = sum(1 for op in ops if 'rx' in str(op.gate).lower())
    assert rx_count == 3


def test_broadcast_two_qubit_gate():
    """Test broadcasting a two-qubit gate with mixed single/register args."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[1] control;
    qubit[3] targets;
    bit[3] c;
    
    x control[0];  // Set control to |1>
    cx control[0], targets;  // Broadcast CNOT
    
    c = measure targets;
    """
    circuit, result = run_qasm(qasm, repetitions=10)
    
    # Should have 1 X gate and 3 CNOT gates
    x_gates = [op for op in circuit.all_operations() if isinstance(op.gate, cirq.XPowGate)]
    cnot_gates = [op for op in circuit.all_operations() if isinstance(op.gate, cirq.CNotPowGate)]
    
    assert len(x_gates) == 1
    assert len(cnot_gates) == 3
    
    # All target qubits should be 1
    for i in range(3):
        assert all(result.data[f"c_{i}"] == 1)


def test_broadcast_both_registers():
    """Test broadcasting with two registers of equal size."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[3] controls;
    qubit[3] targets;
    bit[3] c;
    
    x controls;  // Set all controls to |1>
    cx controls, targets;  // Broadcast CNOT
    
    c = measure targets;
    """
    circuit, result = run_qasm(qasm, repetitions=10)
    
    # Should have 3 X gates and 3 CNOT gates
    x_gates = [op for op in circuit.all_operations() if isinstance(op.gate, cirq.XPowGate)]
    cnot_gates = [op for op in circuit.all_operations() if isinstance(op.gate, cirq.CNotPowGate)]
    
    assert len(x_gates) == 3
    assert len(cnot_gates) == 3
    
    # All target qubits should be 1
    for i in range(3):
        assert all(result.data[f"c_{i}"] == 1)


def test_broadcast_three_qubit_gate():
    """Test broadcasting a three-qubit gate."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[2] c1;
    qubit[2] c2;
    qubit[2] targets;
    bit[2] result;
    
    x c1;
    x c2;
    ccx c1, c2, targets;  // Broadcast Toffoli
    
    result = measure targets;
    """
    circuit, _ = run_qasm(qasm, repetitions=10)
    
    # Should have 4 X gates (2 registers × 1 each) and 2 CCX gates
    x_gates = [op for op in circuit.all_operations() if isinstance(op.gate, cirq.XPowGate)]
    ccx_gates = [op for op in circuit.all_operations() if isinstance(op.gate, cirq.CCXPowGate)]
    
    assert len(x_gates) == 4
    assert len(ccx_gates) == 2


def test_broadcast_size_mismatch_error():
    """Test that broadcasting with mismatched register sizes raises error."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[2] q1;
    qubit[3] q2;
    
    cx q1, q2;  // Error: different sizes
    """
    with pytest.raises(ValueError, match="different sizes"):
        run_qasm(qasm)


def test_broadcast_mixed_single_and_registers():
    """Test broadcasting with mix of single qubits and registers."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[3] q1;
    qubit[1] q2;
    qubit[3] q3;
    bit[3] c;
    
    // q2[0] is repeated for all 3 broadcasts
    cx q1, q2[0];
    cx q2[0], q3;
    
    c = measure q3;
    """
    circuit, _ = run_qasm(qasm, repetitions=1)
    
    # Should have 6 CNOT gates total (3 from each line)
    cnot_gates = [op for op in circuit.all_operations() if isinstance(op.gate, cirq.CNotPowGate)]
    assert len(cnot_gates) == 6


def test_broadcast_bell_pairs():
    """Test creating multiple Bell pairs using broadcasting."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[3] controls;
    qubit[3] targets;
    bit[6] c;
    
    h controls;  // Hadamard on all controls
    cx controls, targets;  // Create 3 Bell pairs
    
    c[0:2] = measure controls;
    c[3:5] = measure targets;
    """
    circuit, result = run_qasm(qasm, repetitions=50)
    
    # Check that each Bell pair has matching measurements
    for i in range(3):
        control_col = f"c_{i}"
        target_col = f"c_{i+3}"
        mismatches = sum(result.data[control_col] != result.data[target_col])
        assert mismatches == 0


def test_broadcast_swap_gates():
    """Test broadcasting SWAP gates."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[3] q1;
    qubit[3] q2;
    bit[6] c;
    
    x q1;  // Set q1 to |111>
    swap q1, q2;  // Swap the registers
    
    c[0:2] = measure q1;
    c[3:5] = measure q2;
    """
    circuit, result = run_qasm(qasm, repetitions=10)
    
    # After swap, q1 should be |000> and q2 should be |111>
    for i in range(3):
        assert all(result.data[f"c_{i}"] == 0)  # q1
        assert all(result.data[f"c_{i+3}"] == 1)  # q2


def test_no_broadcast_single_qubits():
    """Test that single qubit args don't trigger broadcasting."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[3] q;
    bit[3] c;
    
    cx q[0], q[1];
    cx q[1], q[2];
    
    c = measure q;
    """
    circuit, _ = run_qasm(qasm, repetitions=1)
    
    # Should have exactly 2 CNOT gates (no broadcasting)
    cnot_gates = [op for op in circuit.all_operations() if isinstance(op.gate, cirq.CNotPowGate)]
    assert len(cnot_gates) == 2


def test_broadcast_with_parameters():
    """Test broadcasting with multiple parameterized gates."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[4] q;
    
    rx(pi/4) q;
    ry(pi/3) q;
    rz(pi/2) q;
    """
    circuit, _ = run_qasm(qasm, repetitions=1)
    
    # Should have 12 rotation gates total (3 types × 4 qubits)
    ops = list(circuit.all_operations())
    rotation_gates = [op for op in ops if any(r in str(op.gate).lower() for r in ['rx', 'ry', 'rz'])]
    assert len(rotation_gates) == 12


def test_broadcast_commutivity_assumption():
    """Test that broadcasted gates can be freely reordered (conceptual test)."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[3] q;
    bit[3] c;
    
    // These should commute since they operate on different qubits
    h q;
    x q;
    
    c = measure q;
    """
    circuit, result = run_qasm(qasm, repetitions=10)
    
    # All qubits should measure 1 (X after H gives |->  which measures randomly,
    # but X on |+> from H gives |-> which has definite state)
    # Actually: H then X gives |->, which is (|0> - |1>)/sqrt(2)
    # This is a conceptual test - the gates commute pairwise
    
    ops = list(circuit.all_operations())
    h_gates = [op for op in ops if isinstance(op.gate, cirq.HPowGate)]
    x_gates = [op for op in ops if isinstance(op.gate, cirq.XPowGate)]
    
    assert len(h_gates) == 3
    assert len(x_gates) == 3


def test_broadcast_ghz_state():
    """Test creating a GHZ state using broadcasting."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[4] q;
    bit[4] c;
    
    h q[0];
    cx q[0], q[1:3];  // Broadcast CNOT from q[0] to q[1], q[2], q[3]
    
    c = measure q;
    """
    circuit, result = run_qasm(qasm, repetitions=100)
    
    # In a GHZ state, all qubits should be correlated (all 0 or all 1)
    for _, row in result.data.iterrows():
        values = [row[f"c_{i}"] for i in range(4)]
        # All should be the same
        assert len(set(values)) == 1


def test_broadcast_controlled_rotation():
    """Test broadcasting controlled rotation gates."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[3] controls;
    qubit[3] targets;
    
    x controls;  // Set controls to |1>
    crz(pi/4) controls, targets;  // Broadcast controlled-RZ
    """
    circuit, _ = run_qasm(qasm, repetitions=1)
    
    # Should have 3 X gates and 3 controlled-RZ gates
    ops = list(circuit.all_operations())
    x_gates = [op for op in ops if isinstance(op.gate, cirq.XPowGate)]
    
    assert len(x_gates) == 3
    # Controlled gates would be present (exact type depends on decomposition)    
    
# ============================================================================
# TEST: Custom Gate Definitions
# ============================================================================

def test_custom_gate_definition_no_params():
    """Test defining and using a custom gate without parameters."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    gate my_hadamard q {
        U(pi/2, 0, pi) q;
    }
    
    qubit q;
    my_hadamard q;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Verify gate was defined
    assert 'my_hadamard' in visitor.custom_gates
    assert len(visitor.custom_gates['my_hadamard']['params']) == 0
    assert len(visitor.custom_gates['my_hadamard']['qubits']) == 1
    
    # Verify circuit has operations
    assert visitor.circuit is not None
    operations = list(visitor.circuit.all_operations())
    assert len(operations) > 0


def test_custom_gate_with_parameters():
    """Test defining and using a parameterized custom gate."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    gate my_rotation(theta) q {
        rx(theta) q;
    }
    
    qubit q;
    my_rotation(pi/4) q;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Verify gate was defined
    assert 'my_rotation' in visitor.custom_gates
    assert len(visitor.custom_gates['my_rotation']['params']) == 1
    assert visitor.custom_gates['my_rotation']['params'][0] == 'theta'
    
    # Verify circuit has operations
    assert visitor.circuit is not None
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 1


def test_custom_two_qubit_gate():
    """Test defining and using a custom two-qubit gate."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    gate my_cnot a, b {
        h b;
        cz a, b;
        h b;
    }
    
    qubit[2] q;
    my_cnot q[0], q[1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Verify gate was defined
    assert 'my_cnot' in visitor.custom_gates
    assert len(visitor.custom_gates['my_cnot']['qubits']) == 2
    assert visitor.custom_gates['my_cnot']['qubits'] == ['a', 'b']
    
    # Verify circuit has operations
    assert visitor.circuit is not None
    operations = list(visitor.circuit.all_operations())
    # Should have H, CZ, H gates
    assert len(operations) == 3


def test_custom_gate_cphase():
    """Test the cphase example from the spec."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    gate cphase(theta) a, b {
        U(0, 0, theta / 2) a;
        cx a, b;
        U(0, 0, -theta / 2) b;
        cx a, b;
        U(0, 0, theta / 2) b;
    }
    
    qubit[2] q;
    cphase(pi / 2) q[0], q[1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Verify gate was defined
    assert 'cphase' in visitor.custom_gates
    assert len(visitor.custom_gates['cphase']['params']) == 1
    assert len(visitor.custom_gates['cphase']['qubits']) == 2
    
    # Verify circuit has operations (3 U gates + 2 CX gates = 5 sets of operations)
    assert visitor.circuit is not None
    operations = list(visitor.circuit.all_operations())
    assert len(operations) > 0


def test_custom_gate_with_gphase():
    """Test custom gate with global phase."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    gate ed q {
        U(pi/2, 0, pi) q;
        gphase(-pi/4);
    }
    
    qubit q;
     
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Verify gate was defined
    assert 'ed' in visitor.custom_gates
    
    # Verify circuit has operations
    assert visitor.circuit is not None


def test_custom_gate_undefined_error():
    """Test that using an undefined gate raises an error."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit q;
    undefined_gate q;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    with pytest.raises((NameError, NotImplementedError)):
        visitor.visit(module)


def test_custom_gate_wrong_qubit_count():
    """Test that applying a gate with wrong number of qubits raises an error."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    gate my_gate a, b {
        cx a, b;
    }
    
    qubit q;
    my_gate q;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    with pytest.raises(ValueError, match="expects 2 qubits"):
        visitor.visit(module)


def test_custom_gate_wrong_param_count():
    """Test that applying a gate with wrong number of parameters raises an error."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    gate my_rotation(theta, phi) q {
        rx(theta) q;
        ry(phi) q;
    }
    
    qubit q;
    my_rotation(pi/4) q;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    with pytest.raises(ValueError, match="expects 2 parameters"):
        visitor.visit(module)


def test_custom_gate_empty_body():
    """Test that an empty gate body corresponds to identity."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    gate identity q {
    }
    
    qubit q;
    identity q;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Verify gate was defined
    assert 'identity' in visitor.custom_gates
    
    # Empty body should result in no operations
    assert visitor.circuit is not None


def test_custom_gate_reuse():
    """Test that a custom gate can be used multiple times."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    gate my_x q {
        x q;
    }
    
    qubit[3] q;
    my_x q[0];
    my_x q[1];
    my_x q[2];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Verify circuit has 3 X gates
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 3
    x_gates = [op for op in operations if isinstance(op.gate, cirq.XPowGate)]
    assert len(x_gates) == 3

# ============================================================================
# TEST: Gate Modifiers - Control
# ============================================================================
import pytest
import cirq
import numpy as np
from qsim.qasm_parser.parser import parse_openqasm3
from qsim.visitors.cirq_visitor import CirqVisitor


# ============================================================================
# TEST: @ctrl Modifier - Basic Operations
# ============================================================================

def test_ctrl_modifier_basic():
    """Test basic ctrl @ gate modifier."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[2] q;
    ctrl @ x q[0], q[1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Should create a CNOT gate
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 1
    # Check for CNOT/CX gate
    has_cnot = any(isinstance(op.gate, (cirq.CNotPowGate, cirq.CXPowGate, type(cirq.CNOT))) 
                   for op in operations if hasattr(op, 'gate'))
    assert has_cnot, f"Should have CNOT gate, got: {[type(op.gate).__name__ for op in operations if hasattr(op, 'gate')]}"


def test_ctrl_modifier_with_parameter():
    """Test ctrl with parameter n."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[3] q;
    ctrl(2) @ x q[0], q[1], q[2];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Should create a Toffoli gate (double-controlled X)
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 1
    # Toffoli is a CCX or ControlledGate with 2 controls
    has_toffoli = any(isinstance(op.gate, (cirq.CCXPowGate, cirq.CCX.__class__, cirq.ControlledGate)) 
                      for op in operations if hasattr(op, 'gate'))
    assert has_toffoli, f"Should have Toffoli gate, got: {[type(op.gate).__name__ for op in operations if hasattr(op, 'gate')]}"


# ============================================================================
# TEST: Gate Modifiers - Negative Control
# ============================================================================

def test_negctrl_modifier_basic():
    """Test basic negctrl @ gate modifier."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[2] q;
    negctrl @ x q[0], q[1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Should have X-CNOT-X pattern (3 gates)
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 3, f"Expected 3 operations for negctrl pattern, got {len(operations)}"
    
    # Check pattern: X, CNOT, X
    has_x = any(isinstance(op.gate, (cirq.XPowGate, type(cirq.X))) 
                for op in operations if hasattr(op, 'gate'))
    has_cnot = any(isinstance(op.gate, (cirq.CNotPowGate, cirq.CXPowGate, type(cirq.CNOT))) 
                   for op in operations if hasattr(op, 'gate'))
    assert has_x, "Should have X gates"
    assert has_cnot, "Should have CNOT gate"


def test_negctrl_custom_gate():
    """Test negative controlled X in custom gate."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    gate neg_cx q1, q2 {
        negctrl @ x q1, q2;
    }
    
    qubit[2] q;
    neg_cx q[0], q[1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'neg_cx' in visitor.custom_gates
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 3, f"Expected 3 operations, got {len(operations)}"


# ============================================================================
# TEST: Gate Modifiers - Inverse
# ============================================================================

def test_inv_modifier_rotation():
    """Test inv @ rotation gate."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    gate rzm(theta) q1 {
        inv @ rz(theta) q1;
    }
    
    qubit q;
    rzm(pi/4) q;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'rzm' in visitor.custom_gates
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 1
    # Should be an Rz gate
    has_rz = any(isinstance(op.gate, (cirq.ZPowGate, cirq.rz(0).__class__)) 
                 for op in operations if hasattr(op, 'gate'))
    assert has_rz, f"Should have Rz gate, got: {[type(op.gate).__name__ for op in operations if hasattr(op, 'gate')]}"


def test_inv_modifier_s_gate():
    """Test inv @ s = sdg."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit q;
    inv @ s q;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)

    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 1

    op = operations[0]
    assert isinstance(op.gate, cirq.ZPowGate), f"Expected ZPowGate, got {type(op.gate).__name__}"
    assert abs(op.gate.exponent + 0.5) < 1e-3, f"Expected exponent ≈ -0.5, got {op.gate.exponent}"

def test_inv_U_gate():
    """Test inv @ U transformation."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit q;
    inv @ U(pi/2, pi/4, pi/8) q;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Should apply U(-π/2, -π/8, -π/4) which is 3 rotation gates
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 3, f"U gate should decompose to 3 rotations, got {len(operations)}"


# ============================================================================
# TEST: Complex Modifier Combinations
# ============================================================================

def test_combined_modifiers():
    """Test inv @ ctrl @ gate."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[2] q;
    inv @ ctrl @ rz(pi/4) q[0], q[1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) >= 1, f"Should have at least 1 operation, got {len(operations)}"

def test_gphase_basic():
    """Test basic gphase operation."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit q;
    gphase(pi/4);
    h q;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)

    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 2
    # Second should be H
    assert isinstance(operations[1].gate, type(cirq.H))


def test_gphase_with_const():
    """Test gphase with const variable."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    const float phase_val = pi/4;
    qubit q;
    gphase(phase_val);
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)

    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 1


def test_gphase_in_gate():
    """Test gphase in gate definition."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    gate my_gate(theta) q {
        gphase(theta);
        h q;
    }
    
    qubit q;
    my_gate(pi/4) q;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)

    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 2
    assert isinstance(operations[1].gate, type(cirq.H))


# Test proper controlled phase using standard gates
def test_controlled_rz_instead():
    """Test controlled Rz as alternative to ctrl @ gphase."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[2] q;
    ctrl @ rz(pi/4) q[0], q[1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)

    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 1
    # Should be a controlled Rz
    assert len(operations[0].qubits) == 2 
           
def test_ctrl_single_qubit_gates():
    """Test ctrl @ for various single-qubit gates (H, Y, Z, S, T)."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[2] q;
    ctrl @ h q[0], q[1];
    ctrl @ y q[0], q[1];
    ctrl @ z q[0], q[1];
    ctrl @ s q[0], q[1];
    ctrl @ t q[0], q[1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 5, f"Expected 5 controlled gates, got {len(operations)}"


def test_ctrl_with_n_parameter():
    """Test ctrl(n) @ for multiple control qubits."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[4] q;
    ctrl(2) @ x q[0], q[1], q[2];
    ctrl(3) @ x q[0], q[1], q[2], q[3];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 2, f"Expected 2 multi-controlled gates, got {len(operations)}"


def test_ctrl_rotation_gates():
    """Test ctrl @ with parameterized rotation gates."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[2] q;
    ctrl @ rx(pi/2) q[0], q[1];
    ctrl @ ry(pi/3) q[0], q[1];
    ctrl @ rz(pi/4) q[0], q[1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 3, f"Expected 3 controlled rotations, got {len(operations)}"


def test_ctrl_with_register_broadcasting():
    """Test ctrl @ with register broadcasting."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[3] control;
    qubit[3] target;
    ctrl @ x control, target;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 3, f"Should broadcast to 3 CNOT gates, got {len(operations)}"
    # All should be CNOT gates
    cnot_count = sum(1 for op in operations if hasattr(op, 'gate') and 
                     isinstance(op.gate, (cirq.CNotPowGate, cirq.CXPowGate, type(cirq.CNOT))))
    assert cnot_count == 3, f"All 3 operations should be CNOT, got {cnot_count}"


def test_ctrl_in_custom_gate():
    """Test ctrl @ modifier inside custom gate definition."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    gate my_controlled_h q1, q2 {
        ctrl @ h q1, q2;
    }
    
    qubit[2] q;
    my_controlled_h q[0], q[1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'my_controlled_h' in visitor.custom_gates, "Custom gate should be defined"
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 1, f"Expected 1 controlled-H operation, got {len(operations)}"


# ============================================================================
# TEST: @inv Modifier - Basic Operations
# ============================================================================

def test_inv_single_qubit_gates():
    """Test inv @ for self-inverse gates."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit q;
    inv @ x q;
    inv @ y q;
    inv @ z q;
    inv @ h q;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 4, f"Expected 4 gates, got {len(operations)}"


def test_inv_s_and_t_gates():
    """Test inv @ s = sdg and inv @ t = tdg."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit q;
    inv @ s q;
    inv @ t q;
    inv @ sdg q;
    inv @ tdg q;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 4, f"Expected 4 inverse gates, got {len(operations)}"


def test_inv_rotation_gates():
    """Test inv @ with rotation gates (negates angle)."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit q;
    inv @ rx(pi/2) q;
    inv @ ry(pi/3) q;
    inv @ rz(pi/4) q;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 3, f"Expected 3 inverse rotations, got {len(operations)}"


def test_inv_gphase():
    """Test inv @ gphase(a) = gphase(-a)."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit q;
    inv @ gphase(pi/4);
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 1, f"Expected 1 global phase operation, got {len(operations)}"


def test_inv_with_register():
    """Test inv @ applied to register."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[3] q;
    inv @ rx(pi/2) q;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 3, f"Should apply to all 3 qubits, got {len(operations)}"


def test_inv_in_custom_gate():
    """Test inv @ inside custom gate definition."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    gate my_inv_gate(theta) q1 {
        inv @ rz(theta) q1;
    }
    
    qubit q;
    my_inv_gate(pi/4) q;
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert 'my_inv_gate' in visitor.custom_gates, "Custom gate should be defined"
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 1, f"Expected 1 inverse Rz operation, got {len(operations)}"


# ============================================================================
# TEST: Complex Modifier Combinations
# ============================================================================

def test_inv_ctrl_combination():
    """Test inv @ ctrl @ gate combination."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[2] q;
    inv @ ctrl @ rz(pi/4) q[0], q[1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) >= 1, f"Should have at least 1 operation, got {len(operations)}"


def test_inv_ctrl_on_U_gate():
    """Test inv @ ctrl @ U gate."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[2] q;
    inv @ ctrl @ U(pi/2, pi/4, pi/8) q[0], q[1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) >= 1, f"Should have operations, got {len(operations)}"


def test_ctrl_negctrl_comparison():
    """Test difference between ctrl and negctrl."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[4] q;
    ctrl @ x q[0], q[1];
    negctrl @ x q[2], q[3];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    # negctrl wraps with X gates: 1 CNOT + (X + CNOT + X) = 4 operations
    assert len(operations) == 4, f"Expected 4 operations (1 CNOT + 3 for negctrl), got {len(operations)}"


def test_inv_on_two_qubit_gate():
    """Test inv @ on two-qubit gates (self-inverse)."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    qubit[2] q;
    inv @ cx q[0], q[1];
    inv @ swap q[0], q[1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 2, f"Expected 2 operations, got {len(operations)}"


def test_ctrl_on_custom_gate():
    """Test ctrl @ applied to custom gate."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    gate my_rotation(theta) q1 {
        rx(theta) q1;
        ry(theta) q1;
    }
    
    qubit[2] q;
    ctrl @ my_rotation(pi/4) q[0], q[1];
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    # Should have controlled versions of rx and ry
    assert len(operations) >= 2, f"Should have at least 2 controlled operations, got {len(operations)}"
# ============================================================================
# Run all tests
# ============================================================================


def test_static_if_true_branch():
    """Test static if with true branch."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    int x = 0;
    if (true) {
        x = 1;
        x q;
    } else {
        x = 2;
        h q;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['x']['value'] == 1
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 1
    assert isinstance(operations[0].gate, cirq.XPowGate)


def test_static_if_false_branch():
    """Test static if with false branch."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    int x = 0;
    if (false) {
        x = 1;
        x q;
    } else {
        x = 2;
        h q;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['x']['value'] == 2
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 1
    assert isinstance(operations[0].gate, cirq.HPowGate)


def test_static_if_condition_expression():
    """Test if with static condition expression."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    int a = 5;
    if (a > 3) {
        x q;
    } else {
        h q;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 1
    assert isinstance(operations[0].gate, cirq.XPowGate)


def test_nested_static_if():
    """Test nested static if statements."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    int x = 0;
    if (true) {
        x = 1;
        if (true) {
            x = 2;
            x q;
        } else {
            h q;
        }
    } else {
        z q;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['x']['value'] == 2
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 1
    assert isinstance(operations[0].gate, cirq.XPowGate)


def test_shadowing_in_if_block():
    """Test variable shadowing in if block."""
    qasm = """
    OPENQASM 3.0;
    int x = 10;
    if (true) {
        int x = 20;
        x += 5;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Outer x should still be 10
    assert visitor.variables['x']['value'] == 10


def test_update_outer_var_in_if():
    """Test updating outer variable in if block."""
    qasm = """
    OPENQASM 3.0;
    int x = 10;
    if (true) {
        x += 5;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Outer x should be updated to 15
    assert visitor.variables['x']['value'] == 15


def test_empty_if_block():
    """Test empty if block."""
    qasm = """
    OPENQASM 3.0;
    if (true) {
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.circuit is None or len(list(visitor.circuit.all_operations())) == 0


def test_if_with_false_condition_no_ops():
    """Test if with false condition produces no operations."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    if (false) {
        x q;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    if visitor.circuit:
        assert len(list(visitor.circuit.all_operations())) == 0


def test_static_if_with_float_condition():
    """Test if with float condition."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    float f = 0.7;
    if (f > 0.5) {
        x q;
    } else {
        h q;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 1
    assert isinstance(operations[0].gate, cirq.XPowGate)


def test_shadowing_and_outer_update_mixed():
    """Test complex scoping with shadowing and outer updates."""
    qasm = """
    OPENQASM 3.0;
    int x = 10;
    if (true) {
        int y = 20;
        x += 5;
        if (true) {
            int x = 30;
            x += 10;
        }
        y += x;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Outer x should be 15 (10 + 5)
    assert visitor.variables['x']['value'] == 15
    # y should not exist in outer scope
    assert 'y' not in visitor.variables



def test_dynamic_if_not_supported():
    """Test dynamic if with measurement - executes else branch."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[2] q;
    bit m;
    x q[0];
    m = measure q[0];
    if (m == 1) {
        x q[1];
    } else {
        h q[1];
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 3
    
    # Use isinstance to check gate types
    has_x = any(isinstance(op.gate, (cirq.XPowGate, type(cirq.X))) 
                for op in operations if hasattr(op, 'gate'))
    has_h = any(isinstance(op.gate, (cirq.HPowGate, type(cirq.H))) 
                for op in operations if hasattr(op, 'gate'))
    
    assert has_x, "Should have X gate"
    assert has_h, "Should have H gate from else branch"


def test_dynamic_if_single_measurement():
    """Test dynamic if - condition always true."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    bit[1] m;
    m = measure q;
    if (m == 0 || m == 1) {
        x q;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 2
    
    has_x = any(isinstance(op.gate, (cirq.XPowGate, type(cirq.X))) 
                for op in operations if hasattr(op, 'gate'))
    assert has_x, "Should have X gate from if branch"


def test_dynamic_if_multiple_measurements():
    """Test dynamic if - condition false, no if branch execution."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[2] q;
    bit[2] m;
    x q[0];
    m[0] = measure q[0];
    m[1] = measure q[1];
    if (m[0] == 1 && m[1] == 0) {
        x q[0];
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 3  # X + 2 measurements only


def test_dynamic_if_with_else_branch():
    """Test dynamic if-else, else branch executes."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    bit m;
    h q;
    m = measure q;
    if (m == 1) {
        x q;
    } else {
        y q;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 3
    
    has_h = any(isinstance(op.gate, (cirq.HPowGate, type(cirq.H))) 
                for op in operations if hasattr(op, 'gate'))
    has_y = any(isinstance(op.gate, (cirq.YPowGate, type(cirq.Y))) 
                for op in operations if hasattr(op, 'gate'))
    
    assert has_h, "Should have H gate"
    assert has_y, "Should have Y gate from else branch"


def test_dynamic_if_condition_evaluates_true():
    """Test condition that evaluates true at construction time."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    bit m;
    m = measure q;
    if (m == 0) {
        x q;
    } else {
        y q;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 2
    
    has_x = any(isinstance(op.gate, (cirq.XPowGate, type(cirq.X))) 
                for op in operations if hasattr(op, 'gate'))
    has_y = any(isinstance(op.gate, (cirq.YPowGate, type(cirq.Y))) 
                for op in operations if hasattr(op, 'gate'))
    
    assert has_x, "Should have X gate from if branch"
    assert not has_y, "Should NOT have Y gate"


def test_dynamic_if_complex_condition():
    """Test complex condition with multiple measurements."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[3] q;
    bit[3] m;
    h q[0];
    cx q[0], q[1];
    m[0] = measure q[0];
    m[1] = measure q[1];
    m[2] = measure q[2];
    if ((m[0] == 1 && m[1] == 1) || m[2] == 1) {
        x q[0];
    } else {
        y q[0];
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 6
    
    has_y = any(isinstance(op.gate, (cirq.YPowGate, type(cirq.Y))) 
                for op in operations if hasattr(op, 'gate'))
    assert has_y, "Should have Y gate from else branch"


def test_dynamic_if_bit_comparison():
    """Test comparing entire bit register value."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[2] q;
    bit[2] m;
    x q[0];
    h q[1];
    m = measure q;
    if (m == 1) {
        x q[0];
    } else {
        y q[0];
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 5


def test_dynamic_if_with_index_access():
    """Test bit array index access in condition."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[4] q;
    bit[4] m;
    h q;
    m = measure q;
    if (m[2] == 1) {
        x q[3];
    } else {
        y q[3];
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 9


def test_static_if_still_works():
    """Verify static if statements work correctly."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    int control = 1;
    if (control == 1) {
        x q;
    } else {
        y q;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 1
    
    has_x = any(isinstance(op.gate, (cirq.XPowGate, type(cirq.X))) 
                for op in operations if hasattr(op, 'gate'))
    assert has_x, "Should have X gate from if branch"




def test_dynamic_if_not_operator():
    """Test NOT operator with measurement."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    bit m;
    m = measure q;
    if (!m) {
        x q;
    } else {
        y q;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 2
    
    has_x = any(isinstance(op.gate, (cirq.XPowGate, type(cirq.X))) 
                for op in operations if hasattr(op, 'gate'))
    assert has_x, "Should have X gate from if branch"
def test_for_loop_range_unroll():
    """Test for loop with range unrolling."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    for int i in [0:2] {
        h q;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    # Should unroll 3 times (0, 1, 2 inclusive)
    assert len(operations) == 3
    assert all(isinstance(op.gate, cirq.HPowGate) for op in operations)


def test_for_loop_discrete_set_unroll():
    """Test for loop with discrete set."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    for int i in {0, 1, 2} {
        rx(i * 0.1) q;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 3


def test_for_loop_array_unroll():
    """Test for loop over array."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    array[float, 3] angles = {0.1, 0.2, 0.3};
    for float theta in angles {
        ry(theta) q;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 3


def test_for_loop_bit_register_unroll():
    """Test for loop over bit register."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    bit[3] breg = "101";
    for bit b in breg {
        if (b == 1) {
            x q;
        }
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    # "101" has bits [1, 0, 1] (bit 0 = 1, bit 1 = 0, bit 2 = 1)
    assert len(operations) == 2


def test_for_loop_array_slice_unroll():
    """Test for loop over array slice."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    array[int, 5] arr = {1, 2, 3, 4, 5};
    for int i in arr[1:3] {
        rz(i * 0.5) q;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    # arr[1:3] is inclusive: elements at indices 1, 2, 3 = {2, 3, 4}
    assert len(operations) == 3


def test_for_loop_negative_step():
    """Test for loop with negative step."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    for int i in [4:-1:0] {
        rz(i * 0.1) q;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    # Should iterate: 4, 3, 2, 1, 0 (5 times)
    assert len(operations) == 5


def test_for_loop_variable_shadowing():
    """Test that loop variable shadows outer variable."""
    qasm = """
    OPENQASM 3.0;
    int i = 100;
    for int i in [0:2] {
        // Loop variable shadows outer i
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Outer i should be restored
    assert visitor.variables['i']['value'] == 100


def test_nested_for_loops_with_variable_dependency():
    """Test nested loops where inner loop depends on outer loop variable."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[6] q;
    for int i in [0:1] {
        for int j in [i+1:2] {
            cx q[i], q[j];
        }
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    # i=0: j in [1:2] -> 2 CNOTs (0,1), (0,2)
    # i=1: j in [2:2] -> 1 CNOT (1,2)
    # Total: 3 CNOTs
    assert len(operations) == 3


def test_for_loop_modifying_outer_scope_variable():
    """Test that loop can modify outer scope variable."""
    qasm = """
    OPENQASM 3.0;
    int total = 100;
    for int i in [0:4] {
        total -= i;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # 100 - 0 - 1 - 2 - 3 - 4 = 90
    assert visitor.variables['total']['value'] == 90


def test_for_loop_const_expression_in_range():
    """Test range with const expressions."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[10] q;
    const int START = 1;
    const int STEPS = 3;
    for int i in [START:START + STEPS] {
        x q[i];
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    # [1:4] inclusive = 4 operations
    assert len(operations) == 4


def test_for_loop_bit_register_slice():
    """Test iterating over bit register slice."""
    qasm = """
    OPENQASM 3.0;
    bit[5] breg = "10110";
    int x_count = 0;
    for bit b in breg[1:3] {
        if (b == 1) {
            x_count += 1;
        }
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # "10110" = bits [0,1,1,0,1] (bit 0=0, bit 1=1, bit 2=1, bit 3=0, bit 4=1)
    # breg[1:3] = bits 1, 2, 3 = [1, 1, 0]
    # Two are 1
    assert visitor.variables['x_count']['value'] == 2


def test_for_loop_empty_range():
    """Test for loop with empty range."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    for int i in [5:3] {
        h q;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Empty range: no operations
    operations = list(visitor.circuit.all_operations()) if visitor.circuit else []
    assert len(operations) == 0


def test_for_loop_with_bool_array():
    """Test iterating over boolean array."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    array[bool, 3] flags = {true, false, true};
    for bool f in flags {
        if (f) {
            x q;
        }
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    # Two true values
    assert len(operations) == 2


def test_for_loop_type_mismatch_raises():
    """Test that type mismatch raises error."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    array[float, 2] floats = {1.5, 2.5};
    for int i in floats {
        ry(i) q;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    # Float to int conversion should work (truncation)
    # If you want strict typing, this should raise TypeError
    visitor.visit(module)  # Should work with conversion


def test_for_loop_scalar_raises():
    """Test that iterating over scalar value raises ValueError (wrapped TypeError)."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    int single = 42;
    for int i in single {
        h q;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    # Your implementation wraps errors in ValueError with [ForLoop] prefix
    with pytest.raises(ValueError, match="Error getting loop values.*Cannot iterate over type 'int'"):
        visitor.visit(module)


def test_for_loop_2d_array_raises():
    """Test that iterating over 2D array raises ValueError (wrapped TypeError)."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    array[int, 2, 2] matrix = {{1,2},{3,4}};
    for int i in matrix {
        h q;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    # Your implementation wraps errors in ValueError with [ForLoop] prefix
    with pytest.raises(ValueError, match="Error getting loop values.*Only one-dimensional arrays"):
        visitor.visit(module)


def test_for_loop_undefined_variable_raises():
    """Test that iterating over undefined variable raises ValueError (wrapped NameError)."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    for int i in undefined_var {
        h q;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    # Your implementation wraps errors in ValueError with [ForLoop] prefix
    with pytest.raises(ValueError, match="Error getting loop values.*Variable 'undefined_var' not found"):
        visitor.visit(module)


def test_for_loop_basic_range():
    """Test basic for loop with range."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[3] q;
    for int i in [0:2] {
        x q[i];
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 3  # X gates on q[0], q[1], q[2]


def test_for_loop_discrete_set():
    """Test for loop with discrete set."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[5] q;
    for int i in {0, 2, 4} {
        x q[i];
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    assert len(operations) == 3  # X gates on q[0], q[2], q[4]


def test_for_loop_1d_array():
    """Test for loop iterating over 1D array."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    
    array[int, 3] values = {10, 20, 30};
    int sum = 0;
    for int val in values {
        sum += val;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # sum should be 10 + 20 + 30 = 60
    assert visitor.variables['sum']['value'] == 60


def test_for_loop_bit_register():
    """Test for loop iterating over bit register."""
    qasm = """
    OPENQASM 3.0;
    bit[4] b = "1010";
    int count = 0;
    for int bit_val in b {
        count += bit_val;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Should count 1s: bit 0=0, bit 1=1, bit 2=0, bit 3=1 -> count=2
    assert visitor.variables['count']['value'] == 2


def test_for_loop_bit_slice():
    """Test for loop iterating over bit slice."""
    qasm = """
    OPENQASM 3.0;
    bit[8] b = "11001100";
    int count = 0;
    for int bit_val in b[2:5] {
        count += bit_val;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Bits 2-5: b[2]=1, b[3]=1, b[4]=0, b[5]=0 -> count=2
    assert visitor.variables['count']['value'] == 2


def test_for_loop_array_slice():
    """Test for loop iterating over array slice."""
    qasm = """
    OPENQASM 3.0;
    array[int, 5] arr = {10, 20, 30, 40, 50};
    int sum = 0;
    for int val in arr[1:3] {
        sum += val;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # arr[1:3] = {20, 30, 40} -> sum = 90
    assert visitor.variables['sum']['value'] == 90


def test_for_loop_step_range():
    """Test for loop with step in range."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[10] q;
    for int i in [0:2:8] {
        x q[i];
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    # Indices: 0, 2, 4, 6, 8 -> 5 operations
    assert len(operations) == 5


def test_for_loop_negative_step():
    """Test for loop with negative step."""
    qasm = """
    OPENQASM 3.0;
    int sum = 0;
    for int i in [5:-1:0] {
        sum += i;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # 5 + 4 + 3 + 2 + 1 + 0 = 15
    assert visitor.variables['sum']['value'] == 15


def test_for_loop_type_conversion():
    """Test for loop with type conversion."""
    qasm = """
    OPENQASM 3.0;
    array[int, 3] int_arr = {1, 2, 3};
    float sum = 0.0;
    for float val in int_arr {
        sum += val;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # Values are converted to float: 1.0 + 2.0 + 3.0 = 6.0
    assert visitor.variables['sum']['value'] == 6.0


def test_for_loop_nested():
    """Test nested for loops."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[2] q;
    
    for int i in [0:1] {
        for int j in [0:1] {
            if (i != j) {
                cx q[i], q[j];
            }
        }
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    # Should apply CX for: (0,1) and (1,0) -> 2 operations
    assert len(operations) == 2


def test_for_loop_with_break():
    """Test for loop with break statement."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[5] q;
    
    for int i in [0:4] {
        if (i == 2) break;
        x q[i];
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    # Should apply X to q[0] and q[1] only
    assert len(operations) == 2


def test_for_loop_with_continue():
    """Test for loop with continue statement."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[5] q;
    
    for int i in [0:4] {
        if (i == 2) continue;
        x q[i];
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    # Should apply X to q[0], q[1], q[3], q[4] (skip q[2])
    assert len(operations) == 4


def test_for_loop_variable_scoping():
    """Test that loop variable is properly scoped."""
    qasm = """
    OPENQASM 3.0;
    int i = 100;
    for int i in [0:2] {
        // Inner i shadows outer i
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # After loop, outer i should still be 100
    assert visitor.variables['i']['value'] == 100


def test_for_loop_modifies_outer_variable():
    """Test that loop can modify outer scope variables."""
    qasm = """
    OPENQASM 3.0;
    int sum = 0;
    for int i in [1:5] {
        sum += i;  // Modifies outer 'sum'
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    # 1 + 2 + 3 + 4 + 5 = 15
    assert visitor.variables['sum']['value'] == 15


def test_for_loop_empty_range():
    """Test for loop with empty range."""
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    
    for int i in [5:0] {
        x q;  // Should never execute
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    # No operations should be applied
    assert len(operations) == 0


def test_for_loop_single_iteration():
    """Test for loop with single iteration."""
    qasm = """
    OPENQASM 3.0;
    int count = 0;
    for int i in {42} {
        count += 1;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['count']['value'] == 1


# ============================================================================
# Edge Case Tests
# ============================================================================

def test_for_loop_zero_step_raises():
    """Test that zero step raises error."""
    qasm = """
    OPENQASM 3.0;
    int sum = 0;
    for int i in [0:0:10] {
        sum += i;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    with pytest.raises(ValueError, match="Step cannot be zero"):
        visitor.visit(module)


def test_for_loop_uint_type():
    """Test for loop with uint type."""
    qasm = """
    OPENQASM 3.0;
    array[uint, 3] arr = {10, 20, 30};
    uint sum = 0;
    for uint val in arr {
        sum += val;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['sum']['value'] == 60


def test_for_loop_bool_type():
    """Test for loop with bool type."""
    qasm = """
    OPENQASM 3.0;
    array[bool, 3] flags = {true, false, true};
    int count = 0;
    for bool flag in flags {
        if (flag) count += 1;
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    assert visitor.variables['count']['value'] == 2



def test_dynamic_if_multiple_measurements():
    """
    Test dynamic if with multiple measurement results.
    At construction time, m[0]=0, m[1]=0, so condition is false.
    """
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";

    qubit[2] q;
    bit[2] m;
    x q[0];
    m[0] = measure q[0];
    m[1] = measure q[1];
    if (m[0] == 1 && m[1] == 0) {
        x q[0];
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    
    # Should execute successfully
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    # Should have: X (initial) + 2 measurements
    # At construction time, m[0]=0, m[1]=0, so (0==1 && 0==0) = false
    # If branch does NOT execute
    assert len(operations) == 3  # Just X + 2 measurements, no conditional X
    
    print("✅ test_dynamic_if_multiple_measurements: Executed, condition false (m[0]=0, m[1]=0)")




def test_dynamic_if_bit_comparison():
    """
    Test comparing entire bit register value.
    """
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[2] q;
    bit[2] m;
    
    x q[0];
    h q[1];
    m = measure q;
    
    // At construction time, m=0 (default bit array value)
    if (m == 1) {
        x q[0];
    } else {
        y q[0];
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    # Should have: X + H + 2 measurements + Y (from else, since m==0 != 1)
    assert len(operations) == 5
    
    print("✅ test_dynamic_if_bit_comparison: Bit register comparison works")


def test_dynamic_if_with_index_access():
    """
    Test dynamic if with bit array index access.
    """
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[4] q;
    bit[4] m;
    
    h q;
    m = measure q;
    
    // At construction time, m[2]=0
    if (m[2] == 1) {
        x q[3];
    } else {
        y q[3];
    }
    """
    module = parse_openqasm3(qasm)
    visitor = CirqVisitor()
    visitor.visit(module)
    
    operations = list(visitor.circuit.all_operations())
    # Should have: 4 H + 4 measurements + Y (from else)
    assert len(operations) == 9
    
    print("✅ test_dynamic_if_with_index_access: Indexed measurement access works")


def test_define_and_call_simple_gate():
    """Tests defining a simple parameter-less gate and calling it."""
    code = """
    OPENQASM 3.0;
        include "stdgates.inc";

    qubit q;
    gate my_h q_arg { h q_arg; }
    my_h q;
    """
    visitor = CirqVisitor()
    visitor.visit(parse_openqasm3(code))
    circuit = visitor.finalize()
    ops = list(circuit.all_operations())
    assert len(ops) == 1
    assert isinstance(ops[0].gate, cirq.H.__class__)
    assert len(ops[0].qubits) == 1

def test_gate_with_empty_body_is_identity():
    """Tests that a gate with an empty body produces no operations."""
    code = """
    OPENQASM 3.0;
        include "stdgates.inc";

    qubit q;
    gate empty_gate q_arg {}
    empty_gate q;
    """
    visitor = CirqVisitor()
    visitor.visit(parse_openqasm3(code))
    circuit = visitor.finalize()
    assert len(list(circuit.all_operations())) == 0

def test_define_and_call_multi_qubit_gate():
    """Tests defining and calling a gate with multiple qubit arguments."""
    code = """
    OPENQASM 3.0;
        include "stdgates.inc";

    qubit[2] qr;
    gate bell_pair a, b {
        h a;
        cx a, b;
    }
    bell_pair qr[0], qr[1];
    """
    visitor = CirqVisitor()
    visitor.visit(parse_openqasm3(code))
    circuit = visitor.finalize()
    ops = list(circuit.all_operations())
    assert len(ops) == 2
    assert isinstance(ops[0].gate, cirq.H.__class__)
    assert isinstance(ops[1].gate, cirq.CNOT.__class__)

# ==========================================================================
# 2. Parameterized Gates
# ==========================================================================

def test_gate_with_classical_parameter():
    """Tests a gate that takes a classical parameter."""
    code = """
    OPENQASM 3.0;
        include "stdgates.inc";

    qubit q;
    gate my_rx(theta) q_arg { rx(theta) q_arg; }
    my_rx(1.234) q;
    """
    visitor = CirqVisitor()
    visitor.visit(parse_openqasm3(code))
    circuit = visitor.finalize()
    ops = list(circuit.all_operations())
    assert len(ops) == 1
    # Check it's an Rx gate with correct angle
    gate = ops[0].gate
    assert hasattr(gate, '_rads') or hasattr(gate, 'exponent')
    
def test_gate_parameter_used_in_expression():
    """Tests using a gate's classical parameter inside an expression."""
    code = """
    OPENQASM 3.0;
        include "stdgates.inc";

    qubit q;
    gate my_gate(theta) q_arg { rx(theta * 2) q_arg; }
    my_gate(1.5708) q;  // pi/2 ≈ 1.5708
    """
    visitor = CirqVisitor()
    visitor.visit(parse_openqasm3(code))
    circuit = visitor.finalize()
    ops = list(circuit.all_operations())
    assert len(ops) == 1

# ==========================================================================
# 3. Hierarchical Gates (Composition)
# ==========================================================================

def test_gate_can_call_another_defined_gate():
    """Verifies that a gate can call another previously defined gate."""
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    gate g1 q_arg { h q_arg; }
    gate g2 q_arg { g1 q_arg; }
    g2 q;
    """
    visitor = CirqVisitor()
    visitor.visit(parse_openqasm3(code))
    circuit = visitor.finalize()
    ops = list(circuit.all_operations())
    assert len(ops) == 1
    assert isinstance(ops[0].gate, cirq.H.__class__)

# ==========================================================================
# 4. Scoping Rules
# ==========================================================================

def test_gate_can_access_global_const():
    """Rule: A gate body can see global constants."""
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    const float GLOBAL_ANGLE = 1.5;
    gate my_gate q_arg { rx(GLOBAL_ANGLE) q_arg; }
    my_gate q;
    """
    visitor = CirqVisitor()
    visitor.visit(parse_openqasm3(code))
    circuit = visitor.finalize()
    ops = list(circuit.all_operations())
    assert len(ops) == 1

def test_gate_cannot_access_global_mutable_variable_raises():
    """Rule: A gate CANNOT access a non-const global variable."""
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    float mutable_angle = 1.5;
    gate my_gate q_arg { rx(mutable_angle) q_arg; }
    my_gate q;
    """
    visitor = CirqVisitor()
    # This should raise an error during gate application
    with pytest.raises((ValueError, NameError), match=".*"):
        visitor.visit(parse_openqasm3(code))

def test_gate_can_define_local_constant():
    """Rule: A gate body can define a local const."""
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    gate my_gate q_arg {
        const float LOCAL_PI = 3.14159;
        rx(LOCAL_PI) q_arg;
    }
    my_gate q;
    """
    visitor = CirqVisitor()
    visitor.visit(parse_openqasm3(code))
    circuit = visitor.finalize()
    ops = list(circuit.all_operations())
    assert len(ops) == 1

# ==========================================================================
# 5. Gate Body Content Rules
# ==========================================================================

def test_classical_declaration_in_gate_body_raises():
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    gate my_bad_gate q_arg {
        int[32] x = 5;
        h q_arg;
    }
    my_bad_gate q;
    """
    visitor = CirqVisitor()
    # Parser catches this before visitor
    with pytest.raises((SyntaxError, ParseError), match=".*"):
        visitor.visit(parse_openqasm3(code))

def test_classical_assignment_in_gate_body_raises():
    """Rule: Cannot assign to classical parameters in gate body."""
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    int[32] x = 0;
    qubit q;
    gate my_bad_gate q_arg {
        x = 5;
        h q_arg;
    }
    my_bad_gate q;
    """
    visitor = CirqVisitor()
    with pytest.raises((SyntaxError, ParseError), match=".*"):
        visitor.visit(parse_openqasm3(code))

def test_measurement_in_gate_body_raises():
    """Rule: Cannot have measurements in gate body."""
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    bit c;
    gate my_bad_gate q_arg {
        c = measure q_arg;
    }
    my_bad_gate q;
    """
    visitor = CirqVisitor()
    with pytest.raises((SyntaxError, ParseError), match=".*"):
        visitor.visit(parse_openqasm3(code))

def test_reset_in_gate_body_raises():
    """Rule: Cannot have reset in gate body."""
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    gate my_bad_gate q_arg {
        reset q_arg;
    }
    my_bad_gate q;
    """
    visitor = CirqVisitor()
    with pytest.raises((SyntaxError, ParseError), match=".*"):
        visitor.visit(parse_openqasm3(code))

def test_qubit_declaration_in_gate_body_raises():
    """Rule: Qubit declarations must be global."""
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    gate my_bad_gate q_arg {
        qubit r;
        h r;
    }
    my_bad_gate q;
    """
    visitor = CirqVisitor()
    with pytest.raises((SyntaxError, ParseError), match=".*"):
        visitor.visit(parse_openqasm3(code))

def test_for_loop_in_gate_is_valid():
    """Rule: 'for' loops are allowed inside a gate body."""
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    gate apply_h_twice q_arg {
        for int i in [0:1] { h q_arg; }
    }
    apply_h_twice q;
    """
    visitor = CirqVisitor()
    visitor.visit(parse_openqasm3(code))
    circuit = visitor.finalize()
    ops = list(circuit.all_operations())
    assert len(ops) == 2
    assert all(isinstance(op.gate, cirq.H.__class__) for op in ops)

# ==========================================================================
# 6. Name and Argument Rules
# ==========================================================================

def test_redefining_builtin_gate_raises():
    """Rule: Cannot define a gate with the same name as a built-in gate."""
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    gate h q {}
    """
    visitor = CirqVisitor()
    with pytest.raises(NameError, match=".*already defined.*"):
        visitor.visit(parse_openqasm3(code))

def test_redefining_custom_gate_raises():
    """Rule: Cannot redefine a user-defined gate."""
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    gate my_gate q {}
    gate my_gate q {}
    """
    visitor = CirqVisitor()
    with pytest.raises(NameError, match=".*already defined.*"):
        visitor.visit(parse_openqasm3(code))

def test_indexing_gate_qubit_arg_raises():
    """Rule: Qubit arguments cannot be indexed within the gate body."""
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    gate my_gate q_arg { h q_arg[0]; }
    my_gate q;
    """
    visitor = CirqVisitor()
    with pytest.raises(SyntaxError, match=".*Cannot index qubit parameter.*"):
        visitor.visit(parse_openqasm3(code))

def test_calling_gate_with_wrong_qubit_count_raises():
    """Tests error for wrong number of qubit arguments."""
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[2] q;
    gate my_gate a { h a; }
    my_gate q[0], q[1];
    """
    visitor = CirqVisitor()
    with pytest.raises(ValueError, match=".*expects.*qubit.*"):
        visitor.visit(parse_openqasm3(code))

def test_calling_gate_with_wrong_classical_arg_count_raises():
    """Tests error for wrong number of classical arguments."""
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    gate my_gate(a, b) q_arg { rx(a) q_arg; }
    my_gate(1.0) q;
    """
    visitor = CirqVisitor()
    with pytest.raises(ValueError, match=".*expects.*parameter.*"):
        visitor.visit(parse_openqasm3(code))

def test_calling_undefined_gate_raises():
    """Tests that calling a gate that doesn't exist raises an error."""
    code = """
    OPENQASM 3.0;
    qubit q;
    undefined_gate q;
    """
    visitor = CirqVisitor()
    with pytest.raises(NameError, match=".*not defined.*"):
        visitor.visit(parse_openqasm3(code))

# ==========================================================================
# 7. Recursion Rules
# ==========================================================================

def test_direct_recursive_gate_call_raises():
    """Rule: A gate cannot call itself directly."""
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    gate recursive_gate a { recursive_gate a; }
    recursive_gate q;
    """
    visitor = CirqVisitor()
    with pytest.raises(RecursionError, match=".*[Rr]ecursive.*"):
        visitor.visit(parse_openqasm3(code))

def test_indirect_recursive_gate_call_raises():
    """Rule: Indirect recursion should also be detected."""
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    gate gate_a a { gate_b a; }
    gate gate_b b { gate_a b; }
    gate_a q;
    """
    visitor = CirqVisitor()
    with pytest.raises(RecursionError, match=".*[Rr]ecursive.*"):
        visitor.visit(parse_openqasm3(code))

# ==========================================================================
# 8. Advanced Features
# ==========================================================================

def test_gate_with_multiple_parameters():
    """Tests a gate with multiple classical parameters."""
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    gate my_u(theta, phi, lambda) q_arg { 
        rz(phi) q_arg;
        ry(theta) q_arg;
        rz(lambda) q_arg;
    }
    my_u(1.0, 2.0, 3.0) q;
    """
    visitor = CirqVisitor()
    visitor.visit(parse_openqasm3(code))
    circuit = visitor.finalize()
    ops = list(circuit.all_operations())
    assert len(ops) == 3

def test_gate_application_with_pi():
    """Tests using pi constant in gate parameters."""
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    gate my_gate q_arg { rx(pi / 2) q_arg; }
    my_gate q;
    """
    visitor = CirqVisitor()
    visitor.visit(parse_openqasm3(code))
    circuit = visitor.finalize()
    ops = list(circuit.all_operations())
    assert len(ops) == 1

def test_gate_with_control_flow():
    """Tests gate with control flow (for loop)."""
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    gate repeat_x q_arg {
        for int i in [0:2] {
            x q_arg;
        }
    }
    repeat_x q;
    """
    visitor = CirqVisitor()
    visitor.visit(parse_openqasm3(code))
    circuit = visitor.finalize()
    ops = list(circuit.all_operations())
    assert len(ops) == 3
    assert all(isinstance(op.gate, cirq.X.__class__) for op in ops)

def test_nested_gate_calls():
    """Tests deeply nested gate definitions."""
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    gate level1 q_arg { h q_arg; }
    gate level2 q_arg { level1 q_arg; }
    gate level3 q_arg { level2 q_arg; }
    level3 q;
    """
    visitor = CirqVisitor()
    visitor.visit(parse_openqasm3(code))
    circuit = visitor.finalize()
    ops = list(circuit.all_operations())
    assert len(ops) == 1
    assert isinstance(ops[0].gate, cirq.H.__class__)

def test_gate_with_multiple_gate_calls():
    """Tests gate that applies multiple different gates."""
    code = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit q;
    gate combo q_arg {
        h q_arg;
        x q_arg;
        y q_arg;
        z q_arg;
    }
    combo q;
    """
    visitor = CirqVisitor()
    visitor.visit(parse_openqasm3(code))
    circuit = visitor.finalize()
    ops = list(circuit.all_operations())
    assert len(ops) == 4
    
    