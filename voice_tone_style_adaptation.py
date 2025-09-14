#!/usr/bin/env python3
"""
Voice Tone & Style Adaptation System
Advanced voice personality adaptation based on conversation context, user sentiment, and business scenarios
"""

import time
import threading
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
from collections import defaultdict, deque
import asyncio

try:
    from logger import log_info, log_error, log_warning
except ImportError:
    def log_info(msg): print(f"INFO - {msg}")
    def log_error(msg): print(f"ERROR - {msg}")
    def log_warning(msg): print(f"WARNING - {msg}")

class VoicePersonality(Enum):
    """Voice personality types"""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    ENTHUSIASTIC = "enthusiastic"
    CALM = "calm"
    EMPATHETIC = "empathetic"
    CONFIDENT = "confident"
    WARM = "warm"
    AUTHORITATIVE = "authoritative"
    CHEERFUL = "cheerful"
    PATIENT = "patient"
    ENERGETIC = "energetic"
    SOPHISTICATED = "sophisticated"

class EmotionalState(Enum):
    """Emotional states for voice adaptation"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    EXCITED = "excited"
    CALM = "calm"
    FRUSTRATED = "frustrated"
    SURPRISED = "surprised"
    CONFIDENT = "confident"
    NERVOUS = "nervous"
    NEUTRAL = "neutral"

class BusinessScenario(Enum):
    """Business scenario types"""
    GREETING = "greeting"
    PRODUCT_INQUIRY = "product_inquiry"
    PRICE_NEGOTIATION = "price_negotiation"
    COMPLAINT_HANDLING = "complaint_handling"
    TECHNICAL_SUPPORT = "technical_support"
    ORDER_CONFIRMATION = "order_confirmation"
    THANK_YOU = "thank_you"
    CLOSING = "closing"
    UPSELLING = "upselling"
    FOLLOW_UP = "follow_up"

class VoiceIntensity(Enum):
    """Voice intensity levels"""
    SUBTLE = "subtle"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

@dataclass
class VoiceStyleProfile:
    """Comprehensive voice style profile"""
    personality: VoicePersonality
    emotional_state: EmotionalState
    business_scenario: BusinessScenario
    intensity: VoiceIntensity
    
    # SSML Parameters
    rate: float = 1.0  # Speech rate (0.5-2.0)
    pitch: str = "+0%"  # Pitch adjustment
    volume: str = "medium"  # Volume level
    emphasis_level: str = "moderate"  # Emphasis strength
    pause_duration: int = 300  # Pause duration in ms
    
    # Advanced parameters
    emotional_coloring: float = 0.5  # How much emotion to apply (0-1)
    formality_level: float = 0.5  # Formality (0=casual, 1=very formal)
    energy_level: float = 0.5  # Energy (0=low, 1=high)
    warmth_factor: float = 0.5  # Warmth (0=cold, 1=very warm)
    
    # Context-specific adjustments
    cultural_adaptation: Dict[str, Any] = None
    language_specific_params: Dict[str, Any] = None

@dataclass
class VoiceAdaptationResult:
    """Result of voice adaptation process"""
    original_text: str
    adapted_ssml: str
    voice_profile: VoiceStyleProfile
    adaptation_confidence: float
    processing_time: float
    applied_adaptations: List[str]
    metadata: Dict[str, Any]

class VoiceToneStyleAdaptation:
    """Advanced voice tone and style adaptation system"""
    
    def __init__(self):
        # Voice style mappings
        self.personality_mappings = self._initialize_personality_mappings()
        self.scenario_mappings = self._initialize_scenario_mappings()
        self.emotion_mappings = self._initialize_emotion_mappings()
        
        # Adaptation rules and weights
        self.adaptation_rules = self._initialize_adaptation_rules()
        
        # Context tracking
        self.user_voice_preferences = {}  # user_id -> preferences
        self.conversation_contexts = {}   # session_id -> context
        self.adaptation_history = deque(maxlen=1000)  # Recent adaptations
        
        # Performance metrics
        self.metrics = {
            "total_adaptations": 0,
            "personality_usage": defaultdict(int),
            "scenario_usage": defaultdict(int),
            "emotion_usage": defaultdict(int),
            "average_adaptation_time": 0.0,
            "user_satisfaction_scores": [],
            "adaptation_effectiveness": 0.0
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
        log_info("🎭 Voice Tone & Style Adaptation System initialized")
    
    def _initialize_personality_mappings(self) -> Dict[VoicePersonality, Dict[str, Any]]:
        """Initialize personality to voice parameter mappings"""
        
        return {
            VoicePersonality.PROFESSIONAL: {
                "rate": 0.95,
                "pitch": "+0%",
                "volume": "medium",
                "emphasis": "moderate",
                "pause_duration": 400,
                "formality_level": 0.8,
                "energy_level": 0.6,
                "warmth_factor": 0.4,
                "descriptors": ["clear", "articulate", "composed"]
            },
            
            VoicePersonality.FRIENDLY: {
                "rate": 1.05,
                "pitch": "+2%",
                "volume": "medium",
                "emphasis": "moderate",
                "pause_duration": 250,
                "formality_level": 0.3,
                "energy_level": 0.7,
                "warmth_factor": 0.8,
                "descriptors": ["warm", "approachable", "conversational"]
            },
            
            VoicePersonality.ENTHUSIASTIC: {
                "rate": 1.15,
                "pitch": "+5%",
                "volume": "loud",
                "emphasis": "strong",
                "pause_duration": 200,
                "formality_level": 0.2,
                "energy_level": 0.9,
                "warmth_factor": 0.7,
                "descriptors": ["energetic", "excited", "animated"]
            },
            
            VoicePersonality.CALM: {
                "rate": 0.85,
                "pitch": "-2%",
                "volume": "medium",
                "emphasis": "reduced",
                "pause_duration": 500,
                "formality_level": 0.5,
                "energy_level": 0.3,
                "warmth_factor": 0.6,
                "descriptors": ["soothing", "steady", "peaceful"]
            },
            
            VoicePersonality.EMPATHETIC: {
                "rate": 0.9,
                "pitch": "+1%",
                "volume": "soft",
                "emphasis": "gentle",
                "pause_duration": 400,
                "formality_level": 0.4,
                "energy_level": 0.5,
                "warmth_factor": 0.9,
                "descriptors": ["understanding", "caring", "supportive"]
            },
            
            VoicePersonality.CONFIDENT: {
                "rate": 1.0,
                "pitch": "+3%",
                "volume": "loud",
                "emphasis": "strong",
                "pause_duration": 300,
                "formality_level": 0.6,
                "energy_level": 0.8,
                "warmth_factor": 0.5,
                "descriptors": ["assured", "decisive", "strong"]
            },
            
            VoicePersonality.WARM: {
                "rate": 0.95,
                "pitch": "+2%",
                "volume": "medium",
                "emphasis": "gentle",
                "pause_duration": 350,
                "formality_level": 0.3,
                "energy_level": 0.6,
                "warmth_factor": 0.95,
                "descriptors": ["affectionate", "caring", "nurturing"]
            },
            
            VoicePersonality.AUTHORITATIVE: {
                "rate": 0.9,
                "pitch": "-1%",
                "volume": "loud",
                "emphasis": "strong",
                "pause_duration": 400,
                "formality_level": 0.9,
                "energy_level": 0.7,
                "warmth_factor": 0.3,
                "descriptors": ["commanding", "expert", "decisive"]
            },
            
            VoicePersonality.CHEERFUL: {
                "rate": 1.1,
                "pitch": "+4%",
                "volume": "medium",
                "emphasis": "moderate",
                "pause_duration": 250,
                "formality_level": 0.2,
                "energy_level": 0.8,
                "warmth_factor": 0.8,
                "descriptors": ["upbeat", "positive", "joyful"]
            },
            
            VoicePersonality.PATIENT: {
                "rate": 0.8,
                "pitch": "+0%",
                "volume": "medium",
                "emphasis": "gentle",
                "pause_duration": 600,
                "formality_level": 0.5,
                "energy_level": 0.4,
                "warmth_factor": 0.7,
                "descriptors": ["tolerant", "understanding", "unhurried"]
            }
        }
    
    def _initialize_scenario_mappings(self) -> Dict[BusinessScenario, Dict[str, Any]]:
        """Initialize business scenario to voice parameter mappings"""
        
        return {
            BusinessScenario.GREETING: {
                "preferred_personalities": [VoicePersonality.FRIENDLY, VoicePersonality.WARM, VoicePersonality.CHEERFUL],
                "energy_boost": 0.2,
                "warmth_boost": 0.3,
                "formality_adjustment": -0.1,
                "special_phrases": ["Welcome", "Hello", "Good morning", "Great to see you"]
            },
            
            BusinessScenario.PRODUCT_INQUIRY: {
                "preferred_personalities": [VoicePersonality.PROFESSIONAL, VoicePersonality.CONFIDENT, VoicePersonality.FRIENDLY],
                "energy_boost": 0.1,
                "warmth_boost": 0.1,
                "formality_adjustment": 0.2,
                "special_phrases": ["Let me help", "I'd recommend", "Perfect choice", "Excellent quality"]
            },
            
            BusinessScenario.PRICE_NEGOTIATION: {
                "preferred_personalities": [VoicePersonality.CONFIDENT, VoicePersonality.PROFESSIONAL, VoicePersonality.CALM],
                "energy_boost": 0.0,
                "warmth_boost": 0.0,
                "formality_adjustment": 0.3,
                "special_phrases": ["Fair price", "Best value", "Special offer", "Great deal"]
            },
            
            BusinessScenario.COMPLAINT_HANDLING: {
                "preferred_personalities": [VoicePersonality.EMPATHETIC, VoicePersonality.CALM, VoicePersonality.PATIENT],
                "energy_boost": -0.3,
                "warmth_boost": 0.4,
                "formality_adjustment": 0.1,
                "special_phrases": ["I understand", "I'm sorry", "Let me help", "We'll fix this"]
            },
            
            BusinessScenario.TECHNICAL_SUPPORT: {
                "preferred_personalities": [VoicePersonality.PATIENT, VoicePersonality.PROFESSIONAL, VoicePersonality.CONFIDENT],
                "energy_boost": -0.1,
                "warmth_boost": 0.2,
                "formality_adjustment": 0.2,
                "special_phrases": ["Step by step", "Let me explain", "Easy solution", "Don't worry"]
            },
            
            BusinessScenario.ORDER_CONFIRMATION: {
                "preferred_personalities": [VoicePersonality.PROFESSIONAL, VoicePersonality.CONFIDENT, VoicePersonality.FRIENDLY],
                "energy_boost": 0.1,
                "warmth_boost": 0.2,
                "formality_adjustment": 0.3,
                "special_phrases": ["Confirmed", "All set", "Perfect", "Thank you for ordering"]
            },
            
            BusinessScenario.THANK_YOU: {
                "preferred_personalities": [VoicePersonality.WARM, VoicePersonality.CHEERFUL, VoicePersonality.FRIENDLY],
                "energy_boost": 0.3,
                "warmth_boost": 0.4,
                "formality_adjustment": -0.2,
                "special_phrases": ["Thank you so much", "We appreciate", "Grateful", "Wonderful"]
            },
            
            BusinessScenario.UPSELLING: {
                "preferred_personalities": [VoicePersonality.ENTHUSIASTIC, VoicePersonality.CONFIDENT, VoicePersonality.FRIENDLY],
                "energy_boost": 0.3,
                "warmth_boost": 0.1,
                "formality_adjustment": 0.0,
                "special_phrases": ["Perfect addition", "Great upgrade", "You'll love", "Special offer"]
            }
        }
    
    def _initialize_emotion_mappings(self) -> Dict[EmotionalState, Dict[str, Any]]:
        """Initialize emotional state to voice parameter mappings"""
        
        return {
            EmotionalState.HAPPY: {
                "rate_modifier": 1.1,
                "pitch_modifier": "+3%",
                "volume_modifier": "medium",
                "emphasis_boost": 0.2,
                "energy_boost": 0.3,
                "warmth_boost": 0.2
            },
            
            EmotionalState.SAD: {
                "rate_modifier": 0.85,
                "pitch_modifier": "-3%",
                "volume_modifier": "soft",
                "emphasis_boost": -0.3,
                "energy_boost": -0.4,
                "warmth_boost": 0.1
            },
            
            EmotionalState.ANGRY: {
                "rate_modifier": 1.2,
                "pitch_modifier": "+2%",
                "volume_modifier": "loud",
                "emphasis_boost": 0.4,
                "energy_boost": 0.5,
                "warmth_boost": -0.3
            },
            
            EmotionalState.EXCITED: {
                "rate_modifier": 1.15,
                "pitch_modifier": "+5%",
                "volume_modifier": "loud",
                "emphasis_boost": 0.3,
                "energy_boost": 0.4,
                "warmth_boost": 0.2
            },
            
            EmotionalState.CALM: {
                "rate_modifier": 0.9,
                "pitch_modifier": "-1%",
                "volume_modifier": "medium",
                "emphasis_boost": -0.2,
                "energy_boost": -0.3,
                "warmth_boost": 0.2
            },
            
            EmotionalState.FRUSTRATED: {
                "rate_modifier": 1.0,
                "pitch_modifier": "+1%",
                "volume_modifier": "medium",
                "emphasis_boost": 0.1,
                "energy_boost": 0.2,
                "warmth_boost": -0.1
            },
            
            EmotionalState.CONFIDENT: {
                "rate_modifier": 1.0,
                "pitch_modifier": "+2%",
                "volume_modifier": "loud",
                "emphasis_boost": 0.3,
                "energy_boost": 0.3,
                "warmth_boost": 0.0
            },
            
            EmotionalState.NEUTRAL: {
                "rate_modifier": 1.0,
                "pitch_modifier": "+0%",
                "volume_modifier": "medium",
                "emphasis_boost": 0.0,
                "energy_boost": 0.0,
                "warmth_boost": 0.0
            }
        }
    
    def _initialize_adaptation_rules(self) -> Dict[str, Any]:
        """Initialize adaptation rules and weights"""
        
        return {
            "personality_weight": 0.4,
            "scenario_weight": 0.3,
            "emotion_weight": 0.2,
            "user_preference_weight": 0.1,
            
            "min_adaptation_confidence": 0.3,
            "max_rate_change": 0.5,  # Maximum rate change from baseline
            "max_pitch_change": 10,  # Maximum pitch change in %
            "adaptation_smoothing": 0.7,  # How much to smooth between adaptations
            
            "cultural_adaptations": {
                "hi": {  # Hindi/Indian cultural adaptations
                    "formality_boost": 0.2,
                    "warmth_boost": 0.1,
                    "respect_markers": ["ji", "sahab", "madam"],
                    "pause_extension": 100
                },
                "es": {  # Spanish cultural adaptations
                    "warmth_boost": 0.3,
                    "energy_boost": 0.1,
                    "friendly_markers": ["amigo", "señor", "señora"]
                },
                "fr": {  # French cultural adaptations
                    "formality_boost": 0.3,
                    "sophistication_boost": 0.2,
                    "elegant_markers": ["monsieur", "madame", "s'il vous plaît"]
                }
            }
        }
    
    async def adapt_voice_style(self, text: str, context: Dict[str, Any], 
                              user_id: Optional[str] = None,
                              session_id: Optional[str] = None) -> VoiceAdaptationResult:
        """Adapt voice style based on comprehensive context analysis"""
        
        start_time = time.time()
        
        try:
            # Step 1: Analyze context and determine optimal voice profile
            voice_profile = await self._analyze_and_create_voice_profile(text, context, user_id, session_id)
            
            # Step 2: Generate adapted SSML
            adapted_ssml = await self._generate_adapted_ssml(text, voice_profile, context)
            
            # Step 3: Calculate adaptation confidence
            confidence = self._calculate_adaptation_confidence(voice_profile, context)
            
            # Step 4: Track applied adaptations
            applied_adaptations = self._get_applied_adaptations(voice_profile)
            
            processing_time = time.time() - start_time
            
            # Create result
            result = VoiceAdaptationResult(
                original_text=text,
                adapted_ssml=adapted_ssml,
                voice_profile=voice_profile,
                adaptation_confidence=confidence,
                processing_time=processing_time,
                applied_adaptations=applied_adaptations,
                metadata={
                    "context": context,
                    "user_id": user_id,
                    "session_id": session_id,
                    "language": context.get("detected_language", "en")
                }
            )
            
            # Update metrics and history
            self._update_adaptation_metrics(result)
            self._store_adaptation_history(result)
            
            log_info(f"🎭 Voice adapted: {voice_profile.personality.value} style "
                    f"({confidence:.2f} confidence, {processing_time*1000:.1f}ms)")
            
            return result
            
        except Exception as e:
            log_error(f"Voice adaptation failed: {e}")
            processing_time = time.time() - start_time
            
            return VoiceAdaptationResult(
                original_text=text,
                adapted_ssml=f'<speak>{text}</speak>',  # Basic SSML fallback
                voice_profile=self._get_default_voice_profile(),
                adaptation_confidence=0.0,
                processing_time=processing_time,
                applied_adaptations=[],
                metadata={"error": str(e)}
            )
    
    async def _analyze_and_create_voice_profile(self, text: str, context: Dict[str, Any],
                                              user_id: Optional[str], session_id: Optional[str]) -> VoiceStyleProfile:
        """Analyze context and create optimal voice style profile"""
        
        # Step 1: Determine business scenario
        scenario = self._detect_business_scenario(text, context)
        
        # Step 2: Detect emotional state
        emotional_state = self._detect_emotional_state(text, context)
        
        # Step 3: Select optimal personality
        personality = self._select_optimal_personality(scenario, emotional_state, context, user_id)
        
        # Step 4: Determine intensity level
        intensity = self._calculate_voice_intensity(context, emotional_state)
        
        # Step 5: Create base profile
        base_profile = VoiceStyleProfile(
            personality=personality,
            emotional_state=emotional_state,
            business_scenario=scenario,
            intensity=intensity
        )
        
        # Step 6: Apply personality-based parameters
        self._apply_personality_parameters(base_profile)
        
        # Step 7: Apply scenario-based adjustments
        self._apply_scenario_adjustments(base_profile, scenario)
        
        # Step 8: Apply emotional adjustments
        self._apply_emotional_adjustments(base_profile, emotional_state)
        
        # Step 9: Apply user preferences
        if user_id:
            self._apply_user_preferences(base_profile, user_id)
        
        # Step 10: Apply cultural adaptations
        language = context.get("detected_language", "en")
        self._apply_cultural_adaptations(base_profile, language)
        
        # Step 11: Smooth and validate parameters
        self._validate_and_smooth_parameters(base_profile)
        
        return base_profile
    
    def _detect_business_scenario(self, text: str, context: Dict[str, Any]) -> BusinessScenario:
        """Detect the business scenario from text and context"""
        
        text_lower = text.lower()
        
        # Intent-based detection
        intent = context.get("intent", "general")
        
        scenario_mappings = {
            "greeting": BusinessScenario.GREETING,
            "product_inquiry": BusinessScenario.PRODUCT_INQUIRY,
            "price_inquiry": BusinessScenario.PRICE_NEGOTIATION,
            "complaint": BusinessScenario.COMPLAINT_HANDLING,
            "problem": BusinessScenario.COMPLAINT_HANDLING,
            "technical": BusinessScenario.TECHNICAL_SUPPORT,
            "help": BusinessScenario.TECHNICAL_SUPPORT,
            "order": BusinessScenario.ORDER_CONFIRMATION,
            "confirmation": BusinessScenario.ORDER_CONFIRMATION,
            "thanks": BusinessScenario.THANK_YOU,
            "appreciation": BusinessScenario.THANK_YOU,
            "goodbye": BusinessScenario.CLOSING,
            "closing": BusinessScenario.CLOSING
        }
        
        if intent in scenario_mappings:
            return scenario_mappings[intent]
        
        # Keyword-based detection
        scenario_keywords = {
            BusinessScenario.GREETING: ["hello", "hi", "good morning", "welcome", "namaste", "hola"],
            BusinessScenario.PRODUCT_INQUIRY: ["product", "item", "switch", "wire", "cable", "fan", "bulb"],
            BusinessScenario.PRICE_NEGOTIATION: ["price", "cost", "rate", "charge", "kitna", "cuanto"],
            BusinessScenario.COMPLAINT_HANDLING: ["problem", "issue", "complaint", "wrong", "broken", "not working"],
            BusinessScenario.TECHNICAL_SUPPORT: ["how to", "installation", "setup", "connect", "wire", "install"],
            BusinessScenario.THANK_YOU: ["thank", "thanks", "grateful", "appreciate", "dhanyawad", "gracias"],
            BusinessScenario.CLOSING: ["bye", "goodbye", "see you", "take care", "alvida"]
        }
        
        for scenario, keywords in scenario_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return scenario
        
        return BusinessScenario.PRODUCT_INQUIRY  # Default
    
    def _detect_emotional_state(self, text: str, context: Dict[str, Any]) -> EmotionalState:
        """Detect emotional state from text and context"""
        
        # Use sentiment from context if available
        sentiment = context.get("sentiment", "neutral")
        
        sentiment_emotion_mapping = {
            "positive": EmotionalState.HAPPY,
            "negative": EmotionalState.SAD,
            "neutral": EmotionalState.NEUTRAL
        }
        
        if sentiment in sentiment_emotion_mapping:
            base_emotion = sentiment_emotion_mapping[sentiment]
        else:
            base_emotion = EmotionalState.NEUTRAL
        
        # Refine based on text analysis
        text_lower = text.lower()
        
        emotion_keywords = {
            EmotionalState.EXCITED: ["excited", "amazing", "fantastic", "wow", "great", "excellent"],
            EmotionalState.FRUSTRATED: ["frustrated", "annoying", "problem", "issue", "not working"],
            EmotionalState.ANGRY: ["angry", "mad", "terrible", "awful", "hate"],
            EmotionalState.HAPPY: ["happy", "pleased", "satisfied", "good", "wonderful"],
            EmotionalState.CALM: ["okay", "fine", "alright", "peaceful", "relaxed"]
        }
        
        # Check for emotional keywords
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return emotion
        
        return base_emotion
    
    def _select_optimal_personality(self, scenario: BusinessScenario, emotional_state: EmotionalState,
                                  context: Dict[str, Any], user_id: Optional[str]) -> VoicePersonality:
        """Select optimal voice personality based on context"""
        
        # Get scenario preferences
        scenario_mapping = self.scenario_mappings.get(scenario, {})
        preferred_personalities = scenario_mapping.get("preferred_personalities", [])
        
        # Consider emotional state
        emotion_personality_mapping = {
            EmotionalState.HAPPY: [VoicePersonality.CHEERFUL, VoicePersonality.ENTHUSIASTIC, VoicePersonality.WARM],
            EmotionalState.SAD: [VoicePersonality.EMPATHETIC, VoicePersonality.CALM, VoicePersonality.PATIENT],
            EmotionalState.ANGRY: [VoicePersonality.CALM, VoicePersonality.EMPATHETIC, VoicePersonality.PATIENT],
            EmotionalState.EXCITED: [VoicePersonality.ENTHUSIASTIC, VoicePersonality.ENERGETIC, VoicePersonality.CHEERFUL],
            EmotionalState.FRUSTRATED: [VoicePersonality.PATIENT, VoicePersonality.EMPATHETIC, VoicePersonality.CALM],
            EmotionalState.CONFIDENT: [VoicePersonality.CONFIDENT, VoicePersonality.PROFESSIONAL, VoicePersonality.AUTHORITATIVE]
        }
        
        emotion_preferences = emotion_personality_mapping.get(emotional_state, [])
        
        # Check user preferences
        user_preferences = []
        if user_id and user_id in self.user_voice_preferences:
            user_prefs = self.user_voice_preferences[user_id]
            user_preferences = user_prefs.get("preferred_personalities", [])
        
        # Combine preferences with weights
        personality_scores = defaultdict(float)
        
        # Scenario-based scoring (40% weight)
        for personality in preferred_personalities:
            personality_scores[personality] += 0.4
        
        # Emotion-based scoring (30% weight)
        for personality in emotion_preferences:
            personality_scores[personality] += 0.3
        
        # User preference scoring (30% weight)
        for personality in user_preferences:
            personality_scores[personality] += 0.3
        
        # Select highest scoring personality
        if personality_scores:
            best_personality = max(personality_scores.items(), key=lambda x: x[1])[0]
            return best_personality
        
        # Fallback based on scenario
        if preferred_personalities:
            return preferred_personalities[0]
        
        return VoicePersonality.FRIENDLY  # Default fallback
    
    def _calculate_voice_intensity(self, context: Dict[str, Any], emotional_state: EmotionalState) -> VoiceIntensity:
        """Calculate appropriate voice intensity level"""
        
        # Base intensity on emotional state
        emotion_intensity_mapping = {
            EmotionalState.EXCITED: VoiceIntensity.STRONG,
            EmotionalState.ANGRY: VoiceIntensity.VERY_STRONG,
            EmotionalState.HAPPY: VoiceIntensity.MODERATE,
            EmotionalState.SAD: VoiceIntensity.SUBTLE,
            EmotionalState.FRUSTRATED: VoiceIntensity.MODERATE,
            EmotionalState.CALM: VoiceIntensity.SUBTLE,
            EmotionalState.CONFIDENT: VoiceIntensity.STRONG,
            EmotionalState.NEUTRAL: VoiceIntensity.MODERATE
        }
        
        base_intensity = emotion_intensity_mapping.get(emotional_state, VoiceIntensity.MODERATE)
        
        # Adjust based on context confidence
        confidence = context.get("confidence", 0.5)
        if confidence < 0.3:
            # Lower intensity for low confidence contexts
            intensity_downgrade = {
                VoiceIntensity.VERY_STRONG: VoiceIntensity.STRONG,
                VoiceIntensity.STRONG: VoiceIntensity.MODERATE,
                VoiceIntensity.MODERATE: VoiceIntensity.SUBTLE,
                VoiceIntensity.SUBTLE: VoiceIntensity.SUBTLE
            }
            return intensity_downgrade.get(base_intensity, base_intensity)
        
        return base_intensity
    
    def _apply_personality_parameters(self, profile: VoiceStyleProfile):
        """Apply personality-based voice parameters"""
        
        personality_params = self.personality_mappings.get(profile.personality, {})
        
        profile.rate = personality_params.get("rate", 1.0)
        profile.pitch = personality_params.get("pitch", "+0%")
        profile.volume = personality_params.get("volume", "medium")
        profile.pause_duration = personality_params.get("pause_duration", 300)
        profile.formality_level = personality_params.get("formality_level", 0.5)
        profile.energy_level = personality_params.get("energy_level", 0.5)
        profile.warmth_factor = personality_params.get("warmth_factor", 0.5)
    
    def _apply_scenario_adjustments(self, profile: VoiceStyleProfile, scenario: BusinessScenario):
        """Apply business scenario-specific adjustments"""
        
        scenario_params = self.scenario_mappings.get(scenario, {})
        
        # Apply boosts
        energy_boost = scenario_params.get("energy_boost", 0)
        warmth_boost = scenario_params.get("warmth_boost", 0)
        formality_adjustment = scenario_params.get("formality_adjustment", 0)
        
        profile.energy_level = max(0, min(1, profile.energy_level + energy_boost))
        profile.warmth_factor = max(0, min(1, profile.warmth_factor + warmth_boost))
        profile.formality_level = max(0, min(1, profile.formality_level + formality_adjustment))
    
    def _apply_emotional_adjustments(self, profile: VoiceStyleProfile, emotional_state: EmotionalState):
        """Apply emotional state-based adjustments"""
        
        emotion_params = self.emotion_mappings.get(emotional_state, {})
        
        # Apply rate modifier
        rate_modifier = emotion_params.get("rate_modifier", 1.0)
        profile.rate *= rate_modifier
        
        # Apply pitch modifier (combine with existing pitch)
        pitch_modifier = emotion_params.get("pitch_modifier", "+0%")
        if pitch_modifier != "+0%":
            # Simple pitch combination (would need more sophisticated logic in production)
            profile.pitch = pitch_modifier
        
        # Apply volume modifier
        volume_modifier = emotion_params.get("volume_modifier")
        if volume_modifier:
            profile.volume = volume_modifier
        
        # Apply energy and warmth boosts
        energy_boost = emotion_params.get("energy_boost", 0)
        warmth_boost = emotion_params.get("warmth_boost", 0)
        
        profile.energy_level = max(0, min(1, profile.energy_level + energy_boost))
        profile.warmth_factor = max(0, min(1, profile.warmth_factor + warmth_boost))
        
        # Adjust emotional coloring
        profile.emotional_coloring = min(1.0, profile.emotional_coloring + abs(energy_boost) + abs(warmth_boost))
    
    def _apply_user_preferences(self, profile: VoiceStyleProfile, user_id: str):
        """Apply user-specific voice preferences"""
        
        if user_id not in self.user_voice_preferences:
            return
        
        user_prefs = self.user_voice_preferences[user_id]
        
        # Apply preference-based adjustments
        if "rate_preference" in user_prefs:
            profile.rate *= user_prefs["rate_preference"]
        
        if "energy_preference" in user_prefs:
            profile.energy_level = max(0, min(1, profile.energy_level + user_prefs["energy_preference"]))
        
        if "warmth_preference" in user_prefs:
            profile.warmth_factor = max(0, min(1, profile.warmth_factor + user_prefs["warmth_preference"]))
        
        if "formality_preference" in user_prefs:
            profile.formality_level = max(0, min(1, profile.formality_level + user_prefs["formality_preference"]))
    
    def _apply_cultural_adaptations(self, profile: VoiceStyleProfile, language: str):
        """Apply language/culture-specific adaptations"""
        
        cultural_rules = self.adaptation_rules.get("cultural_adaptations", {})
        
        if language in cultural_rules:
            cultural_params = cultural_rules[language]
            
            # Apply cultural adjustments
            if "formality_boost" in cultural_params:
                profile.formality_level = max(0, min(1, profile.formality_level + cultural_params["formality_boost"]))
            
            if "warmth_boost" in cultural_params:
                profile.warmth_factor = max(0, min(1, profile.warmth_factor + cultural_params["warmth_boost"]))
            
            if "pause_extension" in cultural_params:
                profile.pause_duration += cultural_params["pause_extension"]
            
            # Store cultural context
            profile.cultural_adaptation = cultural_params
            profile.language_specific_params = {"language": language}
    
    def _validate_and_smooth_parameters(self, profile: VoiceStyleProfile):
        """Validate and smooth voice parameters to ensure they're within acceptable ranges"""
        
        rules = self.adaptation_rules
        
        # Clamp rate to acceptable range
        max_rate_change = rules.get("max_rate_change", 0.5)
        profile.rate = max(0.5, min(2.0, profile.rate))
        profile.rate = max(1.0 - max_rate_change, min(1.0 + max_rate_change, profile.rate))
        
        # Validate pitch (extract numeric value and clamp)
        try:
            pitch_value = int(profile.pitch.replace("%", "").replace("+", ""))
            max_pitch_change = rules.get("max_pitch_change", 10)
            pitch_value = max(-max_pitch_change, min(max_pitch_change, pitch_value))
            profile.pitch = f"{'+' if pitch_value >= 0 else ''}{pitch_value}%"
        except:
            profile.pitch = "+0%"
        
        # Ensure volume is valid
        valid_volumes = ["silent", "x-soft", "soft", "medium", "loud", "x-loud"]
        if profile.volume not in valid_volumes:
            profile.volume = "medium"
        
        # Clamp other parameters
        profile.emotional_coloring = max(0.0, min(1.0, profile.emotional_coloring))
        profile.formality_level = max(0.0, min(1.0, profile.formality_level))
        profile.energy_level = max(0.0, min(1.0, profile.energy_level))
        profile.warmth_factor = max(0.0, min(1.0, profile.warmth_factor))
        
        # Ensure pause duration is reasonable
        profile.pause_duration = max(100, min(2000, profile.pause_duration))
    
    async def _generate_adapted_ssml(self, text: str, profile: VoiceStyleProfile, context: Dict[str, Any]) -> str:
        """Generate SSML with adaptive voice styling"""
        
        # Start SSML document
        ssml_parts = ['<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"']
        
        # Add language if available
        language = context.get("detected_language", "en")
        language_code = self._get_ssml_language_code(language)
        if language_code:
            ssml_parts.append(f' xml:lang="{language_code}"')
        
        ssml_parts.append('>')
        
        # Add voice selection if specific voice is preferred
        voice_selection = self._get_voice_selection(profile, context)
        if voice_selection:
            ssml_parts.append(f'<voice {voice_selection}>')
        
        # Add prosody controls
        prosody_attrs = []
        
        if profile.rate != 1.0:
            prosody_attrs.append(f'rate="{profile.rate}"')
        
        if profile.pitch != "+0%":
            prosody_attrs.append(f'pitch="{profile.pitch}"')
        
        if profile.volume != "medium":
            prosody_attrs.append(f'volume="{profile.volume}"')
        
        if prosody_attrs:
            ssml_parts.append(f'<prosody {" ".join(prosody_attrs)}>')
        
        # Process text with adaptive styling
        styled_text = self._apply_text_styling(text, profile, context)
        ssml_parts.append(styled_text)
        
        # Close prosody tag
        if prosody_attrs:
            ssml_parts.append('</prosody>')
        
        # Close voice tag
        if voice_selection:
            ssml_parts.append('</voice>')
        
        # Close speak tag
        ssml_parts.append('</speak>')
        
        return ''.join(ssml_parts)
    
    def _get_ssml_language_code(self, language: str) -> Optional[str]:
        """Get proper SSML language code"""
        
        language_mappings = {
            "en": "en-US",
            "hi": "hi-IN",
            "es": "es-ES",
            "fr": "fr-FR",
            "de": "de-DE",
            "it": "it-IT",
            "pt": "pt-PT",
            "ja": "ja-JP",
            "ko": "ko-KR",
            "zh": "zh-CN",
            "ar": "ar-SA",
            "ru": "ru-RU"
        }
        
        return language_mappings.get(language)
    
    def _get_voice_selection(self, profile: VoiceStyleProfile, context: Dict[str, Any]) -> Optional[str]:
        """Get voice selection attributes for SSML"""
        
        # This would integrate with the multilingual voice system
        # For now, return None to use default voice
        return None
    
    def _apply_text_styling(self, text: str, profile: VoiceStyleProfile, context: Dict[str, Any]) -> str:
        """Apply text-level styling based on voice profile"""
        
        styled_parts = []
        sentences = text.split('.')
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Add sentence with styling
            sentence_parts = []
            
            # Add emphasis for important words
            if profile.personality in [VoicePersonality.ENTHUSIASTIC, VoicePersonality.CONFIDENT]:
                sentence = self._add_emphasis_tags(sentence, profile)
            
            sentence_parts.append(sentence)
            
            # Add appropriate pause after sentence
            if i < len(sentences) - 1:  # Not the last sentence
                pause_ms = profile.pause_duration
                
                # Adjust pause based on personality
                if profile.personality == VoicePersonality.PATIENT:
                    pause_ms = int(pause_ms * 1.5)
                elif profile.personality == VoicePersonality.ENERGETIC:
                    pause_ms = int(pause_ms * 0.7)
                
                sentence_parts.append(f'<break time="{pause_ms}ms"/>')
            
            styled_parts.extend(sentence_parts)
        
        return ''.join(styled_parts)
    
    def _add_emphasis_tags(self, text: str, profile: VoiceStyleProfile) -> str:
        """Add SSML emphasis tags to important words"""
        
        # Words that often deserve emphasis in business context
        emphasis_words = {
            "excellent", "perfect", "great", "amazing", "best", "quality",
            "guarantee", "warranty", "special", "offer", "deal", "save",
            "important", "urgent", "critical", "essential", "required"
        }
        
        words = text.split()
        result_words = []
        
        for word in words:
            clean_word = word.lower().strip('.,!?')
            if clean_word in emphasis_words and profile.energy_level > 0.6:
                # Add emphasis based on personality
                if profile.personality == VoicePersonality.ENTHUSIASTIC:
                    result_words.append(f'<emphasis level="strong">{word}</emphasis>')
                else:
                    result_words.append(f'<emphasis level="moderate">{word}</emphasis>')
            else:
                result_words.append(word)
        
        return ' '.join(result_words)
    
    def _calculate_adaptation_confidence(self, profile: VoiceStyleProfile, context: Dict[str, Any]) -> float:
        """Calculate confidence score for the adaptation"""
        
        confidence_factors = []
        
        # Base confidence from context
        base_confidence = context.get("confidence", 0.5)
        confidence_factors.append(base_confidence * 0.3)
        
        # Personality match confidence
        personality_confidence = 0.8  # Assume good personality matching
        confidence_factors.append(personality_confidence * 0.3)
        
        # Scenario detection confidence
        scenario_confidence = 0.7  # Assume reasonable scenario detection
        confidence_factors.append(scenario_confidence * 0.2)
        
        # Emotional state confidence
        emotion_confidence = 0.6  # Moderate confidence in emotion detection
        confidence_factors.append(emotion_confidence * 0.2)
        
        # Combine confidence factors
        total_confidence = sum(confidence_factors)
        
        # Apply minimum confidence threshold
        min_confidence = self.adaptation_rules.get("min_adaptation_confidence", 0.3)
        return max(min_confidence, total_confidence)
    
    def _get_applied_adaptations(self, profile: VoiceStyleProfile) -> List[str]:
        """Get list of adaptations that were applied"""
        
        adaptations = []
        
        adaptations.append(f"personality:{profile.personality.value}")
        adaptations.append(f"emotion:{profile.emotional_state.value}")
        adaptations.append(f"scenario:{profile.business_scenario.value}")
        adaptations.append(f"intensity:{profile.intensity.value}")
        
        if profile.rate != 1.0:
            adaptations.append(f"rate_adjustment:{profile.rate:.2f}")
        
        if profile.pitch != "+0%":
            adaptations.append(f"pitch_adjustment:{profile.pitch}")
        
        if profile.volume != "medium":
            adaptations.append(f"volume_adjustment:{profile.volume}")
        
        if profile.cultural_adaptation:
            adaptations.append("cultural_adaptation")
        
        if profile.formality_level != 0.5:
            adaptations.append(f"formality:{profile.formality_level:.2f}")
        
        return adaptations
    
    def _get_default_voice_profile(self) -> VoiceStyleProfile:
        """Get default voice profile for fallback"""
        
        return VoiceStyleProfile(
            personality=VoicePersonality.FRIENDLY,
            emotional_state=EmotionalState.NEUTRAL,
            business_scenario=BusinessScenario.PRODUCT_INQUIRY,
            intensity=VoiceIntensity.MODERATE
        )
    
    def _update_adaptation_metrics(self, result: VoiceAdaptationResult):
        """Update performance metrics"""
        
        with self._lock:
            self.metrics["total_adaptations"] += 1
            
            # Update personality usage
            personality = result.voice_profile.personality
            self.metrics["personality_usage"][personality] += 1
            
            # Update scenario usage
            scenario = result.voice_profile.business_scenario
            self.metrics["scenario_usage"][scenario] += 1
            
            # Update emotion usage
            emotion = result.voice_profile.emotional_state
            self.metrics["emotion_usage"][emotion] += 1
            
            # Update average adaptation time
            total = self.metrics["total_adaptations"]
            current_avg = self.metrics["average_adaptation_time"]
            self.metrics["average_adaptation_time"] = \
                (current_avg * (total - 1) + result.processing_time) / total
    
    def _store_adaptation_history(self, result: VoiceAdaptationResult):
        """Store adaptation in history for analysis"""
        
        history_entry = {
            "timestamp": time.time(),
            "personality": result.voice_profile.personality.value,
            "emotion": result.voice_profile.emotional_state.value,
            "scenario": result.voice_profile.business_scenario.value,
            "confidence": result.adaptation_confidence,
            "processing_time": result.processing_time,
            "adaptations_count": len(result.applied_adaptations)
        }
        
        self.adaptation_history.append(history_entry)
    
    def learn_user_preferences(self, user_id: str, feedback: Dict[str, Any]):
        """Learn user voice preferences from feedback"""
        
        with self._lock:
            if user_id not in self.user_voice_preferences:
                self.user_voice_preferences[user_id] = {
                    "preferred_personalities": [],
                    "rate_preference": 1.0,
                    "energy_preference": 0.0,
                    "warmth_preference": 0.0,
                    "formality_preference": 0.0,
                    "feedback_count": 0
                }
            
            prefs = self.user_voice_preferences[user_id]
            prefs["feedback_count"] += 1
            
            # Update preferences based on feedback
            if "personality_rating" in feedback and feedback["personality_rating"] > 7:
                personality = feedback.get("personality")
                if personality and personality not in prefs["preferred_personalities"]:
                    prefs["preferred_personalities"].append(personality)
            
            # Adjust parameters based on feedback
            if "rate_feedback" in feedback:
                rate_adjustment = (feedback["rate_feedback"] - 5) * 0.02  # Scale -5 to +5 to -0.1 to +0.1
                prefs["rate_preference"] = max(0.5, min(1.5, prefs["rate_preference"] + rate_adjustment))
            
            if "energy_feedback" in feedback:
                energy_adjustment = (feedback["energy_feedback"] - 5) * 0.05
                prefs["energy_preference"] = max(-0.3, min(0.3, prefs["energy_preference"] + energy_adjustment))
            
            log_info(f"🎓 Updated voice preferences for user {user_id}: {prefs['feedback_count']} feedback entries")
    
    def get_adaptation_analytics(self) -> Dict[str, Any]:
        """Get comprehensive adaptation analytics"""
        
        with self._lock:
            # Recent adaptations analysis
            recent_adaptations = [entry for entry in self.adaptation_history 
                                if time.time() - entry["timestamp"] < 3600]  # Last hour
            
            # Personality popularity
            personality_stats = dict(self.metrics["personality_usage"])
            total_adaptations = sum(personality_stats.values())
            personality_percentages = {
                personality.value: (count / total_adaptations) * 100
                for personality, count in personality_stats.items()
            } if total_adaptations > 0 else {}
            
            # Performance metrics
            avg_confidence = sum(entry["confidence"] for entry in recent_adaptations) / \
                           len(recent_adaptations) if recent_adaptations else 0
            
            return {
                "overview": {
                    "total_adaptations": self.metrics["total_adaptations"],
                    "average_adaptation_time": self.metrics["average_adaptation_time"],
                    "recent_adaptations_1h": len(recent_adaptations),
                    "average_confidence": avg_confidence,
                    "users_with_preferences": len(self.user_voice_preferences)
                },
                "personality_usage": personality_percentages,
                "scenario_distribution": dict(self.metrics["scenario_usage"]),
                "emotion_distribution": dict(self.metrics["emotion_usage"]),
                "performance_metrics": {
                    "avg_processing_time_ms": self.metrics["average_adaptation_time"] * 1000,
                    "adaptation_effectiveness": self.metrics.get("adaptation_effectiveness", 0.0),
                    "user_satisfaction_avg": sum(self.metrics["user_satisfaction_scores"]) / 
                                          len(self.metrics["user_satisfaction_scores"]) 
                                          if self.metrics["user_satisfaction_scores"] else 0
                },
                "system_capabilities": {
                    "personalities_available": len(VoicePersonality),
                    "emotions_supported": len(EmotionalState),
                    "scenarios_supported": len(BusinessScenario),
                    "cultural_adaptations": len(self.adaptation_rules.get("cultural_adaptations", {}))
                }
            }
    
    def cleanup(self):
        """Clean up adaptation system resources"""
        
        with self._lock:
            # Clear old adaptation history
            current_time = time.time()
            cutoff_time = current_time - (7 * 24 * 3600)  # Keep last 7 days
            
            filtered_history = [entry for entry in self.adaptation_history 
                              if entry["timestamp"] > cutoff_time]
            
            self.adaptation_history.clear()
            self.adaptation_history.extend(filtered_history)
            
            log_info(f"✅ Voice adaptation system cleanup completed. "
                    f"History: {len(self.adaptation_history)} entries retained")

