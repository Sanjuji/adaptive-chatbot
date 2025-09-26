#!/usr/bin/env python3
"""
Intelligent Error Recovery System - Advanced Error Handling & Recovery
Provides comprehensive error handling, fallback mechanisms, graceful degradation, and automatic recovery
Ensures system reliability and continuous operation even during failures
"""

import asyncio
import json
import time
import threading
import traceback
from typing import Dict, List, Any, Optional, Callable, Union, Type
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
from pathlib import Path
from enum import Enum
import functools
import inspect
import sys

from logger import log_info, log_error, log_warning
from performance_monitor import monitor_performance, MetricType, get_performance_monitor

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"           # Minor issues, system continues normally
    MEDIUM = "medium"     # Moderate issues, degraded functionality
    HIGH = "high"         # Serious issues, significant impact
    CRITICAL = "critical" # System-threatening issues, immediate attention

class RecoveryStrategy(Enum):
    """Available recovery strategies"""
    RETRY = "retry"                    # Retry the operation
    FALLBACK = "fallback"             # Use fallback mechanism
    DEGRADE = "degrade"               # Graceful degradation
    RESTART = "restart"               # Restart component
    IGNORE = "ignore"                 # Ignore and continue
    ESCALATE = "escalate"             # Escalate to human operator

class ComponentState(Enum):
    """Component health states"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    FAILED = "failed"
    RECOVERING = "recovering"

@dataclass
class ErrorRecord:
    """Error record for tracking and analysis"""
    error_id: str
    timestamp: datetime
    component: str
    error_type: str
    severity: ErrorSeverity
    message: str
    stack_trace: Optional[str]
    context: Dict[str, Any]
    recovery_attempted: bool = False
    recovery_strategy: Optional[RecoveryStrategy] = None
    recovery_successful: bool = False

@dataclass
class ComponentHealth:
    """Component health status"""
    component_name: str
    state: ComponentState
    last_error: Optional[ErrorRecord]
    error_count: int
    success_count: int
    last_success: Optional[datetime]
    health_score: float  # 0.0 - 1.0
    recovery_attempts: int = 0

@dataclass
class RecoveryAction:
    """Recovery action definition"""
    name: str
    strategy: RecoveryStrategy
    max_attempts: int
    backoff_factor: float
    timeout_seconds: float
    conditions: Dict[str, Any]
    action_function: Optional[Callable] = None

class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, 
                 name: str,
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 expected_exception: Type[Exception] = Exception):
        
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
        
        self._lock = threading.RLock()
    
    def __call__(self, func):
        """Decorator to wrap function with circuit breaker"""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            with self._lock:
                if self.state == "open":
                    if self._should_attempt_reset():
                        self.state = "half-open"
                        log_info(f"🔄 Circuit breaker {self.name} attempting reset")
                    else:
                        raise Exception(f"Circuit breaker {self.name} is open")
                
                try:
                    result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                    
                    if self.state == "half-open":
                        self.state = "closed"
                        self.failure_count = 0
                        log_info(f"✅ Circuit breaker {self.name} reset successfully")
                    
                    return result
                    
                except self.expected_exception as e:
                    self._record_failure()
                    raise
        
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit breaker"""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _record_failure(self):
        """Record a failure"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            log_warning(f"⚠️ Circuit breaker {self.name} opened after {self.failure_count} failures")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state"""
        return {
            "name": self.name,
            "state": self.state,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "failure_threshold": self.failure_threshold
        }

