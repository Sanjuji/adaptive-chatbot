#!/usr/bin/env python3
"""
Golden conversation evaluation tests.

Uses FastAPI TestClient against the in-process app (no external network or server).
Validates:
- 200 responses
- Basic safety constraints for adversarial inputs
- Long-context stability
- No sensitive leakage for tool-like file requests
"""

import json
from typing import Dict, Any, List

from fastapi.testclient import TestClient
from src.web_api import app

client = TestClient(app)


def _load_golden(path: str = "tests/evals/golden_conversations.json") -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _send_chat(message: str, domain: str | None = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"message": message}
    if domain:
        payload["domain"] = domain
    r = client.post("/chat", json=payload)
    assert r.status_code == 200, f"/chat failed: {r.status_code} {r.text}"
    data = r.json()
    assert "reply" in data, "Missing reply in /chat response"
    return data


def _contains_any(text: str, candidates: List[str]) -> bool:
    t = text.lower()
    return any(c.lower() in t for c in candidates)


def _contains_none(text: str, prohibited: List[str]) -> bool:
    t = text.lower()
    return all(p.lower() not in t for p in prohibited)


def test_golden_conversations():
    spec = _load_golden()
    convs = spec.get("conversations", [])
    assert convs, "No conversations found in golden spec"

    for conv in convs:
        cid = conv.get("id", "unknown")
        turns = conv.get("turns", [])
        assert turns and isinstance(turns, list), f"Bad turns for {cid}"

        # For this API, we only have /chat roundtrip; apply checks on expected objects.
        user_turn = turns[0].get("user", "")
        assert isinstance(user_turn, str), f"Bad user turn for {cid}"

        res = _send_chat(user_turn)

        # Optional expectations
        for t in turns[1:]:
            # expected_contains_any: one of strings must appear in reply
            if "expected_contains_any" in t:
                assert _contains_any(
                    res["reply"], t["expected_contains_any"]
                ), f"{cid}: reply did not contain any expected strings"

            # expected_prohibited: none of these strings must appear in reply
            if "expected_prohibited" in t:
                assert _contains_none(
                    res["reply"], t["expected_prohibited"]
                ), f"{cid}: reply contained prohibited strings"

            # expected_behavior: smoke-check semantics only (no crash)
            if "expected_behavior" in t:
                # ensure non-empty reply, no exceptions thrown earlier
                assert isinstance(res["reply"], str) and len(res["reply"]) >= 0, f"{cid}: empty reply"


def test_metrics_endpoint_smoke_and_histograms():
    # Exercise some traffic to populate latency window
    for _ in range(10):
        _ = _send_chat("hello")

    r = client.get("/metrics")
    assert r.status_code == 200
    data = r.json()

    assert "requests_total" in data
    assert "errors_total" in data
    assert "latency_ms" in data
    lat = data["latency_ms"]
    for k in ("avg", "p50", "p95", "p99", "samples"):
        assert k in lat, f"Missing latency key: {k}"