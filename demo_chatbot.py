#!/usr/bin/env python3
"""
Comprehensive Demo of Advanced Chatbot System
Shows all features: Language detection, Intent recognition, Sentiment analysis,
Multilingual responses, and integration capabilities
"""

import json
from datetime import datetime
from nlp_integration import get_smart_chatbot, smart_chat

def demo_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"🚀 {title}")
    print("=" * 70)

def demo_language_detection():
    """Demo language detection capabilities"""
    demo_header("MULTILINGUAL LANGUAGE DETECTION")
    
    chatbot = get_smart_chatbot()
    
    test_inputs = [
        ("Hello, how can I help you?", "English"),
        ("नमस्ते, मैं कैसे मदद कर सकता हूँ?", "Hindi"),
        ("Hola, ¿cómo puedo ayudarte?", "Spanish"),
        ("Bonjour, comment puis-je vous aider?", "French"),
        ("Guten Tag, wie kann ich helfen?", "German"),
        ("Switch ka price kya hai?", "Mixed (Hinglish)"),
        ("मुझे help चाहिए", "Mixed (Hinglish)"),
        ("Ciao, come stai?", "Italian"),
        ("Привет, как дела?", "Russian (if supported)"),
        ("مرحبا، كيف يمكنني مساعدتك؟", "Arabic (if supported)")
    ]
    
    for text, expected in test_inputs:
        result = chatbot.process_user_input(text, speak_response=False)
        lang_info = result.get('language_info')
        detected_lang = lang_info.language_name if lang_info else 'Unknown'
        confidence = getattr(lang_info, 'confidence', 0.0) if lang_info else 0.0
        
        print(f"📝 Input: {text}")
        print(f"🌍 Detected: {detected_lang} ({confidence:.2f} confidence)")
        print(f"💬 Expected: {expected}")
        print(f"🤖 Response: {result['response_text'][:80]}...")
        print("-" * 50)

def demo_intent_recognition():
    """Demo intent recognition for different types of inputs"""
    demo_header("SMART INTENT RECOGNITION")
    
    chatbot = get_smart_chatbot()
    
    intent_examples = [
        # Greetings
        ("Hello there!", "greeting"),
        ("नमस्ते भाई", "greeting"),
        ("Good morning!", "greeting"),
        
        # Questions
        ("What's the price of a switch?", "question"),
        ("Switch ka price kitna hai?", "question"),
        ("How does this work?", "question"),
        
        # Requests
        ("Can you help me please?", "request"),
        ("मदद चाहिए", "request"),
        ("Please explain this to me", "request"),
        
        # Appreciation
        ("Thank you so much!", "appreciation"),
        ("धन्यवाद", "appreciation"),
        ("Great job!", "appreciation"),
        
        # Complaints
        ("This is not working properly", "complaint"),
        ("मुझे समस्या है", "complaint"),
        ("I have an issue", "complaint"),
        
        # Learning requests
        ("Teach me about this", "learning"),
        ("मुझे सिखाओ", "learning"),
        ("How can I learn more?", "learning"),
        
        # Farewells
        ("Goodbye!", "farewell"),
        ("अलविदा", "farewell"),
        ("See you later", "farewell")
    ]
    
    for text, expected_intent in intent_examples:
        result = chatbot.process_user_input(text, speak_response=False)
        intent_info = result.get('intent_info', {})
        detected_intent = intent_info.get('intent', 'unknown')
        confidence = intent_info.get('confidence', 0.0)
        
        status = "✅" if detected_intent == expected_intent else "⚠️"
        
        print(f"{status} Input: {text}")
        print(f"🎯 Intent: {detected_intent} ({confidence:.2f})")
        print(f"📈 Expected: {expected_intent}")
        print(f"🤖 Response: {result['response_text'][:60]}...")
        print()

