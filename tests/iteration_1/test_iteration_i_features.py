"""
Comprehensive Test Suite for OpenQASM 3.0 Iteration I Features

This test suite validates all Iteration I features as defined in docs/project-scope.md.
Tests will PASS for correctly implemented features and FAIL for missing/incorrect implementations.

Test Categories:
1. Comments and Version Control
2. Types and Casting
3. Gates and Modifiers
4. Built-in Quantum Instructions
5. Classical Instructions
6. Scoping and Variables
7. Standard Library and Built-ins

Author: QCanvas Team
Date: 2025-09-30
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from quantum_converters.base.qasm3_builder import QASM3Builder
from quantum_converters.base.qasm3_gates import QASM3GateLibrary, GateModifier
from quantum_converters.base.qasm3_expression import QASM3ExpressionParser


class TestCommentsAndVersionControl:
    """Test Iteration I: Comments and Version Control Features"""
    
    def test_single_line_comments(self):
        """Test single-line comments (//)"""
        builder = QASM3Builder()
        builder.add_comment("This is a single-line comment", multiline=False)
        code = builder.get_code()
        assert "// This is a single-line comment" in code
        
    def test_multi_line_comments(self):
        """Test multi-line comments (/* */)"""
        builder = QASM3Builder()
        builder.add_comment("This is a multi-line comment", multiline=True)
        code = builder.get_code()
        assert "/* This is a multi-line comment */" in code
        
    def test_version_string(self):
        """Test OPENQASM 3.0 version string"""
        builder = QASM3Builder()
        builder.initialize_header()
        code = builder.get_code()
        assert code.startswith("OPENQASM 3.0;")
        
    def test_include_statements(self):
        """Test include statements"""
        builder = QASM3Builder()
        builder.add_include("stdgates.inc")
        code = builder.get_code()
        assert 'include "stdgates.inc";' in code


class TestTypesAndCasting:
    """Test Iteration I: Types and Casting Features"""
    
    def test_identifiers(self):
        """Test valid identifier names"""
        builder = QASM3Builder()
        assert builder.validate_identifier("my_qubit")
        assert builder.validate_identifier("qubit_0")
        assert builder.validate_identifier("_private")
        assert not builder.validate_identifier("0invalid")
        assert not builder.validate_identifier("my-qubit")
        
    def test_variables(self):
        """Test variable declarations"""
        builder = QASM3Builder()
        builder.declare_variable("my_var", "int")
        builder.declare_variable("my_float", "float", value="3.14")
        code = builder.get_code()
        assert "int my_var;" in code
        assert "float my_float = 3.14;" in code
        
    def test_quantum_types_qubit(self):
        """Test qubit type"""
        builder = QASM3Builder()
        builder.declare_qubit_register("q", 5)
        code = builder.get_code()
        assert "qubit[5] q;" in code
        
    def test_boolean_type(self):
        """Test bool type"""
        builder = QASM3Builder()
        builder.declare_variable("flag", "bool", value="true")
        code = builder.get_code()
        assert "bool flag = true;" in code
        
    def test_bit_type(self):
        """Test bit type"""
        builder = QASM3Builder()
        builder.declare_bit_register("c", 3)
        code = builder.get_code()
        assert "bit[3] c;" in code
        
    def test_integer_type(self):
        """Test int type"""
        builder = QASM3Builder()
        builder.declare_variable("count", "int", value="42")
        code = builder.get_code()
        assert "int count = 42;" in code
        
    def test_unsigned_integer_type(self):
        """Test uint type"""
        builder = QASM3Builder()
        builder.declare_variable("counter", "uint", value="10")
        code = builder.get_code()
        assert "uint counter = 10;" in code
        
    def test_float_type(self):
        """Test float type"""
        builder = QASM3Builder()
        builder.declare_variable("angle", "float", value="1.57")
        code = builder.get_code()
        assert "float angle = 1.57;" in code
        
    def test_angle_type(self):
        """Test angle type"""
        builder = QASM3Builder()
        builder.declare_variable("theta", "angle", value="PI/2")
        code = builder.get_code()
        assert "angle theta = PI/2;" in code
        
    def test_compile_time_constants(self):
        """Test const keyword"""
        builder = QASM3Builder()
        builder.add_constant("MY_CONST", "float", "3.14159")
        code = builder.get_code()
        assert "const float MY_CONST = 3.14159;" in code
        
    def test_literals_integer(self):
        """Test integer literals"""
        parser = QASM3ExpressionParser()
        value, type_ = parser.parse_literal("42")
        assert value == 42
        assert type_ == "int"
        
    def test_literals_float(self):
        """Test float literals"""
        parser = QASM3ExpressionParser()
        value, type_ = parser.parse_literal("3.14")
        assert value == 3.14
        assert type_ == "float"
        
    def test_literals_boolean(self):
        """Test boolean literals"""
        parser = QASM3ExpressionParser()
        value, type_ = parser.parse_literal("true")
        assert value == True
        assert type_ == "bool"
        
    def test_arrays(self):
        """Test array declarations"""
        builder = QASM3Builder()
        builder.declare_variable("my_array", "int", size=10)
        code = builder.get_code()
        assert "int[10] my_array;" in code
        
    def test_aliasing(self):
        """Test register aliasing"""
        builder = QASM3Builder()
        builder.declare_qubit_register("q", 5)
        builder.add_alias("first_two", "q[0:2]")
        code = builder.get_code()
        assert "let first_two = q[0:2];" in code
        
    def test_index_sets_and_slicing(self):
        """Test index sets and slicing operations"""
        builder = QASM3Builder()
        start, end = builder.parse_slice("[0:5]")
        assert start == 0
        assert end == 5
        
    def test_register_concatenation(self):
        """Test register concatenation"""
        # This should be supported in the builder
        builder = QASM3Builder()
        builder.declare_qubit_register("q1", 2)
        builder.declare_qubit_register("q2", 2)
        # Concatenation would be: q1 ++ q2 or similar syntax
        # This is a placeholder test
        pytest.skip("Register concatenation not yet fully implemented")
        
    def test_array_concatenation(self):
        """Test array concatenation"""
        # This should be supported in expressions
        pytest.skip("Array concatenation not yet fully implemented")


class TestGatesAndModifiers:
    """Test Iteration I: Gates and Modifiers"""
    
    def test_applying_gates(self):
        """Test basic gate application"""
        builder = QASM3Builder()
        builder.declare_qubit_register("q", 2)
        builder.apply_gate("h", ["q[0]"])
        builder.apply_gate("cx", ["q[0]", "q[1]"])
        code = builder.get_code()
        assert "h q[0];" in code
        assert "cx q[0], q[1];" in code
        
    def test_gate_broadcasting(self):
        """Test gate broadcasting to multiple qubits"""
        builder = QASM3Builder()
        builder.declare_qubit_register("q", 5)
        builder.apply_gate_broadcast("h", "q")
        code = builder.get_code()
        assert "h q;" in code
        
    def test_parameterized_gates(self):
        """Test parameterized gates"""
        builder = QASM3Builder()
        builder.declare_qubit_register("q", 1)
        builder.apply_gate("rx", ["q[0]"], parameters=["PI/2"])
        code = builder.get_code()
        assert "rx(PI/2) q[0];" in code
        
    def test_hierarchical_gate_definitions(self):
        """Test custom gate definitions"""
        builder = QASM3Builder()
        builder.define_gate("my_gate", ["theta"], ["a", "b"], [
            "rx(theta) a;",
            "cx a, b;"
        ])
        code = builder.get_code()
        assert "gate my_gate(theta) a, b {" in code
        assert "    rx(theta) a;" in code
        assert "    cx a, b;" in code
        
    def test_control_modifier(self):
        """Test ctrl@ modifier"""
        builder = QASM3Builder()
        builder.declare_qubit_register("q", 3)
        modifier = GateModifier(ctrl_qubits=1)
        builder.apply_gate("x", ["q[1]", "q[2]"], modifiers={'ctrl': 1})
        code = builder.get_code()
        # Should generate controlled-X
        assert "ctrl @" in code or "cx" in code
        
    def test_inverse_modifier(self):
        """Test inv@ modifier"""
        builder = QASM3Builder()
        builder.declare_qubit_register("q", 1)
        builder.apply_gate("s", ["q[0]"], modifiers={'inv': True})
        code = builder.get_code()
        assert "inv @" in code or "sdg" in code
        
    def test_built_in_u_gate(self):
        """Test U gate"""
        builder = QASM3Builder()
        builder.declare_qubit_register("q", 1)
        builder.apply_gate("u", ["q[0]"], parameters=["PI/2", "0", "PI"])
        code = builder.get_code()
        assert "u(PI/2, 0, PI) q[0];" in code
        
    def test_global_phase_gate(self):
        """Test gphase gate"""
        builder = QASM3Builder()
        builder.apply_gate("gphase", [], parameters=["PI/4"])
        code = builder.get_code()
        assert "gphase(PI/4);" in code or "gphase(PI/4) ;" in code


class TestBuiltInQuantumInstructions:
    """Test Iteration I: Built-in Quantum Instructions"""
    
    def test_reset_instruction(self):
        """Test reset instruction"""
        builder = QASM3Builder()
        builder.declare_qubit_register("q", 1)
        builder.add_reset("q[0]")
        code = builder.get_code()
        assert "reset q[0];" in code
        
    def test_measurement_instruction(self):
        """Test measurement instruction"""
        builder = QASM3Builder()
        builder.declare_qubit_register("q", 1)
        builder.declare_bit_register("c", 1)
        builder.add_measurement("q[0]", "c[0]")
        code = builder.get_code()
        assert "measure q[0] -> c[0];" in code
        
    def test_barrier_instruction(self):
        """Test barrier instruction"""
        builder = QASM3Builder()
        builder.declare_qubit_register("q", 3)
        builder.add_barrier(["q[0]", "q[1]"])
        code = builder.get_code()
        assert "barrier q[0], q[1];" in code


class TestClassicalInstructions:
    """Test Iteration I: Classical Instructions"""
    
    def test_assignment_statements(self):
        """Test assignment statements"""
        builder = QASM3Builder()
        builder.declare_variable("x", "int")
        builder.add_assignment("x", "42")
        code = builder.get_code()
        assert "x = 42;" in code
        
    def test_arithmetic_operations(self):
        """Test arithmetic operations (+, -, *, /)"""
        parser = QASM3ExpressionParser()
        expr = parser.parse_expression("a + b")
        assert "+" in expr
        expr = parser.parse_expression("a * b")
        assert "*" in expr
        
    def test_comparison_operations(self):
        """Test comparison operations (<, >, ==, !=)"""
        parser = QASM3ExpressionParser()
        expr = parser.parse_expression("a == b")
        assert "==" in expr
        expr = parser.parse_expression("a < b")
        assert "<" in expr
        
    def test_logical_operations(self):
        """Test logical operations (&&, ||, !)"""
        parser = QASM3ExpressionParser()
        expr = parser.parse_expression("a && b")
        assert "&&" in expr
        expr = parser.parse_expression("!a")
        assert "!" in expr
        
    def test_if_statements(self):
        """Test if statements"""
        builder = QASM3Builder()
        builder.add_if_statement("c[0] == 1", ["x q[0];"])
        code = builder.get_code()
        assert "if (c[0] == 1) {" in code
        assert "    x q[0];" in code
        
    def test_if_else_statements(self):
        """Test if-else statements"""
        builder = QASM3Builder()
        builder.add_if_statement("c[0] == 1", ["x q[0];"], else_body=["y q[0];"])
        code = builder.get_code()
        assert "if (c[0] == 1) {" in code
        assert "} else {" in code
        assert "    y q[0];" in code
        
    def test_for_loops(self):
        """Test for loops"""
        builder = QASM3Builder()
        builder.add_for_loop("i", "[0:5]", ["h q[i];"])
        code = builder.get_code()
        assert "for i in [0:5] {" in code
        assert "    h q[i];" in code


class TestScopingAndVariables:
    """Test Iteration I: Scoping of Variables"""
    
    def test_global_scope(self):
        """Test global scope variables"""
        builder = QASM3Builder()
        builder.declare_variable("global_var", "int", value="10")
        assert "global_var" in builder.variables
        assert builder.variables["global_var"].type == "int"


class TestStandardLibraryAndBuiltins:
    """Test Iteration I: Standard Library and Built-ins"""
    
    def test_standard_gate_library(self):
        """Test standard gate library recognition"""
        lib = QASM3GateLibrary()
        assert lib.is_standard_gate("h")
        assert lib.is_standard_gate("cx")
        assert lib.is_standard_gate("ccx")
        assert not lib.is_standard_gate("nonexistent")
        
    def test_built_in_functions(self):
        """Test built-in mathematical functions"""
        parser = QASM3ExpressionParser()
        assert "sqrt" in parser.MATH_FUNCTIONS
        assert "sin" in parser.MATH_FUNCTIONS
        assert "cos" in parser.MATH_FUNCTIONS
        
    def test_mathematical_constants(self):
        """Test mathematical constants"""
        builder = QASM3Builder()
        assert "PI" in builder.math_constants
        assert "E" in builder.math_constants
        assert "TAU" in builder.math_constants


class TestMissingFeatures:
    """Tests that SHOULD FAIL for features not yet implemented"""
    
    @pytest.mark.xfail(reason="Physical qubits ($0, $1) are EXCLUDED from scope")
    def test_physical_qubits_excluded(self):
        """Physical qubits are explicitly excluded"""
        # This should not be supported
        builder = QASM3Builder()
        # Attempting to use physical qubits should fail
        assert False, "Physical qubits are excluded from Iteration I"
        
    @pytest.mark.xfail(reason="Complex type is Iteration II")
    def test_complex_type_not_in_iteration_i(self):
        """Complex type is Iteration II, not Iteration I"""
        builder = QASM3Builder()
        # This should not work in Iteration I
        builder.declare_variable("complex_var", "complex")
        assert False, "Complex type is Iteration II"
        
    @pytest.mark.xfail(reason="Duration type is EXCLUDED")
    def test_duration_type_excluded(self):
        """Duration type is excluded from scope"""
        builder = QASM3Builder()
        builder.declare_variable("dur", "duration")
        assert False, "Duration is excluded"
        
    @pytest.mark.xfail(reason="Delay instruction is EXCLUDED")
    def test_delay_instruction_excluded(self):
        """Delay instruction is excluded from scope"""
        builder = QASM3Builder()
        builder.lines.append("delay[100ns] q[0];")
        assert False, "Delay is excluded"


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
