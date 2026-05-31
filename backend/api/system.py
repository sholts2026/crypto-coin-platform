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

    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Say exactly: GEMINI_OK")
        text = response.text.strip()
        return {
            "gemini_connected": True,
            "response": text,
            "key_preview": f"{key[:6]}...{key[-4:]}",
        }
    except Exception as e:
        return {
            "gemini_connected": False,
            "reason": str(e),
            "key_preview": f"{key[:6]}...{key[-4:]}",
        }
