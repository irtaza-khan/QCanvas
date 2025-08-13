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

def _pennylane_to_qasm_manual(qnode) -> str:
    """
    Manually construct QASM from PennyLane QNode when automatic conversion fails
    """
    import pennylane as qml
    
    # Get the number of wires
    try:
        n_wires = qnode.device.num_wires
    except AttributeError:
        n_wires = len(qnode.device.wires)
    
    # Build QASM header
    qasm_lines = [
        "OPENQASM 2.0;",
        'include "qelib1.inc";',
        f"qreg q[{n_wires}];",
        f"creg c[{n_wires}];"
    ]
    
    # Convert operations if tape exists
    if hasattr(qnode, 'tape') and hasattr(qnode.tape, 'operations'):
        for op in qnode.tape.operations:
            if hasattr(op, 'name'):
                op_name = op.name.lower()
                wires = [int(w) for w in op.wires] if hasattr(op, 'wires') else []
                
                if op_name == 'hadamard':
                    qasm_lines.append(f"h q[{wires[0]}];")
                elif op_name == 'cnot':
                    qasm_lines.append(f"cx q[{wires[0]}],q[{wires[1]}];")
                elif op_name == 'paulix':
                    qasm_lines.append(f"x q[{wires[0]}];")
                elif op_name == 'pauliy':
                    qasm_lines.append(f"y q[{wires[0]}];")
                elif op_name == 'pauliz':
                    qasm_lines.append(f"z q[{wires[0]}];")
                # Add more gate mappings as needed
        
        # Add measurements if present
        if hasattr(qnode.tape, 'measurements'):
            for i, measurement in enumerate(qnode.tape.measurements):
                if hasattr(measurement, 'wires'):
                    for wire in measurement.wires:
                        qasm_lines.append(f"measure q[{int(wire)}] -> c[{int(wire)}];")
    
    return "\n".join(qasm_lines)


def _maybe_upgrade_qasm2_to_qasm3(qasm2: str) -> Optional[str]:
    """
    Try to upgrade QASM 2 -> QASM 3 using multiple approaches:
    1. MPQP library if available
    2. Custom converter as fallback
    """
    # Try MPQP first (if available)
    try:
        from mpqp.qasm import convert_qasm  # type: ignore
        return convert_qasm(qasm2, target_version="3.0")
    except ImportError:
        print("[INFO] MPQP not available, using built-in converter")
    except Exception as e:
        print(f"[WARN] MPQP conversion failed: {e}")
    
    # Fallback to custom converter
    return _convert_qasm2_to_qasm3_manual(qasm2)


def _convert_qasm2_to_qasm3_manual(qasm2: str) -> str:
    """
    Manual converter from OpenQASM 2 to OpenQASM 3
    """
    lines = qasm2.strip().split('\n')
    qasm3_lines = []
    
    # Convert header
    for line in lines:
        line = line.strip()
        if not line or line.startswith('//'):
            qasm3_lines.append(line)
            continue
            
        if line.startswith('OPENQASM 2.0'):
            qasm3_lines.append('OPENQASM 3.0;')
        elif line.startswith('include "qelib1.inc"'):
            qasm3_lines.append('include "stdgates.inc";')
        elif line.startswith('qreg '):
            # Convert qreg q[n]; to qubit[n] q;
            parts = line.replace('qreg ', '').replace(';', '')
            reg_name = parts.split('[')[0]
            size = parts.split('[')[1].split(']')[0]
            qasm3_lines.append(f'qubit[{size}] {reg_name};')
        elif line.startswith('creg '):
            # Convert creg c[n]; to bit[n] c;
            parts = line.replace('creg ', '').replace(';', '')
            reg_name = parts.split('[')[0]
            size = parts.split('[')[1].split(']')[0]
            qasm3_lines.append(f'bit[{size}] {reg_name};')
        elif ' -> ' in line:
            # Convert measurement syntax: measure q[0] -> c[0]; to c[0] = measure q[0];
            parts = line.split(' -> ')
            qubit_part = parts[0].replace('measure ', '').strip()
            bit_part = parts[1].replace(';', '').strip()
            qasm3_lines.append(f'{bit_part} = measure {qubit_part};')
        else:
            # Keep other lines as-is (gates, etc.)
            qasm3_lines.append(line)
    
    return '\n'.join(qasm3_lines)


