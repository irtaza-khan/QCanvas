# QCanvas Test Suite Overview

This document provides a detailed, comprehensive overview of the `tests` directory within the QCanvas quantum computing platform. The test suite is organized into clearly defined layers extending from granular unit tests up to complete end-to-end workflows, ensuring reliability and accuracy across different integrations and frameworks.

## Directory Structure Overview

The central `tests/` directory is primarily broken down into the following distinct categories:

- **`tests/unit/`**: Tests for isolated classes, functions, and models.
- **`tests/integration/`**: Verification of interactions between varied system components, external APIs, and quantum framework SDKs.
- **`tests/e2e/`**: Complete top-to-bottom testing of user workflows, encompassing frontend behavior and end-to-end processing pipelines.
- **`tests/iteration_1/`**: Dedicated suite isolating testing logic and documents relating specifically to the initial application iteration.
- **`tests/fixtures/`**: Static datasets, expected file outputs, and sample files used repeatedly within test environments.

---

## 1. Unit Testing Layer (`tests/unit/`)

Unit tests mock external dependencies, ensuring that independent pieces of logic operate precisely as intended. 

- **Framework Converters (`test_converters/`)**
  Validates logic isolating AST transversals and syntax generation for external simulators without invoking those external libraries.
  - `test_cirq_converter.py`, `test_pennylane_converter.py`, `test_qiskit_converter.py`: Provider-specific conversion.
  - `test_framework_converters.py`: Generalized cross-framework translation testing.
- **Simulator Operations (`test_simulator/`)**
  Isolates testing for the execution paths and states of internal backends vs external targets.
- **API Tests (`test_api/`)**
  Validates API endpoint responses and serializers based purely on mocked inputs.
- **Config & Infrastructure (`test_config_registries.py`)**
  Verifies that tool registries and settings map configuration values properly over internal data structures.

## 2. Integration Testing Layer (`tests/integration/`)

Focuses on accurate translations and state handling across QCanvas components and targeted actual framework environments (Qiskit, PennyLane, Cirq), confirming real behavior rather than mocked definitions.

- **Framework Integrations:**
  - `test_qiskit_integration.py`, `test_cirq_integration.py`, `test_pennylane_integration.py`: Endpoints translating internal OpenQASM 3.0 representations out to functioning external objects in actual software runtimes.
  - Generative outputs (`demo_cirq_output.py`, `demo_qiskit_output.py`, `demo_pennylane_output.py`) exist to demonstrate realistic use-cases.
- **Language Iteration Features:**
  - `test_iteration_ii_language_features.py` & `test_pennylane_iteration_ii.py`: Validating complex mathematical expressions, declarations, and iteration II OpenQASM syntax configurations.
  - `test_control_flow.py` & `test_gate_modifiers.py`: Evaluates logic structures spanning loops, conditional constraints, and complex gate manipulations natively required by quantum schemas.
- **Documentation:** Included in this module are localized guides (`INTEGRATION_SUMMARY.md`, `INTEGRATION_PROGRESS.md`) managing feature delivery and parity.

## 3. End-to-End (E2E) Testing Layer (`tests/e2e/`)

Simulates actions taking place from user interaction points straight down to the database/quantum processing, ensuring systemic stability.

- **`test_compilation_e2e.py`**: A massive test tracking compilation behaviors spanning initial OpenQASM input, systemic syntax checking, lexing, code-generation bounds, through to final executed outcomes.
- **`test_frontend_integration.py`**: Verifies the handshakes, WebSocket integrations, and API routes binding the web IDE UI to internal backend handlers. 
- **`test_user_workflows.py` & `test_complete_workflow.py`**: User journey testing mirroring standard application access behavior (e.g., login, compile code, execute circuit, track achievement). 

## 4. Iteration I Archive (`tests/iteration_1/`)

Serves as the testing bedrock that established parity during the initial development sprint. Features here focus heavily on early baseline metrics.

- `test_iteration_i_features.py`: The monolithic test suite evaluating the basic gate, bitwise, and compiler standards finalized during the project's opening stage.
- Also includes rich historical implementation context (`IMPLEMENTATION_STATUS.md`, `SUMMARY.md`, etc.).

## 5. Security & Infrastructure Shell

Crucial top-level infrastructure wrapping the execution paths.

- **`run_all_tests.py`**: The comprehensive runner enabling test suite execution by selective flags (e.g., `--category unit`, `--category integration`). 
- **`conftest.py`**: Pytest configurator initializing fixtures (database mock objects, authenticated client sessions, fake architectures) distributed globally across the suite.
- **`test_security.py`**: Validates the application’s outermost armor. Evaluates HTTP response headers (HSTS, CSP, X-Frame-Options) and ensures database `ApiActivity` auditing registers properly against API abuse or endpoint scanning.

## 6. Real-World Fixtures (`tests/fixtures/`)

Standardized static data repositories ensuring the testing layer does not drift.

- `sample_circuits/`: Houses standard input examples.
- `expected_outputs/`: Holds frozen JSON representations or structural text outputs of successful conversions. Tests load these to compare output artifacts dynamically, guaranteeing code refactors do not break expected logic.

---

## 7. Execution Metrics & Status

The QCanvas test suite utilizes heavily parametrized tests capable of multiplying core assertions across a massive volume of sample logic variations, generating large automated validation counts. 

**Latest Pytest Summary (`pytest tests/`)**
- **Passed:** 2359 validations
- **Skipped:** 30 (Primarily simulator backends skipped when explicit frameworks are not available locally: e.g., `test_quantum_simulator.py`)
- **XFail (Expected Failures):** 4
  - `test_physical_qubits_excluded` - Physical qubits are excluded in standard scopes.
  - `test_complex_type_not_in_iteration_i` - Acknowledged missing in Iteration I specs.
  - `test_duration_type_excluded` - Intentional omission.
  - `test_delay_instruction_excluded` - Intentional omission.
- **Warnings:** 2963 (Usually derived from OpenQASM token deprecations or downstream simulator module warnings)
- **Time Elapsed:** ~168.05 seconds (0:02:48)

These metrics showcase the platform's intensive generative testing capability—executing thousands of logical permutations deep within compiling trees, lexing patterns, and AST boundaries to ensure absolute quantum semantic stability.
