#!/usr/bin/env python3
"""
Voice Personality Adaptation Engine - Context-Aware Voice Selection
Implements intelligent voice personality selection based on business domain, user sentiment, and conversation context
Provides dynamic voice adaptation for enhanced user experience
"""

import asyncio
import json
import time
import threading
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import random

from logger import log_info, log_error, log_warning
from performance_monitor import monitor_performance, MetricType, get_performance_monitor

class VoiceGender(Enum):
    """Voice gender options"""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"

class VoiceAge(Enum):
    """Voice age categories"""
    YOUNG = "young"      # 18-30
    MIDDLE = "middle"    # 30-50  
    MATURE = "mature"    # 50+

class VoiceAccent(Enum):
    """Voice accent types"""
    INDIAN = "indian"
    BRITISH = "british"
    AMERICAN = "american"
    NEUTRAL = "neutral"

class VoiceEmotion(Enum):
    """Voice emotional tones"""
    CHEERFUL = "cheerful"
    CALM = "calm"
    EXCITED = "excited"
    EMPATHETIC = "empathetic"
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    SERIOUS = "serious"

class BusinessContext(Enum):
    """Business context types"""
    GREETING = "greeting"
    PRODUCT_INQUIRY = "product_inquiry"
    PRICE_NEGOTIATION = "price_negotiation"
    TECHNICAL_SUPPORT = "technical_support"
    CONSULTATION = "consultation"
    CLOSING = "closing"
    COMPLAINT_HANDLING = "complaint_handling"

@dataclass
class VoiceCharacteristics:
    """Voice characteristics profile"""
    voice_id: str
    name: str
    gender: VoiceGender
    age: VoiceAge
    accent: VoiceAccent
    language_code: str
    speaking_rate: float = 1.0
    pitch: float = 0.0
    volume: float = 0.0
    emotional_range: List[VoiceEmotion] = field(default_factory=list)
    business_suitability: Dict[BusinessContext, float] = field(default_factory=dict)
    cultural_affinity: List[str] = field(default_factory=list)
    formality_level: float = 0.5  # 0.0 = very casual, 1.0 = very formal

@dataclass
class VoiceAdaptationContext:
    """Context for voice adaptation decisions"""
    user_mood: str
    conversation_state: str
    business_context: BusinessContext
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[str] = field(default_factory=list)
    cultural_context: Optional[str] = None
    urgency_level: float = 0.0
    formality_required: float = 0.5
    emotional_tone: Optional[str] = None

@dataclass
class VoicePersonalityProfile:
    """Complete voice personality profile"""
    profile_id: str
    name: str
    description: str
    voice_characteristics: VoiceCharacteristics
    personality_traits: Dict[str, float]  # trait -> strength (0-1)
    adaptation_rules: Dict[str, Any]
    usage_stats: Dict[str, int] = field(default_factory=dict)
    last_used: Optional[datetime] = None

