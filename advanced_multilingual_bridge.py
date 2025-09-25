#!/usr/bin/env python3
"""
Advanced Multilingual Integration Bridge
Connects multilingual EdgeTTS system with existing adaptive chatbot
"""

import asyncio
import threading
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json

try:
    from multilingual_voice_system import get_multilingual_voice_system, speak_multilingual
    from adaptive_chatbot_enhanced import EnhancedAdaptiveChatbot
    from intelligent_integration_bridge import IntelligentChatbotBridge
    from logger import log_info, log_error, log_warning
except ImportError as e:
    print(f"Import error: {e}")
    def log_info(msg): print(f"INFO - {msg}")
    def log_error(msg): print(f"ERROR - {msg}")
    def log_warning(msg): print(f"WARNING - {msg}")

@dataclass
class MultilingualResponse:
    """Multilingual response with voice synthesis"""
    text: str
    language: str
    sentiment: str
    confidence: float
    voice_generated: bool
    response_time: float
    context: Dict[str, Any]

class AdvancedMultilingualBridge:
    """Advanced bridge integrating multilingual voice with intelligent chatbot"""
    
    def __init__(self):
        # Initialize components
        self.voice_system = get_multilingual_voice_system()
        self.adaptive_chatbot = None
        self.intelligence_bridge = None
        
        # Configuration
        self.config = {
            "auto_voice_enabled": True,
            "language_auto_detection": True,
            "voice_consistency_mode": True,
            "context_aware_responses": True,
            "multilingual_learning": True,
            "voice_feedback_enabled": True,
            "response_timeout": 30.0,
            "max_response_length": 500
        }
        
        # Session tracking
        self.session_stats = {
            "total_interactions": 0,
            "languages_used": set(),
            "average_response_time": 0.0,
            "voice_success_rate": 0.0,
            "multilingual_accuracy": 0.0,
            "user_satisfaction_score": 0.0
        }
        
        # Language-specific context
        self.language_contexts = {}
        self.conversation_memory = []
        
        # Initialize systems
        self._initialize_systems()
    
    def _initialize_systems(self):
        """Initialize all required systems"""
        try:
            # Initialize adaptive chatbot
            self.adaptive_chatbot = EnhancedAdaptiveChatbot()
            log_info("✅ Enhanced Adaptive Chatbot initialized")
            
            # Initialize intelligence bridge
            self.intelligence_bridge = IntelligentChatbotBridge()
            log_info("✅ Intelligence Integration Bridge initialized")
            
            # Configure voice system preferences
            self.voice_system.set_voice_preferences(
                auto_switch=True,
                consistency_mode=self.config["voice_consistency_mode"],
                style_adaptation=True
            )
            
            log_info("🌍 Advanced Multilingual Bridge fully initialized")
            
        except Exception as e:
            log_error(f"System initialization failed: {e}")
            raise
    
    async def process_multilingual_query(self, user_input: str, 
                                       detected_language: Optional[str] = None,
                                       user_context: Optional[Dict] = None) -> MultilingualResponse:
        """Process query with full multilingual intelligence and voice response"""
        
        start_time = time.time()
        
        try:
            # Detect language if not provided
            if not detected_language:
                detected_language = await self._detect_language_advanced(user_input)
            
            log_info(f"🗣️ Processing query in {detected_language}: {user_input[:50]}...")
            
            # Get intelligent response using the intelligence bridge
            intelligence_response = await self._get_intelligent_response(
                user_input, detected_language, user_context
            )
            
            # Extract response components
            response_text = intelligence_response.get("response", "I'm sorry, I couldn't understand that.")
            sentiment = intelligence_response.get("sentiment", "neutral")
            confidence = intelligence_response.get("confidence", 0.5)
            context = intelligence_response.get("context", {})
            
            # Enhance context with language-specific information
            enhanced_context = self._enhance_context_multilingual(
                context, detected_language, user_input, sentiment
            )
            
            # Generate voice response if enabled
            voice_generated = False
            if self.config["auto_voice_enabled"]:
                voice_generated = await self._generate_voice_response(
                    response_text, detected_language, sentiment, enhanced_context
                )
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Update session statistics
            self._update_session_stats(detected_language, response_time, voice_generated, confidence)
            
            # Store conversation memory
            self._store_conversation_memory(user_input, response_text, detected_language, enhanced_context)
            
            # Create multilingual response
            multilingual_response = MultilingualResponse(
                text=response_text,
                language=detected_language,
                sentiment=sentiment,
                confidence=confidence,
                voice_generated=voice_generated,
                response_time=response_time,
                context=enhanced_context
            )
            
            log_info(f"✅ Multilingual response generated in {response_time:.2f}s (Voice: {voice_generated})")
            return multilingual_response
            
        except Exception as e:
            log_error(f"Multilingual query processing failed: {e}")
            
            # Return error response
            return MultilingualResponse(
                text="I apologize, but I encountered an error processing your request.",
                language=detected_language or "en",
                sentiment="apologetic",
                confidence=0.0,
                voice_generated=False,
                response_time=time.time() - start_time,
                context={"error": str(e)}
            )
    
    async def _detect_language_advanced(self, text: str) -> str:
        """Advanced language detection with context awareness"""
        
        try:
            # Use intelligence bridge for language detection
            if hasattr(self.intelligence_bridge, 'detect_language_advanced'):
                detected = await self.intelligence_bridge.detect_language_advanced(text)
                if detected:
                    return detected
            
            # Fallback to basic detection
            if hasattr(self.intelligence_bridge, 'nlp_engine'):
                detected = self.intelligence_bridge.nlp_engine.detect_language(text)
                if detected:
                    return detected
            
            # Simple heuristic detection as last resort
            return self._simple_language_detection(text)
            
        except Exception as e:
            log_error(f"Language detection failed: {e}")
            return "en"  # Default to English
    
    def _simple_language_detection(self, text: str) -> str:
        """Simple heuristic language detection"""
        
        # Hindi detection
        hindi_chars = set("अआइईउऊएओअंअः")
        if any(char in text for char in hindi_chars):
            return "hi"
        
        # Arabic detection
        arabic_chars = set("أبتثجحخدذرزسشصضطظعغفقكلمنهوي")
        if any(char in text for char in arabic_chars):
            return "ar"
        
        # Chinese detection
        chinese_chars = set("的一是了我不人在他有这个上们来到时大地为子中你说生国年着就那和要她出也得里后自以会家可下而过天去能对小多然于心学么之都好看起发当没成只如事把还用第样道想作种开要")
        if any(char in text for char in chinese_chars):
            return "zh"
        
        # Spanish indicators
        spanish_words = ["hola", "gracias", "por", "favor", "como", "estas", "muy", "bien"]
        if any(word in text.lower() for word in spanish_words):
            return "es"
        
        # French indicators
        french_words = ["bonjour", "merci", "comment", "vous", "allez", "tres", "bien", "oui"]
        if any(word in text.lower() for word in french_words):
            return "fr"
        
        # German indicators
        german_words = ["hallo", "danke", "wie", "geht", "ihnen", "gut", "bitte", "gern"]
        if any(word in text.lower() for word in german_words):
            return "de"
        
        return "en"  # Default to English
    
    async def _get_intelligent_response(self, user_input: str, language: str, 
                                      user_context: Optional[Dict]) -> Dict[str, Any]:
        """Get intelligent response using the integration bridge"""
        
        try:
            # Process with intelligence bridge
            response = await self.intelligence_bridge.process_intelligent_query(
                user_input, user_context
            )
            
            # Add language-specific enhancements
            if language != "en":
                response = await self._enhance_response_for_language(response, language)
            
            return response
            
        except Exception as e:
            log_error(f"Intelligent response generation failed: {e}")
            
            # Fallback to basic response
            try:
                basic_response = self.adaptive_chatbot.generate_response(
                    user_input, user_context or {}
                )
                return {
                    "response": basic_response,
                    "sentiment": "neutral",
                    "confidence": 0.6,
                    "context": user_context or {},
                    "source": "fallback"
                }
            except Exception as fallback_error:
                log_error(f"Fallback response failed: {fallback_error}")
                return {
                    "response": "I'm having trouble understanding. Could you please rephrase?",
                    "sentiment": "apologetic",
                    "confidence": 0.3,
                    "context": {},
                    "source": "error_fallback"
                }
    
    async def _enhance_response_for_language(self, response: Dict[str, Any], language: str) -> Dict[str, Any]:
        """Enhance response with language-specific considerations"""
        
        try:
            # Language-specific response modifications
            if language == "hi":
                # Add Hindi politeness markers
                response_text = response.get("response", "")
                if not any(word in response_text.lower() for word in ["ji", "aap", "dhanyawad"]):
                    if response_text.endswith("."):
                        response_text = response_text[:-1] + " ji."
                    response["response"] = response_text
            
            elif language == "es":
                # Add Spanish courtesy
                response_text = response.get("response", "")
                if "gracias" not in response_text.lower() and "por favor" not in response_text.lower():
                    if response_text.endswith("."):
                        response_text += " ¡Gracias!"
                    response["response"] = response_text
            
            elif language == "fr":
                # Add French politeness
                response_text = response.get("response", "")
                if "merci" not in response_text.lower() and "s'il vous plaît" not in response_text.lower():
                    if response_text.endswith("."):
                        response_text += " Merci."
                    response["response"] = response_text
            
            # Add cultural context
            response["cultural_context"] = {
                "language": language,
                "politeness_level": "high",
                "formality": "moderate"
            }
            
            return response
            
        except Exception as e:
            log_error(f"Language enhancement failed: {e}")
            return response
    
    def _enhance_context_multilingual(self, context: Dict, language: str, 
                                    user_input: str, sentiment: str) -> Dict[str, Any]:
        """Enhance context with multilingual considerations"""
        
        enhanced_context = context.copy()
        
        # Add multilingual metadata
        enhanced_context.update({
            "detected_language": language,
            "original_input": user_input,
            "sentiment": sentiment,
            "multilingual_session": True,
            "language_confidence": self._calculate_language_confidence(user_input, language),
            "cultural_context": self._get_cultural_context(language),
            "voice_preferences": self._get_language_voice_preferences(language)
        })
        
        # Add conversation history context for this language
        if language in self.language_contexts:
            enhanced_context["language_history"] = self.language_contexts[language][-5:]  # Last 5 interactions
        
        return enhanced_context
    
    def _calculate_language_confidence(self, text: str, detected_language: str) -> float:
        """Calculate confidence score for language detection"""
        
        # Simple confidence based on text characteristics
        confidence = 0.5  # Base confidence
        
        if detected_language == "en":
            # English confidence based on common words
            english_words = ["the", "and", "is", "to", "of", "in", "it", "you", "that", "he"]
            word_matches = sum(1 for word in english_words if word in text.lower())
            confidence = min(0.9, 0.5 + (word_matches * 0.05))
        
        elif detected_language == "hi":
            # Hindi confidence based on Devanagari script
            devanagari_chars = sum(1 for char in text if '\u0900' <= char <= '\u097F')
            if devanagari_chars > 0:
                confidence = min(0.95, 0.7 + (devanagari_chars / len(text)))
        
        return confidence
    
    def _get_cultural_context(self, language: str) -> Dict[str, Any]:
        """Get cultural context for language"""
        
        cultural_contexts = {
            "en": {
                "formality_level": "moderate",
                "directness": "direct",
                "hierarchy_awareness": "low"
            },
            "hi": {
                "formality_level": "high",
                "directness": "indirect",
                "hierarchy_awareness": "high",
                "respectful_address": True
            },
            "es": {
                "formality_level": "moderate",
                "directness": "moderate",
                "hierarchy_awareness": "moderate",
                "warmth": "high"
            },
            "fr": {
                "formality_level": "high",
                "directness": "indirect",
                "hierarchy_awareness": "moderate",
                "elegance": "high"
            },
            "de": {
                "formality_level": "high",
                "directness": "direct",
                "hierarchy_awareness": "moderate",
                "precision": "high"
            }
        }
        
        return cultural_contexts.get(language, cultural_contexts["en"])
    
    def _get_language_voice_preferences(self, language: str) -> Dict[str, Any]:
        """Get voice preferences for language"""
        
        # Get available voices for the language
        available_voices = self.voice_system.get_available_voices(language)
        
        return {
            "available_voices": len(available_voices),
            "preferred_gender": "female" if language in ["hi", "fr"] else "neutral",
            "preferred_style": "friendly",
            "voice_switching": "enabled"
        }
    
    async def _generate_voice_response(self, text: str, language: str, 
                                     sentiment: str, context: Dict) -> bool:
        """Generate voice response with multilingual system"""
        
        try:
            # Limit text length for voice synthesis
            if len(text) > self.config["max_response_length"]:
                text = text[:self.config["max_response_length"]] + "..."
                log_warning(f"Response truncated for voice synthesis: {len(text)} chars")
            
            # Generate voice
            success = await self.voice_system.speak_with_auto_voice(
                text, language, sentiment, context
            )
            
            if success:
                log_info(f"🔊 Voice response generated successfully in {language}")
            else:
                log_warning(f"Voice response failed for {language}")
            
            return success
            
        except Exception as e:
            log_error(f"Voice generation failed: {e}")
            return False
    
    def _update_session_stats(self, language: str, response_time: float, 
                            voice_generated: bool, confidence: float):
        """Update session statistics"""
        
        self.session_stats["total_interactions"] += 1
        self.session_stats["languages_used"].add(language)
        
        # Update average response time
        total_time = (self.session_stats["average_response_time"] * 
                     (self.session_stats["total_interactions"] - 1) + response_time)
        self.session_stats["average_response_time"] = total_time / self.session_stats["total_interactions"]
        
        # Update voice success rate
        if voice_generated:
            current_successes = (self.session_stats["voice_success_rate"] * 
                               (self.session_stats["total_interactions"] - 1))
            self.session_stats["voice_success_rate"] = (current_successes + 1) / self.session_stats["total_interactions"]
        
        # Update multilingual accuracy (based on confidence)
        total_accuracy = (self.session_stats["multilingual_accuracy"] * 
                         (self.session_stats["total_interactions"] - 1) + confidence)
        self.session_stats["multilingual_accuracy"] = total_accuracy / self.session_stats["total_interactions"]
    
    def _store_conversation_memory(self, user_input: str, response: str, 
                                 language: str, context: Dict):
        """Store conversation in memory for context"""
        
        memory_entry = {
            "timestamp": time.time(),
            "user_input": user_input,
            "response": response,
            "language": language,
            "context": context
        }
        
        # Store in general memory
        self.conversation_memory.append(memory_entry)
        if len(self.conversation_memory) > 100:  # Limit memory size
            self.conversation_memory = self.conversation_memory[-100:]
        
        # Store in language-specific memory
        if language not in self.language_contexts:
            self.language_contexts[language] = []
        
        self.language_contexts[language].append(memory_entry)
        if len(self.language_contexts[language]) > 20:  # Limit per language
            self.language_contexts[language] = self.language_contexts[language][-20:]
    
    def get_multilingual_statistics(self) -> Dict[str, Any]:
        """Get comprehensive multilingual statistics"""
        
        # Get voice system stats
        voice_stats = self.voice_system.get_voice_statistics()
        
        # Get intelligence bridge stats if available
        intelligence_stats = {}
        if hasattr(self.intelligence_bridge, 'get_session_statistics'):
            intelligence_stats = self.intelligence_bridge.get_session_statistics()
        
        return {
            "session_stats": {
                **self.session_stats,
                "languages_used": list(self.session_stats["languages_used"])
            },
            "voice_system": voice_stats,
            "intelligence_bridge": intelligence_stats,
            "memory": {
                "total_conversations": len(self.conversation_memory),
                "languages_in_memory": list(self.language_contexts.keys()),
                "memory_per_language": {
                    lang: len(memories) for lang, memories in self.language_contexts.items()
                }
            },
            "configuration": self.config
        }
    
    def configure_multilingual_settings(self, **settings):
        """Configure multilingual bridge settings"""
        
        for key, value in settings.items():
            if key in self.config:
                self.config[key] = value
                log_info(f"🔧 Updated {key} to {value}")
            else:
                log_warning(f"Unknown configuration key: {key}")
        
        # Update voice system preferences if needed
        voice_settings = {}
        if "voice_consistency_mode" in settings:
            voice_settings["consistency_mode"] = settings["voice_consistency_mode"]
        if "auto_voice_enabled" in settings:
            voice_settings["auto_switch"] = settings["auto_voice_enabled"]
        
        if voice_settings:
            self.voice_system.set_voice_preferences(**voice_settings)
    
    async def batch_process_multilingual(self, queries: List[Tuple[str, Optional[str]]]) -> List[MultilingualResponse]:
        """Process multiple multilingual queries efficiently"""
        
        log_info(f"🚀 Processing {len(queries)} multilingual queries")
        
        tasks = []
        for query, language in queries:
            task = self.process_multilingual_query(query, language)
            tasks.append(task)
        
        # Process all queries concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                log_error(f"Query {i} failed: {result}")
                # Create error response
                error_response = MultilingualResponse(
                    text="Processing error occurred",
                    language=queries[i][1] or "en",
                    sentiment="apologetic",
                    confidence=0.0,
                    voice_generated=False,
                    response_time=0.0,
                    context={"error": str(result)}
                )
                successful_results.append(error_response)
            else:
                successful_results.append(result)
        
        log_info(f"✅ Completed batch processing: {len(successful_results)} responses")
        return successful_results
    
    def cleanup(self):
        """Cleanup all systems"""
        try:
            if self.voice_system:
                self.voice_system.cleanup()
            if hasattr(self.intelligence_bridge, 'cleanup'):
                self.intelligence_bridge.cleanup()
            
            log_info("✅ Advanced Multilingual Bridge cleaned up")
        except Exception as e:
            log_error(f"Cleanup failed: {e}")

