"""
LLM client — wraps Google Gemini Pro.
Falls back gracefully to mock responses when no API key is set.
"""
from __future__ import annotations
import os
import logging

logger = logging.getLogger(__name__)

_client = None
_model  = None


def _init():
    global _client, _model
    key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("gemini_api_key", "")
    if not key:
        return False
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        _model = genai.GenerativeModel("gemini-1.5-flash")
        logger.info("Gemini Pro initialised ✓")
        return True
    except Exception as e:
        logger.warning(f"Gemini init failed: {e}")
        return False


_ready = _init()


def ask(prompt: str, fallback: str = "") -> str:
    """
    Send a prompt to Gemini Pro.
    Returns fallback string if Gemini is unavailable.
    """
    if not _ready or _model is None:
        logger.debug("Gemini not available — using fallback")
        return fallback
    try:
        response = _model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.warning(f"Gemini request failed: {e}")
        return fallback


def is_available() -> bool:
    return _ready and _model is not None
