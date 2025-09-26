#!/usr/bin/env python3
"""
Performance Monitoring Dashboard - O3 Level Optimization
Real-time performance monitoring and analytics dashboard
"""

import time
import threading
import logging
import json
import psutil
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import functools
import statistics
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    CUSTOM = "custom"

@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: float
    value: float
    metric_type: MetricType
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class PerformanceAlert:
    """Performance alert"""
    timestamp: float
    metric_type: MetricType
    threshold: float
    actual_value: float
    severity: str
    message: str
    resolved: bool = False

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_sent_mb: float
    network_recv_mb: float
    process_count: int
    load_average: float

class PerformanceMonitor:
    """
    O3 Level Performance Monitor
    - Real-time system monitoring
    - Custom metric tracking
    - Alert system
    - Historical data analysis
    - Performance optimization suggestions
    """
    
    def __init__(self, 
                 monitoring_interval: float = 1.0,
                 history_size: int = 3600,  # 1 hour at 1s intervals
                 alert_thresholds: Optional[Dict[str, float]] = None):
        self.monitoring_interval = monitoring_interval
        self.history_size = history_size
        
        # Data storage
        self._metrics: Dict[MetricType, deque] = {
            metric_type: deque(maxlen=history_size)
            for metric_type in MetricType
        }
        self._system_metrics: deque = deque(maxlen=history_size)
        self._custom_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=history_size))
        
        # Alert system
        self._alert_thresholds = alert_thresholds or {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_usage_percent': 90.0,
            'response_time_ms': 5000.0,
            'error_rate_percent': 10.0
        }
        self._alerts: List[PerformanceAlert] = []
        self._alert_callbacks: List[Callable] = []
        
        # Monitoring control
        self._monitoring_active = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        
        # Performance tracking
        self._function_times: Dict[str, List[float]] = defaultdict(list)
        self._error_counts: Dict[str, int] = defaultdict(int)
        self._request_counts: Dict[str, int] = defaultdict(int)
        
        # Start monitoring
        self.start_monitoring()
        
        logger.info("📊 Performance Monitor initialized")
    
    def start_monitoring(self):
        """Start performance monitoring"""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="PerformanceMonitor"
        )
        self._monitor_thread.start()
        
        logger.info("📈 Performance monitoring started")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while not self._shutdown_event.is_set():
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                self._system_metrics.append(system_metrics)
                
                # Check for alerts
                self._check_alerts(system_metrics)
                
                # Update metric histories
                self._update_metric_histories(system_metrics)
                
            except Exception as e:
                logger.error(f"❌ Performance monitoring error: {e}")
            
            # Wait for next monitoring cycle
            self._shutdown_event.wait(self.monitoring_interval)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / 1024 / 1024
            memory_available_mb = memory.available / 1024 / 1024
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / 1024 / 1024 / 1024
            
            # Network metrics
            network = psutil.net_io_counters()
            network_sent_mb = network.bytes_sent / 1024 / 1024
            network_recv_mb = network.bytes_recv / 1024 / 1024
            
            # Process metrics
            process_count = len(psutil.pids())
            
            # Load average (Unix only)
            try:
                load_average = psutil.getloadavg()[0]
            except AttributeError:
                load_average = 0.0
            
            return SystemMetrics(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                memory_available_mb=memory_available_mb,
                disk_usage_percent=disk_usage_percent,
                disk_free_gb=disk_free_gb,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                process_count=process_count,
                load_average=load_average
            )
            
        except Exception as e:
            logger.error(f"❌ Error collecting system metrics: {e}")
            return SystemMetrics(
                timestamp=time.time(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                memory_available_mb=0.0,
                disk_usage_percent=0.0,
                disk_free_gb=0.0,
                network_sent_mb=0.0,
                network_recv_mb=0.0,
                process_count=0,
                load_average=0.0
            )
    
    def _check_alerts(self, metrics: SystemMetrics):
        """Check for performance alerts"""
        current_time = time.time()
        
        # Check CPU alert
        if metrics.cpu_percent > self._alert_thresholds.get('cpu_percent', 80.0):
            self._create_alert(
                MetricType.CPU,
                self._alert_thresholds['cpu_percent'],
                metrics.cpu_percent,
                f"High CPU usage: {metrics.cpu_percent:.1f}%"
            )
        
        # Check memory alert
        if metrics.memory_percent > self._alert_thresholds.get('memory_percent', 85.0):
            self._create_alert(
                MetricType.MEMORY,
                self._alert_thresholds['memory_percent'],
                metrics.memory_percent,
                f"High memory usage: {metrics.memory_percent:.1f}%"
            )
        
        # Check disk alert
        if metrics.disk_usage_percent > self._alert_thresholds.get('disk_usage_percent', 90.0):
            self._create_alert(
                MetricType.DISK,
                self._alert_thresholds['disk_usage_percent'],
                metrics.disk_usage_percent,
                f"High disk usage: {metrics.disk_usage_percent:.1f}%"
            )
    
    def _create_alert(self, metric_type: MetricType, threshold: float, 
                     actual_value: float, message: str):
        """Create a performance alert"""
        # Check if similar alert already exists
        recent_alerts = [
            alert for alert in self._alerts
            if alert.metric_type == metric_type and 
               not alert.resolved and
               time.time() - alert.timestamp < 300  # 5 minutes
        ]
        
        if recent_alerts:
            return  # Don't spam alerts
        
        alert = PerformanceAlert(
            timestamp=time.time(),
            metric_type=metric_type,
            threshold=threshold,
            actual_value=actual_value,
            severity="HIGH" if actual_value > threshold * 1.2 else "MEDIUM",
            message=message
        )
        
        self._alerts.append(alert)
        
        # Notify callbacks
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"❌ Alert callback error: {e}")
        
        logger.warning(f"⚠️ Performance Alert: {message}")
    
    def _update_metric_histories(self, metrics: SystemMetrics):
        """Update metric histories"""
        current_time = time.time()
        
        # Add system metrics to type-specific collections
        self._metrics[MetricType.CPU].append(
            MetricPoint(current_time, metrics.cpu_percent, MetricType.CPU)
        )
        self._metrics[MetricType.MEMORY].append(
            MetricPoint(current_time, metrics.memory_percent, MetricType.MEMORY)
        )
        self._metrics[MetricType.DISK].append(
            MetricPoint(current_time, metrics.disk_usage_percent, MetricType.DISK)
        )
    
    def record_custom_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a custom metric"""
        current_time = time.time()
        self._custom_metrics[name].append(
            MetricPoint(current_time, value, MetricType.CUSTOM, tags or {})
        )
    
    def record_function_time(self, function_name: str, execution_time: float):
        """Record function execution time"""
        self._function_times[function_name].append(execution_time)
        
        # Keep only recent times
        if len(self._function_times[function_name]) > 1000:
            self._function_times[function_name] = self._function_times[function_name][-500:]
        
        # Record as custom metric
        self.record_custom_metric(f"function_time_{function_name}", execution_time)
    
    def record_error(self, error_type: str):
        """Record an error occurrence"""
        self._error_counts[error_type] += 1
        self.record_custom_metric(f"error_{error_type}", 1.0)
    
    def record_request(self, request_type: str):
        """Record a request"""
        self._request_counts[request_type] += 1
        self.record_custom_metric(f"request_{request_type}", 1.0)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        if not self._system_metrics:
            return {}
        
        latest = self._system_metrics[-1]
        
        return {
            'timestamp': latest.timestamp,
            'cpu_percent': latest.cpu_percent,
            'memory_percent': latest.memory_percent,
            'memory_used_mb': latest.memory_used_mb,
            'memory_available_mb': latest.memory_available_mb,
            'disk_usage_percent': latest.disk_usage_percent,
            'disk_free_gb': latest.disk_free_gb,
            'network_sent_mb': latest.network_sent_mb,
            'network_recv_mb': latest.network_recv_mb,
            'process_count': latest.process_count,
            'load_average': latest.load_average
        }
    
    def get_metric_history(self, metric_type: MetricType, minutes: int = 60) -> List[MetricPoint]:
        """Get metric history for specified time period"""
        cutoff_time = time.time() - (minutes * 60)
        return [
            point for point in self._metrics[metric_type]
            if point.timestamp >= cutoff_time
        ]
    
    def get_function_stats(self, function_name: str) -> Dict[str, float]:
        """Get function performance statistics"""
        times = self._function_times.get(function_name, [])
        if not times:
            return {}
        
        return {
            'count': len(times),
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'median_time': statistics.median(times),
            'p95_time': np.percentile(times, 95) if times else 0.0,
            'p99_time': np.percentile(times, 99) if times else 0.0
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        current = self.get_current_metrics()
        
        # Calculate averages over last hour
        recent_metrics = list(self._system_metrics)[-60:] if len(self._system_metrics) >= 60 else list(self._system_metrics)
        
        avg_cpu = statistics.mean([m.cpu_percent for m in recent_metrics]) if recent_metrics else 0.0
        avg_memory = statistics.mean([m.memory_percent for m in recent_metrics]) if recent_metrics else 0.0
        
        # Function performance
        function_stats = {}
        for func_name in self._function_times:
            function_stats[func_name] = self.get_function_stats(func_name)
        
        # Error summary
        error_summary = dict(self._error_counts)
        
        # Request summary
        request_summary = dict(self._request_counts)
        
        # Active alerts
        active_alerts = [alert for alert in self._alerts if not alert.resolved]
        
        return {
            'current': current,
            'averages': {
                'cpu_percent': avg_cpu,
                'memory_percent': avg_memory
            },
            'function_performance': function_stats,
            'error_summary': error_summary,
            'request_summary': request_summary,
            'active_alerts': len(active_alerts),
            'monitoring_active': self._monitoring_active
        }
    
    def register_alert_callback(self, callback: Callable):
        """Register alert callback"""
        self._alert_callbacks.append(callback)
    
    def shutdown(self):
        """Shutdown performance monitor"""
        logger.info("🛑 Shutting down Performance Monitor")
        
        self._monitoring_active = False
        self._shutdown_event.set()
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)
        
        logger.info("✅ Performance Monitor shutdown complete")

# Global instance
_performance_monitor: Optional[PerformanceMonitor] = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor

def performance_timer(func: Callable) -> Callable:
    """Decorator to time function execution"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            execution_time = time.time() - start_time
            monitor = get_performance_monitor()
            monitor.record_function_time(func.__name__, execution_time)
    
    return wrapper

def record_error(error_type: str):
    """Record an error"""
    get_performance_monitor().record_error(error_type)

def record_request(request_type: str):
    """Record a request"""
    get_performance_monitor().record_request(request_type)

# Cleanup on module unload
import atexit
atexit.register(lambda: _performance_monitor.shutdown() if _performance_monitor else None)
