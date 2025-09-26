#!/usr/bin/env python3
"""
Core Chatbot Logic

This module contains the primary AdaptiveChatbot class, which orchestrates all
subsystems, including conversation management, NLP processing, voice I/O,
and state management.
"""

import asyncio
import time
from typing import Dict, Any

from conversation.manager import get_conversation_manager
from nlp.engine import get_nlp_engine
from voice.manager import get_voice_manager
from utils.logger import get_logger
from core.state_manager import get_state_manager

class AdaptiveChatbot:
    """
    The central orchestrator for the chatbot. It integrates all components
    to manage the conversation flow from user input to system response.
    """

    def __init__(self, config: Dict[str, Any], logger):
        self.config = config
        self.logger = logger
        self.is_running = False

        self.logger.info("Initializing chatbot subsystems...")
        # Initialize and connect all major components
        self.state_manager = get_state_manager(config.get('state'))
        self.conversation_manager = get_conversation_manager(config.get('conversation'))
        self.nlp_engine = get_nlp_engine(config.get('nlp'))
        self.voice_manager = get_voice_manager(config.get('voice'))
        self.logger.info("All subsystems initialized.")

    async def process_input(self, user_input: str, session_id: str) -> str:
        """
        Processes user input through the full NLP and conversation pipeline.
        
        Args:
            user_input: The text input from the user.
            session_id: The unique identifier for the current conversation session.

        Returns:
            The generated text response to be delivered to the user.
        """
        start_time = time.time()
        self.logger.info(f"Processing input for session {session_id}: '{user_input[:50]}...'")

        # 1. NLP Analysis
        nlp_analysis = await self.nlp_engine.analyze(user_input)
        self.logger.debug(f"NLP Analysis complete: Intent='{nlp_analysis.get('intent')}', Language='{nlp_analysis.get('language')}'")

        # 2. Get conversation context
        context = self.state_manager.get_session_context(session_id)
        context.update({'nlp': nlp_analysis})

        # 3. Generate a response using the conversation manager
        response_text = await self.conversation_manager.generate_response(user_input, context)
        self.logger.debug(f"Generated response: '{response_text[:50]}...'")

        # 4. Update state
        self.state_manager.update_session(session_id, user_input, response_text)

        # 5. Text-to-Speech
        if self.voice_manager.is_enabled():
            await self.voice_manager.speak(response_text, language=nlp_analysis.get('language', 'en'))

        processing_time = (time.time() - start_time) * 1000
        self.logger.info(f"Input processed in {processing_time:.2f} ms.")

        return response_text

    def start(self, mode: str = 'voice'):
        """
        Starts the main loop of the chatbot based on the selected mode.
        """
        self.is_running = True
        self.logger.info(f"Chatbot started in '{mode}' mode.")

        if mode == 'voice':
            # The voice manager handles the continuous listening loop
            asyncio.run(self.voice_manager.start_listening_loop(self.process_input))
        elif mode == 'text':
            # A simple CLI for text-based interaction
            self._run_text_cli()
        else:
            self.logger.warning(f"Unknown mode '{mode}'. Defaulting to text mode.")
            self._run_text_cli()

    def _run_text_cli(self):
        """Runs a simple command-line interface for text interaction."""
        session_id = self.state_manager.create_session()
        print("Chatbot is ready. Type 'exit' to quit.")
        while self.is_running:
            try:
                user_input = input("You: ")
                if user_input.lower() in ['exit', 'quit']:
                    break
                
                response = asyncio.run(self.process_input(user_input, session_id))
                print(f"Bot: {response}")

            except (KeyboardInterrupt, EOFError):
                break
        self.shutdown()

    def shutdown(self):
        """Gracefully shuts down the chatbot and its components."""
        if not self.is_running:
            return
        self.logger.info("Shutting down chatbot...")
        self.is_running = False
        self.voice_manager.shutdown()
        self.state_manager.save_all_sessions()
        self.logger.info("Chatbot has been shut down.")