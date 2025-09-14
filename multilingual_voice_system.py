#!/usr/bin/env python3
"""
Multilingual EdgeTTS Integration System
Dynamic voice switching based on detected language with comprehensive voice mapping
"""

import asyncio
import edge_tts
import pygame
import io
import time
import threading
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import random

try:
    from logger import log_info, log_error, log_warning
except ImportError:
    def log_info(msg): print(f"INFO - {msg}")
    def log_error(msg): print(f"ERROR - {msg}")
    def log_warning(msg): print(f"WARNING - {msg}")

class VoiceGender(Enum):
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"

class VoiceStyle(Enum):
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    CHEERFUL = "cheerful"
    CALM = "calm"
    EXCITED = "excited"
    SAD = "sad"
    ANGRY = "angry"

@dataclass
class VoiceProfile:
    """Voice profile with metadata"""
    name: str
    language: str
    locale: str
    gender: VoiceGender
    age_group: str  # Child, Teen, Adult, Senior
    style_capabilities: List[VoiceStyle]
    quality_score: float  # 0.0 to 1.0
    is_neural: bool = True

class MultilingualVoiceSystem:
    """Advanced multilingual voice system with dynamic switching"""
    
    def __init__(self):
        self.current_voice = None
        self.current_language = None
        self.voice_cache = {}  # Cache generated audio
        self.voice_profiles = self._initialize_voice_profiles()
        self.conversation_context = {
            "user_preferences": {},
            "dominant_language": "en",
            "emotional_state": "neutral",
            "conversation_style": "friendly"
        }
        
        # Initialize audio system
        self._setup_audio()
        
        # Voice switching settings
        self.auto_switch_enabled = True
        self.voice_consistency_mode = True  # Keep same voice for consistency
        self.style_adaptation_enabled = True
        
    def _initialize_voice_profiles(self) -> Dict[str, List[VoiceProfile]]:
        """Initialize comprehensive voice profiles for all languages"""
        return {
            # Hindi voices
            "hi": [
                VoiceProfile("hi-IN-MadhurNeural", "hi", "hi-IN", VoiceGender.MALE, "Adult", 
                           [VoiceStyle.FRIENDLY, VoiceStyle.PROFESSIONAL], 0.9),
                VoiceProfile("hi-IN-SwaraNeural", "hi", "hi-IN", VoiceGender.FEMALE, "Adult",
                           [VoiceStyle.FRIENDLY, VoiceStyle.CHEERFUL], 0.95),
                VoiceProfile("hi-IN-AnanyaNeural", "hi", "hi-IN", VoiceGender.FEMALE, "Teen",
                           [VoiceStyle.CHEERFUL, VoiceStyle.EXCITED], 0.85),
            ],
            
            # English voices
            "en": [
                VoiceProfile("en-US-JennyNeural", "en", "en-US", VoiceGender.FEMALE, "Adult",
                           [VoiceStyle.FRIENDLY, VoiceStyle.PROFESSIONAL], 0.95),
                VoiceProfile("en-US-GuyNeural", "en", "en-US", VoiceGender.MALE, "Adult",
                           [VoiceStyle.PROFESSIONAL, VoiceStyle.CALM], 0.9),
                VoiceProfile("en-US-AriaNeural", "en", "en-US", VoiceGender.FEMALE, "Adult",
                           [VoiceStyle.CHEERFUL, VoiceStyle.EXCITED], 0.92),
                VoiceProfile("en-IN-NeerjaNeural", "en", "en-IN", VoiceGender.FEMALE, "Adult",
                           [VoiceStyle.FRIENDLY, VoiceStyle.PROFESSIONAL], 0.88),
                VoiceProfile("en-IN-PrabhatNeural", "en", "en-IN", VoiceGender.MALE, "Adult",
                           [VoiceStyle.PROFESSIONAL, VoiceStyle.CALM], 0.85),
            ],
            
            # Spanish voices
            "es": [
                VoiceProfile("es-ES-ElviraNeural", "es", "es-ES", VoiceGender.FEMALE, "Adult",
                           [VoiceStyle.FRIENDLY, VoiceStyle.PROFESSIONAL], 0.9),
                VoiceProfile("es-ES-AlvaroNeural", "es", "es-ES", VoiceGender.MALE, "Adult",
                           [VoiceStyle.PROFESSIONAL, VoiceStyle.CALM], 0.88),
                VoiceProfile("es-MX-DaliaNeural", "es", "es-MX", VoiceGender.FEMALE, "Adult",
                           [VoiceStyle.CHEERFUL, VoiceStyle.FRIENDLY], 0.92),
            ],
            
            # French voices
            "fr": [
                VoiceProfile("fr-FR-DeniseNeural", "fr", "fr-FR", VoiceGender.FEMALE, "Adult",
                           [VoiceStyle.PROFESSIONAL, VoiceStyle.CALM], 0.9),
                VoiceProfile("fr-FR-HenriNeural", "fr", "fr-FR", VoiceGender.MALE, "Adult",
                           [VoiceStyle.PROFESSIONAL, VoiceStyle.FRIENDLY], 0.88),
                VoiceProfile("fr-CA-SylvieNeural", "fr", "fr-CA", VoiceGender.FEMALE, "Adult",
                           [VoiceStyle.FRIENDLY, VoiceStyle.CHEERFUL], 0.85),
            ],
            
            # German voices
            "de": [
                VoiceProfile("de-DE-KatjaNeural", "de", "de-DE", VoiceGender.FEMALE, "Adult",
                           [VoiceStyle.PROFESSIONAL, VoiceStyle.FRIENDLY], 0.9),
                VoiceProfile("de-DE-ConradNeural", "de", "de-DE", VoiceGender.MALE, "Adult",
                           [VoiceStyle.PROFESSIONAL, VoiceStyle.CALM], 0.88),
                VoiceProfile("de-AT-IngridNeural", "de", "de-AT", VoiceGender.FEMALE, "Adult",
                           [VoiceStyle.FRIENDLY, VoiceStyle.CHEERFUL], 0.87),
            ],
            
            # Italian voices
            "it": [
                VoiceProfile("it-IT-ElsaNeural", "it", "it-IT", VoiceGender.FEMALE, "Adult",
                           [VoiceStyle.FRIENDLY, VoiceStyle.PROFESSIONAL], 0.9),
                VoiceProfile("it-IT-DiegoNeural", "it", "it-IT", VoiceGender.MALE, "Adult",
                           [VoiceStyle.PROFESSIONAL, VoiceStyle.CALM], 0.88),
                VoiceProfile("it-IT-IsabellaNeural", "it", "it-IT", VoiceGender.FEMALE, "Teen",
                           [VoiceStyle.CHEERFUL, VoiceStyle.EXCITED], 0.85),
            ],
            
            # Portuguese voices
            "pt": [
                VoiceProfile("pt-BR-FranciscaNeural", "pt", "pt-BR", VoiceGender.FEMALE, "Adult",
                           [VoiceStyle.FRIENDLY, VoiceStyle.CHEERFUL], 0.9),
                VoiceProfile("pt-BR-AntonioNeural", "pt", "pt-BR", VoiceGender.MALE, "Adult",
                           [VoiceStyle.PROFESSIONAL, VoiceStyle.CALM], 0.88),
                VoiceProfile("pt-PT-RaquelNeural", "pt", "pt-PT", VoiceGender.FEMALE, "Adult",
                           [VoiceStyle.PROFESSIONAL, VoiceStyle.FRIENDLY], 0.87),
            ],
            
            # Japanese voices
            "ja": [
                VoiceProfile("ja-JP-NanamiNeural", "ja", "ja-JP", VoiceGender.FEMALE, "Adult",
                           [VoiceStyle.FRIENDLY, VoiceStyle.PROFESSIONAL], 0.95),
                VoiceProfile("ja-JP-KeitaNeural", "ja", "ja-JP", VoiceGender.MALE, "Adult",
                           [VoiceStyle.PROFESSIONAL, VoiceStyle.CALM], 0.9),
                VoiceProfile("ja-JP-AoiNeural", "ja", "ja-JP", VoiceGender.FEMALE, "Teen",
                           [VoiceStyle.CHEERFUL, VoiceStyle.EXCITED], 0.88),
            ],
            
            # Korean voices
            "ko": [
                VoiceProfile("ko-KR-SunHiNeural", "ko", "ko-KR", VoiceGender.FEMALE, "Adult",
                           [VoiceStyle.FRIENDLY, VoiceStyle.PROFESSIONAL], 0.9),
                VoiceProfile("ko-KR-InJoonNeural", "ko", "ko-KR", VoiceGender.MALE, "Adult",
                           [VoiceStyle.PROFESSIONAL, VoiceStyle.CALM], 0.88),
            ],
            
            # Chinese voices
            "zh": [
                VoiceProfile("zh-CN-XiaoxiaoNeural", "zh", "zh-CN", VoiceGender.FEMALE, "Adult",
                           [VoiceStyle.FRIENDLY, VoiceStyle.PROFESSIONAL], 0.95),
                VoiceProfile("zh-CN-YunxiNeural", "zh", "zh-CN", VoiceGender.MALE, "Adult",
                           [VoiceStyle.PROFESSIONAL, VoiceStyle.CALM], 0.9),
                VoiceProfile("zh-HK-HiuMaanNeural", "zh", "zh-HK", VoiceGender.FEMALE, "Adult",
                           [VoiceStyle.FRIENDLY, VoiceStyle.CHEERFUL], 0.88),
            ],
            
            # Arabic voices
            "ar": [
                VoiceProfile("ar-SA-ZariyahNeural", "ar", "ar-SA", VoiceGender.FEMALE, "Adult",
                           [VoiceStyle.PROFESSIONAL, VoiceStyle.FRIENDLY], 0.9),
                VoiceProfile("ar-SA-HamedNeural", "ar", "ar-SA", VoiceGender.MALE, "Adult",
                           [VoiceStyle.PROFESSIONAL, VoiceStyle.CALM], 0.88),
                VoiceProfile("ar-EG-SalmaNeural", "ar", "ar-EG", VoiceGender.FEMALE, "Adult",
                           [VoiceStyle.FRIENDLY, VoiceStyle.CHEERFUL], 0.85),
            ],
            
            # Russian voices
            "ru": [
                VoiceProfile("ru-RU-SvetlanaNeural", "ru", "ru-RU", VoiceGender.FEMALE, "Adult",
                           [VoiceStyle.PROFESSIONAL, VoiceStyle.FRIENDLY], 0.9),
                VoiceProfile("ru-RU-DmitryNeural", "ru", "ru-RU", VoiceGender.MALE, "Adult",
                           [VoiceStyle.PROFESSIONAL, VoiceStyle.CALM], 0.88),
            ],
            
            # Turkish voices
            "tr": [
                VoiceProfile("tr-TR-EmelNeural", "tr", "tr-TR", VoiceGender.FEMALE, "Adult",
                           [VoiceStyle.FRIENDLY, VoiceStyle.PROFESSIONAL], 0.9),
                VoiceProfile("tr-TR-AhmetNeural", "tr", "tr-TR", VoiceGender.MALE, "Adult",
                           [VoiceStyle.PROFESSIONAL, VoiceStyle.CALM], 0.88),
            ],
        }
    
    def _setup_audio(self):
        """Setup audio system"""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
                pygame.mixer.init()
                log_info("✅ Multilingual audio system initialized")
        except Exception as e:
            log_error(f"Audio setup failed: {e}")
    
    def select_optimal_voice(self, language: str, sentiment: str = "neutral", 
                           gender_preference: Optional[VoiceGender] = None,
                           style_preference: Optional[VoiceStyle] = None) -> Optional[VoiceProfile]:
        """Select optimal voice based on language, sentiment, and preferences"""
        
        # Normalize language code
        language = self._normalize_language_code(language)
        
        if language not in self.voice_profiles:
            log_warning(f"Language {language} not supported, using English")
            language = "en"
        
        voices = self.voice_profiles[language]
        
        # Filter by preferences
        if gender_preference:
            voices = [v for v in voices if v.gender == gender_preference]
        
        if style_preference:
            voices = [v for v in voices if style_preference in v.style_capabilities]
        
        if not voices:
            voices = self.voice_profiles[language]  # Fallback to all voices
        
        # Select based on sentiment and quality
        scored_voices = []
        for voice in voices:
            score = voice.quality_score
            
            # Boost score based on sentiment-style matching
            if sentiment == "positive" and VoiceStyle.CHEERFUL in voice.style_capabilities:
                score += 0.1
            elif sentiment == "negative" and VoiceStyle.CALM in voice.style_capabilities:
                score += 0.1
            elif sentiment == "neutral" and VoiceStyle.PROFESSIONAL in voice.style_capabilities:
                score += 0.05
            
            # Prefer adult voices for professional context
            if voice.age_group == "Adult":
                score += 0.05
            
            scored_voices.append((voice, score))
        
        # Select voice with highest score
        if scored_voices:
            scored_voices.sort(key=lambda x: x[1], reverse=True)
            selected_voice = scored_voices[0][0]
            
            log_info(f"🎙️ Selected voice: {selected_voice.name} for {language} ({sentiment})")
            return selected_voice
        
        return None
    
    def _normalize_language_code(self, language: str) -> str:
        """Normalize language codes to standard format"""
        language_mappings = {
            "zh-cn": "zh", "zh-tw": "zh", "zh-hk": "zh",
            "en-us": "en", "en-gb": "en", "en-in": "en",
            "es-es": "es", "es-mx": "es", "es-ar": "es",
            "fr-fr": "fr", "fr-ca": "fr",
            "de-de": "de", "de-at": "de", "de-ch": "de",
            "pt-br": "pt", "pt-pt": "pt",
            "ar-sa": "ar", "ar-eg": "ar", "ar-ae": "ar",
        }
        
        return language_mappings.get(language.lower(), language.lower())
    
    async def speak_with_auto_voice(self, text: str, language: str, 
                                  sentiment: str = "neutral", 
                                  context: Dict = None) -> bool:
        """Speak text with automatically selected voice based on language and context"""
        
        try:
            # Select optimal voice
            voice_profile = self.select_optimal_voice(
                language=language,
                sentiment=sentiment,
                style_preference=self._get_style_from_context(context)
            )
            
            if not voice_profile:
                log_error(f"No voice available for language: {language}")
                return False
            
            # Check if we should switch voices
            if self._should_switch_voice(language, voice_profile):
                self.current_voice = voice_profile.name
                self.current_language = language
                log_info(f"🔄 Voice switched to: {voice_profile.name}")
            
            # Generate and play speech
            success = await self._generate_and_play_speech(text, voice_profile)
            
            # Update conversation context
            if success:
                self._update_conversation_context(language, sentiment, voice_profile)
            
            return success
            
        except Exception as e:
            log_error(f"Voice synthesis failed: {e}")
            return False
    
    def _get_style_from_context(self, context: Dict) -> Optional[VoiceStyle]:
        """Determine voice style from conversation context"""
        if not context:
            return VoiceStyle.FRIENDLY
        
        # Map emotional states to voice styles
        emotional_state = context.get("emotional_state", "neutral")
        intent = context.get("intent", "general")
        
        style_mapping = {
            "happy": VoiceStyle.CHEERFUL,
            "excited": VoiceStyle.EXCITED,
            "sad": VoiceStyle.CALM,
            "angry": VoiceStyle.CALM,
            "neutral": VoiceStyle.FRIENDLY,
            "positive": VoiceStyle.CHEERFUL,
            "negative": VoiceStyle.CALM
        }
        
        # Intent-based style selection
        if intent in ["complaint", "problem"]:
            return VoiceStyle.CALM
        elif intent in ["appreciation", "thanks"]:
            return VoiceStyle.CHEERFUL
        elif intent in ["business_inquiry", "technical"]:
            return VoiceStyle.PROFESSIONAL
        
        return style_mapping.get(emotional_state, VoiceStyle.FRIENDLY)
    
    def _should_switch_voice(self, language: str, voice_profile: VoiceProfile) -> bool:
        """Determine if voice should be switched"""
        
        if not self.auto_switch_enabled:
            return False
        
        # Always switch if language changed
        if self.current_language != language:
            return True
        
        # Don't switch if consistency mode is enabled and we have a current voice
        if self.voice_consistency_mode and self.current_voice:
            return False
        
        # Switch if the new voice has significantly higher quality
        if self.current_voice and voice_profile:
            current_voices = [v for voices in self.voice_profiles.values() 
                            for v in voices if v.name == self.current_voice]
            if current_voices:
                current_quality = current_voices[0].quality_score
                if voice_profile.quality_score - current_quality > 0.1:
                    return True
        
        return not self.current_voice  # Switch if no current voice
    
    async def _generate_and_play_speech(self, text: str, voice_profile: VoiceProfile) -> bool:
        """Generate and play speech using EdgeTTS"""
        
        try:
            # Check cache first
            cache_key = f"{voice_profile.name}:{hash(text)}"
            if cache_key in self.voice_cache:
                audio_data = self.voice_cache[cache_key]
                log_info("🔄 Using cached audio")
            else:
                # Generate speech
                log_info(f"🎙️ Generating speech: {text[:50]}...")
                
                # Create EdgeTTS communication with SSML for style control
                ssml_text = self._create_ssml_text(text, voice_profile)
                communicate = edge_tts.Communicate(ssml_text, voice_profile.name)
                
                # Generate audio data
                audio_data = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data += chunk["data"]
                
                # Cache the audio (limit cache size)
                if len(self.voice_cache) < 50:
                    self.voice_cache[cache_key] = audio_data
            
            # Play audio
            if audio_data:
                return self._play_audio(audio_data)
            
            return False
            
        except Exception as e:
            log_error(f"Speech generation failed: {e}")
            return False
    
    def _create_ssml_text(self, text: str, voice_profile: VoiceProfile) -> str:
        """Create clean text without SSML to avoid technical details in speech"""
        
        # CRITICAL FIX: Return clean text only, no SSML tags
        # SSML tags were leaking into actual speech causing technical parameter verbalization
        
        # Clean the text of any existing SSML or technical artifacts
        clean_text = text.strip()
        
        # Remove any existing SSML tags if they somehow got into the text
        import re
        clean_text = re.sub(r'<[^>]+>', '', clean_text)  # Remove any XML/SSML tags
        
        # Remove technical parameters that might have leaked
        technical_terms = ['rate="', 'pitch="', 'prosody', 'speak version', 'xmlns', 'break time']
        for term in technical_terms:
            if term in clean_text:
                clean_text = re.sub(r'.*' + re.escape(term) + r'.*?>', '', clean_text)
        
        # Clean up extra spaces and ensure proper text
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # For now, return plain text to avoid SSML leakage
        return clean_text
        ssml += '</speak>'
        
        return ssml
    
    def _play_audio(self, audio_data: bytes) -> bool:
        """Play audio data using pygame"""
        
        try:
            # Stop any current audio
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                time.sleep(0.1)
            
            # Play audio
            audio_buffer = io.BytesIO(audio_data)
            pygame.mixer.music.load(audio_buffer)
            pygame.mixer.music.play()
            
            # Wait for playback to complete
            start_time = time.time()
            max_wait = 60  # 60 second timeout
            
            while pygame.mixer.music.get_busy():
                if time.time() - start_time > max_wait:
                    pygame.mixer.music.stop()
                    log_warning("Audio playback timeout")
                    return False
                time.sleep(0.1)
            
            log_info("✅ Audio playback completed")
            return True
            
        except Exception as e:
            log_error(f"Audio playback failed: {e}")
            return False
    
    def _update_conversation_context(self, language: str, sentiment: str, voice_profile: VoiceProfile):
        """Update conversation context for better voice selection"""
        
        self.conversation_context.update({
            "dominant_language": language,
            "emotional_state": sentiment,
            "last_voice_used": voice_profile.name,
            "voice_consistency_preference": self.voice_consistency_mode
        })
        
        # Track user preferences
        if "language_preferences" not in self.conversation_context:
            self.conversation_context["language_preferences"] = {}
        
        lang_prefs = self.conversation_context["language_preferences"]
        if language not in lang_prefs:
            lang_prefs[language] = {"count": 0, "preferred_voice": None}
        
        lang_prefs[language]["count"] += 1
        lang_prefs[language]["preferred_voice"] = voice_profile.name
    
    def get_available_voices(self, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available voices for a language or all languages"""
        
        if language:
            language = self._normalize_language_code(language)
            if language in self.voice_profiles:
                return [self._voice_to_dict(v) for v in self.voice_profiles[language]]
            return []
        
        # Return all voices
        all_voices = []
        for voices in self.voice_profiles.values():
            all_voices.extend([self._voice_to_dict(v) for v in voices])
        
        return all_voices
    
    def _voice_to_dict(self, voice_profile: VoiceProfile) -> Dict[str, Any]:
        """Convert voice profile to dictionary"""
        return {
            "name": voice_profile.name,
            "language": voice_profile.language,
            "locale": voice_profile.locale,
            "gender": voice_profile.gender.value,
            "age_group": voice_profile.age_group,
            "styles": [style.value for style in voice_profile.style_capabilities],
            "quality_score": voice_profile.quality_score,
            "is_neural": voice_profile.is_neural
        }
    
    def set_voice_preferences(self, **preferences):
        """Set voice preferences for future selections"""
        
        if "auto_switch" in preferences:
            self.auto_switch_enabled = preferences["auto_switch"]
        
        if "consistency_mode" in preferences:
            self.voice_consistency_mode = preferences["consistency_mode"]
        
        if "style_adaptation" in preferences:
            self.style_adaptation_enabled = preferences["style_adaptation"]
        
        self.conversation_context.update(preferences)
        log_info(f"🔧 Voice preferences updated: {preferences}")
    
    def get_voice_statistics(self) -> Dict[str, Any]:
        """Get voice usage statistics"""
        
        return {
            "current_voice": self.current_voice,
            "current_language": self.current_language,
            "total_languages": len(self.voice_profiles),
            "total_voices": sum(len(voices) for voices in self.voice_profiles.values()),
            "cache_size": len(self.voice_cache),
            "conversation_context": self.conversation_context,
            "settings": {
                "auto_switch_enabled": self.auto_switch_enabled,
                "voice_consistency_mode": self.voice_consistency_mode,
                "style_adaptation_enabled": self.style_adaptation_enabled
            }
        }
    
    def cleanup(self):
        """Cleanup voice system resources"""
        try:
            if pygame.mixer.get_init():
                pygame.mixer.quit()
            self.voice_cache.clear()
            log_info("✅ Multilingual voice system cleaned up")
        except Exception as e:
            log_error(f"Voice system cleanup failed: {e}")

# Global instance
_multilingual_voice_system = None

def get_multilingual_voice_system() -> MultilingualVoiceSystem:
    """Get global multilingual voice system instance"""
    global _multilingual_voice_system
    if _multilingual_voice_system is None:
        _multilingual_voice_system = MultilingualVoiceSystem()
    return _multilingual_voice_system

async def speak_multilingual(text: str, language: str, sentiment: str = "neutral", 
                           context: Dict = None) -> bool:
    """Convenience function for multilingual speech"""
    system = get_multilingual_voice_system()
    return await system.speak_with_auto_voice(text, language, sentiment, context)

if __name__ == "__main__":
    # Test the multilingual voice system
    import asyncio
    
    async def test_multilingual_voices():
        print("🎙️ Testing Multilingual Voice System")
        print("=" * 50)
        
        system = get_multilingual_voice_system()
        
        # Test different languages and contexts
        test_cases = [
            ("Hello! Welcome to our electrical shop.", "en", "positive"),
            ("नमस्ते! हमारी electrical shop में आपका स्वागत है।", "hi", "friendly"),
            ("¡Hola! ¿Cómo puedo ayudarte hoy?", "es", "cheerful"),
            ("Bonjour! Comment puis-je vous aider?", "fr", "professional"),
            ("Guten Tag! Wie kann ich Ihnen helfen?", "de", "friendly"),
            ("I'm sorry to hear about the problem.", "en", "sad"),
            ("धन्यवाद! आपकी मदद करके खुशी हुई।", "hi", "happy"),
        ]
        
        for text, language, sentiment in test_cases:
            print(f"\n🗣️ Testing: {language} ({sentiment})")
            print(f"Text: {text}")
            
            success = await system.speak_with_auto_voice(text, language, sentiment)
            
            if success:
                print("✅ Speech generated successfully")
            else:
                print("❌ Speech generation failed")
            
            time.sleep(1)  # Brief pause between tests
        
        # Show statistics
        print(f"\n📊 Voice System Statistics:")
        stats = system.get_voice_statistics()
        print(f"• Current Voice: {stats['current_voice']}")
        print(f"• Current Language: {stats['current_language']}")
        print(f"• Total Languages: {stats['total_languages']}")
        print(f"• Total Voices: {stats['total_voices']}")
        print(f"• Cache Size: {stats['cache_size']}")
    
    # Run the test
    try:
        asyncio.run(test_multilingual_voices())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed: {e}")