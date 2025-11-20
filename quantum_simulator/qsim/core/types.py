from dataclasses import dataclass
from typing import Dict, Any, Optional
from pathlib import Path


@dataclass
class RunArgs:
    """Arguments for run_qasm orchestration."""
    qasm_input: str | Path  # QASM3 code or .qasm file path
    backend: str = 'cirq'  # e.g., 'cirq', 'qiskit', 'pennylane'
    shots: int = 1024  # 0 for exact statevector/probs


@dataclass
class SimResult:
    """Simulation output."""
    counts: Dict[str, int]  # e.g., {'00': 512, '11': 512}
    metadata: Dict[str, Any]  # e.g., {'n_qubits': 2, 'visitor': 'cirq'}
    probs: Optional[Dict[str, float]] = None  # For shots=0: {'00': 0.5, '11': 0.5}
    circuit: Any = None  # Framework circuit for vizualization