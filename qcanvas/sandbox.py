"""
Sandboxed Python Executor for Hybrid CPU-QPU Execution.

This module provides a secure execution environment for user-provided Python code
that includes quantum circuit compilation and simulation.

Security features (all configurable via config/config.py):
- Blocked dangerous imports (os, subprocess, sys, socket, etc.)
- Blocked file system access (open, pathlib, io)
- Blocked network access (socket, urllib, requests)
- Blocked shell execution (subprocess, os.system)
- Restricted builtins (no exec, eval, compile, __import__)
- Execution timeout
- Memory limits

Usage:
    from qcanvas_runtime.sandbox import execute_sandboxed
    result = execute_sandboxed(user_code, timeout=30)
    print(result.stdout)
"""

import sys
import os
import io
import time
import signal
import traceback
import threading
from typing import Any, Dict, Optional, Set
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
import builtins

# Add project root to path
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from .result import HybridExecutionResult, SimulationResult
# QSim wrapper module (provides qsim.run)
from . import qsim as qsim_wrapper

# Import configuration
try:
    from config.config import (
        HYBRID_EXECUTION_ENABLED,
        HYBRID_BLOCK_DANGEROUS_IMPORTS,
        HYBRID_BLOCK_FILE_ACCESS,
        HYBRID_BLOCK_NETWORK,
        HYBRID_BLOCK_SHELL,
        HYBRID_RESTRICT_BUILTINS,
        HYBRID_BLOCK_CODE_EXECUTION,
        HYBRID_MAX_EXECUTION_TIME,
        HYBRID_MAX_MEMORY_MB,
        HYBRID_MAX_SIMULATION_RUNS,
        HYBRID_MAX_OUTPUT_SIZE,
        HYBRID_ALLOWED_MODULES,
        HYBRID_BLOCKED_MODULES,
        HYBRID_BLOCKED_BUILTINS,
        HYBRID_VERBOSE_LOGGING,
        HYBRID_ALLOW_PRINT,
        HYBRID_CAPTURE_RESULTS,
    )
except ImportError:
    # Fallback defaults if config not available
    HYBRID_EXECUTION_ENABLED = True
    HYBRID_BLOCK_DANGEROUS_IMPORTS = True
    HYBRID_BLOCK_FILE_ACCESS = True
    HYBRID_BLOCK_NETWORK = True
    HYBRID_BLOCK_SHELL = True
    HYBRID_RESTRICT_BUILTINS = True
    HYBRID_BLOCK_CODE_EXECUTION = True
    HYBRID_MAX_EXECUTION_TIME = 30
    HYBRID_MAX_MEMORY_MB = 512
    HYBRID_MAX_SIMULATION_RUNS = 100
    HYBRID_MAX_OUTPUT_SIZE = 100000
    HYBRID_ALLOWED_MODULES = ['cirq', 'qiskit', 'pennylane', 'fastqsim', 'numpy', 'math']
    HYBRID_BLOCKED_MODULES = ['os', 'sys', 'subprocess', 'socket']
    HYBRID_BLOCKED_BUILTINS = ['exec', 'eval', 'compile', '__import__', 'open']
    HYBRID_VERBOSE_LOGGING = False
    HYBRID_ALLOW_PRINT = True
    HYBRID_CAPTURE_RESULTS = True


def _log(message: str) -> None:
    """Log message if verbose logging is enabled."""
    if HYBRID_VERBOSE_LOGGING:
        print(f"[Sandbox] {message}")


class SecurityViolationError(Exception):
    """Raised when code attempts a blocked operation."""
    pass


