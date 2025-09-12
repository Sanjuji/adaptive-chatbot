"""
Adaptive Chatbot - Core chatbot class with learning capabilities
"""

import json
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import re

from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .knowledge_store import KnowledgeStore
from .config import Config


class AdaptiveChatbot:
    """
    Main chatbot class that can learn and adapt from conversations.
    Supports multiple domains and persistent knowledge storage.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the chatbot with configuration and models."""
        self.config = Config(config_path)
        self.knowledge_store = KnowledgeStore(self.config.database_path)
        
        # Initialize sentence transformer model for embeddings
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logging.error(f"Failed to load sentence transformer model: {e}")
            self.sentence_model = None
        
        # Current conversation context
        self.conversation_history = []
        self.current_domain = "general"
        
        # Learning parameters
        self.confidence_threshold = 0.7
        self.max_context_length = 5
        
        logging.info("AdaptiveChatbot initialized successfully")
    
    def set_domain(self, domain: str) -> None:
        """Set the current domain for the chatbot (e.g., 'shop', 'general')."""
        self.current_domain = domain
        logging.info(f"Domain set to: {domain}")
    
    def process_message(self, user_message: str) -> str:
        """
        Process a user message and generate a response.
        This includes learning from the conversation.
        """
        # Clean and normalize the message
        cleaned_message = self._clean_message(user_message)
        
        # Add to conversation history
        self.conversation_history.append({
            'type': 'user',
            'message': cleaned_message,
            'timestamp': datetime.now().isoformat(),
            'domain': self.current_domain
        })
        
        # Trim conversation history if too long
        if len(self.conversation_history) > self.max_context_length * 2:
            self.conversation_history = self.conversation_history[-self.max_context_length * 2:]
        
        # Find relevant knowledge
        relevant_info = self._find_relevant_knowledge(cleaned_message)
        
        # Generate response
        response = self._generate_response(cleaned_message, relevant_info)
        
        # Add response to conversation history
        self.conversation_history.append({
            'type': 'bot',
            'message': response,
            'timestamp': datetime.now().isoformat(),
            'domain': self.current_domain
        })
        
        return response
    
    def learn_from_input(self, user_input: str, expected_response: str, 
                        category: str = None) -> bool:
        """
        Teach the chatbot new information.
        
        Args:
            user_input: The user's question or statement
            expected_response: The correct response to learn
            category: Optional category for organization
        
        Returns:
            True if learning was successful
        """
        try:
            # Clean inputs
            cleaned_input = self._clean_message(user_input)
            cleaned_response = self._clean_message(expected_response)
            
            # Create knowledge entry
            knowledge_entry = {
                'input': cleaned_input,
                'response': cleaned_response,
                'category': category or 'learned',
                'domain': self.current_domain,
                'confidence': 1.0,  # High confidence for manually taught information
                'created_at': datetime.now().isoformat(),
                'usage_count': 0
            }
            
            # Store in knowledge base
            success = self.knowledge_store.add_knowledge(knowledge_entry)
            
            if success:
                logging.info(f"Successfully learned: {cleaned_input[:50]}...")
                return True
            else:
                logging.error("Failed to store knowledge")
                return False
                
        except Exception as e:
            logging.error(f"Error during learning: {e}")
            return False
    
    def _find_relevant_knowledge(self, message: str) -> List[Dict[str, Any]]:
        """Find relevant knowledge entries for the given message."""
        if not self.sentence_model:
            # Fallback to keyword matching if no sentence model
            return self._keyword_search(message)
        
        try:
            # Get message embedding
            message_embedding = self.sentence_model.encode([message])
            
            # Get all knowledge entries for current domain
            all_knowledge = self.knowledge_store.get_knowledge_by_domain(
                self.current_domain
            )
            
            if not all_knowledge:
                # Try general domain if nothing found
                all_knowledge = self.knowledge_store.get_knowledge_by_domain("general")
            
            if not all_knowledge:
                return []
            
            # Calculate similarities
            relevant_entries = []
            for entry in all_knowledge:
                try:
                    input_embedding = self.sentence_model.encode([entry['input']])
                    similarity = cosine_similarity(message_embedding, input_embedding)[0][0]
                    
                    if similarity > self.confidence_threshold:
                        entry['similarity'] = similarity
                        relevant_entries.append(entry)
                except Exception as e:
                    logging.warning(f"Error calculating similarity: {e}")
                    continue
            
            # Sort by similarity
            relevant_entries.sort(key=lambda x: x['similarity'], reverse=True)
            
            return relevant_entries[:3]  # Return top 3 matches
            
        except Exception as e:
            logging.error(f"Error finding relevant knowledge: {e}")
            return self._keyword_search(message)
    
    def _keyword_search(self, message: str) -> List[Dict[str, Any]]:
        """Fallback keyword-based search."""
        keywords = self._extract_keywords(message)
        return self.knowledge_store.search_by_keywords(keywords, self.current_domain)
    
    def _extract_keywords(self, message: str) -> List[str]:
        """Extract meaningful keywords from a message."""
        # Simple keyword extraction - can be improved with NLP
        words = re.findall(r'\b\w+\b', message.lower())
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                      'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were',
                      'kya', 'hai', 'ka', 'ki', 'ke', 'ko', 'me', 'se'}
        
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return keywords[:10]  # Return top 10 keywords
    
    def _generate_response(self, message: str, relevant_info: List[Dict[str, Any]]) -> str:
        """Generate a response based on the message and relevant knowledge."""
        if relevant_info:
            # Use the most relevant response
            best_match = relevant_info[0]
            
            # Update usage count
            self.knowledge_store.update_usage_count(best_match.get('id'))
            
            response = best_match['response']
            
            # Add some variability to avoid robotic responses
            if len(relevant_info) > 1:
                # Could potentially blend multiple responses or pick randomly
                pass
            
            return response
        else:
            # No relevant knowledge found, use default responses
            return self._get_default_response(message)
    
    def _get_default_response(self, message: str) -> str:
        """Generate default response when no knowledge is found."""
        # Check if it's a greeting
        if any(greeting in message.lower() for greeting in ['hello', 'hi', 'hey', 'namaste', 'namaskar']):
            return "Hello! Main aapki kaise madad kar sakta hun? Aap mujhe kuch bhi puch sakte hain ya naya kuch sikha sakte hain."
        
        # Check if it's a learning request
        if any(teach in message.lower() for teach in ['sikha', 'teach', 'learn', 'yaad']):
            return "Bilkul! Aap mujhe kuch naya sikha sakte hain. Bas batayiye ki kya seekhna hai. Main yaad rakh lunga aur aage use karunga."
        
        # Check for shop-related queries
        if self.current_domain == 'shop' and any(word in message.lower() for word in ['price', 'cost', 'kitne', 'kya rate', 'available']):
            return "Main abhi is product ke bare mein nahi janta, lekin aap mujhe sikha sakte hain. Kripaya batayiye ki is item ka price kya hai ya koi aur details?"
        
        # General response
        return ("Maaf kijiye, main is bare mein nahi janta. Kya aap mujhe sikha sakte hain? "
                "Ya phir koi aur sawal puch sakte hain jiske bare mein main janta hun.")
    
    def _clean_message(self, message: str) -> str:
        """Clean and normalize message text."""
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', message.strip())
        
        # Could add more cleaning steps like:
        # - Spelling correction
        # - Removing special characters
        # - Normalizing numbers
        
        return cleaned
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about the chatbot's knowledge."""
        return self.knowledge_store.get_stats()
    
    def export_knowledge(self, filepath: str) -> bool:
        """Export knowledge to a JSON file."""
        try:
            knowledge = self.knowledge_store.get_all_knowledge()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(knowledge, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logging.error(f"Error exporting knowledge: {e}")
            return False
    
    def import_knowledge(self, filepath: str) -> bool:
        """Import knowledge from a JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                knowledge_list = json.load(f)
            
            success_count = 0
            for knowledge in knowledge_list:
                if self.knowledge_store.add_knowledge(knowledge):
                    success_count += 1
            
            logging.info(f"Imported {success_count}/{len(knowledge_list)} knowledge entries")
            return success_count > 0
            
        except Exception as e:
            logging.error(f"Error importing knowledge: {e}")
            return False
    
    def clear_conversation_history(self) -> None:
        """Clear the current conversation history."""
        self.conversation_history = []
        logging.info("Conversation history cleared")
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the current conversation history."""
        return self.conversation_history.copy()
