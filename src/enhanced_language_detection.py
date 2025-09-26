#!/usr/bin/env python3
"""
Enhanced Language Detection & Auto-Switch System
Real-time language detection with confidence scoring and seamless transitions
"""

import re
import time
import threading
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum
import unicodedata
from collections import defaultdict, Counter
import asyncio

try:
    import langdetect
    from langdetect import detect, detect_langs, DetectorFactory
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

try:
    from textblob import TextBlob
    # Check if TextBlob has language detection capability
    test_blob = TextBlob("test")
    if hasattr(test_blob, 'detect_language'):
        TEXTBLOB_AVAILABLE = True
    else:
        TEXTBLOB_AVAILABLE = False
except ImportError:
    TEXTBLOB_AVAILABLE = False

try:
    from polyglot.detect import Detector
    POLYGLOT_AVAILABLE = True
except ImportError:
    POLYGLOT_AVAILABLE = False

try:
    from logger import log_info, log_error, log_warning
except ImportError:
    def log_info(msg): print(f"INFO - {msg}")
    def log_error(msg): print(f"ERROR - {msg}")
    def log_warning(msg): print(f"WARNING - {msg}")

class DetectionMethod(Enum):
    """Language detection methods"""
    HEURISTIC = "heuristic"
    LANGDETECT = "langdetect" 
    TEXTBLOB = "textblob"
    POLYGLOT = "polyglot"
    ENSEMBLE = "ensemble"
    CONTEXT = "context"

class LanguageConfidence(Enum):
    """Confidence levels for language detection"""
    VERY_HIGH = "very_high"  # 0.9+
    HIGH = "high"           # 0.8+
    MEDIUM = "medium"       # 0.6+
    LOW = "low"            # 0.4+
    VERY_LOW = "very_low"  # <0.4

@dataclass
class LanguageDetectionResult:
    """Result of language detection"""
    detected_language: str
    confidence: float
    confidence_level: LanguageConfidence
    method_used: DetectionMethod
    alternative_languages: List[Tuple[str, float]]
    is_mixed_language: bool
    detected_segments: List[Tuple[str, str, float]]  # text, lang, confidence
    script_info: Dict[str, Any]
    processing_time: float

@dataclass
class LanguageContext:
    """Context for language detection"""
    conversation_history: List[str]
    user_preferred_languages: List[str]
    detected_language_sequence: List[str]
    topic_context: Optional[str]
    location_context: Optional[str]
    time_context: Optional[str]

