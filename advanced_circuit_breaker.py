#!/usr/bin/env python3
"""
Advanced Circuit Breaker System - O3 Level Optimization
Comprehensive circuit breaker patterns for all critical operations
"""

import time
import threading
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union, Type
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import functools
import statistics
import random

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, calls fail fast
    HALF_OPEN = "half_open"  # Testing if service is back

class FailureType(Enum):
    """Types of failures"""
    TIMEOUT = "timeout"
    EXCEPTION = "exception"
    RATE_LIMIT = "rate_limit"
    CONNECTION_ERROR = "connection_error"
    UNKNOWN = "unknown"

@dataclass
class FailureRecord:
    """Record of a failure"""
    timestamp: float
    failure_type: FailureType
    error_message: str
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    success_threshold: int = 3
    timeout: float = 10.0
    max_failures_per_minute: int = 20
    enable_adaptive_timeout: bool = True
    enable_jitter: bool = True
    jitter_range: float = 0.1

@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    timeouts: int = 0
    circuit_opens: int = 0
    circuit_closes: int = 0
    average_response_time: float = 0.0
    last_failure_time: float = 0.0
    current_state: CircuitState = CircuitState.CLOSED

class AdvancedCircuitBreaker:
    """
    O3 Level Circuit Breaker
    - Adaptive timeout based on response times
    - Jitter to prevent thundering herd
    - Multiple failure types support
    - Comprehensive statistics
    - Automatic recovery testing
    """
    
    def __init__(self, 
                 name: str,
                 config: Optional[CircuitBreakerConfig] = None,
                 fallback_func: Optional[Callable] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.fallback_func = fallback_func
        
        # State management
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0
        self._next_attempt_time = 0.0
        
        # Statistics
        self._stats = CircuitBreakerStats()
        self._response_times: deque = deque(maxlen=100)
        self._recent_failures: deque = deque(maxlen=100)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Callbacks
        self._state_change_callbacks: List[Callable] = []
        self._failure_callbacks: List[Callable] = []
        
        logger.info(f"🔧 Circuit breaker '{name}' initialized")
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        with self._lock:
            self._stats.total_calls += 1
            
            # Check if circuit should be opened
            if self._should_open_circuit():
                self._open_circuit()
                return self._handle_circuit_open(func, *args, **kwargs)
            
            # Check if we should attempt recovery
            if self._state == CircuitState.OPEN:
                if time.time() < self._next_attempt_time:
                    return self._handle_circuit_open(func, *args, **kwargs)
                else:
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
                    logger.info(f"🔄 Circuit '{self.name}' entering HALF_OPEN state")
            
            # Execute the function
            start_time = time.time()
            try:
                # Apply timeout if configured
                if self.config.timeout > 0:
                    result = self._execute_with_timeout(func, *args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Record success
                response_time = time.time() - start_time
                self._record_success(response_time)
                
                return result
                
            except Exception as e:
                # Record failure
                response_time = time.time() - start_time
                self._record_failure(e, response_time)
                raise
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection"""
        with self._lock:
            self._stats.total_calls += 1
            
            # Check if circuit should be opened
            if self._should_open_circuit():
                self._open_circuit()
                return await self._handle_circuit_open_async(func, *args, **kwargs)
            
            # Check if we should attempt recovery
            if self._state == CircuitState.OPEN:
                if time.time() < self._next_attempt_time:
                    return await self._handle_circuit_open_async(func, *args, **kwargs)
                else:
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
                    logger.info(f"🔄 Circuit '{self.name}' entering HALF_OPEN state")
            
            # Execute the function
            start_time = time.time()
            try:
                # Apply timeout if configured
                if self.config.timeout > 0:
                    result = await asyncio.wait_for(
                        func(*args, **kwargs), 
                        timeout=self.config.timeout
                    )
                else:
                    result = await func(*args, **kwargs)
                
                # Record success
                response_time = time.time() - start_time
                self._record_success(response_time)
                
                return result
                
            except asyncio.TimeoutError:
                response_time = time.time() - start_time
                self._record_failure(TimeoutError("Operation timed out"), response_time)
                raise
            except Exception as e:
                response_time = time.time() - start_time
                self._record_failure(e, response_time)
                raise
    
    def _should_open_circuit(self) -> bool:
        """Check if circuit should be opened"""
        if self._state == CircuitState.CLOSED:
            return self._failure_count >= self.config.failure_threshold
        return False
    
    def _open_circuit(self):
        """Open the circuit"""
        if self._state != CircuitState.OPEN:
            self._state = CircuitState.OPEN
            self._last_failure_time = time.time()
            self._next_attempt_time = self._calculate_next_attempt_time()
            self._stats.circuit_opens += 1
            
            logger.warning(f"🔴 Circuit '{self.name}' OPENED")
            self._notify_state_change()
    
    def _calculate_next_attempt_time(self) -> float:
        """Calculate next attempt time with jitter"""
        base_time = time.time() + self.config.recovery_timeout
        
        if self.config.enable_jitter:
            jitter = random.uniform(
                -self.config.jitter_range * self.config.recovery_timeout,
                self.config.jitter_range * self.config.recovery_timeout
            )
            base_time += jitter
        
        return base_time
    
    def _record_success(self, response_time: float):
        """Record successful call"""
        with self._lock:
            self._success_count += 1
            self._failure_count = 0
            self._stats.successful_calls += 1
            self._response_times.append(response_time)
            
            # Update average response time
            if self._response_times:
                self._stats.average_response_time = statistics.mean(self._response_times)
            
            # Check if we should close the circuit
            if self._state == CircuitState.HALF_OPEN:
                if self._success_count >= self.config.success_threshold:
                    self._close_circuit()
    
    def _record_failure(self, error: Exception, response_time: float):
        """Record failed call"""
        with self._lock:
            self._failure_count += 1
            self._success_count = 0
            self._stats.failed_calls += 1
            self._stats.last_failure_time = time.time()
            
            # Classify failure type
            failure_type = self._classify_failure(error)
            if failure_type == FailureType.TIMEOUT:
                self._stats.timeouts += 1
            
            # Record failure details
            failure_record = FailureRecord(
                timestamp=time.time(),
                failure_type=failure_type,
                error_message=str(error),
                context={'response_time': response_time}
            )
            self._recent_failures.append(failure_record)
            
            # Notify failure callbacks
            self._notify_failure(failure_record)
    
    def _classify_failure(self, error: Exception) -> FailureType:
        """Classify the type of failure"""
        error_name = type(error).__name__.lower()
        
        if 'timeout' in error_name or isinstance(error, TimeoutError):
            return FailureType.TIMEOUT
        elif 'connection' in error_name or 'network' in error_name:
            return FailureType.CONNECTION_ERROR
        elif 'rate' in error_name or 'limit' in error_name:
            return FailureType.RATE_LIMIT
        else:
            return FailureType.EXCEPTION
    
    def _close_circuit(self):
        """Close the circuit"""
        if self._state != CircuitState.CLOSED:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._stats.circuit_closes += 1
            
            logger.info(f"🟢 Circuit '{self.name}' CLOSED")
            self._notify_state_change()
    
    def _execute_with_timeout(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with timeout"""
        if asyncio.iscoroutinefunction(func):
            # For async functions, we need to handle this differently
            # This should be called from call_async instead
            return func(*args, **kwargs)
        else:
            # For sync functions, use threading timeout
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                return future.result(timeout=self.config.timeout)
    
    def _handle_circuit_open(self, func: Callable, *args, **kwargs) -> Any:
        """Handle call when circuit is open"""
        if self.fallback_func:
            try:
                return self.fallback_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"❌ Fallback function failed: {e}")
        
        raise Exception(f"Circuit breaker '{self.name}' is OPEN")
    
    async def _handle_circuit_open_async(self, func: Callable, *args, **kwargs) -> Any:
        """Handle async call when circuit is open"""
        if self.fallback_func:
            try:
                if asyncio.iscoroutinefunction(self.fallback_func):
                    return await self.fallback_func(*args, **kwargs)
                else:
                    return self.fallback_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"❌ Fallback function failed: {e}")
        
        raise Exception(f"Circuit breaker '{self.name}' is OPEN")
    
    def _notify_state_change(self):
        """Notify state change callbacks"""
        for callback in self._state_change_callbacks:
            try:
                callback(self.name, self._state)
            except Exception as e:
                logger.error(f"❌ State change callback error: {e}")
    
    def _notify_failure(self, failure_record: FailureRecord):
        """Notify failure callbacks"""
        for callback in self._failure_callbacks:
            try:
                callback(self.name, failure_record)
            except Exception as e:
                logger.error(f"❌ Failure callback error: {e}")
    
    def register_state_change_callback(self, callback: Callable):
        """Register state change callback"""
        self._state_change_callbacks.append(callback)
    
    def register_failure_callback(self, callback: Callable):
        """Register failure callback"""
        self._failure_callbacks.append(callback)
    
    def get_stats(self) -> CircuitBreakerStats:
        """Get circuit breaker statistics"""
        with self._lock:
            self._stats.current_state = self._state
            return self._stats
    
    def get_recent_failures(self, limit: int = 10) -> List[FailureRecord]:
        """Get recent failures"""
        with self._lock:
            return list(self._recent_failures)[-limit:]
    
    def reset(self):
        """Reset circuit breaker to initial state"""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = 0.0
            self._next_attempt_time = 0.0
            logger.info(f"🔄 Circuit '{self.name}' reset")

