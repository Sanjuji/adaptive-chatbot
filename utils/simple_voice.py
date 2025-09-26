#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Voice Interface - Direct EdgeTTS + Basic Speech Recognition
Sirf EdgeTTS use karte hain with simple speech recognition.
"""

import asyncio
import edge_tts
import pygame
import io
import speech_recognition as sr
import threading
import time
import atexit
from typing import Optional
from utils.logger import log_info, log_error, log_warning

class SimpleVoiceInterface:
    """Simple voice interface with EdgeTTS and basic speech recognition"""
    
    def __init__(self):
        self.voice = "hi-IN-MadhurNeural"  # Hindi male voice
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self._pygame_initialized = False
        self._setup_audio()
        # Register cleanup on exit
        atexit.register(self.cleanup)
    
    def _setup_audio(self):
        """Setup audio components with proper error handling"""
        try:
            # Initialize pygame for audio playback (avoid double init)
            if not pygame.mixer.get_init():
                pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
                pygame.mixer.init()
                self._pygame_initialized = True
                log_info("✅ Audio output initialized")
            else:
                log_info("✅ Audio output already initialized")
            
            # Setup microphone with better error handling
            try:
                # Get available microphones
                mic_list = sr.Microphone.list_microphone_names()
                if not mic_list:
                    raise Exception("No microphones found")
                    
                self.microphone = sr.Microphone()
                
                # Optimize recognizer settings
                self.recognizer.energy_threshold = 300
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.pause_threshold = 0.8
                
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                log_info(f"✅ Microphone initialized ({len(mic_list)} devices available)")
            except Exception as e:
                log_warning(f"Microphone setup issue: {e}")
                self.microphone = None
                
        except Exception as e:
            log_error(f"Audio setup failed: {e}")
            self._pygame_initialized = False
    
    def speak(self, text: str) -> bool:
        """Speak text using EdgeTTS with proper resource management"""
        if not text or not text.strip():
            return False
            
        if not self._pygame_initialized:
            log_warning("Audio not initialized, cannot speak")
            return False
        
        try:
            log_info(f"🔊 Speaking: {text[:50]}...")
            
            # Use advanced event loop manager for proper async handling
            from utils.advanced_event_loop_manager import get_loop_manager
            from utils.advanced_circuit_breaker import circuit_breaker, get_circuit_breaker
            
            loop_manager = get_loop_manager()
            audio_data = loop_manager.run_async_safely(
                self._generate_speech(text), timeout=30
            )
            
            if audio_data and len(audio_data) > 0:
                # Stop any current music first
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                    time.sleep(0.1)
                
                # Play audio using pygame
                audio_buffer = io.BytesIO(audio_data)
                pygame.mixer.music.load(audio_buffer)
                pygame.mixer.music.play()
                
                # Wait for playback to complete with timeout
                max_wait = 60  # 60 second timeout
                waited = 0
                while pygame.mixer.music.get_busy() and waited < max_wait:
                    time.sleep(0.1)
                    waited += 0.1
                
                if waited >= max_wait:
                    pygame.mixer.music.stop()
                    log_warning("Speech playback timeout")
                
                log_info("✅ Speech completed")
                return True
            else:
                log_error("Failed to generate speech or empty audio")
                return False
                
        except Exception as e:
            log_error(f"Speech generation failed: {e}")
            # Try to stop any stuck audio
            try:
                pygame.mixer.music.stop()
            except:
                pass
            return False
    
    async def _generate_speech(self, text: str) -> Optional[bytes]:
        """Generate speech using EdgeTTS"""
        try:
            # Create EdgeTTS communication
            communicate = edge_tts.Communicate(text, self.voice)
            
            # Generate audio data
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            return audio_data
            
        except Exception as e:
            log_error(f"EdgeTTS generation failed: {e}")
            return None
    
    def listen(self, timeout: int = 10) -> Optional[str]:
        """Listen for speech and return recognized text"""
        if not self.microphone:
            log_warning("Microphone not available")
            return None
        
        try:
            log_info(f"🎤 Listening... (timeout: {timeout}s)")
            
            with self.microphone as source:
                # Listen for audio with timeout
                try:
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                except sr.WaitTimeoutError:
                    log_warning("Listening timeout")
                    return None
            
            # Try recognition with different engines
            recognition_methods = [
                ("Google (hi-IN)", lambda: self.recognizer.recognize_google(audio, language="hi-IN")),
                ("Google (en-IN)", lambda: self.recognizer.recognize_google(audio, language="en-IN")),
                ("Google (en-US)", lambda: self.recognizer.recognize_google(audio, language="en-US"))
            ]
            
            for method_name, method in recognition_methods:
                try:
                    result = method()
                    if result and result.strip():
                        log_info(f"✅ Recognized ({method_name}): {result}")
                        return result.strip()
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    log_warning(f"{method_name} request failed: {e}")
                    continue
            
            log_warning("Speech recognition failed - could not understand audio")
            return None
            
        except Exception as e:
            log_error(f"Speech recognition error: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if voice interface is available"""
        return self.microphone is not None and self._pygame_initialized
    
    def cleanup(self):
        """Cleanup resources properly"""
        try:
            log_info("Cleaning up voice interface...")
            
            # Stop any playing audio
            if self._pygame_initialized:
                try:
                    pygame.mixer.music.stop()
                    pygame.mixer.quit()
                    log_info("✅ Audio resources cleaned up")
                except Exception as e:
                    log_warning(f"Audio cleanup issue: {e}")
            
            # Clear microphone
            self.microphone = None
            self._pygame_initialized = False
            
            log_info("✅ Voice interface cleanup completed")
            
        except Exception as e:
            log_error(f"Voice cleanup error: {e}")

# Global instance
_voice_interface = None

def get_simple_voice():
    """Get singleton voice interface"""
    global _voice_interface
    if _voice_interface is None:
        _voice_interface = SimpleVoiceInterface()
    return _voice_interface

def speak_simple(text: str) -> bool:
    """Simple speak function"""
    return get_simple_voice().speak(text)

def listen_simple(timeout: int = 10) -> Optional[str]:
    """Simple listen function"""
    return get_simple_voice().listen(timeout)

def is_voice_ready() -> bool:
    """Check if voice is ready"""
    return get_simple_voice().is_available()