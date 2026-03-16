"""
Gate Mappings Configuration Module

WHAT THIS FILE DOES:
    Defines centralized gate name mappings between framework-specific gate names
    and OpenQASM 3.0 gate mnemonics. Provides registry structures for Qiskit, Cirq,
    and PennyLane frameworks. Includes helper functions to access mappings and
    inverse mappings (framework gate name → OpenQASM mnemonic).

HOW IT LINKS TO OTHER FILES:
    - Used by: All converter classes (qiskit_to_qasm.py, cirq_to_qasm.py, pennylane_to_qasm.py)
               for gate name translation
    - Used by: All parser classes for mapping framework gates to OpenQASM names
    - Uses: schemas.py (FrameworkGateRegistry, GateMap data structures)
    - Part of: Config module providing centralized configuration

INPUT:
    - Framework gate names: Framework-specific gate identifiers (e.g., "PauliX", "Hadamard")
    - Used in: get_*_inverse_qasm_map() functions, registry access

OUTPUT:
    - Gate mappings: FrameworkGateRegistry instances for each framework
    - Inverse mappings: Dict[str, str] mapping framework gate names to OpenQASM mnemonics
    - Returned by: get_qiskit_inverse_qasm_map(), get_cirq_inverse_qasm_map(),
                   get_pl_inverse_qasm_map() functions

STAGE OF USE:
    - Configuration Stage: Loaded at module import time
    - Conversion Stage: Used during gate name translation
    - Parsing Stage: Used when mapping parsed gates to OpenQASM names
    - Used throughout: Anywhere gate name translation is needed

TOOLS USED:
    - typing.Mapping, Dict: Type hints for mapping structures
    - pydantic: FrameworkGateRegistry and GateMap use Pydantic models (from schemas.py)

MAPPING STRUCTURE:
    - QISKIT_TO_QASM_REGISTRY: Maps Qiskit gate IDs to GateMap (with OpenQASM names)
    - CIRQ_TO_QASM_REGISTRY: Maps Cirq gate IDs to GateMap
    - PENNYLANE_TO_QASM_REGISTRY: Maps PennyLane gate IDs to GateMap
    - Inverse maps: Framework gate names → OpenQASM mnemonics (for parsers)

ARCHITECTURE ROLE:
    Centralized gate mapping configuration. Ensures consistent gate name translation
    across all converters and parsers. Single source of truth for framework-to-OpenQASM
    gate mappings.

Author: QCanvas Team
Date: 2025-08-08
Version: 1.0.0
"""

from typing import Mapping, Dict
from .schemas import FrameworkGateRegistry, GateMap


# PennyLane → OpenQASM 3 (Iteration I + Iteration II gates)
_PENNYLANE_TO_QASM = FrameworkGateRegistry(
    framework="pennylane",
    mapping={
        # Single-qubit Pauli gates
        "x": GateMap(openqasm_gate="x", target_gate="PauliX"),
        "y": GateMap(openqasm_gate="y", target_gate="PauliY"),
        "z": GateMap(openqasm_gate="z", target_gate="PauliZ"),

        # Single-qubit gates
        "h": GateMap(openqasm_gate="h", target_gate="Hadamard"),
        "s": GateMap(openqasm_gate="s", target_gate="S"),
        "t": GateMap(openqasm_gate="t", target_gate="T"),
        "id": GateMap(openqasm_gate="id", target_gate="Identity"),

        # Parameterized single-qubit gates
        "rx": GateMap(openqasm_gate="rx", target_gate="RX", param_order=["theta"]),
        "ry": GateMap(openqasm_gate="ry", target_gate="RY", param_order=["theta"]),
        "rz": GateMap(openqasm_gate="rz", target_gate="RZ", param_order=["lambda"]),
        "p": GateMap(openqasm_gate="p", target_gate="PhaseShift", param_order=["lambda"]),

        # Two-qubit gates (Iteration I)
        "cx": GateMap(openqasm_gate="cx", target_gate="CNOT"),
        "cz": GateMap(openqasm_gate="cz", target_gate="CZ"),
        "swap": GateMap(openqasm_gate="swap", target_gate="SWAP"),

        # Iteration II: Controlled two-qubit gates
        "cy": GateMap(openqasm_gate="cy", target_gate="CY"),
        "ch": GateMap(openqasm_gate="ch", target_gate="ControlledHadamard"),
        "crx": GateMap(openqasm_gate="crx", target_gate="CRX", param_order=["theta"]),
        "cry": GateMap(openqasm_gate="cry", target_gate="CRY", param_order=["theta"]),
        "crz": GateMap(openqasm_gate="crz", target_gate="CRZ", param_order=["lambda"]),
        "cp": GateMap(openqasm_gate="cp", target_gate="ControlledPhaseShift", param_order=["lambda"]),

        # Three-qubit gates (Iteration I)
        "ccx": GateMap(openqasm_gate="ccx", target_gate="Toffoli"),
        
        # Iteration II: Three-qubit gates
        "cswap": GateMap(openqasm_gate="cswap", target_gate="CSWAP"),
        "ccz": GateMap(openqasm_gate="ccz", target_gate="CCZ"),
        
        # Iteration II: Global phase
        "gphase": GateMap(openqasm_gate="gphase", target_gate="GlobalPhase", param_order=["gamma"]),

        # Grover and Multi-controlled (Common in algorithms)
        "mcx": GateMap(openqasm_gate="mcx", target_gate="MultiControlledX"),
        "grover": GateMap(openqasm_gate="grover", target_gate="GroverOperator"),
    },
)


# Expose read-only mapping and a helper accessor
PENNYLANE_TO_QASM_REGISTRY: FrameworkGateRegistry = _PENNYLANE_TO_QASM