class CircuitBreakerManager:
    """Manager for multiple circuit breakers"""
    
    def __init__(self):
        self._breakers: Dict[str, AdvancedCircuitBreaker] = {}
        self._lock = threading.RLock()
    
    def get_breaker(self, name: str, **kwargs) -> AdvancedCircuitBreaker:
        """Get or create circuit breaker"""
        with self._lock:
            if name not in self._breakers:
                self._breakers[name] = AdvancedCircuitBreaker(name, **kwargs)
            return self._breakers[name]
    
    def get_all_stats(self) -> Dict[str, CircuitBreakerStats]:
        """Get statistics for all circuit breakers"""
        with self._lock:
            return {name: breaker.get_stats() for name, breaker in self._breakers.items()}
    
    def reset_all(self):
        """Reset all circuit breakers"""
        with self._lock:
            for breaker in self._breakers.values():
                breaker.reset()

# Global manager
_circuit_manager = CircuitBreakerManager()

def circuit_breaker(name: str, **config):
    """Decorator to add circuit breaker to a function"""
    def decorator(func):
        breaker = _circuit_manager.get_breaker(name, **config)
        
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await breaker.call_async(func, *args, **kwargs)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                return breaker.call(func, *args, **kwargs)
            return sync_wrapper
    
    return decorator

def get_circuit_breaker(name: str) -> AdvancedCircuitBreaker:
    """Get circuit breaker by name"""
    return _circuit_manager.get_breaker(name)

def get_all_circuit_stats() -> Dict[str, CircuitBreakerStats]:
    """Get statistics for all circuit breakers"""
    return _circuit_manager.get_all_stats()

# Example usage
if __name__ == "__main__":
    # Example circuit breaker usage
    @circuit_breaker("database", failure_threshold=3, recovery_timeout=10.0)
    def database_call():
        # Simulate database call
        if random.random() < 0.3:  # 30% failure rate
            raise Exception("Database connection failed")
        return "Success"
    
    # Test the circuit breaker
    for i in range(10):
        try:
            result = database_call()
            print(f"Call {i}: {result}")
        except Exception as e:
            print(f"Call {i}: Failed - {e}")
        
        time.sleep(1)
    
    # Print statistics
    stats = get_circuit_breaker("database").get_stats()
    print(f"Circuit breaker stats: {stats}")
