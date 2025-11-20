import pytest
import math
import numpy as np
from qiskit import QuantumCircuit
from qsim.qasm_parser import parse_openqasm3
from qsim.visitors.qiskit_visitor import QiskitVisitor, Angle
import qiskit.circuit
from qiskit.circuit.library import SdgGate, HGate, RXGate, RZGate, XGate, TGate, CHGate, CCXGate, CXGate
from qiskit.circuit.controlledgate import ControlledGate
from qsim.core.exceptions import ParseError

def get_circuit_from_code(code: str) -> QuantumCircuit:
    """Helper to parse and visit an OpenQASM3 code snippet."""
    visitor = QiskitVisitor()
    visitor.visit(parse_openqasm3(code))
    return visitor.finalize()

class TestQubitDeclarations:
    def test_simple_qubit_declaration(self):
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert isinstance(qc, QuantumCircuit)
        assert visitor.get_var('qubits', 'q').size == 2
        assert qc.num_qubits == 2

    def test_const_qubit_size(self):
        code = """
        OPENQASM 3.0;
        const uint SIZE = 5;
        qubit[SIZE] q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert qc.num_qubits == 5
        assert visitor.get_var('qubits', 'q').size == 5

    def test_invalid_non_const_qubit_size(self):
        code = """
        OPENQASM 3.0;
        uint runtime_size = 5;
        qubit[runtime_size] q;
        """
        visitor = QiskitVisitor()
        with pytest.raises(TypeError, match="Qubit register 'q' size must be a compile-time constant"):
            visitor.visit(parse_openqasm3(code))

    def test_negative_qubit_size(self):
        code = """
        OPENQASM 3.0;
        const int SIZE = -1;
        qubit[SIZE] q;
        """
        visitor = QiskitVisitor()
        with pytest.raises(ValueError, match="Register size must be a non-negative integer"):
            visitor.visit(parse_openqasm3(code))

    def test_qubit_declaration_in_non_global_scope(self):
        code = """
        OPENQASM 3.0;
        if (true) {
            qubit q;
        }
        """
        visitor = QiskitVisitor()
        with pytest.raises(ParseError, match="qubit declarations must be global"):
            visitor.visit(parse_openqasm3(code))
class TestClassicalDeclarations:
    def test_classical_declarations_initialized(self):
        code = """
        OPENQASM 3.0;
        int[8] a = -10;
        float[64] c = 3.14;
        bool d = true;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'a') == -10
        assert math.isclose(visitor.get_var('env', 'c'), 3.14)
        assert visitor.get_var('env', 'd') is True

    def test_uint_overflow(self):
        code = """
        OPENQASM 3.0;
        uint[4] x = 18;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'x') == 2  # 18 & ((1 << 4) - 1) = 2

    def test_unsupported_float_size(self):
        code = """
        OPENQASM 3.0;
        float[18] z;
        """
        visitor = QiskitVisitor()
        with pytest.raises(TypeError, match="Unsupported float size: float\\[18\\]"):
            visitor.visit(parse_openqasm3(code))

    def test_bit_declaration(self):
        code = """
        OPENQASM 3.0;
        bit[4] c = "1010";
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('clbits', 'c') == [1, 0, 1, 0]

    def test_classical_declaration_in_dynamic_branch(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        bit m;
        m = measure q;
        if (m == 1) {
            int x = 10;
        }
        """
        visitor = QiskitVisitor()
        with pytest.raises(ValueError, match="Classical declarations not allowed in dynamic control blocks"):
            visitor.visit(parse_openqasm3(code))

class TestExpressions:
    @pytest.mark.parametrize("expression, expected", [
        ("10 + 5", 15),
        ("10 - 12", -2),
        ("5 * 3", 15),
        ("10 / 4", 2.5),
        ("10 % 3", 1),
        ("2 ** 4", 16),
        ("-5", -5),
    ])
    def test_arithmetic_expressions(self, expression, expected):
        code = f"""
        OPENQASM 3.0;
        float[64] result = {expression};
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert math.isclose(visitor.get_var('env', 'result'), expected)

    @pytest.mark.parametrize("expression, expected", [
        ("10 > 5", True),
        ("10 < 5", False),
        ("5.0 <= 5.0", True),
        ("5 >= 6", False),
        ("10 == 10.0", True),
        ("10 != 5", True),
    ])
    def test_comparison_expressions(self, expression, expected):
        code = f"""
        OPENQASM 3.0;
        bool result = {expression};
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'result') is expected

    @pytest.mark.parametrize("expression, expected", [
        ("true && false", False),
        ("true || false", True),
        ("!true", False),
    ])
    def test_logical_expressions(self, expression, expected):
        code = f"""
        OPENQASM 3.0;
        bool result = {expression};
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'result') is expected

    def test_nested_and_combined_expressions(self):
        code = """
        OPENQASM 3.0;
        int[32] a = 10;
        int[32] b = 4;
        int[32] c = 5;
        float[64] d = 2.0;
        float[64] result1 = (a + b) * c / d;
        bool result2 = (a > b) && (c / d == 2.5);
        int[32] result3 = -(a ** 2 % 9);
        bool final_check = !(result1 == 35.0 && result2 || result3 > 0);
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert math.isclose(visitor.get_var('env', 'result1'), 35.0)
        assert visitor.get_var('env', 'result2') is True
        assert visitor.get_var('env', 'result3') == -1
        assert visitor.get_var('env', 'final_check') is False

    def test_literal_formats_and_bitstring_initialization(self):
        code = """
        OPENQASM 3.0;
        int[32] i_hex = 0xff;
        int[32] i_oct = 0o77;
        int[32] i_bin = 0b11000011;
        float[64] f_sci = 1.2e2;
        float[64] f_dot = .5;
        bit[8] b = "10100101";
        int[32] result = i_hex + i_oct - i_bin;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'i_hex') == 255
        assert visitor.get_var('env', 'i_oct') == 63
        assert visitor.get_var('env', 'i_bin') == 195
        assert math.isclose(visitor.get_var('env', 'f_sci'), 120.0)
        assert math.isclose(visitor.get_var('env', 'f_dot'), 0.5)
        assert visitor.get_var('clbits', 'b') == [1, 0, 1, 0, 0, 1, 0, 1]
        assert visitor.get_var('env', 'result') == 123

class TestConstants:
    def test_const_for_qubit_declaration(self):
        code = """
        OPENQASM 3.0;
        const uint SIZE = 5;
        qubit[SIZE] q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert qc.num_qubits == 5
        assert visitor.get_var('env', 'SIZE') == 5

    def test_const_expression_for_qubit_declaration(self):
        code = """
        OPENQASM 3.0;
        const uint A = 2;
        qubit[A * 3 + 1] q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert qc.num_qubits == 7

    def test_invalid_const_initialized_by_runtime_var(self):
        code = """
        OPENQASM 3.0;
        int runtime_var = 10;
        const int B = runtime_var;
        """
        visitor = QiskitVisitor()
        with pytest.raises(TypeError, match="Initializer for constant variable 'B' must be a compile-time constant"):
            visitor.visit(parse_openqasm3(code))

    def test_valid_const_initialized_by_const_expression(self):
        code = """
        OPENQASM 3.0;
        const uint A = 10;
        const int B = -2;
        const int C = A * B + 5;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'C') == -15
        assert visitor.is_const('C') is True

    def test_invalid_const_assignment(self):
        code = """
        OPENQASM 3.0;
        const uint u1 = 4;
        u1 = 5;
        """
        visitor = QiskitVisitor()
        with pytest.raises(TypeError, match="Cannot assign to constant variable 'u1'"):
            visitor.visit(parse_openqasm3(code))

class TestMeasurements:
    def test_simple_measurement(self):
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        bit[2] c;
        c[0] = measure q[0];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        measure_ops = [instr.operation for instr in qc.data if instr.operation.name == "measure"]
        assert len(measure_ops) == 1
        assert qc.data[0].qubits[0]._index == 0
        assert qc.data[0].clbits[0]._index == 0

    def test_measurement_with_broadcast(self):
        code = """
        OPENQASM 3.0;
        qubit[10] q;
        bit[10] c;
        c = measure q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        measure_ops = [instr.operation for instr in qc.data if instr.operation.name == "measure"]
        assert len(measure_ops) == 10
        measured_qubits = [qc.data[i].qubits[0]._index for i in range(len(qc.data))]
        measured_clbits = [qc.data[i].clbits[0]._index for i in range(len(qc.data))]
        assert sorted(measured_qubits) == list(range(10))
        assert sorted(measured_clbits) == list(range(10))

    def test_measurement_with_slicing(self):
        code = """
        OPENQASM 3.0;
        qubit[4] q;
        bit[4] c;
        c[0:2] = measure q[1:3];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        measure_ops = [instr.operation for instr in qc.data if instr.operation.name == "measure"]
        assert len(measure_ops) == 3  # Inclusive range 1:3 -> [1, 2, 3]
        measured_qubits = [qc.data[i].qubits[0]._index for i in range(len(qc.data))]
        measured_clbits = [qc.data[i].clbits[0]._index for i in range(len(qc.data))]
        assert sorted(measured_qubits) == [1, 2, 3]
        assert sorted(measured_clbits) == [0, 1, 2]

    def test_measurement_with_step_slice(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        bit[3] c;
        c = measure q[0:2:4];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        measure_ops = [instr.operation for instr in qc.data if instr.operation.name == "measure"]
        assert len(measure_ops) == 3
        measured_qubits = [qc.data[i].qubits[0]._index for i in range(3)]
        assert sorted(measured_qubits) == [0, 2, 4]

    def test_measurement_in_dynamic_branch(self):
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        bit[2] c;
        c[0] = measure q[0];
        if (c[0] == 1) {
            c[1] = measure q[1];
        }
        """
        visitor = QiskitVisitor()
        with pytest.raises(ValueError, match="Measurements not allowed in dynamic control blocks"):
            visitor.visit(parse_openqasm3(code))

