#!/usr/bin/env python3
"""
⚡ Optimized Async/Await Handler
Fixes event loop issues and provides proper async management
"""

import asyncio
import concurrent.futures
import contextvars
import functools
import logging
import sys
import threading
import time
from typing import Any, Callable, Coroutine, Optional, TypeVar, Union
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type variables
T = TypeVar('T')

class OptimizedEventLoopManager:
    """Manages event loops properly across different contexts"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._main_loop = None
        self._thread_loops = {}
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        
    def get_or_create_loop(self) -> asyncio.AbstractEventLoop:
        """Get current loop or create new one safely"""
        try:
            # Try to get running loop (Python 3.10+)
            if sys.version_info >= (3, 10):
                try:
                    return asyncio.get_running_loop()
                except RuntimeError:
                    pass
            
            # Try to get current event loop
            try:
                loop = asyncio.get_event_loop()
                if loop and not loop.is_closed():
                    return loop
            except RuntimeError:
                pass
            
            # Create new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
            
        except Exception as e:
            logger.error(f"Failed to get/create event loop: {e}")
            # Fallback: create a simple new loop
            return asyncio.new_event_loop()
    
    def run_async(self, coro: Coroutine[Any, Any, T]) -> T:
        """Run async coroutine safely in any context"""
        # Check if we're already in an async context
        try:
            # If a loop is running, schedule the coroutine as a task
            asyncio.get_running_loop()
            return asyncio.create_task(coro)
        except RuntimeError:
            # Not in async context; proceed to run synchronously
            pass

        # Get or create event loop
        loop = self.get_or_create_loop()

        # If loop is running, schedule coroutine thread-safely
        if loop.is_running():
            future = asyncio.run_coroutine_threadsafe(coro, loop)
            return future.result()
        else:
            # Run to completion in this thread
            try:
                return loop.run_until_complete(coro)
            finally:
                # Keep loop open for potential reuse (no-op placeholder)
                if loop and not loop.is_closed():
                    pass
    
    def cleanup(self):
        """Clean up resources"""
        self._executor.shutdown(wait=True)
        
        # Close thread loops
        for loop in self._thread_loops.values():
            if not loop.is_closed():
                loop.close()
        
        # Close main loop if exists
        if self._main_loop and not self._main_loop.is_closed():
            self._main_loop.close()

class AsyncContextManager:
    """Manages async context properly"""
    
    def __init__(self):
        self.loop_manager = OptimizedEventLoopManager()
        self._context_stack = []
        
    async def __aenter__(self):
        """Enter async context"""
        self._context_stack.append(asyncio.current_task())
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context"""
        if self._context_stack:
            self._context_stack.pop()
        return False
    
    @staticmethod
    def ensure_async(func: Callable) -> Callable:
        """Decorator to ensure function runs in async context"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if asyncio.iscoroutinefunction(func):
                loop_manager = OptimizedEventLoopManager()
                return loop_manager.run_async(func(*args, **kwargs))
            else:
                return func(*args, **kwargs)
        return wrapper

class OptimizedAsyncExecutor:
    """Optimized async execution with proper error handling"""
    
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.pending_tasks = set()
        
    async def execute(self, coro: Coroutine) -> Any:
        """Execute coroutine with concurrency control"""
        async with self.semaphore:
            task = asyncio.create_task(coro)
            self.pending_tasks.add(task)
            try:
                result = await task
                return result
            except asyncio.CancelledError:
                logger.warning("Task cancelled")
                raise
            except Exception as e:
                logger.error(f"Task failed: {e}")
                raise
            finally:
                self.pending_tasks.discard(task)
    
    async def execute_batch(self, coros: list) -> list:
        """Execute multiple coroutines with optimization"""
        tasks = []
        for coro in coros:
            task = self.execute(coro)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        clean_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Batch execution error: {result}")
            else:
                clean_results.append(result)
        
        return clean_results
    
    async def cleanup(self):
        """Cancel all pending tasks"""
        for task in self.pending_tasks:
            task.cancel()
        
        if self.pending_tasks:
            await asyncio.gather(*self.pending_tasks, return_exceptions=True)

def async_safe(func: Callable) -> Callable:
    """Decorator to make any function async-safe"""
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            # Run sync function in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, func, *args, **kwargs)
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            loop_manager = OptimizedEventLoopManager()
            return loop_manager.run_async(func(*args, **kwargs))
        else:
            return func(*args, **kwargs)
    
    # Return appropriate wrapper based on context
    try:
        asyncio.get_running_loop()
        return async_wrapper
    except RuntimeError:
        return sync_wrapper

class AsyncTaskManager:
    """Manages async tasks with proper lifecycle"""
    
    def __init__(self):
        self.tasks = {}
        self.completed_tasks = {}
        self._lock = asyncio.Lock()
        
    async def create_task(self, name: str, coro: Coroutine) -> asyncio.Task:
        """Create and track a task"""
        async with self._lock:
            if name in self.tasks:
                # Cancel existing task
                self.tasks[name].cancel()
                
            task = asyncio.create_task(coro)
            self.tasks[name] = task
            
            # Add completion callback
            task.add_done_callback(
                lambda t: asyncio.create_task(self._task_done(name, t))
            )
            
            return task
    
    async def _task_done(self, name: str, task: asyncio.Task):
        """Handle task completion"""
        async with self._lock:
            if name in self.tasks:
                del self.tasks[name]
                self.completed_tasks[name] = {
                    'completed_at': time.time(),
                    'exception': task.exception() if not task.cancelled() else None,
                    'cancelled': task.cancelled()
                }
    
    async def cancel_task(self, name: str) -> bool:
        """Cancel a specific task"""
        async with self._lock:
            if name in self.tasks:
                self.tasks[name].cancel()
                return True
            return False
    
    async def cancel_all(self):
        """Cancel all running tasks"""
        async with self._lock:
            for task in self.tasks.values():
                task.cancel()
            
            # Wait for all to complete
            if self.tasks:
                await asyncio.gather(*self.tasks.values(), return_exceptions=True)
    
    async def wait_for_task(self, name: str, timeout: float = None) -> Any:
        """Wait for a specific task to complete"""
        async with self._lock:
            if name not in self.tasks:
                if name in self.completed_tasks:
                    return self.completed_tasks[name]
                return None
            
            task = self.tasks[name]
        
        try:
            return await asyncio.wait_for(task, timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Task {name} timed out")
            return None

class AsyncResourceManager:
    """Manages async resources with proper cleanup"""
    
    def __init__(self):
        self.resources = {}
        self._cleanup_handlers = {}
        
    async def acquire(self, name: str, factory: Callable) -> Any:
        """Acquire a resource"""
        if name not in self.resources:
            resource = await factory() if asyncio.iscoroutinefunction(factory) else factory()
            self.resources[name] = resource
        return self.resources[name]
    
    async def release(self, name: str):
        """Release a resource"""
        if name in self.resources:
            # Call cleanup handler if exists
            if name in self._cleanup_handlers:
                handler = self._cleanup_handlers[name]
                if asyncio.iscoroutinefunction(handler):
                    await handler(self.resources[name])
                else:
                    handler(self.resources[name])
            
            del self.resources[name]
            if name in self._cleanup_handlers:
                del self._cleanup_handlers[name]
    
    def register_cleanup(self, name: str, handler: Callable):
        """Register cleanup handler for resource"""
        self._cleanup_handlers[name] = handler
    
    async def cleanup_all(self):
        """Clean up all resources"""
        for name in list(self.resources.keys()):
            await self.release(name)

# Global instances
_loop_manager = None
_task_manager = None
_resource_manager = None

def get_loop_manager() -> OptimizedEventLoopManager:
    """Get global loop manager"""
    global _loop_manager
    if not _loop_manager:
        _loop_manager = OptimizedEventLoopManager()
    return _loop_manager

def get_task_manager() -> AsyncTaskManager:
    """Get global task manager"""
    global _task_manager
    if not _task_manager:
        _task_manager = AsyncTaskManager()
    return _task_manager

def get_resource_manager() -> AsyncResourceManager:
    """Get global resource manager"""
    global _resource_manager
    if not _resource_manager:
        _resource_manager = AsyncResourceManager()
    return _resource_manager

async def optimized_gather(*coros, return_exceptions=False, max_concurrent=10):
    """Optimized version of asyncio.gather with concurrency control"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def bounded_coro(coro):
        async with semaphore:
            try:
                return await coro
            except Exception as e:
                if return_exceptions:
                    return e
                raise
    
    tasks = [bounded_coro(coro) for coro in coros]
    return await asyncio.gather(*tasks)