# Global instance
_voice_adaptation_system = None

def get_voice_adaptation_system() -> VoiceToneStyleAdaptation:
    """Get global voice adaptation system instance"""
    global _voice_adaptation_system
    if _voice_adaptation_system is None:
        _voice_adaptation_system = VoiceToneStyleAdaptation()
    return _voice_adaptation_system

if __name__ == "__main__":
    # Test the voice adaptation system
    import asyncio
    
    async def test_voice_adaptation():
        print("🎭 Testing Voice Tone & Style Adaptation")
        print("=" * 50)
        
        system = get_voice_adaptation_system()
        
        # Test different scenarios
        test_cases = [
            {
                "text": "Welcome to our electrical shop! How can I help you today?",
                "context": {
                    "intent": "greeting",
                    "sentiment": "positive",
                    "confidence": 0.9,
                    "detected_language": "en"
                },
                "scenario": "Greeting"
            },
            {
                "text": "I'm really sorry to hear about this problem. Let me help you fix it right away.",
                "context": {
                    "intent": "complaint",
                    "sentiment": "negative",
                    "confidence": 0.8,
                    "detected_language": "en"
                },
                "scenario": "Complaint Handling"
            },
            {
                "text": "This is an excellent choice! You'll absolutely love this premium switch.",
                "context": {
                    "intent": "product_inquiry",
                    "sentiment": "positive",
                    "confidence": 0.85,
                    "detected_language": "en"
                },
                "scenario": "Product Recommendation"
            },
            {
                "text": "धन्यवाद जी! आपकी सेवा करके खुशी हुई।",
                "context": {
                    "intent": "thanks",
                    "sentiment": "positive",
                    "confidence": 0.9,
                    "detected_language": "hi"
                },
                "scenario": "Thank You (Hindi)"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🎬 Test {i}: {test_case['scenario']}")
            print(f"Text: {test_case['text']}")
            
            # Adapt voice style
            result = await system.adapt_voice_style(
                test_case["text"],
                test_case["context"],
                user_id=f"test_user_{i % 2}"  # Alternate between 2 users
            )
            
            print(f"✅ Adaptation completed:")
            print(f"  • Personality: {result.voice_profile.personality.value}")
            print(f"  • Emotion: {result.voice_profile.emotional_state.value}")
            print(f"  • Scenario: {result.voice_profile.business_scenario.value}")
            print(f"  • Confidence: {result.adaptation_confidence:.2f}")
            print(f"  • Processing time: {result.processing_time*1000:.1f}ms")
            print(f"  • Adaptations: {len(result.applied_adaptations)}")
            
            # Show key voice parameters
            profile = result.voice_profile
            print(f"  • Voice params: rate={profile.rate:.2f}, pitch={profile.pitch}, "
                  f"volume={profile.volume}")
            print(f"  • Personality traits: energy={profile.energy_level:.2f}, "
                  f"warmth={profile.warmth_factor:.2f}, formality={profile.formality_level:.2f}")
            
            # Show SSML sample
            ssml_sample = result.adapted_ssml[:100] + "..." if len(result.adapted_ssml) > 100 else result.adapted_ssml
            print(f"  • SSML sample: {ssml_sample}")
            
            await asyncio.sleep(0.5)  # Brief pause between tests
        
        # Test user preference learning
        print(f"\n🎓 Testing User Preference Learning:")
        user_feedback = {
            "personality_rating": 8,
            "personality": VoicePersonality.ENTHUSIASTIC,
            "rate_feedback": 7,  # Slightly faster preferred
            "energy_feedback": 8   # Higher energy preferred
        }
        
        system.learn_user_preferences("test_user_1", user_feedback)
        print(f"✅ User preferences updated based on feedback")
        
        # Show analytics
        print(f"\n📊 Voice Adaptation Analytics:")
        analytics = system.get_adaptation_analytics()
        
        print(f"  • Total adaptations: {analytics['overview']['total_adaptations']}")
        print(f"  • Average confidence: {analytics['overview']['average_confidence']:.2f}")
        print(f"  • Average processing time: {analytics['performance_metrics']['avg_processing_time_ms']:.1f}ms")
        print(f"  • Users with preferences: {analytics['overview']['users_with_preferences']}")
        
        if analytics['personality_usage']:
            top_personalities = sorted(analytics['personality_usage'].items(), 
                                     key=lambda x: x[1], reverse=True)[:3]
            print(f"  • Top personalities: {', '.join([f'{p}({v:.1f}%)' for p, v in top_personalities])}")
        
        # Cleanup
        system.cleanup()
        print("\n✅ Voice Tone & Style Adaptation test completed")
    
    # Run the test
    asyncio.run(test_voice_adaptation())