class ScriptDetector:
    """Advanced script detection for better language identification"""
    
    def __init__(self):
        # Unicode script mappings
        self.script_language_mappings = {
            'Devanagari': ['hi', 'mr', 'ne', 'sa'],
            'Arabic': ['ar', 'fa', 'ur'],
            'Latin': ['en', 'es', 'fr', 'de', 'it', 'pt', 'ro', 'pl'],
            'Cyrillic': ['ru', 'bg', 'sr', 'uk', 'mk'],
            'Han': ['zh', 'ja'],
            'Hiragana': ['ja'],
            'Katakana': ['ja'],
            'Hangul': ['ko'],
            'Thai': ['th'],
            'Bengali': ['bn'],
            'Gujarati': ['gu'],
            'Telugu': ['te'],
            'Tamil': ['ta'],
            'Kannada': ['kn'],
            'Malayalam': ['ml'],
            'Oriya': ['or'],
            'Punjabi': ['pa'],
        }
        
        # Language-specific character patterns
        self.language_patterns = {
            'hi': re.compile(r'[\u0900-\u097F]+'),  # Devanagari
            'ar': re.compile(r'[\u0600-\u06FF\u0750-\u077F]+'),  # Arabic
            'zh': re.compile(r'[\u4e00-\u9fff]+'),  # CJK Unified Ideographs
            'ja': re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4e00-\u9fff]+'),  # Hiragana + Katakana + Kanji
            'ko': re.compile(r'[\uAC00-\uD7AF]+'),  # Hangul
            'ru': re.compile(r'[\u0400-\u04FF]+'),  # Cyrillic
            'th': re.compile(r'[\u0E00-\u0E7F]+'),  # Thai
            'bn': re.compile(r'[\u0980-\u09FF]+'),  # Bengali
            'gu': re.compile(r'[\u0A80-\u0AFF]+'),  # Gujarati
            'te': re.compile(r'[\u0C00-\u0C7F]+'),  # Telugu
            'ta': re.compile(r'[\u0B80-\u0BFF]+'),  # Tamil
            'kn': re.compile(r'[\u0C80-\u0CFF]+'),  # Kannada
            'ml': re.compile(r'[\u0D00-\u0D7F]+'),  # Malayalam
        }
    
    def detect_scripts(self, text: str) -> Dict[str, float]:
        """Detect writing scripts in text with confidence scores"""
        if not text:
            return {}
        
        script_counts = defaultdict(int)
        total_chars = 0
        
        for char in text:
            if char.isalpha():
                script_name = unicodedata.name(char, '').split()[0] if unicodedata.name(char, '') else 'Unknown'
                # Simplify script names
                if 'DEVANAGARI' in unicodedata.name(char, ''):
                    script_name = 'Devanagari'
                elif 'ARABIC' in unicodedata.name(char, ''):
                    script_name = 'Arabic'
                elif 'LATIN' in unicodedata.name(char, ''):
                    script_name = 'Latin'
                elif 'CYRILLIC' in unicodedata.name(char, ''):
                    script_name = 'Cyrillic'
                elif 'CJK' in unicodedata.name(char, '') or 'IDEOGRAPH' in unicodedata.name(char, ''):
                    script_name = 'Han'
                elif 'HIRAGANA' in unicodedata.name(char, ''):
                    script_name = 'Hiragana'
                elif 'KATAKANA' in unicodedata.name(char, ''):
                    script_name = 'Katakana'
                elif 'HANGUL' in unicodedata.name(char, ''):
                    script_name = 'Hangul'
                
                script_counts[script_name] += 1
                total_chars += 1
        
        if total_chars == 0:
            return {}
        
        # Convert to percentages
        script_percentages = {
            script: count / total_chars 
            for script, count in script_counts.items()
        }
        
        return script_percentages
    
    def suggest_languages_from_scripts(self, script_info: Dict[str, float]) -> List[Tuple[str, float]]:
        """Suggest possible languages based on detected scripts"""
        language_scores = defaultdict(float)
        
        for script, percentage in script_info.items():
            if script in self.script_language_mappings:
                possible_langs = self.script_language_mappings[script]
                for lang in possible_langs:
                    language_scores[lang] += percentage
        
        # Sort by score and return top candidates
        return sorted(language_scores.items(), key=lambda x: x[1], reverse=True)

