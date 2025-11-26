"""
QSim wrapper module for hybrid execution.

This module provides a clean interface to QSim that can be imported
in user code as `import qsim`.

Usage:
    import qsim
    result = qsim.run(qasm_code, shots=1024, backend="cirq")
    print(result.counts)
"""

import sys
import os
from typing import Optional, Dict, Any

# Add project root to path for imports
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from .result import SimulationResult

# Import actual QSim
try:
    from qsim import run_qasm as _qsim_run, RunArgs as _RunArgs, SimResult as _SimResult
    QSIM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: QSim not available: {e}")
    QSIM_AVAILABLE = False
    _qsim_run = None
    _RunArgs = None
    _SimResult = None


# Track simulation runs for result collection
_simulation_results: list = []


def get_simulation_results() -> list:
    """Get all simulation results from this execution."""
    return _simulation_results.copy()


def clear_simulation_results() -> None:
    """Clear stored simulation results."""
    global _simulation_results
    _simulation_results = []


def run(
    qasm_code: str,
    shots: int = 1024,
    backend: str = "cirq"
) -> SimulationResult:
    """
    Execute OpenQASM 3.0 code using QSim.
    
    Args:
        qasm_code: OpenQASM 3.0 code to execute
        shots: Number of measurement shots (default: 1024)
        backend: Simulation backend to use (default: "cirq")
            Options: "cirq", "qiskit", "pennylane"
    
    Returns:
        SimulationResult with counts, probabilities, and metadata
        
    Raises:
        RuntimeError: If QSim is not available or execution fails
        
    Example:
        >>> qasm = '''
        ... OPENQASM 3.0;
        ... include "stdgates.inc";
        ... qubit[2] q;
        ... h q[0];
        ... cx q[0], q[1];
        ... bit[2] c;
        ... c = measure q;
        ... '''
        >>> result = qsim.run(qasm, shots=1000, backend="cirq")
        >>> print(result.counts)
        {'00': 498, '11': 502}
    """
    global _simulation_results
    
    if not QSIM_AVAILABLE:
        raise RuntimeError(
            "QSim is not available. Please ensure qsim package is installed."
        )
    
    # Validate backend
    valid_backends = ['cirq', 'qiskit', 'pennylane']
    if backend not in valid_backends:
        raise ValueError(
            f"Invalid backend: '{backend}'. "
            f"Valid options: {', '.join(valid_backends)}"
        )
    
    # Validate shots
    if shots < 0:
        raise ValueError(f"Shots must be non-negative, got: {shots}")
    
    try:
        # Create run arguments
        args = _RunArgs(
            qasm_input=qasm_code,
            backend=backend,
            shots=shots
        )
        
        # Execute with QSim
        sim_result: _SimResult = _qsim_run(args)
        
        # Convert to our SimulationResult format
        metadata = sim_result.metadata or {}
        
        # Calculate probabilities from counts
        total_counts = sum(sim_result.counts.values()) if sim_result.counts else 0
        probabilities = {}
        if total_counts > 0:
            for state, count in sim_result.counts.items():
                probabilities[state] = count / total_counts
        elif sim_result.probs:
            probabilities = dict(sim_result.probs)
        
        result = SimulationResult(
            counts=dict(sim_result.counts) if sim_result.counts else {},
            probabilities=probabilities,
            statevector=None,  # Not always available
            shots=shots,
            backend=backend,
            execution_time=metadata.get('execution_time', ''),
            simulation_time=metadata.get('simulation_time', ''),
            memory_usage=metadata.get('memory_usage', ''),
            cpu_usage=metadata.get('cpu_usage', ''),
            fidelity=metadata.get('fidelity', 100.0),
            n_qubits=metadata.get('n_qubits', 0),
            metadata=metadata,
        )
        
        # Store result for collection
        _simulation_results.append(result.to_dict())
        
        return result
        
    except Exception as e:
        raise RuntimeError(f"QSim execution failed: {str(e)}") from e


def run_batch(
    qasm_codes: list,
    shots: int = 1024,
    backend: str = "cirq"
) -> list:
    """
    Execute multiple QASM codes in batch.
    
    Args:
        qasm_codes: List of OpenQASM 3.0 code strings
        shots: Number of measurement shots (default: 1024)
        backend: Simulation backend to use (default: "cirq")
    
    Returns:
        List of SimulationResult objects
    """
    results = []
    for qasm in qasm_codes:
        result = run(qasm, shots=shots, backend=backend)
        results.append(result)
    return results


# Aliases for convenience
execute = run
simulate = run

