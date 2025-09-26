"""
Advanced Audio Optimization System
Optimizes audio buffer management, pygame integration, and voice processing
"""

import asyncio
import threading
import time
import weakref
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Tuple
import gc
import psutil
import numpy as np

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False

class AudioState(Enum):
    """Audio processing states"""
    IDLE = "idle"
    RECORDING = "recording"
    PLAYING = "playing"
    PROCESSING = "processing"
    ERROR = "error"

class AudioQuality(Enum):
    """Audio quality levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"

@dataclass
class AudioBuffer:
    """Optimized audio buffer with overflow protection"""
    data: deque = field(default_factory=deque)
    max_size: int = 4096
    overflow_threshold: float = 0.8
    sample_rate: int = 44100
    channels: int = 2
    dtype: str = "float32"
    created_at: float = field(default_factory=time.time)
    last_access: float = field(default_factory=time.time)
    
    def add_data(self, audio_data: np.ndarray) -> bool:
        """Add audio data to buffer with overflow protection"""
        try:
            current_size = len(self.data)
            if current_size >= self.max_size * self.overflow_threshold:
                # Trigger overflow protection
                self._handle_overflow()
            
            self.data.append(audio_data)
            self.last_access = time.time()
            return True
        except Exception as e:
            print(f"Error adding audio data: {e}")
            return False
    
    def get_data(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        """Get audio data from buffer with timeout"""
        try:
            if self.data:
                self.last_access = time.time()
                return self.data.popleft()
            return None
        except Exception as e:
            print(f"Error getting audio data: {e}")
            return None
    
    def _handle_overflow(self):
        """Handle buffer overflow by removing oldest data"""
        while len(self.data) > self.max_size // 2:
            self.data.popleft()
    
    def clear(self):
        """Clear the buffer"""
        self.data.clear()
    
    def size(self) -> int:
        """Get current buffer size"""
        return len(self.data)

@dataclass
class AudioMetrics:
    """Audio processing metrics"""
    timestamp: float
    buffer_size: int
    buffer_usage_percent: float
    overflow_count: int
    processing_time: float
    audio_quality: AudioQuality
    memory_usage_mb: float
    cpu_usage_percent: float
    errors: int
    warnings: int

class AdvancedAudioOptimizer:
    """Advanced audio optimization system"""
    
    def __init__(self):
        self.buffers: Dict[str, AudioBuffer] = {}
        self.metrics_history: deque = deque(maxlen=1000)
        self.optimization_callbacks: List[Callable] = []
        self.cleanup_callbacks: List[Callable] = []
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
        
        # Audio quality settings
        self.quality_settings = {
            AudioQuality.LOW: {
                'sample_rate': 22050,
                'channels': 1,
                'buffer_size': 1024,
                'bit_depth': 16
            },
            AudioQuality.MEDIUM: {
                'sample_rate': 44100,
                'channels': 2,
                'buffer_size': 2048,
                'bit_depth': 24
            },
            AudioQuality.HIGH: {
                'sample_rate': 48000,
                'channels': 2,
                'buffer_size': 4096,
                'bit_depth': 32
            },
            AudioQuality.ULTRA: {
                'sample_rate': 96000,
                'channels': 2,
                'buffer_size': 8192,
                'bit_depth': 32
            }
        }
        
        self.current_quality = AudioQuality.MEDIUM
        self._initialize_audio_system()
    
    def _initialize_audio_system(self):
        """Initialize audio system with optimizations"""
        try:
            if PYGAME_AVAILABLE:
                pygame.mixer.pre_init(
                    frequency=self.quality_settings[self.current_quality]['sample_rate'],
                    size=-self.quality_settings[self.current_quality]['bit_depth'],
                    channels=self.quality_settings[self.current_quality]['channels'],
                    buffer=self.quality_settings[self.current_quality]['buffer_size']
                )
                pygame.mixer.init()
                print("✅ Pygame audio system initialized with optimizations")
            
            if SOUNDDEVICE_AVAILABLE:
                # Configure sounddevice for optimal performance
                sd.default.samplerate = self.quality_settings[self.current_quality]['sample_rate']
                sd.default.channels = self.quality_settings[self.current_quality]['channels']
                sd.default.dtype = 'float32'
                print("✅ SoundDevice configured for optimal performance")
            
        except Exception as e:
            print(f"⚠️ Audio system initialization warning: {e}")
    
    def create_audio_buffer(self, name: str, quality: AudioQuality = None) -> AudioBuffer:
        """Create an optimized audio buffer"""
        with self._lock:
            if quality is None:
                quality = self.current_quality
            
            settings = self.quality_settings[quality]
            buffer = AudioBuffer(
                max_size=settings['buffer_size'],
                sample_rate=settings['sample_rate'],
                channels=settings['channels'],
                dtype='float32'
            )
            
            self.buffers[name] = buffer
            print(f"✅ Created audio buffer '{name}' with {quality.value} quality")
            return buffer
    
    def optimize_audio_quality(self, target_quality: AudioQuality):
        """Dynamically optimize audio quality based on system performance"""
        with self._lock:
            current_metrics = self._get_system_metrics()
            
            # Adjust quality based on system performance
            if current_metrics['cpu_usage'] > 80 or current_metrics['memory_usage'] > 85:
                # System under stress, reduce quality
                if target_quality.value in ['ultra', 'high']:
                    target_quality = AudioQuality.MEDIUM
                elif target_quality.value == 'medium':
                    target_quality = AudioQuality.LOW
            elif current_metrics['cpu_usage'] < 30 and current_metrics['memory_usage'] < 60:
                # System has resources, can increase quality
                if target_quality.value == 'low':
                    target_quality = AudioQuality.MEDIUM
                elif target_quality.value == 'medium':
                    target_quality = AudioQuality.HIGH
            
            if target_quality != self.current_quality:
                self._apply_quality_settings(target_quality)
                self.current_quality = target_quality
                print(f"🔄 Audio quality optimized to {target_quality.value}")
    
    def _apply_quality_settings(self, quality: AudioQuality):
        """Apply quality settings to audio system"""
        try:
            settings = self.quality_settings[quality]
            
            if PYGAME_AVAILABLE and pygame.mixer.get_init():
                pygame.mixer.quit()
                pygame.mixer.pre_init(
                    frequency=settings['sample_rate'],
                    size=-settings['bit_depth'],
                    channels=settings['channels'],
                    buffer=settings['buffer_size']
                )
                pygame.mixer.init()
            
            if SOUNDDEVICE_AVAILABLE:
                sd.default.samplerate = settings['sample_rate']
                sd.default.channels = settings['channels']
            
            # Update existing buffers
            for buffer in self.buffers.values():
                buffer.sample_rate = settings['sample_rate']
                buffer.channels = settings['channels']
                buffer.max_size = settings['buffer_size']
                
        except Exception as e:
            print(f"⚠️ Error applying quality settings: {e}")
    
    def optimize_audio_processing(self, audio_data: np.ndarray, 
                                processing_type: str = "general") -> np.ndarray:
        """Optimize audio data processing"""
        try:
            start_time = time.perf_counter()
            
            # Apply quality-based optimizations
            if self.current_quality == AudioQuality.LOW:
                # Downsample for low quality
                if len(audio_data.shape) > 1 and audio_data.shape[1] > 1:
                    audio_data = audio_data[:, 0]  # Mono conversion
            
            # Apply noise reduction for better quality
            if self.current_quality in [AudioQuality.HIGH, AudioQuality.ULTRA]:
                audio_data = self._apply_noise_reduction(audio_data)
            
            # Normalize audio levels
            audio_data = self._normalize_audio(audio_data)
            
            processing_time = time.perf_counter() - start_time
            
            # Record metrics
            self._record_processing_metrics(processing_time, len(audio_data))
            
            return audio_data
            
        except Exception as e:
            print(f"⚠️ Audio processing optimization error: {e}")
            return audio_data
    
    def _apply_noise_reduction(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply basic noise reduction"""
        try:
            # Simple high-pass filter to remove low-frequency noise
            if len(audio_data) > 1:
                # Apply a simple moving average filter
                window_size = min(5, len(audio_data) // 10)
                if window_size > 1:
                    kernel = np.ones(window_size) / window_size
                    audio_data = np.convolve(audio_data, kernel, mode='same')
            
            return audio_data
        except Exception:
            return audio_data
    
    def _normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio levels"""
        try:
            if np.max(np.abs(audio_data)) > 0:
                # Normalize to prevent clipping
                max_val = np.max(np.abs(audio_data))
                if max_val > 1.0:
                    audio_data = audio_data / max_val * 0.95
            return audio_data
        except Exception:
            return audio_data
    
    def start_monitoring(self):
        """Start audio performance monitoring"""
        if not self._monitoring:
            self._monitoring = True
            self._monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self._monitor_thread.start()
            print("🔍 Audio monitoring started")
    
    def stop_monitoring(self):
        """Stop audio performance monitoring"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
        print("⏹️ Audio monitoring stopped")
    
    def _monitoring_loop(self):
        """Audio monitoring loop"""
        while self._monitoring:
            try:
                self._collect_audio_metrics()
                self._optimize_buffers()
                time.sleep(0.1)  # Monitor every 100ms
            except Exception as e:
                print(f"⚠️ Audio monitoring error: {e}")
                time.sleep(1.0)
    
    def _collect_audio_metrics(self):
        """Collect audio performance metrics"""
        try:
            current_metrics = self._get_system_metrics()
            
            total_buffer_size = sum(buffer.size() for buffer in self.buffers.values())
            max_buffer_size = sum(buffer.max_size for buffer in self.buffers.values())
            buffer_usage = (total_buffer_size / max_buffer_size * 100) if max_buffer_size > 0 else 0
            
            metrics = AudioMetrics(
                timestamp=time.time(),
                buffer_size=total_buffer_size,
                buffer_usage_percent=buffer_usage,
                overflow_count=0,  # Track overflows
                processing_time=0.0,  # Track processing time
                audio_quality=self.current_quality,
                memory_usage_mb=current_metrics['memory_usage'],
                cpu_usage_percent=current_metrics['cpu_usage'],
                errors=0,
                warnings=0
            )
            
            self.metrics_history.append(metrics)
            
            # Trigger optimization callbacks
            for callback in self.optimization_callbacks:
                try:
                    callback(metrics)
                except Exception as e:
                    print(f"⚠️ Optimization callback error: {e}")
                    
        except Exception as e:
            print(f"⚠️ Metrics collection error: {e}")
    
    def _optimize_buffers(self):
        """Optimize audio buffers based on usage patterns"""
        try:
            current_time = time.time()
            
            for name, buffer in self.buffers.items():
                # Clean up old unused buffers
                if current_time - buffer.last_access > 30:  # 30 seconds
                    if buffer.size() > 0:
                        buffer.clear()
                        print(f"🧹 Cleaned up unused buffer '{name}'")
                
                # Optimize buffer size based on usage
                if buffer.size() > buffer.max_size * 0.9:
                    # Buffer is nearly full, increase size
                    buffer.max_size = min(buffer.max_size * 1.5, 16384)
                elif buffer.size() < buffer.max_size * 0.1:
                    # Buffer is mostly empty, decrease size
                    buffer.max_size = max(buffer.max_size * 0.8, 512)
                    
        except Exception as e:
            print(f"⚠️ Buffer optimization error: {e}")
    
    def _get_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics"""
        try:
            process = psutil.Process()
            return {
                'cpu_usage': process.cpu_percent(),
                'memory_usage': process.memory_info().rss / 1024 / 1024,  # MB
                'memory_percent': psutil.virtual_memory().percent
            }
        except Exception:
            return {'cpu_usage': 0.0, 'memory_usage': 0.0, 'memory_percent': 0.0}
    
    def _record_processing_metrics(self, processing_time: float, data_size: int):
        """Record audio processing metrics"""
        # This would be implemented to track processing performance
        pass
    
    def register_optimization_callback(self, callback: Callable):
        """Register optimization callback"""
        self.optimization_callbacks.append(callback)
    
    def register_cleanup_callback(self, callback: Callable):
        """Register cleanup callback"""
        self.cleanup_callbacks.append(callback)
    
    def get_audio_statistics(self) -> Dict[str, Any]:
        """Get comprehensive audio statistics"""
        try:
            if not self.metrics_history:
                return {"error": "No metrics available"}
            
            recent_metrics = list(self.metrics_history)[-10:]  # Last 10 measurements
            
            return {
                "current_quality": self.current_quality.value,
                "active_buffers": len(self.buffers),
                "total_buffer_size": sum(buffer.size() for buffer in self.buffers.values()),
                "average_cpu_usage": np.mean([m.cpu_usage_percent for m in recent_metrics]),
                "average_memory_usage": np.mean([m.memory_usage_mb for m in recent_metrics]),
                "average_buffer_usage": np.mean([m.buffer_usage_percent for m in recent_metrics]),
                "monitoring_active": self._monitoring,
                "pygame_available": PYGAME_AVAILABLE,
                "sounddevice_available": SOUNDDEVICE_AVAILABLE
            }
        except Exception as e:
            return {"error": f"Statistics error: {e}"}
    
    def cleanup(self):
        """Cleanup audio resources"""
        try:
            self.stop_monitoring()
            
            # Clear all buffers
            for buffer in self.buffers.values():
                buffer.clear()
            self.buffers.clear()
            
            # Run cleanup callbacks
            for callback in self.cleanup_callbacks:
                try:
                    callback()
                except Exception as e:
                    print(f"⚠️ Cleanup callback error: {e}")
            
            # Cleanup pygame
            if PYGAME_AVAILABLE and pygame.mixer.get_init():
                pygame.mixer.quit()
            
            print("🧹 Audio optimizer cleanup completed")
            
        except Exception as e:
            print(f"⚠️ Audio cleanup error: {e}")

def get_audio_optimizer() -> AdvancedAudioOptimizer:
    """Get the global audio optimizer instance"""
    global _audio_optimizer
    if '_audio_optimizer' not in globals():
        _audio_optimizer = AdvancedAudioOptimizer()
    return _audio_optimizer

def optimize_audio_processing(audio_data: np.ndarray, processing_type: str = "general") -> np.ndarray:
    """Optimize audio data processing"""
    return get_audio_optimizer().optimize_audio_processing(audio_data, processing_type)

def create_optimized_audio_buffer(name: str, quality: AudioQuality = None) -> AudioBuffer:
    """Create an optimized audio buffer"""
    return get_audio_optimizer().create_audio_buffer(name, quality)

def start_audio_monitoring():
    """Start audio performance monitoring"""
    get_audio_optimizer().start_monitoring()

def stop_audio_monitoring():
    """Stop audio performance monitoring"""
    get_audio_optimizer().stop_monitoring()

def get_audio_statistics() -> Dict[str, Any]:
    """Get audio optimization statistics"""
    return get_audio_optimizer().get_audio_statistics()

def cleanup_audio_optimizer():
    """Cleanup audio optimizer resources"""
    get_audio_optimizer().cleanup()

if __name__ == "__main__":
    # Test the audio optimizer
    print("🎵 Testing Advanced Audio Optimizer")
    print("=" * 50)
    
    optimizer = get_audio_optimizer()
    
    # Test buffer creation
    buffer = optimizer.create_audio_buffer("test_buffer", AudioQuality.HIGH)
    print(f"✅ Created buffer: {buffer}")
    
    # Test monitoring
    optimizer.start_monitoring()
    time.sleep(2)
    
    # Show statistics
    stats = optimizer.get_audio_statistics()
    print(f"📊 Audio Statistics: {stats}")
    
    # Cleanup
    optimizer.cleanup()
    print("✅ Audio optimizer test completed")
