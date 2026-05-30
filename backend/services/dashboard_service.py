from __future__ import annotations
from core import memory


def get_overview() -> dict:
    trends  = memory.load_trends()
    ideas   = memory.load_token_ideas()
    drafts  = memory.load_social_drafts()
    risks   = memory.load_risk_reviews()
    decs    = memory.load_decisions()
    scores  = memory.load_scores()

    top_trend = trends[0] if trends else None
    best_decision = decs[-1] if decs else None

    best_score = max(scores, key=lambda s: s.get("final_opportunity_score", 0), default=None) if scores else None
    best_idea = None
    if best_score:
        best_idea = next((i for i in ideas if i["id"] == best_score["token_idea_id"]), None)

    checklist = best_decision.get("launch_checklist_status", {}) if best_decision else {}
    total_items = len(checklist) or 12
    done_items = sum(1 for v in checklist.values() if v)
    readiness = round(done_items / total_items * 100, 1) if total_items else 0

    total_warnings = sum(
        len(r.get("flagged_phrases", [])) + len(r.get("flagged_claims", []))
        for r in risks
    )

    next_action = "Run collect-trends to start"
    if trends and not ideas:
        next_action = "Run generate-token-ideas"
    elif ideas and not risks:
        next_action = "Run risk-review"
    elif risks and not decs:
        next_action = "Run ceo-decision"
    elif decs and best_decision and best_decision.get("human_approval_status") == "pending":
        next_action = "Review CEO decision and approve in dashboard"

    return {
        "top_trending_narratives": [t.get("phrase") for t in trends[:3]],
        "best_token_opportunity": best_idea.get("token_name") if best_idea else None,
        "best_opportunity_ticker": best_idea.get("ticker") if best_idea else None,
        "launch_readiness_score": readiness,
        "total_token_ideas": len(ideas),
        "total_social_drafts": len(drafts),
        "total_risk_warnings": total_warnings,
        "total_trends_detected": len(trends),
        "total_decisions": len(decs),
        "system_status": "operational",
        "next_recommended_action": next_action,
        "ceo_recommendation": best_decision.get("recommended_token_name") if best_decision else None,
    }


def get_agent_statuses() -> list:
    from datetime import datetime
    agents = [
        "ceo_agent", "trend_hunter_agent", "token_concept_agent",
        "token_builder_agent", "social_strategy_agent",
        "community_agent", "brand_agent", "risk_review_agent",
    ]
    status_data = {
        "trend_hunter_agent":   {"output_file": "trends.json",         "loader": memory.load_trends},
        "token_concept_agent":  {"output_file": "token_ideas.json",    "loader": memory.load_token_ideas},
        "risk_review_agent":    {"output_file": "risk_reviews.json",   "loader": memory.load_risk_reviews},
        "brand_agent":          {"output_file": "brand_packages.json", "loader": memory.load_brand_packages},
        "social_strategy_agent":{"output_file": "social_drafts.json",  "loader": memory.load_social_drafts},
        "ceo_agent":            {"output_file": "decisions.json",      "loader": memory.load_decisions},
        "community_agent":      {"output_file": "community_packages.json", "loader": lambda: memory.load_json("community_packages.json", [])},
        "token_builder_agent":  {"output_file": "contracts_data.json", "loader": memory.load_contracts},
    }
    results = []
    for name in agents:
        info = status_data.get(name, {})
        loader = info.get("loader")
        data = loader() if loader else []
        results.append({
            "agent_name": name,
            "current_task": "idle",
            "last_run_time": data[-1].get("created_at") if data and isinstance(data, list) and data else None,
            "last_output_count": len(data) if isinstance(data, list) else 0,
            "status": "ready",
            "errors": [],
            "warnings": [],
        })
    return results