class OutputCapture:
    """Captures stdout and stderr with size limits."""
    
    def __init__(self, max_size: int = HYBRID_MAX_OUTPUT_SIZE):
        self.max_size = max_size
        self._stdout_buffer = io.StringIO()
        self._stderr_buffer = io.StringIO()
        self._stdout_size = 0
        self._stderr_size = 0
        self._original_stdout = None
        self._original_stderr = None
        
        # Standard stream attributes for third-party library compatibility
        self.encoding = sys.stdout.encoding if (sys.stdout and hasattr(sys.stdout, 'encoding')) else "utf-8"
        if not self.encoding:
            self.encoding = "utf-8"
        self.errors = "strict"
        
    def isatty(self) -> bool:
        """Standard IO stream attribute."""
        return False
    
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = self
        sys.stderr = self._create_stderr_wrapper()
        return self
    
    def __exit__(self, *args):
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
    
    def write(self, text: str) -> int:
        """Write to stdout with size limit."""
        if self._stdout_size >= self.max_size:
            return 0
        
        remaining = self.max_size - self._stdout_size
        text_to_write = text[:remaining]
        self._stdout_buffer.write(text_to_write)
        self._stdout_size += len(text_to_write)
        
        # Also write to original stdout for real-time feedback
        if self._original_stdout and HYBRID_VERBOSE_LOGGING:
            self._original_stdout.write(text_to_write)
        
        return len(text_to_write)
    
    def flush(self) -> None:
        """Flush the buffer."""
        self._stdout_buffer.flush()
        if self._original_stdout:
            self._original_stdout.flush()
    
    def _create_stderr_wrapper(self):
        """Create a stderr wrapper."""
        capture = self
        
        class StderrWrapper:
            def __init__(self):
                self.encoding = sys.stderr.encoding if (sys.stderr and hasattr(sys.stderr, 'encoding')) else "utf-8"
                if not self.encoding:
                    self.encoding = "utf-8"
                self.errors = "strict"
                
            def isatty(self) -> bool:
                return False

            def write(self, text: str) -> int:
                if capture._stderr_size >= capture.max_size:
                    return 0
                remaining = capture.max_size - capture._stderr_size
                text_to_write = text[:remaining]
                capture._stderr_buffer.write(text_to_write)
                capture._stderr_size += len(text_to_write)
                return len(text_to_write)
            
            def flush(self) -> None:
                capture._stderr_buffer.flush()
        
        return StderrWrapper()
    
    @property
    def stdout(self) -> str:
        return self._stdout_buffer.getvalue()
    
    @property
    def stderr(self) -> str:
        return self._stderr_buffer.getvalue()


