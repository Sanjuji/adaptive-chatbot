#!/usr/bin/env python3
"""
🛡️ Advanced System Reliability and Security Manager
Addresses critical system-level issues and vulnerabilities
"""

import asyncio
import json
import os
import re
import sys
import threading
import time
import traceback
import weakref
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
import logging
import hashlib
import secrets
import psutil
import queue
from urllib.parse import unquote

class CircuitBreakerError(Exception):
    """Circuit breaker is open"""
    pass

class SecurityViolationError(Exception):
    """Security violation detected"""
    pass

class CircuitBreaker:
    """Circuit breaker pattern implementation to prevent recursive failures"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self._lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        with self._lock:
            if self.state == 'OPEN':
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = 'HALF_OPEN'
                else:
                    raise CircuitBreakerError(f"Circuit breaker is OPEN for {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                if self.state == 'HALF_OPEN':
                    self.state = 'CLOSED'
                    self.failure_count = 0
                return result
            
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = 'OPEN'
                
                raise e

class DependencyResolver:
    """Dynamic dependency resolution with fallback mechanisms"""
    
    def __init__(self):
        self.module_cache = {}
        self.fallback_modules = {
            'speech_recognition': ['pyaudio', 'sounddevice'],
            'pyttsx3': ['win32com.client', 'espeak'],
            'edge_tts': ['gtts', 'pyttsx3'],
            'transformers': ['openai', 'anthropic'],
            'torch': ['tensorflow', 'sklearn']
        }
        self.circuit_breakers = {}
    
    def get_circuit_breaker(self, module_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for module"""
        if module_name not in self.circuit_breakers:
            self.circuit_breakers[module_name] = CircuitBreaker()
        return self.circuit_breakers[module_name]
    
    def safe_import(self, module_name: str, fallback_enabled: bool = True):
        """Safely import module with fallback options"""
        if module_name in self.module_cache:
            return self.module_cache[module_name]
        
        circuit_breaker = self.get_circuit_breaker(module_name)
        
        def _import_module():
            return __import__(module_name)
        
        try:
            module = circuit_breaker.call(_import_module)
            self.module_cache[module_name] = module
            logging.info(f"✅ Successfully imported {module_name}")
            return module
        
        except (ImportError, CircuitBreakerError) as e:
            logging.warning(f"⚠️ Failed to import {module_name}: {e}")
            
            if fallback_enabled and module_name in self.fallback_modules:
                for fallback in self.fallback_modules[module_name]:
                    try:
                        fallback_module = self.safe_import(fallback, fallback_enabled=False)
                        logging.info(f"✅ Using fallback {fallback} for {module_name}")
                        self.module_cache[module_name] = fallback_module
                        return fallback_module
                    except:
                        continue
            
            logging.error(f"❌ All import attempts failed for {module_name}")
            return None

