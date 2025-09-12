"""
Knowledge Store - SQLite-based persistent storage for chatbot knowledge
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class KnowledgeStore:
    """
    Handles persistent storage and retrieval of chatbot knowledge using SQLite.
    """
    
    def __init__(self, db_path: str = "data/knowledge.db"):
        """Initialize the knowledge store with database connection."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
        logging.info(f"KnowledgeStore initialized with database: {self.db_path}")
    
    def _init_database(self) -> None:
        """Initialize the database schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create knowledge table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS knowledge (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        input TEXT NOT NULL,
                        response TEXT NOT NULL,
                        category TEXT DEFAULT 'general',
                        domain TEXT DEFAULT 'general',
                        confidence REAL DEFAULT 1.0,
                        created_at TEXT NOT NULL,
                        updated_at TEXT,
                        usage_count INTEGER DEFAULT 0,
                        metadata TEXT,
                        UNIQUE(input, domain)
                    )
                """)
                
                # Create indexes for better search performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_domain ON knowledge(domain)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_category ON knowledge(category)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_input ON knowledge(input)
                """)
                
                # Create conversation log table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        message_type TEXT NOT NULL,
                        message TEXT NOT NULL,
                        response TEXT,
                        domain TEXT DEFAULT 'general',
                        timestamp TEXT NOT NULL,
                        metadata TEXT
                    )
                """)
                
                conn.commit()
                logging.info("Database schema initialized successfully")
                
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise
    
    def add_knowledge(self, knowledge: Dict[str, Any]) -> bool:
        """
        Add new knowledge to the store.
        
        Args:
            knowledge: Dictionary containing knowledge data
            
        Returns:
            True if successfully added, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Prepare metadata
                metadata = {}
                for key in ['tags', 'source', 'validation_status']:
                    if key in knowledge:
                        metadata[key] = knowledge[key]
                
                cursor.execute("""
                    INSERT OR REPLACE INTO knowledge 
                    (input, response, category, domain, confidence, created_at, 
                     updated_at, usage_count, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    knowledge['input'],
                    knowledge['response'],
                    knowledge.get('category', 'general'),
                    knowledge.get('domain', 'general'),
                    knowledge.get('confidence', 1.0),
                    knowledge.get('created_at', datetime.now().isoformat()),
                    datetime.now().isoformat(),
                    knowledge.get('usage_count', 0),
                    json.dumps(metadata) if metadata else None
                ))
                
                conn.commit()
                logging.debug(f"Added knowledge: {knowledge['input'][:50]}...")
                return True
                
        except Exception as e:
            logging.error(f"Error adding knowledge: {e}")
            return False
    
    def get_knowledge_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Get all knowledge entries for a specific domain."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM knowledge 
                    WHERE domain = ? 
                    ORDER BY usage_count DESC, created_at DESC
                """, (domain,))
                
                results = []
                for row in cursor.fetchall():
                    knowledge = dict(row)
                    if knowledge['metadata']:
                        try:
                            metadata = json.loads(knowledge['metadata'])
                            knowledge.update(metadata)
                        except:
                            pass
                    results.append(knowledge)
                
                return results
                
        except Exception as e:
            logging.error(f"Error getting knowledge by domain: {e}")
            return []
    
    def search_by_keywords(self, keywords: List[str], domain: str = None) -> List[Dict[str, Any]]:
        """Search knowledge by keywords."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Build search query
                keyword_conditions = []
                params = []
                
                for keyword in keywords:
                    keyword_conditions.append("(input LIKE ? OR response LIKE ?)")
                    params.extend([f"%{keyword}%", f"%{keyword}%"])
                
                query = f"""
                    SELECT *, 
                    ({' + '.join(['(CASE WHEN input LIKE ? OR response LIKE ? THEN 1 ELSE 0 END)' for _ in keywords])}) as relevance_score
                    FROM knowledge 
                    WHERE ({' OR '.join(keyword_conditions)})
                """
                
                # Add domain filter if specified
                if domain:
                    query += " AND domain = ?"
                    params.append(domain)
                
                query += " ORDER BY relevance_score DESC, usage_count DESC"
                
                # Add keyword parameters for relevance scoring
                relevance_params = []
                for keyword in keywords:
                    relevance_params.extend([f"%{keyword}%", f"%{keyword}%"])
                
                all_params = relevance_params + params
                cursor.execute(query, all_params)
                
                results = []
                for row in cursor.fetchall():
                    knowledge = dict(row)
                    if knowledge['metadata']:
                        try:
                            metadata = json.loads(knowledge['metadata'])
                            knowledge.update(metadata)
                        except:
                            pass
                    results.append(knowledge)
                
                return results[:10]  # Return top 10 matches
                
        except Exception as e:
            logging.error(f"Error searching by keywords: {e}")
            return []
    
    def update_usage_count(self, knowledge_id: int) -> bool:
        """Update the usage count for a knowledge entry."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE knowledge 
                    SET usage_count = usage_count + 1,
                        updated_at = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), knowledge_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logging.error(f"Error updating usage count: {e}")
            return False
    
    def delete_knowledge(self, knowledge_id: int) -> bool:
        """Delete a knowledge entry."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM knowledge WHERE id = ?", (knowledge_id,))
                conn.commit()
                
                return cursor.rowcount > 0
                
        except Exception as e:
            logging.error(f"Error deleting knowledge: {e}")
            return False
    
    def get_knowledge_by_id(self, knowledge_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific knowledge entry by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM knowledge WHERE id = ?", (knowledge_id,))
                row = cursor.fetchone()
                
                if row:
                    knowledge = dict(row)
                    if knowledge['metadata']:
                        try:
                            metadata = json.loads(knowledge['metadata'])
                            knowledge.update(metadata)
                        except:
                            pass
                    return knowledge
                
                return None
                
        except Exception as e:
            logging.error(f"Error getting knowledge by ID: {e}")
            return None
    
    def get_all_knowledge(self) -> List[Dict[str, Any]]:
        """Get all knowledge entries."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM knowledge 
                    ORDER BY domain, category, created_at DESC
                """)
                
                results = []
                for row in cursor.fetchall():
                    knowledge = dict(row)
                    if knowledge['metadata']:
                        try:
                            metadata = json.loads(knowledge['metadata'])
                            knowledge.update(metadata)
                        except:
                            pass
                    results.append(knowledge)
                
                return results
                
        except Exception as e:
            logging.error(f"Error getting all knowledge: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge store."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total entries
                cursor.execute("SELECT COUNT(*) FROM knowledge")
                total_entries = cursor.fetchone()[0]
                
                # Entries by domain
                cursor.execute("""
                    SELECT domain, COUNT(*) 
                    FROM knowledge 
                    GROUP BY domain 
                    ORDER BY COUNT(*) DESC
                """)
                domain_stats = dict(cursor.fetchall())
                
                # Entries by category
                cursor.execute("""
                    SELECT category, COUNT(*) 
                    FROM knowledge 
                    GROUP BY category 
                    ORDER BY COUNT(*) DESC
                """)
                category_stats = dict(cursor.fetchall())
                
                # Most used entries
                cursor.execute("""
                    SELECT input, usage_count 
                    FROM knowledge 
                    WHERE usage_count > 0
                    ORDER BY usage_count DESC 
                    LIMIT 5
                """)
                most_used = [{'input': row[0], 'usage_count': row[1]} 
                            for row in cursor.fetchall()]
                
                return {
                    'total_entries': total_entries,
                    'domains': domain_stats,
                    'categories': category_stats,
                    'most_used': most_used
                }
                
        except Exception as e:
            logging.error(f"Error getting stats: {e}")
            return {}
    
    def log_conversation(self, session_id: str, message_type: str, 
                        message: str, response: str = None, 
                        domain: str = "general", metadata: Dict = None) -> bool:
        """Log a conversation turn."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO conversations 
                    (session_id, message_type, message, response, domain, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    message_type,
                    message,
                    response,
                    domain,
                    datetime.now().isoformat(),
                    json.dumps(metadata) if metadata else None
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logging.error(f"Error logging conversation: {e}")
            return False
    
    def get_conversation_history(self, session_id: str = None, 
                               limit: int = 100) -> List[Dict[str, Any]]:
        """Get conversation history."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if session_id:
                    cursor.execute("""
                        SELECT * FROM conversations 
                        WHERE session_id = ?
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    """, (session_id, limit))
                else:
                    cursor.execute("""
                        SELECT * FROM conversations 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    """, (limit,))
                
                results = []
                for row in cursor.fetchall():
                    conv = dict(row)
                    if conv['metadata']:
                        try:
                            metadata = json.loads(conv['metadata'])
                            conv.update(metadata)
                        except:
                            pass
                    results.append(conv)
                
                return results
                
        except Exception as e:
            logging.error(f"Error getting conversation history: {e}")
            return []
    
    def cleanup_old_conversations(self, days: int = 30) -> int:
        """Clean up old conversation logs."""
        try:
            cutoff_date = datetime.now().replace(microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM conversations 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logging.info(f"Cleaned up {deleted_count} old conversation entries")
                return deleted_count
                
        except Exception as e:
            logging.error(f"Error cleaning up conversations: {e}")
            return 0