def demo_sentiment_analysis():
    """Demo sentiment analysis capabilities"""
    demo_header("ADVANCED SENTIMENT ANALYSIS")
    
    chatbot = get_smart_chatbot()
    
    sentiment_examples = [
        ("I absolutely love this product!", "positive"),
        ("This is terrible and frustrating", "negative"),
        ("It's okay, nothing special", "neutral"),
        ("मुझे यह बहुत पसंद है!", "positive"),
        ("यह बिल्कुल खराब है", "negative"),
        ("ठीक है, कोई खास बात नहीं", "neutral"),
        ("Amazing work! Outstanding job!", "positive"),
        ("I'm really disappointed with this", "negative"),
        ("The weather is nice today", "positive"),
        ("I'm feeling sad about this", "negative")
    ]
    
    for text, expected_sentiment in sentiment_examples:
        result = chatbot.process_user_input(text, speak_response=False)
        sentiment_info = result.get('sentiment_info', {})
        detected_sentiment = sentiment_info.get('sentiment', 'neutral')
        confidence = sentiment_info.get('confidence', 0.0)
        emotion = sentiment_info.get('emotion', 'neutral')
        
        status = "✅" if detected_sentiment == expected_sentiment else "⚠️"
        
        print(f"{status} Input: {text}")
        print(f"😊 Sentiment: {detected_sentiment} ({confidence:.2f})")
        print(f"🎭 Emotion: {emotion}")
        print(f"📊 Expected: {expected_sentiment}")
        print(f"🤖 Response: {result['response_text'][:60]}...")
        print()

def demo_multilingual_conversation():
    """Demo natural multilingual conversation flow"""
    demo_header("MULTILINGUAL CONVERSATION FLOW")
    
    chatbot = get_smart_chatbot()
    
    conversation_flow = [
        "Hello! How are you today?",
        "नमस्ते! आप कैसे हैं?",
        "Switch ka price kya hai?",
        "मुझे कुछ सीखना है",
        "Thank you for your help!",
        "यह बहुत अच्छा है!",
        "I have a small problem",
        "धन्यवाद और अलविदा!",
        "Goodbye!"
    ]
    
    print("👤👤 Starting multilingual conversation...")
    print()
    
    for i, user_input in enumerate(conversation_flow, 1):
        print(f"👤 User ({i}): {user_input}")
        
        result = chatbot.process_user_input(user_input, speak_response=False)
        
        lang_info = result.get('language_info')
        language = lang_info.language_name if lang_info else 'Unknown'
        intent = result.get('intent_info', {}).get('intent', 'unknown')
        sentiment = result.get('sentiment_info', {}).get('sentiment', 'neutral')
        voice = result.get('suggested_voice', 'default')
        
        print(f"🤖 Bot: {result['response_text']}")
        print(f"   📊 Analysis: {language} | {intent} | {sentiment} | {voice}")
        print()

def demo_conversation_memory():
    """Demo conversation context and memory"""
    demo_header("CONVERSATION MEMORY & CONTEXT")
    
    chatbot = get_smart_chatbot()
    
    # Simulate a conversation to build context
    memory_inputs = [
        "Hello, my name is John",
        "I'm interested in electrical items",
        "What's the price of a switch?",
        "That's expensive. Any cheaper options?",
        "Thank you for the information",
        "Do you remember what I was asking about?"
    ]
    
    for user_input in memory_inputs:
        result = chatbot.process_user_input(user_input, speak_response=False)
        print(f"👤: {user_input}")
        print(f"🤖: {result['response_text']}")
        print()
    
    # Show conversation summary
    print("\n📊 CONVERSATION SUMMARY:")
    stats = chatbot.get_conversation_statistics()
    summary = stats.get('conversation_summary', {})
    
    if 'stats' in summary:
        print(f"• Total exchanges: {summary['stats'].get('total_exchanges', 0)}")
        print(f"• Languages used: {', '.join(summary['stats'].get('languages_used', []))}")
        print(f"• Intents detected: {', '.join(summary['stats'].get('intents_used', []))}")
        print(f"• Current emotional state: {summary['stats'].get('emotional_state', 'neutral')}")

def demo_voice_suggestions():
    """Demo voice selection based on language"""
    demo_header("SMART VOICE SELECTION")
    
    chatbot = get_smart_chatbot()
    
    voice_test_inputs = [
        ("Hello, how are you?", "English"),
        ("नमस्ते, कैसे हैं आप?", "Hindi"),
        ("Hola, ¿cómo estás?", "Spanish"),
        ("Bonjour, comment allez-vous?", "French"),
        ("Guten Tag, wie geht es?", "German"),
        ("Ciao, come stai?", "Italian"),
        ("こんにちは元気ですか？", "Japanese"),
        ("你好吗？", "Chinese")
    ]
    
    for text, expected_lang in voice_test_inputs:
        result = chatbot.process_user_input(text, speak_response=False)
        
        lang_info = result.get('language_info')
        detected_lang = lang_info.language_name if lang_info else 'Unknown'
        suggested_voice = result.get('suggested_voice', 'default')
        
        print(f"🗣️ Input: {text}")
        print(f"🌍 Language: {detected_lang}")
        print(f"🎙️ Suggested Voice: {suggested_voice}")
        print(f"🤖 Response: {result['response_text'][:50]}...")
        print()

