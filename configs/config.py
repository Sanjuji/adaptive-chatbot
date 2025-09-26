#!/usr/bin/env python3
"""
Unified Configuration System for Adaptive Chatbot
Centralizes all settings and configurations
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Centralized configuration management"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "data"
        self.logs_dir = self.base_dir / "logs"
        
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Load configuration
        self._load_default_config()
    
    def _load_default_config(self):
        """Load default configuration settings"""
        
        # Database settings
        self.knowledge_db_path = self.data_dir / "knowledge_base.json"
        
        # Voice settings
        self.voice_config = {
            "recognition_timeout": 10,
            "max_retry_attempts": 3,
            "energy_threshold": 300,
            "pause_threshold": 0.8,
            "phrase_threshold": 0.3,
            "default_language": "hi-IN",
            "fallback_language": "en-US"
        }
        
        # TTS settings - EdgeTTS Realistic Voice Engine
        self.tts_config = {
            "default_engine": "edgetts",  # Realistic human-like voice engine
            "default_voice": "english_male_warm",  # Confident, Authentic, Warm
            "hindi_voice": "hindi_male",  # For Hindi content
            "volume": 0.8,
            "speech_rate": "normal",  # Natural speaking rate
            "prefer_male_voice": True,
            "realistic_speech": True
        }
        
        # Learning settings
        self.learning_config = {
            "confidence_threshold": 0.7,
            "max_knowledge_entries": 10000,
            "auto_save": True,
            "backup_enabled": True
        }
        
        # Application settings
        self.app_config = {
            "app_name": "Adaptive Chatbot",
            "version": "1.0.0",
            "debug_mode": False,
            "log_level": "INFO"
        }
        
        # UI settings
        self.ui_config = {
            "show_timestamps": True,
            "use_emojis": True,
            "max_history_display": 50,
            "default_script": "devanagari"  # devanagari or hinglish
        }
    
    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        """Get configuration value"""
        try:
            config_section = getattr(self, f"{section}_config", {})
            if key is None:
                return config_section
            return config_section.get(key, default)
        except Exception:
            return default
    
    def set(self, section: str, key: str, value: Any) -> bool:
        """Set configuration value"""
        try:
            config_section = getattr(self, f"{section}_config", {})
            config_section[key] = value
            return True
        except Exception:
            return False
    
    def get_log_file_path(self) -> Path:
        """Get log file path"""
        return self.logs_dir / "chatbot.log"
    
    def get_knowledge_file_path(self) -> Path:
        """Get knowledge database file path"""
        return self.knowledge_db_path
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled"""
        return self.app_config.get("debug_mode", False)

# Global configuration instance
config = Config()