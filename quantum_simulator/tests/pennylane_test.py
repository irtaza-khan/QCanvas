import pytest
from qsim.visitors.pennylane_visitor import PennylaneVisitor, Angle
from qsim.qasm_parser import parse_openqasm3
from qsim.core.exceptions import ParseError
import pennylane as qml
import math
import numpy as np
import re
import openqasm3


class TestQubitDeclarations:
    
    def test_pennylane_visitor_simple_circuit(self):
        code = """
            OPENQASM 3.0;
            qubit[2] q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        circuit = visitor.finalize()
        assert isinstance(circuit, qml.tape.QuantumTape)
        assert visitor.get_var('qubits', 'q') == [0, 1]

class TestClassicalDeclarations:
    
    def test_classical_declarations_initialized(self):
        code = "OPENQASM 3.0; int[8] a = -10; float[64] c = 3.14; bool d = true;"
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'a') == -10
        assert math.isclose(visitor.get_var('env', 'c'), 3.14)
        assert visitor.get_var('env', 'd') is True

    def test_uint_overflow(self):
        code = "OPENQASM 3.0; uint[4] x = 18;"
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'x') == 2

    def test_unsupported_float_size_raises_error(self):
        code = "OPENQASM 3.0; float[18] z;"
        visitor = PennylaneVisitor()
        with pytest.raises(TypeError, match="Unsupported float size: float\\[18\\]"):
            visitor.visit(parse_openqasm3(code))

    def test_gate_with_classical_variable_parameter(self):
        code = "OPENQASM 3.0; qubit q; float[64] my_angle = pi / 2; rx(my_angle) q;"
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        op = tape.operations[0]
        assert op.name == 'RX' and math.isclose(op.parameters[0], math.pi / 2)

class TestExpressions:
    
    @pytest.mark.parametrize("expression, expected", [
        ("10 + 5", 15),
        ("10 - 12", -2),
        ("5 * 3", 15),
        ("10 / 4", 2.5),
        ("10 % 3", 1),
        ("2 ** 4", 16),
        ("-5", -5)  # Unary minus
    ])
    def test_arithmetic_expressions(self, expression, expected):
        code = f"OPENQASM 3.0; float[64] result = {expression};"
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert math.isclose(visitor.get_var('env', 'result'), expected)

    @pytest.mark.parametrize("expression, expected", [
        ("10 > 5", True),
        ("10 < 5", False),
        ("5.0 <= 5.0", True),
        ("5 >= 6", False),
        ("10 == 10.0", True),
        ("10 != 5", True)
    ])
    def test_comparison_expressions(self, expression, expected):
        code = f"OPENQASM 3.0; bool result = {expression};"
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'result') is expected

    @pytest.mark.parametrize("expression, expected", [
        ("true && false", False),
        ("true || false", True),
        ("!true", False),
    ])
    def test_logical_expressions(self, expression, expected):
        code = f"OPENQASM 3.0; bool result = {expression};"
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'result') is expected

    def test_nested_and_combined_expressions(self):
        code = """
        OPENQASM 3.0;
        int[32] a = 10;
        int[32] b = 4;
        int[32] c = 5;
        float[64] d = 2.0;

        // Test precedence and parentheses
        float[64] result1 = (a + b) * c / d;

        // Test complex logical, comparison, and arithmetic
        bool result2 = (a > b) && (c / d == 2.5);

        // Test unary, power, and modulo
        int[32] result3 = -(a ** 2 % 9);

        // Test a deeply nested expression
        bool final_check = !(result1 == 35.0 && result2 || result3 > 0);
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))

        assert math.isclose(visitor.get_var('env', 'result1'), 35.0)
        assert visitor.get_var('env', 'result2') is True
        assert visitor.get_var('env', 'result3') == -1
        assert visitor.get_var('env', 'final_check') is False

    def test_literal_formats_and_bitstring_initialization(self):
        code = """
        OPENQASM 3.0;

        // Test different integer literal formats
        int[32] i_hex = 0xff;          // 255
        int[32] i_oct = 0o77;          // 63
        int[32] i_bin = 0b1100_0011;   // 195

        // Test different float literal formats
        float[64] f_sci = 1.2e2;       // 120.0
        float[64] f_dot = .5;          // 0.5

        // Test bitstring initialization
        bit[8] b = "1010_0101";

        // Test that these literals work in expressions
        int[32] result = i_hex + i_oct - i_bin;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'i_hex') == 255
        assert visitor.get_var('env', 'i_oct') == 63
        assert visitor.get_var('env', 'i_bin') == 195
        assert math.isclose(visitor.get_var('env', 'f_sci'), 120.0)
        assert math.isclose(visitor.get_var('env', 'f_dot'), 0.5)
        assert visitor.get_var('env', 'result') == 123
        assert visitor.get_var('clbits', 'b') == [1, 0, 1, 0, 0, 1, 0, 1]

class TestConstants:
    
    def test_const_for_qubit_declaration(self):
        code = """
        OPENQASM 3.0;
        const uint SIZE = 5;
        qubit[SIZE] q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert len(visitor.get_var("qubits", "q")) == 5

    def test_const_expression_for_qubit_declaration(self):
        code = """
        OPENQASM 3.0;
        const uint A = 2;
        qubit[A * 3 + 1] q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert len(visitor.get_var("qubits", "q")) == 7

    def test_invalid_runtime_var_for_qubit_size(self):
        code = """
        OPENQASM 3.0;
        uint runtime_size = 5;
        qubit[runtime_size] q;
        """
        visitor = PennylaneVisitor()
        with pytest.raises(TypeError, match="must be a compile-time constant"):
            visitor.visit(parse_openqasm3(code))

    def test_invalid_reassignment_to_const(self):
        code = """
        OPENQASM 3.0;
        const int a = 10;
        a = 5;
        """
        visitor = PennylaneVisitor()
        with pytest.raises(TypeError, match="Cannot assign to constant variable 'a'"):
            visitor.visit(parse_openqasm3(code))

    def test_invalid_const_initialized_by_runtime_var(self):
        code = """
        OPENQASM 3.0;
        int runtime_var = 10;
        const int B = runtime_var;
        """
        visitor = PennylaneVisitor()
        with pytest.raises(TypeError, match="must be a compile-time constant"):
            visitor.visit(parse_openqasm3(code))

    def test_valid_const_initialized_by_const_expression(self):
        code = """
        OPENQASM 3.0;
        const uint A = 10;
        const int B = -2;
        const int C = A * B + 5; // Should be -15
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var("env", "C") == -15
        assert visitor.is_const("C") is True

