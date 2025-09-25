"""
Voice Interface for Adaptive Chatbot - Speech Recognition and Text-to-Speech
"""

import speech_recognition as sr
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import threading
import queue
import time
import tempfile
import os
from core.edge_tts_engine import get_edge_tts_engine, cleanup_edge_tts


class VoiceInterface:
    """
    Handles speech recognition and text-to-speech for the chatbot.
    Supports both local TTS (pyttsx3) and Google TTS (gTTS) for better language support.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the voice interface with configuration."""
        self.config = config or {}
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        
        # Initialize microphone with error handling
        try:
            # Try to use Realtek microphone first (index 13 from our test)
            self.microphone = sr.Microphone(device_index=13)  # Realtek HD Audio Mic
            print("🎤 Using Realtek microphone")
        except:
            try:
                # Fallback to default microphone
                self.microphone = sr.Microphone()
                print("🎤 Using default microphone")
            except Exception as e:
                logging.error(f"Failed to initialize any microphone: {e}")
                raise
        
        # Initialize EdgeTTS engine for realistic speech
        self.edge_tts = get_edge_tts_engine()
        
        # Voice settings
        self.language = self.config.get('language', 'hi-IN')  # Hindi-India for recognition
        self.tts_voice = self.config.get('tts_voice', 'english_male_warm')  # Default EdgeTTS voice
        self.speech_rate = self.config.get('speech_rate', 180)
        self.voice_volume = self.config.get('voice_volume', 0.8)
        
        # Audio settings
        self.energy_threshold = self.config.get('energy_threshold', 200)  # Lower for better sensitivity
        self.pause_threshold = self.config.get('pause_threshold', 0.5)     # Faster response
        self.timeout = self.config.get('timeout', 3)                      # Shorter timeout
        self.phrase_time_limit = self.config.get('phrase_time_limit', 8)   # Reasonable phrase limit
        
        # Configure EdgeTTS voice
        self.edge_tts.set_voice(self.tts_voice)
        self.edge_tts.set_volume(self.voice_volume)
        
        # Adjust for ambient noise
        self._calibrate_microphone()
        
        logging.info("Voice interface initialized with realistic EdgeTTS")
    
    
    
    def _calibrate_microphone(self) -> None:
        """Calibrate microphone for ambient noise."""
        try:
            print("🎤 Calibrating microphone... Please stay quiet for a moment...")
            
            # Use direct microphone calibration without context manager
            self.recognizer.adjust_for_ambient_noise(self.microphone, duration=1)
            
            # Set better recognition settings
            self.recognizer.energy_threshold = max(100, min(self.energy_threshold, self.recognizer.energy_threshold))
            self.recognizer.pause_threshold = self.pause_threshold
            self.recognizer.dynamic_energy_threshold = True
            
            print(f"✅ Microphone ready! Energy threshold: {self.recognizer.energy_threshold}")
            logging.info(f"Microphone calibrated. Energy threshold: {self.recognizer.energy_threshold}")
        except Exception as e:
            # Set manual defaults if calibration fails
            self.recognizer.energy_threshold = 150
            self.recognizer.pause_threshold = 0.5
            self.recognizer.dynamic_energy_threshold = True
            print(f"⚠️ Calibration failed, using manual settings. Energy: {self.recognizer.energy_threshold}")
            logging.error(f"Error calibrating microphone: {e}")
    
    def listen_for_speech(self, prompt: str = "Listening...") -> Optional[str]:
        """
        Listen for speech input and convert to text.
        
        Args:
            prompt: Message to display while listening
            
        Returns:
            Recognized text or None if failed
        """
        try:
            print(f"\n🎤 {prompt}")
            
            with self.microphone as source:
                # Listen for audio
                audio = self.recognizer.listen(
                    source, 
                    timeout=self.timeout,
                    phrase_time_limit=self.phrase_time_limit
                )
            
            print("🔄 Processing speech...")
            
            # Try to recognize speech with multiple languages
            languages_to_try = [self.language, 'en-IN', 'hi-IN', 'en-US', 'en']
            
            for lang in languages_to_try:
                try:
                    print(f"🔍 Trying recognition with language: {lang}")
                    text = self.recognizer.recognize_google(audio, language=lang)
                    if text.strip():
                        print(f"✅ Successfully recognized ({lang}): '{text}'")
                        logging.info(f"Recognized ({lang}): {text}")
                        return text.strip()
                except sr.UnknownValueError:
                    print(f"⚠️ No speech understood with {lang}")
                    continue
                except sr.RequestError as e:
                    print(f"❌ Network error with {lang}: {e}")
                    logging.error(f"Error with {lang}: {e}")
                    continue
            
            # If all languages fail, try without language specification
            try:
                text = self.recognizer.recognize_google(audio)
                if text.strip():
                    logging.info(f"Recognized (auto): {text}")
                    return text.strip()
            except:
                pass
                
            print("❌ Could not understand speech. Please try again.")
            return None
            
        except sr.WaitTimeoutError:
            print("⏰ Timeout - No speech detected")
            return None
        except Exception as e:
            logging.error(f"Error in speech recognition: {e}")
            print(f"❌ Error: {e}")
            return None
    
    def speak_text(self, text: str) -> bool:
        """
        Convert text to speech and play it using realistic EdgeTTS.
        
        Args:
            text: Text to speak
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not text.strip():
                return False
            
            print(f"🔊 Speaking: {text}")
            
            # Use EdgeTTS for realistic human-like speech
            return self.edge_tts.speak(text, blocking=True)
                
        except Exception as e:
            logging.error(f"Error in EdgeTTS text-to-speech: {e}")
            return False
    
    
    def get_voice_input(self, prompt: str = "Say something...") -> Optional[str]:
        """
        Get voice input with retry mechanism.
        
        Args:
            prompt: Prompt to display
            
        Returns:
            Recognized text or None
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            text = self.listen_for_speech(prompt)
            if text:
                return text
            
            retry_count += 1
            if retry_count < max_retries:
                self.speak_text("Mujhe samajh nahi aaya. Kripaya dobara kahiye.")
                time.sleep(1)
        
        return None
    
    def get_available_voices(self) -> dict:
        """Get list of available EdgeTTS voices."""
        try:
            return self.edge_tts.get_available_voices()
        except Exception as e:
            logging.error(f"Error getting EdgeTTS voices: {e}")
            return {}
    
    def set_voice(self, voice_name: str) -> bool:
        """Set EdgeTTS voice by name."""
        try:
            success = self.edge_tts.set_voice(voice_name)
            if success:
                self.tts_voice = voice_name
                logging.info(f"EdgeTTS voice set to: {voice_name}")
            return success
        except Exception as e:
            logging.error(f"Error setting EdgeTTS voice: {e}")
            return False
    
    def set_volume(self, volume: float) -> bool:
        """Set TTS volume (0.0 to 1.0)."""
        try:
            self.edge_tts.set_volume(volume)
            self.voice_volume = volume
            logging.info(f"EdgeTTS volume set to: {volume}")
            return True
        except Exception as e:
            logging.error(f"Error setting EdgeTTS volume: {e}")
            return False
    
    def test_voice_interface(self) -> bool:
        """Test the voice interface with EdgeTTS."""
        try:
            print("🧪 Testing realistic voice interface...")
            
            # Test EdgeTTS
            test_message = "Namaste! Main aapki realistic voice assistant hun. Hello! I can hear your voice with natural human-like speech."
            if not self.speak_text(test_message):
                print("❌ EdgeTTS test failed")
                return False
            
            print("✅ EdgeTTS realistic speech test passed")
            
            # Test speech recognition
            print("Now testing speech recognition...")
            self.speak_text("Kripaya kuch boliye. Please say something with my new realistic voice.")
            
            text = self.listen_for_speech("Testing speech recognition...")
            if text:
                print(f"✅ Speech recognition test passed. Heard: {text}")
                self.speak_text(f"Aapne kaha: {text}. Kaisi lagi meri nayi realistic awaaz?")
                return True
            else:
                print("❌ Speech recognition test failed")
                return False
                
        except Exception as e:
            logging.error(f"Error testing voice interface: {e}")
            print(f"❌ Test failed: {e}")
            return False
    
    def cleanup(self) -> None:
        """Cleanup resources."""
        try:
            if self.edge_tts:
                self.edge_tts.cleanup()
            cleanup_edge_tts()  # Clean up global instance
            logging.info("Voice interface with EdgeTTS cleaned up")
        except Exception as e:
            logging.error(f"Error cleaning up voice interface: {e}")


