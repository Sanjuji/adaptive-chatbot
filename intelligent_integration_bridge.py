#!/usr/bin/env python3
"""
Intelligent Integration Bridge
Seamlessly integrates advanced NLP, electrical business logic, and existing systems
"""

import time
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import all systems
try:
    from nlp_integration import get_smart_chatbot
    from electrical_business_enhancer import get_electrical_enhancer
    from unified_learning_manager import UnifiedLearningManager
    from simple_voice import SimpleVoiceInterface
    from logger import log_info, log_error, log_warning
    INTEGRATION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Integration bridge incomplete: {e}")
    INTEGRATION_AVAILABLE = False

class IntelligentChatbotBridge:
    """
    Intelligent bridge that combines:
    - Advanced NLP (multilingual, sentiment, intent)
    - Electrical business domain knowledge  
    - Existing learning system
    - Voice interface
    - Context management
    """
    
    def __init__(self):
        self.nlp_chatbot = get_smart_chatbot() if INTEGRATION_AVAILABLE else None
        self.electrical_enhancer = get_electrical_enhancer() if INTEGRATION_AVAILABLE else None
        self.learning_manager = UnifiedLearningManager() if INTEGRATION_AVAILABLE else None
        self.voice_interface = SimpleVoiceInterface() if INTEGRATION_AVAILABLE else None
        
        self.conversation_history = []
        self.session_stats = {
            "start_time": datetime.now(),
            "interactions": 0,
            "successful_responses": 0,
            "knowledge_hits": 0,
            "electrical_queries": 0,
            "languages_detected": set(),
            "intents_detected": set()
        }
        
        # Initialize electrical knowledge
        self._initialize_electrical_knowledge()
        
    def _initialize_electrical_knowledge(self):
        """Initialize electrical business knowledge in learning manager"""
        if self.electrical_enhancer and self.learning_manager:
            try:
                added = self.electrical_enhancer.add_electrical_knowledge(self.learning_manager)
                if added:
                    log_info("✅ Electrical business knowledge loaded successfully")
                else:
                    log_warning("⚠️ Some electrical knowledge may already exist")
            except Exception as e:
                log_error(f"Failed to initialize electrical knowledge: {e}")
    
    def process_intelligent_query(self, user_input: str, speak_response: bool = False) -> Dict[str, Any]:
        """
        Intelligently process user query using all available systems:
        1. Advanced NLP analysis (language, intent, sentiment)
        2. Electrical business enhancement
        3. Knowledge base lookup
        4. Context-aware response generation
        5. Voice synthesis (optional)
        """
        
        start_time = time.time()
        result = {
            "user_input": user_input,
            "timestamp": datetime.now().isoformat(),
            "processing_time": 0,
            "success": False,
            "response_text": "",
            "confidence": 0.0,
            "sources": [],
            "analysis": {}
        }
        
        try:
            self.session_stats["interactions"] += 1
            log_info(f"🧠 Processing intelligent query: {user_input[:50]}...")
            
            # Step 1: Advanced NLP Analysis
            nlp_analysis = self._perform_nlp_analysis(user_input)
            result["analysis"]["nlp"] = nlp_analysis
            
            # Step 2: Electrical Business Enhancement
            electrical_analysis = self._perform_electrical_analysis(user_input)
            result["analysis"]["electrical"] = electrical_analysis
            
            # Step 3: Knowledge Base Lookup
            knowledge_response = self._lookup_knowledge(user_input, electrical_analysis)
            result["analysis"]["knowledge"] = knowledge_response
            
            # Step 4: Intelligent Response Generation
            intelligent_response = self._generate_intelligent_response(
                user_input, nlp_analysis, electrical_analysis, knowledge_response
            )
            result.update(intelligent_response)
            
            # Step 5: Voice Synthesis (if requested)
            if speak_response and self.voice_interface:
                self._speak_intelligent_response(result["response_text"], nlp_analysis)
            
            # Step 6: Update conversation context
            self._update_conversation_context(user_input, result)
            
            # Step 7: Update session statistics
            self._update_session_stats(nlp_analysis, electrical_analysis, result["success"])
            
            result["processing_time"] = round(time.time() - start_time, 3)
            result["success"] = True
            self.session_stats["successful_responses"] += 1
            
            log_info(f"✅ Query processed successfully in {result['processing_time']}s")
            
        except Exception as e:
            log_error(f"Intelligent query processing failed: {e}")
            result.update({
                "success": False,
                "error": str(e),
                "response_text": "I apologize, but I encountered a technical issue. Please try again.",
                "processing_time": round(time.time() - start_time, 3)
            })
        
        return result
    
    def _perform_nlp_analysis(self, user_input: str) -> Dict[str, Any]:
        """Perform advanced NLP analysis"""
        if not self.nlp_chatbot:
            return {"available": False, "error": "NLP system not available"}
        
        try:
            # Get comprehensive NLP analysis
            nlp_result = self.nlp_chatbot.nlp_engine.generate_response(user_input)
            
            return {
                "available": True,
                "language_info": {
                    "language": nlp_result['language_info'].detected_language,
                    "language_name": nlp_result['language_info'].language_name,
                    "confidence": nlp_result['language_info'].confidence,
                    "is_mixed": getattr(nlp_result['language_info'], 'is_mixed_language', False)
                },
                "intent_info": nlp_result['intent_info'],
                "sentiment_info": nlp_result['sentiment_info'],
                "suggested_voice": nlp_result['suggested_voice']
            }
            
        except Exception as e:
            log_warning(f"NLP analysis failed: {e}")
            return {"available": False, "error": str(e)}
    
    def _perform_electrical_analysis(self, user_input: str) -> Dict[str, Any]:
        """Perform electrical business specific analysis"""
        if not self.electrical_enhancer:
            return {"available": False, "error": "Electrical enhancer not available"}
        
        try:
            # Enhanced intent recognition for electrical domain
            enhanced_intent = self.electrical_enhancer.enhance_intent_recognition(user_input)
            
            # Product identification
            identified_products = self.electrical_enhancer.identify_products(user_input)
            
            # Electrical knowledge lookup
            electrical_knowledge = self.electrical_enhancer.get_electrical_knowledge(user_input)
            
            # Query suggestions
            suggestions = self.electrical_enhancer.get_electrical_suggestions(user_input)
            
            return {
                "available": True,
                "enhanced_intent": enhanced_intent,
                "identified_products": identified_products,
                "electrical_knowledge": electrical_knowledge,
                "suggestions": suggestions,
                "is_electrical_query": len(identified_products) > 0 or enhanced_intent.get('electrical_specific', False)
            }
            
        except Exception as e:
            log_warning(f"Electrical analysis failed: {e}")
            return {"available": False, "error": str(e)}
    
    def _lookup_knowledge(self, user_input: str, electrical_analysis: Dict) -> Dict[str, Any]:
        """Lookup knowledge from all available sources"""
        knowledge_result = {
            "traditional_kb": None,
            "electrical_kb": None,
            "best_match": None,
            "confidence": 0.0
        }
        
        try:
            # Traditional knowledge base lookup
            if self.learning_manager:
                traditional_answer = self.learning_manager.find_answer(user_input)
                if traditional_answer:
                    knowledge_result["traditional_kb"] = traditional_answer
                    knowledge_result["confidence"] = max(knowledge_result["confidence"], 0.8)
            
            # Electrical knowledge base lookup
            if electrical_analysis.get("available") and electrical_analysis.get("electrical_knowledge"):
                knowledge_result["electrical_kb"] = electrical_analysis["electrical_knowledge"]
                knowledge_result["confidence"] = max(knowledge_result["confidence"], 0.9)
            
            # Determine best match
            if knowledge_result["electrical_kb"] and electrical_analysis.get("is_electrical_query"):
                knowledge_result["best_match"] = knowledge_result["electrical_kb"]
                knowledge_result["source"] = "electrical_kb"
            elif knowledge_result["traditional_kb"]:
                knowledge_result["best_match"] = knowledge_result["traditional_kb"]
                knowledge_result["source"] = "traditional_kb"
            
            if knowledge_result["best_match"]:
                self.session_stats["knowledge_hits"] += 1
                
        except Exception as e:
            log_warning(f"Knowledge lookup failed: {e}")
            knowledge_result["error"] = str(e)
        
        return knowledge_result
    
    def _generate_intelligent_response(self, user_input: str, nlp_analysis: Dict, 
                                     electrical_analysis: Dict, knowledge_response: Dict) -> Dict[str, Any]:
        """Generate intelligent response using all available information"""
        
        response_result = {
            "response_text": "",
            "confidence": 0.0,
            "sources": [],
            "response_type": "unknown"
        }
        
        try:
            # Priority 1: Direct knowledge match
            if knowledge_response.get("best_match"):
                response_result.update({
                    "response_text": knowledge_response["best_match"],
                    "confidence": knowledge_response.get("confidence", 0.8),
                    "sources": [knowledge_response.get("source", "knowledge_base")],
                    "response_type": "knowledge_based"
                })
                
                # Add electrical context if relevant
                if electrical_analysis.get("is_electrical_query"):
                    self.session_stats["electrical_queries"] += 1
                
                return response_result
            
            # Priority 2: Electrical business specific response
            if electrical_analysis.get("available") and electrical_analysis.get("is_electrical_query"):
                intent_info = electrical_analysis.get("enhanced_intent", {})
                electrical_response = self.electrical_enhancer.generate_electrical_response(user_input, intent_info)
                
                response_result.update({
                    "response_text": electrical_response,
                    "confidence": intent_info.get("confidence", 0.7),
                    "sources": ["electrical_business"],
                    "response_type": "electrical_specific"
                })
                
                self.session_stats["electrical_queries"] += 1
                return response_result
            
            # Priority 3: NLP-powered contextual response
            if nlp_analysis.get("available"):
                # Use the advanced NLP system for general responses
                nlp_response = self.nlp_chatbot.process_user_input(user_input, speak_response=False)
                
                response_result.update({
                    "response_text": nlp_response["response_text"],
                    "confidence": nlp_response.get("intent_info", {}).get("confidence", 0.6),
                    "sources": ["advanced_nlp"],
                    "response_type": "nlp_generated"
                })
                
                return response_result
            
            # Fallback: Basic response
            response_result.update({
                "response_text": "मैं आपकी बात समझ गया हूँ। आप मुझसे electrical items, prices, या services के बारे में पूछ सकते हैं।",
                "confidence": 0.5,
                "sources": ["fallback"],
                "response_type": "fallback"
            })
            
        except Exception as e:
            log_error(f"Response generation failed: {e}")
            response_result.update({
                "response_text": "माफ करिए, मुझे आपका जवाब देने में तकनीकी समस्या आई है। कृपया दोबारा कोशिश करें।",
                "confidence": 0.3,
                "sources": ["error"],
                "response_type": "error",
                "error": str(e)
            })
        
        return response_result
    
    def _speak_intelligent_response(self, response_text: str, nlp_analysis: Dict):
        """Speak response using intelligent voice selection"""
        try:
            if not self.voice_interface:
                return
            
            # Use voice suggestion from NLP analysis if available
            if nlp_analysis.get("available") and nlp_analysis.get("suggested_voice"):
                # For now, use the default voice since EdgeTTS voice switching is complex
                success = self.voice_interface.speak(response_text)
                if success:
                    log_info(f"🔊 Spoke response using intelligent voice selection")
                else:
                    log_warning("Voice synthesis failed")
            else:
                # Fallback to default voice
                self.voice_interface.speak(response_text)
                
        except Exception as e:
            log_warning(f"Intelligent voice synthesis failed: {e}")
    
    def _update_conversation_context(self, user_input: str, result: Dict[str, Any]):
        """Update conversation context and history"""
        try:
            conversation_entry = {
                "timestamp": result["timestamp"],
                "user_input": user_input,
                "response": result["response_text"],
                "confidence": result["confidence"],
                "sources": result["sources"],
                "response_type": result["response_type"],
                "processing_time": result["processing_time"],
                "success": result["success"]
            }
            
            # Add analysis data
            if "analysis" in result:
                if result["analysis"].get("nlp", {}).get("available"):
                    nlp = result["analysis"]["nlp"]
                    conversation_entry.update({
                        "language": nlp.get("language_info", {}).get("language"),
                        "intent": nlp.get("intent_info", {}).get("intent"),
                        "sentiment": nlp.get("sentiment_info", {}).get("sentiment")
                    })
                
                if result["analysis"].get("electrical", {}).get("is_electrical_query"):
                    conversation_entry["electrical_query"] = True
                    electrical = result["analysis"]["electrical"]
                    conversation_entry["products"] = [p["product"] for p in electrical.get("identified_products", [])]
            
            self.conversation_history.append(conversation_entry)
            
            # Keep only last 50 conversations to manage memory
            if len(self.conversation_history) > 50:
                self.conversation_history = self.conversation_history[-50:]
                
        except Exception as e:
            log_warning(f"Failed to update conversation context: {e}")
    
    def _update_session_stats(self, nlp_analysis: Dict, electrical_analysis: Dict, success: bool):
        """Update session statistics"""
        try:
            if success:
                # Track languages
                if nlp_analysis.get("available"):
                    lang = nlp_analysis.get("language_info", {}).get("language")
                    if lang:
                        self.session_stats["languages_detected"].add(lang)
                    
                    # Track intents
                    intent = nlp_analysis.get("intent_info", {}).get("intent")
                    if intent:
                        self.session_stats["intents_detected"].add(intent)
                
                # Track electrical queries
                if electrical_analysis.get("is_electrical_query"):
                    self.session_stats["electrical_queries"] += 1
                    
        except Exception as e:
            log_warning(f"Failed to update session stats: {e}")
    
    def get_intelligent_statistics(self) -> Dict[str, Any]:
        """Get comprehensive intelligent chatbot statistics"""
        try:
            current_time = datetime.now()
            session_duration = (current_time - self.session_stats["start_time"]).total_seconds()
            
            stats = {
                "session_info": {
                    "start_time": self.session_stats["start_time"].isoformat(),
                    "current_time": current_time.isoformat(),
                    "duration_seconds": round(session_duration),
                    "duration_formatted": self._format_duration(session_duration)
                },
                
                "interaction_stats": {
                    "total_interactions": self.session_stats["interactions"],
                    "successful_responses": self.session_stats["successful_responses"],
                    "success_rate": (self.session_stats["successful_responses"] / max(self.session_stats["interactions"], 1)) * 100,
                    "knowledge_hits": self.session_stats["knowledge_hits"],
                    "electrical_queries": self.session_stats["electrical_queries"]
                },
                
                "language_analysis": {
                    "languages_detected": list(self.session_stats["languages_detected"]),
                    "total_languages": len(self.session_stats["languages_detected"]),
                    "intents_detected": list(self.session_stats["intents_detected"]),
                    "total_intents": len(self.session_stats["intents_detected"])
                },
                
                "system_status": {
                    "nlp_system": "Available" if self.nlp_chatbot else "Unavailable",
                    "electrical_enhancer": "Available" if self.electrical_enhancer else "Unavailable", 
                    "learning_manager": "Available" if self.learning_manager else "Unavailable",
                    "voice_interface": "Available" if self.voice_interface else "Unavailable"
                },
                
                "conversation_analysis": self._analyze_conversation_patterns()
            }
            
            return stats
            
        except Exception as e:
            log_error(f"Failed to get intelligent statistics: {e}")
            return {"error": str(e)}
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds//60)}m {int(seconds%60)}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def _analyze_conversation_patterns(self) -> Dict[str, Any]:
        """Analyze conversation patterns for insights"""
        try:
            if not self.conversation_history:
                return {"message": "No conversation data available"}
            
            # Analyze response types
            response_types = {}
            languages = {}
            intents = {}
            avg_processing_time = 0
            
            for entry in self.conversation_history:
                # Response types
                resp_type = entry.get("response_type", "unknown")
                response_types[resp_type] = response_types.get(resp_type, 0) + 1
                
                # Languages
                lang = entry.get("language", "unknown")
                languages[lang] = languages.get(lang, 0) + 1
                
                # Intents
                intent = entry.get("intent", "unknown")
                intents[intent] = intents.get(intent, 0) + 1
                
                # Processing time
                avg_processing_time += entry.get("processing_time", 0)
            
            avg_processing_time /= len(self.conversation_history)
            
            return {
                "total_conversations": len(self.conversation_history),
                "response_type_distribution": response_types,
                "language_distribution": languages,
                "intent_distribution": intents,
                "average_processing_time": round(avg_processing_time, 3),
                "most_common_language": max(languages.items(), key=lambda x: x[1])[0] if languages else "none",
                "most_common_intent": max(intents.items(), key=lambda x: x[1])[0] if intents else "none"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def teach_intelligent_system(self, question: str, answer: str) -> Dict[str, Any]:
        """Teach the intelligent system using all available methods"""
        try:
            result = {
                "success": False,
                "methods_used": [],
                "analysis": {}
            }
            
            # Analyze the question first
            if self.nlp_chatbot:
                nlp_analysis = self.nlp_chatbot.nlp_engine.detect_language(question)
                intent_analysis = self.nlp_chatbot.nlp_engine.extract_intent(question)
                result["analysis"]["language"] = nlp_analysis.language_name
                result["analysis"]["intent"] = intent_analysis["intent"]
            
            # Add to traditional learning manager
            if self.learning_manager:
                if self.learning_manager.add_knowledge(question, answer):
                    result["methods_used"].append("traditional_learning")
                    result["success"] = True
            
            # If it's electrical related, also add context
            if self.electrical_enhancer:
                products = self.electrical_enhancer.identify_products(question)
                if products:
                    result["analysis"]["products"] = [p["product"] for p in products]
                    result["analysis"]["electrical_related"] = True
            
            return result
            
        except Exception as e:
            log_error(f"Intelligent teaching failed: {e}")
            return {"success": False, "error": str(e)}

# Global intelligent bridge instance
_intelligent_bridge = None

def get_intelligent_bridge() -> IntelligentChatbotBridge:
    """Get global intelligent chatbot bridge instance"""
    global _intelligent_bridge
    if _intelligent_bridge is None:
        _intelligent_bridge = IntelligentChatbotBridge()
    return _intelligent_bridge

def smart_intelligent_chat(user_input: str, speak: bool = False) -> str:
    """Convenience function for intelligent chat"""
    bridge = get_intelligent_bridge()
    result = bridge.process_intelligent_query(user_input, speak_response=speak)
    return result.get("response_text", "Sorry, I couldn't process that request.")

if __name__ == "__main__":
    # Test the intelligent bridge
    print("🧠 Intelligent Integration Bridge Test")
    print("=" * 60)
    
    bridge = get_intelligent_bridge()
    
    test_queries = [
        "Hello! How are you?",
        "नमस्ते, कैसे हैं आप?", 
        "Switch ka price kya hai?",
        "Wire kitne ka milta hai?",
        "Electrical shop ka address kya hai?",
        "Thank you for helping!",
        "MCB installation charges",
        "Bulb repair service"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        result = bridge.process_intelligent_query(query)
        
        print(f"🤖 Response: {result['response_text']}")
        print(f"⚡ Processed in: {result['processing_time']}s")
        print(f"🎯 Confidence: {result['confidence']:.2f}")
        print(f"📊 Sources: {', '.join(result['sources'])}")
        print(f"🔧 Type: {result['response_type']}")
        
        if result.get('analysis', {}).get('electrical', {}).get('identified_products'):
            products = result['analysis']['electrical']['identified_products']
            print(f"🔌 Products: {[p['product'] for p in products]}")
        
        print("-" * 50)
    
    # Show final statistics
    print("\n📊 SESSION STATISTICS:")
    stats = bridge.get_intelligent_statistics()
    
    interaction_stats = stats.get('interaction_stats', {})
    print(f"• Total interactions: {interaction_stats.get('total_interactions', 0)}")
    print(f"• Success rate: {interaction_stats.get('success_rate', 0):.1f}%")
    print(f"• Electrical queries: {interaction_stats.get('electrical_queries', 0)}")
    
    language_stats = stats.get('language_analysis', {})
    print(f"• Languages detected: {language_stats.get('total_languages', 0)}")
    print(f"• Intents detected: {language_stats.get('total_intents', 0)}")
    
    print(f"\n✅ Test completed successfully!")