#!/usr/bin/env python3
"""
Adaptive Chatbot - Production-Ready Main Application
Unified architecture with comprehensive error handling and all features
"""

import sys
import os
import argparse
import time
from typing import Optional, Dict, Any
import signal
import atexit

# Import our modules with error handling
try:
    from config import config
    from logger import log_info, log_error, log_warning
except ImportError as e:
    print(f"❌ Critical dependency missing: {e}")
    print("Please ensure all required modules are in the same directory.")
    sys.exit(1)

try:
    from simple_voice import speak_simple as speak, listen_simple as listen, is_voice_ready as is_voice_available
except ImportError as e:
    print(f"❌ Voice interface unavailable: {e}")
    # Fallback to dummy functions
    def speak(text): return False
    def listen(timeout=10): return None
    def is_voice_available(): return False
    log_error(f"Voice interface disabled due to missing dependencies: {e}")

try:
    from unified_learning_manager import get_learning_manager, learn, ask, get_stats
except ImportError as e:
    print(f"❌ Learning system unavailable: {e}")
    sys.exit(1)

try:
    from validators import sanitize_user_input, is_safe_input
    from advanced_event_loop_manager import get_loop_manager, run_async_safely
    from advanced_memory_manager import get_memory_manager, memory_monitor, register_memory_cleanup
    from performance_monitoring_dashboard import get_performance_monitor, performance_timer
except ImportError as e:
    print(f"❌ Validation system unavailable: {e}")
    # Fallback to basic validation
    def sanitize_user_input(text): return str(text).strip() if text else ""
    def is_safe_input(text): return bool(text and len(str(text).strip()) > 0)
    log_warning(f"Using basic validation due to: {e}")

