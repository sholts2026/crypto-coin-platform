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


_sdk = None  # "new" or "old"
_new_client = None
_MODEL_NAME = "gemini-2.0-flash"


def _init():
    """Initialise without probing — avoids burning rate-limit quota on startup."""
    global _client, _model, _sdk, _new_client
    key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("gemini_api_key", "")
    if not key:
        return False

    # Prefer new SDK (google-genai) — required for AQ. key format
    try:
        from google import genai as new_genai
        _new_client = new_genai.Client(api_key=key)
        _model = _MODEL_NAME
        _sdk = "new"
        logger.info(f"Gemini (new SDK) ready, model={_MODEL_NAME} ✓")
        return True
    except ImportError:
        logger.debug("google-genai not installed, trying legacy SDK")
    except Exception as e:
        logger.debug(f"New SDK init failed: {e}")

    # Fallback: old SDK
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        _model = genai.GenerativeModel("gemini-pro")
        _sdk = "old"
        logger.info("Gemini (legacy SDK) ready ✓")
        return True
    except Exception as e:
        logger.warning(f"Gemini legacy SDK init failed: {e}")

    return False


_ready = _init()


def ask(prompt: str, fallback: str = "") -> str:
    """
    Send a prompt to Gemini.
    Returns fallback string if Gemini is unavailable.
    """
    if not _ready or _model is None:
        logger.debug("Gemini not available — using fallback")
        return fallback
    try:
        if _sdk == "new" and _new_client is not None:
            response = _new_client.models.generate_content(
                model=_model, contents=prompt
            )
            return response.text.strip()
        else:
            response = _model.generate_content(prompt)
            return response.text.strip()
    except Exception as e:
        logger.warning(f"Gemini request failed: {e}")
        return fallback


def is_available() -> bool:
    return _ready and _model is not None
