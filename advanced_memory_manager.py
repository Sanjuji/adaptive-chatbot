#!/usr/bin/env python3
"""
Advanced Memory Manager - O3 Level Optimization
Comprehensive memory management with leak detection and optimization
"""

import gc
import sys
import threading
import time
import weakref
import tracemalloc
import psutil
import logging
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import atexit
import functools

logger = logging.getLogger(__name__)

class MemoryState(Enum):
    """Memory usage states"""
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class MemoryMetrics:
    """Memory usage metrics"""
    timestamp: float
    current_mb: float
    peak_mb: float
    available_mb: float
    usage_percent: float
    state: MemoryState
    gc_collections: int
    objects_count: int
    weak_refs_count: int

@dataclass
class MemoryLeak:
    """Detected memory leak"""
    object_type: str
    count: int
    size_mb: float
    growth_rate: float
    first_detected: float
    last_seen: float
    stack_trace: List[str]

class AdvancedMemoryManager:
    """
    O3 Level Memory Manager
    - Real-time memory monitoring
    - Automatic leak detection
    - Intelligent garbage collection
    - Resource cleanup automation
    - Memory optimization strategies
    """
    
    def __init__(self, 
                 monitoring_interval: float = 5.0,
                 leak_detection_threshold: float = 0.1,
                 emergency_threshold: float = 0.9):
        self.monitoring_interval = monitoring_interval
        self.leak_detection_threshold = leak_detection_threshold
        self.emergency_threshold = emergency_threshold
        
        # Memory tracking
        self._metrics_history: deque = deque(maxlen=1000)
        self._object_counts: Dict[str, int] = defaultdict(int)
        self._object_sizes: Dict[str, float] = defaultdict(float)
        self._weak_refs: Set[weakref.ref] = set()
        
        # Leak detection
        self._detected_leaks: Dict[str, MemoryLeak] = {}
        self._baseline_objects: Dict[str, int] = {}
        self._leak_check_interval = 30.0
        self._last_leak_check = 0.0
        
        # Cleanup callbacks
        self._cleanup_callbacks: List[Callable] = []
        self._emergency_callbacks: List[Callable] = []
        
        # Monitoring control
        self._monitoring_active = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        
        # Performance optimization
        self._gc_thresholds = (700, 10, 10)  # Generation 0, 1, 2 thresholds
        self._last_gc_time = 0.0
        self._gc_interval = 10.0
        
        # Start monitoring
        self.start_monitoring()
        
        # Register cleanup
        atexit.register(self.shutdown)
        
        logger.info("🧠 Advanced Memory Manager initialized")
    
    def start_monitoring(self):
        """Start memory monitoring"""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="MemoryMonitor"
        )
        self._monitor_thread.start()
        
        # Start tracemalloc for detailed tracking
        if not tracemalloc.is_tracing():
            tracemalloc.start()
        
        logger.info("📊 Memory monitoring started")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while not self._shutdown_event.is_set():
            try:
                # Collect current metrics
                metrics = self._collect_metrics()
                self._metrics_history.append(metrics)
                
                # Check for memory issues
                self._check_memory_state(metrics)
                
                # Periodic leak detection
                current_time = time.time()
                if current_time - self._last_leak_check > self._leak_check_interval:
                    self._detect_memory_leaks()
                    self._last_leak_check = current_time
                
                # Optimize garbage collection
                self._optimize_garbage_collection(metrics)
                
                # Cleanup weak references
                self._cleanup_weak_refs()
                
            except Exception as e:
                logger.error(f"❌ Memory monitoring error: {e}")
            
            # Wait for next monitoring cycle
            self._shutdown_event.wait(self.monitoring_interval)
    
    def _collect_metrics(self) -> MemoryMetrics:
        """Collect current memory metrics"""
        try:
            # Get process memory info
            process = psutil.Process()
            memory_info = process.memory_info()
            current_mb = memory_info.rss / 1024 / 1024
            
            # Get system memory info
            system_memory = psutil.virtual_memory()
            available_mb = system_memory.available / 1024 / 1024
            usage_percent = system_memory.percent / 100.0
            
            # Get peak memory
            peak_mb = current_mb
            if self._metrics_history:
                peak_mb = max(m.current_mb for m in self._metrics_history)
            
            # Determine memory state
            if usage_percent >= self.emergency_threshold:
                state = MemoryState.EMERGENCY
            elif usage_percent >= 0.8:
                state = MemoryState.CRITICAL
            elif usage_percent >= 0.6:
                state = MemoryState.HIGH
            else:
                state = MemoryState.NORMAL
            
            # Get GC stats
            gc_stats = gc.get_stats()
            total_collections = sum(stat['collections'] for stat in gc_stats)
            
            # Count objects
            objects_count = len(gc.get_objects())
            
            return MemoryMetrics(
                timestamp=time.time(),
                current_mb=current_mb,
                peak_mb=peak_mb,
                available_mb=available_mb,
                usage_percent=usage_percent,
                state=state,
                gc_collections=total_collections,
                objects_count=objects_count,
                weak_refs_count=len(self._weak_refs)
            )
            
        except Exception as e:
            logger.error(f"❌ Error collecting memory metrics: {e}")
            return MemoryMetrics(
                timestamp=time.time(),
                current_mb=0.0,
                peak_mb=0.0,
                available_mb=0.0,
                usage_percent=0.0,
                state=MemoryState.NORMAL,
                gc_collections=0,
                objects_count=0,
                weak_refs_count=0
            )
    
    def _check_memory_state(self, metrics: MemoryMetrics):
        """Check memory state and trigger appropriate actions"""
        if metrics.state == MemoryState.EMERGENCY:
            logger.critical(f"🚨 EMERGENCY: Memory usage at {metrics.usage_percent:.1%}")
            self._trigger_emergency_cleanup()
        elif metrics.state == MemoryState.CRITICAL:
            logger.warning(f"⚠️ CRITICAL: Memory usage at {metrics.usage_percent:.1%}")
            self._trigger_aggressive_cleanup()
        elif metrics.state == MemoryState.HIGH:
            logger.info(f"📈 HIGH: Memory usage at {metrics.usage_percent:.1%}")
            self._trigger_normal_cleanup()
    
    def _trigger_emergency_cleanup(self):
        """Trigger emergency memory cleanup"""
        logger.critical("🚨 Triggering emergency memory cleanup")
        
        # Call emergency callbacks
        for callback in self._emergency_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"❌ Emergency callback error: {e}")
        
        # Force aggressive garbage collection
        for generation in range(3):
            collected = gc.collect(generation)
            logger.debug(f"🗑️ Collected {collected} objects from generation {generation}")
        
        # Clear caches if possible
        self._clear_optimizable_caches()
    
    def _trigger_aggressive_cleanup(self):
        """Trigger aggressive memory cleanup"""
        logger.warning("🧹 Triggering aggressive memory cleanup")
        
        # Call normal cleanup callbacks
        for callback in self._cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"❌ Cleanup callback error: {e}")
        
        # Force garbage collection
        collected = gc.collect()
        logger.debug(f"🗑️ Collected {collected} objects")
        
        # Clear some caches
        self._clear_optimizable_caches()
    
    def _trigger_normal_cleanup(self):
        """Trigger normal memory cleanup"""
        # Call cleanup callbacks
        for callback in self._cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"❌ Cleanup callback error: {e}")
        
        # Light garbage collection
        if time.time() - self._last_gc_time > self._gc_interval:
            collected = gc.collect()
            self._last_gc_time = time.time()
            logger.debug(f"🗑️ Collected {collected} objects")
    
    def _detect_memory_leaks(self):
        """Detect potential memory leaks"""
        try:
            current_objects = {}
            
            # Count objects by type
            for obj in gc.get_objects():
                obj_type = type(obj).__name__
                current_objects[obj_type] = current_objects.get(obj_type, 0) + 1
            
            # Compare with baseline
            if not self._baseline_objects:
                self._baseline_objects = current_objects.copy()
                return
            
            # Check for significant growth
            for obj_type, current_count in current_objects.items():
                baseline_count = self._baseline_objects.get(obj_type, 0)
                
                if baseline_count > 0:
                    growth_rate = (current_count - baseline_count) / baseline_count
                    
                    if growth_rate > self.leak_detection_threshold:
                        # Potential leak detected
                        if obj_type in self._detected_leaks:
                            leak = self._detected_leaks[obj_type]
                            leak.count = current_count
                            leak.last_seen = time.time()
                            leak.growth_rate = growth_rate
                        else:
                            # New leak detected
                            leak = MemoryLeak(
                                object_type=obj_type,
                                count=current_count,
                                size_mb=self._estimate_object_size(obj_type, current_count),
                                growth_rate=growth_rate,
                                first_detected=time.time(),
                                last_seen=time.time(),
                                stack_trace=self._get_object_stack_trace(obj_type)
                            )
                            self._detected_leaks[obj_type] = leak
                            
                            logger.warning(f"🔍 Potential memory leak detected: {obj_type} "
                                         f"(growth: {growth_rate:.1%})")
            
            # Update baseline
            self._baseline_objects = current_objects.copy()
            
        except Exception as e:
            logger.error(f"❌ Memory leak detection error: {e}")
    
    def _estimate_object_size(self, obj_type: str, count: int) -> float:
        """Estimate memory size for object type"""
        # Rough estimates for common object types
        size_estimates = {
            'str': 50,  # bytes
            'list': 56,
            'dict': 232,
            'tuple': 40,
            'set': 200,
            'function': 136,
            'method': 64,
            'frame': 400,
            'generator': 200,
        }
        
        avg_size = size_estimates.get(obj_type, 100)  # Default estimate
        return (avg_size * count) / 1024 / 1024  # Convert to MB
    
    def _get_object_stack_trace(self, obj_type: str) -> List[str]:
        """Get stack trace for object type (simplified)"""
        try:
            import traceback
            return traceback.format_stack()[-5:]  # Last 5 frames
        except:
            return ["Stack trace unavailable"]
    
    def _optimize_garbage_collection(self, metrics: MemoryMetrics):
        """Optimize garbage collection based on memory usage"""
        if metrics.state == MemoryState.EMERGENCY:
            # Emergency: aggressive GC
            gc.set_threshold(100, 5, 5)
        elif metrics.state == MemoryState.CRITICAL:
            # Critical: more frequent GC
            gc.set_threshold(300, 8, 8)
        elif metrics.state == MemoryState.HIGH:
            # High: moderate GC
            gc.set_threshold(500, 10, 10)
        else:
            # Normal: standard GC
            gc.set_threshold(700, 10, 10)
    
    def _clear_optimizable_caches(self) -> None:
        """Clear caches that can be safely cleared"""
        try:
            # Clear Python's internal caches
            import sys
            if hasattr(sys, '_clear_type_cache'):
                sys._clear_type_cache()
            
            # Clear module cache if memory is critical
            if len(self._metrics_history) > 10:
                recent_metrics = list(self._metrics_history)[-5:]
                avg_usage = sum(m.usage_percent for m in recent_metrics) / len(recent_metrics)
                
                if avg_usage > 0.8:
                    # Clear some module caches (more selective)
                    cached_modules = []
                    for module_name in list(sys.modules.keys()):
                        if (module_name.startswith('_') and 
                            module_name not in ['__main__', '__builtins__'] and
                            not module_name.startswith('__pycache__')):
                            cached_modules.append(module_name)
                    
                    # Only clear non-critical modules
                    for module_name in cached_modules[:10]:  # Limit to 10 modules
                        try:
                            if module_name in sys.modules:
                                del sys.modules[module_name]
                        except (KeyError, AttributeError):
                            continue
                                
        except Exception as e:
            logger.error(f"❌ Cache clearing error: {e}")
    
    def _cleanup_weak_refs(self):
        """Clean up dead weak references"""
        dead_refs = []
        for ref in self._weak_refs:
            if ref() is None:
                dead_refs.append(ref)
        
        for ref in dead_refs:
            self._weak_refs.discard(ref)
    
    def register_cleanup_callback(self, callback: Callable):
        """Register cleanup callback"""
        self._cleanup_callbacks.append(callback)
    
    def register_emergency_callback(self, callback: Callable):
        """Register emergency cleanup callback"""
        self._emergency_callbacks.append(callback)
    
    def create_weak_ref(self, obj: Any) -> weakref.ref:
        """Create weak reference with tracking"""
        ref = weakref.ref(obj, self._weak_ref_callback)
        self._weak_refs.add(ref)
        return ref
    
    def _weak_ref_callback(self, ref):
        """Callback for when weak reference is deleted"""
        self._weak_refs.discard(ref)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        if not self._metrics_history:
            return {}
        
        latest = self._metrics_history[-1]
        
        return {
            'current_mb': latest.current_mb,
            'peak_mb': latest.peak_mb,
            'usage_percent': latest.usage_percent,
            'state': latest.state.value,
            'objects_count': latest.objects_count,
            'weak_refs_count': latest.weak_refs_count,
            'gc_collections': latest.gc_collections,
            'detected_leaks': len(self._detected_leaks),
            'leak_details': {
                leak.object_type: {
                    'count': leak.count,
                    'size_mb': leak.size_mb,
                    'growth_rate': leak.growth_rate,
                    'age_hours': (time.time() - leak.first_detected) / 3600
                }
                for leak in self._detected_leaks.values()
            },
            'history_length': len(self._metrics_history),
            'monitoring_active': self._monitoring_active
        }
    
    def get_detected_leaks(self) -> List[MemoryLeak]:
        """Get list of detected memory leaks"""
        return list(self._detected_leaks.values())
    
    def clear_detected_leaks(self):
        """Clear detected leaks (reset baseline)"""
        self._detected_leaks.clear()
        self._baseline_objects.clear()
        logger.info("🧹 Cleared memory leak detection baseline")
    
    def force_cleanup(self):
        """Force immediate memory cleanup"""
        logger.info("🧹 Forcing immediate memory cleanup")
        
        # Call all cleanup callbacks
        for callback in self._cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"❌ Cleanup callback error: {e}")
        
        # Force garbage collection
        collected = 0
        for generation in range(3):
            collected += gc.collect(generation)
        
        logger.info(f"🗑️ Cleanup complete: {collected} objects collected")
        return collected
    
    def shutdown(self):
        """Shutdown memory manager"""
        logger.info("🛑 Shutting down Memory Manager")
        
        self._monitoring_active = False
        self._shutdown_event.set()
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)
        
        # Final cleanup
        self.force_cleanup()
        
        # Stop tracemalloc
        if tracemalloc.is_tracing():
            tracemalloc.stop()
        
        logger.info("✅ Memory Manager shutdown complete")

# Global instance
_memory_manager: Optional[AdvancedMemoryManager] = None

def get_memory_manager() -> AdvancedMemoryManager:
    """Get global memory manager instance"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = AdvancedMemoryManager()
    return _memory_manager

def memory_monitor(func: Callable) -> Callable:
    """Decorator to monitor memory usage of functions"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        manager = get_memory_manager()
        
        # Get memory before
        before_metrics = manager._collect_metrics()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # Get memory after
            after_metrics = manager._collect_metrics()
            
            # Log memory usage
            memory_delta = after_metrics.current_mb - before_metrics.current_mb
            if abs(memory_delta) > 1.0:  # Only log significant changes
                logger.debug(f"📊 {func.__name__}: {memory_delta:+.1f}MB memory delta")
    
    return wrapper

def register_memory_cleanup(callback: Callable):
    """Register memory cleanup callback"""
    get_memory_manager().register_cleanup_callback(callback)

def register_emergency_cleanup(callback: Callable):
    """Register emergency cleanup callback"""
    get_memory_manager().register_emergency_callback(callback)

# Cleanup on module unload
atexit.register(lambda: _memory_manager.shutdown() if _memory_manager else None)
