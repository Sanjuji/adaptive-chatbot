#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NLP Integration Module
Connects advanced NLP capabilities with existing adaptive chatbot
"""

import os
import sys
from typing import Dict, Any, Optional

# Import advanced NLP first
try:
    from advanced_nlp import get_nlp_engine, analyze_and_respond
    NLP_AVAILABLE = True
except ImportError as e:
    print(f"❌ Advanced NLP not available: {e}")
    NLP_AVAILABLE = False

# Import existing modules
try:
    from learning_manager import LearningManager
    LEARNING_AVAILABLE = True
except ImportError:
    LEARNING_AVAILABLE = False

try:
    from voice_response_system import VoiceResponseSystem
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

try:
    from logger import log_info, log_error, log_warning
except ImportError:
    # Fallback logging
    def log_info(msg): print(f"INFO - {msg}")
    def log_error(msg): print(f"ERROR - {msg}")
    def log_warning(msg): print(f"WARNING - {msg}")

class SmartChatbotIntegration:
    """
    Integration class that combines:
    - Advanced NLP for language understanding
    - Existing learning manager for knowledge
    - Voice response system for speech output
    """
    
    def __init__(self):
        if not NLP_AVAILABLE:
            raise ImportError("Advanced NLP engine is required but not available")
        
        self.nlp_engine = get_nlp_engine()
        
        # Initialize learning manager if available
        if LEARNING_AVAILABLE:
            try:
                self.learning_manager = LearningManager()
                log_info("✅ Learning Manager initialized")
            except Exception as e:
                log_error(f"Learning Manager initialization failed: {e}")
                self.learning_manager = None
        else:
            log_warning("Learning Manager not available")
            self.learning_manager = None
        
        # Initialize voice system if available
        if VOICE_AVAILABLE:
            try:
                self.voice_system = VoiceResponseSystem()
                log_info("✅ Voice Response System initialized")
            except Exception as e:
                log_error(f"Voice System initialization failed: {e}")
                self.voice_system = None
        else:
            log_warning("Voice Response System not available")
            self.voice_system = None
        
        log_info("🤖 Smart Chatbot Integration initialized")
    
    def process_user_input(self, user_input: str, speak_response: bool = True) -> Dict[str, Any]:
        """
        Process user input using advanced NLP and existing knowledge base
        
        Args:
            user_input: User's text input
            speak_response: Whether to speak the response
            
        Returns:
            Dict containing response and analysis data
        """
        try:
            # Step 1: Advanced NLP analysis
            log_info(f"🔍 Analyzing input: {user_input}")
            
            # Get NLP analysis
            nlp_result = self.nlp_engine.generate_response(user_input)
            
            language_info = nlp_result['language_info']
            intent_info = nlp_result['intent_info']
            sentiment_info = nlp_result['sentiment_info']
            
            log_info(f"Language: {language_info.language_name}, Intent: {intent_info['intent']}, Sentiment: {sentiment_info['sentiment']}")
            
            # Step 2: Check existing knowledge base for questions
            knowledge_response = None
            if intent_info['intent'] == 'question' and self.learning_manager:
                knowledge_response = self.learning_manager.get_answer(user_input)
                if knowledge_response:
                    log_info("📚 Found answer in knowledge base")
            
            # Step 3: Generate appropriate response
            if knowledge_response:
                # Use knowledge base answer with NLP context
                response_text = knowledge_response
                response_source = "knowledge_base"
            else:
                # Use NLP-generated response
                response_text = nlp_result['response_text']
                response_source = "nlp_engine"
            
            # Step 4: Handle learning requests
            if intent_info['intent'] == 'learning' or "teach me" in user_input.lower():
                if self.learning_manager:
                    response_text = self._handle_learning_request(user_input, language_info.detected_language)
                    response_source = "learning_system"
            
            # Step 5: Select appropriate voice for response
            suggested_voice = nlp_result['suggested_voice']
            
            # Step 6: Speak response if requested
            if speak_response and self.voice_system:
                self._speak_response(response_text, suggested_voice, language_info.detected_language)
            
            # Step 7: Return comprehensive result
            return {
                "response_text": response_text,
                "response_source": response_source,
                "language_info": language_info,
                "intent_info": intent_info,
                "sentiment_info": sentiment_info,
                "suggested_voice": suggested_voice,
                "knowledge_found": knowledge_response is not None,
                "conversation_context": nlp_result.get('conversation_context'),
                "success": True
            }
            
        except Exception as e:
            log_error(f"Error processing user input: {e}")
            return {
                "response_text": "I'm sorry, I encountered an error. Please try again.",
                "response_source": "error",
                "success": False,
                "error": str(e)
            }
    
    def _handle_learning_request(self, user_input: str, language: str) -> str:
        """Handle requests to learn new information"""
        
        learning_prompts = {
            'hi': [
                "मैं सीखने के लिए तैयार हूँ! आप मुझे क्या सिखाना चाहते हैं?",
                "बताइए क्या सिखाना है? मैं ध्यान से सुनूंगा।",
                "कुछ नया सीखने के लिए उत्सुक हूँ! शुरू करिए।"
            ],
            'en': [
                "I'm ready to learn! What would you like to teach me?",
                "Please tell me what you'd like me to learn. I'm listening carefully.",
                "I'm excited to learn something new! Please go ahead."
            ],
            'es': [
                "¡Estoy listo para aprender! ¿Qué te gustaría enseñarme?",
                "Por favor dime qué quieres que aprenda."
            ],
            'fr': [
                "Je suis prêt à apprendre! Que voudriez-vous m'enseigner?",
                "Dites-moi ce que vous aimeriez que j'apprenne."
            ]
        }
        
        prompts = learning_prompts.get(language, learning_prompts['en'])
        return prompts[0]  # Can be randomized
    
    def _speak_response(self, text: str, voice: str, language: str):
        """Speak the response using appropriate voice"""
        try:
            if self.voice_system:
                # Use suggested voice from NLP analysis
                self.voice_system.speak_text(text, voice=voice)
                log_info(f"🔊 Spoke response using voice: {voice}")
        except Exception as e:
            log_warning(f"Could not speak response: {e}")
    
    def teach_chatbot(self, question: str, answer: str, language: str = None) -> Dict[str, Any]:
        """
        Teach the chatbot new information
        
        Args:
            question: The question to learn
            answer: The answer to associate with the question
            language: Optional language code
            
        Returns:
            Dict with learning result
        """
        try:
            if not self.learning_manager:
                return {"success": False, "message": "Learning system not available"}
            
            # Use NLP to analyze the question
            nlp_result = self.nlp_engine.generate_response(question)
            detected_language = nlp_result['language_info'].detected_language
            
            # Store in learning manager
            success = self.learning_manager.learn(question, answer)
            
            if success:
                response_text = self._get_learning_success_message(detected_language)
                log_info(f"✅ Learned: {question} -> {answer}")
            else:
                response_text = self._get_learning_failure_message(detected_language)
                log_warning(f"❌ Failed to learn: {question} -> {answer}")
            
            return {
                "success": success,
                "message": response_text,
                "language": detected_language,
                "question": question,
                "answer": answer
            }
            
        except Exception as e:
            log_error(f"Teaching failed: {e}")
            return {"success": False, "message": f"Teaching failed: {e}"}
    
    def _get_learning_success_message(self, language: str) -> str:
        """Get success message in appropriate language"""
        messages = {
            'hi': "बहुत अच्छा! मैंने यह सीख लिया है। अब मैं इस सवाल का जवाब दे सकूंगा।",
            'en': "Great! I've learned this. Now I can answer this question.",
            'es': "¡Genial! He aprendido esto. Ahora puedo responder esta pregunta.",
            'fr': "Excellent! J'ai appris cela. Maintenant je peux répondre à cette question."
        }
        return messages.get(language, messages['en'])
    
    def _get_learning_failure_message(self, language: str) -> str:
        """Get failure message in appropriate language"""
        messages = {
            'hi': "माफ करें, मुझे यह सीखने में समस्या हुई। कृपया दोबारा कोशिश करें।",
            'en': "Sorry, I had trouble learning this. Please try again.",
            'es': "Lo siento, tuve problemas para aprender esto. Por favor intenta de nuevo.",
            'fr': "Désolé, j'ai eu des problèmes pour apprendre cela. Veuillez réessayer."
        }
        return messages.get(language, messages['en'])
    
    def get_conversation_statistics(self) -> Dict[str, Any]:
        """Get conversation statistics and insights"""
        try:
            # Get NLP conversation summary
            nlp_summary = self.nlp_engine.get_conversation_summary()
            
            # Get learning manager statistics if available
            learning_stats = {}
            if self.learning_manager:
                try:
                    learning_stats = {
                        "knowledge_entries": len(self.learning_manager.knowledge),
                        "recent_learning": "Available" if hasattr(self.learning_manager, 'get_recent_learning') else "Not available"
                    }
                except:
                    learning_stats = {"status": "Learning stats unavailable"}
            
            return {
                "conversation_summary": nlp_summary,
                "learning_statistics": learning_stats,
                "nlp_engine_status": "Active",
                "voice_system_status": "Active" if self.voice_system else "Inactive"
            }
            
        except Exception as e:
            log_error(f"Error getting statistics: {e}")
            return {"error": str(e)}
    
    def set_voice_settings(self, voice: str = None, rate: int = None, volume: float = None):
        """Configure voice settings"""
        try:
            if self.voice_system:
                if hasattr(self.voice_system, 'set_voice_settings'):
                    self.voice_system.set_voice_settings(voice=voice, rate=rate, volume=volume)
                    log_info(f"🔧 Voice settings updated: voice={voice}, rate={rate}, volume={volume}")
        except Exception as e:
            log_warning(f"Could not update voice settings: {e}")
    
    def process_batch_inputs(self, inputs: list) -> list:
        """Process multiple inputs in batch for testing"""
        results = []
        for user_input in inputs:
            result = self.process_user_input(user_input, speak_response=False)
            
            # Safely extract language info
            lang_info = result.get("language_info")
            language = getattr(lang_info, 'language_name', 'Unknown') if lang_info else 'Unknown'
            
            # Safely extract intent info
            intent_info = result.get("intent_info", {})
            intent = intent_info.get("intent", "unknown") if isinstance(intent_info, dict) else "unknown"
            
            # Safely extract sentiment info
            sentiment_info = result.get("sentiment_info", {})
            sentiment = sentiment_info.get("sentiment", "neutral") if isinstance(sentiment_info, dict) else "neutral"
            
            results.append({
                "input": user_input,
                "output": result["response_text"],
                "language": language,
                "intent": intent,
                "sentiment": sentiment
            })
        return results

# Global integration instance
_chatbot_integration = None

def get_smart_chatbot() -> SmartChatbotIntegration:
    """Get global chatbot integration instance"""
    global _chatbot_integration
    if _chatbot_integration is None:
        _chatbot_integration = SmartChatbotIntegration()
    return _chatbot_integration

def smart_chat(user_input: str, speak: bool = True) -> str:
    """Convenience function for simple chat interaction"""
    chatbot = get_smart_chatbot()
    result = chatbot.process_user_input(user_input, speak_response=speak)
    return result.get("response_text", "Sorry, I couldn't process that.")

if __name__ == "__main__":
    # Quick test of the integration
    print("🤖 Smart Chatbot Integration Test")
    print("=" * 50)
    
    chatbot = get_smart_chatbot()
    
    test_inputs = [
        "Hello!",
        "नमस्ते",
        "Switch ka price kya hai?",
        "Thank you!",
        "Teach me something",
        "Goodbye"
    ]
    
    for inp in test_inputs:
        result = chatbot.process_user_input(inp, speak_response=False)
        print(f"Input: {inp}")
        print(f"Output: {result['response_text']}")
        lang_name = getattr(result.get('language_info'), 'language_name', 'Unknown') if result.get('language_info') else 'Unknown'
        print(f"Language: {lang_name}")
        print("-" * 30)
