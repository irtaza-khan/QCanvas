from typing import Dict
from .base_visitor import BaseVisitor
from .cirq_visitor import CirqVisitor
from .qiskit_visitor import QiskitVisitor
from .pennylane_visitor import PennylaneVisitor

VISITORS: Dict[str, type[BaseVisitor]] = {
    'cirq': CirqVisitor,
    'qiskit': QiskitVisitor,
    'pennylane': PennylaneVisitor,
}

def get_visitor(name: str) -> BaseVisitor:
    cls = VISITORS.get(name.lower(), CirqVisitor)  # Default cirq
    return cls()
