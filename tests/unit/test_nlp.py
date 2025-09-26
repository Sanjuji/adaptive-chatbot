#!/usr/bin/env python3
"""
Demo script for Advanced NLP System
Tests multilingual conversation capabilities
"""

import sys
import json
from datetime import datetime

# Import the advanced NLP module
try:
    from nlp.advanced_nlp import get_nlp_engine, analyze_and_respond, detect_language
    from utils.logger import log_info, log_error
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_language_detection():
    """Test language detection capabilities"""
    print("=" * 60)
    print("🌍 LANGUAGE DETECTION TEST")
    print("=" * 60)
    
    test_texts = [
        ("Hello, how are you?", "en"),
        ("नमस्ते, आप कैसे हैं?", "hi"),
        ("Hola, ¿cómo estás?", "es"),
        ("Bonjour, comment ça va?", "fr"),
        ("Guten Tag, wie geht es Ihnen?", "de"),
        ("Switch ka price kya hai?", "hi"),  # Hinglish
        ("मैं ठीक हूँ thanks", "hi"),  # Mixed
        ("Ciao, come stai?", "it"),
        ("こんにちは、元気ですか？", "ja"),
        ("你好吗？", "zh")
    ]
    
    nlp = get_nlp_engine()
    
    for text, expected in test_texts:
        lang_info = nlp.detect_language(text)
        status = "✅" if lang_info.detected_language == expected else "⚠️"
        
        print(f"{status} Text: {text}")
        print(f"   Detected: {lang_info.language_name} ({lang_info.detected_language})")
        print(f"   Expected: {expected}")
        print(f"   Confidence: {lang_info.confidence:.2f}")
        print(f"   Mixed: {lang_info.is_mixed_language}")
        if lang_info.dominant_languages:
            print(f"   Dominant: {lang_info.dominant_languages}")
        print()

def test_intent_recognition():
    """Test intent recognition"""
    print("=" * 60)
    print("🎯 INTENT RECOGNITION TEST")
    print("=" * 60)
    
    test_cases = [
        ("Hi there!", "greeting"),
        ("नमस्ते", "greeting"),
        ("Good morning", "greeting"),
        ("Bye bye", "farewell"),
        ("अलविदा", "farewell"),
        ("What is the price of switch?", "question"),
        ("Switch ka price kya hai?", "question"),
        ("Can you help me?", "request"),
        ("Please tell me about this", "request"),
        ("Thanks a lot!", "appreciation"),
        ("धन्यवाद", "appreciation"),
        ("I have a problem", "complaint"),
        ("समस्या है", "complaint"),
        ("Teach me how to do this", "learning"),
        ("मुझे सिखाओ", "learning"),
        ("I like this weather", "general")
    ]
    
    nlp = get_nlp_engine()
    
    for text, expected in test_cases:
        intent_info = nlp.extract_intent(text)
        status = "✅" if intent_info['intent'] == expected else "⚠️"
        
        print(f"{status} Text: {text}")
        print(f"   Intent: {intent_info['intent']} (confidence: {intent_info['confidence']:.2f})")
        print(f"   Expected: {expected}")
        if intent_info['entities']:
            print(f"   Entities: {intent_info['entities']}")
        print()

def test_conversation_flow():
    """Test full conversation flow"""
    print("=" * 60)
    print("💬 CONVERSATION FLOW TEST")
    print("=" * 60)
    
    conversation_tests = [
        "Hello!",
        "How are you?",
        "Switch ka price kya hai?",
        "Thank you for helping!",
        "I have a problem with my device",
        "नमस्ते भाई",
        "क्या हाल है?",
        "बहुत अच्छा काम किया है",
        "Goodbye!"
    ]
    
    nlp = get_nlp_engine()
    
    for i, user_input in enumerate(conversation_tests, 1):
        print(f"👤 User ({i}): {user_input}")
        
        # Generate response
        result = nlp.generate_response(user_input)
        
        print(f"🤖 Bot: {result['response_text']}")
        print(f"   Language: {result['language_info'].language_name}")
        print(f"   Intent: {result['intent_info']['intent']}")
        print(f"   Sentiment: {result['sentiment_info']['sentiment']}")
        print(f"   Suggested Voice: {result['suggested_voice']}")
        print()

