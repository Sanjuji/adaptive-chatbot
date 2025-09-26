#!/usr/bin/env python3
"""
Multilingual EdgeTTS Integration - Import Alias
This module provides compatibility imports for the main adaptive chatbot
"""

# Import the actual multilingual voice system
from multilingual_voice_system import (
    get_multilingual_voice_system as get_multilingual_tts_system,
    MultilingualVoiceSystem,
    VoiceProfile,
    VoiceGender,
    VoiceStyle,
    speak_multilingual
)

# Export the main function expected by main_adaptive_chatbot.py
__all__ = [
    'get_multilingual_tts_system',
    'MultilingualVoiceSystem', 
    'VoiceProfile',
    'VoiceGender',
    'VoiceStyle',
    'speak_multilingual'
]