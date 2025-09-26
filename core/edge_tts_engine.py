"""
EdgeTTS Voice Engine - Realistic Human-like Text-to-Speech
Provides ElevenLabs quality voices for free using Microsoft EdgeTTS
"""

import asyncio
import edge_tts
import pygame
import tempfile
import os
import logging
from typing import Optional, Dict, Any
import threading
from concurrent.futures import ThreadPoolExecutor
import time
from core.hinglish_voice_processor import hinglish_processor

# Optional streaming playback via PyAudio
try:
    import pyaudio  # type: ignore
    _HAVE_PYAUDIO = True
except Exception:
    _HAVE_PYAUDIO = False

logger = logging.getLogger(__name__)

class EdgeTTSEngine:
    """High-quality realistic text-to-speech using Microsoft EdgeTTS"""
    
    def __init__(self):
        self.available_voices = {
            'english_male': {
                'voice': 'en-US-BrianNeural',  # Sincere, Calm, Approachable
                'rate': '+0%',
                'pitch': '+0Hz'
            },
            'english_male_warm': {
                'voice': 'en-US-AndrewNeural',  # Confident, Authentic, Warm
                'rate': '+10%',
                'pitch': '+0Hz'
            },
            'multilingual_warm': {
                'voice': 'en-US-AndrewMultilingualNeural',  # Multilingual - Best for Devanagari
                'rate': '+5%',
                'pitch': '+0Hz'
            },
            'multilingual_deep': {
                'voice': 'en-US-AdamMultilingualNeural',  # Warm, engaging, deep
                'rate': '+0%',
                'pitch': '+0Hz'
            },
            'multilingual_smooth': {
                'voice': 'en-US-DavisMultilingualNeural',  # Soothing, calm, smooth
                'rate': '+0%',
                'pitch': '+0Hz'
            },
            'hindi_male': {
                'voice': 'hi-IN-MadhurNeural',  # Natural Hindi voice
                'rate': '+0%',
                'pitch': '+0Hz'
            },
            'hindi_male_warm': {
                'voice': 'hi-IN-ArjunNeural',  # Alternative Hindi voice
                'rate': '+5%',
                'pitch': '+0Hz'
            }
        }
        
        self.current_voice = 'multilingual_warm'  # Default to multilingual for Devanagari support
        self.volume = 0.8
        self.temp_dir = tempfile.gettempdir()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.streaming_enabled = True  # Prefer streaming when PyAudio is available
        
        # Initialize pygame mixer for fallback audio playback
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            logger.info("EdgeTTS: Pygame mixer initialized (fallback player)")
        except Exception as e:
            logger.error(f"EdgeTTS: Failed to initialize pygame mixer: {e}")
            # Do not raise; streaming path might still work with PyAudio
    
    def set_voice(self, voice_name: str) -> bool:
        """Set the current voice"""
        if voice_name in self.available_voices:
            self.current_voice = voice_name
            logger.info(f"EdgeTTS: Voice set to {voice_name} ({self.available_voices[voice_name]['voice']})")
            return True
        else:
            logger.warning(f"EdgeTTS: Voice '{voice_name}' not available")
            return False
    
    def set_volume(self, volume: float) -> None:
        """Set volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
        logger.info(f"EdgeTTS: Volume set to {self.volume}")
    
    async def _generate_and_play_optimized(self, text: str, output_file: str) -> bool:
        """Optimized speech generation and playback in one async function"""
        success = await self._generate_speech_async(text, output_file)
        if success:
            success = self._play_audio_file(output_file)
        return success
    
    async def _generate_speech_async(self, text: str, output_file: str) -> bool:
        """Generate speech asynchronously using EdgeTTS (file-based fallback)."""
        try:
            voice_config = self.available_voices[self.current_voice]
            
            # CRITICAL FIX: Clean text to ensure no technical parameters are spoken
            import re
            clean_text = text.strip()
            
            # Remove technical parameters that might leak into speech
            technical_artifacts = [
                'rate="', 'pitch="', 'prosody', 'speak version', 'xmlns', 'break time',
                'pitch rate', 'speech rate', 'confidence', 'processing time'
            ]
            
            for artifact in technical_artifacts:
                if artifact in clean_text.lower():
                    # Remove sentences containing technical parameters
                    sentences = clean_text.split('.')
                    clean_sentences = [s for s in sentences if artifact not in s.lower()]
                    clean_text = '. '.join(clean_sentences).strip()
            
            # Remove any XML/SSML tags that might have leaked
            clean_text = re.sub(r'<[^>]*>', '', clean_text)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            
            if not clean_text:
                clean_text = "Sorry, I couldn't process that properly."
            
            # Create EdgeTTS communicate object with clean text
            communicate = edge_tts.Communicate(
                text=clean_text,
                voice=voice_config['voice']
            )
            
            # Save to file (mp3)
            await communicate.save(output_file)
            
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                logger.info(f"EdgeTTS: Speech generated successfully: {len(text)} characters")
                return True
            else:
                logger.error("EdgeTTS: Generated file is empty or doesn't exist")
                return False
                
        except Exception as e:
            logger.error(f"EdgeTTS: Speech generation failed: {e}")
            return False
    
    def _play_audio_file(self, file_path: str) -> bool:
        """Play audio file using pygame"""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            return True
            
        except Exception as e:
            logger.error(f"EdgeTTS: Audio playback failed: {e}")
            return False
    
    async def _stream_pcm_async(self, text: str) -> bool:
        """Stream PCM audio via PyAudio while synthesizing with EdgeTTS."""
        if not _HAVE_PYAUDIO:
            return False
        try:
            voice_config = self.available_voices[self.current_voice]
            communicate = edge_tts.Communicate(text=text, voice=voice_config['voice'])
            pa = pyaudio.PyAudio()
            stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True, frames_per_buffer=1024)
            try:
                async for chunk in communicate.stream(output_format="raw-16khz-16bit-mono-pcm"):
                    if chunk["type"].lower() == "audio":
                        data = chunk.get("data", b"")
                        if data:
                            stream.write(data)
                return True
            finally:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception:
                    pass
                pa.terminate()
        except Exception as e:
            logger.error(f"EdgeTTS: Streaming synthesis failed: {e}")
            return False

    def speak(self, text: str, blocking: bool = True, auto_voice_select: bool = True) -> bool:
        """
        Speak the given text using realistic EdgeTTS voice with intelligent processing
        
        Args:
            text: Text to speak
            blocking: If True, wait for speech to complete
            auto_voice_select: If True, automatically select best voice for content
            
        Returns:
            bool: True if successful
        """
        if not text or not text.strip():
            return False
        
        try:
            # Process text for optimal pronunciation
            processed_text, recommended_voice = hinglish_processor.preprocess_text_for_tts(text)
            
            # Use recommended voice if auto-selection is enabled
            if auto_voice_select and recommended_voice in self.available_voices:
                original_voice = self.current_voice
                self.set_voice(recommended_voice)
                logger.info(f"EdgeTTS: Auto-selected voice '{recommended_voice}' for content")
            else:
                original_voice = None
            
            # Create unique temp file for this speech
            temp_file = os.path.join(self.temp_dir, f"edgetts_{int(time.time() * 1000)}.mp3")
            
            def speech_task() -> bool:
                try:
                    # Optimized async handling with proper error recovery
                    loop = None
                    try:
                        loop = asyncio.get_running_loop()
                        # Running in async context - create future
                        future = asyncio.run_coroutine_threadsafe(
                            self._generate_and_play_optimized(processed_text, temp_file), loop
                        )
                        success = future.result(timeout=30)
                    except RuntimeError:
                        # No running loop - create new one
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            success = loop.run_until_complete(
                                self._generate_and_play_optimized(processed_text, temp_file)
                            )
                        finally:
                            loop.close()
                    
                    # Cleanup temp file
                    try:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                    except OSError as e:
                        logger.warning(f"Failed to cleanup temp file: {e}")
                    
                    # Restore original voice if changed
                    if original_voice:
                        self.set_voice(original_voice)
                    
                    return success
                    
                except asyncio.TimeoutError:
                    logger.error("EdgeTTS: Speech generation timed out")
                    if original_voice:
                        self.set_voice(original_voice)
                    return False
                except Exception as e:
                    logger.error(f"EdgeTTS: Speech task failed: {e}")
                    if original_voice:
                        self.set_voice(original_voice)
                    return False
            
            # Prefer streaming path when possible
            if self.streaming_enabled and _HAVE_PYAUDIO:
                def stream_task() -> bool:
                    try:
                        # Handle async context
                        try:
                            loop = asyncio.get_running_loop()
                            fut = asyncio.run_coroutine_threadsafe(self._stream_pcm_async(processed_text), loop)
                            return fut.result(timeout=30)
                        except RuntimeError:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                return loop.run_until_complete(self._stream_pcm_async(processed_text))
                            finally:
                                loop.close()
                    except Exception as e:
                        logger.error(f"EdgeTTS: Streaming task failed, falling back: {e}")
                        return False
                # Try streaming, fallback to file if it fails
                ok = stream_task() if blocking else self.executor.submit(stream_task) or True
                if ok:
                    return True
                # fallthrough to file-based path
            
            if blocking:
                return speech_task()
            else:
                # Run in background thread
                self.executor.submit(speech_task)
                return True
                
        except Exception as e:
            logger.error(f"EdgeTTS: Speak method failed: {e}")
            return False
    
    def stop(self) -> None:
        """Stop current speech"""
        try:
            pygame.mixer.music.stop()
            logger.info("EdgeTTS: Speech stopped")
        except Exception as e:
            logger.warning(f"EdgeTTS: Stop failed: {e}")
    
    def is_speaking(self) -> bool:
        """Check if currently speaking"""
        try:
            return pygame.mixer.music.get_busy()
        except:
            return False
    
    def get_available_voices(self) -> Dict[str, str]:
        """Get list of available voices with descriptions"""
        return {
            name: f"{config['voice']} - Rate: {config['rate']}, Pitch: {config['pitch']}"
            for name, config in self.available_voices.items()
        }
    
    def test_voice(self, voice_name: str = None) -> bool:
        """Test a voice by speaking sample text"""
        original_voice = self.current_voice
        
        if voice_name and voice_name in self.available_voices:
            self.set_voice(voice_name)
        
        test_text = "Namaste! Main aapka naya realistic voice assistant hu. Kya aapko meri awaaz achhi lag rahi hai?"
        
        success = self.speak(test_text, blocking=True)
        
        if voice_name:
            self.set_voice(original_voice)  # Restore original voice
            
        return success
    
    def cleanup(self) -> None:
        """Clean up resources"""
        try:
            self.stop()
            self.executor.shutdown(wait=False)
            pygame.mixer.quit()
            logger.info("EdgeTTS: Cleanup completed")
        except Exception as e:
            logger.warning(f"EdgeTTS: Cleanup warning: {e}")

# Global instance for easy access
edge_tts_engine = None

def get_edge_tts_engine() -> EdgeTTSEngine:
    """Get or create EdgeTTS engine instance"""
    global edge_tts_engine
    if edge_tts_engine is None:
        edge_tts_engine = EdgeTTSEngine()
    return edge_tts_engine

def cleanup_edge_tts():
    """Clean up global EdgeTTS engine"""
    global edge_tts_engine
    if edge_tts_engine is not None:
        edge_tts_engine.cleanup()
        edge_tts_engine = None