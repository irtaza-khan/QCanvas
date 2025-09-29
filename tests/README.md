# QCanvas Test Suite

This directory contains comprehensive tests for the QCanvas quantum computing platform.

## Test Structure

```
tests/
├── README.md                    # This file
├── conftest.py                  # Pytest configuration and fixtures
├── run_all_tests.py            # Comprehensive test runner
├── unit/                       # Unit tests
│   ├── test_converters/       # Converter tests
│   │   └── test_framework_converters.py # Framework converter tests
│   ├── test_simulator/        # Quantum simulator tests
│   │   └── test_quantum_simulator.py # Simulator backend tests
│   └── test_api/              # API tests
│       └── test_api_routes.py # API route tests
├── integration/               # Integration tests
│   ├── test_api_integration.py # API integration tests
│   └── test_full_conversion.py # Full conversion workflow tests
├── e2e/                       # End-to-end tests
│   └── test_complete_workflow.py # Complete workflow tests
└── fixtures/                  # Test fixtures and data
    ├── sample_circuits/       # Sample quantum circuits
    └── expected_outputs/      # Expected test outputs
```

## Running Tests

### Using the Comprehensive Test Runner

```bash
# Run all tests
python run_tests.py

# Run specific test categories
python run_tests.py --category unit
python run_tests.py --category integration
python run_tests.py --category e2e

# Run specific test files
python run_tests.py --tests tests/unit/test_converters/test_qiskit_converter.py
python run_tests.py --tests tests/unit/test_converters/

# Run with options
python run_tests.py --verbosity 2 --failfast
```

### Using the Test Directory Runner

```bash
# Run all tests in the tests directory
python tests/run_all_tests.py

# Run specific categories
python tests/run_all_tests.py unit
python tests/run_all_tests.py integration
python tests/run_all_tests.py e2e
```

### Using unittest directly

```bash
# Run all tests
python -m unittest discover tests

# Run specific test modules
python -m unittest tests.unit.test_converters.test_qiskit_converter
python -m unittest tests.unit.test_converters.test_cirq_converter

# Run with verbose output
python -m unittest discover tests -v
```

### Using pytest

```bash
# Install pytest if not already installed
pip install pytest

# Run all tests
pytest tests/

# Run specific test categories
pytest tests/unit/ -m unit
pytest tests/integration/ -m integration
pytest tests/e2e/ -m e2e

# Run with markers
pytest tests/ -m "not slow"
pytest tests/ -m "unit and not slow"
```

## Test Categories

### Unit Tests (`tests/unit/`)

- **Converter Tests** (`test_converters/`)
  - `test_framework_converters.py`: Tests for framework converters (Qiskit, Cirq, PennyLane)

- **Simulator Tests** (`test_simulator/`)
  - `test_quantum_simulator.py`: Tests for quantum simulator backends

- **API Tests** (`test_api/`)
  - `test_api_routes.py`: Tests for API routes and endpoints

### Integration Tests (`tests/integration/`)

- `test_api_integration.py`: Tests for API integration and data flow
- `test_full_conversion.py`: Tests for complete conversion workflow

### End-to-End Tests (`tests/e2e/`)

- `test_complete_workflow.py`: Tests for complete user workflows

## Test Features

### Comprehensive Coverage

- **Lexical Analysis**: Tokenization of OpenQASM 3.0 source code
- **Parsing**: AST generation from token streams
- **Semantic Analysis**: Type checking and scope management
- **Code Generation**: Pretty-printing and roundtrip compilation
- **Error Handling**: Syntax and semantic error detection
- **Edge Cases**: Tricky scenarios and boundary conditions
- **Performance**: Large program handling and optimization

### Test Data and Fixtures

- **Sample Programs**: Various OpenQASM 3.0 programs for testing
- **Expected Outputs**: Reference outputs for validation
- **Error Cases**: Invalid programs for error handling tests
- **Performance Data**: Large programs for performance testing

