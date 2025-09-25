#!/usr/bin/env python3
"""
Comprehensive Logging System for Adaptive Chatbot
Provides structured logging with error tracking and debugging capabilities
"""

import logging
import sys
import io
from datetime import datetime
from pathlib import Path
from typing import Optional
from config import config


def _reconfigure_std_streams_for_utf8():
    """Best-effort: ensure stdout/stderr use UTF-8 with safe error handling.
    Prevents UnicodeEncodeError on Windows consoles with legacy code pages.
    """
    try:
        # Python 3.7+ TextIOWrapper supports reconfigure
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        # Fallback: wrap streams with UTF-8 writers that replace errors
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
        except Exception:
            pass
        try:
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True)
        except Exception:
            pass


class _EncodingSafeFilter(logging.Filter):
    """Sanitize record messages so they are encodable on the active stdout encoding."""
    def __init__(self, stream_encoding: str):
        super().__init__()
        self.encoding = (stream_encoding or "utf-8").lower()

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            # Ensure record.msg is safe to emit on the console
            msg = record.getMessage()
            safe = msg.encode(self.encoding, errors="replace").decode(self.encoding, errors="replace")
            # Mutate record for downstream formatter/output
            record.msg = safe
            record.args = None
        except Exception:
            # If anything goes wrong, let the record pass through
            pass
        return True


class ChatbotLogger:
    """Enhanced logging system for the chatbot"""
    
    def __init__(self, name: str = "AdaptiveChatbot"):
        # Ensure our process streams are UTF-8 where possible
        _reconfigure_std_streams_for_utf8()

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup logging handlers for console and file output"""
        
        # Console handler (encoding-safe)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.addFilter(_EncodingSafeFilter(getattr(sys.stdout, "encoding", "utf-8")))
        
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
