# QCanvas Integration Test Commands

## 📋 Overview

This document provides comprehensive test commands for validating the QCanvas quantum circuit conversion system. All commands assume you're in the project root directory with the virtual environment activated.

## 🚀 Quick Setup

```bash
# Navigate to project directory
cd D:\University\Uni\FYP\QCanvas

# Activate virtual environment
.\qasm_env\Scripts\Activate.ps1

# Verify pytest is installed
pip list | findstr pytest
```

## 🧪 Test Categories

### 1. **Iteration I Tests** (Core Features)
Tests all OpenQASM 3.0 Iteration I features as defined in `docs/project-scope.md`

### 2. **Integration Tests** (Converter Integration)
Tests the integration of QASM3Builder with all three framework converters

### 3. **Demo Scripts** (Live Output)
Shows actual OpenQASM 3.0 output from each converter

---

## 🔬 Iteration I Tests

### Basic Commands
```bash
# Run all Iteration I tests
python -m pytest tests/iteration_1/test_iteration_i_features.py -v

# Run with detailed output
python -m pytest tests/iteration_1/test_iteration_i_features.py -vv --tb=short

# Run with line-by-line output
python -m pytest tests/iteration_1/test_iteration_i_features.py -v --tb=line
```

### Specific Test Categories
```bash
# Test comments and version control
python -m pytest tests/iteration_1/test_iteration_i_features.py::TestCommentsAndVersionControl -v

# Test types and casting
python -m pytest tests/iteration_1/test_iteration_i_features.py::TestTypesAndCasting -v

# Test gates and modifiers
python -m pytest tests/iteration_1/test_iteration_i_features.py::TestGatesAndModifiers -v

# Test quantum instructions
python -m pytest tests/iteration_1/test_iteration_i_features.py::TestBuiltInQuantumInstructions -v

# Test classical instructions
python -m pytest tests/iteration_1/test_iteration_i_features.py::TestClassicalInstructions -v

# Test scoping and variables
python -m pytest tests/iteration_1/test_iteration_i_features.py::TestScopingAndVariables -v

# Test standard library
python -m pytest tests/iteration_1/test_iteration_i_features.py::TestStandardLibraryAndBuiltins -v

# Test missing features (expected to fail)
python -m pytest tests/iteration_1/test_iteration_i_features.py::TestMissingFeatures -v
```

### Advanced Options
```bash
# Run only failed tests (if any)
python -m pytest tests/iteration_1/test_iteration_i_features.py --lf -v

# Run with coverage report
python -m pytest tests/iteration_1/test_iteration_i_features.py --cov=quantum_converters -v

# Run and stop on first failure
python -m pytest tests/iteration_1/test_iteration_i_features.py -x -v

# Run with performance profiling
python -m pytest tests/iteration_1/test_iteration_i_features.py --durations=10 -v
```

### Expected Results
```
✅ PASSED: 42 tests (core features implemented)
🟡 SKIPPED: 2 tests (concatenation features - deferred)
❌ XFAIL: 4 tests (excluded features - expected to fail)

Total: 48 tests
Success Rate: 100% of implemented features
```

---

## 🔗 Integration Tests

### All Integration Tests
```bash
# Run all integration tests (Cirq, Qiskit, PennyLane)
python -m pytest tests/integration/ -v

# Run with detailed output
python -m pytest tests/integration/ -v --tb=short

# Run with line-by-line output
python -m pytest tests/integration/ -v --tb=line
```

### Individual Converter Tests
```bash
# Test Cirq converter integration
python -m pytest tests/integration/test_cirq_integration.py -v

# Test Qiskit converter integration
python -m pytest tests/integration/test_qiskit_integration.py -v

# Test PennyLane converter integration
python -m pytest tests/integration/test_pennylane_integration.py -v
```

### Specific Test Cases
```bash
# Test simple circuits
python -m pytest tests/integration/ -k "test_simple_circuit" -v

# Test parameterized gates
python -m pytest tests/integration/ -k "test_parameterized_gates" -v

# Test measurements
python -m pytest tests/integration/ -k "test_measurements" -v

# Test gate modifiers
python -m pytest tests/integration/ -k "test_inverse_modifier" -v

# Test statistics
python -m pytest tests/integration/ -k "test_statistics" -v

# Test multi-qubit gates
python -m pytest tests/integration/ -k "test_multiple_qubit_gates" -v
```

### Expected Results
```
✅ Cirq Integration: 7/7 tests passing
✅ Qiskit Integration: 8/8 tests passing  
✅ PennyLane Integration: 7/7 tests passing

Total: 22 tests
Success Rate: 100%
```

---

## 🎬 Demo Scripts

### Run All Demos
```bash
# Cirq demo - shows actual OpenQASM 3.0 output
python tests/integration/demo_cirq_output.py

# Qiskit demo - shows actual OpenQASM 3.0 output
python tests/integration/demo_qiskit_output.py

# PennyLane demo - shows actual OpenQASM 3.0 output
python tests/integration/demo_pennylane_output.py
```

### What Each Demo Shows

**Cirq Demo** (`demo_cirq_output.py`):
- Bell state circuit with H and CNOT gates
- Parameterized rotations (RX, RY, RZ)
- Inverse gate modifiers (inv@)
- Multi-qubit gates (Toffoli, CZ, SWAP)
- Complete OpenQASM 3.0 structure with constants and variables