class AdaptiveChatbot:
    """Main application class for the Adaptive Chatbot"""
    
    def __init__(self):
        self.learning_manager = None
        self.running = False
        self.current_mode = None
        # Track newly learned Q-A pairs during a conversation session
        self.learned_entries = []  # List[Dict[str, str]] with keys: question, answer
        
        # Register cleanup
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all components with error handling"""
        try:
            log_info("🤖 Adaptive Chatbot शुरू हो रहा है...")
            
            # Initialize learning manager
            self.learning_manager = get_learning_manager()
            log_info("✅ Learning manager तैयार")
            
            log_info("🎉 Adaptive Chatbot तैयार है!")
            
        except Exception as e:
            log_error("Failed to initialize chatbot", error=e)
            raise
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        log_info("Interrupt signal received, shutting down gracefully...")
        self.running = False
    
    def run_interactive_menu(self):
        """Run the interactive menu for mode selection"""
        while True:
            try:
                self._display_main_menu()
                choice = self._get_user_choice()
                
                if choice == '1':
                    self.run_voice_teaching()
                elif choice == '2':
                    self.run_voice_chat()
                elif choice == '3':
                    self.run_text_chat()
                elif choice == '4':
                    self.show_statistics()
                elif choice == '5':
                    self.manage_knowledge()
                elif choice == '6':
                    log_info("👋 Goodbye! Dhanyawad!")
                    break
                else:
                    print("❌ Galat choice! कृपया 1-6 में से choose करें।")
                    
            except KeyboardInterrupt:
                log_info("\\n👋 Goodbye! Dhanyawad!")
                break
            except Exception as e:
                log_error("Menu error", error=e)
                print(f"❌ Error आया: {e}")
    
    def _display_main_menu(self):
        """Display the main menu"""
        app_name = config.get('app', 'app_name', 'Adaptive Chatbot')
        version = config.get('app', 'version', '1.0.0')
        
        print("\\n" + "="*60)
        print(f"🤖 {app_name} v{version}")
        print("="*60)
        print("\\nChoose your interaction mode:")
        print("1️⃣  इंटरैक्टिव वॉइस टीचिंग (आवाज़ से सिखाएं)")
        print("2️⃣  वॉइस चैट (बोलकर बात करें)")
        print("3️⃣  टेक्स्ट चैट (टाइप करके बात करें)")
        print("4️⃣  आँकड़े दिखाएं")
        print("5️⃣  ज्ञान प्रबंधन")
        print("6️⃣  बाहर निकलें")
        print("-"*60)
    
    def _get_user_choice(self) -> str:
        """Get user's menu choice with validation"""
        try:
            choice = input("\\nEnter your choice (1-6): ").strip()
            return choice
        except EOFError:
            return '6'  # Exit on EOF
        except Exception:
            return ''
    
    def run_voice_teaching(self):
        """Run interactive voice teaching mode with EdgeTTS"""
        try:
            if not is_voice_available():
                print("❌ Voice उपलब्ध नहीं। Microphone aur speakers check करें।")
                return
            
            print("\\n🎓 Interactive Voice Teaching Mode - EdgeTTS Powered!")
            print("=" * 60)
            print("🎤 Instructions:")
            print("• 'Teach' बोलकर teaching शुरू करें")
            print("• 'Exit' बोलकर main menu में जाइए")
            print("• Bot step-by-step guide करेगा")
            print("-" * 60)
            
            speak("Namaste! Main EdgeTTS ke saath ready hun. Mujhe kuch naya sikhane ke liye 'teach' boliye!")
            
            self.running = True
            while self.running:
                print("\\n🎤 Command suniye...")
                command = listen(timeout=15)
                
                if not command:
                    speak("Kuch sunaayi nahi diya. Phir se koshish kariye.")
                    continue
                
                print(f"👤 Command: {command}")
                command_lower = command.lower()
                
                # Exit commands
                if any(word in command_lower for word in ['exit', 'quit', 'bahar', 'nikal', 'bye']):
                    speak("Main menu mein wapas ja rahe hain. Dhanyawad!")
                    break
                
                # Teaching command
                if any(word in command_lower for word in ['teach', 'teech', 'sikha', 'learn', 'sikhao']):
                    self._voice_teaching_workflow()
                else:
                    # Try to answer the question
                    answer = ask(command)
                    if answer:
                        speak(f"Jawab hai: {answer}")
                    else:
                        speak("Mujhe iska jawab nahi pata. Aap mujhe sikha sakte hain - 'teach' boliye!")
                        
        except KeyboardInterrupt:
            speak("Teaching mode band kar raha hun. Alvida!")
            print("\\n👋 Teaching stopped by user")
        except Exception as e:
            log_error("Voice teaching error", error=e)
            print(f"❌ Voice teaching में error: {e}")
    
    def _voice_teaching_workflow(self):
        """Execute voice teaching workflow with EdgeTTS"""
        try:
            print("\\n📚 Starting Teaching Workflow...")
            
            # Step 1: Get question
            speak("Accha! Ab mujhe bataiye ki aap kya sawal sikhana chahte hain?")
            print("🎤 Question सुनिए...")
            question = listen(timeout=20)
            
            if not question:
                speak("Koi sawal nahi mila. Phir se try kariye.")
                return
            
            print(f"❓ Question: {question}")
            
            # Step 2: Get answer
            speak(f"Bahut accha! Ab bataiye ki '{question}' ka jawab kya hai?")
            print("🎤 Answer सुनिए...")
            answer = listen(timeout=30)
            
            if not answer:
                speak("Koi jawab nahi mila. Phir se try kariye.")
                return
            
            print(f"💡 Answer: {answer}")
            
            # Step 3: Confirm
            speak(f"Samajh gaya! To '{question}' ka jawab hai '{answer}'. Yeh sahi hai?")
            print("🎤 Confirmation सुनिए (yes/no)...")
            confirmation = listen(timeout=10)
            
            if confirmation and any(word in confirmation.lower() for word in ['yes', 'han', 'haan', 'sahi', 'correct', 'theek']):
                # Save knowledge
                if learn(question, answer):
                    speak("Dhanyawad! Maine yeh seekh liya hai.")
                    print("✅ Successfully saved to knowledge base!")
                    
                    # Test immediately
                    time.sleep(1)
                    speak(f"Test karte hain: {question}")
                    time.sleep(0.5)
                    
                    test_answer = ask(question)
                    if test_answer:
                        speak(f"Jawab mil gaya: {test_answer}")
                        speak("Perfect! Maine successfully seekh liya!")
                        print(f"🎉 Test successful: {question} -> {test_answer}")
                    else:
                        speak("Test mein kuch problem aayi. But knowledge save ho gaya.")
                        print("⚠️ Test failed but knowledge saved")
                else:
                    speak("Seekhne mein koi technical problem aayi. Phir se koshish kariye.")
                    print("❌ Failed to save to knowledge base")
            else:
                speak("Theek hai, maine yeh nahi seekha. Koi baat nahi.")
                print("❌ Teaching cancelled by user")
            
            print("-" * 50)
                
        except Exception as e:
            log_error("Voice teaching workflow error", error=e)
            speak("Teaching mein koi technical problem aayi.")
            print(f"❌ Teaching workflow error: {e}")
    
    def run_voice_chat(self):
        """Run voice chat mode with simple EdgeTTS"""
        try:
            if not is_voice_available():
                print("❌ Voice उपलब्ध नहीं। Microphone aur speakers check करें।")
                return
            
            print("\n🗣️ Voice Chat Mode - EdgeTTS Powered!")
            print("=" * 45)
            print("🎤 Instructions:")
            print("• Hindi ya English में naturally बोलिए")
            print("• 'Exit' बोलकर main menu में जाइए")
            print("-" * 45)
            
            # Welcome message with EdgeTTS
            speak("Namaste! Main EdgeTTS ke saath ready hun. Aap mujhse kuch bhi pooch sakte hain!")
            
            self.running = True
            chat_count = 0
            
            while self.running:
                print(f"\n🎤 Listening... (Chat #{chat_count + 1})")
                user_input = listen(timeout=15)
                
                if not user_input:
                    print("⏰ Timeout - kuch सुनायी नहीं दिया")
                    continue
                
                print(f"👤 You said: {user_input}")
                
                # Check for exit
                if any(word in user_input.lower() for word in ['exit', 'quit', 'bahar', 'alvida', 'bye']):
                    speak("Alvida! Baat karke bahut accha laga. Dhanyawad!")
                    break
                
                # Get response
                response = self._get_chat_response(user_input)
                print(f"🤖 Bot response: {response}")
                speak(response)
                
                # If we don't know, ask user for the correct answer and learn it (voice mode)
                if response.startswith("Mujhe iska jawab nahi pata."):
                    self._learn_from_user_voice(user_input)
                
                chat_count += 1
                
            # End-of-conversation summary
            self._print_session_summary()
                
        except KeyboardInterrupt:
            speak("Chat band kar raha hun. Alvida!")
            print("\n👋 Chat stopped by user")
            # End-of-conversation summary even on interrupt
            self._print_session_summary()
        except Exception as e:
            log_error("Voice chat error", error=e)
            print(f"❌ Voice chat में error: {e}")
    
    def run_text_chat(self):
        """Run text chat mode"""
        try:
            print("\\n💬 Text Chat Mode")
            print("="*30)
            print("Instructions:")
            print("• Type your messages in Hindi or English")
            print("• Type 'teach' for teaching mode")
            print("• Type 'exit' to return to main menu")
            print("-"*30)
            
            while True:
                try:
                    user_input = input("\n👤 You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Sanitize input
                    safe_input = sanitize_user_input(user_input)
                    if not is_safe_input(safe_input):
                        print("🤖 Bot: ❌ Invalid input detected. Please try again.")
                        continue
                    
                    # Check for exit
                    if safe_input.lower() in ['exit', 'quit', 'bahar', 'alvida']:
                        print("🤖 Bot: 👋 Alvida! Baat karke accha laga.")
                        # End-of-conversation summary
                        self._print_session_summary()
                        break
                    
                    # Check for teaching mode
                    if safe_input.lower() in ['teach', 'teech', 'sikha']:
                        self._text_teaching_mode()
                        continue
                    
                    # Get response
                    response = self._get_chat_response(safe_input)
                    print(f"🤖 Bot: {response}")
                    
                    # If we don't know, ask user and learn (text mode)
                    if response.startswith("Mujhe iska jawab nahi pata."):
                        self._learn_from_user_text(safe_input)
                except KeyboardInterrupt:
                    print("\
🤖 Bot: 👋 Chat band kar raha hun. Alvida!")
                    # End-of-conversation summary even on interrupt
                    self._print_session_summary()
                    break
                except Exception as e:
                    log_error("Text chat error", error=e)
                    print(f"❌ Error: {e}")
                    
        except Exception as e:
            log_error("Text chat mode error", error=e)
    
    def _text_teaching_mode(self):
        """Handle text-based teaching"""
        try:
            print("\\n📚 Teaching Mode Activated!")
            print("-"*30)
            
            # Get question
            question = input("❓ Question (sawal): ").strip()
            if not question:
                print("🤖 Koi sawal nahi mila.")
                return
            
            question = sanitize_user_input(question)
            if not is_safe_input(question):
                print("🤖 Invalid question format.")
                return
            
            # Get answer
            answer = input("💡 Answer (jawab): ").strip()
            if not answer:
                print("🤖 Koi jawab nahi mila.")
                return
            
            answer = sanitize_user_input(answer)
            if not is_safe_input(answer):
                print("🤖 Invalid answer format.")
                return
            
            # Confirm
            print(f"\\n🔄 Confirmation: '{question}' -> '{answer}'")
            confirm = input("✅ Is this correct? (y/n): ").lower()
            
            if confirm in ['y', 'yes', 'han', 'haan']:
                if learn(question, answer):
                    print("🎉 Successfully learned! Testing...")
                    
                    # Test immediately
                    test_response = ask(question)
                    if test_response:
                        print(f"🧪 Test: {question} -> {test_response}")
                        print("✅ Teaching successful!")
                    else:
                        print("❌ Teaching failed - could not retrieve answer")
                else:
                    print("❌ Teaching failed - could not save knowledge")
            else:
                print("❌ Teaching cancelled.")
                
        except Exception as e:
            log_error("Text teaching error", error=e)
            print(f"❌ Teaching error: {e}")
        
        print("-"*30)
        print("📝 Back to normal chat...")
    
    def _get_chat_response(self, query: str) -> str:
        """Get chat response for a query"""
        try:
            # Try knowledge base first
            answer = ask(query)
            if answer:
                return answer
            
            # Keep only help queries as those are functional
            query_lower = query.lower()
            
            help_queries = ['help', 'madad', 'sahayata', 'guide']
            if any(word in query_lower for word in help_queries):
                return """📚 Main in kaamon mein aapki madad kar sakta hun:

• Aapke sawaalon ka jawab de sakta hun
• Nayi jankari seekh sakta hun  
• Baatcheet kar sakta hun
• Madad aur sujhaav de sakta hun

Bas aap mujhse kuch bhi poochiye ya 'teach' kahkar mujhe nayi cheezon sikhaiye!"""
            
            # Default response (unknown) - follow the specified behavior
            return "Mujhe iska jawab nahi pata. Kya aap mujhe iska sahi jawab bata sakte hai? Main ise yaad rakhunga."
            
        except Exception as e:
            log_error("Chat response error", error=e)
            return "❌ Kuch takneeki samasya aayi hai."
    
    def show_statistics(self):
        """Show knowledge base statistics"""
        try:
            print("\\n📊 Knowledge Base Statistics")
            print("="*40)
            
            stats = get_stats()
            
            if 'error' in stats:
                print(f"❌ Error getting statistics: {stats['error']}")
                return
            
            print(f"📚 Total Knowledge Entries: {stats['total_entries']}")
            print(f"📈 Recent Additions (24h): {stats['recent_additions']}")
            print(f"⭐ Average Usage: {stats['average_usage']}")
            
            if stats['most_used']:
                print(f"🔥 Most Used: {stats['most_used']['question'][:50]}... ({stats['most_used']['count']} times)")
            
            if stats['least_used']:
                print(f"❄️ Least Used: {stats['least_used']['question'][:50]}... ({stats['least_used']['count']} times)")
            
            # Voice interface status (Simple EdgeTTS)
            print(f"\\n🎤 Voice Interface Status:")
            print(f"   EdgeTTS Initialized: {'✅' if is_voice_available() else '❌'}")
            print(f"   TTS Engine: EdgeTTS (hi-IN-MadhurNeural)")
            print(f"   Speech Recognition: Google API")
            
        except Exception as e:
            log_error("Statistics error", error=e)
            print(f"❌ Statistics error: {e}")
        
        input("\\nPress Enter to continue...")
    
    def manage_knowledge(self):
        """Knowledge management menu"""
        try:
            while True:
                print("\\n🗂️ Knowledge Management")
                print("="*30)
                print("1. Export Knowledge")
                print("2. Import Knowledge") 
                print("3. Back to Main Menu")
                
                choice = input("\\nChoose option (1-3): ").strip()
                
                if choice == '1':
                    self._export_knowledge()
                elif choice == '2':
                    self._import_knowledge()
                elif choice == '3':
                    break
                else:
                    print("❌ Invalid choice!")
                    
        except Exception as e:
            log_error("Knowledge management error", error=e)
    
    def _export_knowledge(self):
        """Export knowledge to file"""
        try:
            filename = input("Enter filename (default: knowledge_export.json): ").strip()
            if not filename:
                filename = "knowledge_export.json"
            
            if self.learning_manager.export_knowledge(filename):
                print(f"✅ Knowledge exported to: {filename}")
            else:
                print("❌ Export failed")
                
        except Exception as e:
            log_error("Export error", error=e)
            print(f"❌ Export error: {e}")
    
    def _import_knowledge(self):
        """Import knowledge from file"""
        try:
            filename = input("Enter filename to import: ").strip()
            if not filename:
                print("❌ No filename provided")
                return
            
            success, total = self.learning_manager.import_knowledge(filename)
            print(f"✅ Imported {success}/{total} entries")
            
        except Exception as e:
            log_error("Import error", error=e)
            print(f"❌ Import error: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            log_info("Cleaning up resources...")
            
            if self.learning_manager:
                self.learning_manager.cleanup()
            
            # Simple voice interface doesn't need cleanup
            
            log_info("Cleanup completed")
            
        except Exception as e:
            log_error("Cleanup error", error=e)
    
    def _learn_from_user_text(self, question: str):
        """Interactive learning flow for text mode when the bot doesn't know the answer."""
        try:
            answer = input("💬 Aapka jawab: ").strip()
            if not answer:
                print("🤖 Bot: ❌ Koi jawab nahi mila. Agli baar koshish kariye.")
                return
            
            # Confirm and save
            print("🤖 Bot: Thik hai, main ise yaad rakhunga.")
            if learn(question, answer):
                # Track for session summary
                self.learned_entries.append({"question": question, "answer": answer})
                
                # Optional: immediate test
                test = ask(question)
                if test:
                    print(f"🧪 Test: '{question}' -> '{test}'")
                    print("✅ Teaching successful!")
                else:
                    print("⚠️ Test failed, but knowledge may be saved.")
            else:
                print("❌ Saving failed. Kripya fir se koshish karein.")
        except Exception as e:
            log_error("Text interactive learning error", error=e)
            print(f"❌ Error: {e}")
    
    def _learn_from_user_voice(self, question: str):
        """Interactive learning flow for voice mode when the bot doesn't know the answer."""
        try:
            # Ask for the correct answer via TTS and listen
            speak("Mujhe iska jawab nahi pata. Kya aap mujhe iska sahi jawab bata sakte hai? Main ise yaad rakhunga.")
            print("🎤 Correct answer सुनिए...")
            answer = listen(timeout=20)
            if not answer:
                speak("Koi jawab nahi mila. Agli baar koshish kariye.")
                print("❌ Koi jawab nahi mila.")
                return
            
            speak("Thik hai, main ise yaad rakhunga.")
            if learn(question, answer):
                # Track for session summary
                self.learned_entries.append({"question": question, "answer": answer})
                # Optional: immediate test
                test = ask(question)
                if test:
                    speak(f"Test: {question}")
                    speak(f"Jawab: {test}")
                    print(f"🧪 Test: '{question}' -> '{test}'")
                else:
                    speak("Test mein samasya aayi. Lekin maine aapka jawab save kar liya hai.")
                    print("⚠️ Test failed, but knowledge may be saved.")
            else:
                speak("Save karne mein samasya aayi. Kripya fir se koshish karein.")
                print("❌ Saving failed.")
        except Exception as e:
            log_error("Voice interactive learning error", error=e)
            print(f"❌ Error: {e}")
    
    def _print_session_summary(self):
        """Print a summary of all newly stored Q-A entries for this conversation session."""
        if not self.learned_entries:
            return
        print("\n📝 Conversation Summary - Newly Stored Knowledge")
        print("="*50)
        for idx, entry in enumerate(self.learned_entries, start=1):
            q = entry.get("question", "")
            a = entry.get("answer", "")
            print(f"{idx}. Question: {q}")
            print(f"   Answer:   {a}")
        print("="*50)
        # Optionally clear after summary so the next conversation starts fresh
        self.learned_entries.clear()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Adaptive Chatbot - AI Assistant that learns from you')
    parser.add_argument('--mode', choices=['menu', 'voice', 'text'], default='menu',
                       help='Start mode: menu (default), voice, or text')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--version', action='version', 
                       version=f'Adaptive Chatbot v{config.get("app", "version", "1.0.0")}')
    
    args = parser.parse_args()
    
    # Set debug mode
    if args.debug:
        config.set('app', 'debug_mode', True)
        log_info("Debug mode enabled")
    
    try:
        # Initialize chatbot
        chatbot = AdaptiveChatbot()
        
        # Run based on mode
        if args.mode == 'menu':
            chatbot.run_interactive_menu()
        elif args.mode == 'voice':
            chatbot.run_voice_chat()
        elif args.mode == 'text':
            chatbot.run_text_chat()
            
    except KeyboardInterrupt:
        log_info("\\nApplication interrupted by user")
    except Exception as e:
        log_error("Application error", error=e)
        print(f"❌ Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()