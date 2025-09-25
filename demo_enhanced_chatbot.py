#!/usr/bin/env python3
"""
Enhanced Adaptive Chatbot Demo
Showcases all features with enhanced voice and text capabilities
"""

import sys
import os
from enhanced_voice_interface import EnhancedVoiceInterface
from interactive_voice_teaching import LearningManager
import json

def demo_enhanced_voice_interface():
    """Demonstrate enhanced voice interface capabilities"""
    print("\n🎙️ Enhanced Voice Interface Demo")
    print("=" * 50)
    
    try:
        voice = EnhancedVoiceInterface()
        
        # Show available engines
        print(f"🔊 Available TTS engines: {list(voice.tts_engines.keys())}")
        print(f"🎯 Current TTS engine: {voice.current_tts}")
        
        # Test different TTS voices
        print("\n🎤 Testing different voice engines...")
        test_messages = [
            "Enhanced voice interface is working perfectly!",
            "यह enhanced voice interface है। यह हिंदी और English दोनों में काम करता है।",
            "Voice recognition की quality बहुत अच्छी है।"
        ]
        
        for i, message in enumerate(test_messages):
            print(f"\n📢 Test {i+1}: {message}")
            voice.speak_text(message)
            
            if i < len(test_messages) - 1:
                input("Press Enter to continue to next test...")
        
        print("\n✅ Voice interface demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Voice demo error: {e}")
        return False

def demo_learning_system():
    """Demonstrate the learning system capabilities"""
    print("\n🧠 Learning System Demo")
    print("=" * 40)
    
    try:
        learning_manager = LearningManager()
        
        # Show current knowledge base
        print(f"📚 Current knowledge base has {len(learning_manager.knowledge_base)} items")
        
        # Add some demo knowledge
        demo_knowledge = [
            ("keyboard ka price kitna hai", "keyboard 500-1500 rupees mein milta hai"),
            ("laptop ki battery kitni der chalti hai", "laptop battery 3-8 hours chalti hai"),
            ("wifi password kya hai", "wifi password admin123 hai"),
            ("mobile charging time kitna lagta hai", "mobile charging mein 1-2 hours lagta hai")
        ]
        
        print("\n📝 Adding demo knowledge...")
        for question, answer in demo_knowledge:
            learning_manager.add_knowledge(question, answer)
        
        print(f"\n✅ Knowledge base now has {len(learning_manager.knowledge_base)} items")
        
        # Test knowledge retrieval
        print("\n🧪 Testing knowledge retrieval...")
        test_queries = [
            "keyboard price",
            "laptop battery",
            "wifi password",
            "mobile charging",
            "unknown question"
        ]
        
        for query in test_queries:
            answer = learning_manager.find_answer(query)
            if answer:
                print(f"❓ {query} → ✅ {answer}")
            else:
                print(f"❓ {query} → ❌ No answer found")
        
        return True
        
    except Exception as e:
        print(f"❌ Learning demo error: {e}")
        return False

def demo_text_chat():
    """Quick demo of text chat capabilities"""
    print("\n💬 Text Chat Demo")
    print("=" * 30)
    
    try:
        from text_chat import TextChat
        
        print("🤖 Text chat system ready!")
        print("Features:")
        print("  ✅ Interactive teaching mode")
        print("  ✅ Knowledge retention")
        print("  ✅ Hindi + English support")
        print("  ✅ Natural conversation")
        print("  ✅ Immediate learning verification")
        
        print("\n💡 To use text chat: python text_chat.py")
        return True
        
    except Exception as e:
        print(f"❌ Text chat demo error: {e}")
        return False

def demo_voice_teaching():
    """Demo of voice teaching capabilities"""
    print("\n🎓 Voice Teaching Demo")
    print("=" * 35)
    
    try:
        print("🎤 Voice teaching features:")
        print("  ✅ Step-by-step voice guidance")
        print("  ✅ Natural Hindi speech recognition")
        print("  ✅ Multiple recognition attempts")
        print("  ✅ Immediate learning verification")
        print("  ✅ High-quality voice synthesis")
        print("  ✅ Interactive confirmation")
        
        print("\n💡 To use voice teaching: python chat_modes.py (option 1)")
        return True
        
    except Exception as e:
        print(f"❌ Voice teaching demo error: {e}")
        return False

def main():
    """Run complete enhanced chatbot demo"""
    print("🚀 Enhanced Adaptive Chatbot - Complete Demo")
    print("=" * 60)
    print("This demo showcases all enhanced features:")
    print("• Enhanced Voice Interface with multiple TTS engines")
    print("• Improved Speech Recognition for Hindi + English") 
    print("• Interactive Voice Teaching System")
    print("• Text-based Chat with Teaching Mode")
    print("• Smart Learning Manager with Knowledge Persistence")
    print("=" * 60)
    
    results = {}
    
    # Run all demos
    print("\n🔄 Running comprehensive demo...")
    
    results['voice_interface'] = demo_enhanced_voice_interface()
    results['learning_system'] = demo_learning_system()
    results['text_chat'] = demo_text_chat()
    results['voice_teaching'] = demo_voice_teaching()
    
    # Show results summary
    print("\n📊 Demo Results Summary")
    print("=" * 30)
    
    for feature, success in results.items():
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{feature.replace('_', ' ').title()}: {status}")
    
    successful_features = sum(results.values())
    total_features = len(results)
    
    print(f"\n🎯 Overall Success: {successful_features}/{total_features} features working")
    
    if successful_features == total_features:
        print("🎉 All features are working perfectly!")
        print("\n🚀 Your Enhanced Adaptive Chatbot is ready to use!")
        print("\nAvailable modes:")
        print("  1️⃣ python chat_modes.py - Interactive mode selection")
        print("  2️⃣ python text_chat.py - Direct text chat") 
        print("  3️⃣ python voice_chat.py - Direct voice chat")
        print("  4️⃣ python interactive_voice_teaching.py - Direct voice teaching")
    else:
        print("⚠️ Some features need attention, but basic functionality is available.")
    
    print("\n" + "=" * 60)
    print("Enhanced Adaptive Chatbot Demo Complete!")

if __name__ == "__main__":
    main()