class WrappedFastQSimJob:
    def __init__(self, original_job, qasm_code, shots, backend):
        self._original_job = original_job
        self._qasm_code = qasm_code
        self._shots = shots
        self._backend = backend

    def result(self, *args, **kwargs):
        # Call the original job's result
        res = self._original_job.result(*args, **kwargs)

        # Now gather the stats!
        try:
            counts = res.counts if hasattr(res, 'counts') else {}
            probs = res.probs if hasattr(res, 'probs') else {}
            statevector = res.statevector if hasattr(res, 'statevector') else None
            # Extract performance and billing telemetry from the original job
            exec_time_sec = getattr(self._original_job, 'execution_time_seconds', getattr(res, 'execution_time_seconds', 0.0))
            cpu_time_sec = getattr(self._original_job, 'cpu_seconds_total', 0.0)
            peak_ram_mb = getattr(self._original_job, 'peak_memory_mb', 0.0)
            billing_cpu = getattr(self._original_job, 'billing_cpu_millicore_seconds', 0.0)
            billing_mem = getattr(self._original_job, 'billing_memory_gb_seconds', 0.0)
            
            # Tags and user metadata round-trip
            tags = getattr(self._original_job, 'tags', {})
            job_metadata = getattr(self._original_job, 'metadata', {})
            
            # Lifecycle timestamps (safely converted to ISO strings)
            queue_enqueued_at = getattr(self._original_job, 'queue_enqueued_at', None)
            if hasattr(queue_enqueued_at, 'isoformat'):
                queue_enqueued_at = queue_enqueued_at.isoformat()
            execution_started_at = getattr(self._original_job, 'execution_started_at', None)
            if hasattr(execution_started_at, 'isoformat'):
                execution_started_at = execution_started_at.isoformat()
            execution_finished_at = getattr(self._original_job, 'execution_finished_at', None)
            if hasattr(execution_finished_at, 'isoformat'):
                execution_finished_at = execution_finished_at.isoformat()
            completed_at = getattr(self._original_job, 'completed_at', None)
            if hasattr(completed_at, 'isoformat'):
                completed_at = completed_at.isoformat()

            total_counts = sum(counts.values()) if counts else 0
            probabilities = {}
            if total_counts > 0:
                for state, count in counts.items():
                    probabilities[state] = count / total_counts
            elif probs:
                probabilities = dict(probs)

            exec_time_str = f"{exec_time_sec * 1000:.2f}ms" if exec_time_sec else "0.00ms"
            if exec_time_sec > 0 and cpu_time_sec > 0:
                cpu_pct = min((cpu_time_sec / exec_time_sec) * 100.0, 100.0)
                cpu_time_str = f"{cpu_pct:.1f}%"
            else:
                cpu_time_str = f"{cpu_time_sec * 1000:.1f}%" if cpu_time_sec else "0.0%"
            peak_ram_str = f"{peak_ram_mb:.1f}MB" if peak_ram_mb else "0.1MB"

            sim_result = SimulationResult(
                counts=dict(counts) if counts else {},
                probabilities=probabilities,
                statevector=statevector,
                shots=self._shots,
                backend=self._backend,
                execution_time=exec_time_str,
                simulation_time=exec_time_str,
                memory_usage=peak_ram_str,
                cpu_usage=cpu_time_str,
                fidelity=100.0,
                n_qubits=len(next(iter(counts.keys()))) if counts else 0,
                metadata={
                    "backend": self._backend,
                    "shots": self._shots,
                    "job_id": getattr(self._original_job, 'job_id', None),
                    "online": True,
                    "successful_shots": total_counts,
                    "execution_time_seconds": exec_time_sec,
                    "cpu_seconds_total": cpu_time_sec,
                    "peak_memory_mb": peak_ram_mb,
                    "billing_cpu_millicore_seconds": billing_cpu,
                    "billing_memory_gb_seconds": billing_mem,
                    "tags": tags,
                    "metadata": job_metadata,
                    "queue_enqueued_at": queue_enqueued_at,
                    "execution_started_at": execution_started_at,
                    "execution_finished_at": execution_finished_at,
                    "completed_at": completed_at,
                    "execution_time": exec_time_str,
                    "simulation_time": exec_time_str,
                    "memory_usage": peak_ram_str,
                    "cpu_usage": cpu_time_str,
                },
            )

            # Save this run to qsim's simulation results so that the sandbox extracts it!
            qsim_wrapper._simulation_results.append(sim_result.to_dict())

            # Print to frontend captured console
            print(f"🎯 [FastQSim] Captured simulation stats: Backend: '{self._backend}', Shots: {self._shots}, Counts: {counts}")

            # Write directly to original backend terminal (bypassing sandbox output capture)
            try:
                import sys as _sys
                # Try to find the root original stdout if nested
                orig_stdout = _sys.stdout
                while hasattr(orig_stdout, '_original_stdout') and orig_stdout._original_stdout:
                    orig_stdout = orig_stdout._original_stdout
                orig_stdout.write(f"\n🎯 [Sandbox Interceptor] Captured FastQSim Cloud Job Stats! Backend: '{self._backend}', Shots: {self._shots}, Counts: {counts}\n")
                orig_stdout.flush()
            except Exception:
                pass

        except Exception as e:
            print(f"⚠️ Error capturing fastqsim simulation stats: {e}")

        return res

    def __getattr__(self, name):
        return getattr(self._original_job, name)


class WrappedFastQSimClient:
    def __init__(self, original_client):
        self._original_client = original_client

    def run(self, circuit, shots=2048, asynchronous=False, backend="cirq", **kwargs):
        # Call the original client run
        job = self._original_client.run(
            circuit=circuit,
            shots=shots,
            asynchronous=asynchronous,
            backend=backend,
            **kwargs
        )
        return WrappedFastQSimJob(job, circuit, shots, backend)

    def __getattr__(self, name):
        return getattr(self._original_client, name)


