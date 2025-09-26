#!/usr/bin/env python3
"""
Optional Semantic Index using hnswlib for fast vector search on Windows.
Falls back gracefully if hnswlib or sentence-transformers are unavailable.
"""

from __future__ import annotations
import os
import json
import logging
from pathlib import Path
from typing import List, Tuple, Optional, Dict

try:
    import hnswlib  # type: ignore
    HNSW_AVAILABLE = True
except Exception as e:
    HNSW_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    ST_AVAILABLE = True
except Exception:
    ST_AVAILABLE = False

import numpy as np

logger = logging.getLogger(__name__)


class SemanticIndex:
    """Lightweight semantic index wrapper using hnswlib + sentence-transformers."""

    def __init__(self,
                 base_dir: str = "data/vector_index",
                 model_name: str = "all-MiniLM-L6-v2",
                 ef_search: int = 64,
                 M: int = 32,
                 ef_construction: int = 200):
        self.base_dir = Path(base_dir)
        self.model_name = model_name
        self.ef_search = ef_search
        self.M = M
        self.ef_construction = ef_construction
        self.model: Optional[SentenceTransformer] = None
        if not self.base_dir.exists():
            self.base_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_model(self) -> None:
        if not ST_AVAILABLE:
            raise RuntimeError("sentence-transformers not available. Install it to use semantic index.")
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)

    def _domain_paths(self, domain: str) -> Tuple[Path, Path, Path]:
        ddir = self.base_dir / domain
        index_path = ddir / "index.bin"
        meta_path = ddir / "meta.json"
        map_path = ddir / "mapping.json"
        return index_path, meta_path, map_path

    def available(self) -> bool:
        return HNSW_AVAILABLE and ST_AVAILABLE

    def build(self, items: List[Tuple[int, str]], domain: str) -> bool:
        """Build or rebuild index for domain from (id, text) items."""
        if not HNSW_AVAILABLE:
            logger.warning("hnswlib not available; semantic index build skipped.")
            return False
        if not items:
            logger.info(f"No items to index for domain '{domain}'.")
            return False
        self._ensure_model()
        ids = [i for i, _ in items]
        texts = [t for _, t in items]
        # Compute embeddings
        embs = self.model.encode(texts, batch_size=64, convert_to_numpy=True, show_progress_bar=False)
        # Normalize for cosine similarity
        norms = np.linalg.norm(embs, axis=1, keepdims=True) + 1e-10
        embs = embs / norms
        dim = embs.shape[1]

        # Prepare paths
        index_path, meta_path, map_path = self._domain_paths(domain)
        index_path.parent.mkdir(parents=True, exist_ok=True)

        # Create index
        p = hnswlib.Index(space='cosine', dim=dim)
        p.init_index(max_elements=len(ids), ef_construction=self.ef_construction, M=self.M)
        p.add_items(embs, ids)
        p.set_ef(self.ef_search)
        # Save
        p.save_index(str(index_path))
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump({
                'dim': dim,
                'ef_search': self.ef_search,
                'M': self.M,
                'ef_construction': self.ef_construction,
                'model_name': self.model_name,
                'count': len(ids)
            }, f, ensure_ascii=False, indent=2)
        with open(map_path, 'w', encoding='utf-8') as f:
            json.dump({'ids': ids}, f, ensure_ascii=False)
        logger.info(f"Built semantic index for domain '{domain}' with {len(ids)} items.")
        return True

    def _load_index(self, domain: str) -> Optional[hnswlib.Index]:  # type: ignore
        if not HNSW_AVAILABLE:
            return None
        index_path, meta_path, _ = self._domain_paths(domain)
        if not index_path.exists() or not meta_path.exists():
            return None
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            dim = int(meta.get('dim', 384))
            p = hnswlib.Index(space='cosine', dim=dim)
            p.load_index(str(index_path))
            p.set_ef(int(meta.get('ef_search', self.ef_search)))
            return p
        except Exception as e:
            logger.error(f"Failed to load semantic index for '{domain}': {e}")
            return None

    def search(self, query: str, domain: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """Return list of (id, similarity) for query."""
        if not HNSW_AVAILABLE:
            logger.debug("hnswlib not available; semantic search skipped.")
            return []
        self._ensure_model()
        p = self._load_index(domain)
        if p is None:
            logger.info(f"No semantic index for domain '{domain}'. Build it first.")
            return []
        q = self.model.encode([query], convert_to_numpy=True)
        q = q / (np.linalg.norm(q, axis=1, keepdims=True) + 1e-10)
        labels, distances = p.knn_query(q, k=max(1, top_k))
        results: List[Tuple[int, float]] = []
        for lbl, dist in zip(labels[0], distances[0]):
            sim = float(1.0 - dist)  # cosine similarity = 1 - distance
            results.append((int(lbl), sim))
        return results
