from __future__ import annotations
import uuid
from datetime import datetime
from typing import List, Dict

from core import memory
from core.schemas import AgentOutput
from core.llm import ask as llm_ask, is_available as llm_ready


def _ai_slogans(name: str, ticker: str, narrative: str, meme: str) -> list:
    if not llm_ready():
        return []
    prompt = f"""Generate 5 punchy, viral crypto token slogans for ${ticker} ({name}).
Concept: {narrative}
Meme angle: {meme}
Rules: Short (max 10 words each). Crypto-native tone. No financial promises. Witty, shareable.
Return ONLY 5 slogans, one per line, no numbers or bullets."""
    result = llm_ask(prompt, fallback="")
    if result:
        return [s.strip() for s in result.strip().split("\n") if s.strip()][:5]
    return []


def _ai_manifesto(name: str, ticker: str, narrative: str, why_now: str) -> str:
    if not llm_ready():
        return ""
    prompt = f"""Write a powerful, emotional crypto token manifesto for {name} (${ticker}).
Concept: {narrative}
Why now: {why_now}
Style: Short paragraphs. Raw, honest, internet-native voice. No hype, no promises. Pure conviction.
Max 120 words. Make it feel like a founding document."""
    return llm_ask(prompt, fallback="")


def _ai_website_copy(name: str, ticker: str, narrative: str, community: str) -> dict:
    if not llm_ready():
        return {}
    prompt = f"""Write website copy for {name} (${ticker}) crypto token.
Concept: {narrative}
Target community: {community}
Return exactly these 3 sections labeled:
HERO: [one punchy headline, max 8 words]
ABOUT: [2 sentence about section, crypto-native tone]
TOKENOMICS: [one sentence fair launch statement]"""
    result = llm_ask(prompt, fallback="")
    copy = {}
    if result:
        for line in result.split("\n"):
            if line.startswith("HERO:"):
                copy["hero_headline"] = line.replace("HERO:", "").strip()
            elif line.startswith("ABOUT:"):
                copy["about_section"] = line.replace("ABOUT:", "").strip()
            elif line.startswith("TOKENOMICS:"):
                copy["tokenomics_intro"] = line.replace("TOKENOMICS:", "").strip()
    return copy


