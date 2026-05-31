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
    errors = []

    # Try new SDK (google-genai) — for AQ. key format
    try:
        from google import genai as new_genai
        client = new_genai.Client(api_key=key)
        for model_name in ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash", "gemini-1.5-pro"]:
            try:
                resp = client.models.generate_content(
                    model=model_name, contents="Say exactly: GEMINI_OK"
                )
                return {
                    "gemini_connected": True,
                    "sdk": "google-genai (new)",
                    "model_used": model_name,
                    "response": resp.text.strip(),
                    "key_preview": key_preview,
                }
            except Exception as e:
                errors.append(f"new/{model_name}: {str(e)[:80]}")
    except ImportError:
        errors.append("google-genai not installed")
    except Exception as e:
        errors.append(f"new SDK init: {str(e)[:80]}")

    # Try old SDK (google-generativeai)
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        for model_name in ["gemini-1.5-flash", "gemini-pro", "gemini-1.0-pro"]:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    "Say exactly: GEMINI_OK",
                    generation_config={"max_output_tokens": 10},
                )
                return {
                    "gemini_connected": True,
                    "sdk": "google-generativeai (legacy)",
                    "model_used": model_name,
                    "response": response.text.strip(),
                    "key_preview": key_preview,
                }
            except Exception as e:
                errors.append(f"old/{model_name}: {str(e)[:80]}")
    except Exception as e:
        errors.append(f"old SDK init: {str(e)[:80]}")

    return {
        "gemini_connected": False,
        "reason": "All SDKs and models failed",
        "errors": errors,
        "key_preview": key_preview,
    }
