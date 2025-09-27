#!/usr/bin/env python3
"""
Input Validation and Sanitization for Adaptive Chatbot
Provides security and data integrity checks
"""

import re
import html
from typing import Any, Optional, Union, List, Dict
from utils.logger import get_logger

logger = get_logger()

class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    def __init__(self):
        # Comprehensive dangerous patterns for security
        self.dangerous_patterns = [
            # Script injection
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'data:text/html',
            
            # Event handlers
            r'on\w+\s*=',
            r'onload\s*=',
            r'onerror\s*=', 
            r'onclick\s*=',
            r'onmouseover\s*=',
            
            # Code execution
            r'eval\s*\(',
            r'exec\s*\(',
            r'execfile\s*\(',
            r'compile\s*\(',
            r'__import__\s*\(',
            r'globals\s*\(',
            r'locals\s*\(',
            
            # System commands
            r'import\s+(os|sys|subprocess|shutil|pickle)',
            r'from\s+(os|sys|subprocess|shutil|pickle)',
            r'os\.(system|popen|remove|rmdir|chmod)',
            r'subprocess\.(call|run|Popen)',
            
            # Path traversal
            r'\.\.[\/\\]',
            r'[\/\\]\.\.',
            r'\.\.\.',
            
            # SQL injection patterns
            r"(union|select|insert|update|delete|drop|alter|create)\s+",
            r"(?:'|\")\s*;\s*",
            r"(?:'|\")\s*(?:or|and)\s+",
            
            # File operations
            r'(open|file|read|write)\s*\(',
            r'with\s+open\s*\(',
            
            # Network operations (be more specific to avoid false positives)
            r'\bsocket\s*\.           # socket.method() calls only',
            r'import\s+socket\b',       # import socket only
            r'\burllib\b',              # urllib module
            r'\brequests\b',            # requests module  
            r'\bhttp://|\bhttps://',    # HTTP protocols
            r'\bfTP://',                # FTP protocol
            r'import\s+urllib',
            r'import\s+requests',
        ]
        
        # Compile patterns for performance
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.dangerous_patterns]
    
    def sanitize_text(self, text: str) -> str:
        """Sanitize text input by removing dangerous content"""
        if not isinstance(text, str):
            return str(text) if text is not None else ""
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Check if this is Hindi/Hinglish text (preserve it)
        has_hindi = any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in text)
        
        # Only apply HTML encoding for non-Hindi text to preserve Hindi characters
        if not has_hindi:
            # HTML encode dangerous characters
            text = html.escape(text)
        
        # Remove potentially dangerous patterns only if they are actual threats
        # Skip pattern removal for Hindi text to preserve legitimate queries
        if not has_hindi:
            for pattern in self.compiled_patterns:
                text = pattern.sub('', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def validate_question(self, question: str) -> bool:
        """Validate question input"""
        if not question or not isinstance(question, str):
            logger.warning("Invalid question: empty or not string")
            return False
        
        # Check length
        if len(question.strip()) < 2:
            logger.warning("Question too short")
            return False
        
        if len(question) > 500:
            logger.warning("Question too long")
            return False
        
        # Check for dangerous patterns
        if self._contains_dangerous_patterns(question):
            logger.warning("Question contains dangerous patterns")
            return False
        
        return True
    
    def validate_answer(self, answer: str) -> bool:
        """Validate answer input"""
        if not answer or not isinstance(answer, str):
            logger.warning("Invalid answer: empty or not string")
            return False
        
        # Check length
        if len(answer.strip()) < 1:
            logger.warning("Answer too short")
            return False
        
        if len(answer) > 1000:
            logger.warning("Answer too long")
            return False
        
        # Check for dangerous patterns
        if self._contains_dangerous_patterns(answer):
            logger.warning("Answer contains dangerous patterns")
            return False
        
        return True
    
    def validate_voice_command(self, command: str) -> bool:
        """Validate voice command input"""
        if not command or not isinstance(command, str):
            return False
        
        # Check length
        if len(command.strip()) < 1:
            return False
        
        if len(command) > 200:
            logger.warning("Voice command too long")
            return False
        
        # Check for dangerous patterns
        if self._contains_dangerous_patterns(command):
            logger.warning("Voice command contains dangerous patterns")
            return False
        
        return True
    
    def _contains_dangerous_patterns(self, text: str) -> bool:
        """Check if text contains dangerous patterns"""
        # Skip pattern check for Hindi/Hinglish text
        has_hindi = any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in text)
        if has_hindi:
            # Only check for very specific dangerous patterns in Hindi text
            dangerous_hindi_patterns = [
                r'<script.*?>.*?</script>',
                r'javascript:',
                r'eval\s*\(',
                r'exec\s*\(',
                r'os\.system\s*\('
            ]
            for pattern_str in dangerous_hindi_patterns:
                if re.search(pattern_str, text, re.IGNORECASE):
                    return True
            return False
        
        # Regular pattern check for non-Hindi text
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return True
        return False
    
    def safe_filename(self, filename: str) -> str:
        """Create a safe filename from input"""
        if not filename:
            return "untitled"
        
        # Remove dangerous characters
        safe_chars = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Limit length
        safe_chars = safe_chars[:100]
        
        # Ensure it doesn't start with dot or dash
        if safe_chars.startswith('.') or safe_chars.startswith('-'):
            safe_chars = 'file_' + safe_chars
        
        return safe_chars or "untitled"
    
    def validate_json_data(self, data: Any) -> bool:
        """Validate JSON data structure"""
        try:
            # Check if it's a valid dictionary
            if not isinstance(data, dict):
                return False
            
            # Check for required fields
            if 'question' in data or 'answer' in data:
                if 'question' in data and not self.validate_question(data['question']):
                    return False
                if 'answer' in data and not self.validate_answer(data['answer']):
                    return False
            
            # Check for nested dangerous content
            return self._validate_dict_recursive(data)
        
        except Exception as e:
            logger.error("JSON validation error", exc_info=True)
            return False
    
    def _validate_dict_recursive(self, data: dict, max_depth: int = 10) -> bool:
        """Recursively validate dictionary content"""
        if max_depth <= 0:
            return False
        
        for key, value in data.items():
            # Validate keys
            if isinstance(key, str) and self._contains_dangerous_patterns(key):
                return False
            
            # Validate values
            if isinstance(value, str):
                if self._contains_dangerous_patterns(value):
                    return False
            elif isinstance(value, dict):
                if not self._validate_dict_recursive(value, max_depth - 1):
                    return False
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and self._contains_dangerous_patterns(item):
                        return False
        
        return True

