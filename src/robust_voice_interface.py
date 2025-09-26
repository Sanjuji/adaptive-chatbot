#!/usr/bin/env python3
"""
Robust Voice Interface with Comprehensive Error Handling
Optimized performance and graceful fallback mechanisms
"""

import speech_recognition as sr
import pyttsx3
import time
import threading
from typing import Optional, Dict, Any, List
import tempfile
import os
from config import config
from logger import log_info, log_error, log_warning, log_voice_event
from validators import safe_input
from transliteration import enhanced_transliterate, has_devanagari

# Optional imports with fallbacks
try:
    from core.edge_tts_engine import get_edge_tts_engine, cleanup_edge_tts
    from core.hinglish_voice_processor import hinglish_processor
    EDGETTS_AVAILABLE = True
except ImportError:
    EDGETTS_AVAILABLE = False
    log_warning("EdgeTTS not available")

try:
    import win32com.client
    WINDOWS_SAPI_AVAILABLE = True
except ImportError:
    WINDOWS_SAPI_AVAILABLE = False
    log_warning("Windows SAPI not available")

try:
    from gtts import gTTS
    import pygame
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    log_warning("Google TTS not available")

class VoiceInterfaceError(Exception):
    """Custom exception for voice interface errors"""
    pass

class RobustVoiceInterface:
    """Production-ready voice interface with comprehensive error handling"""
    
    def __init__(self):
        self.recognizer = None
        self.microphone = None
        self.tts_engines = {}
        self.current_tts = None
        self.is_initialized = False
        self.initialization_lock = threading.Lock()
        
        # Performance settings
        self.recognition_timeout = config.get('voice', 'recognition_timeout', 10)
        self.max_retry_attempts = config.get('voice', 'max_retry_attempts', 3)
        
        # Initialize in background
        self._lazy_initialize()
    
    def _lazy_initialize(self):
        """Lazy initialization to improve startup performance"""
        if self.is_initialized:
            return True
        
        with self.initialization_lock:
            if self.is_initialized:  # Double-check
                return True
            
            try:
                log_info("Initializing voice interface...")
                
                # Initialize recognizer
                self._init_recognizer()
                
                # Initialize TTS engines
                self._init_tts_engines()
                
                self.is_initialized = True
                log_info("Voice interface initialized successfully")
                return True
                
            except Exception as e:
                log_error("Failed to initialize voice interface", error=e)
                return False
    
    def _init_recognizer(self):
        """Initialize speech recognizer with Hinglish optimization"""
        try:
            self.recognizer = sr.Recognizer()
            
            # Get optimized settings for Hinglish recognition
            if EDGETTS_AVAILABLE:
                hinglish_config = hinglish_processor.optimize_for_speech_recognition('hinglish')
                self.recognizer.energy_threshold = hinglish_config['energy_threshold']
                self.recognizer.pause_threshold = hinglish_config['pause_threshold']
            else:
                # Fallback settings
                self.recognizer.energy_threshold = config.get('voice', 'energy_threshold', 300)
                self.recognizer.pause_threshold = config.get('voice', 'pause_threshold', 0.7)
            
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.phrase_threshold = config.get('voice', 'phrase_threshold', 0.5)
            
            # Initialize microphone
            self._init_microphone()
            
            log_info(f"Speech recognizer optimized for Hinglish - Energy: {self.recognizer.energy_threshold}, Pause: {self.recognizer.pause_threshold}")
            
        except Exception as e:
            log_error("Failed to initialize speech recognizer", error=e)
            raise VoiceInterfaceError(f"Speech recognizer initialization failed: {e}")
    
    def _init_microphone(self):
        """Initialize microphone with intelligent selection"""
        try:
            mic_list = sr.Microphone.list_microphone_names()
            log_info(f"Found {len(mic_list)} audio devices")
            
            # Smart microphone selection
            selected_mic = self._select_best_microphone(mic_list)
            
            if selected_mic is not None:
                self.microphone = sr.Microphone(device_index=selected_mic)
                log_voice_event("MICROPHONE_INIT", f"Selected device index {selected_mic}")
            else:
                self.microphone = sr.Microphone()
                log_voice_event("MICROPHONE_INIT", "Using default microphone")
            
            # Test microphone
            self._test_microphone()
            
        except Exception as e:
            log_error("Microphone initialization failed", error=e)
            # Fallback to default microphone
            try:
                self.microphone = sr.Microphone()
                log_warning("Using fallback default microphone")
            except Exception as fallback_error:
                raise VoiceInterfaceError(f"Microphone initialization completely failed: {fallback_error}")
    
    def _select_best_microphone(self, mic_list: List[str]) -> Optional[int]:
        """Intelligently select the best microphone"""
        # Preferred microphone types (in order of preference)
        preferred_types = [
            ['microphone', 'webcam'],  # USB microphones, webcam mics
            ['array', 'realtek'],      # Microphone arrays, Realtek audio
            ['input'],                 # General input devices
        ]
        
        # Avoid these types
        avoid_types = ['speakers', 'output', 'mapper - output', 'headphones']
        
        for preference_group in preferred_types:
            for i, name in enumerate(mic_list):
                name_lower = name.lower()
                
                # Skip if it's an output device
                if any(avoid_type in name_lower for avoid_type in avoid_types):
                    continue
                
                # Check if it matches preferred type
                if any(pref_type in name_lower for pref_type in preference_group):
                    log_info(f"Selected microphone: {name}")
                    return i
        
        return None
    
    def _test_microphone(self):
        """Test microphone functionality"""
        try:
            with self.microphone as source:
                # Quick ambient noise adjustment
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            log_voice_event("MICROPHONE_TEST", "Microphone test passed")
        except Exception as e:
            log_warning("Microphone test failed", error=e)
    
    def _init_tts_engines(self):
        """Initialize TTS engines with EdgeTTS priority"""
        self.tts_engines = {}
        
        # 1. EdgeTTS (Primary choice - Realistic human-like voice)
        if EDGETTS_AVAILABLE:
            try:
                edge_engine = get_edge_tts_engine()
                if edge_engine:
                    # Configure optimal voice for Hindi Devanagari - multilingual works best
                    edge_engine.set_voice('multilingual_warm')
                    edge_engine.set_volume(0.8)
                    self.tts_engines['edgetts'] = edge_engine
                    log_voice_event("TTS_INIT", "EdgeTTS multilingual voice initialized for Devanagari")
            except Exception as e:
                log_warning("EdgeTTS initialization failed", error=e)
        
        # 2. Windows SAPI (Fallback for Windows)
        if WINDOWS_SAPI_AVAILABLE:
            try:
                sapi = self._init_sapi_engine()
                if sapi:
                    self.tts_engines['sapi'] = sapi
                    log_voice_event("TTS_INIT", "Windows SAPI initialized")
            except Exception as e:
                log_warning("SAPI initialization failed", error=e)
        
        # 3. Pyttsx3 (Reliable fallback)
        try:
            pyttsx3_engine = self._init_pyttsx3_engine()
            if pyttsx3_engine:
                self.tts_engines['pyttsx3'] = pyttsx3_engine
                log_voice_event("TTS_INIT", "Pyttsx3 initialized")
        except Exception as e:
            log_warning("Pyttsx3 initialization failed", error=e)
        
        # 4. Google TTS (Internet-dependent fallback)
        if GTTS_AVAILABLE:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self.tts_engines['gtts'] = True
                log_voice_event("TTS_INIT", "Google TTS initialized")
            except Exception as e:
                log_warning("Google TTS initialization failed", error=e)
        
        # Set default engine
        self._set_default_tts_engine()
    
    def _init_sapi_engine(self):
        """Initialize Windows SAPI TTS engine"""
        try:
            sapi = win32com.client.Dispatch("SAPI.SpVoice")
            voices = sapi.GetVoices()
            
            # Try to find a good male voice first, then fallback to any voice
            best_voice = None
            
            # First priority: Male voices
            for voice in voices:
                desc = voice.GetDescription().lower()
                if any(keyword in desc for keyword in ['david', 'male', 'mark', 'ravi']):
                    best_voice = voice
                    log_info(f"Selected male voice: {voice.GetDescription()}")
                    break
            
            # Fallback: Any available voice
            if not best_voice and voices:
                best_voice = voices.Item(0)  # Use first available voice
                log_info(f"Using fallback voice: {best_voice.GetDescription()}")
            
            if best_voice:
                sapi.Voice = best_voice
                log_info(f"SAPI voice selected: {best_voice.GetDescription()}")
            
            # Configure settings for normal, natural speech
            sapi.Rate = config.get('tts', 'sapi_rate', -1)  # Slightly slower than default (0) for clarity
            sapi.Volume = int(config.get('tts', 'volume', 0.8) * 100)
            
            return sapi
            
        except Exception as e:
            log_error("SAPI engine initialization failed", error=e)
            return None
    
    def _init_pyttsx3_engine(self):
        """Initialize Pyttsx3 TTS engine"""
        try:
            engine = pyttsx3.init(driverName='sapi5' if os.name == 'nt' else None)
            
            # Configure voice - prefer male voices
            voices = engine.getProperty('voices')
            if voices:
                # Try to find a good male voice first
                best_voice = None
                
                # First priority: Male voices
                for voice in voices:
                    voice_name = voice.name.lower()
                    if any(keyword in voice_name for keyword in ['david', 'male', 'mark', 'ravi']):
                        best_voice = voice
                        log_info(f"Pyttsx3 male voice selected: {voice.name}")
                        break
                
                # Fallback: Use first available voice
                if not best_voice:
                    best_voice = voices[0]
                    log_info(f"Pyttsx3 fallback voice selected: {best_voice.name}")
                
                if best_voice:
                    engine.setProperty('voice', best_voice.id)
            
            # Configure settings for normal, natural speech
            engine.setProperty('rate', config.get('tts', 'speech_rate', 180))  # Normal speaking rate
            engine.setProperty('volume', config.get('tts', 'volume', 0.8))
            
            return engine
            
        except Exception as e:
            log_error("Pyttsx3 engine initialization failed", error=e)
            return None
    
    def _set_default_tts_engine(self):
        """Set the default TTS engine based on availability (EdgeTTS priority for Hinglish)"""
        preference_order = ['edgetts', 'sapi', 'pyttsx3', 'gtts']
        
        for engine_name in preference_order:
            if engine_name in self.tts_engines:
                self.current_tts = engine_name
                log_info(f"Default TTS engine set to: {engine_name}")
                return
        
        if not self.tts_engines:
            log_warning("No TTS engines available")
            self.current_tts = None
    
    def speak_text(self, text: str, retry_on_failure: bool = True) -> bool:
        """Speak text with Hinglish-optimized error handling"""
        if not text or not text.strip():
            return False
        
        # Ensure initialization
        if not self._lazy_initialize():
            log_error("Cannot speak: voice interface not initialized")
            return False
        
        # Sanitize input
        safe_text = safe_input.validator.sanitize_text(text)
        if not safe_text:
            log_warning("Cannot speak: text sanitization failed")
            return False
        
        log_info(f"Speaking: {safe_text[:50]}...")
        
        # Try primary engine with original text (no modification for EdgeTTS)
        if self._try_speak_with_engine(self.current_tts, safe_text):
            log_voice_event("TTS_SUCCESS", f"Engine: {self.current_tts}")
            return True
        
        # Try fallback engines if retry is enabled
        if retry_on_failure:
            return self._try_fallback_speech(safe_text)
        
        return False
    
    def _try_speak_with_engine(self, engine_name: str, text: str) -> bool:
        """Try to speak with a specific engine"""
        if not engine_name or engine_name not in self.tts_engines:
            return False
        
        try:
            if engine_name == 'edgetts':
                # EdgeTTS - Realistic human-like voice with intelligent processing
                edge_engine = self.tts_engines['edgetts']
                # Use auto voice selection for best Hinglish pronunciation
                return edge_engine.speak(text, blocking=True, auto_voice_select=True)
                
            elif engine_name == 'sapi':
                # Add a minimal delay for natural pacing
                time.sleep(0.1)
                sapi_engine = self.tts_engines['sapi']
                # Ensure normal speech rate is set
                sapi_engine.Rate = config.get('tts', 'sapi_rate', -1)
                sapi_engine.Speak(text)
                # Brief pause after speaking
                time.sleep(0.1)
                return True
                
            elif engine_name == 'pyttsx3':
                time.sleep(0.1)
                engine = self.tts_engines['pyttsx3']
                # Ensure normal speech rate
                engine.setProperty('rate', config.get('tts', 'speech_rate', 180))
                engine.say(text)
                engine.runAndWait()
                time.sleep(0.1)
                return True
                
            elif engine_name == 'gtts':
                return self._speak_with_gtts(text)
        
        except Exception as e:
            log_error(f"TTS engine {engine_name} failed", error=e)
            return False
        
        return False
    
    def _try_fallback_speech(self, text: str) -> bool:
        """Try fallback TTS engines"""
        fallback_engines = [name for name in self.tts_engines.keys() if name != self.current_tts]
        
        for engine_name in fallback_engines:
            log_info(f"Trying fallback TTS engine: {engine_name}")
            if self._try_speak_with_engine(engine_name, text):
                log_voice_event("TTS_FALLBACK_SUCCESS", f"Engine: {engine_name}")
                return True
        
        log_error("All TTS engines failed")
        return False
    
    def _speak_with_gtts(self, text: str) -> bool:
        """Speak using Google TTS"""
        try:
            # Determine language
            language = 'hi' if any(ord(char) > 127 for char in text) else 'en'
            
            tts = gTTS(text=text, lang=language, slow=False)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                
                # Play with pygame
                pygame.mixer.music.load(tmp_file.name)
                pygame.mixer.music.play()
                
                # Wait for playback completion
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                # Cleanup
                try:
                    os.unlink(tmp_file.name)
                except:
                    pass  # Ignore cleanup errors
                
                return True
                
        except Exception as e:
            log_error("Google TTS failed", error=e)
            return False
    
    def listen_for_speech(self, timeout: int = None, language: str = None) -> Optional[str]:
        """Listen for speech with Hinglish optimization"""
        if not self._lazy_initialize():
            log_error("Cannot listen: voice interface not initialized")
            return None
        
        if timeout is None:
            timeout = self.recognition_timeout
        
        # Use Hinglish-optimized language settings
        if language is None:
            if EDGETTS_AVAILABLE:
                hinglish_config = hinglish_processor.optimize_for_speech_recognition('hinglish')
                language = hinglish_config['primary_language']
            else:
                language = config.get('voice', 'default_language', 'en-IN')  # Better for Hinglish
        
        try:
            log_voice_event("LISTENING_START", f"Timeout: {timeout}s, Language: {language}")
            
            with self.microphone as source:
                # Optimized ambient noise adjustment for Hinglish
                self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                
                # Listen for audio with Hinglish-optimized parameters
                phrase_limit = 18 if EDGETTS_AVAILABLE else 20
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit
                )
            
            # Try recognition with Hinglish fallback
            return self._recognize_speech_with_hinglish_fallback(audio, language)
            
        except sr.WaitTimeoutError:
            log_voice_event("LISTENING_TIMEOUT", "No speech detected", success=False)
            return None
            
        except Exception as e:
            log_error("Speech listening failed", error=e)
            return None
    
    def _recognize_speech_with_hinglish_fallback(self, audio, primary_language: str) -> Optional[str]:
        """Recognize speech with Hinglish-optimized fallback options and processing"""
        
        # Get Hinglish-optimized language sequence
        if EDGETTS_AVAILABLE:
            hinglish_config = hinglish_processor.optimize_for_speech_recognition('hinglish')
            languages_to_try = [primary_language] + hinglish_config['fallback_languages']
        else:
            languages_to_try = [primary_language, 'en-IN', 'hi-IN', 'en-US']
        
        recognition_methods = [
            ('Google', lambda lang: self.recognizer.recognize_google(audio, language=lang)),
        ]
        
        # Try Windows Speech Recognition if available
        if hasattr(self.recognizer, 'recognize_sphinx'):
            recognition_methods.append(
                ('Windows', lambda _: self.recognizer.recognize_sphinx(audio))
            )
        
        for method_name, recognition_func in recognition_methods:
            for lang in languages_to_try:
                try:
                    result = recognition_func(lang)
                    if result and result.strip():
                        # Post-process with Hinglish processor
                        if EDGETTS_AVAILABLE:
                            result = hinglish_processor.post_process_recognition_result(result)
                        
                        # Filter out nonsensical or repetitive results
                        if self._is_valid_speech_result(result):
                            # Transliterate Devanagari to Hinglish if needed
                            if has_devanagari(result):
                                result = enhanced_transliterate(result)
                                log_info(f"Transliterated to Hinglish: {result[:50]}")
                            
                            # Validate the result
                            safe_result = safe_input.get_voice_command(result)
                            if safe_result:
                                log_voice_event("RECOGNITION_SUCCESS", f"Method: {method_name} ({lang}), Text: {safe_result[:50]}")
                                return safe_result
                            else:
                                log_warning(f"Recognition result failed validation: {result[:50]}")
                        else:
                            log_warning(f"Recognition result filtered out: {result[:50]}")
                            
                except sr.UnknownValueError:
                    # Try next language
                    continue
                except sr.RequestError as e:
                    log_error(f"Recognition service error ({method_name} - {lang})", error=e)
                    continue
                except Exception as e:
                    log_error(f"Recognition error ({method_name} - {lang})", error=e)
                    continue
            
            # Log failure for this method after trying all languages
            log_voice_event("RECOGNITION_UNKNOWN", f"Method: {method_name} - All languages failed", success=False)
        
        log_voice_event("RECOGNITION_FAILED", "All methods and languages failed", success=False)
        return None
    
    def _is_valid_speech_result(self, result: str) -> bool:
        """Filter out nonsensical or repetitive speech recognition results"""
        if not result or len(result.strip()) < 2:
            return False
        
        result_lower = result.lower().strip()
        
        # Filter out repetitive patterns (like "hello hello hello")
        words = result_lower.split()
        if len(words) > 3:
            # Check for excessive repetition of the same word
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            # If any word repeats more than 3 times, it's likely noise
            if any(count > 3 for count in word_counts.values()):
                return False
            
            # Check for sequences like "hello hello hello hello"
            for i in range(len(words) - 2):
                if words[i] == words[i+1] == words[i+2]:
                    return False
        
        # Filter out common noise patterns
        noise_patterns = [
            'fast forward',
            'rewind', 
            'play',
            'pause',
            'next',
            'previous',
            'volume up',
            'volume down',
            'मी मी मी',  # Common noise
            'ला ला ला',  # Common noise
            'उह उह उह',  # Common noise
            'mmm mmm mmm',
            'uh uh uh',
            'ah ah ah'
        ]
        
        for pattern in noise_patterns:
            if pattern in result_lower:
                return False
        
        # Filter out very short meaningless sounds
        if len(result_lower) < 4 and result_lower in ['uh', 'ah', 'um', 'हम', 'उम', 'अ', 'ओ']:
            return False
        
        return True
    
    def _add_natural_pauses(self, text: str) -> str:
        """Add natural pauses to text for better speech clarity (disabled for EdgeTTS)"""
        # EdgeTTS handles natural pauses better internally
        # Avoid text modification that causes letter-by-letter pronunciation
        return text
    
    def is_available(self) -> bool:
        """Check if voice interface is available and functional"""
        return self._lazy_initialize() and self.current_tts is not None
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed status of voice interface"""
        return {
            'initialized': self.is_initialized,
            'microphone_available': self.microphone is not None,
            'tts_engines': list(self.tts_engines.keys()),
            'current_tts': self.current_tts,
            'recognition_available': self.recognizer is not None
        }
    
    def cleanup(self):
        """Cleanup voice interface resources"""
        try:
            if 'edgetts' in self.tts_engines:
                self.tts_engines['edgetts'].cleanup()
                cleanup_edge_tts()
            
            if 'pyttsx3' in self.tts_engines:
                self.tts_engines['pyttsx3'].stop()
            
            if 'gtts' in self.tts_engines and GTTS_AVAILABLE:
                pygame.mixer.quit()
                
            log_info("Voice interface cleanup completed")
            
        except Exception as e:
            log_error("Voice interface cleanup failed", error=e)

# Global instance with lazy initialization
_voice_interface = None
_voice_lock = threading.Lock()

def get_voice_interface() -> RobustVoiceInterface:
    """Get global voice interface instance (singleton pattern)"""
    global _voice_interface
    
    if _voice_interface is None:
        with _voice_lock:
            if _voice_interface is None:
                _voice_interface = RobustVoiceInterface()
    
    return _voice_interface

# Convenience functions
def speak(text: str) -> bool:
    """Convenience function to speak text"""
    return get_voice_interface().speak_text(text)

def listen(timeout: int = 10) -> Optional[str]:
    """Convenience function to listen for speech"""
    return get_voice_interface().listen_for_speech(timeout=timeout)

def is_voice_available() -> bool:
    """Check if voice functionality is available"""
    return get_voice_interface().is_available()