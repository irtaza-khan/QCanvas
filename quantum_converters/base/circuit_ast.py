"""
Circuit AST (Abstract Syntax Tree) Module

This module defines the intermediate representation for quantum circuits
parsed from various frameworks. It provides a unified AST structure that
can be converted to OpenQASM 3.0.

Author: QCanvas Team
Date: 2025-01-15
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
    qubit: int
    clbit: int
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
    qubits: Optional[List[int]] = None
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
    operations: List[Union[GateNode, MeasurementNode, ResetNode, BarrierNode]] = field(default_factory=list)
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
