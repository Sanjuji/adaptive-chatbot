#!/usr/bin/env python3
"""
FastAPI service exposing health, knowledge search, and simple chat endpoints.
Run with: uvicorn src.web_api:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from .config import Config
from .knowledge_store import KnowledgeStore
from .learning import LearningManager

# Hybrid retrieval (FTS then semantic)
try:
    from .retrieval import hybrid_search
except Exception:
    hybrid_search = None  # type: ignore

app = FastAPI(title="Adaptive Chatbot API", version="1.0.0")

# Singletons
_cfg = Config()
_ks = KnowledgeStore(_cfg.database_path)
_lm = LearningManager(_ks)


class SearchRequest(BaseModel):
    query: str
    domain: Optional[str] = None
    top_k: int = 5


class SearchResponseItem(BaseModel):
    id: int
    input: str
    response: Optional[str] = None
    domain: Optional[str] = None
    _source: Optional[str] = None
    _score: Optional[float] = None


class ChatRequest(BaseModel):
    message: str
    domain: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    source: str

class TeachRequest(BaseModel):
    input: str
    response: str
    domain: Optional[str] = "general"
    category: Optional[str] = "learned"
    confidence: Optional[float] = 1.0
    validation_status: Optional[str] = None  # e.g., 'pending', 'approved'

class TeachBulkRequest(BaseModel):
    items: List[TeachRequest]


@app.get("/health")
async def health() -> Dict[str, Any]:
    try:
        # Simple DB check
        _ = _ks.get_stats()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/knowledge/search", response_model=List[SearchResponseItem])
async def knowledge_search(req: SearchRequest):
    if not req.query or not req.query.strip():
        return []
    # Threshold selection (per-domain override)
    th = _cfg.retrieval_similarity_threshold
    if req.domain and isinstance(_cfg.retrieval_similarity_thresholds, dict):
        th = _cfg.retrieval_similarity_thresholds.get(req.domain, th)

    # Use hybrid if available; else FTS/LIKE
    if hybrid_search is not None:
        rows = hybrid_search(_ks, req.query, domain=req.domain, top_k=req.top_k, min_semantic_similarity=th)
    else:
        # Fallback to FTS then LIKE
        try:
            rows = _ks.search_fulltext(req.query, domain=req.domain, limit=req.top_k)
            rows = [{**r, '_source': 'fts', '_score': None} for r in rows]
        except Exception:
            words = [w for w in req.query.split() if len(w) > 1]
            rows = _ks.search_by_keywords(words, domain=req.domain)[:req.top_k]
            rows = [{**r, '_source': 'like', '_score': None} for r in rows]

    # Serialize
    out: List[SearchResponseItem] = []
    for r in rows:
        out.append(SearchResponseItem(
            id=int(r.get('id', 0)),
            input=str(r.get('input', '')),
            response=r.get('response'),
            domain=r.get('domain'),
            _source=r.get('_source'),
            _score=r.get('_score')
        ))
    return out


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Empty message")

    # Try knowledge base first
    try:
        rows = _ks.search_fulltext(req.message, domain=req.domain, limit=1)
        if rows:
            return ChatResponse(reply=str(rows[0].get('response', '')), source='fts')
    except Exception:
        pass

    # Fallback to hybrid if available
    if hybrid_search is not None:
        th = _cfg.retrieval_similarity_threshold
        if req.domain and isinstance(_cfg.retrieval_similarity_thresholds, dict):
            th = _cfg.retrieval_similarity_thresholds.get(req.domain, th)
        rows = hybrid_search(_ks, req.message, domain=req.domain, top_k=1, min_semantic_similarity=th)
        if rows:
            return ChatResponse(reply=str(rows[0].get('response', '')), source=rows[0].get('_source') or 'hybrid')

    # Final fallback
    return ChatResponse(reply="Mujhe iska jawab nahi pata. Kya aap thoda detail batayenge?", source='fallback')


# ---------------------- Threshold management ----------------------
class Thresholds(BaseModel):
    global_threshold: float
    per_domain: Dict[str, float] = {}


@app.get("/config/retrieval-threshold", response_model=Thresholds)
async def get_thresholds():
    try:
        return Thresholds(
            global_threshold=float(_cfg.retrieval_similarity_threshold),
            per_domain=dict(_cfg.retrieval_similarity_thresholds or {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/config/retrieval-threshold", response_model=Thresholds)
async def set_thresholds(payload: Thresholds):
    try:
        _cfg.retrieval_similarity_threshold = float(payload.global_threshold)
        _cfg.retrieval_similarity_thresholds = dict(payload.per_domain or {})
        _cfg.save_config()
        return Thresholds(
            global_threshold=float(_cfg.retrieval_similarity_threshold),
            per_domain=dict(_cfg.retrieval_similarity_thresholds or {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/knowledge/teach")
async def knowledge_teach(req: TeachRequest) -> Dict[str, Any]:
    try:
        ok = _lm.teach_chatbot(
            user_input=req.input,
            expected_response=req.response,
            category=req.category or "learned",
            domain=req.domain or "general",
            confidence=req.confidence or 1.0
        )
        if ok and req.validation_status:
            # If caller wants to mark as pending/approved, update metadata
            # We need the id to do this precisely; as a pragmatic approach,
            # attempt to find the row via exact input+domain match.
            rows = _ks.search_by_keywords([req.input], domain=req.domain)
            for r in rows:
                if r.get('input') == req.input and r.get('domain') == req.domain:
                    _ks.set_validation_status(int(r['id']), req.validation_status)
                    break
        return {"success": bool(ok)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/knowledge/import")
async def knowledge_import(req: TeachBulkRequest, domain: Optional[str] = None) -> Dict[str, Any]:
    try:
        # Build list for batch_teach
        items = []
        dom = domain or "general"
        for it in req.items:
            items.append({
                'input': it.input,
                'response': it.response,
                'category': it.category or 'learned',
                'confidence': it.confidence or 1.0
            })
        success, total = _lm.batch_teach(items, domain=dom)
        return {"success": success, "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge/pending", response_model=List[SearchResponseItem])
async def knowledge_pending(domain: Optional[str] = None, limit: int = 100):
    try:
        rows = _ks.get_pending_knowledge(domain=domain, limit=limit)
        out: List[SearchResponseItem] = []
        for r in rows:
            out.append(SearchResponseItem(
                id=int(r.get('id', 0)),
                input=str(r.get('input', '')),
                response=r.get('response'),
                domain=r.get('domain'),
                _source='pending',
                _score=None
            ))
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ApproveRequest(BaseModel):
    id: int
    status: str = "approved"


@app.post("/knowledge/approve")
async def knowledge_approve(req: ApproveRequest) -> Dict[str, Any]:
    try:
        ok = _ks.set_validation_status(req.id, req.status)
        return {"success": bool(ok)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
