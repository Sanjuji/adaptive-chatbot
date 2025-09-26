#!/usr/bin/env python3
"""
Advanced Multilingual Processor - Sophisticated Language Processing
Handles Hinglish, code-switching, contextual language detection, and multilingual understanding
Optimized for Indian market with Hindi-English mixed conversations
"""

import asyncio
import re
import json
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict, Counter
from enum import Enum
import string

# Try to import language detection libraries
try:
    from langdetect import detect, detect_langs, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    from googletrans import Translator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

from utils.logger import log_info, log_error, log_warning
from utils.performance_monitor import monitor_performance, MetricType, get_performance_monitor

class LanguageCode(Enum):
    """Supported language codes"""
    HINDI = "hi"
    ENGLISH = "en"
    HINGLISH = "hi-en"
    UNKNOWN = "unknown"

class ScriptType(Enum):
    """Text script types"""
    LATIN = "latin"
    DEVANAGARI = "devanagari"
    MIXED = "mixed"
    UNKNOWN = "unknown"

@dataclass
class LanguageSegment:
    """Language segment in text"""
    text: str
    language: LanguageCode
    confidence: float
    start_pos: int
    end_pos: int
    script_type: ScriptType
    is_transliterated: bool = False

@dataclass
class MultilingualAnalysis:
    """Complete multilingual analysis result"""
    original_text: str
    primary_language: LanguageCode
    confidence: float
    segments: List[LanguageSegment]
    is_code_switching: bool
    transliterated_text: Optional[str] = None
    translated_text: Optional[str] = None
    context_hints: Dict[str, Any] = None
    processing_time_ms: float = 0.0

class HinglishDetector:
    """Advanced Hinglish and code-switching detection"""
    
    def __init__(self):
        # Common Hinglish patterns and words
        self.hinglish_patterns = [
            # Common Hinglish phrases
            r'\b(?:kya|hai|hain|kaise|kaun|kahan|kab|kyun|kaise|theek|accha|nahi|haa|ji)\b',
            # Mixed expressions
            r'\b(?:yaar|dude|bhai|didi|uncle|aunty|sir|madam)\b',
            # Transliterated Hindi words in English
            r'\b(?:namaste|dhanyawad|shukriya|arre|oye|chal|dekh|sun|kar|bol)\b',
            # Business terms
            r'\b(?:dukan|shop|paisa|rupees|kitna|price|rate|cost)\b'
        ]
        
        # Hindi words commonly found in Hinglish
        self.hindi_indicators = {
            'kya', 'hai', 'hain', 'aap', 'main', 'hum', 'tum', 'wo', 'ye',
            'kaise', 'kaun', 'kahan', 'kab', 'kyun', 'nahi', 'haa', 'ji',
            'theek', 'accha', 'bura', 'chahiye', 'kar', 'karo', 'kiya',
            'dekho', 'suno', 'bolo', 'chalo', 'aao', 'jao', 'raho',
            'paisa', 'rupees', 'kitna', 'zyada', 'kam', 'sab', 'kuch'
        }
        
        # English words commonly used in Hinglish
        self.english_indicators = {
            'price', 'rate', 'cost', 'shop', 'market', 'business', 'service',
            'install', 'repair', 'quality', 'brand', 'good', 'bad', 'nice',
            'please', 'thank', 'sorry', 'ok', 'okay', 'yes', 'no',
            'switch', 'wire', 'light', 'fan', 'socket', 'mcb', 'electrical'
        }
        
        # Devanagari script range
        self.devanagari_range = range(0x0900, 0x097F)
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.hinglish_patterns]
    
    def detect_script_type(self, text: str) -> ScriptType:
        """Detect the script type of text"""
        if not text.strip():
            return ScriptType.UNKNOWN
        
        # Count characters by script
        latin_count = 0
        devanagari_count = 0
        total_alpha = 0
        
        for char in text:
            if char.isalpha():
                total_alpha += 1
                if ord(char) in self.devanagari_range:
                    devanagari_count += 1
                elif char.isascii():
                    latin_count += 1
        
        if total_alpha == 0:
            return ScriptType.UNKNOWN
        
        # Determine script type
        devanagari_ratio = devanagari_count / total_alpha
        latin_ratio = latin_count / total_alpha
        
        if devanagari_ratio > 0.7:
            return ScriptType.DEVANAGARI
        elif latin_ratio > 0.7:
            return ScriptType.LATIN
        elif devanagari_count > 0 and latin_count > 0:
            return ScriptType.MIXED
        else:
            return ScriptType.UNKNOWN
    
    def calculate_hinglish_score(self, text: str) -> float:
        """Calculate Hinglish probability score (0-1)"""
        if not text.strip():
            return 0.0
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        if not words:
            return 0.0
        
        score = 0.0
        total_words = len(words)
        
        # Check for Hindi indicators
        hindi_count = sum(1 for word in words if word in self.hindi_indicators)
        
        # Check for English indicators
        english_count = sum(1 for word in words if word in self.english_indicators)
        
        # Check for Hinglish patterns
        pattern_matches = sum(1 for pattern in self.compiled_patterns if pattern.search(text))
        
        # Check script mixing
        script_type = self.detect_script_type(text)
        script_bonus = 0.3 if script_type == ScriptType.MIXED else 0.0
        
        # Calculate score
        hindi_score = (hindi_count / total_words) * 0.4
        english_score = (english_count / total_words) * 0.2
        pattern_score = min(pattern_matches / total_words, 0.3) * 0.3
        
        score = hindi_score + english_score + pattern_score + script_bonus
        
        # Bonus for mixed language indicators
        if hindi_count > 0 and english_count > 0:
            score += 0.2
        
        return min(score, 1.0)

