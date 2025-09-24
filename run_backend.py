#!/usr/bin/env python3
"""
QCanvas Backend Runner

This script starts the FastAPI backend server with proper environment setup.
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Set up the Python environment for running the backend."""
    # Get the project root directory
    project_root = Path(__file__).parent.absolute()
    
    # Add project root to Python path
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Set PYTHONPATH environment variable
    os.environ['PYTHONPATH'] = str(project_root)
    
    print(f"✓ Project root: {project_root}")
    print(f"✓ PYTHONPATH: {os.environ.get('PYTHONPATH')}")

def check_dependencies():
    """Check if required dependencies are available."""
    required_packages = [
        'fastapi',
        'uvicorn', 
        'qiskit',
        'cirq',
        'pennylane'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} (missing)")
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + ' '.join(missing_packages))
        return False
    
    return True

def test_converters():
    """Test if quantum converters can be imported."""
    try:
        from quantum_converters.converters.qiskit_to_qasm import convert_qiskit_to_qasm3
        from quantum_converters.converters.cirq_to_qasm import convert_cirq_to_qasm3
        from quantum_converters.converters.pennylane_to_qasm import convert_pennylane_to_qasm3
        print("✓ All quantum converters imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Converter import error: {e}")
        return False

def run_backend():
    """Start the FastAPI backend server."""
    try:
        # Change to backend directory
        backend_dir = Path(__file__).parent / "backend"
        os.chdir(backend_dir)
        
        print("\n🚀 Starting QCanvas Backend...")
        print("Backend will be available at: http://localhost:8000")
        print("API documentation: http://localhost:8000/docs")
        print("Press Ctrl+C to stop\n")
        
        # Start uvicorn server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Backend stopped")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return False
    
    return True

def main():
    """Main function to set up and run the backend."""
    print("🔧 QCanvas Backend Setup")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    print("\n📦 Checking Dependencies...")
    if not check_dependencies():
        print("\n❌ Please install missing dependencies before continuing.")
        return False
    
    print("\n🔌 Testing Quantum Converters...")
    if not test_converters():
        print("\n⚠️  Quantum converters have import issues, but backend will still start.")
        print("Some conversion features may not work correctly.")
    
    print("\n" + "=" * 50)
    
    # Run the backend
    return run_backend()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
