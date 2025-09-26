#!/usr/bin/env python3
"""
Hybrid retrieval orchestrator: FTS5 first, then semantic (hnswlib) fallback.
"""
from __future__ import annotations
import logging
from typing import List, Dict, Any, Optional

from .knowledge_store import KnowledgeStore

try:
    from .semantic_index import SemanticIndex
    SEM_AVAILABLE = True
except Exception:
    SEM_AVAILABLE = False

logger = logging.getLogger(__name__)


def hybrid_search(ks: KnowledgeStore,
                  query: str,
                  domain: Optional[str] = None,
                  top_k: int = 5,
                  min_semantic_similarity: float = 0.65) -> List[Dict[str, Any]]:
    """
    Perform hybrid search: FTS5 first, then semantic fallback (if available).
    Returns a list of knowledge rows (dicts). Adds `_source` and `_score` keys.
    """
    # 1) FTS first
    fts = ks.search_fulltext(query, domain=domain, limit=top_k)
    results: List[Dict[str, Any]] = []
    for row in fts:
        row_copy = dict(row)
        row_copy['_source'] = 'fts'
        row_copy['_score'] = None
        results.append(row_copy)
    if len(results) >= top_k:
        return results

    # 2) Semantic fallback
    if SEM_AVAILABLE:
        try:
            si = SemanticIndex()
            if si.available():
                sem = si.search(query, domain or 'general', top_k=top_k)
                # Filter by similarity threshold and fetch rows
                for kid, sim in sem:
                    if sim < min_semantic_similarity:
                        continue
                    row = ks.get_knowledge_by_id(kid)
                    if row:
                        row['_source'] = 'semantic'
                        row['_score'] = sim
                        results.append(row)
                # Deduplicate by id, keep best
                seen = {}
                deduped: List[Dict[str, Any]] = []
                for r in results:
                    rid = r.get('id')
                    if rid in seen:
                        # Keep fts over semantic or higher score
                        prev = seen[rid]
                        if prev.get('_source') == 'semantic' and r.get('_source') == 'fts':
                            seen[rid] = r
                        elif r.get('_score', 0) > prev.get('_score', 0):
                            seen[rid] = r
                    else:
                        seen[rid] = r
                deduped = list(seen.values())
                # Sort: fts first, then semantic by score desc
                deduped.sort(key=lambda x: (0 if x.get('_source') == 'fts' else 1, -(x.get('_score') or 0)))
                return deduped[:top_k]
        except Exception as e:
            logger.warning(f"Semantic fallback failed: {e}")

    return results[:top_k]
