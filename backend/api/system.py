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

    candidates = [
        "gemini-1.5-flash", "gemini-1.5-flash-latest",
        "gemini-1.5-pro", "gemini-pro", "gemini-1.0-pro",
    ]
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        for model_name in candidates:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    "Say exactly: GEMINI_OK",
                    generation_config={"max_output_tokens": 10},
                )
                return {
                    "gemini_connected": True,
                    "model_used": model_name,
                    "response": response.text.strip(),
                    "key_preview": f"{key[:6]}...{key[-4:]}",
                }
            except Exception as e:
                continue
        return {
            "gemini_connected": False,
            "reason": "All model candidates failed",
            "tried": candidates,
            "key_preview": f"{key[:6]}...{key[-4:]}",
        }
    except Exception as e:
        return {
            "gemini_connected": False,
            "reason": str(e),
            "key_preview": f"{key[:6]}...{key[-4:]}",
        }
