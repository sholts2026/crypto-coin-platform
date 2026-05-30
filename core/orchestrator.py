from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional

from core import memory
from core.scoring import compute_opportunity_score, rank_token_ideas


class Orchestrator:
    """
    Coordinates agent execution order:
    TrendHunter → TokenConcept → RiskReview → Brand → SocialStrategy → Community → CEO
    TokenBuilder is triggered after CEO approves a concept.
    """

    def collect_trends(self, use_mock: bool = True):
        from agents.trend_hunter_agent.agent import TrendHunterAgent
        agent = TrendHunterAgent(use_mock=use_mock)
        result = agent.run()
        return result

    def generate_token_ideas(self, trend_ids: Optional[list[str]] = None):
        from agents.token_concept_agent.agent import TokenConceptAgent
        trends = memory.load_trends()
        if trend_ids:
            trends = [t for t in trends if t.get("id") in trend_ids]
        agent = TokenConceptAgent()
        result = agent.run(trends)
        return result

    def run_risk_review(self):
        from agents.risk_review_agent.agent import RiskReviewAgent
        ideas = memory.load_token_ideas()
        agent = RiskReviewAgent()
        result = agent.run(ideas)
        return result

    def generate_brand_packages(self, token_idea_id: Optional[str] = None):
        from agents.brand_agent.agent import BrandAgent
        ideas = memory.load_token_ideas()
        if token_idea_id:
            ideas = [i for i in ideas if i.get("id") == token_idea_id]
        agent = BrandAgent()
        result = agent.run(ideas)
        return result

    def generate_social_calendar(self, token_idea_id: Optional[str] = None):
        from agents.social_strategy_agent.agent import SocialStrategyAgent
        ideas = memory.load_token_ideas()
        if token_idea_id:
            ideas = [i for i in ideas if i.get("id") == token_idea_id]
        agent = SocialStrategyAgent()
        result = agent.run(ideas)
        return result

    def prepare_contract(self, token_idea_id: str, chain: str = "ethereum"):
        from agents.token_builder_agent.agent import TokenBuilderAgent
        ideas = memory.load_token_ideas()
        idea = next((i for i in ideas if i.get("id") == token_idea_id), None)
        if not idea:
            raise ValueError(f"Token idea {token_idea_id} not found")
        agent = TokenBuilderAgent()
        result = agent.run(idea, chain=chain)
        return result

    def score_token_ideas(self):
        ideas = memory.load_token_ideas()
        risk_reviews = memory.load_risk_reviews()
        risk_map = {r["subject_id"]: r for r in risk_reviews}
        scores = []
        for idea in ideas:
            iid = idea["id"]
            risk = risk_map.get(iid, {})
            score = compute_opportunity_score(
                token_idea_id=iid,
                trend_strength=idea.get("virality_score", 60),
                meme_potential=idea.get("meme_potential", 60),
                community_potential=idea.get("community_potential", 60),
                novelty=idea.get("novelty", 60),
                timing=idea.get("timing", 60),
                technical_feasibility=idea.get("technical_feasibility", 80),
                brand_strength=idea.get("brand_strength", 60),
                risk_score=risk.get("overall_risk_score", 5) * 10,
            )
            scores.append(score.model_dump())
        memory.save_scores(scores)
        return scores

    def ceo_decision(self):
        from agents.ceo_agent.agent import CEOAgent
        ideas = memory.load_token_ideas()
        scores = memory.load_scores()
        risks = memory.load_risk_reviews()
        agent = CEOAgent()
        result = agent.run(ideas, scores, risks)
        return result

    def export_report(self) -> dict:
        from agents.ceo_agent.agent import CEOAgent
        decisions = memory.load_decisions()
        trends = memory.load_trends()
        ideas = memory.load_token_ideas()
        scores = memory.load_scores()
        risks = memory.load_risk_reviews()
        drafts = memory.load_social_drafts()
        brands = memory.load_brand_packages()

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_trends":        len(trends),
                "total_token_ideas":   len(ideas),
                "total_social_drafts": len(drafts),
                "total_risk_reviews":  len(risks),
                "total_decisions":     len(decisions),
            },
            "top_trends":  trends[:5],
            "top_ideas":   sorted(scores, key=lambda s: s.get("final_opportunity_score", 0), reverse=True)[:3],
            "latest_decision": decisions[-1] if decisions else None,
        }
