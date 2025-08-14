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