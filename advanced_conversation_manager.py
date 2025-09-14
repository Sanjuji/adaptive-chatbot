#!/usr/bin/env python3
"""
Advanced Conversation Manager
Sophisticated conversation context management with memory persistence, 
topic tracking, user profiling, and conversation flow optimization
"""

import json
import time
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import pickle
import os

try:
    from logger import log_info, log_error, log_warning
except ImportError:
    def log_info(msg): print(f"INFO - {msg}")
    def log_error(msg): print(f"ERROR - {msg}")
    def log_warning(msg): print(f"WARNING - {msg}")

class ConversationPhase(Enum):
    """Phases of conversation flow"""
    GREETING = "greeting"
    INQUIRY = "inquiry"
    NEGOTIATION = "negotiation"
    CONFIRMATION = "confirmation"
    APPRECIATION = "appreciation"
    CLOSING = "closing"
    PROBLEM_SOLVING = "problem_solving"
    FOLLOW_UP = "follow_up"

class UserPersonality(Enum):
    """User personality types for adaptation"""
    ANALYTICAL = "analytical"
    EXPRESSIVE = "expressive"
    DRIVER = "driver"
    AMIABLE = "amiable"
    TECHNICAL = "technical"
    CASUAL = "casual"
    FORMAL = "formal"

@dataclass
class ConversationTurn:
    """Single conversation turn"""
    turn_id: str
    timestamp: datetime
    user_input: str
    system_response: str
    detected_language: str
    intent: str
    sentiment: str
    confidence: float
    topic: str
    phase: ConversationPhase
    voice_used: Optional[str] = None
    response_time: float = 0.0
    satisfaction_score: Optional[float] = None

@dataclass
class TopicInfo:
    """Information about conversation topics"""
    topic_id: str
    topic_name: str
    keywords: List[str]
    frequency: int
    last_discussed: datetime
    satisfaction_level: float
    related_products: List[str]
    resolution_status: str  # "resolved", "pending", "unresolved"

@dataclass
class UserProfile:
    """Comprehensive user profile"""
    user_id: str
    first_seen: datetime
    last_interaction: datetime
    total_conversations: int
    preferred_language: str
    secondary_languages: List[str]
    personality_type: UserPersonality
    communication_style: str
    interests: List[str]
    purchase_history: List[Dict]
    satisfaction_score: float
    frequent_topics: List[str]
    preferred_voice_gender: Optional[str]
    preferred_voice_style: Optional[str]
    business_relationship: str  # "new", "regular", "vip"
    custom_preferences: Dict[str, Any]

@dataclass
class ConversationSession:
    """Complete conversation session"""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime]
    turns: List[ConversationTurn]
    primary_language: str
    languages_used: List[str]
    topics_discussed: List[str]
    phases_completed: List[ConversationPhase]
    overall_sentiment: str
    satisfaction_score: Optional[float]
    business_outcome: Optional[str]
    follow_up_required: bool
    summary: Optional[str]

