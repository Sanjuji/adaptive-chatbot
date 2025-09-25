#!/usr/bin/env python3
"""
Voice Chat System
Uses the enhanced voice interface for natural conversation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_voice_interface import EnhancedVoiceInterface
from interactive_voice_teaching import LearningManager
import json
import time

class VoiceChat:
    """Voice-based chatbot using enhanced voice interface"""
    
    def __init__(self):
        self.voice = EnhancedVoiceInterface()
        self.learning_manager = LearningManager()
        self.setup_voice()
    
    def setup_voice(self):
        """Setup voice interface with optimized settings"""
        print("🎤 Setting up voice chat...")
        
        # Setup speech recognition
        self.voice.setup_speech_recognition(
            engine="google",  # Try Google first for better accuracy
            language="hi-IN"
        )
        
        # Setup TTS
        self.voice.setup_tts(
            engine="sapi",  # Use Windows SAPI for natural voice
            voice_id=0
        )
        
        print("✅ Voice chat ready!")
    
    def listen_with_retry(self, prompt=""):
        """Listen with multiple retries and fallback options"""
        attempts = 0
        max_attempts = 2
        
        while attempts < max_attempts:
            try:
                if prompt:
                    print(f"🤖 {prompt}")
                    self.voice.text_to_speech(prompt)
                
                print("🎤 Listening...")
                result = self.voice.speech_to_text(timeout=8)
                
                if result and result.strip():
                    print(f"👤 {result}")
                    return result.strip()
                else:
                    attempts += 1
                    if attempts < max_attempts:
                        self.voice.text_to_speech("समझ नहीं आया। फिर से बोलें।")
                    
            except Exception as e:
                attempts += 1
                print(f"❌ Recognition error: {e}")
                if attempts < max_attempts:
                    self.voice.text_to_speech("Sorry, please try again.")
        
        return None
    
    def get_response(self, query):
        """Get response for a query"""
        # Try to find answer in knowledge base
        answer = self.learning_manager.find_answer(query)
        
        if answer:
            return answer
        
        # Default responses for common greetings
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['hello', 'hi', 'namaste', 'नमस्ते', 'हैलो']):
            return "नमस्ते! मैं आपकी मदद के लिए हूं। आप मुझसे कुछ भी पूछ सकते हैं।"
        
        if any(word in query_lower for word in ['how are you', 'कैसे हो', 'कैसे हैं']):
            return "मैं ठीक हूं, धन्यवाद! आप कैसे हैं?"
        
        if any(word in query_lower for word in ['thank you', 'thanks', 'धन्यवाद', 'शुक्रिया']):
            return "आपका स्वागत है! कुछ और पूछना चाहते हैं?"
        
        if any(word in query_lower for word in ['name', 'नाम', 'who are you', 'आप कौन हैं']):
            return "मैं एक एडेप्टिव चैटबॉट हूं। मैं सीखता रहता हूं और आपकी मदद करता हूं।"
        
        # Default response when no answer is found
        return "मुझे इसका जवाब नहीं पता। आप मुझे इसके बारे में सिखा सकते हैं।"
    
    def start_chat(self):
        """Start the voice chat session"""
        print("\n🗣️ Voice Chat Session Started")
        print("=" * 40)
        
        # Welcome message
        welcome_msg = "नमस्ते! आइए बात करते हैं। आप कुछ भी पूछ सकते हैं।"
        print(f"🤖 {welcome_msg}")
        self.voice.text_to_speech(welcome_msg)
        
        while True:
            # Listen for user input
            user_input = self.listen_with_retry()
            
            if not user_input:
                continue
            
            # Check for exit commands
            if any(word in user_input.lower() for word in ['exit', 'quit', 'bye', 'बाई', 'अलविदा', 'goodbye']):
                goodbye_msg = "अलविदा! बात करके अच्छा लगा।"
                print(f"🤖 {goodbye_msg}")
                self.voice.text_to_speech(goodbye_msg)
                break
            
            # Get and speak response
            response = self.get_response(user_input)
            print(f"🤖 {response}")
            self.voice.text_to_speech(response)

def main():
    """Main function to run the voice chat system"""
    try:
        print("🚀 Starting Voice Chat System...")
        chat = VoiceChat()
        chat.start_chat()
        
    except KeyboardInterrupt:
        print("\n👋 Voice chat interrupted by user.")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your microphone is connected and working.")

if __name__ == "__main__":
    main()