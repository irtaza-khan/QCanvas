"""
Circuit AST (Abstract Syntax Tree) Module

WHAT THIS FILE DOES:
    Defines the unified intermediate representation (IR) for quantum circuits parsed
    from various frameworks. Provides dataclasses for circuit operations (gates,
    measurements, resets, barriers) and the main CircuitAST container. This AST serves
    as a framework-agnostic representation that can be converted to OpenQASM 3.0.

HOW IT LINKS TO OTHER FILES:
    - Used by: All parser classes (qiskit_parser.py, cirq_parser.py, pennylane_parser.py)
               build CircuitAST instances from source code
    - Used by: All converter classes use CircuitAST as intermediate representation
    - Imported by: qasm3_builder.py (converts AST to OpenQASM 3.0 code)
    - Part of: Base module providing core data structures

INPUT:
    - Framework-specific source code (via parsers)
    - Circuit operations extracted from AST parsing
    - Used in: Parser classes build CircuitAST from parsed operations

OUTPUT:
    - CircuitAST: Complete circuit representation with operations list
    - GateNode, MeasurementNode, ResetNode, BarrierNode: Individual operation nodes
    - Statistics: Gate counts, depth, measurement detection (via helper methods)
    - Returned by: Parser.parse() methods

STAGE OF USE:
    - Parsing Stage: Built by AST parsers from source code
    - Analysis Stage: Analyzed for statistics and validation
    - Conversion Stage: Converted to OpenQASM 3.0 by QASM3Builder
    - Used throughout: Core intermediate representation in conversion pipeline

TOOLS USED:
    - dataclasses.dataclass: Python dataclasses for operation nodes
    - typing.List, Dict, Optional, Union: Type hints for operation lists and metadata
    - Built-in methods: get_gate_count(), get_depth(), has_measurements() for analysis

ARCHITECTURE ROLE:
    Provides the unified intermediate representation that bridges framework-specific
    parsers and OpenQASM 3.0 generation. This abstraction enables framework-agnostic
    circuit processing and conversion logic.

Author: QCanvas Team
Date: 2025-08-03
Version: 1.0.0
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field


@dataclass
class GateNode:
    """
    Represents a quantum gate operation in the circuit AST.

    Attributes:
        name: Gate name (e.g., 'h', 'cx', 'rx')
        qubits: List of qubit indices this gate operates on
        parameters: List of gate parameters (for parameterized gates)
        modifiers: Dict of gate modifiers (e.g., {'inv': True} for inverse)
        metadata: Additional gate metadata
    """
    name: str
    qubits: List[int] = field(default_factory=list)
    parameters: List[Union[float, str]] = field(default_factory=list)
    modifiers: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MeasurementNode:
    """
    Represents a measurement operation in the circuit AST.

    Attributes:
        qubit: Qubit index being measured
        clbit: Classical bit index storing the result
        metadata: Additional measurement metadata
    """
    qubit: Union[int, str]
    clbit: Union[int, str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResetNode:
    """
    Represents a qubit reset operation in the circuit AST.

    Attributes:
        qubit: Qubit index being reset
        metadata: Additional reset metadata
    """
    qubit: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BarrierNode:
    """
    Represents a barrier operation in the circuit AST.

    Attributes:
        qubits: List of qubit indices for the barrier (None for all qubits)
        metadata: Additional barrier metadata
    """
    qubits: Optional[List[Union[int, str]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ForLoopNode:
    """
    Represents a for loop in the circuit AST.

    Attributes:
        variable: Loop variable name (e.g., 'i')
        range_start: Start of range (inclusive)
        range_end: End of range (exclusive, for Python-style range)
        body: List of operations inside the loop body
        metadata: Additional loop metadata
    """
    variable: str
    range_start: int
    range_end: int
    body: List[Union[GateNode, MeasurementNode, ResetNode, BarrierNode, 'ForLoopNode', 'IfStatementNode']] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IfStatementNode:
    """
    Represents an if statement in the circuit AST.

    Attributes:
        condition: Condition expression (as string representation)
        body: List of operations in the if block
        else_body: Optional list of operations in the else block
        metadata: Additional if statement metadata
    """
    condition: str
    body: List[Union[GateNode, MeasurementNode, ResetNode, BarrierNode, 'ForLoopNode', 'IfStatementNode']] = field(default_factory=list)
    else_body: Optional[List[Union[GateNode, MeasurementNode, ResetNode, BarrierNode, 'ForLoopNode', 'IfStatementNode']]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CircuitAST:
    """
    Abstract Syntax Tree representation of a quantum circuit.

    This unified representation can be built from various quantum frameworks
    and converted to OpenQASM 3.0.

    Attributes:
        qubits: Number of qubits in the circuit
        clbits: Number of classical bits in the circuit
        operations: List of circuit operations (gates, measurements, etc.)
        parameters: Dict of circuit parameters
        metadata: Additional circuit metadata
    """
    qubits: int = 0
    clbits: int = 0
    operations: List[Union[GateNode, MeasurementNode, ResetNode, BarrierNode, 'ForLoopNode', 'IfStatementNode']] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_gate(self, gate: GateNode) -> None:
        """Add a gate operation to the circuit."""
        self.operations.append(gate)

    def add_measurement(self, measurement: MeasurementNode) -> None:
        """Add a measurement operation to the circuit."""
        self.operations.append(measurement)

    def add_reset(self, reset: ResetNode) -> None:
        """Add a reset operation to the circuit."""
        self.operations.append(reset)

    def add_barrier(self, barrier: BarrierNode) -> None:
        """Add a barrier operation to the circuit."""
        self.operations.append(barrier)

    def add_for_loop(self, for_loop: 'ForLoopNode') -> None:
        """Add a for loop to the circuit."""
        self.operations.append(for_loop)

    def add_if_statement(self, if_stmt: 'IfStatementNode') -> None:
        """Add an if statement to the circuit."""
        self.operations.append(if_stmt)

    def get_gate_count(self) -> Dict[str, int]:
        """Get count of each gate type in the circuit."""
        counts = {}
        for op in self.operations:
            if isinstance(op, GateNode):
                counts[op.name] = counts.get(op.name, 0) + 1
        return counts

    def get_depth(self) -> int:
        """Calculate circuit depth (simplified - doesn't account for parallelism)."""
        return len([op for op in self.operations if isinstance(op, GateNode)])

    def has_measurements(self) -> bool:
        """Check if circuit contains measurement operations."""
        return any(isinstance(op, MeasurementNode) for op in self.operations)

    def __str__(self) -> str:
        """String representation of the circuit AST."""
        lines = [f"CircuitAST(qubits={self.qubits}, clbits={self.clbits})"]
        for i, op in enumerate(self.operations):
            lines.append(f"  {i}: {op}")
        return "\n".join(lines)
