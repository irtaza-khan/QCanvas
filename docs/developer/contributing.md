# Contributing to QCanvas

## Welcome Contributors! 🚀

Thank you for your interest in contributing to QCanvas! This guide will help you get started with contributing to the project, whether you're fixing bugs, adding features, improving documentation, or helping with testing.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Code Style and Standards](#code-style-and-standards)
4. [Testing Guidelines](#testing-guidelines)
5. [Documentation Guidelines](#documentation-guidelines)
6. [Submitting Changes](#submitting-changes)
7. [Review Process](#review-process)
8. [Release Process](#release-process)
9. [Community Guidelines](#community-guidelines)

## Getting Started

### Before You Begin

1. **Check Existing Issues**: Look through existing issues to see if your contribution is already being worked on
2. **Join Discussions**: Participate in GitHub Discussions to understand current priorities
3. **Read Documentation**: Familiarize yourself with the project structure and architecture
4. **Set Up Development Environment**: Follow the development setup guide below

### Types of Contributions

We welcome various types of contributions:

- **Bug Fixes**: Fix issues and improve stability
- **Feature Development**: Add new frameworks, backends, or features
- **Documentation**: Improve guides, tutorials, and API documentation
- **Testing**: Add tests, improve test coverage, or help with testing
- **Performance**: Optimize code, improve efficiency
- **UI/UX**: Enhance the frontend interface and user experience
- **DevOps**: Improve deployment, CI/CD, and infrastructure
- **Community**: Help with discussions, answer questions, mentor others

### Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Discord/Slack**: For real-time chat (links in project README)
- **Email**: For private or sensitive matters

## Development Setup

### Prerequisites

- **Python 3.8+**: Required for backend development
- **Node.js 16+**: Required for frontend development
- **Git**: For version control
- **Docker**: For containerized development (optional but recommended)
- **PostgreSQL**: For database development
- **Redis**: For caching and WebSocket sessions

### Local Development Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/qcanvas/qcanvas.git
cd qcanvas
```

#### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### 3. Set Up Frontend Environment

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

#### 4. Configure Environment

```bash
# Copy environment template
cp environment.env .env

# Edit .env with your settings
# Required settings:
# - DATABASE_URL
# - REDIS_URL
# - SECRET_KEY
```

#### 5. Set Up Database

```bash
# Using Docker (recommended)
docker-compose up -d postgres redis

# Or install locally
# PostgreSQL: https://www.postgresql.org/download/
# Redis: https://redis.io/download
```

#### 6. Run Migrations

```bash
# Initialize database
python -m alembic upgrade head
```

#### 7. Start Development Servers

```bash
# Terminal 1: Backend
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend && npm start

# Terminal 3: Database (if not using Docker)
# Start PostgreSQL and Redis services
```

### Docker Development Setup

For containerized development:

```bash
# Build and start all services
docker-compose up --build

# Access services
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Database: localhost:5432
# Redis: localhost:6379
```

### IDE Setup

#### VS Code Configuration

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

#### Recommended Extensions

- **Python**: Microsoft Python extension
- **Pylance**: Python language server
- **Black Formatter**: Code formatting
- **Flake8**: Linting
- **Prettier**: JavaScript/TypeScript formatting
- **ESLint**: JavaScript linting
- **GitLens**: Git integration

## Code Style and Standards

### Python Code Style

We follow PEP 8 with some modifications:

#### Formatting

- **Black**: Use Black for code formatting
- **Line Length**: 88 characters (Black default)
- **Import Sorting**: Use `isort` for import organization

```bash
# Format code
black backend/ quantum_converters/ quantum_simulator/

# Sort imports
isort backend/ quantum_converters/ quantum_simulator/
```

#### Naming Conventions

- **Classes**: PascalCase (e.g., `QuantumCircuit`)
- **Functions/Variables**: snake_case (e.g., `convert_circuit`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_QUBITS`)
- **Private Methods**: Leading underscore (e.g., `_internal_method`)

#### Type Hints

Use type hints for all function parameters and return values:

```python
from typing import Optional, List, Dict, Any

def convert_circuit(
    source_code: str,
    source_framework: str,
    target_framework: str,
    optimization_level: int = 1
) -> ConversionResult:
    """Convert quantum circuit between frameworks."""
    pass
```

#### Documentation

- **Docstrings**: Use Google-style docstrings
- **Comments**: Explain complex logic, not obvious code
- **README**: Keep updated with setup instructions

```python
def convert_circuit(source_code: str, target_framework: str) -> ConversionResult:
    """Convert quantum circuit to target framework.
    
    Args:
        source_code: Source circuit code
        target_framework: Target framework name
        
    Returns:
        ConversionResult: Conversion result with converted code
        
    Raises:
        ConversionError: If conversion fails
        ValidationError: If input validation fails
    """
    pass
```

### JavaScript/TypeScript Code Style

#### Formatting

- **Prettier**: Use Prettier for code formatting
- **ESLint**: Use ESLint for linting
- **TypeScript**: Use TypeScript for type safety

```bash
# Format code
npm run format

# Lint code
npm run lint

# Fix linting issues
npm run lint:fix
```

#### Naming Conventions

- **Components**: PascalCase (e.g., `CircuitEditor`)
- **Functions/Variables**: camelCase (e.g., `convertCircuit`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)
- **Files**: kebab-case (e.g., `circuit-editor.jsx`)

#### Component Structure

```jsx
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * Circuit editor component for quantum circuit input.
 */
const CircuitEditor = ({ initialCode, onCodeChange, framework }) => {
    const [code, setCode] = useState(initialCode);
    
    useEffect(() => {
        onCodeChange(code);
    }, [code, onCodeChange]);
    
    return (
        <div className="circuit-editor">
            <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder={`Enter ${framework} code...`}
            />
        </div>
    );
};

CircuitEditor.propTypes = {
    initialCode: PropTypes.string,
    onCodeChange: PropTypes.func.isRequired,
    framework: PropTypes.string.isRequired,
};

CircuitEditor.defaultProps = {
    initialCode: '',
};

export default CircuitEditor;
```

### Git Commit Standards

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### Commit Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

#### Examples

```bash
# Feature commit
git commit -m "feat(converter): add support for Braket framework"

# Bug fix commit
git commit -m "fix(simulator): resolve memory leak in statevector backend"

# Documentation commit
git commit -m "docs(api): update endpoint documentation"

# Test commit
git commit -m "test(converters): add unit tests for Cirq parser"
```

## Testing Guidelines

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_api/           # API tests
│   ├── test_converters/    # Converter tests
│   └── test_simulator/     # Simulator tests
├── integration/            # Integration tests
├── e2e/                   # End-to-end tests
└── fixtures/              # Test data and fixtures
```

### Writing Tests

#### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch
from quantum_converters.converters.cirq_to_qasm import CirqToQasmConverter

class TestCirqToQasmConverter:
    def setup_method(self):
        self.converter = CirqToQasmConverter()
    
    def test_convert_bell_state(self):
        """Test conversion of Bell state circuit."""
        # Arrange
        source_code = """
        import cirq
        q0, q1 = cirq.LineQubit.range(2)
        circuit = cirq.Circuit(
            cirq.H(q0),
            cirq.CNOT(q0, q1),
            cirq.measure(q0, q1)
        )
        """
        
        # Act
        result = self.converter.convert(source_code)
        
        # Assert
        assert result.success is True
        assert "OPENQASM 3.0" in result.qasm_code
        assert "h q[0]" in result.qasm_code
        assert "cx q[0], q[1]" in result.qasm_code
    
    def test_convert_invalid_code(self):
        """Test conversion with invalid code."""
        # Arrange
        invalid_code = "invalid python code"
        
        # Act & Assert
        with pytest.raises(ConversionError):
            self.converter.convert(invalid_code)
    
    @patch('quantum_converters.converters.cirq_to_qasm.cirq')
    def test_convert_with_mock_cirq(self, mock_cirq):
        """Test conversion with mocked Cirq."""
        # Arrange
        mock_cirq.LineQubit.range.return_value = [Mock(), Mock()]
        
        # Act
        result = self.converter.convert("import cirq")
        
        # Assert
        mock_cirq.LineQubit.range.assert_called_once_with(2)
```

#### Integration Tests

```python
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

class TestConversionAPI:
    def test_convert_circuit_endpoint(self):
        """Test circuit conversion endpoint."""
        # Arrange
        request_data = {
            "source_framework": "cirq",
            "target_framework": "qiskit",
            "source_code": "import cirq\nq0, q1 = cirq.LineQubit.range(2)",
            "optimization_level": 1
        }
        
        # Act
        response = client.post("/api/convert", json=request_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["source_framework"] == "cirq"
        assert data["target_framework"] == "qiskit"
        assert "converted_code" in data
    
    def test_convert_invalid_framework(self):
        """Test conversion with invalid framework."""
        # Arrange
        request_data = {
            "source_framework": "invalid",
            "target_framework": "qiskit",
            "source_code": "test code"
        }
        
        # Act
        response = client.post("/api/convert", json=request_data)
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
```

#### End-to-End Tests

```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestFrontendIntegration:
    def setup_method(self):
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:3000")
    
    def teardown_method(self):
        self.driver.quit()
    
    def test_circuit_conversion_workflow(self):
        """Test complete circuit conversion workflow."""
        # Navigate to converter
        self.driver.find_element(By.LINK_TEXT, "Circuit Converter").click()
        
        # Select source framework
        source_select = self.driver.find_element(By.ID, "source-framework")
        source_select.click()
        source_select.find_element(By.XPATH, "//option[text()='Cirq']").click()
        
        # Enter code
        code_editor = self.driver.find_element(By.ID, "code-editor")
        code_editor.clear()
        code_editor.send_keys("import cirq\nq0, q1 = cirq.LineQubit.range(2)")
        
        # Select target framework
        target_select = self.driver.find_element(By.ID, "target-framework")
        target_select.click()
        target_select.find_element(By.XPATH, "//option[text()='Qiskit']").click()
        
        # Convert
        convert_button = self.driver.find_element(By.ID, "convert-button")
        convert_button.click()
        
        # Wait for results
        wait = WebDriverWait(self.driver, 10)
        result_element = wait.until(
            EC.presence_of_element_located((By.ID, "conversion-result"))
        )
        
        # Verify results
        assert "from qiskit" in result_element.text
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with coverage
pytest --cov=backend --cov=quantum_converters --cov=quantum_simulator

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_converters/test_cirq_converter.py

# Run specific test function
pytest tests/unit/test_converters/test_cirq_converter.py::TestCirqToQasmConverter::test_convert_bell_state
```

### Test Coverage Requirements

- **Unit Tests**: Minimum 80% coverage
- **Integration Tests**: All API endpoints covered
- **E2E Tests**: Critical user workflows covered

## Documentation Guidelines

### Documentation Structure

```
docs/
├── api/                    # API documentation
│   ├── endpoints.md       # API endpoints reference
│   └── schemas.md         # Data schemas
├── user-guide/            # User documentation
│   ├── getting-started.md # Getting started guide
│   ├── examples.md        # Examples and tutorials
│   └── supported-frameworks.md # Framework documentation
├── developer/             # Developer documentation
│   ├── architecture.md    # System architecture
│   ├── contributing.md    # This file
│   └── adding-new-converter.md # How to add new converters
└── deployment/            # Deployment documentation
    ├── docker.md          # Docker deployment
    └── production.md      # Production deployment
```

### Writing Documentation

#### Style Guide

- **Clear and Concise**: Write clearly and avoid jargon
- **Examples**: Include practical examples
- **Code Blocks**: Use syntax highlighting
- **Links**: Link to related documentation
- **Images**: Include diagrams and screenshots when helpful

#### Markdown Standards

```markdown
# Main Heading

## Section Heading

### Subsection Heading

**Bold text** for emphasis
*Italic text* for terms
`code` for inline code

```python
# Code block with syntax highlighting
def example_function():
    return "Hello, World!"
```

> Blockquote for important notes

- List item 1
- List item 2
  - Nested list item

1. Numbered list item 1
2. Numbered list item 2

[Link text](URL)

![Alt text](image-url)
```

#### API Documentation

For API endpoints, include:

- **Endpoint URL**: Full URL with method
- **Request Body**: JSON schema with examples
- **Response**: JSON schema with examples
- **Error Codes**: Possible error responses
- **Authentication**: If required
- **Rate Limits**: If applicable

```markdown
### POST /api/convert

Convert a quantum circuit between frameworks.

**Request Body:**
```json
{
  "source_framework": "cirq",
  "target_framework": "qiskit",
  "source_code": "import cirq\nq0, q1 = cirq.LineQubit.range(2)",
  "optimization_level": 1
}
```

**Response:**
```json
{
  "success": true,
  "source_framework": "cirq",
  "target_framework": "qiskit",
  "converted_code": "from qiskit import QuantumCircuit...",
  "qasm_code": "OPENQASM 3.0;...",
  "execution_time": 0.125
}
```

**Error Responses:**
- `400 Bad Request`: Invalid input parameters
- `500 Internal Server Error`: Server error
```

## Submitting Changes

### Workflow

1. **Fork the Repository**: Create your own fork
2. **Create a Branch**: Create a feature branch
3. **Make Changes**: Implement your changes
4. **Test Your Changes**: Run tests and verify functionality
5. **Commit Your Changes**: Use conventional commit format
6. **Push to Your Fork**: Push your branch to your fork
7. **Create a Pull Request**: Submit a PR for review

### Creating a Pull Request

#### PR Template

```markdown
## Description

Brief description of the changes made.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass (if applicable)
- [ ] Manual testing completed

## Checklist

- [ ] Code follows the style guidelines
- [ ] Self-review of code completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Documentation is updated
- [ ] Changes generate no new warnings
- [ ] Tests are added that prove the fix is effective or that the feature works

## Screenshots (if applicable)

Add screenshots to help explain your changes.

## Additional Notes

Any additional information or context.
```

#### PR Guidelines

- **Clear Title**: Use conventional commit format
- **Detailed Description**: Explain what and why, not how
- **Related Issues**: Link to related issues
- **Screenshots**: Include for UI changes
- **Test Coverage**: Ensure adequate test coverage

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] No new warnings
- [ ] Self-review completed
- [ ] PR description is clear and complete

## Review Process

### Review Guidelines

#### For Contributors

- **Respond Promptly**: Respond to review comments quickly
- **Be Open to Feedback**: Accept constructive criticism
- **Explain Decisions**: Explain why you made certain choices
- **Update PR**: Make requested changes and update the PR

#### For Reviewers

- **Be Constructive**: Provide helpful, specific feedback
- **Focus on Code**: Review the code, not the person
- **Ask Questions**: If something is unclear, ask for clarification
- **Suggest Improvements**: Offer specific suggestions for improvement

### Review Checklist

- [ ] Code follows project standards
- [ ] Tests are adequate and pass
- [ ] Documentation is updated
- [ ] No security issues
- [ ] Performance is acceptable
- [ ] Error handling is appropriate
- [ ] Code is maintainable

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests
2. **Code Review**: At least one maintainer reviews
3. **Approval**: PR must be approved before merging
4. **Merge**: PR is merged after approval

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

### Release Steps

1. **Create Release Branch**: `release/v1.2.0`
2. **Update Version**: Update version in all files
3. **Update Changelog**: Document all changes
4. **Final Testing**: Run full test suite
5. **Create Release**: Create GitHub release
6. **Deploy**: Deploy to production
7. **Announce**: Announce release to community

### Release Checklist

- [ ] Version updated in all files
- [ ] Changelog updated
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Release notes written
- [ ] Deployment tested
- [ ] Community notified

## Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please read our [Code of Conduct](CODE_OF_CONDUCT.md).

### Communication

- **Be Respectful**: Treat others with respect
- **Be Helpful**: Help others when you can
- **Be Patient**: Everyone learns at their own pace
- **Be Constructive**: Provide constructive feedback

### Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Discord/Slack**: For real-time chat
- **Email**: For private matters

### Recognition

Contributors are recognized in several ways:

- **Contributors List**: GitHub automatically tracks contributors
- **Release Notes**: Contributors are mentioned in release notes
- **Documentation**: Contributors are credited in documentation
- **Community Events**: Recognition at community events

## Conclusion

Thank you for contributing to QCanvas! Your contributions help make quantum computing more accessible and powerful for everyone.

If you have any questions or need help getting started, don't hesitate to reach out to the community. We're here to help!

Happy coding! 🚀
