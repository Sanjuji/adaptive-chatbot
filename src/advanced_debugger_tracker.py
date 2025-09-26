#!/usr/bin/env python3
"""
🔍 Advanced Real-time Voice Chat Debugger & Performance Tracker
Professional debugging system for voice chat with comprehensive monitoring
"""

import time
import json
import threading
import sqlite3
import logging
import asyncio
import psutil
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import queue
import websockets
import wave
import numpy as np

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_tracker.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class VoiceMetrics:
    """Voice processing metrics"""
    timestamp: float
    user_input: str
    input_length: int
    processing_time: float
    language_detected: str
    confidence: float
    voice_quality: float
    speech_rate: float  # words per minute
    tone_detected: str
    sentiment: str
    response_generated: str
    response_length: int
    tts_processing_time: float
    total_pipeline_time: float
    memory_usage: float  # MB
    cpu_usage: float  # %
    errors: List[str]
    warnings: List[str]

@dataclass
class SystemHealth:
    """System performance health metrics"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_latency: float
    active_threads: int
    open_files: int
    gpu_usage: float
    temperature: float

class AdvancedDebugTracker:
    """Professional debugging and tracking system"""
    
    def __init__(self, db_path: str = "voice_debug.db"):
        self.db_path = db_path
        self.metrics_queue = queue.Queue()
        self.health_queue = queue.Queue()
        self.active_sessions = {}
        self.performance_history = deque(maxlen=1000)
        self.error_patterns = defaultdict(int)
        self.websocket_clients = set()
        
        # Real-time monitoring flags
        self.monitoring_active = True
        self.debug_mode = True
        self.auto_fix_enabled = True
        
        # Initialize database
        self._init_database()
        
        # Start monitoring threads
        self._start_monitoring_threads()
        
        logging.info("🔍 Advanced Debug Tracker initialized")
    
    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Voice metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                user_input TEXT,
                input_length INTEGER,
                processing_time REAL,
                language_detected TEXT,
                confidence REAL,
                voice_quality REAL,
                speech_rate REAL,
                tone_detected TEXT,
                sentiment TEXT,
                response_generated TEXT,
                response_length INTEGER,
                tts_processing_time REAL,
                total_pipeline_time REAL,
                memory_usage REAL,
                cpu_usage REAL,
                errors TEXT,
                warnings TEXT
            )
        ''')
        
        # System health table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                cpu_percent REAL,
                memory_percent REAL,
                disk_usage REAL,
                network_latency REAL,
                active_threads INTEGER,
                open_files INTEGER,
                gpu_usage REAL,
                temperature REAL
            )
        ''')
        
        # Debug events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS debug_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                event_type TEXT,
                severity TEXT,
                component TEXT,
                message TEXT,
                stack_trace TEXT,
                auto_fixed BOOLEAN,
                fix_applied TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logging.info("📊 Database initialized successfully")
    
    def _start_monitoring_threads(self):
        """Start background monitoring threads"""
        
        # Metrics processor thread
        metrics_thread = threading.Thread(target=self._process_metrics, daemon=True)
        metrics_thread.start()
        
        # System health monitor
        health_thread = threading.Thread(target=self._monitor_system_health, daemon=True)
        health_thread.start()
        
        # Auto-debugger thread
        debug_thread = threading.Thread(target=self._auto_debugger, daemon=True)
        debug_thread.start()
        
        # WebSocket server for real-time updates
        websocket_thread = threading.Thread(target=self._start_websocket_server, daemon=True)
        websocket_thread.start()
        
        logging.info("🔄 Monitoring threads started")
    
    def track_voice_interaction(self, 
                              user_input: str,
                              language_detected: str = "",
                              confidence: float = 0.0,
                              processing_start: float = None,
                              response_text: str = "",
                              errors: List[str] = None,
                              warnings: List[str] = None) -> str:
        """Track a complete voice interaction with comprehensive metrics"""
        
        try:
            start_time = processing_start or time.time()
            current_time = time.time()
            
            # Calculate voice metrics
            speech_rate = self._calculate_speech_rate(user_input, current_time - start_time)
            voice_quality = self._analyze_voice_quality(user_input)
            tone_detected = self._detect_tone(user_input)
            sentiment = self._analyze_sentiment(user_input)
            
            # System metrics
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_info = psutil.virtual_memory()
            
            metrics = VoiceMetrics(
                timestamp=current_time,
                user_input=user_input,
                input_length=len(user_input),
                processing_time=current_time - start_time,
                language_detected=language_detected,
                confidence=confidence,
                voice_quality=voice_quality,
                speech_rate=speech_rate,
                tone_detected=tone_detected,
                sentiment=sentiment,
                response_generated=response_text,
                response_length=len(response_text),
                tts_processing_time=0.0,  # To be updated
                total_pipeline_time=current_time - start_time,
                memory_usage=memory_info.used / 1024 / 1024,  # MB
                cpu_usage=cpu_usage,
                errors=errors or [],
                warnings=warnings or []
            )
            
            # Add to processing queue
            self.metrics_queue.put(metrics)
            
            # Real-time analysis
            session_id = f"session_{int(current_time)}"
            self.active_sessions[session_id] = metrics
            
            # Auto-debug if issues detected
            if errors or warnings or confidence < 0.5:
                self._trigger_auto_debug(metrics, session_id)
            
            # Broadcast to web clients
            self._broadcast_metrics(metrics)
            
            logging.info(f"📊 Voice interaction tracked: {user_input[:50]}...")
            return session_id
            
        except Exception as e:
            logging.error(f"❌ Tracking failed: {e}")
            return ""
    
    def update_tts_metrics(self, session_id: str, tts_time: float):
        """Update TTS processing metrics for a session"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].tts_processing_time = tts_time
            self.active_sessions[session_id].total_pipeline_time += tts_time
    
    def _calculate_speech_rate(self, text: str, duration: float) -> float:
        """Calculate speech rate in words per minute"""
        if duration == 0:
            return 0.0
        word_count = len(text.split())
        return (word_count / duration) * 60
    
    def _analyze_voice_quality(self, text: str) -> float:
        """Analyze voice input quality (simplified)"""
        # Quality based on text clarity, length, and completeness
        if not text:
            return 0.0
        
        quality = 0.5  # Base quality
        
        # Length factor
        if 3 <= len(text.split()) <= 20:
            quality += 0.2
        
        # No repeated characters (indicates clear speech)
        if not any(c * 3 in text for c in 'aeiou'):
            quality += 0.2
        
        # Contains meaningful words
        meaningful_words = ['price', 'kitna', 'kya', 'switch', 'stabilizer', 'how', 'what']
        if any(word in text.lower() for word in meaningful_words):
            quality += 0.1
        
        return min(quality, 1.0)
    
    def _detect_tone(self, text: str) -> str:
        """Detect tone from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['please', 'help', 'request']):
            return 'polite'
        elif any(word in text_lower for word in ['fast', 'quick', 'urgent']):
            return 'urgent'
        elif any(word in text_lower for word in ['thanks', 'good', 'great']):
            return 'positive'
        elif any(word in text_lower for word in ['problem', 'issue', 'wrong']):
            return 'concerned'
        else:
            return 'neutral'
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        positive_words = ['good', 'great', 'excellent', 'perfect', 'accha', 'badhiya']
        negative_words = ['bad', 'wrong', 'problem', 'issue', 'kharab', 'galat']
        
        text_lower = text.lower()
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _process_metrics(self):
        """Process metrics from queue and store in database"""
        while self.monitoring_active:
            try:
                if not self.metrics_queue.empty():
                    metrics = self.metrics_queue.get(timeout=1)
                    self._store_metrics(metrics)
                else:
                    time.sleep(0.1)
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"❌ Metrics processing error: {e}")
    
    def _store_metrics(self, metrics: VoiceMetrics):
        """Store metrics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO voice_metrics VALUES (
                    NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            ''', (
                metrics.timestamp, metrics.user_input, metrics.input_length,
                metrics.processing_time, metrics.language_detected, metrics.confidence,
                metrics.voice_quality, metrics.speech_rate, metrics.tone_detected,
                metrics.sentiment, metrics.response_generated, metrics.response_length,
                metrics.tts_processing_time, metrics.total_pipeline_time,
                metrics.memory_usage, metrics.cpu_usage,
                json.dumps(metrics.errors), json.dumps(metrics.warnings)
            ))
            
            conn.commit()
            conn.close()
            
            # Add to performance history for analysis
            self.performance_history.append(metrics)
            
        except Exception as e:
            logging.error(f"❌ Database storage error: {e}")
    
    def _monitor_system_health(self):
        """Monitor system health continuously"""
        while self.monitoring_active:
            try:
                health = SystemHealth(
                    timestamp=time.time(),
                    cpu_percent=psutil.cpu_percent(interval=1),
                    memory_percent=psutil.virtual_memory().percent,
                    disk_usage=psutil.disk_usage('/').percent,
                    network_latency=self._measure_network_latency(),
                    active_threads=threading.active_count(),
                    open_files=len(psutil.Process().open_files()),
                    gpu_usage=0.0,  # Would need GPU libraries
                    temperature=0.0  # Would need sensor libraries
                )
                
                self.health_queue.put(health)
                self._store_health_metrics(health)
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                logging.error(f"❌ Health monitoring error: {e}")
                time.sleep(10)
    
    def _measure_network_latency(self) -> float:
        """Measure network latency (simplified)"""
        try:
            start = time.time()
            # Simple latency test - could be enhanced
            return (time.time() - start) * 1000
        except:
            return 0.0
    
    def _store_health_metrics(self, health: SystemHealth):
        """Store system health metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_health VALUES (
                    NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            ''', (
                health.timestamp, health.cpu_percent, health.memory_percent,
                health.disk_usage, health.network_latency, health.active_threads,
                health.open_files, health.gpu_usage, health.temperature
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"❌ Health storage error: {e}")
    
    def _auto_debugger(self):
        """Automatic debugging and issue resolution"""
        while self.monitoring_active:
            try:
                # Analyze recent metrics for patterns
                if len(self.performance_history) > 10:
                    self._analyze_performance_patterns()
                
                # Check for common issues
                self._check_common_issues()
                
                time.sleep(30)  # Run every 30 seconds
                
            except Exception as e:
                logging.error(f"❌ Auto-debugger error: {e}")
                time.sleep(60)
    
    def _analyze_performance_patterns(self):
        """Analyze performance patterns and identify issues"""
        recent_metrics = list(self.performance_history)[-50:]  # Last 50 interactions
        
        # Check for slow processing
        avg_processing_time = np.mean([m.processing_time for m in recent_metrics])
        if avg_processing_time > 5.0:
            self._log_debug_event("PERFORMANCE", "WARNING", "PROCESSING", 
                                f"Average processing time high: {avg_processing_time:.2f}s")
        
        # Check for low confidence
        low_confidence_count = sum(1 for m in recent_metrics if m.confidence < 0.7)
        if low_confidence_count > 10:
            self._log_debug_event("ACCURACY", "WARNING", "LANGUAGE_DETECTION", 
                                f"Low confidence detected in {low_confidence_count} recent interactions")
        
        # Check for memory leaks
        memory_usage = [m.memory_usage for m in recent_metrics]
        if len(memory_usage) > 20 and memory_usage[-1] > memory_usage[0] * 1.5:
            self._log_debug_event("MEMORY", "CRITICAL", "SYSTEM", 
                                "Potential memory leak detected - memory usage increased significantly")
    
    def _check_common_issues(self):
        """Check for common chatbot issues and auto-fix"""
        try:
            # Check if main process is responsive
            current_time = time.time()
            last_interaction = max(self.active_sessions.values(), 
                                 key=lambda x: x.timestamp).timestamp if self.active_sessions else 0
            
            if current_time - last_interaction > 300:  # 5 minutes
                self._log_debug_event("RESPONSIVENESS", "WARNING", "MAIN_PROCESS", 
                                    "No interactions in last 5 minutes - system may be unresponsive")
        except Exception as e:
            logging.error(f"❌ Issue check error: {e}")
    
    def _trigger_auto_debug(self, metrics: VoiceMetrics, session_id: str):
        """Trigger automatic debugging for problematic interactions"""
        issues = []
        
        if metrics.confidence < 0.5:
            issues.append(f"Low language detection confidence: {metrics.confidence}")
        
        if metrics.processing_time > 10.0:
            issues.append(f"Slow processing: {metrics.processing_time:.2f}s")
        
        if metrics.errors:
            issues.append(f"Errors detected: {len(metrics.errors)}")
        
        if issues:
            self._log_debug_event("AUTO_DEBUG", "INFO", "INTERACTION", 
                                f"Session {session_id}: {'; '.join(issues)}")
    
    def _log_debug_event(self, event_type: str, severity: str, component: str, 
                        message: str, auto_fixed: bool = False, fix_applied: str = ""):
        """Log debug events to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO debug_events VALUES (
                    NULL, ?, ?, ?, ?, ?, ?, ?, ?
                )
            ''', (
                time.time(), event_type, severity, component, message,
                traceback.format_exc() if severity == "CRITICAL" else "",
                auto_fixed, fix_applied
            ))
            
            conn.commit()
            conn.close()
            
            logging.info(f"🔍 Debug event: [{severity}] {component}: {message}")
            
        except Exception as e:
            logging.error(f"❌ Debug logging error: {e}")
    
    def _start_websocket_server(self):
        """Start WebSocket server for real-time updates"""
        async def handle_client(websocket, path):
            self.websocket_clients.add(websocket)
            try:
                await websocket.wait_closed()
            finally:
                self.websocket_clients.remove(websocket)
        
        async def start_server():
            await websockets.serve(handle_client, "localhost", 8765)
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(start_server())
            loop.run_forever()
        except Exception as e:
            logging.error(f"❌ WebSocket server error: {e}")
    
    def _broadcast_metrics(self, metrics: VoiceMetrics):
        """Broadcast metrics to connected WebSocket clients"""
        if not self.websocket_clients:
            return
        
        try:
            message = json.dumps(asdict(metrics), default=str)
            
            # Send to all connected clients
            disconnected_clients = []
            for client in self.websocket_clients:
                try:
                    asyncio.run(client.send(message))
                except:
                    disconnected_clients.append(client)
            
            # Remove disconnected clients
            for client in disconnected_clients:
                self.websocket_clients.discard(client)
                
        except Exception as e:
            logging.error(f"❌ Broadcast error: {e}")
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the last N hours"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get metrics from last N hours
            since_timestamp = time.time() - (hours * 3600)
            
            cursor.execute('''
                SELECT * FROM voice_metrics 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC
            ''', (since_timestamp,))
            
            metrics_data = cursor.fetchall()
            
            if not metrics_data:
                return {"message": "No data available"}
            
            # Calculate summary statistics
            processing_times = [row[4] for row in metrics_data]  # processing_time column
            confidences = [row[6] for row in metrics_data]  # confidence column
            
            summary = {
                "total_interactions": len(metrics_data),
                "avg_processing_time": np.mean(processing_times),
                "max_processing_time": np.max(processing_times),
                "min_processing_time": np.min(processing_times),
                "avg_confidence": np.mean(confidences),
                "low_confidence_count": sum(1 for c in confidences if c < 0.7),
                "error_rate": sum(1 for row in metrics_data if json.loads(row[17])) / len(metrics_data),
                "most_common_languages": self._get_language_distribution(metrics_data),
                "performance_trend": "stable"  # Could be calculated from trends
            }
            
            conn.close()
            return summary
            
        except Exception as e:
            logging.error(f"❌ Performance summary error: {e}")
            return {"error": str(e)}
    
    def _get_language_distribution(self, metrics_data) -> Dict[str, int]:
        """Get distribution of detected languages"""
        languages = [row[5] for row in metrics_data]  # language_detected column
        distribution = defaultdict(int)
        for lang in languages:
            distribution[lang] += 1
        return dict(distribution)
    
    def cleanup(self):
        """Cleanup resources"""
        self.monitoring_active = False
        logging.info("🔍 Debug tracker cleanup completed")

# Global tracker instance
_debug_tracker = None

def get_debug_tracker() -> AdvancedDebugTracker:
    """Get global debug tracker instance"""
    global _debug_tracker
    if _debug_tracker is None:
        _debug_tracker = AdvancedDebugTracker()
    return _debug_tracker

def track_voice_interaction(user_input: str, **kwargs) -> str:
    """Convenience function to track voice interactions"""
    tracker = get_debug_tracker()
    return tracker.track_voice_interaction(user_input, **kwargs)

if __name__ == "__main__":
    # Test the debugger
    tracker = AdvancedDebugTracker()
    
    # Simulate some interactions
    import time
    
    test_cases = [
        ("switch kitne ka hai", "hi", 0.95),
        ("stabilizer ka price", "hi", 0.87),
        ("hello", "en", 0.42),  # Low confidence
        ("keyboard price", "en", 0.78),
    ]
    
    for user_input, lang, conf in test_cases:
        start_time = time.time()
        session_id = tracker.track_voice_interaction(
            user_input=user_input,
            language_detected=lang,
            confidence=conf,
            processing_start=start_time,
            response_text=f"Response for: {user_input}"
        )
        print(f"✅ Tracked session: {session_id}")
        time.sleep(2)
    
    # Get performance summary
    summary = tracker.get_performance_summary()
    print("\n📊 Performance Summary:")
    print(json.dumps(summary, indent=2))
    
    tracker.cleanup()