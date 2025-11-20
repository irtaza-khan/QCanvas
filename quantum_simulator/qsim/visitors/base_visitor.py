from abc import ABC, abstractmethod
import pyqasm

class BaseVisitor(ABC):
    """
    Abstract base class for QSim visitors.
    Defines the interface and traversal logic.
    """

    def visit(self, module: pyqasm.Qasm3Module):
        """Dispatch to the appropriate visit method based on node type."""
        for node in module._statements:
            method_name = "visit_" + type(node).__name__
            visitor = getattr(self, method_name, self.generic_visit)
            visitor(node)
            
            
    def _visit_node(self, node):
        """
        Internal helper for recursive dispatch to any node type.
        This should be called manually by visitors for complex nodes.
        """
        method_name = "visit_" + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)


        
    @abstractmethod
    def finalize(self, visited_block):
        """
        Hook for producing a final object 
        (QuantumCircuit, Cirq.Circuit, QNode, etc).
        Must be implemented by subclasses.
        """
        pass

    def generic_visit(self, node):
        """Default handler if no visit_* method is implemented."""
        raise NotImplementedError(
            f"No visit method defined for node type {type(node).__name__}"
        )
