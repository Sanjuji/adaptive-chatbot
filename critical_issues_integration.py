#!/usr/bin/env python3
# Compatibility shim for tests importing top-level module
# Re-exports everything from src.critical_issues_integration

from src.critical_issues_integration import *  # noqa: F401,F403