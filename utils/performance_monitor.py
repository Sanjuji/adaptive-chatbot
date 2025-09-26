#!/usr/bin/env python3
"""
Performance Monitor - Real-time System Performance Tracking
Monitors memory usage, response times, cache performance, and system health
Provides alerts and optimization recommendations
"""

import asyncio
import time
import threading
import psutil
import json
import sqlite3
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import deque, defaultdict
from pathlib import Path
from enum import Enum
import weakref
import gc

from utils.logger import get_logger

logger = get_logger()

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning" 
    CRITICAL = "critical"

class MetricType(Enum):
    """Performance metric types"""
    RESPONSE_TIME = "response_time"
    MEMORY_USAGE = "memory_usage"
    CACHE_HIT_RATE = "cache_hit_rate" 
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    MODEL_LOAD_TIME = "model_load_time"
    VOICE_SYNTHESIS_TIME = "voice_synthesis_time"
    KNOWLEDGE_SEARCH_TIME = "knowledge_search_time"

@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    timestamp: datetime
    metric_type: MetricType
    value: float
    context: Dict[str, Any] = None
    component: str = "system"

@dataclass
class AlertRule:
    """Performance alert rule"""
    name: str
    metric_type: MetricType
    condition: str  # "gt", "lt", "eq"
    threshold: float
    duration_seconds: int = 0  # Alert if condition persists
    level: AlertLevel = AlertLevel.WARNING
    callback: Optional[Callable] = None

@dataclass
class SystemHealth:
    """System health snapshot"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    memory_available: float
    disk_usage: float
    response_time_avg: float
    error_rate: float
    cache_hit_rate: float
    active_components: List[str]
    is_healthy: bool

class ComponentMonitor:
    """Monitors individual system components"""
    
    def __init__(self, name: str):
        self.name = name
        self.metrics = deque(maxlen=1000)  # Store last 1000 metrics
        self.start_time = time.time()
        self.total_calls = 0
        self.total_errors = 0
        self.response_times = deque(maxlen=100)  # Last 100 response times
        
    def record_call(self, response_time: float, error: bool = False):
        """Record a component call"""
        self.total_calls += 1
        if error:
            self.total_errors += 1
        self.response_times.append(response_time)
        
        # Record metric
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            metric_type=MetricType.RESPONSE_TIME,
            value=response_time,
            component=self.name
        )
        self.metrics.append(metric)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get component statistics"""
        if not self.response_times:
            return {
                "name": self.name,
                "total_calls": self.total_calls,
                "total_errors": self.total_errors,
                "error_rate": 0.0,
                "avg_response_time": 0.0,
                "uptime_seconds": time.time() - self.start_time
            }
        
        avg_response = sum(self.response_times) / len(self.response_times)
        error_rate = (self.total_errors / max(self.total_calls, 1)) * 100
        
        return {
            "name": self.name,
            "total_calls": self.total_calls,
            "total_errors": self.total_errors,
            "error_rate": error_rate,
            "avg_response_time": avg_response,
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times),
            "uptime_seconds": time.time() - self.start_time
        }

