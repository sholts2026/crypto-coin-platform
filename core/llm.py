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


CANDIDATE_MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro",
    "gemini-pro",
    "gemini-1.0-pro",
]


def _init():
    global _client, _model
    key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("gemini_api_key", "")
    if not key:
        return False
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        for model_name in CANDIDATE_MODELS:
            try:
                m = genai.GenerativeModel(model_name)
                # Quick probe — confirms the model is reachable
                m.generate_content("hi", generation_config={"max_output_tokens": 5})
                _model = m
                logger.info(f"Gemini initialised with model: {model_name} ✓")
                return True
            except Exception as probe_err:
                logger.debug(f"Model {model_name} not available: {probe_err}")
                continue
        logger.warning("No Gemini model found — all candidates failed")
        return False
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
