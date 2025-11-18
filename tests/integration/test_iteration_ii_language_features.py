"""
Integration Tests for Iteration II Language Features

Tests Iteration II language features including:
- Complex type
- While loops, break, continue
- Bitwise and shift operators
- Subroutines/functions

Author: QCanvas Team
Date: 2025-11-18
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from quantum_converters.base.qasm3_builder import QASM3Builder
from quantum_converters.base.qasm3_expression import QASM3ExpressionParser


class TestIterationIILanguageFeatures:
    """Test Iteration II language features"""
    
    def test_complex_type(self):
        """Test complex type support"""
        builder = QASM3Builder()
        builder.initialize_header()
        builder.declare_variable("c", "complex")
        
        code = builder.get_code()
        assert "complex c;" in code
        
    def test_while_loop(self):
        """Test while loop"""
        builder = QASM3Builder()
        builder.initialize_header()
        builder.declare_variable("counter", "int")
        
        builder.add_while_loop("counter < 10", [
            "counter = counter + 1;",
            "h q[0];"
        ])
        
        code = builder.get_code()
        assert "while (counter < 10) {" in code
        assert "counter = counter + 1;" in code
        
    def test_break_statement(self):
        """Test break statement"""
        builder = QASM3Builder()
        builder.initialize_header()
        
        builder.add_while_loop("true", [
            "h q[0];",
            "break;"
        ])
        
        code = builder.get_code()
        assert "break;" in code
        
    def test_continue_statement(self):
        """Test continue statement"""
        builder = QASM3Builder()
        builder.initialize_header()
        
        builder.add_for_loop("i", "[0:10]", [
            "if (i == 5) { continue; }"
        ])
        
        code = builder.get_code()
        assert "continue;" in code
        
    def test_bitwise_and_operator(self):
        """Test bitwise AND operator"""
        parser = QASM3ExpressionParser()
        expr = parser.parse_expression("a & b")
        assert "&" in expr
        
    def test_bitwise_or_operator(self):
        """Test bitwise OR operator"""
        parser = QASM3ExpressionParser()
        expr = parser.parse_expression("a | b")
        assert "|" in expr
        
    def test_bitwise_xor_operator(self):
        """Test bitwise XOR operator"""
        parser = QASM3ExpressionParser()
        expr = parser.parse_expression("a ^ b")
        assert "^" in expr
        
    def test_bitwise_not_operator(self):
        """Test bitwise NOT operator"""
        parser = QASM3ExpressionParser()
        expr = parser.parse_expression("~a")
        assert "~" in expr
        
    def test_shift_left_operator(self):
        """Test shift left operator"""
        parser = QASM3ExpressionParser()
        expr = parser.parse_expression("a << 2")
        assert "<<" in expr
        
    def test_shift_right_operator(self):
        """Test shift right operator"""
        parser = QASM3ExpressionParser()
        expr = parser.parse_expression("a >> 3")
        assert ">>" in expr
        
    def test_subroutine_definition(self):
        """Test subroutine/function definition"""
        builder = QASM3Builder()
        builder.initialize_header()
        
        builder.define_subroutine(
            "compute",
            ["int x", "int y"],
            "int",
            [
                "int result = x + y;",
                "return result;"
            ]
        )
        
        code = builder.get_code()
        assert "def compute(int x, int y) -> int {" in code
        assert "return result;" in code
        
    def test_void_subroutine(self):
        """Test void subroutine (no return type)"""
        builder = QASM3Builder()
        builder.initialize_header()
        
        builder.define_subroutine(
            "prepare_state",
            ["qubit q"],
            None,  # void function
            [
                "h q;",
                "s q;"
            ]
        )
        
        code = builder.get_code()
        assert "def prepare_state(qubit q) {" in code
        assert " -> " not in code.split("def prepare_state")[1].split("{")[0]
        
    def test_return_statement(self):
        """Test return statement"""
        builder = QASM3Builder()
        builder.initialize_header()
        builder.add_return_statement("42")
        
        code = builder.get_code()
        assert "return 42;" in code
        
    def test_void_return(self):
        """Test void return statement"""
        builder = QASM3Builder()
        builder.initialize_header()
        builder.add_return_statement()
        
        code = builder.get_code()
        assert "return;" in code
        
    def test_combined_iteration_ii_features(self):
        """Test multiple Iteration II features together"""
        builder = QASM3Builder()
        builder.initialize_header()
        builder.declare_qubit_register("q", 2)
        
        # Complex variable
        builder.declare_variable("amplitude", "complex")
        
        # Subroutine with while loop
        builder.define_subroutine(
            "iterate",
            ["int max_iter"],
            "int",
            [
                "int i = 0;",
                "while (i < max_iter) {",
                "    if (i & 1) {  // Bitwise AND",
                "        continue;",
                "    }",
                "    i = i << 1;  // Shift left",
                "    if (i > 100) {",
                "        break;",
                "    }",
                "}",
                "return i;"
            ]
        )
        
        code = builder.get_code()
        # Check all features are present
        assert "complex amplitude;" in code
        assert "def iterate(int max_iter) -> int {" in code
        assert "while (i < max_iter) {" in code
        assert "i & 1" in code
        assert "i << 1" in code
        assert "continue;" in code
        assert "break;" in code
        assert "return i;" in code


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