class AdvancedConversationManager:
    """Advanced conversation management with persistence and analytics"""
    
    def __init__(self, database_path: str = "conversation_data.db"):
        self.database_path = database_path
        self.active_sessions = {}  # session_id -> ConversationSession
        self.user_profiles = {}    # user_id -> UserProfile
        self.topic_tracker = {}    # topic_id -> TopicInfo
        
        # Configuration
        self.config = {
            "max_active_sessions": 100,
            "session_timeout_minutes": 60,
            "memory_retention_days": 90,
            "auto_summary_turns": 20,
            "personality_learning_enabled": True,
            "topic_persistence_enabled": True,
            "voice_preference_learning": True,
            "satisfaction_tracking": True
        }
        
        # Analytics
        self.analytics = {
            "total_conversations": 0,
            "average_conversation_length": 0.0,
            "most_common_topics": [],
            "language_distribution": {},
            "satisfaction_trends": [],
            "personality_distribution": {},
            "phase_completion_rates": {}
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Initialize database and load data
        self._initialize_database()
        self._load_persistent_data()
        
        log_info("🧠 Advanced Conversation Manager initialized")
    
    def _initialize_database(self):
        """Initialize SQLite database for persistence"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # User profiles table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        user_id TEXT PRIMARY KEY,
                        profile_data TEXT,
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP
                    )
                """)
                
                # Conversation sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id TEXT,
                        session_data TEXT,
                        start_time TIMESTAMP,
                        end_time TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                    )
                """)
                
                # Topics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS topics (
                        topic_id TEXT PRIMARY KEY,
                        topic_data TEXT,
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP
                    )
                """)
                
                # Analytics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS analytics (
                        metric_name TEXT PRIMARY KEY,
                        metric_data TEXT,
                        updated_at TIMESTAMP
                    )
                """)
                
                conn.commit()
                log_info("✅ Conversation database initialized")
                
        except Exception as e:
            log_error(f"Database initialization failed: {e}")
    
    def _load_persistent_data(self):
        """Load persistent data from database"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Load user profiles
                cursor.execute("SELECT user_id, profile_data FROM user_profiles")
                for user_id, profile_data in cursor.fetchall():
                    try:
                        profile_dict = json.loads(profile_data)
                        # Convert datetime strings back to datetime objects
                        profile_dict['first_seen'] = datetime.fromisoformat(profile_dict['first_seen'])
                        profile_dict['last_interaction'] = datetime.fromisoformat(profile_dict['last_interaction'])
                        profile_dict['personality_type'] = UserPersonality(profile_dict['personality_type'])
                        
                        self.user_profiles[user_id] = UserProfile(**profile_dict)
                    except Exception as e:
                        log_warning(f"Failed to load user profile {user_id}: {e}")
                
                # Load topics
                cursor.execute("SELECT topic_id, topic_data FROM topics")
                for topic_id, topic_data in cursor.fetchall():
                    try:
                        topic_dict = json.loads(topic_data)
                        topic_dict['last_discussed'] = datetime.fromisoformat(topic_dict['last_discussed'])
                        self.topic_tracker[topic_id] = TopicInfo(**topic_dict)
                    except Exception as e:
                        log_warning(f"Failed to load topic {topic_id}: {e}")
                
                # Load analytics
                cursor.execute("SELECT metric_name, metric_data FROM analytics")
                for metric_name, metric_data in cursor.fetchall():
                    try:
                        self.analytics[metric_name] = json.loads(metric_data)
                    except Exception as e:
                        log_warning(f"Failed to load analytics {metric_name}: {e}")
                
                log_info(f"📊 Loaded {len(self.user_profiles)} user profiles, {len(self.topic_tracker)} topics")
                
        except Exception as e:
            log_error(f"Failed to load persistent data: {e}")
    
    def start_conversation(self, user_id: str, initial_context: Optional[Dict] = None) -> str:
        """Start a new conversation session"""
        with self._lock:
            try:
                session_id = self._generate_session_id(user_id)
                current_time = datetime.now()
                
                # Get or create user profile
                user_profile = self._get_or_create_user_profile(user_id)
                
                # Create new session
                session = ConversationSession(
                    session_id=session_id,
                    user_id=user_id,
                    start_time=current_time,
                    end_time=None,
                    turns=[],
                    primary_language=user_profile.preferred_language,
                    languages_used=[],
                    topics_discussed=[],
                    phases_completed=[],
                    overall_sentiment="neutral",
                    satisfaction_score=None,
                    business_outcome=None,
                    follow_up_required=False,
                    summary=None
                )
                
                self.active_sessions[session_id] = session
                
                # Update user profile
                user_profile.last_interaction = current_time
                user_profile.total_conversations += 1
                
                # Clean up old sessions
                self._cleanup_old_sessions()
                
                log_info(f"🎬 Started conversation session {session_id} for user {user_id}")
                return session_id
                
            except Exception as e:
                log_error(f"Failed to start conversation: {e}")
                raise
    
    def add_turn(self, session_id: str, user_input: str, system_response: str, 
                 metadata: Dict[str, Any]) -> str:
        """Add a conversation turn to active session"""
        with self._lock:
            try:
                if session_id not in self.active_sessions:
                    raise ValueError(f"Session {session_id} not found")
                
                session = self.active_sessions[session_id]
                turn_id = f"{session_id}_{len(session.turns)}"
                
                # Extract metadata
                detected_language = metadata.get('detected_language', 'en')
                intent = metadata.get('intent', 'general')
                sentiment = metadata.get('sentiment', 'neutral')
                confidence = metadata.get('confidence', 0.5)
                topic = metadata.get('topic', 'general')
                voice_used = metadata.get('voice_used')
                response_time = metadata.get('response_time', 0.0)
                
                # Determine conversation phase
                phase = self._determine_conversation_phase(session, user_input, intent)
                
                # Create turn
                turn = ConversationTurn(
                    turn_id=turn_id,
                    timestamp=datetime.now(),
                    user_input=user_input,
                    system_response=system_response,
                    detected_language=detected_language,
                    intent=intent,
                    sentiment=sentiment,
                    confidence=confidence,
                    topic=topic,
                    phase=phase,
                    voice_used=voice_used,
                    response_time=response_time
                )
                
                session.turns.append(turn)
                
                # Update session metadata
                self._update_session_metadata(session, turn)
                
                # Update topic tracking
                self._update_topic_tracking(topic, detected_language)
                
                # Update user profile
                self._update_user_profile(session.user_id, turn)
                
                # Auto-generate summary if needed
                if len(session.turns) % self.config["auto_summary_turns"] == 0:
                    self._generate_session_summary(session_id)
                
                log_info(f"💬 Added turn {turn_id} to session {session_id}")
                return turn_id
                
            except Exception as e:
                log_error(f"Failed to add turn: {e}")
                raise
    
    def end_conversation(self, session_id: str, satisfaction_score: Optional[float] = None,
                        business_outcome: Optional[str] = None) -> Dict[str, Any]:
        """End conversation session and generate summary"""
        with self._lock:
            try:
                if session_id not in self.active_sessions:
                    raise ValueError(f"Session {session_id} not found")
                
                session = self.active_sessions[session_id]
                session.end_time = datetime.now()
                session.satisfaction_score = satisfaction_score
                session.business_outcome = business_outcome
                
                # Generate final summary
                summary = self._generate_session_summary(session_id)
                session.summary = summary
                
                # Determine follow-up requirements
                session.follow_up_required = self._requires_follow_up(session)
                
                # Update analytics
                self._update_analytics(session)
                
                # Persist session
                self._persist_session(session)
                
                # Remove from active sessions
                completed_session = self.active_sessions.pop(session_id)
                
                # Calculate session metrics
                duration = (session.end_time - session.start_time).total_seconds()
                turn_count = len(session.turns)
                
                session_summary = {
                    "session_id": session_id,
                    "user_id": session.user_id,
                    "duration_seconds": duration,
                    "turn_count": turn_count,
                    "languages_used": session.languages_used,
                    "topics_discussed": session.topics_discussed,
                    "phases_completed": [phase.value for phase in session.phases_completed],
                    "overall_sentiment": session.overall_sentiment,
                    "satisfaction_score": session.satisfaction_score,
                    "business_outcome": session.business_outcome,
                    "follow_up_required": session.follow_up_required,
                    "summary": session.summary
                }
                
                log_info(f"🎬 Ended conversation session {session_id} - Duration: {duration:.1f}s, Turns: {turn_count}")
                return session_summary
                
            except Exception as e:
                log_error(f"Failed to end conversation: {e}")
                raise
    
    def get_conversation_context(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive conversation context for current session"""
        with self._lock:
            try:
                if session_id not in self.active_sessions:
                    return {}
                
                session = self.active_sessions[session_id]
                user_profile = self.user_profiles.get(session.user_id)
                
                # Recent turns context
                recent_turns = session.turns[-5:] if len(session.turns) > 5 else session.turns
                
                # Topic context
                current_topics = list(set([turn.topic for turn in recent_turns]))
                topic_context = {}
                for topic in current_topics:
                    if topic in self.topic_tracker:
                        topic_context[topic] = {
                            "frequency": self.topic_tracker[topic].frequency,
                            "satisfaction": self.topic_tracker[topic].satisfaction_level,
                            "related_products": self.topic_tracker[topic].related_products,
                            "resolution_status": self.topic_tracker[topic].resolution_status
                        }
                
                # Language patterns
                language_usage = {}
                for turn in session.turns:
                    lang = turn.detected_language
                    language_usage[lang] = language_usage.get(lang, 0) + 1
                
                # Sentiment progression
                sentiment_progression = [turn.sentiment for turn in session.turns[-10:]]
                
                # Current phase and suggested next phases
                current_phase = session.turns[-1].phase if session.turns else ConversationPhase.GREETING
                suggested_phases = self._suggest_next_phases(session, current_phase)
                
                context = {
                    "session_info": {
                        "session_id": session_id,
                        "user_id": session.user_id,
                        "duration_minutes": (datetime.now() - session.start_time).total_seconds() / 60,
                        "turn_count": len(session.turns),
                        "primary_language": session.primary_language
                    },
                    "user_profile": {
                        "personality_type": user_profile.personality_type.value if user_profile else "casual",
                        "communication_style": user_profile.communication_style if user_profile else "friendly",
                        "business_relationship": user_profile.business_relationship if user_profile else "new",
                        "preferred_language": user_profile.preferred_language if user_profile else "en",
                        "satisfaction_score": user_profile.satisfaction_score if user_profile else 0.5,
                        "frequent_topics": user_profile.frequent_topics if user_profile else []
                    },
                    "conversation_flow": {
                        "current_phase": current_phase.value,
                        "phases_completed": [p.value for p in session.phases_completed],
                        "suggested_next_phases": [p.value for p in suggested_phases],
                        "topics_discussed": session.topics_discussed,
                        "languages_used": session.languages_used
                    },
                    "recent_context": {
                        "recent_turns": [
                            {
                                "user_input": turn.user_input,
                                "intent": turn.intent,
                                "sentiment": turn.sentiment,
                                "topic": turn.topic,
                                "language": turn.detected_language
                            } for turn in recent_turns
                        ],
                        "sentiment_progression": sentiment_progression,
                        "language_usage": language_usage,
                        "dominant_sentiment": max(set(sentiment_progression), key=sentiment_progression.count) if sentiment_progression else "neutral"
                    },
                    "topic_context": topic_context,
                    "recommendations": {
                        "voice_style": self._recommend_voice_style(session, user_profile),
                        "response_tone": self._recommend_response_tone(session),
                        "follow_up_suggestions": self._generate_follow_up_suggestions(session)
                    }
                }
                
                return context
                
            except Exception as e:
                log_error(f"Failed to get conversation context: {e}")
                return {}
    
    def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive insights about a user"""
        with self._lock:
            try:
                if user_id not in self.user_profiles:
                    return {}
                
                profile = self.user_profiles[user_id]
                
                # Get user's conversation history
                with sqlite3.connect(self.database_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT session_data FROM conversation_sessions 
                        WHERE user_id = ? ORDER BY start_time DESC LIMIT 10
                    """, (user_id,))
                    
                    recent_sessions = []
                    for (session_data,) in cursor.fetchall():
                        try:
                            session_dict = json.loads(session_data)
                            recent_sessions.append(session_dict)
                        except:
                            continue
                
                # Calculate insights
                insights = {
                    "profile_summary": {
                        "user_id": user_id,
                        "relationship_level": profile.business_relationship,
                        "personality_type": profile.personality_type.value,
                        "communication_style": profile.communication_style,
                        "satisfaction_score": profile.satisfaction_score,
                        "total_conversations": profile.total_conversations,
                        "first_seen": profile.first_seen.isoformat(),
                        "last_interaction": profile.last_interaction.isoformat()
                    },
                    "language_preferences": {
                        "primary": profile.preferred_language,
                        "secondary": profile.secondary_languages
                    },
                    "interaction_patterns": {
                        "frequent_topics": profile.frequent_topics,
                        "interests": profile.interests,
                        "purchase_history": profile.purchase_history
                    },
                    "voice_preferences": {
                        "gender": profile.preferred_voice_gender,
                        "style": profile.preferred_voice_style
                    },
                    "recent_activity": {
                        "sessions_count": len(recent_sessions),
                        "avg_satisfaction": sum(s.get('satisfaction_score', 0.5) for s in recent_sessions) / max(len(recent_sessions), 1),
                        "common_phases": self._analyze_common_phases(recent_sessions),
                        "language_distribution": self._analyze_language_distribution(recent_sessions)
                    },
                    "recommendations": {
                        "engagement_strategy": self._recommend_engagement_strategy(profile),
                        "product_suggestions": self._recommend_products(profile),
                        "communication_approach": self._recommend_communication_approach(profile)
                    }
                }
                
                return insights
                
            except Exception as e:
                log_error(f"Failed to get user insights: {e}")
                return {}
    
    def _generate_session_id(self, user_id: str) -> str:
        """Generate unique session ID"""
        timestamp = str(int(time.time() * 1000))
        unique_string = f"{user_id}_{timestamp}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
    
    def _get_or_create_user_profile(self, user_id: str) -> UserProfile:
        """Get existing user profile or create new one"""
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]
        
        # Create new profile
        profile = UserProfile(
            user_id=user_id,
            first_seen=datetime.now(),
            last_interaction=datetime.now(),
            total_conversations=0,
            preferred_language="en",
            secondary_languages=[],
            personality_type=UserPersonality.CASUAL,
            communication_style="friendly",
            interests=[],
            purchase_history=[],
            satisfaction_score=0.5,
            frequent_topics=[],
            preferred_voice_gender=None,
            preferred_voice_style=None,
            business_relationship="new",
            custom_preferences={}
        )
        
        self.user_profiles[user_id] = profile
        self._persist_user_profile(profile)
        
        log_info(f"👤 Created new user profile for {user_id}")
        return profile
    
    def _determine_conversation_phase(self, session: ConversationSession, 
                                    user_input: str, intent: str) -> ConversationPhase:
        """Determine current conversation phase"""
        # Phase determination logic based on intent and conversation history
        if len(session.turns) == 0:
            if any(greeting in user_input.lower() for greeting in ["hello", "hi", "namaste", "hola", "bonjour"]):
                return ConversationPhase.GREETING
        
        if intent in ["greeting", "introduction"]:
            return ConversationPhase.GREETING
        elif intent in ["question", "inquiry", "product_inquiry", "price_inquiry"]:
            return ConversationPhase.INQUIRY
        elif intent in ["bargain", "negotiate", "price_discussion"]:
            return ConversationPhase.NEGOTIATION
        elif intent in ["confirmation", "order", "purchase"]:
            return ConversationPhase.CONFIRMATION
        elif intent in ["appreciation", "thanks", "compliment"]:
            return ConversationPhase.APPRECIATION
        elif intent in ["goodbye", "closing", "end"]:
            return ConversationPhase.CLOSING
        elif intent in ["complaint", "problem", "issue", "help"]:
            return ConversationPhase.PROBLEM_SOLVING
        elif intent in ["follow_up", "check", "status"]:
            return ConversationPhase.FOLLOW_UP
        else:
            # Default to inquiry for unknown intents
            return ConversationPhase.INQUIRY
    
    def _update_session_metadata(self, session: ConversationSession, turn: ConversationTurn):
        """Update session metadata based on new turn"""
        # Update languages used
        if turn.detected_language not in session.languages_used:
            session.languages_used.append(turn.detected_language)
        
        # Update topics discussed
        if turn.topic not in session.topics_discussed:
            session.topics_discussed.append(turn.topic)
        
        # Update phases completed
        if turn.phase not in session.phases_completed:
            session.phases_completed.append(turn.phase)
        
        # Update overall sentiment (weighted average)
        sentiments = [t.sentiment for t in session.turns]
        sentiment_weights = {"positive": 1, "neutral": 0, "negative": -1}
        avg_sentiment = sum(sentiment_weights.get(s, 0) for s in sentiments) / len(sentiments)
        
        if avg_sentiment > 0.3:
            session.overall_sentiment = "positive"
        elif avg_sentiment < -0.3:
            session.overall_sentiment = "negative"
        else:
            session.overall_sentiment = "neutral"
    
    def _update_topic_tracking(self, topic: str, language: str):
        """Update topic tracking information"""
        if topic not in self.topic_tracker:
            self.topic_tracker[topic] = TopicInfo(
                topic_id=topic,
                topic_name=topic,
                keywords=[topic],
                frequency=0,
                last_discussed=datetime.now(),
                satisfaction_level=0.5,
                related_products=[],
                resolution_status="pending"
            )
        
        topic_info = self.topic_tracker[topic]
        topic_info.frequency += 1
        topic_info.last_discussed = datetime.now()
    
    def _update_user_profile(self, user_id: str, turn: ConversationTurn):
        """Update user profile based on conversation turn"""
        if user_id not in self.user_profiles:
            return
        
        profile = self.user_profiles[user_id]
        
        # Update language preferences
        if turn.detected_language != profile.preferred_language:
            if turn.detected_language not in profile.secondary_languages:
                profile.secondary_languages.append(turn.detected_language)
        
        # Update frequent topics
        if turn.topic not in profile.frequent_topics:
            profile.frequent_topics.append(turn.topic)
            if len(profile.frequent_topics) > 10:  # Limit to top 10
                profile.frequent_topics = profile.frequent_topics[-10:]
        
        # Update voice preferences if voice was used
        if turn.voice_used:
            # Extract gender and style from voice name (simplified)
            if "female" in turn.voice_used.lower() or any(name in turn.voice_used.lower() for name in ["jenny", "aria", "swara"]):
                profile.preferred_voice_gender = "female"
            elif "male" in turn.voice_used.lower() or any(name in turn.voice_used.lower() for name in ["guy", "madhur"]):
                profile.preferred_voice_gender = "male"
    
    def _persist_user_profile(self, profile: UserProfile):
        """Persist user profile to database"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                profile_dict = asdict(profile)
                # Convert datetime objects to ISO format strings
                profile_dict['first_seen'] = profile.first_seen.isoformat()
                profile_dict['last_interaction'] = profile.last_interaction.isoformat()
                profile_dict['personality_type'] = profile.personality_type.value
                
                profile_data = json.dumps(profile_dict)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO user_profiles (user_id, profile_data, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (profile.user_id, profile_data, datetime.now(), datetime.now()))
                
                conn.commit()
                
        except Exception as e:
            log_error(f"Failed to persist user profile {profile.user_id}: {e}")
    
    def _persist_session(self, session: ConversationSession):
        """Persist conversation session to database"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                session_dict = asdict(session)
                # Convert datetime objects and enums to serializable format
                session_dict['start_time'] = session.start_time.isoformat()
                session_dict['end_time'] = session.end_time.isoformat() if session.end_time else None
                
                # Convert turns
                turns_serializable = []
                for turn in session.turns:
                    turn_dict = asdict(turn)
                    turn_dict['timestamp'] = turn.timestamp.isoformat()
                    turn_dict['phase'] = turn.phase.value
                    turns_serializable.append(turn_dict)
                session_dict['turns'] = turns_serializable
                
                # Convert phases
                session_dict['phases_completed'] = [p.value for p in session.phases_completed]
                
                session_data = json.dumps(session_dict)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO conversation_sessions 
                    (session_id, user_id, session_data, start_time, end_time)
                    VALUES (?, ?, ?, ?, ?)
                """, (session.session_id, session.user_id, session_data, 
                     session.start_time, session.end_time))
                
                conn.commit()
                
        except Exception as e:
            log_error(f"Failed to persist session {session.session_id}: {e}")
    
    def _generate_session_summary(self, session_id: str) -> str:
        """Generate intelligent session summary"""
        if session_id not in self.active_sessions:
            return ""
        
        session = self.active_sessions[session_id]
        if not session.turns:
            return "Empty conversation session"
        
        # Extract key information
        topics = list(set([turn.topic for turn in session.turns]))
        languages = session.languages_used
        phases = [p.value for p in session.phases_completed]
        sentiments = [turn.sentiment for turn in session.turns]
        
        # Generate summary
        summary_parts = []
        summary_parts.append(f"Conversation with {len(session.turns)} turns")
        
        if len(languages) > 1:
            summary_parts.append(f"multilingual ({', '.join(languages)})")
        
        if topics:
            main_topics = topics[:3]  # Top 3 topics
            summary_parts.append(f"discussing {', '.join(main_topics)}")
        
        if phases:
            summary_parts.append(f"completing phases: {', '.join(phases[-3:])}")  # Last 3 phases
        
        # Sentiment summary
        positive_count = sentiments.count("positive")
        negative_count = sentiments.count("negative")
        if positive_count > negative_count:
            summary_parts.append("with positive outcome")
        elif negative_count > positive_count:
            summary_parts.append("addressing concerns")
        
        summary = ". ".join(summary_parts).capitalize() + "."
        return summary
    
    def _suggest_next_phases(self, session: ConversationSession, 
                           current_phase: ConversationPhase) -> List[ConversationPhase]:
        """Suggest logical next conversation phases"""
        phase_transitions = {
            ConversationPhase.GREETING: [ConversationPhase.INQUIRY, ConversationPhase.PROBLEM_SOLVING],
            ConversationPhase.INQUIRY: [ConversationPhase.NEGOTIATION, ConversationPhase.CONFIRMATION],
            ConversationPhase.NEGOTIATION: [ConversationPhase.CONFIRMATION, ConversationPhase.INQUIRY],
            ConversationPhase.CONFIRMATION: [ConversationPhase.APPRECIATION, ConversationPhase.FOLLOW_UP],
            ConversationPhase.PROBLEM_SOLVING: [ConversationPhase.CONFIRMATION, ConversationPhase.FOLLOW_UP],
            ConversationPhase.APPRECIATION: [ConversationPhase.CLOSING, ConversationPhase.FOLLOW_UP],
            ConversationPhase.FOLLOW_UP: [ConversationPhase.CLOSING, ConversationPhase.INQUIRY],
            ConversationPhase.CLOSING: [ConversationPhase.GREETING]  # For future conversations
        }
        
        return phase_transitions.get(current_phase, [ConversationPhase.INQUIRY])
    
    def _recommend_voice_style(self, session: ConversationSession, 
                              user_profile: Optional[UserProfile]) -> str:
        """Recommend appropriate voice style based on context"""
        if not user_profile:
            return "friendly"
        
        # Base recommendation on personality type
        style_mapping = {
            UserPersonality.ANALYTICAL: "professional",
            UserPersonality.EXPRESSIVE: "cheerful",
            UserPersonality.DRIVER: "confident",
            UserPersonality.AMIABLE: "warm",
            UserPersonality.TECHNICAL: "precise",
            UserPersonality.CASUAL: "friendly",
            UserPersonality.FORMAL: "professional"
        }
        
        base_style = style_mapping.get(user_profile.personality_type, "friendly")
        
        # Adjust based on conversation sentiment
        if session.overall_sentiment == "negative":
            return "calm"
        elif session.overall_sentiment == "positive":
            return "cheerful"
        
        return base_style
    
    def _recommend_response_tone(self, session: ConversationSession) -> str:
        """Recommend appropriate response tone"""
        recent_sentiments = [turn.sentiment for turn in session.turns[-3:]]
        
        if "negative" in recent_sentiments:
            return "empathetic"
        elif "positive" in recent_sentiments:
            return "enthusiastic"
        elif ConversationPhase.PROBLEM_SOLVING in session.phases_completed:
            return "helpful"
        elif ConversationPhase.NEGOTIATION in session.phases_completed:
            return "accommodating"
        else:
            return "friendly"
    
    def _generate_follow_up_suggestions(self, session: ConversationSession) -> List[str]:
        """Generate contextual follow-up suggestions"""
        suggestions = []
        
        # Based on topics discussed
        if "price" in session.topics_discussed:
            suggestions.append("Offer detailed pricing information")
        if "installation" in session.topics_discussed:
            suggestions.append("Schedule installation appointment")
        if "warranty" in session.topics_discussed:
            suggestions.append("Provide warranty documentation")
        
        # Based on phases completed
        if ConversationPhase.INQUIRY in session.phases_completed:
            suggestions.append("Send product catalog")
        if ConversationPhase.NEGOTIATION in session.phases_completed:
            suggestions.append("Prepare final quotation")
        if ConversationPhase.PROBLEM_SOLVING in session.phases_completed:
            suggestions.append("Follow up on resolution")
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _requires_follow_up(self, session: ConversationSession) -> bool:
        """Determine if conversation requires follow-up"""
        # Check for unresolved issues
        if ConversationPhase.PROBLEM_SOLVING in session.phases_completed:
            return True
        
        # Check for pending confirmations
        if ConversationPhase.NEGOTIATION in session.phases_completed and \
           ConversationPhase.CONFIRMATION not in session.phases_completed:
            return True
        
        # Check satisfaction score
        if session.satisfaction_score and session.satisfaction_score < 0.7:
            return True
        
        return False
    
    def _update_analytics(self, session: ConversationSession):
        """Update conversation analytics"""
        self.analytics["total_conversations"] += 1
        
        # Update language distribution
        for lang in session.languages_used:
            self.analytics["language_distribution"][lang] = \
                self.analytics["language_distribution"].get(lang, 0) + 1
        
        # Update satisfaction trends
        if session.satisfaction_score:
            self.analytics["satisfaction_trends"].append({
                "timestamp": session.end_time.isoformat(),
                "score": session.satisfaction_score
            })
        
        # Persist analytics
        self._persist_analytics()
    
    def _persist_analytics(self):
        """Persist analytics to database"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                for metric_name, metric_data in self.analytics.items():
                    cursor.execute("""
                        INSERT OR REPLACE INTO analytics (metric_name, metric_data, updated_at)
                        VALUES (?, ?, ?)
                    """, (metric_name, json.dumps(metric_data), datetime.now()))
                
                conn.commit()
                
        except Exception as e:
            log_error(f"Failed to persist analytics: {e}")
    
    def _cleanup_old_sessions(self):
        """Clean up old active sessions"""
        current_time = datetime.now()
        timeout_threshold = current_time - timedelta(minutes=self.config["session_timeout_minutes"])
        
        expired_sessions = [
            session_id for session_id, session in self.active_sessions.items()
            if session.start_time < timeout_threshold
        ]
        
        for session_id in expired_sessions:
            log_info(f"⏰ Auto-ending expired session {session_id}")
            try:
                self.end_conversation(session_id, business_outcome="timeout")
            except:
                # If ending fails, just remove from active sessions
                self.active_sessions.pop(session_id, None)
    
    def get_conversation_analytics(self) -> Dict[str, Any]:
        """Get comprehensive conversation analytics"""
        with self._lock:
            # Calculate dynamic metrics
            total_users = len(self.user_profiles)
            active_sessions_count = len(self.active_sessions)
            
            # Language distribution
            lang_dist = self.analytics.get("language_distribution", {})
            total_lang_uses = sum(lang_dist.values())
            lang_percentages = {lang: (count/total_lang_uses)*100 
                              for lang, count in lang_dist.items()} if total_lang_uses > 0 else {}
            
            # User relationship distribution
            relationship_dist = {}
            for profile in self.user_profiles.values():
                rel = profile.business_relationship
                relationship_dist[rel] = relationship_dist.get(rel, 0) + 1
            
            # Satisfaction trend
            satisfaction_trend = self.analytics.get("satisfaction_trends", [])
            avg_satisfaction = sum(s["score"] for s in satisfaction_trend) / max(len(satisfaction_trend), 1)
            
            return {
                "overview": {
                    "total_conversations": self.analytics.get("total_conversations", 0),
                    "total_users": total_users,
                    "active_sessions": active_sessions_count,
                    "avg_satisfaction": avg_satisfaction
                },
                "language_analytics": {
                    "distribution": lang_dist,
                    "percentages": lang_percentages,
                    "supported_languages": len(lang_dist)
                },
                "user_analytics": {
                    "relationship_distribution": relationship_dist,
                    "total_users": total_users
                },
                "topic_analytics": {
                    "total_topics": len(self.topic_tracker),
                    "most_frequent": sorted(
                        [(topic, info.frequency) for topic, info in self.topic_tracker.items()],
                        key=lambda x: x[1], reverse=True
                    )[:10]
                },
                "satisfaction_analytics": {
                    "average_score": avg_satisfaction,
                    "trend_data": satisfaction_trend[-20:],  # Last 20 data points
                    "total_ratings": len(satisfaction_trend)
                }
            }
    
    def cleanup(self):
        """Clean up resources and persist final data"""
        with self._lock:
            # End all active sessions
            for session_id in list(self.active_sessions.keys()):
                try:
                    self.end_conversation(session_id, business_outcome="system_shutdown")
                except:
                    pass
            
            # Persist all user profiles
            for profile in self.user_profiles.values():
                self._persist_user_profile(profile)
            
            # Persist analytics
            self._persist_analytics()
            
            log_info("✅ Advanced Conversation Manager cleaned up")

# Global instance
_conversation_manager = None

def get_conversation_manager() -> AdvancedConversationManager:
    """Get global conversation manager instance"""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = AdvancedConversationManager()
    return _conversation_manager

if __name__ == "__main__":
    # Test the conversation manager
    import time
    
    def test_conversation_manager():
        print("🧠 Testing Advanced Conversation Manager")
        print("=" * 50)
        
        manager = get_conversation_manager()
        
        # Test user profile creation
        user_id = "test_user_001"
        session_id = manager.start_conversation(user_id)
        print(f"✅ Started session: {session_id}")
        
        # Test conversation turns
        test_turns = [
            ("Hello! I need electrical items.", {"detected_language": "en", "intent": "greeting", "sentiment": "neutral", "topic": "general"}),
            ("Switch kitna ka hai?", {"detected_language": "hi", "intent": "price_inquiry", "sentiment": "neutral", "topic": "switches"}),
            ("Wire bhi chahiye installation ke liye.", {"detected_language": "hi", "intent": "product_inquiry", "sentiment": "neutral", "topic": "installation"}),
            ("Thank you for the help!", {"detected_language": "en", "intent": "appreciation", "sentiment": "positive", "topic": "service"})
        ]
        
        for user_input, metadata in test_turns:
            turn_id = manager.add_turn(session_id, user_input, f"Response to: {user_input}", metadata)
            print(f"📝 Added turn: {turn_id}")
        
        # Test context retrieval
        context = manager.get_conversation_context(session_id)
        print(f"🔍 Context phases: {context.get('conversation_flow', {}).get('phases_completed', [])}")
        print(f"🌍 Languages used: {context.get('conversation_flow', {}).get('languages_used', [])}")
        
        # Test session ending
        summary = manager.end_conversation(session_id, satisfaction_score=0.9, business_outcome="successful_inquiry")
        print(f"🎬 Session ended: {summary['turn_count']} turns, {summary['duration_seconds']:.1f}s")
        
        # Test user insights
        insights = manager.get_user_insights(user_id)
        print(f"👤 User insights: {insights.get('profile_summary', {}).get('personality_type', 'unknown')}")
        
        # Test analytics
        analytics = manager.get_conversation_analytics()
        print(f"📊 Total conversations: {analytics['overview']['total_conversations']}")
        print(f"📊 Languages: {list(analytics['language_analytics']['distribution'].keys())}")
        
        # Cleanup
        manager.cleanup()
        print("✅ Conversation Manager test completed")
    
    test_conversation_manager()