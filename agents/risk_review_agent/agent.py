from __future__ import annotations
import uuid
from datetime import datetime
from typing import List, Dict

from core import memory
from core.schemas import AgentOutput


RISKY_PHRASES = [
    "guaranteed", "100x", "moon", "get rich", "risk-free",
    "insider", "pump", "pre-sale bonus", "limited spots",
    "exclusive deal", "celebrity endorsement", "endorsed by",
]

RISKY_CLAIMS = [
    "first ever", "only one", "revolutionary", "never been done",
    "will 10x", "destined to", "cannot fail",
]

PLATFORM_RISK_KEYWORDS = {
    "twitter": ["spam", "follow for follow", "retweet to win", "guaranteed airdrop"],
    "tiktok": ["not an ad", "crypto giveaway", "send crypto"],
    "reddit": ["shill", "paid promotion without disclosure"],
}

TRADEMARK_WATCH = ["pepe", "doge", "shib", "floki", "elon", "trump", "biden", "apple", "google"]


def _score_ip_risk(concept: Dict) -> float:
    name = (concept.get("token_name", "") + " " + concept.get("ticker", "")).lower()
    hits = sum(1 for w in TRADEMARK_WATCH if w in name)
    return min(10.0, hits * 3.0 + 1.0)


def _score_marketing_risk(concept: Dict) -> float:
    text = " ".join([
        concept.get("one_line_narrative", ""),
        concept.get("meme_angle", ""),
        concept.get("utility_angle", ""),
    ]).lower()
    hits = sum(1 for p in RISKY_PHRASES if p in text)
    claims = sum(1 for c in RISKY_CLAIMS if c in text)
    return min(10.0, hits * 1.5 + claims * 2.0 + 1.0)


def _score_technical_risk(concept: Dict) -> float:
    # Simple heuristic: pure meme = low tech risk, complex utility = moderate
    utility = concept.get("utility_angle", "").lower()
    if "pure meme" in utility or "community" in utility:
        return 1.5
    if "defi" in utility or "lending" in utility or "bridge" in utility:
        return 6.0
    return 3.0


def _score_reputational_risk(concept: Dict) -> float:
    risks = concept.get("possible_risks", [])
    base = 2.0 + len(risks) * 0.5
    return min(10.0, base)


def _flag_phrases(concept: Dict) -> List[str]:
    all_text = " ".join([
        concept.get("one_line_narrative", ""),
        concept.get("meme_angle", ""),
        concept.get("why_now", ""),
    ]).lower()
    return [p for p in RISKY_PHRASES if p in all_text]


def _flag_claims(concept: Dict) -> List[str]:
    all_text = " ".join([
        concept.get("one_line_narrative", ""),
        concept.get("why_now", ""),
        concept.get("utility_angle", ""),
    ]).lower()
    return [c for c in RISKY_CLAIMS if c in all_text]


def _weak_narratives(concept: Dict) -> List[str]:
    weak = []
    if len(concept.get("one_line_narrative", "")) < 20:
        weak.append("Narrative too short — needs more specificity")
    if not concept.get("utility_angle"):
        weak.append("No utility angle — pure meme is viable but limits longevity")
    if concept.get("novelty", 100) < 50:
        weak.append("Low novelty score — market may already have similar tokens")
    return weak


class RiskReviewAgent:
    NAME = "risk_review_agent"

    def run(self, concepts: List[Dict]) -> AgentOutput:
        existing_reviews = memory.load_risk_reviews()
        reviewed_ids = {r["subject_id"] for r in existing_reviews}

        new_reviews = []
        for concept in concepts:
            cid = concept.get("id")
            if cid in reviewed_ids:
                continue

            ip_risk       = _score_ip_risk(concept)
            marketing_risk= _score_marketing_risk(concept)
            tech_risk     = _score_technical_risk(concept)
            rep_risk      = _score_reputational_risk(concept)
            platform_risk = 3.0
            token_risk    = (ip_risk + marketing_risk + tech_risk) / 3

            overall = round(
                token_risk * 0.25 + marketing_risk * 0.20 + ip_risk * 0.20 +
                platform_risk * 0.15 + rep_risk * 0.10 + tech_risk * 0.10,
                2
            )

            flagged_p = _flag_phrases(concept)
            flagged_c = _flag_claims(concept)
            weak_n    = _weak_narratives(concept)

            required = []
            if ip_risk > 5:
                required.append("Trademark/IP legal review required")
            if marketing_risk > 4:
                required.append("Marketing copy legal review required")
            if overall > 6:
                required.append("Full compliance review before launch")

            revisions = []
            if flagged_p:
                revisions.append(f"Remove or qualify phrases: {', '.join(flagged_p)}")
            if flagged_c:
                revisions.append(f"Soften claims: {', '.join(flagged_c)}")
            if weak_n:
                revisions.extend(weak_n)

            review = {
                "id": f"risk_{str(uuid.uuid4())[:8]}",
                "subject_id": cid,
                "subject_type": "token_concept",
                "token_risk_score": round(token_risk, 2),
                "marketing_risk_score": round(marketing_risk, 2),
                "ip_trademark_risk": round(ip_risk, 2),
                "platform_risk": round(platform_risk, 2),
                "reputational_risk": round(rep_risk, 2),
                "technical_risk": round(tech_risk, 2),
                "overall_risk_score": overall,
                "flagged_phrases": flagged_p,
                "flagged_claims": flagged_c,
                "weak_narratives": weak_n,
                "required_reviews": required,
                "suggested_revisions": revisions,
                "reviewed_at": datetime.utcnow().isoformat(),
                "reviewer_agent": self.NAME,
            }
            new_reviews.append(review)

        all_reviews = existing_reviews + new_reviews
        memory.save_risk_reviews(all_reviews)

        avg_risk = round(sum(r["overall_risk_score"] for r in new_reviews) / max(len(new_reviews), 1), 2) if new_reviews else 0

        return AgentOutput(
            timestamp=datetime.utcnow(),
            agent_name=self.NAME,
            input_summary=f"Reviewed {len(concepts)} concepts, produced {len(new_reviews)} new risk reports",
            output=new_reviews,
            score=avg_risk,
            next_recommended_action="Run score-token-ideas then ceo-decision to rank and choose the best concept",
        )
