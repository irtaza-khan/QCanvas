"""
Verification script for the qcanvas package build.
Tests compiling Cirq, Qiskit, and PennyLane circuits to OpenQASM 3.0.
"""

import sys
import os

# Ensure the workspace root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import qcanvas

print("==========================================")
print(f"Verifying qcanvas Package (v{qcanvas.__version__})")
print("==========================================")


def test_cirq():
    print("\n--- Testing Cirq Compilation ---")
    try:
        import cirq
        print("[OK] cirq module is available")
    except ImportError:
        print("[SKIPPED] cirq is not installed. Skipping Cirq circuit test.")
        return False

    try:
        q0, q1 = cirq.LineQubit.range(2)
        circuit = cirq.Circuit(
            cirq.H(q0),
            cirq.CNOT(q0, q1),
            cirq.measure(q0, q1, key="m")
        )
        print("Generated Cirq Circuit object successfully")
        
        qasm = qcanvas.compile(circuit, framework="cirq")
        print("\nSuccessfully compiled to OpenQASM 3.0:")
        print(qasm.strip())
        return "OPENQASM 3.0" in qasm
    except Exception as e:
        print(f"[FAIL] Failed to compile Cirq: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_qiskit():
    print("\n--- Testing Qiskit Compilation ---")
    try:
        import qiskit
        from qiskit import QuantumCircuit
        print("[OK] qiskit module is available")
    except ImportError:
        print("[SKIPPED] qiskit is not installed. Skipping Qiskit circuit test.")
        return False

    try:
        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)
        print("Generated Qiskit QuantumCircuit object successfully")

        qasm = qcanvas.compile(circuit, framework="qiskit")
        print("\nSuccessfully compiled to OpenQASM 3.0:")
        print(qasm.strip())
        return "OPENQASM 3.0" in qasm
    except Exception as e:
        print(f"[FAIL] Failed to compile Qiskit: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pennylane():
    print("\n--- Testing PennyLane Compilation ---")
    try:
        import pennylane as qml
        print("[OK] pennylane module is available")
    except ImportError:
        print("[SKIPPED] pennylane is not installed. Skipping PennyLane circuit test.")
        return False

    try:
        source_code = """
import pennylane as qml

dev = qml.device('default.qubit', wires=2)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.state()

def get_circuit():
    return circuit
"""
        print("Generated PennyLane Source Code successfully")

        qasm = qcanvas.compile(source_code, framework="pennylane")
        print("\nSuccessfully compiled to OpenQASM 3.0:")
        print(qasm.strip())
        return "OPENQASM 3.0" in qasm
    except Exception as e:
        print(f"[FAIL] Failed to compile PennyLane: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    cirq_res = test_cirq()
    qiskit_res = test_qiskit()
    pennylane_res = test_pennylane()
    
    print("\n==========================================")
    print("Verification Summary:")
    print(f"  Cirq Compilation:      {'PASSED' if cirq_res else 'FAILED/SKIPPED'}")
    print(f"  Qiskit Compilation:    {'PASSED' if qiskit_res else 'FAILED/SKIPPED'}")
    print(f"  PennyLane Compilation: {'PASSED' if pennylane_res else 'FAILED/SKIPPED'}")
    print("==========================================")
