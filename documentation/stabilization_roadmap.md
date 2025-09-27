# Adaptive Chatbot Stabilization Roadmap, Runbook, and Security Policy

Version: 1.0.0
Last Updated: 2025-09-26

Overview
This document consolidates:
- Stabilization Roadmap (what we hardened and what to keep improving)
- Ops Runbook (how to run, test, measure, and recover)
- Security and Compliance Policy (guardrails, logging hygiene, PII, secrets)

1) Stabilization Roadmap

Completed (This Release)
- API Reliability and Observability
  - FastAPI entrypoint [src/web_api.py]
  - Structured logging middleware with request IDs, safer error responses (no internals)
  - Basic rate limiting (token bucket, per-IP, dev-safe)
  - CORS and CSP headers (default allow-all for dev, tighten for prod)
  - /metrics endpoint with latency histograms (avg, p50, p95, p99) and rolling window
- Test Stabilization
  - All tests pass: 47 passed locally
  - Legacy wrappers restored in [utils/logger.py] (log_info/log_error/log_warning/log_debug)
  - Fixed validator regex literal error in [utils/validator.py]
  - Langdetect fallback and deterministic seeding in [nlp/advanced_nlp.py]
  - Atexit cleanup guard in [src/optimized_async_handler.py]
  - Safe path fallback in [src/critical_issues_integration.py] to avoid None returns
  - Top-level module shims + path hooks: [optimized_async_handler.py], [system_reliability_security.py], [critical_issues_integration.py], [sitecustomize.py], and [tests/conftest.py]
- CI/CD
  - GitHub Actions workflow: [.github/workflows/ci.yml]
  - Pinned constraints for reproducible builds: [constraints-dev.txt]
  - Static checks wired: ruff, mypy; tests run with pytest
- Evaluation Harness
  - Golden conversation set: [tests/evals/golden_conversations.json]
  - Evaluations: [tests/evals/test_golden_conversations.py] (safety, multilingual, adversarial, long-context)
- Performance Tooling
  - Local perf benchmark script: [scripts/perf_bench.py] (avg, p50, p95, p99)
- Config Merge Correctness
  - Schema-aware recursive overlay merge in [src/config.py] (nested keys like app:, voice: now applied)

In Progress / Next Iteration (Operationalization)
- Security Hardening (Production)
  - Secrets management: store in environment variables or a cloud secret manager (Azure Key Vault, AWS Secrets Manager)
  - Lock down CORS allow_origins to trusted domains (env-driven)
  - Set strict CSP tailored to frontend (block inline scripts, only required sources)
  - Rate limiter backed by Redis, with per-token (per-tenant) quotas
  - Enhance PII redaction (names, addresses) using deterministic masking rules and expandable patterns
- Retrieval/RAG
  - Audit chunking/overlap and metadata filters; compare ANN/FAISS settings; unify dimensionality with the embedding model
  - Add reranking integration path; add stale data detection and reindex frequency controls
- Performance & Cost
  - Add caching at knowledge search layer and DB read path; batch DB calls where safe
  - Tune thread/loop execution strategies to avoid overhead in short tasks
- Documentation
  - Expand runbooks per environment (dev/staging/prod); SLOs and error budgets; escalation matrix

2) Operations Runbook

Local Development
- Environment
  - Python 3.11
  - Windows: run in cmd with .venv; Linux/macOS: use your shell venv
- Setup
  - python --version
  - py -3.11 -m venv .venv (Windows) | python3.11 -m venv .venv (Linux/macOS)
  - .venv\Scripts\activate (Windows) | source .venv/bin/activate (Linux/macOS)
  - python -m pip install --upgrade pip
  - python -m pip install -r data/static/requirements.txt -c constraints-dev.txt
- Run API
  - set APP_ENV=development (Windows) | export APP_ENV=development (Linux/macOS)
  - python -m uvicorn src.web_api:app --host 0.0.0.0 --port 8000 --reload
