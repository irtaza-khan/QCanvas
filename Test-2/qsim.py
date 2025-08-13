"""
QSIM Compilation Adapter: Qiskit / Cirq / PennyLane  -> OpenQASM 3 (preferred) or QASM 2 (fallback)

Usage (demo):
    python qsim_compile.py

Library requirements:
    - Qiskit >= 0.46 (for qiskit.qasm3.dumps)
    - Cirq >= 1.2 (to_qasm with version="3.0")
    - PennyLane >= 0.41 (tape.to_openqasm / qml.to_openqasm)
    - Optional: mpqp (for QASM2 -> QASM3 upgrade)
"""

from dataclasses import dataclass
from typing import Literal, Optional, Dict, Any

# Optional imports resolved lazily in functions.
# This module does not execute user code directly; instead it expects caller to
# pass source strings that define a function returning a circuit object.

Language = Literal["qiskit", "cirq", "pennylane"]

@dataclass
class CompileResult:
    ok: bool
    language: Language
    format: Literal["qasm3", "qasm2"]
    program: str
    stats: Dict[str, Any]

# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------

def _analyze_qiskit_circuit(qc) -> Dict[str, Any]:
    from qiskit.transpiler import CouplingMap
    try:
        n_qubits = qc.num_qubits
    except Exception:
        n_qubits = len(getattr(qc, "qubits", []))
    try:
        n_clbits = qc.num_clbits
    except Exception:
        n_clbits = len(getattr(qc, "clbits", []))
    try:
        depth = qc.depth()
    except Exception:
        depth = None
    return {
        "n_qubits": n_qubits,
        "n_clbits": n_clbits,
        "depth": depth,
        "has_parameters": bool(getattr(qc, "parameters", [])),
        "basis_gates": list(getattr(qc, "count_ops", lambda: {})().keys())
        if hasattr(qc, "count_ops")
        else None,
    }

def _maybe_upgrade_qasm2_to_qasm3(qasm2: str) -> Optional[str]:
    """
    Try to upgrade QASM 2 -> QASM 3 using 'mpqp' if available.
    Returns QASM3 string, or None if upgrade isn't possible.
    """
    try:
        from mpqp.qasm import convert_qasm  # type: ignore
    except Exception:
        return None
    try:
        return convert_qasm(qasm2, target_version="3.0")  # API provided by MPQP docs
    except Exception:
        return None

# --------------------------------------------------------------------------------------
# Language adapters
# --------------------------------------------------------------------------------------

def compile_qiskit_to_qasm3(source: str) -> CompileResult:
    """
    Expect 'source' to define a function get_circuit() -> qiskit.QuantumCircuit
    (keeps things safe and explicit).
    """
    import runpy, types, io, contextlib
    mod_globals = {}
    runpy.run_module = runpy.run_module  # just to appease linters
    # Execute user code in an isolated globals dict
    exec(compile(source, "<qiskit_src>", "exec"), mod_globals)
    get_circuit = mod_globals.get("get_circuit")
    if not callable(get_circuit):
        raise ValueError("Qiskit source must define a callable get_circuit()")
    qc = get_circuit()

    # Export to OpenQASM 3
    import qiskit.qasm3 as qasm3
    program = qasm3.dumps(qc)
    stats = _analyze_qiskit_circuit(qc)
    return CompileResult(ok=True, language="qiskit", format="qasm3", program=program, stats=stats)

def compile_cirq_to_qasm3(source: str) -> CompileResult:
    """
    Expect 'source' to define a function get_circuit() -> cirq.Circuit
    """
    import runpy
    ns = {}
    exec(compile(source, "<cirq_src>", "exec"), ns)
    get_circuit = ns.get("get_circuit")
    if not callable(get_circuit):
        raise ValueError("Cirq source must define a callable get_circuit()")
    circuit = get_circuit()

    # Export to OpenQASM 3
    try:
        # Newer Cirq
        program = circuit.to_qasm(version="3.0")
    except Exception:
        # Older style
        import cirq
        program = cirq.qasm(circuit, args=cirq.QasmArgs(version="3.0"))

    # Basic stats
    try:
        n_qubits = len(circuit.all_qubits())
        depth = circuit.depth()
    except Exception:
        n_qubits, depth = None, None
    stats = {"n_qubits": n_qubits, "depth": depth}
    return CompileResult(ok=True, language="cirq", format="qasm3", program=program, stats=stats)

