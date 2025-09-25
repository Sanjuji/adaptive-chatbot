#!/usr/bin/env python3
"""
🚀 AI-Powered Adaptive Chatbot Launcher
Final integrated system with all advanced features
"""

import sys
import os
import argparse
import time
from datetime import datetime

def print_banner():
    """Print startup banner"""
    banner = """
    ╔════════════════════════════════════════════════════════════════════════╗
    ║                                                                        ║
    ║    🤖 AI-POWERED ADAPTIVE CHATBOT 2.0                                 ║ 
    ║                                                                        ║
    ║    🧠 Advanced NLP & Multilingual Intelligence                        ║
    ║    🔌 Specialized Electrical Business Domain                          ║
    ║    🗣️ Voice-Enabled Conversation System                              ║
    ║    📚 Intelligent Learning & Knowledge Management                     ║
    ║                                                                        ║
    ╚════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)
    
def check_dependencies():
    """Check and report system dependencies"""
    print("🔍 Checking system dependencies...")
    
    dependencies = {
        "Core Systems": ["config", "logger", "validators"],
        "Voice Interface": ["simple_voice", "edge_tts", "speech_recognition", "pygame"],
        "Learning System": ["unified_learning_manager"],
        "Advanced NLP": ["advanced_nlp", "transformers", "torch", "langdetect", "textblob"],
        "Business Logic": ["electrical_business_enhancer", "nlp_integration"],
        "Integration": ["intelligent_integration_bridge"]
    }
    
    missing_deps = []
    available_systems = []
    
    for category, deps in dependencies.items():
        category_available = True
        for dep in deps:
            try:
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

def show_system_info():
    """Show system information"""
    print("\n📊 SYSTEM INFORMATION:")
    print(f"  🕒 Launch Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  🐍 Python Version: {sys.version.split()[0]}")
    print(f"  💾 Platform: {sys.platform}")
    print(f"  📂 Working Directory: {os.getcwd()}")

def launch_intelligent_bridge():
    """Launch the intelligent integration bridge"""
    try:
        print("\n🧠 Launching Intelligent Integration Bridge...")
        from intelligent_integration_bridge import get_intelligent_bridge
        
        bridge = get_intelligent_bridge()
        print("✅ Intelligent Bridge initialized successfully!")
        
        return bridge
        
    except ImportError as e:
        print(f"❌ Failed to import intelligent bridge: {e}")
        return None
    except Exception as e:
        print(f"❌ Failed to initialize intelligent bridge: {e}")
        return None

def launch_enhanced_chatbot():
    """Launch the enhanced chatbot interface"""
    try:
        print("\n🤖 Launching Enhanced Chatbot Interface...")
        from adaptive_chatbot_enhanced import EnhancedAdaptiveChatbot
        
        chatbot = EnhancedAdaptiveChatbot()
        print("✅ Enhanced Chatbot initialized successfully!")
        
        return chatbot
        
    except ImportError as e:
        print(f"❌ Failed to import enhanced chatbot: {e}")
        return None
    except Exception as e:
        print(f"❌ Failed to initialize enhanced chatbot: {e}")
        return None

def run_quick_test(bridge=None):
    """Run a quick system test"""
    if not bridge:
        print("⚠️ Skipping quick test (no bridge available)")
        return
    
    print("\n🧪 Running Quick System Test...")
    
    test_queries = [
        "Hello!",
        "Switch ka price kya hai?",
        "नमस्ते",
        "Thank you!"
    ]
    
    success_count = 0
    
    for query in test_queries:
        try:
            result = bridge.process_intelligent_query(query)
            if result.get("success"):
                success_count += 1
                print(f"  ✅ '{query}' -> Success")
            else:
                print(f"  ❌ '{query}' -> Failed")
        except Exception as e:
            print(f"  ❌ '{query}' -> Error: {e}")
    
    print(f"\n📊 Test Results: {success_count}/{len(test_queries)} passed")
    
    if success_count == len(test_queries):
        print("🎉 All systems operational!")
    else:
        print("⚠️ Some systems may have issues")

def show_feature_summary():
    """Show available features"""
    features = {
        "🌍 Multilingual Support": [
            "Language detection for 50+ languages",
            "Mixed language handling (Hinglish, etc.)",
            "Cultural context awareness",
            "Automatic voice selection"
        ],
        
        "🧠 Advanced AI Capabilities": [
            "Intent recognition & classification",
            "Sentiment analysis with confidence scoring", 
            "Context-aware conversation memory",
            "Transformer-based response generation"
        ],
        
        "🔌 Electrical Business Intelligence": [
            "Product identification & categorization",
            "Price inquiry handling",
            "Installation & service requests",
            "Technical specification queries"
        ],
        
        "🗣️ Voice Interface": [
            "EdgeTTS high-quality speech synthesis",
            "Speech recognition with multiple engines",
            "Language-appropriate voice selection",
            "Conversation flow management"
        ],
        
        "📚 Learning & Knowledge": [
            "Dynamic knowledge acquisition",
            "Fuzzy matching for query variations",
            "Usage-based optimization",
            "Backup & recovery systems"
        ],
        
        "⚙️ System Integration": [
            "Intelligent response prioritization",
            "Multiple knowledge source fusion",
            "Performance monitoring",
            "Comprehensive error handling"
        ]
    }
    
    print("\n🎯 AVAILABLE FEATURES:")
    for category, feature_list in features.items():
        print(f"\n{category}:")
        for feature in feature_list:
            print(f"  • {feature}")

def interactive_mode(chatbot=None, bridge=None):
    """Run interactive mode"""
    print("\n🎮 INTERACTIVE MODE")
    print("=" * 50)
    
    if chatbot:
        print("🤖 Enhanced Chatbot Interface Available")
        chatbot.run_interactive_menu()
    elif bridge:
        print("🧠 Using Intelligent Bridge Interface")
        
        print("💬 Type your messages (type 'exit' to quit):")
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("🤖 Goodbye! Thanks for chatting!")
                    break
                
                if not user_input:
                    continue
                
                # Process with intelligent bridge
                result = bridge.process_intelligent_query(user_input)
                print(f"🤖 AI: {result['response_text']}")
                
                # Show analysis (optional)
                if result.get('confidence', 0) > 0.8:
                    print(f"   💯 High confidence response")
                
            except KeyboardInterrupt:
                print("\n🤖 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    else:
        print("❌ No chatbot interface available")

def demo_mode(bridge=None):
    """Run demonstration mode"""
    if not bridge:
        print("❌ Demo mode requires intelligent bridge")
        return
    
    print("\n🎭 DEMO MODE")
    print("=" * 40)
    
    print("🌍 Multilingual Conversation Demo:")
    
    demo_conversations = [
        ("English", "Hello! What electrical items do you have?"),
        ("Hindi", "नमस्ते! Switch का price क्या है?"),
        ("Mixed", "Wire kitne ka milta hai bhai?"),
        ("Business", "Do you provide installation service?"),
        ("Technical", "What MCB rating do I need?"),
        ("Appreciation", "धन्यवाद for your help!"),
    ]
    
    for lang_type, query in demo_conversations:
        print(f"\n🗣️ {lang_type}: {query}")
        
        try:
            result = bridge.process_intelligent_query(query)
            
            print(f"🤖 Response: {result['response_text']}")
            print(f"📊 Analysis: {result['confidence']:.2f} confidence | "
                  f"{result['response_type']} | {result['processing_time']}s")
            
            # Show electrical context if available
            electrical = result.get('analysis', {}).get('electrical', {})
            if electrical.get('identified_products'):
                products = [p['product'] for p in electrical['identified_products']]
                print(f"🔌 Products: {', '.join(products)}")
                
        except Exception as e:
            print(f"❌ Demo error: {e}")
        
        time.sleep(1)  # Brief pause between demos
    
    # Show final statistics
    print(f"\n📊 DEMO STATISTICS:")
    try:
        stats = bridge.get_intelligent_statistics()
        interaction_stats = stats.get('interaction_stats', {})
        print(f"• Conversations: {interaction_stats.get('total_interactions', 0)}")
        print(f"• Success Rate: {interaction_stats.get('success_rate', 0):.1f}%")
        print(f"• Electrical Queries: {interaction_stats.get('electrical_queries', 0)}")
    except Exception as e:
        print(f"Stats unavailable: {e}")

def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(description='AI-Powered Adaptive Chatbot Launcher')
    parser.add_argument('--mode', choices=['interactive', 'demo', 'test', 'info'], 
                       default='interactive', help='Launch mode')
    parser.add_argument('--skip-test', action='store_true', help='Skip system test')
    parser.add_argument('--minimal', action='store_true', help='Minimal output mode')
    
    args = parser.parse_args()
    
    try:
        # Print banner
        if not args.minimal:
            print_banner()
            show_system_info()
        
        # Check dependencies
        missing_deps, available_systems = check_dependencies()
        
        if missing_deps and not args.minimal:
            print(f"\n⚠️ Missing dependencies:")
            for dep in missing_deps[:5]:  # Show first 5
                print(f"  • {dep}")
            if len(missing_deps) > 5:
                print(f"  ... and {len(missing_deps) - 5} more")
        
        print(f"\n✅ Available Systems: {len(available_systems)}")
        
        # Initialize systems
        bridge = launch_intelligent_bridge()
        chatbot = launch_enhanced_chatbot()
        
        if not bridge and not chatbot:
            print("❌ Failed to initialize any chatbot system")
            sys.exit(1)
        
        # Run system test
        if not args.skip_test and bridge:
            run_quick_test(bridge)
        
        # Show features
        if args.mode == 'info':
            show_feature_summary()
            return
        
        # Run selected mode
        if args.mode == 'interactive':
            interactive_mode(chatbot, bridge)
        elif args.mode == 'demo':
            demo_mode(bridge)
        elif args.mode == 'test':
            run_quick_test(bridge)
            if bridge:
                stats = bridge.get_intelligent_statistics()
                print(f"\n📊 System Stats: {stats}")
        
        print(f"\n✅ AI Chatbot session completed successfully!")
        
    except KeyboardInterrupt:
        print(f"\n👋 Goodbye! Session terminated by user.")
    except Exception as e:
        print(f"❌ Launcher error: {e}")
        sys.exit(1)
    finally:
        print(f"🕒 Session ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()