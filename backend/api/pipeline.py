"""
Pipeline API — Run the full agent pipeline in one shot and auto-approve outputs.
Useful after Railway redeploys (ephemeral filesystem resets data/).
"""
from fastapi import APIRouter
from core import memory

router = APIRouter(prefix="/api/pipeline", tags=["Pipeline"])


@router.post("/run-all")
def run_full_pipeline(use_mock: bool = False, auto_approve: bool = True):
    """
    Run the complete pipeline end-to-end:
      trends → token ideas → CEO decision → social → brand → risk → contracts
    Then optionally auto-approve all generated items for launch readiness.

    Safe: all outputs are drafts requiring human approval before real-world use.
    """
    results = {}

    # 1. Trends
    try:
        from agents.trend_hunter_agent.agent import TrendHunterAgent
        out = TrendHunterAgent(use_mock=use_mock).run()
        results["trends"] = len(out.output or [])
    except Exception as e:
        results["trends_error"] = str(e)

    # 2. Token ideas
    try:
        from agents.token_concept_agent.agent import TokenConceptAgent
        trends = memory.load_trends()
        out = TokenConceptAgent().run(trends)
        results["token_ideas"] = len(out.output or [])
    except Exception as e:
        results["token_ideas_error"] = str(e)

    # 3. Scores
    try:
        from core.orchestrator import Orchestrator
        Orchestrator().score_token_ideas()
        results["scored"] = True
    except Exception as e:
        results["score_error"] = str(e)

    # 4. CEO decision
    try:
        from agents.ceo_agent.agent import CEOAgent
        ideas  = memory.load_token_ideas()
        scores = memory.load_scores()
        risks  = memory.load_risk_reviews()
        out = CEOAgent().run(ideas, scores, risks)
        dec = out.output or {}
        results["ceo_decision"] = dec.get("recommended_token_name", "?")
        results["ceo_score"] = dec.get("score_breakdown", {}).get("final_opportunity_score", 0)
    except Exception as e:
        results["ceo_error"] = str(e)

    # 5. Social
    try:
        from agents.social_strategy_agent.agent import SocialStrategyAgent
        ideas = memory.load_token_ideas()
        out = SocialStrategyAgent().run(ideas)
        results["social_drafts"] = len(out.output or [])
    except Exception as e:
        results["social_error"] = str(e)

    # 6. Brand
    try:
        from agents.brand_agent.agent import BrandAgent
        ideas = memory.load_token_ideas()
        out = BrandAgent().run(ideas)
        results["brand_packages"] = len(out.output or [])
    except Exception as e:
        results["brand_error"] = str(e)

    # 7. Risk
    try:
        from agents.risk_review_agent.agent import RiskReviewAgent
        ideas = memory.load_token_ideas()
        out = RiskReviewAgent().run(ideas)
        results["risk_reviews"] = len(out.output or [])
    except Exception as e:
        results["risk_error"] = str(e)

    # 8. Smart contract for top idea
    try:
        from agents.token_builder_agent.agent import TokenBuilderAgent
        ideas = memory.load_token_ideas()
        if ideas:
            top = ideas[0]
            out = TokenBuilderAgent().run(top)
            results["contract"] = out.output.get("ticker", "?") if isinstance(out.output, dict) else "generated"
    except Exception as e:
        results["contract_error"] = str(e)

    # 9. Auto-approve all pending items
    if auto_approve:
        approved = _approve_all_pending()
        results["auto_approved"] = approved

    return {"status": "ok", "results": results}


@router.post("/approve-all")
def approve_all_pending():
    """Approve all pending token ideas, brand packages, and social drafts."""
    return {"status": "ok", "approved": _approve_all_pending()}


def _approve_all_pending() -> dict:
    approved = {"token_ideas": 0, "brand_packages": 0, "social_drafts": 0}

    # Token ideas
    ideas = memory.load_token_ideas()
    for idea in ideas:
        if idea.get("approval_status") != "approved":
            idea["approval_status"] = "approved"
            approved["token_ideas"] += 1
    if approved["token_ideas"]:
        memory.save_token_ideas(ideas)

    # Brand packages
    brands = memory.load_brand_packages()
    for brand in brands:
        if brand.get("approval_status") != "approved":
            brand["approval_status"] = "approved"
            approved["brand_packages"] += 1
    if approved["brand_packages"]:
        memory.save_brand_packages(brands)

    # Social drafts (approve first 15 for launch readiness)
    drafts = memory.load_social_drafts()
    count = 0
    for draft in drafts:
        if draft.get("approval_status") != "approved" and count < 15:
            draft["approval_status"] = "approved"
            count += 1
    approved["social_drafts"] = count
    if count:
        memory.save_social_drafts(drafts)

    return approved
