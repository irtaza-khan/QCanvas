# Quantum Converters Package
# This package provides converters for various quantum computing frameworks to OpenQASM 3.0

__version__ = "1.0.0"
__author__ = "QCanvas Team"

# Make key components available at package level
try:
    from .converters.qiskit_to_qasm import convert_qiskit_to_qasm3
    from .converters.cirq_to_qasm import convert_cirq_to_qasm3
    from .converters.pennylane_to_qasm import convert_pennylane_to_qasm3
    from .base.ConversionResult import ConversionResult, ConversionStats
    
    __all__ = [
        'convert_qiskit_to_qasm3',
        'convert_cirq_to_qasm3', 
        'convert_pennylane_to_qasm3',
        'ConversionResult',
        'ConversionStats'
    ]
except ImportError as e:
    # Some dependencies might not be available
    print(f"Warning: Could not import all converter modules: {e}")
    __all__ = []
