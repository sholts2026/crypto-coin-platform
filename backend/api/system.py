from fastapi import APIRouter
import os

router = APIRouter(prefix="/api/system", tags=["System"])


@router.get("/gemini-test")
def gemini_test():
    """Test if Gemini is connected and working."""
    key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("gemini_api_key", "")

    if not key:
        return {
            "gemini_connected": False,
            "reason": "GEMINI_API_KEY not set in environment",
            "key_preview": None,
        }

    key_preview = f"{key[:6]}...{key[-4:]}"
    try:
        from google import genai as new_genai
        client = new_genai.Client(api_key=key)
        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Say exactly: GEMINI_OK",
        )
        return {
            "gemini_connected": True,
            "sdk": "google-genai",
            "model_used": "gemini-2.0-flash",
            "response": resp.text.strip(),
            "key_preview": key_preview,
        }
    except Exception as e:
        return {
            "gemini_connected": False,
            "reason": str(e)[:200],
            "key_preview": key_preview,
        }
