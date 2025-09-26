#!/usr/bin/env python3
"""
Text Chat System
Simple text-based conversation with the adaptive chatbot
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interactive_voice_teaching import LearningManager
import json
import time

class TextChat:
    """Text-based chatbot using the learning manager"""
    
    def __init__(self):
        self.learning_manager = LearningManager()
        print("📝 Text chat initialized!")
    
    def get_response(self, query):
        """Get response for a query"""
        # Try to find answer in knowledge base
        answer = self.learning_manager.find_answer(query)
        
        if answer:
            return f"💡 {answer}"
        
        # Default responses for common greetings
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['hello', 'hi', 'namaste', 'नमस्ते', 'हैलो']):
            return "🙏 नमस्ते! मैं आपकी मदद के लिए हूं। आप मुझसे कुछ भी पूछ सकते हैं।"
        
        if any(word in query_lower for word in ['how are you', 'कैसे हो', 'कैसे हैं']):
            return "😊 मैं ठीक हूं, धन्यवाद! आप कैसे हैं?"
        
        if any(word in query_lower for word in ['thank you', 'thanks', 'धन्यवाद', 'शुक्रिया']):
            return "🤗 आपका स्वागत है! कुछ और पूछना चाहते हैं?"
        
        if any(word in query_lower for word in ['name', 'नाम', 'who are you', 'आप कौन हैं']):
            return "🤖 मैं एक एडेप्टिव चैटबॉट हूं। मैं सीखता रहता हूं और आपकी मदद करता हूं।"
        
        if any(word in query_lower for word in ['help', 'मदद', 'सहायता']):
            return """📚 मैं इन कामों में आपकी मदद कर सकता हूं:
            
• आपके सवालों का जवाब दे सकता हूं
• नई जानकारी सीख सकता हूं  
• बातचीत कर सकता हूं
• मदद और सुझाव दे सकता हूं

बस आप मुझसे कुछ भी पूछें या 'teach' लिखकर मुझे नई चीज़ें सिखाएं!"""
        
        # Default response when no answer is found
        return "🤔 मुझे इसका जवाब नहीं पता। आप मुझे इसके बारे में सिखा सकते हैं या voice teaching mode का उपयोग करें।"
    
    def start_chat(self):
        """Start the text chat session"""
        print("\n💬 Text Chat Session Started")
        print("=" * 40)
        print("🤖 नमस्ते! मैं आपकी टेक्स्ट चैट के लिए तैयार हूं।")
        print("💡 Type 'help' for assistance, 'exit' to quit")
        print("-" * 40)
        
        while True:
            try:
                # Get user input
                user_input = input("👤 You: ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'बाई', 'अलविदा', 'goodbye']:
                    print("🤖 Bot: 👋 अलविदा! बात करके अच्छा लगा।")
                    break
                
                # Special teaching command
                if user_input.lower() in ['teach', 'टीच', 'सिखा']:
                    self.text_teaching_session()
                    continue
                
                # Get and display response
                response = self.get_response(user_input)
                print(f"🤖 Bot: {response}")
                print()
                
            except KeyboardInterrupt:
                print("\n🤖 Bot: 👋 चैट बंद कर रहा हूं। अलविदा!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def text_teaching_session(self):
        """Handle text-based teaching"""
        print("\n📚 Teaching Mode Activated!")
        print("-" * 30)
        
        try:
            # Get question
            question = input("❓ Question (सवाल): ").strip()
            if not question:
                print("🤖 कोई सवाल नहीं मिला।")
                return
            
            # Get answer
            answer = input("💡 Answer (जवाब): ").strip()
            if not answer:
                print("🤖 कोई जवाब नहीं मिला।")
                return
            
            # Confirm
            print(f"\n🔄 Confirmation: '{question}' -> '{answer}'")
            confirm = input("✅ Is this correct? (y/n): ").lower()
            
            if confirm in ['y', 'yes', 'हाँ', 'हां']:
                # Save the knowledge
                self.learning_manager.add_knowledge(question, answer)
                print("🎉 Successfully learned! Testing...")
                
                # Test immediately
                test_response = self.learning_manager.find_answer(question)
                if test_response:
                    print(f"🧪 Test: {question} -> {test_response}")
                    print("✅ Teaching successful!")
                else:
                    print("❌ Teaching failed - could not retrieve answer")
            else:
                print("❌ Teaching cancelled.")
                
        except KeyboardInterrupt:
            print("\n❌ Teaching cancelled.")
        
        print("-" * 30)
        print("📝 Back to normal chat...")

def main():
    """Main function to run the text chat system"""
    try:
        print("🚀 Starting Text Chat System...")
        chat = TextChat()
        chat.start_chat()
        
    except KeyboardInterrupt:
        print("\n👋 Text chat interrupted by user.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()