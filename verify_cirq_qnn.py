import cirq
from quantum_converters.parsers.cirq_parser import CirqASTVisitor
import ast

def test_cirq_qnn_substitution():
    code = """
import cirq
import sympy

def create_circuit(weights):
    qubits = cirq.LineQubit.range(2)
    circuit = cirq.Circuit()
    for layer in range(2):
        for i in range(2):
            circuit.append(cirq.rx(weights[layer, i]).on(qubits[i]))
    return circuit
"""
    tree = ast.parse(code)
    visitor = CirqASTVisitor()
    visitor.visit(tree)
    
    print("\nArray Parameters (Shapes):")
    print(visitor.array_parameters)
    
    # Check if we saw substituted indices
    found = False
    for op in visitor.operations:
        if hasattr(op, 'parameters'):
            if any('weights[0, 1]' in str(p) for p in op.parameters):
                found = True
                print(f"DEBUG: Found substituted parameter in op: {op}")
    
    if found and visitor.array_parameters.get('weights') == [2, 2]:
         print("\nSUCCESS: Cirq multi-dimensional substitution verified!")
    else:
         print("\nFAILURE: Cirq verification failed.")

if __name__ == "__main__":
    test_cirq_qnn_substitution()