def _generate_brand(concept: Dict) -> Dict:
    name = concept.get("token_name", "Token")
    ticker = concept.get("ticker", "TKN")
    narrative = concept.get("one_line_narrative", "")
    community = concept.get("target_community", "crypto community")
    meme = concept.get("meme_angle", "")
    why_now = concept.get("why_now", "")

    # AI-generated content (falls back to templates if no key)
    ai_slogans   = _ai_slogans(name, ticker, narrative, meme)
    ai_manifesto = _ai_manifesto(name, ticker, narrative, why_now)
    ai_copy      = _ai_website_copy(name, ticker, narrative, community)

    slogans = ai_slogans if ai_slogans else [
        f"${ticker} — {narrative[:60]}",
        "The coin the internet was waiting for.",
        "Not just a token. A movement.",
        "Built by the community. For the community.",
        "Early is everything. You're early.",
    ]

    manifesto = ai_manifesto if ai_manifesto else (
        f"We are {name}.\n\nWe didn't start with a VC deck. We started with a meme.\n\n"
        f"Every great movement starts as a joke. Then it becomes inevitable.\n\n"
        f"${ticker} is our bet on the internet. On community. On timing.\n\nWelcome to {name}."
    )

    return {
        "id": f"brand_{str(uuid.uuid4())[:8]}",
        "token_idea_id": concept.get("id"),
        "token_name_options": [
            name,
            f"{name} Protocol",
            f"The {name}",
            f"{ticker} Token",
        ],
        "ticker_options": [
            ticker,
            f"{ticker}X",
            ticker[:3],
        ],
        "slogans": slogans,
        "tone_of_voice": (
            f"Confident, irreverent, and self-aware. The {name} brand speaks like "
            f"the smartest person in the room who refuses to take themselves too seriously. "
            f"Meme-literate but not cringe. Punchy. Never corporate. Never preachy."
        ),
        "visual_direction": (
            f"Dark background with neon accent colors. Primary: electric green or hot pink. "
            f"Typography: bold grotesque or pixel-style. Logo: simple, immediately recognizable "
            f"at 32x32px. Aesthetic: cyberpunk meets internet culture. "
            f"Vibe: 4am energy, terminal green, early internet nostalgia."
        ),
        "logo_prompts": [
            f"Minimalist logo for ${ticker} cryptocurrency. Dark background, single icon, neon glow effect. "
            f"Icon represents: {name.lower()}. Clean vector style. No text.",
            f"Pixel art logo of {name.lower()} character. 64x64 grid. Neon palette. Crypto aesthetic.",
            f"Abstract geometric mark for {ticker} token. Sacred geometry inspired. Gradient from purple to cyan.",
        ],
        "website_copy": {
            "hero_headline": ai_copy.get("hero_headline", f"${ticker}"),
            "hero_subheadline": narrative,
            "cta_primary": "Join the Community",
            "cta_secondary": "Read the Manifesto",
            "about_section": ai_copy.get("about_section", (
                f"{name} is a community-driven token born from internet culture and crypto. {narrative} "
                f"We don't promise returns. We promise a movement."
            )),
            "tokenomics_intro": ai_copy.get("tokenomics_intro", "Fair launch. Community first. No VC allocation."),
            "footer_disclaimer": (
                f"${ticker} is a community token. Nothing on this website constitutes financial advice. "
                f"Crypto assets are highly volatile. Never invest more than you can afford to lose. DYOR."
            ),
        },
        "landing_page_structure": [
            "Hero: Token name + one-line narrative + CTA to Telegram",
            "Why now: trend context card",
            "Tokenomics: simple allocation pie chart",
            "Community: Telegram + Discord + Twitter links",
            "Manifesto: short scrollable statement",
            "Roadmap: Phase 1 (launch), Phase 2 (utility), Phase 3 (governance)",
            "FAQ: 5-7 most common questions",
            "Footer: disclaimer + contract address (post-launch)",
        ],
        "whitepaper_lite": f"""# ${ticker} — {name}
## What is {name}?
{narrative}

## Why Now?
{concept.get('why_now', 'The trend is live. The community is ready. The moment is now.')}

## Tokenomics
- Total Supply: 1,000,000,000 {ticker}
- Liquidity: 40% (locked)
- Community: 30%
- Treasury: 10%
- Team: 10% (vested 12 months)
- Marketing: 10%

## Community
Target: {community}

## Roadmap
- Phase 1: Fair launch, Telegram/Discord setup, social campaign
- Phase 2: CEX listing outreach, community events, meme competitions
- Phase 3: Utility development, partnerships, governance vote

## Disclaimer
{ticker} is a community meme token. This is not financial advice. DYOR.
""",
        "manifesto": manifesto,
        "meme_language": [
            f"WAGMI {ticker}",
            f"${ticker} szn is here",
            f"ser, have you heard about {name}?",
            f"not selling my {ticker} until [absurd goal]",
            f"gm {ticker} holders",
            f"my {ticker} bag is not a financial decision, it's a lifestyle",
            f"if you know, you know. ${ticker}.",
        ],
        "brand_consistency_guide": (
            f"1. Always write the ticker as ${ticker} (dollar sign prefix).\n"
            f"2. Never promise price performance or returns.\n"
            f"3. Tone: playful, not reckless. Smart, not pretentious.\n"
            f"4. Every post must be shareable standalone — no context needed.\n"
            f"5. Dark backgrounds only in official branded assets.\n"
            f"6. Logo must appear in all header images.\n"
            f"7. Community > team. Always position the community as the protagonist.\n"
            f"8. Legal disclaimer on website, never in social posts (too corporate).\n"
        ),
        "created_at": datetime.utcnow().isoformat(),
        "approval_status": "pending",
    }


class BrandAgent:
    NAME = "brand_agent"

    def run(self, concepts: List[Dict]) -> AgentOutput:
        existing = memory.load_brand_packages()
        existing_ids = {b["token_idea_id"] for b in existing}

        new_brands = []
        for concept in concepts:
            if concept.get("id") in existing_ids:
                continue
            brand = _generate_brand(concept)
            new_brands.append(brand)

        all_brands = existing + new_brands
        memory.save_brand_packages(all_brands)

        return AgentOutput(
            timestamp=datetime.utcnow(),
            agent_name=self.NAME,
            input_summary=f"Generated {len(new_brands)} brand packages for {len(concepts)} concepts",
            output=new_brands,
            score=None,
            next_recommended_action="Review brand packages in dashboard and approve or request revision",
        )
