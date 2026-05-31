from __future__ import annotations
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any

from core import memory
from core.schemas import AgentOutput
from core.llm import ask as llm_ask, is_available as llm_ready


CONCEPT_TEMPLATES = {
    "twitter": {
        "meme_angle": "Twitter-native meme with punchy one-liners and quote-tweet bait",
        "community": "CT degens, influencer followers, meme traders",
        "utility": "Community governance and tip token",
    },
    "reddit": {
        "meme_angle": "Community-driven narrative with deep lore and running jokes",
        "community": "Reddit power users, long-form thinkers, community builders",
        "utility": "Forum reputation and reward token",
    },
    "tiktok": {
        "meme_angle": "Visual, fast, normie-accessible humor with 10-second hooks",
        "community": "TikTok finance creators, Gen Z newcomers, pet and lifestyle audiences",
        "utility": "Creator reward and content monetization",
    },
    "youtube": {
        "meme_angle": "Documentary-style narrative, serious with absurdist undertones",
        "community": "Finance YouTube audience, researchers, semi-serious investors",
        "utility": "Educational content and research bounty token",
    },
    "crypto_news": {
        "meme_angle": "Industry insider joke with technical credibility",
        "community": "Crypto-native builders, VCs, protocol developers",
        "utility": "Protocol fee and governance token",
    },
}


def _ai_enhance_concept(trend: Dict, opportunity: str) -> Dict:
    """Use Gemini to generate a creative token concept from a trend opportunity."""
    phrase = trend.get("phrase", "")
    platform = trend.get("source_platform", "twitter")
    why = trend.get("why_it_matters", "")

    prompt = f"""You are a crypto token concept designer. Create ONE viral meme token concept.

Trend: "{phrase}" (from {platform})
Opportunity: "{opportunity}"
Why it matters: "{why}"

Respond with ONLY a JSON object (no markdown, no explanation):
{{
  "token_name": "catchy 2-3 word name",
  "ticker": "3-5 letter ticker symbol",
  "one_line_narrative": "one punchy sentence (max 12 words)",
  "meme_angle": "what makes it funny/viral",
  "target_community": "who will love this token",
  "utility_angle": "simple utility or governance angle",
  "why_now": "why this exact moment is perfect (1 sentence)"
}}"""

    raw = llm_ask(prompt, fallback="")
    if raw:
        try:
            # Strip markdown code fences if present
            clean = raw.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return json.loads(clean.strip())
        except Exception:
            pass
    return {}


def _generate_concepts_for_trend(trend: Dict) -> List[Dict]:
    """Generate 1-3 token concept cards from a trend."""
    platform = trend.get("source_platform", "twitter")
    template = CONCEPT_TEMPLATES.get(platform, CONCEPT_TEMPLATES["twitter"])
    opportunities = trend.get("token_narrative_opportunities", [])
    if not opportunities:
        opportunities = [f"Token based on '{trend['phrase']}' narrative"]

    concepts = []
    for opp in opportunities[:2]:
        # Try AI-enhanced concept first, fall back to template
        ai_data = _ai_enhance_concept(trend, opp) if llm_ready() else {}

        name    = ai_data.get("token_name") or _derive_name_ticker(opp, trend["phrase"])[0]
        ticker  = ai_data.get("ticker") or _derive_name_ticker(opp, trend["phrase"])[1]
        narrative = ai_data.get("one_line_narrative") or opp
        meme    = ai_data.get("meme_angle") or template["meme_angle"]
        community = ai_data.get("target_community") or template["community"]
        utility = ai_data.get("utility_angle") or template["utility"]
        why_now = ai_data.get("why_now") or trend.get("why_it_matters", "Trend is live and accelerating.")

        concepts.append({
            "id": f"idea_{str(uuid.uuid4())[:8]}",
            "token_name": name,
            "ticker": ticker,
            "one_line_narrative": narrative,
            "target_community": community,
            "meme_angle": meme,
            "utility_angle": utility,
            "why_now": why_now,
            "possible_risks": _assess_risks(trend),
            "virality_score": min(100, trend.get("meme_potential", 60) + 5),
            "launch_readiness_score": _launch_readiness(trend),
            "meme_potential": trend.get("meme_potential", 60),
            "community_potential": trend.get("community_size", 60),
            "novelty": trend.get("novelty_score", 60),
            "timing": _timing_score(trend),
            "technical_feasibility": 85,
            "brand_strength": 65,
            "source_trend_id": trend.get("id"),
            "created_at": datetime.utcnow().isoformat(),
            "approval_status": "pending",
            "ceo_notes": "",
            "ai_generated": bool(ai_data),
        })
    return concepts


def _derive_name_ticker(opportunity: str, phrase: str) -> tuple[str, str]:
    words = opportunity.upper().split()
    ticker_words = [w for w in words if len(w) >= 3 and w.isalpha()]
    if ticker_words:
        ticker = ticker_words[0][:5]
    else:
        ticker = phrase.upper().replace(" ", "")[:5]

    phrase_words = phrase.title().split()
    if len(phrase_words) >= 2:
        name = " ".join(phrase_words[:2])
    else:
        name = phrase.title()

    return name, ticker


def _assess_risks(trend: Dict) -> List[str]:
    risks = []
    if trend.get("saturation_level", 0) > 50:
        risks.append("High market saturation — crowded narrative space")
    if trend.get("expected_lifespan_days", 30) < 14:
        risks.append("Short trend lifespan — timing is critical")
    if trend.get("crypto_relevance", 50) < 60:
        risks.append("Low crypto relevance — harder to convert trend to token buyers")
    if not risks:
        risks.append("Standard launch and execution risk")
    return risks


def _launch_readiness(trend: Dict) -> float:
    base = 60.0
    if trend.get("crypto_relevance", 0) > 80:
        base += 10
    if trend.get("expected_lifespan_days", 0) > 20:
        base += 10
    if trend.get("saturation_level", 100) < 30:
        base += 10
    return min(100.0, base)


def _timing_score(trend: Dict) -> float:
    lifespan = trend.get("expected_lifespan_days", 14)
    velocity = trend.get("velocity_score", 50)
    saturation = trend.get("saturation_level", 50)
    raw = velocity * 0.5 + (100 - saturation) * 0.3 + min(lifespan, 60) * 0.2
    return round(min(100.0, raw), 1)


class TokenConceptAgent:
    NAME = "token_concept_agent"

    def run(self, trends: List[Dict]) -> AgentOutput:
        existing = memory.load_token_ideas()
        existing_ids = {i.get("source_trend_id") for i in existing}

        new_concepts = []
        for trend in trends:
            if trend.get("composite_score", 0) < 50:
                continue
            concepts = _generate_concepts_for_trend(trend)
            new_concepts.extend(concepts)

        all_ideas = existing + new_concepts
        memory.save_token_ideas(all_ideas)

        return AgentOutput(
            timestamp=datetime.utcnow(),
            agent_name=self.NAME,
            input_summary=f"Processed {len(trends)} trends, generated {len(new_concepts)} new token concepts",
            output=new_concepts,
            score=None,
            next_recommended_action="Run run-risk-review to assess each concept before CEO scoring",
        )
