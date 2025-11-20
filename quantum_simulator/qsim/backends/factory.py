from typing import Dict
from .base import BaseBackend
from .cirq import CirqBackend
from .qiskit import QiskitBackend
from .pennylane import PennylaneBackend

BACKENDS: Dict[str, type[BaseBackend]] = {
    'cirq': CirqBackend,
    'qiskit': QiskitBackend,
    'pennylane': PennylaneBackend,
}

def get_backend(name: str) -> BaseBackend:
    cls = BACKENDS.get(name.lower(), CirqBackend)  # Default cirq
    return cls()