class HeuristicDetector:
    """Heuristic language detection based on patterns and keywords"""
    
    def __init__(self):
        self.language_keywords = {
            'en': ['the', 'and', 'is', 'to', 'of', 'in', 'it', 'you', 'that', 'he', 'was', 'for', 'on', 'are', 'as', 'with'],
            'hi': [
                # Devanagari Hindi words
                'है', 'का', 'की', 'के', 'में', 'को', 'से', 'और', 'यह', 'वह', 'पर', 'इस', 'उस', 'कि', 'जो', 'या',
                'नहीं', 'भी', 'हैं', 'था', 'थी', 'थे', 'होगा', 'होगी', 'होंगे', 'कर', 'करना', 'करने', 'किया', 'कुछ', 'सब',
                'बहुत', 'अच्छा', 'अच्छी', 'अच्छे', 'ठीक', 'खुश', 'दुखी', 'खराब', 'अब', 'फिर', 'वापस', 'जाना', 'आना',
                
                # Romanized Hindi (Hinglish) - CRITICAL FIX
                'hai', 'ka', 'ki', 'ke', 'mein', 'ko', 'se', 'aur', 'yah', 'yeh', 'vah', 'wo', 'par', 'is', 'us', 
                'nahi', 'nahin', 'bhi', 'hain', 'tha', 'thi', 'the', 'hoga', 'hogi', 'honge', 'kar', 'karna', 'karne', 'kiya',
                'kuch', 'kuchh', 'sab', 'sabko', 'sabse', 'sabka', 'sabki', 'sabke',
                
                # Common Hinglish words that cause misdetection
                'kitna', 'kitne', 'kitni', 'kaise', 'kaisa', 'kaisi', 'kya', 'kyu', 'kyon', 'kaha', 'kahan', 'kab', 'kyun',
                'aap', 'aapka', 'aapki', 'aapke', 'tumhara', 'tumhari', 'tumhare', 'mera', 'meri', 'mere',
                'bahut', 'accha', 'acchi', 'acche', 'theek', 'thik', 'khushi', 'khush', 'dukhi', 'kharab', 'bura', 'buri', 'bure',
                'ab', 'abhi', 'phir', 'vapas', 'wapas', 'jana', 'jaana', 'aana', 'ana', 'ghar', 'paisa', 'paise', 'price', 'khareed',
                'main', 'mai', 'hum', 'humko', 'humse', 'humara', 'humari', 'humare', 'tum', 'tumko', 'tumse',
                'haal', 'hal', 'lagega', 'lagegi', 'lagenge', 'chahiye', 'chaahiye', 'milega', 'milegi', 'milenge',
                'switch', 'phone', 'mobile', 'laptop', 'computer', 'internet', 'wifi', 'network', 'connection',
                'problem', 'issue', 'trouble', 'help', 'madad', 'sahayata', 'solution', 'hal', 'upay',
                'business', 'kaam', 'vyavasaya', 'naukri', 'job', 'office', 'ghar', 'family', 'parivar',
                'time', 'samay', 'din', 'raat', 'subah', 'shaam', 'dopahar', 'morning', 'evening', 'night',
                'paani', 'khana', 'khaana', 'food', 'water', 'milk', 'dudh', 'chai', 'coffee', 'nashta', 'lunch', 'dinner'
            ],
            'es': ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se', 'no', 'te', 'lo', 'le', 'da', 'su'],
            'fr': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir', 'que', 'pour', 'dans', 'ce', 'son', 'une'],
            'de': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich', 'des', 'auf', 'für', 'ist', 'im', 'dem'],
            'it': ['il', 'di', 'che', 'e', 'la', 'per', 'un', 'in', 'con', 'del', 'da', 'a', 'al', 'le', 'si', 'dei'],
            'pt': ['o', 'de', 'a', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com', 'não', 'uma', 'os', 'no', 'se'],
            'ru': ['в', 'и', 'не', 'на', 'я', 'быть', 'с', 'а', 'как', 'по', 'но', 'они', 'к', 'у', 'его', 'за'],
            'ar': ['في', 'من', 'إلى', 'على', 'عن', 'مع', 'بين', 'تحت', 'فوق', 'أمام', 'خلف', 'يمين', 'يسار', 'داخل', 'خارج'],
            'zh': ['的', '一', '是', '了', '我', '不', '人', '在', '他', '有', '这', '个', '上', '们', '来', '到'],
            'ja': ['の', 'に', 'は', 'を', 'た', 'が', 'で', 'て', 'と', 'し', 'れ', 'さ', 'ある', 'いる', 'する', 'なる'],
            'ko': ['이', '그', '저', '것', '수', '있', '하', '되', '과', '같', '들', '만', '의', '를', '에', '도']
        }
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = {}
        for lang, keywords in self.language_keywords.items():
            pattern = r'\b(?:' + '|'.join(re.escape(kw) for kw in keywords) + r')\b'
            self.compiled_patterns[lang] = re.compile(pattern, re.IGNORECASE)
    
    def detect_language(self, text: str, top_n: int = 5) -> List[Tuple[str, float]]:
        """Detect language using heuristic keyword matching"""
        if not text:
            return []
        
        text_lower = text.lower()
        word_count = len(text_lower.split())
        
        if word_count == 0:
            return []
        
        language_scores = {}
        
        for lang, pattern in self.compiled_patterns.items():
            matches = pattern.findall(text_lower)
            score = len(matches) / word_count
            if score > 0:
                language_scores[lang] = score
        
        # Sort by score and return top N
        sorted_scores = sorted(language_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[:top_n]

class EnhancedLanguageDetector:
    """Advanced language detection with multiple methods and context awareness"""
    
    def __init__(self):
        self.script_detector = ScriptDetector()
        self.heuristic_detector = HeuristicDetector()
        
        # Detection settings
        self.settings = {
            'min_confidence_threshold': 0.3,
            'mixed_language_threshold': 0.4,
            'context_weight': 0.2,
            'ensemble_method': 'weighted_vote',
            'enable_context_learning': True,
            'segment_detection_enabled': True
        }
        
        # Context tracking
        self.language_contexts = {}  # user_id -> LanguageContext
        self.detection_history = []  # List of recent detections
        self.performance_metrics = {
            'total_detections': 0,
            'method_usage': defaultdict(int),
            'accuracy_by_method': defaultdict(list),
            'average_confidence': 0.0
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Initialize langdetect if available
        if LANGDETECT_AVAILABLE:
            DetectorFactory.seed = 0  # For consistent results
        
        log_info("🔍 Enhanced Language Detector initialized")
    
    async def detect_language_advanced(self, text: str, user_id: Optional[str] = None,
                                     context: Optional[LanguageContext] = None) -> LanguageDetectionResult:
        """Advanced language detection with multiple methods and context"""
        
        start_time = time.time()
        
        try:
            # Input validation
            if not text or not text.strip():
                return self._create_default_result(start_time)
            
            text = text.strip()
            
            # Get or create context
            if user_id and user_id in self.language_contexts:
                user_context = self.language_contexts[user_id]
            elif context:
                user_context = context
            else:
                user_context = LanguageContext([], [], [], None, None, None)
            
            # Step 1: Script-based detection
            script_info = self.script_detector.detect_scripts(text)
            script_suggestions = self.script_detector.suggest_languages_from_scripts(script_info)
            
            # Step 2: Multiple detection methods
            detection_results = {}
            
            # Heuristic detection
            heuristic_results = self.heuristic_detector.detect_language(text)
            detection_results[DetectionMethod.HEURISTIC] = heuristic_results
            
            # LangDetect library
            if LANGDETECT_AVAILABLE:
                langdetect_results = await self._detect_with_langdetect(text)
                detection_results[DetectionMethod.LANGDETECT] = langdetect_results
            
            # TextBlob detection
            if TEXTBLOB_AVAILABLE:
                textblob_results = await self._detect_with_textblob(text)
                detection_results[DetectionMethod.TEXTBLOB] = textblob_results
            
            # Polyglot detection
            if POLYGLOT_AVAILABLE:
                polyglot_results = await self._detect_with_polyglot(text)
                detection_results[DetectionMethod.POLYGLOT] = polyglot_results
            
            # Step 3: Context-aware adjustment
            if user_context and self.settings['enable_context_learning']:
                context_adjustments = self._apply_context_adjustments(detection_results, user_context)
                detection_results[DetectionMethod.CONTEXT] = context_adjustments
            
            # Step 4: Ensemble method to combine results
            final_result = await self._ensemble_detection(
                detection_results, script_suggestions, text, user_context
            )
            
            # Step 5: Mixed language detection
            if self.settings['segment_detection_enabled']:
                segments = await self._detect_language_segments(text)
                final_result.detected_segments = segments
                final_result.is_mixed_language = len(set(seg[1] for seg in segments)) > 1
            
            # Step 6: Update context and metrics
            self._update_detection_context(user_id, final_result, text)
            self._update_performance_metrics(final_result)
            
            final_result.processing_time = time.time() - start_time
            final_result.script_info = script_info
            
            log_info(f"🔍 Language detected: {final_result.detected_language} "
                    f"({final_result.confidence:.2f} confidence, {final_result.method_used.value})")
            
            return final_result
            
        except Exception as e:
            log_error(f"Language detection failed: {e}")
            return self._create_error_result(start_time, str(e))
    
    async def _detect_with_langdetect(self, text: str) -> List[Tuple[str, float]]:
        """Detect language using langdetect library"""
        try:
            # Get multiple possible languages with probabilities
            lang_probs = detect_langs(text)
            return [(lang.lang, lang.prob) for lang in lang_probs]
        except Exception as e:
            log_warning(f"LangDetect failed: {e}")
            return []
    
    async def _detect_with_textblob(self, text: str) -> List[Tuple[str, float]]:
        """Detect language using TextBlob"""
        try:
            blob = TextBlob(text)
            detected_lang = blob.detect_language  # Property, not method
            # TextBlob doesn't provide confidence, so we estimate based on text length
            confidence = min(0.8, len(text) / 100)  # Simple heuristic
            return [(detected_lang, confidence)]
        except Exception as e:
            log_warning(f"TextBlob detection failed: {e}")
            return []
    
    async def _detect_with_polyglot(self, text: str) -> List[Tuple[str, float]]:
        """Detect language using Polyglot"""
        try:
            detector = Detector(text, quiet=True)
            results = []
            for language in detector.languages:
                results.append((language.code, language.confidence))
            return results
        except Exception as e:
            log_warning(f"Polyglot detection failed: {e}")
            return []
    
    def _apply_context_adjustments(self, detection_results: Dict[DetectionMethod, List[Tuple[str, float]]], 
                                 context: LanguageContext) -> List[Tuple[str, float]]:
        """Apply context-based adjustments to detection results"""
        
        context_scores = defaultdict(float)
        
        # Boost scores for user's preferred languages
        for lang in context.user_preferred_languages:
            context_scores[lang] += 0.3
        
        # Boost scores for recently detected languages
        recent_languages = Counter(context.detected_language_sequence[-10:])  # Last 10 detections
        for lang, count in recent_languages.items():
            context_scores[lang] += 0.1 * (count / 10)  # Up to 0.1 boost
        
        # Apply topic-based adjustments (simplified)
        if context.topic_context:
            topic_lang_mapping = {
                'business': ['en', 'hi'],
                'technical': ['en'],
                'casual': ['hi', 'en']
            }
            
            topic_languages = topic_lang_mapping.get(context.topic_context, [])
            for lang in topic_languages:
                context_scores[lang] += 0.1
        
        return list(context_scores.items())
    
    async def _ensemble_detection(self, detection_results: Dict[DetectionMethod, List[Tuple[str, float]]], 
                                script_suggestions: List[Tuple[str, float]], 
                                text: str, context: LanguageContext) -> LanguageDetectionResult:
        """Combine results from multiple detection methods using ensemble approach"""
        
        # Weight different methods - INCREASED heuristic weight for better Hindi detection
        method_weights = {
            DetectionMethod.HEURISTIC: 0.4,  # Increased for better Hindi/Hinglish detection
            DetectionMethod.LANGDETECT: 0.25,  # Reduced since it fails on short Hindi phrases
            DetectionMethod.TEXTBLOB: 0.1,
            DetectionMethod.POLYGLOT: 0.15,
            DetectionMethod.CONTEXT: 0.1
        }
        
        # Combine scores using weighted voting
        combined_scores = defaultdict(float)
        methods_used = []
        
        for method, results in detection_results.items():
            if results:
                methods_used.append(method)
                weight = method_weights.get(method, 0.1)
                
                for lang, confidence in results:
                    combined_scores[lang] += confidence * weight
        
        # Add script-based suggestions with lower weight
        for lang, script_confidence in script_suggestions:
            combined_scores[lang] += script_confidence * 0.1
        
        # CRITICAL FIX: Context-aware detection for short inputs
        text_lower = text.lower().strip()
        words = text_lower.split()
        
        # For very short inputs (1-2 words), use conversation context
        if len(words) <= 2 and context and context.detected_language_sequence:
            recent_lang = context.detected_language_sequence[-1]  # Last detected language
            if recent_lang == 'hi':  # Continue in Hindi context
                combined_scores['hi'] += 0.8  # Strong boost for context continuity
                
        # Common English words that appear in Hindi conversations
        english_in_hindi_words = ['switch', 'stabilizer', 'motor', 'fan', 'light', 'socket', 'wire', 'cable', 'meter']
        if any(word in text_lower for word in english_in_hindi_words):
            # These are typically used in Hindi electrical conversations
            combined_scores['hi'] += 0.6
        
        # CRITICAL FIX: Special boost for Hindi when Hinglish patterns are detected
        hinglish_patterns = ['kitna', 'kitne', 'kaise', 'kya', 'aap', 'hai', 'ka', 'ke', 'ki', 'switch', 'price', 'paisa', 'paise']
        hinglish_matches = sum(1 for pattern in hinglish_patterns if pattern in text_lower)
        if hinglish_matches > 0:
            # Strong boost for Hindi when Hinglish patterns detected
            combined_scores['hi'] += hinglish_matches * 0.3
        
        if not combined_scores:
            return self._create_default_result(time.time())
        
        # Find the language with highest combined score
        sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        best_lang, best_confidence = sorted_results[0]
        
        # Determine primary method used
        primary_method = DetectionMethod.ENSEMBLE
        if len(methods_used) == 1:
            primary_method = methods_used[0]
        
        # Create confidence level
        confidence_level = self._determine_confidence_level(best_confidence)
        
        # Get alternative languages
        alternatives = sorted_results[1:6]  # Top 5 alternatives
        
        return LanguageDetectionResult(
            detected_language=best_lang,
            confidence=best_confidence,
            confidence_level=confidence_level,
            method_used=primary_method,
            alternative_languages=alternatives,
            is_mixed_language=False,  # Will be updated later
            detected_segments=[],     # Will be updated later
            script_info={},          # Will be updated later
            processing_time=0.0      # Will be updated later
        )
    
    async def _detect_language_segments(self, text: str) -> List[Tuple[str, str, float]]:
        """Detect language in different segments of mixed-language text"""
        
        # Split text into sentences and phrases
        sentences = re.split(r'[.!?]+', text)
        segments = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # Skip very short segments
                continue
            
            try:
                # Use simple detection for each segment
                if LANGDETECT_AVAILABLE:
                    detected_lang = langdetect.detect(sentence)
                    # Estimate confidence based on sentence characteristics
                    confidence = min(0.8, len(sentence) / 50)
                    segments.append((sentence, detected_lang, confidence))
                else:
                    # Fallback to heuristic detection
                    heuristic_results = self.heuristic_detector.detect_language(sentence, top_n=1)
                    if heuristic_results:
                        lang, confidence = heuristic_results[0]
                        segments.append((sentence, lang, confidence))
            except:
                # If detection fails, use default
                segments.append((sentence, 'en', 0.3))
        
        return segments
    
    def _determine_confidence_level(self, confidence: float) -> LanguageConfidence:
        """Determine confidence level based on numerical confidence"""
        if confidence >= 0.9:
            return LanguageConfidence.VERY_HIGH
        elif confidence >= 0.8:
            return LanguageConfidence.HIGH
        elif confidence >= 0.6:
            return LanguageConfidence.MEDIUM
        elif confidence >= 0.4:
            return LanguageConfidence.LOW
        else:
            return LanguageConfidence.VERY_LOW
    
    def _create_default_result(self, start_time: float) -> LanguageDetectionResult:
        """Create default result for empty or invalid input"""
        return LanguageDetectionResult(
            detected_language='en',
            confidence=0.3,
            confidence_level=LanguageConfidence.LOW,
            method_used=DetectionMethod.HEURISTIC,
            alternative_languages=[],
            is_mixed_language=False,
            detected_segments=[],
            script_info={},
            processing_time=time.time() - start_time
        )
    
    def _create_error_result(self, start_time: float, error_msg: str) -> LanguageDetectionResult:
        """Create error result"""
        return LanguageDetectionResult(
            detected_language='en',
            confidence=0.1,
            confidence_level=LanguageConfidence.VERY_LOW,
            method_used=DetectionMethod.HEURISTIC,
            alternative_languages=[],
            is_mixed_language=False,
            detected_segments=[],
            script_info={'error': error_msg},
            processing_time=time.time() - start_time
        )
    
    def _update_detection_context(self, user_id: Optional[str], 
                                result: LanguageDetectionResult, text: str):
        """Update language detection context for user"""
        
        if not user_id:
            return
        
        with self._lock:
            if user_id not in self.language_contexts:
                self.language_contexts[user_id] = LanguageContext([], [], [], None, None, None)
            
            context = self.language_contexts[user_id]
            
            # Update conversation history
            context.conversation_history.append(text)
            if len(context.conversation_history) > 50:  # Keep last 50 messages
                context.conversation_history = context.conversation_history[-50:]
            
            # Update detected language sequence
            context.detected_language_sequence.append(result.detected_language)
            if len(context.detected_language_sequence) > 20:  # Keep last 20 detections
                context.detected_language_sequence = context.detected_language_sequence[-20:]
            
            # Update user preferred languages based on usage
            lang_usage = Counter(context.detected_language_sequence)
            most_used_languages = [lang for lang, count in lang_usage.most_common(3)]
            context.user_preferred_languages = most_used_languages
    
    def _update_performance_metrics(self, result: LanguageDetectionResult):
        """Update detection performance metrics"""
        
        with self._lock:
            self.performance_metrics['total_detections'] += 1
            self.performance_metrics['method_usage'][result.method_used] += 1
            
            # Update average confidence
            total = self.performance_metrics['total_detections']
            current_avg = self.performance_metrics['average_confidence']
            self.performance_metrics['average_confidence'] = \
                (current_avg * (total - 1) + result.confidence) / total
            
            # Store recent detection for analysis
            self.detection_history.append({
                'timestamp': time.time(),
                'language': result.detected_language,
                'confidence': result.confidence,
                'method': result.method_used.value
            })
            
            # Keep only recent history
            if len(self.detection_history) > 1000:
                self.detection_history = self.detection_history[-1000:]
    
    def get_detection_analytics(self) -> Dict[str, Any]:
        """Get comprehensive detection analytics"""
        
        with self._lock:
            recent_detections = [d for d in self.detection_history if time.time() - d['timestamp'] < 3600]  # Last hour
            
            # Language distribution
            lang_dist = Counter(d['language'] for d in recent_detections)
            
            # Method performance
            method_performance = defaultdict(list)
            for detection in recent_detections:
                method_performance[detection['method']].append(detection['confidence'])
            
            method_avg_confidence = {
                method: sum(confidences) / len(confidences)
                for method, confidences in method_performance.items()
                if confidences
            }
            
            # Detection speed analysis
            processing_times = [d.get('processing_time', 0) for d in recent_detections if d.get('processing_time')]
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            return {
                'overview': {
                    'total_detections': self.performance_metrics['total_detections'],
                    'average_confidence': self.performance_metrics['average_confidence'],
                    'active_users': len(self.language_contexts),
                    'recent_detections_1h': len(recent_detections)
                },
                'language_distribution': dict(lang_dist.most_common(10)),
                'method_usage': dict(self.performance_metrics['method_usage']),
                'method_performance': method_avg_confidence,
                'performance_metrics': {
                    'avg_processing_time_ms': avg_processing_time * 1000,
                    'detection_methods_available': len([m for m in DetectionMethod if getattr(self, f'_{m.value}_available', True)]),
                    'context_learning_enabled': self.settings['enable_context_learning']
                }
            }
    
    def configure_detection_settings(self, **settings):
        """Configure detection settings"""
        
        for key, value in settings.items():
            if key in self.settings:
                self.settings[key] = value
                log_info(f"🔧 Updated detection setting {key} to {value}")
            else:
                log_warning(f"Unknown detection setting: {key}")
    
    def get_user_language_profile(self, user_id: str) -> Dict[str, Any]:
        """Get language profile for specific user"""
        
        if user_id not in self.language_contexts:
            return {}
        
        context = self.language_contexts[user_id]
        
        # Language usage analysis
        lang_usage = Counter(context.detected_language_sequence)
        total_detections = len(context.detected_language_sequence)
        
        language_percentages = {
            lang: (count / total_detections) * 100
            for lang, count in lang_usage.items()
        } if total_detections > 0 else {}
        
        # Recent language trends
        recent_languages = context.detected_language_sequence[-10:]
        recent_trend = Counter(recent_languages)
        
        return {
            'user_id': user_id,
            'total_conversations': len(context.conversation_history),
            'total_detections': total_detections,
            'preferred_languages': context.user_preferred_languages,
            'language_usage_percentage': language_percentages,
            'recent_language_trend': dict(recent_trend),
            'is_multilingual': len(lang_usage) > 1,
            'dominant_language': lang_usage.most_common(1)[0][0] if lang_usage else 'en'
        }
    
    async def detect_language_realtime(self, text: str, user_id: Optional[str] = None) -> str:
        """Fast real-time language detection for quick switching"""
        
        # For real-time detection, use the fastest available method
        try:
            # Quick script-based detection first
            script_info = self.script_detector.detect_scripts(text)
            if script_info:
                script_suggestions = self.script_detector.suggest_languages_from_scripts(script_info)
                if script_suggestions and script_suggestions[0][1] > 0.7:
                    return script_suggestions[0][0]
            
            # Quick heuristic detection
            heuristic_results = self.heuristic_detector.detect_language(text, top_n=1)
            if heuristic_results and heuristic_results[0][1] > 0.3:
                return heuristic_results[0][0]
            
            # Use langdetect as fallback if available
            if LANGDETECT_AVAILABLE:
                return langdetect.detect(text)
            
            # Context-based guess
            if user_id and user_id in self.language_contexts:
                context = self.language_contexts[user_id]
                if context.user_preferred_languages:
                    return context.user_preferred_languages[0]
            
            return 'en'  # Default fallback
            
        except Exception as e:
            log_warning(f"Real-time detection failed: {e}")
            return 'en'
    
    def cleanup(self):
        """Clean up resources"""
        with self._lock:
            # Clear old context data
            current_time = time.time()
            users_to_remove = []
            
            for user_id, context in self.language_contexts.items():
                # Remove inactive users (no detection in last 7 days)
                if (not context.detected_language_sequence or 
                    current_time - max(d['timestamp'] for d in self.detection_history 
                                     if d.get('user_id') == user_id) > 7 * 24 * 3600):
                    users_to_remove.append(user_id)
            
            for user_id in users_to_remove:
                del self.language_contexts[user_id]
            
            # Limit detection history
            if len(self.detection_history) > 5000:
                self.detection_history = self.detection_history[-1000:]
            
            log_info(f"✅ Language detection cleanup completed. Removed {len(users_to_remove)} inactive users")

# Global instance
_language_detector = None

def get_language_detector() -> EnhancedLanguageDetector:
    """Get global language detector instance"""
    global _language_detector
    if _language_detector is None:
        _language_detector = EnhancedLanguageDetector()
    return _language_detector

async def detect_language_enhanced(text: str, user_id: Optional[str] = None) -> LanguageDetectionResult:
    """Convenience function for enhanced language detection"""
    detector = get_language_detector()
    return await detector.detect_language_advanced(text, user_id)

async def detect_language_fast(text: str, user_id: Optional[str] = None) -> str:
    """Convenience function for fast language detection"""
    detector = get_language_detector()
    return await detector.detect_language_realtime(text, user_id)

if __name__ == "__main__":
    # Test the enhanced language detector
    import asyncio
    
    async def test_language_detection():
        print("🔍 Testing Enhanced Language Detection")
        print("=" * 50)
        
        detector = get_language_detector()
        
        test_cases = [
            ("Hello, how are you today?", "en"),
            ("नमस्ते, आप कैसे हैं?", "hi"),
            ("Hola, ¿cómo estás?", "es"),
            ("Bonjour, comment allez-vous?", "fr"),
            ("Hello भाई, switch kitna ka hai?", "mixed"),  # Mixed language
            ("السلام عليكم", "ar"),
            ("こんにちは、元気ですか？", "ja"),
            ("안녕하세요", "ko"),
            ("Привет, как дела?", "ru"),
            ("Thanks बहुत धन्यवाद!", "mixed"),  # Another mixed case
        ]
        
        user_id = "test_user"
        
        for text, expected in test_cases:
            print(f"\nTesting: {text}")
            print(f"Expected: {expected}")
            
            # Full detection
            result = await detector.detect_language_advanced(text, user_id)
            print(f"Detected: {result.detected_language} ({result.confidence:.2f} confidence)")
            print(f"Method: {result.method_used.value}")
            print(f"Mixed: {result.is_mixed_language}")
            print(f"Processing time: {result.processing_time*1000:.1f}ms")
            
            if result.alternative_languages:
                alts = ", ".join([f"{lang}({conf:.2f})" for lang, conf in result.alternative_languages[:3]])
                print(f"Alternatives: {alts}")
            
            # Fast detection
            fast_result = await detector.detect_language_realtime(text, user_id)
            print(f"Fast detection: {fast_result}")
        
        # Test analytics
        print(f"\n📊 Detection Analytics:")
        analytics = detector.get_detection_analytics()
        print(f"Total detections: {analytics['overview']['total_detections']}")
        print(f"Average confidence: {analytics['overview']['average_confidence']:.2f}")
        print(f"Language distribution: {analytics['language_distribution']}")
        
        # Test user profile
        profile = detector.get_user_language_profile(user_id)
        print(f"\n👤 User Profile:")
        print(f"Preferred languages: {profile.get('preferred_languages', [])}")
        print(f"Is multilingual: {profile.get('is_multilingual', False)}")
        print(f"Dominant language: {profile.get('dominant_language', 'unknown')}")
        
        detector.cleanup()
        print("\n✅ Enhanced Language Detection test completed")
    
    # Run the test
    asyncio.run(test_language_detection())