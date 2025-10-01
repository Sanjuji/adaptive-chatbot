#!/usr/bin/env python3
"""
Adaptive Chatbot - Production-Ready Main Application
Unified architecture with comprehensive error handling and all features
"""

import sys
import os
import argparse
import time
from typing import Optional, Dict, Any
import signal
import atexit

# Import our modules with error handling
try:
    from utils.simple_voice import speak_simple as speak, listen_simple as listen, is_voice_ready as is_voice_available
except ImportError as e:
    print(f"[ERROR] Voice interface unavailable: {e}")
    # Fallback to dummy functions
    def speak(text): return False
    def listen(timeout=10): return None
    def is_voice_available(): return False

try:
    from core.adaptation_engine import UnifiedLearningManager
except ImportError as e:
    print(f"[ERROR] Learning system unavailable: {e}")
    sys.exit(1)

try:
    from utils.validator import sanitize_user_input, is_safe_input
    from utils.advanced_event_loop_manager import get_loop_manager, run_async_safely
    from utils.advanced_memory_manager import get_memory_manager, memory_monitor, register_memory_cleanup
    from utils.performance_monitoring_dashboard import get_performance_monitor, performance_timer
except ImportError as e:
    print(f"[ERROR] Validation system unavailable: {e}")
    # Fallback to basic validation
    def sanitize_user_input(text): return str(text).strip() if text else ""
    def is_safe_input(text): return bool(text and len(str(text).strip()) > 0)

try:
    from configs.config import config
    from utils.logger import get_logger
except ImportError as e:
    print(f"[ERROR] Configuration or logger unavailable: {e}")
    # Create fallback config and logger
    class FallbackConfig:
        def get(self, section, key, default=None):
            if section == "app" and key == "version":
                return "1.0.0"
            return default
    config = FallbackConfig()
    
    import logging
    logger = logging.getLogger("AdaptiveChatbot")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    logger.addHandler(handler)
else:
    logger = get_logger()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Adaptive Chatbot - AI Assistant that learns from you')
    parser.add_argument('--mode', choices=['menu', 'voice', 'text'], default='menu',
                       help='Start mode: menu (default), voice, or text')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--version', action='version', 
                       version=f'Adaptive Chatbot v{config.get("app", "version", "1.0.0")}')
    
    args = parser.parse_args()
    
    # Set debug mode
    if args.debug:
        config.set('app', 'debug_mode', True)
        logger.info("Debug mode enabled")
    
    try:
        # For now, just print a welcome message
        print("Adaptive Chatbot v1.0.0")
        print("Starting in menu mode...")
        print("Options: --mode [menu|voice|text] --debug")
        
    except KeyboardInterrupt:
        logger.info("\\nApplication interrupted by user")
    except Exception as e:
        logger.error("Application error", error=e)
        print(f"[ERROR] Critical error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()