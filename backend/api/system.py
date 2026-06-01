from fastapi import APIRouter
import os

router = APIRouter(prefix="/api/system", tags=["System"])


@router.get("/ai-test")
def ai_test():
    """Test which AI provider is connected and working."""
    from core.llm import ask, is_available, provider_name

    if not is_available():
        groq_key = os.environ.get("GROQ_API_KEY", "")
        gemini_key = os.environ.get("GEMINI_API_KEY", "")
        return {
            "ai_connected": False,
            "reason": "No AI provider initialised",
            "groq_key_set": bool(groq_key),
            "gemini_key_set": bool(gemini_key),
        }

    result = ask("Say exactly three words: AI IS WORKING", fallback="")
    if result:
        return {
            "ai_connected": True,
            "provider": provider_name(),
            "response": result,
        }
    return {
        "ai_connected": False,
        "provider": provider_name(),
        "reason": "Provider initialised but request failed",
    }


@router.get("/gemini-test")
def gemini_test():
    """Legacy endpoint — redirects to /api/system/ai-test."""
    return ai_test()


@router.get("/scheduler")
def scheduler_status():
    """Check autonomous CEO scheduler — running status and next run times."""
    from backend.scheduler import get_scheduler_status
    return get_scheduler_status()


@router.post("/scheduler/run-now")
def scheduler_run_now():
    """Trigger CEO pipeline immediately (same as scheduled job)."""
    from backend.scheduler import job_ceo_pipeline
    import threading
    thread = threading.Thread(target=job_ceo_pipeline, daemon=True)
    thread.start()
    return {
        "status": "started",
        "message": "CEO pipeline running in background — check Telegram in ~30 seconds",
    }