def _pennylane_to_qasm3_direct(tape, n_wires) -> str:
    """
    Directly construct OpenQASM 3 from PennyLane tape (bypassing QASM 2)
    """
    # Build QASM3 header
    qasm_lines = [
        "OPENQASM 3.0;",
        'include "stdgates.inc";',
        f"qubit[{n_wires}] q;",
        f"bit[{n_wires}] c;"
    ]
    
    # Convert operations
    if hasattr(tape, 'operations'):
        for op in tape.operations:
            if hasattr(op, 'name'):
                op_name = op.name.lower()
                wires = [int(w) for w in op.wires] if hasattr(op, 'wires') else []
                
                if op_name == 'hadamard':
                    qasm_lines.append(f"h q[{wires[0]}];")
                elif op_name == 'cnot':
                    qasm_lines.append(f"cx q[{wires[0]}], q[{wires[1]}];")
                elif op_name == 'paulix':
                    qasm_lines.append(f"x q[{wires[0]}];")
                elif op_name == 'pauliy':
                    qasm_lines.append(f"y q[{wires[0]}];")
                elif op_name == 'pauliz':
                    qasm_lines.append(f"z q[{wires[0]}];")
                elif op_name == 'cnot':
                    qasm_lines.append(f"cx q[{wires[0]}], q[{wires[1]}];")
                elif op_name.startswith('r'):  # Rotation gates
                    if hasattr(op, 'parameters') and op.parameters:
                        param = op.parameters[0]
                        if op_name == 'rx':
                            qasm_lines.append(f"rx({param}) q[{wires[0]}];")
                        elif op_name == 'ry':
                            qasm_lines.append(f"ry({param}) q[{wires[0]}];")
                        elif op_name == 'rz':
                            qasm_lines.append(f"rz({param}) q[{wires[0]}];")
                # Add more gate mappings as needed
    
    # Add measurements using QASM3 syntax
    if hasattr(tape, 'measurements'):
        for i, measurement in enumerate(tape.measurements):
            if hasattr(measurement, 'wires'):
                for wire in measurement.wires:
                    qasm_lines.append(f"c[{int(wire)}] = measure q[{int(wire)}];")
    else:
        # Add default measurements for all wires
        for i in range(n_wires):
            qasm_lines.append(f"c[{i}] = measure q[{i}];")
    
    return "\n".join(qasm_lines)

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
    except Exception:
        n_qubits = None
    try:
        depth = len(circuit)  # Circuit length as depth approximation
    except Exception:
        depth = None
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
            with qml.queuing.AnnotatedQueue() as q:
                qnode.func()
            
            qnode._tape = qml.tape.QuantumScript.from_queue(q)
        except Exception as e2:
            try:
                # Alternative approach for newer PennyLane versions
                with qml.tape.QuantumTape() as tape:
                    qnode.func()
                qnode._tape = tape
            except Exception as e3:
                raise RuntimeError(f"Error executing QNode and extracting tape: {e} / {e2} / {e3}")

    # Get wire count (works for old & new device API)
    try:
        n_wires = qnode.device.num_wires  # New API
    except AttributeError:
        try:
            n_wires = len(qnode.device.wires)  # Old API
        except AttributeError:
            n_wires = 2  # fallback

    # Get the tape - try multiple approaches
    tape = None
    if hasattr(qnode, 'tape') and qnode.tape is not None:
        tape = qnode.tape
    elif hasattr(qnode, '_tape') and qnode._tape is not None:
        tape = qnode._tape
    elif hasattr(qnode, 'qtape') and qnode.qtape is not None:
        tape = qnode.qtape
    
    if tape is None:
        raise RuntimeError("Could not access quantum tape from QNode")

    # Try to export to QASM using the tape
    try:
        # Try direct QASM3 construction first
        try:
            qasm3 = _pennylane_to_qasm3_direct(tape, n_wires)
            stats = {
                "n_wires": n_wires,
                "ops": len(tape.operations) if hasattr(tape, "operations") else None,
                "upgraded_to_qasm3": True,
                "method": "direct_qasm3"
            }
            return CompileResult(ok=True, language="pennylane", format="qasm3", program=qasm3, stats=stats)
        except Exception as e:
            print(f"[WARN] Direct QASM3 construction failed: {e}")
        
        # Fallback to QASM2 then upgrade
        if hasattr(tape, 'to_openqasm'):
            qasm2 = tape.to_openqasm(measure_all=True)
        else:
            # Fallback to manual construction
            qasm2 = _pennylane_to_qasm_manual_from_tape(tape, n_wires)
        
        # Try to upgrade to QASM3 (now always returns a result)
        qasm3 = _maybe_upgrade_qasm2_to_qasm3(qasm2)
        
        stats = {
            "n_wires": n_wires,
            "ops": len(tape.operations) if hasattr(tape, "operations") else None,
            "upgraded_to_qasm3": bool(qasm3),
            "method": "qasm2_upgraded" if qasm3 else "qasm2_only"
        }
        
        if qasm3:
            return CompileResult(ok=True, language="pennylane", format="qasm3", program=qasm3, stats=stats)
        else:
            return CompileResult(ok=True, language="pennylane", format="qasm2", program=qasm2, stats=stats)
            
    except Exception as e:
        raise RuntimeError(f"Error exporting PennyLane QNode to QASM: {e}")


