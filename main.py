#!/usr/bin/env python3
"""
Main entry point for Adaptive Chatbot
"""

if __name__ == "__main__":
    try:
        # Try to import the main chatbot
        from core.chatbot_clean import main
        main()
    except ImportError:
        # Fallback to simple chatbot
        print("Using simple fallback chatbot...")
        from simple_chatbot import main
        main()
    except Exception as e:
        print(f"Error starting chatbot: {e}")
        print("Please check dependencies and configuration.") 