class VoiceLibrary:
    """Manages available voice personalities"""
    
    def __init__(self):
        self.voices = {}  # Voice ID -> VoiceCharacteristics
        self.personalities = {}  # Profile ID -> VoicePersonalityProfile
        
        # Initialize with sample voices
        self._initialize_sample_voices()
        
        # Create personality profiles
        self._create_personality_profiles()
    
    def _initialize_sample_voices(self):
        """Initialize sample voice characteristics"""
        
        sample_voices = [
            # Hindi voices
            VoiceCharacteristics(
                voice_id="hi-IN-MadhurNeural",
                name="Madhur (Hindi Male)",
                gender=VoiceGender.MALE,
                age=VoiceAge.MIDDLE,
                accent=VoiceAccent.INDIAN,
                language_code="hi-IN",
                speaking_rate=0.9,
                pitch=0.0,
                emotional_range=[VoiceEmotion.FRIENDLY, VoiceEmotion.PROFESSIONAL, VoiceEmotion.CALM],
                business_suitability={
                    BusinessContext.GREETING: 0.9,
                    BusinessContext.PRODUCT_INQUIRY: 0.8,
                    BusinessContext.TECHNICAL_SUPPORT: 0.9
                },
                cultural_affinity=["indian", "hindi", "business"],
                formality_level=0.7
            ),
            
            VoiceCharacteristics(
                voice_id="hi-IN-SwaraNeural", 
                name="Swara (Hindi Female)",
                gender=VoiceGender.FEMALE,
                age=VoiceAge.YOUNG,
                accent=VoiceAccent.INDIAN,
                language_code="hi-IN",
                speaking_rate=0.95,
                pitch=0.1,
                emotional_range=[VoiceEmotion.CHEERFUL, VoiceEmotion.FRIENDLY, VoiceEmotion.EMPATHETIC],
                business_suitability={
                    BusinessContext.GREETING: 0.95,
                    BusinessContext.CONSULTATION: 0.9,
                    BusinessContext.COMPLAINT_HANDLING: 0.85
                },
                cultural_affinity=["indian", "hindi", "customer_service"],
                formality_level=0.5
            ),
            
            # English voices
            VoiceCharacteristics(
                voice_id="en-IN-NeerjaNeural",
                name="Neerja (English-Indian Female)",
                gender=VoiceGender.FEMALE,
                age=VoiceAge.MIDDLE,
                accent=VoiceAccent.INDIAN,
                language_code="en-IN",
                speaking_rate=0.9,
                pitch=-0.05,
                emotional_range=[VoiceEmotion.PROFESSIONAL, VoiceEmotion.CALM, VoiceEmotion.FRIENDLY],
                business_suitability={
                    BusinessContext.TECHNICAL_SUPPORT: 0.9,
                    BusinessContext.PRICE_NEGOTIATION: 0.8,
                    BusinessContext.CONSULTATION: 0.85
                },
                cultural_affinity=["indian", "english", "professional"],
                formality_level=0.8
            ),
            
            VoiceCharacteristics(
                voice_id="en-IN-PrabhatNeural",
                name="Prabhat (English-Indian Male)",
                gender=VoiceGender.MALE,
                age=VoiceAge.MIDDLE,
                accent=VoiceAccent.INDIAN,
                language_code="en-IN",
                speaking_rate=0.85,
                pitch=-0.1,
                emotional_range=[VoiceEmotion.PROFESSIONAL, VoiceEmotion.SERIOUS, VoiceEmotion.CALM],
                business_suitability={
                    BusinessContext.TECHNICAL_SUPPORT: 0.95,
                    BusinessContext.PRICE_NEGOTIATION: 0.9,
                    BusinessContext.CONSULTATION: 0.8
                },
                cultural_affinity=["indian", "english", "technical"],
                formality_level=0.9
            ),
            
            # International voices for comparison
            VoiceCharacteristics(
                voice_id="en-US-AriaNeural",
                name="Aria (US English Female)",
                gender=VoiceGender.FEMALE,
                age=VoiceAge.YOUNG,
                accent=VoiceAccent.AMERICAN,
                language_code="en-US",
                speaking_rate=1.0,
                pitch=0.05,
                emotional_range=[VoiceEmotion.CHEERFUL, VoiceEmotion.FRIENDLY, VoiceEmotion.EXCITED],
                business_suitability={
                    BusinessContext.GREETING: 0.8,
                    BusinessContext.PRODUCT_INQUIRY: 0.7
                },
                cultural_affinity=["american", "english", "casual"],
                formality_level=0.4
            ),
            
            VoiceCharacteristics(
                voice_id="en-GB-SoniaNeural",
                name="Sonia (UK English Female)",
                gender=VoiceGender.FEMALE,
                age=VoiceAge.MIDDLE,
                accent=VoiceAccent.BRITISH,
                language_code="en-GB",
                speaking_rate=0.9,
                pitch=0.0,
                emotional_range=[VoiceEmotion.PROFESSIONAL, VoiceEmotion.CALM, VoiceEmotion.SERIOUS],
                business_suitability={
                    BusinessContext.TECHNICAL_SUPPORT: 0.8,
                    BusinessContext.CONSULTATION: 0.85
                },
                cultural_affinity=["british", "english", "formal"],
                formality_level=0.85
            )
        ]
        
        for voice in sample_voices:
            self.voices[voice.voice_id] = voice
    
    def _create_personality_profiles(self):
        """Create voice personality profiles"""
        
        profiles = [
            # Professional consultant personality
            VoicePersonalityProfile(
                profile_id="professional_consultant",
                name="Professional Consultant",
                description="Authoritative, knowledgeable, and trustworthy for business consultations",
                voice_characteristics=self.voices["en-IN-PrabhatNeural"],
                personality_traits={
                    "authority": 0.9,
                    "warmth": 0.6,
                    "enthusiasm": 0.4,
                    "patience": 0.8,
                    "expertise": 0.9
                },
                adaptation_rules={
                    "technical_queries": {"speaking_rate": 0.8, "pitch": -0.1},
                    "price_discussions": {"speaking_rate": 0.85, "volume": -0.05},
                    "explanations": {"speaking_rate": 0.8, "pitch": 0.0}
                }
            ),
            
            # Friendly helper personality
            VoicePersonalityProfile(
                profile_id="friendly_helper",
                name="Friendly Helper",
                description="Warm, approachable, and helpful for general customer service",
                voice_characteristics=self.voices["hi-IN-SwaraNeural"],
                personality_traits={
                    "authority": 0.5,
                    "warmth": 0.9,
                    "enthusiasm": 0.8,
                    "patience": 0.9,
                    "expertise": 0.7
                },
                adaptation_rules={
                    "greetings": {"speaking_rate": 0.95, "pitch": 0.1},
                    "complaints": {"speaking_rate": 0.85, "pitch": -0.05},
                    "general_inquiry": {"speaking_rate": 0.9, "pitch": 0.05}
                }
            ),
            
            # Technical expert personality
            VoicePersonalityProfile(
                profile_id="technical_expert",
                name="Technical Expert",
                description="Precise, knowledgeable, and methodical for technical support",
                voice_characteristics=self.voices["en-IN-NeerjaNeural"],
                personality_traits={
                    "authority": 0.8,
                    "warmth": 0.5,
                    "enthusiasm": 0.3,
                    "patience": 0.7,
                    "expertise": 0.95
                },
                adaptation_rules={
                    "technical_explanations": {"speaking_rate": 0.75, "pitch": -0.05},
                    "safety_instructions": {"speaking_rate": 0.7, "volume": 0.1},
                    "troubleshooting": {"speaking_rate": 0.8, "pitch": 0.0}
                }
            ),
            
            # Empathetic supporter personality
            VoicePersonalityProfile(
                profile_id="empathetic_supporter",
                name="Empathetic Supporter", 
                description="Understanding, caring, and supportive for complaint handling",
                voice_characteristics=self.voices["hi-IN-SwaraNeural"],
                personality_traits={
                    "authority": 0.4,
                    "warmth": 0.95,
                    "enthusiasm": 0.5,
                    "patience": 0.95,
                    "expertise": 0.6
                },
                adaptation_rules={
                    "complaints": {"speaking_rate": 0.8, "pitch": -0.1, "volume": -0.1},
                    "apologies": {"speaking_rate": 0.75, "pitch": -0.15},
                    "reassurance": {"speaking_rate": 0.85, "pitch": 0.0}
                }
            ),
            
            # Enthusiastic sales personality
            VoicePersonalityProfile(
                profile_id="enthusiastic_sales",
                name="Enthusiastic Sales",
                description="Energetic, persuasive, and engaging for product promotion",
                voice_characteristics=self.voices["hi-IN-MadhurNeural"],
                personality_traits={
                    "authority": 0.7,
                    "warmth": 0.8,
                    "enthusiasm": 0.9,
                    "patience": 0.6,
                    "expertise": 0.8
                },
                adaptation_rules={
                    "product_features": {"speaking_rate": 1.0, "pitch": 0.1},
                    "promotions": {"speaking_rate": 1.05, "pitch": 0.15, "volume": 0.1},
                    "closing_deals": {"speaking_rate": 0.9, "pitch": 0.05}
                }
            )
        ]
        
        for profile in profiles:
            self.personalities[profile.profile_id] = profile
    
    def get_voice(self, voice_id: str) -> Optional[VoiceCharacteristics]:
        """Get voice characteristics by ID"""
        return self.voices.get(voice_id)
    
    def get_personality(self, profile_id: str) -> Optional[VoicePersonalityProfile]:
        """Get personality profile by ID"""
        return self.personalities.get(profile_id)
    
    def list_voices_by_language(self, language_code: str) -> List[VoiceCharacteristics]:
        """Get all voices for a specific language"""
        return [voice for voice in self.voices.values() if voice.language_code == language_code]
    
    def list_personalities_by_context(self, business_context: BusinessContext) -> List[VoicePersonalityProfile]:
        """Get personalities suitable for business context"""
        suitable_profiles = []
        
        for profile in self.personalities.values():
            voice = profile.voice_characteristics
            suitability = voice.business_suitability.get(business_context, 0.0)
            
            if suitability > 0.5:  # Minimum suitability threshold
                suitable_profiles.append(profile)
        
        # Sort by suitability score
        suitable_profiles.sort(
            key=lambda p: p.voice_characteristics.business_suitability.get(business_context, 0.0),
            reverse=True
        )
        
        return suitable_profiles