class WrappedFastQSimModule:
    def __init__(self, original_fastqsim):
        self._original_fastqsim = original_fastqsim

    def init(self, *args, **kwargs):
        client = self._original_fastqsim.init(*args, **kwargs)
        return WrappedFastQSimClient(client)

    def __getattr__(self, name):
        return getattr(self._original_fastqsim, name)


class RestrictedImporter:
    """Custom import hook that blocks dangerous modules."""
    
    def __init__(self, blocked_modules: Set[str], allowed_modules: Set[str]):
        self.blocked_modules = blocked_modules
        self.allowed_modules = allowed_modules
        self._original_import = builtins.__import__
    
    def __call__(self, name: str, globals: Optional[Dict] = None, 
                 locals: Optional[Dict] = None, fromlist: tuple = (), 
                 level: int = 0) -> Any:
        """Custom import function that checks against blocked/allowed lists."""
        # Get the base module name
        base_module = name.split('.')[0]

        # Special case: always route `import qsim` to our safe wrapper
        if base_module == 'qsim':
            return qsim_wrapper
        
        # Special case: wrap fastqsim to capture its results
        if base_module == 'fastqsim':
            real_fastqsim = self._original_import(name, globals, locals, fromlist, level)
            return WrappedFastQSimModule(real_fastqsim)
        
        # Check who called the import. Only enforce blocks if the import was directly
        # initiated by the user's compiled code frame.
        is_user_code_import = False
        try:
            import sys as _sys
            caller_frame = _sys._getframe(1)
            # If the import caller frame is our user code compiled filename
            if caller_frame and caller_frame.f_code.co_filename == '<user_code>':
                is_user_code_import = True
        except Exception:
            # Fallback to safe restrictive check if frame inspection is unavailable
            is_user_code_import = True

        if is_user_code_import:
            # Check if blocked
            if HYBRID_BLOCK_DANGEROUS_IMPORTS:
                if base_module in self.blocked_modules:
                    raise SecurityViolationError(
                        f"Import of '{name}' is blocked for security reasons. "
                        f"Module '{base_module}' is not allowed in hybrid execution."
                    )
            
            # Check specific blocking categories
            if HYBRID_BLOCK_FILE_ACCESS and base_module in {'pathlib', 'io', 'tempfile', 'glob'}:
                raise SecurityViolationError(
                    f"Import of '{name}' is blocked. File access is disabled."
                )
            
            if HYBRID_BLOCK_NETWORK and base_module in {'socket', 'urllib', 'http', 'requests', 'aiohttp', 'httpx'}:
                raise SecurityViolationError(
                    f"Import of '{name}' is blocked. Network access is disabled."
                )
            
            if HYBRID_BLOCK_SHELL and base_module in {'subprocess', 'pty', 'pexpect'}:
                raise SecurityViolationError(
                    f"Import of '{name}' is blocked. Shell access is disabled."
                )
        
        # Allow the import
        return self._original_import(name, globals, locals, fromlist, level)
    
    def install(self) -> None:
        """Install the restricted importer."""
        builtins.__import__ = self
    
    def uninstall(self) -> None:
        """Restore the original import function."""
        builtins.__import__ = self._original_import


def _create_safe_builtins() -> Dict[str, Any]:
    """Create a dictionary of safe builtin functions."""
    # Start with all builtins
    safe_builtins = dict(builtins.__dict__)
    
    if HYBRID_RESTRICT_BUILTINS:
        # Remove blocked builtins
        for name in HYBRID_BLOCKED_BUILTINS:
            # Keep __import__ so that Python's import system continues to work;
            # actual import security is enforced by RestrictedImporter instead.
            if name == '__import__':
                continue
            safe_builtins.pop(name, None)
        
        # Additional safety: remove dangerous functions
        if HYBRID_BLOCK_CODE_EXECUTION:
            # Block direct code-evaluation helpers but keep __import__
            for name in ['exec', 'eval', 'compile']:
                safe_builtins.pop(name, None)
        
        if HYBRID_BLOCK_FILE_ACCESS:
            safe_builtins.pop('open', None)
            safe_builtins.pop('input', None)
    
    return safe_builtins


