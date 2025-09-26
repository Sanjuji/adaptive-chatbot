"""
Comprehensive Test Suite for Optimized System
Tests all optimization components and integrations
"""

import asyncio
import time
import threading
import sys
import os
from typing import Dict, Any, List
import traceback

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_test_header(test_name: str):
    """Print test header"""
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {test_name}")
    print(f"{'='*60}")

def print_test_result(test_name: str, success: bool, details: str = ""):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   Details: {details}")

def test_event_loop_manager():
    """Test advanced event loop manager"""
    print_test_header("Advanced Event Loop Manager")
    
    try:
        from advanced_event_loop_manager import get_loop_manager, run_async_safely
        
        # Test basic functionality
        loop_manager = get_loop_manager()
        print_test_result("Loop manager creation", loop_manager is not None)
        
        # Test async execution
        async def test_async():
            await asyncio.sleep(0.1)
            return "async_test_passed"
        
        result = run_async_safely(test_async())
        print_test_result("Async execution", result == "async_test_passed")
        
        # Test performance stats
        stats = loop_manager.get_performance_stats()
        print_test_result("Performance stats", isinstance(stats, dict) and len(stats) > 0)
        
        return True
        
    except Exception as e:
        print_test_result("Event loop manager", False, str(e))
        return False

def test_memory_manager():
    """Test advanced memory manager"""
    print_test_header("Advanced Memory Manager")
    
    try:
        from advanced_memory_manager import get_memory_manager, memory_monitor
        
        # Test memory manager creation
        mem_manager = get_memory_manager()
        print_test_result("Memory manager creation", mem_manager is not None)
        
        # Test memory monitoring
        mem_manager.start_monitoring()
        time.sleep(1)
        
        stats = mem_manager.get_memory_stats()
        print_test_result("Memory stats", isinstance(stats, dict) and 'current_mb' in stats)
        
        # Test memory monitor decorator
        @memory_monitor
        def test_function():
            return [i for i in range(1000)]
        
        result = test_function()
        print_test_result("Memory monitor decorator", len(result) == 1000)
        
        mem_manager.shutdown()
        return True
        
    except Exception as e:
        print_test_result("Memory manager", False, str(e))
        return False

def test_circuit_breaker():
    """Test advanced circuit breaker"""
    print_test_header("Advanced Circuit Breaker")
    
    try:
        from advanced_circuit_breaker import AdvancedCircuitBreaker, CircuitBreakerConfig
        
        # Test circuit breaker creation
        config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=1.0)
        breaker = AdvancedCircuitBreaker("test_breaker", config)
        print_test_result("Circuit breaker creation", breaker is not None)
        
        # Test successful call
        def success_func():
            return "success"
        
        result = breaker.call(success_func)
        print_test_result("Successful call", result == "success")
        
        # Test failing call
        def fail_func():
            raise Exception("Test failure")
        
        try:
            breaker.call(fail_func)
            print_test_result("Failing call handling", False, "Should have raised exception")
        except Exception:
            print_test_result("Failing call handling", True)
        
        # Test stats
        stats = breaker.get_stats()
        print_test_result("Circuit breaker stats", isinstance(stats, dict))
        
        return True
        
    except Exception as e:
        print_test_result("Circuit breaker", False, str(e))
        return False

def test_audio_optimizer():
    """Test advanced audio optimizer"""
    print_test_header("Advanced Audio Optimizer")
    
    try:
        from advanced_audio_optimizer import get_audio_optimizer, AudioQuality
        
        # Test audio optimizer creation
        optimizer = get_audio_optimizer()
        print_test_result("Audio optimizer creation", optimizer is not None)
        
        # Test buffer creation
        buffer = optimizer.create_audio_buffer("test_buffer", AudioQuality.HIGH)
        print_test_result("Audio buffer creation", buffer is not None)
        
        # Test monitoring
        optimizer.start_monitoring()
        time.sleep(1)
        
        stats = optimizer.get_audio_statistics()
        print_test_result("Audio statistics", isinstance(stats, dict) and 'monitoring_active' in stats)
        
        optimizer.stop_monitoring()
        optimizer.cleanup()
        return True
        
    except Exception as e:
        print_test_result("Audio optimizer", False, str(e))
        return False

