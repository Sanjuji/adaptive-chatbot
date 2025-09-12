"""
Learning mechanism for the Adaptive Chatbot
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re

from .knowledge_store import KnowledgeStore


class LearningManager:
    """
    Manages the learning process for the chatbot.
    Handles training data import, interactive learning, and knowledge validation.
    """
    
    def __init__(self, knowledge_store: KnowledgeStore):
        """Initialize the learning manager."""
        self.knowledge_store = knowledge_store
        self.pending_knowledge = []  # Knowledge waiting for validation
        
    def import_knowledge_file(self, filepath: str, domain: str = "general") -> Tuple[int, int]:
        """
        Import knowledge from a JSON file.
        
        Args:
            filepath: Path to the JSON file
            domain: Domain to assign to imported knowledge
            
        Returns:
            Tuple of (success_count, total_count)
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                knowledge_list = json.load(f)
            
            success_count = 0
            total_count = len(knowledge_list)
            
            for knowledge in knowledge_list:
                # Ensure domain is set
                knowledge['domain'] = knowledge.get('domain', domain)
                knowledge['created_at'] = datetime.now().isoformat()
                
                if self.knowledge_store.add_knowledge(knowledge):
                    success_count += 1
                else:
                    logging.warning(f"Failed to import: {knowledge.get('input', 'Unknown')}")
            
            logging.info(f"Imported {success_count}/{total_count} knowledge entries from {filepath}")
            return success_count, total_count
            
        except Exception as e:
            logging.error(f"Error importing knowledge file: {e}")
            return 0, 0
    
    def teach_chatbot(self, user_input: str, expected_response: str, 
                     category: str = "learned", domain: str = "general", 
                     confidence: float = 1.0) -> bool:
        """
        Teach the chatbot a new input-response pair.
        
        Args:
            user_input: The user's question or statement
            expected_response: The correct response
            category: Category for organization
            domain: Domain for the knowledge
            confidence: Confidence score (0-1)
            
        Returns:
            True if successfully learned
        """
        try:
            knowledge_entry = {
                'input': user_input.strip(),
                'response': expected_response.strip(),
                'category': category,
                'domain': domain,
                'confidence': confidence,
                'created_at': datetime.now().isoformat(),
                'usage_count': 0,
                'source': 'manual_training'
            }
            
            success = self.knowledge_store.add_knowledge(knowledge_entry)
            
            if success:
                logging.info(f"Successfully taught: {user_input[:50]}...")
                return True
            else:
                logging.error("Failed to store knowledge")
                return False
                
        except Exception as e:
            logging.error(f"Error teaching chatbot: {e}")
            return False
    
    def batch_teach(self, training_data: List[Dict[str, Any]], 
                   domain: str = "general") -> Tuple[int, int]:
        """
        Teach multiple input-response pairs in batch.
        
        Args:
            training_data: List of dictionaries with 'input' and 'response' keys
            domain: Domain for all knowledge entries
            
        Returns:
            Tuple of (success_count, total_count)
        """
        success_count = 0
        total_count = len(training_data)
        
        for data in training_data:
            if 'input' in data and 'response' in data:
                success = self.teach_chatbot(
                    data['input'],
                    data['response'],
                    data.get('category', 'learned'),
                    domain,
                    data.get('confidence', 1.0)
                )
                if success:
                    success_count += 1
            else:
                logging.warning(f"Invalid training data format: {data}")
        
        logging.info(f"Batch teaching completed: {success_count}/{total_count} successful")
        return success_count, total_count
    
    def interactive_learning(self, user_message: str, bot_response: str, 
                           user_feedback: str) -> bool:
        """
        Learn from user feedback during conversation.
        
        Args:
            user_message: Original user message
            bot_response: Bot's response
            user_feedback: User's feedback (positive/negative/correction)
            
        Returns:
            True if learning occurred
        """
        try:
            feedback_lower = user_feedback.lower()
            
            # Positive feedback - increase confidence
            if any(word in feedback_lower for word in ['good', 'correct', 'right', 'sahi', 'achha']):
                self._reinforce_knowledge(user_message, bot_response)
                return True
            
            # Negative feedback - decrease confidence or learn correction
            elif any(word in feedback_lower for word in ['wrong', 'incorrect', 'bad', 'galat', 'nahi']):
                self._decrease_confidence(user_message, bot_response)
                return True
            
            # Correction provided
            elif any(word in feedback_lower for word in ['actually', 'correct answer', 'sach mein']):
                # Extract the correction
                correction = self._extract_correction(user_feedback)
                if correction:
                    return self.teach_chatbot(user_message, correction, "corrected")
            
            return False
            
        except Exception as e:
            logging.error(f"Error in interactive learning: {e}")
            return False
    
    def _reinforce_knowledge(self, user_input: str, response: str) -> None:
        """Reinforce existing knowledge by updating confidence."""
        # Find matching knowledge entry
        knowledge_entries = self.knowledge_store.search_by_keywords(
            self._extract_keywords(user_input)
        )
        
        for entry in knowledge_entries:
            if entry['input'] == user_input and entry['response'] == response:
                # Increase usage count and confidence
                self.knowledge_store.update_usage_count(entry['id'])
                # Could also update confidence score if needed
                break
    
    def _decrease_confidence(self, user_input: str, response: str) -> None:
        """Decrease confidence of knowledge that received negative feedback."""
        knowledge_entries = self.knowledge_store.search_by_keywords(
            self._extract_keywords(user_input)
        )
        
        for entry in knowledge_entries:
            if entry['input'] == user_input and entry['response'] == response:
                # Could implement confidence decrease logic here
                logging.info(f"Negative feedback recorded for: {user_input[:50]}...")
                break
    
    def _extract_correction(self, feedback: str) -> Optional[str]:
        """Extract correction from user feedback."""
        # Simple extraction - could be improved with NLP
        patterns = [
            r'actually (.+)',
            r'correct answer is (.+)',
            r'it should be (.+)',
            r'sach mein (.+)',
            r'correct (.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, feedback, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for searching."""
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                      'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were',
                      'kya', 'hai', 'ka', 'ki', 'ke', 'ko', 'me', 'se'}
        
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        return keywords[:10]
    
    def validate_knowledge(self, knowledge_id: int, is_valid: bool) -> bool:
        """
        Validate a knowledge entry.
        
        Args:
            knowledge_id: ID of the knowledge entry
            is_valid: Whether the knowledge is valid
            
        Returns:
            True if validation was successful
        """
        try:
            if is_valid:
                # Knowledge is valid - could increase confidence
                logging.info(f"Knowledge {knowledge_id} validated as correct")
                return True
            else:
                # Knowledge is invalid - could decrease confidence or delete
                logging.info(f"Knowledge {knowledge_id} marked as invalid")
                # For now, we'll keep it but could implement deletion logic
                return True
                
        except Exception as e:
            logging.error(f"Error validating knowledge: {e}")
            return False
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about the learning process."""
        try:
            knowledge_stats = self.knowledge_store.get_stats()
            
            # Add learning-specific stats
            learning_stats = {
                'total_knowledge_entries': knowledge_stats.get('total_entries', 0),
                'domains': knowledge_stats.get('domains', {}),
                'categories': knowledge_stats.get('categories', {}),
                'most_used_knowledge': knowledge_stats.get('most_used', []),
                'pending_validations': len(self.pending_knowledge)
            }
            
            return learning_stats
            
        except Exception as e:
            logging.error(f"Error getting learning stats: {e}")
            return {}
    
    def suggest_improvements(self) -> List[Dict[str, Any]]:
        """Suggest improvements based on usage patterns."""
        suggestions = []
        
        try:
            stats = self.knowledge_store.get_stats()
            
            # Suggest adding knowledge for domains with few entries
            for domain, count in stats.get('domains', {}).items():
                if count < 10:
                    suggestions.append({
                        'type': 'add_knowledge',
                        'domain': domain,
                        'message': f"Domain '{domain}' has only {count} knowledge entries. Consider adding more."
                    })
            
            # Suggest reviewing unused knowledge
            all_knowledge = self.knowledge_store.get_all_knowledge()
            unused_count = sum(1 for k in all_knowledge if k.get('usage_count', 0) == 0)
            
            if unused_count > 0:
                suggestions.append({
                    'type': 'review_unused',
                    'count': unused_count,
                    'message': f"{unused_count} knowledge entries have never been used. Consider reviewing them."
                })
            
        except Exception as e:
            logging.error(f"Error generating suggestions: {e}")
        
        return suggestions
    
    def export_training_data(self, filepath: str, domain: str = None) -> bool:
        """
        Export knowledge as training data.
        
        Args:
            filepath: Path to save the training data
            domain: Optional domain filter
            
        Returns:
            True if export was successful
        """
        try:
            if domain:
                knowledge_list = self.knowledge_store.get_knowledge_by_domain(domain)
            else:
                knowledge_list = self.knowledge_store.get_all_knowledge()
            
            # Format for training
            training_data = []
            for knowledge in knowledge_list:
                training_data.append({
                    'input': knowledge['input'],
                    'response': knowledge['response'],
                    'category': knowledge.get('category', 'general'),
                    'domain': knowledge.get('domain', 'general'),
                    'confidence': knowledge.get('confidence', 1.0),
                    'usage_count': knowledge.get('usage_count', 0)
                })
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, ensure_ascii=False, indent=2)
            
            logging.info(f"Exported {len(training_data)} training entries to {filepath}")
            return True
            
        except Exception as e:
            logging.error(f"Error exporting training data: {e}")
            return False
