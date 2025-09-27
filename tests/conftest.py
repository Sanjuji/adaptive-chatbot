#!/usr/bin/env python3
"""
Pytest configuration to ensure repository root modules are importable in tests.

- Prepends the repo root (parent of this tests/ directory) to sys.path so that
  top-level shim modules like 'optimized_async_handler.py',
  'system_reliability_security.py', and 'critical_issues_integration.py'
  are importable regardless of pytest's path tweaks.
- Forces UTF-8 stdout/stderr encoding to avoid UnicodeEncodeError from prints.
"""

import os
import sys
from pathlib import Path

# Ensure repo root is on sys.path at highest priority
TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Force UTF-8 for console outputs during tests to avoid encoding issues on Windows
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

try:
    # On Windows, wrap stdout/stderr with UTF-8 writers if needed
    if sys.platform.startswith("win"):
        import io, msvcrt  # type: ignore
        if sys.stdout and sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        if sys.stderr and sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
except Exception:
    # Best-effort; don't break tests if the console cannot be wrapped
    pass