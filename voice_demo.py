#!/usr/bin/env python3
"""
Voice Demo - Test all available EdgeTTS realistic voices
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from core.edge_tts_engine import EdgeTTSEngine

def demo_all_voices():
    """Demo all available realistic voices"""
    print("🎤 EdgeTTS Realistic Voice Demo")
    print("=" * 40)
    
    try:
        engine = EdgeTTSEngine()
        voices = engine.get_available_voices()
        
        print(f"\n🗣️ Available Voices ({len(voices)}):")
        for name, details in voices.items():
            print(f"  • {name}: {details}")
        
        print("\n🔊 Testing each voice:")
        
        # Test messages for different voices
        test_messages = {
            'english_male': "Hello! I am your realistic English voice assistant.",
            'english_male_warm': "Namaste! Main aapka warm and confident voice assistant hun.",  
            'english_male_deep': "This is the deep, warm voice. Very natural sounding.",
            'hindi_male': "Namaste! Main Hindi mein bol raha hun. Kya aap sun sakte hain?",
            'hindi_male_warm': "Dhanyawad! Aap ka naya realistic voice assistant taiyar hai."
        }
        
        for voice_name in voices.keys():
            print(f"\n🎵 Testing: {voice_name}")
            engine.set_voice(voice_name)
            
            # Use specific message or default
            message = test_messages.get(voice_name, f"Testing {voice_name} voice. Sounds realistic!")
            
            success = engine.speak(message, blocking=True)
            if success:
                print(f"✅ {voice_name} - Working!")
            else:
                print(f"❌ {voice_name} - Failed!")
        
        print("\n✨ Demo completed! Choose your favorite voice for the chatbot.")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    finally:
        try:
            engine.cleanup()
        except:
            pass

if __name__ == "__main__":
    demo_all_voices()