"""
Intelligent Caching System with TTL and Memory Limits
Advanced caching with automatic optimization and cleanup
"""

import asyncio
import hashlib
import json
import pickle
import threading
import time
import weakref
from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Union, Tuple
import gc
import psutil

class CacheStrategy(Enum):
    """Caching strategies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # Adaptive based on usage patterns

class CachePriority(Enum):
    """Cache priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    DISPOSABLE = 5

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    ttl: Optional[float] = None
    priority: CachePriority = CachePriority.MEDIUM
    size_bytes: int = 0
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    def update_access(self):
        """Update access information"""
        self.last_accessed = time.time()
        self.access_count += 1
    
    def get_age(self) -> float:
        """Get age of entry in seconds"""
        return time.time() - self.created_at
    
    def get_idle_time(self) -> float:
        """Get idle time in seconds"""
        return time.time() - self.last_accessed

@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    timestamp: float
    total_entries: int
    total_size_bytes: int
    hit_count: int
    miss_count: int
    eviction_count: int
    hit_rate: float
    memory_usage_mb: float
    average_access_time: float
    oldest_entry_age: float
    newest_entry_age: float

class IntelligentCache:
    """Intelligent caching system with multiple strategies"""
    
    def __init__(self, 
                 max_size: int = 1000,
                 max_memory_mb: int = 100,
                 default_ttl: Optional[float] = None,
                 strategy: CacheStrategy = CacheStrategy.ADAPTIVE):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.default_ttl = default_ttl
        self.strategy = strategy
        
        # Storage
        self._entries: OrderedDict[str, CacheEntry] = OrderedDict()
        self._access_times: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = {}
        
        # Metrics
        self._hit_count = 0
        self._miss_count = 0
        self._eviction_count = 0
        self._total_access_time = 0.0
        self._access_count = 0
        
        # Threading
        self._lock = threading.RLock()
        self._cleanup_thread: Optional[threading.Thread] = None
        self._monitoring = False
        
        # Callbacks
        self._eviction_callbacks: List[Callable] = []
        self._cleanup_callbacks: List[Callable] = []
        
        # Start background cleanup
        self._start_cleanup_thread()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        start_time = time.perf_counter()
        
        with self._lock:
            try:
                if key in self._entries:
                    entry = self._entries[key]
                    
                    # Check if expired
                    if entry.is_expired():
                        self._remove_entry(key)
                        self._miss_count += 1
                        return default
                    
                    # Update access information
                    entry.update_access()
                    self._access_times[key] = time.time()
                    self._access_counts[key] = self._access_counts.get(key, 0) + 1
                    
                    # Move to end (LRU behavior)
                    self._entries.move_to_end(key)
                    
                    self._hit_count += 1
                    access_time = time.perf_counter() - start_time
                    self._total_access_time += access_time
                    self._access_count += 1
                    
                    return entry.value
                else:
                    self._miss_count += 1
                    return default
                    
            except Exception as e:
                print(f"⚠️ Cache get error for key '{key}': {e}")
                self._miss_count += 1
                return default
    
    def set(self, key: str, value: Any, 
            ttl: Optional[float] = None,
            priority: CachePriority = CachePriority.MEDIUM,
            tags: List[str] = None,
            dependencies: List[str] = None) -> bool:
        """Set value in cache"""
        try:
            with self._lock:
                # Calculate size
                size_bytes = self._calculate_size(value)
                
                # Check memory limits
                if size_bytes > self.max_memory_bytes:
                    print(f"⚠️ Value too large for cache: {size_bytes} bytes")
                    return False
                
                # Create entry
                entry = CacheEntry(
                    key=key,
                    value=value,
                    created_at=time.time(),
                    last_accessed=time.time(),
                    ttl=ttl or self.default_ttl,
                    priority=priority,
                    size_bytes=size_bytes,
                    tags=tags or [],
                    dependencies=dependencies or []
                )
                
                # Remove existing entry if present
                if key in self._entries:
                    self._remove_entry(key)
                
                # Add new entry
                self._entries[key] = entry
                self._access_times[key] = time.time()
                self._access_counts[key] = 0
                
                # Check if we need to evict
                self._check_eviction()
                
                return True
                
        except Exception as e:
            print(f"⚠️ Cache set error for key '{key}': {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete entry from cache"""
        with self._lock:
            if key in self._entries:
                self._remove_entry(key)
                return True
            return False
    
    def clear(self):
        """Clear all entries"""
        with self._lock:
            self._entries.clear()
            self._access_times.clear()
            self._access_counts.clear()
            self._hit_count = 0
            self._miss_count = 0
            self._eviction_count = 0
            self._total_access_time = 0.0
            self._access_count = 0
    
    def _remove_entry(self, key: str):
        """Remove entry and update metrics"""
        if key in self._entries:
            entry = self._entries.pop(key)
            self._access_times.pop(key, None)
            self._access_counts.pop(key, None)
            self._eviction_count += 1
            
            # Run eviction callbacks
            for callback in self._eviction_callbacks:
                try:
                    callback(key, entry)
                except Exception as e:
                    logger.warning(f"Eviction callback error: {e}")
    
    def _check_eviction(self):
        """Check if eviction is needed and perform it"""
        # Check size limit
        while len(self._entries) > self.max_size:
            self._evict_entry()
        
        # Check memory limit
        while self._get_total_memory_usage() > self.max_memory_bytes:
            self._evict_entry()
    
    def _evict_entry(self):
        """Evict an entry based on strategy"""
        if not self._entries:
            return
        
        if self.strategy == CacheStrategy.LRU:
            # Remove least recently used
            key_to_remove = next(iter(self._entries))
        elif self.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            key_to_remove = min(self._access_counts.keys(), 
                              key=lambda k: self._access_counts.get(k, 0))
        elif self.strategy == CacheStrategy.TTL:
            # Remove oldest entry
            key_to_remove = min(self._entries.keys(),
                              key=lambda k: self._entries[k].created_at)
        else:  # ADAPTIVE
            # Adaptive strategy based on multiple factors
            key_to_remove = self._select_adaptive_eviction()
        
        self._remove_entry(key_to_remove)
    
    def _select_adaptive_eviction(self) -> str:
        """Select entry for eviction using adaptive strategy"""
        current_time = time.time()
        
        # Score each entry based on multiple factors
        scores = {}
        for key, entry in self._entries.items():
            score = 0
            
            # Age factor (older = higher score)
            age = entry.get_age()
            score += age * 0.1
            
            # Idle time factor (more idle = higher score)
            idle_time = entry.get_idle_time()
            score += idle_time * 0.2
            
            # Access count factor (fewer accesses = higher score)
            access_count = self._access_counts.get(key, 0)
            score += (100 - access_count) * 0.1
            
            # Priority factor (lower priority = higher score)
            priority_scores = {
                CachePriority.CRITICAL: 0,
                CachePriority.HIGH: 1,
                CachePriority.MEDIUM: 2,
                CachePriority.LOW: 3,
                CachePriority.DISPOSABLE: 4
            }
            score += priority_scores.get(entry.priority, 2) * 0.3
            
            # Size factor (larger = higher score)
            score += entry.size_bytes / 1024 * 0.1
            
            scores[key] = score
        
        # Return key with highest score (most evictable)
        return max(scores.keys(), key=lambda k: scores[k])
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate size of value in bytes"""
        try:
            if isinstance(value, (str, bytes)):
                return len(value)
            elif isinstance(value, (int, float, bool)):
                return 8
            else:
                # Try to serialize and measure
                serialized = pickle.dumps(value)
                return len(serialized)            except (TypeError, ValueError, AttributeError):
                return 1024  # Default estimate
    
    def _get_total_memory_usage(self) -> int:
        """Get total memory usage of cache"""
        return sum(entry.size_bytes for entry in self._entries.values())
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        if not self._monitoring:
            self._monitoring = True
            self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self._cleanup_thread.start()
    
    def _cleanup_loop(self):
        """Background cleanup loop"""
        while self._monitoring:
            try:
                self._cleanup_expired_entries()
                self._optimize_cache()
                time.sleep(1.0)  # Run every second
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
                time.sleep(5.0)
    
    def _cleanup_expired_entries(self):
        """Remove expired entries"""
        with self._lock:
            expired_keys = []
            for key, entry in self._entries.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._remove_entry(key)
    
    def _optimize_cache(self):
        """Optimize cache based on usage patterns"""
        with self._lock:
            # Clean up old access tracking data
            current_time = time.time()
            old_keys = [k for k, t in self._access_times.items() 
                       if current_time - t > 3600]  # 1 hour
            for key in old_keys:
                self._access_times.pop(key, None)
                self._access_counts.pop(key, None)
    
    def get_metrics(self) -> CacheMetrics:
        """Get cache performance metrics"""
        with self._lock:
            total_entries = len(self._entries)
            total_size = self._get_total_memory_usage()
            
            hit_rate = 0.0
            if self._hit_count + self._miss_count > 0:
                hit_rate = self._hit_count / (self._hit_count + self._miss_count)
            
            average_access_time = 0.0
            if self._access_count > 0:
                average_access_time = self._total_access_time / self._access_count
            
            oldest_age = 0.0
            newest_age = 0.0
            if self._entries:
                ages = [entry.get_age() for entry in self._entries.values()]
                oldest_age = max(ages)
                newest_age = min(ages)
            
            return CacheMetrics(
                timestamp=time.time(),
                total_entries=total_entries,
                total_size_bytes=total_size,
                hit_count=self._hit_count,
                miss_count=self._miss_count,
                eviction_count=self._eviction_count,
                hit_rate=hit_rate,
                memory_usage_mb=total_size / 1024 / 1024,
                average_access_time=average_access_time,
                oldest_entry_age=oldest_age,
                newest_entry_age=newest_age
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        metrics = self.get_metrics()
        
        return {
            "strategy": self.strategy.value,
            "max_size": self.max_size,
            "max_memory_mb": self.max_memory_bytes / 1024 / 1024,
            "current_entries": metrics.total_entries,
            "current_memory_mb": metrics.memory_usage_mb,
            "hit_rate": f"{metrics.hit_rate:.2%}",
            "total_hits": metrics.hit_count,
            "total_misses": metrics.miss_count,
            "evictions": metrics.eviction_count,
            "average_access_time_ms": metrics.average_access_time * 1000,
            "oldest_entry_age_seconds": metrics.oldest_entry_age,
            "newest_entry_age_seconds": metrics.newest_entry_age,
            "monitoring_active": self._monitoring
        }
    
    def register_eviction_callback(self, callback: Callable):
        """Register eviction callback"""
        self._eviction_callbacks.append(callback)
    
    def register_cleanup_callback(self, callback: Callable):
        """Register cleanup callback"""
        self._cleanup_callbacks.append(callback)
    
    def cleanup(self):
        """Cleanup cache resources"""
        self._monitoring = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=1.0)
        
        self.clear()
        
        # Run cleanup callbacks
        for callback in self._cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"⚠️ Cleanup callback error: {e}")

class CacheManager:
    """Manager for multiple cache instances"""
    
    def __init__(self):
        self._caches: Dict[str, IntelligentCache] = {}
        self._lock = threading.RLock()
    
    def create_cache(self, name: str, **kwargs) -> IntelligentCache:
        """Create a new cache instance"""
        with self._lock:
            if name in self._caches:
                print(f"⚠️ Cache '{name}' already exists")
                return self._caches[name]
            
            cache = IntelligentCache(**kwargs)
            self._caches[name] = cache
            print(f"✅ Created cache '{name}'")
            return cache
    
    def get_cache(self, name: str) -> Optional[IntelligentCache]:
        """Get cache instance by name"""
        return self._caches.get(name)
    
    def delete_cache(self, name: str) -> bool:
        """Delete cache instance"""
        with self._lock:
            if name in self._caches:
                cache = self._caches.pop(name)
                cache.cleanup()
                return True
            return False
    
    def get_all_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all caches"""
        return {name: cache.get_statistics() for name, cache in self._caches.items()}
    
    def cleanup_all(self):
        """Cleanup all caches"""
        with self._lock:
            for cache in self._caches.values():
                cache.cleanup()
            self._caches.clear()

def get_cache_manager() -> CacheManager:
    """Get the global cache manager"""
    global _cache_manager
    if '_cache_manager' not in globals():
        _cache_manager = CacheManager()
    return _cache_manager

def create_cache(name: str, **kwargs) -> IntelligentCache:
    """Create a new cache"""
    return get_cache_manager().create_cache(name, **kwargs)

def get_cache(name: str) -> Optional[IntelligentCache]:
    """Get cache by name"""
    return get_cache_manager().get_cache(name)

def cache_result(ttl: Optional[float] = None, 
                priority: CachePriority = CachePriority.MEDIUM,
                cache_name: str = "default"):
    """Decorator to cache function results"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Get cache
            cache = get_cache(cache_name)
            if cache is None:
                cache = create_cache(cache_name)
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Compute result
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl=ttl, priority=priority)
            
            return result
        return wrapper
    return decorator

if __name__ == "__main__":
    # Test the intelligent caching system
    print("🗄️ Testing Intelligent Caching System")
    print("=" * 50)
    
    # Create cache
    cache = create_cache("test_cache", max_size=100, max_memory_mb=10)
    
    # Test basic operations
    cache.set("key1", "value1", ttl=5.0)
    cache.set("key2", {"data": "complex"}, priority=CachePriority.HIGH)
    
    print(f"Get key1: {cache.get('key1')}")
    print(f"Get key2: {cache.get('key2')}")
    
    # Test metrics
    stats = cache.get_statistics()
    print(f"Cache statistics: {stats}")
    
    # Test decorator
    @cache_result(ttl=10.0, priority=CachePriority.HIGH)
    def expensive_function(n):
        time.sleep(0.1)  # Simulate expensive operation
        return n * n
    
    # First call (cache miss)
    start = time.time()
    result1 = expensive_function(5)
    time1 = time.time() - start
    
    # Second call (cache hit)
    start = time.time()
    result2 = expensive_function(5)
    time2 = time.time() - start
    
    print(f"Expensive function result: {result1}")
    print(f"First call time: {time1:.3f}s")
    print(f"Second call time: {time2:.3f}s")
    print(f"Speedup: {time1/time2:.1f}x")
    
    # Cleanup
    get_cache_manager().cleanup_all()
    print("✅ Cache system test completed")