### Test Utilities

- **Fixtures**: Reusable test components
- **Mock Objects**: Simulated dependencies
- **Test Data**: Sample inputs and expected outputs
- **Assertions**: Custom assertion methods

## Writing New Tests

### Unit Test Structure

```python
import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Import your test dependencies here
# from your_module import YourClass

class TestNewFeature(unittest.TestCase):
    """Test new feature functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize your test fixtures here
        pass
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        source = '''OPENQASM 3.0;
qubit q;
h q;'''
        
        result = self.compiler.compile(source)
        self.assertTrue(result.success)
    
    def test_edge_case(self):
        """Test edge case."""
        # Test implementation
        pass

if __name__ == '__main__':
    unittest.main()
```

### Integration Test Structure

```python
import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import your test dependencies here
# from your_module import YourClass

class TestFeatureIntegration(unittest.TestCase):
    """Test feature integration."""
    
    def test_complete_workflow(self):
        """Test complete workflow."""
        # Test complete workflow
        pass

if __name__ == '__main__':
    unittest.main()
```

### End-to-End Test Structure

```python
import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class TestCompleteWorkflow(unittest.TestCase):
    """Test complete user workflow."""
    
    def test_user_workflow(self):
        """Test complete user workflow."""
        # Test complete user workflow
        pass

if __name__ == '__main__':
    unittest.main()
```

## Test Configuration

### Pytest Configuration

The `conftest.py` file provides:
- **Fixtures**: Reusable test components
- **Markers**: Test categorization
- **Configuration**: Pytest settings

### Test Markers

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.e2e`: End-to-end tests
- `@pytest.mark.slow`: Slow-running tests

### Test Data

- **Sample Circuits**: Located in `tests/fixtures/sample_circuits/`
- **Expected Outputs**: Located in `tests/fixtures/expected_outputs/`
- **Test Fixtures**: Defined in `conftest.py`

## Continuous Integration

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: python run_tests.py
```

### Local Development

```bash
# Run tests before committing
python run_tests.py

# Run specific test categories
python run_tests.py --category unit
python run_tests.py --category integration

# Run with verbose output
python run_tests.py --verbosity 2
```

## Test Maintenance

### Adding New Tests

1. Create test file in appropriate directory
2. Follow naming convention: `test_*.py`
3. Use descriptive test method names
4. Add appropriate docstrings
5. Include both positive and negative test cases

### Updating Tests

1. Update test data when requirements change
2. Add new test cases for new features
3. Remove obsolete tests
4. Update expected outputs

### Test Documentation

1. Keep README.md updated
2. Document test data sources
3. Explain complex test scenarios
4. Provide examples for new test writers

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure project root is in Python path
2. **Missing Dependencies**: Install required packages
3. **Test Failures**: Check test data and expected outputs
4. **Performance Issues**: Use appropriate test markers

### Debugging Tests

```bash
# Run specific test with verbose output
python -m unittest tests.unit.test_converters.test_qiskit_converter -v

# Run with debug output
python -m unittest tests.unit.test_converters.test_qiskit_converter -v -s

# Run single test method
python -m unittest tests.unit.test_converters.test_qiskit_converter.TestQiskitConverter.test_basic_conversion
```

### Test Coverage

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run -m unittest discover tests
coverage report
coverage html
```

## Contributing

When contributing to the test suite:

1. **Follow the structure**: Place tests in appropriate directories
2. **Use descriptive names**: Make test names clear and informative
3. **Include docstrings**: Document what each test does
4. **Add fixtures**: Use fixtures for reusable test data
5. **Test edge cases**: Include boundary conditions and error cases
6. **Update documentation**: Keep this README updated

## Resources

- [Python unittest documentation](https://docs.python.org/3/library/unittest.html)
- [pytest documentation](https://docs.pytest.org/)
- [OpenQASM 3.0 specification](https://openqasm.com/)
- [QCanvas project documentation](../docs/)
