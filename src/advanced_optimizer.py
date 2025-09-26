#!/usr/bin/env python3
"""
🚀 Advanced Performance Optimizer and Debugger
Deep system optimization with performance profiling and debugging
"""

import asyncio
import cProfile
import gc
import io
import json
import logging
import os
import sys
import threading
import time
import tracemalloc
import weakref
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache, wraps
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable
import warnings

# Try to import optional dependencies
try:
    import psutil
except ImportError:
    print("⚠️ psutil not available, using basic system metrics")
    psutil = None
    
    # Create a mock psutil for basic functionality
    class MockProcess:
        def memory_info(self):
            class MemInfo:
                rss = 100 * 1024 * 1024  # Default 100MB
            return MemInfo()
        
        def cpu_percent(self, interval=None):
            return 10.0
    
    class MockPsutil:
        @staticmethod
        def Process():
            return MockProcess()
        
        @staticmethod
        def cpu_percent(interval=1):
            return 10.0
        
        @staticmethod
        def virtual_memory():
            class VMem:
                percent = 50.0
            return VMem()
        
        @staticmethod
        def disk_usage(path):
            class DiskUsage:
                percent = 30.0
            return DiskUsage()
        
        @staticmethod
        def disk_io_counters():
            return None
        
        @staticmethod
        def net_io_counters():
            class NetIO:
                dropin = 0
                dropout = 0
            return NetIO()
    
    if not psutil:
        psutil = MockPsutil()

try:
    import memory_profiler
except ImportError:
    memory_profiler = None

try:
    import pstats
except ImportError:
    pstats = None

# Configure optimized logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics container"""
    function_name: str
    execution_time: float
    memory_before: float
    memory_after: float
    memory_peak: float
    cpu_percent: float
    thread_count: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def memory_delta(self) -> float:
        return self.memory_after - self.memory_before

