"""
config.py  (project root)

This module is a thin re-export shim.
ALL authoritative settings live in backend/config.py.
Import from there directly; use this only for legacy scripts at the root level.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from config import *  # noqa: F401, F403  — deliberate re-export
