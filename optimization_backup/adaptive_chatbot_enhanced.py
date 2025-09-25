#!/usr/bin/env python3
"""
Enhanced Adaptive Chatbot - AI-Powered with Advanced NLP
Integrates advanced multilingual NLP capabilities with existing chatbot systems
"""

import sys
import os
import argparse
import time
from typing import Optional, Dict, Any
import signal
import atexit

# Import existing modules with error handling
try:
    from config import config
    from logger import log_info, log_error, log_warning
except ImportError as e:
    print(f"❌ Critical dependency missing: {e}")
    sys.exit(1)

# Import voice system
try:
    from simple_voice import SimpleVoiceInterface
    voice_interface = SimpleVoiceInterface()
    
    def speak(text): 
        return voice_interface.speak(text)
    def listen(timeout=10): 
        return voice_interface.listen(timeout)
    def is_voice_available(): 
        return voice_interface.microphone is not None
except ImportError as e:
    print(f"❌ Voice interface unavailable: {e}")
    def speak(text): return False
    def listen(timeout=10): return None
    def is_voice_available(): return False

# Import learning system
try:
    from unified_learning_manager import UnifiedLearningManager
    learning_manager = UnifiedLearningManager()
    
    def learn(question, answer):
        return learning_manager.add_knowledge(question, answer)
    def ask(question):
        return learning_manager.find_answer(question)
    def get_stats():
        return learning_manager.get_statistics()
except ImportError as e:
    print(f"❌ Learning system unavailable: {e}")
    sys.exit(1)

# Import advanced NLP system
try:
    from nlp_integration import get_smart_chatbot, smart_chat
    smart_chatbot = get_smart_chatbot()
    NLP_AVAILABLE = True
    log_info("🧠 Advanced NLP system loaded successfully")
except ImportError as e:
    print(f"⚠️ Advanced NLP not available: {e}")
    print("📝 Falling back to basic chatbot functionality")
    NLP_AVAILABLE = False
    smart_chatbot = None

# Import validation
try:
    from validators import sanitize_user_input, is_safe_input
except ImportError as e:
    def sanitize_user_input(text): return str(text).strip() if text else ""
    def is_safe_input(text): return bool(text and len(str(text).strip()) > 0)