class AdvancedProfiler:
    """Advanced profiling system with memory and CPU tracking"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.profiler = cProfile.Profile()
        self.memory_snapshots = []
        self.active_traces = {}
        self._lock = threading.Lock()
        
        # Start memory tracking
        tracemalloc.start()
        
    @contextmanager
    def profile_function(self, func_name: str):
        """Context manager for profiling function execution"""
        process = psutil.Process()
        
        # Pre-execution measurements
        gc.collect()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        cpu_before = process.cpu_percent()
        thread_count = threading.active_count()
        
        # Start profiling
        start_time = time.perf_counter()
        
        try:
            yield
        finally:
            # Post-execution measurements
            execution_time = time.perf_counter() - start_time
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            cpu_percent = process.cpu_percent() - cpu_before
            
            # Get peak memory
            current, peak = tracemalloc.get_traced_memory()
            memory_peak = peak / 1024 / 1024  # MB
            
            # Store metrics
            with self._lock:
                self.metrics.append(PerformanceMetrics(
                    function_name=func_name,
                    execution_time=execution_time,
                    memory_before=memory_before,
                    memory_after=memory_after,
                    memory_peak=memory_peak,
                    cpu_percent=cpu_percent,
                    thread_count=thread_count
                ))
    
    def get_memory_leaks(self) -> List[Dict]:
        """Detect potential memory leaks"""
        snapshot = tracemalloc.take_snapshot()
        
        if self.memory_snapshots:
            # Compare with previous snapshot
            top_stats = snapshot.compare_to(self.memory_snapshots[-1], 'lineno')
            leaks = []
            
            for stat in top_stats[:10]:
                if stat.size_diff > 1024 * 1024:  # > 1MB growth
                    leaks.append({
                        'file': stat.traceback.format()[0] if stat.traceback else 'unknown',
                        'size_diff': stat.size_diff / 1024 / 1024,  # MB
                        'count_diff': stat.count_diff
                    })
            
            self.memory_snapshots.append(snapshot)
            return leaks
        
        self.memory_snapshots.append(snapshot)
        return []
    
    def generate_report(self) -> Dict:
        """Generate comprehensive performance report"""
        if not self.metrics:
            return {'error': 'No metrics collected'}
        
        total_time = sum(m.execution_time for m in self.metrics)
        avg_memory = sum(m.memory_delta for m in self.metrics) / len(self.metrics)
        
        # Find bottlenecks
        bottlenecks = sorted(self.metrics, key=lambda x: x.execution_time, reverse=True)[:5]
        memory_heavy = sorted(self.metrics, key=lambda x: x.memory_delta, reverse=True)[:5]
        
        return {
            'summary': {
                'total_functions_profiled': len(self.metrics),
                'total_execution_time': total_time,
                'average_memory_delta': avg_memory,
                'peak_memory_usage': max(m.memory_peak for m in self.metrics),
                'average_cpu_usage': sum(m.cpu_percent for m in self.metrics) / len(self.metrics)
            },
            'bottlenecks': [
                {
                    'function': b.function_name,
                    'time': b.execution_time,
                    'percentage': (b.execution_time / total_time) * 100
                }
                for b in bottlenecks
            ],
            'memory_intensive': [
                {
                    'function': m.function_name,
                    'memory_delta': m.memory_delta,
                    'peak_memory': m.memory_peak
                }
                for m in memory_heavy
            ],
            'potential_leaks': self.get_memory_leaks()
        }

class PerformanceOptimizer:
    """System-wide performance optimization manager"""
    
    def __init__(self):
        self.profiler = AdvancedProfiler()
        self.optimization_rules = {}
        self.cache_stats = {'hits': 0, 'misses': 0}
        self._optimization_cache = {}
        
    def optimize_imports(self):
        """Optimize module imports with lazy loading"""
        optimized_imports = {}
        
        # Analyze current imports
        for name, module in sys.modules.items():
            if module and hasattr(module, '__file__'):
                try:
                    size = os.path.getsize(module.__file__) if module.__file__ else 0
                    optimized_imports[name] = {
                        'size': size,
                        'loaded': True,
                        'optimize': size > 1024 * 1024  # Flag large modules
                    }
                except:
                    pass
        
        return optimized_imports
    
    def optimize_memory(self):
        """Optimize memory usage"""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Force garbage collection
        gc.collect()
        gc.collect()  # Second pass for cyclic references
        
        # Clear caches
        for obj in gc.get_objects():
            if hasattr(obj, 'cache_clear'):
                try:
                    obj.cache_clear()
                except:
                    pass
        
        # Trim memory pools
        if hasattr(sys, 'intern'):
            # Clear interned strings
            gc.collect()
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        freed = initial_memory - final_memory
        
        logger.info(f"🧹 Memory optimization freed {freed:.2f} MB")
        
        return {
            'initial_memory': initial_memory,
            'final_memory': final_memory,
            'freed_memory': freed,
            'gc_stats': gc.get_stats()
        }
    
    def optimize_async_operations(self):
        """Optimize async operations and event loops"""
        recommendations = []
        
        # Check for running event loops
        try:
            loop = asyncio.get_running_loop()
            
            # Check for pending tasks
            pending = asyncio.all_tasks(loop)
            if len(pending) > 100:
                recommendations.append({
                    'issue': 'Too many pending tasks',
                    'count': len(pending),
                    'fix': 'Consider using task groups or limiting concurrent tasks'
                })
            
            # Check for slow callbacks
            if hasattr(loop, 'slow_callback_duration'):
                if loop.slow_callback_duration > 0.1:
                    recommendations.append({
                        'issue': 'Slow callbacks detected',
                        'duration': loop.slow_callback_duration,
                        'fix': 'Move CPU-intensive work to thread pool'
                    })
        except RuntimeError:
            pass
        
        return recommendations
    
    def optimize_thread_pools(self):
        """Optimize thread pool configurations"""
        cpu_count = os.cpu_count() or 1
        current_threads = threading.active_count()
        
        recommendations = {
            'cpu_count': cpu_count,
            'current_threads': current_threads,
            'optimal_workers': min(32, (cpu_count + 4)),
            'io_workers': cpu_count * 2,
            'cpu_workers': cpu_count
        }
        
        if current_threads > cpu_count * 4:
            recommendations['warning'] = 'Too many threads active, consider consolidation'
        
        return recommendations
    
    def detect_bottlenecks(self) -> List[Dict]:
        """Detect performance bottlenecks in the system"""
        bottlenecks = []
        
        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 80:
            bottlenecks.append({
                'type': 'CPU',
                'severity': 'HIGH',
                'value': cpu_percent,
                'recommendation': 'Consider optimizing algorithms or using multiprocessing'
            })
        
        # Check memory usage
        memory = psutil.virtual_memory()
        if memory.percent > 85:
            bottlenecks.append({
                'type': 'Memory',
                'severity': 'HIGH',
                'value': memory.percent,
                'recommendation': 'Implement memory pooling or increase system RAM'
            })
        
        # Check disk I/O
        disk_io = psutil.disk_io_counters()
        if disk_io:
            io_wait = (disk_io.read_time + disk_io.write_time) / 1000
            if io_wait > 100:
                bottlenecks.append({
                    'type': 'Disk I/O',
                    'severity': 'MEDIUM',
                    'value': io_wait,
                    'recommendation': 'Consider using SSD or implementing caching'
                })
        
        # Check network
        net_io = psutil.net_io_counters()
        if net_io.dropin + net_io.dropout > 1000:
            bottlenecks.append({
                'type': 'Network',
                'severity': 'MEDIUM',
                'value': net_io.dropin + net_io.dropout,
                'recommendation': 'Check network stability and implement retry logic'
            })
        
        return bottlenecks

class AsyncOptimizer:
    """Async-specific optimizations"""
    
    @staticmethod
    async def optimize_coroutine_execution(coros: List, max_concurrent: int = 10):
        """Execute coroutines with optimized concurrency"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def bounded_coro(coro):
            async with semaphore:
                return await coro
        
        return await asyncio.gather(*[bounded_coro(c) for c in coros])
    
    @staticmethod
    def create_optimized_event_loop():
        """Create an optimized event loop with proper settings"""
        # Use uvloop if available (much faster)
        try:
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            logger.info("✅ Using uvloop for better performance")
        except ImportError:
            pass
        
        loop = asyncio.new_event_loop()
        
        # Enable debug mode in development
        if os.getenv('DEBUG'):
            loop.set_debug(True)
            warnings.simplefilter('always', ResourceWarning)
        
        # Set proper exception handler
        def exception_handler(loop, context):
            exception = context.get('exception')
            if isinstance(exception, asyncio.CancelledError):
                return
            logger.error(f"Unhandled exception in event loop: {context}")
        
        loop.set_exception_handler(exception_handler)
        
        return loop

