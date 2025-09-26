#!/usr/bin/env python3
"""
Context-Aware Conversation Manager - Advanced Conversation Intelligence
Manages conversation context, memory, personality adaptation, and intelligent context switching
Optimized for natural, human-like conversations with business context awareness
"""

import asyncio
import json
import sqlite3
import time
import threading
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
from pathlib import Path
from enum import Enum
import hashlib
import re

from logger import log_info, log_error, log_warning
from performance_monitor import monitor_performance, MetricType, get_performance_monitor

class ConversationState(Enum):
    """Current state of conversation"""
    GREETING = "greeting"
    INQUIRY = "inquiry"
    DISCUSSION = "discussion"
    CLARIFICATION = "clarification"
    NEGOTIATION = "negotiation"
    CLOSING = "closing"
    FOLLOW_UP = "follow_up"

class UserMood(Enum):
    """Detected user mood/sentiment"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    FRUSTRATED = "frustrated"
    URGENT = "urgent"
    CURIOUS = "curious"
    DECISIVE = "decisive"

class PersonalityType(Enum):
    """Bot personality types"""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    TECHNICAL = "technical"
    CONSULTATIVE = "consultative"
    SUPPORTIVE = "supportive"

class ContextType(Enum):
    """Types of conversation context"""
    PERSONAL = "personal"         # User preferences, history
    BUSINESS = "business"         # Product/service context
    TECHNICAL = "technical"       # Technical specifications
    TRANSACTIONAL = "transactional"  # Pricing, orders
    RELATIONAL = "relational"     # Relationship building

@dataclass
class ConversationTurn:
    """Single conversation turn"""
    turn_id: str
    user_input: str
    bot_response: str
    timestamp: datetime
    language: str
    mood: UserMood
    state: ConversationState
    context_used: List[str]
    confidence: float
    processing_time_ms: float

@dataclass
class UserProfile:
    """User profile and preferences"""
    user_id: str
    name: Optional[str] = None
    preferred_language: str = "hi-en"
    communication_style: str = "friendly"
    business_context: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    interaction_history: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    last_interaction: Optional[datetime] = None
    total_interactions: int = 0

@dataclass
class ConversationContext:
    """Context information for conversation"""
    context_id: str
    context_type: ContextType
    data: Dict[str, Any]
    importance: float  # 0.0 - 1.0
    expiry_time: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    created_at: Optional[datetime] = None

@dataclass
class ConversationMemory:
    """Conversation memory structure"""
    memory_id: str
    content: str
    memory_type: str  # "fact", "preference", "context", "relationship"
    importance: float
    related_topics: List[str]
    created_at: datetime
    last_used: Optional[datetime] = None
    use_count: int = 0

class MoodDetector:
    """Detects user mood from conversation patterns"""
    
    def __init__(self):
        # Mood indicators
        self.mood_patterns = {
            UserMood.POSITIVE: [
                r'\b(?:good|great|excellent|perfect|amazing|wonderful|fantastic|nice|happy|pleased|satisfied)\b',
                r'\b(?:accha|badhiya|zabardast|superb|brilliant)\b',
                r'(?:thank|dhanyawad|shukriya)',
                r'(?:👍|😊|😃|😄|🙂|✅)'
            ],
            UserMood.FRUSTRATED: [
                r'\b(?:problem|issue|trouble|frustrated|annoyed|upset|disappointed|bad|terrible|awful)\b',
                r'\b(?:pareshani|takleef|problem|galat|bura)\b',
                r'\b(?:not working|doesn\'t work|broken|failed)\b',
                r'(?:😠|😡|😤|😫|😩|❌)'
            ],
            UserMood.URGENT: [
                r'\b(?:urgent|emergency|immediately|asap|quickly|fast|right now|urgent|turant)\b',
                r'\b(?:urgent|jaldi|abhi|turant|emergency)\b',
                r'(?:!!|!!!)',
                r'\b(?:help|madad|please|please help)\b.*(?:urgent|jaldi)'
            ],
            UserMood.CURIOUS: [
                r'\b(?:how|what|why|where|when|tell me|explain|kaise|kya|kyun|kahan|kab)\b',
                r'\b(?:interested|curious|want to know|batao|samjhao)\b',
                r'(?:\?.*\?|\?{2,})'
            ],
            UserMood.DECISIVE: [
                r'\b(?:want|need|buy|purchase|order|book|confirm|yes|han|definitely|sure)\b',
                r'\b(?:chahiye|lena hai|kharidna|book karna|confirm)\b',
                r'\b(?:decided|final|ok|done|go ahead)\b'
            ]
        }
        
        # Compile patterns
        self.compiled_patterns = {}
        for mood, patterns in self.mood_patterns.items():
            self.compiled_patterns[mood] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def detect_mood(self, text: str, context: Dict[str, Any] = None) -> Tuple[UserMood, float]:
        """Detect user mood from text"""
        mood_scores = defaultdict(float)
        
        # Pattern matching
        for mood, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                matches = len(pattern.findall(text))
                mood_scores[mood] += matches * 0.3
        
        # Context-based adjustments
        if context:
            # Previous mood influence
            if 'previous_mood' in context and context['previous_mood'] != UserMood.NEUTRAL.value:
                prev_mood = UserMood(context['previous_mood'])
                mood_scores[prev_mood] += 0.2
            
            # Response time influence
            if 'response_time' in context and context['response_time'] < 2.0:
                mood_scores[UserMood.URGENT] += 0.1
            
            # Conversation length influence
            if 'turn_count' in context and context['turn_count'] > 5:
                mood_scores[UserMood.FRUSTRATED] += 0.1
        
        # Text length and punctuation
        if len(text) > 100:
            mood_scores[UserMood.CURIOUS] += 0.1
        
        exclamation_count = text.count('!')
        if exclamation_count > 1:
            mood_scores[UserMood.URGENT] += 0.2
        elif exclamation_count == 1:
            mood_scores[UserMood.POSITIVE] += 0.1
        
        # Determine best mood
        if not mood_scores:
            return UserMood.NEUTRAL, 0.5
        
        best_mood = max(mood_scores, key=mood_scores.get)
        confidence = min(mood_scores[best_mood], 1.0)
        
        # Minimum confidence threshold
        if confidence < 0.3:
            return UserMood.NEUTRAL, 0.5
        
        return best_mood, confidence

class PersonalityAdapter:
    """Adapts bot personality based on context and user"""
    
    def __init__(self):
        self.personality_profiles = {
            PersonalityType.PROFESSIONAL: {
                "tone": "formal",
                "language_style": "business",
                "response_length": "concise",
                "emoji_usage": "minimal",
                "technical_level": "medium"
            },
            PersonalityType.FRIENDLY: {
                "tone": "warm",
                "language_style": "casual",
                "response_length": "conversational",
                "emoji_usage": "moderate",
                "technical_level": "low"
            },
            PersonalityType.TECHNICAL: {
                "tone": "precise",
                "language_style": "technical",
                "response_length": "detailed", 
                "emoji_usage": "none",
                "technical_level": "high"
            },
            PersonalityType.CONSULTATIVE: {
                "tone": "advisory",
                "language_style": "consultative",
                "response_length": "thorough",
                "emoji_usage": "selective",
                "technical_level": "medium-high"
            },
            PersonalityType.SUPPORTIVE: {
                "tone": "empathetic",
                "language_style": "supportive",
                "response_length": "reassuring",
                "emoji_usage": "appropriate",
                "technical_level": "low-medium"
            }
        }
    
    def determine_optimal_personality(self, 
                                    user_profile: UserProfile, 
                                    conversation_context: Dict[str, Any],
                                    user_mood: UserMood) -> PersonalityType:
        """Determine optimal personality for current context"""
        
        # Default personality
        personality = PersonalityType.FRIENDLY
        
        # Business context influence
        if conversation_context.get('domain') == 'electrical_business':
            if conversation_context.get('intent') in ['pricing', 'negotiation']:
                personality = PersonalityType.PROFESSIONAL
            elif conversation_context.get('intent') == 'technical_support':
                personality = PersonalityType.TECHNICAL
            elif conversation_context.get('intent') == 'consultation':
                personality = PersonalityType.CONSULTATIVE
        
        # Mood-based adjustments
        mood_personality_map = {
            UserMood.FRUSTRATED: PersonalityType.SUPPORTIVE,
            UserMood.URGENT: PersonalityType.PROFESSIONAL,
            UserMood.CURIOUS: PersonalityType.CONSULTATIVE,
            UserMood.DECISIVE: PersonalityType.PROFESSIONAL,
            UserMood.POSITIVE: PersonalityType.FRIENDLY
        }
        
        if user_mood in mood_personality_map:
            personality = mood_personality_map[user_mood]
        
        # User preference override
        if user_profile.communication_style:
            style_personality_map = {
                'formal': PersonalityType.PROFESSIONAL,
                'friendly': PersonalityType.FRIENDLY,
                'technical': PersonalityType.TECHNICAL,
                'consultative': PersonalityType.CONSULTATIVE
            }
            if user_profile.communication_style in style_personality_map:
                personality = style_personality_map[user_profile.communication_style]
        
        return personality
    
    def get_personality_guidelines(self, personality: PersonalityType) -> Dict[str, str]:
        """Get guidelines for given personality"""
        return self.personality_profiles.get(personality, self.personality_profiles[PersonalityType.FRIENDLY])

class ContextAwareConversationManager:
    """Main conversation manager with context awareness"""
    
    def __init__(self, db_path: str = "data/conversation.db"):
        self.db_path = db_path
        
        # Core components
        self.mood_detector = MoodDetector()
        self.personality_adapter = PersonalityAdapter()
        
        # Storage
        self.active_conversations = {}  # Session ID -> Conversation data
        self.user_profiles = {}  # User ID -> UserProfile
        self.conversation_contexts = {}  # Context ID -> ConversationContext
        self.conversation_memories = deque(maxlen=1000)  # Recent memories
        
        # State tracking
        self.current_sessions = {}  # Session ID -> Current state
        self.context_weights = defaultdict(float)  # Context importance weights
        
        # Performance tracking
        self.response_times = deque(maxlen=100)
        self.context_hits = 0
        self.context_misses = 0
        
        # Threading
        self._lock = threading.RLock()
        
        # Initialize database
        self._initialize_database()
        
        # Load existing data
        asyncio.create_task(self._load_existing_data())
        
        log_info("🧠 Context-Aware Conversation Manager initialized")
    
    def _initialize_database(self):
        """Initialize conversation database"""
        try:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                # Enable optimizations
                conn.execute('PRAGMA journal_mode=WAL')
                conn.execute('PRAGMA synchronous=NORMAL')
                
                # User profiles table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        user_id TEXT PRIMARY KEY,
                        name TEXT,
                        preferred_language TEXT,
                        communication_style TEXT,
                        business_context TEXT,
                        preferences TEXT,
                        interaction_history TEXT,
                        created_at TEXT,
                        last_interaction TEXT,
                        total_interactions INTEGER DEFAULT 0
                    )
                ''')
                
                # Conversation turns table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS conversation_turns (
                        turn_id TEXT PRIMARY KEY,
                        session_id TEXT,
                        user_id TEXT,
                        user_input TEXT,
                        bot_response TEXT,
                        timestamp TEXT,
                        language TEXT,
                        mood TEXT,
                        state TEXT,
                        context_used TEXT,
                        confidence REAL,
                        processing_time_ms REAL
                    )
                ''')
                
                # Conversation contexts table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS conversation_contexts (
                        context_id TEXT PRIMARY KEY,
                        context_type TEXT,
                        data TEXT,
                        importance REAL,
                        expiry_time TEXT,
                        access_count INTEGER DEFAULT 0,
                        last_accessed TEXT,
                        created_at TEXT
                    )
                ''')
                
                # Conversation memories table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS conversation_memories (
                        memory_id TEXT PRIMARY KEY,
                        content TEXT,
                        memory_type TEXT,
                        importance REAL,
                        related_topics TEXT,
                        created_at TEXT,
                        last_used TEXT,
                        use_count INTEGER DEFAULT 0
                    )
                ''')
                
                # Create indexes
                conn.execute('CREATE INDEX IF NOT EXISTS idx_turns_session ON conversation_turns(session_id)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_turns_user ON conversation_turns(user_id)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_turns_timestamp ON conversation_turns(timestamp)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_contexts_type ON conversation_contexts(context_type)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_memories_type ON conversation_memories(memory_type)')
                
            log_info("💬 Conversation database initialized")
            
        except Exception as e:
            log_error(f"Failed to initialize conversation database: {e}")
    
    async def _load_existing_data(self):
        """Load existing user profiles and contexts"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Load user profiles
                cursor = conn.execute('SELECT * FROM user_profiles LIMIT 100')
                for row in cursor.fetchall():
                    user_profile = UserProfile(
                        user_id=row[0],
                        name=row[1],
                        preferred_language=row[2] or "hi-en",
                        communication_style=row[3] or "friendly",
                        business_context=json.loads(row[4] or '{}'),
                        preferences=json.loads(row[5] or '{}'),
                        interaction_history=json.loads(row[6] or '[]'),
                        created_at=datetime.fromisoformat(row[7]) if row[7] else None,
                        last_interaction=datetime.fromisoformat(row[8]) if row[8] else None,
                        total_interactions=row[9] or 0
                    )
                    self.user_profiles[user_profile.user_id] = user_profile
                
                # Load recent conversation contexts
                cursor = conn.execute('''
                    SELECT * FROM conversation_contexts 
                    WHERE expiry_time IS NULL OR expiry_time > ?
                    ORDER BY created_at DESC LIMIT 500
                ''', (datetime.now().isoformat(),))
                
                for row in cursor.fetchall():
                    context = ConversationContext(
                        context_id=row[0],
                        context_type=ContextType(row[1]),
                        data=json.loads(row[2]),
                        importance=row[3],
                        expiry_time=datetime.fromisoformat(row[4]) if row[4] else None,
                        access_count=row[5] or 0,
                        last_accessed=datetime.fromisoformat(row[6]) if row[6] else None,
                        created_at=datetime.fromisoformat(row[7]) if row[7] else None
                    )
                    self.conversation_contexts[context.context_id] = context
                
                # Load recent memories
                cursor = conn.execute('''
                    SELECT * FROM conversation_memories 
                    ORDER BY created_at DESC LIMIT 200
                ''')
                
                for row in cursor.fetchall():
                    memory = ConversationMemory(
                        memory_id=row[0],
                        content=row[1],
                        memory_type=row[2],
                        importance=row[3],
                        related_topics=json.loads(row[4] or '[]'),
                        created_at=datetime.fromisoformat(row[5]),
                        last_used=datetime.fromisoformat(row[6]) if row[6] else None,
                        use_count=row[7] or 0
                    )
                    self.conversation_memories.append(memory)
                
            log_info(f"📚 Loaded {len(self.user_profiles)} user profiles, "
                    f"{len(self.conversation_contexts)} contexts, "
                    f"{len(self.conversation_memories)} memories")
            
        except Exception as e:
            log_error(f"Failed to load existing data: {e}")
    
    @monitor_performance("conversation_manager")
    async def process_conversation_turn(self, 
                                      session_id: str,
                                      user_id: str,
                                      user_input: str,
                                      context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a single conversation turn"""
        
        start_time = time.time()
        
        try:
            # Get or create user profile
            user_profile = await self._get_or_create_user_profile(user_id)
            
            # Detect user mood
            mood_context = {
                'previous_mood': self._get_previous_mood(session_id),
                'turn_count': len(self.active_conversations.get(session_id, [])),
                'response_time': context.get('response_time', 0) if context else 0
            }
            user_mood, mood_confidence = self.mood_detector.detect_mood(user_input, mood_context)
            
            # Determine conversation state
            conversation_state = await self._determine_conversation_state(session_id, user_input, user_mood)
            
            # Retrieve relevant context
            relevant_contexts = await self._retrieve_relevant_context(user_input, user_profile, conversation_state)
            
            # Determine optimal personality
            conversation_context = context or {}
            conversation_context.update({
                'domain': self._extract_domain_from_input(user_input),
                'intent': self._extract_intent_from_input(user_input)
            })
            
            optimal_personality = self.personality_adapter.determine_optimal_personality(
                user_profile, conversation_context, user_mood
            )
            
            # Generate conversation guidelines
            personality_guidelines = self.personality_adapter.get_personality_guidelines(optimal_personality)
            
            # Store conversation turn
            turn_id = f"turn_{session_id}_{int(time.time() * 1000)}"
            processing_time = (time.time() - start_time) * 1000
            
            turn = ConversationTurn(
                turn_id=turn_id,
                user_input=user_input,
                bot_response="",  # Will be filled by the calling system
                timestamp=datetime.now(),
                language=user_profile.preferred_language,
                mood=user_mood,
                state=conversation_state,
                context_used=[ctx.context_id for ctx in relevant_contexts],
                confidence=mood_confidence,
                processing_time_ms=processing_time
            )
            
            # Update conversation tracking
            await self._update_conversation_tracking(session_id, user_id, turn)
            
            # Update user profile
            await self._update_user_profile_interaction(user_profile, user_input, user_mood)
            
            # Store context if needed
            await self._store_conversation_context(session_id, user_input, conversation_context)
            
            # Record performance
            self.response_times.append(processing_time)
            
            # Prepare response data
            response_data = {
                'session_id': session_id,
                'turn_id': turn_id,
                'user_mood': user_mood.value,
                'mood_confidence': mood_confidence,
                'conversation_state': conversation_state.value,
                'optimal_personality': optimal_personality.value,
                'personality_guidelines': personality_guidelines,
                'relevant_contexts': [asdict(ctx) for ctx in relevant_contexts],
                'user_profile': asdict(user_profile),
                'processing_time_ms': processing_time,
                'language': user_profile.preferred_language
            }
            
            return response_data
            
        except Exception as e:
            log_error(f"Failed to process conversation turn: {e}")
            processing_time = (time.time() - start_time) * 1000
            return {
                'session_id': session_id,
                'error': str(e),
                'processing_time_ms': processing_time,
                'user_mood': UserMood.NEUTRAL.value,
                'conversation_state': ConversationState.DISCUSSION.value,
                'optimal_personality': PersonalityType.FRIENDLY.value
            }
    
    async def _get_or_create_user_profile(self, user_id: str) -> UserProfile:
        """Get existing user profile or create new one"""
        with self._lock:
            if user_id in self.user_profiles:
                return self.user_profiles[user_id]
            
            # Create new profile
            profile = UserProfile(
                user_id=user_id,
                created_at=datetime.now(),
                total_interactions=0
            )
            
            self.user_profiles[user_id] = profile
            
            # Save to database
            asyncio.create_task(self._save_user_profile(profile))
            
            return profile
    
    def _get_previous_mood(self, session_id: str) -> Optional[str]:
        """Get previous mood from session"""
        if session_id in self.active_conversations:
            conversations = self.active_conversations[session_id]
            if conversations:
                return conversations[-1].get('mood')
        return None
    
    async def _determine_conversation_state(self, session_id: str, user_input: str, user_mood: UserMood) -> ConversationState:
        """Determine current conversation state"""
        
        # Check for greeting patterns
        greeting_patterns = [
            r'\b(?:hello|hi|hey|namaste|good morning|good afternoon|good evening)\b',
            r'\b(?:kaise|kaisan|kya haal|how are you)\b'
        ]
        
        if any(re.search(pattern, user_input, re.IGNORECASE) for pattern in greeting_patterns):
            return ConversationState.GREETING
        
        # Check for inquiry patterns
        inquiry_patterns = [
            r'\b(?:what|how|where|when|why|tell me|explain)\b',
            r'\b(?:kya|kaise|kahan|kab|kyun|batao|samjhao)\b',
            r'\?'
        ]
        
        if any(re.search(pattern, user_input, re.IGNORECASE) for pattern in inquiry_patterns):
            return ConversationState.INQUIRY
        
        # Check for negotiation/pricing patterns
        negotiation_patterns = [
            r'\b(?:price|cost|rate|discount|offer|deal|negotiate)\b',
            r'\b(?:kitna|paisa|rupees|price|rate|kam)\b'
        ]
        
        if any(re.search(pattern, user_input, re.IGNORECASE) for pattern in negotiation_patterns):
            return ConversationState.NEGOTIATION
        
        # Check for closing patterns
        closing_patterns = [
            r'\b(?:bye|goodbye|thanks|thank you|dhanyawad|ok|done)\b',
            r'\b(?:bye|alvida|dhanyawad|theek hai|ho gaya)\b'
        ]
        
        if any(re.search(pattern, user_input, re.IGNORECASE) for pattern in closing_patterns):
            return ConversationState.CLOSING
        
        # Mood-based states
        if user_mood == UserMood.FRUSTRATED:
            return ConversationState.CLARIFICATION
        elif user_mood == UserMood.URGENT:
            return ConversationState.CLARIFICATION
        
        # Default to discussion
        return ConversationState.DISCUSSION
    
    async def _retrieve_relevant_context(self, 
                                       user_input: str, 
                                       user_profile: UserProfile,
                                       conversation_state: ConversationState) -> List[ConversationContext]:
        """Retrieve relevant conversation contexts"""
        
        relevant_contexts = []
        input_lower = user_input.lower()
        
        # Score contexts based on relevance
        context_scores = []
        
        for context in self.conversation_contexts.values():
            score = 0.0
            
            # Check if context has expired
            if context.expiry_time and context.expiry_time < datetime.now():
                continue
            
            # Text similarity scoring (simplified)
            context_text = json.dumps(context.data).lower()
            common_words = set(input_lower.split()) & set(context_text.split())
            if common_words:
                score += len(common_words) * 0.1
            
            # Context type relevance
            type_relevance = {
                ConversationState.GREETING: [ContextType.PERSONAL, ContextType.RELATIONAL],
                ConversationState.INQUIRY: [ContextType.BUSINESS, ContextType.TECHNICAL],
                ConversationState.NEGOTIATION: [ContextType.TRANSACTIONAL, ContextType.BUSINESS],
                ConversationState.DISCUSSION: [ContextType.BUSINESS, ContextType.TECHNICAL],
                ConversationState.CLARIFICATION: [ContextType.TECHNICAL, ContextType.BUSINESS]
            }
            
            if conversation_state in type_relevance and context.context_type in type_relevance[conversation_state]:
                score += 0.3
            
            # Importance weighting
            score *= context.importance
            
            # Recent access bonus
            if context.last_accessed and context.last_accessed > datetime.now() - timedelta(hours=1):
                score += 0.2
            
            context_scores.append((context, score))
        
        # Sort by score and return top contexts
        context_scores.sort(key=lambda x: x[1], reverse=True)
        
        for context, score in context_scores[:5]:  # Top 5 contexts
            if score > 0.1:  # Minimum relevance threshold
                relevant_contexts.append(context)
                
                # Update access tracking
                context.access_count += 1
                context.last_accessed = datetime.now()
                self.context_hits += 1
            else:
                self.context_misses += 1
        
        return relevant_contexts
    
    def _extract_domain_from_input(self, user_input: str) -> str:
        """Extract domain from user input"""
        business_keywords = [
            'switch', 'wire', 'light', 'fan', 'socket', 'mcb', 'electrical',
            'price', 'cost', 'install', 'repair', 'service'
        ]
        
        if any(keyword in user_input.lower() for keyword in business_keywords):
            return 'electrical_business'
        
        return 'general'
    
    def _extract_intent_from_input(self, user_input: str) -> str:
        """Extract intent from user input"""
        intent_patterns = {
            'pricing': [r'\b(?:price|cost|rate|kitna|paisa)\b'],
            'technical_support': [r'\b(?:how to|install|setup|problem|issue|help)\b'],
            'consultation': [r'\b(?:suggest|recommend|advice|batao|samjhao)\b'],
            'negotiation': [r'\b(?:discount|offer|deal|kam|negotiate)\b']
        }
        
        for intent, patterns in intent_patterns.items():
            if any(re.search(pattern, user_input, re.IGNORECASE) for pattern in patterns):
                return intent
        
        return 'general_inquiry'
    
    async def _update_conversation_tracking(self, session_id: str, user_id: str, turn: ConversationTurn):
        """Update conversation tracking data"""
        with self._lock:
            if session_id not in self.active_conversations:
                self.active_conversations[session_id] = []
            
            # Add turn to active conversations
            self.active_conversations[session_id].append({
                'turn_id': turn.turn_id,
                'user_input': turn.user_input,
                'timestamp': turn.timestamp.isoformat(),
                'mood': turn.mood.value,
                'state': turn.state.value,
                'language': turn.language
            })
            
            # Limit conversation history per session
            if len(self.active_conversations[session_id]) > 20:
                self.active_conversations[session_id] = self.active_conversations[session_id][-20:]
            
            # Update current session state
            self.current_sessions[session_id] = {
                'user_id': user_id,
                'current_state': turn.state.value,
                'current_mood': turn.mood.value,
                'last_update': turn.timestamp
            }
        
        # Save to database
        await self._save_conversation_turn(turn, session_id, user_id)
    
    async def _update_user_profile_interaction(self, user_profile: UserProfile, user_input: str, user_mood: UserMood):
        """Update user profile based on interaction"""
        user_profile.last_interaction = datetime.now()
        user_profile.total_interactions += 1
        
        # Add to interaction history (last 10 interactions)
        user_profile.interaction_history.append({
            'input': user_input[:100],  # Truncate for storage
            'mood': user_mood.value,
            'timestamp': datetime.now().isoformat()
        })
        
        if len(user_profile.interaction_history) > 10:
            user_profile.interaction_history = user_profile.interaction_history[-10:]
        
        # Update preferences based on patterns
        await self._update_user_preferences(user_profile, user_input, user_mood)
        
        # Save updated profile
        await self._save_user_profile(user_profile)
    
    async def _update_user_preferences(self, user_profile: UserProfile, user_input: str, user_mood: UserMood):
        """Update user preferences based on interaction patterns"""
        
        # Communication style detection
        if user_mood == UserMood.POSITIVE and 'please' in user_input.lower():
            user_profile.communication_style = 'polite'
        elif any(word in user_input.lower() for word in ['urgent', 'jaldi', 'quick']):
            user_profile.communication_style = 'direct'
        elif any(word in user_input.lower() for word in ['explain', 'detail', 'samjhao']):
            user_profile.communication_style = 'detailed'
        
        # Business context updates
        if 'electrical' in user_input.lower() or any(word in user_input.lower() for word in ['switch', 'wire', 'mcb']):
            if 'electrical_interest' not in user_profile.business_context:
                user_profile.business_context['electrical_interest'] = 1
            else:
                user_profile.business_context['electrical_interest'] += 1
        
        # Language preference detection
        hindi_words = ['kya', 'hai', 'aap', 'main', 'ji', 'dhanyawad']
        english_words = ['what', 'how', 'please', 'thank', 'you']
        
        hindi_count = sum(1 for word in hindi_words if word in user_input.lower())
        english_count = sum(1 for word in english_words if word in user_input.lower())
        
        if hindi_count > english_count:
            user_profile.preferences['prefers_hindi'] = True
        elif english_count > hindi_count:
            user_profile.preferences['prefers_english'] = True
        else:
            user_profile.preferences['prefers_hinglish'] = True
    
    async def _store_conversation_context(self, session_id: str, user_input: str, context: Dict[str, Any]):
        """Store conversation context for future reference"""
        
        # Determine context type
        context_type = ContextType.BUSINESS if context.get('domain') == 'electrical_business' else ContextType.PERSONAL
        
        # Create context entry
        context_id = f"ctx_{session_id}_{hashlib.md5(user_input.encode()).hexdigest()[:8]}"
        
        conversation_context = ConversationContext(
            context_id=context_id,
            context_type=context_type,
            data={
                'user_input': user_input,
                'domain': context.get('domain'),
                'intent': context.get('intent'),
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            },
            importance=0.7,  # Default importance
            expiry_time=datetime.now() + timedelta(hours=24),  # 24-hour expiry
            created_at=datetime.now()
        )
        
        # Store context
        self.conversation_contexts[context_id] = conversation_context
        
        # Save to database
        await self._save_conversation_context(conversation_context)
    
    async def _save_user_profile(self, user_profile: UserProfile):
        """Save user profile to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO user_profiles 
                    (user_id, name, preferred_language, communication_style, business_context, 
                     preferences, interaction_history, created_at, last_interaction, total_interactions)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_profile.user_id,
                    user_profile.name,
                    user_profile.preferred_language,
                    user_profile.communication_style,
                    json.dumps(user_profile.business_context),
                    json.dumps(user_profile.preferences),
                    json.dumps(user_profile.interaction_history),
                    user_profile.created_at.isoformat() if user_profile.created_at else None,
                    user_profile.last_interaction.isoformat() if user_profile.last_interaction else None,
                    user_profile.total_interactions
                ))
        except Exception as e:
            log_error(f"Failed to save user profile: {e}")
    
    async def _save_conversation_turn(self, turn: ConversationTurn, session_id: str, user_id: str):
        """Save conversation turn to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO conversation_turns 
                    (turn_id, session_id, user_id, user_input, bot_response, timestamp, 
                     language, mood, state, context_used, confidence, processing_time_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    turn.turn_id,
                    session_id,
                    user_id,
                    turn.user_input,
                    turn.bot_response,
                    turn.timestamp.isoformat(),
                    turn.language,
                    turn.mood.value,
                    turn.state.value,
                    json.dumps(turn.context_used),
                    turn.confidence,
                    turn.processing_time_ms
                ))
        except Exception as e:
            log_error(f"Failed to save conversation turn: {e}")
    
    async def _save_conversation_context(self, context: ConversationContext):
        """Save conversation context to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO conversation_contexts 
                    (context_id, context_type, data, importance, expiry_time, 
                     access_count, last_accessed, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    context.context_id,
                    context.context_type.value,
                    json.dumps(context.data),
                    context.importance,
                    context.expiry_time.isoformat() if context.expiry_time else None,
                    context.access_count,
                    context.last_accessed.isoformat() if context.last_accessed else None,
                    context.created_at.isoformat() if context.created_at else None
                ))
        except Exception as e:
            log_error(f"Failed to save conversation context: {e}")
    
    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get conversation summary for session"""
        if session_id not in self.active_conversations:
            return {'error': 'Session not found'}
        
        conversation = self.active_conversations[session_id]
        session_state = self.current_sessions.get(session_id, {})
        
        # Analyze conversation patterns
        moods = [turn.get('mood') for turn in conversation]
        states = [turn.get('state') for turn in conversation]
        
        mood_counts = Counter(moods)
        state_counts = Counter(states)
        
        return {
            'session_id': session_id,
            'total_turns': len(conversation),
            'current_state': session_state.get('current_state'),
            'current_mood': session_state.get('current_mood'),
            'dominant_mood': mood_counts.most_common(1)[0] if mood_counts else None,
            'conversation_flow': state_counts,
            'last_interaction': session_state.get('last_update'),
            'user_id': session_state.get('user_id')
        }
    
    def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights about a specific user"""
        if user_id not in self.user_profiles:
            return {'error': 'User not found'}
        
        profile = self.user_profiles[user_id]
        
        return {
            'user_id': user_id,
            'total_interactions': profile.total_interactions,
            'preferred_language': profile.preferred_language,
            'communication_style': profile.communication_style,
            'business_interests': profile.business_context,
            'preferences': profile.preferences,
            'last_interaction': profile.last_interaction.isoformat() if profile.last_interaction else None,
            'interaction_patterns': self._analyze_user_patterns(profile)
        }
    
    def _analyze_user_patterns(self, profile: UserProfile) -> Dict[str, Any]:
        """Analyze user interaction patterns"""
        if not profile.interaction_history:
            return {}
        
        # Mood patterns
        moods = [interaction.get('mood') for interaction in profile.interaction_history if 'mood' in interaction]
        mood_distribution = Counter(moods)
        
        # Time patterns (simplified)
        recent_interactions = len([i for i in profile.interaction_history 
                                 if 'timestamp' in i and 
                                 datetime.fromisoformat(i['timestamp']) > datetime.now() - timedelta(days=7)])
        
        return {
            'mood_distribution': dict(mood_distribution),
            'recent_activity': recent_interactions,
            'avg_session_length': len(profile.interaction_history) / max(profile.total_interactions / 5, 1),  # Approximate
            'engagement_level': 'high' if profile.total_interactions > 20 else 'medium' if profile.total_interactions > 5 else 'low'
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get conversation manager performance statistics"""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        context_hit_rate = self.context_hits / max(self.context_hits + self.context_misses, 1) * 100
        
        return {
            'active_sessions': len(self.active_conversations),
            'total_users': len(self.user_profiles),
            'total_contexts': len(self.conversation_contexts),
            'avg_response_time_ms': avg_response_time,
            'context_hit_rate': context_hit_rate,
            'memory_usage': {
                'active_conversations': len(self.active_conversations),
                'conversation_memories': len(self.conversation_memories),
                'user_profiles_loaded': len(self.user_profiles)
            }
        }
    
    async def cleanup(self):
        """Clean up conversation manager resources"""
        log_info("🧹 Cleaning up Conversation Manager...")
        
        # Clear active data
        with self._lock:
            self.active_conversations.clear()
            self.current_sessions.clear()
            self.context_weights.clear()
            self.response_times.clear()
        
        log_info("✅ Conversation Manager cleanup completed")


# Global instance
_conversation_manager = None

def get_conversation_manager(**kwargs) -> ContextAwareConversationManager:
    """Get or create global conversation manager"""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ContextAwareConversationManager(**kwargs)
    return _conversation_manager

if __name__ == "__main__":
    # Test the conversation manager
    async def test_conversation_manager():
        print("🧪 Testing Context-Aware Conversation Manager")
        print("=" * 60)
        
        # Create manager
        manager = ContextAwareConversationManager(db_path="test_conversation.db")
        
        # Wait for initialization
        await asyncio.sleep(1)
        
        # Test conversation scenarios
        test_scenarios = [
            # Greeting scenario
            {
                'session_id': 'test_session_1',
                'user_id': 'user_123',
                'inputs': [
                    'Hello, namaste!',
                    'Switch ka price kya hai?',
                    'Accha, installation bhi karvana hai',
                    'Thank you, bahut helpful tha'
                ]
            },
            # Technical inquiry scenario  
            {
                'session_id': 'test_session_2', 
                'user_id': 'user_456',
                'inputs': [
                    'MCB installation kaise karte hain?',
                    'Safety precautions kya hain?',
                    'Kitna time lagega?'
                ]
            }
        ]
        
        print("\n🗣️ Testing Conversation Scenarios:")
        
        for scenario in test_scenarios:
            session_id = scenario['session_id']
            user_id = scenario['user_id']
            
            print(f"\n--- Session: {session_id} ---")
            
            for i, user_input in enumerate(scenario['inputs'], 1):
                print(f"\nTurn {i}: User: {user_input}")
                
                # Process conversation turn
                result = await manager.process_conversation_turn(
                    session_id=session_id,
                    user_id=user_id, 
                    user_input=user_input,
                    context={'response_time': 1.5}
                )
                
                print(f"Mood: {result['user_mood']} (confidence: {result['mood_confidence']:.2f})")
                print(f"State: {result['conversation_state']}")
                print(f"Personality: {result['optimal_personality']}")
                print(f"Contexts used: {len(result['relevant_contexts'])}")
                print(f"Processing time: {result['processing_time_ms']:.1f}ms")
                
                if result['relevant_contexts']:
                    print("Relevant contexts:")
                    for ctx in result['relevant_contexts']:
                        print(f"  • {ctx['context_type']}: {ctx['data'].get('domain', 'N/A')}")
        
        # Test conversation summaries
        print("\n📊 Conversation Summaries:")
        for scenario in test_scenarios:
            session_id = scenario['session_id']
            summary = manager.get_conversation_summary(session_id)
            
            print(f"\n{session_id}:")
            print(f"  • Total turns: {summary['total_turns']}")
            print(f"  • Current state: {summary['current_state']}")
            print(f"  • Current mood: {summary['current_mood']}")
            print(f"  • Dominant mood: {summary.get('dominant_mood')}")
        
        # Test user insights
        print("\n👤 User Insights:")
        test_users = ['user_123', 'user_456']
        
        for user_id in test_users:
            insights = manager.get_user_insights(user_id)
            print(f"\n{user_id}:")
            print(f"  • Total interactions: {insights['total_interactions']}")
            print(f"  • Communication style: {insights['communication_style']}")
            print(f"  • Preferred language: {insights['preferred_language']}")
            
            if insights.get('interaction_patterns'):
                patterns = insights['interaction_patterns']
                print(f"  • Engagement level: {patterns.get('engagement_level')}")
                print(f"  • Recent activity: {patterns.get('recent_activity')}")
        
        # Performance statistics
        print("\n📈 Performance Statistics:")
        stats = manager.get_performance_stats()
        print(f"  • Active sessions: {stats['active_sessions']}")
        print(f"  • Total users: {stats['total_users']}")
        print(f"  • Context hit rate: {stats['context_hit_rate']:.1f}%")
        print(f"  • Avg response time: {stats['avg_response_time_ms']:.1f}ms")
        
        # Cleanup
        await manager.cleanup()
        print("\n🧹 Test completed")
    
    # Run test
    asyncio.run(test_conversation_manager())