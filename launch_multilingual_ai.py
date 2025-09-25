#!/usr/bin/env python3
"""
🌍 Advanced Multilingual AI Chatbot Launcher
Full integration with EdgeTTS multilingual voice system
"""

import sys
import os
import argparse
import time
import asyncio
from datetime import datetime
from typing import Dict, Optional, Any

def print_multilingual_banner():
    """Print enhanced multilingual banner"""
    banner = """
    ╔════════════════════════════════════════════════════════════════════════╗
    ║                                                                        ║
    ║    🌍 MULTILINGUAL AI CHATBOT 3.0                                     ║ 
    ║                                                                        ║
    ║    🗣️ EdgeTTS Voice Synthesis (15+ Languages)                        ║
    ║    🧠 Advanced NLP & Language Detection                               ║
    ║    🔌 Electrical Business Intelligence                                ║
    ║    📚 Intelligent Learning & Memory                                   ║
    ║    🎙️ Dynamic Voice Switching                                        ║
    ║                                                                        ║
    ╚════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)
    
def check_multilingual_dependencies():
    """Check multilingual system dependencies"""
    print("🔍 Checking multilingual dependencies...")
    
    dependencies = {
        "Multilingual Voice": ["edge_tts", "pygame", "asyncio", "io"],
        "Language Detection": ["langdetect", "textblob"],
        "Core Multilingual": ["multilingual_voice_system", "advanced_multilingual_bridge"],
        "Base Systems": ["adaptive_chatbot_enhanced", "intelligent_integration_bridge"],
        "Advanced NLP": ["transformers", "torch", "advanced_nlp"],
        "Business Logic": ["electrical_business_enhancer"],
        "Utilities": ["logger", "config", "validators"]
    }
    
    missing_deps = []
    available_systems = []
    
    for category, deps in dependencies.items():
        category_available = True
        for dep in deps:
            try:
                if "." not in dep:  # Skip checking built-in modules
                    __import__(dep)
            except ImportError:
                missing_deps.append(f"{category}: {dep}")
                category_available = False
        
        if category_available:
            available_systems.append(category)
            print(f"  ✅ {category}")
        else:
            print(f"  ⚠️ {category} (partial)")
    
    return missing_deps, available_systems

def show_multilingual_features():
    """Show multilingual features"""
    features = {
        "🌍 Multilingual Voice Synthesis": [
            "EdgeTTS integration with 60+ neural voices",
            "Auto-language detection and voice switching",
            "SSML-based emotion and style control",
            "Voice caching for performance optimization",
            "Language-specific prosody adjustment"
        ],
        
        "🗣️ Supported Languages": [
            "English (US, UK, IN) - 5 voices",
            "Hindi (Devanagari script) - 3 voices", 
            "Spanish (ES, MX) - 3 voices",
            "French (FR, CA) - 3 voices",
            "German (DE, AT) - 3 voices",
            "Chinese, Japanese, Korean, Arabic, Russian, Turkish"
        ],
        
        "🧠 Advanced Language Processing": [
            "Real-time language detection with confidence scoring",
            "Cultural context awareness for responses",
            "Mixed-language handling (Hinglish, Spanglish)",
            "Language-specific conversation memory",
            "Automatic politeness adaptation"
        ],
        
        "🎙️ Voice Intelligence": [
            "Context-aware voice style selection",
            "Sentiment-based prosody adjustment",
            "Gender and age preference support",
            "Voice consistency across conversations",
            "Dynamic quality optimization"
        ],
        
        "🔌 Business Intelligence": [
            "Multilingual product recognition",
            "Cross-language price inquiries",
            "Technical specifications in local language",
            "Service requests with cultural adaptation"
        ],
        
        "📊 Performance & Analytics": [
            "Voice synthesis success monitoring",
            "Language accuracy tracking",
            "Response time optimization",
            "User satisfaction scoring",
            "Conversation flow analytics"
        ]
    }
    
    print("\n🎯 MULTILINGUAL FEATURES:")
    for category, feature_list in features.items():
        print(f"\n{category}:")
        for feature in feature_list:
            print(f"  • {feature}")

async def launch_multilingual_bridge():
    """Launch the multilingual bridge system"""
    try:
        print("\n🌍 Launching Advanced Multilingual Bridge...")
        from advanced_multilingual_bridge import get_multilingual_bridge
        
        bridge = get_multilingual_bridge()
        print("✅ Multilingual Bridge initialized successfully!")
        
        # Show voice statistics
        voice_stats = bridge.voice_system.get_voice_statistics()
        print(f"   📊 {voice_stats['total_languages']} languages, {voice_stats['total_voices']} voices available")
        
        return bridge
        
    except ImportError as e:
        print(f"❌ Failed to import multilingual bridge: {e}")
        return None
    except Exception as e:
        print(f"❌ Failed to initialize multilingual bridge: {e}")
        return None

async def run_multilingual_test(bridge=None):
    """Run comprehensive multilingual test"""
    if not bridge:
        print("⚠️ Skipping multilingual test (no bridge available)")
        return
    
    print("\n🧪 Running Multilingual System Test...")
    
    test_queries = [
        ("Hello! Welcome to our electrical shop.", "en", "positive"),
        ("नमस्ते! LED bulb की price क्या है?", "hi", "inquiry"),
        ("¿Cuánto cuesta un ventilador de techo?", "es", "inquiry"),
        ("Merci beaucoup for your excellent service!", "fr", "appreciation"),
        ("Wire installation ki service available hai?", "hi", "service_request"),
        ("Thank you for helping me!", "en", "appreciation")
    ]
    
    success_count = 0
    total_response_time = 0
    voice_success_count = 0
    
    for i, (query, expected_lang, context_type) in enumerate(test_queries, 1):
        print(f"\n🔄 Test {i}/{len(test_queries)}: {expected_lang}")
        print(f"   Query: {query}")
        
        try:
            # Process multilingual query
            response = await bridge.process_multilingual_query(
                query, expected_lang, {"context_type": context_type}
            )
            
            # Check results
            if response.text and response.language:
                success_count += 1
                total_response_time += response.response_time
                if response.voice_generated:
                    voice_success_count += 1
                
                print(f"   ✅ Response ({response.language}): {response.text[:60]}...")
                print(f"   📊 Confidence: {response.confidence:.2f} | Time: {response.response_time:.2f}s | Voice: {response.voice_generated}")
            else:
                print(f"   ❌ Invalid response received")
                
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
        
        await asyncio.sleep(0.5)  # Brief pause
    
    # Show test summary
    print(f"\n📊 MULTILINGUAL TEST RESULTS:")
    print(f"   • Success Rate: {success_count}/{len(test_queries)} ({success_count/len(test_queries):.1%})")
    print(f"   • Voice Success: {voice_success_count}/{len(test_queries)} ({voice_success_count/len(test_queries):.1%})")
    if success_count > 0:
        print(f"   • Avg Response Time: {total_response_time/success_count:.2f}s")
    
    # Show system statistics
    stats = bridge.get_multilingual_statistics()
    print(f"   • Languages Used: {', '.join(stats['session_stats']['languages_used'])}")
    print(f"   • Cache Size: {stats['voice_system']['cache_size']} audio files")
    
    if success_count == len(test_queries):
        print("🎉 All multilingual systems operational!")
    else:
        print("⚠️ Some multilingual features may have issues")

async def demo_multilingual_conversation(bridge=None):
    """Run multilingual conversation demo"""
    if not bridge:
        print("❌ Multilingual demo requires bridge")
        return
    
    print("\n🎭 MULTILINGUAL CONVERSATION DEMO")
    print("=" * 50)
    
    demo_scenarios = [
        {
            "title": "🇺🇸 English Customer Inquiry",
            "query": "Hello! I need a ceiling fan for my living room. What options do you have?",
            "language": "en"
        },
        {
            "title": "🇮🇳 Hindi Mixed Language Query", 
            "query": "नमस्ते भाई! Switch board ki latest price बताइए।",
            "language": "hi"
        },
        {
            "title": "🇪🇸 Spanish Product Inquiry",
            "query": "¡Hola! ¿Tienen cables eléctricos para instalación doméstica?",
            "language": "es"
        },
        {
            "title": "🇫🇷 French Technical Question",
            "query": "Bonjour! Quel type de disjoncteur recommandez-vous pour une maison?",
            "language": "fr"
        },
        {
            "title": "🌍 Auto-Detect Mixed Languages",
            "query": "Thank you! आपकी service बहुत अच्छी है। Merci beaucoup!",
            "language": None
        }
    ]
    
    for i, scenario in enumerate(demo_scenarios, 1):
        print(f"\n🎬 Scenario {i}: {scenario['title']}")
        print(f"   Customer: {scenario['query']}")
        
        try:
            # Process with multilingual bridge
            response = await bridge.process_multilingual_query(
                scenario['query'], 
                scenario['language'],
                {"demo_mode": True, "context_type": "customer_inquiry"}
            )
            
            print(f"   🤖 AI ({response.language}): {response.text}")
            print(f"   📊 Analysis: {response.sentiment} sentiment | {response.confidence:.2f} confidence")
            print(f"   🎙️ Voice: {'✅ Generated' if response.voice_generated else '❌ Failed'}")
            print(f"   ⏱️ Response Time: {response.response_time:.2f}s")
            
            # Show detected context
            context = response.context
            if context.get('detected_language'):
                print(f"   🔍 Detected: {context['detected_language']} (confidence: {context.get('language_confidence', 0):.2f})")
            
        except Exception as e:
            print(f"   ❌ Demo error: {e}")
        
        await asyncio.sleep(2)  # Pause between scenarios
    
    # Final statistics
    print(f"\n🏁 DEMO COMPLETED")
    stats = bridge.get_multilingual_statistics()
    session_stats = stats['session_stats']
    
    print(f"📊 Session Summary:")
    print(f"   • Total Interactions: {session_stats['total_interactions']}")
    print(f"   • Languages Used: {', '.join(session_stats['languages_used'])}")
    print(f"   • Average Response Time: {session_stats['average_response_time']:.2f}s")
    print(f"   • Voice Success Rate: {session_stats['voice_success_rate']:.1%}")
    print(f"   • Multilingual Accuracy: {session_stats['multilingual_accuracy']:.1%}")

async def interactive_multilingual_mode(bridge=None):
    """Run interactive multilingual conversation mode"""
    if not bridge:
        print("❌ Interactive mode requires multilingual bridge")
        return
    
    print("\n🎮 INTERACTIVE MULTILINGUAL MODE")
    print("=" * 50)
    print("🌍 Speak in any supported language! The AI will auto-detect and respond appropriately.")
    print("📝 Commands: 'exit', 'quit', 'stats', 'voices', 'config'")
    print("💬 Start typing your messages:")
    
    conversation_count = 0
    
    while True:
        try:
            # Get user input
            user_input = input(f"\n👤 You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                print("🤖 Goodbye! Thanks for the multilingual chat!")
                break
            elif user_input.lower() == 'stats':
                # Show current statistics
                stats = bridge.get_multilingual_statistics()
                session_stats = stats['session_stats']
                print(f"📊 Current Session Stats:")
                print(f"   • Conversations: {session_stats['total_interactions']}")
                print(f"   • Languages: {', '.join(session_stats['languages_used'])}")
                print(f"   • Avg Time: {session_stats['average_response_time']:.2f}s")
                print(f"   • Voice Success: {session_stats['voice_success_rate']:.1%}")
                continue
            elif user_input.lower() == 'voices':
                # Show available voices
                voice_system = bridge.voice_system
                print(f"🎙️ Available Voice Systems:")
                for lang in ['en', 'hi', 'es', 'fr', 'de']:
                    voices = voice_system.get_available_voices(lang)
                    if voices:
                        print(f"   • {lang.upper()}: {len(voices)} voices")
                continue
            elif user_input.lower() == 'config':
                # Show configuration
                print(f"⚙️ Current Configuration:")
                for key, value in bridge.config.items():
                    print(f"   • {key}: {value}")
                continue
            elif not user_input:
                continue
            
            # Process multilingual query
            print(f"   🔄 Processing...")
            
            response = await bridge.process_multilingual_query(
                user_input,
                None,  # Auto-detect language
                {
                    "conversation_mode": "interactive",
                    "conversation_count": conversation_count
                }
            )
            
            # Display response
            print(f"🤖 AI ({response.language}): {response.text}")
            
            # Show quick analysis
            if response.confidence > 0.8:
                print(f"   💯 High confidence response")
            elif response.confidence < 0.5:
                print(f"   ❓ Low confidence - please clarify")
            
            if response.voice_generated:
                print(f"   🔊 Voice response played")
            
            conversation_count += 1
            
        except KeyboardInterrupt:
            print(f"\n🤖 Chat interrupted. Thanks for using multilingual AI!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again or type 'exit' to quit.")

async def main():
    """Async main launcher function"""
    parser = argparse.ArgumentParser(description='Multilingual AI Chatbot Launcher')
    parser.add_argument('--mode', choices=['interactive', 'demo', 'test', 'info', 'voices'], 
                       default='interactive', help='Launch mode')
    parser.add_argument('--language', type=str, help='Preferred language (en, hi, es, fr, de, etc.)')
    parser.add_argument('--voice-off', action='store_true', help='Disable voice synthesis')
    parser.add_argument('--skip-test', action='store_true', help='Skip system test')
    parser.add_argument('--minimal', action='store_true', help='Minimal output mode')
    
    args = parser.parse_args()
    
    try:
        # Print banner
        if not args.minimal:
            print_multilingual_banner()
            print(f"\n📊 SYSTEM INFORMATION:")
            print(f"  🕒 Launch Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  🐍 Python Version: {sys.version.split()[0]}")
            print(f"  💾 Platform: {sys.platform}")
            print(f"  📂 Working Directory: {os.getcwd()}")
        
        # Check dependencies
        missing_deps, available_systems = check_multilingual_dependencies()
        
        if missing_deps and not args.minimal:
            print(f"\n⚠️ Missing dependencies:")
            for dep in missing_deps[:5]:  # Show first 5
                print(f"  • {dep}")
            if len(missing_deps) > 5:
                print(f"  ... and {len(missing_deps) - 5} more")
        
        print(f"\n✅ Available Systems: {len(available_systems)}")
        
        # Show features in info mode
        if args.mode == 'info':
            show_multilingual_features()
            return
        
        # Initialize multilingual bridge
        bridge = await launch_multilingual_bridge()
        
        if not bridge:
            print("❌ Failed to initialize multilingual system")
            sys.exit(1)
        
        # Configure based on arguments
        if args.language:
            bridge.configure_multilingual_settings(preferred_language=args.language)
            print(f"🌍 Preferred language set to: {args.language}")
        
        if args.voice_off:
            bridge.configure_multilingual_settings(auto_voice_enabled=False)
            print("🔇 Voice synthesis disabled")
        
        # Run system test
        if not args.skip_test:
            await run_multilingual_test(bridge)
        
        # Run selected mode
        if args.mode == 'interactive':
            await interactive_multilingual_mode(bridge)
        elif args.mode == 'demo':
            await demo_multilingual_conversation(bridge)
        elif args.mode == 'test':
            await run_multilingual_test(bridge)
        elif args.mode == 'voices':
            # Show detailed voice information
            voice_system = bridge.voice_system
            all_voices = voice_system.get_available_voices()
            print(f"\n🎙️ AVAILABLE VOICES ({len(all_voices)} total):")
            
            by_language = {}
            for voice in all_voices:
                lang = voice['language']
                if lang not in by_language:
                    by_language[lang] = []
                by_language[lang].append(voice)
            
            for lang, voices in sorted(by_language.items()):
                print(f"\n{lang.upper()} ({len(voices)} voices):")
                for voice in voices:
                    print(f"  • {voice['name']} ({voice['gender']}, {voice['age_group']}) - Quality: {voice['quality_score']:.1f}")
        
        print(f"\n✅ Multilingual AI session completed successfully!")
        
    except KeyboardInterrupt:
        print(f"\n👋 Goodbye! Session terminated by user.")
    except Exception as e:
        print(f"❌ Launcher error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        print(f"🕒 Session ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    # Run the async main function
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Failed to start multilingual system: {e}")
        sys.exit(1)