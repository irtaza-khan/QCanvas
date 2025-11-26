"""
QCanvas Runtime Package

Provides compile() and compile_and_execute() functions for hybrid CPU-QPU execution.
This package is injected into the sandboxed execution environment.

Usage in user code:
    from qcanvas import compile
    import qsim
    
    # Compile circuit to QASM
    qasm = compile(circuit, framework="cirq")
    
    # Execute QASM
    result = qsim.run(qasm, shots=1024, backend="cirq")
    print(result.counts)
"""

from .core import compile, compile_and_execute
from .result import SimulationResult, HybridExecutionResult

__all__ = [
    'compile',
    'compile_and_execute', 
    'SimulationResult',
    'HybridExecutionResult',
]

__version__ = '1.0.0'