class SafeInput:
    """Safe input wrapper with automatic validation and sanitization"""
    
    def __init__(self):
        self.validator = InputValidator()
    
    def get_question(self, raw_input: str) -> Optional[str]:
        """Get safely validated question"""
        try:
            sanitized = self.validator.sanitize_text(raw_input)
            if self.validator.validate_question(sanitized):
                return sanitized
            return None
        except Exception as e:
            logger.error("Error getting safe question", exc_info=True)
            return None
    
    def get_answer(self, raw_input: str) -> Optional[str]:
        """Get safely validated answer"""
        try:
            sanitized = self.validator.sanitize_text(raw_input)
            if self.validator.validate_answer(sanitized):
                return sanitized
            return None
        except Exception as e:
            logger.error("Error getting safe answer", exc_info=True)
            return None
    
    def get_voice_command(self, raw_input: str) -> Optional[str]:
        """Get safely validated voice command"""
        try:
            sanitized = self.validator.sanitize_text(raw_input)
            if self.validator.validate_voice_command(sanitized):
                return sanitized
            return None
        except Exception as e:
            logger.error("Error getting safe voice command", exc_info=True)
            return None

# Global instances
validator = InputValidator()
safe_input = SafeInput()

# Helper functions
def sanitize_user_input(text: str) -> str:
    """Sanitize user input text"""
    return validator.sanitize_text(text)

def validate_teaching_input(question: str, answer: str) -> bool:
    """Validate teaching input (question and answer pair)"""
    return validator.validate_question(question) and validator.validate_answer(answer)

def is_safe_input(text: str) -> bool:
    """Check if input is safe"""
    if not text:
        return False
    # Basic safety check - allow most text, especially Hindi/Hinglish
    has_hindi = any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in text)
    if has_hindi:
        # Hindi text is generally safe for our use case
        return True
    return not validator._contains_dangerous_patterns(text)