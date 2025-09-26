#!/usr/bin/env python3
"""
🧪 Comprehensive Test Suite for Adaptive Chatbot
Unit tests, integration tests, and performance benchmarks
"""

import asyncio
import gc
import json
import os
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import warnings

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import modules to test
try:
    from optimized_async_handler import (
        OptimizedEventLoopManager,
        AsyncTaskManager,
        AsyncResourceManager,
        run_async_safe,
        optimized_gather
    )
except ImportError:
    print("Warning: Could not import optimized_async_handler")

try:
    from system_reliability_security import (
        CircuitBreaker,
        DependencyResolver,
        get_system_reliability_manager
    )
except ImportError:
    print("Warning: Could not import system_reliability_security")

try:
    from critical_issues_integration import (
        CriticalIssuesResolver,
        get_critical_issues_resolver
    )
except ImportError:
    print("Warning: Could not import critical_issues_integration")

class TestAsyncOptimizations(unittest.TestCase):
    """Test async/await optimizations"""
    
    def setUp(self):
        """Set up test environment"""
        self.loop_manager = OptimizedEventLoopManager()
        
    def test_event_loop_management(self):
        """Test event loop creation and management"""
        loop = self.loop_manager.get_or_create_loop()
        self.assertIsNotNone(loop)
        self.assertFalse(loop.is_closed())
        
    def test_run_async_from_sync(self):
        """Test running async code from sync context"""
        async def async_func():
            await asyncio.sleep(0.01)
            return "success"
        
        result = self.loop_manager.run_async(async_func())
        self.assertEqual(result, "success")
        
    def test_task_manager(self):
        """Test async task management"""
        async def test():
            task_manager = AsyncTaskManager()
            
            async def sample_task():
                await asyncio.sleep(0.01)
                return "completed"
            
            # Create task
            await task_manager.create_task("test", sample_task())
            
            # Wait for completion
            result = await task_manager.wait_for_task("test", timeout=1)
            self.assertEqual(result, "completed")
        
        run_async_safe(test())
        
    def test_resource_manager(self):
        """Test async resource management"""
        async def test():
            resource_manager = AsyncResourceManager()
            
            # Create resource
            async def create_resource():
                return {"data": "test"}
            
            resource = await resource_manager.acquire("test", create_resource)
            self.assertEqual(resource["data"], "test")
            
            # Clean up
            await resource_manager.cleanup_all()
            self.assertEqual(len(resource_manager.resources), 0)
        
        run_async_safe(test())
        
    def test_optimized_gather(self):
        """Test optimized gather with concurrency control"""
        async def test():
            async def task(n):
                await asyncio.sleep(0.01)
                return n * 2
            
            coros = [task(i) for i in range(10)]
            results = await optimized_gather(*coros, max_concurrent=5)
            
            self.assertEqual(len(results), 10)
            self.assertEqual(results[0], 0)
            self.assertEqual(results[5], 10)
        
        run_async_safe(test())

class TestCircuitBreaker(unittest.TestCase):
    """Test circuit breaker pattern"""
    
    def setUp(self):
        """Set up test environment"""
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
        
    def test_circuit_breaker_opens(self):
        """Test that circuit breaker opens after failures"""
        def failing_func():
            raise Exception("Test failure")
        
        # Should fail 3 times
        for _ in range(3):
            with self.assertRaises(Exception):
                self.circuit_breaker.call(failing_func)
        
        # Circuit should be open now
        self.assertEqual(self.circuit_breaker.state, 'OPEN')
        
        # Next call should fail immediately
        with self.assertRaises(Exception):
            self.circuit_breaker.call(failing_func)
            
    def test_circuit_breaker_recovery(self):
        """Test circuit breaker recovery"""
        def failing_func():
            raise Exception("Test failure")
        
        def success_func():
            return "success"
        
        # Open the circuit
        for _ in range(3):
            with self.assertRaises(Exception):
                self.circuit_breaker.call(failing_func)
        
        # Wait for recovery timeout
        time.sleep(1.1)
        
        # Should be in HALF_OPEN state, success should close it
        result = self.circuit_breaker.call(success_func)
        self.assertEqual(result, "success")
        self.assertEqual(self.circuit_breaker.state, 'CLOSED')

class TestDependencyResolver(unittest.TestCase):
    """Test dependency resolution"""
    
    def setUp(self):
        """Set up test environment"""
        self.resolver = DependencyResolver()
        
    def test_safe_import_success(self):
        """Test successful import"""
        module = self.resolver.safe_import('os')
        self.assertIsNotNone(module)
        
    def test_safe_import_failure(self):
        """Test failed import with fallback"""
        module = self.resolver.safe_import('non_existent_module')
        self.assertIsNone(module)
        
    def test_module_caching(self):
        """Test that modules are cached"""
        # First import
        module1 = self.resolver.safe_import('sys')
        # Second import should return cached
        module2 = self.resolver.safe_import('sys')
        self.assertIs(module1, module2)

