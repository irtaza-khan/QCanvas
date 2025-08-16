#!/usr/bin/env python3
"""
Debug script to test the quantum converters directly
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_qiskit_converter():
    """Test the Qiskit converter directly"""
    print("🔍 Testing Qiskit Converter...")
    
    # Sample Qiskit code
    qiskit_code = '''
from qiskit import QuantumCircuit

def get_circuit():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc
'''
    
    try:
        from quantum_converters.converters.qiskit_to_qasm import convert_qiskit_to_qasm3
        print("✓ Qiskit converter imported successfully")
        
        print("🚀 Converting Qiskit code...")
        result = convert_qiskit_to_qasm3(qiskit_code)
        
        print(f"✓ Conversion successful!")
        print(f"Result type: {type(result)}")
        print(f"QASM code preview:\n{result.qasm_code[:200]}...")
        print(f"Stats: qubits={result.stats.n_qubits}, depth={result.stats.depth}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Conversion error: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_conversion_service():
    """Test the conversion service"""
    print("\n🔍 Testing Conversion Service...")
    
    qiskit_code = '''
from qiskit import QuantumCircuit

def get_circuit():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc
'''
    
    try:
        from backend.app.services.conversion_service import ConversionService
        print("✓ ConversionService imported successfully")
        
        service = ConversionService()
        print("✓ ConversionService instantiated")
        
        print("🚀 Converting via service...")
        result = service.convert_to_qasm(qiskit_code, "qiskit", "classic")
        
        print(f"✓ Service conversion result: {result.get('success', False)}")
        if result.get('success'):
            print(f"QASM preview: {result['qasm_code'][:100]}...")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Service error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🧪 QCanvas Converter Debug Test")
    print("=" * 50)
    
    # Test dependencies
    print("📦 Checking dependencies...")
    try:
        import qiskit
        print(f"✓ Qiskit version: {qiskit.__version__}")
    except ImportError:
        print("❌ Qiskit not installed")
        return False
    
    print("\n" + "=" * 50)
    
    # Test converter directly
    success1 = test_qiskit_converter()
    
    # Test conversion service
    success2 = test_conversion_service()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Direct converter: {'✓ PASS' if success1 else '❌ FAIL'}")
    print(f"Conversion service: {'✓ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! The converter should work.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    return success1 and success2

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