class PerformanceMonitor:
    """Main performance monitoring system"""
    
    def __init__(self, 
                 db_path: str = "data/performance.db",
                 monitoring_interval: int = 30,
                 history_retention_hours: int = 24):
        
        self.db_path = db_path
        self.monitoring_interval = monitoring_interval
        self.history_retention_hours = history_retention_hours
        
        # Monitoring data
        self.metrics = deque(maxlen=10000)  # Store last 10k metrics
        self.components = {}  # Component name -> ComponentMonitor
        self.alert_rules = []
        self.active_alerts = {}  # Rule name -> last alert time
        
        # System tracking
        self.start_time = datetime.now()
        self.process = psutil.Process()
        
        # Threading
        self._monitoring_task = None
        self._monitoring_active = False
        self._lock = threading.RLock()
        
        # Performance baselines
        self.baselines = {
            MetricType.RESPONSE_TIME: 1000.0,  # 1 second baseline
            MetricType.MEMORY_USAGE: 4000.0,   # 4GB memory baseline
            MetricType.CACHE_HIT_RATE: 70.0,   # 70% cache hit rate
            MetricType.ERROR_RATE: 5.0,        # 5% error rate
        }
        
        # Initialize database
        self._initialize_database()
        
        # Setup default alert rules
        self._setup_default_alerts()
        
        logger.info("📊 Performance Monitor initialized")
    
    def _initialize_database(self):
        """Initialize performance metrics database"""
        try:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                # Enable optimizations
                conn.execute('PRAGMA journal_mode=WAL')
                conn.execute('PRAGMA synchronous=NORMAL')
                
                # Create metrics table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        metric_type TEXT NOT NULL,
                        value REAL NOT NULL,
                        component TEXT NOT NULL,
                        context TEXT
                    )
                ''')
                
                # Create health snapshots table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS health_snapshots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        cpu_usage REAL,
                        memory_usage REAL,
                        memory_available REAL,
                        disk_usage REAL,
                        response_time_avg REAL,
                        error_rate REAL,
                        cache_hit_rate REAL,
                        is_healthy BOOLEAN,
                        components TEXT
                    )
                ''')
                
                # Create indexes
                conn.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_metrics_type ON metrics(metric_type)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_metrics_component ON metrics(component)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_health_timestamp ON health_snapshots(timestamp)')
                
            logger.info("📈 Performance database initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize performance database: {e}")
    
    def _setup_default_alerts(self):
        """Setup default performance alert rules"""
        default_rules = [
            AlertRule(
                name="high_memory_usage",
                metric_type=MetricType.MEMORY_USAGE,
                condition="gt",
                threshold=3500.0,  # 3.5GB
                duration_seconds=60,
                level=AlertLevel.WARNING
            ),
            AlertRule(
                name="critical_memory_usage", 
                metric_type=MetricType.MEMORY_USAGE,
                condition="gt",
                threshold=4000.0,  # 4GB
                duration_seconds=30,
                level=AlertLevel.CRITICAL
            ),
            AlertRule(
                name="slow_response_time",
                metric_type=MetricType.RESPONSE_TIME,
                condition="gt", 
                threshold=2000.0,  # 2 seconds
                duration_seconds=60,
                level=AlertLevel.WARNING
            ),
            AlertRule(
                name="low_cache_hit_rate",
                metric_type=MetricType.CACHE_HIT_RATE,
                condition="lt",
                threshold=50.0,  # 50%
                duration_seconds=300,  # 5 minutes
                level=AlertLevel.INFO
            ),
            AlertRule(
                name="high_error_rate",
                metric_type=MetricType.ERROR_RATE,
                condition="gt",
                threshold=10.0,  # 10%
                duration_seconds=120,
                level=AlertLevel.CRITICAL
            )
        ]
        
        for rule in default_rules:
            self.add_alert_rule(rule)
    
    def add_alert_rule(self, rule: AlertRule):
        """Add performance alert rule"""
        with self._lock:
            self.alert_rules.append(rule)
            logger.info(f"📢 Added alert rule: {rule.name} ({rule.level.value})")
    
    def register_component(self, name: str) -> ComponentMonitor:
        """Register a system component for monitoring"""
        with self._lock:
            if name not in self.components:
                self.components[name] = ComponentMonitor(name)
                logger.info(f"📋 Registered component for monitoring: {name}")
            return self.components[name]
    
    def record_metric(self, 
                     metric_type: MetricType, 
                     value: float, 
                     component: str = "system",
                     context: Dict[str, Any] = None):
        """Record a performance metric"""
        
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            metric_type=metric_type,
            value=value,
            context=context,
            component=component
        )
        
        with self._lock:
            self.metrics.append(metric)
        
        # Store in database (async)
        asyncio.create_task(self._store_metric(metric))
        
        # Check alert rules
        self._check_alerts(metric)
    
    async def _store_metric(self, metric: PerformanceMetric):
        """Store metric in database"""
        try:
            context_json = json.dumps(metric.context) if metric.context else None
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO metrics (timestamp, metric_type, value, component, context)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    metric.timestamp.isoformat(),
                    metric.metric_type.value,
                    metric.value,
                    metric.component,
                    context_json
                ))
                
        except Exception as e:
            logger.error(f"Failed to store metric: {e}")
    
    def _check_alerts(self, metric: PerformanceMetric):
        """Check if metric triggers any alerts"""
        for rule in self.alert_rules:
            if rule.metric_type != metric.metric_type:
                continue
            
            # Check condition
            triggered = False
            if rule.condition == "gt" and metric.value > rule.threshold:
                triggered = True
            elif rule.condition == "lt" and metric.value < rule.threshold:
                triggered = True
            elif rule.condition == "eq" and abs(metric.value - rule.threshold) < 0.001:
                triggered = True
            
            if triggered:
                self._handle_alert(rule, metric)
    
    def _handle_alert(self, rule: AlertRule, metric: PerformanceMetric):
        """Handle triggered alert"""
        current_time = time.time()
        
        # Check if we should suppress repeated alerts
        if rule.name in self.active_alerts:
            last_alert_time = self.active_alerts[rule.name]
            if current_time - last_alert_time < rule.duration_seconds:
                return  # Suppress repeated alert
        
        self.active_alerts[rule.name] = current_time
        
        alert_msg = (
            f"🚨 ALERT [{rule.level.value.upper()}] {rule.name}: "
            f"{metric.metric_type.value} = {metric.value:.2f} "
            f"({rule.condition} {rule.threshold}) in {metric.component}"
        )
        
        if rule.level == AlertLevel.CRITICAL:
            logger.error(alert_msg)
        elif rule.level == AlertLevel.WARNING:
            logger.warning(alert_msg)
        else:
            logger.info(alert_msg)
        
        # Call custom callback if provided
        if rule.callback:
            try:
                rule.callback(rule, metric)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
    
    def get_system_health(self) -> SystemHealth:
        """Get current system health snapshot"""
        try:
            # Get system metrics
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            cpu_percent = self.process.cpu_percent()
            
            # Get disk usage
            disk_usage = psutil.disk_usage('.').percent
            
            # Calculate response time average
            response_times = []
            for component in self.components.values():
                if component.response_times:
                    response_times.extend(component.response_times)
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
            
            # Calculate error rate
            total_calls = sum(c.total_calls for c in self.components.values())
            total_errors = sum(c.total_errors for c in self.components.values())
            error_rate = (total_errors / max(total_calls, 1)) * 100
            
            # Calculate cache hit rate (placeholder - would integrate with actual cache systems)
            cache_hit_rate = 75.0  # Would be calculated from actual cache stats
            
            # Determine if system is healthy
            is_healthy = (
                memory_percent < 85.0 and
                cpu_percent < 90.0 and
                avg_response_time < 2000.0 and
                error_rate < 10.0
            )
            
            health = SystemHealth(
                timestamp=datetime.now(),
                cpu_usage=cpu_percent,
                memory_usage=memory_info.rss / (1024 * 1024),  # MB
                memory_available=psutil.virtual_memory().available / (1024 * 1024),  # MB
                disk_usage=disk_usage,
                response_time_avg=avg_response_time,
                error_rate=error_rate,
                cache_hit_rate=cache_hit_rate,
                active_components=list(self.components.keys()),
                is_healthy=is_healthy
            )
            
            return health
            
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return SystemHealth(
                timestamp=datetime.now(),
                cpu_usage=0.0,
                memory_usage=0.0,
                memory_available=0.0,
                disk_usage=0.0,
                response_time_avg=0.0,
                error_rate=100.0,
                cache_hit_rate=0.0,
                active_components=[],
                is_healthy=False
            )
    
    async def start_monitoring(self):
        """Start background monitoring"""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        logger.info("🔄 Starting performance monitoring...")
        
        while self._monitoring_active:
            try:
                # Take system health snapshot
                health = self.get_system_health()
                
                # Record system metrics
                self.record_metric(MetricType.MEMORY_USAGE, health.memory_usage)
                self.record_metric(MetricType.RESPONSE_TIME, health.response_time_avg)
                self.record_metric(MetricType.ERROR_RATE, health.error_rate)
                self.record_metric(MetricType.CACHE_HIT_RATE, health.cache_hit_rate)
                
                # Store health snapshot
                await self._store_health_snapshot(health)
                
                # Cleanup old data
                await self._cleanup_old_data()
                
                # Log health summary every 5 minutes
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    await self._log_health_summary(health)
                
                # Wait for next monitoring cycle
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Monitoring cycle error: {e}")
                await asyncio.sleep(10)  # Short delay before retry
    
    async def _store_health_snapshot(self, health: SystemHealth):
        """Store health snapshot in database"""
        try:
            components_json = json.dumps(health.active_components)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO health_snapshots 
                    (timestamp, cpu_usage, memory_usage, memory_available, disk_usage,
                     response_time_avg, error_rate, cache_hit_rate, is_healthy, components)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    health.timestamp.isoformat(),
                    health.cpu_usage,
                    health.memory_usage,
                    health.memory_available,
                    health.disk_usage,
                    health.response_time_avg,
                    health.error_rate,
                    health.cache_hit_rate,
                    health.is_healthy,
                    components_json
                ))
                
        except Exception as e:
            logger.error(f"Failed to store health snapshot: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old performance data"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=self.history_retention_hours)
            cutoff_str = cutoff_time.isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                # Clean old metrics
                cursor = conn.execute('DELETE FROM metrics WHERE timestamp < ?', (cutoff_str,))
                deleted_metrics = cursor.rowcount
                
                # Clean old health snapshots
                cursor = conn.execute('DELETE FROM health_snapshots WHERE timestamp < ?', (cutoff_str,))
                deleted_snapshots = cursor.rowcount
                
                if deleted_metrics > 0 or deleted_snapshots > 0:
                    logger.info(f"🧹 Cleaned {deleted_metrics} old metrics, {deleted_snapshots} old snapshots")
                    
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
    
    async def _log_health_summary(self, health: SystemHealth):
        """Log system health summary"""
        status_emoji = "✅" if health.is_healthy else "⚠️"
        
        logger.info(f'''
{status_emoji} System Health Summary:
  • Memory: {health.memory_usage:.1f}MB ({health.memory_available:.1f}MB available)
  • CPU: {health.cpu_usage:.1f}%
  • Disk: {health.disk_usage:.1f}%
  • Avg Response Time: {health.response_time_avg:.1f}ms
  • Error Rate: {health.error_rate:.1f}%
  • Cache Hit Rate: {health.cache_hit_rate:.1f}%
  • Active Components: {len(health.active_components)}
        ''')
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self._monitoring_active = False
        logger.info("🛑 Performance monitoring stopped")
    
    def get_metrics_summary(self, 
                           hours: int = 1, 
                           component: str = None) -> Dict[str, Any]:
        """Get performance metrics summary"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filter metrics
            recent_metrics = [
                m for m in self.metrics 
                if m.timestamp >= cutoff_time and (component is None or m.component == component)
            ]
            
            if not recent_metrics:
                return {"message": "No metrics found", "count": 0}
            
            # Group by metric type
            metrics_by_type = defaultdict(list)
            for metric in recent_metrics:
                metrics_by_type[metric.metric_type].append(metric.value)
            
            # Calculate summary statistics
            summary = {
                "time_range_hours": hours,
                "component": component or "all",
                "total_metrics": len(recent_metrics),
                "metric_types": {}
            }
            
            for metric_type, values in metrics_by_type.items():
                summary["metric_types"][metric_type.value] = {
                    "count": len(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "latest": values[-1] if values else 0
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {"error": str(e)}
    
    def get_component_stats(self) -> Dict[str, Any]:
        """Get statistics for all monitored components"""
        with self._lock:
            stats = {}
            for name, monitor in self.components.items():
                stats[name] = monitor.get_stats()
            return stats
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        health = self.get_system_health()
        metrics_summary = self.get_metrics_summary(hours=1)
        component_stats = self.get_component_stats()
        
        # Calculate performance scores
        memory_score = max(0, 100 - health.memory_usage / 40)  # Score out of 100
        response_score = max(0, 100 - health.response_time_avg / 20)
        error_score = max(0, 100 - health.error_rate * 10)
        cache_score = health.cache_hit_rate
        
        overall_score = (memory_score + response_score + error_score + cache_score) / 4
        
        # Determine performance grade
        if overall_score >= 90:
            grade = "A+"
        elif overall_score >= 80:
            grade = "A"
        elif overall_score >= 70:
            grade = "B"
        elif overall_score >= 60:
            grade = "C"
        else:
            grade = "D"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "uptime_hours": (datetime.now() - self.start_time).total_seconds() / 3600,
            "overall_score": overall_score,
            "performance_grade": grade,
            "health": asdict(health),
            "metrics_summary": metrics_summary,
            "component_stats": component_stats,
            "active_alerts": len(self.active_alerts),
            "recommendations": self._get_performance_recommendations(health)
        }
    
    def _get_performance_recommendations(self, health: SystemHealth) -> List[str]:
        """Get performance optimization recommendations"""
        recommendations = []
        
        if health.memory_usage > 3000:  # 3GB
            recommendations.append("Consider enabling aggressive memory cleanup - memory usage is high")
        
        if health.response_time_avg > 1000:  # 1 second
            recommendations.append("Response times are slow - check for blocking operations")
        
        if health.error_rate > 5:  # 5%
            recommendations.append("Error rate is elevated - review error logs for issues")
        
        if health.cache_hit_rate < 60:  # 60%
            recommendations.append("Cache hit rate is low - consider tuning cache settings")
        
        if health.cpu_usage > 80:  # 80%
            recommendations.append("CPU usage is high - consider optimizing compute-intensive operations")
        
        if not recommendations:
            recommendations.append("System performance is optimal - no immediate recommendations")
        
        return recommendations
    
    async def cleanup(self):
        """Clean up monitoring resources"""
        logger.info("🧹 Cleaning up Performance Monitor...")
        
        # Stop monitoring
        self.stop_monitoring()
        
        # Clear data structures
        with self._lock:
            self.metrics.clear()
            self.components.clear()
            self.alert_rules.clear()
            self.active_alerts.clear()
        
        logger.info("✅ Performance Monitor cleanup completed")


# Global monitor instance
_performance_monitor = None

def get_performance_monitor(**kwargs) -> PerformanceMonitor:
    """Get or create global performance monitor"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor(**kwargs)
    return _performance_monitor

