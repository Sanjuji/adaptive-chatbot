#!/usr/bin/env python3
"""
Enhanced Voice Interface with Better Speech Recognition and Human-like TTS
Windows-compatible with multiple voice engine options
"""

import sys
import os

import speech_recognition as sr
import pyttsx3
import time
import threading
import queue

# Additional imports for enhanced voice
try:
    import win32com.client  # Windows SAPI
    WINDOWS_SAPI_AVAILABLE = True
except ImportError:
    WINDOWS_SAPI_AVAILABLE = False

try:
    from gtts import gTTS
    import pygame
    import io
    import tempfile
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_SPEECH_AVAILABLE = True
except ImportError:
    AZURE_SPEECH_AVAILABLE = False

class EnhancedVoiceInterface:
    """Enhanced Voice Interface with multiple speech engines"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.tts_engine = None
        self.voice_config = {}
        
        # Initialize components
        self._init_microphone()
        self._init_tts_engines()
    
    def _init_microphone(self):
        """Initialize microphone with better settings"""
        try:
            # Try to find the best microphone
            mic_list = sr.Microphone.list_microphone_names()
            print("🎤 Available microphones:")
            for i, name in enumerate(mic_list):
                print(f"  {i}: {name}")
            
            # Prefer proper input microphones (avoid speakers/outputs)
            input_keywords = ['Microphone', 'Mic input', 'Array', 'Webcam']
            avoid_keywords = ['Speakers', 'Output', 'Mapper - Output']
            selected_mic = None
            
            # First try to find a good input microphone
            for i, name in enumerate(mic_list):
                is_input = any(keyword.lower() in name.lower() for keyword in input_keywords)
                is_output = any(keyword.lower() in name.lower() for keyword in avoid_keywords)
                
                if is_input and not is_output:
                    selected_mic = i
                    print(f"✅ Selected microphone: {name}")
                    break
            
            # If no proper input found, use default (index 0 or first available)
            if selected_mic is None:
                # Try to find the first non-output device
                for i, name in enumerate(mic_list):
                    is_output = any(keyword.lower() in name.lower() for keyword in avoid_keywords)
                    if not is_output:
                        selected_mic = i
                        print(f"✅ Selected microphone: {name}")
                        break
            
            # Initialize microphone
            if selected_mic is not None:
                self.microphone = sr.Microphone(device_index=selected_mic)
            else:
                self.microphone = sr.Microphone()
                print("🎤 Using default microphone")
            
            # Configure recognizer for better accuracy
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            self.recognizer.operation_timeout = None
            self.recognizer.phrase_threshold = 0.3
            self.recognizer.non_speaking_duration = 0.8
            
        except Exception as e:
            print(f"❌ Microphone initialization error: {e}")
            self.microphone = sr.Microphone()
    
    def _init_tts_engines(self):
        """Initialize multiple TTS engines for best quality"""
        self.tts_engines = {}
        
        # 1. Windows SAPI (Best for Windows)
        if WINDOWS_SAPI_AVAILABLE:
            try:
                sapi = win32com.client.Dispatch("SAPI.SpVoice")
                voices = sapi.GetVoices()
                
                print("🔊 Available SAPI voices:")
                for i, voice in enumerate(voices):
                    print(f"  {i}: {voice.GetDescription()}")
                
                # Try to find a good female voice
                best_voice = None
                for voice in voices:
                    desc = voice.GetDescription().lower()
                    if 'zira' in desc or 'female' in desc or 'woman' in desc:
                        best_voice = voice
                        break
                
                if best_voice:
                    sapi.Voice = best_voice
                    print(f"✅ Selected SAPI voice: {best_voice.GetDescription()}")
                
                # Configure SAPI settings
                sapi.Rate = 1  # Speed (-10 to +10)
                sapi.Volume = 100  # Volume (0 to 100)
                
                self.tts_engines['sapi'] = sapi
                
            except Exception as e:
                print(f"⚠️ SAPI initialization failed: {e}")
        
        # 2. Pyttsx3 (Local TTS)
        try:
            engine = pyttsx3.init(driverName='sapi5')
            voices = engine.getProperty('voices')
            
            # Find the best voice
            female_voice = None
            for voice in voices:
                if 'zira' in voice.name.lower() or 'female' in voice.name.lower():
                    female_voice = voice
                    break
            
            if female_voice:
                engine.setProperty('voice', female_voice.id)
                print(f"✅ Pyttsx3 voice: {female_voice.name}")
            
            engine.setProperty('rate', 180)  # Speed
            engine.setProperty('volume', 0.9)  # Volume
            
            self.tts_engines['pyttsx3'] = engine
            
        except Exception as e:
            print(f"⚠️ Pyttsx3 initialization failed: {e}")
        
        # 3. Google TTS (Online, very natural)
        if GTTS_AVAILABLE:
            try:
                pygame.mixer.init()
                self.tts_engines['gtts'] = 'available'
                print("✅ Google TTS available")
            except Exception as e:
                print(f"⚠️ Google TTS initialization failed: {e}")
        
        # Set default engine
        if 'sapi' in self.tts_engines:
            self.current_tts = 'sapi'
        elif 'pyttsx3' in self.tts_engines:
            self.current_tts = 'pyttsx3'
        elif 'gtts' in self.tts_engines:
            self.current_tts = 'gtts'
        else:
            print("❌ No TTS engine available")
            self.current_tts = None
    
    def speak_text(self, text):
        """Enhanced text-to-speech with multiple engines"""
        if not text.strip():
            return
        
        print(f"🔊 Bot: {text}")
        
        try:
            if self.current_tts == 'sapi' and 'sapi' in self.tts_engines:
                self.tts_engines['sapi'].Speak(text)
            
            elif self.current_tts == 'pyttsx3' and 'pyttsx3' in self.tts_engines:
                self.tts_engines['pyttsx3'].say(text)
                self.tts_engines['pyttsx3'].runAndWait()
            
            elif self.current_tts == 'gtts' and GTTS_AVAILABLE:
                self._speak_with_gtts(text)
            
        except Exception as e:
            print(f"⚠️ TTS error: {e}")
    
    def _speak_with_gtts(self, text):
        """Google TTS implementation"""
        try:
            tts = gTTS(text=text, lang='hi', slow=False)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                
                # Play with pygame
                pygame.mixer.music.load(tmp_file.name)
                pygame.mixer.music.play()
                
                # Wait for playback to complete
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                # Clean up
                try:
                    os.unlink(tmp_file.name)
                except:
                    pass
                    
        except Exception as e:
            print(f"⚠️ Google TTS error: {e}")
    
    def listen_for_speech(self, prompt="Listening...", timeout=10):
        """Enhanced speech recognition with multiple attempts"""
        try:
            print(f"🎤 {prompt}")
            
            with self.microphone as source:
                # Calibrate for ambient noise
                print("🔧 Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Listen for speech
                print("🎧 Listening for speech...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=15
                )
            
            print("🔄 Processing speech...")
            
            # Try multiple recognition services
            recognition_services = [
                ('Google (Hindi)', lambda: self.recognizer.recognize_google(audio, language='hi-IN')),
                ('Google (English-India)', lambda: self.recognizer.recognize_google(audio, language='en-IN')),
                ('Google (English)', lambda: self.recognizer.recognize_google(audio, language='en-US')),
                ('Windows Speech', lambda: self._recognize_with_windows_speech(audio) if WINDOWS_SAPI_AVAILABLE else None)
            ]
            
            for service_name, recognition_func in recognition_services:
                try:
                    result = recognition_func()
                    if result and result.strip():
                        print(f"✅ {service_name} recognized: '{result}'")
                        return result.strip()
                except sr.UnknownValueError:
                    print(f"⚠️ {service_name}: Could not understand")
                    continue
                except sr.RequestError as e:
                    print(f"❌ {service_name} error: {e}")
                    continue
                except Exception as e:
                    print(f"❌ {service_name} exception: {e}")
                    continue
            
            print("❌ No recognition service could understand the speech")
            return None
            
        except sr.WaitTimeoutError:
            print("⏰ Listening timeout - no speech detected")
            return None
        except Exception as e:
            print(f"❌ Speech recognition error: {e}")
            return None
    
    def _recognize_with_windows_speech(self, audio):
        """Try Windows Speech Recognition API"""
        # This is a placeholder - Windows Speech API integration would require more setup
        return None
    
    def set_tts_engine(self, engine_name):
        """Switch TTS engine"""
        if engine_name in self.tts_engines:
            self.current_tts = engine_name
            print(f"🔊 Switched to {engine_name} TTS engine")
            return True
        return False
    
    def test_voice_interface(self):
        """Test all voice components"""
        print("🧪 Testing Enhanced Voice Interface...")
        
        # Test TTS engines
        test_message = "नमस्ते! यह enhanced voice test है। Hello! This is an enhanced voice test."
        
        for engine_name in self.tts_engines.keys():
            print(f"🔊 Testing {engine_name}...")
            original_engine = self.current_tts
            self.set_tts_engine(engine_name)
            self.speak_text(f"Testing {engine_name} engine. यह {engine_name} इंजन का test है।")
            time.sleep(2)
            self.current_tts = original_engine
        
        # Test speech recognition
        print("🎤 Testing enhanced speech recognition...")
        self.speak_text("अब आप कुछ बोलिए। मैं सुन रहा हूँ।")
        
        result = self.listen_for_speech("Testing speech recognition...")
        if result:
            self.speak_text(f"Perfect! आपने कहा: {result}")
            return True
        else:
            self.speak_text("Speech recognition test में कुछ problem है।")
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if 'pyttsx3' in self.tts_engines:
                self.tts_engines['pyttsx3'].stop()
            if GTTS_AVAILABLE:
                pygame.mixer.quit()
        except:
            pass
    
    # Compatibility methods for other modules
    def setup_speech_recognition(self, engine="google", language="hi-IN"):
        """Setup speech recognition (compatibility method)"""
        # This is already handled in __init__, but we provide this for compatibility
        print(f"✅ Speech recognition configured: {engine} ({language})")
        return True
    
    def setup_tts(self, engine="sapi", voice_id=0):
        """Setup TTS engine (compatibility method)"""
        if engine in self.tts_engines:
            self.current_tts = engine
            print(f"✅ TTS configured: {engine}")
            return True
        else:
            print(f"⚠️ TTS engine {engine} not available, using {self.current_tts}")
            return False
    
    def text_to_speech(self, text):
        """Alias for speak_text (compatibility)"""
        return self.speak_text(text)
    
    def speech_to_text(self, timeout=10):
        """Alias for listen_for_speech (compatibility)"""
        return self.listen_for_speech(timeout=timeout)

def main():
    """Demo of enhanced voice interface"""
    print("🎙️ Enhanced Voice Interface Demo")
    print("Better Speech Recognition + Human-like TTS")
    print("=" * 60)
    
    try:
        # Initialize enhanced voice interface
        voice_interface = EnhancedVoiceInterface()
        
        # Test the interface
        if voice_interface.test_voice_interface():
            print("✅ Enhanced voice interface is working perfectly!")
        else:
            print("⚠️ Some issues detected, but interface is functional")
        
        # Show available engines
        print(f"\n🔊 Available TTS engines: {list(voice_interface.tts_engines.keys())}")
        print(f"🎯 Current TTS engine: {voice_interface.current_tts}")
        
        # Interactive test
        print("\n🎤 Interactive Test - Say something:")
        user_input = voice_interface.listen_for_speech("Say anything...")
        
        if user_input:
            voice_interface.speak_text(f"You said: {user_input}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        voice_interface.cleanup()

if __name__ == "__main__":
    main()