class FallbackManager:
    """Manages fallback mechanisms for different components"""
    
    def __init__(self):
        self.fallback_handlers = {}  # Component -> Fallback function
        self.fallback_cache = {}     # Component -> Cached fallback results
        self.fallback_stats = defaultdict(int)  # Track fallback usage
    
    def register_fallback(self, component: str, fallback_func: Callable, cache_duration: int = 300):
        """Register a fallback handler for a component"""
        self.fallback_handlers[component] = {
            'function': fallback_func,
            'cache_duration': cache_duration,
            'last_used': None
        }
        log_info(f"📋 Registered fallback for {component}")
    
    async def execute_fallback(self, component: str, context: Dict[str, Any] = None) -> Any:
        """Execute fallback for a component"""
        if component not in self.fallback_handlers:
            log_warning(f"No fallback handler registered for {component}")
            return None
        
        handler = self.fallback_handlers[component]
        
        # Check cache first
        cache_key = f"{component}_{hash(str(context))}"
        if cache_key in self.fallback_cache:
            cache_entry = self.fallback_cache[cache_key]
            if time.time() - cache_entry['timestamp'] < handler['cache_duration']:
                log_info(f"🔄 Using cached fallback for {component}")
                return cache_entry['result']
        
        try:
            # Execute fallback
            log_info(f"🆘 Executing fallback for {component}")
            
            if asyncio.iscoroutinefunction(handler['function']):
                result = await handler['function'](context or {})
            else:
                result = handler['function'](context or {})
            
            # Cache result
            self.fallback_cache[cache_key] = {
                'result': result,
                'timestamp': time.time()
            }
            
            # Update stats
            self.fallback_stats[component] += 1
            handler['last_used'] = datetime.now()
            
            return result
            
        except Exception as e:
            log_error(f"Fallback execution failed for {component}: {e}")
            return None
    
    def get_fallback_stats(self) -> Dict[str, Any]:
        """Get fallback usage statistics"""
        return {
            'registered_fallbacks': list(self.fallback_handlers.keys()),
            'usage_stats': dict(self.fallback_stats),
            'cache_size': len(self.fallback_cache)
        }

class GracefulDegradation:
    """Manages graceful degradation of system functionality"""
    
    def __init__(self):
        self.feature_priorities = {}  # Feature -> Priority level (1-10)
        self.degraded_features = set()
        self.degradation_rules = {}   # Condition -> Features to degrade
        
    def set_feature_priority(self, feature: str, priority: int):
        """Set priority for a feature (1 = lowest, 10 = highest)"""
        self.feature_priorities[feature] = priority
        log_info(f"📊 Set priority {priority} for feature {feature}")
    
    def add_degradation_rule(self, condition: str, features_to_degrade: List[str]):
        """Add a degradation rule"""
        self.degradation_rules[condition] = features_to_degrade
        log_info(f"📋 Added degradation rule: {condition} -> {features_to_degrade}")
    
    def evaluate_degradation(self, system_state: Dict[str, Any]) -> List[str]:
        """Evaluate which features should be degraded based on system state"""
        features_to_degrade = set()
        
        # Check degradation rules
        for condition, features in self.degradation_rules.items():
            if self._evaluate_condition(condition, system_state):
                features_to_degrade.update(features)
        
        # Apply priority-based degradation if needed
        if system_state.get('memory_usage_percent', 0) > 80:
            # Degrade low-priority features
            low_priority_features = [
                feature for feature, priority in self.feature_priorities.items()
                if priority <= 3
            ]
            features_to_degrade.update(low_priority_features)
        
        return list(features_to_degrade)
    
    def _evaluate_condition(self, condition: str, system_state: Dict[str, Any]) -> bool:
        """Evaluate a degradation condition"""
        try:
            # Simple condition evaluation (can be extended)
            if condition == "high_memory":
                return system_state.get('memory_usage_percent', 0) > 75
            elif condition == "high_error_rate":
                return system_state.get('error_rate', 0) > 10
            elif condition == "slow_response":
                return system_state.get('avg_response_time', 0) > 2000
            elif condition == "many_failures":
                return system_state.get('component_failures', 0) > 3
            
            return False
            
        except Exception as e:
            log_error(f"Failed to evaluate degradation condition {condition}: {e}")
            return False
    
    def apply_degradation(self, features: List[str]):
        """Apply degradation to specified features"""
        newly_degraded = []
        
        for feature in features:
            if feature not in self.degraded_features:
                self.degraded_features.add(feature)
                newly_degraded.append(feature)
                log_warning(f"🔻 Degrading feature: {feature}")
        
        return newly_degraded
    
    def restore_features(self, features: List[str] = None):
        """Restore degraded features"""
        if features is None:
            features = list(self.degraded_features)
        
        restored = []
        for feature in features:
            if feature in self.degraded_features:
                self.degraded_features.remove(feature)
                restored.append(feature)
                log_info(f"🔺 Restored feature: {feature}")
        
        return restored
    
    def is_feature_degraded(self, feature: str) -> bool:
        """Check if a feature is currently degraded"""
        return feature in self.degraded_features
    
    def get_degradation_status(self) -> Dict[str, Any]:
        """Get current degradation status"""
        return {
            'degraded_features': list(self.degraded_features),
            'feature_priorities': self.feature_priorities,
            'degradation_rules': self.degradation_rules
        }