class CodeOptimizer:
    """Source code optimization suggestions"""
    
    @staticmethod
    def analyze_code_patterns(file_path: str) -> List[Dict]:
        """Analyze code for optimization opportunities"""
        if not os.path.exists(file_path):
            return []
        
        optimizations = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            # Check for inefficient patterns
            
            # Multiple string concatenation
            if '+' in line and ('"' in line or "'" in line) and line.count('+') > 2:
                optimizations.append({
                    'line': i,
                    'issue': 'Multiple string concatenations',
                    'suggestion': 'Use f-strings or join()',
                    'severity': 'MEDIUM'
                })
            
            # List comprehension opportunities
            if 'append(' in line and 'for ' in lines[max(0, i-2):i]:
                optimizations.append({
                    'line': i,
                    'issue': 'Loop with append',
                    'suggestion': 'Consider list comprehension',
                    'severity': 'LOW'
                })
            
            # Unnecessary list() calls
            if 'list(' in line and 'for ' in line:
                optimizations.append({
                    'line': i,
                    'issue': 'Unnecessary list() call',
                    'suggestion': 'Remove list() for generators',
                    'severity': 'LOW'
                })
            
            # Global variable usage
            if line.strip().startswith('global '):
                optimizations.append({
                    'line': i,
                    'issue': 'Global variable usage',
                    'suggestion': 'Consider class attributes or function parameters',
                    'severity': 'MEDIUM'
                })
            
            # Bare except clauses
            if 'except:' in line:
                optimizations.append({
                    'line': i,
                    'issue': 'Bare except clause',
                    'suggestion': 'Specify exception types',
                    'severity': 'HIGH'
                })
        
        return optimizations

class SystemDebugger:
    """Advanced debugging utilities"""
    
    def __init__(self):
        self.error_log = []
        self.warning_log = []
        self.debug_mode = os.getenv('DEBUG', False)
        
    def analyze_error_patterns(self) -> Dict:
        """Analyze error patterns for common issues"""
        patterns = {
            'import_errors': 0,
            'type_errors': 0,
            'value_errors': 0,
            'async_errors': 0,
            'memory_errors': 0,
            'other_errors': 0
        }
        
        for error in self.error_log:
            if 'ImportError' in str(error):
                patterns['import_errors'] += 1
            elif 'TypeError' in str(error):
                patterns['type_errors'] += 1
            elif 'ValueError' in str(error):
                patterns['value_errors'] += 1
            elif 'asyncio' in str(error) or 'await' in str(error):
                patterns['async_errors'] += 1
            elif 'MemoryError' in str(error) or 'memory' in str(error).lower():
                patterns['memory_errors'] += 1
            else:
                patterns['other_errors'] += 1
        
        return patterns
    
    def check_system_health(self) -> Dict:
        """Comprehensive system health check"""
        health = {
            'status': 'HEALTHY',
            'issues': [],
            'metrics': {}
        }
        
        # CPU check
        cpu = psutil.cpu_percent(interval=1)
        health['metrics']['cpu'] = cpu
        if cpu > 90:
            health['status'] = 'CRITICAL'
            health['issues'].append('CPU usage critical')
        elif cpu > 70:
            health['status'] = 'WARNING'
            health['issues'].append('CPU usage high')
        
        # Memory check
        memory = psutil.virtual_memory()
        health['metrics']['memory'] = memory.percent
        if memory.percent > 90:
            health['status'] = 'CRITICAL'
            health['issues'].append('Memory usage critical')
        elif memory.percent > 75:
            if health['status'] != 'CRITICAL':
                health['status'] = 'WARNING'
            health['issues'].append('Memory usage high')
        
        # Disk check
        disk = psutil.disk_usage('/')
        health['metrics']['disk'] = disk.percent
        if disk.percent > 95:
            health['status'] = 'CRITICAL'
            health['issues'].append('Disk space critical')
        elif disk.percent > 85:
            if health['status'] != 'CRITICAL':
                health['status'] = 'WARNING'
            health['issues'].append('Disk space low')
        
        # Thread check
        thread_count = threading.active_count()
        health['metrics']['threads'] = thread_count
        if thread_count > 100:
            if health['status'] == 'HEALTHY':
                health['status'] = 'WARNING'
            health['issues'].append('Too many active threads')
        
        return health