# Decorator for monitoring function performance
def monitor_performance(component_name: str):
    """Decorator to monitor function performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            component_monitor = monitor.register_component(component_name)
            
            start_time = time.time()
            error_occurred = False
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error_occurred = True
                raise
            finally:
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                component_monitor.record_call(response_time, error_occurred)
        
        # Handle async functions
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                monitor = get_performance_monitor()
                component_monitor = monitor.register_component(component_name)
                
                start_time = time.time()
                error_occurred = False
                
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    error_occurred = True
                    raise
                finally:
                    response_time = (time.time() - start_time) * 1000
                    component_monitor.record_call(response_time, error_occurred)
            
            return async_wrapper
        else:
            return wrapper
    
    return decorator

if __name__ == "__main__":
    # Test the performance monitor
    async def test_performance_monitor():
        print("🧪 Testing Performance Monitor")
        print("=" * 50)
        
        # Create monitor
        monitor = PerformanceMonitor(
            db_path="test_performance.db",
            monitoring_interval=5,  # 5 seconds for testing
            history_retention_hours=1
        )
        
        # Register test components
        nlp_monitor = monitor.register_component("nlp_processor")
        voice_monitor = monitor.register_component("voice_synthesizer")
        knowledge_monitor = monitor.register_component("knowledge_retrieval")
        
        # Simulate some activity
        print("\n📊 Simulating component activity...")
        
        # Simulate NLP processing
        nlp_monitor.record_call(150.0)  # 150ms
        nlp_monitor.record_call(200.0)  # 200ms
        nlp_monitor.record_call(180.0)  # 180ms
        
        # Simulate voice synthesis
        voice_monitor.record_call(800.0)  # 800ms
        voice_monitor.record_call(950.0)  # 950ms
        voice_monitor.record_call(720.0)  # 720ms
        
        # Simulate knowledge retrieval
        knowledge_monitor.record_call(50.0)   # 50ms - cached
        knowledge_monitor.record_call(300.0)  # 300ms - not cached
        knowledge_monitor.record_call(45.0)   # 45ms - cached
        
        # Record some system metrics
        monitor.record_metric(MetricType.MEMORY_USAGE, 2048.0)  # 2GB
        monitor.record_metric(MetricType.CACHE_HIT_RATE, 75.0)  # 75%
        monitor.record_metric(MetricType.ERROR_RATE, 2.5)       # 2.5%
        
        # Get health snapshot
        print("\n🏥 System Health:")
        health = monitor.get_system_health()
        print(f"  • Memory Usage: {health.memory_usage:.1f}MB")
        print(f"  • CPU Usage: {health.cpu_usage:.1f}%")
        print(f"  • Response Time: {health.response_time_avg:.1f}ms")
        print(f"  • Error Rate: {health.error_rate:.1f}%")
        print(f"  • Healthy: {'✅' if health.is_healthy else '❌'}")
        
        # Get component statistics
        print("\n📈 Component Statistics:")
        stats = monitor.get_component_stats()
        for name, stat in stats.items():
            print(f"  • {name}:")
            print(f"    - Calls: {stat['total_calls']}")
            print(f"    - Avg Response: {stat['avg_response_time']:.1f}ms")
            print(f"    - Error Rate: {stat['error_rate']:.1f}%")
        
        # Get performance report
        print("\n📋 Performance Report:")
        report = monitor.get_performance_report()
        print(f"  • Overall Score: {report['overall_score']:.1f}/100")
        print(f"  • Performance Grade: {report['performance_grade']}")
        print(f"  • Active Alerts: {report['active_alerts']}")
        print(f"  • Recommendations:")
        for rec in report['recommendations']:
            print(f"    - {rec}")
        
        # Test monitoring for a short period
        print("\n🔄 Starting monitoring (will run for 15 seconds)...")
        monitoring_task = asyncio.create_task(monitor.start_monitoring())
        
        # Let it monitor for a bit
        await asyncio.sleep(15)
        
        monitor.stop_monitoring()
        monitoring_task.cancel()
        
        # Cleanup
        await monitor.cleanup()
        print("\n🧹 Test completed")
    
    # Run test
    asyncio.run(test_performance_monitor())
