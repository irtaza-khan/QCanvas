from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseBackend(ABC):
    """
    Abstract base for QSim backends.
    Consumes visitor circuit and simulates.
    """

    @abstractmethod
    def run(self, circuit: Any, shots: int = 1024) -> Dict[str, Any]:
        """
        Run simulation.
        Args:
            circuit: From visitor.finalize() (e.g., cirq.Circuit).
            shots: >0 for sampling; 0 for exact state/probs.
        Returns:
            {'counts': {'00': 512, ...}, 'probs': {...}, 'metadata': {...}}
        """
        pass

    def to_counts(self, result: Dict[str, Any]) -> Dict[str, int]:
        """Normalize to counts (default impl)."""
        return result.get('counts', {})