# Global instance
_multilingual_bridge = None

def get_multilingual_bridge() -> AdvancedMultilingualBridge:
    """Get global multilingual bridge instance"""
    global _multilingual_bridge
    if _multilingual_bridge is None:
        _multilingual_bridge = AdvancedMultilingualBridge()
    return _multilingual_bridge

async def process_multilingual_conversation(text: str, language: Optional[str] = None, 
                                          context: Optional[Dict] = None) -> MultilingualResponse:
    """Convenience function for multilingual conversation processing"""
    bridge = get_multilingual_bridge()
    return await bridge.process_multilingual_query(text, language, context)

if __name__ == "__main__":
    # Test the multilingual bridge
    import asyncio
    
    async def test_multilingual_bridge():
        print("🌍 Testing Advanced Multilingual Bridge")
        print("=" * 60)
        
        bridge = get_multilingual_bridge()
        
        # Test queries in different languages
        test_queries = [
            ("Hello! What electrical products do you have?", "en"),
            ("नमस्ते! मुझे LED bulbs की जानकारी चाहिए।", "hi"),
            ("¿Cuánto cuesta un ventilador de techo?", "es"),
            ("I need help with a wire installation.", "en"),
            ("धन्यवाद! आपकी service बहुत अच्छी है।", "hi"),
            ("Can you recommend a good electrician?", None),  # Auto-detect
        ]
        
        for i, (query, lang) in enumerate(test_queries, 1):
            print(f"\n🔄 Test {i}: {lang or 'auto-detect'}")
            print(f"Query: {query}")
            
            try:
                response = await bridge.process_multilingual_query(query, lang)
                
                print(f"✅ Response ({response.language}): {response.text[:100]}...")
                print(f"   Sentiment: {response.sentiment}")
                print(f"   Confidence: {response.confidence:.2f}")
                print(f"   Voice Generated: {response.voice_generated}")
                print(f"   Response Time: {response.response_time:.2f}s")
                
            except Exception as e:
                print(f"❌ Test failed: {e}")
            
            await asyncio.sleep(1)  # Brief pause
        
        # Show statistics
        print(f"\n📊 Multilingual Bridge Statistics:")
        stats = bridge.get_multilingual_statistics()
        
        session_stats = stats["session_stats"]
        print(f"• Total Interactions: {session_stats['total_interactions']}")
        print(f"• Languages Used: {', '.join(session_stats['languages_used'])}")
        print(f"• Avg Response Time: {session_stats['average_response_time']:.2f}s")
        print(f"• Voice Success Rate: {session_stats['voice_success_rate']:.1%}")
        print(f"• Multilingual Accuracy: {session_stats['multilingual_accuracy']:.1%}")
        
        # Cleanup
        bridge.cleanup()
    
    # Run the test
    try:
        asyncio.run(test_multilingual_bridge())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed: {e}")