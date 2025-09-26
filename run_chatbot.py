#!/usr/bin/env python3
"""
Adaptive Chatbot Project - Main Execution Entry Point

This script initializes and launches the chatbot application, orchestrating all
the modular components from their respective directories.
"""

import sys
import argparse
from pathlib import Path

# Ensure the project root is in the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.chatbot import AdaptiveChatbot
from utils.logger import setup_logger
from configs.loader import load_config

def main():
    """
    Main function to parse arguments, initialize components, and run the chatbot.
    """
    # 1. Setup command-line argument parsing
    parser = argparse.ArgumentParser(description="Adaptive Chatbot Runner")
    parser.add_argument(
        "--env",
        default="development",
        choices=["development", "staging", "production"],
        help="Specify the runtime environment (development, staging, production)."
    )
    parser.add_argument(
        "--mode",
        default="voice",
        choices=["voice", "text", "debug"],
        help="Specify the interaction mode (voice, text, or debug)."
    )
    args = parser.parse_args()

    # 2. Initialize core components
    # The logger is set up first to capture logs from all subsequent initializations.
    logger = setup_logger()
    logger.info(f"Starting Adaptive Chatbot in '{args.env}' environment...")

    # Load configuration based on the specified environment.
    # This allows for different settings (e.g., model paths, API keys) per environment.
    config = load_config(env=args.env)
    if not config:
        logger.critical("Failed to load configuration. Shutting down.")
        sys.exit(1)

    # 3. Launch the chatbot
    # The main chatbot class is instantiated with the loaded config and logger.
    try:
        chatbot = AdaptiveChatbot(config=config, logger=logger)
        logger.info("AdaptiveChatbot initialized successfully.")

        # The chatbot's start method handles the main application loop.
        chatbot.start(mode=args.mode)

    except Exception as e:
        logger.critical(f"A critical error occurred during chatbot startup: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()