class EnhancedAdaptiveChatbot:
    """Enhanced chatbot with AI-powered NLP capabilities"""
    
    def __init__(self):
        self.running = False
        self.current_mode = None
        self.conversation_count = 0
        self.nlp_enabled = NLP_AVAILABLE
        
        # Register cleanup
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all components with error handling"""
        try:
            log_info("🚀 Enhanced Adaptive Chatbot शुरू हो रहा है...")
            
            if self.nlp_enabled:
                log_info("✅ AI-powered NLP system active")
                log_info("🌍 Multilingual support enabled")
                log_info("🎯 Intent recognition active") 
                log_info("😊 Sentiment analysis active")
                log_info("💬 Context-aware responses enabled")
            else:
                log_info("⚠️ Running in basic mode (NLP disabled)")
            
            log_info("✅ Voice interface ready" if is_voice_available() else "⚠️ Voice interface disabled")
            log_info("✅ Learning system ready")
            log_info("🎉 Enhanced Adaptive Chatbot तैयार है!")
            
        except Exception as e:
            log_error("Failed to initialize enhanced chatbot", error=e)
            raise
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        log_info("Interrupt signal received, shutting down gracefully...")
        self.running = False
    
    def run_interactive_menu(self):
        """Run the enhanced interactive menu"""
        while True:
            try:
                self._display_enhanced_menu()
                choice = self._get_user_choice()
                
                if choice == '1':
                    self.run_ai_voice_teaching()
                elif choice == '2':
                    self.run_ai_voice_chat()
                elif choice == '3':
                    self.run_ai_text_chat()
                elif choice == '4':
                    self.run_multilingual_demo()
                elif choice == '5':
                    self.show_ai_statistics()
                elif choice == '6':
                    self.manage_knowledge()
                elif choice == '7':
                    self.configure_settings()
                elif choice == '8':
                    log_info("👋 Goodbye! AI-powered conversation complete!")
                    break
                else:
                    print("❌ Invalid choice! कृपया 1-8 में से choose करें।")
                    
            except KeyboardInterrupt:
                log_info("\n👋 Goodbye! Dhanyawad!")
                break
            except Exception as e:
                log_error("Menu error", error=e)
                print(f"❌ Error: {e}")
    
    def _display_enhanced_menu(self):
        """Display the enhanced main menu with AI features"""
        app_name = config.get('app', 'app_name', 'Enhanced Adaptive Chatbot')
        version = config.get('app', 'version', '2.0.0')
        
        print("\n" + "="*70)
        print(f"🤖 {app_name} v{version}")
        if self.nlp_enabled:
            print("🧠 AI-Powered | 🌍 Multilingual | 🎯 Smart | 💬 Context-Aware")
        print("="*70)
        print("\nChoose your AI interaction mode:")
        
        print("1️⃣  🎓 AI Voice Teaching (आवाज़ से सिखाएं - Smart)")
        print("2️⃣  🗣️  AI Voice Chat (बोलकर बात करें - Intelligent)")  
        print("3️⃣  💬 AI Text Chat (टाइप करके बात करें - Multilingual)")
        print("4️⃣  🌍 Multilingual Demo (भाषा प्रदर्शन)")
        print("5️⃣  📊 AI Analytics (आँकड़े और विश्लेषण)")
        print("6️⃣  🧠 Knowledge Management (ज्ञान प्रबंधन)")
        print("7️⃣  ⚙️  Settings (सेटिंग्स)")
        print("8️⃣  🚪 Exit (बाहर निकलें)")
        
        if self.nlp_enabled:
            stats = smart_chatbot.get_conversation_statistics()
            summary = stats.get('conversation_summary', {})
            if 'stats' in summary and summary['stats'].get('total_exchanges', 0) > 0:
                print(f"\n📊 Session Stats: {summary['stats']['total_exchanges']} exchanges, "
                      f"{len(summary['stats'].get('languages_used', []))} languages")
        
        print("-"*70)
    
    def _get_user_choice(self) -> str:
        """Get user's menu choice with validation"""
        try:
            choice = input("\nEnter your choice (1-8): ").strip()
            return choice
        except EOFError:
            return '8'  # Exit on EOF
        except Exception:
            return ''
    
    def run_ai_voice_teaching(self):
        """AI-powered voice teaching with multilingual support"""
        try:
            if not is_voice_available():
                print("❌ Voice unavailable. Please check microphone and speakers.")
                return
            
            print("\n🎓 AI-Powered Voice Teaching Mode!")
            print("=" * 60)
            print("🧠 Features:")
            print("• Multilingual support (Hindi/English/others)")
            print("• Intent recognition")
            print("• Smart voice selection")
            print("• Context-aware responses")
            print("🎤 Say 'teach' to start, 'exit' to return")
            print("-" * 60)
            
            # AI-powered welcome
            if self.nlp_enabled:
                welcome_msg = "Namaste! Main AI-powered system hun. Multilingual support ke saath ready hun!"
                speak(welcome_msg)
            else:
                speak("Namaste! Voice teaching mode ready hai!")
            
            self.running = True
            while self.running:
                print("\n🎤 AI listening...")
                command = listen(timeout=15)
                
                if not command:
                    speak("Kuch sunaayi nahi diya. Phir se try kariye.")
                    continue
                
                print(f"👤 You said: {command}")
                
                # Exit check
                if any(word in command.lower() for word in ['exit', 'quit', 'bahar', 'nikal', 'bye']):
                    if self.nlp_enabled:
                        response = smart_chat("goodbye", speak=False)
                        speak(response)
                    else:
                        speak("Main menu mein wapas ja rahe hain. Dhanyawad!")
                    break
                
                # Teaching workflow
                if any(word in command.lower() for word in ['teach', 'teech', 'sikha', 'learn', 'sikhao']):
                    self._ai_voice_teaching_workflow()
                else:
                    # AI-powered response to questions
                    if self.nlp_enabled:
                        result = smart_chatbot.process_user_input(command, speak_response=False)
                        
                        # Check if we have knowledge
                        if result.get('knowledge_found'):
                            response = result['response_text']
                        else:
                            # Try traditional learning manager
                            answer = ask(command)
                            if answer:
                                response = f"मुझे मालूम है: {answer}"
                            else:
                                response = result['response_text']
                        
                        # Speak with appropriate voice
                        voice = result.get('suggested_voice', 'hi-IN-MadhurNeural')
                        speak(response)
                        
                        # Show AI analysis
                        lang_info = result.get('language_info')
                        print(f"🧠 AI Analysis: {lang_info.language_name if lang_info else 'Unknown'} | "
                              f"{result.get('intent_info', {}).get('intent', 'unknown')} | "
                              f"{result.get('sentiment_info', {}).get('sentiment', 'neutral')}")
                    else:
                        # Fallback to basic response
                        answer = ask(command)
                        if answer:
                            speak(f"Jawab hai: {answer}")
                        else:
                            speak("Mujhe iska jawab nahi pata. 'teach' boliye!")
                        
        except KeyboardInterrupt:
            speak("Teaching mode band kar raha hun. Alvida!")
        except Exception as e:
            log_error("AI voice teaching error", error=e)
            print(f"❌ Error: {e}")
    
    def _ai_voice_teaching_workflow(self):
        """AI-enhanced voice teaching workflow"""
        try:
            print("\n🧠 AI Teaching Workflow Starting...")
            
            # Step 1: Get question with AI analysis
            speak("Accha! Ab mujhe bataiye ki aap kya sawal sikhana chahte hain?")
            question = listen(timeout=20)
            
            if not question:
                speak("Koi sawal nahi mila. Phir se try kariye.")
                return
            
            print(f"❓ Question: {question}")
            
            # AI analysis of question
            if self.nlp_enabled:
                q_analysis = smart_chatbot.nlp_engine.detect_language(question)
                intent_info = smart_chatbot.nlp_engine.extract_intent(question)
                print(f"🧠 Question Analysis: {q_analysis.language_name} | {intent_info['intent']}")
            
            # Step 2: Get answer
            speak(f"Samajh gaya! Ab bataiye ki '{question}' ka jawab kya hai?")
            answer = listen(timeout=30)
            
            if not answer:
                speak("Koi jawab nahi mila. Phir se try kariye.")
                return
            
            print(f"💡 Answer: {answer}")
            
            # AI analysis of answer
            if self.nlp_enabled:
                a_analysis = smart_chatbot.nlp_engine.analyze_sentiment(answer)
                print(f"🧠 Answer Analysis: {a_analysis['sentiment']} sentiment ({a_analysis['confidence']:.2f})")
            
            # Step 3: AI-powered confirmation
            if self.nlp_enabled:
                confirm_msg = smart_chat(f"Please confirm: {question} -> {answer}", speak=False)
            else:
                confirm_msg = f"Confirm kijiye: '{question}' ka jawab hai '{answer}'. Sahi hai?"
            
            speak(confirm_msg)
            confirmation = listen(timeout=10)
            
            if confirmation and any(word in confirmation.lower() for word in ['yes', 'han', 'haan', 'sahi', 'correct', 'theek']):
                # Save knowledge
                if learn(question, answer):
                    if self.nlp_enabled:
                        success_msg = smart_chat("Thank you for teaching me!", speak=False)
                    else:
                        success_msg = "Dhanyawad! Maine seekh liya hai."
                    
                    speak(success_msg)
                    print("✅ Successfully saved!")
                    
                    # AI-powered test
                    time.sleep(1)
                    test_answer = ask(question)
                    if test_answer:
                        speak(f"Test successful: {test_answer}")
                        print(f"🧠 AI Test: ✅ {question} -> {test_answer}")
                    else:
                        speak("Knowledge saved but test mein issue aayi.")
                else:
                    speak("Technical problem aayi. Phir se try kariye.")
            else:
                speak("Theek hai, cancel kar diya.")
                
        except Exception as e:
            log_error("AI teaching workflow error", error=e)
            speak("Teaching mein technical problem aayi.")
    
    def run_ai_voice_chat(self):
        """AI-powered voice chat with multilingual support"""
        try:
            if not is_voice_available():
                print("❌ Voice unavailable. Please check audio devices.")
                return
            
            print("\n🗣️ AI-Powered Voice Chat Mode!")
            print("=" * 50)
            print("🧠 AI Features:")
            print("• Multilingual conversation")
            print("• Intent & sentiment analysis")
            print("• Context-aware responses")
            print("• Smart voice selection")
            print("🎤 Speak naturally, say 'exit' to return")
            print("-" * 50)
            
            # AI welcome
            if self.nlp_enabled:
                speak("Namaste! Main AI-powered chatbot hun. Multilingual conversation ke liye ready hun!")
            else:
                speak("Voice chat ready hai! Baat shuru kariye!")
            
            self.running = True
            chat_count = 0
            
            while self.running:
                print(f"\n🎤 AI Listening... (Chat #{chat_count + 1})")
                user_input = listen(timeout=15)
                
                if not user_input:
                    print("⏰ Timeout")
                    continue
                
                print(f"👤 You: {user_input}")
                
                # Exit check
                if any(word in user_input.lower() for word in ['exit', 'quit', 'bahar', 'alvida', 'bye']):
                    if self.nlp_enabled:
                        farewell = smart_chat("goodbye", speak=False)
                        speak(farewell)
                    else:
                        speak("Alvida! Baat karke accha laga!")
                    break
                
                # AI-powered response
                response = self._get_ai_chat_response(user_input)
                print(f"🤖 AI Bot: {response}")
                speak(response)
                
                chat_count += 1
                
        except KeyboardInterrupt:
            speak("Chat band kar raha hun. Alvida!")
        except Exception as e:
            log_error("AI voice chat error", error=e)
            print(f"❌ Error: {e}")
    
    def run_ai_text_chat(self):
        """AI-powered text chat with full NLP analysis"""
        try:
            print("\n💬 AI-Powered Text Chat Mode")
            print("="*50)
            print("🧠 AI Features:")
            print("• Multilingual support (50+ languages)")
            print("• Intent recognition & sentiment analysis")
            print("• Context-aware responses")
            print("• Learning integration")
            print("Commands: 'teach', 'stats', 'analyze', 'exit'")
            print("-"*50)
            
            if self.nlp_enabled:
                print("🤖 AI: Hello! I can chat in multiple languages with AI intelligence!")
                print("🤖 AI: नमस्ते! मैं AI के साथ कई भाषाओं में बात कर सकता हूँ!")
            
            while True:
                try:
                    user_input = input("\n👤 You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Sanitize input
                    safe_input = sanitize_user_input(user_input)
                    if not is_safe_input(safe_input):
                        print("🤖 AI: Invalid input. Please try again.")
                        continue
                    
                    # Exit check
                    if safe_input.lower() in ['exit', 'quit', 'bahar', 'alvida']:
                        if self.nlp_enabled:
                            farewell = smart_chat("goodbye", speak=False)
                            print(f"🤖 AI: {farewell}")
                        else:
                            print("🤖 Bot: Goodbye! Thanks for chatting!")
                        break
                    
                    # Special commands
                    if safe_input.lower() == 'teach':
                        self._ai_text_teaching_mode()
                        continue
                    elif safe_input.lower() == 'stats' and self.nlp_enabled:
                        self._show_conversation_stats()
                        continue
                    elif safe_input.lower() == 'analyze' and self.nlp_enabled:
                        self._analyze_text_input()
                        continue
                    
                    # AI-powered response
                    response, analysis = self._get_ai_text_response(safe_input)
                    print(f"🤖 AI: {response}")
                    
                    # Show AI analysis
                    if analysis and self.nlp_enabled:
                        print(f"🧠 Analysis: {analysis}")
                    
                except KeyboardInterrupt:
                    print("\n🤖 AI: Chat session ended. Goodbye!")
                    break
                except Exception as e:
                    log_error("AI text chat error", error=e)
                    print(f"❌ Error: {e}")
                    
        except Exception as e:
            log_error("AI text chat mode error", error=e)
    
    def run_multilingual_demo(self):
        """Demonstrate multilingual AI capabilities"""
        try:
            print("\n🌍 Multilingual AI Demonstration")
            print("="*50)
            
            if not self.nlp_enabled:
                print("❌ Advanced NLP not available for demo")
                return
            
            demo_phrases = [
                ("Hello! How are you?", "English"),
                ("नमस्ते! आप कैसे हैं?", "Hindi"),
                ("¡Hola! ¿Cómo estás?", "Spanish"),  
                ("Bonjour! Comment allez-vous?", "French"),
                ("Guten Tag! Wie geht es Ihnen?", "German"),
                ("Switch ka price kya hai?", "Hinglish"),
                ("Thank you very much!", "English"),
                ("धन्यवाद!", "Hindi")
            ]
            
            print("🎭 Demonstrating AI language detection and responses:")
            print("-"*50)
            
            for phrase, expected_lang in demo_phrases:
                print(f"\n📝 Input: {phrase}")
                
                result = smart_chatbot.process_user_input(phrase, speak_response=False)
                
                # Display analysis
                lang_info = result.get('language_info')
                detected_lang = lang_info.language_name if lang_info else 'Unknown'
                intent = result.get('intent_info', {}).get('intent', 'unknown')
                sentiment = result.get('sentiment_info', {}).get('sentiment', 'neutral')
                voice = result.get('suggested_voice', 'default')
                
                print(f"🌍 Detected: {detected_lang}")
                print(f"🎯 Intent: {intent}")
                print(f"😊 Sentiment: {sentiment}")
                print(f"🎙️ Voice: {voice}")
                print(f"🤖 Response: {result['response_text']}")
                print(f"📊 Expected: {expected_lang}")
                
                # Optional: speak the response
                choice = input("🔊 Speak this response? (y/n): ").lower()
                if choice == 'y':
                    speak(result['response_text'])
                
                print("-"*30)
                
        except Exception as e:
            log_error("Multilingual demo error", error=e)
            print(f"❌ Demo error: {e}")
    
    def show_ai_statistics(self):
        """Show comprehensive AI and chatbot statistics"""
        try:
            print("\n📊 AI & Chatbot Analytics")
            print("="*50)
            
            # Traditional learning stats
            try:
                basic_stats = get_stats()
                print("📚 Knowledge Base:")
                print(f"  • Total entries: {basic_stats.get('total_entries', 0)}")
                print(f"  • Recent additions: {basic_stats.get('recent_count', 0)}")
                print(f"  • Success rate: {basic_stats.get('success_rate', 0):.1f}%")
            except:
                print("📚 Knowledge Base: Stats unavailable")
            
            # AI conversation stats
            if self.nlp_enabled:
                print("\n🧠 AI Conversation Analytics:")
                stats = smart_chatbot.get_conversation_statistics()
                
                summary = stats.get('conversation_summary', {})
                if 'stats' in summary:
                    s = summary['stats']
                    print(f"  • Total exchanges: {s.get('total_exchanges', 0)}")
                    print(f"  • Languages detected: {len(s.get('languages_used', []))}")
                    print(f"  • Intents recognized: {len(s.get('intents_used', []))}")
                    print(f"  • Current language: {s.get('current_language', 'unknown')}")
                    print(f"  • Emotional state: {s.get('emotional_state', 'neutral')}")
                    
                    if s.get('languages_used'):
                        print(f"  • Languages: {', '.join(s['languages_used'][:10])}")
                    if s.get('intents_used'):
                        print(f"  • Intents: {', '.join(s['intents_used'][:10])}")
                
                # System status
                print(f"\n⚙️ System Status:")
                print(f"  • NLP Engine: {stats.get('nlp_engine_status', 'Unknown')}")
                print(f"  • Learning System: {stats.get('learning_statistics', {}).get('status', 'Unknown')}")
                print(f"  • Voice System: {stats.get('voice_system_status', 'Unknown')}")
            else:
                print("\n🧠 AI Analytics: Not available (NLP disabled)")
            
            print("\n🎯 Session Info:")
            print(f"  • Voice available: {'Yes' if is_voice_available() else 'No'}")
            print(f"  • AI enabled: {'Yes' if self.nlp_enabled else 'No'}")
            print(f"  • Conversation count: {self.conversation_count}")
            
        except Exception as e:
            log_error("Statistics display error", error=e)
            print(f"❌ Stats error: {e}")
    
    def manage_knowledge(self):
        """Enhanced knowledge management interface"""
        try:
            print("\n🧠 Knowledge Management")
            print("="*40)
            print("1️⃣ View knowledge entries")
            print("2️⃣ Add knowledge manually")
            print("3️⃣ Search knowledge")
            print("4️⃣ Export knowledge")
            print("5️⃣ AI knowledge analysis")
            print("6️⃣ Back to main menu")
            
            choice = input("\nChoose option (1-6): ").strip()
            
            if choice == '1':
                self._view_knowledge_entries()
            elif choice == '2':
                self._add_manual_knowledge()
            elif choice == '3':
                self._search_knowledge()
            elif choice == '4':
                self._export_knowledge()
            elif choice == '5' and self.nlp_enabled:
                self._ai_knowledge_analysis()
            elif choice == '6':
                return
            else:
                print("❌ Invalid choice!")
                
        except Exception as e:
            log_error("Knowledge management error", error=e)
            print(f"❌ Error: {e}")
    
    def configure_settings(self):
        """Configuration and settings menu"""
        try:
            print("\n⚙️ Settings & Configuration")
            print("="*40)
            print("1️⃣ Voice settings")
            print("2️⃣ AI settings")
            print("3️⃣ Language preferences")
            print("4️⃣ Performance settings")
            print("5️⃣ Reset to defaults")
            print("6️⃣ Back to main menu")
            
            choice = input("\nChoose option (1-6): ").strip()
            
            if choice == '1':
                self._configure_voice_settings()
            elif choice == '2' and self.nlp_enabled:
                self._configure_ai_settings()
            elif choice == '3' and self.nlp_enabled:
                self._configure_language_preferences()
            elif choice == '4':
                self._configure_performance_settings()
            elif choice == '5':
                self._reset_settings()
            elif choice == '6':
                return
            else:
                print("❌ Invalid choice or feature unavailable!")
                
        except Exception as e:
            log_error("Settings error", error=e)
            print(f"❌ Settings error: {e}")
    
    def _get_ai_chat_response(self, user_input: str) -> str:
        """Get AI-powered chat response"""
        try:
            if self.nlp_enabled:
                # Use AI system
                result = smart_chatbot.process_user_input(user_input, speak_response=False)
                
                # Try knowledge base first
                if result.get('intent_info', {}).get('intent') == 'question':
                    knowledge_answer = ask(user_input)
                    if knowledge_answer:
                        return f"I know that: {knowledge_answer}"
                
                return result['response_text']
            else:
                # Fallback to basic response
                answer = ask(user_input)
                if answer:
                    return answer
                return "I understand, but I don't have specific information about that. You can teach me!"
                
        except Exception as e:
            log_error("AI chat response error", error=e)
            return "Sorry, I encountered a technical issue. Please try again."
    
    def _get_ai_text_response(self, user_input: str) -> tuple:
        """Get AI text response with analysis"""
        try:
            if self.nlp_enabled:
                result = smart_chatbot.process_user_input(user_input, speak_response=False)
                
                # Build analysis string
                lang_info = result.get('language_info')
                analysis = f"{lang_info.language_name if lang_info else 'Unknown'} | "
                analysis += f"{result.get('intent_info', {}).get('intent', 'unknown')} | "
                analysis += f"{result.get('sentiment_info', {}).get('sentiment', 'neutral')}"
                
                # Check knowledge base
                if result.get('intent_info', {}).get('intent') == 'question':
                    knowledge_answer = ask(user_input)
                    if knowledge_answer:
                        return knowledge_answer, analysis
                
                return result['response_text'], analysis
            else:
                # Basic response
                answer = ask(user_input)
                if answer:
                    return answer, "Basic mode"
                return "I don't have information about that. Use 'teach' to help me learn!", "Basic mode"
                
        except Exception as e:
            log_error("AI text response error", error=e)
            return "Technical error occurred.", "Error"
    
    def _ai_text_teaching_mode(self):
        """AI-enhanced text teaching"""
        try:
            print("\n🎓 AI-Enhanced Teaching Mode")
            print("-"*30)
            
            question = input("❓ Question: ").strip()
            if not question:
                print("🤖 No question provided.")
                return
            
            # AI analysis of question
            if self.nlp_enabled:
                result = smart_chatbot.nlp_engine.detect_language(question)
                print(f"🧠 Detected language: {result.language_name}")
                
                intent = smart_chatbot.nlp_engine.extract_intent(question)
                print(f"🎯 Intent: {intent['intent']} ({intent['confidence']:.2f})")
            
            answer = input("💡 Answer: ").strip()
            if not answer:
                print("🤖 No answer provided.")
                return
            
            # AI analysis of answer
            if self.nlp_enabled:
                sentiment = smart_chatbot.nlp_engine.analyze_sentiment(answer)
                print(f"😊 Answer sentiment: {sentiment['sentiment']} ({sentiment['confidence']:.2f})")
            
            print(f"\n🔄 Confirmation: '{question}' -> '{answer}'")
            confirm = input("✅ Correct? (y/n): ").lower()
            
            if confirm in ['y', 'yes']:
                if learn(question, answer):
                    if self.nlp_enabled:
                        success_msg = smart_chat("Great! I learned something new!", speak=False)
                        print(f"🤖 {success_msg}")
                    else:
                        print("🎉 Successfully learned!")
                    
                    # Test
                    test_answer = ask(question)
                    if test_answer:
                        print(f"🧪 Test successful: {test_answer}")
                else:
                    print("❌ Teaching failed")
            else:
                print("❌ Teaching cancelled")
                
        except Exception as e:
            log_error("AI text teaching error", error=e)
            print(f"❌ Teaching error: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        try:
            log_info("Cleaning up resources...")
            if hasattr(self, 'voice_interface'):
                self.voice_interface.cleanup()
        except Exception as e:
            log_error("Cleanup error", error=e)
    
    # Additional helper methods for menu options
    def _view_knowledge_entries(self):
        """View knowledge entries"""
        print("\n📚 Knowledge entries feature - implementation needed")
    
    def _add_manual_knowledge(self):
        """Add knowledge manually"""
        print("\n➕ Manual knowledge addition feature - implementation needed")
    
    def _search_knowledge(self):
        """Search knowledge"""
        print("\n🔍 Knowledge search feature - implementation needed")
    
    def _export_knowledge(self):
        """Export knowledge"""
        print("\n📤 Knowledge export feature - implementation needed")
    
    def _ai_knowledge_analysis(self):
        """AI knowledge analysis"""
        if self.nlp_enabled:
            print("\n🧠 AI Knowledge Analysis feature - implementation needed")
    
    def _configure_voice_settings(self):
        """Configure voice settings"""
        print("\n🎙️ Voice configuration feature - implementation needed")
    
    def _configure_ai_settings(self):
        """Configure AI settings"""
        if self.nlp_enabled:
            print("\n🧠 AI configuration feature - implementation needed")
    
    def _configure_language_preferences(self):
        """Configure language preferences"""
        print("\n🌍 Language preferences feature - implementation needed")
    
    def _configure_performance_settings(self):
        """Configure performance settings"""
        print("\n⚡ Performance settings feature - implementation needed")
    
    def _reset_settings(self):
        """Reset settings"""
        print("\n🔄 Reset settings feature - implementation needed")
    
    def _show_conversation_stats(self):
        """Show detailed conversation statistics"""
        if self.nlp_enabled:
            stats = smart_chatbot.get_conversation_statistics()
            print(f"\n📊 Detailed Stats: {stats}")
    
    def _analyze_text_input(self):
        """Analyze text input in detail"""
        if self.nlp_enabled:
            text = input("🔬 Enter text to analyze: ").strip()
            if text:
                result = smart_chatbot.nlp_engine.generate_response(text)
                print(f"🧠 Full Analysis: {result}")

def main():
    """Main entry point"""
    try:
        parser = argparse.ArgumentParser(description='Enhanced Adaptive Chatbot with AI')
        parser.add_argument('--mode', choices=['interactive', 'voice', 'text'], 
                          default='interactive', help='Chatbot mode')
        parser.add_argument('--no-ai', action='store_true', 
                          help='Disable AI features')
        
        args = parser.parse_args()
        
        # Create chatbot
        chatbot = EnhancedAdaptiveChatbot()
        
        if args.no_ai:
            chatbot.nlp_enabled = False
            print("🤖 Running in basic mode (AI disabled)")
        
        # Run in specified mode
        if args.mode == 'interactive':
            chatbot.run_interactive_menu()
        elif args.mode == 'voice':
            chatbot.run_ai_voice_chat()
        elif args.mode == 'text':
            chatbot.run_ai_text_chat()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        log_error("Main application error", error=e)
        print(f"❌ Application error: {e}")
    finally:
        print("✅ Application terminated gracefully")

if __name__ == "__main__":
    main()