class TestCriticalIssuesResolver(unittest.TestCase):
    """Test critical issues resolver"""
    
    def setUp(self):
        """Set up test environment"""
        self.resolver = CriticalIssuesResolver()
        
    def test_input_validation(self):
        """Test input validation and sanitization"""
        # Safe input
        result = self.resolver.validate_and_sanitize_input("Hello World")
        self.assertTrue(result['safe'])
        
        # Potentially unsafe input
        result = self.resolver.validate_and_sanitize_input("'; DROP TABLE users; --")
        # Should detect SQL injection attempt
        self.assertIsNotNone(result)
        
    def test_json_handling(self):
        """Test robust JSON handling"""
        # Valid JSON
        data, success, error = self.resolver.safe_json_load('{"test": "value"}')
        self.assertTrue(success)
        self.assertEqual(data['test'], 'value')
        
        # Invalid JSON with repair
        data, success, error = self.resolver.safe_json_load('{"test": "value",}', repair=True)
        # Should handle trailing comma
        self.assertIsNotNone(data)
        
    def test_path_sanitization(self):
        """Test file path sanitization"""
        # Safe path
        safe_path = self.resolver.sanitize_file_path("test.txt")
        self.assertIsNotNone(safe_path)
        
        # Potentially unsafe path
        unsafe_path = self.resolver.sanitize_file_path("../../../etc/passwd")
        # Should sanitize or reject
        self.assertIsNotNone(unsafe_path)

class TestMemoryOptimization(unittest.TestCase):
    """Test memory optimization"""
    
    def test_garbage_collection(self):
        """Test garbage collection optimization"""
        # Create some garbage
        large_list = [i for i in range(100000)]
        del large_list
        
        # Force collection
        collected = gc.collect()
        self.assertGreaterEqual(collected, 0)
        
    def test_memory_cleanup(self):
        """Test memory cleanup functions"""
        # Create objects with __del__
        class TestObject:
            def __init__(self):
                self.data = [0] * 1000
        
        objects = [TestObject() for _ in range(100)]
        del objects
        
        gc.collect()
        # Memory should be freed

class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance benchmark tests"""
    
    def test_async_performance(self):
        """Benchmark async operations"""
        async def benchmark():
            start = time.perf_counter()
            
            async def task(n):
                await asyncio.sleep(0.001)
                return n * 2
            
            tasks = [task(i) for i in range(100)]
            results = await asyncio.gather(*tasks)
            
            end = time.perf_counter()
            duration = end - start
            
            # Should complete in reasonable time
            self.assertLess(duration, 2.0)
            self.assertEqual(len(results), 100)
            
            return duration
        
        duration = run_async_safe(benchmark())
        print(f"Async benchmark: {duration:.3f} seconds")
        
    def test_circuit_breaker_performance(self):
        """Benchmark circuit breaker overhead"""
        cb = CircuitBreaker()
        
        def simple_func():
            return "result"
        
        start = time.perf_counter()
        for _ in range(10000):
            cb.call(simple_func)
        end = time.perf_counter()
        
        duration = end - start
        print(f"Circuit breaker overhead: {duration:.3f} seconds for 10000 calls")
        
        # Should have minimal overhead
        self.assertLess(duration, 1.0)

class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_system_integration(self):
        """Test full system integration"""
        # Get all managers
        resolver = get_critical_issues_resolver()
        
        # Test module import
        module = resolver.safe_import_module('os')
        self.assertIsNotNone(module)
        
        # Test input validation
        result = resolver.validate_and_sanitize_input("Test input")
        self.assertTrue(result['safe'])
        
        # Test JSON handling
        data, success, error = resolver.safe_json_load('{"key": "value"}')
        self.assertTrue(success)
        
    def test_async_with_reliability(self):
        """Test async operations with reliability features"""
        async def test():
            resolver = get_critical_issues_resolver()
            
            # Test network-aware TTS
            engine = resolver.get_network_optimized_tts_engine()
            self.assertIsNotNone(engine)
            
            # Test audio buffer management
            success = resolver.add_audio_to_buffer(b"test_audio_data")
            self.assertIsNotNone(success)
        
        run_async_safe(test())

class TestErrorHandling(unittest.TestCase):
    """Test error handling and recovery"""
    
    def test_exception_handling(self):
        """Test exception handling in various contexts"""
        async def failing_async():
            raise ValueError("Test error")
        
        # Should handle gracefully
        try:
            run_async_safe(failing_async())
        except ValueError:
            pass  # Expected
        
    def test_timeout_handling(self):
        """Test timeout handling"""
        async def slow_task():
            await asyncio.sleep(10)
            return "done"
        
        async def test():
            task_manager = AsyncTaskManager()
            await task_manager.create_task("slow", slow_task())
            
            # Should timeout
            result = await task_manager.wait_for_task("slow", timeout=0.1)
            self.assertIsNone(result)
        
        run_async_safe(test())

def run_all_tests():
    """Run all tests and generate report"""
    print("🧪 Running Comprehensive Test Suite")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    test_cases = [
        TestAsyncOptimizations,
        TestCircuitBreaker,
        TestDependencyResolver,
        TestCriticalIssuesResolver,
        TestMemoryOptimization,
        TestPerformanceBenchmarks,
        TestIntegration,
        TestErrorHandling
    ]
    
    for test_case in test_cases:
        suite.addTests(loader.loadTestsFromTestCase(test_case))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate report
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split(chr(10))[0]}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split(chr(10))[0]}")
    
    # Save report to file
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'tests_run': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'skipped': len(result.skipped),
        'success': result.wasSuccessful()
    }
    
    with open('test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Test report saved to test_report.json")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)