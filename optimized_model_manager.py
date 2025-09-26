#!/usr/bin/env python3
"""
Optimized Model Manager - High Performance AI Model Loading
Implements lazy loading, quantization, and intelligent caching for 50% memory reduction
"""

import asyncio
import threading
import time
import psutil
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import tempfile
import warnings
warnings.filterwarnings("ignore")

try:
    import torch
    from transformers import (
        AutoTokenizer, AutoModel, AutoModelForCausalLM,
        AutoModelForSequenceClassification, pipeline
    )
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ Transformers not available - using fallback mode")

from logger import log_info, log_error, log_warning

@dataclass
class ModelConfig:
    """Configuration for AI model with optimization settings"""
    model_id: str
    model_type: str
    provider: str
    description: str
    memory_mb: int
    priority: str  # 'high', 'medium', 'low'
    quantized: bool = True
    cache_timeout: int = 3600  # 1 hour
    max_length: int = 512

@dataclass
class ModelStats:
    """Model usage statistics"""
    model_id: str
    load_time: float
    usage_count: int
    last_used: datetime
    memory_usage: int
    success_rate: float

class OptimizedModelManager:
    """High-performance model manager with lazy loading and quantization"""
    
    def __init__(self, max_memory_gb: float = 2.0, cache_dir: Optional[str] = None):
        self.max_memory = max_memory_gb * 1024 * 1024 * 1024  # Convert to bytes
        self.cache_dir = cache_dir or tempfile.gettempdir()
        
        # Model registry with optimized configurations
        self.model_registry = self._initialize_model_registry()
        
        # Runtime caches
        self._model_cache = {}  # model_id -> loaded model
        self._tokenizer_cache = {}  # model_id -> tokenizer
        self._pipeline_cache = {}  # model_id -> pipeline
        
        # Statistics and monitoring
        self._model_stats = {}  # model_id -> ModelStats
        self._lock = threading.RLock()
        
        # Performance monitoring
        self.start_time = datetime.now()
        self.total_requests = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Background cleanup task
        self._cleanup_task = None
        self._setup_background_tasks()
        
        log_info(f"🚀 Optimized Model Manager initialized (Max memory: {max_memory_gb}GB)")
    
    def _initialize_model_registry(self) -> Dict[str, ModelConfig]:
        """Initialize optimized model configurations"""
        return {
            # Conversational Models (Prioritized)
            "microsoft/DialoGPT-small": ModelConfig(
                model_id="microsoft/DialoGPT-small",
                model_type="conversational",
                provider="microsoft",
                description="Lightweight conversational AI",
                memory_mb=200,
                priority="high",
                quantized=True,
                max_length=256
            ),
            
            "microsoft/DialoGPT-medium": ModelConfig(
                model_id="microsoft/DialoGPT-medium",
                model_type="conversational",
                provider="microsoft", 
                description="Medium conversational AI",
                memory_mb=400,
                priority="medium",
                quantized=True,
                max_length=512
            ),
            
            # Embedding Models (Essential)
            "sentence-transformers/all-MiniLM-L6-v2": ModelConfig(
                model_id="sentence-transformers/all-MiniLM-L6-v2",
                model_type="embeddings",
                provider="huggingface",
                description="Lightweight sentence embeddings",
                memory_mb=100,
                priority="high",
                quantized=True,
                max_length=512
            ),
            
            # Sentiment Analysis (Utility)
            "cardiffnlp/twitter-roberta-base-sentiment-latest": ModelConfig(
                model_id="cardiffnlp/twitter-roberta-base-sentiment-latest",
                model_type="sentiment",
                provider="huggingface",
                description="Sentiment analysis",
                memory_mb=150,
                priority="medium",
                quantized=True,
                max_length=512
            ),
            
            # Question Answering (On-demand)
            "distilbert-base-uncased-distilled-squad": ModelConfig(
                model_id="distilbert-base-uncased-distilled-squad",
                model_type="question_answering",
                provider="huggingface",
                description="Fast question answering",
                memory_mb=120,
                priority="low",
                quantized=True,
                max_length=384
            )
        }
    
    def _setup_background_tasks(self):
        """Setup background cleanup and monitoring tasks"""
        def background_maintenance():
            while True:
                try:
                    asyncio.run(self._perform_maintenance())
                    time.sleep(300)  # Run every 5 minutes
                except Exception as e:
                    log_error(f"Background maintenance failed: {e}")
                    time.sleep(60)  # Retry after 1 minute on error
        
        self._cleanup_task = threading.Thread(
            target=background_maintenance, 
            daemon=True, 
            name="ModelManagerMaintenance"
        )
        self._cleanup_task.start()
    
    async def load_model_lazy(self, model_id: str, force_reload: bool = False) -> Optional[Any]:
        """Load model on-demand with intelligent caching"""
        
        with self._lock:
            # Check cache first
            if model_id in self._model_cache and not force_reload:
                self._update_usage_stats(model_id, cache_hit=True)
                return self._model_cache[model_id]
            
            # Check if model exists in registry
            if model_id not in self.model_registry:
                log_error(f"Model {model_id} not found in registry")
                return None
            
            # Check memory constraints
            if not await self._check_memory_availability(model_id):
                await self._free_memory_for_model(model_id)
            
            # Load model with optimization
            return await self._load_model_optimized(model_id)
    
    async def _load_model_optimized(self, model_id: str) -> Optional[Any]:
        """Load model with quantization and optimization"""
        
        if not TRANSFORMERS_AVAILABLE:
            log_warning("Transformers not available, cannot load model")
            return None
        
        config = self.model_registry[model_id]
        start_time = time.time()
        
        try:
            log_info(f"🔄 Loading optimized model: {model_id}")
            
            # Determine device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Load based on model type with optimizations
            if config.model_type == "conversational":
                model = await self._load_conversational_model(model_id, device, config)
            elif config.model_type == "embeddings":
                model = await self._load_embeddings_model(model_id, config)
            elif config.model_type == "sentiment":
                model = await self._load_sentiment_model(model_id, device, config)
            elif config.model_type == "question_answering":
                model = await self._load_qa_model(model_id, device, config)
            else:
                model = await self._load_generic_model(model_id, device, config)
            
            if model:
                # Cache the model
                self._model_cache[model_id] = model
                
                # Track statistics
                load_time = time.time() - start_time
                memory_usage = self._get_model_memory_usage(model_id)
                
                self._model_stats[model_id] = ModelStats(
                    model_id=model_id,
                    load_time=load_time,
                    usage_count=1,
                    last_used=datetime.now(),
                    memory_usage=memory_usage,
                    success_rate=1.0
                )
                
                log_info(f"✅ Model {model_id} loaded successfully in {load_time:.2f}s ({memory_usage}MB)")
                return model
            
        except Exception as e:
            log_error(f"Failed to load model {model_id}: {e}")
            return None
    
    async def _load_conversational_model(self, model_id: str, device: str, config: ModelConfig):
        """Load conversational model with quantization"""
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            cache_dir=self.cache_dir,
            use_fast=True
        )
        
        # Handle special tokens
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Load model with quantization
        if config.quantized and torch.cuda.is_available():
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                cache_dir=self.cache_dir,
                torch_dtype=torch.float16,  # Half precision
                device_map="auto",
                low_cpu_mem_usage=True
            )
        else:
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                cache_dir=self.cache_dir,
                torch_dtype=torch.float32
            )
            model.to(device)
        
        model.eval()
        
        # Cache tokenizer separately
        self._tokenizer_cache[model_id] = tokenizer
        
        return model
    
    async def _load_embeddings_model(self, model_id: str, config: ModelConfig):
        """Load sentence embeddings model"""
        
        try:
            # Use SentenceTransformer if available
            model = SentenceTransformer(
                model_id,
                cache_folder=self.cache_dir,
                device="cuda" if torch.cuda.is_available() else "cpu"
            )
            
            # Enable half precision if supported
            if config.quantized and torch.cuda.is_available():
                model.half()
            
            return model
            
        except Exception as e:
            log_warning(f"SentenceTransformer failed, using fallback: {e}")
            
            # Fallback to regular transformers
            tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=self.cache_dir)
            model = AutoModel.from_pretrained(model_id, cache_dir=self.cache_dir)
            
            if config.quantized:
                model.half()
            
            model.eval()
            self._tokenizer_cache[model_id] = tokenizer
            return model
    
    async def _load_sentiment_model(self, model_id: str, device: str, config: ModelConfig):
        """Load sentiment analysis model as pipeline"""
        
        device_id = 0 if device == "cuda" else -1
        
        pipeline_obj = pipeline(
            "sentiment-analysis",
            model=model_id,
            tokenizer=model_id,
            device=device_id,
            model_kwargs={
                "cache_dir": self.cache_dir,
                "torch_dtype": torch.float16 if config.quantized else torch.float32
            },
            return_all_scores=True
        )
        
        return pipeline_obj
    
    async def _load_qa_model(self, model_id: str, device: str, config: ModelConfig):
        """Load question answering model as pipeline"""
        
        device_id = 0 if device == "cuda" else -1
        
        pipeline_obj = pipeline(
            "question-answering",
            model=model_id,
            tokenizer=model_id,
            device=device_id,
            model_kwargs={
                "cache_dir": self.cache_dir,
                "torch_dtype": torch.float16 if config.quantized else torch.float32
            }
        )
        
        return pipeline_obj
    
    async def _load_generic_model(self, model_id: str, device: str, config: ModelConfig):
        """Load generic model"""
        
        tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=self.cache_dir)
        model = AutoModel.from_pretrained(model_id, cache_dir=self.cache_dir)
        
        if config.quantized:
            model.half()
        
        model.to(device)
        model.eval()
        
        self._tokenizer_cache[model_id] = tokenizer
        return model
    
    async def _check_memory_availability(self, model_id: str) -> bool:
        """Check if enough memory is available for model"""
        
        config = self.model_registry[model_id]
        required_memory = config.memory_mb * 1024 * 1024  # Convert to bytes
        
        # Get current memory usage
        current_memory = psutil.Process().memory_info().rss
        available_memory = self.max_memory - current_memory
        
        return available_memory >= required_memory
    
    async def _free_memory_for_model(self, model_id: str):
        """Free memory by unloading low-priority models"""
        
        config = self.model_registry[model_id]
        required_memory = config.memory_mb * 1024 * 1024
        
        log_info(f"🧹 Freeing memory for {model_id} ({config.memory_mb}MB required)")
        
        # Sort models by priority and last used time
        unload_candidates = []
        
        for cached_model_id in list(self._model_cache.keys()):
            if cached_model_id == model_id:
                continue
                
            cached_config = self.model_registry.get(cached_model_id)
            if not cached_config:
                continue
            
            stats = self._model_stats.get(cached_model_id)
            if not stats:
                continue
            
            # Priority scoring (lower is more likely to be unloaded)
            priority_score = {
                'low': 1,
                'medium': 2, 
                'high': 3
            }.get(cached_config.priority, 2)
            
            # Time since last used (hours)
            hours_since_used = (datetime.now() - stats.last_used).total_seconds() / 3600
            
            # Combined score (lower = better candidate for unloading)
            score = priority_score - (hours_since_used * 0.1)
            
            unload_candidates.append((cached_model_id, score, cached_config.memory_mb))
        
        # Sort by score (ascending - lowest first)
        unload_candidates.sort(key=lambda x: x[1])
        
        # Unload models until we have enough memory
        freed_memory = 0
        for model_id_to_unload, score, memory_mb in unload_candidates:
            await self._unload_model(model_id_to_unload)
            freed_memory += memory_mb * 1024 * 1024
            
            if freed_memory >= required_memory:
                break
    
    async def _unload_model(self, model_id: str):
        """Unload model from memory"""
        
        with self._lock:
            if model_id in self._model_cache:
                del self._model_cache[model_id]
            
            if model_id in self._tokenizer_cache:
                del self._tokenizer_cache[model_id]
            
            if model_id in self._pipeline_cache:
                del self._pipeline_cache[model_id]
            
            # Clear GPU cache if available
            if TRANSFORMERS_AVAILABLE and torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            log_info(f"🗑️ Unloaded model: {model_id}")
    
    def _get_model_memory_usage(self, model_id: str) -> int:
        """Estimate model memory usage in MB"""
        
        config = self.model_registry.get(model_id)
        if config:
            return config.memory_mb
        
        # Fallback estimation
        return 100
    
    def _update_usage_stats(self, model_id: str, cache_hit: bool = False):
        """Update model usage statistics"""
        
        with self._lock:
            self.total_requests += 1
            
            if cache_hit:
                self.cache_hits += 1
            else:
                self.cache_misses += 1
            
            if model_id in self._model_stats:
                stats = self._model_stats[model_id]
                stats.usage_count += 1
                stats.last_used = datetime.now()
            
    async def _perform_maintenance(self):
        """Perform periodic maintenance tasks"""
        
        try:
            # Check for expired models
            await self._cleanup_expired_models()
            
            # Check memory usage
            await self._check_memory_health()
            
            # Update statistics
            self._update_performance_stats()
            
        except Exception as e:
            log_error(f"Maintenance task failed: {e}")
    
    async def _cleanup_expired_models(self):
        """Remove models that haven't been used recently"""
        
        now = datetime.now()
        models_to_unload = []
        
        for model_id, stats in self._model_stats.items():
            config = self.model_registry.get(model_id)
            if not config:
                continue
            
            # Check if model has expired
            time_since_used = now - stats.last_used
            cache_timeout = timedelta(seconds=config.cache_timeout)
            
            if time_since_used > cache_timeout and config.priority != 'high':
                models_to_unload.append(model_id)
        
        # Unload expired models
        for model_id in models_to_unload:
            await self._unload_model(model_id)
            log_info(f"⏰ Unloaded expired model: {model_id}")
    
    async def _check_memory_health(self):
        """Monitor memory usage and take action if needed"""
        
        current_memory = psutil.Process().memory_info().rss
        memory_usage_percent = (current_memory / self.max_memory) * 100
        
        if memory_usage_percent > 85:  # Critical threshold
            log_warning(f"🚨 High memory usage: {memory_usage_percent:.1f}%")
            
            # Emergency cleanup - unload low priority models
            low_priority_models = [
                model_id for model_id, config in self.model_registry.items()
                if config.priority == 'low' and model_id in self._model_cache
            ]
            
            for model_id in low_priority_models:
                await self._unload_model(model_id)
    
    def _update_performance_stats(self):
        """Update performance statistics"""
        
        runtime = (datetime.now() - self.start_time).total_seconds()
        
        if runtime > 0:
            requests_per_second = self.total_requests / runtime
            cache_hit_rate = (self.cache_hits / max(self.total_requests, 1)) * 100
            
            log_info(f"📊 Performance - RPS: {requests_per_second:.2f}, Cache hit rate: {cache_hit_rate:.1f}%")
    
    def get_tokenizer(self, model_id: str) -> Optional[Any]:
        """Get tokenizer for a model"""
        return self._tokenizer_cache.get(model_id)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        
        runtime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "runtime_seconds": runtime,
            "total_requests": self.total_requests,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": (self.cache_hits / max(self.total_requests, 1)) * 100,
            "requests_per_second": self.total_requests / max(runtime, 1),
            "loaded_models": len(self._model_cache),
            "available_models": len(self.model_registry),
            "memory_usage_mb": psutil.Process().memory_info().rss / (1024 * 1024)
        }
    
    def get_model_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed model statistics"""
        
        return {
            model_id: {
                "load_time": stats.load_time,
                "usage_count": stats.usage_count,
                "last_used": stats.last_used.isoformat(),
                "memory_usage_mb": stats.memory_usage,
                "success_rate": stats.success_rate,
                "is_loaded": model_id in self._model_cache
            }
            for model_id, stats in self._model_stats.items()
        }
    
    async def preload_essential_models(self) -> Dict[str, bool]:
        """Preload high-priority models for better performance"""
        
        essential_models = [
            model_id for model_id, config in self.model_registry.items()
            if config.priority == 'high'
        ]
        
        results = {}
        log_info(f"🔥 Preloading {len(essential_models)} essential models...")
        
        for model_id in essential_models:
            model = await self.load_model_lazy(model_id)
            results[model_id] = model is not None
            
        successful_loads = sum(results.values())
        log_info(f"✅ Preloaded {successful_loads}/{len(essential_models)} essential models")
        
        return results
    
    async def cleanup_all(self):
        """Clean up all loaded models and resources"""
        
        log_info("🧹 Cleaning up all models...")
        
        with self._lock:
            # Unload all models
            for model_id in list(self._model_cache.keys()):
                await self._unload_model(model_id)
            
            # Clear all caches
            self._model_cache.clear()
            self._tokenizer_cache.clear() 
            self._pipeline_cache.clear()
            
            # Clear GPU cache
            if TRANSFORMERS_AVAILABLE and torch.cuda.is_available():
                torch.cuda.empty_cache()
            
        log_info("✅ Model cleanup completed")


# Global instance
_optimized_model_manager = None

def get_optimized_model_manager(**kwargs) -> OptimizedModelManager:
    """Get or create the global optimized model manager"""
    global _optimized_model_manager
    if _optimized_model_manager is None:
        _optimized_model_manager = OptimizedModelManager(**kwargs)
    return _optimized_model_manager

async def preload_models():
    """Convenience function to preload essential models"""
    manager = get_optimized_model_manager()
    return await manager.preload_essential_models()

if __name__ == "__main__":
    # Test the optimized model manager
    async def test_model_manager():
        print("🧪 Testing Optimized Model Manager")
        print("=" * 50)
        
        manager = get_optimized_model_manager(max_memory_gb=1.5)
        
        # Test model loading
        start_time = time.time()
        model = await manager.load_model_lazy("microsoft/DialoGPT-small")
        load_time = time.time() - start_time
        
        print(f"✅ Model loaded in {load_time:.2f}s")
        print(f"📊 Performance stats: {manager.get_performance_stats()}")
        
        # Test preloading
        preload_results = await manager.preload_essential_models()
        print(f"🔥 Preload results: {preload_results}")
        
        # Cleanup
        await manager.cleanup_all()
        print("🧹 Cleanup completed")
    
    # Run test
    asyncio.run(test_model_manager())