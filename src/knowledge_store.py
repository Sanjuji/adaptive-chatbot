"""
Knowledge Store - SQLite-based persistent storage for chatbot knowledge
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
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
        """Initialize the database schema with WAL and optional FTS5."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Pragmas for performance and durability
                try:
                    cursor.execute("PRAGMA journal_mode=WAL;")
                    cursor.execute("PRAGMA synchronous=NORMAL;")
                    cursor.execute("PRAGMA temp_store=MEMORY;")
                    # Cache size in pages; set ~64MB (assuming 4096-byte pages -> -16384 pages)
                    cursor.execute("PRAGMA cache_size=-16384;")
                except Exception as pe:
                    logging.warning(f"Failed to set SQLite pragmas: {pe}")
                
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
                
                # Create FTS5 virtual table and triggers (if available)
                try:
                    cursor.execute(
                        "CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(\n"
                        "  input,\n"
                        "  response,\n"
                        "  content='knowledge',\n"
                        "  content_rowid='id',\n"
                        "  tokenize='unicode61'\n"
                        ");"
                    )
                    # Triggers to keep FTS in sync
                    cursor.execute(
                        "CREATE TRIGGER IF NOT EXISTS knowledge_ai AFTER INSERT ON knowledge BEGIN\n"
                        "  INSERT INTO knowledge_fts(rowid, input, response) VALUES (new.id, new.input, new.response);\n"
                        "END;"
                    )
                    cursor.execute(
                        "CREATE TRIGGER IF NOT EXISTS knowledge_ad AFTER DELETE ON knowledge BEGIN\n"
                        "  INSERT INTO knowledge_fts(knowledge_fts, rowid, input, response) VALUES('delete', old.id, old.input, old.response);\n"
                        "END;"
                    )
                    cursor.execute(
                        "CREATE TRIGGER IF NOT EXISTS knowledge_au AFTER UPDATE ON knowledge BEGIN\n"
                        "  INSERT INTO knowledge_fts(knowledge_fts, rowid, input, response) VALUES('delete', old.id, old.input, old.response);\n"
                        "  INSERT INTO knowledge_fts(rowid, input, response) VALUES (new.id, new.input, new.response);\n"
                        "END;"
                    )
                    logging.info("SQLite FTS5 enabled for knowledge table")
                except sqlite3.OperationalError as fe:
                    logging.warning(f"FTS5 not available or failed to initialize: {fe}")
                
                conn.commit()
                # Best-effort: ensure FTS content is synchronized with base table
                try:
                    self.ensure_fts_sync()
                except Exception:
                    pass
                logging.info("Database schema initialized successfully (WAL, indices, FTS if available)")
                
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise

    def ensure_fts_sync(self) -> None:
        """
        Ensure FTS virtual table contains the same rows as the base table.
        This handles cases where FTS was created after rows already existed.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                try:
                    # Attempt FTS5 rebuild from content table
                    cur.execute("INSERT INTO knowledge_fts(knowledge_fts) VALUES('rebuild');")
                    conn.commit()
                    logging.info("FTS index rebuilt from content table")
                    return
                except sqlite3.OperationalError:
                    # Fall back to manual repopulation
                    try:
                        cur.execute("DELETE FROM knowledge_fts;")
                        cur.execute("INSERT INTO knowledge_fts(rowid, input, response) SELECT id, input, response FROM knowledge;")
                        conn.commit()
                        logging.info("FTS index repopulated from base table")
                    except Exception as e:
                        logging.debug(f"Manual FTS repopulation failed: {e}")
        except Exception as e:
            logging.debug(f"FTS sync skipped: {e}")
        
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
        """Search knowledge by keywords (FTS5 if available, otherwise LIKE)."""
        try:
            # Try FTS5 first using joined MATCH query
            query_text = ' '.join(keywords)
            fts_results = self.search_fulltext(query_text, domain=domain, limit=10)
            if fts_results:
                return fts_results
        except Exception as _:
            # Ignore and fallback to LIKE
            pass
        
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

    def get_inputs_for_domain(self, domain: Optional[str] = None) -> List[Tuple[int, str]]:
        """Return list of (id, input) for building semantic indexes."""
        items: List[Tuple[int, str]] = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                if domain:
                    cursor.execute("SELECT id, input FROM knowledge WHERE domain = ? ORDER BY id ASC", (domain,))
                else:
                    cursor.execute("SELECT id, input FROM knowledge ORDER BY id ASC")
                for row in cursor.fetchall():
                    items.append((row["id"], row["input"]))
        except Exception as e:
            logging.error(f"Error fetching inputs for domain: {e}")
        return items
    
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

    # -------------------- Metadata utilities --------------------
    def update_metadata(self, knowledge_id: int, updates: Dict[str, Any]) -> bool:
        """Merge update keys into the metadata JSON for a knowledge row."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT metadata FROM knowledge WHERE id = ?", (knowledge_id,))
                row = cursor.fetchone()
                if not row:
                    return False
                current_meta = {}
                if row["metadata"]:
                    try:
                        current_meta = json.loads(row["metadata"]) or {}
                    except Exception:
                        current_meta = {}
                current_meta.update(updates or {})
                cursor.execute("UPDATE knowledge SET metadata = ?, updated_at = ? WHERE id = ?",
                               (json.dumps(current_meta), datetime.now().isoformat(), knowledge_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error updating metadata: {e}")
            return False

    def set_validation_status(self, knowledge_id: int, status: str) -> bool:
        """Set validation_status in metadata for the given knowledge row."""
        return self.update_metadata(knowledge_id, {"validation_status": status})

    def get_pending_knowledge(self, domain: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Return rows whose metadata indicates validation_status == 'pending'."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                if domain:
                    cursor.execute(
                        """
                        SELECT * FROM knowledge 
                        WHERE domain = ? AND metadata LIKE '%"validation_status": "pending"%'
                        ORDER BY created_at DESC LIMIT ?
                        """,
                        (domain, limit)
                    )
                else:
                    cursor.execute(
                        """
                        SELECT * FROM knowledge 
                        WHERE metadata LIKE '%"validation_status": "pending"%'
                        ORDER BY created_at DESC LIMIT ?
                        """,
                        (limit,)
                    )
                results: List[Dict[str, Any]] = []
                for row in cursor.fetchall():
                    item = dict(row)
                    if item.get('metadata'):
                        try:
                            md = json.loads(item['metadata'])
                            item.update(md)
                        except Exception:
                            pass
                    results.append(item)
                return results
        except Exception as e:
            logging.error(f"Error getting pending knowledge: {e}")
            return []

    def search_fulltext(self, query_text: str, domain: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Full-text search using FTS5 if available, with safe fallbacks (LIKE) when no hits."""
        results: List[Dict[str, Any]] = []
        # 1) Try FTS5 (if available)
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                sql = (
                    "SELECT k.*, k.id as kid FROM knowledge_fts f "
                    "JOIN knowledge k ON k.id = f.rowid "
                    "WHERE f MATCH ?"
                )
                params: List[Any] = [query_text]
                if domain:
                    sql += " AND k.domain = ?"
                    params.append(domain)
                try:
                    sql_ranked = sql + " ORDER BY bm25(f) LIMIT ?"
                    params_ranked = params + [limit]
                    cursor.execute(sql_ranked, params_ranked)
                except sqlite3.OperationalError:
                    # Fallback without bm25 function
                    sql_plain = sql + " LIMIT ?"
                    params_plain = params + [limit]
                    cursor.execute(sql_plain, params_plain)
                for row in cursor.fetchall():
                    item = dict(row)
                    if item.get('metadata'):
                        try:
                            md = json.loads(item['metadata'])
                            item.update(md)
                        except Exception:
                            pass
                    results.append(item)
        except sqlite3.OperationalError as e:
            logging.debug(f"FTS search unavailable: {e}")
        except Exception as e:
            logging.error(f"Error in FTS search: {e}")

        # 2) If FTS yielded no results, fallback to LIKE keywords search
        if not results:
            try:
                words = [w for w in (query_text or '').split() if len(w) > 1]
                if words:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.row_factory = sqlite3.Row
                        cursor = conn.cursor()
                        keyword_conditions = []
                        params: List[Any] = []
                        for w in words:
                            keyword_conditions.append("(input LIKE ? OR response LIKE ?)")
                            params.extend([f"%{w}%", f"%{w}%"])
                        sql_like = f"SELECT * FROM knowledge WHERE {' OR '.join(keyword_conditions)}"
                        if domain:
                            sql_like += " AND domain = ?"
                            params.append(domain)
                        sql_like += " ORDER BY usage_count DESC, id DESC LIMIT ?"
                        params.append(limit)
                        cursor.execute(sql_like, params)
                        for row in cursor.fetchall():
                            item = dict(row)
                            if item.get('metadata'):
                                try:
                                    md = json.loads(item['metadata'])
                                    item.update(md)
                                except Exception:
                                    pass
                            results.append(item)
            except Exception as e:
                logging.debug(f"LIKE fallback failed: {e}")

        return results
    
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