class VoiceAdaptationEngine:
    """Core engine for voice personality adaptation"""
    
    def __init__(self):
        self.voice_library = VoiceLibrary()
        
        # Adaptation history
        self.adaptation_history = deque(maxlen=1000)
        
        # User voice preferences
        self.user_voice_preferences = {}  # User ID -> Preferences
        
        # Performance tracking
        self.adaptation_stats = {
            'total_adaptations': 0,
            'personality_usage': defaultdict(int),
            'context_adaptations': defaultdict(int),
            'user_satisfaction_scores': deque(maxlen=100)
        }
        
        # Threading
        self._lock = threading.RLock()
        
        log_info("🎭 Voice Adaptation Engine initialized")
    
    @monitor_performance("voice_personality_engine")
    async def select_optimal_voice(self, context: VoiceAdaptationContext, user_id: str = None) -> Dict[str, Any]:
        """Select optimal voice personality for given context"""
        
        start_time = time.time()
        
        try:
            # Get user preferences
            user_prefs = self.user_voice_preferences.get(user_id, {}) if user_id else {}
            
            # Analyze context requirements
            context_requirements = self._analyze_context_requirements(context)
            
            # Score all available personalities
            personality_scores = await self._score_personalities(context, context_requirements, user_prefs)
            
            # Select best personality
            selected_personality = self._select_best_personality(personality_scores)
            
            # Apply dynamic adaptations
            adapted_settings = self._apply_dynamic_adaptations(selected_personality, context)
            
            # Record adaptation decision
            adaptation_record = {
                'timestamp': datetime.now(),
                'user_id': user_id,
                'context': asdict(context),
                'selected_personality': selected_personality.profile_id,
                'adapted_settings': adapted_settings,
                'confidence_score': personality_scores[selected_personality.profile_id]['total_score']
            }
            
            with self._lock:
                self.adaptation_history.append(adaptation_record)
                self.adaptation_stats['total_adaptations'] += 1
                self.adaptation_stats['personality_usage'][selected_personality.profile_id] += 1
                self.adaptation_stats['context_adaptations'][context.business_context.value] += 1
            
            # Update personality usage stats
            selected_personality.usage_stats[context.business_context.value] = \
                selected_personality.usage_stats.get(context.business_context.value, 0) + 1
            selected_personality.last_used = datetime.now()
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                'personality_profile': asdict(selected_personality),
                'voice_settings': adapted_settings,
                'confidence_score': personality_scores[selected_personality.profile_id]['total_score'],
                'adaptation_reasons': personality_scores[selected_personality.profile_id]['reasons'],
                'processing_time_ms': processing_time,
                'voice_id': selected_personality.voice_characteristics.voice_id,
                'voice_name': selected_personality.voice_characteristics.name
            }
            
        except Exception as e:
            log_error(f"Voice adaptation failed: {e}")
            
            # Fallback to default voice
            default_personality = self.voice_library.personalities.get("friendly_helper")
            if default_personality:
                return {
                    'personality_profile': asdict(default_personality),
                    'voice_settings': self._get_default_settings(default_personality.voice_characteristics),
                    'confidence_score': 0.5,
                    'adaptation_reasons': ['fallback_due_to_error'],
                    'processing_time_ms': (time.time() - start_time) * 1000,
                    'voice_id': default_personality.voice_characteristics.voice_id,
                    'voice_name': default_personality.voice_characteristics.name,
                    'error': str(e)
                }
            else:
                return {'error': f'Voice adaptation failed: {e}'}
    
    def _analyze_context_requirements(self, context: VoiceAdaptationContext) -> Dict[str, float]:
        """Analyze context to determine voice requirements"""
        
        requirements = {
            'formality_required': context.formality_required,
            'warmth_needed': 0.5,
            'authority_needed': 0.5,
            'enthusiasm_needed': 0.5,
            'patience_needed': 0.5,
            'expertise_needed': 0.5
        }
        
        # Adjust based on user mood
        mood = context.user_mood.lower()
        if mood == 'frustrated':
            requirements['warmth_needed'] = 0.9
            requirements['patience_needed'] = 0.95
            requirements['authority_needed'] = 0.3
        elif mood == 'urgent':
            requirements['authority_needed'] = 0.8
            requirements['enthusiasm_needed'] = 0.7
        elif mood == 'curious':
            requirements['expertise_needed'] = 0.8
            requirements['patience_needed'] = 0.8
        elif mood == 'positive':
            requirements['enthusiasm_needed'] = 0.8
            requirements['warmth_needed'] = 0.8
        
        # Adjust based on business context
        business_context = context.business_context
        if business_context == BusinessContext.TECHNICAL_SUPPORT:
            requirements['expertise_needed'] = 0.9
            requirements['authority_needed'] = 0.8
            requirements['patience_needed'] = 0.8
        elif business_context == BusinessContext.COMPLAINT_HANDLING:
            requirements['warmth_needed'] = 0.95
            requirements['patience_needed'] = 0.95
            requirements['authority_needed'] = 0.4
        elif business_context == BusinessContext.PRICE_NEGOTIATION:
            requirements['authority_needed'] = 0.8
            requirements['expertise_needed'] = 0.8
            requirements['enthusiasm_needed'] = 0.6
        elif business_context == BusinessContext.GREETING:
            requirements['warmth_needed'] = 0.9
            requirements['enthusiasm_needed'] = 0.7
        
        # Adjust based on conversation state
        conv_state = context.conversation_state.lower()
        if conv_state == 'clarification':
            requirements['patience_needed'] = 0.9
            requirements['expertise_needed'] = 0.8
        elif conv_state == 'closing':
            requirements['warmth_needed'] = 0.8
            requirements['formality_required'] = 0.7
        
        return requirements
    
    async def _score_personalities(self, 
                                 context: VoiceAdaptationContext,
                                 requirements: Dict[str, float],
                                 user_prefs: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Score all personalities against context requirements"""
        
        scores = {}
        
        for personality_id, personality in self.voice_library.personalities.items():
            score_details = {
                'trait_alignment': 0.0,
                'context_suitability': 0.0,
                'user_preference': 0.0,
                'cultural_fit': 0.0,
                'usage_history': 0.0,
                'total_score': 0.0,
                'reasons': []
            }
            
            # Score trait alignment
            trait_score = 0.0
            trait_count = 0
            
            for trait, required_level in requirements.items():
                if trait.endswith('_needed'):
                    trait_name = trait.replace('_needed', '')
                elif trait.endswith('_required'):
                    trait_name = trait.replace('_required', 'formality')
                else:
                    continue
                
                personality_trait_level = personality.personality_traits.get(trait_name, 0.5)
                
                # Calculate alignment score (closer to requirement = higher score)
                alignment = 1.0 - abs(personality_trait_level - required_level)
                trait_score += alignment
                trait_count += 1
            
            if trait_count > 0:
                score_details['trait_alignment'] = trait_score / trait_count
            
            # Score business context suitability
            voice_char = personality.voice_characteristics
            context_suitability = voice_char.business_suitability.get(context.business_context, 0.5)
            score_details['context_suitability'] = context_suitability
            
            # Score user preferences
            user_pref_score = 0.5  # Default neutral
            if user_prefs:
                # Check gender preference
                if 'preferred_gender' in user_prefs:
                    if voice_char.gender.value == user_prefs['preferred_gender']:
                        user_pref_score += 0.2
                
                # Check age preference
                if 'preferred_age' in user_prefs:
                    if voice_char.age.value == user_prefs['preferred_age']:
                        user_pref_score += 0.15
                
                # Check formality preference
                if 'preferred_formality' in user_prefs:
                    formality_diff = abs(voice_char.formality_level - user_prefs['preferred_formality'])
                    user_pref_score += 0.15 * (1.0 - formality_diff)
                
                # Check if user has used this personality before
                if 'previous_personalities' in user_prefs:
                    if personality_id in user_prefs['previous_personalities']:
                        user_pref_score += 0.1  # Slight bonus for familiarity
            
            score_details['user_preference'] = min(user_pref_score, 1.0)
            
            # Score cultural fit
            cultural_score = 0.5  # Default neutral
            if context.cultural_context:
                if context.cultural_context.lower() in voice_char.cultural_affinity:
                    cultural_score = 0.8
                    score_details['reasons'].append('cultural_match')
            
            score_details['cultural_fit'] = cultural_score
            
            # Score based on usage history (slight penalty for overused personalities)
            total_usage = sum(personality.usage_stats.values())
            if total_usage > 0:
                # Slight penalty for overused personalities to encourage variety
                usage_penalty = min(total_usage / 100.0, 0.2)  # Max 0.2 penalty
                score_details['usage_history'] = 1.0 - usage_penalty
            else:
                score_details['usage_history'] = 1.0  # No penalty for unused
            
            # Calculate weighted total score
            weights = {
                'trait_alignment': 0.35,
                'context_suitability': 0.30,
                'user_preference': 0.15,
                'cultural_fit': 0.10,
                'usage_history': 0.10
            }
            
            total_score = sum(score_details[component] * weights[component] 
                            for component in weights.keys())
            
            score_details['total_score'] = total_score
            
            # Add reasoning
            if score_details['trait_alignment'] > 0.8:
                score_details['reasons'].append('excellent_trait_match')
            if score_details['context_suitability'] > 0.8:
                score_details['reasons'].append('highly_suitable_for_context')
            if score_details['user_preference'] > 0.7:
                score_details['reasons'].append('matches_user_preferences')
            
            scores[personality_id] = score_details
        
        return scores
    
    def _select_best_personality(self, personality_scores: Dict[str, Dict[str, Any]]) -> VoicePersonalityProfile:
        """Select the best personality based on scores"""
        
        # Sort by total score
        sorted_personalities = sorted(
            personality_scores.items(),
            key=lambda x: x[1]['total_score'],
            reverse=True
        )
        
        if not sorted_personalities:
            # Fallback to default
            return self.voice_library.personalities["friendly_helper"]
        
        best_personality_id = sorted_personalities[0][0]
        
        # Add some randomness to avoid always selecting the same personality
        # If top 2 personalities are close in score (within 0.1), randomly pick one
        if (len(sorted_personalities) > 1 and 
            sorted_personalities[0][1]['total_score'] - sorted_personalities[1][1]['total_score'] < 0.1):
            
            # Randomly pick between top 2
            best_personality_id = random.choice([sorted_personalities[0][0], sorted_personalities[1][0]])
        
        return self.voice_library.personalities[best_personality_id]
    
    def _apply_dynamic_adaptations(self, 
                                 personality: VoicePersonalityProfile, 
                                 context: VoiceAdaptationContext) -> Dict[str, Any]:
        """Apply dynamic adaptations to voice settings based on context"""
        
        voice_char = personality.voice_characteristics
        
        # Start with base settings
        settings = {
            'voice_id': voice_char.voice_id,
            'speaking_rate': voice_char.speaking_rate,
            'pitch': voice_char.pitch,
            'volume': voice_char.volume,
            'language': voice_char.language_code,
            'emotion': 'neutral'
        }
        
        # Apply personality-specific rules
        adaptation_rules = personality.adaptation_rules
        
        # Apply context-specific adaptations
        business_context = context.business_context.value
        if business_context in adaptation_rules:
            rule_adaptations = adaptation_rules[business_context]
            for setting, adjustment in rule_adaptations.items():
                if setting in settings:
                    settings[setting] += adjustment
        
        # Apply mood-based adaptations
        mood = context.user_mood.lower()
        if mood == 'frustrated':
            settings['speaking_rate'] *= 0.9  # Speak slower
            settings['pitch'] -= 0.05  # Lower pitch for calmness
            settings['emotion'] = 'empathetic'
        elif mood == 'urgent':
            settings['speaking_rate'] *= 1.1  # Speak faster
            settings['volume'] += 0.05  # Slightly louder
            settings['emotion'] = 'professional'
        elif mood == 'positive':
            settings['pitch'] += 0.05  # Higher pitch for enthusiasm
            settings['emotion'] = 'cheerful'
        elif mood == 'curious':
            settings['speaking_rate'] *= 0.95  # Slightly slower for clarity
            settings['emotion'] = 'friendly'
        
        # Apply urgency adjustments
        if context.urgency_level > 0.7:
            settings['speaking_rate'] *= (1.0 + context.urgency_level * 0.2)
            settings['volume'] += context.urgency_level * 0.1
        
        # Apply formality adjustments
        formality_diff = context.formality_required - voice_char.formality_level
        if abs(formality_diff) > 0.2:
            if formality_diff > 0:  # Need more formality
                settings['speaking_rate'] *= 0.95
                settings['pitch'] -= 0.05
            else:  # Need less formality
                settings['speaking_rate'] *= 1.05
                settings['pitch'] += 0.05
        
        # Ensure settings are within reasonable bounds
        settings['speaking_rate'] = max(0.5, min(2.0, settings['speaking_rate']))
        settings['pitch'] = max(-0.5, min(0.5, settings['pitch']))
        settings['volume'] = max(-0.5, min(0.5, settings['volume']))
        
        return settings
    
    def _get_default_settings(self, voice_char: VoiceCharacteristics) -> Dict[str, Any]:
        """Get default settings for a voice"""
        return {
            'voice_id': voice_char.voice_id,
            'speaking_rate': voice_char.speaking_rate,
            'pitch': voice_char.pitch,
            'volume': voice_char.volume,
            'language': voice_char.language_code,
            'emotion': 'neutral'
        }
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Update user voice preferences"""
        with self._lock:
            if user_id not in self.user_voice_preferences:
                self.user_voice_preferences[user_id] = {}
            
            self.user_voice_preferences[user_id].update(preferences)
        
        log_info(f"🎛️ Updated voice preferences for user {user_id}")
    
    def record_user_feedback(self, user_id: str, personality_id: str, satisfaction_score: float):
        """Record user satisfaction feedback"""
        with self._lock:
            self.adaptation_stats['user_satisfaction_scores'].append({
                'user_id': user_id,
                'personality_id': personality_id,
                'score': satisfaction_score,
                'timestamp': datetime.now()
            })
        
        log_info(f"📝 Recorded user feedback: {satisfaction_score} for {personality_id}")
    
    def get_adaptation_analytics(self) -> Dict[str, Any]:
        """Get voice adaptation analytics"""
        with self._lock:
            # Calculate average satisfaction
            satisfaction_scores = [
                entry['score'] for entry in self.adaptation_stats['user_satisfaction_scores']
                if isinstance(entry, dict) and 'score' in entry
            ]
            
            avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0.0
            
            # Get personality performance
            personality_performance = {}
            for personality_id in self.voice_library.personalities.keys():
                personality_scores = [
                    entry['score'] for entry in self.adaptation_stats['user_satisfaction_scores']
                    if isinstance(entry, dict) and entry.get('personality_id') == personality_id
                ]
                
                personality_performance[personality_id] = {
                    'usage_count': self.adaptation_stats['personality_usage'][personality_id],
                    'avg_satisfaction': sum(personality_scores) / len(personality_scores) if personality_scores else 0.0,
                    'feedback_count': len(personality_scores)
                }
            
            return {
                'total_adaptations': self.adaptation_stats['total_adaptations'],
                'average_satisfaction': avg_satisfaction,
                'personality_usage': dict(self.adaptation_stats['personality_usage']),
                'context_adaptations': dict(self.adaptation_stats['context_adaptations']),
                'personality_performance': personality_performance,
                'total_users': len(self.user_voice_preferences),
                'recent_adaptations': len([
                    record for record in self.adaptation_history
                    if record['timestamp'] > datetime.now() - timedelta(hours=24)
                ])
            }
    
    def get_voice_recommendations(self, context: VoiceAdaptationContext) -> List[Dict[str, Any]]:
        """Get voice recommendations for given context"""
        
        try:
            # Get suitable personalities for context
            suitable_personalities = self.voice_library.list_personalities_by_context(context.business_context)
            
            recommendations = []
            for personality in suitable_personalities[:3]:  # Top 3 recommendations
                voice_char = personality.voice_characteristics
                suitability_score = voice_char.business_suitability.get(context.business_context, 0.0)
                
                recommendation = {
                    'personality_id': personality.profile_id,
                    'name': personality.name,
                    'description': personality.description,
                    'voice_name': voice_char.name,
                    'voice_id': voice_char.voice_id,
                    'suitability_score': suitability_score,
                    'traits': personality.personality_traits,
                    'language': voice_char.language_code,
                    'formality_level': voice_char.formality_level
                }
                
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            log_error(f"Failed to generate voice recommendations: {e}")
            return []

# Global instance
_voice_personality_engine = None

def get_voice_personality_engine() -> VoiceAdaptationEngine:
    """Get or create global voice personality engine"""
    global _voice_personality_engine
    if _voice_personality_engine is None:
        _voice_personality_engine = VoiceAdaptationEngine()
    return _voice_personality_engine

if __name__ == "__main__":
    # Test the voice personality engine
    async def test_voice_personality_engine():
        print("🧪 Testing Voice Personality Adaptation Engine")
        print("=" * 60)
        
        # Create engine
        engine = VoiceAdaptationEngine()
        
        # Test different contexts
        test_contexts = [
            # Technical support scenario
            VoiceAdaptationContext(
                user_mood="curious",
                conversation_state="inquiry",
                business_context=BusinessContext.TECHNICAL_SUPPORT,
                user_preferences={"preferred_gender": "female", "preferred_formality": 0.8},
                urgency_level=0.3,
                formality_required=0.8,
                cultural_context="indian"
            ),
            
            # Complaint handling scenario
            VoiceAdaptationContext(
                user_mood="frustrated",
                conversation_state="clarification",
                business_context=BusinessContext.COMPLAINT_HANDLING,
                urgency_level=0.7,
                formality_required=0.6,
                emotional_tone="empathetic"
            ),
            
            # Sales/greeting scenario
            VoiceAdaptationContext(
                user_mood="positive",
                conversation_state="greeting",
                business_context=BusinessContext.GREETING,
                urgency_level=0.2,
                formality_required=0.4,
                cultural_context="indian"
            ),
            
            # Price negotiation scenario
            VoiceAdaptationContext(
                user_mood="decisive",
                conversation_state="negotiation",
                business_context=BusinessContext.PRICE_NEGOTIATION,
                urgency_level=0.5,
                formality_required=0.7
            )
        ]
        
        print("\n🎭 Testing Voice Adaptation Scenarios:")
        
        for i, context in enumerate(test_contexts, 1):
            print(f"\n--- Scenario {i}: {context.business_context.value} ---")
            print(f"User Mood: {context.user_mood}")
            print(f"Conversation State: {context.conversation_state}")
            print(f"Formality Required: {context.formality_required}")
            print(f"Urgency Level: {context.urgency_level}")
            
            # Select optimal voice
            result = await engine.select_optimal_voice(context, user_id="test_user")
            
            if 'error' not in result:
                print(f"\n✅ Selected Voice: {result['voice_name']}")
                print(f"Personality: {result['personality_profile']['name']}")
                print(f"Confidence Score: {result['confidence_score']:.3f}")
                print(f"Processing Time: {result['processing_time_ms']:.1f}ms")
                
                # Show voice settings
                settings = result['voice_settings']
                print(f"Voice Settings:")
                print(f"  • Speaking Rate: {settings['speaking_rate']:.2f}")
                print(f"  • Pitch: {settings['pitch']:.2f}")
                print(f"  • Emotion: {settings['emotion']}")
                print(f"  • Language: {settings['language']}")
                
                # Show adaptation reasons
                if result['adaptation_reasons']:
                    print(f"Adaptation Reasons: {', '.join(result['adaptation_reasons'])}")
            else:
                print(f"❌ Error: {result['error']}")
        
        # Test user preferences
        print("\n👤 Testing User Preferences:")
        engine.update_user_preferences("test_user", {
            "preferred_gender": "female",
            "preferred_age": "middle",
            "preferred_formality": 0.7,
            "previous_personalities": ["friendly_helper", "technical_expert"]
        })
        
        # Test with updated preferences
        updated_result = await engine.select_optimal_voice(test_contexts[0], user_id="test_user")
        print(f"With User Preferences: {updated_result['voice_name']}")
        
        # Test voice recommendations
        print("\n📋 Voice Recommendations:")
        recommendations = engine.get_voice_recommendations(test_contexts[0])
        
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec['name']} ({rec['voice_name']})")
            print(f"     Suitability: {rec['suitability_score']:.2f}")
            print(f"     Traits: Authority={rec['traits'].get('authority', 0):.1f}, "
                  f"Warmth={rec['traits'].get('warmth', 0):.1f}")
        
        # Record some feedback
        print("\n📝 Recording User Feedback:")
        engine.record_user_feedback("test_user", "technical_expert", 4.5)
        engine.record_user_feedback("test_user", "friendly_helper", 4.8)
        engine.record_user_feedback("test_user", "professional_consultant", 4.2)
        
        # Get analytics
        print("\n📊 Voice Adaptation Analytics:")
        analytics = engine.get_adaptation_analytics()
        
        print(f"Total Adaptations: {analytics['total_adaptations']}")
        print(f"Average Satisfaction: {analytics['average_satisfaction']:.2f}")
        print(f"Total Users: {analytics['total_users']}")
        
        print("\nPersonality Usage:")
        for personality, count in analytics['personality_usage'].items():
            print(f"  • {personality}: {count} times")
        
        print("\nPersonality Performance:")
        for personality, perf in analytics['personality_performance'].items():
            if perf['feedback_count'] > 0:
                print(f"  • {personality}: {perf['avg_satisfaction']:.2f} avg satisfaction "
                      f"({perf['feedback_count']} feedback)")
        
        print("\n🧹 Test completed")
    
    # Run test
    asyncio.run(test_voice_personality_engine())