**Qiskit Demo** (`demo_qiskit_output.py`):
- Bell state with measurements and classical bits
- Parameterized rotations with mathematical constants
- Inverse gate modifiers (sdg, tdg)
- Multi-qubit gates (Toffoli, CZ, SWAP)
- Control flow examples (if statements, for loops)

**PennyLane Demo** (`demo_pennylane_output.py`):
- Quantum teleportation setup
- Parameterized rotations (RX, RY, RZ)
- Multi-qubit gates (CZ, SWAP, Toffoli)
- Complete circuit statistics and gate counts

---

## 🎯 Complete Test Suite

### Run Everything
```bash
# Run all tests (Iteration I + Integration)
python -m pytest tests/iteration_1/ tests/integration/ -v

# Run with summary output
python -m pytest tests/iteration_1/ tests/integration/ -v --tb=line -q

# Run and stop on first failure
python -m pytest tests/iteration_1/ tests/integration/ -v -x
```

### Comprehensive Analysis
```bash
# Run with coverage report
python -m pytest tests/iteration_1/ tests/integration/ --cov=quantum_converters -v

# Run with performance profiling
python -m pytest tests/iteration_1/ tests/integration/ --durations=10 -v

# Run with HTML coverage report
python -m pytest tests/iteration_1/ tests/integration/ --cov=quantum_converters --cov-report=html -v
```

### Expected Complete Results
```
Iteration I Tests: 42 passed, 2 skipped, 4 xfailed
Integration Tests: 22 passed
Total: 64 tests
Success Rate: 100% for implemented features
```

---

## 🔍 Debugging Commands

### Verbose Output
```bash
# Maximum verbosity
python -m pytest tests/iteration_1/ tests/integration/ -vvv

# Show local variables on failure
python -m pytest tests/iteration_1/ tests/integration/ -v --tb=long

# Show captured output
python -m pytest tests/iteration_1/ tests/integration/ -v -s
```

### Specific Test Debugging
```bash
# Run only one specific test
python -m pytest tests/integration/test_cirq_integration.py::TestCirqIntegration::test_simple_circuit -v -s

# Run with print statements visible
python -m pytest tests/integration/demo_cirq_output.py -v -s

# Run with pdb debugger on failure
python -m pytest tests/iteration_1/ tests/integration/ --pdb -v
```

### Performance Analysis
```bash
# Show slowest tests
python -m pytest tests/iteration_1/ tests/integration/ --durations=0 -v

# Run with memory profiling
python -m pytest tests/iteration_1/ tests/integration/ --profile -v

# Run with timing
python -m pytest tests/iteration_1/ tests/integration/ --timeout=30 -v
```

---

## 📊 Test Results Interpretation

### Success Indicators
- ✅ **PASSED**: Feature implemented and working correctly
- 🟡 **SKIPPED**: Feature partially implemented or deferred
- ❌ **XFAIL**: Feature intentionally excluded (expected to fail)

### Failure Indicators
- ❌ **FAILED**: Unexpected failure - needs investigation
- ⚠️ **ERROR**: Test setup or execution error
- 🔄 **RETRY**: Test flaky or timing-dependent

### Coverage Metrics
- **Line Coverage**: Percentage of code lines executed
- **Branch Coverage**: Percentage of code branches tested
- **Function Coverage**: Percentage of functions called

---

## 🚀 Continuous Integration

### Pre-commit Testing
```bash
# Quick smoke test
python -m pytest tests/integration/ -x -v

# Full validation
python -m pytest tests/iteration_1/ tests/integration/ -v

# Performance check
python -m pytest tests/iteration_1/ tests/integration/ --durations=10 -v
```

### Release Testing
```bash
# Complete test suite with coverage
python -m pytest tests/iteration_1/ tests/integration/ --cov=quantum_converters --cov-report=html --cov-report=term -v

# Run all demo scripts
python tests/integration/demo_cirq_output.py
python tests/integration/demo_qiskit_output.py
python tests/integration/demo_pennylane_output.py
```

---

## 📝 Notes

### Test Environment
- **Python**: 3.13.2
- **Pytest**: 8.4.1
- **Virtual Environment**: `qasm_env`
- **Platform**: Windows 10

### Dependencies
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `cirq` - Cirq framework
- `qiskit` - Qiskit framework
- `pennylane` - PennyLane framework

### File Locations
- **Iteration I Tests**: `tests/iteration_1/test_iteration_i_features.py`
- **Integration Tests**: `tests/integration/test_*_integration.py`
- **Demo Scripts**: `tests/integration/demo_*_output.py`
- **Documentation**: `tests/iteration_1/README.md`, `tests/integration/INTEGRATION_SUMMARY.md`

---

## 🎉 Success Criteria

The QCanvas integration is successful when:

- ✅ **All Iteration I tests pass** (42/42 implemented features)
- ✅ **All integration tests pass** (22/22 converter tests)
- ✅ **Demo scripts produce valid OpenQASM 3.0**
- ✅ **No unexpected failures or errors**
- ✅ **Coverage >80% for core components**

**Current Status: 100% Success Rate** 🎊

---

*For questions or issues, refer to the main project documentation or contact the development team.*