def get_pl_to_qasm_mapping() -> Mapping[str, GateMap]:
    """Return a read-only view over the PennyLane → OpenQASM canonical mapping."""
    return PENNYLANE_TO_QASM_REGISTRY.mapping


_PL_INVERSE_QASM_MAP: Dict[str, str] = {
    # key: PennyLane target gate name, value: OpenQASM mnemonic
    gate_map.target_gate: gate_id for gate_id, gate_map in PENNYLANE_TO_QASM_REGISTRY.mapping.items()
}


def get_pl_inverse_qasm_map() -> Mapping[str, str]:
    """Return a read-only map of PennyLane gate name → OpenQASM mnemonic."""
    return _PL_INVERSE_QASM_MAP


# Qiskit → OpenQASM 3 (Iteration I)
_QISKIT_TO_QASM = FrameworkGateRegistry(
    framework="qiskit",
    mapping={
        # Single-qubit
        "h": GateMap(openqasm_gate="h", target_gate="h"),
        "x": GateMap(openqasm_gate="x", target_gate="x"),
        "y": GateMap(openqasm_gate="y", target_gate="y"),
        "z": GateMap(openqasm_gate="z", target_gate="z"),
        "s": GateMap(openqasm_gate="s", target_gate="s"),
        "t": GateMap(openqasm_gate="t", target_gate="t"),
        "sx": GateMap(openqasm_gate="sx", target_gate="sx"),
        "id": GateMap(openqasm_gate="id", target_gate="id"),
        # Param single-qubit
        "rx": GateMap(openqasm_gate="rx", target_gate="rx", param_order=["theta"]),
        "ry": GateMap(openqasm_gate="ry", target_gate="ry", param_order=["theta"]),
        "rz": GateMap(openqasm_gate="rz", target_gate="rz", param_order=["lambda"]),
        "p": GateMap(openqasm_gate="p", target_gate="p", param_order=["lambda"]),
        "u": GateMap(openqasm_gate="u", target_gate="u", param_order=["theta","phi","lambda"]),
        # Two-qubit
        "cx": GateMap(openqasm_gate="cx", target_gate="cx"),
        "cz": GateMap(openqasm_gate="cz", target_gate="cz"),
        "swap": GateMap(openqasm_gate="swap", target_gate="swap"),
        # Param two-qubit
        "crx": GateMap(openqasm_gate="crx", target_gate="crx", param_order=["theta"]),
        "cry": GateMap(openqasm_gate="cry", target_gate="cry", param_order=["theta"]),
        "crz": GateMap(openqasm_gate="crz", target_gate="crz", param_order=["lambda"]),
        "cp": GateMap(openqasm_gate="cp", target_gate="cp", param_order=["lambda"]),
        "cu": GateMap(openqasm_gate="cu", target_gate="cu", param_order=["theta", "phi", "lambda", "gamma"]),
        # Three-qubit
        "ccx": GateMap(openqasm_gate="ccx", target_gate="ccx"),
        # Special
        "gphase": GateMap(openqasm_gate="gphase", target_gate="gphase", param_order=["gamma"]),
    },
)

QISKIT_TO_QASM_REGISTRY: FrameworkGateRegistry = _QISKIT_TO_QASM
_QISKIT_INVERSE_QASM_MAP: Dict[str, str] = {
    # Here target_gate == qiskit name used in instruction.name in lowercase
    gate_map.target_gate: gate_id for gate_id, gate_map in QISKIT_TO_QASM_REGISTRY.mapping.items()
}


def get_qiskit_inverse_qasm_map() -> Mapping[str, str]:
    return _QISKIT_INVERSE_QASM_MAP


# Cirq → OpenQASM 3 (Iteration I)
_CIRQ_TO_QASM = FrameworkGateRegistry(
    framework="cirq",
    mapping={
        # Map to Cirq class-ish identifiers for readability; converters can resolve specifics
        "h": GateMap(openqasm_gate="h", target_gate="H"),
        "x": GateMap(openqasm_gate="x", target_gate="X"),
        "y": GateMap(openqasm_gate="y", target_gate="Y"),
        "z": GateMap(openqasm_gate="z", target_gate="Z"),
        "s": GateMap(openqasm_gate="s", target_gate="S"),
        "t": GateMap(openqasm_gate="t", target_gate="T"),
        "id": GateMap(openqasm_gate="id", target_gate="I"),
        "rx": GateMap(openqasm_gate="rx", target_gate="Rx", param_order=["theta"]),
        "ry": GateMap(openqasm_gate="ry", target_gate="Ry", param_order=["theta"]),
        "rz": GateMap(openqasm_gate="rz", target_gate="Rz", param_order=["lambda"]),
        "cx": GateMap(openqasm_gate="cx", target_gate="CNOT"),
        "cz": GateMap(openqasm_gate="cz", target_gate="CZ"),
        "swap": GateMap(openqasm_gate="swap", target_gate="SWAP"),
        "ccx": GateMap(openqasm_gate="ccx", target_gate="CCX"),
        "gphase": GateMap(openqasm_gate="gphase", target_gate="GlobalPhase", param_order=["gamma"]),
    },
)

CIRQ_TO_QASM_REGISTRY: FrameworkGateRegistry = _CIRQ_TO_QASM
_CIRQ_INVERSE_QASM_MAP: Dict[str, str] = {
    gate_map.target_gate: gate_id for gate_id, gate_map in CIRQ_TO_QASM_REGISTRY.mapping.items()
}


def get_cirq_inverse_qasm_map() -> Mapping[str, str]:
    return _CIRQ_INVERSE_QASM_MAP


