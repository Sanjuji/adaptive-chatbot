#!/usr/bin/env python3
"""
Shared Logging Utility

Configures a standardized logger for consistent logging across the application.
"""

import logging
import sys
from pathlib import Path

_logger_instance = None

def setup_logger(log_level=logging.INFO, log_file="logs/app.log"):
    """
    Configures and returns a logger instance.
    
    This function is designed to be called once at application startup.
    """
    global _logger_instance
    if _logger_instance:
        return _logger_instance

    # Ensure logs directory exists
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger("AdaptiveChatbot")
    logger.setLevel(log_level)
    logger.propagate = False  # Prevent duplicate logs in parent loggers

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # Create file handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG) # Log debug level to file
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Add handlers to the logger
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    _logger_instance = logger
    return logger

def get_logger():
    """
    Returns the singleton logger instance.
    
    If the logger has not been set up, it will be initialized with default settings.
    """
    if _logger_instance is None:
        return setup_logger()
    return _logger_instance

# The old helper functions are no longer needed as modules can now call
# from utils.logger import get_logger
# logger = get_logger()
# logger.info("message")