class TestMeasurements:
    
    def test_openqasm3_measurement(self):
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        bit[2] c;
        c[0] = measure q[0];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        measure_ops = [op for op in tape.operations if isinstance(op, qml.measurements.MidMeasureMP)]
        assert len(measure_ops) == 1

    def test_openqasm3_measurement_with_broadcast(self):
        code = """
        OPENQASM 3.0;
        qubit[10] q;
        bit[10] c;
        c = measure q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        measure_ops = [op for op in tape.operations if isinstance(op, qml.measurements.MidMeasureMP)]
        assert len(measure_ops) == 10

    def test_measurement_with_slicing(self):
        code = """
        OPENQASM 3.0;
        qubit[4] q;
        bit[4] c;
        // Measure 3 qubits (q[1], q[2], q[3]) and store in 3 bits (c[0], c[1], c[2])
        c[0:2] = measure q[1:3];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()

        measure_ops = [op for op in tape.operations if isinstance(op, qml.measurements.MidMeasureMP)]
        assert len(measure_ops) == 3
        measured_wires = sorted([op.wires[0] for op in measure_ops])
        assert measured_wires == [1, 2, 3]

        clbits = visitor.get_var('clbits', 'c')
        assert isinstance(clbits[0], qml.measurements.MeasurementValue)
        assert isinstance(clbits[1], qml.measurements.MeasurementValue)
        assert isinstance(clbits[2], qml.measurements.MeasurementValue)
        assert clbits[3] == 0

    def test_measurement_with_step_slice(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        bit[3] c;
        c = measure q[0:2:4];  // Measures q[0], q[2], q[4]
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()

        measure_ops = [op for op in tape.operations if isinstance(op, qml.measurements.MidMeasureMP)]
        assert len(measure_ops) == 3
        measured_wires = sorted([op.wires[0] for op in measure_ops])
        assert measured_wires == [0, 2, 4]

        clbits = visitor.get_var('clbits', 'c')
        assert all(isinstance(bit, qml.measurements.MeasurementValue) for bit in clbits)

class TestResets:
    
    def test_reset_operation_on_slice(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        reset q[1:3];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        
        reset_ops = [op for op in tape.operations if isinstance(op, qml.StatePrep)]
        assert len(reset_ops) == 3

    def test_reset_with_step_slice(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        reset q[0:2:4];  // Resets q[0], q[2], q[4]
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        
        reset_ops = [op for op in tape.operations if isinstance(op, qml.StatePrep)]
        assert len(reset_ops) == 3
        reset_wires = sorted([op.wires[0] for op in reset_ops])
        assert reset_wires == [0, 2, 4]

class TestAliasing:
    
    def test_simple_alias_of_slice(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        let my_alias = q[1:3];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        
        assert visitor.get_var('qubits', 'my_alias') == [1, 2, 3]

    def test_alias_of_single_qubit(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        let single_q = q[4];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('qubits', 'single_q') == [4]

    def test_gate_on_aliased_register(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        let middle_three = q[1:3];
        cx middle_three[0], middle_three[1];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        cnot_op = tape.operations[0]
        assert cnot_op.name == 'CNOT'
        assert cnot_op.wires.tolist() == [1, 2]

    def test_invalid_duplicate_alias_name(self):
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        let q = q[0];
        """
        visitor = PennylaneVisitor()
        with pytest.raises(NameError, match="already declared"):
            visitor.visit(parse_openqasm3(code))

    def test_negative_indexing_on_alias(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        let reg = q[1:4]; // Wires [1, 2, 3, 4]
        x reg[-1];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        x_op = tape.operations[0]
        assert x_op.wires.tolist() == [4]

    def test_discrete_set_indexing_on_alias(self):
        code = """
        OPENQASM 3.0;
        qubit[10] q;
        let my_reg = q[2:8]; // Wires [2, 3, 4, 5, 6, 7, 8]
        let selection = my_reg[{0, 5, 2}];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('qubits', 'selection') == [2, 7, 4]

    def test_gate_on_discrete_set_selection(self):
        code = """
        OPENQASM 3.0;
        qubit[10] q;
        let my_reg = q[2:8];
        let selection = my_reg[{0, 5, 2}]; // Wires [2, 7, 4]
        h selection[1];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        h_op = tape.operations[0]
        assert h_op.name == 'Hadamard'
        assert h_op.wires.tolist() == [7]

    def test_invalid_alias_on_classical_bits(self):
        code = """
        OPENQASM 3.0;
        bit[4] c;
        let my_classical_alias = c[0:1];
        """
        visitor = PennylaneVisitor()
        with pytest.raises(TypeError, match="Aliases can only be created for quantum registers."):
            visitor.visit(parse_openqasm3(code))

    def test_alias_with_step_slice(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        let my_alias = q[0:2:4];  // Wires [0, 2, 4]
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('qubits', 'my_alias') == [0, 2, 4]

    def test_gate_on_alias_with_step(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        let my_alias = q[0:2:4];
        x my_alias[1];  // Wire 2
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        x_op = tape.operations[0]
        assert x_op.name == 'PauliX'
        assert x_op.wires.tolist() == [2]

class TestConcatenation:
    
    def test_concatenation_of_two_registers(self):
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        qubit[3] r;
        let combined = q ++ r;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('qubits', 'combined') == [0, 1, 2, 3, 4]

    def test_concatenation_of_slices_and_aliases(self):
        code = """
        OPENQASM 3.0;
        qubit[10] q;
        let first_two = q[0:1];
        let last_q = q[9];
        let middle_slice = q[4:5];
        let final_reg = first_two ++ middle_slice ++ last_q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('qubits', 'final_reg') == [0, 1, 4, 5, 9]

    def test_gate_on_concatenated_alias(self):
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        qubit[3] r;
        let combined = r ++ q; // wires [2, 3, 4, 0, 1]
        x combined[3];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        x_op = tape.operations[0]
        assert x_op.name == 'PauliX'
        assert x_op.wires.tolist() == [0]

    def test_invalid_self_concatenation(self):
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        let test = q ++ q;
        """
        visitor = PennylaneVisitor()
        with pytest.raises(ValueError, match="Cannot concatenate a register with itself"):
            visitor.visit(parse_openqasm3(code))

    def test_invalid_mixed_type_concatenation(self):
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        bit[2] c;
        let test = q ++ c;
        """
        visitor = PennylaneVisitor()
        with pytest.raises(TypeError, match="Can only concatenate quantum registers"):
            visitor.visit(parse_openqasm3(code))

    def test_invalid_concatenation_of_classical_bits(self):
        code = """
        OPENQASM 3.0;
        bit[2] c1;
        bit[2] c2;
        let combined_c = c1 ++ c2;
        """
        visitor = PennylaneVisitor()
        with pytest.raises(TypeError, match="Can only concatenate quantum registers"):
            visitor.visit(parse_openqasm3(code))

class TestGates:
    
    @pytest.mark.parametrize("gate", ["id", "x", "y", "z", "h", "s", "sdg", "t", "tdg"])
    def test_single_qubit_gates(self, gate):
        code = f"""
        OPENQASM 3.0;
        qubit[3] q;
        qubit kj;
        {gate} kj;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        assert isinstance(tape, qml.tape.QuantumTape)
        assert len(tape.operations) == 1

    @pytest.mark.parametrize("gate", ["cx", "cy", "cz"])
    def test_controlled_gates(self, gate):
        code = f"""
        OPENQASM 3.0;
        qubit[2] q;
        qubit kj;
        {gate} q[0], kj;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        assert len(tape.operations[0].wires) == 2

    @pytest.mark.parametrize("gate, angle", [("rx", "pi/2"), ("ry", "pi/2"), ("rz", "pi/2")])
    def test_rotation_gates(self, gate, angle):
        code = f"""
        OPENQASM 3.0;
        qubit q;
        {gate}({angle}) q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        op = tape.operations[0]
        assert math.isclose(op.parameters[0], math.pi/2, rel_tol=1e-9)

    @pytest.mark.parametrize("gate", ["swap", "cswap", "iswap", "sqrtiswap"])
    def test_swap_gates(self, gate):
        if gate == "cswap":
            code = f"""
            OPENQASM 3.0;
            qubit[3] q;
            qubit kj;
            {gate} q[0], q[2], kj;
            """
        else:
            code = f"""
            OPENQASM 3.0;
            qubit[2] q;
            qubit kj;
            {gate} kj, q[1];
            """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        assert isinstance(tape, qml.tape.QuantumTape)

    @pytest.mark.parametrize("params", [("pi/2", "pi/4", "pi"),])
    def test_u_gate(self, params):
        code = f"""
        OPENQASM 3.0;
        qubit q;
        u({params[0]}, {params[1]}, {params[2]}) q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        op = tape.operations[0]

        assert isinstance(op, qml.U3)
        assert math.isclose(op.parameters[0], math.pi/2, rel_tol=1e-9)
        assert math.isclose(op.parameters[1], math.pi/4, rel_tol=1e-9)
        assert math.isclose(op.parameters[2], math.pi, rel_tol=1e-9)

    def test_gate_with_array_parameter(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        array[float[64], 1] params = {pi / 2};
        rx(params[0]) q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        op = tape.operations[0]
        assert op.name == 'RX'
        assert math.isclose(op.parameters[0], math.pi / 2, rel_tol=1e-9)

    def test_gate_with_complex_expression_parameter(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        const float[64] const_angle = pi / 4;
        float[64] var_angle = pi / 2;
        rx(const_angle + var_angle * 2 - pi) q;  // pi/4 + pi - pi = pi/4
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        op = tape.operations[0]
        assert op.name == 'RX'
        assert math.isclose(op.parameters[0], math.pi / 4, rel_tol=1e-9)

    @pytest.mark.parametrize("gate", ["sx", "p"])
    def test_single_qubit_gates_extended(self, gate):
        if gate == "p":
            code = """
            OPENQASM 3.0;
            qubit q;
            p(pi/3) q;
            """
            expected_params = 1
            expected_name = "PhaseShift"
            expected_angle = math.pi / 3
        else:  # sx
            code = """
            OPENQASM 3.0;
            qubit q;
            sx q;
            """
            expected_params = 0
            expected_name = "SX"
            expected_angle = None

        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        op = tape.operations[0]

        assert isinstance(tape, qml.tape.QuantumTape)
        assert len(tape.operations) == 1
        assert len(op.wires) == 1
        assert op.name == expected_name
        assert len(op.parameters) == expected_params

        if expected_params > 0:
            assert math.isclose(op.parameters[0], expected_angle, rel_tol=1e-9)
            
            
    @pytest.mark.parametrize(
        "gate, pl_op",
        [
            ("ch", qml.CH),
            ("ccx", qml.Toffoli),
        ]
    )
    def test_multiqubit_gates_extended(self, gate, pl_op):
        if gate == "ccx":
            code = f"""
            OPENQASM 3.0;
            qubit[3] q;
            {gate} q[0], q[1], q[2];
            """
            expected_wires = 3
        else: # ch
            code = f"""
            OPENQASM 3.0;
            qubit[2] q;
            {gate} q[0], q[1];
            """
            expected_wires = 2
        
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        op = tape.operations[0]

        assert isinstance(op, pl_op)
        assert len(op.wires) == expected_wires
        assert len(op.parameters) == 0

    @pytest.mark.parametrize("gate, angle", [("cp", "pi/3"), ("crx", "pi/4"), ("cry", "pi/8"), ("crz", "pi/6")])
    def test_parametrized_controlled_gates(self, gate, angle):
        code = f"""
        OPENQASM 3.0;
        qubit[2] q;
        {gate}({angle}) q[0], q[1];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        op = tape.operations[0]
        
        assert len(op.wires) == 2
        assert len(op.parameters) == 1
        assert math.isclose(op.parameters[0], eval(f"math.{angle}"), rel_tol=1e-9)


class TestGlobalPhase:
    
    def test_global_phase(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        gphase(pi/3);
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert math.isclose(visitor.global_phase, math.pi/3, rel_tol=1e-9)

    def test_multiple_global_phase_accumulation(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        gphase(pi/2);
        gphase(pi/2);
        gphase(-pi);  // Should accumulate to 0
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        phase_ops = [op for op in tape.operations if isinstance(op, qml.GlobalPhase)]
        assert len(phase_ops) == 3
        assert math.isclose(visitor.global_phase, 0, rel_tol=1e-9)

class TestArrays:
    
    def test_unsupported_complex_array_raises_error(self):
        code = """
        OPENQASM 3.0;
        array[complex[float[64]], 2] my_complex_arr;
        """
        visitor = PennylaneVisitor()
        with pytest.raises(NotImplementedError, match="Array of 'complex'"):
            visitor.visit(parse_openqasm3(code))

    def test_bit_array_declaration(self):
        code = """
        OPENQASM 3.0;
        array[bit, 4] my_bit_arr = {"0", "1", "0", "1"};
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'my_bit_arr') is not None
        assert np.array_equal(visitor.get_var('env', 'my_bit_arr'), np.array([0, 1, 0, 1], dtype=np.uint8))

    def test_partial_initializer_mismatch_raises_error(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 3] my_arr = {1, 2};  // Missing one element
        """
        visitor = PennylaneVisitor()
        with pytest.raises(ValueError, match="Initializer .* has 2 elements, but expected .* 3"):
            visitor.visit(parse_openqasm3(code))

    def test_excess_initializer_mismatch_raises_error(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 2] my_arr = {1, 2, 3};  // One extra
        """
        visitor = PennylaneVisitor()
        with pytest.raises(ValueError, match="Initializer .* has 3 elements, but expected .* 2"):
            visitor.visit(parse_openqasm3(code))

    def test_compound_assignment_on_array_element(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 2] my_arr = {1, 2};
        my_arr[0] += 3;  // Should become 4
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert np.array_equal(visitor.get_var('env', 'my_arr'), np.array([4, 2], dtype=np.int32))

    def test_compound_assignment_on_array_slice_raises_error(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 3] my_arr = {1, 2, 3};
        my_arr[0:2] += my_arr[1:2];  // Invalid
        """
        visitor = PennylaneVisitor()
        with pytest.raises(TypeError, match="Compound assignment is only supported for single array elements, not slices."):
            visitor.visit(parse_openqasm3(code))

    def test_overflow_on_bounded_type_assignment(self):
        code = """
        OPENQASM 3.0;
        array[uint[8], 1] my_uint_arr;
        my_uint_arr[0] = 257;  // Should wrap to 1 (257 % 256)
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'my_uint_arr')[0] == 1

    def test_underflow_on_bounded_type_assignment(self):
        code = """
        OPENQASM 3.0;
        array[int[8], 1] my_int_arr;
        my_int_arr[0] = -129;  // Should wrap to 127 or handle per two's complement
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'my_int_arr')[0] == 127

    def test_overflow_wrap_int16_array(self):
        code = """
        OPENQASM 3.0;
        array[int[16], 1] my_int16_arr;
        my_int16_arr[0] = 32768;  // Should wrap to -32768
        my_int16_arr[0] += 40000;  // Further wrap (from -32768 + 40000 = 7232, but post-compound wrap if needed)
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        arr = visitor.get_var('env', 'my_int16_arr')
        assert arr[0] == 7232
        assert arr.dtype == np.int16

    def test_evaluate_indexed_array_in_expression(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 3] my_arr = {10, 20, 30};
        int[32] result = my_arr[1] + 5;  // Should be 25
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'result') == 25

    def test_evaluate_sliced_array_in_expression(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 4] my_arr = {1, 2, 3, 4};
        bool is_equal = my_arr[0:2] == my_arr[1:3]; 
        """
        visitor = PennylaneVisitor()
        with pytest.raises(NotImplementedError, match="Use of array slices in expressions"):
            visitor.visit(parse_openqasm3(code))

    def test_out_of_bounds_array_index_raises_error(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 2] my_arr = {1, 2};
        int[32] result = my_arr[3];
        """
        visitor = PennylaneVisitor()
        with pytest.raises(IndexError, match="index .* is out of bounds"):
            visitor.visit(parse_openqasm3(code))

    def test_negative_indexing_on_array(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 4] my_arr = {10, 20, 30, 40};
        int[32] last = my_arr[-1];  // 40
        int[32] second_last = my_arr[-2];  // 30
        int[32] first = my_arr[-4];  // 10
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'last') == 40
        assert visitor.get_var('env', 'second_last') == 30
        assert visitor.get_var('env', 'first') == 10

    def test_negative_indexing_in_array_slice(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 5] my_arr = {1, 2, 3, 4, 5};
        array[int[32], 2] slice_last_two = my_arr[-2:];  // {4, 5} (inclusive, adjust for Python slice)
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert np.array_equal(visitor.get_var('env', 'slice_last_two'), np.array([4, 5], dtype=np.int32))

    def test_multidimensional_array_initialization_and_assignment(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 2, 3] matrix = {{1, 2, 3}, {4, 5, 6}};
        matrix[1][2] = 10;  // Change to {{1,2,3}, {4,5,10}}
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        expected = np.array([[1, 2, 3], [4, 5, 10]], dtype=np.int32)
        assert np.array_equal(visitor.get_var("env", "matrix"), expected)

    def test_zero_sized_and_max_dimension_array(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 0] empty_arr;  // Zero size
        array[int[32], 1,1,1,1,1,1,1] max_dim = {{{{{{{1}}}}}}};  // 7 dims
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var("env", "empty_arr").shape == (0,)
        assert visitor.get_var("env", "max_dim").shape == (1,1,1,1,1,1,1)
        assert visitor.get_var("env", "max_dim")[0,0,0,0,0,0,0] == 1

    def test_array_initialization_from_other_array(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 2, 3] source = {{1, 2, 3}, {4, 5, 6}};
        array[int[32], 2, 3] copy = source;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        expected = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.int32)
        assert np.array_equal(visitor.get_var("env", "copy"), expected)

    def test_array_initialization_from_slice(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 4] my_arr = {1, 2, 3, 4};
        array[int[32], 2] slice_init = my_arr[1:2];  // {2, 3}
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert np.array_equal(visitor.get_var("env", "slice_init"), np.array([2, 3], dtype=np.int32))

    def test_array_slice_with_step(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 5] my_arr = {0, 1, 2, 3, 4};
        array[int[32], 3] sliced = my_arr[0:2:4];  // {0, 2, 4}
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert np.array_equal(visitor.get_var("env", "sliced"), np.array([0, 2, 4], dtype=np.int32))

    def test_assignment_to_slice_with_step(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 5] my_arr = {0, 1, 2, 3, 4};
        array[int[32], 3] new_values = {10, 20, 30};
        my_arr[0:2:4] = new_values; // Becomes {10, 1, 20, 3, 30}
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert np.array_equal(visitor.get_var("env", "my_arr"), np.array([10, 1, 20, 3, 30], dtype=np.int32))

    def test_multidimensional_slice_initialization(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 3, 4] matrix = {{1,2,3,4},{5,6,7,8},{9,10,11,12}};
        array[int[32], 2, 2] submatrix = matrix[0:1, 1:2];  // {{2,3},{6,7}}
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        expected = np.array([[2, 3], [6, 7]], dtype=np.int32)
        assert np.array_equal(visitor.get_var("env", "submatrix"), expected)


    def test_compound_assignment_on_float_array_element(self):
        code = """
        OPENQASM 3.0;
        array[float[64], 2] my_arr = {1.0, 2.0};
        my_arr[0] *= 3.0;  // Becomes 3.0
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert np.array_equal(visitor.get_var("env", "my_arr"), np.array([3.0, 2.0], dtype=np.float64))

    def test_negative_indexing_in_multidimensional_array(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 2, 3] matrix = {{1,2,3},{4,5,6}};
        int[32] val = matrix[-1][-1];  // 6
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var("env", "val") == 6

    def test_access_to_max_dimension_array_element(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 1,1,1,1,1,1,1] max_dim = {{{{{{{1}}}}}}};
        int[32] val = max_dim[0][0][0][0][0][0][0];  // 1
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var("env", "val") == 1

class TestAngles:
    
    def test_angle_declaration_and_initialization(self):
        code = """
        OPENQASM 3.0;
        angle[32] theta = pi;
        angle[64] phi;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        
        assert visitor.get_var('env', 'theta') is not None
        assert isinstance(visitor.get_var('env', 'theta'), Angle)
        assert visitor.get_var('env', 'theta').size == 32
        expected_uint = round((math.pi / (2 * math.pi)) * (2**32))
        assert visitor.get_var('env', 'theta').uint_value == expected_uint
        
        assert visitor.get_var('env', 'theta') is not None
        assert isinstance(visitor.get_var('env', 'phi'), Angle)
        assert visitor.get_var('env', 'phi').size == 64
        assert visitor.get_var('env', 'phi').uint_value == 0

    def test_angle_invalid_size(self):
        code = """
        OPENQASM 3.0;
        angle[8] theta = pi;  // Unsupported size
        """
        visitor = PennylaneVisitor()
        with pytest.raises(TypeError, match="Unsupported angle size: angle\\[8\\]"):
            visitor.visit(parse_openqasm3(code))

    def test_angle_assignment(self):
        code = """
        OPENQASM 3.0;
        angle[32] theta = pi;
        theta = 3 * pi;  // Should normalize to pi
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        
        assert visitor.get_var('env', 'theta') is not None
        assert isinstance(visitor.get_var('env', 'theta'), Angle)
        assert visitor.get_var('env', 'theta').size == 32
        expected_uint = round((math.pi / (2 * math.pi)) * (2**32))
        assert visitor.get_var('env', 'theta').uint_value == expected_uint

    def test_angle_compound_assignment(self):
        code = """
        OPENQASM 3.0;
        angle[32] theta = pi / 2;
        theta += pi;  // Should normalize to 3pi/2
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        
        assert visitor.get_var('env', 'theta') is not None
        assert isinstance(visitor.get_var('env', 'theta'), Angle)
        assert visitor.get_var('env', 'theta').size == 32
        expected_float = (math.pi / 2 + math.pi) % (2 * math.pi)
        expected_uint = round((expected_float / (2 * math.pi)) * (2**32))
        assert visitor.get_var('env', 'theta').uint_value == expected_uint

    def test_angle_in_expression(self):
        code = """
        OPENQASM 3.0;
        angle[32] theta = pi;
        float[32] result = theta + pi / 2;  // Should evaluate to 3pi/2
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        
        assert visitor.get_var('env', 'result') is not None
        expected_float = (math.pi + math.pi / 2) % (2 * math.pi)
        assert np.isclose(visitor.get_var('env', 'result'), expected_float, rtol=1e-5)

    def test_angle_negative_value(self):
        code = """
        OPENQASM 3.0;
        angle[32] theta = -pi;  // Should normalize to pi
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        
        assert visitor.get_var('env', 'theta') is not None
        assert isinstance(visitor.get_var('env', 'theta'), Angle)
        assert visitor.get_var('env', 'theta').size == 32
        expected_float = (-math.pi) % (2 * math.pi)
        expected_uint = round((expected_float / (2 * math.pi)) * (2**32))
        assert visitor.get_var('env', 'theta').uint_value == expected_uint

    def test_angle_in_quantum_gate(self):
        code = """
        OPENQASM 3.0;
        qubit[1] q;
        angle[32] theta = pi / 2;
        rx(theta) q[0];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        
        rx_ops = [op for op in tape.operations if isinstance(op, qml.RX)]
        assert len(rx_ops) == 1
        assert rx_ops[0].wires.tolist() == [0]
        assert np.isclose(rx_ops[0].parameters[0], math.pi / 2, rtol=1e-5)

    def test_angle_array_declaration(self):
        code = """
        OPENQASM 3.0;
        array[angle[32], 2] angles = {pi / 2, pi};
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        
        assert visitor.get_var('env', 'angles') is not None
        assert isinstance(visitor.get_var('env', 'angles'), np.ndarray)
        assert visitor.get_var('env', 'angles').dtype == np.float32
        assert visitor.get_var('env', 'angles').shape == (2,)
        assert np.isclose(visitor.get_var('env', 'angles')[0], math.pi / 2, rtol=1e-5)
        assert np.isclose(visitor.get_var('env', 'angles')[1], math.pi, rtol=1e-5)

    def test_angle_array_initialization_from_array(self):
        code = """
        OPENQASM 3.0;
        array[float[32], 2] source = {pi / 2, pi};
        array[angle[32], 2] angles = source;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        
        assert visitor.get_var('env', 'angles') is not None
        assert isinstance(visitor.get_var('env', 'angles'), np.ndarray)
        assert visitor.get_var('env', 'angles').dtype == np.float32
        assert visitor.get_var('env', 'angles').shape == (2,)
        assert np.isclose(visitor.get_var('env', 'angles')[0], math.pi / 2, rtol=1e-5)
        assert np.isclose(visitor.get_var('env', 'angles')[1], math.pi, rtol=1e-5)

    def test_angle_array_invalid_size(self):
        code = """
        OPENQASM 3.0;
        array[angle[8], 2] angles = {pi / 2, pi};  // Unsupported size
        """
        visitor = PennylaneVisitor()
        with pytest.raises(TypeError, match="Unsupported angle size: angle\\[8\\]"):
            visitor.visit(parse_openqasm3(code))

    def test_angle_in_invalid_expression(self):
        code = """
        OPENQASM 3.0;
        angle[32] theta = pi;
        bit result = theta;  // Invalid: cannot assign angle to bit
        """
        visitor = PennylaneVisitor()
        with pytest.raises(ValueError, match="Cannot assign value"):
            visitor.visit(parse_openqasm3(code))


    def test_angle_comparison(self):
        code = """
        OPENQASM 3.0;
        angle[32] theta = pi;
        angle[32] phi = pi / 2;
        bool is_greater = theta > phi;  // True
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'is_greater') is True

    def test_angle_overflow_in_compound_assignment(self):
        code = """
        OPENQASM 3.0;
        angle[32] theta = pi;
        theta += 3 * pi;  // pi + 3pi = 4pi mod 2pi = 0
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        
        assert visitor.get_var('env', 'theta') is not None
        assert isinstance(visitor.get_var('env', 'theta'), Angle)
        expected_float = (math.pi + 3 * math.pi) % (2 * math.pi)
        expected_uint = round((expected_float / (2 * math.pi)) * (2**32))
        assert visitor.get_var('env', 'theta').uint_value == expected_uint
        assert math.isclose(expected_float, 0, rel_tol=1e-9)

class TestIndexing:
    
    def test_invalid_multi_dimensional_indexing_on_qubit_register(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        let a = q[1:3][0];
        """
        visitor = PennylaneVisitor()
        with pytest.raises(TypeError, match="Multi-dimensional indexing is only supported for classical arrays."):
            visitor.visit(parse_openqasm3(code))

    def test_bit_assignment_from_non_literal(self):
        code = """
        OPENQASM 3.0;
        bit[2] c;
        bit[1] d = "1";
        int[32] x = 10;
        c[0] = d[0];  // From another bit
        c[1] = x > 5;  // From expression (bool)
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('clbits', 'c') == [1, 1]

    def test_bit_assignment_from_array_element(self):
        code = """
        OPENQASM 3.0;
        array[bit, 2] bit_arr = {"0", "1"};
        bit[1] c;
        c[0] = bit_arr[1];  // "1"
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('clbits', 'c') == [1]

    def test_multidimensional_bit_array(self):
        code = """
        OPENQASM 3.0;
        array[bit, 2, 2] bit_matrix = {{"0", "1"}, {"1", "0"}};
        bit[1] result = bit_matrix[1][0];  // "1"
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('clbits', 'result') == [1]

    def test_negative_indexing_on_bit_register(self):
        code = """
        OPENQASM 3.0;
        bit[4] c = "1010";
        bit[1] last = c[-1];  // 0
        bit[1] first = c[-4];  // 1
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('clbits', 'last') == [0]
        assert visitor.get_var('clbits', 'first') == [1]

    def test_negative_indexing_on_qubit_register(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        x q[-1];  // Last qubit (wire 4)
        x q[-3];  // Third last (wire 2)
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        x_ops = [op for op in tape.operations if op.name == 'PauliX']
        assert len(x_ops) == 2
        assert x_ops[0].wires[0] == 4
        assert x_ops[1].wires[0] == 2

    def test_negative_indexing_in_qubit_slice_1(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        reset q[-3:-1];  // Wires 2,3,4 (inclusive)
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        reset_ops = [op for op in tape.operations if isinstance(op, qml.StatePrep)]
        assert len(reset_ops) == 3
        assert sorted([op.wires[0] for op in reset_ops]) == [2, 3, 4]

    def test_negative_indexing_in_qubit_slice_2(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        reset q[-5:-1];  // Wires 0,1,2,3,4 (inclusive)
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        reset_ops = [op for op in tape.operations if isinstance(op, qml.StatePrep)]
        assert len(reset_ops) == 5
        assert sorted([op.wires[0] for op in reset_ops]) == [0, 1, 2, 3, 4]

    def test_expression_in_array_index(self):
        code = """
        OPENQASM 3.0;
        int[32] idx = 1 + 1;  // 2
        array[int[32], 4] my_arr = {10, 20, 30, 40};
        int[32] result = my_arr[idx];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'result') == 30

    def test_non_const_index_in_array_access(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 3] my_arr = {1, 2, 3};
        int[32] dynamic_idx = 1;
        int[32] result = my_arr[dynamic_idx];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'result') == 2

    def test_non_integer_index_expression_raises_error(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 3] my_arr = {1,2,3};
        float[32] bad_idx = 1.5;
        int[32] result = my_arr[bad_idx];
        """
        visitor = PennylaneVisitor()
        with pytest.raises(IndexError):
            visitor.visit(parse_openqasm3(code))
            
class TestIfElse:
    
    def test_static_if_true_branch(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        int[32] x = 0;
        if (true) {
            x = 1;
            x q;
        } else {
            x = 2;
            h q;
        }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'x') == 1
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 1
        assert ops[0].name == 'PauliX'

    def test_static_if_false_branch(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        int[32] x = 0;
        if (false) {
            x = 1;
            x q;
        } else {
            x = 2;
            h q;
        }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'x') == 2
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 1
        assert ops[0].name == 'Hadamard'

    def test_static_if_no_else(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        int[32] x = 0;
        if (true) {
            x = 1;
            x q;
        }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'x') == 1
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 1
        assert ops[0].name == 'PauliX'

    def test_static_if_condition_expression(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        int[32] a = 5;
        if (a > 3) {
            x q;
        } else {
            h q;
        }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 1
        assert ops[0].name == 'PauliX'

    def test_dynamic_if_with_measure(self):
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        bit[1] m;
        x q[0];
        m = measure q[0];
        if (m == 1) {
            x q[1];
        } else {
            h q[1];
        }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 4  # X on q0, MidMeasure on q0, Conditional X and H on q1 (one applied but both present)
        assert ops[0].name == 'PauliX' and ops[0].wires[0] == 0
        assert ops[1].name == 'MidMeasureMP' and ops[1].wires[0] == 0        
        # The conditional is a callable, but we can check the tape structure
        # Note: Actual inspection might require executing or deeper check, but for test, check types

    def test_nested_static_if(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        int[32] x = 0;
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
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'x') == 2
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 1
        assert ops[0].name == 'PauliX'

    def test_nested_measurement(self):
        code = """
        OPENQASM 3.0;
        qubit[3] q;
        bit[2] m;
        x q[0];
        m[0] = measure q[0];
        if (m[0] == 1) {
            x q[1];
            m[1] = measure q[1];
        } else {
            h q[1];
        }
        """
        visitor = PennylaneVisitor()
        with pytest.raises(ValueError, match="Only quantum functions that contain no measurements can be applied conditionally."):
            visitor.visit(parse_openqasm3(code))
            
    def test_nested_dynamic_if(self):
        code = """
        OPENQASM 3.0;
        qubit[3] q;
        bit[2] m;
        x q[0];
        m[0] = measure q[0];
        if (m[0] == 1) {
            x q[1];
            if (m[1] == 0) {
                z q[2];
            }   
        } else {
            h q[1];
        }
        """
        visitor = PennylaneVisitor()
        with pytest.raises(ValueError, match="Nested dynamic control blocks are not allowed."):
            visitor.visit(parse_openqasm3(code))


    def test_shadowing_in_if_block(self):
        code = """
        OPENQASM 3.0;
        int[32] x = 10;
        if (true) {
            int[32] x = 20;  // Shadowed
            x += 5;  // Local x = 25
        }
        // Outer x still 10
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'x') == 10  # Outer not affected

    def test_update_outer_var_in_if(self):
        code = """
        OPENQASM 3.0;
        int[32] x = 10;
        if (true) {
            x += 5;  // Updates outer x to 15
        }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'x') == 15

    def test_invalid_classical_decl_in_dynamic_if(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        bit[1] m;
        m = measure q;
        if (m == 1) {
            int[32] x = 10;  // Invalid in dynamic
        }
        """
        visitor = PennylaneVisitor()
        with pytest.raises(ValueError, match="Classical declarations not allowed in dynamic control blocks."):
            visitor.visit(parse_openqasm3(code))

    def test_invalid_standalone_expression_in_dynamic_if(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        bit[1] m;
        m = measure q;
        if (m == 1) {
            5 * 3;
        }
        """
        visitor = PennylaneVisitor()
        with pytest.raises(ValueError, match="Standalone expression statements not allowed in dynamic control blocks."):
            visitor.visit(parse_openqasm3(code))

    def test_expression_in_gate_param_in_dynamic_if(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        bit[1] m;
        m = measure q;
        if (m == 1) {
            rx(pi / 2) q;
        }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 2  # measure, conditional RX

    def test_complex_condition_with_measurements(self):
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        bit[2] m;
        x q[0];
        m[0] = measure q[0];
        m[1] = measure q[1];
        if (m[0] == 1 && m[1] == 0) {
            x q[0];
        }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 4  # X q0, measure q0, measure q1, conditional X q0

    def test_if_with_false_condition_no_ops(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        if (false) {
            x q;
        }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        assert len(tape.operations) == 0

    def test_if_with_runtime_condition_but_static_eval(self):
        code = """
        OPENQASM 3.0;
        int[32] a = 5;
        qubit q;
        if (a == 5) {
            x q;
        } else {
            h q;
        }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 1
        assert ops[0].name == 'PauliX'

    def test_alias_in_static_if(self):
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        if (true) {
            let alias_q = q[0];
            x alias_q;
        }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 1
        assert ops[0].name == 'PauliX' and ops[0].wires[0] == 0

    def test_invalid_alias_in_dynamic_if(self):
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        bit[1] m;
        m = measure q[0];
        if (m == 1) {
            let alias_q = q[1];
            x alias_q;
        }
        """
        visitor = PennylaneVisitor()
        with pytest.raises(ValueError, match="Alias statements not allowed in dynamic control blocks."):
            visitor.visit(parse_openqasm3(code))

    def test_empty_if_block(self):
        code = """
        OPENQASM 3.0;
        if (true) {
        }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        assert len(tape.operations) == 0

    def test_if_with_measurement_in_condition(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        bit[1] m;
        m = measure q;
        if (m == 0 || m == 1) {  // Always true, but dynamic
            x q;
        }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 2  # measure, conditional X

    def test_shadowing_and_outer_update_mixed(self):
        code = """
        OPENQASM 3.0;
        int[32] x = 10;
        if (true) {
            int[32] y = 20;
            x += 5;  // Outer x to 15
            if (true) {
                int[32] x = 30;  // Shadowed inner x
                x += 10;  // Inner x to 40
            }
            y += x;  // y += 15 (outer x)
        }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'x') == 15


    def test_static_if_with_float_condition(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        float[64] f = 0.7;
        if (f > 0.5) {
            x q;
        } else {
            h q;
        }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 1
        assert ops[0].name == 'PauliX'


    def test_reset_in_dynamic_if(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        bit m;
        h q;
        m = measure q;
        if (m == 1) {
            reset q;
        }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 3 # H, MidMeasureMP, Conditional
        # Further inspection of the conditional's true_fn could check for StatePrep

    def test_invalid_classical_assignment_in_dynamic_if(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        bit m;
        int[32] x = 5;
        m = measure q;
        if (m == 1) {
            x = 10; // This should be disallowed
        }
        """
        visitor = PennylaneVisitor()
        # Your error message is "Constant declarations...", but the code blocks assignments too.
        # You might want to adjust the error message or the logic.
        # For now, we test the existing behavior.
        with pytest.raises(ValueError, match="Constant declarations not allowed in dynamic control blocks."):
            visitor.visit(parse_openqasm3(code))

    def test_mixed_static_dynamic_condition(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        bit m;
        const int[32] a = 1;
        m = measure q;
        if (a == 1 && m == 1) {
            x q;
        }
        """
        visitor = PennylaneVisitor()
        with pytest.raises(RuntimeError, match=re.escape("Error applying operator '&&' to measurement values: unsupported operand type(s) for &: 'bool' and 'MeasurementValue'")):
            visitor.visit(parse_openqasm3(code))

class TestForLoops:
    
    def test_for_loop_range_unroll(self):
        code = """
            OPENQASM 3.0;
            qubit[1] q;
            for int[32] i in [0:2] {
                h q[0];
            }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        circuit = visitor.finalize()
        # Unrolls 3 times (0,1,2 inclusive)
        assert len(circuit.operations) == 3
        for op in circuit.operations:
            assert isinstance(op, qml.Hadamard)
            assert op.wires[0] == 0


    def test_for_loop_discrete_set_unroll(self):
        code = """
            OPENQASM 3.0;
            qubit[1] q;
            for int[32] i in {0, 1, 2} {
                rx(i * 0.1) q[0];
            }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        circuit = visitor.finalize()
        # Unrolls 3 times
        assert len(circuit.operations) == 3
        params = [op.parameters[0] for op in circuit.operations]
        np.testing.assert_allclose(params, [0.0, 0.1, 0.2])


    def test_for_loop_array_unroll(self):
        code = """
            OPENQASM 3.0;
            qubit[1] q;
            array[float[32], 3] angles = {0.1, 0.2, 0.3};
            for float[32] theta in angles {
                ry(theta) q[0];
            }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        circuit = visitor.finalize()
        # Unrolls 3 times
        assert len(circuit.operations) == 3
        params = [op.parameters[0] for op in circuit.operations]
        np.testing.assert_allclose(params, [0.1, 0.2, 0.3])


    def test_for_loop_bit_register_unroll(self):
        code = """
            OPENQASM 3.0;
            qubit[1] q;
            bit[3] breg = "101";
            for bit b in breg {
                if (b == 1) {
                    x q[0];
                }
            }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        circuit = visitor.finalize()
        # Unrolls 3 times, but if-block executes twice (for 1s at pos 0,2)
        assert len(circuit.operations) == 2
        for op in circuit.operations:
            assert isinstance(op, qml.PauliX)
            assert op.wires[0] == 0


    def test_for_loop_array_slice_unroll(self):
        code = """
            OPENQASM 3.0;
            qubit[1] q;
            array[int[32], 5] arr = {1, 2, 3, 4, 5};
            for int[32] i in arr[1:3] {
                rz(i * 0.5) q[0];
            }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        circuit = visitor.finalize()
        # due to inclusive slicing, unrolls 3 times (2,3)
        assert len(circuit.operations) == 3
        params = [op.parameters[0] for op in circuit.operations]
        np.testing.assert_allclose(params, [1.0, 1.5, 2.0])


    def test_for_loop_negative_step_unroll(self):
        code = """
            OPENQASM 3.0;
            qubit[1] q;
            for int[32] i in [4:-1:0] {
                rz(i * 0.1) q[0];
            }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        circuit = visitor.finalize()
        # Unrolls 5 times (4,3,2,1,0 inclusive)
        assert len(circuit.operations) == 5
        params = [op.parameters[0] for op in circuit.operations]
        np.testing.assert_allclose(params, [0.4, 0.3, 0.2, 0.1, 0.0])
        
        
    def test_for_loop_variable_shadowing(self):
        """Tests that a loop variable shadows an outer variable without modifying it."""
        code = """
            OPENQASM 3.0;
            int[32] i = 100;
            for int[32] i in [0:2] {
                // Inside the loop, 'i' refers to the loop variable (0, 1, 2)
            }
            // After the loop, 'i' should revert to its original value.
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        # The outer 'i' should be unaffected by the loop.
        assert visitor.get_var('env', 'i') == 100
        
        
    def test_nested_for_loops_with_variable_dependency(self):
        """Tests that an inner loop can access the outer loop's variable."""
        code = """
            OPENQASM 3.0;
            qubit[6] q;
            // Should produce CNOTs on (0,1), (0,2), (1,2)
            for int[32] i in [0:1] {
                for int[32] j in [i+1:2] {
                    cx q[i], q[j];
                }
            }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        circuit = visitor.finalize()
        ops = circuit.operations
        assert len(ops) == 3
        assert ops[0].name == 'CNOT' and ops[0].wires.tolist() == [0, 1]
        assert ops[1].name == 'CNOT' and ops[1].wires.tolist() == [0, 2]
        assert ops[2].name == 'CNOT' and ops[2].wires.tolist() == [1, 2]
   
        
    def test_for_loop_modifying_outer_scope_variable(self):
        """Tests that a loop can modify a variable declared in an outer scope."""
        code = """
            OPENQASM 3.0;
            int[32] total = 100;
            for int[32] i in [0:4] {
                total -= i; // total should become 100-0-1-2-3-4 = 90
            }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'total') == 90


    def test_for_loop_iterable_from_const_expression(self):
        """
        Tests that the iterable can be a range defined by a compile-time
        constant expression.
        """
        code = """
            OPENQASM 3.0;
            qubit[10] q;
            const int[32] START = 1;
            const int[32] STEPS = 3;
            // Loop should run for i in [1 : 1 + STEPS] -> 1, 2, 3, 4
            for int[32] i in [START : START + STEPS] {
                x q[i];
            }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        circuit = visitor.finalize()
        ops = circuit.operations
        assert len(ops) == 4
        # Check that the gates were applied to the correct wires
        wires_hit = [op.wires[0] for op in ops]
        assert wires_hit == [1, 2, 3, 4]
        
        
    def test_for_loop_bit_register_slice_unroll(self):
        """Tests iterating over a slice of a classical bit register."""
        code = """
            OPENQASM 3.0;
            qubit q;
            bit[5] breg = "10110";
            int[32] x_count = 0;
            // Slice is inclusive, should iterate over bits at index 1, 2, 3 -> {0, 1, 1}
            for bit b in breg[1:3] {
                if (b == 1) {
                    x_count += 1;
                }
            }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        # Two of the bits in the slice {0, 1, 1} are 1.
        assert visitor.get_var('env', 'x_count') == 2


    def test_for_loop_empty_range(self):
        code = """
            OPENQASM 3.0;
            qubit[1] q;
            for int[32] i in [5:3] {
                h q[0];
            }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        circuit = visitor.finalize()
        # Empty range: no operations
        assert len(circuit.operations) == 0
        

    def test_for_loop_empty_array(self):
        code = """
            OPENQASM 3.0;
            qubit[1] q;
            array[int[32], 0] empty_arr = {};
            for int[32] i in empty_arr {
                x q[0];
            }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        circuit = visitor.finalize()
        # Empty array: no operations
        assert len(circuit.operations) == 0


    def test_for_loop_with_bool_array(self):
        """Tests iterating over an array of booleans."""
        code = """
            OPENQASM 3.0;
            qubit q;
            array[bool, 3] flags = {true, false, true};
            for bool f in flags {
                if (f) {
                    x q;
                }
            }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        circuit = visitor.finalize()
        # The 'if' block should execute twice
        assert len(circuit.operations) == 2
        assert all(op.name == 'PauliX' for op in circuit.operations)


    def test_for_loop_with_angle_variable(self):
        """Tests iterating with an angle type loop variable."""
        code = """
            OPENQASM 3.0;
            qubit q;
            array[float[64], 2] rads = {pi/2, pi};
            for angle[32] a in rads {
                rz(a) q;
            }
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        circuit = visitor.finalize()
        assert len(circuit.operations) == 2
        params = [op.parameters[0] for op in circuit.operations]
        np.testing.assert_allclose(params, [math.pi / 2, math.pi])


    def test_for_loop_type_mismatch_raises(self):
        code = """
            OPENQASM 3.0;
            qubit[1] q;
            array[float[32], 2] floats = {1.5, 2.5};
            for int[32] i in floats {
                ry(i) q[0];
            }
        """
        visitor = PennylaneVisitor()
        with pytest.raises(TypeError, match="Error converting loop variable 'i' value"):
            visitor.visit(parse_openqasm3(code))


    def test_for_loop_no_type_raises(self):
        code = """
            OPENQASM 3.0;
            include "stdgates.inc";
            qubit[1] q;
            for i in [0:1] {  // Missing type
                h q[0];
            }
        """
        visitor = PennylaneVisitor()
        with pytest.raises(ParseError, match="Failed to parse OpenQASM 3 code"):
            visitor.visit(parse_openqasm3(code))


    def test_for_loop_invalid_iterable_scalar_raises(self):
        code = """
            OPENQASM 3.0;
            qubit[1] q;
            int[32] single = 42;
            for int[32] i in single {
                h q[0];
            }
        """
        visitor = PennylaneVisitor()
        with pytest.raises(TypeError, match="Cannot iterate over type 'classical_value' or single scalar value."):
            visitor.visit(parse_openqasm3(code))


    def test_for_loop_2d_array_raises(self):
        code = """
            OPENQASM 3.0;
            qubit[1] q;
            array[int[32], 2, 2] matrix = {{1,2},{3,4}};
            for int[32] i in matrix {
                h q[0];
            }
        """
        visitor = PennylaneVisitor()
        with pytest.raises(TypeError, match="Only one-dimensional arrays can be iterated over."):
            visitor.visit(parse_openqasm3(code))


    def test_for_loop_in_dynamic_branch_raises(self):
        code = """
            OPENQASM 3.0;
            qubit[1] q;
            bit[1] c;
            c = measure q;
            if (c == 1) {
                for int[32] i in [0:1] {
                    h q[0];
                }
            }
        """
        visitor = PennylaneVisitor()
        with pytest.raises(ValueError, match="For loops not allowed in dynamic control blocks."):
            visitor.visit(parse_openqasm3(code))


class TestBarrier:
    def test_targeted_barrier(self):
        """Tests a barrier on a subset of qubits by inspecting the tape operations."""
        code = """
        OPENQASM 3.0;
        qubit[3] q;
        h q[0];
        cx q[1], q[2];
        barrier q[0], q[1];
        x q[0];
        z q[2];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        circuit = visitor.finalize()
        
        # FIX: Instead of checking the drawn string, inspect the tape's operations.
        # The tape includes the final Probs measurement, so we check the operations before it.
        ops = circuit.operations
        
        # There should be 5 operations: H, CNOT, Barrier, X, Z
        assert len(ops) == 5
        
        # Check the type and wires of each operation in sequence
        assert isinstance(ops[0], qml.Hadamard) and ops[0].wires.tolist() == [0]
        assert isinstance(ops[1], qml.CNOT) and ops[1].wires.tolist() == [1, 2]
        assert isinstance(ops[2], qml.Barrier) and ops[2].wires.tolist() == [0, 1]
        assert isinstance(ops[3], qml.PauliX) and ops[3].wires.tolist() == [0]
        assert isinstance(ops[4], qml.PauliZ) and ops[4].wires.tolist() == [2]

    def test_global_barrier(self):
        """Tests a global barrier with no specified qubits by inspecting the tape."""
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        h q[0];
        barrier;
        cx q[0], q[1];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        circuit = visitor.finalize()

        # FIX: Inspect the operations on the tape for robustness.
        ops = circuit.operations

        # There should be 3 operations: H, Barrier, CNOT
        assert len(ops) == 3

        assert isinstance(ops[0], qml.Hadamard) and ops[0].wires.tolist() == [0]
        # Global barrier should apply to all declared qubits
        assert isinstance(ops[1], qml.Barrier) and ops[1].wires.tolist() == [0, 1]
        assert isinstance(ops[2], qml.CNOT) and ops[2].wires.tolist() == [0, 1]


class TestInclude:
    
    def test_simple_include_with_scope_inheritance(self, tmp_path, monkeypatch):
        """
        Tests that an included file correctly inherits and uses variables
        from the parent scope at runtime.
        """
        # Create my_definitions.qasm (no gates)
        defs_file = tmp_path / "my_definitions.qasm"
        defs_file.write_text("""
            OPENQASM 3.0;
            int[32] j = i + 5; // Should see 'i' from main code
        """)

        # The main program code as a string
        main_qasm_string = """
            OPENQASM 3.0;
            int[32] i = 100;
            include "my_definitions.qasm";
        """

        # Temporarily change the current directory to where the file exists
        monkeypatch.chdir(tmp_path)

        # Use the visitor in the original way
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(main_qasm_string))

        # Check that variables from both the string and the file exist
        assert visitor.get_var('env', 'i') == 100
        assert visitor.get_var('env', 'j') == 105

    def test_stdgates_include_is_ignored(self, tmp_path, monkeypatch):
        """
        Tests that including 'stdgates.inc' is ignored and does not
        cause a FileNotFoundError.
        """
        main_qasm_string = """
            OPENQASM 3.0;
            include "stdgates.inc";
            qubit q;
        """
        monkeypatch.chdir(tmp_path)
        visitor = PennylaneVisitor()
        
        # This should execute without error, as stdgates.inc is skipped
        visitor.visit(parse_openqasm3(main_qasm_string))

    def test_nested_include(self, tmp_path, monkeypatch):
        """Tests that nested includes resolve paths and scopes correctly at runtime."""
        # Create b.qasm
        b_file = tmp_path / "b.qasm"
        b_file.write_text("""
            OPENQASM 3.0;
            int[32] b = a + 1;
        """)

        # Create a.qasm which includes b.qasm
        a_file = tmp_path / "a.qasm"
        a_file.write_text("""
            OPENQASM 3.0;
            int[32] a = 10;
            include "b.qasm";
        """)

        main_qasm_string = 'OPENQASM 3.0; include "a.qasm";'

        monkeypatch.chdir(tmp_path)
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(main_qasm_string))

        assert visitor.get_var('env', 'a') == 10
        assert visitor.get_var('env', 'b') == 11

    def test_include_file_not_found_raises(self, tmp_path, monkeypatch):
        """Tests that an appropriate error is raised for a missing file."""
        main_qasm_string = 'OPENQASM 3.0; include "nonexistent.qasm";'
        
        monkeypatch.chdir(tmp_path)
        visitor = PennylaneVisitor()
        with pytest.raises(FileNotFoundError):
            visitor.visit(parse_openqasm3(main_qasm_string))

    def test_circular_include_is_handled(self, tmp_path, monkeypatch):
        """
        Tests that a circular dependency does not cause infinite recursion.
        """
        (tmp_path / "a.qasm").write_text('OPENQASM 3.0; include "b.qasm"; int[32] a = 1;')
        (tmp_path / "b.qasm").write_text('OPENQASM 3.0; include "a.qasm"; int[32] b = 2;')
        main_qasm_string = 'OPENQASM 3.0; include "a.qasm";'

        monkeypatch.chdir(tmp_path)
        visitor = PennylaneVisitor()
        
        # The test is that this finishes without a RecursionError
        visitor.visit(parse_openqasm3(main_qasm_string))

        # Both variables should be defined exactly once.
        assert visitor.get_var('env', 'a') == 1
        assert visitor.get_var('env', 'b') == 2


class TestGateDefinition:
    # ==========================================================================
    # 1. Basic Definition and Call
    # ==========================================================================

    def test_define_and_call_simple_gate(self):
        """Tests defining a simple parameter-less gate and calling it."""
        code = """
        OPENQASM 3.0;
        qubit q;
        gate my_h q_arg { h q_arg; }
        my_h q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 1
        assert ops[0].name == 'Hadamard'
        assert ops[0].wires.tolist() == [0]

    def test_gate_with_empty_body_is_identity(self):
        """Tests that a gate with an empty body produces no operations."""
        code = """
        OPENQASM 3.0;
        qubit q;
        gate empty_gate q_arg {}
        empty_gate q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        assert len(tape.operations) == 0

    def test_define_and_call_multi_qubit_gate(self):
        """Tests defining and calling a gate with multiple qubit arguments."""
        code = """
        OPENQASM 3.0;
        qubit[2] qr;
        gate bell_pair a, b {
            h a;
            cx a, b;
        }
        bell_pair qr[0], qr[1];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 2
        assert ops[0].name == 'Hadamard' and ops[0].wires.tolist() == [0]
        assert ops[1].name == 'CNOT' and ops[1].wires.tolist() == [0, 1]

    # ==========================================================================
    # 2. Parameterized Gates
    # ==========================================================================

    def test_gate_with_classical_parameter(self):
        """Tests a gate that takes a classical parameter and promotes it."""
        code = """
        OPENQASM 3.0;
        qubit q;
        gate my_rx(theta) q_arg { rx(theta) q_arg; }
        my_rx(1.234) q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 1
        assert ops[0].name == 'RX'
        assert math.isclose(ops[0].parameters[0], 1.234)

    def test_gate_parameter_used_in_expression(self):
        """Tests using a gate's classical parameter inside an expression."""
        code = """
        OPENQASM 3.0;
        qubit q;
        gate my_gate(theta) q_arg { rx(theta * 2) q_arg; }
        my_gate(pi / 4) q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 1
        assert ops[0].name == 'RX'
        assert math.isclose(ops[0].parameters[0], math.pi / 2)

    # ==========================================================================
    # 3. Hierarchical Gates (Composition)
    # ==========================================================================

    def test_gate_can_call_another_defined_gate(self):
        """Verifies that a gate can call another previously defined gate."""
        code = """
        OPENQASM 3.0;
        qubit q;
        gate g1 q_arg { h q_arg; }
        gate g2 q_arg { g1 q_arg; } // g2 calls g1
        g2 q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 1
        assert ops[0].name == 'Hadamard'

    # ==========================================================================
    # 4. Scoping Rules
    # ==========================================================================

    def test_gate_defined_in_local_scope_raises(self):
        """Rule: Gate definitions are only allowed in the global scope."""
        code = """
        OPENQASM 3.0;
        for int i in [0:0] {
            gate my_local_gate q {} // ILLEGAL
        }
        """
        visitor = PennylaneVisitor()
        with pytest.raises(ParseError, match="Failed to parse OpenQASM 3 code: Failed to parse OpenQASM string: L4:C12: gate definitions must be global"):
            visitor.visit(parse_openqasm3(code))

    def test_gate_can_access_global_const(self):
        """Rule: A gate body can see global constants."""
        code = """
        OPENQASM 3.0;
        qubit q;
        const float[64] GLOBAL_ANGLE = 1.5;
        gate my_gate q_arg { rx(GLOBAL_ANGLE) q_arg; }
        my_gate q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        assert tape.operations[0].parameters[0] == 1.5

    def test_gate_cannot_access_global_mutable_variable_raises(self):
        """Rule: A gate CANNOT access a non-const global variable."""
        code = """
        OPENQASM 3.0;
        qubit q;
        float[64] mutable_angle = 1.5;
        gate my_gate q_arg { rx(mutable_angle) q_arg; } // ILLEGAL
        my_gate q;
        """
        visitor = PennylaneVisitor()
        with pytest.raises(NameError, match="Gate cannot access non-constant global variable 'mutable_angle'."):
            visitor.visit(parse_openqasm3(code))

    def test_gate_local_alias_is_scoped(self):
        """Rule: A 'let' alias inside a gate is locally scoped."""
        code = """
        OPENQASM 3.0;
        qubit qr;
        gate my_gate q_reg {
            let inner_q = q_reg;
            h inner_q;
        }
        my_gate qr;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        assert tape.operations[0].name == 'Hadamard' and tape.operations[0].wires.tolist() == [0]

        with pytest.raises(NameError, match="'inner_q' is not defined"):
            visitor.visit_Identifier(openqasm3.ast.Identifier(name="inner_q"))

    def test_gate_can_define_local_constant_and_it_is_destroyed(self):
        """Rule: A gate body can define a local const, which is destroyed after."""
        code = """
        OPENQASM 3.0;
        qubit q;
        gate my_gate q_arg {
            const float[64] LOCAL_PI = 3.14159;
            rx(LOCAL_PI) q_arg;
        }
        my_gate q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 1
        assert ops[0].name == 'RX'
        assert math.isclose(ops[0].parameters[0], 3.14159)

        # Verify the constant is not accessible in the global scope afterwards
        with pytest.raises(NameError, match="'LOCAL_PI' is not defined"):
            visitor.visit_Identifier(openqasm3.ast.Identifier(name="LOCAL_PI"))

    # ==========================================================================
    # 5. Gate Body Content Rules
    # ==========================================================================

    @pytest.mark.parametrize("illegal_statement, error_message", [
        ("int[32] x = 5;", ".* cannot declare classical variables in a gate"),
        ("bit[1] c;", ".* cannot declare classical variables in a gate"),
        ("x = 5;", ".* cannot assign to classical parameters in a gate"),
        ("measure q_arg;", ".* cannot have a non-unitary 'measure' instruction in a gate"),
        ("reset q_arg;", ".* cannot have a non-unitary 'reset' instruction in a gate"),
        ("qubit r;", ".* qubit declarations must be global")
    ])
    def test_illegal_statements_in_gate_body_raise(self, illegal_statement, error_message):
        """Rule: Various statements are forbidden inside a gate body."""
        code = f"""
        OPENQASM 3.0;
        int[32] x;
        gate my_bad_gate q_arg {{
            {illegal_statement}
        }}
        """
        visitor = PennylaneVisitor()
        with pytest.raises(ParseError, match=error_message):
            visitor.visit(parse_openqasm3(code))

    def test_for_loop_in_gate_is_valid(self):
        """Rule: 'for' loops are allowed inside a gate body."""
        code = """
        OPENQASM 3.0;
        qubit q;
        gate apply_h_twice q_arg {
            for int i in [0:1] { h q_arg; }
        }
        apply_h_twice q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        assert len(tape.operations) == 2
        assert all(op.name == 'Hadamard' for op in tape.operations)

    # ==========================================================================
    # 6. Name and Argument Rules
    # ==========================================================================

    def test_redefining_builtin_gate_raises(self):
        """Rule: Cannot define a gate with the same name as a built-in gate."""
        code = "OPENQASM 3.0; gate h q {}"
        visitor = PennylaneVisitor()
        with pytest.raises(NameError, match="Gate 'h' is already defined."):
            visitor.visit(parse_openqasm3(code))

    def test_redefining_custom_gate_raises(self):
        """Rule: Cannot redefine a user-defined gate."""
        code = """
        OPENQASM 3.0;
        gate my_gate q {}
        gate my_gate q {}
        """
        visitor = PennylaneVisitor()
        with pytest.raises(NameError, match="Gate 'my_gate' is already defined."):
            visitor.visit(parse_openqasm3(code))

    def test_indexing_gate_qubit_arg_raises(self):
        """Rule: Qubit arguments cannot be indexed within the gate body."""
        code = """
        OPENQASM 3.0;
        gate my_gate q_arg { h q_arg[0]; } // ILLEGAL
        """
        visitor = PennylaneVisitor()
        with pytest.raises(SyntaxError, match="Cannot index qubit parameter 'q_arg'"):
            visitor.visit(parse_openqasm3(code))

    def test_calling_gate_with_wrong_qubit_count_raises(self):
        """Tests error for wrong number of qubit arguments."""
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        gate my_gate a { h a; }
        my_gate q[0], q[1]; // Calling with 2, needs 1
        """
        visitor = PennylaneVisitor()
        with pytest.raises(TypeError, match="Gate 'my_gate' called with 2 qubit arguments, but definition requires 1"):
            visitor.visit(parse_openqasm3(code))

    def test_calling_gate_with_wrong_classical_arg_count_raises(self):
        """Tests error for wrong number of classical arguments."""
        code = """
        OPENQASM 3.0;
        qubit q;
        gate my_gate(a, b) q_arg { }
        my_gate(1.0) q; // Calling with 1, needs 2
        """
        visitor = PennylaneVisitor()
        with pytest.raises(TypeError, match="Gate 'my_gate' called with 1 classical arguments, but definition requires 2"):
            visitor.visit(parse_openqasm3(code))

    def test_calling_undefined_gate_raises(self):
        """Tests that calling a gate that doesn't exist raises an error."""
        code = "OPENQASM 3.0; qubit q; undefined_gate q;"
        visitor = PennylaneVisitor()
        with pytest.raises(NameError, match="Gate 'undefined_gate' is not defined."):
            visitor.visit(parse_openqasm3(code))

    # ==========================================================================
    # 7. Recursion Rules
    # ==========================================================================

    def test_direct_recursive_gate_call_raises(self):
        """Rule: A gate cannot call itself directly."""
        code = """
        OPENQASM 3.0;
        qubit q;
        gate recursive_gate a { recursive_gate a; } // ILLEGAL
        recursive_gate q;
        """
        visitor = PennylaneVisitor()
        with pytest.raises(RecursionError, match="Recursive gate call detected: 'recursive_gate'"):
            visitor.visit(parse_openqasm3(code))


class TestGateModifiers:
  
    def test_inv_on_builtin_gate(self):
            """Tests the 'inv' modifier on a standard gate."""
            code = """
            OPENQASM 3.0;
            qubit q;
            inv @ s q;
            """
            visitor = PennylaneVisitor()
            visitor.visit(parse_openqasm3(code))
            tape = visitor.finalize()
            ops = tape.operations
            assert len(ops) == 1
            # The inverse of S is Sdg
            assert ops[0].name == 'Adjoint(S)'

    def test_nested_inv_on_builtin_gate(self):
        """Tests that a double 'inv' modifier cancels out."""
        code = """
        OPENQASM 3.0;
        qubit q;
        inv @ inv @ h q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 1
        # name should be Adjoint(Adjoint(H)) which simplifies to H
        assert ops[0].name == "Adjoint(Adjoint(Hadamard))"
        
    def test_pow_on_builtin_gate(self):
        """Tests the 'pow' modifier on a standard gate."""
        code = """
        OPENQASM 3.0;
        qubit q;
        pow(3) @ x q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 1
        assert isinstance(ops[0], qml.ops.op_math.Pow)
        assert ops[0].base.name == 'PauliX'
        assert ops[0].z == 3

    def test_nested_pow_on_builtin_gate(self):
        """Tests that nested 'pow' modifiers multiply their exponents."""
        code = """
        OPENQASM 3.0;
        qubit q;
        pow(2) @ pow(3) @ t q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 1
        # pow(2) @ pow(3) @ T should be Pow(Pow(T, 3), 2)
        # PennyLane doesn't simplify this, so we check the structure.
        assert isinstance(ops[0], qml.ops.op_math.Pow)
        assert ops[0].z == 2
        assert isinstance(ops[0].base, qml.ops.op_math.Pow)
        assert ops[0].base.z == 3
        assert ops[0].base.base.name == 'T'
        
    def test_inv_of_pow_on_builtin_gate(self):
        """Tests applying 'inv' to a 'pow' modified gate."""
        code = """
        OPENQASM 3.0;
        qubit q;
        inv @ pow(3) @ s q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations

        # Expected structure: Adjoint(Pow(S, 3))
        assert len(ops) == 1
        final_op = ops[0]

        assert isinstance(final_op, qml.ops.op_math.Adjoint)
        
        pow_op = final_op.base
        assert isinstance(pow_op, qml.ops.op_math.Pow)
        assert pow_op.z == 3
        
        s_gate = pow_op.base
        assert s_gate.name == 'S'

    def test_pow_of_inv_on_builtin_gate(self):
        """Tests applying 'pow' to an 'inv' modified gate."""
        code = """
        OPENQASM 3.0;
        qubit q;
        pow(3) @ inv @ s q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations

        # Expected structure: Pow(Adjoint(S), 3)
        assert len(ops) == 1
        final_op = ops[0]

        assert isinstance(final_op, qml.ops.op_math.Pow)
        assert final_op.z == 3
        
        adjoint_op = final_op.base
        assert isinstance(adjoint_op, qml.ops.op_math.Adjoint)
        
        s_gate = adjoint_op.base
        assert s_gate.name == 'S'


    def test_inv_on_custom_gate(self):
        """Tests 'inv' modifier on a single-op custom gate."""
        code = """
        OPENQASM 3.0;
        gate myx(theta) q {
            rx(theta) q;
        }
        qubit q;
        inv @ myx(0.5) q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 1
        # Expected: Adjoint(RX)
        assert isinstance(ops[0], qml.ops.op_math.Adjoint)
        assert ops[0].base.name == "RX"

    def test_inv_on_multiop_custom_gate(self):
        """Tests 'inv' modifier on a multi-op custom gate."""
        code = """
        OPENQASM 3.0;
        gate combo(theta, phi) q {
            rx(theta) q;
            rz(phi) q;
        }
        qubit q;
        inv @ combo(0.5, 0.3) q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        # Two ops → reversed and adjointed
        assert len(ops) == 2
        assert ops[0].name == "Adjoint(RZ)"
        assert ops[1].name == "Adjoint(RX)"

    def test_pow_on_custom_gate_single_op(self):
        """Tests 'pow' modifier on a single-op custom gate."""
        code = """
        OPENQASM 3.0;
        gate myx(theta) q {
            rx(theta) q;
        }
        qubit q;
        pow(2) @ myx(0.25) q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        # Expect Pow(RX, 2)
        assert len(ops) == 1
        assert isinstance(ops[0], qml.ops.op_math.Pow)
        assert ops[0].base.name == "RX"
        assert ops[0].z == 2

    def test_pow_on_custom_gate_multiop(self):
        """Tests 'pow' modifier on a multi-op custom gate."""
        code = """
        OPENQASM 3.0;
        gate combo(theta, phi) q {
            rx(theta) q;
            rz(phi) q;
        }
        qubit q;
        pow(3) @ combo(0.2, 0.5) q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        # Multi-op → repeated sequence (3×2 = 6)
        assert len(ops) == 6
        names = [op.name for op in ops]
        assert names == ["RX", "RZ", "RX", "RZ", "RX", "RZ"]

    def test_nested_inv_on_custom_gate(self):
        """Tests that nested 'inv' on custom gate applies twice."""
        code = """
        OPENQASM 3.0;
        gate myx(theta) q {
            rx(theta) q;
        }
        qubit q;
        inv @ inv @ myx(0.7) q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 1
        # Adjoint(Adjoint(RX)) — PennyLane won’t simplify automatically
        assert isinstance(ops[0], qml.ops.op_math.Adjoint)
        assert isinstance(ops[0].base, qml.ops.op_math.Adjoint)
        assert ops[0].base.base.name == "RX"

    def test_nested_pow_on_custom_gate(self):
        """Tests nested pow modifiers on a custom gate."""
        code = """
        OPENQASM 3.0;
        gate myx(theta) q {
            rx(theta) q;
        }
        qubit q;
        pow(2) @ pow(3) @ myx(0.8) q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        # Expect Pow(Pow(RX, 3), 2)
        assert len(ops) == 1
        outer = ops[0]
        assert isinstance(outer, qml.ops.op_math.Pow)
        assert outer.z == 2
        inner = outer.base
        assert isinstance(inner, qml.ops.op_math.Pow)
        assert inner.z == 3
        assert inner.base.name == "RX"

    def test_inv_of_pow_on_custom_gate(self):
        """Tests inv applied to a pow-modified custom gate."""
        code = """
        OPENQASM 3.0;
        gate myx(theta) q {
            rx(theta) q;
        }
        qubit q;
        inv @ pow(3) @ myx(0.5) q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        # Expect Adjoint(Pow(RX, 3))
        assert len(ops) == 1
        adj = ops[0]
        assert isinstance(adj, qml.ops.op_math.Adjoint)
        inner = adj.base
        assert isinstance(inner, qml.ops.op_math.Pow)
        assert inner.z == 3
        assert inner.base.name == "RX"

    def test_pow_of_inv_on_custom_gate(self):
        """Tests pow applied to an inv-modified custom gate."""
        code = """
        OPENQASM 3.0;
        gate myx(theta) q {
            rx(theta) q;
        }
        qubit q;
        pow(3) @ inv @ myx(0.5) q;
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        # Expect Pow(Adjoint(RX), 3)
        assert len(ops) == 1
        pow_op = ops[0]
        assert isinstance(pow_op, qml.ops.op_math.Pow)
        assert pow_op.z == 3
        adj = pow_op.base
        assert isinstance(adj, qml.ops.op_math.Adjoint)
        assert adj.base.name == "RX"
        
    def test_ctrl_on_builtin_gate_single_qubit(self):
        """Apply a single control on a single-qubit built-in gate."""
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        ctrl(1) @ h q[1], q[0];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations

        assert len(ops) == 1
        ctrl_op = ops[0]
        assert isinstance(ctrl_op, qml.ops.op_math.Controlled)
        assert ctrl_op.control_wires.tolist() == [1]
        assert ctrl_op.base.name == "Hadamard"

    def test_negctrl_on_builtin_gate_single_qubit(self):
        """Apply negated control on a single-qubit built-in gate."""
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        negctrl(1) @ x q[1], q[0];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations

        assert len(ops) == 1
        ctrl_op = ops[0]
        assert isinstance(ctrl_op, qml.ops.op_math.Controlled)
        assert ctrl_op.control_wires.tolist() == [1]
        assert ctrl_op.control_values == [0]  # negctrl
        assert ctrl_op.base.name == "PauliX"

    # --- Custom Gates ---
    def test_ctrl_on_custom_gate_single_op(self):
        """Control applied to a custom gate with a single operation."""
        code = """
        OPENQASM 3.0;
        qubit[3] q;
        gate g1 q_arg { h q_arg; }
        ctrl(2) @ g1 q[2], q[0], q[1];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations

        assert len(ops) == 1
        ctrl_op = ops[0]
        assert isinstance(ctrl_op, qml.ops.op_math.Controlled)
        # Last 2 qubits are controls
        assert ctrl_op.control_wires.tolist() == [2, 0]
        assert ctrl_op.base.name == "Hadamard"

    def test_negctrl_on_custom_gate_single_op(self):
        """Negated control applied to a custom gate with a single operation."""
        code = """
        OPENQASM 3.0;
        qubit[3] q;
        gate g1 q_arg { x q_arg; }
        negctrl(2) @ g1 q[2], q[0], q[1];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations

        assert len(ops) == 1
        ctrl_op = ops[0]
        assert isinstance(ctrl_op, qml.ops.op_math.Controlled)
        assert ctrl_op.control_wires.tolist() == [2, 0]
        assert ctrl_op.control_values == [0, 0]  # negctrl
        assert ctrl_op.base.name == "PauliX"

    def test_ctrl_on_custom_gate_multiple_ops(self):
        """Control applied to a custom gate with multiple operations."""
        code = """
        OPENQASM 3.0;
        qubit[4] q;
        gate g1 q_arg { h q_arg; x q_arg; }
        ctrl(2) @ g1 q[2], q[0], q[1];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations

        assert len(ops) == 2
        ctrl_op = ops[0]
        assert isinstance(ctrl_op, qml.ops.op_math.Controlled)
        assert ctrl_op.control_wires.tolist() == [2, 0]

    def test_negctrl_on_custom_gate_multiple_ops(self):
        """Negated control applied to a multi-op custom gate."""
        code = """
        OPENQASM 3.0;
        qubit[4] q;
        gate g1 q_arg { h q_arg; x q_arg; }
        negctrl(2) @ g1 q[2], q[0], q[1];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations

        assert len(ops) == 2
        ctrl_op = ops[0]
        assert isinstance(ctrl_op, qml.ops.op_math.Controlled)
        assert ctrl_op.control_wires.tolist() == [2, 0]
        assert ctrl_op.control_values == [0, 0]

    def test_ctrl_on_x_is_simplified_to_cnot(self):
        """Tests that 'ctrl @ x' is simplified to a CNOT."""
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        ctrl @ x q[0], q[1];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        assert len(ops) == 1
        assert ops[0].name == "CNOT" # Not "Controlled"
        
    def test_not_enough_target_qubits_after_control_raises_error(self):
        """Tests error when controls leave too few qubits for the target gate."""
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        // CNOT needs 2 target qubits, but ctrl(1) leaves only 1.
        ctrl(1) @ cx q[0], q[1]; 
        """
        visitor = PennylaneVisitor()
        with pytest.raises(ValueError, match="PauliX: wrong number of wires. 0 wires given, 1 expected."):
            visitor.visit(parse_openqasm3(code))
            
    def test_inv_of_ctrl_on_builtin_gate(self):
        """Tests applying 'inv' to a controlled gate."""
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        inv @ ctrl @ h q[0], q[1];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations

        assert len(ops) == 1
        final_op = ops[0]

        # The outer layer should be Adjoint
        assert isinstance(final_op, qml.ops.op_math.Adjoint)
        
        # The inner layer should be the Controlled op
        ctrl_op = final_op.base
        assert isinstance(ctrl_op, qml.ops.op_math.Controlled)
        assert ctrl_op.control_wires.tolist() == [0]
        assert ctrl_op.base.name == "Hadamard"

    def test_pow_of_ctrl_on_builtin_gate(self):
        """Tests applying 'pow' to a controlled gate."""
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        pow(3) @ ctrl @ h q[0], q[1];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations

        assert len(ops) == 1
        final_op = ops[0]

        # The outer layer should be Pow
        assert isinstance(final_op, qml.ops.op_math.Pow)
        assert final_op.z == 3
        
        # The inner layer should be the Controlled op
        ctrl_op = final_op.base
        assert isinstance(ctrl_op, qml.ops.op_math.Controlled)
        assert ctrl_op.control_wires.tolist() == [0]
        assert ctrl_op.base.name == "Hadamard"


class TestGateBroadcasting:

    # ==========================================================================
    # 1. Basic Broadcasting on Built-in Gates
    # ==========================================================================

    def test_basic_broadcasting_on_builtin_gate(self):
        """Tests applying a single-qubit gate to a qubit register."""
        code = """
        OPENQASM 3.0;
        qubit[3] qr;
        h qr; // Broadcasts to h qr[0]; h qr[1]; h qr[2];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        
        assert len(ops) == 3
        assert all(op.name == 'Hadamard' for op in ops)
        assert ops[0].wires.tolist() == [0]
        assert ops[1].wires.tolist() == [1]
        assert ops[2].wires.tolist() == [2]

    def test_multi_qubit_broadcasting_on_builtin_gate(self):
        """Tests applying a two-qubit gate to two registers of the same size."""
        code = """
        OPENQASM 3.0;
        qubit[2] qra;
        qubit[2] qrb;
        cx qra, qrb; // Broadcasts to cx qra[0], qrb[0]; cx qra[1], qrb[1];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        
        assert len(ops) == 2
        assert all(op.name == 'CNOT' for op in ops)
        assert ops[0].wires.tolist() == [0, 2]
        assert ops[1].wires.tolist() == [1, 3]

    def test_broadcasting_mismatched_size_raises(self):
        """Rule: Broadcasting registers must have the same length (if > 1)."""
        code = """
        OPENQASM 3.0;
        qubit[2] qra;
        qubit[3] qrb;
        cx qra, qrb; // ILLEGAL: 2 != 3
        """
        visitor = PennylaneVisitor()
        with pytest.raises(ValueError, match="Broadcast sizes mismatch: .*"):
            visitor.visit(parse_openqasm3(code))

    def test_broadcasting_with_single_qubit_and_register(self):
        """Tests broadcasting a multi-qubit gate where one argument is a single qubit."""
        code = """
        OPENQASM 3.0;
        qubit qa;
        qubit[2] qr;
        cx qa, qr; // Broadcasts to cx qa, qr[0]; cx qa, qr[1];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        
        # qa is wire 0, qr is wires 1, 2
        assert len(ops) == 2
        assert all(op.name == 'CNOT' for op in ops)
        assert ops[0].wires.tolist() == [0, 1]
        assert ops[1].wires.tolist() == [0, 2]

    # ==========================================================================
    # 2. Broadcasting with Parameterized Gates
    # ==========================================================================

    def test_broadcasting_with_classical_parameter(self):
        """Tests a parameterized gate applied across a register."""
        code = """
        OPENQASM 3.0;
        qubit[2] qr;
        rx(pi/2) qr; 
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        
        assert len(ops) == 2
        assert all(op.name == 'RX' for op in ops)
        assert math.isclose(ops[0].parameters[0], math.pi / 2)
        assert ops[0].wires.tolist() == [0]
        assert ops[1].wires.tolist() == [1]


    # ==========================================================================
    # 3. Broadcasting on Custom Gates
    # ==========================================================================

    def test_broadcasting_on_custom_gate_multi_op(self):
        """Tests applying a multi-op custom gate across a register."""
        code = """
        OPENQASM 3.0;
        qubit[2] qr;
        gate my_gate a { h a; x a; }
        my_gate qr; // Broadcasts to h qr[i]; x qr[i]; for i=0, 1
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations

        assert len(ops) == 4
        # Iteration 0: H(0), X(0)
        assert ops[0].name == 'Hadamard' and ops[0].wires.tolist() == [0]
        assert ops[1].name == 'PauliX' and ops[1].wires.tolist() == [0]
        # Iteration 1: H(1), X(1)
        assert ops[2].name == 'Hadamard' and ops[2].wires.tolist() == [1]
        assert ops[3].name == 'PauliX' and ops[3].wires.tolist() == [1]

    # ==========================================================================
    # 4. Broadcasting with Modifiers
    # ==========================================================================

    def test_broadcasting_with_inv_modifier(self):
        """Tests 'inv' modifier applied to a broadcasted gate."""
        code = """
        OPENQASM 3.0;
        qubit[2] qr;
        inv @ s qr; // inv@s qr[0]; inv@s qr[1];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        
        assert len(ops) == 2
        assert all(op.name == 'Adjoint(S)' for op in ops)
        assert ops[0].wires.tolist() == [0]
        assert ops[1].wires.tolist() == [1]

    def test_broadcasting_with_pow_modifier(self):
        """Tests 'pow' modifier applied to a broadcasted gate."""
        code = """
        OPENQASM 3.0;
        qubit[2] qr;
        pow(3) @ x qr; // pow(3)@x qr[0]; pow(3)@x qr[1];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        
        assert len(ops) == 2
        assert all(isinstance(op, qml.ops.op_math.Pow) for op in ops)
        assert ops[0].base.name == 'PauliX' and ops[0].wires.tolist() == [0]
        assert ops[1].base.name == 'PauliX' and ops[1].wires.tolist() == [1]

    def test_broadcasting_with_ctrl_modifier(self):
        """Tests 'ctrl' modifier applied to two broadcasted registers."""
        code = """
        OPENQASM 3.0;
        qubit[2] qc;
        qubit[2] qt;
        ctrl @ x qc, qt; // ctrl@x qc[0], qt[0]; ctrl@x qc[1], qt[1]; -> CNOTs
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        
        # qc is wires 0, 1. qt is wires 2, 3.
        assert len(ops) == 2
        assert all(op.name == 'CNOT' for op in ops)
        # Iteration 0: Control=qc[0], Target=qt[0]
        assert ops[0].wires.tolist() == [0, 2]
        # Iteration 1: Control=qc[1], Target=qt[1]
        assert ops[1].wires.tolist() == [1, 3]

    def test_broadcasting_with_negctrl_modifier(self):
        """Tests 'negctrl' modifier applied to two broadcasted registers."""
        code = """
        OPENQASM 3.0;
        qubit[2] qc;
        qubit[2] qt;
        negctrl @ h qc, qt; 
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        
        # qc is wires 0, 1. qt is wires 2, 3.
        assert len(ops) == 2
        assert all(isinstance(op, qml.ops.op_math.Controlled) for op in ops)
        
        # Iteration 0: Control=qc[0] (0-controlled), Target=qt[0]
        assert ops[0].control_wires.tolist() == [0]
        assert ops[0].control_values == [0]
        assert ops[0].base.name == 'Hadamard'
        
        # Iteration 1: Control=qc[1] (0-controlled), Target=qt[1]
        assert ops[1].control_wires.tolist() == [1]
        assert ops[1].control_values == [0]
        assert ops[1].base.name == 'Hadamard'

    def test_ctrl_on_broadcast_with_single_control_qubit(self):
        """Tests 'ctrl' modifier where the control is a single qubit and the target is a register."""
        code = """
        OPENQASM 3.0;
        qubit qc;
        qubit[2] qr;
        ctrl @ x qc, qr; // ctrl@x qc, qr[0]; ctrl@x qc, qr[1];
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        
        # qc is wire 0, qr is wires 1, 2.
        assert len(ops) == 2
        assert all(op.name == 'CNOT' for op in ops)
        # Iteration 0: Control=qc (wire 0), Target=qr[0] (wire 1)
        assert ops[0].wires.tolist() == [0, 1]
        # Iteration 1: Control=qc (wire 0), Target=qr[1] (wire 2)
        assert ops[1].wires.tolist() == [0, 2]
    
    
    def test_multi_ctrl_on_broadcasted_builtin_gate(self):
        """
        Tests multi-control (ctrl(2)) applied to two broadcasted registers (C: 2, T: 2).
        Target is a single-qubit gate (H).
        Expected: ctrl@h on C[i], C[i+2], T[i] for i=0, 1. (A CCH gate)
        """
        code = """
        OPENQASM 3.0;
        qubit[2] qc1; // Wires 0, 1
        qubit[2] qc2; // Wires 2, 3
        qubit[2] qt;  // Wires 4, 5
        
        // Target gate is H, which needs 1 qubit. Controls need 2. Total args = 3 registers (6 qubits).
        ctrl(2) @ h qc1, qc2, qt; 
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations
        
        assert len(ops) == 2
        assert all(isinstance(op, qml.ops.op_math.Controlled) for op in ops)
        
        # Iteration 0: Wires used are [qc1[0]=0, qc2[0]=2, qt[0]=4]. Controls are first 2.
        assert ops[0].control_wires.tolist() == [0, 2]
        assert ops[0].wires.tolist() == [0, 2, 4]
        assert ops[0].base.name == 'Hadamard' and ops[0].base.wires.tolist() == [4]
        
        # Iteration 1: Wires used are [qc1[1]=1, qc2[1]=3, qt[1]=5]. Controls are first 2.
        assert ops[1].control_wires.tolist() == [1, 3]
        assert ops[1].wires.tolist() == [1, 3, 5]
        assert ops[1].base.name == 'Hadamard' and ops[1].base.wires.tolist() == [5]


    def test_multi_ctrl_on_broadcasted_custom_gate(self):
        """
        Tests multi-control (ctrl(2)) applied to a broadcasted custom gate.
        """
        code = """
        OPENQASM 3.0;
        qubit qc;    // W0 (Single qubit control argument)
        qubit[2] qr_c; // W1, W2 (Broadcasted control argument)
        qubit[2] qr_t; // W3, W4 (Broadcasted target argument)

        gate g1 a { h a; x a; } // Target gate needs 1 qubit.

        // Size is 2 (from qr_c, qr_t).
        // Each iteration uses 3 qubits
        // Wires are listed as: [qc, qr_c[i], qr_t[i]]
        ctrl(2) @ g1 qc, qr_c, qr_t; 
        """
        visitor = PennylaneVisitor()
        visitor.visit(parse_openqasm3(code))
        tape = visitor.finalize()
        ops = tape.operations

        assert len(ops) == 4
        
        # --- Iteration 0: Wires [0, 1, 3] ---
        # 1. Controlled H (target wire 3, controls 0, 1)
        assert isinstance(ops[0], qml.ops.op_math.Controlled)
        assert ops[0].control_wires.tolist() == [0, 1]
        assert ops[0].base.name == 'Hadamard' and ops[0].base.wires.tolist() == [3]
        
        # 2. Controlled X (target wire 3, controls 0, 1)
        assert isinstance(ops[1], qml.ops.op_math.Controlled)
        assert ops[1].control_wires.tolist() == [0, 1]
        assert ops[1].base.name == 'PauliX' and ops[1].base.wires.tolist() == [3]

        # --- Iteration 1: Wires [0, 2, 4] ---
        # 3. Controlled H (target wire 4, controls 0, 2)
        assert isinstance(ops[2], qml.ops.op_math.Controlled)
        assert ops[2].control_wires.tolist() == [0, 2]
        assert ops[2].base.name == 'Hadamard' and ops[2].base.wires.tolist() == [4]
        
        # 4. Controlled X (target wire 4, controls 0, 2)
        assert isinstance(ops[3], qml.ops.op_math.Controlled)
        assert ops[3].control_wires.tolist() == [0, 2]
        assert ops[3].base.name == 'PauliX' and ops[3].base.wires.tolist() == [4]


if __name__ == "__main__":
    pytest.main([__file__])
    