class IntelligentErrorRecoverySystem:
    """Main error recovery system with intelligent recovery strategies"""
    
    def __init__(self, max_error_history: int = 1000):
        self.max_error_history = max_error_history
        
        # Core components
        self.fallback_manager = FallbackManager()
        self.graceful_degradation = GracefulDegradation()
        
        # Error tracking
        self.error_history = deque(maxlen=max_error_history)
        self.component_health = {}  # Component -> ComponentHealth
        self.circuit_breakers = {}  # Component -> CircuitBreaker
        
        # Recovery strategies
        self.recovery_strategies = {}  # Error type -> RecoveryAction
        self.recovery_history = deque(maxlen=500)
        
        # System state
        self.system_health_score = 1.0
        self.last_health_check = None
        
        # Threading
        self._lock = threading.RLock()
        
        # Initialize default strategies
        self._initialize_default_strategies()
        
        # Initialize component health tracking
        self._initialize_component_health()
        
        log_info("🛡️ Intelligent Error Recovery System initialized")
    
    def _initialize_default_strategies(self):
        """Initialize default recovery strategies"""
        default_strategies = [
            RecoveryAction("connection_retry", RecoveryStrategy.RETRY, 3, 2.0, 30.0, {"error_type": "ConnectionError"}),
            RecoveryAction("timeout_fallback", RecoveryStrategy.FALLBACK, 1, 1.0, 5.0, {"error_type": "TimeoutError"}),
            RecoveryAction("memory_degrade", RecoveryStrategy.DEGRADE, 1, 1.0, 0.0, {"error_type": "MemoryError"}),
            RecoveryAction("model_restart", RecoveryStrategy.RESTART, 2, 5.0, 60.0, {"component": "model_manager"}),
            RecoveryAction("generic_retry", RecoveryStrategy.RETRY, 2, 1.5, 10.0, {"error_type": "Exception"})
        ]
        
        for strategy in default_strategies:
            self.recovery_strategies[strategy.name] = strategy
    
    def _initialize_component_health(self):
        """Initialize component health tracking"""
        components = [
            "multilingual_processor",
            "business_intelligence", 
            "conversation_manager",
            "knowledge_retrieval",
            "voice_synthesis",
            "model_manager",
            "memory_manager"
        ]
        
        for component in components:
            self.component_health[component] = ComponentHealth(
                component_name=component,
                state=ComponentState.HEALTHY,
                last_error=None,
                error_count=0,
                success_count=0,
                last_success=datetime.now(),
                health_score=1.0
            )
    
    def register_circuit_breaker(self, component: str, **kwargs) -> CircuitBreaker:
        """Register a circuit breaker for a component"""
        circuit_breaker = CircuitBreaker(name=component, **kwargs)
        self.circuit_breakers[component] = circuit_breaker
        log_info(f"⚡ Registered circuit breaker for {component}")
        return circuit_breaker
    
    def add_recovery_strategy(self, strategy: RecoveryAction):
        """Add a custom recovery strategy"""
        self.recovery_strategies[strategy.name] = strategy
        log_info(f"🔧 Added recovery strategy: {strategy.name}")
    
    async def handle_error(self, 
                          component: str,
                          error: Exception,
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle an error with intelligent recovery"""
        
        start_time = time.time()
        
        try:
            # Create error record
            error_record = ErrorRecord(
                error_id=f"err_{int(time.time() * 1000)}_{component}",
                timestamp=datetime.now(),
                component=component,
                error_type=type(error).__name__,
                severity=self._classify_error_severity(error, component),
                message=str(error),
                stack_trace=traceback.format_exc(),
                context=context or {}
            )
            
            # Record error
            self._record_error(error_record)
            
            # Update component health
            self._update_component_health(component, error_record)
            
            # Determine recovery strategy
            recovery_strategy = self._select_recovery_strategy(error_record)
            
            # Execute recovery
            recovery_result = await self._execute_recovery(error_record, recovery_strategy)
            
            # Update error record with recovery info
            error_record.recovery_attempted = True
            error_record.recovery_strategy = recovery_strategy.strategy if recovery_strategy else None
            error_record.recovery_successful = recovery_result.get('success', False)
            
            # Log recovery attempt
            if recovery_result.get('success'):
                log_info(f"✅ Successfully recovered from {error_record.error_type} in {component}")
            else:
                log_warning(f"❌ Failed to recover from {error_record.error_type} in {component}")
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                'error_id': error_record.error_id,
                'component': component,
                'error_type': error_record.error_type,
                'severity': error_record.severity.value,
                'recovery_attempted': error_record.recovery_attempted,
                'recovery_strategy': error_record.recovery_strategy.value if error_record.recovery_strategy else None,
                'recovery_successful': error_record.recovery_successful,
                'recovery_result': recovery_result,
                'processing_time_ms': processing_time
            }
            
        except Exception as recovery_error:
            log_error(f"Error recovery system failure: {recovery_error}")
            return {
                'error_id': 'recovery_failed',
                'component': component,
                'error_type': type(error).__name__,
                'recovery_attempted': False,
                'recovery_successful': False,
                'recovery_error': str(recovery_error)
            }
    
    def _classify_error_severity(self, error: Exception, component: str) -> ErrorSeverity:
        """Classify error severity based on error type and component"""
        
        # Critical errors
        if isinstance(error, (SystemExit, KeyboardInterrupt, MemoryError)):
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        if isinstance(error, (ConnectionError, OSError, RuntimeError)):
            return ErrorSeverity.HIGH
        
        # Medium severity errors
        if isinstance(error, (TimeoutError, ValueError, TypeError, AttributeError)):
            # Check component criticality
            critical_components = ["model_manager", "knowledge_retrieval"]
            if component in critical_components:
                return ErrorSeverity.HIGH
            return ErrorSeverity.MEDIUM
        
        # Low severity by default
        return ErrorSeverity.LOW
    
    def _record_error(self, error_record: ErrorRecord):
        """Record error in history"""
        with self._lock:
            self.error_history.append(error_record)
        
        # Record in performance monitor
        monitor = get_performance_monitor()
        monitor.record_metric(
            MetricType.ERROR_RATE,
            1.0,
            error_record.component,
            {
                "error_type": error_record.error_type,
                "severity": error_record.severity.value
            }
        )
    
    def _update_component_health(self, component: str, error_record: ErrorRecord):
        """Update component health based on error"""
        with self._lock:
            if component not in self.component_health:
                self.component_health[component] = ComponentHealth(
                    component_name=component,
                    state=ComponentState.HEALTHY,
                    last_error=None,
                    error_count=0,
                    success_count=0,
                    last_success=None,
                    health_score=1.0
                )
            
            health = self.component_health[component]
            health.last_error = error_record
            health.error_count += 1
            
            # Calculate health score
            total_operations = health.error_count + health.success_count
            if total_operations > 0:
                health.health_score = health.success_count / total_operations
            
            # Update state based on error rate and severity
            error_rate = health.error_count / max(total_operations, 1)
            
            if error_record.severity == ErrorSeverity.CRITICAL or error_rate > 0.5:
                health.state = ComponentState.FAILED
            elif error_record.severity == ErrorSeverity.HIGH or error_rate > 0.3:
                health.state = ComponentState.FAILING
            elif error_rate > 0.1:
                health.state = ComponentState.DEGRADED
            
            # Update system health score
            self._update_system_health()
    
    def _update_system_health(self):
        """Update overall system health score"""
        if not self.component_health:
            self.system_health_score = 1.0
            return
        
        # Calculate weighted average of component health
        total_score = sum(health.health_score for health in self.component_health.values())
        self.system_health_score = total_score / len(self.component_health)
        
        self.last_health_check = datetime.now()
    
    def _select_recovery_strategy(self, error_record: ErrorRecord) -> Optional[RecoveryAction]:
        """Select appropriate recovery strategy for error"""
        
        # Find matching strategies
        matching_strategies = []
        
        for strategy in self.recovery_strategies.values():
            matches = True
            
            # Check conditions
            for condition_key, condition_value in strategy.conditions.items():
                if condition_key == "error_type" and error_record.error_type != condition_value:
                    matches = False
                    break
                elif condition_key == "component" and error_record.component != condition_value:
                    matches = False
                    break
                elif condition_key == "severity" and error_record.severity != condition_value:
                    matches = False
                    break
            
            if matches:
                matching_strategies.append(strategy)
        
        if not matching_strategies:
            # Use generic retry as fallback
            return self.recovery_strategies.get("generic_retry")
        
        # Select best strategy based on severity and success rate
        best_strategy = matching_strategies[0]
        
        # Prefer specific strategies over generic ones
        for strategy in matching_strategies:
            if len(strategy.conditions) > len(best_strategy.conditions):
                best_strategy = strategy
        
        return best_strategy
    
    async def _execute_recovery(self, 
                               error_record: ErrorRecord, 
                               strategy: Optional[RecoveryAction]) -> Dict[str, Any]:
        """Execute recovery strategy"""
        
        if not strategy:
            return {'success': False, 'reason': 'No recovery strategy found'}
        
        try:
            if strategy.strategy == RecoveryStrategy.RETRY:
                return await self._execute_retry_recovery(error_record, strategy)
            elif strategy.strategy == RecoveryStrategy.FALLBACK:
                return await self._execute_fallback_recovery(error_record, strategy)
            elif strategy.strategy == RecoveryStrategy.DEGRADE:
                return await self._execute_degradation_recovery(error_record, strategy)
            elif strategy.strategy == RecoveryStrategy.RESTART:
                return await self._execute_restart_recovery(error_record, strategy)
            elif strategy.strategy == RecoveryStrategy.IGNORE:
                return {'success': True, 'action': 'ignored', 'reason': 'Error ignored per strategy'}
            else:
                return {'success': False, 'reason': f'Unknown recovery strategy: {strategy.strategy}'}
                
        except Exception as e:
            log_error(f"Recovery strategy execution failed: {e}")
            return {'success': False, 'reason': f'Recovery execution error: {str(e)}'}
    
    async def _execute_retry_recovery(self, 
                                    error_record: ErrorRecord, 
                                    strategy: RecoveryAction) -> Dict[str, Any]:
        """Execute retry recovery strategy"""
        
        component_health = self.component_health.get(error_record.component)
        if component_health and component_health.recovery_attempts >= strategy.max_attempts:
            return {'success': False, 'reason': 'Max retry attempts exceeded'}
        
        # Exponential backoff
        backoff_time = strategy.backoff_factor ** (component_health.recovery_attempts if component_health else 0)
        
        log_info(f"🔄 Retrying {error_record.component} after {backoff_time:.1f}s delay")
        await asyncio.sleep(backoff_time)
        
        # Mark as recovery attempt
        if component_health:
            component_health.recovery_attempts += 1
        
        return {
            'success': True,
            'action': 'retry_scheduled',
            'backoff_time': backoff_time,
            'attempt': component_health.recovery_attempts if component_health else 1
        }
    
    async def _execute_fallback_recovery(self, 
                                       error_record: ErrorRecord, 
                                       strategy: RecoveryAction) -> Dict[str, Any]:
        """Execute fallback recovery strategy"""
        
        try:
            result = await self.fallback_manager.execute_fallback(
                error_record.component,
                error_record.context
            )
            
            if result is not None:
                return {
                    'success': True,
                    'action': 'fallback_executed',
                    'result': 'fallback_data_available'
                }
            else:
                return {
                    'success': False,
                    'action': 'fallback_failed',
                    'reason': 'Fallback returned no result'
                }
                
        except Exception as e:
            return {
                'success': False,
                'action': 'fallback_error',
                'reason': str(e)
            }
    
    async def _execute_degradation_recovery(self, 
                                          error_record: ErrorRecord, 
                                          strategy: RecoveryAction) -> Dict[str, Any]:
        """Execute graceful degradation recovery"""
        
        # Determine features to degrade based on component and error
        features_to_degrade = []
        
        if error_record.component == "voice_synthesis":
            features_to_degrade = ["voice_generation", "audio_streaming"]
        elif error_record.component == "multilingual_processor":
            features_to_degrade = ["advanced_language_detection", "translation"]
        elif error_record.component == "business_intelligence":
            features_to_degrade = ["dynamic_pricing", "market_analysis"]
        
        if features_to_degrade:
            degraded = self.graceful_degradation.apply_degradation(features_to_degrade)
            return {
                'success': True,
                'action': 'features_degraded',
                'degraded_features': degraded
            }
        else:
            return {
                'success': False,
                'action': 'no_degradation_available',
                'reason': 'No degradable features identified'
            }
    
    async def _execute_restart_recovery(self, 
                                      error_record: ErrorRecord, 
                                      strategy: RecoveryAction) -> Dict[str, Any]:
        """Execute component restart recovery"""
        
        log_warning(f"🔄 Attempting to restart {error_record.component}")
        
        # This would trigger a restart of the specific component
        # Implementation depends on component architecture
        
        return {
            'success': True,
            'action': 'restart_scheduled',
            'component': error_record.component,
            'note': 'Restart mechanism would be component-specific'
        }
    
    def record_success(self, component: str):
        """Record a successful operation for a component"""
        with self._lock:
            if component in self.component_health:
                health = self.component_health[component]
                health.success_count += 1
                health.last_success = datetime.now()
                health.recovery_attempts = 0  # Reset recovery attempts
                
                # Update health score
                total_operations = health.error_count + health.success_count
                health.health_score = health.success_count / total_operations
                
                # Improve state if error rate is low
                error_rate = health.error_count / total_operations
                if error_rate < 0.05:
                    health.state = ComponentState.HEALTHY
                elif error_rate < 0.1:
                    health.state = ComponentState.DEGRADED
                
                self._update_system_health()
    
    def get_system_health_report(self) -> Dict[str, Any]:
        """Get comprehensive system health report"""
        
        # Component health summary
        component_summary = {}
        for name, health in self.component_health.items():
            component_summary[name] = {
                'state': health.state.value,
                'health_score': health.health_score,
                'error_count': health.error_count,
                'success_count': health.success_count,
                'last_error': health.last_error.error_type if health.last_error else None
            }
        
        # Recent error analysis
        recent_errors = [
            error for error in self.error_history
            if error.timestamp > datetime.now() - timedelta(hours=1)
        ]
        
        error_types = defaultdict(int)
        error_components = defaultdict(int)
        
        for error in recent_errors:
            error_types[error.error_type] += 1
            error_components[error.component] += 1
        
        # Recovery success rate
        recovery_attempts = len([e for e in self.error_history if e.recovery_attempted])
        recovery_successes = len([e for e in self.error_history if e.recovery_successful])
        recovery_success_rate = (recovery_successes / max(recovery_attempts, 1)) * 100
        
        return {
            'system_health_score': self.system_health_score,
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'component_health': component_summary,
            'recent_errors': {
                'total': len(recent_errors),
                'by_type': dict(error_types),
                'by_component': dict(error_components)
            },
            'recovery_stats': {
                'attempts': recovery_attempts,
                'successes': recovery_successes,
                'success_rate': recovery_success_rate
            },
            'degraded_features': list(self.graceful_degradation.degraded_features),
            'circuit_breaker_states': {
                name: cb.get_state() for name, cb in self.circuit_breakers.items()
            },
            'fallback_stats': self.fallback_manager.get_fallback_stats()
        }
    
    def get_error_analysis(self, hours: int = 24) -> Dict[str, Any]:
        """Get detailed error analysis"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_errors = [error for error in self.error_history if error.timestamp >= cutoff_time]
        
        if not recent_errors:
            return {'message': 'No errors in specified time period', 'hours': hours}
        
        # Error patterns
        error_patterns = {
            'by_severity': defaultdict(int),
            'by_component': defaultdict(int),
            'by_type': defaultdict(int),
            'by_hour': defaultdict(int)
        }
        
        for error in recent_errors:
            error_patterns['by_severity'][error.severity.value] += 1
            error_patterns['by_component'][error.component] += 1
            error_patterns['by_type'][error.error_type] += 1
            error_patterns['by_hour'][error.timestamp.hour] += 1
        
        # Most problematic components
        component_error_rates = {}
        for component, health in self.component_health.items():
            total_ops = health.error_count + health.success_count
            if total_ops > 0:
                component_error_rates[component] = (health.error_count / total_ops) * 100
        
        return {
            'time_period_hours': hours,
            'total_errors': len(recent_errors),
            'error_patterns': {k: dict(v) for k, v in error_patterns.items()},
            'component_error_rates': component_error_rates,
            'recovery_success_rate': (
                len([e for e in recent_errors if e.recovery_successful]) / 
                max(len([e for e in recent_errors if e.recovery_attempted]), 1)
            ) * 100,
            'most_common_errors': dict(sorted(error_patterns['by_type'].items(), 
                                           key=lambda x: x[1], reverse=True)[:5])
        }
    
    async def cleanup(self):
        """Clean up error recovery system"""
        log_info("🧹 Cleaning up Error Recovery System...")
        
        # Clear error history and reset states
        with self._lock:
            self.error_history.clear()
            self.recovery_history.clear()
            
            # Reset component health
            for health in self.component_health.values():
                health.recovery_attempts = 0
        
        # Restore all degraded features
        self.graceful_degradation.restore_features()
        
        log_info("✅ Error Recovery System cleanup completed")


# Global instance
_error_recovery_system = None

def get_error_recovery_system(**kwargs) -> IntelligentErrorRecoverySystem:
    """Get or create global error recovery system"""
    global _error_recovery_system
    if _error_recovery_system is None:
        _error_recovery_system = IntelligentErrorRecoverySystem(**kwargs)
    return _error_recovery_system

def error_recovery_decorator(component: str = "unknown"):
    """Decorator to add error recovery to functions"""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            recovery_system = get_error_recovery_system()
            try:
                result = await func(*args, **kwargs)
                recovery_system.record_success(component)
                return result
            except Exception as e:
                await recovery_system.handle_error(component, e, {
                    'function': func.__name__,
                    'args': str(args)[:100],
                    'kwargs': str(kwargs)[:100]
                })
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            recovery_system = get_error_recovery_system()
            try:
                result = func(*args, **kwargs)
                recovery_system.record_success(component)
                return result
            except Exception as e:
                asyncio.create_task(recovery_system.handle_error(component, e, {
                    'function': func.__name__,
                    'args': str(args)[:100],
                    'kwargs': str(kwargs)[:100]
                }))
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

if __name__ == "__main__":
    # Test the error recovery system
    async def test_error_recovery_system():
        print("🧪 Testing Intelligent Error Recovery System")
        print("=" * 60)
        
        # Create system
        recovery_system = IntelligentErrorRecoverySystem()
        
        # Register some fallbacks
        async def nlp_fallback(context):
            return {"fallback": True, "message": "Using cached NLP results"}
        
        def voice_fallback(context):
            return {"fallback": True, "message": "Using text-only response"}
        
        recovery_system.fallback_manager.register_fallback("nlp_processor", nlp_fallback)
        recovery_system.fallback_manager.register_fallback("voice_synthesis", voice_fallback)
        
        # Set feature priorities for degradation
        recovery_system.graceful_degradation.set_feature_priority("voice_generation", 3)
        recovery_system.graceful_degradation.set_feature_priority("translation", 5)
        recovery_system.graceful_degradation.set_feature_priority("business_intelligence", 8)
        
        # Add degradation rules
        recovery_system.graceful_degradation.add_degradation_rule(
            "high_memory", ["voice_generation", "translation"]
        )
        
        print("\n🧪 Testing Error Scenarios:")
        
        # Test different error types
        test_errors = [
            ("nlp_processor", ConnectionError("Failed to connect to model server")),
            ("voice_synthesis", TimeoutError("Voice generation timeout")),
            ("business_intelligence", MemoryError("Insufficient memory for analysis")),
            ("knowledge_retrieval", ValueError("Invalid query format")),
            ("model_manager", RuntimeError("Model loading failed"))
        ]
        
        for component, error in test_errors:
            print(f"\n--- Testing {component}: {type(error).__name__} ---")
            
            recovery_result = await recovery_system.handle_error(
                component=component,
                error=error,
                context={"test_scenario": True}
            )
            
            print(f"Error ID: {recovery_result['error_id']}")
            print(f"Severity: {recovery_result['severity']}")
            print(f"Recovery attempted: {recovery_result['recovery_attempted']}")
            print(f"Recovery strategy: {recovery_result.get('recovery_strategy', 'None')}")
            print(f"Recovery successful: {recovery_result['recovery_successful']}")
        
        # Test some successful operations
        print("\n✅ Recording successful operations...")
        for component in ["nlp_processor", "voice_synthesis", "knowledge_retrieval"]:
            for _ in range(5):  # Multiple successes
                recovery_system.record_success(component)
        
        # Get system health report
        print("\n🏥 System Health Report:")
        health_report = recovery_system.get_system_health_report()
        
        print(f"System Health Score: {health_report['system_health_score']:.3f}")
        print(f"Component Health:")
        for name, health in health_report['component_health'].items():
            print(f"  • {name}: {health['state']} (score: {health['health_score']:.3f})")
        
        print(f"\nRecent Errors: {health_report['recent_errors']['total']}")
        print(f"Recovery Success Rate: {health_report['recovery_stats']['success_rate']:.1f}%")
        
        if health_report['degraded_features']:
            print(f"Degraded Features: {', '.join(health_report['degraded_features'])}")
        
        # Get error analysis
        print("\n📊 Error Analysis:")
        error_analysis = recovery_system.get_error_analysis(hours=1)
        
        if 'total_errors' in error_analysis:
            print(f"Total errors: {error_analysis['total_errors']}")
            print("Most common errors:")
            for error_type, count in error_analysis['most_common_errors'].items():
                print(f"  • {error_type}: {count}")
        
        # Test circuit breaker
        print("\n⚡ Testing Circuit Breaker:")
        circuit_breaker = recovery_system.register_circuit_breaker(
            "test_service", failure_threshold=3, recovery_timeout=5
        )
        
        @circuit_breaker
        def failing_service():
            raise ConnectionError("Service unavailable")
        
        # Trigger failures to open circuit breaker
        for i in range(5):
            try:
                failing_service()
            except:
                print(f"  Attempt {i+1}: Circuit breaker state = {circuit_breaker.state}")
        
        print(f"Final circuit breaker state: {circuit_breaker.get_state()}")
        
        # Test graceful degradation
        print("\n🔻 Testing Graceful Degradation:")
        system_state = {
            'memory_usage_percent': 85,
            'error_rate': 15,
            'component_failures': 4
        }
        
        features_to_degrade = recovery_system.graceful_degradation.evaluate_degradation(system_state)
        print(f"Features to degrade: {features_to_degrade}")
        
        if features_to_degrade:
            degraded = recovery_system.graceful_degradation.apply_degradation(features_to_degrade)
            print(f"Actually degraded: {degraded}")
        
        # Cleanup
        await recovery_system.cleanup()
        print("\n🧹 Test completed")
    
    # Run test
    asyncio.run(test_error_recovery_system())