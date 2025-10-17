# Complete Workflow: User Clicking "Convert to QASM" to QASM Output

This document details the full workflow in the QCanvas project starting from the user clicking the "Convert to QASM" button in the frontend, through all function calls, processing steps, and files involved, until the OpenQASM 3.0 code is generated and displayed.

---

## 1. User Action: Click "Convert to QASM" Button

**File:** `frontend/components/TopBar.tsx`

- The user clicks the "Compile to QASM" button.
- This triggers the `handleConvertToQASM` function.

### Key Function: `handleConvertToQASM`

- Reads the current active file content and framework from the Zustand store (`useFileStore`).
- Calls the frontend API function `quantumApi.convertToQasm(code, framework, style)`.

---

## 2. Frontend API Call: Convert to QASM

**File:** `frontend/lib/api.ts`

### Function: `convertToQasm`

- Sends a POST request to backend endpoint `/api/converter/convert`.
- Payload includes:
  - `code`: The quantum circuit source code (Qiskit, Cirq, PennyLane).
  - `framework`: The selected framework.
  - `style`: QASM output style (classic or compact).

---

## 3. Backend API Route: Conversion Request Handling

**File:** `backend/app/api/routes/converter.py`

### Endpoint: `POST /api/converter/convert`

- Receives the conversion request as a `ConversionRequest` Pydantic model.
- Validates the request (non-empty code, supported framework).
- Calls `ConversionService.convert_to_qasm(code, framework, style)`.

---

## 4. Backend Service: Conversion Logic

**File:** `backend/app/services/conversion_service.py`

### Method: `convert_to_qasm`

- Selects the appropriate converter based on the framework:
  - Qiskit: `quantum_converters.converters.qiskit_to_qasm.QiskitToQASM3Converter`
  - Cirq: `quantum_converters.converters.cirq_to_qasm.CirqToQASM3Converter`
  - PennyLane: `quantum_converters.converters.pennylane_to_qasm.PennylaneToQASM3Converter`
- Calls the converter's `convert(source_code)` method.
- Receives a `ConversionResult` containing:
  - `qasm_code`: The generated OpenQASM 3.0 code.
  - `stats`: Conversion statistics (qubits, depth, gate counts).
- Returns a dictionary with success status, QASM code, framework, version, and stats.

---

## 5. Converter: Qiskit to QASM Conversion (Example)

**File:** `quantum_converters/converters/qiskit_to_qasm.py`

### Class: `QiskitToQASM3Converter`

- `convert(qiskit_source: str) -> ConversionResult`
  - Attempts AST-based parsing using `QiskitASTParser` to build a circuit AST.
  - Analyzes the AST to extract statistics.
  - Converts AST to QASM using `QASM3Builder`.
  - If AST parsing fails, falls back to runtime execution of source code to get a `QuantumCircuit`.
  - Converts `QuantumCircuit` to QASM using `QASM3Builder`.

### Key Steps in Conversion

- **AST Parsing:** `QiskitASTParser.parse(source_code)`
- **Circuit Analysis:** `_analyze_circuit_ast(circuit_ast)`
- **QASM Generation:** `_convert_ast_to_qasm3(circuit_ast)`
- **Fallback Execution:** `_execute_qiskit_source(source_code)` and `_convert_to_qasm3(qc)`

---

## 6. QASM Code Generation

**File:** `quantum_converters/base/qasm3_builder.py`

### Class: `QASM3Builder`

- Builds OpenQASM 3.0 code with:
  - Header and includes
  - Qubit and classical bit register declarations
  - Variable declarations for parameters
  - Gate definitions and operations
  - Measurements, resets, barriers
- Formats parameters with mathematical constants (PI, E, etc.)
- Applies gate modifiers (control, inverse, power)
- Returns the complete QASM code string.

---

## 7. Backend Response

- The backend returns a `ConversionResponse` JSON with:
  - `success`: true/false
  - `qasm_code`: The generated OpenQASM 3.0 code (if success)
  - `conversion_stats`: Circuit statistics
  - `framework` and `qasm_version`

---

## 8. Frontend Handling of Response

**File:** `frontend/components/TopBar.tsx`

- Receives the response from the API.
- Updates the Zustand store with the compiled QASM code and stats.
- Triggers UI update to display the QASM code in the `ResultsPane` component.

---

## 9. Display QASM Code

**File:** `frontend/components/ResultsPane.tsx`

- The QASM code is displayed in the "OpenQASM" tab.
- User can view, copy, or download the generated QASM code.

---

## Summary of Key Files and Functions

| Step | File | Function/Class | Description |
|-------|-------|----------------|-------------|
| 1 | `frontend/components/TopBar.tsx` | `handleConvertToQASM` | User action triggers conversion |
| 2 | `frontend/lib/api.ts` | `convertToQasm` | Frontend API call to backend |
| 3 | `backend/app/api/routes/converter.py` | `convert_to_qasm` | API route handler |
| 4 | `backend/app/services/conversion_service.py` | `convert_to_qasm` | Service logic to select converter |
| 5 | `quantum_converters/converters/qiskit_to_qasm.py` | `QiskitToQASM3Converter.convert` | Conversion logic for Qiskit |
| 6 | `quantum_converters/base/qasm3_builder.py` | `QASM3Builder` | QASM code generation |
| 7 | `frontend/components/ResultsPane.tsx` | Render QASM code | Display generated QASM |
| 8 | `backend/app/api/routes/simulator.py` | `execute` | QSim execution endpoint for hybrid flow |

---

This workflow applies similarly for Cirq and PennyLane frameworks with their respective converters.

---

If you want, I can also provide a similar detailed workflow for the "Run" button or other features.
