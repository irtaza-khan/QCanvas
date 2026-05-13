# FastQSim API Cookbook

Practical examples for common SDK tasks.

## 1. Running a Circuit (Synchronous)
```python
import fastqsim
client = fastqsim.init()

qasm = 'OPENQASM 3.0; include "stdgates.inc"; qubit[2] q; h q[0]; cx q[0], q[1];'
job = client.run(qasm, backend="qiskit", shots=1024)
result = job.result()
print(result.counts)
```

## 2. Running a Circuit (Asynchronous)
```python
job = client.run(qasm, asynchronous=True)
print(f"Job ID: {job.job_id}")

# Wait for results later
completed_job = client.wait(job.job_id, timeout=300)
print(completed_job.result().counts)
```

## 3. Statevector Simulation
```python
job = client.run(qasm, shots=0, simulation_type="statevector")
sv = job.get_statevector()
print(sv[0]) # Amplitude of |00>
```

## 4. Density Matrix (Noisy Simulation)
```python
job = client.run(qasm, simulation_type="density_matrix")
result = job.result()
print(result.density_matrix)
```

## 5. Matrix Product State (MPS)
Best for large circuits with low entanglement.
```python
job = client.run(qasm, simulation_type="mps")
```

## 6. Batch Execution
Submit multiple circuits concurrently.
```python
circuits = [qasm1, qasm2, qasm3]
jobs = client.run_batch(circuits, max_parallel=5)
completed = client.wait([j.job_id for j in jobs])
```

## 7. Searching Job History
```python
from datetime import datetime, timedelta
yesterday = datetime.now() - timedelta(days=1)

jobs = client.search(run_status="completed", start_date=yesterday, limit=10)
for j in jobs:
    print(f"{j.job_id}: {j.execution_time_seconds}s")
```

## 8. Error Handling
```python
from fastqsim import JobFailedError, JobTimeoutError

try:
    job = client.run(qasm, shots=1024)
    result = job.result(timeout=60)
except JobFailedError as e:
    print(f"Failed: {e.reason}")
except JobTimeoutError:
    print("Timed out!")
```