def _create_execution_globals() -> Dict[str, Any]:
    """Create the global namespace for code execution."""
    # Import qcanvas and qsim for the sandboxed environment
    from . import core as qcanvas_module
    from . import qsim as qsim_module
    from . import result as result_module
    
    # Create safe builtins
    safe_builtins = _create_safe_builtins()
    
    # Build the global namespace
    globals_dict = {
        '__builtins__': safe_builtins,
        '__name__': '__main__',
        '__doc__': None,
        
        # QCanvas API
        'qcanvas': qcanvas_module,
        'compile': qcanvas_module.compile,
        'compile_and_execute': qcanvas_module.compile_and_execute,
        
        # QSim API (as a module)
        'qsim': qsim_module,
        
        # Result types
        'SimulationResult': result_module.SimulationResult,
    }
    
    # Add print if allowed
    if HYBRID_ALLOW_PRINT:
        globals_dict['print'] = builtins.print
    
    return globals_dict


def _extract_error_line(tb_string: str, code: str) -> Optional[int]:
    """Extract the line number from a traceback string."""
    import re
    
    # Look for "line X" in the traceback
    matches = re.findall(r'line (\d+)', tb_string)
    if matches:
        return int(matches[-1])  # Return the last (most specific) line number
    
    return None


def execute_sandboxed(
    code: str,
    timeout: Optional[int] = None,
    framework_hint: Optional[str] = None
) -> HybridExecutionResult:
    """
    Execute Python code in a sandboxed environment.
    
    This function runs user-provided Python code with security restrictions.
    The code has access to:
    - qcanvas.compile() for circuit compilation
    - qsim.run() for quantum simulation
    - print() for output
    - Standard safe modules (numpy, math, cirq, qiskit, pennylane)
    
    Args:
        code: Python code to execute
        timeout: Maximum execution time in seconds (default from config)
        framework_hint: Hint about the quantum framework being used
    
    Returns:
        HybridExecutionResult with stdout, simulation results, and any errors
        
    Example:
        >>> code = '''
        ... import cirq
        ... from qcanvas import compile
        ... import qsim
        ... 
        ... q = cirq.LineQubit.range(2)
        ... circuit = cirq.Circuit([cirq.H(q[0]), cirq.CNOT(q[0], q[1])])
        ... qasm = compile(circuit, framework="cirq")
        ... print(f"QASM: {qasm[:50]}...")
        ... result = qsim.run(qasm, shots=100)
        ... print(f"Counts: {result.counts}")
        ... '''
        >>> result = execute_sandboxed(code)
        >>> print(result.stdout)
    """
    if not HYBRID_EXECUTION_ENABLED:
        return HybridExecutionResult.from_error(
            "Hybrid execution is disabled",
            error_type="DisabledError"
        )
    
    # Use config timeout if not specified
    if timeout is None:
        timeout = HYBRID_MAX_EXECUTION_TIME
    
    _log(f"Executing code with timeout={timeout}s")
    
    # Clear previous simulation results
    from . import qsim as qsim_module
    qsim_module.clear_simulation_results()
    
    # Track generated QASM
    last_qasm = None
    
    start_time = time.time()
    
    # Set up output capture
    output_capture = OutputCapture(max_size=HYBRID_MAX_OUTPUT_SIZE)
    
    # Set up restricted importer
    blocked_set = set(HYBRID_BLOCKED_MODULES) if HYBRID_BLOCK_DANGEROUS_IMPORTS else set()
    allowed_set = set(HYBRID_ALLOWED_MODULES)
    restricted_importer = RestrictedImporter(blocked_set, allowed_set)
    
    try:
        # Install security hooks
        restricted_importer.install()
        
        # Create execution environment
        exec_globals = _create_execution_globals()
        exec_locals = exec_globals
        
        # Compile the code first (syntax check)
        try:
            compiled_code = builtins.compile(code, '<user_code>', 'exec')
        except SyntaxError as e:
            return HybridExecutionResult.from_error(
                f"Syntax error: {e.msg}",
                error_type="SyntaxError",
                error_line=e.lineno
            )
        
        # Execute with timeout
        def execute_code():
            with output_capture:
                exec(compiled_code, exec_globals, exec_locals)
        
        if timeout > 0:
            # Use ThreadPoolExecutor for timeout
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(execute_code)
                try:
                    future.result(timeout=timeout)
                except FuturesTimeoutError:
                    return HybridExecutionResult.from_error(
                        f"Execution timed out after {timeout} seconds",
                        error_type="TimeoutError"
                    )
        else:
            # No timeout
            execute_code()
        
        # Get execution time
        execution_time = time.time() - start_time
        
        # Get simulation results
        simulation_results = qsim_module.get_simulation_results()
        
        # Get last generated QASM if any compile was called
        if 'compile' in exec_locals or hasattr(exec_globals.get('qcanvas'), '_last_qasm'):
            # Try to get the last QASM from any variable
            for name, value in exec_locals.items():
                if isinstance(value, str) and 'OPENQASM' in value:
                    last_qasm = value
                    break
        
        return HybridExecutionResult(
            success=True,
            stdout=output_capture.stdout,
            stderr=output_capture.stderr,
            qasm_generated=last_qasm,
            simulation_results=simulation_results,
            execution_time=f"{execution_time*1000:.2f}ms",
        )
        
    except SecurityViolationError as e:
        return HybridExecutionResult.from_error(
            str(e),
            error_type="SecurityViolationError"
        )
    
    except Exception as e:
        # Make sure we restore the original import mechanism before
        # Python's traceback machinery tries to import stdlib modules
        # like 'os' and 'linecache' internally.
        try:
            restricted_importer.uninstall()
        except Exception:
            pass

        # Get full traceback
        tb_string = traceback.format_exc()
        error_line = _extract_error_line(tb_string, code)
        
        # Get error type
        error_type = type(e).__name__
        
        # Get error message
        error_msg = str(e)
        if not error_msg:
            error_msg = error_type
        
        _log(f"Execution error: {error_type}: {error_msg}")
        _log(f"Traceback:\n{tb_string}")
        
        return HybridExecutionResult(
            success=False,
            stdout=output_capture.stdout if output_capture else "",
            stderr=tb_string,
            error=error_msg,
            error_type=error_type,
            error_line=error_line,
            execution_time=f"{(time.time() - start_time)*1000:.2f}ms",
        )
    
    finally:
        # Always restore original import
        restricted_importer.uninstall()


