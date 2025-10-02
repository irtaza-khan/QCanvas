"""
Qiskit to OpenQASM 3.0 Converter Module

This module provides functionality to convert Qiskit quantum circuits
to OpenQASM 3.0 format. It serves as an intermediate representation (IR)
converter for unified quantum simulators.

Key Features:
- Uses AST (Abstract Syntax Tree) parsing instead of dynamic execution (exec)
- AST parsing provides security by analyzing code structure without execution
- Avoids potential security risks associated with executing user-provided code
- Enables static analysis of quantum circuits for better reliability

Comparison with exec-based approach:
- exec: Executes code dynamically, potentially unsafe for untrusted input
- AST: Parses code structure safely, extracts operations without running code

Author: QCanvas Team
Date: 2025-09-30
Version: 2.0.0 - Integrated with QASM3Builder
"""

import inspect
from typing import Dict, Any, Optional, Union
from qiskit import QuantumCircuit
from quantum_converters.base.ConversionResult import ConversionResult, ConversionStats
from quantum_converters.base.qasm3_builder import QASM3Builder
from quantum_converters.base.qasm3_gates import QASM3GateLibrary, GateModifier
from quantum_converters.parsers.qiskit_parser import QiskitASTParser
from quantum_converters.base.circuit_ast import CircuitAST

