"""
Core functions for qcanvas runtime.

Provides compile() and compile_and_execute() functions that are injected
into the sandboxed execution environment for hybrid CPU-QPU execution.
"""

import sys
import os
from typing import Any, Optional, Union

# Add project root to path for imports
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from .result import SimulationResult

# Import converters
try:
    from quantum_converters.converters.cirq_to_qasm import convert_cirq_to_qasm3
    from quantum_converters.converters.qiskit_to_qasm import convert_qiskit_to_qasm3
    from quantum_converters.converters.pennylane_to_qasm import convert_pennylane_to_qasm3
    CONVERTERS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Converters not available: {e}")
    CONVERTERS_AVAILABLE = False
    convert_cirq_to_qasm3 = None
    convert_qiskit_to_qasm3 = None
    convert_pennylane_to_qasm3 = None

# Import QSim
try:
    from qsim import run_qasm as qsim_run, RunArgs, SimResult
    QSIM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: QSim not available: {e}")
    QSIM_AVAILABLE = False
    qsim_run = None
    RunArgs = None
    SimResult = None


def _detect_framework(circuit: Any) -> str:
    """
    Auto-detect the framework of a circuit object.
    
    Args:
        circuit: A circuit object from Cirq, Qiskit, or PennyLane
        
    Returns:
        Framework name: 'cirq', 'qiskit', or 'pennylane'
        
    Raises:
        ValueError: If framework cannot be detected
    """
    type_name = type(circuit).__name__
    module_name = type(circuit).__module__
    
    # Check Cirq
    if 'cirq' in module_name.lower() or type_name == 'Circuit':
        return 'cirq'
    
    # Check Qiskit
    if 'qiskit' in module_name.lower() or type_name == 'QuantumCircuit':
        return 'qiskit'
    
    # Check PennyLane
    if 'pennylane' in module_name.lower() or 'qml' in module_name.lower():
        return 'pennylane'
    
    raise ValueError(
        f"Cannot auto-detect framework for circuit of type '{type_name}' "
        f"from module '{module_name}'. Please specify framework explicitly."
    )


def _circuit_to_code(circuit: Any, framework: str) -> str:
    """
    Convert a circuit object to executable Python code string.
    
    For Cirq and Qiskit, we can work directly with the circuit object.
    For PennyLane QNodes, we need special handling.
    """
    if framework == 'cirq':
        # Cirq circuits can be converted directly using their internal representation.
        # We'll serialize the circuit operations to code in a format that matches
        # what our existing Cirq parser already supports (q0, q1 = LineQubit.range(...)).
        try:
            import cirq
            lines: list[str] = ["import cirq"]

            # Get all qubits in a deterministic order
            qubits = sorted(circuit.all_qubits(), key=lambda q: (str(type(q)), str(q)))
            if not qubits:
                return None

            # Create stable variable names q0, q1, ..., qN
            qubit_names = [f"q{i}" for i in range(len(qubits))]

            if all(isinstance(q, cirq.LineQubit) for q in qubits):
                # Pattern the existing parser already understands:
                if len(qubits) == 1:
                    # Single qubit: q0 = cirq.LineQubit(0)
                    lines.append(f"{qubit_names[0]} = cirq.LineQubit(0)")
                else:
                    # Multiple qubits: q0, q1 = cirq.LineQubit.range(2)
                    lines.append(f"{', '.join(qubit_names)} = cirq.LineQubit.range({len(qubits)})")
            else:
                # Named qubits: create explicit NamedQubit declarations
                for i, qubit in enumerate(qubits):
                    lines.append(f"{qubit_names[i]} = cirq.NamedQubit('{qubit}')")

            lines.append("circuit = cirq.Circuit([")

            # Convert each operation
            for moment in circuit:
                for op in moment:
                    gate = op.gate
                    gate_qubits = op.qubits

                    # Map each qubit in the operation to one of our q{i} names
                    qubit_refs: list[str] = []
                    for gq in gate_qubits:
                        idx = qubits.index(gq)
                        qubit_refs.append(qubit_names[idx])

                    # Format the operation:
                    # - Standard gates: cirq.H(q0), cirq.CNOT(q0, q1), etc.
                    # - Measurements: cirq.measure(q0, q1, key='m')
                    if isinstance(gate, getattr(cirq, "MeasurementGate", ())):
                        # Measurement: use cirq.measure with qubit refs and key
                        key = getattr(gate, "key", "m")
                        lines.append(
                            f"    cirq.measure({', '.join(qubit_refs)}, key='{key}'),"
                        )
                    else:
                        gate_str = str(gate)
                        if qubit_refs:
                            lines.append(f"    cirq.{gate_str}({', '.join(qubit_refs)}),")

            lines.append("])")
            return "\n".join(lines)
        except Exception:
            # Fall back to string representation
            return str(circuit)
    
    elif framework == 'qiskit':
        # Qiskit circuits can be exported to QASM directly
        try:
            # Try to get QASM 3.0 directly if available
            return circuit.qasm() if hasattr(circuit, 'qasm') else str(circuit)
        except Exception:
            return str(circuit)
    
    elif framework == 'pennylane':
        # PennyLane QNodes are functions, we need their tape
        try:
            if hasattr(circuit, 'tape') and circuit.tape is not None:
                return str(circuit.tape)
            return str(circuit)
        except Exception:
            return str(circuit)
    
    return str(circuit)


