# TODO: Implement AST Parsing for Qiskit

## Tasks
- [x] Update `quantum_converters/converters/__init__.py` to import `convert_qiskit_to_qasm3` from `qiskit_to_qasm_new` instead of `qiskit_to_qasm`
- [x] Add VERBOSE variable for debugging in `quantum_converters/parsers/qiskit_parser.py` and descriptive print statements in AST parsing
- [x] Add logging in `QiskitASTParser.parse()` to confirm AST parsing usage
- [x] Add explanatory comments in `quantum_converters/converters/qiskit_to_qasm_new.py` contrasting AST vs exec approaches
- [x] Test the change by running a conversion to ensure it works
- [x] Verify AST usage via log messages and VERBOSE output
