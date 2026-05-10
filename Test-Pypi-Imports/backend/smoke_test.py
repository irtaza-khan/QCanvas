from pathlib import Path
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app import app


def main() -> None:
    client = TestClient(app)

    samples = {
        "cirq": """import cirq
from qcanvas import compile

def get_circuit():
    q0, q1 = cirq.LineQubit.range(2)
    return cirq.Circuit(
        cirq.H(q0),
        cirq.CNOT(q0, q1),
        cirq.measure(q0, q1, key='m')
    )
""",
        "qiskit": """from qiskit import QuantumCircuit
from qcanvas import compile

def get_circuit():
    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure([0, 1], [0, 1])
    return circuit
""",
        "pennylane": """import pennylane as qml
from qcanvas import compile

dev = qml.device('default.qubit', wires=2)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.expval(qml.PauliZ(0))
""",
    }

    for framework, code in samples.items():
        response = client.post("/compile", json={"code": code, "framework": framework})
        payload = response.json()
        print(framework, response.status_code, payload)
        assert response.status_code == 200
        assert payload["ok"] is True
        assert isinstance(payload["qasm"], str)


if __name__ == "__main__":
    main()