- Smoke Tests
  - curl http://127.0.0.1:8000/health
  - curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d "{\"message\":\"hello\"}"
  - curl http://127.0.0.1:8000/metrics
- Tests
  - pytest -q
- Static Checks
  - ruff check .
  - mypy .

Golden Evaluations
- Spec: [tests/evals/golden_conversations.json]
- Tests: pytest -q tests/evals/test_golden_conversations.py
- Acceptance criteria:
  - Reliability: Pass rate >= 90%
  - Safety: No leakage for adversarial injections
  - Long-context: No crash; stable fallback
  - Latency: p95 < 1200ms (local baseline); adjust per environment
  - Cost: local track ~0

Performance Bench
- Start API locally
- python scripts/perf_bench.py --host http://127.0.0.1:8000 --iters 200 --payload "hello"
- Collect avg/p50/p95/p99 and compare against SLOs

Deploy (CI/CD)
- CI workflow: [.github/workflows/ci.yml]
  - Installs deps with pinned [constraints-dev.txt]
  - Runs ruff, mypy, pytest
- Environments:
  - Dev: APP_ENV=development (wide CORS), low rate limits, local stores
  - Staging: tighten CORS, use managed stores; add synthetic traffic; enforce golden evals
  - Prod: strict CORS/CSP, managed secrets, Redis-backed rate-limiting, centralized logging

Incident Handling
- Identify
  - Check /metrics for spikes in errors_total, latency p95/p99
  - Tail logs: logs/chatbot.log, logs/app.log for errors around timestamps
- Mitigate
  - Rollback via CI to last green commit
  - Enable safe fallback paths in retrieval; reduce batch sizes; widen timeouts temporarily
- Root Cause Analysis
  - Reproduce with minimal inputs; add test covering the defect
  - Capture request IDs from logs; correlate with routes and timers
- Prevent
  - Add regression tests/evals; wire into CI
  - Promote configuration knobs to environment to avoid code redeploys for tuning

3) Security & Compliance Policy (Baseline)

PII and Sensitive Data
- Redaction:
  - Basic patterns for emails and phone numbers are masked in API responses via _redact_pii
  - Extend with stronger patterns for names/addresses where applicable
- Logging Hygiene:
  - Avoid logging raw user inputs where not required; never log secrets
  - Use request IDs; prefer structured logs over free-text

Secrets Management
- Do not commit secrets to repo
- Use environment variables or external secret manager
- Provide a .env.example file to document required variables; load via python-dotenv only in development if needed

Access Control and Least Privilege
- Databases and file paths restricted to app data dirs; path traversal guarded by sanitization logic
- For multi-tenant contexts, ensure token-based rate limiting and RBAC on routes

Network and Browser Security
- CORS defaults to allow-all in dev; tighten to known origins in prod
- CSP set to restrict sources; no inline scripts by default
- X-Content-Type-Options: nosniff

Dependencies and Supply Chain
- Reproducible installs via [constraints-dev.txt]
- CI runs static checks and tests on every push/PR
- Periodic dependency audit (pip-audit or SCA tool)

Disaster Recovery
- Backup knowledge files and DB snapshots (retain last N)
- Recovery: restore from snapshot; reindex retrieval stores if needed

Appendix: File Index
- API & Middleware: [src/web_api.py]
- Config System: [src/config.py]
- Logger Utility: [utils/logger.py]
- Validator: [utils/validator.py]
- NLP Core: [nlp/advanced_nlp.py]
- Async Util: [src/optimized_async_handler.py], [optimized_async_handler.py]
- Reliability & Security: [src/system_reliability_security.py], [system_reliability_security.py]
- Critical Integrations: [src/critical_issues_integration.py], [critical_issues_integration.py]
- Golden Evals: [tests/evals/golden_conversations.json], [tests/evals/test_golden_conversations.py]
- CI: [.github/workflows/ci.yml]
- Constraints: [constraints-dev.txt]
- Perf: [scripts/perf_bench.py]