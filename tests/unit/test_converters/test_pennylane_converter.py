# TODO: Implement tests
import pennylane as qml
import numpy as np

dev = qml.device('default.qubit', wires=3)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    qml.RX(np.pi/4, wires=0)
    qml.RY(np.pi/2, wires=1)
    qml.CNOT(wires=[0, 1])
    qml.RZ(np.pi/3, wires=2)
    qml.CZ(wires=[1, 2])
    return qml.expval(qml.PauliZ(0))
