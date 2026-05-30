from fastapi import APIRouter, HTTPException
from core import memory

router = APIRouter(prefix="/api/risk", tags=["Risk"])


@router.get("")
def list_risk_reviews(subject_id: str = None):
    reviews = memory.load_risk_reviews()
    if subject_id:
        reviews = [r for r in reviews if r.get("subject_id") == subject_id]
    return {"reviews": reviews, "total": len(reviews)}


@router.get("/summary")
def risk_summary():
    reviews = memory.load_risk_reviews()
    if not reviews:
        return {"avg_overall": 0, "high_risk_count": 0, "reviews": []}
    avg = sum(r.get("overall_risk_score", 0) for r in reviews) / len(reviews)
    high_risk = [r for r in reviews if r.get("overall_risk_score", 0) > 6]
    total_warnings = sum(
        len(r.get("flagged_phrases", [])) + len(r.get("flagged_claims", []))
        for r in reviews
    )
    return {
        "avg_overall_risk": round(avg, 2),
        "high_risk_count": len(high_risk),
        "total_warnings": total_warnings,
        "reviews": reviews,
    }


@router.post("/run")
def run_risk_review():
    ideas = memory.load_token_ideas()
    if not ideas:
        raise HTTPException(400, "No token ideas to review")
    from agents.risk_review_agent.agent import RiskReviewAgent
    result = RiskReviewAgent().run(ideas)
    return {"status": "ok", "reviewed": len(result.output or []), "output": result.output}
