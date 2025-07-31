from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import json
import numpy as np

# Core imports for different frameworks
try:
    from qiskit import QuantumCircuit, qasm3, ClassicalRegister, QuantumRegister
    from qiskit_aer import AerSimulator
    from qiskit.visualization import plot_histogram
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False

try:
    import cirq
    CIRQ_AVAILABLE = True
except ImportError:
    CIRQ_AVAILABLE = False

try:
    from braket.circuits import Circuit as BraketCircuit
    from braket.devices import LocalSimulator
    BRAKET_AVAILABLE = True
except ImportError:
    BRAKET_AVAILABLE = False

class FrameworkType(Enum):
    QISKIT = "qiskit"
    CIRQ = "cirq"
    BRAKET = "braket"
    OPENQASM = "openqasm"

class GateType(Enum):
    H = "h"           # Hadamard
    X = "x"           # Pauli-X
    Y = "y"           # Pauli-Y  
    Z = "z"           # Pauli-Z
    CNOT = "cnot"     # Controlled-NOT
    CZ = "cz"         # Controlled-Z
    RX = "rx"         # Rotation-X
    RY = "ry"         # Rotation-Y
    RZ = "rz"         # Rotation-Z
    MEASURE = "measure"

@dataclass
class QuantumGate:
    """Universal gate representation"""
    gate_type: GateType
    qubits: List[int]
    parameters: List[float] = None
    classical_bits: List[int] = None  # For measurements

@dataclass
class QuantumIR:
    """Quantum Intermediate Representation"""
    num_qubits: int
    num_classical_bits: int
    gates: List[QuantumGate]
    metadata: Dict[str, Any] = None

@dataclass 
class SimulationResult:
    """Standardized simulation result"""
    counts: Dict[str, int]
    shots: int
    execution_time: float
    backend_name: str
    circuit_depth: int
    success: bool
    error_message: Optional[str] = None
    statevector: Optional[np.ndarray] = None

class QuantumSimulator(ABC):
    """Abstract base class for quantum simulators"""
    
    @abstractmethod
    def execute_ir(self, ir: QuantumIR, shots: int = 1000) -> SimulationResult:
        """Execute quantum IR and return results"""
        pass
    
    @abstractmethod
    def supports_statevector(self) -> bool:
        """Check if simulator supports statevector output"""
        pass
    
    @abstractmethod 
    def get_backend_info(self) -> Dict[str, Any]:
        """Get simulator backend information"""
        pass

class QiskitSimulator(QuantumSimulator):
    """Qiskit Aer simulator implementation"""
    
    def __init__(self):
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit not available")
        self.simulator = AerSimulator()
    
    def execute_ir(self, ir: QuantumIR, shots: int = 1000) -> SimulationResult:
        import time
        start_time = time.time()
        
        try:
            # Convert IR to Qiskit circuit
            qc = self._ir_to_qiskit(ir)
            
            # Execute simulation
            result = self.simulator.run(qc, shots=shots).result()
            counts = result.get_counts()
            
            execution_time = time.time() - start_time
            
            return SimulationResult(
                counts=counts,
                shots=shots,
                execution_time=execution_time,
                backend_name="qiskit_aer",
                circuit_depth=qc.depth(),
                success=True
            )
            
        except Exception as e:
            return SimulationResult(
                counts={},
                shots=shots,
                execution_time=time.time() - start_time,
                backend_name="qiskit_aer", 
                circuit_depth=0,
                success=False,
                error_message=str(e)
            )
    
    def _ir_to_qiskit(self, ir: QuantumIR) -> QuantumCircuit:
        """Convert IR to Qiskit circuit"""
        qc = QuantumCircuit(ir.num_qubits, ir.num_classical_bits)
        
        for gate in ir.gates:
            if gate.gate_type == GateType.H:
                qc.h(gate.qubits[0])
            elif gate.gate_type == GateType.X:
                qc.x(gate.qubits[0])
            elif gate.gate_type == GateType.Y:
                qc.y(gate.qubits[0])
            elif gate.gate_type == GateType.Z:
                qc.z(gate.qubits[0])
            elif gate.gate_type == GateType.CNOT:
                qc.cx(gate.qubits[0], gate.qubits[1])
            elif gate.gate_type == GateType.CZ:
                qc.cz(gate.qubits[0], gate.qubits[1])
            elif gate.gate_type == GateType.RX:
                qc.rx(gate.parameters[0], gate.qubits[0])
            elif gate.gate_type == GateType.RY:
                qc.ry(gate.parameters[0], gate.qubits[0])
            elif gate.gate_type == GateType.RZ:
                qc.rz(gate.parameters[0], gate.qubits[0])
            elif gate.gate_type == GateType.MEASURE:
                qc.measure(gate.qubits[0], gate.classical_bits[0])
        
        return qc
    
    def supports_statevector(self) -> bool:
        return True
    
    def get_backend_info(self) -> Dict[str, Any]:
        return {
            "name": "Qiskit Aer",
            "version": "latest",
            "max_qubits": 32,
            "supports_noise": True
        }

