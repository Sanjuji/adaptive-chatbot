#!/usr/bin/env python3
\"\"\"
Adaptive Chatbot - Production-Ready Main Application
Unified architecture with comprehensive error handling and all features
\"\"\"

import sys
import os
import argparse
import time
from typing import Optional, Dict, Any
import signal
import atexit

# Import our modules with error handling
try:
    from utils.simple_voice import speak_simple as speak, listen_simple as listen, is_voice_ready as is_voice_available
except ImportError as e:
    print(f\"[ERROR] Voice interface unavailable: {e}\")
    # Fallback to dummy functions
    def speak(text): return False
    def listen(timeout=10): return None
    def is_voice_available(): return False

try:
    from core.adaptation_engine import UnifiedLearningManager
except ImportError as e:
    print(f\"[ERROR] Learning system unavailable: {e}\")
    sys.exit(1)

try:
    from utils.validator import sanitize_user_input, is_safe_input
    from utils.advanced_event_loop_manager import get_loop_manager, run_async_safely
    from utils.advanced_memory_manager import get_memory_manager, memory_monitor, register_memory_cleanup
    from utils.performance_monitoring_dashboard import get_performance_monitor, performance_timer
except ImportError as e:
    print(f\"[ERROR] Validation system unavailable: {e}\")
    # Fallback to basic validation
    def sanitize_user_input(text): return str(text).strip() if text else \"\"
    def is_safe_input(text): return bool(text and len(str(text).strip()) > 0)

try:
    from configs.config import config
    from utils.logger import get_logger
except ImportError as e:
    print(f\"[ERROR] Configuration or logger unavailable: {e}\")
    # Create fallback config and logger
    class FallbackConfig:
        def get(self, section, key, default=None):
            if section == \"app\" and key == \"version\":
                return \"1.0.0\"
            return default
    config = FallbackConfig()
    
    import logging
    logger = logging.getLogger(\"AdaptiveChatbot\")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    logger.addHandler(handler)
else:
    logger = get_logger()

class AdaptiveChatbot:
    \"\"\"Main application class for the Adaptive Chatbot\"\"\"
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
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
        \"\"\"Initialize all components with error handling\"\"\"
        try:
            self.logger.info(\"[BOT] Adaptive Chatbot शुरू हो रहा है...\")
            
            # Initialize learning manager
            self.learning_manager = UnifiedLearningManager(self.logger)
            self.logger.info(\"[OK] Learning manager तैयार\")
            
            self.logger.info(\"[INFO] Adaptive Chatbot तैयार है!\")
            
        except Exception as e:
            self.logger.error(\"Failed to initialize chatbot\", error=e)
            raise
    
    def _signal_handler(self, signum, frame):
        \"\"\"Handle interrupt signals\"\"\"
        self.logger.info(\"Interrupt signal received, shutting down gracefully...\")
        self.running = False

    def start(self, mode):
        \"\"\"Start the chatbot in the specified mode.\"\"\"
        if mode == 'voice':
            self.run_voice_chat()
        elif mode == 'text':
            self.run_text_chat()
        elif mode == 'debug':
            self.run_interactive_menu()
        else:
            self.run_interactive_menu()

    def run_interactive_menu(self):
        \"\"\"Run the interactive menu for mode selection\"\"\"
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
                    self.logger.info(\" Goodbye! Dhanyawad!\")
                    break
                else:
                    print(\"[ERROR] Galat choice! कृपया 1-6 में से choose करें।\")
                    
            except KeyboardInterrupt:
                self.logger.info(\"\\n Goodbye! Dhanyawad!\")
                break
            except Exception as e:
                self.logger.error(\"Menu error\", error=e)
                print(f\"[ERROR] Error आया: {e}\")
    
    def _display_main_menu(self):
        \"\"\"Display the main menu\"\"\"
        app_name = self.config.get('app', 'app_name', 'Adaptive Chatbot')
        version = self.config.get('app', 'version', '1.0.0')
        
        print(\"\\n\" + \"=\"*60)
        print(f\"[BOT] {app_name} v{version}\")
        print(\"=\"*60)
        print(\"\\nChoose your interaction mode:\")
        print(\"1.  इंटरैक्टिव वॉइस टीचिंग (आवाज़ से सिखाएं)\")
        print(\"2.  वॉइस चैट (बोलकर बात करें)\")
        print(\"3.  टेक्स्ट चैट (टाइप करके बात करें)\")
        print(\"4.  आँकड़े दिखाएं\")
        print(\"5.  ज्ञान प्रबंधन\")
        print(\"6.  बाहर निकलें\")
        print(\"-\"*60)
    
    def _get_user_choice(self) -> str:
        \"\"\"Get user's menu choice with validation\"\"\"
        try:
            choice = input(\"\\nEnter your choice (1-6): \").strip()
            return choice
        except EOFError:
            return '6'  # Exit on EOF
        except Exception:
            return ''
    
    def run_voice_teaching(self):
        \"\"\"Run interactive voice teaching mode with EdgeTTS\"\"\"
        try:
            if not is_voice_available():
                print(\"[ERROR] Voice उपलब्ध नहीं। Microphone aur speakers check करें।\")
                return
            
            print(\"\\n[INFO] Interactive Voice Teaching Mode - EdgeTTS Powered!\")
            print(\"=\" * 60)
            print(\"[MIC] Instructions:\")
            print(\"• 'Teach' बोलकर teaching शुरू करें\")
            print(\"• 'Exit' बोलकर main menu में जाइए\")
            print(\"• Bot step-by-step guide करेगा\")
            print(\"-\" * 60)
            
            speak(\"Namaste! Main EdgeTTS ke saath ready hun. Mujhe kuch naya sikhane ke liye 'teach' boliye!\")
            
            self.running = True
            while self.running:
                print(\"\\n[MIC] Command suniye...\")
                command = listen(timeout=15)
                
                if not command:
                    speak(\"Kuch sunaayi nahi diya. Phir se koshish kariye.\")
                    continue
                
                print(f\"👤 Command: {command}\")
                command_lower = command.lower()
                
                # Exit commands
                if any(word in command_lower for word in ['exit', 'quit', 'bahar', 'nikal', 'bye']):
                    speak(\"Main menu mein wapas ja rahe hain. Dhanyawad!\")
                    break
                
                # Teaching command
                if any(word in command_lower for word in ['teach', 'teech', 'sikha', 'learn', 'sikhao']):
                    self._voice_teaching_workflow()
                else:
                    # Try to answer the question
                    answer = self.learning_manager.find_answer(command)
                    if answer:
                        speak(f\"Jawab hai: {answer}\")
                    else:
                        speak(\"Mujhe iska jawab nahi pata. Aap mujhe sikha sakte hain - 'teach' boliye!\")
                        
        except KeyboardInterrupt:
            speak(\"Teaching mode band kar raha hun. Alvida!\")
            print(\"\\n Teaching stopped by user\")
        except Exception as e:
            self.logger.error(\"Voice teaching error\", error=e)
            print(f\"[ERROR] Voice teaching में error: {e}\")

    def _voice_teaching_workflow(self):
        \"\"\"Execute voice teaching workflow with EdgeTTS\"\"\"
        try:
            print(\"\\n[INFO] Starting Teaching Workflow...\")
            
            # Step 1: Get question
            speak(\"Accha! Ab mujhe bataiye ki aap kya sawal sikhana chahte hain?\")
            print(\"[MIC] Question सुनिए...\")
            question = listen(timeout=20)
            
            if not question:
                speak(\"Koi sawal nahi mila. Phir se try kariye.\")
                return
            
            print(f\"[?] Question: {question}\")
            
            # Step 2: Get answer
            speak(f\"Bahut accha! Ab bataiye ki '{question}' ka jawab kya hai?\")
            print(\"[MIC] Answer सुनिए...\")
            answer = listen(timeout=30)
            
            if not answer:
                speak(\"Koi jawab nahi mila. Phir se try kariye.\")
                return
            
            print(f\"[!] Answer: {answer}\")
            
            # Step 3: Confirm
            speak(f\"Samajh gaya! To '{question}' ka jawab hai '{answer}'. Yeh sahi hai?\")
            print(\"[MIC] Confirmation सुनिए (yes/no)...\")
            confirmation = listen(timeout=10)
            
            if confirmation and any(word in confirmation.lower() for word in ['yes', 'han', 'haan', 'sahi', 'correct', 'theek']):
                # Save knowledge
                if self.learning_manager.add_knowledge(question, answer):
                    speak(\"Dhanyawad! Maine yeh seekh liya hai.\")
                    print(\"[OK] Successfully saved to knowledge base!\")
                    
                    # Test immediately
                    time.sleep(1)
                    speak(f\"Test karte hain: {question}\")
                    time.sleep(0.5)
                    
                    test_answer = self.learning_manager.find_answer(question)
                    if test_answer:
                        speak(f\"Jawab mil gaya: {test_answer}\")
                        speak(\"Perfect! Maine successfully seekh liya!\")
                        print(f\"[INFO] Test successful: {question} -> {test_answer}\")
                    else:
                        speak(\"Test mein kuch problem aayi. But knowledge save ho gaya.\")
                        print(\"[WARN] Test failed but knowledge saved\")
                else:
                    speak(\"Seekhne mein koi technical problem aayi. Phir se koshish kariye.\")
                    print(\"[ERROR] Failed to save to knowledge base\")
            else:
                speak(\"Theek hai, maine yeh nahi seekha. Koi baat nahi.\")
                print(\"[ERROR] Teaching cancelled by user\")
            
            print(\"-\" * 50)
                
        except Exception as e:
            self.logger.error(\"Voice teaching workflow error\", error=e)
            speak(\"Teaching mein koi technical problem aayi.\")
            print(f\"[ERROR] Teaching workflow error: {e}\")

    def run_voice_chat(self):
        \"\"\"Run voice chat mode with simple EdgeTTS\"\"\"
        try:
            if not is_voice_available():
                print(\"[ERROR] Voice उपलब्ध नहीं। Microphone aur speakers check करें।\")
                return
            
            print(\"\\n[VOICE] Voice Chat Mode - EdgeTTS Powered!\")
            print(\"=\" * 45)
            print(\"[MIC] Instructions:\")
            print(\"• Hindi ya English में naturally बोलिए\")
            print(\"• 'Exit' बोलकर main menu में जाइए\")
            print(\"-\" * 45)
            
            # Welcome message with EdgeTTS
            speak(\"Namaste! Main EdgeTTS ke saath ready hun. Aap mujhse kuch bhi pooch sakte hain!\")
            
            self.running = True
            chat_count = 0
            
            while self.running:
                print(f\"\\n[MIC] Listening... (Chat #{chat_count + 1})\")
                user_input = listen(timeout=15)
                
                if not user_input:
                    print(\"[TIMEOUT] Timeout - kuch सुनायी नहीं दिया\")
                    continue
                
                print(f\"👤 You said: {user_input}\")
                
                # Check for exit
                if any(word in user_input.lower() for word in ['exit', 'quit', 'bahar', 'alvida', 'bye']):
                    speak(\"Alvida! Baat karke bahut accha laga. Dhanyawad!\")
                    break
                
                # Get response
                response = self._get_chat_response(user_input)
                print(f\"[BOT] Bot response: {response}\")
                speak(response)
                
                # If we don't know, ask user for the correct answer and learn it (voice mode)
                if response.startswith(\"Mujhe iska jawab nahi pata.\"):
                    self._learn_from_user_voice(user_input)
                
                chat_count += 1
                
            # End-of-conversation summary
            self._print_session_summary()
                
        except KeyboardInterrupt:
            speak(\"Chat band kar raha hun. Alvida!\")
            print(\"\\n Chat stopped by user\")
            # End-of-conversation summary even on interrupt
            self._print_session_summary()
        except Exception as e:
            self.logger.error(\"Voice chat error\", error=e)
            print(f\"[ERROR] Voice chat में error: {e}\")

    def run_text_chat(self):
        \"\"\"Run text chat mode\"\"\"
        try:
            print(\"\\n[CHAT] Text Chat Mode\")
            print(\"=\"*30)
            print(\"Instructions:\")
            print(\"• Type your messages in Hindi or English\")
            print(\"• Type 'teach' for teaching mode\")
            print(\"• Type 'exit' to return to main menu\")
            print(\"-\"*30)
            
            while True:
                try:
                    user_input = input(\"\\n👤 You: \").strip()
                    
                    if not user_input:
                        continue
                    
                    # Sanitize input
                    safe_input = sanitize_user_input(user_input)
                    if not is_safe_input(safe_input):
                        print(\"[BOT] Bot: [ERROR] Invalid input detected. Please try again.\")
                        continue
                    
                    # Check for exit
                    if safe_input.lower() in ['exit', 'quit', 'bahar', 'alvida']:
                        print(\"[BOT] Bot:  Alvida! Baat karke accha laga.\")
                        # End-of-conversation summary
                        self._print_session_summary()
                        break
                    
                    # Check for teaching mode
                    if safe_input.lower() in ['teach', 'teech', 'sikha']:
                        self._text_teaching_mode()
                        continue
                    
                    # Get response
                    response = self._get_chat_response(safe_input)
                    print(f\"[BOT] Bot: {response}\")
                    
                    # If we don't know, ask user and learn (text mode)
                    if response.startswith(\"Mujhe iska jawab nahi pata.\"):
                        self._learn_from_user_text(safe_input)
                except KeyboardInterrupt:
                    print(\"\\r\\n[BOT] Bot:  Chat band kar raha hun. Alvida!\")
                    # End-of-conversation summary even on interrupt
                    self._print_session_summary()
                    break
                except Exception as e:
                    self.logger.error(\"Text chat error\", error=e)
                    print(f\"[ERROR] Error: {e}\")
                    
        except Exception as e:
            self.logger.error(\"Text chat mode error\", error=e)

    def _text_teaching_mode(self):
        \"\"\"Handle text-based teaching\"\"\"
        try:
            print(\"\\n[INFO] Teaching Mode Activated!\")
            print(\"-\"*30)
            
            # Get question
            question = input(\"[?] Question (sawal): \").strip()
            if not question:
                print(\"[BOT] Koi sawal nahi mila.\")
                return
            
            question = sanitize_user_input(question)
            if not is_safe_input(question):
                print(\"[BOT] Invalid question format.\")
                return
            
            # Get answer
            answer = input(\"[!] Answer (jawab): \").strip()
            if not answer:
                print(\"[BOT] Koi jawab nahi mila.\")
                return
            
            answer = sanitize_user_input(answer)
            if not is_safe_input(answer):
                print(\"[BOT] Invalid answer format.\")
                return
            
            # Confirm
            print(f\"\\n[SYNC] Confirmation: '{question}' -> '{answer}'\")
            confirm = input(\"[OK] Is this correct? (y/n): \").lower()
            
            if confirm in ['y', 'yes', 'han', 'haan']:
                if self.learning_manager.add_knowledge(question, answer):
                    print(\"[INFO] Successfully learned! Testing...\")
                    
                    # Test immediately
                    test_response = self.learning_manager.find_answer(question)
                    if test_response:
                        print(f\"[TEST] Test: {question} -> {test_response}\")
                        print(\"[OK] Teaching successful!\")
                    else:
                        print(\"[ERROR] Teaching failed - could not retrieve answer\")
                else:
                    print(\"[ERROR] Teaching failed - could not save knowledge\")
            else:
                print(\"[ERROR] Teaching cancelled.\")
                
        except Exception as e:
            self.logger.error(\"Text teaching error\", error=e)
            print(f\"[ERROR] Teaching error: {e}\")
        
        print(\"-\"*30)
        print(\"[NOTE] Back to normal chat...\")

    def _get_chat_response(self, query: str) -> str:
        \"\"\"Get chat response for a query\"\"\"
        try:
            # Try knowledge base first
            answer = self.learning_manager.find_answer(query)
            if answer:
                return answer
            
            # Keep only help queries as those are functional
            query_lower = query.lower()
            
            help_queries = ['help', 'madad', 'sahayata', 'guide']
            if any(word in query_lower for word in help_queries):
                return \"\"\"[INFO] Main in kaamon mein aapki madad kar sakta hun:

• Aapke sawaalon ka jawab de sakta hun
• Nayi jankari seekh sakta hun  
• Baatcheet kar sakta hun
• Madad aur sujhaav de sakta hun

Bas aap mujhse kuch bhi poochiye ya 'teach' kahkar mujhe nayi cheezon sikhaiye!\"\"\"
            
            # Default response (unknown) - follow the specified behavior
            return \"Mujhe iska jawab nahi pata. Kya aap mujhe iska sahi jawab bata sakte hai? Main ise yaad rakhunga.\"
            
        except Exception as e:
            self.logger.error(\"Chat response error\", error=e)
            return \"[ERROR] Kuch takneeki samasya aayi hai.\"

    def show_statistics(self):
        \"\"\"Show knowledge base statistics\"\"\"
        try:
            print(\"\\n[STATS] Knowledge Base Statistics\")
            print(\"=\"*40)
            
            stats = self.learning_manager.get_statistics()
            
            if 'error' in stats:
                print(f\"[ERROR] Error getting statistics: {stats['error']}\")
                return
            
            print(f\"[NOTE] Total Knowledge Entries: {stats['total_entries']}\")
            print(f\"[GRAPH] Recent Additions (24h): {stats['recent_additions']}\")
            print(f\"[STAR] Average Usage: {stats['average_usage']}\")
            
            if stats['most_used']:
                print(f\"[FIRE] Most Used: {stats['most_used']['question'][:50]}... ({stats['most_used']['count']} times)\")
            
            if stats['least_used']:
                print(f\"[ICE] Least Used: {stats['least_used']['question'][:50]}... ({stats['least_used']['count']} times)\")
            
            # Voice interface status (Simple EdgeTTS)
            print(f\"\\n[MIC] Voice Interface Status:\")
            print(f\"   EdgeTTS Initialized: {'[OK]' if is_voice_available() else '[ERROR]'}\")
            print(f\"   TTS Engine: EdgeTTS (hi-IN-MadhurNeural)\")
            print(f\"   Speech Recognition: Google API\")
            
        except Exception as e:
            self.logger.error(\"Statistics error\", error=e)
            print(f\"[ERROR] Statistics error: {e}\")
        
        input(\"\\nPress Enter to continue...\")

    def manage_knowledge(self):
        \"\"\"Knowledge management menu\"\"\"
        try:
            while True:
                print(\"\\n[FILES] Knowledge Management\")
                print(\"=\"*30)
                print(\"1. Export Knowledge\")
                print(\"2. Import Knowledge\") 
                print(\"3. Back to Main Menu\")
                
                choice = input(\"\\nChoose option (1-3): \").strip()
                
                if choice == '1':
                    self._export_knowledge()
                elif choice == '2':
                    self._import_knowledge()
                elif choice == '3':
                    break
                else:
                    print(\"[ERROR] Invalid choice!\")
                    
        except Exception as e:
            self.logger.error(\"Knowledge management error\", error=e)

    def _export_knowledge(self):
        \"\"\"Export knowledge to file\"\"\"
        try:
            filename = input(\"Enter filename (default: knowledge_export.json): \").strip()
            if not filename:
                filename = \"knowledge_export.json\"
            
            if self.learning_manager.export_knowledge(filename):
                print(f\"[OK] Knowledge exported to: {filename}\")
            else:
                print(\"[ERROR] Export failed\")
                
        except Exception as e:
            self.logger.error(\"Export error\", error=e)
            print(f\"[ERROR] Export error: {e}\")

    def _import_knowledge(self):
        \"\"\"Import knowledge from file\"\"\"
        try:
            filename = input(\"Enter filename to import: \").strip()
            if not filename:
                print(\"[ERROR] No filename provided\")
                return
            
            success, total = self.learning_manager.import_knowledge(filename)
            print(f\"[OK] Imported {success}/{total} entries\")
            
        except Exception as e:
            self.logger.error(\"Import error\", error=e)
            print(f\"[ERROR] Import error: {e}\")

    def cleanup(self):
        \"\"\"Cleanup resources\"\"\"
        try:
            self.logger.info(\"Cleaning up resources...\")
            
            if self.learning_manager:
                self.learning_manager.cleanup()
            
            # Simple voice interface doesn't need cleanup
            
            self.logger.info(\"Cleanup completed\")
            
        except Exception as e:
            self.logger.error(\"Cleanup error\", error=e)

    def _learn_from_user_text(self, question: str):
        \"\"\"Interactive learning flow for text mode when the bot doesn't know the answer.\"\"\"
        try:
            answer = input(\"[CHAT] Aapka jawab: \").strip()
            if not answer:
                print(\"[BOT] Bot: [ERROR] Koi jawab nahi mila. Agli baar koshish kariye.\")
                return
            
            # Confirm and save
            print(\"[BOT] Bot: Thik hai, main ise yaad rakhunga.\")
            if self.learning_manager.add_knowledge(question, answer):
                # Track for session summary
                self.learned_entries.append({\"question\": question, \"answer\": answer})
                
                # Optional: immediate test
                test = self.learning_manager.find_answer(question)
                if test:
                    print(f\"[TEST] Test: '{question}' -> '{test}'\")
                    print(\"[OK] Teaching successful!\")
                else:
                    print(\"[WARN] Test failed, but knowledge may be saved.\")
            else:
                print(\"[ERROR] Saving failed. Kripya fir se koshish karein.\")
        except Exception as e:
            self.logger.error(\"Text interactive learning error\", error=e)
            print(f\"[ERROR] Error: {e}\")

    def _learn_from_user_voice(self, question: str):
        \"\"\"Interactive learning flow for voice mode when the bot doesn't know the answer.\"\"\"
        try:
            # Ask for the correct answer via TTS and listen
            speak(\"Mujhe iska jawab nahi pata. Kya aap mujhe iska sahi jawab bata sakte hai? Main ise yaad rakhunga.\")
            print(\"[MIC] Correct answer सुनिए...\")
            answer = listen(timeout=20)
            if not answer:
                speak(\"Koi jawab nahi mila. Agli baar koshish kariye.\")
                print(\"[ERROR] Koi jawab nahi mila.\")
                return
            
            speak(\"Thik hai, main ise yaad rakhunga.\")
            if self.learning_manager.add_knowledge(question, answer):
                # Track for session summary
                self.learned_entries.append({\"question\": question, \"answer\": answer})
                # Optional: immediate test
                test = self.learning_manager.find_answer(question)
                if test:
                    speak(f\"Test: {question}\")
                    speak(f\"Jawab: {test}\")
                    print(f\"[TEST] Test: '{question}' -> '{test}'\")
                else:
                    speak(\"Test mein samasya aayi. Lekin maine aapka jawab save kar liya hai.\")
                    print(\"[WARN] Test failed, but knowledge may be saved.\")
            else:
                speak(\"Save karne mein samasya aayi. Kripya fir se koshish karein.\")
                print(\"[ERROR] Saving failed.\")
        except Exception as e:
            self.logger.error(\"Voice interactive learning error\", error=e)
            print(f\"[ERROR] Error: {e}\")

    def _print_session_summary(self):
        \"\"\"Print a summary of all newly stored Q-A entries for this conversation session.\"\"\"
        if not self.learned_entries:
            return
        print(\"\\n[NOTE] Conversation Summary - Newly Stored Knowledge\")
        print(\"=\"*50)
        for idx, entry in enumerate(self.learned_entries, start=1):
            q = entry.get(\"question\", \"\")
            a = entry.get(\"answer\", \"\")
            print(f\"{idx}. Question: {q}\")
            print(f\"   Answer:   {a}\")
        print(\"=\"*50)
        # Optionally clear after summary so the next conversation starts fresh
        self.learned_entries.clear()

def main():
    \"\"\"Main function\"\"\"
    parser = argparse.ArgumentParser(description='Adaptive Chatbot - AI Assistant that learns from you')
    parser.add_argument('--mode', choices=['menu', 'voice', 'text'], default='menu',
                       help='Start mode: menu (default), voice, or text')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--version', action='version', 
                       version=f'Adaptive Chatbot v{config.get(\"app\", \"version\", \"1.0.0\")}')
    
    args = parser.parse_args()
    
    # Set debug mode
    if args.debug:
        config.set('app', 'debug_mode', True)
        logger.info(\"Debug mode enabled\")
    
    try:
        # Initialize chatbot
        chatbot = AdaptiveChatbot(config, logger)
        
        # Run based on mode
        if args.mode == 'menu':
            chatbot.run_interactive_menu()
        elif args.mode == 'voice':
            chatbot.run_voice_chat()
        elif args.mode == 'text':
            chatbot.run_text_chat()
            
    except KeyboardInterrupt:
        logger.info(\"\\nApplication interrupted by user\")
    except Exception as e:
        logger.error(\"Application error\", error=e)
        print(f\"[ERROR] Critical error: {e}\")
        sys.exit(1)

if __name__ == \"__main__\":
    main()