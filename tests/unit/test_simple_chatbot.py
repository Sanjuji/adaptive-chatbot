import unittest
from unittest.mock import patch
from simple_chatbot import main, SimpleChatbot

class TestSimpleChatbotMain(unittest.TestCase):

    @patch('simple_chatbot.SimpleChatbot.show_stats')
    @patch('simple_chatbot.SimpleChatbot.demo_chat')
    @patch('simple_chatbot.SimpleChatbot.chat')
    @patch('builtins.input', return_value='yes')
    def test_main_starts_interactive_chat_on_yes(self, mock_input, mock_chat, mock_demo_chat, mock_show_stats):
        """
        Test that main() function starts interactive chat if user inputs 'yes'.
        """
        main()
        mock_demo_chat.assert_called_once()
        mock_show_stats.assert_called_once()
        mock_input.assert_called_once_with("\nDo you want to start an interactive chat? (yes/no): ")
        mock_chat.assert_called_once()

    @patch('simple_chatbot.SimpleChatbot.show_stats')
    @patch('simple_chatbot.SimpleChatbot.demo_chat')
    @patch('simple_chatbot.SimpleChatbot.chat')
    @patch('builtins.input', return_value='no')
    def test_main_does_not_start_interactive_chat_on_no(self, mock_input, mock_chat, mock_demo_chat, mock_show_stats):
        """
        Test that main() function does not start interactive chat if user inputs 'no'.
        """
        main()
        mock_demo_chat.assert_called_once()
        mock_show_stats.assert_called_once()
        mock_input.assert_called_once_with("\nDo you want to start an interactive chat? (yes/no): ")
        mock_chat.assert_not_called()

if __name__ == '__main__':
    unittest.main()