class PriorityThreadPoolManager:
    """Priority-based thread pool to prevent thread starvation"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.high_priority_pool = ThreadPoolExecutor(max_workers=max(1, self.max_workers // 3))
        self.normal_priority_pool = ThreadPoolExecutor(max_workers=max(1, self.max_workers // 2))
        self.low_priority_pool = ThreadPoolExecutor(max_workers=max(1, self.max_workers // 6))
        self.task_queue = queue.PriorityQueue()
        self.shutdown_event = threading.Event()
        self._start_scheduler()
    
    def _start_scheduler(self):
        """Start the task scheduler thread"""
        scheduler_thread = threading.Thread(target=self._scheduler_worker, daemon=True)
        scheduler_thread.start()
    
    def _scheduler_worker(self):
        """Worker thread that schedules tasks based on priority"""
        while not self.shutdown_event.is_set():
            try:
                priority, task_id, func, args, kwargs, future = self.task_queue.get(timeout=1)
                
                if priority <= 1:  # High priority
                    pool = self.high_priority_pool
                elif priority <= 5:  # Normal priority
                    pool = self.normal_priority_pool
                else:  # Low priority
                    pool = self.low_priority_pool
                
                pool_future = pool.submit(func, *args, **kwargs)
                
                # Forward result/exception to original future
                def forward_result(pf):
                    try:
                        result = pf.result()
                        future.set_result(result)
                    except Exception as e:
                        future.set_exception(e)
                
                pool_future.add_done_callback(forward_result)
                
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"❌ Scheduler error: {e}")
    
    def submit(self, func: Callable, *args, priority: int = 5, **kwargs):
        """Submit task with priority (lower number = higher priority)"""
        future = asyncio.Future()
        task_id = secrets.token_hex(8)
        self.task_queue.put((priority, task_id, func, args, kwargs, future))
        return future
    
    def shutdown(self):
        """Shutdown all thread pools"""
        self.shutdown_event.set()
        self.high_priority_pool.shutdown(wait=True)
        self.normal_priority_pool.shutdown(wait=True)
        self.low_priority_pool.shutdown(wait=True)

class NetworkAwareTTSManager:
    """Network-aware TTS with bandwidth detection and fallback"""
    
    def __init__(self):
        self.bandwidth_threshold = 100 * 1024  # 100 KB/s minimum
        self.last_bandwidth_check = 0
        self.bandwidth_check_interval = 30  # seconds
        self.current_bandwidth = float('inf')
        self.fallback_tts = None
        self.primary_tts = None
        
    def check_bandwidth(self) -> float:
        """Check current network bandwidth"""
        now = time.time()
        if now - self.last_bandwidth_check < self.bandwidth_check_interval:
            return self.current_bandwidth
        
        try:
            import requests
            start_time = time.time()
            response = requests.get('http://httpbin.org/bytes/10240', timeout=5)  # 10KB test
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                bandwidth = len(response.content) / elapsed  # bytes per second
                self.current_bandwidth = bandwidth
                self.last_bandwidth_check = now
                return bandwidth
            else:
                self.current_bandwidth = 0
                return 0
        
        except Exception as e:
            logging.warning(f"⚠️ Bandwidth check failed: {e}")
            self.current_bandwidth = 0
            return 0
    
    def get_optimal_tts_engine(self):
        """Get optimal TTS engine based on network conditions"""
        bandwidth = self.check_bandwidth()
        
        if bandwidth > self.bandwidth_threshold:
            # Use high-quality online TTS
            return 'edge_tts'
        else:
            # Fallback to local TTS
            logging.info("🔄 Using local TTS due to low bandwidth")
            return 'pyttsx3'
    
    async def synthesize_with_fallback(self, text: str, language: str = 'en') -> bytes:
        """Synthesize speech with automatic fallback"""
        engine = self.get_optimal_tts_engine()
        
        try:
            if engine == 'edge_tts':
                return await self._edge_tts_synthesize(text, language)
            else:
                return await self._local_tts_synthesize(text, language)
        
        except Exception as e:
            logging.warning(f"⚠️ Primary TTS failed: {e}, trying fallback")
            try:
                if engine == 'edge_tts':
                    return await self._local_tts_synthesize(text, language)
                else:
                    return await self._edge_tts_synthesize(text, language)
            except Exception as fallback_error:
                logging.error(f"❌ All TTS engines failed: {fallback_error}")
                return b''  # Silent fallback
    
    async def _edge_tts_synthesize(self, text: str, language: str) -> bytes:
        """EdgeTTS synthesis"""
        # Implementation would integrate with existing EdgeTTS
        return b'edge_tts_audio_data'
    
    async def _local_tts_synthesize(self, text: str, language: str) -> bytes:
        """Local TTS synthesis"""
        # Implementation would integrate with pyttsx3
        return b'local_tts_audio_data'

class AudioBufferManager:
    """Advanced audio buffer management with overflow protection"""
    
    def __init__(self, max_buffer_size: int = 4096, overflow_threshold: float = 0.8):
        self.max_buffer_size = max_buffer_size
        self.overflow_threshold = overflow_threshold
        self.audio_queue = queue.Queue(maxsize=max_buffer_size)
        self.buffer_monitor_thread = None
        self.monitoring = False
        
    def start_monitoring(self):
        """Start buffer monitoring"""
        self.monitoring = True
        self.buffer_monitor_thread = threading.Thread(target=self._monitor_buffer, daemon=True)
        self.buffer_monitor_thread.start()
    
    def _monitor_buffer(self):
        """Monitor buffer levels and prevent overflow"""
        while self.monitoring:
            try:
                queue_size = self.audio_queue.qsize()
                utilization = queue_size / self.max_buffer_size
                
                if utilization > self.overflow_threshold:
                    logging.warning(f"⚠️ Audio buffer at {utilization*100:.1f}% capacity")
                    self._emergency_flush()
                
                time.sleep(0.1)  # Check 10 times per second
                
            except Exception as e:
                logging.error(f"❌ Buffer monitoring error: {e}")
    
    def _emergency_flush(self):
        """Emergency buffer flush to prevent overflow"""
        flushed_count = 0
        while not self.audio_queue.empty() and flushed_count < self.max_buffer_size // 4:
            try:
                self.audio_queue.get_nowait()
                flushed_count += 1
            except queue.Empty:
                break
        
        logging.info(f"🔄 Emergency flushed {flushed_count} audio buffers")
    
    def add_audio_data(self, audio_data: bytes) -> bool:
        """Add audio data to buffer with overflow protection"""
        try:
            self.audio_queue.put_nowait(audio_data)
            return True
        except queue.Full:
            logging.warning("⚠️ Audio buffer full, dropping data")
            return False
    
    def get_audio_data(self, timeout: float = 1.0) -> Optional[bytes]:
        """Get audio data from buffer"""
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def stop_monitoring(self):
        """Stop buffer monitoring"""
        self.monitoring = False
        if self.buffer_monitor_thread:
            self.buffer_monitor_thread.join(timeout=1)

class RobustJSONHandler:
    """Robust JSON handling with comprehensive error logging"""
    
    def __init__(self):
        self.validation_schemas = {}
        self.repair_strategies = {
            'trailing_comma': self._fix_trailing_comma,
            'unquoted_keys': self._fix_unquoted_keys,
            'single_quotes': self._fix_single_quotes,
        }
    
    def safe_load(self, json_str: str, schema_name: str = None, repair: bool = True) -> tuple:
        """
        Safely load JSON with detailed error reporting
        Returns: (data, success, error_message)
        """
        if not json_str or not isinstance(json_str, str):
            return None, False, "Invalid input: empty or non-string data"
        
        # Try direct parsing first
        try:
            data = json.loads(json_str)
            if schema_name and not self._validate_schema(data, schema_name):
                return data, False, f"Schema validation failed for {schema_name}"
            return data, True, None
        
        except json.JSONDecodeError as e:
            logging.warning(f"⚠️ JSON parse error: {e}")
            
            if repair:
                # Try repair strategies
                for strategy_name, strategy_func in self.repair_strategies.items():
                    try:
                        repaired_json = strategy_func(json_str)
                        data = json.loads(repaired_json)
                        logging.info(f"✅ JSON repaired using {strategy_name}")
                        return data, True, f"Repaired using {strategy_name}"
                    
                    except Exception as repair_error:
                        logging.debug(f"Repair strategy {strategy_name} failed: {repair_error}")
                        continue
            
            # Log detailed error information
            error_details = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'line_number': getattr(e, 'lineno', 'unknown'),
                'column_number': getattr(e, 'colno', 'unknown'),
                'position': getattr(e, 'pos', 'unknown'),
                'input_length': len(json_str),
                'input_preview': json_str[:200] + '...' if len(json_str) > 200 else json_str
            }
            
            logging.error(f"❌ JSON parsing failed: {json.dumps(error_details, indent=2)}")
            return None, False, f"Parse error: {e}"
        
        except Exception as e:
            logging.error(f"❌ Unexpected JSON error: {e}")
            return None, False, f"Unexpected error: {e}"
    
    def safe_dump(self, data: Any, indent: int = 2, ensure_ascii: bool = False) -> tuple:
        """
        Safely dump JSON with error handling
        Returns: (json_str, success, error_message)
        """
        try:
            json_str = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii, default=str)
            return json_str, True, None
        
        except Exception as e:
            logging.error(f"❌ JSON serialization error: {e}")
            return None, False, str(e)
    
    def _fix_trailing_comma(self, json_str: str) -> str:
        """Fix trailing commas in JSON"""
        # Remove trailing commas before closing brackets/braces
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        return json_str
    
    def _fix_unquoted_keys(self, json_str: str) -> str:
        """Fix unquoted keys in JSON"""
        # Add quotes around unquoted keys
        json_str = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
        return json_str
    
    def _fix_single_quotes(self, json_str: str) -> str:
        """Fix single quotes in JSON"""
        # Replace single quotes with double quotes (simple approach)
        json_str = json_str.replace("'", '"')
        return json_str
    
    def _validate_schema(self, data: Any, schema_name: str) -> bool:
        """Validate data against registered schema"""
        if schema_name not in self.validation_schemas:
            return True  # No schema registered, assume valid
        
        schema = self.validation_schemas[schema_name]
        # Implementation would use jsonschema library
        return True  # Placeholder

class AdvancedSecurityLayer:
    """Advanced security layer with path traversal and injection protection"""
    
    def __init__(self):
        self.path_traversal_patterns = [
            r'\.\./',
            r'\.\.\\',
            r'%2e%2e%2f',
            r'%2e%2e%5c',
            r'..%2f',
            r'..%5c',
            r'%252e%252e%252f',
            r'%252e%252e%255c'
        ]
        
        self.injection_patterns = {
            'sql': [
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b)",
                r"(\b(UNION|OR|AND)\s+\d+\s*=\s*\d+)",
                r"(--|#|/\*|\*/)",
                r"(\b(EXEC|EXECUTE)\b)",
            ],
            'command': [
                r"([;&|`$()])",
                r"(\b(rm|del|format|shutdown|reboot)\b)",
                r"(\\x[0-9a-fA-F]{2})",
                r"(%[0-9a-fA-F]{2})",
            ],
            'script': [
                r"(<script[^>]*>.*?</script>)",
                r"(javascript:|vbscript:|data:)",
                r"(on\w+\s*=)",
                r"(eval\s*\(|function\s*\()",
            ]
        }
        
        self.session_tokens = {}
        self.token_rotation_interval = 3600  # 1 hour
    
    def sanitize_path(self, path: str) -> str:
        """Sanitize file path to prevent traversal attacks"""
        if not isinstance(path, str):
            raise SecurityViolationError("Path must be a string")
        
        # Decode URL encoding
        decoded_path = unquote(path)
        
        # Check for path traversal patterns
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, decoded_path, re.IGNORECASE):
                raise SecurityViolationError(f"Path traversal attempt detected: {pattern}")
        
        # Normalize path and ensure it's within allowed boundaries
        normalized_path = os.path.normpath(decoded_path)
        
        # Convert to absolute path and check if it's within project directory
        project_root = os.path.abspath(os.path.dirname(__file__))
        abs_path = os.path.abspath(os.path.join(project_root, normalized_path))
        
        if not abs_path.startswith(project_root):
            raise SecurityViolationError("Path outside project directory not allowed")
        
        return abs_path
    
    def detect_injection(self, user_input: str, context: str = 'general') -> dict:
        """Detect various injection attempts"""
        if not isinstance(user_input, str):
            return {'safe': True, 'threats': []}
        
        threats_detected = []
        
        # Check against all injection patterns
        for injection_type, patterns in self.injection_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, user_input, re.IGNORECASE | re.MULTILINE)
                if matches:
                    threats_detected.append({
                        'type': injection_type,
                        'pattern': pattern,
                        'matches': matches,
                        'severity': self._assess_threat_severity(injection_type, pattern)
                    })
        
        is_safe = len(threats_detected) == 0
        
        if not is_safe:
            logging.warning(f"⚠️ Injection threats detected in {context}: {threats_detected}")
        
        return {
            'safe': is_safe,
            'threats': threats_detected,
            'sanitized_input': self._sanitize_input(user_input, threats_detected)
        }
    
    def _assess_threat_severity(self, injection_type: str, pattern: str) -> str:
        """Assess threat severity level"""
        high_risk_patterns = ['DROP', 'DELETE', 'rm', 'format', 'eval']
        
        if any(risk in pattern.upper() for risk in high_risk_patterns):
            return 'HIGH'
        elif injection_type in ['sql', 'command']:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _sanitize_input(self, user_input: str, threats: list) -> str:
        """Sanitize input by removing/escaping threats"""
        sanitized = user_input
        
        for threat in threats:
            for match in threat['matches']:
                if isinstance(match, tuple):
                    for m in match:
                        if m:
                            sanitized = sanitized.replace(m, '[FILTERED]')
                else:
                    sanitized = sanitized.replace(match, '[FILTERED]')
        
        return sanitized
    
    def generate_session_token(self, user_id: str) -> str:
        """Generate secure session token"""
        token = secrets.token_urlsafe(32)
        timestamp = time.time()
        
        self.session_tokens[user_id] = {
            'token': token,
            'created_at': timestamp,
            'last_used': timestamp
        }
        
        return token
    
    def validate_session_token(self, user_id: str, token: str) -> bool:
        """Validate and rotate session token if needed"""
        if user_id not in self.session_tokens:
            return False
        
        stored_token_info = self.session_tokens[user_id]
        current_time = time.time()
        
        # Check token validity
        if stored_token_info['token'] != token:
            return False
        
        # Check if token needs rotation
        if current_time - stored_token_info['created_at'] > self.token_rotation_interval:
            new_token = self.generate_session_token(user_id)
            logging.info(f"🔄 Session token rotated for user {user_id}")
        
        # Update last used time
        stored_token_info['last_used'] = current_time
        return True

class SystemReliabilityManager:
    """Main system reliability and security manager"""
    
    def __init__(self):
        self.dependency_resolver = DependencyResolver()
        self.thread_pool_manager = PriorityThreadPoolManager()
        self.network_tts_manager = NetworkAwareTTSManager()
        self.audio_buffer_manager = AudioBufferManager()
        self.json_handler = RobustJSONHandler()
        self.security_layer = AdvancedSecurityLayer()
        
        self.resource_monitors = {}
        self.cleanup_callbacks = []
        self.monitoring_active = False
        
        # Start monitoring
        self.start_system_monitoring()
        
        logging.info("🛡️ System Reliability and Security Manager initialized")
    
    def start_system_monitoring(self):
        """Start comprehensive system monitoring"""
        self.monitoring_active = True
        
        # Start audio buffer monitoring
        self.audio_buffer_manager.start_monitoring()
        
        # Start resource monitoring
        monitor_thread = threading.Thread(target=self._resource_monitor_loop, daemon=True)
        monitor_thread.start()
        
        # Register cleanup callbacks
        import atexit
        atexit.register(self.shutdown)
        
        logging.info("✅ System monitoring started")
    
    def _resource_monitor_loop(self):
        """Monitor system resources and trigger cleanup"""
        while self.monitoring_active:
            try:
                # Check memory usage
                memory_info = psutil.virtual_memory()
                if memory_info.percent > 85:
                    logging.warning(f"⚠️ High memory usage: {memory_info.percent}%")
                    self._trigger_memory_cleanup()
                
                # Check file handles
                process = psutil.Process()
                if hasattr(process, 'num_fds'):  # Unix
                    fd_count = process.num_fds()
                elif hasattr(process, 'num_handles'):  # Windows
                    fd_count = process.num_handles()
                else:
                    fd_count = 0
                
                if fd_count > 500:  # Threshold for file handles
                    logging.warning(f"⚠️ High file handle usage: {fd_count}")
                    self._trigger_file_handle_cleanup()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logging.error(f"❌ Resource monitoring error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _trigger_memory_cleanup(self):
        """Trigger memory cleanup routines"""
        logging.info("🧹 Triggering memory cleanup")
        
        # Call registered cleanup callbacks
        for callback in self.cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                logging.error(f"❌ Cleanup callback error: {e}")
        
        # Force garbage collection
        import gc
        gc.collect()
    
    def _trigger_file_handle_cleanup(self):
        """Trigger file handle cleanup"""
        logging.info("🧹 Triggering file handle cleanup")
        
        # Close unused file handles (implementation specific)
        # This would involve tracking open files and closing unused ones
        
    def register_cleanup_callback(self, callback: Callable):
        """Register cleanup callback for resource management"""
        self.cleanup_callbacks.append(callback)
    
    def shutdown(self):
        """Shutdown all systems gracefully"""
        logging.info("🛑 Shutting down System Reliability Manager")
        
        self.monitoring_active = False
        self.thread_pool_manager.shutdown()
        self.audio_buffer_manager.stop_monitoring()
        
        # Trigger final cleanup
        self._trigger_memory_cleanup()
        
        logging.info("✅ System Reliability Manager shut down complete")

# Global instance
_system_reliability_manager = None

def get_system_reliability_manager() -> SystemReliabilityManager:
    """Get global system reliability manager instance"""
    global _system_reliability_manager
    if _system_reliability_manager is None:
        _system_reliability_manager = SystemReliabilityManager()
    return _system_reliability_manager

# Decorator for adding reliability features to functions
def with_reliability(priority: int = 5, max_retries: int = 3, circuit_breaker: bool = True):
    """Decorator to add reliability features to functions"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            manager = get_system_reliability_manager()
            
            if circuit_breaker:
                circuit = manager.dependency_resolver.get_circuit_breaker(func.__name__)
                return await manager.thread_pool_manager.submit(
                    circuit.call, func, *args, priority=priority, **kwargs
                )
            else:
                return await manager.thread_pool_manager.submit(
                    func, *args, priority=priority, **kwargs
                )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            manager = get_system_reliability_manager()
            
            if circuit_breaker:
                circuit = manager.dependency_resolver.get_circuit_breaker(func.__name__)
                return circuit.call(func, *args, **kwargs)
            else:
                return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

if __name__ == "__main__":
    # Test the system
    manager = get_system_reliability_manager()
    
    # Test JSON handling
    test_json = '{"test": "value", "number": 42,}'  # Trailing comma
    data, success, error = manager.json_handler.safe_load(test_json, repair=True)
    print(f"JSON test: success={success}, data={data}")
    
    # Test security
    malicious_path = "../../../etc/passwd"
    try:
        safe_path = manager.security_layer.sanitize_path(malicious_path)
        print(f"Path sanitization failed: {safe_path}")
    except SecurityViolationError as e:
        print(f"✅ Security working: {e}")
    
    # Test injection detection
    malicious_input = "'; DROP TABLE users; --"
    result = manager.security_layer.detect_injection(malicious_input)
    print(f"Injection detection: {result}")
    
    print("🛡️ System reliability tests completed")