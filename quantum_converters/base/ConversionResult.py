"""
Conversion Result Data Classes

WHAT THIS FILE DOES:
    Defines data structures for conversion results and statistics. Provides containers
    for OpenQASM 3.0 code output and metadata about the converted circuit (qubit count,
    depth, gate counts, etc.). These are the standard return types for all converters.

HOW IT LINKS TO OTHER FILES:
    - Used by: All converter classes (qiskit_to_qasm.py, cirq_to_qasm.py, pennylane_to_qasm.py)
               return ConversionResult instances
    - Imported by: abstract_converter.py (defines return type for convert() method)
    - Used by: API endpoints that return conversion results to frontend
    - Part of: Base module providing core data structures

INPUT:
    - qasm_code (str): Generated OpenQASM 3.0 code string
    - stats (ConversionStats): Statistics about the converted circuit
    - Used in: ConversionResult constructor

OUTPUT:
    - ConversionResult: Complete conversion result with code and statistics
    - ConversionStats: Circuit metadata (qubits, depth, gate counts, measurements)
    - Returned by: All converter.convert() methods

STAGE OF USE:
    - Conversion Stage: Created after successful circuit conversion
    - Analysis Stage: Statistics computed during AST analysis
    - Response Stage: Returned to API endpoints and frontend
    - Used throughout: End-to-end conversion pipeline

TOOLS USED:
    - dataclasses.dataclass: Python dataclass for structured data
    - typing.Dict, Optional: Type hints for statistics dictionary
    - Built-in print: For formatted statistics display (print_stats method)

ARCHITECTURE ROLE:
    Provides the standardized output format for the entire conversion system,
    ensuring consistency across all framework converters and enabling unified
    result handling in the API layer.

Author: QCanvas Team
Date: 2025-08-02
Version: 1.0.0
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class ConversionStats:
    """Statistics about the converted circuit."""
    n_qubits: int
    depth: Optional[int] = None
    n_moments: Optional[int] = None
    gate_counts: Optional[Dict[str, int]] = None
    has_measurements: bool = False

@dataclass
class ConversionResult:
    """Container for conversion results including QASM code and statistics."""
    qasm_code: str
    stats: ConversionStats

    def print_stats(self):
        """Print the conversion statistics in a formatted way."""
        print("\nCircuit Statistics:")
        print(f"  - Qubits: {self.stats.n_qubits}")
        print(f"  - Depth: {self.stats.depth}")
        print(f"  - Number of moments: {self.stats.n_moments}")
        print(f"  - Has measurements: {self.stats.has_measurements}")
        print(f"  - Gate counts: {self.stats.gate_counts}")