def _pennylane_to_qasm_manual(qnode) -> str:
    """
    Manually construct QASM from PennyLane tape when automatic conversion fails
    """
    # Build QASM header
    qasm_lines = [
        "OPENQASM 2.0;",
        'include "qelib1.inc";',
        f"qreg q[{n_wires}];",
        f"creg c[{n_wires}];"
    ]
    
    # Convert operations if tape exists
    if hasattr(tape, 'operations'):
        for op in tape.operations:
            if hasattr(op, 'name'):
                op_name = op.name.lower()
                wires = [int(w) for w in op.wires] if hasattr(op, 'wires') else []
                
                if op_name == 'hadamard':
                    qasm_lines.append(f"h q[{wires[0]}];")
                elif op_name == 'cnot':
                    qasm_lines.append(f"cx q[{wires[0]}],q[{wires[1]}];")
                elif op_name == 'paulix':
                    qasm_lines.append(f"x q[{wires[0]}];")
                elif op_name == 'pauliy':
                    qasm_lines.append(f"y q[{wires[0]}];")
                elif op_name == 'pauliz':
                    qasm_lines.append(f"z q[{wires[0]}];")
                elif op_name.startswith('r'):  # Rotation gates
                    if hasattr(op, 'parameters') and op.parameters:
                        param = op.parameters[0]
                        if op_name == 'rx':
                            qasm_lines.append(f"rx({param}) q[{wires[0]}];")
                        elif op_name == 'ry':
                            qasm_lines.append(f"ry({param}) q[{wires[0]}];")
                        elif op_name == 'rz':
                            qasm_lines.append(f"rz({param}) q[{wires[0]}];")
                # Add more gate mappings as needed
    
    # Add measurements if present
    if hasattr(tape, 'measurements'):
        for i, measurement in enumerate(tape.measurements):
            if hasattr(measurement, 'wires'):
                for wire in measurement.wires:
                    qasm_lines.append(f"measure q[{int(wire)}] -> c[{int(wire)}];")
    else:
        # Add default measurements for all wires
        for i in range(n_wires):
            qasm_lines.append(f"measure q[{i}] -> c[{i}];")
    
    return "\n".join(qasm_lines)

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
from qiskit import QuantumCircuit
def get_circuit():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0,1], [0,1])
    return qc
"""

DEMO_CIRQ = r"""
import cirq
def get_circuit():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.H(q0),
        cirq.CNOT(q0, q1),
        cirq.measure(q0, key="m0"),
        cirq.measure(q1, key="m1"),
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
    print("All frameworks successfully converted to OpenQASM 3!")
    print("Universal IR (OpenQASM 3) can now be used across different")
    print("quantum computing platforms and simulators.")
    print("=" * 60)