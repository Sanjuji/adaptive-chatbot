#!/usr/bin/env python3
"""
Unified Learning Manager for Adaptive Chatbot
Consolidates all learning functionality with robust error handling
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import threading
from config import config
from logger import log_info, log_error, log_warning, log_learning_event
from validators import safe_input, validate_teaching_input
from hindi_transliterator import transliterate_hindi, normalize_hindi_query, get_query_variations

class LearningManagerError(Exception):
    """Custom exception for learning manager errors"""
    pass

class UnifiedLearningManager:
    """Production-ready learning manager with comprehensive error handling"""
    
    def __init__(self, knowledge_file: str = None):
        self.knowledge_file = knowledge_file or config.get_knowledge_file_path()
        self.knowledge_base = {}
        self.knowledge_lock = threading.Lock()
        self.backup_enabled = config.get('learning', 'backup_enabled', True)
        self.max_entries = config.get('learning', 'max_knowledge_entries', 10000)
        
        # Performance monitoring
        self._memory_limit_mb = config.get('learning', 'memory_limit_mb', 100)
        self._access_count = 0
        self._last_cleanup = datetime.now()
        
        # Initialize knowledge base with error recovery
        if not self._load_knowledge_base():
            log_warning("Knowledge base initialization failed, starting with empty base")
    
    def _load_knowledge_base(self) -> bool:
        """Load knowledge base from file with error handling"""
        try:
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    self.knowledge_base = json.load(f)
                
                log_info(f"Knowledge base loaded: {len(self.knowledge_base)} entries")
                return True
            else:
                # Create empty knowledge base
                self.knowledge_base = {}
                self._save_knowledge_base()  # Create file
                log_info("Created new knowledge base file")
                return True
                
        except json.JSONDecodeError as e:
            log_error("Invalid JSON in knowledge file", error=e)
            # Backup corrupted file and start fresh
            self._backup_corrupted_file()
            self.knowledge_base = {}
            return False
            
        except Exception as e:
            log_error("Failed to load knowledge base", error=e)
            self.knowledge_base = {}
            return False
    
    def _save_knowledge_base(self) -> bool:
        """Save knowledge base to file with error handling"""
        try:
            # Create backup if enabled
            if self.backup_enabled and os.path.exists(self.knowledge_file):
                self._create_backup()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.knowledge_file), exist_ok=True)
            
            # Write to temporary file first
            temp_file = f"{self.knowledge_file}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
            
            # Atomic move
            if os.name == 'nt':  # Windows
                if os.path.exists(self.knowledge_file):
                    os.remove(self.knowledge_file)
                os.rename(temp_file, self.knowledge_file)
            else:  # Unix-like
                os.rename(temp_file, self.knowledge_file)
            
            log_info(f"Knowledge base saved: {len(self.knowledge_base)} entries")
            return True
            
        except Exception as e:
            log_error("Failed to save knowledge base", error=e)
            # Clean up temp file
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
            return False
    
    def _create_backup(self):
        """Create backup of current knowledge file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{self.knowledge_file}.backup_{timestamp}"
            
            with open(self.knowledge_file, 'r', encoding='utf-8') as src:
                with open(backup_file, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            log_info(f"Backup created: {backup_file}")
            
            # Clean old backups (keep only last 5)
            self._cleanup_old_backups()
            
        except Exception as e:
            log_warning("Failed to create backup", error=e)
    
    def _cleanup_old_backups(self):
        """Remove old backup files"""
        try:
            backup_dir = os.path.dirname(self.knowledge_file)
            backup_files = []
            
            for file in os.listdir(backup_dir):
                if file.startswith(os.path.basename(self.knowledge_file) + '.backup_'):
                    backup_files.append(os.path.join(backup_dir, file))
            
            # Sort by creation time and keep only 5 most recent
            backup_files.sort(key=os.path.getctime, reverse=True)
            for old_backup in backup_files[5:]:
                os.remove(old_backup)
                log_info(f"Removed old backup: {old_backup}")
                
        except Exception as e:
            log_warning("Failed to cleanup old backups", error=e)
    
    def _backup_corrupted_file(self):
        """Backup corrupted knowledge file"""
        try:
            corrupted_file = f"{self.knowledge_file}.corrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(self.knowledge_file, corrupted_file)
            log_warning(f"Corrupted file backed up as: {corrupted_file}")
        except Exception as e:
            log_error("Failed to backup corrupted file", error=e)
    
    def add_knowledge(self, question: str, answer: str, metadata: Dict[str, Any] = None) -> bool:
        """Add new knowledge with comprehensive validation"""
        try:
            # Validate inputs
            safe_question = safe_input.get_question(question)
            safe_answer = safe_input.get_answer(answer)
            
            if not safe_question or not safe_answer:
                log_warning("Knowledge rejected: validation failed")
                log_learning_event(question, answer, success=False)
                return False
            
            # Check for duplicates
            if self._is_duplicate(safe_question):
                log_info(f"Knowledge already exists: {safe_question[:50]}...")
                return True  # Not an error, just already exists
            
            # Check capacity limits
            if len(self.knowledge_base) >= self.max_entries:
                log_warning(f"Knowledge base full (max {self.max_entries} entries)")
                return False
            
            with self.knowledge_lock:
                # Create knowledge entry
                entry = {
                    'answer': safe_answer,
                    'created_at': datetime.now().isoformat(),
                    'usage_count': 0,
                    'confidence': 1.0
                }
                
                # Add metadata if provided
                if metadata:
                    entry.update(metadata)
                
                # Store knowledge
                self.knowledge_base[safe_question.lower().strip()] = entry
                
                # Save to file
                if self._save_knowledge_base():
                    log_learning_event(safe_question, safe_answer, success=True)
                    return True
                else:
                    # Rollback on save failure
                    del self.knowledge_base[safe_question.lower().strip()]
                    return False
                    
        except Exception as e:
            log_error("Failed to add knowledge", error=e)
            return False
    
    def find_answer(self, query: str, update_usage: bool = True) -> Optional[str]:
        """Find answer for query with fuzzy matching and performance monitoring"""
        try:
            if not query or not isinstance(query, str):
                return None
            
            # Performance monitoring
            self._access_count += 1
            if self._access_count % 100 == 0:
                self._check_memory_usage()
                self._periodic_cleanup()
            
            # Sanitize query - but preserve Hindi characters
            clean_query = query.strip()
            if not clean_query:
                return None
            
            # Normalize and transliterate the query
            normalized_query = normalize_hindi_query(clean_query)
            query_lower = normalized_query.lower().strip()
            
            log_info(f"🔍 Searching for: Original='{clean_query}', Normalized='{query_lower}'")
            
            # Generate query variations including transliterations
            query_variations = get_query_variations(query_lower)
            normalized_queries = self._normalize_hindi_query(query_lower)
            
            # Combine all variations
            all_variations = [query_lower] + query_variations + normalized_queries
            all_variations = list(dict.fromkeys(all_variations))  # Remove duplicates while preserving order
            
            log_info(f"📝 Query variations: {all_variations[:5]}")
            
            with self.knowledge_lock:
                # Try all variations for direct match
                for variation in all_variations:
                    if variation in self.knowledge_base:
                        entry = self.knowledge_base[variation]
                        answer = entry['answer']
                        log_info(f"✅ Found match with variation: '{variation}'")
                        
                        # Update usage count
                        if update_usage:
                            entry['usage_count'] = entry.get('usage_count', 0) + 1
                            self._save_knowledge_base()
                        
                        return answer
                
                # Enhanced fuzzy matching with all variations
                best_match = None
                for variation in all_variations:
                    match = self._find_best_match(variation)
                    if match:
                        best_match = match
                        break
                
                if best_match:
                    entry = self.knowledge_base[best_match]
                    answer = entry['answer']
                    log_info(f"✅ Found fuzzy match: '{best_match}'")
                    
                    # Update usage count
                    if update_usage:
                        entry['usage_count'] = entry.get('usage_count', 0) + 1
                        # Don't save immediately for fuzzy matches to avoid excessive I/O
                    
                    return answer
                
                log_warning(f"❌ No match found for query: '{clean_query}'")
                return None
                
        except Exception as e:
            log_error("Failed to find answer", error=e)
            return None
    
    def _normalize_hindi_query(self, query: str) -> List[str]:
        """Generate normalized variations of Hindi queries for better matching"""
        variations = []
        
        # Common Hindi postposition variations
        replacements = [
            # rate/price variations FIRST (highest priority)
            (' ka price', ' ka rate'),     # wire ka price -> wire ka rate  
            (' ka rate', ' ka price'),     # wire ka rate -> wire ka price
            (' ki price', ' ki rate'),     # wire ki price -> wire ki rate
            (' ki rate', ' ki price'),     # wire ki rate -> wire ki price
            
            # Add/remove 'ka' for bare price queries
            (' ka price', ' price'),       # mcb ka price -> mcb price
            (' price', ' ki price'),       # mcb price -> mcb ki price
            (' price', ' ka price'),       # mcb price -> mcb ka price
            
            # ka/ki/ke variations
            (' ka price', ' ki price'),    # socket ka price -> socket ki price
            (' ka price', ' ke price'),    # socket ka price -> socket ke price
            (' ki price', ' ka price'),    # socket ki price -> socket ka price
            (' ki price', ' ke price'),    # socket ki price -> socket ke price
            (' ke price', ' ka price'),    # socket ke price -> socket ka price
            (' ke price', ' ki price'),    # socket ke price -> socket ki price
            
            # ka/ki without 'price' word
            ('ka ', 'ki '),               # switch ka -> switch ki
            ('ka ', 'ke '),               # switch ka -> switch ke
            ('ki ', 'ka '),               # switch ki -> switch ka
            ('ki ', 'ke '),               # switch ki -> switch ke
            ('ke ', 'ka '),               # switch ke -> switch ka
            ('ke ', 'ki '),               # switch ke -> switch ki
            
            # Common question patterns
            (' hai', ''),                 # Remove 'hai' at end
            (' he', ''),                  # Remove 'he' at end
            ('kitna ', ''),               # Remove 'kitna'
            ('kya ', ''),                 # Remove 'kya'
        ]
        
        for old_pattern, new_pattern in replacements:
            if old_pattern in query:
                variation = query.replace(old_pattern, new_pattern).strip()
                if variation != query and variation not in variations and len(variation) > 2:
                    variations.append(variation)
        
        return variations[:8]  # Allow more variations for better matching
    
    def _find_best_match(self, query: str) -> Optional[str]:
        """Find best matching question using precise fuzzy logic"""
        try:
            query_words = set(query.split())
            query_clean = query.strip().lower()
            best_match = None
            best_score = 0
            
            for question in self.knowledge_base.keys():
                question_words = set(question.split())
                question_clean = question.strip().lower()
                
                # Exact match check (should have been caught earlier)
                if query_clean == question_clean:
                    return question
                
                # Strict substring matching
                if query_clean in question_clean and len(query_clean) > 3:
                    # Only match if query is substantial part of question
                    if len(query_clean) / len(question_clean) > 0.6:
                        return question
                
                if question_clean in query_clean and len(question_clean) > 3:
                    # Only match if question is substantial part of query
                    if len(question_clean) / len(query_clean) > 0.6:
                        return question
                
                # Word overlap scoring - much more strict
                common_words = query_words.intersection(question_words)
                if len(common_words) >= 2:  # At least 2 common words
                    # Both coverage ratios must be high
                    query_coverage = len(common_words) / len(query_words)
                    question_coverage = len(common_words) / len(question_words)
                    
                    # Require high coverage on both sides
                    if query_coverage >= 0.7 and question_coverage >= 0.7:
                        score = (query_coverage + question_coverage) / 2
                        
                        if score > best_score:
                            best_score = score
                            best_match = question
            
            # Lower threshold for better Hindi/Hinglish matching (60% or better)
            if best_score >= 0.6:
                log_info(f"🎯 Fuzzy match found: '{best_match}' with score {best_score:.2f}")
                return best_match
            return None
            
        except Exception as e:
            log_error("Error in fuzzy matching", error=e)
            return None
    
    def _is_duplicate(self, question: str) -> bool:
        """Check if question already exists"""
        try:
            question_lower = question.lower().strip()
            return question_lower in self.knowledge_base
        except:
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        try:
            with self.knowledge_lock:
                total_entries = len(self.knowledge_base)
                
                if total_entries == 0:
                    return {
                        'total_entries': 0,
                        'most_used': None,
                        'least_used': None,
                        'average_usage': 0,
                        'recent_additions': 0
                    }
                
                # Calculate usage statistics
                usage_counts = [entry.get('usage_count', 0) for entry in self.knowledge_base.values()]
                avg_usage = sum(usage_counts) / len(usage_counts) if usage_counts else 0
                
                # Find most/least used
                most_used = max(self.knowledge_base.items(), 
                              key=lambda x: x[1].get('usage_count', 0))
                least_used = min(self.knowledge_base.items(), 
                               key=lambda x: x[1].get('usage_count', 0))
                
                # Recent additions (last 24 hours)
                recent_count = 0
                cutoff_time = datetime.now().timestamp() - 86400  # 24 hours
                
                for entry in self.knowledge_base.values():
                    try:
                        created_at = datetime.fromisoformat(entry.get('created_at', ''))
                        if created_at.timestamp() > cutoff_time:
                            recent_count += 1
                    except:
                        pass
                
                return {
                    'total_entries': total_entries,
                    'most_used': {
                        'question': most_used[0],
                        'count': most_used[1].get('usage_count', 0)
                    },
                    'least_used': {
                        'question': least_used[0],
                        'count': least_used[1].get('usage_count', 0)
                    },
                    'average_usage': round(avg_usage, 2),
                    'recent_additions': recent_count
                }
                
        except Exception as e:
            log_error("Failed to get statistics", error=e)
            return {'error': str(e)}
    
    def export_knowledge(self, export_file: str) -> bool:
        """Export knowledge to a file"""
        try:
            with self.knowledge_lock:
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
                
                log_info(f"Knowledge exported to: {export_file}")
                return True
                
        except Exception as e:
            log_error("Failed to export knowledge", error=e)
            return False
    
    def import_knowledge(self, import_file: str, merge: bool = True) -> Tuple[int, int]:
        """Import knowledge from a file"""
        try:
            if not os.path.exists(import_file):
                log_error(f"Import file not found: {import_file}")
                return 0, 0
            
            with open(import_file, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            if not isinstance(imported_data, dict):
                log_error("Invalid import format: expected dictionary")
                return 0, 0
            
            success_count = 0
            total_count = len(imported_data)
            
            with self.knowledge_lock:
                for question, entry in imported_data.items():
                    try:
                        # Validate entry format
                        if not isinstance(entry, dict) or 'answer' not in entry:
                            log_warning(f"Invalid entry format: {question}")
                            continue
                        
                        # Check if already exists
                        if not merge and question in self.knowledge_base:
                            continue
                        
                        # Add entry
                        self.knowledge_base[question] = entry
                        success_count += 1
                        
                    except Exception as e:
                        log_warning(f"Failed to import entry: {question}", error=e)
                        continue
                
                # Save updated knowledge base
                if success_count > 0:
                    self._save_knowledge_base()
            
            log_info(f"Imported {success_count}/{total_count} knowledge entries")
            return success_count, total_count
            
        except Exception as e:
            log_error("Failed to import knowledge", error=e)
            return 0, 0
    
    def _check_memory_usage(self):
        """Monitor memory usage and trigger cleanup if needed"""
        try:
            import sys
            # Get approximate memory usage
            kb_size = len(str(self.knowledge_base).encode('utf-8')) // 1024
            
            if kb_size > self._memory_limit_mb * 1024:  # Convert MB to KB
                log_warning(f"Knowledge base size {kb_size}KB exceeds limit {self._memory_limit_mb}MB")
                self._emergency_cleanup()
                
        except Exception as e:
            log_warning(f"Memory check failed: {e}")
    
    def _periodic_cleanup(self):
        """Periodic maintenance tasks"""
        try:
            now = datetime.now()
            if (now - self._last_cleanup).seconds > 3600:  # Every hour
                # Remove unused entries (0 usage for 30+ days)
                removed = 0
                with self.knowledge_lock:
                    cutoff_date = now.replace(day=now.day-30) if now.day > 30 else now.replace(month=now.month-1, day=30)
                    
                    to_remove = []
                    for key, entry in self.knowledge_base.items():
                        if entry.get('usage_count', 0) == 0:
                            created = datetime.fromisoformat(entry.get('created_at', now.isoformat()))
                            if created < cutoff_date:
                                to_remove.append(key)
                    
                    for key in to_remove[:50]:  # Limit bulk removals
                        del self.knowledge_base[key]
                        removed += 1
                
                if removed > 0:
                    log_info(f"Periodic cleanup: removed {removed} unused entries")
                    self._save_knowledge_base()
                
                self._last_cleanup = now
                
        except Exception as e:
            log_warning(f"Periodic cleanup failed: {e}")
    
    def _emergency_cleanup(self):
        """Emergency cleanup when memory limit exceeded"""
        try:
            with self.knowledge_lock:
                # Remove oldest, least used entries
                entries = [(k, v) for k, v in self.knowledge_base.items()]
                entries.sort(key=lambda x: (x[1].get('usage_count', 0), x[1].get('created_at', '')))
                
                # Keep only most recent 80% of entries
                keep_count = int(len(entries) * 0.8)
                entries_to_keep = entries[-keep_count:]
                
                self.knowledge_base = {k: v for k, v in entries_to_keep}
                
                removed = len(entries) - keep_count
                log_warning(f"Emergency cleanup: removed {removed} entries due to memory limit")
                
                # Force save
                self._save_knowledge_base()
                
        except Exception as e:
            log_error(f"Emergency cleanup failed: {e}")
    
    def cleanup(self):
        """Cleanup resources with comprehensive error handling"""
        try:
            log_info("Starting learning manager cleanup...")
            
            # Final memory check
            self._check_memory_usage()
            
            # Final save
            if self._save_knowledge_base():
                log_info("✅ Knowledge base saved successfully")
            else:
                log_error("❌ Failed to save knowledge base during cleanup")
            
            log_info("✅ Learning manager cleanup completed")
            
        except Exception as e:
            log_error("Learning manager cleanup failed", error=e)

# Global instance
_learning_manager = None
_learning_lock = threading.Lock()

def get_learning_manager() -> UnifiedLearningManager:
    """Get global learning manager instance (singleton pattern)"""
    global _learning_manager
    
    if _learning_manager is None:
        with _learning_lock:
            if _learning_manager is None:
                _learning_manager = UnifiedLearningManager()
    
    return _learning_manager

# Convenience functions
def learn(question: str, answer: str) -> bool:
    """Convenience function to add knowledge"""
    return get_learning_manager().add_knowledge(question, answer)

def ask(question: str) -> Optional[str]:
    """Convenience function to get answer"""
    return get_learning_manager().find_answer(question)

def get_stats() -> Dict[str, Any]:
    """Convenience function to get statistics"""
    return get_learning_manager().get_statistics()