class AdvancedMultilingualProcessor:
    """Advanced multilingual processing with Hinglish support"""
    
    def __init__(self, enable_translation: bool = True):
        self.enable_translation = enable_translation
        self.hinglish_detector = HinglishDetector()
        
        # Translation cache
        self.translation_cache = {}
        
        # Language model preferences
        self.language_preferences = {
            LanguageCode.HINDI: 0.3,
            LanguageCode.ENGLISH: 0.4,
            LanguageCode.HINGLISH: 0.3
        }
        
        # Context tracking
        self.conversation_language_history = []
        
        # Initialize translator
        self.translator = None
        if TRANSLATOR_AVAILABLE and enable_translation:
            try:
                self.translator = Translator()
                log_info("🌐 Google Translator initialized")
            except Exception as e:
                log_warning(f"Failed to initialize translator: {e}")
        
        # Initialize NLTK components
        self._initialize_nltk()
        
        log_info("🌍 Advanced Multilingual Processor initialized")
    
    def _initialize_nltk(self):
        """Initialize NLTK components"""
        if not NLTK_AVAILABLE:
            return
        
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            log_info("📚 NLTK components initialized")
        except Exception as e:
            log_warning(f"NLTK initialization failed: {e}")
    
    @monitor_performance("multilingual_processor")
    async def analyze_text(self, text: str, context: Dict[str, Any] = None) -> MultilingualAnalysis:
        """Perform comprehensive multilingual analysis"""
        
        start_time = time.time()
        
        try:
            # Basic validation
            if not text or not text.strip():
                return MultilingualAnalysis(
                    original_text=text,
                    primary_language=LanguageCode.UNKNOWN,
                    confidence=0.0,
                    segments=[],
                    is_code_switching=False,
                    processing_time_ms=0.0
                )
            
            text = text.strip()
            
            # Detect primary language
            primary_language, primary_confidence = await self._detect_primary_language(text)
            
            # Segment text by language
            segments = await self._segment_by_language(text)
            
            # Determine if code-switching is present
            is_code_switching = self._detect_code_switching(segments)
            
            # Generate transliteration if needed
            transliterated_text = None
            if primary_language == LanguageCode.HINGLISH:
                transliterated_text = await self._transliterate_hinglish(text)
            
            # Generate translation if requested
            translated_text = None
            if self.enable_translation and primary_language != LanguageCode.ENGLISH:
                translated_text = await self._translate_to_english(text)
            
            # Extract context hints
            context_hints = self._extract_context_hints(text, segments)
            
            # Update conversation history
            self._update_language_history(primary_language)
            
            processing_time = (time.time() - start_time) * 1000
            
            # Record performance metrics
            monitor = get_performance_monitor()
            monitor.record_metric(
                MetricType.RESPONSE_TIME, 
                processing_time,
                "multilingual_processor",
                {"language": primary_language.value, "segments": len(segments)}
            )
            
            return MultilingualAnalysis(
                original_text=text,
                primary_language=primary_language,
                confidence=primary_confidence,
                segments=segments,
                is_code_switching=is_code_switching,
                transliterated_text=transliterated_text,
                translated_text=translated_text,
                context_hints=context_hints,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            log_error(f"Multilingual analysis failed: {e}")
            processing_time = (time.time() - start_time) * 1000
            
            return MultilingualAnalysis(
                original_text=text,
                primary_language=LanguageCode.UNKNOWN,
                confidence=0.0,
                segments=[],
                is_code_switching=False,
                processing_time_ms=processing_time
            )
    
    async def _detect_primary_language(self, text: str) -> Tuple[LanguageCode, float]:
        """Detect the primary language of text"""
        
        # Check for Hinglish first
        hinglish_score = self.hinglish_detector.calculate_hinglish_score(text)
        
        if hinglish_score > 0.6:  # High Hinglish confidence
            return LanguageCode.HINGLISH, hinglish_score
        
        # Use langdetect for other languages
        if LANGDETECT_AVAILABLE:
            try:
                detections = detect_langs(text)
                
                for detection in detections:
                    if detection.lang == 'hi' and detection.prob > 0.7:
                        return LanguageCode.HINDI, detection.prob
                    elif detection.lang == 'en' and detection.prob > 0.7:
                        # Check if it might be Hinglish with low confidence
                        if hinglish_score > 0.3:
                            return LanguageCode.HINGLISH, (detection.prob + hinglish_score) / 2
                        return LanguageCode.ENGLISH, detection.prob
                
                # If no high confidence detection but some Hinglish indicators
                if hinglish_score > 0.3:
                    return LanguageCode.HINGLISH, hinglish_score
                
                # Return the highest confidence detection
                if detections:
                    best = detections[0]
                    if best.lang == 'hi':
                        return LanguageCode.HINDI, best.prob
                    elif best.lang == 'en':
                        return LanguageCode.ENGLISH, best.prob
                        
            except LangDetectException:
                pass
        
        # Fallback: script-based detection
        script_type = self.hinglish_detector.detect_script_type(text)
        
        if script_type == ScriptType.DEVANAGARI:
            return LanguageCode.HINDI, 0.8
        elif script_type == ScriptType.MIXED:
            return LanguageCode.HINGLISH, 0.7
        elif script_type == ScriptType.LATIN:
            if hinglish_score > 0.2:
                return LanguageCode.HINGLISH, hinglish_score
            else:
                return LanguageCode.ENGLISH, 0.6
        
        return LanguageCode.UNKNOWN, 0.0
    
    async def _segment_by_language(self, text: str) -> List[LanguageSegment]:
        """Segment text by language boundaries"""
        
        segments = []
        
        # Simple sentence-based segmentation for now
        sentences = self._split_sentences(text)
        current_pos = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Find position in original text
            start_pos = text.find(sentence, current_pos)
            if start_pos == -1:
                start_pos = current_pos
            
            end_pos = start_pos + len(sentence)
            current_pos = end_pos
            
            # Detect language for this segment
            lang, confidence = await self._detect_primary_language(sentence)
            
            # Detect script type
            script_type = self.hinglish_detector.detect_script_type(sentence)
            
            # Check if transliterated
            is_transliterated = (lang == LanguageCode.HINGLISH or 
                               (lang == LanguageCode.HINDI and script_type == ScriptType.LATIN))
            
            segment = LanguageSegment(
                text=sentence,
                language=lang,
                confidence=confidence,
                start_pos=start_pos,
                end_pos=end_pos,
                script_type=script_type,
                is_transliterated=is_transliterated
            )
            
            segments.append(segment)
        
        return segments
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        
        if NLTK_AVAILABLE:
            try:
                return sent_tokenize(text)
            except:
                pass
        
        # Fallback: simple splitting
        sentences = re.split(r'[.!?।]\s*', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _detect_code_switching(self, segments: List[LanguageSegment]) -> bool:
        """Detect if code-switching is present in segments"""
        
        if len(segments) < 2:
            return False
        
        # Check for language transitions
        languages = [seg.language for seg in segments]
        unique_languages = set(languages)
        
        # Code-switching if multiple languages present
        if len(unique_languages) > 1:
            return True
        
        # Check for Hinglish (which is inherently code-switching)
        if LanguageCode.HINGLISH in unique_languages:
            return True
        
        return False
    
    async def _transliterate_hinglish(self, text: str) -> str:
        """Transliterate Hinglish to more readable form"""
        
        # Simple transliteration mappings
        transliteration_map = {
            'kya': 'क्या',
            'hai': 'है',
            'hain': 'हैं',
            'aap': 'आप',
            'main': 'मैं',
            'hum': 'हम',
            'theek': 'ठीक',
            'accha': 'अच्छा',
            'nahi': 'नहीं',
            'ji': 'जी',
            'dhanyawad': 'धन्यवाद',
            'namaste': 'नमस्ते'
        }
        
        # For now, return a simplified transliteration
        words = text.lower().split()
        transliterated_words = []
        
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in transliteration_map:
                transliterated_words.append(transliteration_map[clean_word])
            else:
                transliterated_words.append(word)
        
        return ' '.join(transliterated_words)
    
    async def _translate_to_english(self, text: str) -> Optional[str]:
        """Translate text to English"""
        
        if not self.translator:
            return None
        
        # Check cache first
        cache_key = f"translate_{hash(text)}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        try:
            # Detect source language for better translation
            detected_lang = None
            if LANGDETECT_AVAILABLE:
                try:
                    detected_lang = detect(text)
                except:
                    pass
            
            # Translate
            if detected_lang and detected_lang in ['hi', 'en']:
                src_lang = detected_lang
            else:
                src_lang = 'auto'  # Auto-detect
            
            translation = self.translator.translate(text, src=src_lang, dest='en')
            result = translation.text
            
            # Cache the result
            self.translation_cache[cache_key] = result
            
            # Limit cache size
            if len(self.translation_cache) > 1000:
                # Remove oldest entries
                keys_to_remove = list(self.translation_cache.keys())[:100]
                for key in keys_to_remove:
                    del self.translation_cache[key]
            
            return result
            
        except Exception as e:
            log_warning(f"Translation failed: {e}")
            return None
    
    def _extract_context_hints(self, text: str, segments: List[LanguageSegment]) -> Dict[str, Any]:
        """Extract contextual hints from the text"""
        
        hints = {
            'domain_indicators': [],
            'business_terms': [],
            'emotional_indicators': [],
            'question_words': [],
            'politeness_markers': []
        }
        
        text_lower = text.lower()
        
        # Business/electrical domain indicators
        business_terms = [
            'switch', 'wire', 'light', 'fan', 'socket', 'mcb', 'electrical',
            'price', 'rate', 'cost', 'kitna', 'paisa', 'rupees', 'install'
        ]
        
        for term in business_terms:
            if term in text_lower:
                hints['business_terms'].append(term)
        
        # Question words
        question_words = ['kya', 'kaun', 'kaise', 'kahan', 'kab', 'kyun', 'what', 'how', 'where', 'when', 'why']
        for word in question_words:
            if word in text_lower:
                hints['question_words'].append(word)
        
        # Politeness markers
        polite_words = ['please', 'ji', 'sir', 'madam', 'dhanyawad', 'shukriya', 'sorry']
        for word in polite_words:
            if word in text_lower:
                hints['politeness_markers'].append(word)
        
        # Emotional indicators
        emotional_words = ['accha', 'bura', 'good', 'bad', 'excellent', 'problem', 'help', 'urgent']
        for word in emotional_words:
            if word in text_lower:
                hints['emotional_indicators'].append(word)
        
        # Determine if it's likely a business query
        if hints['business_terms']:
            hints['domain_indicators'].append('electrical_business')
        
        if hints['question_words']:
            hints['domain_indicators'].append('inquiry')
        
        return hints
    
    def _update_language_history(self, language: LanguageCode):
        """Update conversation language history"""
        self.conversation_language_history.append({
            'language': language,
            'timestamp': datetime.now()
        })
        
        # Keep only last 20 interactions
        if len(self.conversation_language_history) > 20:
            self.conversation_language_history = self.conversation_language_history[-20:]
    
    def get_conversation_language_trend(self) -> Dict[str, Any]:
        """Get language usage trends in conversation"""
        
        if not self.conversation_language_history:
            return {'primary_language': LanguageCode.UNKNOWN.value, 'confidence': 0.0}
        
        # Count language usage
        language_counts = Counter()
        for entry in self.conversation_language_history[-10:]:  # Last 10 interactions
            language_counts[entry['language']] += 1
        
        if not language_counts:
            return {'primary_language': LanguageCode.UNKNOWN.value, 'confidence': 0.0}
        
        # Find most common language
        most_common = language_counts.most_common(1)[0]
        primary_language = most_common[0]
        confidence = most_common[1] / len(self.conversation_language_history[-10:])
        
        return {
            'primary_language': primary_language.value,
            'confidence': confidence,
            'language_distribution': {lang.value: count for lang, count in language_counts.items()},
            'is_multilingual': len(language_counts) > 1
        }
    
    async def get_optimal_response_language(self, analysis: MultilingualAnalysis) -> LanguageCode:
        """Determine optimal language for response"""
        
        # Consider conversation history
        trend = self.get_conversation_language_trend()
        
        # If user consistently uses one language, match it
        if trend['confidence'] > 0.7:
            return LanguageCode(trend['primary_language'])
        
        # Match the input language
        if analysis.primary_language != LanguageCode.UNKNOWN:
            return analysis.primary_language
        
        # Default to Hinglish for mixed conversations
        if analysis.is_code_switching:
            return LanguageCode.HINGLISH
        
        # Fallback to English
        return LanguageCode.ENGLISH
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        
        trend = self.get_conversation_language_trend()
        
        return {
            'total_interactions': len(self.conversation_language_history),
            'language_trend': trend,
            'translation_cache_size': len(self.translation_cache),
            'features': {
                'langdetect_available': LANGDETECT_AVAILABLE,
                'nltk_available': NLTK_AVAILABLE,
                'translator_available': self.translator is not None
            }
        }
    
    async def cleanup(self):
        """Clean up resources"""
        log_info("🧹 Cleaning up Multilingual Processor...")
        
        self.translation_cache.clear()
        self.conversation_language_history.clear()
        
        log_info("✅ Multilingual Processor cleanup completed")


# Global instance
_multilingual_processor = None

def get_multilingual_processor(**kwargs) -> AdvancedMultilingualProcessor:
    """Get or create global multilingual processor"""
    global _multilingual_processor
    if _multilingual_processor is None:
        _multilingual_processor = AdvancedMultilingualProcessor(**kwargs)
    return _multilingual_processor

if __name__ == "__main__":
    # Test the multilingual processor
    async def test_multilingual_processor():
        print("🧪 Testing Advanced Multilingual Processor")
        print("=" * 60)
        
        # Create processor
        processor = AdvancedMultilingualProcessor(enable_translation=True)
        
        # Test cases with different language combinations
        test_cases = [
            "Switch ka price kya hai?",  # Hinglish
            "Wire kitne rupees mein milta hai?",  # Hinglish with business terms
            "Please tell me about MCB installation.",  # English with business context
            "Main ek electrical shop khol raha hun.",  # Hindi transliterated
            "Aap ki shop mein LED lights available hain?",  # Mixed Hindi-English
            "Thank you, ji. Bahut accha hai.",  # Polite Hinglish
            "What is the rate of copper wire?",  # Pure English
            "मैं एक इलेक्ट्रिकल दुकान खोल रहा हूं।"  # Pure Hindi (Devanagari)
        ]
        
        print(f"\n🔤 Testing {len(test_cases)} multilingual samples...")
        
        total_processing_time = 0
        
        for i, text in enumerate(test_cases, 1):
            print(f"\n--- Test Case {i} ---")
            print(f"Input: {text}")
            
            # Analyze text
            analysis = await processor.analyze_text(text)
            total_processing_time += analysis.processing_time_ms
            
            print(f"Primary Language: {analysis.primary_language.value}")
            print(f"Confidence: {analysis.confidence:.3f}")
            print(f"Code-switching: {'Yes' if analysis.is_code_switching else 'No'}")
            print(f"Segments: {len(analysis.segments)}")
            
            # Show segments
            for j, segment in enumerate(analysis.segments):
                print(f"  Segment {j+1}: '{segment.text}' ({segment.language.value}, {segment.confidence:.2f})")
            
            # Show context hints
            if analysis.context_hints:
                hints = analysis.context_hints
                if hints['business_terms']:
                    print(f"Business terms: {', '.join(hints['business_terms'])}")
                if hints['question_words']:
                    print(f"Question words: {', '.join(hints['question_words'])}")
                if hints['domain_indicators']:
                    print(f"Domain: {', '.join(hints['domain_indicators'])}")
            
            # Show translation if available
            if analysis.translated_text and analysis.translated_text != text:
                print(f"Translation: {analysis.translated_text}")
            
            # Optimal response language
            optimal_lang = await processor.get_optimal_response_language(analysis)
            print(f"Optimal Response Language: {optimal_lang.value}")
            
            print(f"Processing time: {analysis.processing_time_ms:.1f}ms")
        
        # Show overall statistics
        print(f"\n📊 Processing Summary:")
        print(f"Total processing time: {total_processing_time:.1f}ms")
        print(f"Average time per analysis: {total_processing_time/len(test_cases):.1f}ms")
        
        # Get language trends
        trend = processor.get_conversation_language_trend()
        print(f"\n📈 Language Trends:")
        print(f"Primary language: {trend['primary_language']}")
        print(f"Confidence: {trend['confidence']:.3f}")
        print(f"Multilingual conversation: {'Yes' if trend['is_multilingual'] else 'No'}")
        
        if 'language_distribution' in trend:
            print("Language distribution:")
            for lang, count in trend['language_distribution'].items():
                print(f"  • {lang}: {count} interactions")
        
        # Get processing stats
        stats = processor.get_processing_stats()
        print(f"\n⚙️ System Stats:")
        print(f"Total interactions: {stats['total_interactions']}")
        print(f"Translation cache size: {stats['translation_cache_size']}")
        print("Available features:")
        for feature, available in stats['features'].items():
            status = "✅" if available else "❌"
            print(f"  • {feature}: {status}")
        
        # Cleanup
        await processor.cleanup()
        print("\n🧹 Test completed")
    
    # Run test
    asyncio.run(test_multilingual_processor())