class TestResets:
    def test_reset_operation_on_slice(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        reset q[1:3];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        reset_ops = [instr.operation for instr in qc.data if instr.operation.name == "reset"]
        assert len(reset_ops) == 3
        reset_qubits = [qc.data[i].qubits[0]._index for i in range(3)]
        assert sorted(reset_qubits) == [1, 2, 3]

    def test_reset_with_step_slice(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        reset q[0:2:4];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        reset_ops = [instr.operation for instr in qc.data if instr.operation.name == "reset"]
        assert len(reset_ops) == 3
        reset_qubits = [qc.data[i].qubits[0]._index for i in range(3)]
        assert sorted(reset_qubits) == [0, 2, 4]

class TestAliasing:
    def test_simple_alias_of_slice(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        let my_alias = q[1:3];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        alias = visitor.get_var('qubits', 'my_alias')
        assert len(alias) == 3
        assert [q._index for q in alias] == [1, 2, 3]

    def test_alias_of_single_qubit(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        let single_q = q[4];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        alias = visitor.get_var('qubits', 'single_q')
        assert len(alias) == 1
        assert alias[0]._index == 4

    def test_gate_on_aliased_register(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        let middle_three = q[1:3];
        cx middle_three[0], middle_three[1];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert qc.data[0].operation.name == "cx"
        assert qc.data[0].qubits[0]._index == 1
        assert qc.data[0].qubits[1]._index == 2

    def test_invalid_duplicate_alias_name(self):
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        let q = q[0];
        """
        visitor = QiskitVisitor()
        with pytest.raises(NameError, match="Variable 'q' is already declared in this scope"):
            visitor.visit(parse_openqasm3(code))

    def test_negative_indexing_on_alias(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        let reg = q[1:4];
        x reg[-1];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert qc.data[0].operation.name == "x"
        assert qc.data[0].qubits[0]._index == 4

    def test_discrete_set_indexing_on_alias(self):
        code = """
        OPENQASM 3.0;
        qubit[10] q;
        let my_reg = q[2:8];
        let selection = my_reg[{0, 5, 2}];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        alias = visitor.get_var('qubits', 'selection')
        assert [q._index for q in alias] == [2, 7, 4]

    def test_gate_on_discrete_set_selection(self):
        code = """
        OPENQASM 3.0;
        qubit[10] q;
        let my_reg = q[2:8];
        let selection = my_reg[{0, 5, 2}];
        h selection[1];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert qc.data[0].operation.name == "h"
        assert qc.data[0].qubits[0]._index == 7

    def test_invalid_alias_on_classical_bits(self):
        code = """
        OPENQASM 3.0;
        bit[4] c;
        let my_classical_alias = c[0:1];
        """
        visitor = QiskitVisitor()
        with pytest.raises(TypeError, match="Aliases can only be created for quantum registers"):
            visitor.visit(parse_openqasm3(code))

    def test_alias_with_step_slice(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        let my_alias = q[0:2:4];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        alias = visitor.get_var('qubits', 'my_alias')
        assert [q._index for q in alias] == [0, 2, 4]

    def test_gate_on_alias_with_step(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        let my_alias = q[0:2:4];
        x my_alias[1];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert qc.data[0].operation.name == "x"
        assert qc.data[0].qubits[0]._index == 2

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
        visitor = QiskitVisitor()
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
        visitor = QiskitVisitor()
        # This should execute without error, as stdgates.inc is skipped
        visitor.visit(parse_openqasm3(main_qasm_string))
        assert visitor.get_var('qubits', 'q') is not None

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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(main_qasm_string))
        assert visitor.get_var('env', 'a') == 10
        assert visitor.get_var('env', 'b') == 11

    def test_include_file_not_found_raises(self, tmp_path, monkeypatch):
        """Tests that an appropriate error is raised for a missing file."""
        main_qasm_string = 'OPENQASM 3.0; include "nonexistent.qasm";'
        monkeypatch.chdir(tmp_path)
        visitor = QiskitVisitor()
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
        visitor = QiskitVisitor()
        # The test is that this finishes without a RecursionError
        visitor.visit(parse_openqasm3(main_qasm_string))
        # Both variables should be defined exactly once.
        assert visitor.get_var('env', 'a') == 1
        assert visitor.get_var('env', 'b') == 2

    def test_include_with_gate_definition(self, tmp_path, monkeypatch):
        """Tests that gate definitions in included files work correctly."""
        gate_file = tmp_path / "custom_gates.qasm"
        gate_file.write_text("""
        OPENQASM 3.0;
        gate mygate q {
            h q;
            x q;
        }
        """)
        main_qasm_string = """
        OPENQASM 3.0;
        include "custom_gates.qasm";
        qubit q;
        mygate q;
        """
        monkeypatch.chdir(tmp_path)
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(main_qasm_string))
        qc = visitor.finalize()
        # Check that the circuit has the expected operations from the custom gate
        assert 'mygate' in visitor.custom_gates
        assert len(qc.data) > 0  # Should have operations from mygate

    def test_include_with_constants(self, tmp_path, monkeypatch):
        """Tests that constants in included files are accessible."""
        const_file = tmp_path / "constants.qasm"
        const_file.write_text("""
        OPENQASM 3.0;
        const int[32] MY_CONST = 42;
        """)
        main_qasm_string = """
        OPENQASM 3.0;
        include "constants.qasm";
        int[32] result = MY_CONST * 2;
        """
        monkeypatch.chdir(tmp_path)
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(main_qasm_string))
        assert visitor.get_var('env', 'MY_CONST') == 42
        assert visitor.get_var('env', 'result') == 84

class TestGates:
    @pytest.mark.parametrize("gate", ["id", "x", "y", "z", "h", "s", "sdg", "t", "tdg"])
    def test_single_qubit_gates(self, gate):
        code = f"""
        OPENQASM 3.0;
        qubit[3] q;
        qubit kj;
        {gate} kj;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 1
        assert qc.data[0].operation.name == gate

    @pytest.mark.parametrize("gate", ["cx", "cy", "cz"])
    def test_controlled_gates(self, gate):
        code = f"""
        OPENQASM 3.0;
        qubit[2] q;
        qubit kj;
        {gate} q[0], kj;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert qc.data[0].operation.name == gate
        assert len(qc.data[0].qubits) == 2

    @pytest.mark.parametrize("gate, angle", [
        ("rx", "pi/2"),
        ("ry", "pi/4"),
        ("rz", "pi"),
    ])
    def test_rotation_gates(self, gate, angle):
        code = f"""
        OPENQASM 3.0;
        qubit q;
        {gate}({angle}) q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert qc.data[0].operation.name == gate
        assert math.isclose(qc.data[0].operation.params[0], eval(angle.replace("pi", "math.pi")), rel_tol=1e-9)

    @pytest.mark.parametrize("gate", ["swap", "cswap"])
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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert qc.data[0].operation.name == gate

    def test_iswap_unsupported(self):
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        iswap q[0], q[1];
        """
        visitor = QiskitVisitor()
        with pytest.raises(NameError, match="Gate 'iswap' is not defined"):
            visitor.visit(parse_openqasm3(code))

    def test_u_gate(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        u(pi/2, pi/4, pi) q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert qc.data[0].operation.name == "u"
        for actual, expected in zip(qc.data[0].operation.params, [math.pi/2, math.pi/4, math.pi]):
            assert math.isclose(actual, expected, rel_tol=1e-9)

    def test_gate_with_classical_variable_parameter(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        float[64] my_angle = pi / 2;
        rx(my_angle) q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert qc.data[0].operation.name == "rx"
        assert math.isclose(qc.data[0].operation.params[0], math.pi / 2, rel_tol=1e-9)

    def test_custom_gate(self):
        code = """
        OPENQASM 3.0;
        gate mygate(a) q {
            rx(a) q;
            gphase(-pi/2);
        }
        qubit q;
        mygate(pi/2) q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 1
        assert qc.data[0].operation.name == "rx"
        assert math.isclose(qc.data[0].operation.params[0], math.pi/2, rel_tol=1e-9)
        assert np.isclose(np.exp(1j * qc.global_phase), np.exp(1j * (-math.pi/2)))

class TestGlobalPhase:
    def test_global_phase(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        gphase(pi/3);
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert math.isclose(qc.global_phase, math.pi/3, rel_tol=1e-9)

    def test_multiple_global_phase_accumulation(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        gphase(pi/2);
        gphase(pi/2);
        gphase(-pi);
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert math.isclose(qc.global_phase, 0, rel_tol=1e-9)

class TestAngles:
    def test_angle_declaration_and_initialization(self):
        code = """
        OPENQASM 3.0;
        angle[32] theta = pi;
        angle[64] phi;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        
        assert visitor.get_var('env', 'theta') is not None
        assert isinstance(visitor.get_var('env', 'theta'), Angle)
        assert visitor.get_var('env', 'theta').size == 32
        expected_uint = round((math.pi / (2 * math.pi)) * (2**32))
        assert visitor.get_var('env', 'theta').uint_value == expected_uint
        
        assert visitor.get_var('env', 'phi') is not None
        assert isinstance(visitor.get_var('env', 'phi'), Angle)
        assert visitor.get_var('env', 'phi').size == 64
        assert visitor.get_var('env', 'phi').uint_value == 0

    def test_angle_invalid_size(self):
        code = """
        OPENQASM 3.0;
        angle[8] theta = pi;  // Unsupported size
        """
        visitor = QiskitVisitor()
        with pytest.raises(TypeError, match="Unsupported angle size: angle\\[8\\]. Supported sizes are: \\[16, 32, 64\\]"):
            visitor.visit(parse_openqasm3(code))

    def test_angle_assignment(self):
        code = """
        OPENQASM 3.0;
        angle[32] theta = pi;
        theta = 3 * pi;  // Should normalize to pi
        """
        visitor = QiskitVisitor()
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
        visitor = QiskitVisitor()
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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        
        assert visitor.get_var('env', 'result') is not None
        expected_float = (math.pi + math.pi / 2) % (2 * math.pi)
        assert np.isclose(visitor.get_var('env', 'result'), expected_float, rtol=1e-5)

    def test_angle_negative_value(self):
        code = """
        OPENQASM 3.0;
        angle[32] theta = -pi;  // Should normalize to pi
        """
        visitor = QiskitVisitor()
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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        circuit = visitor.finalize()
        
        rx_ops = [instr.operation for instr in circuit.data if instr.operation.name == 'rx']
        assert len(rx_ops) == 1
        assert circuit.qregs[0][0] == [instr.qubits[0] for instr in circuit.data if instr.operation.name == 'rx'][0]
        assert np.isclose(circuit.data[0].operation.params[0], math.pi / 2, rtol=1e-5)
        
    def test_angle_array_declaration(self):
        code = """
        OPENQASM 3.0;
        array[angle[32], 2] angles = {pi / 2, pi};
        """
        visitor = QiskitVisitor()
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
        visitor = QiskitVisitor()
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
        visitor = QiskitVisitor()
        with pytest.raises(TypeError, match="Unsupported angle size: angle\\[8\\]. Supported sizes are: \\[16, 32, 64\\]"):
            visitor.visit(parse_openqasm3(code))

    def test_angle_in_invalid_expression(self):
        code = """
        OPENQASM 3.0;
        angle[32] theta = pi;
        bit result = theta;  // Invalid: cannot assign angle to bit

        """
        visitor = QiskitVisitor()
        with pytest.raises(ValueError, match="Cannot assign value"):
            visitor.visit(parse_openqasm3(code))

    def test_angle_comparison(self):
        code = """
        OPENQASM 3.0;
        angle[32] theta = pi;
        angle[32] phi = pi / 2;
        bool is_greater = theta > phi;  // True
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'is_greater') is True

    def test_angle_overflow_in_compound_assignment(self):
        code = """
        OPENQASM 3.0;
        angle[32] theta = pi;
        theta += 3 * pi;  // pi + 3pi = 4pi mod 2pi = 0
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        
        assert visitor.get_var('env', 'theta') is not None
        assert isinstance(visitor.get_var('env', 'theta'), Angle)
        expected_float = (math.pi + 3 * math.pi) % (2 * math.pi)
        expected_uint = round((expected_float / (2 * math.pi)) * (2**32))
        assert visitor.get_var('env', 'theta').uint_value == expected_uint
        assert math.isclose(expected_float, 0, rel_tol=1e-9)

class TestArrays:
    def test_array_declaration(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 3] arr = {1, 2, 3};
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        arr = visitor.get_var('env', 'arr')
        assert isinstance(arr, np.ndarray)
        assert np.array_equal(arr, np.array([1, 2, 3], dtype=np.int32))

    def test_array_wrong_initialization_length(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 2] badarr = {1, 2, 3};
        """
        visitor = QiskitVisitor()
        with pytest.raises(ValueError, match="Initializer .* has 3 elements, but expected .* 2"):
            visitor.visit(parse_openqasm3(code))

    def test_compound_assignment_on_array_element(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 2] my_arr = {1, 2};
        my_arr[0] += 3;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert np.array_equal(visitor.get_var('env', 'my_arr'), np.array([4, 2], dtype=np.int32))

    def test_compound_assignment_on_array_slice(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 3] my_arr = {1, 2, 3};
        my_arr[0:2] += my_arr[1:2];
        """
        visitor = QiskitVisitor()
        with pytest.raises(TypeError, match="Compound assignment is only supported for single array elements, not slices"):
            visitor.visit(parse_openqasm3(code))

    def test_overflow_on_bounded_type_assignment(self):
        code = """
        OPENQASM 3.0;
        array[uint[8], 1] my_uint_arr;
        my_uint_arr[0] = 257;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'my_uint_arr')[0] == 1

    def test_multidimensional_array_initialization(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 2, 3] matrix = {{1, 2, 3}, {4, 5, 6}};
        matrix[1][2] = 10;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        expected = np.array([[1, 2, 3], [4, 5, 10]], dtype=np.int32)
        assert np.array_equal(visitor.get_var('env', 'matrix'), expected)

    def test_array_slice_initialization(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 4] my_arr = {1, 2, 3, 4};
        array[int[32], 2] slice_init = my_arr[1:2];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert np.array_equal(visitor.get_var('env', 'slice_init'), np.array([2, 3], dtype=np.int32))

    def test_array_slice_with_step(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 5] my_arr = {0, 1, 2, 3, 4};
        array[int[32], 3] sliced = my_arr[0:2:4];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert np.array_equal(visitor.get_var('env', 'sliced'), np.array([0, 2, 4], dtype=np.int32))

class TestIndexing:
    def test_invalid_multi_dimensional_indexing_on_qubit_register(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        let a = q[1:3][0];
        """
        visitor = QiskitVisitor()
        with pytest.raises(TypeError, match="Multi-dimensional indexing is only supported for classical arrays"):
            visitor.visit(parse_openqasm3(code))

    def test_bit_assignment_from_non_literal(self):
        code = """
        OPENQASM 3.0;
        bit[2] c;
        bit[1] d = "1";
        int[32] x = 10;
        c[0] = d[0];
        c[1] = x > 5;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('clbits', 'c') == [1, 1]

    def test_negative_indexing_on_array(self):
        code = """
        OPENQASM 3.0;
        array[int[32], 4] my_arr = {10, 20, 30, 40};
        int[32] last = my_arr[-1];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'last') == 40

    def test_negative_indexing_on_qubit_register(self):
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        x q[-1];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert qc.data[0].operation.name == "x"
        assert qc.data[0].qubits[0]._index == 4


class TestConcatenation:
    """Tests for register concatenation (++) operator."""
    
    def test_concatenation_of_two_registers(self):
        """Tests basic concatenation of two quantum registers."""
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        qubit[3] r;
        let combined = q ++ r;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        
        combined = visitor.get_var('qubits', 'combined')
        assert len(combined) == 5
        assert [visitor.qc.find_bit(q).index for q in combined] == [0, 1, 2, 3, 4]
    
    def test_concatenation_of_slices_and_aliases(self):
        """Tests concatenating slices and aliases."""
        code = """
        OPENQASM 3.0;
        qubit[10] q;
        let first_two = q[0:1];
        let last_q = q[9];
        let middle_slice = q[4:5];
        let final_reg = first_two ++ middle_slice ++ last_q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        
        final_reg = visitor.get_var('qubits', 'final_reg')
        assert len(final_reg) == 5
        assert [visitor.qc.find_bit(q).index for q in final_reg] == [0, 1, 4, 5, 9]
    
    def test_gate_on_concatenated_alias(self):
        """Tests applying a gate to a concatenated register."""
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        qubit[3] r;
        let combined = r ++ q;
        x combined[3];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        assert len(qc.data) == 1
        assert qc.data[0].operation.name == "x"
        assert visitor.qc.find_bit(qc.data[0].qubits[0]).index == 0
    
    def test_concatenation_preserves_order(self):
        """Tests that concatenation order is preserved."""
        code = """
        OPENQASM 3.0;
        qubit[2] a;
        qubit[2] b;
        qubit[2] c;
        let abc = a ++ b ++ c;
        let cba = c ++ b ++ a;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        
        abc = visitor.get_var('qubits', 'abc')
        cba = visitor.get_var('qubits', 'cba')
        
        assert [visitor.qc.find_bit(q).index for q in abc] == [0, 1, 2, 3, 4, 5]
        assert [visitor.qc.find_bit(q).index for q in cba] == [4, 5, 2, 3, 0, 1]
    
    def test_concatenation_with_single_qubit(self):
        """Tests concatenating a register with a single qubit."""
        code = """
        OPENQASM 3.0;
        qubit[3] q;
        qubit single;
        let combined = q ++ single;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        
        combined = visitor.get_var('qubits', 'combined')
        assert len(combined) == 4
        assert [visitor.qc.find_bit(q).index for q in combined] == [0, 1, 2, 3]
    
    def test_concatenation_with_indexed_qubits(self):
        """Tests concatenating indexed qubits."""
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        let combined = q[0] ++ q[2] ++ q[4];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        
        combined = visitor.get_var('qubits', 'combined')
        assert len(combined) == 3
        assert [visitor.qc.find_bit(q).index for q in combined] == [0, 2, 4]
    
    def test_concatenation_with_step_slices(self):
        """Tests concatenating registers with step slices."""
        code = """
        OPENQASM 3.0;
        qubit[10] q;
        let evens = q[0:2:8];
        let odds = q[1:2:9];
        let combined = evens ++ odds;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        
        combined = visitor.get_var('qubits', 'combined')
        assert len(combined) == 10
        assert [visitor.qc.find_bit(q).index for q in combined] == [0, 2, 4, 6, 8, 1, 3, 5, 7, 9]
    
    def test_gate_on_concatenated_slice(self):
        """Tests applying gates to slices of concatenated registers."""
        code = """
        OPENQASM 3.0;
        qubit[2] a;
        qubit[2] b;
        let ab = a ++ b;
        h ab[0];
        cx ab[1], ab[2];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        assert len(qc.data) == 2
        assert qc.data[0].operation.name == "h"
        assert visitor.qc.find_bit(qc.data[0].qubits[0]).index == 0
        assert qc.data[1].operation.name == "cx"
        assert visitor.qc.find_bit(qc.data[1].qubits[0]).index == 1
        assert visitor.qc.find_bit(qc.data[1].qubits[1]).index == 2
    
    def test_measurement_on_concatenated_register(self):
        """Tests measuring qubits from a concatenated register."""
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        qubit[2] r;
        bit[4] c;
        let combined = q ++ r;
        c = measure combined;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        measure_ops = [instr for instr in qc.data if instr.operation.name == "measure"]
        assert len(measure_ops) == 4
        measured_qubits = sorted([visitor.qc.find_bit(instr.qubits[0]).index for instr in measure_ops])
        assert measured_qubits == [0, 1, 2, 3]
    
    def test_invalid_self_concatenation(self):
        """Tests that concatenating a register with itself raises an error."""
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        let test = q ++ q;
        """
        visitor = QiskitVisitor()
        with pytest.raises(ValueError, match="Cannot concatenate registers with overlapping qubits"):
            visitor.visit(parse_openqasm3(code))
    
    def test_invalid_self_concatenation_with_slice(self):
        """Tests that concatenating a register with its slice raises an error."""
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        let test = q ++ q[1:3];
        """
        visitor = QiskitVisitor()
        with pytest.raises(ValueError, match="Cannot concatenate registers with overlapping qubits"):
            visitor.visit(parse_openqasm3(code))
    
    def test_invalid_concatenation_with_alias_overlap(self):
        """Tests that concatenating overlapping aliases raises an error."""
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        let a = q[0:2];
        let b = q[1:3];
        let test = a ++ b;
        """
        visitor = QiskitVisitor()
        with pytest.raises(ValueError, match="Cannot concatenate registers with overlapping qubits"):
            visitor.visit(parse_openqasm3(code))
    
    def test_invalid_mixed_type_concatenation(self):
        """Tests that concatenating quantum and classical registers raises an error."""
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        bit[2] c;
        let test = q ++ c;
        """
        visitor = QiskitVisitor()
        with pytest.raises(TypeError, match="Can only concatenate quantum registers"):
            visitor.visit(parse_openqasm3(code))
    
    def test_concatenation_in_gate_call(self):
        """Tests using concatenated registers directly in gate calls."""
        code = """
        OPENQASM 3.0;
        qubit[2] a;
        qubit[2] b;
        let combined = a ++ b;
        barrier combined;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        assert len(qc.data) == 1
        assert qc.data[0].operation.name == "barrier"
        barrier_qubits = sorted([visitor.qc.find_bit(q).index for q in qc.data[0].qubits])
        assert barrier_qubits == [0, 1, 2, 3]
    
    def test_concatenation_with_negative_indices(self):
        """Tests concatenating slices with negative indices."""
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        let first_last = q[0] ++ q[-1];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        
        first_last = visitor.get_var('qubits', 'first_last')
        assert len(first_last) == 2
        assert [visitor.qc.find_bit(q).index for q in first_last] == [0, 4]
    
    def test_concatenation_chaining(self):
        """Tests chaining multiple concatenations."""
        code = """
        OPENQASM 3.0;
        qubit[1] a;
        qubit[1] b;
        qubit[1] c;
        qubit[1] d;
        let abcd = a ++ b ++ c ++ d;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        
        abcd = visitor.get_var('qubits', 'abcd')
        assert len(abcd) == 4
        assert [visitor.qc.find_bit(q).index for q in abcd] == [0, 1, 2, 3]
    
    def test_concatenation_with_discrete_set(self):
        """Tests concatenating with discrete set selections."""
        code = """
        OPENQASM 3.0;
        qubit[6] q;
        let selection = q[{0, 2, 4}] ++ q[{1, 3, 5}];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        
        selection = visitor.get_var('qubits', 'selection')
        assert len(selection) == 6
        assert [visitor.qc.find_bit(q).index for q in selection] == [0, 2, 4, 1, 3, 5]
    
    def test_reset_on_concatenated_register(self):
        """Tests resetting qubits in a concatenated register."""
        code = """
        OPENQASM 3.0;
        qubit[2] a;
        qubit[2] b;
        let ab = a ++ b;
        reset ab[1:2];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        reset_ops = [instr for instr in qc.data if instr.operation.name == "reset"]
        assert len(reset_ops) == 2
        reset_qubits = sorted([visitor.qc.find_bit(instr.qubits[0]).index for instr in reset_ops])
        assert reset_qubits == [1, 2]
    
    def test_concatenation_result_can_be_sliced(self):
        """Tests that concatenation results can be further sliced."""
        code = """
        OPENQASM 3.0;
        qubit[3] a;
        qubit[3] b;
        let ab = a ++ b;
        let middle = ab[2:4];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        
        middle = visitor.get_var('qubits', 'middle')
        assert len(middle) == 3
        assert [visitor.qc.find_bit(q).index for q in middle] == [2, 3, 4]
    
    def test_concatenation_with_empty_slice(self):
        """Tests behavior when concatenating with results of empty operations."""
        code = """
        OPENQASM 3.0;
        qubit[3] a;
        qubit[2] b;
        let ab = a[0:1] ++ b;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        
        ab = visitor.get_var('qubits', 'ab')
        assert len(ab) == 4
        assert [visitor.qc.find_bit(q).index for q in ab] == [0, 1, 3, 4]

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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'x') == 1
        qc = visitor.finalize()
        assert len(qc.data) == 1
        assert qc.data[0].operation.name == "x"

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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'x') == 2
        qc = visitor.finalize()
        assert len(qc.data) == 1
        assert qc.data[0].operation.name == "h"

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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'x') == 1
        qc = visitor.finalize()
        assert len(qc.data) == 1
        assert qc.data[0].operation.name == "x"

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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 1
        assert qc.data[0].operation.name == "x"

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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 3  # X, measure, and if_else
        assert qc.data[0].operation.name == "x"
        assert qc.data[1].operation.name == "measure"
        assert qc.data[2].operation.name == "if_else"
        assert isinstance(qc.data[2].operation, qiskit.circuit.ControlFlowOp)

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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'x') == 2
        qc = visitor.finalize()
        assert len(qc.data) == 1
        assert qc.data[0].operation.name == "x"

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
        visitor = QiskitVisitor()
        with pytest.raises(ValueError, match="Measurements not allowed in dynamic control blocks"):
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
        visitor = QiskitVisitor()
        with pytest.raises(ValueError, match="Nested dynamic control blocks are not allowed"):
            visitor.visit(parse_openqasm3(code))

    def test_shadowing_in_if_block(self):
        code = """
        OPENQASM 3.0;
        int[32] x = 10;
        if (true) {
            int[32] x = 20;
            x += 5;
        }
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'x') == 10

    def test_update_outer_var_in_if(self):
        code = """
        OPENQASM 3.0;
        int[32] x = 10;
        if (true) {
            x += 5;
        }
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        assert visitor.get_var('env', 'x') == 15

    def test_invalid_classical_decl_in_dynamic_if(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        bit[1] m;
        m = measure q;
        if (m == 1) {
            int[32] x = 10;
        }
        """
        visitor = QiskitVisitor()
        with pytest.raises(ValueError, match="Classical declarations not allowed in dynamic control blocks"):
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
        visitor = QiskitVisitor()
        with pytest.raises(ValueError, match="Standalone expression statements not allowed in dynamic control blocks"):
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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 2  # measure, if_else
        assert qc.data[0].operation.name == "measure"
        assert qc.data[1].operation.name == "if_else"
        assert isinstance(qc.data[1].operation, qiskit.circuit.ControlFlowOp)
        # Check the true branch circuit
        true_circuit = qc.data[1].operation.blocks[0]
        assert len(true_circuit.data) == 1
        assert true_circuit.data[0].operation.name == "rx"
        assert math.isclose(true_circuit.data[0].operation.params[0], math.pi / 2, rel_tol=1e-9)

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
        visitor = QiskitVisitor()
        with pytest.raises(ValueError, match="Cannot determine classical register for dynamic if condition"):
            visitor.visit(parse_openqasm3(code))

    def test_if_with_false_condition_no_ops(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        if (false) {
            x q;
        }
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 0

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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 1
        assert qc.data[0].operation.name == "x"

    def test_alias_in_static_if(self):
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        if (true) {
            let alias_q = q[0];
            x alias_q;
        }
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 1
        assert qc.data[0].operation.name == "x"
        assert qc.data[0].qubits[0]._index == 0

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
        visitor = QiskitVisitor()
        with pytest.raises(ValueError, match="Alias statements not allowed in dynamic control blocks"):
            visitor.visit(parse_openqasm3(code))

    def test_empty_if_block(self):
        code = """
        OPENQASM 3.0;
        if (true) {
        }
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 0

    def test_if_with_measurement_in_condition(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        bit[1] m;
        m = measure q;
        if (m == 0 || m == 1) {
            x q;
        }
        """
        visitor = QiskitVisitor()
        with pytest.raises(ValueError, match="Cannot determine classical register for dynamic if condition"):
            visitor.visit(parse_openqasm3(code))

    def test_shadowing_and_outer_update_mixed(self):
        code = """
        OPENQASM 3.0;
        int[32] x = 10;
        if (true) {
            int[32] y = 20;
            x += 5;
            if (true) {
                int[32] x = 30;
                x += 10;
            }
            y += x;
        }
        """
        visitor = QiskitVisitor()
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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 1
        assert qc.data[0].operation.name == "x"

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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 3  # h, measure, if_else
        assert qc.data[0].operation.name == "h"
        assert qc.data[1].operation.name == "measure"
        assert qc.data[2].operation.name == "if_else"
        assert isinstance(qc.data[2].operation, qiskit.circuit.ControlFlowOp)
        true_circuit = qc.data[2].operation.blocks[0]
        assert len(true_circuit.data) == 1
        assert true_circuit.data[0].operation.name == "reset"

    def test_invalid_classical_assignment_in_dynamic_if(self):
        code = """
        OPENQASM 3.0;
        qubit q;
        bit m;
        int[32] x = 5;
        m = measure q;
        if (m == 1) {
            x = 10;
        }
        """
        visitor = QiskitVisitor()
        with pytest.raises(ValueError, match="Classical assignments not allowed in dynamic control blocks"):
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
        visitor = QiskitVisitor()
        with pytest.raises(ValueError, match="Cannot determine classical register for dynamic if condition"):
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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        # Unrolls 3 times (0,1,2 inclusive)
        assert len(qc.data) == 3
        for op in qc.data:
            assert op.operation.name == "h"
            assert qc.find_bit(op.qubits[0]).index == 0

    def test_for_loop_discrete_set_unroll(self):
        code = """
        OPENQASM 3.0;
        qubit[1] q;
        for int[32] i in {0, 1, 2} {
            rx(i * 0.1) q[0];
        }
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        # Unrolls 3 times
        assert len(qc.data) == 3
        for idx, op in enumerate(qc.data):
            assert op.operation.name == "rx"
            assert math.isclose(op.operation.params[0], idx * 0.1)
            assert qc.find_bit(op.qubits[0]).index == 0

    def test_for_loop_array_unroll(self):
        code = """
        OPENQASM 3.0;
        qubit[1] q;
        array[float[32], 3] angles = {0.1, 0.2, 0.3};
        for float[32] theta in angles {
            ry(theta) q[0];
        }
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        # Unrolls 3 times
        assert len(qc.data) == 3
        expected_params = [0.1, 0.2, 0.3]
        for idx, op in enumerate(qc.data):
            assert op.operation.name == "ry"
            # Use rel_tol for float32 precision - default is too strict
            assert math.isclose(op.operation.params[0], expected_params[idx], rel_tol=1e-6)

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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        # Unrolls 3 times, but if-block executes twice (for 1s at pos 0,2)
        assert len(qc.data) == 2
        for op in qc.data:
            assert op.operation.name == "x"
            assert qc.find_bit(op.qubits[0]).index == 0

    def test_for_loop_array_slice_unroll(self):
        code = """
        OPENQASM 3.0;
        qubit[1] q;
        array[int[32], 5] arr = {1, 2, 3, 4, 5};
        for int[32] i in arr[1:3] {
            rz(i * 0.5) q[0];
        }
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        # Unrolls 3 times (indices 1,2,3 -> 2,3,4)
        assert len(qc.data) == 3
        expected_params = [1.0, 1.5, 2.0]
        for idx, op in enumerate(qc.data):
            assert op.operation.name == "rz"
            assert math.isclose(op.operation.params[0], expected_params[idx])
            assert qc.find_bit(op.qubits[0]).index == 0

    def test_for_loop_negative_step_unroll(self):
        code = """
        OPENQASM 3.0;
        qubit[1] q;
        for int[32] i in [4:-1:0] {
            rz(i * 0.1) q[0];
        }
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        # Unrolls 5 times (4,3,2,1,0 inclusive)
        assert len(qc.data) == 5
        expected_params = [0.4, 0.3, 0.2, 0.1, 0.0]
        for idx, op in enumerate(qc.data):
            assert op.operation.name == "rz"
            assert math.isclose(op.operation.params[0], expected_params[idx])
            assert qc.find_bit(op.qubits[0]).index == 0

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
        visitor = QiskitVisitor()
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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 3
        # Check operations
        assert qc.data[0].operation.name == "cx"
        assert qc.find_bit(qc.data[0].qubits[0]).index == 0
        assert qc.find_bit(qc.data[0].qubits[1]).index == 1
        assert qc.data[1].operation.name == "cx"
        assert qc.find_bit(qc.data[1].qubits[0]).index == 0
        assert qc.find_bit(qc.data[1].qubits[1]).index == 2
        assert qc.data[2].operation.name == "cx"
        assert qc.find_bit(qc.data[2].qubits[0]).index == 1
        assert qc.find_bit(qc.data[2].qubits[1]).index == 2

    def test_for_loop_modifying_outer_scope_variable(self):
        """Tests that a loop can modify a variable declared in an outer scope."""
        code = """
        OPENQASM 3.0;
        int[32] total = 100;
        for int[32] i in [0:4] {
            total -= i; // total should become 100-0-1-2-3-4 = 90
        }
        """
        visitor = QiskitVisitor()
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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 4
        # Check that the gates were applied to the correct qubits
        expected_indices = [1, 2, 3, 4]
        for idx, op in enumerate(qc.data):
            assert op.operation.name == "x"
            assert qc.find_bit(op.qubits[0]).index == expected_indices[idx]

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
        visitor = QiskitVisitor()
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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        # Empty range: no operations
        assert len(qc.data) == 0

    def test_for_loop_empty_array(self):
        code = """
        OPENQASM 3.0;
        qubit[1] q;
        array[int[32], 0] empty_arr = {};
        for int[32] i in empty_arr {
            x q[0];
        }
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        # Empty array: no operations
        assert len(qc.data) == 0

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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        # The 'if' block should execute twice
        assert len(qc.data) == 2
        for op in qc.data:
            assert op.operation.name == "x"
            assert qc.find_bit(op.qubits[0]).index == 0

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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 2
        expected_params = [math.pi / 2, math.pi]
        for idx, op in enumerate(qc.data):
            assert op.operation.name == "rz"
            assert math.isclose(op.operation.params[0], expected_params[idx], rel_tol=1e-9)
            assert qc.find_bit(op.qubits[0]).index == 0

    def test_for_loop_type_mismatch_raises(self):
        code = """
        OPENQASM 3.0;
        qubit[1] q;
        array[float[32], 2] floats = {1.5, 2.5};
        for int[32] i in floats {
            ry(i) q[0];
        }
        """
        visitor = QiskitVisitor()
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
        visitor=QiskitVisitor()
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
        visitor = QiskitVisitor()
        with pytest.raises(TypeError, match="Cannot iterate over type '.*' or single scalar value."):
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
        visitor = QiskitVisitor()
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
        visitor = QiskitVisitor()
        with pytest.raises(ValueError, match="For loops not allowed in dynamic control blocks."):
            visitor.visit(parse_openqasm3(code))


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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 1
        assert qc.data[0].operation.name == "h"
        assert qc.find_bit(qc.data[0].qubits[0]).index == 0

    def test_gate_with_empty_body_is_identity(self):
        """Tests that a gate with an empty body produces no operations."""
        code = """
        OPENQASM 3.0;
        qubit q;
        gate empty_gate q_arg {}
        empty_gate q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 0

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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 2
        assert qc.data[0].operation.name == "h"
        assert qc.find_bit(qc.data[0].qubits[0]).index == 0
        assert qc.data[1].operation.name == "cx"
        assert qc.find_bit(qc.data[1].qubits[0]).index == 0
        assert qc.find_bit(qc.data[1].qubits[1]).index == 1

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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 1
        assert qc.data[0].operation.name == "rx"
        assert math.isclose(qc.data[0].operation.params[0], 1.234)

    def test_gate_parameter_used_in_expression(self):
        """Tests using a gate's classical parameter inside an expression."""
        code = """
        OPENQASM 3.0;
        qubit q;
        gate my_gate(theta) q_arg { rx(theta * 2) q_arg; }
        my_gate(pi / 4) q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 1
        assert qc.data[0].operation.name == "rx"
        assert math.isclose(qc.data[0].operation.params[0], math.pi / 2)

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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 1
        assert qc.data[0].operation.name == "h"
        assert qc.find_bit(qc.data[0].qubits[0]).index == 0

    # ==========================================================================
    # 4. Scoping Rules
    # ==========================================================================

    def test_gate_defined_in_local_scope_raises(self):
        """Rule: Gate definitions are only allowed in the global scope."""
        code = """
        OPENQASM 3.0;
        for int i in [0:0] {
            gate my_local_gate q {}
        }
        """
        visitor = QiskitVisitor()
        # Parser catches this, so we expect SyntaxError with parser message
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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 1
        assert qc.data[0].operation.name == "rx"
        assert math.isclose(qc.data[0].operation.params[0], 1.5)

    def test_gate_cannot_access_global_mutable_variable_raises(self):
        """Rule: A gate CANNOT access a non-const global variable."""
        code = """
        OPENQASM 3.0;
        qubit q;
        float[64] mutable_angle = 1.5;
        gate my_gate q_arg { rx(mutable_angle) q_arg; } // ILLEGAL
        my_gate q;
        """
        visitor = QiskitVisitor()
        with pytest.raises(NameError, match="Gate or subroutine cannot access non-constant global variable 'mutable_angle'"):
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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 1
        assert qc.data[0].operation.name == "h"
        assert qc.find_bit(qc.data[0].qubits[0]).index == 0

    def test_gate_cannot_declare_classical_vars_raises(self):
        """Rule: Cannot declare classical variables inside a gate body."""
        code = """
        OPENQASM 3.0;
        gate my_gate q_arg {
            int[32] x = 5;
        }
        """
        visitor = QiskitVisitor()
        # Parser catches this
        with pytest.raises(ParseError, match="Failed to parse OpenQASM 3 code"):
            visitor.visit(parse_openqasm3(code))

    def test_gate_local_const_is_scoped(self):
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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 1
        assert qc.data[0].operation.name == "rx"
        assert math.isclose(qc.data[0].operation.params[0], 3.14159)

        # Verify the constant is not accessible in the global scope afterwards
        with pytest.raises(NameError):
            visitor.get_var('env', 'LOCAL_PI')
    # ==========================================================================
    # 5. Gate Body Content Rules
    # ==========================================================================

    @pytest.mark.parametrize("illegal_statement, error_message", [
        ("int[32] x = 5;", "Failed to parse OpenQASM 3 code"),  # Parser error
        ("bit[1] c;", "Failed to parse OpenQASM 3 code"),  # Parser error
        ("x = 5;", "Failed to parse OpenQASM 3 code"),  # Parser error
        ("measure q_arg;", "Failed to parse OpenQASM 3 code"),  # Parser error
        ("reset q_arg;", "Failed to parse OpenQASM 3 code"),  # Parser error
        ("qubit r;", "Failed to parse OpenQASM 3 code")  # Parser error
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
        visitor = QiskitVisitor()
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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        assert len(qc.data) == 2
        assert all(op.operation.name == "h" for op in qc.data)
        assert all(qc.find_bit(op.qubits[0]).index == 0 for op in qc.data)

    # ==========================================================================
    # 6. Name and Argument Rules
    # ==========================================================================

    def test_redefining_builtin_gate_raises(self):
        """Rule: Cannot define a gate with the same name as a built-in gate."""
        code = "OPENQASM 3.0; gate h q {}"
        visitor = QiskitVisitor()
        with pytest.raises(NameError, match="Gate 'h' is already defined and cannot be redeclared"):
            visitor.visit(parse_openqasm3(code))

    def test_redefining_custom_gate_raises(self):
        """Rule: Cannot redefine a user-defined gate."""
        code = """
        OPENQASM 3.0;
        gate my_gate q {}
        gate my_gate q {}
        """
        visitor = QiskitVisitor()
        with pytest.raises(NameError, match="Gate 'my_gate' is already defined and cannot be redeclared"):
            visitor.visit(parse_openqasm3(code))

    def test_indexing_gate_qubit_arg_raises(self):
        """Rule: Qubit arguments cannot be indexed within the gate body."""
        code = """
        OPENQASM 3.0;
        gate my_gate q_arg { h q_arg[0]; }
        """
        visitor = QiskitVisitor()
        with pytest.raises(ValueError, match="Cannot index qubit parameter 'q_arg'"):
            visitor.visit(parse_openqasm3(code))

    def test_calling_gate_with_wrong_qubit_count_raises(self):
        """Tests error for wrong number of qubit arguments."""
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        gate my_gate a { h a; }
        my_gate q[0], q[1]; // Calling with 2, needs 1
        """
        visitor = QiskitVisitor()
        # Changed error message to match actual
        with pytest.raises(TypeError, match="Gate 'my_gate' called with 2 qubit arguments, but definition requires 1"):
            visitor.visit(parse_openqasm3(code))

    def test_calling_gate_with_wrong_classical_arg_count_raises(self):
        """Tests error for wrong number of classical arguments."""
        code = """
        OPENQASM 3.0;
        qubit q;
        gate my_gate(a, b) q_arg { rx(a) q_arg; }
        my_gate(1.0) q;
        """
        visitor = QiskitVisitor()
        with pytest.raises(TypeError, match="Gate 'my_gate' called with 1 classical arguments, but definition requires 2"):
            visitor.visit(parse_openqasm3(code))

    def test_calling_undefined_gate_raises(self):
        """Tests that calling a gate that doesn't exist raises an error."""
        code = "OPENQASM 3.0; qubit q; undefined_gate q;"
        visitor = QiskitVisitor()
        with pytest.raises(NameError, match="Gate 'undefined_gate' is not defined"):  # Changed from NotImplementedError
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
        visitor = QiskitVisitor()
        # Match pattern should just look for the gate name
        with pytest.raises(RecursionError, match="Recursive gate call detected.*recursive_gate"):
            visitor.visit(parse_openqasm3(code))


class TestGateModifiers:
    
    # ============ INV MODIFIER TESTS ============
    
    def test_inv_on_builtin_gate(self):
        """Tests the 'inv' modifier on a standard gate."""
        code = """
        OPENQASM 3.0;
        qubit q;
        inv @ s q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        assert len(qc.data) == 1
        # The inverse of S is Sdg
        assert isinstance(qc.data[0].operation, SdgGate)
    
    def test_nested_inv_on_builtin_gate(self):
        """Tests that a double 'inv' modifier cancels out."""
        code = """
        OPENQASM 3.0;
        qubit q;
        inv @ inv @ h q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        assert len(qc.data) == 1
        # Double inverse should give back the original gate
        assert isinstance(qc.data[0].operation, HGate)
    
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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        assert len(qc.data) == 1
        # Should be inverse of RX
        op = qc.data[0].operation
        assert isinstance(op, RXGate)
        # Check that parameter is negated
        assert np.isclose(op.params[0], -0.5)
    
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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # Two ops → reversed and inverted
        assert len(qc.data) == 2
        # Order should be reversed: RZ first, then RX
        assert isinstance(qc.data[0].operation, RZGate)
        assert isinstance(qc.data[1].operation, RXGate)
        # Parameters should be negated
        assert np.isclose(qc.data[0].operation.params[0], -0.3)
        assert np.isclose(qc.data[1].operation.params[0], -0.5)
    
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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        assert len(qc.data) == 1
        # Double inverse should cancel out
        op = qc.data[0].operation
        assert isinstance(op, RXGate)
        assert np.isclose(op.params[0], 0.7)
    
    def test_inv_on_parametric_gate(self):
        """Tests inv modifier on a parametric gate."""
        code = """
        OPENQASM 3.0;
        qubit q;
        inv @ rx(0.5) q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        assert len(qc.data) == 1
        op = qc.data[0].operation
        assert isinstance(op, RXGate)
        # Parameter should be negated
        assert np.isclose(op.params[0], -0.5)
    
    # ============ POW MODIFIER TESTS ============
    
    def test_pow_on_builtin_gate(self):
        """Tests the 'pow' modifier on a standard gate."""
        code = """
        OPENQASM 3.0;
        qubit q;
        pow(3) @ x q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # pow(3) should repeat the gate 3 times
        assert len(qc.data) == 3
        for i in range(3):
            assert isinstance(qc.data[i].operation, XGate)
    
    def test_nested_pow_on_builtin_gate(self):
        """Tests that nested 'pow' modifiers multiply their exponents."""
        code = """
        OPENQASM 3.0;
        qubit q;
        pow(2) @ pow(3) @ t q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # pow(2) @ pow(3) should give 2*3 = 6 repetitions
        assert len(qc.data) == 6
        for i in range(6):
            assert isinstance(qc.data[i].operation, TGate)
    
    def test_pow_zero_removes_gate(self):
        """Tests that pow(0) removes the gate."""
        code = """
        OPENQASM 3.0;
        qubit q;
        pow(0) @ x q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # pow(0) should result in no operations
        assert len(qc.data) == 0
    
    def test_pow_negative_inverts_and_repeats(self):
        """Tests that pow with negative exponent inverts and repeats."""
        code = """
        OPENQASM 3.0;
        qubit q;
        pow(-2) @ s q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # pow(-2) should give 2 repetitions of inverse (Sdg)
        assert len(qc.data) == 2
        for i in range(2):
            assert isinstance(qc.data[i].operation, SdgGate)
    
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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # Should repeat the gate 2 times
        assert len(qc.data) == 2
        for i in range(2):
            assert isinstance(qc.data[i].operation, RXGate)
            assert np.isclose(qc.data[i].operation.params[0], 0.25)
    
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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # Multi-op → repeated sequence (3×2 = 6)
        assert len(qc.data) == 6
        for i in range(3):
            assert isinstance(qc.data[2*i].operation, RXGate)
            assert np.isclose(qc.data[2*i].operation.params[0], 0.2)
            assert isinstance(qc.data[2*i+1].operation, RZGate)
            assert np.isclose(qc.data[2*i+1].operation.params[0], 0.5)
    
    # ============ COMBINED INV AND POW TESTS ============
    
    def test_inv_of_pow_on_builtin_gate(self):
        """Tests applying 'inv' to a 'pow' modified gate."""
        code = """
        OPENQASM 3.0;
        qubit q;
        inv @ pow(3) @ s q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # inv of (S S S) → Sdg Sdg Sdg (reversed, but same)
        assert len(qc.data) == 3
        for i in range(3):
            assert isinstance(qc.data[i].operation, SdgGate)
    
    def test_pow_of_inv_on_builtin_gate(self):
        """Tests applying 'pow' to an 'inv' modified gate."""
        code = """
        OPENQASM 3.0;
        qubit q;
        pow(3) @ inv @ s q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # pow(3) of Sdg → Sdg Sdg Sdg
        assert len(qc.data) == 3
        for i in range(3):
            assert isinstance(qc.data[i].operation, SdgGate)
    
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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # pow(2*3) → 6 repetitions
        assert len(qc.data) == 6
        for i in range(6):
            assert isinstance(qc.data[i].operation, RXGate)
            assert np.isclose(qc.data[i].operation.params[0], 0.8)
    
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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # inv of (RX RX RX) → RX(-) RX(-) RX(-) (reversed, same)
        assert len(qc.data) == 3
        for i in range(3):
            assert isinstance(qc.data[i].operation, RXGate)
            assert np.isclose(qc.data[i].operation.params[0], -0.5)
    
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
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # pow(3) of RX(-0.5) → RX(-) RX(-) RX(-)
        assert len(qc.data) == 3
        for i in range(3):
            assert isinstance(qc.data[i].operation, RXGate)
            assert np.isclose(qc.data[i].operation.params[0], -0.5)
    
    # ============ CTRL MODIFIER TESTS ============
    
    def test_ctrl_on_builtin_gate_single_qubit(self):
        """Apply a single control on a single-qubit built-in gate."""
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        ctrl(1) @ h q[1], q[0];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        assert len(qc.data) == 1
        op = qc.data[0].operation
        assert isinstance(op, CHGate)
    
    def test_negctrl_on_builtin_gate_single_qubit(self):
        """Apply negated control on a single-qubit built-in gate."""
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        negctrl(1) @ x q[1], q[0];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        assert len(qc.data) == 1
        op = qc.data[0].operation
        assert isinstance(op, ControlledGate)
        assert op.base_gate.name == 'x'
        assert op.ctrl_state == 0
    
    def test_ctrl_on_custom_gate_single_op(self):
        """Control applied to a custom gate with a single operation."""
        code = """
        OPENQASM 3.0;
        qubit[3] q;
        gate g1 q_arg { h q_arg; }
        ctrl(2) @ g1 q[2], q[0], q[1];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        assert len(qc.data) == 1
        op = qc.data[0].operation
        assert isinstance(op, ControlledGate)
        assert op.base_gate.name == 'h'
        assert op.num_ctrl_qubits == 2
    
    def test_negctrl_on_custom_gate_single_op(self):
        """Negated control applied to a custom gate with a single operation."""
        code = """
        OPENQASM 3.0;
        qubit[3] q;
        gate g1 q_arg { x q_arg; }
        negctrl(2) @ g1 q[2], q[0], q[1];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        assert len(qc.data) == 1
        op = qc.data[0].operation
        assert isinstance(op, ControlledGate)
        assert op.base_gate.name == 'x'
        assert op.num_ctrl_qubits == 2
        assert op.ctrl_state == 0  # 0b00 for two controls
    
    def test_ctrl_on_custom_gate_multiple_ops(self):
        """Control applied to a custom gate with multiple operations."""
        code = """
        OPENQASM 3.0;
        qubit[3] q;
        gate g1 q_arg { h q_arg; x q_arg; }
        ctrl(2) @ g1 q[2], q[0], q[1];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        assert len(qc.data) == 2
        op1 = qc.data[0].operation
        assert isinstance(op1, ControlledGate)
        assert op1.base_gate.name == 'h'
        assert op1.num_ctrl_qubits == 2
        op2 = qc.data[1].operation
        assert isinstance(op2, CCXGate)  # X.control(2) simplifies to CCX
    
    def test_negctrl_on_custom_gate_multiple_ops(self):
        """Negated control applied to a multi-op custom gate."""
        code = """
        OPENQASM 3.0;
        qubit[3] q;
        gate g1 q_arg { h q_arg; x q_arg; }
        negctrl(2) @ g1 q[2], q[0], q[1];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        assert len(qc.data) == 2
        op1 = qc.data[0].operation
        assert isinstance(op1, ControlledGate)
        assert op1.base_gate.name == 'h'
        assert op1.num_ctrl_qubits == 2
        assert op1.ctrl_state == 0
        op2 = qc.data[1].operation
        assert isinstance(op2, ControlledGate)
        assert op2.base_gate.name == 'x'
        assert op2.num_ctrl_qubits == 2
        assert op2.ctrl_state == 0
    
    def test_ctrl_on_x_is_simplified_to_cnot(self):
        """Tests that 'ctrl @ x' is simplified to a CNOT."""
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        ctrl @ x q[0], q[1];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        assert len(qc.data) == 1
        assert isinstance(qc.data[0].operation, CXGate)
    
    def test_not_enough_target_qubits_after_control_raises_error(self):
        """Tests error when controls leave too few qubits for the target gate."""
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        // CNOT needs 2 target qubits, but ctrl(1) leaves only 1.
        ctrl(1) @ cx q[0], q[1]; 
        """
        visitor = QiskitVisitor()
        with pytest.raises(ValueError, match=r"Invalid arguments for gate 'cx': qubits=1, params=0"):
            visitor.visit(parse_openqasm3(code))
            visitor.finalize()
    
    def test_inv_of_ctrl_on_builtin_gate(self):
        """Tests applying 'inv' to a controlled gate."""
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        inv @ ctrl @ h q[0], q[1];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        assert len(qc.data) == 1
        op = qc.data[0].operation
        assert isinstance(op, CHGate)  # Since H is self-inverse, CH inv = CH
    
    def test_pow_of_ctrl_on_builtin_gate(self):
        """Tests applying 'pow' to a controlled gate."""
        code = """
        OPENQASM 3.0;
        qubit[2] q;
        pow(3) @ ctrl @ h q[0], q[1];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # Repeats the controlled gate 3 times
        assert len(qc.data) == 3
        for i in range(3):
            assert isinstance(qc.data[i].operation, CHGate)


class TestBroadcasting:
    """Tests for quantum gate broadcasting functionality."""
    
    def test_broadcast_single_qubit_gate_over_register(self):
        """Tests broadcasting a single-qubit gate over a register."""
        code = """
        OPENQASM 3.0;
        qubit[3] q;
        h q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # Should apply h 3 times to q[0], q[1], q[2]
        h_ops = [instr for instr in qc.data if instr.operation.name == "h"]
        assert len(h_ops) == 3
        
        # Check that all qubits from q were targeted
        h_qubits = [qc.find_bit(instr.qubits[0]).index for instr in h_ops]
        assert sorted(h_qubits) == [0, 1, 2]
    
    def test_broadcast_two_qubit_gate_over_registers(self):
        """Tests broadcasting a two-qubit gate over two registers."""
        code = """
        OPENQASM 3.0;
        qubit[3] q;
        qubit[3] r;
        cx q, r;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # Should apply cx 3 times: cx q[0],r[0]; cx q[1],r[1]; cx q[2],r[2]
        cx_ops = [instr for instr in qc.data if instr.operation.name == "cx"]
        assert len(cx_ops) == 3
        
        # Check the control and target qubits
        for i, op in enumerate(cx_ops):
            control_idx = qc.find_bit(op.qubits[0]).index
            target_idx = qc.find_bit(op.qubits[1]).index
            assert control_idx == i  # q[0], q[1], q[2]
            assert target_idx == i + 3  # r[0], r[1], r[2]
    
    def test_broadcast_with_single_qubit_and_register(self):
        """Tests broadcasting where one operand is a single qubit."""
        code = """
        OPENQASM 3.0;
        qubit s;
        qubit[3] q;
        cx s, q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # Should apply cx 3 times with s as control: cx s,q[0]; cx s,q[1]; cx s,q[2]
        cx_ops = [instr for instr in qc.data if instr.operation.name == "cx"]
        assert len(cx_ops) == 3
        
        for op in cx_ops:
            control_idx = qc.find_bit(op.qubits[0]).index
            assert control_idx == 0  # Always 's'
    
    def test_broadcast_parametric_gate(self):
        """Tests broadcasting a parametric gate over registers."""
        code = """
        OPENQASM 3.0;
        qubit[3] q;
        rx(pi/4) q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # Should apply rx 3 times with same parameter
        rx_ops = [instr for instr in qc.data if instr.operation.name == "rx"]
        assert len(rx_ops) == 3
        
        for op in rx_ops:
            assert math.isclose(op.operation.params[0], math.pi / 4)
    
    def test_broadcast_custom_gate(self):
        """Tests broadcasting a custom gate over registers."""
        code = """
        OPENQASM 3.0;
        gate my_gate q { h q; x q; }
        qubit[3] q;
        my_gate q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # Should apply my_gate 3 times, each with h and x
        # So 6 operations total: h,x,h,x,h,x
        assert len(qc.data) == 6
        
        # Check pattern: h, x, h, x, h, x
        for i in range(3):
            assert qc.data[2*i].operation.name == "h"
            assert qc.data[2*i + 1].operation.name == "x"
    
    def test_broadcast_custom_parametric_gate(self):
        """Tests broadcasting a custom parametric gate."""
        code = """
        OPENQASM 3.0;
        gate my_rx(theta) q { rx(theta) q; }
        qubit[3] q;
        my_rx(pi/2) q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # Should apply my_rx 3 times
        rx_ops = [instr for instr in qc.data if instr.operation.name == "rx"]
        assert len(rx_ops) == 3
        
        for op in rx_ops:
            assert math.isclose(op.operation.params[0], math.pi / 2)
    
    def test_broadcast_three_qubit_gate(self):
        """Tests broadcasting a three-qubit gate."""
        code = """
        OPENQASM 3.0;
        qubit[2] a;
        qubit[2] b;
        qubit[2] c;
        cswap a, b, c;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # Should apply cswap 2 times: cswap a[0],b[0],c[0]; cswap a[1],b[1],c[1]
        cswap_ops = [instr for instr in qc.data if instr.operation.name == "cswap"]
        assert len(cswap_ops) == 2
    
    def test_broadcast_barrier_over_multiple_operands(self):
        """Tests that barrier applies to all qubits without broadcasting."""
        code = """
        OPENQASM 3.0;
        qubit[3] q;
        qubit s1;
        qubit s2;
        qubit[3] r;
        barrier q, s1, s2, r;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # Barrier should apply once to all specified qubits
        barrier_ops = [instr for instr in qc.data if instr.operation.name == "barrier"]
        assert len(barrier_ops) == 1
        
        # Should contain all 8 qubits
        assert len(barrier_ops[0].qubits) == 8
    
    def test_broadcast_error_mismatched_sizes(self):
        """Tests that broadcasting with mismatched register sizes raises an error."""
        code = """
        OPENQASM 3.0;
        qubit[3] q;
        qubit[2] r;
        cx q, r;
        """
        visitor = QiskitVisitor()
        with pytest.raises(ValueError, match="Broadcasting error: All quantum register operands must have the same size"):
            visitor.visit(parse_openqasm3(code))
    
    def test_broadcast_with_indexed_qubit(self):
        """Tests that indexed qubits don't trigger broadcasting."""
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        // This should NOT broadcast - it's a single cx on specific qubits
        cx q[0], q[1];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # Should be just 1 cx gate
        cx_ops = [instr for instr in qc.data if instr.operation.name == "cx"]
        assert len(cx_ops) == 1
    
    def test_broadcast_with_sliced_register(self):
        """Tests that sliced registers trigger broadcasting."""
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        qubit[5] r;
        // Slice creates registers of size 3, so broadcast 3 times
        cx q[1:3], r[1:3];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # Should broadcast 3 times over indices 1,2,3
        cx_ops = [instr for instr in qc.data if instr.operation.name == "cx"]
        assert len(cx_ops) == 3
        
        # Check that correct qubits were used
        for i, op in enumerate(cx_ops):
            control_idx = qc.find_bit(op.qubits[0]).index
            target_idx = qc.find_bit(op.qubits[1]).index
            assert control_idx == i + 1  # q[1], q[2], q[3]
            assert target_idx == i + 6  # r[1], r[2], r[3] (r starts at index 5)
    
    def test_broadcast_with_aliases(self):
        """Tests broadcasting with aliased registers."""
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        qubit[5] r;
        let q_alias = q[0:2];
        let r_alias = r[0:2];
        cx q_alias, r_alias;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # Should broadcast 3 times over the aliased ranges
        cx_ops = [instr for instr in qc.data if instr.operation.name == "cx"]
        assert len(cx_ops) == 3
    
    def test_broadcast_with_concatenated_register(self):
        """Tests broadcasting a gate over a concatenated register."""
        code = """
        OPENQASM 3.0;
        qubit[2] a;
        qubit[2] b;
        let ab = a ++ b;
        h ab;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # Should broadcast h 4 times over the concatenated register
        h_ops = [instr for instr in qc.data if instr.operation.name == "h"]
        assert len(h_ops) == 4
        
        # Check all 4 qubits were targeted
        h_qubits = sorted([qc.find_bit(instr.qubits[0]).index for instr in h_ops])
        assert h_qubits == [0, 1, 2, 3]
    
    def test_broadcast_with_modifiers(self):
        """Tests broadcasting with gate modifiers."""
        code = """
        OPENQASM 3.0;
        qubit[3] q;
        inv @ h q;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # Should broadcast inv @ h 3 times (h is self-inverse)
        h_ops = [instr for instr in qc.data if instr.operation.name == "h"]
        assert len(h_ops) == 3
    
    def test_broadcast_controlled_gate(self):
        """Tests broadcasting with control modifiers."""
        code = """
        OPENQASM 3.0;
        qubit[3] control;
        qubit[3] target;
        ctrl @ x control, target;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # Should broadcast cx 3 times
        cx_ops = [instr for instr in qc.data if instr.operation.name == "cx"]
        assert len(cx_ops) == 3
    
    def test_no_broadcast_with_all_indexed(self):
        """Tests that fully indexed operands don't broadcast."""
        code = """
        OPENQASM 3.0;
        qubit[5] q;
        qubit[5] r;
        // Both are indexed, so no broadcasting
        cx q[2], r[3];
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        cx_ops = [instr for instr in qc.data if instr.operation.name == "cx"]
        assert len(cx_ops) == 1
    
    def test_broadcast_swap_gate(self):
        """Tests broadcasting a SWAP gate."""
        code = """
        OPENQASM 3.0;
        qubit[3] q;
        qubit[3] r;
        swap q, r;
        """
        visitor = QiskitVisitor()
        visitor.visit(parse_openqasm3(code))
        qc = visitor.finalize()
        
        # Should broadcast swap 3 times
        swap_ops = [instr for instr in qc.data if instr.operation.name == "swap"]
        assert len(swap_ops) == 3
        
        for i, op in enumerate(swap_ops):
            qubit1_idx = qc.find_bit(op.qubits[0]).index
            qubit2_idx = qc.find_bit(op.qubits[1]).index
            assert qubit1_idx == i
            assert qubit2_idx == i + 3

if __name__ == "__main__":
    pytest.main([__file__])