"""Shared helpers for direct xAI HTTP integrations."""

from __future__ import annotations


def openzuma_xai_user_agent() -> str:
    """Return a stable Openzuma-specific User-Agent for xAI HTTP calls."""
    try:
        from openzuma_cli import __version__
    except Exception:
        __version__ = "unknown"
    return f"Openzuma-Agent/{__version__}"
