"""
Adaptive Chatbot - A scalable chatbot that can learn and remember
"""

__version__ = "1.0.0"
__author__ = "Adaptive Chatbot"
__description__ = "A scalable chatbot that can learn and remember what you teach it"

from .chatbot import AdaptiveChatbot
from .knowledge_store import KnowledgeStore
from .learning import LearningManager
from .config import Config

__all__ = [
    'AdaptiveChatbot',
    'KnowledgeStore', 
    'LearningManager',
    'Config'
]
