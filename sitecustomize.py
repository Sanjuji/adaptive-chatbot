#!/usr/bin/env python3
"""
Module alias shims for tests importing top-level modules.
Maps bare module names to src.* modules.
"""
import importlib
import sys

def _alias(name: str, target: str) -> None:
    try:
        if name in sys.modules:
            return
        sys.modules[name] = importlib.import_module(target)
    except Exception:
        # Keep startup resilient; tests will print warnings if unavailable
        pass

_alias('optimized_async_handler', 'src.optimized_async_handler')
_alias('system_reliability_security', 'src.system_reliability_security')
_alias('critical_issues_integration', 'src.critical_issues_integration')