def test_multilingual_responses():
    """Test responses in different languages"""
    print("=" * 60)
    print("🌐 MULTILINGUAL RESPONSE TEST")
    print("=" * 60)
    
    greetings = [
        "Hello!",
        "नमस्ते!",
        "¡Hola!",
        "Bonjour!",
        "Guten Tag!"
    ]
    
    nlp = get_nlp_engine()
    
    for greeting in greetings:
        result = nlp.generate_response(greeting)
        print(f"Input: {greeting}")
        print(f"Response: {result['response_text']}")
        print(f"Language: {result['language_info'].language_name}")
        print(f"Voice: {result['suggested_voice']}")
        print("-" * 40)

def test_sentiment_analysis():
    """Test sentiment analysis"""
    print("=" * 60)
    print("😊 SENTIMENT ANALYSIS TEST")
    print("=" * 60)
    
    sentiment_tests = [
        ("I love this product!", "positive"),
        ("This is absolutely terrible", "negative"),
        ("It's okay, nothing special", "neutral"),
        ("मुझे यह बहुत पसंद है!", "positive"),
        ("यह बिल्कुल खराब है", "negative"),
        ("ठीक है, कोई खास बात नहीं", "neutral"),
        ("Amazing work! Outstanding!", "positive"),
        ("I'm really frustrated with this", "negative")
    ]
    
    nlp = get_nlp_engine()
    
    for text, expected in sentiment_tests:
        sentiment_info = nlp.analyze_sentiment(text)
        status = "✅" if sentiment_info['sentiment'] == expected else "⚠️"
        
        print(f"{status} Text: {text}")
        print(f"   Sentiment: {sentiment_info['sentiment']} ({sentiment_info['confidence']:.2f})")
        print(f"   Emotion: {sentiment_info['emotion']}")
        print(f"   Expected: {expected}")
        print()

def demonstrate_knowledge_integration():
    """Demonstrate integration with existing knowledge base"""
    print("=" * 60)
    print("🧠 KNOWLEDGE INTEGRATION DEMO")
    print("=" * 60)
    
    # Simulate knowledge base answers
    knowledge_examples = [
        {
            "query": "Switch ka price kya hai?",
            "context": {"knowledge_answer": "Switch ka price 150 rupees hai."}
        },
        {
            "query": "Wire ka rate batao",
            "context": {"knowledge_answer": "Wire ka rate 50 rupees per meter hai."}
        },
        {
            "query": "How much does a socket cost?",
            "context": {"knowledge_answer": "Socket costs around 80 rupees."}
        }
    ]
    
    nlp = get_nlp_engine()
    
    for example in knowledge_examples:
        result = nlp.generate_response(example["query"], example["context"])
        print(f"Query: {example['query']}")
        print(f"Response: {result['response_text']}")
        print(f"Language: {result['language_info'].language_name}")
        print("-" * 40)

def show_conversation_summary():
    """Show conversation summary"""
    print("=" * 60)
    print("📊 CONVERSATION SUMMARY")
    print("=" * 60)
    
    nlp = get_nlp_engine()
    summary = nlp.get_conversation_summary()
    
    print(json.dumps(summary, indent=2, default=str))

def main():
    """Run all tests"""
    print("🚀 Advanced NLP System Test Suite")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Run tests
        test_language_detection()
        test_intent_recognition()
        test_sentiment_analysis()
        test_multilingual_responses()
        test_conversation_flow()
        demonstrate_knowledge_integration()
        show_conversation_summary()
        
        print("=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()