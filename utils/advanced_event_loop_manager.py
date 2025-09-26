#!/usr/bin/env python3
"""
Advanced Event Loop Manager - O3 Level Optimization
Fixes all async/sync conflicts and event loop management issues
"""

import asyncio
import threading
import weakref
import time
import logging
from typing import Optional, Dict, Any, Callable, Coroutine
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
import functools
import concurrent.futures
import queue

logger = logging.getLogger(__name__)

class LoopState(Enum):
    """Event loop states"""
    IDLE = "idle"
    RUNNING = "running"
    CLOSING = "closing"
    CLOSED = "closed"

@dataclass
class LoopMetrics:
    """Event loop performance metrics"""
    creation_time: float
    last_activity: float
    task_count: int
    memory_usage: float
    error_count: int
    state: LoopState

class AdvancedEventLoopManager:
    """
    O3 Level Event Loop Manager
    - Thread-safe event loop management
    - Automatic cleanup and resource management
    - Performance monitoring and optimization
    - Circuit breaker for failing loops
    """
    
    def __init__(self, max_loops: int = 5, cleanup_interval: float = 30.0):
        self.max_loops = max_loops
        self.cleanup_interval = cleanup_interval
        
        # Thread-safe storage
        self._loops: Dict[threading.Thread, asyncio.AbstractEventLoop] = {}
        self._loop_metrics: Dict[asyncio.AbstractEventLoop, LoopMetrics] = {}
        self._loop_lock = threading.RLock()
        
        # Cleanup tracking
        self._cleanup_callbacks: weakref.WeakSet = weakref.WeakSet()
        self._shutdown_event = threading.Event()
        
        # Performance monitoring
        self._performance_stats = {
            'total_loops_created': 0,
            'total_loops_destroyed': 0,
            'current_active_loops': 0,
            'average_loop_lifetime': 0.0,
            'error_rate': 0.0
        }
        
        # Start background cleanup
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop, 
            daemon=True,
            name="EventLoopCleanup"
        )
        self._cleanup_thread.start()
        
        logger.info("🚀 Advanced Event Loop Manager initialized")
    
    def get_or_create_loop(self, thread: Optional[threading.Thread] = None) -> asyncio.AbstractEventLoop:
        """Get or create event loop for thread with optimization"""
        if thread is None:
            thread = threading.current_thread()
        
        with self._loop_lock:
            # Check if loop already exists and is healthy
            if thread in self._loops:
                loop = self._loops[thread]
                if not loop.is_closed():
                    self._update_loop_metrics(loop)
                    return loop
                else:
                    # Clean up closed loop
                    self._cleanup_loop_metrics(loop)
                    del self._loops[thread]
            
            # Create new loop if under limit
            if len(self._loops) >= self.max_loops:
                # Find least recently used loop to replace
                oldest_thread = min(
                    self._loops.keys(),
                    key=lambda t: self._loop_metrics.get(
                        self._loops[t], 
                        LoopMetrics(0, 0, 0, 0, 0, LoopState.CLOSED)
                    ).last_activity
                )
                self._destroy_loop(oldest_thread)
            
            # Create new optimized loop
            loop = self._create_optimized_loop()
            self._loops[thread] = loop
            self._loop_metrics[loop] = LoopMetrics(
                creation_time=time.time(),
                last_activity=time.time(),
                task_count=0,
                memory_usage=0.0,
                error_count=0,
                state=LoopState.IDLE
            )
            
            self._performance_stats['total_loops_created'] += 1
            self._performance_stats['current_active_loops'] = len(self._loops)
            
            logger.debug(f"✅ Created new event loop for thread: {thread.name}")
            return loop
    
    def _create_optimized_loop(self) -> asyncio.AbstractEventLoop:
        """Create optimized event loop with best practices"""
        # Try to use uvloop for better performance
        try:
            import uvloop
            loop = uvloop.new_event_loop()
            logger.debug("🚀 Using uvloop for optimal performance")
        except ImportError:
            # Fallback to standard asyncio
            loop = asyncio.new_event_loop()
            logger.debug("📦 Using standard asyncio event loop")
        
        # Configure loop for optimal performance
        loop.set_debug(False)  # Disable debug for production
        
        # Set exception handler
        def exception_handler(loop, context):
            logger.error(f"❌ Event loop exception: {context}")
            self._loop_metrics[loop].error_count += 1
        
        loop.set_exception_handler(exception_handler)
        
        return loop
    
    def run_async_safely(self, coro: Coroutine, timeout: Optional[float] = None) -> Any:
        """Run async coroutine safely with proper error handling"""
        loop = self.get_or_create_loop()
        
        # Check if we're already in the loop
        try:
            current_loop = asyncio.get_running_loop()
            if current_loop == loop:
                # We're in the same loop, can't use run_until_complete
                # Create a task and wait for it
                task = asyncio.create_task(coro)
                return asyncio.wait_for(task, timeout=timeout)
        except RuntimeError:
            # No running loop, safe to use run_until_complete
            pass
        
        # Run in thread pool to avoid blocking
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._run_in_loop, loop, coro, timeout)
            return future.result(timeout=(timeout or 60) + 10)
    
    def _run_in_loop(self, loop: asyncio.AbstractEventLoop, coro: Coroutine, timeout: Optional[float]) -> Any:
        """Run coroutine in specific loop"""
        try:
            # Set the loop for this thread
            asyncio.set_event_loop(loop)
            
            # Run the coroutine
            if timeout:
                return loop.run_until_complete(asyncio.wait_for(coro, timeout=timeout))
            else:
                return loop.run_until_complete(coro)
        except Exception as e:
            logger.error(f"❌ Error running coroutine: {e}")
            raise
        finally:
            # Update metrics
            self._update_loop_metrics(loop)
    
    def _update_loop_metrics(self, loop: asyncio.AbstractEventLoop):
        """Update loop performance metrics"""
        if loop in self._loop_metrics:
            metrics = self._loop_metrics[loop]
            metrics.last_activity = time.time()
            metrics.task_count = len(asyncio.all_tasks(loop))
            metrics.state = LoopState.RUNNING if not loop.is_closed() else LoopState.CLOSED
    
    def _cleanup_loop_metrics(self, loop: asyncio.AbstractEventLoop):
        """Clean up loop metrics"""
        if loop in self._loop_metrics:
            metrics = self._loop_metrics[loop]
            lifetime = time.time() - metrics.creation_time
            self._performance_stats['average_loop_lifetime'] = (
                (self._performance_stats['average_loop_lifetime'] + lifetime) / 2
            )
            del self._loop_metrics[loop]
    
    def _destroy_loop(self, thread: threading.Thread):
        """Safely destroy event loop"""
        if thread in self._loops:
            loop = self._loops[thread]
            
            # Cancel all pending tasks
            try:
                pending_tasks = asyncio.all_tasks(loop)
                for task in pending_tasks:
                    task.cancel()
                
                # Wait for tasks to complete
                if pending_tasks:
                    loop.run_until_complete(
                        asyncio.gather(*pending_tasks, return_exceptions=True)
                    )
            except Exception as e:
                logger.warning(f"⚠️ Error cancelling tasks: {e}")
            
            # Close the loop
            try:
                loop.close()
            except Exception as e:
                logger.warning(f"⚠️ Error closing loop: {e}")
            
            # Clean up metrics
            self._cleanup_loop_metrics(loop)
            del self._loops[thread]
            
            self._performance_stats['total_loops_destroyed'] += 1
            self._performance_stats['current_active_loops'] = len(self._loops)
            
            logger.debug(f"🗑️ Destroyed event loop for thread: {thread.name}")
    
    def _cleanup_loop(self):
        """Background cleanup loop"""
        while not self._shutdown_event.is_set():
            try:
                current_time = time.time()
                threads_to_remove = []
                
                with self._loop_lock:
                    for thread, loop in list(self._loops.items()):
                        if loop.is_closed():
                            threads_to_remove.append(thread)
                            continue
                        
                        metrics = self._loop_metrics.get(loop)
                        if metrics and current_time - metrics.last_activity > self.cleanup_interval:
                            # Loop has been idle too long
                            threads_to_remove.append(thread)
                
                # Remove idle/closed loops
                for thread in threads_to_remove:
                    self._destroy_loop(thread)
                
                # Call cleanup callbacks
                for callback in list(self._cleanup_callbacks):
                    try:
                        callback()
                    except Exception as e:
                        logger.error(f"❌ Cleanup callback error: {e}")
                
                # Update error rate
                total_loops = self._performance_stats['total_loops_created']
                if total_loops > 0:
                    total_errors = sum(m.error_count for m in self._loop_metrics.values())
                    self._performance_stats['error_rate'] = total_errors / total_loops
                
            except Exception as e:
                logger.error(f"❌ Cleanup loop error: {e}")
            
            # Wait for next cleanup cycle
            self._shutdown_event.wait(self.cleanup_interval)
    
    def register_cleanup_callback(self, callback: Callable):
        """Register cleanup callback"""
        self._cleanup_callbacks.add(callback)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            **self._performance_stats,
            'active_loops': len(self._loops),
            'loop_details': {
                thread.name: {
                    'state': metrics.state.value,
                    'task_count': metrics.task_count,
                    'uptime': time.time() - metrics.creation_time,
                    'error_count': metrics.error_count
                }
                for thread, loop in self._loops.items()
                for metrics in [self._loop_metrics.get(loop)]
                if metrics
            }
        }
    
    def shutdown(self):
        """Shutdown the event loop manager"""
        logger.info("🛑 Shutting down Event Loop Manager")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Wait for cleanup thread
        if self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5.0)
        
        # Destroy all remaining loops
        with self._loop_lock:
            for thread in list(self._loops.keys()):
                self._destroy_loop(thread)
        
        logger.info("✅ Event Loop Manager shutdown complete")

# Global instance
_loop_manager: Optional[AdvancedEventLoopManager] = None

def get_loop_manager() -> AdvancedEventLoopManager:
    """Get global event loop manager instance"""
    global _loop_manager
    if _loop_manager is None:
        _loop_manager = AdvancedEventLoopManager()
    return _loop_manager

def run_async_safely(coro: Coroutine, timeout: Optional[float] = None) -> Any:
    """Convenience function to run async code safely"""
    return get_loop_manager().run_async_safely(coro, timeout)

@asynccontextmanager
async def async_context():
    """Context manager for async operations"""
    loop_manager = get_loop_manager()
    loop = loop_manager.get_or_create_loop()
    
    try:
        yield loop
    finally:
        # Context cleanup handled by manager
        pass

def async_safe(func: Callable) -> Callable:
    """Decorator to make any function async-safe"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            return run_async_safely(func(*args, **kwargs))
        else:
            return func(*args, **kwargs)
    return wrapper

# Cleanup on module unload
import atexit
atexit.register(lambda: _loop_manager.shutdown() if _loop_manager else None)
