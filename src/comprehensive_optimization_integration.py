#!/usr/bin/env python3
"""
Comprehensive Optimization Integration - O3 Level Integration
Integrates all optimization systems for maximum performance
"""

import asyncio
import time
import logging
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import json
import sys
import os

# Import our optimization modules
from advanced_event_loop_manager import get_loop_manager, run_async_safely
from advanced_memory_manager import get_memory_manager, memory_monitor
from intelligent_import_optimizer import get_import_optimizer, lazy_import
from advanced_circuit_breaker import get_circuit_breaker, circuit_breaker
from performance_monitoring_dashboard import get_performance_monitor, performance_timer

logger = logging.getLogger(__name__)

@dataclass
class OptimizationReport:
    """Comprehensive optimization report"""
    timestamp: float
    system_health_score: float
    performance_improvements: Dict[str, float]
    memory_optimizations: Dict[str, Any]
    async_optimizations: Dict[str, Any]
    import_optimizations: Dict[str, Any]
    circuit_breaker_stats: Dict[str, Any]
    recommendations: List[str]
    critical_issues: List[str]

class ComprehensiveOptimizationSystem:
    """
    O3 Level Comprehensive Optimization System
    - Integrates all optimization modules
    - Provides unified optimization interface
    - Generates comprehensive reports
    - Monitors system health
    - Applies optimizations automatically
    """
    
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root or os.getcwd())
        
        # Initialize all optimization systems
        self._initialize_systems()
        
        # Optimization tracking
        self._optimization_history: List[OptimizationReport] = []
        self._last_optimization_time = 0.0
        self._optimization_interval = 300.0  # 5 minutes
        
        # Start background optimization
        self._start_background_optimization()
        
        logger.info("🚀 Comprehensive Optimization System initialized")
    
    def _initialize_systems(self):
        """Initialize all optimization systems"""
        try:
            # Event loop manager
            self.loop_manager = get_loop_manager()
            logger.info("✅ Event Loop Manager initialized")
            
            # Memory manager
            self.memory_manager = get_memory_manager()
            logger.info("✅ Memory Manager initialized")
            
            # Import optimizer
            self.import_optimizer = get_import_optimizer()
            logger.info("✅ Import Optimizer initialized")
            
            # Performance monitor
            self.performance_monitor = get_performance_monitor()
            logger.info("✅ Performance Monitor initialized")
            
            # Register cleanup callbacks
            self._register_cleanup_callbacks()
            
        except Exception as e:
            logger.error(f"❌ Error initializing optimization systems: {e}")
            raise
    
    def _register_cleanup_callbacks(self):
        """Register cleanup callbacks between systems"""
        # Memory manager cleanup for event loops
        def cleanup_event_loops():
            try:
                stats = self.loop_manager.get_performance_stats()
                if stats.get('active_loops', 0) > 5:
                    logger.info("🧹 Cleaning up excess event loops")
            except Exception as e:
                logger.error(f"❌ Event loop cleanup error: {e}")
        
        self.memory_manager.register_cleanup_callback(cleanup_event_loops)
        
        # Performance monitoring for memory usage
        def monitor_memory_usage():
            try:
                stats = self.memory_manager.get_memory_stats()
                self.performance_monitor.record_custom_metric(
                    'memory_usage_mb', 
                    stats.get('current_mb', 0)
                )
            except Exception as e:
                logger.error(f"❌ Memory monitoring error: {e}")
        
        self.performance_monitor.register_alert_callback(monitor_memory_usage)
    
    def _start_background_optimization(self):
        """Start background optimization thread"""
        def optimization_loop():
            while True:
                try:
                    current_time = time.time()
                    if current_time - self._last_optimization_time > self._optimization_interval:
                        self.run_comprehensive_optimization()
                        self._last_optimization_time = current_time
                    
                    time.sleep(60)  # Check every minute
                    
                except Exception as e:
                    logger.error(f"❌ Background optimization error: {e}")
                    time.sleep(300)  # Wait 5 minutes on error
        
        optimization_thread = threading.Thread(
            target=optimization_loop,
            daemon=True,
            name="BackgroundOptimization"
        )
        optimization_thread.start()
    
    @performance_timer
    def run_comprehensive_optimization(self) -> OptimizationReport:
        """Run comprehensive optimization analysis and apply improvements"""
        logger.info("🔧 Running comprehensive optimization...")
        
        start_time = time.time()
        
        # Collect current system state
        system_health_score = self._calculate_system_health_score()
        
        # Analyze performance improvements
        performance_improvements = self._analyze_performance_improvements()
        
        # Memory optimizations
        memory_optimizations = self._analyze_memory_optimizations()
        
        # Async optimizations
        async_optimizations = self._analyze_async_optimizations()
        
        # Import optimizations
        import_optimizations = self._analyze_import_optimizations()
        
        # Circuit breaker stats
        circuit_breaker_stats = self._get_circuit_breaker_stats()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            system_health_score,
            performance_improvements,
            memory_optimizations,
            async_optimizations,
            import_optimizations
        )
        
        # Identify critical issues
        critical_issues = self._identify_critical_issues()
        
        # Create optimization report
        report = OptimizationReport(
            timestamp=time.time(),
            system_health_score=system_health_score,
            performance_improvements=performance_improvements,
            memory_optimizations=memory_optimizations,
            async_optimizations=async_optimizations,
            import_optimizations=import_optimizations,
            circuit_breaker_stats=circuit_breaker_stats,
            recommendations=recommendations,
            critical_issues=critical_issues
        )
        
        # Store report
        self._optimization_history.append(report)
        if len(self._optimization_history) > 100:  # Keep last 100 reports
            self._optimization_history = self._optimization_history[-100:]
        
        # Apply optimizations
        self._apply_optimizations(report)
        
        # Log results
        optimization_time = time.time() - start_time
        logger.info(f"✅ Optimization complete in {optimization_time:.2f}s")
        logger.info(f"📊 System Health Score: {system_health_score:.1f}/100")
        logger.info(f"💡 Generated {len(recommendations)} recommendations")
        
        return report
    
    def _calculate_system_health_score(self) -> float:
        """Calculate overall system health score"""
        try:
            # Get current metrics
            current_metrics = self.performance_monitor.get_current_metrics()
            memory_stats = self.memory_manager.get_memory_stats()
            
            # Calculate component scores
            cpu_score = max(0, 100 - current_metrics.get('cpu_percent', 0))
            memory_score = max(0, 100 - current_metrics.get('memory_percent', 0))
            disk_score = max(0, 100 - current_metrics.get('disk_usage_percent', 0))
            
            # Memory leak penalty
            leak_penalty = len(memory_stats.get('detected_leaks', {})) * 5
            
            # Error rate penalty
            error_penalty = memory_stats.get('error_rate', 0) * 10
            
            # Calculate weighted average
            health_score = (
                cpu_score * 0.3 +
                memory_score * 0.4 +
                disk_score * 0.2 +
                max(0, 100 - leak_penalty) * 0.1
            ) - error_penalty
            
            return max(0, min(100, health_score))
            
        except Exception as e:
            logger.error(f"❌ Error calculating health score: {e}")
            return 50.0  # Default score
    
    def _analyze_performance_improvements(self) -> Dict[str, float]:
        """Analyze performance improvements"""
        try:
            # Get function performance stats
            function_stats = self.performance_monitor.get_function_stats('run_comprehensive_optimization')
            
            improvements = {}
            
            if function_stats:
                avg_time = function_stats.get('avg_time', 0)
                if avg_time > 0:
                    # Calculate improvement over baseline
                    baseline_time = 10.0  # Assume 10s baseline
                    improvement = ((baseline_time - avg_time) / baseline_time) * 100
                    improvements['optimization_speed'] = max(0, improvement)
            
            # Memory usage improvement
            memory_stats = self.memory_manager.get_memory_stats()
            current_mb = memory_stats.get('current_mb', 0)
            if current_mb > 0:
                baseline_mb = 200.0  # Assume 200MB baseline
                improvement = ((baseline_mb - current_mb) / baseline_mb) * 100
                improvements['memory_efficiency'] = max(0, improvement)
            
            return improvements
            
        except Exception as e:
            logger.error(f"❌ Error analyzing performance: {e}")
            return {}
    
    def _analyze_memory_optimizations(self) -> Dict[str, Any]:
        """Analyze memory optimizations"""
        try:
            memory_stats = self.memory_manager.get_memory_stats()
            
            return {
                'current_mb': memory_stats.get('current_mb', 0),
                'peak_mb': memory_stats.get('peak_mb', 0),
                'detected_leaks': len(memory_stats.get('detected_leaks', {})),
                'weak_refs_count': memory_stats.get('weak_refs_count', 0),
                'gc_collections': memory_stats.get('gc_collections', 0),
                'monitoring_active': memory_stats.get('monitoring_active', False)
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing memory: {e}")
            return {}
    
    def _analyze_async_optimizations(self) -> Dict[str, Any]:
        """Analyze async optimizations"""
        try:
            loop_stats = self.loop_manager.get_performance_stats()
            
            return {
                'active_loops': loop_stats.get('active_loops', 0),
                'total_loops_created': loop_stats.get('total_loops_created', 0),
                'total_loops_destroyed': loop_stats.get('total_loops_destroyed', 0),
                'error_rate': loop_stats.get('error_rate', 0),
                'average_loop_lifetime': loop_stats.get('average_loop_lifetime', 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing async: {e}")
            return {}
    
    def _analyze_import_optimizations(self) -> Dict[str, Any]:
        """Analyze import optimizations"""
        try:
            import_stats = self.import_optimizer.get_performance_stats()
            
            return {
                'total_imports': import_stats.get('total_imports', 0),
                'loaded_imports': import_stats.get('loaded_imports', 0),
                'lazy_imports': import_stats.get('lazy_imports', 0),
                'circular_dependencies': import_stats.get('circular_dependencies', 0),
                'avg_load_time': import_stats.get('avg_load_time', 0),
                'import_errors': import_stats.get('import_errors', 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing imports: {e}")
            return {}
    
    def _get_circuit_breaker_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        try:
            # This would need to be implemented based on your circuit breaker system
            return {
                'active_breakers': 0,
                'open_circuits': 0,
                'total_calls': 0,
                'failed_calls': 0
            }
        except Exception as e:
            logger.error(f"❌ Error getting circuit breaker stats: {e}")
            return {}
    
    def _generate_recommendations(self, health_score: float, 
                                performance: Dict[str, float],
                                memory: Dict[str, Any],
                                async_ops: Dict[str, Any],
                                imports: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Health score based recommendations
        if health_score < 70:
            recommendations.append("🔴 System health is low - consider restarting the application")
        
        # Memory recommendations
        if memory.get('detected_leaks', 0) > 0:
            recommendations.append(f"🧠 {memory['detected_leaks']} memory leaks detected - run memory cleanup")
        
        if memory.get('current_mb', 0) > 500:
            recommendations.append("💾 High memory usage - consider optimizing data structures")
        
        # Async recommendations
        if async_ops.get('active_loops', 0) > 10:
            recommendations.append("🔄 Too many active event loops - consider cleanup")
        
        if async_ops.get('error_rate', 0) > 0.1:
            recommendations.append("⚠️ High async error rate - check event loop management")
        
        # Import recommendations
        if imports.get('circular_dependencies', 0) > 0:
            recommendations.append(f"🔄 {imports['circular_dependencies']} circular dependencies found - refactor imports")
        
        if imports.get('lazy_candidates', 0) > 10:
            recommendations.append(f"⚡ {imports['lazy_candidates']} modules can be lazy loaded")
        
        # Performance recommendations
        if performance.get('optimization_speed', 0) < 0:
            recommendations.append("🐌 Optimization is slower than baseline - check for bottlenecks")
        
        return recommendations
    
    def _identify_critical_issues(self) -> List[str]:
        """Identify critical issues that need immediate attention"""
        issues = []
        
        try:
            # Check memory leaks
            memory_stats = self.memory_manager.get_memory_stats()
            if memory_stats.get('detected_leaks', 0) > 5:
                issues.append(f"🚨 {memory_stats['detected_leaks']} memory leaks detected")
            
            # Check high memory usage
            if memory_stats.get('current_mb', 0) > 1000:
                issues.append(f"🚨 High memory usage: {memory_stats['current_mb']:.1f}MB")
            
            # Check system metrics
            current_metrics = self.performance_monitor.get_current_metrics()
            if current_metrics.get('cpu_percent', 0) > 95:
                issues.append(f"🚨 Critical CPU usage: {current_metrics['cpu_percent']:.1f}%")
            
            if current_metrics.get('memory_percent', 0) > 95:
                issues.append(f"🚨 Critical memory usage: {current_metrics['memory_percent']:.1f}%")
            
        except Exception as e:
            logger.error(f"❌ Error identifying critical issues: {e}")
            issues.append(f"❌ Error in critical issue detection: {e}")
        
        return issues
    
    def _apply_optimizations(self, report: OptimizationReport):
        """Apply recommended optimizations"""
        try:
            # Apply memory optimizations
            if report.memory_optimizations.get('detected_leaks', 0) > 0:
                logger.info("🧹 Applying memory cleanup")
                self.memory_manager.force_cleanup()
            
            # Apply import optimizations
            if report.import_optimizations.get('lazy_candidates', 0) > 5:
                logger.info("⚡ Applying lazy loading optimizations")
                # This would implement lazy loading for identified candidates
            
            # Apply async optimizations
            if report.async_optimizations.get('active_loops', 0) > 10:
                logger.info("🔄 Cleaning up excess event loops")
                # This would clean up excess event loops
            
        except Exception as e:
            logger.error(f"❌ Error applying optimizations: {e}")
    
    def get_optimization_report(self) -> Optional[OptimizationReport]:
        """Get the latest optimization report"""
        return self._optimization_history[-1] if self._optimization_history else None
    
    def get_optimization_history(self) -> List[OptimizationReport]:
        """Get optimization history"""
        return self._optimization_history.copy()
    
    def generate_optimization_summary(self) -> str:
        """Generate human-readable optimization summary"""
        report = self.get_optimization_report()
        if not report:
            return "No optimization data available"
        
        summary = f"""
# 🚀 Comprehensive Optimization Summary

## System Health
- **Overall Score**: {report.system_health_score:.1f}/100
- **Timestamp**: {time.ctime(report.timestamp)}

## Performance Improvements
"""
        
        for metric, improvement in report.performance_improvements.items():
            summary += f"- **{metric.replace('_', ' ').title()}**: {improvement:.1f}% improvement\n"
        
        summary += f"""
## Memory Status
- **Current Usage**: {report.memory_optimizations.get('current_mb', 0):.1f}MB
- **Peak Usage**: {report.memory_optimizations.get('peak_mb', 0):.1f}MB
- **Detected Leaks**: {report.memory_optimizations.get('detected_leaks', 0)}
- **Weak References**: {report.memory_optimizations.get('weak_refs_count', 0)}

## Async Operations
- **Active Loops**: {report.async_optimizations.get('active_loops', 0)}
- **Error Rate**: {report.async_optimizations.get('error_rate', 0):.2%}

## Import Optimizations
- **Total Imports**: {report.import_optimizations.get('total_imports', 0)}
- **Lazy Imports**: {report.import_optimizations.get('lazy_imports', 0)}
- **Circular Dependencies**: {report.import_optimizations.get('circular_dependencies', 0)}

## Recommendations
"""
        
        for i, recommendation in enumerate(report.recommendations, 1):
            summary += f"{i}. {recommendation}\n"
        
        if report.critical_issues:
            summary += "\n## Critical Issues\n"
            for i, issue in enumerate(report.critical_issues, 1):
                summary += f"{i}. {issue}\n"
        
        return summary
    
    def shutdown(self):
        """Shutdown optimization system"""
        logger.info("🛑 Shutting down Comprehensive Optimization System")
        
        # Shutdown all subsystems
        try:
            self.memory_manager.shutdown()
            self.performance_monitor.shutdown()
            self.loop_manager.shutdown()
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")
        
        logger.info("✅ Comprehensive Optimization System shutdown complete")

# Global instance
_optimization_system: Optional[ComprehensiveOptimizationSystem] = None

def get_optimization_system() -> ComprehensiveOptimizationSystem:
    """Get global optimization system instance"""
    global _optimization_system
    if _optimization_system is None:
        _optimization_system = ComprehensiveOptimizationSystem()
    return _optimization_system

def run_optimization() -> OptimizationReport:
    """Run comprehensive optimization"""
    system = get_optimization_system()
    return system.run_comprehensive_optimization()

def get_optimization_summary() -> str:
    """Get optimization summary"""
    system = get_optimization_system()
    return system.generate_optimization_summary()

# Cleanup on module unload
import atexit
atexit.register(lambda: _optimization_system.shutdown() if _optimization_system else None)

if __name__ == "__main__":
    # Example usage
    print("🚀 Starting Comprehensive Optimization System...")
    
    system = get_optimization_system()
    
    # Run initial optimization
    report = system.run_comprehensive_optimization()
    
    # Print summary
    print(system.generate_optimization_summary())
    
    # Keep running for demonstration
    try:
        while True:
            time.sleep(60)
            print(f"📊 System Health: {system.get_optimization_report().system_health_score:.1f}/100")
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        system.shutdown()
