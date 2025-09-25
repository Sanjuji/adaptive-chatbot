#!/usr/bin/env python3
"""
Simple Text-Based Demo of Adaptive Chatbot
For testing without UI and voice - just text input/output
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from advanced_conversation_manager import get_conversation_manager
from enhanced_language_detection import get_language_detector
from free_ai_models_integration import get_ai_models_system
from multilingual_edgetts_integration import get_multilingual_tts_system
from voice_tone_style_adaptation import get_voice_adaptation_system
from logger import log_info, log_error

class TextChatbotDemo:
    """Simple text-based chatbot demo"""
    
    def __init__(self):
        log_info("🤖 Initializing Text Demo Chatbot...")
        
        # Initialize core systems
        self.conversation_manager = get_conversation_manager()
        self.language_detector = get_language_detector()
        self.ai_models_system = get_ai_models_system()
        self.voice_adaptation_system = get_voice_adaptation_system()
        self.tts_system = get_multilingual_tts_system()
        
        # User and session
        self.user_id = "demo_user"
        self.session_id = None
        
        log_info("✅ Text Demo Chatbot initialized!")
    
    async def start_chat(self):
        """Start the chat session"""
        
        # Start conversation session
        self.session_id = self.conversation_manager.start_conversation(self.user_id)
        
        print("\n🤖 Adaptive Chatbot - Text Demo")
        print("=" * 50)
        print("• Type in any language (Hindi, English, Spanish, French, etc.)")
        print("• Type 'quit' or 'exit' to stop")
        print("• Type 'voice on' to enable speech output")
        print("• Type 'voice off' to disable speech output")
        print("=" * 50)
        print("\n🤖 Bot: Hello! I'm your adaptive assistant. How can I help you today?")
        
        voice_enabled = False
        
        while True:
            try:
                # Get user input
                user_input = input("\n👤 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n🤖 Bot: Goodbye! Have a great day!")
                    break
                elif user_input.lower() == 'voice on':
                    voice_enabled = True
                    print("\n🤖 Bot: Voice output enabled! 🔊")
                    continue
                elif user_input.lower() == 'voice off':
                    voice_enabled = False
                    print("\n🤖 Bot: Voice output disabled! 🔇")
                    continue
                
                # Process the input
                response = await self.process_message(user_input, voice_enabled)
                print(f"\n🤖 Bot: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                log_error(f"Error in chat loop: {e}")
                print(f"\n❌ Error: {e}")
    
    async def process_message(self, text: str, voice_enabled: bool = False) -> str:
        """Process user message and generate response"""
        
        try:
            # Step 1: Detect language
            lang_result = await self.language_detector.detect_language_advanced(text)
            detected_language = lang_result.detected_language
            confidence = lang_result.confidence
            
            print(f"🌐 Detected: {detected_language} (confidence: {confidence:.2f})")
            
            # Step 2: Get conversation context
            context = self.conversation_manager.get_conversation_context(self.session_id)
            
            # Step 3: Generate AI response
            print("🧠 Generating response...")
            ai_response = await self.ai_models_system.generate_conversation_response(text)
            response_text = ai_response.text if ai_response else "I apologize, but I couldn't generate a response."
            
            # Step 4: Voice adaptation
            voice_context = {
                "intent": "general",
                "sentiment": "neutral", 
                "confidence": ai_response.confidence if ai_response else 0.5,
                "detected_language": detected_language
            }
            
            voice_adaptation_result = await self.voice_adaptation_system.adapt_voice_style(
                response_text,
                voice_context,
                user_id=self.user_id,
                session_id=self.session_id
            )
            
            # Step 5: Add to conversation history
            self.conversation_manager.add_turn(
                session_id=self.session_id,
                user_input=text,
                system_response=response_text,
                metadata={
                    "detected_language": detected_language,
                    "intent": "general",
                    "sentiment": "neutral",
                    "confidence": confidence,
                    "topic": "general",
                    "voice_used": voice_adaptation_result.voice_profile.personality.value if hasattr(voice_adaptation_result.voice_profile, 'personality') else None,
                    "response_time": 0.0
                }
            )
            
            # Step 6: Optional voice output
            if voice_enabled:
                try:
                    print("🔊 Speaking response...")
                    await self.tts_system.speak_with_auto_voice(
                        response_text,
                        detected_language,
                        voice_context.get("sentiment", "neutral"),
                        voice_context
                    )
                except Exception as e:
                    print(f"⚠️ Voice output failed: {e}")
            
            return response_text
            
        except Exception as e:
            log_error(f"Error processing message: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.session_id:
                self.conversation_manager.end_conversation(self.session_id)
            
            # Cleanup systems
            if self.conversation_manager:
                self.conversation_manager.cleanup()
            if self.language_detector:
                self.language_detector.cleanup()
            if self.tts_system:
                self.tts_system.cleanup()
            if self.voice_adaptation_system:
                self.voice_adaptation_system.cleanup()
                
            log_info("✅ Text demo cleanup completed")
        except Exception as e:
            log_error(f"Cleanup error: {e}")

async def main():
    """Main function"""
    demo = TextChatbotDemo()
    try:
        await demo.start_chat()
    finally:
        demo.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")