class CirqSimulator(QuantumSimulator):
    """Cirq simulator implementation"""
    
    def __init__(self):
        if not CIRQ_AVAILABLE:
            raise ImportError("Cirq not available")
        self.simulator = cirq.Simulator()
    
    def execute_ir(self, ir: QuantumIR, shots: int = 1000) -> SimulationResult:
        import time
        start_time = time.time()
        
        try:
            # Convert IR to Cirq circuit
            circuit, measurement_keys = self._ir_to_cirq(ir)
            
            # Execute simulation
            result = self.simulator.run(circuit, repetitions=shots)
            
            # Convert results to standard format
            counts = self._cirq_results_to_counts(result, measurement_keys)
            
            execution_time = time.time() - start_time
            
            return SimulationResult(
                counts=counts,
                shots=shots,
                execution_time=execution_time,
                backend_name="cirq_simulator",
                circuit_depth=len(circuit),
                success=True
            )
            
        except Exception as e:
            return SimulationResult(
                counts={},
                shots=shots,
                execution_time=time.time() - start_time,
                backend_name="cirq_simulator",
                circuit_depth=0,
                success=False,
                error_message=str(e)
            )
    
    def _ir_to_cirq(self, ir: QuantumIR):
        """Convert IR to Cirq circuit"""
        qubits = [cirq.LineQubit(i) for i in range(ir.num_qubits)]
        circuit = cirq.Circuit()
        measurement_keys = []
        
        for gate in ir.gates:
            if gate.gate_type == GateType.H:
                circuit.append(cirq.H(qubits[gate.qubits[0]]))
            elif gate.gate_type == GateType.X:
                circuit.append(cirq.X(qubits[gate.qubits[0]]))
            elif gate.gate_type == GateType.Y:
                circuit.append(cirq.Y(qubits[gate.qubits[0]]))
            elif gate.gate_type == GateType.Z:
                circuit.append(cirq.Z(qubits[gate.qubits[0]]))
            elif gate.gate_type == GateType.CNOT:
                circuit.append(cirq.CNOT(qubits[gate.qubits[0]], qubits[gate.qubits[1]]))
            elif gate.gate_type == GateType.CZ:
                circuit.append(cirq.CZ(qubits[gate.qubits[0]], qubits[gate.qubits[1]]))
            elif gate.gate_type == GateType.RX:
                circuit.append(cirq.rx(gate.parameters[0])(qubits[gate.qubits[0]]))
            elif gate.gate_type == GateType.RY:
                circuit.append(cirq.ry(gate.parameters[0])(qubits[gate.qubits[0]]))
            elif gate.gate_type == GateType.RZ:
                circuit.append(cirq.rz(gate.parameters[0])(qubits[gate.qubits[0]]))
            elif gate.gate_type == GateType.MEASURE:
                key = f"q{gate.qubits[0]}"
                measurement_keys.append(key)
                circuit.append(cirq.measure(qubits[gate.qubits[0]], key=key))
        
        return circuit, measurement_keys
    
    def _cirq_results_to_counts(self, result, measurement_keys):
        """Convert Cirq results to counts dictionary"""
        if not measurement_keys:
            return {"": result.repetitions}
            
        counts = {}
        for i in range(len(result.measurements[measurement_keys[0]])):
            bitstring = ""
            for key in measurement_keys:
                bitstring += str(result.measurements[key][i][0])
            counts[bitstring] = counts.get(bitstring, 0) + 1
        
        return counts
    
    def supports_statevector(self) -> bool:
        return True
    
    def get_backend_info(self) -> Dict[str, Any]:
        return {
            "name": "Cirq Simulator", 
            "version": "latest",
            "max_qubits": 32,
            "supports_noise": True
        }