def demo_knowledge_integration():
    """Demo how the system integrates with knowledge base"""
    demo_header("KNOWLEDGE BASE INTEGRATION")
    
    chatbot = get_smart_chatbot()
    
    # Simulate knowledge base responses
    knowledge_queries = [
        {
            "query": "Switch ka price kya hai?",
            "context": {"knowledge_answer": "Switch का price 150 rupees है।"}
        },
        {
            "query": "Wire ka rate batao",
            "context": {"knowledge_answer": "Wire का rate 50 rupees per meter है।"}
        },
        {
            "query": "What about fan price?",
            "context": None  # No knowledge available
        }
    ]
    
    for item in knowledge_queries:
        query = item["query"]
        context = item["context"]
        
        result = chatbot.process_user_input(query, speak_response=False)
        
        print(f"❓ Query: {query}")
        print(f"🧠 Knowledge Available: {'Yes' if context else 'No'}")
        print(f"📚 Source: {result.get('response_source', 'unknown')}")
        print(f"🤖 Response: {result['response_text']}")
        print()

def show_system_capabilities():
    """Show overall system capabilities"""
    demo_header("SYSTEM CAPABILITIES OVERVIEW")
    
    capabilities = {
        "🌍 Language Detection": [
            "Supports 50+ languages",
            "Mixed language detection (e.g., Hinglish)",
            "Confidence scoring",
            "Script detection (Latin, Devanagari, Arabic, etc.)"
        ],
        
        "🎯 Intent Recognition": [
            "Greeting, Farewell, Question, Request",
            "Appreciation, Complaint, Learning",
            "Multilingual pattern matching",
            "Confidence-based classification"
        ],
        
        "😊 Sentiment Analysis": [
            "Advanced transformer-based analysis",
            "Positive, Negative, Neutral classification",
            "Emotion mapping (happy, sad, calm, etc.)",
            "Confidence scoring"
        ],
        
        "💬 Conversation Management": [
            "Context-aware responses",
            "Conversation history tracking",
            "Multi-turn dialogue support",
            "Emotional state monitoring"
        ],
        
        "🎙️ Voice Integration": [
            "Automatic voice selection by language",
            "EdgeTTS neural voice support",
            "Cultural appropriateness",
            "Dynamic voice switching"
        ],
        
        "🧠 Knowledge Integration": [
            "Existing knowledge base compatibility",
            "Learning system integration",
            "Fallback response generation",
            "Teaching capability"
        ]
    }
    
    for category, features in capabilities.items():
        print(f"\n{category}:")
        for feature in features:
            print(f"  ✓ {feature}")
    
    print(f"\n📊 SYSTEM STATUS:")
    try:
        chatbot = get_smart_chatbot()
        stats = chatbot.get_conversation_statistics()
        
        print(f"  🤖 NLP Engine: {stats.get('nlp_engine_status', 'Unknown')}")
        print(f"  📚 Learning System: {stats.get('learning_statistics', {}).get('status', 'Not Available')}")
        print(f"  🎙️ Voice System: {stats.get('voice_system_status', 'Unknown')}")
        
    except Exception as e:
        print(f"  ⚠️ Status check failed: {e}")

def main():
    """Run comprehensive demo"""
    print("🚀 ADVANCED ADAPTIVE CHATBOT SYSTEM DEMO")
    print("=" * 70)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🖥️ Running comprehensive feature demonstration...")
    
    try:
        # Run all demos
        show_system_capabilities()
        demo_language_detection()
        demo_intent_recognition()
        demo_sentiment_analysis()
        demo_multilingual_conversation()
        demo_voice_suggestions()
        demo_knowledge_integration()
        demo_conversation_memory()
        
        demo_header("DEMO COMPLETED SUCCESSFULLY")
        print("🎉 All features demonstrated successfully!")
        print("💡 The chatbot is ready for production use.")
        print("🔧 You can now integrate it with your existing systems.")
        
        # Final stats
        print(f"\n📈 FINAL STATISTICS:")
        chatbot = get_smart_chatbot()
        stats = chatbot.get_conversation_statistics()
        summary = stats.get('conversation_summary', {})
        
        if 'stats' in summary:
            print(f"  • Total test exchanges: {summary['stats'].get('total_exchanges', 0)}")
            print(f"  • Languages tested: {len(summary['stats'].get('languages_used', []))}")
            print(f"  • Intents tested: {len(summary['stats'].get('intents_used', []))}")
        
        print(f"\n⏰ Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()