#!/usr/bin/env python3
"""
🚀 Enhanced Language Model Caching and Multi-language Optimization
Reduces switching latency and optimizes language processing
"""

import asyncio
import threading
import time
import weakref
from collections import OrderedDict, defaultdict
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
import json
import logging
import hashlib
import pickle
import sqlite3
import psutil

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    data: Any
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    size_bytes: int = 0
    language: str = ""
    model_type: str = ""
    
    def update_access(self):
        """Update access information"""
        self.last_accessed = datetime.now()
        self.access_count += 1

@dataclass
class LanguageModelInfo:
    """Information about a loaded language model"""
    model: Any
    language: str
    model_type: str
    loaded_at: datetime
    memory_usage_mb: float
    load_time_ms: float
    usage_count: int = 0
    last_used: datetime = field(default_factory=datetime.now)

class LRUCache:
    """Thread-safe LRU cache with size limits"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 500):
        self.max_size = max_size
        self.max_memory_mb = max_memory_mb
        self.cache = OrderedDict()
        self.current_memory_mb = 0
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[CacheEntry]:
        """Get item from cache"""
        with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                entry.update_access()
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                return entry
            return None
    
    def put(self, key: str, entry: CacheEntry) -> bool:
        """Put item in cache"""
        with self._lock:
            # Check if we need to evict items
            while (len(self.cache) >= self.max_size or 
                   self.current_memory_mb + entry.size_bytes / 1024 / 1024 > self.max_memory_mb):
                if not self.cache:
                    break
                self._evict_lru()
            
            # Add new entry
            if key in self.cache:
                old_entry = self.cache[key]
                self.current_memory_mb -= old_entry.size_bytes / 1024 / 1024
            
            self.cache[key] = entry
            self.current_memory_mb += entry.size_bytes / 1024 / 1024
            return True
    
    def _evict_lru(self):
        """Evict least recently used item"""
        if self.cache:
            key, entry = self.cache.popitem(last=False)
            self.current_memory_mb -= entry.size_bytes / 1024 / 1024
            logging.debug(f"🗑️ Evicted cache entry: {key}")
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self.cache.clear()
            self.current_memory_mb = 0
    
    def stats(self) -> dict:
        """Get cache statistics"""
        with self._lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'memory_mb': self.current_memory_mb,
                'max_memory_mb': self.max_memory_mb,
                'utilization': len(self.cache) / self.max_size if self.max_size > 0 else 0
            }

class LanguageModelManager:
    """Advanced language model manager with caching and optimization"""
    
    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or Path("cache/language_models")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory caches
        self.model_cache = LRUCache(max_size=10, max_memory_mb=1000)
        self.text_cache = LRUCache(max_size=5000, max_memory_mb=200)
        self.embedding_cache = LRUCache(max_size=2000, max_memory_mb=300)
        
        # Language models tracking
        self.loaded_models: Dict[str, LanguageModelInfo] = {}
        self.preloaded_languages = set()
        self.language_usage_stats = defaultdict(int)
        
        # Performance metrics
        self.switch_times = defaultdict(list)
        self.cache_hit_rates = defaultdict(float)
        
        # Background optimization
        self._optimization_active = True
        self._start_background_optimization()
        
        # Persistent cache
        self._init_persistent_cache()
        
        logging.info("🚀 Language Model Manager initialized")
    
    def _init_persistent_cache(self):
        """Initialize persistent SQLite cache"""
        self.db_path = self.cache_dir / "model_cache.db"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache_entries (
                key TEXT PRIMARY KEY,
                data BLOB,
                language TEXT,
                model_type TEXT,
                created_at TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER,
                size_bytes INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_metadata (
                language TEXT,
                model_type TEXT,
                load_time_ms REAL,
                memory_usage_mb REAL,
                usage_count INTEGER,
                last_used TIMESTAMP,
                PRIMARY KEY (language, model_type)
            )
        """)
        
        conn.commit()
        conn.close()
        
        logging.info("✅ Persistent cache initialized")
    
    def _start_background_optimization(self):
        """Start background optimization threads"""
        # Cache cleanup thread
        cleanup_thread = threading.Thread(target=self._cache_cleanup_loop, daemon=True)
        cleanup_thread.start()
        
        # Model preloader thread
        preloader_thread = threading.Thread(target=self._model_preloader_loop, daemon=True)
        preloader_thread.start()
        
        # Statistics collector thread
        stats_thread = threading.Thread(target=self._stats_collector_loop, daemon=True)
        stats_thread.start()
    
    def _cache_cleanup_loop(self):
        """Background cache cleanup"""
        while self._optimization_active:
            try:
                # Clean expired entries
                self._clean_expired_entries()
                
                # Optimize cache based on usage patterns
                self._optimize_cache_based_on_usage()
                
                # Clean persistent cache
                self._clean_persistent_cache()
                
                time.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logging.error(f"❌ Cache cleanup error: {e}")
                time.sleep(60)
    
    def _model_preloader_loop(self):
        """Background model preloading based on usage patterns"""
        while self._optimization_active:
            try:
                # Analyze usage patterns
                popular_languages = self._get_popular_languages()
                
                # Preload models for popular languages
                for language in popular_languages[:3]:  # Top 3
                    if language not in self.preloaded_languages:
                        self._preload_language_models(language)
                
                time.sleep(600)  # Run every 10 minutes
                
            except Exception as e:
                logging.error(f"❌ Model preloader error: {e}")
                time.sleep(120)
    
    def _stats_collector_loop(self):
        """Collect and analyze performance statistics"""
        while self._optimization_active:
            try:
                # Calculate cache hit rates
                self._calculate_cache_hit_rates()
                
                # Log performance metrics
                self._log_performance_metrics()
                
                # Save statistics to persistent storage
                self._save_statistics()
                
                time.sleep(180)  # Run every 3 minutes
                
            except Exception as e:
                logging.error(f"❌ Stats collector error: {e}")
                time.sleep(60)
    
    async def get_language_model(self, language: str, model_type: str = "default"):
        """Get language model with caching"""
        model_key = f"{language}:{model_type}"
        start_time = time.time()
        
        # Check if model is already loaded
        if model_key in self.loaded_models:
            model_info = self.loaded_models[model_key]
            model_info.usage_count += 1
            model_info.last_used = datetime.now()
            self.language_usage_stats[language] += 1
            
            load_time_ms = (time.time() - start_time) * 1000
            self.switch_times[language].append(load_time_ms)
            
            return model_info.model
        
        # Load model asynchronously
        model = await self._load_model_async(language, model_type)
        
        if model:
            load_time_ms = (time.time() - start_time) * 1000
            memory_usage = self._estimate_model_memory(model)
            
            model_info = LanguageModelInfo(
                model=model,
                language=language,
                model_type=model_type,
                loaded_at=datetime.now(),
                memory_usage_mb=memory_usage,
                load_time_ms=load_time_ms,
                usage_count=1
            )
            
            self.loaded_models[model_key] = model_info
            self.language_usage_stats[language] += 1
            self.switch_times[language].append(load_time_ms)
            
            logging.info(f"✅ Loaded {language} model in {load_time_ms:.1f}ms")
            
            # Save metadata to persistent cache
            self._save_model_metadata(model_info)
            
            return model
        
        return None
    
    async def _load_model_async(self, language: str, model_type: str):
        """Asynchronously load language model"""
        try:
            # Check persistent cache first
            cached_model = self._load_from_persistent_cache(language, model_type)
            if cached_model:
                return cached_model
            
            # Load model based on type and language
            if model_type == "tts":
                model = await self._load_tts_model(language)
            elif model_type == "asr":
                model = await self._load_asr_model(language)
            elif model_type == "nlp":
                model = await self._load_nlp_model(language)
            else:
                model = await self._load_default_model(language)
            
            # Cache the loaded model
            if model:
                self._save_to_persistent_cache(language, model_type, model)
            
            return model
            
        except Exception as e:
            logging.error(f"❌ Failed to load {language} {model_type} model: {e}")
            return None
    
    async def _load_tts_model(self, language: str):
        """Load TTS model for language"""
        # Implementation would load actual TTS model
        # Placeholder for demonstration
        await asyncio.sleep(0.1)  # Simulate loading time
        return f"TTS_MODEL_{language}"
    
    async def _load_asr_model(self, language: str):
        """Load ASR model for language"""
        # Implementation would load actual ASR model
        await asyncio.sleep(0.15)  # Simulate loading time
        return f"ASR_MODEL_{language}"
    
    async def _load_nlp_model(self, language: str):
        """Load NLP model for language"""
        # Implementation would load actual NLP model
        await asyncio.sleep(0.2)  # Simulate loading time
        return f"NLP_MODEL_{language}"
    
    async def _load_default_model(self, language: str):
        """Load default model for language"""
        await asyncio.sleep(0.1)  # Simulate loading time
        return f"DEFAULT_MODEL_{language}"
    
    def _estimate_model_memory(self, model) -> float:
        """Estimate model memory usage in MB"""
        # Placeholder implementation
        # In real implementation, would calculate actual model size
        return 50.0  # MB
    
    def cache_text_processing_result(self, text: str, language: str, 
                                   processing_type: str, result: Any) -> str:
        """Cache text processing result"""
        cache_key = self._generate_cache_key(text, language, processing_type)
        
        # Serialize result for size estimation
        try:
            serialized = pickle.dumps(result)
            size_bytes = len(serialized)
        except:
            size_bytes = len(str(result).encode('utf-8'))
        
        entry = CacheEntry(
            data=result,
            size_bytes=size_bytes,
            language=language,
            model_type=processing_type
        )
        
        self.text_cache.put(cache_key, entry)
        return cache_key
    
    def get_cached_text_result(self, text: str, language: str, 
                              processing_type: str) -> Optional[Any]:
        """Get cached text processing result"""
        cache_key = self._generate_cache_key(text, language, processing_type)
        entry = self.text_cache.get(cache_key)
        return entry.data if entry else None
    
    def _generate_cache_key(self, text: str, language: str, processing_type: str) -> str:
        """Generate cache key for text processing"""
        content = f"{text}:{language}:{processing_type}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _preload_language_models(self, language: str):
        """Preload models for a language"""
        try:
            if language in self.preloaded_languages:
                return
            
            # Preload common model types
            model_types = ["tts", "asr", "nlp"]
            
            async def preload_models():
                tasks = []
                for model_type in model_types:
                    task = self.get_language_model(language, model_type)
                    tasks.append(task)
                
                await asyncio.gather(*tasks, return_exceptions=True)
            
            # Run in new event loop if none exists
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            if loop.is_running():
                # Schedule for later execution
                asyncio.create_task(preload_models())
            else:
                loop.run_until_complete(preload_models())
            
            self.preloaded_languages.add(language)
            logging.info(f"✅ Preloaded models for {language}")
            
        except Exception as e:
            logging.error(f"❌ Failed to preload {language} models: {e}")
    
    def _get_popular_languages(self) -> List[str]:
        """Get most popular languages based on usage statistics"""
        sorted_languages = sorted(
            self.language_usage_stats.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [lang for lang, _ in sorted_languages[:5]]
    
    def _clean_expired_entries(self):
        """Clean expired cache entries"""
        cutoff_time = datetime.now() - timedelta(hours=2)  # 2 hour expiry
        
        # Clean text cache
        with self.text_cache._lock:
            expired_keys = []
            for key, entry in self.text_cache.cache.items():
                if entry.last_accessed < cutoff_time and entry.access_count < 2:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.text_cache.cache[key]
            
            if expired_keys:
                logging.info(f"🧹 Cleaned {len(expired_keys)} expired text cache entries")
    
    def _optimize_cache_based_on_usage(self):
        """Optimize cache based on usage patterns"""
        # Increase cache size for frequently used languages
        popular_languages = self._get_popular_languages()
        
        for language in popular_languages[:2]:  # Top 2 languages
            # Increase cache allocation for popular languages
            pass  # Implementation would adjust cache sizes
    
    def _clean_persistent_cache(self):
        """Clean persistent cache database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete old entries (older than 7 days with low access count)
            cutoff_date = datetime.now() - timedelta(days=7)
            cursor.execute("""
                DELETE FROM cache_entries 
                WHERE last_accessed < ? AND access_count < 5
            """, (cutoff_date.isoformat(),))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            if deleted > 0:
                logging.info(f"🧹 Cleaned {deleted} old persistent cache entries")
        
        except Exception as e:
            logging.error(f"❌ Persistent cache cleanup error: {e}")
    
    def _calculate_cache_hit_rates(self):
        """Calculate cache hit rates"""
        for cache_name, cache in [("text", self.text_cache), ("model", self.model_cache)]:
            stats = cache.stats()
            # Hit rate calculation would be more sophisticated in real implementation
            estimated_hit_rate = min(0.9, stats['utilization'] * 0.8)
            self.cache_hit_rates[cache_name] = estimated_hit_rate
    
    def _log_performance_metrics(self):
        """Log performance metrics"""
        try:
            # Average switch times by language
            avg_switch_times = {}
            for lang, times in self.switch_times.items():
                if times:
                    avg_switch_times[lang] = sum(times) / len(times)
            
            # Memory usage
            total_memory_mb = sum(
                info.memory_usage_mb for info in self.loaded_models.values()
            )
            
            logging.info(f"📊 Performance metrics:")
            logging.info(f"   • Loaded models: {len(self.loaded_models)}")
            logging.info(f"   • Total memory: {total_memory_mb:.1f} MB")
            logging.info(f"   • Cache hit rates: {dict(self.cache_hit_rates)}")
            logging.info(f"   • Avg switch times: {avg_switch_times}")
            
        except Exception as e:
            logging.error(f"❌ Error logging metrics: {e}")
    
    def _save_statistics(self):
        """Save statistics to persistent storage"""
        try:
            stats_file = self.cache_dir / "performance_stats.json"
            stats = {
                'language_usage': dict(self.language_usage_stats),
                'cache_hit_rates': dict(self.cache_hit_rates),
                'loaded_models_count': len(self.loaded_models),
                'preloaded_languages': list(self.preloaded_languages),
                'timestamp': datetime.now().isoformat()
            }
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2)
                
        except Exception as e:
            logging.error(f"❌ Error saving statistics: {e}")
    
    def _load_from_persistent_cache(self, language: str, model_type: str):
        """Load model from persistent cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT data FROM cache_entries 
                WHERE language = ? AND model_type = ?
                ORDER BY last_accessed DESC LIMIT 1
            """, (language, model_type))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return pickle.loads(row[0])
            
        except Exception as e:
            logging.debug(f"Cache load failed: {e}")
        
        return None
    
    def _save_to_persistent_cache(self, language: str, model_type: str, model):
        """Save model to persistent cache"""
        try:
            serialized = pickle.dumps(model)
            size_bytes = len(serialized)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cache_key = f"{language}:{model_type}"
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT OR REPLACE INTO cache_entries 
                (key, data, language, model_type, created_at, last_accessed, access_count, size_bytes)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?)
            """, (cache_key, serialized, language, model_type, now, now, size_bytes))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.debug(f"Cache save failed: {e}")
    
    def _save_model_metadata(self, model_info: LanguageModelInfo):
        """Save model metadata to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO model_metadata
                (language, model_type, load_time_ms, memory_usage_mb, usage_count, last_used)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                model_info.language,
                model_info.model_type,
                model_info.load_time_ms,
                model_info.memory_usage_mb,
                model_info.usage_count,
                model_info.last_used.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"❌ Error saving model metadata: {e}")
    
    def get_cache_statistics(self) -> dict:
        """Get comprehensive cache statistics"""
        return {
            'model_cache': self.model_cache.stats(),
            'text_cache': self.text_cache.stats(),
            'embedding_cache': self.embedding_cache.stats(),
            'loaded_models': len(self.loaded_models),
            'preloaded_languages': list(self.preloaded_languages),
            'language_usage': dict(self.language_usage_stats),
            'cache_hit_rates': dict(self.cache_hit_rates),
            'total_memory_mb': sum(info.memory_usage_mb for info in self.loaded_models.values())
        }
    
    def clear_caches(self):
        """Clear all caches"""
        self.model_cache.clear()
        self.text_cache.clear()
        self.embedding_cache.clear()
        self.loaded_models.clear()
        self.preloaded_languages.clear()
        logging.info("🧹 All caches cleared")
    
    def shutdown(self):
        """Shutdown the language model manager"""
        logging.info("🛑 Shutting down Language Model Manager")
        
        self._optimization_active = False
        
        # Save final statistics
        self._save_statistics()
        
        # Clear caches
        self.clear_caches()
        
        logging.info("✅ Language Model Manager shutdown complete")

# Global instance
_language_model_manager = None

def get_language_model_manager() -> LanguageModelManager:
    """Get global language model manager instance"""
    global _language_model_manager
    if _language_model_manager is None:
        _language_model_manager = LanguageModelManager()
    return _language_model_manager

# Decorator for caching language processing results
def cache_language_processing(processing_type: str = "general"):
    """Decorator to cache language processing results"""
    def decorator(func):
        async def async_wrapper(text: str, language: str, *args, **kwargs):
            manager = get_language_model_manager()
            
            # Check cache first
            cached_result = manager.get_cached_text_result(text, language, processing_type)
            if cached_result is not None:
                return cached_result
            
            # Process and cache result
            result = await func(text, language, *args, **kwargs)
            manager.cache_text_processing_result(text, language, processing_type, result)
            
            return result
        
        def sync_wrapper(text: str, language: str, *args, **kwargs):
            manager = get_language_model_manager()
            
            # Check cache first
            cached_result = manager.get_cached_text_result(text, language, processing_type)
            if cached_result is not None:
                return cached_result
            
            # Process and cache result
            result = func(text, language, *args, **kwargs)
            manager.cache_text_processing_result(text, language, processing_type, result)
            
            return result
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

if __name__ == "__main__":
    # Test the language model manager
    async def test_manager():
        manager = get_language_model_manager()
        
        # Test model loading
        print("Testing model loading...")
        start_time = time.time()
        
        # Load models for different languages
        en_model = await manager.get_language_model("en", "tts")
        hi_model = await manager.get_language_model("hi", "tts")
        es_model = await manager.get_language_model("es", "tts")
        
        load_time = (time.time() - start_time) * 1000
        print(f"✅ Loaded 3 models in {load_time:.1f}ms")
        
        # Test caching
        print("\nTesting caching...")
        start_time = time.time()
        
        # Second access should be faster
        en_model2 = await manager.get_language_model("en", "tts")
        cache_time = (time.time() - start_time) * 1000
        print(f"✅ Cached access in {cache_time:.1f}ms")
        
        # Test text caching
        print("\nTesting text caching...")
        manager.cache_text_processing_result("Hello world", "en", "translation", "नमस्कार संसार")
        cached_result = manager.get_cached_text_result("Hello world", "en", "translation")
        print(f"✅ Text cache result: {cached_result}")
        
        # Print statistics
        stats = manager.get_cache_statistics()
        print(f"\n📊 Cache Statistics: {json.dumps(stats, indent=2, default=str)}")
        
        manager.shutdown()
    
    # Run the test
    asyncio.run(test_manager())
    print("🚀 Language Model Manager tests completed")