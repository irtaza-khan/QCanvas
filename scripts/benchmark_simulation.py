import sys
import os
import time
import asyncio
from typing import List

# Setup path to import backend modules
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(project_root, "backend"))

from app.services.simulation_service import SimulationService

def generate_qasm(qubits: int) -> str:
    """Generate a valid OpenQASM 3.0 string for N qubits (Superposition chain)"""
    qasm = "OPENQASM 3.0;\n"
    qasm += 'include "stdgates.inc";\n'
    qasm += f"qubit[{qubits}] q;\n"
    qasm += f"bit[{qubits}] c;\n"
    
    # Apply Hadamard to all
    for i in range(qubits):
        qasm += f"h q[{i}];\n"
        
    # Apply CNOT chain
    for i in range(qubits - 1):
        qasm += f"cx q[{i}], q[{i+1}];\n"
        
    return qasm

async def benchmark_simulation():
    service = SimulationService()
    
    print("\n" + "="*60)
    print(" Simulation Scalability Benchmark (Python Statevector)")
    print("="*60)
    print(f"{'Qubits':<8} | {'Backend':<12} | {'Time (ms)':>10} | {'Status'}")
    print("-" * 60)
    
    qubit_counts = [4, 8, 12, 16, 20]
    
    for n in qubit_counts:
        qasm_code = generate_qasm(n)
        
        start_time = time.perf_counter()
        try:
            # We explicitly use 'execute_qasm' (Legacy/Python) instead of 'execute_qasm_with_qsim'
            result = service.execute_qasm(qasm_code, backend="statevector", shots=1024)
            
            duration = (time.perf_counter() - start_time) * 1000
            
            status = "✅ OK" if result["success"] else f"❌ FAIL"
            print(f"{n:<8} | {'statevector':<12} | {duration:>10.2f} | {status}")
            
        except Exception as e:
            print(f"{n:<8} | {'statevector':<12} | {'ERROR':>10} | ❌ {str(e)}")

if __name__ == "__main__":
    asyncio.run(benchmark_simulation())