def compile_pennylane_to_qasm3_or2(source: str) -> CompileResult:
    """
    Compile PennyLane QNode to OpenQASM 3 if possible, else fall back to QASM 2.
    """
    import pennylane as qml
    import inspect

    ns = {}
    exec(compile(source, "<pennylane_src>", "exec"), ns)
    get_qnode = ns.get("get_qnode")
    if not callable(get_qnode):
        raise ValueError("PennyLane source must define a callable get_qnode()")

    qnode = get_qnode()

    # Run QNode once to ensure tape is built, with proper error handling
    try:
        # Try to execute the QNode - some QNodes might need parameters
        try:
            qnode()
        except TypeError:
            # If it needs parameters, try with a default parameter
            import inspect
            sig = inspect.signature(qnode.func)
            if sig.parameters:
                # Try with default values or zeros
                args = []
                kwargs = {}
                for param in sig.parameters.values():
                    if param.default != param.empty:
                        continue  # Use default
                    elif param.annotation in (float, int):
                        kwargs[param.name] = 0.0
                    else:
                        kwargs[param.name] = 0.0
                qnode(**kwargs)
            else:
                qnode()
    except Exception as e:
        # If execution fails, we can still try to extract QASM from the tape structure
        print(f"[WARN] QNode execution failed: {e}. Attempting to extract circuit structure...")
        
        # Try to build the tape manually by calling the quantum function
        try:
            # Create a temporary tape to capture operations
            with qml.tape.QuantumTape() as tape:
                qnode.func()
            qnode.tape = tape
        except Exception as e2:
            raise RuntimeError(f"Error executing QNode and extracting tape: {e} / {e2}")

    # Get wire count (works for old & new device API)
    try:
        n_wires = qnode.device.num_wires  # New API
    except AttributeError:
        n_wires = len(qnode.device.wires)  # Old API

    # Try QASM3 if supported
    if hasattr(qml, 'to_openqasm') and "version" in inspect.signature(qml.to_openqasm).parameters:
        try:
            qasm3 = qml.to_openqasm(qnode, version="3")
            stats = {
                "n_wires": n_wires,
                "ops": len(qnode.tape.operations) if hasattr(qnode, "tape") else None,
                "upgraded_to_qasm3": True,
            }
            return CompileResult(ok=True, language="pennylane", format="qasm3", program=qasm3, stats=stats)
        except Exception as e:
            print(f"[WARN] QASM3 export failed: {e}")

    # Otherwise fallback to QASM2 → QASM3 upgrade
    try:
        if hasattr(qml, 'to_openqasm'):
            qasm2 = qml.to_openqasm(qnode)
        else:
            # Fallback for older versions
            qasm2 = qnode.tape.to_openqasm()
    except Exception as e:
        raise RuntimeError(f"Error exporting PennyLane QNode to QASM2: {e}")

    qasm3 = _maybe_upgrade_qasm2_to_qasm3(qasm2)
    stats = {
        "n_wires": n_wires,
        "ops": len(qnode.tape.operations) if hasattr(qnode, "tape") else None,
        "upgraded_to_qasm3": bool(qasm3),
    }

    if qasm3:
        return CompileResult(ok=True, language="pennylane", format="qasm3", program=qasm3, stats=stats)
    else:
        return CompileResult(ok=True, language="pennylane", format="qasm2", program=qasm2, stats=stats)

# --------------------------------------------------------------------------------------
# Facade
# --------------------------------------------------------------------------------------

def compile_to_openqasm(language: Language, source: str) -> CompileResult:
    if language == "qiskit":
        return compile_qiskit_to_qasm3(source)
    if language == "cirq":
        return compile_cirq_to_qasm3(source)
    if language == "pennylane":
        return compile_pennylane_to_qasm3_or2(source)
    raise ValueError(f"Unsupported language: {language}")

# --------------------------------------------------------------------------------------
# Demos (safe, minimal examples)
# --------------------------------------------------------------------------------------

DEMO_QISKIT = r"""
# from qiskit import QuantumCircuit
# def get_circuit():
#     qc = QuantumCircuit(2, 2)
#     qc.h(0)
#     qc.cx(0, 1)
#     qc.measure([0,1], [0,1])
#     return qc


# from qiskit import QuantumCircuit
# def get_circuit():
#     qc = QuantumCircuit(3, 3)
#     qc.h(0)
#     qc.x(1)
#     qc.cx(0, 1)
#     qc.ccx(0, 1, 2)
#     qc.t(0)
#     qc.s(1)
#     qc.rz(1.5708, 2)
#     qc.measure([0, 1, 2], [0, 1, 2])
#     return qc

from qiskit import QuantumCircuit
def get_circuit():
    qc = QuantumCircuit(2, 2)
    qc.rx(3.1415/2, 0)
    qc.ry(3.1415/4, 1)
    qc.swap(0, 1)
    qc.z(0)
    qc.measure([0, 1], [0, 1])
    return qc

"""