def performance_monitor(func):
    """Decorator for monitoring function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = AdvancedProfiler()
        
        with profiler.profile_function(func.__name__):
            result = func(*args, **kwargs)
        
        # Log performance metrics
        if profiler.metrics:
            metric = profiler.metrics[-1]
            if metric.execution_time > 1.0:
                logger.warning(f"⚠️ Slow function: {func.__name__} took {metric.execution_time:.2f}s")
            if metric.memory_delta > 10:
                logger.warning(f"⚠️ Memory heavy: {func.__name__} used {metric.memory_delta:.2f}MB")
        
        return result
    
    return wrapper

async def async_performance_monitor(func):
    """Decorator for monitoring async function performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        profiler = AdvancedProfiler()
        
        with profiler.profile_function(func.__name__):
            result = await func(*args, **kwargs)
        
        # Log performance metrics
        if profiler.metrics:
            metric = profiler.metrics[-1]
            if metric.execution_time > 1.0:
                logger.warning(f"⚠️ Slow async function: {func.__name__} took {metric.execution_time:.2f}s")
        
        return result
    
    return wrapper

# Singleton instances
_optimizer_instance = None
_debugger_instance = None

def get_optimizer() -> PerformanceOptimizer:
    """Get singleton optimizer instance"""
    global _optimizer_instance
    if not _optimizer_instance:
        _optimizer_instance = PerformanceOptimizer()
    return _optimizer_instance

def get_debugger() -> SystemDebugger:
    """Get singleton debugger instance"""
    global _debugger_instance
    if not _debugger_instance:
        _debugger_instance = SystemDebugger()
    return _debugger_instance

def run_complete_optimization():
    """Run complete system optimization"""
    optimizer = get_optimizer()
    debugger = get_debugger()
    
    print("🚀 Starting Complete System Optimization...")
    print("=" * 60)
    
    # 1. System health check
    print("\n📊 System Health Check...")
    health = debugger.check_system_health()
    print(f"Status: {health['status']}")
    for issue in health['issues']:
        print(f"  ⚠️ {issue}")
    
    # 2. Memory optimization
    print("\n🧹 Memory Optimization...")
    memory_result = optimizer.optimize_memory()
    print(f"  Freed: {memory_result['freed_memory']:.2f} MB")
    
    # 3. Import optimization
    print("\n📦 Import Analysis...")
    imports = optimizer.optimize_imports()
    large_modules = [m for m, info in imports.items() if info.get('optimize')]
    if large_modules:
        print(f"  Found {len(large_modules)} large modules to optimize")
    
    # 4. Thread pool optimization
    print("\n🧵 Thread Pool Optimization...")
    thread_opts = optimizer.optimize_thread_pools()
    print(f"  Current threads: {thread_opts['current_threads']}")
    print(f"  Optimal workers: {thread_opts['optimal_workers']}")
    
    # 5. Async optimization
    print("\n⚡ Async Operations...")
    async_opts = optimizer.optimize_async_operations()
    for rec in async_opts:
        print(f"  Issue: {rec['issue']}")
        print(f"  Fix: {rec['fix']}")
    
    # 6. Bottleneck detection
    print("\n🔍 Bottleneck Detection...")
    bottlenecks = optimizer.detect_bottlenecks()
    for bottleneck in bottlenecks:
        print(f"  {bottleneck['type']}: {bottleneck['value']:.1f}%")
        print(f"    Recommendation: {bottleneck['recommendation']}")
    
    # 7. Generate report
    print("\n📈 Performance Report...")
    report = optimizer.profiler.generate_report()
    if 'summary' in report:
        print(f"  Peak memory: {report['summary'].get('peak_memory_usage', 0):.2f} MB")
        print(f"  Avg CPU: {report['summary'].get('average_cpu_usage', 0):.1f}%")
    
    print("\n✅ Optimization Complete!")
    print("=" * 60)
    
    return {
        'health': health,
        'memory': memory_result,
        'threads': thread_opts,
        'async': async_opts,
        'bottlenecks': bottlenecks,
        'report': report
    }

if __name__ == "__main__":
    # Run optimization when executed directly
    results = run_complete_optimization()
    
    # Save results to file
    with open('optimization_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Full report saved to optimization_report.json")