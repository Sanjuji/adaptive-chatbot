#!/usr/bin/env python3
"""
Adaptive Chatbot - Main Integration Script
Brings together all components for a complete multilingual conversational AI experience
"""

import asyncio
import threading
import time
import sys
import os
from typing import Dict, Any, Optional
import numpy as np
from datetime import datetime

# Import all our custom modules
try:
    from multilingual_edgetts_integration import get_multilingual_tts_system
    from advanced_conversation_manager import get_conversation_manager
    from enhanced_language_detection import get_language_detector
    from free_ai_models_integration import get_ai_models_system
    from voice_tone_style_adaptation import get_voice_adaptation_system
    from enhanced_ui_experience import get_ui_system
    from advanced_debugger_tracker import get_debug_tracker, track_voice_interaction
    from logger import log_info, log_error, log_warning
except ImportError as e:
    print(f"Failed to import required modules: {e}")
    print("Please ensure all required Python packages are installed.")
    sys.exit(1)

class AdaptiveChatbot:
    """
    Main Adaptive Chatbot system that integrates all components
    """
    
    def __init__(self):
        """Initialize the adaptive chatbot system"""
        log_info("🚀 Starting Adaptive Chatbot System...")
        
        # Initialize all subsystems
        self.tts_system = None
        self.conversation_manager = None
        self.language_detector = None
        self.ai_models_system = None
        self.voice_adaptation_system = None
        self.ui_system = None
        self.debug_tracker = None
        
        # System state
        self.is_running = False
        self.current_session_id = None
        self.current_user_id = "default_user"
        
        # Audio processing state
        self.is_listening = False
        self.is_speaking = False
        self.audio_queue = asyncio.Queue()
        
        # Initialize subsystems
        self._initialize_systems()
        
        log_info("✅ Adaptive Chatbot System initialized successfully!")
    
    def _initialize_systems(self):
        """Initialize all subsystem components"""
        
        try:
            # Initialize TTS system
            log_info("🔊 Initializing Multilingual TTS System...")
            self.tts_system = get_multilingual_tts_system()
            
            # Initialize conversation manager
            log_info("💬 Initializing Conversation Manager...")
            self.conversation_manager = get_conversation_manager()
            
            # Initialize language detector
            log_info("🌐 Initializing Language Detector...")
            self.language_detector = get_language_detector()
            
            # Initialize AI models system
            log_info("🤖 Initializing AI Models System...")
            self.ai_models_system = get_ai_models_system()
            
            # Initialize voice adaptation system
            log_info("🎭 Initializing Voice Adaptation System...")
            self.voice_adaptation_system = get_voice_adaptation_system()
            
            # Initialize UI system
            log_info("🎨 Initializing UI System...")
            self.ui_system = get_ui_system()
            
            # Initialize Debug Tracker
            log_info("🔍 Initializing Advanced Debug Tracker...")
            self.debug_tracker = get_debug_tracker()
            
            # Connect UI callbacks
            self._setup_ui_callbacks()
            
            # Create initial conversation session
            self.current_session_id = self.conversation_manager.start_conversation(self.current_user_id)
            
            log_info("🔗 All systems connected successfully!")
            
        except Exception as e:
            log_error(f"Failed to initialize systems: {e}")
            raise
    
    def _setup_ui_callbacks(self):
        """Set up callbacks between UI and backend systems"""
        
        # Register UI event callbacks
        self.ui_system.register_callback('start_listening', self._start_listening)
        self.ui_system.register_callback('stop_listening', self._stop_listening)
        self.ui_system.register_callback('toggle_mute', self._toggle_mute)
        
        log_info("🔗 UI callbacks registered")
    
    async def process_user_input(self, text: str, detected_language: str = None) -> str:
        """
        Process user input through the complete pipeline with comprehensive debugging
        """
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            # Step 1: Detect language if not provided
            if not detected_language:
                lang_result = await self.language_detector.detect_language_advanced(text)
                detected_language = lang_result.detected_language
                confidence = lang_result.confidence
                
                # Track potential language detection issues
                if confidence < 0.7:
                    warnings.append(f"Low language detection confidence: {confidence:.2f}")
            else:
                confidence = 1.0
            
            # Update UI with detected language
            self.ui_system.set_language_detected(detected_language, confidence)
            
            # Add user message to UI
            self.ui_system.add_conversation_message(
                speaker="user",
                text=text,
                language=detected_language,
                confidence=confidence
            )
            
            # Step 2: Get conversation context
            context = self.conversation_manager.get_conversation_context(self.current_session_id)
            
            # Step 3: Generate AI response
            self.ui_system.update_status("Generating response...", "info")
            
            # Simplify context for AI model - just pass the text
            ai_response = await self.ai_models_system.generate_conversation_response(
                text
            )
            
            response_text = ai_response.text if ai_response else 'I apologize, but I could not generate a response.'
            response_language = detected_language  # Keep original language for response
            
            # Step 5: Adapt voice style based on context
            voice_context = {
                "intent": "general",
                "sentiment": "neutral",
                "confidence": ai_response.confidence if ai_response else 0.5,
                "detected_language": response_language
            }
            
            voice_adaptation_result = await self.voice_adaptation_system.adapt_voice_style(
                response_text,
                voice_context,
                user_id=self.current_user_id,
                session_id=self.current_session_id
            )
            
            # Step 6: Add conversation turn to history
            processing_time = time.time() - start_time
            
            self.conversation_manager.add_turn(
                session_id=self.current_session_id,
                user_input=text,  # Original user input
                system_response=response_text,
                metadata={
                    "detected_language": response_language,
                    "intent": "general",
                    "sentiment": "neutral",
                    "confidence": ai_response.confidence if ai_response else 0.5,
                    "topic": "general",
                    "voice_used": voice_adaptation_result.voice_profile.personality.value if hasattr(voice_adaptation_result.voice_profile, 'personality') else None,
                    "response_time": processing_time
                }
            )
            
            # Add to UI
            self.ui_system.add_conversation_message(
                speaker="bot",
                text=response_text,
                language=response_language,
                voice_profile=voice_adaptation_result.voice_profile.__dict__,
                processing_time=processing_time
            )
            
            # Step 7: Generate speech with adaptive voice
            self.ui_system.update_status("Generating speech...", "info")
            self.ui_system.set_speaking_status(True)
            
            # Clean and log the text being sent to speech synthesis (for debugging)
            import re
            clean_display_text = re.sub(r'<[^>]*>', '', response_text)  # Remove any XML/SSML
            clean_display_text = clean_display_text.strip()[:50]  # First 50 chars for logging
            log_info(f"🎙️ Generating speech: {clean_display_text}{'...' if len(response_text) > 50 else ''}")
            
            try:
                # Use voice system with adapted context
                voice_context = {
                    "emotional_state": voice_context.get("sentiment", "neutral"),
                    "intent": voice_context.get("intent", "general")
                }
                await self.tts_system.speak_with_auto_voice(
                    response_text,
                    response_language,
                    voice_context.get("emotional_state", "neutral"),
                    voice_context
                )
            except Exception as e:
                log_warning(f"Voice synthesis failed: {e}")
            
            self.ui_system.set_speaking_status(False)
            self.ui_system.update_status("Ready", "success")
            
            # CRITICAL: Track complete voice interaction with debugger
            tts_end_time = time.time()
            if processing_time > 10.0:
                warnings.append(f"Slow processing time: {processing_time:.2f}s")
            
            if not ai_response or not ai_response.text.strip():
                errors.append("Empty or no AI response generated")
            
            session_id = self.debug_tracker.track_voice_interaction(
                user_input=text,
                language_detected=detected_language,
                confidence=confidence,
                processing_start=start_time,
                response_text=response_text,
                errors=errors,
                warnings=warnings
            )
            
            log_info(f"💬 Processed conversation turn in {processing_time:.2f}s (Session: {session_id})")
            
            return response_text
            
        except Exception as e:
            log_error(f"Error processing user input: {e}")
            self.ui_system.update_status(f"Error: {str(e)}", "error")
            self.ui_system.set_speaking_status(False)
            
            # Fallback response
            fallback_response = "I apologize, but I encountered an error processing your request."
            
            if detected_language == 'hi':
                fallback_response = "मुझे खुशी है, लेकिन मुझे आपके अनुरोध को संसाधित करने में त्रुटि हुई।"
            elif detected_language == 'es':
                fallback_response = "Me disculpo, pero encontré un error al procesar su solicitud."
            elif detected_language == 'fr':
                fallback_response = "Je m'excuse, mais j'ai rencontré une erreur lors du traitement de votre demande."
            
            # Still try to speak the fallback
            try:
                await self.tts_system.speak_with_auto_voice(fallback_response, detected_language or 'en', "neutral")
            except:
                pass
            
            return fallback_response
    
    def _start_listening(self):
        """Start listening for voice input"""
        if not self.is_listening:
            self.is_listening = True
            self.ui_system.set_recording_status(True)
            self.ui_system.update_status("Listening...", "info")
            
            # Start voice input processing in a separate thread
            threading.Thread(target=self._voice_input_loop, daemon=True).start()
            
            log_info("🎤 Started listening for voice input")
    
    def _stop_listening(self):
        """Stop listening for voice input"""
        if self.is_listening:
            self.is_listening = False
            self.ui_system.set_recording_status(False)
            self.ui_system.update_status("Ready", "success")
            
            log_info("⏹️ Stopped listening for voice input")
    
    def _toggle_mute(self, is_muted: bool):
        """Toggle mute state"""
        if self.tts_system:
            # Set TTS system volume based on mute state
            volume = 0 if is_muted else self.ui_system.get_settings().get('volume', 70)
            # Note: TTS volume control would need to be implemented in the TTS system
            
        log_info(f"🔇 Audio {'muted' if is_muted else 'unmuted'}")
    
    def _voice_input_loop(self):
        """Voice input processing loop using real speech recognition"""
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            
            # Try to use default microphone
            with sr.Microphone() as source:
                # Adjust for ambient noise
                log_info("🎤 Adjusting for ambient noise... Please wait")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                log_info("🎤 Ready! Speak now...")
                
                while self.is_listening:
                    try:
                        # Listen for audio with timeout
                        audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
                        
                        # Show audio visualization while processing
                        audio_data = np.random.random(20) * 0.5
                        self.ui_system.update_audio_visualization(audio_data)
                        
                        # Try to recognize speech
                        try:
                            # Use Google Speech Recognition (free)
                            text = recognizer.recognize_google(audio)
                            log_info(f"🎤 Heard: {text}")
                            
                            if text.strip():
                                self._stop_listening()
                                
                                # Process the recognized speech
                                def process_async():
                                    loop = asyncio.new_event_loop()
                                    asyncio.set_event_loop(loop)
                                    try:
                                        loop.run_until_complete(self.process_user_input(text))
                                    finally:
                                        loop.close()
                                
                                threading.Thread(target=process_async, daemon=True).start()
                                break
                                
                        except sr.UnknownValueError:
                            # Could not understand audio
                            continue
                        except sr.RequestError as e:
                            log_error(f"Could not request results from Google Speech Recognition service: {e}")
                            break
                            
                    except sr.WaitTimeoutError:
                        # No speech detected, continue listening
                        if not self.is_listening:
                            break
                        continue
                        
        except ImportError:
            log_error("SpeechRecognition not available. Install with: pip install SpeechRecognition")
            self._stop_listening()
        except OSError as e:
            log_error(f"Microphone not available: {e}")
            self._stop_listening()
        except Exception as e:
            log_error(f"Voice input failed: {e}")
            self._stop_listening()
    
    async def run_async(self):
        """Run the chatbot system asynchronously"""
        self.is_running = True
        
        # Add welcome message
        welcome_messages = {
            'en': "Hello! I'm your adaptive assistant. I can help you in multiple languages. How may I assist you today?",
            'hi': "नमस्ते! मैं आपका अनुकूली सहायक हूँ। मैं कई भाषाओं में आपकी मदद कर सकता हूँ। आज मैं आपकी कैसे सहायता कर सकता हूँ?",
            'es': "¡Hola! Soy tu asistente adaptativo. Puedo ayudarte en múltiples idiomas. ¿Cómo puedo ayudarte hoy?",
            'fr': "Bonjour! Je suis votre assistant adaptatif. Je peux vous aider en plusieurs langues. Comment puis-je vous aider aujourd'hui?"
        }
        
        # Choose welcome message based on system locale or default to English
        welcome_text = welcome_messages.get('en')  # Default to English
        
        self.ui_system.add_conversation_message(
            speaker="bot",
            text=welcome_text,
            language="en",
            voice_profile={"personality": "friendly", "energy": 0.7}
        )
        
        # Welcome message speech disabled for better UX
        # User can enable this in settings if needed
        # try:
        #     await self.tts_system.speak_with_auto_voice(welcome_text, "en", "neutral")
        # except Exception as e:
        #     log_warning(f"Could not speak welcome message: {e}")
        
        log_info("🎉 Adaptive Chatbot is ready for conversations!")
        
        # Run the UI main loop
        self.ui_system.run()
    
    def run(self):
        """Run the chatbot system"""
        try:
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # We're already in an async context, create a new thread
                    def run_in_thread():
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        new_loop.run_until_complete(self.run_async())
                        new_loop.close()
                    
                    thread = threading.Thread(target=run_in_thread, daemon=False)
                    thread.start()
                    thread.join()
                else:
                    loop.run_until_complete(self.run_async())
            except RuntimeError:
                # No event loop, create a new one
                asyncio.run(self.run_async())
                
        except KeyboardInterrupt:
            log_info("👋 Shutting down Adaptive Chatbot...")
            self.shutdown()
        except Exception as e:
            log_error(f"Fatal error: {e}")
            raise
    
    def shutdown(self):
        """Shutdown the chatbot system"""
        log_info("🔄 Shutting down Adaptive Chatbot systems...")
        
        self.is_running = False
        self.is_listening = False
        
        try:
            # Cleanup all systems
            if self.tts_system:
                self.tts_system.cleanup()
            
            if self.conversation_manager:
                self.conversation_manager.cleanup()
                
            if self.language_detector:
                self.language_detector.cleanup()
                
            if self.ai_models_system:
                self.ai_models_system.cleanup()
                
            if self.voice_adaptation_system:
                self.voice_adaptation_system.cleanup()
                
            if self.ui_system and hasattr(self.ui_system, 'voice_visualizer'):
                self.ui_system.voice_visualizer.cleanup()
            
            log_info("✅ Adaptive Chatbot shutdown completed")
            
        except Exception as e:
            log_error(f"Error during shutdown: {e}")

def main():
    """Main entry point"""
    print("🤖 Adaptive Chatbot - Complete Multilingual AI Experience")
    print("=" * 60)
    print("Features:")
    print("• 🌐 Multi-language support (Hindi, English, Spanish, French, etc.)")
    print("• 🎭 Adaptive voice personalities")
    print("• 🤖 Free AI model integration")
    print("• 💬 Advanced conversation management")
    print("• 🎨 Enhanced UI with voice visualization")
    print("• 🔊 Natural text-to-speech")
    print("=" * 60)
    
    try:
        # Create and run the adaptive chatbot
        chatbot = AdaptiveChatbot()
        chatbot.run()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error starting chatbot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()