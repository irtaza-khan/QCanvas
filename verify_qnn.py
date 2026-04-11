import pennylane as qml
import numpy as np
from quantum_converters.parsers.pennylane_parser import PennyLaneASTParser

def test_pennylane_qnn_substitution():
    code = """
import pennylane as qml
import numpy as np

def quantum_neural_network(inputs, weights):
    n_qubits = 2
    n_layers = 2
    for i in range(n_qubits):
        qml.RX(inputs[i], wires=i)
    
    for layer in range(n_layers):
        for i in range(n_qubits):
            qml.RX(weights[layer, i, 0], wires=i)
            qml.RY(weights[layer, i, 1], wires=i)
            qml.RZ(weights[layer, i, 2], wires=i)
    
    return [qml.expval(qml.PauliZ(i)) for i in range(2)]
"""
    parser = PennyLaneASTParser()
    circuit_ast = parser.parse(code)
    
    print("\nArray Parameters (Shapes):")
    print(circuit_ast.array_parameters)
    
    # Check that one of the gates has the correct substituted parameter
    found_3d = False
    for op in circuit_ast.operations:
        if hasattr(op, 'params'): # Older versions might use 'params', newer 'parameters'
            p = op.params
        else:
            p = op.parameters
            
        if any('weights[0, 1, 0]' in str(param) for param in p):
            found_3d = True
            print(f"DEBUG: Found substituted parameter in op: {op}")

    if found_3d and circuit_ast.array_parameters.get('weights') == [2, 2, 3]:
        print("\nSUCCESS: Multi-dimensional substitution and shape tracking verified!")
    else:
        print("\nFAILURE: Verification failed.")

if __name__ == "__main__":
    test_pennylane_qnn_substitution()
