# Temporary file to compare gate handling in cirq_to_qasm_new.py and cirq_to_qasm.py

# Gate handling in cirq_to_qasm_new.py (_add_ast_operation method)
cirq_to_qasm_new_gates = [
    'h', 'x', 'y', 'z', 's', 't', 'sx', 'i',
    'rx', 'ry', 'rz',
    'cx', 'cnot', 'cz', 'cy', 'ch', 'swap',
]

# Gate handling in cirq_to_qasm.py (_add_cirq_operation method)
cirq_to_qasm_gates = [
    'HPowGate', '_H', 'XPowGate', '_PauliX', '_X', 'YPowGate', '_PauliY', '_Y',
    'ZPowGate', '_PauliZ', '_Z', 'SPowGate', '_S', 'TPowGate', '_T',
    'CNotPowGate', 'CXPowGate', '_CNOT', 'CZPowGate', '_CZ', 'SwapPowGate', '_SWAP',
    'Rx', 'Ry', 'Rz', 'PhasedXPowGate', 'MatrixGate', 'MeasurementGate',
    'ResetChannel', '_ResetGate', 'IdentityGate', 'ControlledGate', 'GlobalPhaseGate'
]

# Differences:
# cirq_to_qasm_new.py uses simplified gate names (e.g., 'h', 'x', 'cx')
# cirq_to_qasm.py uses Cirq internal gate class names (e.g., 'HPowGate', 'XPowGate')

# Next step: Map cirq_to_qasm.py gate classes to cirq_to_qasm_new.py gate names and add missing support in cirq_to_qasm_new.py

print("Comparison done. Ready to update cirq_to_qasm_new.py with missing gates.")