def test_caching_system():
    """Test intelligent caching system"""
    print_test_header("Intelligent Caching System")
    
    try:
        from intelligent_caching_system import create_cache, CachePriority, cache_result
        
        # Test cache creation
        cache = create_cache("test_cache", max_size=100, max_memory_mb=10)
        print_test_result("Cache creation", cache is not None)
        
        # Test basic operations
        cache.set("key1", "value1", ttl=5.0, priority=CachePriority.HIGH)
        result = cache.get("key1")
        print_test_result("Cache set/get", result == "value1")
        
        # Test cache decorator
        @cache_result(ttl=10.0, priority=CachePriority.HIGH)
        def expensive_function(n):
            time.sleep(0.1)
            return n * n
        
        # First call (cache miss)
        start = time.time()
        result1 = expensive_function(5)
        time1 = time.time() - start
        
        # Second call (cache hit)
        start = time.time()
        result2 = expensive_function(5)
        time2 = time.time() - start
        
        print_test_result("Cache decorator", result1 == result2 and time2 < time1)
        
        # Test statistics
        stats = cache.get_statistics()
        print_test_result("Cache statistics", isinstance(stats, dict) and 'hit_rate' in stats)
        
        cache.cleanup()
        return True
        
    except Exception as e:
        print_test_result("Caching system", False, str(e))
        return False

def test_database_optimizer():
    """Test database optimizer"""
    print_test_header("Database Optimizer")
    
    try:
        from database_optimizer import get_database_optimizer
        
        # Test database optimizer creation
        optimizer = get_database_optimizer("test_optimized.db")
        print_test_result("Database optimizer creation", optimizer is not None)
        
        # Test table creation
        create_table = """
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            name TEXT,
            value INTEGER
        )
        """
        
        success, result, error = optimizer.execute_optimized_query(create_table)
        print_test_result("Table creation", success)
        
        # Test data insertion
        insert_data = "INSERT INTO test_table (name, value) VALUES (?, ?)"
        success, result, error = optimizer.execute_optimized_query(insert_data, ("test", 123))
        print_test_result("Data insertion", success)
        
        # Test data query
        select_data = "SELECT * FROM test_table WHERE name = ?"
        success, result, error = optimizer.execute_optimized_query(select_data, ("test",))
        print_test_result("Data query", success and len(result) > 0)
        
        # Test statistics
        stats = optimizer.get_optimization_statistics()
        print_test_result("Database statistics", isinstance(stats, dict) and 'connection_pool' in stats)
        
        optimizer.cleanup()
        return True
        
    except Exception as e:
        print_test_result("Database optimizer", False, str(e))
        return False

def test_performance_monitor():
    """Test performance monitoring dashboard"""
    print_test_header("Performance Monitoring Dashboard")
    
    try:
        from performance_monitoring_dashboard import get_performance_monitor, performance_timer
        
        # Test performance monitor creation
        monitor = get_performance_monitor()
        print_test_result("Performance monitor creation", monitor is not None)
        
        # Test monitoring
        monitor.start_monitoring()
        time.sleep(1)
        
        # Test performance timer decorator
        @performance_timer
        def test_function():
            time.sleep(0.1)
            return "test_result"
        
        result = test_function()
        print_test_result("Performance timer decorator", result == "test_result")
        
        # Test metrics
        metrics = monitor.get_current_metrics()
        print_test_result("Performance metrics", isinstance(metrics, dict) and 'cpu_percent' in metrics)
        
        monitor.shutdown()
        return True
        
    except Exception as e:
        print_test_result("Performance monitor", False, str(e))
        return False

