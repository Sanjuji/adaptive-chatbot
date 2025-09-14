"""
Configuration system for the Adaptive Chatbot
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Config:
    """Configuration class for the chatbot."""
    
    # Database settings
    database_path: str = "data/knowledge.db"
    
    # Model settings
    sentence_model_name: str = "all-MiniLM-L6-v2"
    confidence_threshold: float = 0.7
    max_context_length: int = 5
    
    # Domain settings
    default_domain: str = "general"
    available_domains: list = field(default_factory=lambda: ["general", "shop", "tech", "personal"])
    
    # Learning settings
    auto_learn_enabled: bool = False
    min_confidence_for_auto_learn: float = 0.9
    max_knowledge_entries: int = 10000
    
    # Conversation settings
    max_response_length: int = 500
    enable_conversation_logging: bool = True
    conversation_cleanup_days: int = 30
    
    # UI settings
    show_confidence_scores: bool = False
    colorize_output: bool = True
    
    # Voice settings
    voice_enabled: bool = True
    use_gtts: bool = True  # Use Google TTS instead of local pyttsx3
    voice_language: str = 'hi-IN'  # Speech recognition language
    tts_language: str = 'hi'  # Text-to-speech language
    speech_rate: int = 150  # Words per minute for local TTS
    voice_id: int = 0  # Voice ID for local TTS
    energy_threshold: int = 300  # Microphone sensitivity
    pause_threshold: float = 0.8  # Pause detection threshold
    timeout: int = 5  # Listening timeout in seconds
    phrase_time_limit: int = 10  # Maximum phrase length in seconds
    
    # Logging settings
    log_level: str = "INFO"
    log_file: str = "logs/chatbot.log"
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration from file or defaults."""
        # Set defaults first
        self.database_path = "data/knowledge.db"
        self.sentence_model_name = "all-MiniLM-L6-v2"
        self.confidence_threshold = 0.7
        self.max_context_length = 5
        self.default_domain = "general"
        self.available_domains = ["general", "shop", "tech", "personal"]
        self.auto_learn_enabled = False
        self.min_confidence_for_auto_learn = 0.9
        self.max_knowledge_entries = 10000
        self.max_response_length = 500
        self.enable_conversation_logging = True
        self.conversation_cleanup_days = 30
        self.show_confidence_scores = False
        self.colorize_output = True
        self.voice_enabled = True
        self.use_gtts = True
        self.voice_language = 'hi-IN'
        self.tts_language = 'hi'
        self.speech_rate = 150
        self.voice_id = 0
        self.energy_threshold = 150  # Much lower for better sensitivity
        self.pause_threshold = 0.5   # Faster response
        self.timeout = 6             # Longer timeout to allow speaking
        self.phrase_time_limit = 10
        self.log_level = "INFO"
        self.log_file = "logs/chatbot.log"
        
        self.config_path = config_path or "config/config.yaml"
        self._load_config()
        self._setup_logging()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        config_file = Path(self.config_path)
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
                
                # Update fields with loaded values
                for key, value in config_data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
                
                logging.info(f"Configuration loaded from {config_file}")
                
            except Exception as e:
                logging.warning(f"Failed to load config from {config_file}: {e}")
                logging.info("Using default configuration")
        else:
            # Create default config file
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """Create a default configuration file."""
        try:
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            default_config = {
                'database_path': self.database_path,
                'sentence_model_name': self.sentence_model_name,
                'confidence_threshold': self.confidence_threshold,
                'max_context_length': self.max_context_length,
                'default_domain': self.default_domain,
                'available_domains': self.available_domains,
                'auto_learn_enabled': self.auto_learn_enabled,
                'min_confidence_for_auto_learn': self.min_confidence_for_auto_learn,
                'max_knowledge_entries': self.max_knowledge_entries,
                'max_response_length': self.max_response_length,
                'enable_conversation_logging': self.enable_conversation_logging,
                'conversation_cleanup_days': self.conversation_cleanup_days,
                'show_confidence_scores': self.show_confidence_scores,
                'colorize_output': self.colorize_output,
                'voice_enabled': self.voice_enabled,
                'use_gtts': self.use_gtts,
                'voice_language': self.voice_language,
                'tts_language': self.tts_language,
                'speech_rate': self.speech_rate,
                'voice_id': self.voice_id,
                'energy_threshold': self.energy_threshold,
                'pause_threshold': self.pause_threshold,
                'timeout': self.timeout,
                'phrase_time_limit': self.phrase_time_limit,
                'log_level': self.log_level,
                'log_file': self.log_file
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            
            logging.info(f"Default configuration created at {config_file}")
            
        except Exception as e:
            logging.error(f"Failed to create default config: {e}")
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_file = Path(self.log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        log_level = getattr(logging, self.log_level.upper(), logging.INFO)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def save_config(self) -> bool:
        """Save current configuration to file."""
        try:
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            config_data = {
                'database_path': self.database_path,
                'sentence_model_name': self.sentence_model_name,
                'confidence_threshold': self.confidence_threshold,
                'max_context_length': self.max_context_length,
                'default_domain': self.default_domain,
                'available_domains': self.available_domains,
                'auto_learn_enabled': self.auto_learn_enabled,
                'min_confidence_for_auto_learn': self.min_confidence_for_auto_learn,
                'max_knowledge_entries': self.max_knowledge_entries,
                'max_response_length': self.max_response_length,
                'enable_conversation_logging': self.enable_conversation_logging,
                'conversation_cleanup_days': self.conversation_cleanup_days,
                'show_confidence_scores': self.show_confidence_scores,
                'colorize_output': self.colorize_output,
                'voice_enabled': self.voice_enabled,
                'use_gtts': self.use_gtts,
                'voice_language': self.voice_language,
                'tts_language': self.tts_language,
                'speech_rate': self.speech_rate,
                'voice_id': self.voice_id,
                'energy_threshold': self.energy_threshold,
                'pause_threshold': self.pause_threshold,
                'timeout': self.timeout,
                'phrase_time_limit': self.phrase_time_limit,
                'log_level': self.log_level,
                'log_file': self.log_file
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            
            logging.info(f"Configuration saved to {config_file}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to save config: {e}")
            return False
    
    def get_domain_config(self, domain: str) -> Dict[str, Any]:
        """Get domain-specific configuration."""
        domain_configs = {
            'shop': {
                'greeting': "Namaste! Main aapki shop assistant hun. Electrical aur electronics ke bare mein puch sakte hain.",
                'categories': ['wires', 'switches', 'bulbs', 'fans', 'electronics', 'appliances'],
                'default_responses': [
                    "Yeh product available hai. Price ke liye puch sakte hain.",
                    "Is item ki details aur price main check kar deta hun.",
                    "Koi specific brand ya model chahiye?"
                ]
            },
            'general': {
                'greeting': "Hello! Main ek adaptive chatbot hun. Main seekh sakta hun jo bhi aap sikhayenge.",
                'categories': ['general', 'conversation', 'help'],
                'default_responses': [
                    "Kripaya mujhe is bare mein aur batayiye.",
                    "Main is topic ke bare mein seekhna chahta hun.",
                    "Aap mujhe is bare mein kya sikhana chahte hain?"
                ]
            },
            'tech': {
                'greeting': "Hi! Main technology aur technical topics mein help kar sakta hun.",
                'categories': ['programming', 'hardware', 'software', 'troubleshooting'],
                'default_responses': [
                    "Yeh interesting technical question hai.",
                    "Is technology ke bare mein aur details chahiye?",
                    "Koi specific technical problem hai?"
                ]
            }
        }
        
        return domain_configs.get(domain, domain_configs['general'])
    
    def update_setting(self, key: str, value: Any) -> bool:
        """Update a configuration setting."""
        if hasattr(self, key):
            setattr(self, key, value)
            logging.info(f"Configuration updated: {key} = {value}")
            return True
        else:
            logging.warning(f"Unknown configuration key: {key}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all configuration settings."""
        return {
            'database_path': self.database_path,
            'sentence_model_name': self.sentence_model_name,
            'confidence_threshold': self.confidence_threshold,
            'max_context_length': self.max_context_length,
            'default_domain': self.default_domain,
            'available_domains': self.available_domains,
            'auto_learn_enabled': self.auto_learn_enabled,
            'min_confidence_for_auto_learn': self.min_confidence_for_auto_learn,
            'max_knowledge_entries': self.max_knowledge_entries,
            'max_response_length': self.max_response_length,
            'enable_conversation_logging': self.enable_conversation_logging,
            'conversation_cleanup_days': self.conversation_cleanup_days,
            'show_confidence_scores': self.show_confidence_scores,
            'colorize_output': self.colorize_output,
            'voice_enabled': self.voice_enabled,
            'use_gtts': self.use_gtts,
            'voice_language': self.voice_language,
            'tts_language': self.tts_language,
            'speech_rate': self.speech_rate,
            'voice_id': self.voice_id,
            'energy_threshold': self.energy_threshold,
            'pause_threshold': self.pause_threshold,
            'timeout': self.timeout,
            'phrase_time_limit': self.phrase_time_limit,
            'log_level': self.log_level,
            'log_file': self.log_file
        }
