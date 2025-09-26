#!/usr/bin/env python3
"""
Unified AdaptiveChatbot orchestrator for CLI/API
Provides a stable interface expected by src/cli.py:
- set_domain(domain)
- process_message(user_input) -> str
- knowledge_store (SQLite)
- conversation_history (list)
Retrieval-first with hybrid search; safe fallback when no confident match.
"""
from __future__ import annotations
from typing import Optional, Dict, Any, List
import logging

from .config import Config
from .knowledge_store import KnowledgeStore

# Hybrid retrieval (FTS then semantic)
try:
    from .retrieval import hybrid_search  # type: ignore
except Exception:
    hybrid_search = None  # type: ignore


class AdaptiveChatbot:
    def __init__(self, config_path: Optional[str] = None):
        # Load layered config; legacy path accepted
        self.config = Config(config_path)
        # Persistent knowledge store
        self.knowledge_store = KnowledgeStore(self.config.database_path)
        # State
        self.current_domain: str = self.config.default_domain
        self.conversation_history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger("AdaptiveChatbot")

    def set_domain(self, domain: str) -> None:
        if domain and isinstance(domain, str):
            self.current_domain = domain
        else:
            self.current_domain = self.config.default_domain

    def _get_threshold(self) -> float:
        th = getattr(self.config, 'retrieval_similarity_threshold', 0.65)
        per = getattr(self.config, 'retrieval_similarity_thresholds', {}) or {}
        if self.current_domain in per:
            th = per[self.current_domain]
        return float(th)

    def _fallback_response(self) -> str:
        # Use domain defaults if present; otherwise a generic helpful fallback
        try:
            domain_cfg = self.config.get_domain_config(self.current_domain) or {}
            defaults = domain_cfg.get('default_responses', [])
            if defaults:
                return str(defaults[0])
        except Exception:
            pass
        return "Mujhe iska jawab nahi pata. Kya aap mujhe iska sahi jawab bata sakte hai? Main ise yaad rakhunga."

    def process_message(self, user_input: str) -> str:
        if not user_input or not str(user_input).strip():
            return "Kripaya kuch boliye ya type kijiye."
        user_input = user_input.strip()

        # Retrieval-first to avoid hallucination
        response: Optional[str] = None
        try:
            th = self._get_threshold()
            if hybrid_search is not None:
                rows = hybrid_search(self.knowledge_store, user_input, domain=self.current_domain, top_k=1, min_semantic_similarity=th)
                if rows:
                    response = rows[0].get('response')
            else:
                # Fallback to FTS/LIKE-only if retrieval orchestrator is unavailable
                try:
                    rows = self.knowledge_store.search_fulltext(user_input, domain=self.current_domain, limit=1)
                    if rows:
                        response = rows[0].get('response')
                except Exception:
                    words = [w for w in user_input.split() if len(w) > 1]
                    rows = self.knowledge_store.search_by_keywords(words, domain=self.current_domain)
                    if rows:
                        response = rows[0].get('response')
        except Exception as e:
            self.logger.debug(f"Hybrid retrieval failed; falling back: {e}")

        if not response:
            response = self._fallback_response()

        # Update conversation history and log
        self.conversation_history.append({
            'user': user_input,
            'bot': response,
            'domain': self.current_domain
        })
        try:
            self.knowledge_store.log_conversation(
                session_id="cli", message_type="text", message=user_input, response=response, domain=self.current_domain
            )
        except Exception:
            pass
        return response