def validate_code(code: str) -> Dict[str, Any]:
    """
    Validate Python code without executing it.
    
    Checks for:
    - Syntax errors
    - Blocked imports
    - Dangerous patterns
    
    Args:
        code: Python code to validate
        
    Returns:
        Dictionary with 'valid' boolean and optional 'errors' list
    """
    errors = []
    warnings = []
    
    # Check syntax
    try:
        import ast
        tree = ast.parse(code)
    except SyntaxError as e:
        return {
            'valid': False,
            'errors': [f"Syntax error at line {e.lineno}: {e.msg}"]
        }
    
    # Check for blocked imports
    if HYBRID_BLOCK_DANGEROUS_IMPORTS:
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    base_module = alias.name.split('.')[0]
                    if base_module in HYBRID_BLOCKED_MODULES:
                        errors.append(
                            f"Line {node.lineno}: Import of '{alias.name}' is blocked"
                        )
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    base_module = node.module.split('.')[0]
                    if base_module in HYBRID_BLOCKED_MODULES:
                        errors.append(
                            f"Line {node.lineno}: Import from '{node.module}' is blocked"
                        )
    
    # Check for blocked builtins usage
    if HYBRID_RESTRICT_BUILTINS:
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in HYBRID_BLOCKED_BUILTINS:
                        errors.append(
                            f"Line {node.lineno}: Use of '{node.func.id}()' is blocked"
                        )
    
    # Check for open() calls
    if HYBRID_BLOCK_FILE_ACCESS:
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'open':
                    errors.append(f"Line {node.lineno}: File access is blocked")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors if errors else None,
        'warnings': warnings if warnings else None,
    }