def test_import_optimizer():
    """Test intelligent import optimizer"""
    print_test_header("Intelligent Import Optimizer")
    
    try:
        from intelligent_import_optimizer import get_import_optimizer, lazy_import
        
        # Test import optimizer creation
        optimizer = get_import_optimizer()
        print_test_result("Import optimizer creation", optimizer is not None)
        
        # Test lazy import
        lazy_math = lazy_import("math")
        math_module = lazy_math()
        result = math_module.sqrt(16)
        print_test_result("Lazy import", result == 4.0)
        
        # Test recommendations
        recommendations = optimizer.get_import_recommendations()
        print_test_result("Import recommendations", isinstance(recommendations, dict))
        
        return True
        
    except Exception as e:
        print_test_result("Import optimizer", False, str(e))
        return False

def test_comprehensive_optimization():
    """Test comprehensive optimization system"""
    print_test_header("Comprehensive Optimization System")
    
    try:
        from comprehensive_optimization_integration import get_optimization_system, run_optimization
        
        # Test optimization system creation
        opt_system = get_optimization_system()
        print_test_result("Optimization system creation", opt_system is not None)
        
        # Test optimization run
        report = run_optimization()
        print_test_result("Optimization run", report is not None and hasattr(report, 'timestamp'))
        
        # Test summary generation
        summary = opt_system.generate_optimization_summary()
        print_test_result("Optimization summary", isinstance(summary, str) and len(summary) > 0)
        
        opt_system.shutdown()
        return True
        
    except Exception as e:
        print_test_result("Comprehensive optimization", False, str(e))
        return False

def test_integration():
    """Test integration between all systems"""
    print_test_header("System Integration Test")
    
    try:
        # Test that all systems can work together
        from advanced_event_loop_manager import get_loop_manager
        from advanced_memory_manager import get_memory_manager
        from intelligent_caching_system import create_cache
        from advanced_audio_optimizer import get_audio_optimizer
        
        # Initialize all systems
        loop_manager = get_loop_manager()
        mem_manager = get_memory_manager()
        cache = create_cache("integration_test")
        audio_opt = get_audio_optimizer()
        
        print_test_result("System initialization", all([
            loop_manager is not None,
            mem_manager is not None,
            cache is not None,
            audio_opt is not None
        ]))
        
        # Test cross-system functionality
        async def integration_test():
            # Use event loop manager
            loop_manager = get_loop_manager()
            
            # Use memory manager
            mem_manager = get_memory_manager()
            
            # Use cache
            cache.set("integration_key", "integration_value")
            cached_value = cache.get("integration_key")
            
            return cached_value == "integration_value"
        
        result = loop_manager.run_async_safely(integration_test())
        print_test_result("Cross-system integration", result)
        
        # Cleanup
        mem_manager.shutdown()
        cache.cleanup()
        audio_opt.cleanup()
        
        return True
        
    except Exception as e:
        print_test_result("System integration", False, str(e))
        return False

def run_all_tests():
    """Run all optimization tests"""
    print("🚀 Starting Comprehensive Optimization System Tests")
    print("=" * 80)
    
    test_functions = [
        test_event_loop_manager,
        test_memory_manager,
        test_circuit_breaker,
        test_audio_optimizer,
        test_caching_system,
        test_database_optimizer,
        test_performance_monitor,
        test_import_optimizer,
        test_comprehensive_optimization,
        test_integration
    ]
    
    results = []
    total_tests = len(test_functions)
    passed_tests = 0
    
    for test_func in test_functions:
        try:
            success = test_func()
            results.append((test_func.__name__, success))
            if success:
                passed_tests += 1
        except Exception as e:
            print(f"❌ CRITICAL ERROR in {test_func.__name__}: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            results.append((test_func.__name__, False))
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print(f"\n📋 DETAILED RESULTS:")
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL TESTS PASSED! The optimization system is working correctly.")
    else:
        print(f"\n⚠️ Some tests failed. Please check the output above for details.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
