"""
High-Performance Configuration for QSIM
Handles GPU detection, threading, and performance optimizations
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import multiprocessing as mp
import psutil

# Try to import GPU libraries
try:
    import cupy as cp
    CUPY_AVAILABLE = True
    GPU_MEMORY = cp.cuda.Device().mem_info[1]  # Total GPU memory
except ImportError:
    CUPY_AVAILABLE = False
    GPU_MEMORY = 0

try:
    import mkl
    MKL_AVAILABLE = True
    # Set MKL to use all available cores
    mkl.set_num_threads(mp.cpu_count())
except ImportError:
    MKL_AVAILABLE = False

try:
    from numba import cuda
    CUDA_AVAILABLE = cuda.is_available()
    if CUDA_AVAILABLE:
        GPU_COUNT = len(cuda.gpus)
    else:
        GPU_COUNT = 0
except ImportError:
    CUDA_AVAILABLE = False
    GPU_COUNT = 0

class ComputeBackend(Enum):
    CPU = "cpu"
    GPU_CUPY = "gpu_cupy"
    GPU_QISKIT_AER = "gpu_qiskit_aer"
    DISTRIBUTED = "distributed"

class OptimizationLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    MAXIMUM = 4

@dataclass
class SystemInfo:
    """System information for performance optimization"""
    cpu_count: int
    physical_cores: int
    total_memory: int  # GB
    available_memory: int  # GB
    gpu_available: bool
    gpu_count: int
    gpu_memory: int  # Bytes
    mkl_available: bool
    cupy_available: bool
    cuda_available: bool

@dataclass
class PerformanceConfig:
    """Configuration for high-performance computing"""
    backend: ComputeBackend
    optimization_level: OptimizationLevel
    max_threads: int
    chunk_size: int
    use_gpu: bool
    gpu_memory_fraction: float
    enable_profiling: bool
    cache_size: int  # MB
    batch_size: int

class ConfigManager:
    """Manages performance configuration and system detection"""
    
    def __init__(self):
        self.system_info = self._detect_system()
        self.performance_config = self._create_default_config()
        self._setup_logging()
        self._optimize_environment()
    
    def _detect_system(self) -> SystemInfo:
        """Detect system capabilities"""
        memory = psutil.virtual_memory()
        
        return SystemInfo(
            cpu_count=mp.cpu_count(),
            physical_cores=psutil.cpu_count(logical=False),
            total_memory=int(memory.total / (1024**3)),  # GB
            available_memory=int(memory.available / (1024**3)),  # GB
            gpu_available=CUPY_AVAILABLE or CUDA_AVAILABLE,
            gpu_count=GPU_COUNT,
            gpu_memory=GPU_MEMORY,
            mkl_available=MKL_AVAILABLE,
            cupy_available=CUPY_AVAILABLE,
            cuda_available=CUDA_AVAILABLE
        )
    
    def _create_default_config(self) -> PerformanceConfig:
        """Create optimal default configuration based on system"""
        # Determine best backend
        if self.system_info.gpu_available and self.system_info.gpu_memory > 2*1024**3:  # 2GB
            backend = ComputeBackend.GPU_CUPY
            use_gpu = True
        else:
            backend = ComputeBackend.CPU
            use_gpu = False
        
        # Set optimization level based on system capabilities
        if self.system_info.total_memory >= 32 and self.system_info.physical_cores >= 8:
            opt_level = OptimizationLevel.MAXIMUM
        elif self.system_info.total_memory >= 16 and self.system_info.physical_cores >= 4:
            opt_level = OptimizationLevel.HIGH
        else:
            opt_level = OptimizationLevel.MEDIUM
        
        return PerformanceConfig(
            backend=backend,
            optimization_level=opt_level,
            max_threads=max(1, self.system_info.physical_cores - 1),
            chunk_size=1000,
            use_gpu=use_gpu,
            gpu_memory_fraction=0.8,
            enable_profiling=True,
            cache_size=512,  # MB
            batch_size=min(10000, max(1000, self.system_info.available_memory * 100))
        )
    
    def _setup_logging(self):
        """Setup performance logging"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        # Performance logger
        perf_logger = logging.getLogger('qsim.performance')
        perf_handler = logging.FileHandler('logs/performance.log')
        perf_handler.setFormatter(logging.Formatter(log_format))
        perf_logger.addHandler(perf_handler)
        perf_logger.setLevel(logging.INFO)
        
        # System logger  
        sys_logger = logging.getLogger('qsim.system')
        sys_handler = logging.FileHandler('logs/system.log')
        sys_handler.setFormatter(logging.Formatter(log_format))
        sys_logger.addHandler(sys_handler)
        sys_logger.setLevel(logging.INFO)
        
        # Log system info
        sys_logger.info(f"System detected: {self.system_info}")
        sys_logger.info(f"Performance config: {self.performance_config}")
    
    def _optimize_environment(self):
        """Optimize environment variables for performance"""
        # NumPy optimizations
        os.environ['OMP_NUM_THREADS'] = str(self.performance_config.max_threads)
        os.environ['OPENBLAS_NUM_THREADS'] = str(self.performance_config.max_threads)
        os.environ['MKL_NUM_THREADS'] = str(self.performance_config.max_threads)
        os.environ['VECLIB_MAXIMUM_THREADS'] = str(self.performance_config.max_threads)
        
        # Memory optimizations
        os.environ['PYTHONHASHSEED'] = '0'  # Reproducible hashing
        
        # CUDA optimizations
        if self.system_info.cuda_available:
            os.environ['CUDA_CACHE_MAXSIZE'] = '2147483648'  # 2GB cache
            os.environ['CUDA_LAUNCH_BLOCKING'] = '0'  # Async execution
    
    def get_optimal_shots_per_batch(self, total_shots: int, num_qubits: int) -> int:
        """Calculate optimal batch size for shots based on system resources"""
        # Estimate memory usage per shot (rough approximation)
        memory_per_shot = 2 ** min(num_qubits, 20) * 16  # bytes for complex128
        
        # Available memory for computation (leave some buffer)
        available_memory = self.system_info.available_memory * 1024**3 * 0.5  # 50% of available
        
        # Calculate optimal batch size
        max_shots_per_batch = int(available_memory / memory_per_shot)
        optimal_batch = min(
            max_shots_per_batch,
            self.performance_config.batch_size,
            total_shots
        )
        
        return max(1, optimal_batch)
    
    def should_use_gpu(self, num_qubits: int, shots: int) -> bool:
        """Determine if GPU should be used based on problem size"""
        if not self.system_info.gpu_available:
            return False
        
        # Use GPU for larger circuits or high shot counts
        gpu_threshold_qubits = 10
        gpu_threshold_shots = 5000
        
        return (num_qubits >= gpu_threshold_qubits or 
                shots >= gpu_threshold_shots)
    
    def get_thread_count(self, num_qubits: int) -> int:
        """Get optimal thread count based on problem size"""
        if num_qubits <= 10:
            return min(4, self.performance_config.max_threads)
        elif num_qubits <= 15:
            return min(8, self.performance_config.max_threads)
        else:
            return self.performance_config.max_threads

# Global configuration instance
config_manager = ConfigManager()

def get_config() -> ConfigManager:
    """Get global configuration manager instance"""
    return config_manager

def log_performance(func_name: str, execution_time: float, 
                   memory_usage: float, additional_info: Dict[str, Any] = None):
    """Log performance metrics"""
    logger = logging.getLogger('qsim.performance')
    info = additional_info or {}
    logger.info(f"Function: {func_name}, Time: {execution_time:.4f}s, "
               f"Memory: {memory_usage:.2f}MB, Info: {info}")

def get_system_status() -> Dict[str, Any]:
    """Get current system status"""
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)
    
    status = {
        'cpu_usage': cpu_percent,
        'memory_usage': memory.percent,
        'available_memory_gb': memory.available / (1024**3),
        'timestamp': psutil.time.time()
    }
    
    if CUPY_AVAILABLE:
        try:
            gpu_info = cp.cuda.Device().mem_info
            status['gpu_memory_used_gb'] = (gpu_info[1] - gpu_info[0]) / (1024**3)
            status['gpu_memory_total_gb'] = gpu_info[1] / (1024**3)
        except:
            pass
    
    return status