def compile(circuit: Any, framework: Optional[str] = None) -> str:
    """
    Compile a quantum circuit to OpenQASM 3.0.
    
    This function takes a circuit object from Cirq, Qiskit, or PennyLane
    and converts it to OpenQASM 3.0 format.
    
    Args:
        circuit: Circuit object from one of the supported frameworks:
            - cirq.Circuit
            - qiskit.QuantumCircuit  
            - pennylane QNode or tape
        framework: Source framework name ("cirq", "qiskit", "pennylane").
            If not provided, will attempt auto-detection.
    
    Returns:
        OpenQASM 3.0 code as a string
        
    Raises:
        ValueError: If framework is not supported or conversion fails
        
    Example:
        >>> import cirq
        >>> q = cirq.LineQubit.range(2)
        >>> circuit = cirq.Circuit([cirq.H(q[0]), cirq.CNOT(q[0], q[1])])
        >>> qasm = compile(circuit, framework="cirq")
        >>> print(qasm)
        OPENQASM 3.0;
        include "stdgates.inc";
        qubit[2] q;
        h q[0];
        cx q[0], q[1];
    """
    if not CONVERTERS_AVAILABLE:
        raise RuntimeError("Quantum converters are not available")
    
    # Auto-detect framework if not specified
    if framework is None:
        framework = _detect_framework(circuit)
    
    framework = framework.lower().strip()
    
    # Validate framework
    if framework not in ('cirq', 'qiskit', 'pennylane'):
        raise ValueError(
            f"Unsupported framework: '{framework}'. "
            f"Supported frameworks: cirq, qiskit, pennylane"
        )
    
    try:
        # For direct circuit objects, we need to convert them to code first
        # then use our existing converters
        
        if framework == 'cirq':
            # Check if it's a Cirq circuit object
            if hasattr(circuit, 'all_qubits') and hasattr(circuit, 'all_operations'):
                # It's a Cirq Circuit object - convert to code representation
                code = _circuit_to_code(circuit, 'cirq')
                if code:
                    result = convert_cirq_to_qasm3(code)
                else:
                    raise ValueError("Failed to convert Cirq circuit to code")
            else:
                # Assume it's already code string
                result = convert_cirq_to_qasm3(str(circuit))
                
        elif framework == 'qiskit':
            # Check if it's a Qiskit QuantumCircuit object
            if hasattr(circuit, 'qasm'):
                # Use Qiskit's built-in QASM export if available
                try:
                    qasm = circuit.qasm()
                    # Convert QASM 2.0 to 3.0 if needed
                    if qasm.startswith('OPENQASM 2.0'):
                        # Basic conversion - replace header
                        qasm = qasm.replace('OPENQASM 2.0', 'OPENQASM 3.0', 1)
                    return qasm
                except Exception:
                    pass
            # Fall back to code conversion
            code = str(circuit)
            result = convert_qiskit_to_qasm3(code)
            
        elif framework == 'pennylane':
            # Check if it's a PennyLane QNode or tape
            if callable(circuit) and hasattr(circuit, 'tape'):
                # It's a QNode - try to get the tape
                code = str(circuit.tape) if circuit.tape else str(circuit)
            else:
                code = str(circuit)
            result = convert_pennylane_to_qasm3(code)
        
        # Extract QASM code from result
        if hasattr(result, 'qasm_code'):
            return result.qasm_code
        elif isinstance(result, str):
            return result
        else:
            return str(result)
            
    except Exception as e:
        raise ValueError(f"Conversion failed for {framework}: {str(e)}") from e


def compile_and_execute(
    circuit: Any,
    framework: Optional[str] = None,
    shots: int = 1024,
    backend: str = "cirq"
) -> SimulationResult:
    """
    Compile a quantum circuit and execute it in a single call.
    
    This is a convenience function that combines compile() and qsim.run().
    
    Args:
        circuit: Circuit object from one of the supported frameworks
        framework: Source framework name (auto-detected if not provided)
        shots: Number of measurement shots (default: 1024)
        backend: Simulation backend to use (default: "cirq")
            Options: "cirq", "qiskit", "pennylane"
    
    Returns:
        SimulationResult with counts, probabilities, and metadata
        
    Example:
        >>> import cirq
        >>> q = cirq.LineQubit.range(2)
        >>> circuit = cirq.Circuit([cirq.H(q[0]), cirq.CNOT(q[0], q[1])])
        >>> result = compile_and_execute(circuit, framework="cirq", shots=1000)
        >>> print(result.counts)
        {'00': 498, '11': 502}
    """
    # Compile circuit to QASM
    qasm = compile(circuit, framework=framework)
    
    # Import qsim module for execution
    from . import qsim as qsim_module
    
    # Execute and return result
    return qsim_module.run(qasm, shots=shots, backend=backend)