DEMO_CIRQ = r"""
# import cirq
# def get_circuit():
#     q0, q1 = cirq.LineQubit.range(2)
#     circuit = cirq.Circuit(
#         cirq.H(q0),
#         cirq.CNOT(q0, q1),
#         cirq.measure(q0, key="m0"),
#         cirq.measure(q1, key="m1"),
#     )
#     return circuit

# import cirq
# def get_circuit():
#     q0, q1, q2 = cirq.LineQubit.range(3)
#     circuit = cirq.Circuit(
#         cirq.H(q0),
#         cirq.X(q1),
#         cirq.CNOT(q0, q1),
#         cirq.CCZ(q0, q1, q2),
#         cirq.T(q0),
#         cirq.S(q1),
#         cirq.rz(1.5708)(q2),
#         cirq.measure(q0, key="m0"),
#         cirq.measure(q1, key="m1"),
#         cirq.measure(q2, key="m2")
#     )
#     return circuit


import cirq
def get_circuit():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.rx(3.1415/2)(q0),
        cirq.ry(3.1415/4)(q1),
        cirq.SWAP(q0, q1),
        cirq.Z(q0),
        cirq.measure(q0, key="m0"),
        cirq.measure(q1, key="m1")
    )
    return circuit

"""

DEMO_PENNYLANE = r"""
import pennylane as qml

def get_qnode():
    # Use shots for sampling measurements, or expval/probs for analytic
    dev = qml.device("default.qubit", wires=2, shots=1024)

    @qml.qnode(dev)
    def bell():
        qml.Hadamard(wires=0)
        qml.CNOT(wires=[0, 1])
        return qml.sample()  # Now works with shots=1024
    
    return bell
"""

# Alternative PennyLane demo with expectation values (analytic)
DEMO_PENNYLANE_ANALYTIC = r"""
import pennylane as qml

def get_qnode():
    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def bell():
        qml.Hadamard(wires=0)
        qml.CNOT(wires=[0, 1])
        return qml.expval(qml.PauliZ(0))  # Analytic expectation value
    
    return bell
"""

if __name__ == "__main__":
    print("=" * 60)
    print("QSIM Compilation Demo: Converting to OpenQASM 3 IR")
    print("=" * 60)
    
    # Demo: Qiskit -> QASM3
    try:
        res_qk = compile_to_openqasm("qiskit", DEMO_QISKIT)
        print(f"\n=== Qiskit -> {res_qk.format.upper()} ===")
        print(f"Stats: {res_qk.stats}")
        print("Program:")
        print(res_qk.program)
    except Exception as e:
        print(f"\n=== Qiskit FAILED ===")
        print(f"Error: {e}")

    # Demo: Cirq -> QASM3
    try:
        res_cq = compile_to_openqasm("cirq", DEMO_CIRQ)
        print(f"\n=== Cirq -> {res_cq.format.upper()} ===")
        print(f"Stats: {res_cq.stats}")
        print("Program:")
        print(res_cq.program)
    except Exception as e:
        print(f"\n=== Cirq FAILED ===")
        print(f"Error: {e}")

    # Demo: PennyLane -> QASM3 (with shots for sampling)
    try:
        res_pl = compile_to_openqasm("pennylane", DEMO_PENNYLANE)
        print(f"\n=== PennyLane -> {res_pl.format.upper()} (with sampling) ===")
        print(f"Stats: {res_pl.stats}")
        print("Program:")
        print(res_pl.program)
    except Exception as e:
        print(f"\n=== PennyLane (sampling) FAILED ===")
        print(f"Error: {e}")
        
        # Try the analytic version as fallback
        try:
            print("\nTrying PennyLane with analytic measurement...")
            res_pl_analytic = compile_to_openqasm("pennylane", DEMO_PENNYLANE_ANALYTIC)
            print(f"\n=== PennyLane -> {res_pl_analytic.format.upper()} (analytic) ===")
            print(f"Stats: {res_pl_analytic.stats}")
            print("Program:")
            print(res_pl_analytic.program)
        except Exception as e2:
            print(f"=== PennyLane (analytic) also FAILED ===")
            print(f"Error: {e2}")
    
    print("\n" + "=" * 60)
    print("Compilation Complete!")
    print("=" * 60)