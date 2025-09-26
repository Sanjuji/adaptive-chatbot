#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced NLU/NLP System with Multilingual Support
ChatGPT-like conversation capabilities with free transformer models
"""

import re
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    from sentence_transformers import SentenceTransformer
    from langdetect import detect, DetectorFactory
    from textblob import TextBlob
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Advanced NLP packages not available: {e}")
    TRANSFORMERS_AVAILABLE = False

from utils.logger import log_info, log_error, log_warning

# Set deterministic language detection
DetectorFactory.seed = 0

@dataclass
class ConversationContext:
    """Store conversation context and memory"""
    user_name: str = "User"
    bot_personality: str = "friendly"
    conversation_history: List[Dict] = None
    current_topic: str = ""
    user_preferences: Dict = None
    emotional_state: str = "neutral"
    language: str = "en"
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.user_preferences is None:
            self.user_preferences = {}

@dataclass
class LanguageInfo:
    """Language detection and processing info"""
    detected_language: str
    confidence: float
    language_name: str
    is_mixed_language: bool = False
    dominant_languages: List[str] = None

class AdvancedNLPEngine:
    """Advanced NLP engine with multilingual conversation capabilities"""
    
    def __init__(self):
        self.context = ConversationContext()
        self.models_loaded = False
        self.sentiment_analyzer = None
        self.embedding_model = None
        self.qa_model = None
        self.conversation_model = None
        
        # Language mappings
        self.language_names = {
            'hi': 'Hindi', 'en': 'English', 'es': 'Spanish', 'fr': 'French', 
            'de': 'German', 'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian',
            'ja': 'Japanese', 'ko': 'Korean', 'zh': 'Chinese', 'ar': 'Arabic',
            'tr': 'Turkish', 'pl': 'Polish', 'nl': 'Dutch', 'sv': 'Swedish',
            'da': 'Danish', 'no': 'Norwegian', 'fi': 'Finnish', 'cs': 'Czech',
            'sk': 'Slovak', 'hu': 'Hungarian', 'ro': 'Romanian', 'bg': 'Bulgarian',
            'hr': 'Croatian', 'sr': 'Serbian', 'sl': 'Slovenian', 'et': 'Estonian',
            'lv': 'Latvian', 'lt': 'Lithuanian', 'mt': 'Maltese', 'ga': 'Irish',
            'cy': 'Welsh', 'eu': 'Basque', 'ca': 'Catalan', 'gl': 'Galician',
            'ta': 'Tamil', 'te': 'Telugu', 'kn': 'Kannada', 'ml': 'Malayalam',
            'gu': 'Gujarati', 'pa': 'Punjabi', 'bn': 'Bengali', 'ur': 'Urdu',
            'ne': 'Nepali', 'si': 'Sinhala', 'my': 'Burmese', 'th': 'Thai',
            'vi': 'Vietnamese', 'id': 'Indonesian', 'ms': 'Malay', 'tl': 'Filipino'
        }
        
        # Initialize models in background
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize AI models for advanced conversation"""
        if not TRANSFORMERS_AVAILABLE:
            log_warning("Transformers not available, using basic NLP")
            return
            
        try:
            log_info("🤖 Loading advanced NLP models...")
            
            # Lightweight sentiment analysis
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            
            # Lightweight sentence embeddings for semantic similarity
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Conversational AI model (lightweight)
            self.conversation_model = pipeline(
                "text-generation",
                model="microsoft/DialoGPT-small",
                tokenizer="microsoft/DialoGPT-small"
            )
            
            self.models_loaded = True
            log_info("✅ Advanced NLP models loaded successfully")
            
        except Exception as e:
            log_error(f"Model loading failed: {e}")
            self.models_loaded = False
    
    def detect_language(self, text: str) -> LanguageInfo:
        """Advanced language detection with confidence scoring"""
        try:
            if not text or len(text.strip()) < 3:
                return LanguageInfo("en", 0.5, "English")
            
            # Primary detection
            detected = detect(text)
            confidence = 0.8  # langdetect doesn't provide confidence
            
            # Check for mixed languages (common in Indian context)
            is_mixed = self._is_mixed_language(text)
            dominant_langs = self._get_dominant_languages(text) if is_mixed else [detected]
            
            language_name = self.language_names.get(detected, detected.upper())
            
            return LanguageInfo(
                detected_language=detected,
                confidence=confidence,
                language_name=language_name,
                is_mixed_language=is_mixed,
                dominant_languages=dominant_langs
            )
            
        except Exception as e:
            log_warning(f"Language detection failed: {e}")
            return LanguageInfo("en", 0.5, "English")
    
    def _is_mixed_language(self, text: str) -> bool:
        """Detect if text contains multiple languages (like Hinglish)"""
        try:
            # Check for mixed scripts
            has_latin = bool(re.search(r'[a-zA-Z]', text))
            has_devanagari = bool(re.search(r'[\u0900-\u097F]', text))
            has_arabic = bool(re.search(r'[\u0600-\u06FF]', text))
            has_chinese = bool(re.search(r'[\u4e00-\u9fff]', text))
            
            script_count = sum([has_latin, has_devanagari, has_arabic, has_chinese])
            return script_count > 1
            
        except (UnicodeDecodeError, AttributeError):
            return False
    
    def _get_dominant_languages(self, text: str) -> List[str]:
        """Get dominant languages in mixed-language text"""
        try:
            # Split text and detect language for each part
            words = text.split()
            lang_counts = {}
            
            for word in words:
                if len(word) > 2:
                    try:
                        lang = detect(word)
                        lang_counts[lang] = lang_counts.get(lang, 0) + 1
                    except (AttributeError, ValueError):
                        continue
            
            # Return top 2 languages
            sorted_langs = sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)
            return [lang for lang, count in sorted_langs[:2]]
            
        except (AttributeError, ValueError):
            return ["en", "hi"]  # Default for Hinglish
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Advanced sentiment analysis with emotion detection"""
        try:
            if not self.models_loaded or not self.sentiment_analyzer:
                # Fallback to TextBlob
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                
                if polarity > 0.3:
                    return {"sentiment": "positive", "confidence": 0.7, "emotion": "happy"}
                elif polarity < -0.3:
                    return {"sentiment": "negative", "confidence": 0.7, "emotion": "sad"}
                else:
                    return {"sentiment": "neutral", "confidence": 0.6, "emotion": "neutral"}
            
            # Advanced sentiment analysis
            results = self.sentiment_analyzer(text)
            
            # Handle the results format (it's a list of lists)
            if isinstance(results, list) and len(results) > 0:
                if isinstance(results[0], list):
                    results = results[0]  # Extract the first (and only) result
            
            # Find highest confidence sentiment
            best_result = max(results, key=lambda x: x['score'])
            sentiment = best_result['label'].lower()
            confidence = best_result['score']
            
            # Map to emotions
            emotion_map = {
                'positive': 'happy',
                'negative': 'sad',
                'neutral': 'calm'
            }
            
            return {
                "sentiment": sentiment,
                "confidence": confidence,
                "emotion": emotion_map.get(sentiment, 'neutral'),
                "all_scores": results
            }
            
        except Exception as e:
            log_warning(f"Sentiment analysis failed: {e}")
            return {"sentiment": "neutral", "confidence": 0.5, "emotion": "neutral"}
    
    def extract_intent(self, text: str) -> Dict[str, Any]:
        """Extract user intent from text"""
        text_lower = text.lower().strip()
        
        # Intent patterns (can be expanded)
        intent_patterns = {
            'greeting': [
                r'\b(hi|hello|hey|namaste|namaskar|adab|sat sri akal|vanakkam)\b',
                r'\b(good morning|good afternoon|good evening)\b',
                r'\b(kaise ho|kaisi ho|how are you|kya haal hai)\b',
                r'(नमस्ते|नमस्कार|आदाब|हैलो|हाय)',
                r'(गुड मॉर्निंग|शुभ प्रभात|शुभ संध्या)'
            ],
            'farewell': [
                r'\b(bye|goodbye|alvida|ta ta|see you|khuda hafiz)\b',
                r'\b(good night|subh ratri|shubh ratri)\b',
                r'(अलविदा|टा टा|खुदा हाफिज|शुभ रात्रि|अच्छी रात)'
            ],
            'question': [
                r'^(what|kya|kya hai|kaise|how|why|kyu|kyon|where|kaha|when|kab)',
                r'\?$',  # Ends with question mark
                r'\b(price|rate|cost|kitna|kitne|kaun|which)\b'
            ],
            'request': [
                r'\b(please|kripaya|meherbani|help|madad|assist)\b',
                r'\b(can you|could you|would you|kya aap)\b',
                r'\b(tell me|batao|bataiye|explain|samjhao)\b'
            ],
            'appreciation': [
                r'\b(thanks|thank you|dhanyawad|shukriya|bahut accha)\b',
                r'\b(good|great|excellent|bahut badhiya|zabardast)\b',
                r'(धन्यवाद|शुक्रिया|बहुत अच्छा|बहुत बढ़िया|ज़बरदस्त|वाह)',
                r'(थैंक यू|थैंक्स|महान|शानदार|वंडरफुल)'
            ],
            'learning': [
                r'\b(teach|sikha|sikhao|learn|seekh|batao)\b',
                r'\b(how to|kaise karte|kya tarika)\b',
                r'(सिखा|सिखाओ|सीख|बताओ|समझाओ|सीखना)',
                r'(कैसे करते|क्या तरीका|मुझे सिखाओ|टीच मी)'
            ],
            'complaint': [
                r'\b(problem|samasya|issue|dikkat|complaint|shikayat)\b',
                r'\b(not working|kaam nahi kar|broken|kharab)\b',
                r'(समस्या|दिक्कत|शिकायत|परेशानी|टेंशन|गड़बड़)',
                r'(काम नहीं कर|खराब|टूट|बिगड़|गलत|बेकार)'
            ]
        }
        
        detected_intents = []
        confidence_scores = {}
        
        for intent, patterns in intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    detected_intents.append(intent)
                    confidence_scores[intent] = confidence_scores.get(intent, 0) + 0.3
        
        if not detected_intents:
            return {"intent": "general", "confidence": 0.5, "entities": []}
        
        # Return highest confidence intent
        primary_intent = max(detected_intents, key=lambda x: confidence_scores.get(x, 0))
        
        return {
            "intent": primary_intent,
            "confidence": min(confidence_scores.get(primary_intent, 0.5), 1.0),
            "all_intents": detected_intents,
            "entities": self.extract_entities(text)
        }
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text"""
        entities = []
        
        # Simple entity patterns
        entity_patterns = {
            'money': r'(\d+)\s*(rupees?|rs\.?|dollars?|\$|euros?|€)',
            'number': r'\b(\d+)\b',
            'time': r'\b(\d{1,2}:\d{2}|\d{1,2}\s*(am|pm|baje))\b',
            'product': r'\b(switch|wire|socket|mcb|cable|fan|bulb|inverter)\b'
        }
        
        for entity_type, pattern in entity_patterns.items():
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                entities.append({
                    "type": entity_type,
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end()
                })
        
        return entities
    
    def generate_response(self, user_input: str, context: Dict = None) -> Dict[str, Any]:
        """Generate ChatGPT-like conversational response"""
        try:
            # Analyze input
            language_info = self.detect_language(user_input)
            sentiment_info = self.analyze_sentiment(user_input)
            intent_info = self.extract_intent(user_input)
            
            # Update context
            self.context.language = language_info.detected_language
            self.context.emotional_state = sentiment_info['emotion']
            
            # Add to conversation history
            self.context.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "language": language_info.detected_language,
                "intent": intent_info['intent'],
                "sentiment": sentiment_info['sentiment']
            })
            
            # Generate contextual response
            response_text = self._generate_contextual_response(
                user_input, language_info, sentiment_info, intent_info, context
            )
            
            return {
                "response_text": response_text,
                "language_info": language_info,
                "sentiment_info": sentiment_info,
                "intent_info": intent_info,
                "suggested_voice": self._suggest_voice(language_info),
                "conversation_context": self.context
            }
            
        except Exception as e:
            log_error(f"Response generation failed: {e}")
            return {
                "response_text": "I understand you, but I'm having some technical difficulties. Can you please try again?",
                "language_info": LanguageInfo("en", 0.5, "English"),
                "sentiment_info": {"sentiment": "neutral", "confidence": 0.5},
                "intent_info": {"intent": "general", "confidence": 0.5},
                "suggested_voice": "en-US-JennyNeural"
            }
    
    def _generate_contextual_response(self, user_input: str, lang_info: LanguageInfo, 
                                    sentiment_info: Dict, intent_info: Dict, context: Dict = None) -> str:
        """Generate contextually appropriate response"""
        
        intent = intent_info['intent']
        language = lang_info.detected_language
        sentiment = sentiment_info['sentiment']
        
        # Intent-based responses with multilingual support
        if intent == 'greeting':
            return self._generate_greeting_response(language, sentiment)
        elif intent == 'farewell':
            return self._generate_farewell_response(language, sentiment)
        elif intent == 'question':
            return self._generate_question_response(user_input, language, context)
        elif intent == 'appreciation':
            return self._generate_appreciation_response(language)
        elif intent == 'complaint':
            return self._generate_complaint_response(language, sentiment)
        elif intent == 'request':
            return self._generate_request_response(user_input, language)
        else:
            return self._generate_general_response(user_input, language, sentiment, context)
    
    def _generate_greeting_response(self, language: str, sentiment: str) -> str:
        """Generate greeting response in appropriate language"""
        greetings = {
            'hi': [
                "नमस्ते! मैं आपकी कैसे सहायता कर सकता हूँ?",
                "आदाब! बताइए क्या चाहिए?",
                "हैलो! क्या हाल है? मैं यहाँ आपकी मदद के लिए हूँ।"
            ],
            'en': [
                "Hello! How can I help you today?",
                "Hi there! What can I do for you?",
                "Greetings! I'm here to assist you."
            ],
            'es': [
                "¡Hola! ¿Cómo puedo ayudarte hoy?",
                "¡Saludos! ¿En qué puedo asistirte?"
            ],
            'fr': [
                "Bonjour! Comment puis-je vous aider?",
                "Salut! Que puis-je faire pour vous?"
            ],
            'de': [
                "Hallo! Wie kann ich Ihnen helfen?",
                "Guten Tag! Womit kann ich behilflich sein?"
            ]
        }
        
        responses = greetings.get(language, greetings['en'])
        return responses[0]  # Can randomize later
    
    def _generate_farewell_response(self, language: str, sentiment: str) -> str:
        """Generate farewell response"""
        farewells = {
            'hi': [
                "अलविदा! बात करके अच्छा लगा। फिर मिलते हैं!",
                "खुदा हाफिज! कभी भी वापस आइएगा।",
                "नमस्कार! आपका दिन शुभ हो।"
            ],
            'en': [
                "Goodbye! It was great talking with you. Come back anytime!",
                "See you later! Have a wonderful day!",
                "Take care! Feel free to return whenever you need help."
            ],
            'es': [
                "¡Adiós! Fue genial hablar contigo.",
                "¡Hasta luego! Que tengas un buen día."
            ],
            'fr': [
                "Au revoir! C'était un plaisir de parler avec vous.",
                "À bientôt! Passez une excellente journée."
            ]
        }
        
        responses = farewells.get(language, farewells['en'])
        return responses[0]
    
    def _generate_question_response(self, user_input: str, language: str, context: Dict = None) -> str:
        """Generate response to questions using knowledge base or general knowledge"""
        # This would integrate with existing knowledge base
        if context and 'knowledge_answer' in context:
            return context['knowledge_answer']
        
        # Default responses for different languages
        responses = {
            'hi': "यह एक दिलचस्प सवाल है। मुझे इसके बारे में और जानकारी चाहिए। आप मुझे इसके बारे में सिखा सकते हैं?",
            'en': "That's an interesting question. I'd need more information about this. Would you like to teach me about it?",
            'es': "Esa es una pregunta interesante. Necesitaría más información al respecto.",
            'fr': "C'est une question intéressante. J'aurais besoin de plus d'informations à ce sujet."
        }
        
        return responses.get(language, responses['en'])
    
    def _generate_general_response(self, user_input: str, language: str, sentiment: str, context: Dict = None) -> str:
        """Generate general conversational response"""
        if sentiment == 'positive':
            responses = {
                'hi': "बहुत अच्छा! मैं खुश हूँ कि आप positive mood में हैं। और कुछ बताइए।",
                'en': "That's wonderful! I'm glad you're in a positive mood. Tell me more!"
            }
        elif sentiment == 'negative':
            responses = {
                'hi': "लगता है कि आप परेशान हैं। मैं आपकी मदद करना चाहता हूँ। क्या समस्या है?",
                'en': "It seems like you're upset. I'd like to help you. What's troubling you?"
            }
        else:
            responses = {
                'hi': "समझ गया। और कुछ बताइए या पूछिए जो आपको चाहिए।",
                'en': "I understand. Please tell me more or ask me anything you need."
            }
        
        return responses.get(language, responses['en'])
    
    def _generate_appreciation_response(self, language: str) -> str:
        """Generate response to appreciation"""
        responses = {
            'hi': "धन्यवाद! आपकी तारीफ से बहुत खुशी हुई। कुछ और काम आए तो बताइएगा।",
            'en': "Thank you so much! I'm delighted to help. Let me know if you need anything else!",
            'es': "¡Muchas gracias! Me complace mucho ayudar.",
            'fr': "Merci beaucoup! Je suis ravi de pouvoir vous aider."
        }
        
        return responses.get(language, responses['en'])
    
    def _generate_complaint_response(self, language: str, sentiment: str) -> str:
        """Generate response to complaints"""
        responses = {
            'hi': "मुझे खुशी है कि आपने मुझसे समस्या के बारे में बताया। मैं इसे हल करने की कोशिश करता हूँ।",
            'en': "I'm sorry to hear about the problem. Let me try to help you resolve this issue.",
            'es': "Lamento escuchar sobre el problema. Permíteme ayudarte a resolverlo.",
            'fr': "Je suis désolé d'apprendre ce problème. Laissez-moi vous aider à le résoudre."
        }
        
        return responses.get(language, responses['en'])
    
    def _generate_request_response(self, user_input: str, language: str) -> str:
        """Generate response to requests"""
        responses = {
            'hi': "ज़रूर! मैं आपकी मदद करने की पूरी कोशिश करूँगा। बताइए क्या चाहिए?",
            'en': "Of course! I'll do my best to help you. What exactly do you need?",
            'es': "¡Por supuesto! Haré mi mejor esfuerzo para ayudarte.",
            'fr': "Bien sûr! Je ferai de mon mieux pour vous aider."
        }
        
        return responses.get(language, responses['en'])
    
    def _suggest_voice(self, language_info: LanguageInfo) -> str:
        """Suggest appropriate EdgeTTS voice based on detected language"""
        # This will be expanded with full EdgeTTS voice mapping
        voice_mapping = {
            'hi': 'hi-IN-MadhurNeural',
            'en': 'en-US-JennyNeural',
            'es': 'es-ES-ElviraNeural',
            'fr': 'fr-FR-DeniseNeural',
            'de': 'de-DE-KatjaNeural',
            'it': 'it-IT-ElsaNeural',
            'pt': 'pt-BR-FranciscaNeural',
            'ru': 'ru-RU-SvetlanaNeural',
            'ja': 'ja-JP-NanamiNeural',
            'ko': 'ko-KR-SunHiNeural',
            'zh': 'zh-CN-XiaoxiaoNeural',
            'ar': 'ar-SA-ZariyahNeural',
            'tr': 'tr-TR-EmelNeural'
        }
        
        return voice_mapping.get(language_info.detected_language, 'en-US-JennyNeural')
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation"""
        history = self.context.conversation_history
        if not history:
            return {"summary": "No conversation yet", "stats": {}}
        
        # Calculate stats
        languages_used = list(set([entry.get('language', 'en') for entry in history]))
        intents_used = list(set([entry.get('intent', 'general') for entry in history]))
        total_exchanges = len(history)
        
        return {
            "summary": f"Conversation with {total_exchanges} exchanges",
            "stats": {
                "total_exchanges": total_exchanges,
                "languages_used": languages_used,
                "intents_used": intents_used,
                "current_language": self.context.language,
                "emotional_state": self.context.emotional_state
            },
            "context": self.context
        }

# Global instance
_nlp_engine = None

def get_nlp_engine() -> AdvancedNLPEngine:
    """Get global NLP engine instance"""
    global _nlp_engine
    if _nlp_engine is None:
        _nlp_engine = AdvancedNLPEngine()
    return _nlp_engine

def analyze_and_respond(user_input: str, context: Dict = None) -> Dict[str, Any]:
    """Convenience function for analysis and response generation"""
    return get_nlp_engine().generate_response(user_input, context)

def detect_language(text: str) -> LanguageInfo:
    """Convenience function for language detection"""
    return get_nlp_engine().detect_language(text)

if __name__ == "__main__":
    # Test the system
    nlp = AdvancedNLPEngine()
    
    test_inputs = [
        "Hello, how are you?",
        "नमस्ते, आप कैसे हैं?",
        "Hola, ¿cómo estás?",
        "Switch ka price kya hai?",
        "I'm having problems with my device",
        "Thank you so much for your help!"
    ]
    
    for text in test_inputs:
        print(f"\nInput: {text}")
        result = nlp.generate_response(text)
        print(f"Language: {result['language_info'].language_name}")
        print(f"Intent: {result['intent_info']['intent']}")
        print(f"Response: {result['response_text']}")
        print(f"Suggested Voice: {result['suggested_voice']}")