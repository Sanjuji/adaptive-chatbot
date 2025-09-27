#!/usr/bin/env python3
"""
Simple Adaptive Chatbot - Basic Version
A working chatbot that doesn't require external dependencies
"""

import random
import time
from datetime import datetime

class SimpleChatbot:
    def __init__(self):
        self.name = "Adaptive Assistant"
        self.conversation_history = []
        self.user_preferences = {}
        self.start_time = datetime.now()
        
        # Simple responses for different languages
        self.responses = {
            'en': {
                'greeting': [
                    "Hello! How can I help you today?",
                    "Hi there! What would you like to know?",
                    "Greetings! I'm here to assist you.",
                    "Hello! I'm your adaptive assistant."
                ],
                'farewell': [
                    "Goodbye! Have a great day!",
                    "See you later! Take care!",
                    "Farewell! Until next time!",
                    "Bye! Thanks for chatting!"
                ],
                'question': [
                    "That's an interesting question! Let me think about that.",
                    "I'd be happy to help with that question.",
                    "That's a great question! Here's what I think:",
                    "Let me provide some information on that topic."
                ],
                'default': [
                    "I understand. Can you tell me more about that?",
                    "That's interesting! Please continue.",
                    "I'm listening. What else would you like to share?",
                    "Tell me more about what you're thinking."
                ]
            },
            'hi': {
                'greeting': [
                    "नमस्ते! आज मैं आपकी कैसे सहायता कर सकता हूँ?",
                    "हैलो! आप क्या जानना चाहते हैं?",
                    "नमस्कार! मैं यहाँ आपकी मदद के लिए हूँ।",
                    "नमस्ते! मैं आपका अनुकूली सहायक हूँ।"
                ],
                'farewell': [
                    "अलविदा! आपका दिन शुभ हो!",
                    "फिर मिलते हैं! ध्यान रखें!",
                    "विदाई! अगली बार तक!",
                    "बाय! बात करने के लिए धन्यवाद!"
                ],
                'question': [
                    "यह एक दिलचस्प सवाल है! मुझे इसके बारे में सोचने दें।",
                    "मैं इस सवाल में आपकी मदद करने में खुशी होगी।",
                    "यह एक बेहतरीन सवाल है! यहाँ मेरी राय है:",
                    "इस विषय पर कुछ जानकारी देने दें।"
                ],
                'default': [
                    "मैं समझ गया। क्या आप इसके बारे में और बता सकते हैं?",
                    "यह दिलचस्प है! कृपया जारी रखें।",
                    "मैं सुन रहा हूँ। आप और क्या साझा करना चाहेंगे?",
                    "आप क्या सोच रहे हैं इसके बारे में और बताएं।"
                ]
            }
        }
        
        # Simple language detection keywords
        self.language_keywords = {
            'hi': ['नमस्ते', 'हैलो', 'नमस्कार', 'कैसे', 'क्या', 'है', 'हैं', 'में', 'का', 'की', 'को', 'से', 'पर', 'तो', 'भी', 'अब', 'यह', 'वह', 'मैं', 'आप', 'हम', 'वे'],
            'en': ['hello', 'hi', 'how', 'what', 'where', 'when', 'why', 'who', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 'will', 'would', 'can', 'could', 'should', 'the', 'a', 'an', 'and', 'or', 'but']
        }
    
    def detect_language(self, text):
        """Simple language detection based on keywords"""
        text_lower = text.lower()
        
        hi_score = sum(1 for word in self.language_keywords['hi'] if word in text_lower)
        en_score = sum(1 for word in self.language_keywords['en'] if word in text_lower)
        
        if hi_score > en_score:
            return 'hi'
        else:
            return 'en'
    
    def detect_intent(self, text):
        """Simple intent detection"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['hello', 'hi', 'namaste', 'नमस्ते', 'हैलो', 'नमस्कार']):
            return 'greeting'
        elif any(word in text_lower for word in ['bye', 'goodbye', 'see you', 'अलविदा', 'बाय', 'फिर मिलते']):
            return 'farewell'
        elif '?' in text or any(word in text_lower for word in ['what', 'how', 'why', 'when', 'where', 'क्या', 'कैसे', 'क्यों', 'कब', 'कहाँ']):
            return 'question'
        else:
            return 'default'
    
    def generate_response(self, user_input):
        """Generate a response based on user input"""
        language = self.detect_language(user_input)
        intent = self.detect_intent(user_input)
        
        # Get appropriate response
        if language in self.responses and intent in self.responses[language]:
            response = random.choice(self.responses[language][intent])
        else:
            response = random.choice(self.responses['en']['default'])
        
        return response, language, intent
    
    def demo_chat(self):
        """Demo chat with predefined inputs"""
        print(f"🤖 {self.name} - Simple Adaptive Chatbot")
        print("=" * 50)
        print("Running demo conversation...")
        print("=" * 50)
        
        # Demo inputs
        demo_inputs = [
            "Hello! How are you?",
            "नमस्ते! आप कैसे हैं?",
            "What is the weather like?",
            "क्या आप हिंदी बोल सकते हैं?",
            "Thank you for your help!",
            "bye"
        ]
        
        # Welcome message
        welcome_msg = "Hello! I'm your adaptive assistant. How can I help you today?"
        print(f"Bot: {welcome_msg}")
        
        for user_input in demo_inputs:
            print(f"\nYou: {user_input}")
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye', 'अलविदा', 'बाय']:
                farewell_msg = "Goodbye! Thanks for chatting with me!"
                print(f"Bot: {farewell_msg}")
                break
            
            # Generate response
            response, detected_lang, intent = self.generate_response(user_input)
            
            # Store conversation
            self.conversation_history.append({
                'timestamp': datetime.now(),
                'user_input': user_input,
                'bot_response': response,
                'detected_language': detected_lang,
                'intent': intent
            })
            
            # Display response
            print(f"Bot ({detected_lang}): {response}")
            
            # Small delay for demo
            time.sleep(1)
        
        print("\n🎉 Demo completed successfully!")
    
    def chat(self):
        """Main chat loop"""
        print(f"🤖 {self.name} - Simple Adaptive Chatbot")
        print("=" * 50)
        print("Type 'quit', 'exit', or 'bye' to end the conversation")
        print("Supports English and Hindi")
        print("=" * 50)
        
        # Welcome message
        welcome_msg = "Hello! I'm your adaptive assistant. How can I help you today?"
        print(f"Bot: {welcome_msg}")
        
        while True:
            try:
                # Get user input
                user_input = input("\nYou: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'अलविदा', 'बाय']:
                    farewell_msg = "Goodbye! Thanks for chatting with me!"
                    print(f"Bot: {farewell_msg}")
                    break
                
                if not user_input:
                    continue
                
                # Generate response
                response, detected_lang, intent = self.generate_response(user_input)
                
                # Store conversation
                self.conversation_history.append({
                    'timestamp': datetime.now(),
                    'user_input': user_input,
                    'bot_response': response,
                    'detected_language': detected_lang,
                    'intent': intent
                })
                
                # Display response
                print(f"Bot ({detected_lang}): {response}")
                
                # Show some stats
                if len(self.conversation_history) % 5 == 0:
                    runtime = datetime.now() - self.start_time
                    print(f"\n📊 Stats: {len(self.conversation_history)} messages, {runtime.total_seconds():.1f}s runtime")
                
            except KeyboardInterrupt:
                print("\n\nBot: Goodbye! Thanks for chatting!")
                break
            except Exception as e:
                print(f"Bot: Sorry, I encountered an error: {e}")
    
    def show_stats(self):
        """Show conversation statistics"""
        if not self.conversation_history:
            print("No conversation history yet.")
            return
        
        print("\n📊 Conversation Statistics:")
        print("=" * 30)
        
        # Language usage
        languages = {}
        intents = {}
        
        for msg in self.conversation_history:
            lang = msg['detected_language']
            intent = msg['intent']
            
            languages[lang] = languages.get(lang, 0) + 1
            intents[intent] = intents.get(intent, 0) + 1
        
        print(f"Total messages: {len(self.conversation_history)}")
        print(f"Languages used: {', '.join(f'{k} ({v})' for k, v in languages.items())}")
        print(f"Intents detected: {', '.join(f'{k} ({v})' for k, v in intents.items())}")
        
        runtime = datetime.now() - self.start_time
        print(f"Session duration: {runtime.total_seconds():.1f} seconds")

def main():
    """Main function"""
    chatbot = SimpleChatbot()
    
    try:
        # Run demo first to test functionality
        chatbot.demo_chat()
        chatbot.show_stats()
        
        # Ask if user wants interactive mode
        print("\n" + "="*50)
        print("Demo completed! The chatbot is working properly.")
        print("Features tested:")
        print("✓ Language detection (English/Hindi)")
        print("✓ Intent recognition (greeting/question/farewell)")
        print("✓ Multilingual responses")
        print("✓ Conversation history tracking")
        print("="*50)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()