class VoiceChatSession:
    """
    Manages a voice chat session with the chatbot.
    """
    
    def __init__(self, voice_interface: VoiceInterface, chatbot):
        """Initialize voice chat session."""
        self.voice_interface = voice_interface
        self.chatbot = chatbot
        self.is_active = False
        self.learning_manager = None
    
    def start_session(self, learning_manager=None) -> None:
        """Start voice chat session."""
        self.is_active = True
        self.learning_manager = learning_manager
        
        # Welcome message in Hinglish
        welcome_msg = "Namaste! Main aapki realistic voice assistant hun. Aap mujhse baat kar sakte hain ya mujhe nayi cheezein sikha sakte hain. 'Bye' kahkar chat band kar sakte hain."
        self.voice_interface.speak_text(welcome_msg)
        
        while self.is_active:
            try:
                # Get voice input
                user_input = self.voice_interface.get_voice_input("आप क्या कहना चाहते हैं?")
                
                if not user_input:
                    continue
                
                # Check for exit commands
                if any(word in user_input.lower() for word in ['bye', 'baay', 'exit', 'quit', 'goodbye']):
                    self.voice_interface.speak_text("Alvida! Phir milenge. Dhanyawad realistic voice experience ke liye!")
                    self.is_active = False
                    break
                
                # Check for teaching commands
                if self._is_teaching_command(user_input):
                    self._handle_teaching(user_input)
                else:
                    # Process with chatbot
                    response = self.chatbot.process_message(user_input)
                    
                    # Speak response
                    self.voice_interface.speak_text(response)
                
            except KeyboardInterrupt:
                self.voice_interface.speak_text("Voice chat बंद हो रहा है।")
                self.is_active = False
                break
            except Exception as e:
                logging.error(f"Error in voice chat session: {e}")
                self.voice_interface.speak_text("कुछ गलती हुई है। कृपया दोबारा कोशिश करें।")
    
    def _is_teaching_command(self, user_input: str) -> bool:
        """Check if user input is a teaching command"""
        lower_input = user_input.lower()
        
        # Teaching keywords in different languages
        teaching_keywords = [
            'teach', 'टीच', 'सिखाओ', 'सिखाना', 'sikhaao', 'sikhana',
            'mujhe sikhana hai', 'teach me', 'मुझे सिखाना है'
        ]
        
        for keyword in teaching_keywords:
            if keyword in lower_input:
                return True
        
        return False
    
    def _handle_teaching(self, user_input: str) -> None:
        """Handle teaching commands"""
        if not self.learning_manager:
            self.voice_interface.speak_text("Sorry, teaching mode available नहीं है।")
            return
        
        try:
            # Extract question and answer from voice input
            question, answer = self._parse_teaching_input(user_input)
            
            if question and answer:
                # Teach the chatbot
                success = self.learning_manager.teach_chatbot(
                    question, answer, "voice_taught", self.chatbot.current_domain
                )
                
                if success:
                    success_msg = f"✅ Perfect! मैंने सीख लिया। अब जब आप पूछेंगे '{question}' तो मैं जानूंगा।"
                    self.voice_interface.speak_text(success_msg)
                    
                    # Test immediately
                    test_response = self.chatbot.process_message(question)
                    self.voice_interface.speak_text(f"देखिए: {test_response}")
                else:
                    self.voice_interface.speak_text("Sorry, मैं सीख नहीं पाया। कृपया फिर कोशिश करें।")
            else:
                self.voice_interface.speak_text("मुझे समझ नहीं आया कि क्या सिखाना है। कृपया साफ़ बोलिए।")
                
        except Exception as e:
            logging.error(f"Error in teaching: {e}")
            self.voice_interface.speak_text("Teaching में कुछ गलती हुई। कृपया फिर कोशिश करें।")
    
    def _parse_teaching_input(self, user_input: str) -> tuple:
        """Parse teaching input to extract question and answer"""
        import re
        
        # Transliterate common Hindi words
        transliterate_map = {
            'स्विच': 'switch', 'की': 'ki', 'प्राइस': 'price', 'कितनी': 'kitni',
            'है': 'hai', 'क्या': 'kya', 'फैन': 'fan', 'वायर': 'wire',
            'का': 'ka', 'रेट': 'rate', 'बल्ब': 'bulb', 'वारंटी': 'warranty',
            'सर्विस': 'service', 'होता': 'hota', 'मिलता': 'milta',
            'रुपये': 'rupees', 'में': 'mein', 'आता': 'aata'
        }
        
        text = user_input
        for hindi, english in transliterate_map.items():
            text = text.replace(hindi, english)
        
        # Different patterns for teaching
        patterns = [
            # "teach switch ki price switch 25 rupees mein milta hai"
            r'(?:teach|टीच|सिखाओ)\s+(.+?)\s+(.+?)\s+(?:hai|है|hota|होता|milta|मिलता)',
            # "mujhe sikhana hai switch ki price 25 rupees"
            r'(?:mujhe sikhana hai|मुझे सिखाना है)\s+(.+?)\s+(.+)',
            # "teach me switch ki price ye 25 rupees hai"
            r'(?:teach me|टीच मी)\s+(.+?)\s+(?:ye|यह|यह है|hai)\s+(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and len(match.groups()) >= 2:
                topic_part = match.group(1).strip()
                answer_part = match.group(2).strip()
                
                # Create a proper question format
                if 'price' in topic_part or 'प्राइस' in topic_part:
                    question = f"{topic_part} kitni hai"
                elif 'kya' in topic_part or 'क्या' in topic_part:
                    question = topic_part
                else:
                    question = f"{topic_part} kya hai"
                
                return question, answer_part
        
        return None, None
    
    def stop_session(self) -> None:
        """Stop voice chat session."""
        self.is_active = False
