"""
LLM client — tries Groq first (fast, generous free tier), falls back to Gemini.
Falls back gracefully to empty string when no AI is available.
"""
from __future__ import annotations
import os
import logging

logger = logging.getLogger(__name__)

_provider = None   # "groq" | "gemini" | None
_groq_client = None
_gemini_client = None
_gemini_model = None
_GROQ_MODEL = "llama-3.3-70b-versatile"
_GEMINI_MODEL = "gemini-2.0-flash"


def _init():
    global _provider, _groq_client, _gemini_client, _gemini_model

    # ── 1. Try Groq ──────────────────────────────────────────────
    groq_key = os.environ.get("GROQ_API_KEY", "")
    if groq_key:
        try:
            from groq import Groq
            _groq_client = Groq(api_key=groq_key)
            _provider = "groq"
            logger.info(f"LLM: Groq ready ({_GROQ_MODEL}) ✓")
            return True
        except ImportError:
            logger.debug("groq package not installed")
        except Exception as e:
            logger.warning(f"Groq init failed: {e}")

    # ── 2. Fall back to Gemini (new SDK) ─────────────────────────
    gemini_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("gemini_api_key", "")
    if gemini_key:
        try:
            from google import genai as new_genai
            _gemini_client = new_genai.Client(api_key=gemini_key)
            _gemini_model = _GEMINI_MODEL
            _provider = "gemini"
            logger.info(f"LLM: Gemini ready ({_GEMINI_MODEL}) ✓")
            return True
        except ImportError:
            logger.debug("google-genai not installed")
        except Exception as e:
            logger.debug(f"Gemini init failed: {e}")

    logger.warning("LLM: no provider available — AI features disabled")
    return False


_ready = _init()


def ask(prompt: str, fallback: str = "") -> str:
    """Send a prompt to the available LLM. Returns fallback if unavailable."""
    if not _ready:
        return fallback

    if _provider == "groq" and _groq_client:
        try:
            resp = _groq_client.chat.completions.create(
                model=_GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"Groq request failed: {e}")
            return fallback

    if _provider == "gemini" and _gemini_client:
        try:
            resp = _gemini_client.models.generate_content(
                model=_gemini_model, contents=prompt
            )
            return resp.text.strip()
        except Exception as e:
            logger.warning(f"Gemini request failed: {e}")
            return fallback

    return fallback


def is_available() -> bool:
    return _ready and _provider is not None


def provider_name() -> str:
    return _provider or "none"
