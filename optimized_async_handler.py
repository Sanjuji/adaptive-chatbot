#!/usr/bin/env python3
"""
Lightweight compatibility layer for async utilities used in tests.

This module provides minimal, dependency-free implementations that satisfy
the test suite contracts. When src.optimized_async_handler is importable,
we defer to it. Otherwise we fall back to the implementations below.
"""

from __future__ import annotations

import asyncio
import functools
import threading
import time
from typing import Any, Callable, Coroutine, Optional, List

# Try to import the full implementation from src first.
try:
    from src.optimized_async_handler import (  # type: ignore
        OptimizedEventLoopManager,
        AsyncTaskManager,
        AsyncResourceManager,
        get_loop_manager,
        get_task_manager,
        get_resource_manager,
        optimized_gather,
        run_async_safe,
    )
    SRC_BACKEND = True
except Exception:
    SRC_BACKEND = False

if not SRC_BACKEND:
    # Minimal, test-oriented implementations

    TCoroutine = Coroutine[Any, Any, Any]

    class OptimizedEventLoopManager:
        """Manage an asyncio event loop that works in both sync/async contexts."""

        _instance: Optional["OptimizedEventLoopManager"] = None
        _lock = threading.Lock()

        def __new__(cls):
            if cls._instance is None:
                with cls._lock:
                    if cls._instance is None:
                        cls._instance = super().__new__(cls)
                        cls._instance._initialized = False
            return cls._instance

        def __init__(self) -> None:
            if getattr(self, "_initialized", False):
                return
            self._initialized = True
            self._loop: Optional[asyncio.AbstractEventLoop] = None

        def get_or_create_loop(self) -> asyncio.AbstractEventLoop:
            # If already running in an event loop, return it
            try:
                running = asyncio.get_running_loop()
                return running
            except RuntimeError:
                pass

            # Reuse cached loop if available and open
            if self._loop and not self._loop.is_closed():
                return self._loop

            # Create a new loop and set it
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            return self._loop

        def run_async(self, coro: TCoroutine) -> Any:
            """Run a coroutine from any context and return its result."""
            try:
                running = asyncio.get_running_loop()
                # Schedule in the current loop (returns Task); we must await in tests,
                # but tests call from sync code, so prefer thread-safe path instead.
                # Use a thread-safe submission to avoid returning a Task to sync code.
                fut = asyncio.run_coroutine_threadsafe(coro, running)
                return fut.result()
            except RuntimeError:
                # Not in an async context
                loop = self.get_or_create_loop()
                return loop.run_until_complete(coro)

        def cleanup(self) -> None:
            """No-op cleanup to satisfy atexit without side effects."""
            try:
                if self._loop and not self._loop.is_closed():
                    # Do not close loop aggressively in tests; background tasks may exist.
                    pass
            except Exception:
                pass

    class AsyncTaskManager:
        """Track async tasks and provide simple lifecycle helpers."""

        def __init__(self) -> None:
            self.tasks: dict[str, asyncio.Task] = {}
            self.completed: dict[str, Any] = {}
            self._lock = asyncio.Lock()

        async def create_task(self, name: str, coro: TCoroutine) -> asyncio.Task:
            async with self._lock:
                if name in self.tasks:
                    self.tasks[name].cancel()
                task = asyncio.create_task(coro)
                self.tasks[name] = task

                def _on_done(t: asyncio.Task, task_name: str = name) -> None:
                    try:
                        self.completed[task_name] = t.result()
                    except Exception as e:
                        self.completed[task_name] = e
                    finally:
                        self.tasks.pop(task_name, None)

                task.add_done_callback(_on_done)
                return task

        async def cancel_task(self, name: str) -> bool:
            async with self._lock:
                t = self.tasks.get(name)
                if t:
                    t.cancel()
                    return True
                return False

        async def cancel_all(self) -> None:
            async with self._lock:
                for t in list(self.tasks.values()):
                    t.cancel()
                if self.tasks:
                    await asyncio.gather(*self.tasks.values(), return_exceptions=True)
                self.tasks.clear()

        async def wait_for_task(self, name: str, timeout: Optional[float] = None) -> Any:
            async with self._lock:
                if name not in self.tasks:
                    # Return completed result if available
                    if name in self.completed:
                        return self.completed[name]
                    return None
                t = self.tasks[name]
            try:
                return await asyncio.wait_for(t, timeout=timeout)
            except asyncio.TimeoutError:
                return None

    class AsyncResourceManager:
        """Simple resource registry with optional cleanup callbacks."""

        def __init__(self) -> None:
            self.resources: dict[str, Any] = {}
            self._cleanup: dict[str, Callable[[Any], Any]] = {}

        async def acquire(self, name: str, factory: Callable[[], Any]) -> Any:
            if name not in self.resources:
                res = factory() if not asyncio.iscoroutinefunction(factory) else await factory()
                self.resources[name] = res
            return self.resources[name]

        def register_cleanup(self, name: str, handler: Callable[[Any], Any]) -> None:
            self._cleanup[name] = handler

        async def release(self, name: str) -> None:
            if name in self.resources:
                res = self.resources.pop(name)
                handler = self._cleanup.pop(name, None)
                if handler:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(res)
                    else:
                        handler(res)

        async def cleanup_all(self) -> None:
            for name in list(self.resources.keys()):
                await self.release(name)

    _loop_manager: Optional[OptimizedEventLoopManager] = None
    _task_manager: Optional[AsyncTaskManager] = None
    _resource_manager: Optional[AsyncResourceManager] = None

    def get_loop_manager() -> OptimizedEventLoopManager:
        global _loop_manager
        if _loop_manager is None:
            _loop_manager = OptimizedEventLoopManager()
        return _loop_manager

    def get_task_manager() -> AsyncTaskManager:
        global _task_manager
        if _task_manager is None:
            _task_manager = AsyncTaskManager()
        return _task_manager

    def get_resource_manager() -> AsyncResourceManager:
        global _resource_manager
        if _resource_manager is None:
            _resource_manager = AsyncResourceManager()
        return _resource_manager

    async def optimized_gather(*coros, return_exceptions: bool = False, max_concurrent: int = 10) -> List[Any]:
        sem = asyncio.Semaphore(max_concurrent)

        async def _wrap(c):
            async with sem:
                try:
                    return await c
                except Exception as e:
                    if return_exceptions:
                        return e
                    raise

        tasks = [_wrap(c) for c in coros]
        return await asyncio.gather(*tasks)

    def run_async_safe(coro: TCoroutine) -> Any:
        return get_loop_manager().run_async(coro)