class QiskitToQASM3Converter:
    """
    A converter class that transforms Qiskit quantum circuits to OpenQASM 3.0 format.

    This converter supports all standard Qiskit gates and circuit structures,
    leveraging Qiskit's native OpenQASM 3.0 export functionality.

    The converter expects source code that defines a function `get_circuit()`
    which returns a qiskit.QuantumCircuit object.
    """

    def __init__(self):
        """Initialize the Qiskit to QASM3 converter."""
        pass

    def _analyze_circuit_ast(self, circuit_ast: CircuitAST) -> ConversionStats:
        """
        Analyze a CircuitAST and extract statistics.

        Args:
            circuit_ast: Parsed circuit AST representation

        Returns:
            ConversionStats: Circuit analysis statistics
        """
        try:
            # Get basic circuit properties from AST
            n_qubits = circuit_ast.qubits
            n_clbits = circuit_ast.clbits

            # Calculate depth (simplified - doesn't account for parallelism)
            depth = circuit_ast.get_depth()

            # Get gate counts
            gate_counts = circuit_ast.get_gate_count()

            # Check for measurements
            has_measurements = circuit_ast.has_measurements()

            return ConversionStats(
                n_qubits=n_qubits,
                depth=depth,
                n_moments=depth,  # Simplified: depth equals moments for AST
                gate_counts=gate_counts,
                has_measurements=has_measurements
            )

        except Exception as e:
            # Return minimal stats if analysis fails
            return ConversionStats(
                n_qubits=0,
                depth=None,
                n_moments=None,
                gate_counts=None,
                has_measurements=False
            )

    def _convert_ast_to_qasm3(self, circuit_ast: CircuitAST) -> str:
        """
        Convert CircuitAST to OpenQASM 3.0 string using QASM3Builder.

        Args:
            circuit_ast: Parsed circuit AST representation

        Returns:
            str: OpenQASM 3.0 code representation

        Raises:
            RuntimeError: If conversion fails
        """
        try:
            # Initialize the QASM3 builder
            builder = QASM3Builder()

            # Get circuit dimensions
            num_qubits = circuit_ast.qubits
            num_clbits = circuit_ast.clbits

            # Build standard prelude
            builder.build_standard_prelude(
                num_qubits=num_qubits,
                num_clbits=num_clbits,
                include_vars=False,
                include_constants=False
            )

            # Add circuit parameters if any (from AST metadata)
            if circuit_ast.parameters:
                builder.add_section_comment("Circuit parameters")
                for param_name in circuit_ast.parameters:
                    builder.declare_variable(param_name, 'float')
                builder.add_blank_line()

            # Convert circuit operations
            builder.add_section_comment("Circuit operations")
            for operation in circuit_ast.operations:
                self._add_ast_operation(builder, operation)

            return builder.get_code()

        except Exception as e:
            raise RuntimeError(f"Failed to convert AST to QASM3: {str(e)}")

    def _add_ast_operation(self, builder: QASM3Builder, operation):
        """
        Add a CircuitAST operation to the QASM builder.

        Args:
            builder: QASM3Builder instance
            operation: CircuitAST operation (GateNode, MeasurementNode, etc.)
        """
        from quantum_converters.base.circuit_ast import GateNode, MeasurementNode, ResetNode, BarrierNode

        if isinstance(operation, GateNode):
            # Handle gate operations
            gate_name = operation.name
            qubits_str = [f"q[{i}]" for i in operation.qubits]

            # Apply modifiers if present
            modifiers = operation.modifiers if operation.modifiers else None

            # Handle different gate types
            if gate_name in ['h', 'x', 'y', 'z', 's', 't', 'sx', 'id', 'i']:
                builder.apply_gate(gate_name, qubits_str, modifiers=modifiers)
            elif gate_name in ['rx', 'ry', 'rz', 'p']:
                if operation.parameters:
                    param = builder.format_parameter(operation.parameters[0])
                    builder.apply_gate(gate_name, qubits_str, parameters=[param], modifiers=modifiers)
            elif gate_name == 'u':
                if len(operation.parameters) >= 3:
                    theta = builder.format_parameter(operation.parameters[0])
                    phi = builder.format_parameter(operation.parameters[1])
                    lam = builder.format_parameter(operation.parameters[2])
                    builder.apply_gate('u', qubits_str, parameters=[theta, phi, lam], modifiers=modifiers)
            elif gate_name in ['cx', 'cnot', 'cz', 'cy', 'ch', 'swap', 'cp', 'crx', 'cry', 'crz', 'ccx', 'ccz', 'cswap']:
                if operation.parameters:
                    param = builder.format_parameter(operation.parameters[0])
                    builder.apply_gate(gate_name, qubits_str, parameters=[param], modifiers=modifiers)
                else:
                    builder.apply_gate(gate_name, qubits_str, modifiers=modifiers)
            else:
                builder.add_comment(f"Unsupported gate: {gate_name}")

        elif isinstance(operation, MeasurementNode):
            # Handle measurement operations
            qubit_str = f"q[{operation.qubit}]"
            clbit_str = f"c[{operation.clbit}]"
            builder.add_measurement(qubit_str, clbit_str)

        elif isinstance(operation, ResetNode):
            # Handle reset operations
            qubit_str = f"q[{operation.qubit}]"
            builder.add_reset(qubit_str)

        elif isinstance(operation, BarrierNode):
            # Handle barrier operations
            if operation.qubits:
                qubits_str = [f"q[{i}]" for i in operation.qubits]
                builder.add_barrier(qubits_str)
            else:
                builder.add_barrier(None)  # All qubits

    def convert(self, qiskit_source: str) -> ConversionResult:
        """
        Convert Qiskit source code to OpenQASM 3.0 format using AST-based parsing.

        This method now uses AST parsing instead of dynamic execution for improved
        security and reliability. It parses the source code to extract circuit operations
        without executing potentially unsafe code.

        Args:
            qiskit_source (str): Complete Qiskit source code defining get_circuit() function

        Returns:
            ConversionResult: Object containing QASM code and conversion statistics

        Raises:
            ValueError: If source code is invalid or doesn't define required function
            ImportError: If Qiskit dependencies are missing
            RuntimeError: If conversion process fails

        Example:
            >>> converter = QiskitToQASM3Converter()
            >>> source = '''
            ... from qiskit import QuantumCircuit
            ... def get_circuit():
            ...     qc = QuantumCircuit(2, 2)
            ...     qc.h(0)
            ...     qc.cx(0, 1)
            ...     qc.measure([0, 1], [0, 1])
            ...     return qc
            ... '''
            >>> result = converter.convert(source)
            >>> print(f"Circuit has {result.stats.n_qubits} qubits and depth {result.stats.depth}")
        """
        # Parse source code using AST parser (secure, no execution)
        parser = QiskitASTParser()
        circuit_ast = parser.parse(qiskit_source)

        # Analyze the parsed circuit AST
        stats = self._analyze_circuit_ast(circuit_ast)

        # Convert AST to OpenQASM 3.0
        qasm3_program = self._convert_ast_to_qasm3(circuit_ast)

        return ConversionResult(qasm_code=qasm3_program, stats=stats)


# Public API function for easy module usage
def convert_qiskit_to_qasm3(qiskit_source: str) -> ConversionResult:
    """
    Convert Qiskit quantum circuit source code to OpenQASM 3.0 format.

    This is a convenience function that creates a converter instance and performs
    the conversion in a single call, returning a ConversionResult object.

    Args:
        qiskit_source (str): Complete Qiskit source code defining get_circuit() function

    Returns:
        ConversionResult: Object containing QASM code and conversion statistics

    Raises:
        ValueError: If source code is invalid or doesn't define required function
        ImportError: If Qiskit dependencies are missing
        RuntimeError: If conversion process fails

    Example:
        >>> from qiskit_qasm_converter import convert_qiskit_to_qasm3
        >>> source = '''
        ... from qiskit import QuantumCircuit
        ... def get_circuit():
        ...     qc = QuantumCircuit(2, 2)
        ...     qc.h(0)
        ...     qc.cx(0, 1)
        ...     qc.measure([0, 1], [0, 1])
        ...     return qc
        ... '''
        >>> result = convert_qiskit_to_qasm3(source)
        >>> print(result.qasm_code)
    """
    converter = QiskitToQASM3Converter()
    return converter.convert(qiskit_source)
