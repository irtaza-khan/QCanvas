@echo off
REM Cirq-RAG-Code-Assistant Development Environment Setup Script
REM For Windows with PyTorch CUDA support

echo 🚀 Setting up Cirq-RAG-Code-Assistant development environment...

REM Check Python version
echo [INFO] Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.11+ and try again.
    pause
    exit /b 1
)

REM Create virtual environment
echo [INFO] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [SUCCESS] Virtual environment created
) else (
    echo [WARNING] Virtual environment already exists
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

REM Install development dependencies
echo [INFO] Installing development dependencies...
pip install -e ".[dev,gpu,quantum]"

REM Install pre-commit hooks
echo [INFO] Installing pre-commit hooks...
pre-commit install
pre-commit install --hook-type pre-push

REM Create necessary directories
echo [INFO] Creating project directories...
if not exist "data\knowledge_base" mkdir "data\knowledge_base"
if not exist "data\datasets" mkdir "data\datasets"
if not exist "data\models" mkdir "data\models"
if not exist "outputs\logs" mkdir "outputs\logs"
if not exist "outputs\reports" mkdir "outputs\reports"
if not exist "outputs\artifacts" mkdir "outputs\artifacts"

REM Create .env file from template
echo [INFO] Creating initial configuration files...
if not exist ".env" (
    if exist "env.template" (
        copy "env.template" ".env" >nul
        echo [SUCCESS] Created .env file from template
    ) else (
        echo [WARNING] env.template not found, creating basic .env file
        echo # Cirq-RAG-Code-Assistant Environment Configuration > .env
        echo DEBUG=true >> .env
        echo ENVIRONMENT=development >> .env
        echo LOG_LEVEL=INFO >> .env
        echo LOG_FILE=outputs/logs/cirq_rag.log >> .env
        echo DATABASE_URL=sqlite:///data/cirq_rag.db >> .env
    )
) else (
    echo [WARNING] .env file already exists
)

REM Test PyTorch CUDA installation
echo [INFO] Testing PyTorch CUDA installation...
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA device: {torch.cuda.get_device_name(0)}' if torch.cuda.is_available() else '⚠️  CUDA device not available - running on CPU')"

REM Run basic tests
echo [INFO] Running basic tests...
python -m pytest tests\unit\test_basic.py -v

REM Final setup summary
echo.
echo [SUCCESS] 🎉 Development environment setup complete!
echo.
echo [INFO] Next steps:
echo   1. Activate the virtual environment: venv\Scripts\activate.bat
echo   2. Review and update .env file with your configuration
echo   3. Start implementing the RAG system: make dev-start
echo   4. Run tests: make test
echo   5. Check code quality: make lint
echo.
echo [INFO] Useful commands:
echo   - make help          # Show all available commands
echo   - make test          # Run all tests
echo   - make lint          # Run linting
echo   - make format        # Format code
echo   - make clean         # Clean build artifacts
echo.
echo [SUCCESS] Happy coding! 🚀
pause
