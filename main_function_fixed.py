def main():
    \"\"\"Main function\"\"\"
    parser = argparse.ArgumentParser(description='Adaptive Chatbot - AI Assistant that learns from you')
    parser.add_argument('--mode', choices=['menu', 'voice', 'text'], default='menu',
                       help='Start mode: menu (default), voice, or text')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--version', action='version', 
                       version=f'Adaptive Chatbot v{config.get(\"app\", \"version\", \"1.0.0\")}')

    args = parser.parse_args()

    # Set debug mode
    if args.debug:
        config.set('app', 'debug_mode', True)
        logger.info(\"Debug mode enabled\")

    try:
        # Initialize chatbot
        chatbot = AdaptiveChatbot(config, logger)

        # Run based on mode
        if args.mode == 'menu':
            chatbot.run_interactive_menu()
        elif args.mode == 'voice':
            chatbot.run_voice_chat()
        elif args.mode == 'text':
            chatbot.run_text_chat()

    except KeyboardInterrupt:
        logger.info(\"\\nApplication interrupted by user\")
    except Exception as e:
        logger.error(\"Application error\", error=e)
        print(f\"[ERROR] Critical error: {e}\")
        sys.exit(1)

if __name__ == \"__main__\":
    main()