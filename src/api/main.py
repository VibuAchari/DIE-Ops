"""Backward-compatible FastAPI entry point.

The application composition now lives in :mod:`src.api.app`.
"""
from src.api.app import app

__all__ = ["app"]
