"""
Professional Hinglish Voice Processor
Handles accurate speech recognition and pronunciation for Hindi-English mix
"""

import re
import unicodedata
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class HinglishVoiceProcessor:
    """Professional processor for Hinglish voice recognition and synthesis"""
    
    def __init__(self):
        # Common Hindi words in Roman script for better pronunciation
        self.hindi_roman_map = {
            'namaste': 'नमस्ते',
            'kya': 'क्या', 
            'hai': 'है',
            'hain': 'हैं',
            'main': 'मैं',
            'aap': 'आप',
            'tum': 'तुम',
            'mera': 'मेरा',
            'tera': 'तेरा',
            'uska': 'उसका',
            'kaise': 'कैसे',
            'kaha': 'कहा',
            'kahan': 'कहाँ',
            'kab': 'कब',
            'kyun': 'क्यों',
            'accha': 'अच्छा',
            'theek': 'ठीक',
            'sahi': 'सही',
            'galat': 'गलत',
            'dhanyawad': 'धन्यवाद',
            'alvida': 'अलविदा',
            'phir': 'फिर',
            'milenge': 'मिलेंगे',
            'awaaz': 'आवाज़',
            'boliye': 'बोलिए',
            'suniye': 'सुनिए',
            'dekho': 'देखो',
            'samjha': 'समझा',
            'seekho': 'सीखो',
            'sikha': 'सिखा',
            'jaana': 'जाना',
            'aana': 'आना',
            'karna': 'करना',
            'banana': 'बनाना'
        }
        
        # Language detection patterns
        self.hindi_patterns = [
            r'[क-ह]',  # Devanagari
            r'\b(hai|hain|ka|ke|ki|ko|se|mein|pe|par|aur|ya|ki|main|aap|tum)\b',
            r'\b(kya|kaise|kaha|kahan|kab|kyun|kaun)\b',
            r'\b(accha|theek|sahi|galat|nahi|han|haan)\b'
        ]
        
        self.english_patterns = [
            r'\b(the|is|are|was|were|have|has|had|will|would|can|could|should|may|might)\b',
            r'\b(what|where|when|why|who|how|which)\b',
            r'\b(good|bad|yes|no|okay|fine|great|nice)\b'
        ]
    
    def detect_language_mix(self, text: str) -> Tuple[str, float]:
        """
        Detect if text is Hindi, English, or Hinglish mix
        Returns: (language, confidence)
        """
        if not text:
            return 'unknown', 0.0
        
        text_lower = text.lower()
        total_words = len(text_lower.split())
        
        if total_words == 0:
            return 'unknown', 0.0
        
        # Count Hindi indicators
        hindi_score = 0
        for pattern in self.hindi_patterns:
            hindi_score += len(re.findall(pattern, text_lower))
        
        # Count English indicators  
        english_score = 0
        for pattern in self.english_patterns:
            english_score += len(re.findall(pattern, text_lower))
        
        # Check for Devanagari characters
        devanagari_chars = len([c for c in text if ord(c) >= 0x0900 and ord(c) <= 0x097F])
        
        if devanagari_chars > 0:
            hindi_score += devanagari_chars * 0.5
        
        # Determine language
        if hindi_score > english_score and hindi_score > total_words * 0.3:
            if english_score > 0:
                return 'hinglish', min(0.9, (hindi_score + english_score) / total_words)
            else:
                return 'hindi', min(0.9, hindi_score / total_words)
        elif english_score > total_words * 0.5:
            if hindi_score > 0:
                return 'hinglish', min(0.9, (hindi_score + english_score) / total_words)
            else:
                return 'english', min(0.9, english_score / total_words)
        else:
            return 'hinglish', 0.5  # Default to Hinglish for mixed content
    
    def optimize_for_speech_recognition(self, language_hint: str = None) -> dict:
        """
        Get optimized speech recognition parameters for Hinglish
        """
        if language_hint == 'hindi':
            return {
                'primary_language': 'hi-IN',
                'fallback_languages': ['en-IN', 'en-US'],
                'energy_threshold': 250,  # Lower for Hindi speech
                'pause_threshold': 0.6,   # Shorter pauses for Hindi
                'phrase_time_limit': 15
            }
        elif language_hint == 'english':
            return {
                'primary_language': 'en-US',
                'fallback_languages': ['en-IN', 'hi-IN'],
                'energy_threshold': 300,
                'pause_threshold': 0.8,
                'phrase_time_limit': 12
            }
        else:  # Hinglish or mixed
            return {
                'primary_language': 'en-IN',  # Best for Hinglish
                'fallback_languages': ['hi-IN', 'en-US'],
                'energy_threshold': 200,  # More sensitive for mixed speech
                'pause_threshold': 0.7,   # Balanced pause detection
                'phrase_time_limit': 18   # Longer for code-switching
            }
    
    def preprocess_text_for_tts(self, text: str) -> Tuple[str, str]:
        """
        Preprocess text for optimal TTS pronunciation
        Returns: (processed_text, recommended_voice)
        """
        if not text:
            return "", "english_male_warm"
        
        language, confidence = self.detect_language_mix(text)
        
        # Clean and normalize text
        processed_text = self._normalize_text(text)
        
        # Choose appropriate voice based on content - english_male_warm best for Hinglish
        if language == 'english' and confidence > 0.8:
            recommended_voice = 'english_male_warm'
            processed_text = self._enhance_english_pronunciation(processed_text)
        else:  # Hindi, Hinglish, or mixed content
            recommended_voice = 'english_male_warm'  # Best for Roman script Hindi words
            processed_text = self._enhance_hinglish_pronunciation(processed_text)
        
        return processed_text, recommended_voice
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for better pronunciation"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Fix common transcription issues
        text = re.sub(r'\bvhat\b', 'what', text, flags=re.IGNORECASE)
        text = re.sub(r'\bvhy\b', 'why', text, flags=re.IGNORECASE)
        text = re.sub(r'\bvhen\b', 'when', text, flags=re.IGNORECASE)
        text = re.sub(r'\bvhere\b', 'where', text, flags=re.IGNORECASE)
        text = re.sub(r'\bph\b', 'of', text, flags=re.IGNORECASE)
        text = re.sub(r'\bpraais\b', 'price', text, flags=re.IGNORECASE)
        text = re.sub(r'\bsvich\b', 'switch', text, flags=re.IGNORECASE)
        
        # Fix common Hindi transcription issues
        text = re.sub(r'\bkitne\s*ka\s*hai\b', 'kitne ka hai', text, flags=re.IGNORECASE)
        text = re.sub(r'\btumhara\s*nam\b', 'tumhara naam', text, flags=re.IGNORECASE)
        
        return text
    
    def _enhance_hindi_pronunciation(self, text: str) -> str:
        """Enhance pronunciation for Hindi content"""
        # Add proper word breaks for compound Hindi words
        text = re.sub(r'\bnamaste\b', 'Namaste', text, flags=re.IGNORECASE)
        text = re.sub(r'\bdhanyawad\b', 'Dhanyawad', text, flags=re.IGNORECASE)
        text = re.sub(r'\bkripaya\b', 'Kripaya', text, flags=re.IGNORECASE)
        
        # Add slight pauses after Hindi words for clarity
        hindi_words = ['namaste', 'dhanyawad', 'kripaya', 'samjha', 'accha']
        for word in hindi_words:
            pattern = fr'\b{word}\b'
            replacement = f'{word},'
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _enhance_english_pronunciation(self, text: str) -> str:
        """Enhance pronunciation for English content"""
        # Ensure proper pronunciation of technical terms
        text = re.sub(r'\bAPI\b', 'A-P-I', text)
        text = re.sub(r'\bURL\b', 'U-R-L', text)
        text = re.sub(r'\bTTS\b', 'T-T-S', text)
        
        return text
    
    def _enhance_hinglish_pronunciation(self, text: str) -> str:
        """Enhance pronunciation for Hinglish mix"""
        # Handle common Hinglish patterns
        text = re.sub(r'\bmain\s+hun\b', 'main hoon', text, flags=re.IGNORECASE)
        text = re.sub(r'\baapka\s+naam\b', 'aapka naam', text, flags=re.IGNORECASE)
        text = re.sub(r'\bkya\s+hai\b', 'kya hai', text, flags=re.IGNORECASE)
        
        # Add natural pauses at language switches
        # English to Hindi switches
        text = re.sub(r'\b(what|how|when|where)\s+(hai|hain|ka|ke|ki)\b', 
                     r'\1, \2', text, flags=re.IGNORECASE)
        
        # Hindi to English switches  
        text = re.sub(r'\b(main|aap|yeh|woh)\s+(is|are|was|were)\b',
                     r'\1, \2', text, flags=re.IGNORECASE)
        
        return text
    
    def post_process_recognition_result(self, text: str) -> str:
        """Post-process speech recognition result for better accuracy"""
        if not text:
            return ""
        
        # Fix common recognition errors
        fixes = {
            'vhat': 'what',
            'vhy': 'why', 
            'vhen': 'when',
            'vhere': 'where',
            'praais': 'price',
            'svich': 'switch',
            'egjit': 'exit',
            'मॉdl': 'model',
            'ऑph़': 'of'
        }
        
        result = text
        for wrong, correct in fixes.items():
            result = re.sub(fr'\b{re.escape(wrong)}\b', correct, result, flags=re.IGNORECASE)
        
        # Clean up mixed scripts
        result = re.sub(r'([a-zA-Z])[़ः]([a-zA-Z])', r'\1\2', result)
        
        return result.strip()

# Global instance
hinglish_processor = HinglishVoiceProcessor()