def run_async_safe(coro: Coroutine) -> Any:
    """Run async coroutine safely from any context"""
    loop_manager = get_loop_manager()
    return loop_manager.run_async(coro)

# Cleanup on exit
import atexit

def cleanup():
    """Cleanup all async resources"""
    # Do not create new resources during interpreter shutdown.
    # Only clean up if a loop manager already exists.
    global _loop_manager
    if _loop_manager is not None:
        try:
            _loop_manager.cleanup()
        except Exception:
            # Best-effort cleanup during atexit
            pass

atexit.register(cleanup)

# Example usage and testing
async def example_async_function(value: int) -> int:
    """Example async function"""
    await asyncio.sleep(0.1)
    return value * 2

def example_sync_function(value: int) -> int:
    """Example sync function"""
    time.sleep(0.1)
    return value * 2

@async_safe
async def mixed_function(value: int) -> int:
    """Function that works in both sync and async contexts"""
    await asyncio.sleep(0.1)
    return value * 3

async def test_async_optimizations():
    """Test async optimizations"""
    print("Testing Async Optimizations...")
    
    # Test executor
    executor = OptimizedAsyncExecutor(max_concurrent=5)
    
    # Test batch execution
    coros = [example_async_function(i) for i in range(10)]
    results = await executor.execute_batch(coros)
    print(f"Batch results: {results}")
    
    # Test task manager
    task_manager = get_task_manager()
    await task_manager.create_task("test_task", example_async_function(5))
    result = await task_manager.wait_for_task("test_task")
    print(f"Task result: {result}")
    
    # Test resource manager
    resource_manager = get_resource_manager()
    
    async def create_resource():
        return {"data": "test_resource"}
    
    resource = await resource_manager.acquire("test", create_resource)
    print(f"Resource: {resource}")
    
    await resource_manager.cleanup_all()
    await executor.cleanup()
    
    print("✅ Async optimizations test complete!")

if __name__ == "__main__":
    # Run tests
    run_async_safe(test_async_optimizations())
