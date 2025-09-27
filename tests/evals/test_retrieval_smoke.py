#!/usr/bin/env python3
"""
Retrieval smoke tests:
- /knowledge/search returns 200 and a list
- Basic shape validation for SearchResponseItem
"""

from __future__ import annotations

from typing import Dict, Any, List

from fastapi.testclient import TestClient
from src.web_api import app

client = TestClient(app)


def test_knowledge_search_returns_list():
    payload: Dict[str, Any] = {"query": "switch price", "top_k": 5}
    r = client.post("/knowledge/search", json=payload)
    assert r.status_code == 200, f"/knowledge/search failed: {r.status_code} {r.text}"
    data = r.json()
    assert isinstance(data, list), "Expected list response"
    # Validate at least the schema keys if present
    if data:
        item = data[0]
        for key in ("id", "input", "domain"):
            assert key in item, f"Missing key in SearchResponseItem: {key}"


def test_knowledge_search_empty_query_is_safe():
    payload: Dict[str, Any] = {"query": "  "}
    r = client.post("/knowledge/search", json=payload)
    assert r.status_code == 200
    assert r.json() == []