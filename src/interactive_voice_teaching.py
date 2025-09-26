#!/usr/bin/env python3
"""
Interactive Voice Teaching System
Uses the enhanced voice interface for natural speech recognition and TTS
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_voice_interface import EnhancedVoiceInterface
import json
import time

class LearningManager:
    """Manages the chatbot's knowledge base and learning capabilities"""
    
    def __init__(self, knowledge_file="knowledge_base.json"):
        self.knowledge_file = knowledge_file
        self.knowledge_base = self.load_knowledge()
    
    def load_knowledge(self):
        """Load existing knowledge base from file"""
        try:
            with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create empty knowledge base if file doesn't exist
            return {}
    
    def save_knowledge(self):
        """Save current knowledge base to file"""
        with open(self.knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
    
    def add_knowledge(self, question, answer):
        """Add new knowledge to the knowledge base"""
        # Clean and normalize the question
        question_key = question.lower().strip()
        self.knowledge_base[question_key] = answer.strip()
        self.save_knowledge()
        print(f"✅ Learned: '{question}' -> '{answer}'")
    
    def find_answer(self, query):
        """Find answer for a given query"""
        query_clean = query.lower().strip()
        
        # Direct match
        if query_clean in self.knowledge_base:
            return self.knowledge_base[query_clean]
        
        # Partial match
        for question, answer in self.knowledge_base.items():
            if query_clean in question or question in query_clean:
                return answer
        
        return None

class InteractiveVoiceTeacher:
    """Interactive voice teaching system"""
    
    def __init__(self):
        self.voice = EnhancedVoiceInterface()
        self.learning_manager = LearningManager()
        self.setup_voice()
    
    def setup_voice(self):
        """Setup voice interface with optimized settings"""
        print("🎤 Setting up voice interface...")
        
        # Setup speech recognition
        self.voice.setup_speech_recognition(
            engine="google",  # Try Google first for better accuracy
            language="hi-IN"
        )
        
        # Setup TTS
        self.voice.setup_tts(
            engine="sapi",  # Use Windows SAPI for natural voice
            voice_id=0
        )
        
        print("✅ Voice interface ready!")
    
    def listen_with_retry(self, prompt=""):
        """Listen with multiple retries and fallback options"""
        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts:
            try:
                if prompt:
                    print(f"\n💭 {prompt}")
                    self.voice.text_to_speech(prompt)
                
                print("🎤 Listening... (speak clearly)")
                result = self.voice.speech_to_text(timeout=10)
                
                if result and result.strip():
                    print(f"👂 I heard: '{result}'")
                    return result.strip()
                else:
                    attempts += 1
                    self.voice.text_to_speech(f"मुझे समझ नहीं आया। कृपया फिर से बोलें। {max_attempts - attempts} attempts left.")
                    
            except Exception as e:
                attempts += 1
                print(f"❌ Recognition error: {e}")
                if attempts < max_attempts:
                    self.voice.text_to_speech("Sorry, please try again.")
        
        print("❌ Could not understand after 3 attempts")
        return None
    
    def interactive_teaching_session(self):
        """Run an interactive teaching session"""
        print("\n🎓 Interactive Voice Teaching Session")
        print("=" * 50)
        
        # Welcome message
        welcome_msg = "नमस्ते! आइए मुझे कुछ नया सिखाएं। बस 'टीच' बोलें।"
        print(f"🤖 {welcome_msg}")
        self.voice.text_to_speech(welcome_msg)
        
        while True:
            # Wait for "teach" command
            command = self.listen_with_retry("Ready! Say 'teach' to start teaching or 'exit' to quit:")
            
            if not command:
                continue
            
            command_lower = command.lower()
            
            if any(word in command_lower for word in ['exit', 'quit', 'bye', 'बाई', 'exit']):
                goodbye_msg = "धन्यवाद! मैंने बहुत कुछ सीखा।"
                print(f"🤖 {goodbye_msg}")
                self.voice.text_to_speech(goodbye_msg)
                break
            
            if any(word in command_lower for word in ['teach', 'टीच', 'सिखा', 'learn']):
                self.teaching_workflow()
            else:
                # Try to answer the question
                answer = self.learning_manager.find_answer(command)
                if answer:
                    response = f"जी हां! {answer}"
                    print(f"🤖 {response}")
                    self.voice.text_to_speech(response)
                else:
                    not_found_msg = "मुझे इसका जवाब नहीं पता। आप मुझे 'टीच' कहकर सिखा सकते हैं।"
                    print(f"🤖 {not_found_msg}")
                    self.voice.text_to_speech(not_found_msg)
    
    def teaching_workflow(self):
        """Execute the step-by-step teaching workflow"""
        print("\n📚 Starting Teaching Process...")
        
        # Step 1: Get the question
        question_prompt = "अच्छा! अब मुझे बताएं कि आप क्या सवाल सिखाना चाहते हैं?"
        question = self.listen_with_retry(question_prompt)
        
        if not question:
            self.voice.text_to_speech("कोई सवाल नहीं मिला। कृपया फिर से कोशिश करें।")
            return
        
        print(f"📝 Question: {question}")
        
        # Step 2: Get the answer
        answer_prompt = f"बहुत अच्छा! अब बताएं कि '{question}' का जवाब क्या है?"
        answer = self.listen_with_retry(answer_prompt)
        
        if not answer:
            self.voice.text_to_speech("कोई जवाब नहीं मिला। कृपया फिर से कोशिश करें।")
            return
        
        print(f"✍️ Answer: {answer}")
        
        # Step 3: Confirm and save
        confirm_msg = f"समझ गया! तो '{question}' का जवाब है '{answer}'. यह सही है?"
        print(f"🤖 {confirm_msg}")
        self.voice.text_to_speech(confirm_msg)
        
        confirmation = self.listen_with_retry("Say 'yes' or 'हाँ' to confirm, 'no' या 'नहीं' to cancel:")
        
        if confirmation and any(word in confirmation.lower() for word in ['yes', 'हाँ', 'हां', 'correct', 'सही', 'यस']):
            # Save the knowledge
            self.learning_manager.add_knowledge(question, answer)
            
            success_msg = "धन्यवाद! मैंने यह सीख लिया है।"
            print(f"🤖 {success_msg}")
            self.voice.text_to_speech(success_msg)
            
            # Step 4: Test the learning immediately
            self.test_new_knowledge(question)
        else:
            cancel_msg = "ठीक है, मैंने यह नहीं सीखा। कृपया फिर से कोशिश करें।"
            print(f"🤖 {cancel_msg}")
            self.voice.text_to_speech(cancel_msg)
    
    def test_new_knowledge(self, question):
        """Test the newly learned knowledge"""
        print(f"\n🧪 Testing new knowledge...")
        
        test_msg = f"चलिए टेस्ट करते हैं। {question}"
        print(f"🤖 {test_msg}")
        self.voice.text_to_speech(test_msg)
        
        # Wait a moment
        time.sleep(1)
        
        # Get the answer
        answer = self.learning_manager.find_answer(question)
        if answer:
            response = f"जवाब: {answer}"
            print(f"🤖 {response}")
            self.voice.text_to_speech(response)
            
            celebration_msg = "बहुत अच्छा! मैंने सफलतापूर्वक सीख लिया!"
            print(f"🤖 {celebration_msg}")
            self.voice.text_to_speech(celebration_msg)
        else:
            error_msg = "कुछ गलत हुआ। मैं अपना जवाब नहीं पा सका।"
            print(f"🤖 {error_msg}")
            self.voice.text_to_speech(error_msg)

def main():
    """Main function to run the interactive voice teaching system"""
    try:
        print("🚀 Starting Interactive Voice Teaching System...")
        teacher = InteractiveVoiceTeacher()
        teacher.interactive_teaching_session()
        
    except KeyboardInterrupt:
        print("\n👋 Teaching session interrupted by user.")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your microphone is connected and working.")

if __name__ == "__main__":
    main()