"""
Result classes for hybrid execution.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


@dataclass
class SimulationResult:
    """
    Result from a quantum simulation (qsim.run()).
    
    Provides Pythonic access to all simulation statistics and results.
    
    Attributes:
        counts: Measurement counts, e.g., {'00': 512, '11': 512}
        probabilities: State probabilities, e.g., {'00': 0.5, '11': 0.5}
        statevector: Optional statevector for shots=0
        shots: Number of shots executed
        backend: Backend used (cirq, qiskit, pennylane)
        execution_time: Execution time string
        memory_usage: Memory usage string
        cpu_usage: CPU usage string
        fidelity: Simulation fidelity percentage
        n_qubits: Number of qubits in circuit
        metadata: Additional metadata from simulation
    """
    counts: Dict[str, int] = field(default_factory=dict)
    probabilities: Dict[str, float] = field(default_factory=dict)
    statevector: Optional[List[complex]] = None
    shots: int = 0
    backend: str = ""
    execution_time: str = ""
    simulation_time: str = ""
    memory_usage: str = ""
    cpu_usage: str = ""
    fidelity: float = 100.0
    n_qubits: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self) -> str:
        """String representation showing key stats."""
        return (
            f"SimulationResult("
            f"counts={self.counts}, "
            f"shots={self.shots}, "
            f"backend='{self.backend}', "
            f"n_qubits={self.n_qubits})"
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        lines = [
            f"Simulation Result:",
            f"  Backend: {self.backend}",
            f"  Qubits: {self.n_qubits}",
            f"  Shots: {self.shots}",
            f"  Counts: {self.counts}",
        ]
        if self.probabilities:
            lines.append(f"  Probabilities: {self.probabilities}")
        if self.execution_time:
            lines.append(f"  Execution Time: {self.execution_time}")
        if self.fidelity:
            lines.append(f"  Fidelity: {self.fidelity:.1f}%")
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'counts': self.counts,
            'probabilities': self.probabilities,
            'statevector': self.statevector,
            'shots': self.shots,
            'backend': self.backend,
            'execution_time': self.execution_time,
            'simulation_time': self.simulation_time,
            'memory_usage': self.memory_usage,
            'cpu_usage': self.cpu_usage,
            'fidelity': self.fidelity,
            'n_qubits': self.n_qubits,
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimulationResult':
        """Create SimulationResult from dictionary."""
        return cls(
            counts=data.get('counts', {}),
            probabilities=data.get('probabilities', data.get('probs', {})),
            statevector=data.get('statevector'),
            shots=data.get('shots', 0),
            backend=data.get('backend', ''),
            execution_time=data.get('execution_time', ''),
            simulation_time=data.get('simulation_time', ''),
            memory_usage=data.get('memory_usage', ''),
            cpu_usage=data.get('cpu_usage', ''),
            fidelity=data.get('fidelity', 100.0),
            n_qubits=data.get('n_qubits', 0),
            metadata=data.get('metadata', {}),
        )


@dataclass
class HybridExecutionResult:
    """
    Result from hybrid Python/quantum execution.
    
    Contains all outputs from executing user code including print statements,
    simulation results, generated QASM, and any errors.
    
    Attributes:
        success: Whether execution completed successfully
        stdout: Captured print() output
        stderr: Captured error output
        qasm_generated: Last generated QASM code (if any)
        simulation_results: List of simulation results from qsim.run() calls
        execution_time: Total execution time
        error: Error message if execution failed
        error_line: Line number where error occurred (if applicable)
        error_type: Type of error (if applicable)
    """
    success: bool = False
    stdout: str = ""
    stderr: str = ""
    qasm_generated: Optional[str] = None
    simulation_results: List[Dict[str, Any]] = field(default_factory=list)
    execution_time: str = ""
    error: Optional[str] = None
    error_line: Optional[int] = None
    error_type: Optional[str] = None
    
    def __repr__(self) -> str:
        """String representation."""
        status = "success" if self.success else "failed"
        return (
            f"HybridExecutionResult("
            f"status={status}, "
            f"simulations={len(self.simulation_results)}, "
            f"output_lines={len(self.stdout.splitlines())})"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'success': self.success,
            'stdout': self.stdout,
            'stderr': self.stderr,
            'qasm_generated': self.qasm_generated,
            'simulation_results': self.simulation_results,
            'execution_time': self.execution_time,
            'error': self.error,
            'error_line': self.error_line,
            'error_type': self.error_type,
        }
    
    @classmethod
    def from_error(cls, error: str, error_type: str = "ExecutionError", 
                   error_line: Optional[int] = None) -> 'HybridExecutionResult':
        """Create a failed result from an error."""
        return cls(
            success=False,
            error=error,
            error_type=error_type,
            error_line=error_line,
        )

