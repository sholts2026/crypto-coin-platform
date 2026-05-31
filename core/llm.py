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


NEW_SDK_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]
OLD_SDK_MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro",
    "gemini-1.0-pro",
]

_sdk = None  # "new" or "old"
_new_client = None


def _init():
    global _client, _model, _sdk, _new_client
    key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("gemini_api_key", "")
    if not key:
        return False

    # Try new SDK (google-genai) first — supports AQ. key format
    try:
        from google import genai as new_genai
        client = new_genai.Client(api_key=key)
        for model_name in NEW_SDK_MODELS:
            try:
                resp = client.models.generate_content(
                    model=model_name,
                    contents="hi",
                )
                _ = resp.text  # confirm response
                _new_client = client
                _model = model_name
                _sdk = "new"
                logger.info(f"Gemini (new SDK) initialised with model: {model_name} ✓")
                return True
            except Exception as e:
                logger.debug(f"New SDK model {model_name} failed: {e}")
                continue
    except ImportError:
        logger.debug("google-genai not installed, trying legacy SDK")
    except Exception as e:
        logger.debug(f"New SDK init failed: {e}")

    # Fallback: old SDK (google-generativeai)
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        for model_name in OLD_SDK_MODELS:
            try:
                m = genai.GenerativeModel(model_name)
                m.generate_content("hi", generation_config={"max_output_tokens": 5})
                _model = m
                _sdk = "old"
                logger.info(f"Gemini (old SDK) initialised with model: {model_name} ✓")
                return True
            except Exception as e:
                logger.debug(f"Old SDK model {model_name} failed: {e}")
                continue
    except Exception as e:
        logger.warning(f"Gemini old SDK init failed: {e}")

    logger.warning("Gemini: no model found with either SDK")
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
