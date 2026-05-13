# FastQSim SDK Overview

The FastQSim SDK is a lightweight, zero-dependency Python library for interacting with the FastQSim quantum simulation cloud.

## Core Concepts

### 1. Design Philosophy
- **QASM 3.0 Only**: The SDK exclusively accepts OpenQASM 3.0 strings.
- **Zero Configuration**: Most settings are handled via environment variables.
- **Async First**: Designed for long-running quantum simulations with efficient polling.

### 2. Environment Variables
| Variable | Description |
| :--- | :--- |
| `FASTQUBIT_USER_ID` | Your unique user identifier (Required). |
| `FASTQSIM_API_TOKEN` | Bearer token for authentication. |
| `FASTQUBIT_ENDPOINT` | API base URL (Default: `https://api.qsim.io`). |
| `FASTQSIM_EXECUTION_MODE` | `cloud` or `local`. |

### 3. Client Lifecycle
Initialize the global client once at the start of your application:
```python
import fastqsim
client = fastqsim.init()
```

### 4. Job Lifecycle
1. **Created**: The job record is initialized.
2. **Queued**: Awaiting a worker pod.
3. **Running**: Simulation is active.
4. **Completed/Failed/Cancelled**: Terminal states.

### 5. Polling Mechanism
The SDK uses **Server-Side Long-Polling**. When you call `job.result()` or `client.wait()`, the server holds the connection for up to 30 seconds, returning immediately when the status changes.

## Data Structures

### The `Job` Object
Contains all metadata about a simulation run:
- `job_id`: Unique UUID.
- `status`: Current `JobStatus` enum.
- `execution_time_seconds`: Wall-clock duration.
- `billing_cpu_millicore_seconds`: Usage metrics.

### The `Result` Object
The payload returned after a successful run:
- `counts`: Dict of bitstring outcomes.
- `probabilities`: Dict of outcome probabilities.
- `statevector`: List of complex amplitudes (if requested).
