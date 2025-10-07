from quantum_converters.config import (
    PENNYLANE_TO_QASM_REGISTRY,
    get_pl_to_qasm_mapping,
    get_pl_inverse_qasm_map,
    QISKIT_TO_QASM_REGISTRY,
    get_qiskit_inverse_qasm_map,
    CIRQ_TO_QASM_REGISTRY,
    get_cirq_inverse_qasm_map,
)


def test_pl_registry_basic_shape():
    reg = PENNYLANE_TO_QASM_REGISTRY
    assert reg.framework == "pennylane"
    m = reg.mapping
    assert "x" in m and m["x"].openqasm_gate == "x"
    assert "rx" in m and m["rx"].param_order == ["theta"]


def test_pl_mapping_readonly_views():
    m = get_pl_to_qasm_mapping()
    assert m["cx"].target_gate == "CNOT"
    inv = get_pl_inverse_qasm_map()
    # Inverse of target gate names map back to OpenQASM
    assert inv["CNOT"] == "cx"


def test_qiskit_registry_and_inverse():
    reg = QISKIT_TO_QASM_REGISTRY
    assert reg.mapping["u"].param_order == ["theta", "phi", "lambda"]
    inv = get_qiskit_inverse_qasm_map()
    assert inv["rx"] == "rx"


def test_cirq_registry_and_inverse():
    reg = CIRQ_TO_QASM_REGISTRY
    assert reg.mapping["rx"].param_order == ["theta"]
    inv = get_cirq_inverse_qasm_map()
    assert inv["CNOT"] == "cx"


