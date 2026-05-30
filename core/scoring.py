from __future__ import annotations
from datetime import datetime
from core.schemas import OpportunityScore


WEIGHTS = {
    "trend_strength":       0.20,
    "meme_potential":       0.20,
    "community_potential":  0.15,
    "novelty":              0.10,
    "timing":               0.15,
    "technical_feasibility":0.10,
    "brand_strength":       0.10,
    "risk_score":           -0.20,   # penalty
}


def compute_opportunity_score(
    token_idea_id: str,
    trend_strength: float,
    meme_potential: float,
    community_potential: float,
    novelty: float,
    timing: float,
    technical_feasibility: float,
    brand_strength: float,
    risk_score: float,
) -> OpportunityScore:
    raw = (
        trend_strength        * WEIGHTS["trend_strength"] +
        meme_potential        * WEIGHTS["meme_potential"] +
        community_potential   * WEIGHTS["community_potential"] +
        novelty               * WEIGHTS["novelty"] +
        timing                * WEIGHTS["timing"] +
        technical_feasibility * WEIGHTS["technical_feasibility"] +
        brand_strength        * WEIGHTS["brand_strength"] +
        risk_score            * WEIGHTS["risk_score"]   # negative weight
    )
    final = max(0.0, min(100.0, raw))

    return OpportunityScore(
        token_idea_id=token_idea_id,
        trend_strength=trend_strength,
        meme_potential=meme_potential,
        community_potential=community_potential,
        novelty=novelty,
        timing=timing,
        technical_feasibility=technical_feasibility,
        brand_strength=brand_strength,
        risk_score=risk_score,
        final_opportunity_score=round(final, 2),
        calculated_at=datetime.utcnow(),
    )


def rank_token_ideas(scores: list[OpportunityScore]) -> list[OpportunityScore]:
    return sorted(scores, key=lambda s: s.final_opportunity_score, reverse=True)


def score_trend(velocity: float, novelty: float, meme: float,
                crypto_rel: float, community: float, saturation: float) -> float:
    raw = (
        velocity    * 0.25 +
        novelty     * 0.20 +
        meme        * 0.20 +
        crypto_rel  * 0.15 +
        community   * 0.10 +
        (100 - saturation) * 0.10
    )
    return round(min(100.0, max(0.0, raw)), 2)