class BraketSimulator(QuantumSimulator):
    """AWS Braket Local simulator implementation"""
    
    def __init__(self):
        if not BRAKET_AVAILABLE:
            raise ImportError("Braket not available")
        self.simulator = LocalSimulator()
    
    def execute_ir(self, ir: QuantumIR, shots: int = 1000) -> SimulationResult:
        import time
        start_time = time.time()
        
        try:
            # Convert IR to Braket circuit
            circuit = self._ir_to_braket(ir)
            
            # Execute simulation
            task = self.simulator.run(circuit, shots=shots)
            result = task.result()
            
            # Convert results
            counts = result.measurement_counts
            
            execution_time = time.time() - start_time
            
            return SimulationResult(
                counts=counts,
                shots=shots,
                execution_time=execution_time,
                backend_name="braket_local",
                circuit_depth=circuit.depth,
                success=True
            )
            
        except Exception as e:
            return SimulationResult(
                counts={},
                shots=shots,
                execution_time=time.time() - start_time,
                backend_name="braket_local",
                circuit_depth=0,
                success=False,
                error_message=str(e)
            )
    
    def _ir_to_braket(self, ir: QuantumIR):
        """Convert IR to Braket circuit"""
        circuit = BraketCircuit()
        
        for gate in ir.gates:
            if gate.gate_type == GateType.H:
                circuit.h(gate.qubits[0])
            elif gate.gate_type == GateType.X:
                circuit.x(gate.qubits[0])
            elif gate.gate_type == GateType.Y:
                circuit.y(gate.qubits[0])
            elif gate.gate_type == GateType.Z:
                circuit.z(gate.qubits[0])
            elif gate.gate_type == GateType.CNOT:
                circuit.cnot(gate.qubits[0], gate.qubits[1])
            elif gate.gate_type == GateType.CZ:
                circuit.cz(gate.qubits[0], gate.qubits[1])
            elif gate.gate_type == GateType.RX:
                circuit.rx(gate.qubits[0], gate.parameters[0])
            elif gate.gate_type == GateType.RY:
                circuit.ry(gate.qubits[0], gate.parameters[0])
            elif gate.gate_type == GateType.RZ:
                circuit.rz(gate.qubits[0], gate.parameters[0])
        
        return circuit
    
    def supports_statevector(self) -> bool:
        return True
    
    def get_backend_info(self) -> Dict[str, Any]:
        return {
            "name": "Braket Local",
            "version": "latest", 
            "max_qubits": 25,
            "supports_noise": False
        }

class UnifiedQuantumSimulator:
    """Main orchestrator for multi-framework quantum simulation"""
    
    def __init__(self):
        self.simulators = {}
        self._register_simulators()
    
    def _register_simulators(self):
        """Register available simulators"""
        if QISKIT_AVAILABLE:
            try:
                self.simulators[FrameworkType.QISKIT] = QiskitSimulator()
            except Exception as e:
                print(f"Failed to initialize Qiskit: {e}")
        
        if CIRQ_AVAILABLE:
            try:
                self.simulators[FrameworkType.CIRQ] = CirqSimulator()
            except Exception as e:
                print(f"Failed to initialize Cirq: {e}")
        
        if BRAKET_AVAILABLE:
            try:
                self.simulators[FrameworkType.BRAKET] = BraketSimulator()
            except Exception as e:
                print(f"Failed to initialize Braket: {e}")
    
    def get_available_backends(self) -> List[str]:
        """Get list of available simulator backends"""
        return [framework.value for framework in self.simulators.keys()]
    
    def execute_circuit(self, ir: QuantumIR, backend: FrameworkType, shots: int = 1000) -> SimulationResult:
        """Execute quantum circuit on specified backend"""
        if backend not in self.simulators:
            return SimulationResult(
                counts={},
                shots=shots,
                execution_time=0,
                backend_name=backend.value,
                circuit_depth=0,
                success=False,
                error_message=f"Backend {backend.value} not available"
            )
        
        return self.simulators[backend].execute_ir(ir, shots)
    
    def compare_backends(self, ir: QuantumIR, shots: int = 1000) -> Dict[str, SimulationResult]:
        """Execute same circuit on all available backends for comparison"""
        results = {}
        for framework, simulator in self.simulators.items():
            results[framework.value] = simulator.execute_ir(ir, shots)
        return results
    
    def get_backend_info(self, backend: FrameworkType) -> Optional[Dict[str, Any]]:
        """Get information about specific backend"""
        if backend in self.simulators:
            return self.simulators[backend].get_backend_info()
        return None

# Example usage and testing
def create_bell_state_ir() -> QuantumIR:
    """Create Bell state circuit in IR format"""
    gates = [
        QuantumGate(GateType.H, [0]),
        QuantumGate(GateType.CNOT, [0, 1]),
        QuantumGate(GateType.MEASURE, [0], classical_bits=[0]),
        QuantumGate(GateType.MEASURE, [1], classical_bits=[1])
    ]
    
    return QuantumIR(
        num_qubits=2,
        num_classical_bits=2,
        gates=gates,
        metadata={"name": "Bell State", "description": "EPR pair creation"}
    )

def demo_unified_simulator():
    """Demonstrate unified simulator functionality"""
    print("🚀 QSIM Unified Quantum Simulator Demo")
    print("=" * 50)
    
    # Initialize unified simulator
    unified_sim = UnifiedQuantumSimulator()
    
    print(f"Available backends: {unified_sim.get_available_backends()}")
    
    # Create test circuit
    bell_ir = create_bell_state_ir()
    
    # Run comparison across all backends
    print("\n📊 Cross-Backend Comparison:")
    results = unified_sim.compare_backends(bell_ir, shots=1000)
    
    for backend, result in results.items():
        print(f"\n{backend.upper()}:")
        if result.success:
            print(f"  Counts: {result.counts}")
            print(f"  Execution time: {result.execution_time:.4f}s")
            print(f"  Circuit depth: {result.circuit_depth}")
        else:
            print(f"  Error: {result.error_message}")

if __name__ == "__main__":
    demo_unified_simulator()