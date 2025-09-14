#!/usr/bin/env python3
"""
Comprehensive Logging System for Adaptive Chatbot
Provides structured logging with error tracking and debugging capabilities
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from config import config

class ChatbotLogger:
    """Enhanced logging system for the chatbot"""
    
    def __init__(self, name: str = "AdaptiveChatbot"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup logging handlers for console and file output"""
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # File handler
        try:
            log_file = config.get_log_file_path()
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
        except Exception:
            # Fallback to current directory
            file_handler = logging.FileHandler('chatbot.log', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
        
        # Formatters
        console_format = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        console_handler.setFormatter(console_format)
        file_handler.setFormatter(file_format)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(self._format_message(message, **kwargs))
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(self._format_message(message, **kwargs))
    
    def error(self, message: str, error: Exception = None, **kwargs):
        """Log error message with optional exception details"""
        formatted_msg = self._format_message(message, **kwargs)
        if error:
            formatted_msg += f" | Error: {str(error)}"
        self.logger.error(formatted_msg)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        if config.is_debug_mode():
            self.logger.debug(self._format_message(message, **kwargs))
    
    def critical(self, message: str, error: Exception = None, **kwargs):
        """Log critical error message"""
        formatted_msg = self._format_message(message, **kwargs)
        if error:
            formatted_msg += f" | Critical Error: {str(error)}"
        self.logger.critical(formatted_msg)
    
    def _format_message(self, message: str, **kwargs) -> str:
        """Format log message with additional context"""
        if kwargs:
            context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            return f"{message} | {context}"
        return message
    
    def log_voice_event(self, event_type: str, details: str = "", success: bool = True):
        """Log voice-related events"""
        status = "SUCCESS" if success else "FAILED"
        self.info(f"Voice Event: {event_type} - {status}", details=details)
    
    def log_learning_event(self, question: str, answer: str, success: bool = True):
        """Log learning events"""
        status = "LEARNED" if success else "FAILED_TO_LEARN"
        self.info(f"Learning Event: {status}", question=question[:50], answer=answer[:50])
    
    def log_error_with_context(self, error: Exception, context: dict = None):
        """Log error with full context"""
        error_details = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat()
        }
        
        if context:
            error_details.update(context)
        
        self.error("Application Error Occurred", error=error, **error_details)

# Global logger instance
logger = ChatbotLogger()

# Helper functions for easy access
def log_info(message: str, **kwargs):
    logger.info(message, **kwargs)

def log_warning(message: str, **kwargs):
    logger.warning(message, **kwargs)

def log_error(message: str, error: Exception = None, **kwargs):
    logger.error(message, error=error, **kwargs)

def log_debug(message: str, **kwargs):
    logger.debug(message, **kwargs)

def log_voice_event(event_type: str, details: str = "", success: bool = True):
    logger.log_voice_event(event_type, details, success)

def log_learning_event(question: str, answer: str, success: bool = True):
    logger.log_learning_event(question, answer, success)