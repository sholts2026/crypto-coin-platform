"""
Community Manager Agent
Broadcasts to Telegram Channel + Discord on CEO events.
Runs under the CEO — auto-posts when decisions are made.
"""
from __future__ import annotations
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional

import httpx

from core import memory
from core.schemas import AgentOutput
from core.llm import ask as llm_ask, is_available as llm_ready


# ──────────────────────────────────────────────
# Channel helpers
# ──────────────────────────────────────────────

def _telegram_channel_id() -> str:
    return os.environ.get("TELEGRAM_CHANNEL_ID", "")

def _discord_webhook_url() -> str:
    return os.environ.get("DISCORD_WEBHOOK_URL", "")

def _telegram_bot_token() -> str:
    return os.environ.get("TELEGRAM_BOT_TOKEN", "")


def post_to_telegram_channel(text: str) -> bool:
    """Post a message to the Telegram channel."""
    token = _telegram_bot_token()
    channel = _telegram_channel_id()
    if not token or not channel:
        return False
    try:
        r = httpx.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": channel, "text": text, "parse_mode": "Markdown"},
            timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return False


def post_to_discord(text: str, title: str = "") -> bool:
    """Post a message to Discord via webhook."""
    webhook = _discord_webhook_url()
    if not webhook:
        return False
    try:
        payload = {
            "embeds": [{
                "title": title or "CryptoLaunch AI Update",
                "description": text,
                "color": 0x00FF88,
                "footer": {"text": "CryptoLaunch AI • All outputs require human approval"},
                "timestamp": datetime.utcnow().isoformat(),
            }]
        }
        r = httpx.post(webhook, json=payload, timeout=10)
        return r.status_code in (200, 204)
    except Exception:
        return False


def broadcast(text: str, title: str = "") -> Dict:
    """Broadcast to all configured channels."""
    tg = post_to_telegram_channel(text)
    dc = post_to_discord(text, title)
    return {
        "telegram": tg,
        "discord": dc,
        "channels_reached": sum([tg, dc]),
    }


# ──────────────────────────────────────────────
# AI message generators
# ──────────────────────────────────────────────

def _generate_ceo_announcement(decision: Dict) -> str:
    name   = decision.get("recommended_token_name", "Token")
    score  = decision.get("score_breakdown", {}).get("final_opportunity_score", 0)
    reasons = decision.get("selection_reasons", [])

    if llm_ready():
        reasons_txt = "\n".join(f"- {r}" for r in reasons[:3])
        prompt = f"""Write a hype but honest Telegram announcement for a crypto token launch.
Token: {name}
Opportunity score: {score:.0f}/100
Key reasons: {reasons_txt}

Rules:
- Max 200 words
- Crypto-native tone, use emojis
- End with "All investments require your own research. Not financial advice."
- Do NOT mention price targets or guaranteed returns
- Mention the community decides everything"""

        result = llm_ask(prompt, fallback="")
        if result:
            return result

    # Template fallback
    ticker = name.split("(")[-1].rstrip(")").strip() if "(" in name else "TOKEN"
    return (
        f"🚀 *CEO DECISION: {name}*\n\n"
        f"Our AI CEO has selected *{name}* as the next token launch candidate.\n\n"
        f"📊 Opportunity Score: *{score:.0f}/100*\n\n"
        f"{''.join(f'✅ {r}' + chr(10) for r in reasons[:3])}\n"
        f"🗳️ Community approval vote coming soon.\n\n"
        f"_Not financial advice. DYOR._"
    )


def _generate_daily_update() -> str:
    trends    = memory.load_trends()
    ideas     = memory.load_token_ideas()
    drafts    = memory.load_social_drafts()
    decisions = memory.load_decisions()

    best = decisions[-1] if decisions else None
    name  = best.get("recommended_token_name", "TBD") if best else "TBD"

    if llm_ready():
        prompt = f"""Write a short daily community update for a crypto token launch platform.
Current status:
- Trending narratives tracked: {len(trends)}
- Token concepts in pipeline: {len(ideas)}
- Social posts ready: {len(drafts)}
- CEO recommendation: {name}

Write a friendly, energetic 3-sentence Telegram update.
Use emojis. End with "Stay tuned 👀"
Do not mention prices or financial advice."""
        result = llm_ask(prompt, fallback="")
        if result:
            return result

    return (
        f"📡 *Daily Update*\n\n"
        f"🔍 Monitoring {len(trends)} trends\n"
        f"💡 {len(ideas)} token concepts in pipeline\n"
        f"✍️ {len(drafts)} social posts ready\n"
        f"👑 CEO pick: *{name}*\n\n"
        f"Stay tuned 👀"
    )


def _generate_welcome_message(concept: Dict) -> str:
    name   = concept.get("token_name", "Token")
    ticker = concept.get("ticker", "TKN")
    narrative = concept.get("one_line_narrative", "")

    return (
        f"👋 *Welcome to {name} Community!*\n\n"
        f"_{narrative}_\n\n"
        f"You're early. That's the only advantage that matters.\n\n"
        f"${ticker} is community-driven. No VCs. No insiders.\n\n"
        f"📌 Read pinned messages\n"
        f"💬 Introduce yourself\n"
        f"🤝 Get involved\n\n"
        f"WAGMI 🟢"
    )


# ──────────────────────────────────────────────
# Community package builder (kept from v1)
# ──────────────────────────────────────────────

def _generate_community_package(concept: Dict) -> Dict:
    name   = concept.get("token_name", "Token")
    ticker = concept.get("ticker", "TKN")

    return {
        "id": f"comm_{str(uuid.uuid4())[:8]}",
        "token_idea_id": concept.get("id"),
        "welcome_message": _generate_welcome_message(concept),
        "faq_drafts": [
            {"q": f"What is ${ticker}?",    "a": concept.get("one_line_narrative", "A community token.")},
            {"q": "Is this a rug pull?",     "a": f"${ticker} is a community project. Liquidity locked. Contract published on Etherscan. DYOR."},
            {"q": "Who is the team?",        "a": f"${ticker} is community-driven and pseudonymous. The contract is the source of truth."},
            {"q": "What is total supply?",   "a": "1,000,000,000 tokens. No minting after launch."},
            {"q": "How do I buy?",           "a": f"${ticker} will launch on DEX. Instructions in official channels only. Never buy from DM links."},
        ],
        "channel_structure": {
            "telegram": [f"{name} Announcements", f"{name} Community", f"{name} Memes"],
            "discord":  {
                "Info":      ["#rules", "#announcements"],
                "Community": ["#general", "#memes", "#introductions"],
                "Trading":   ["#price-chat", "#dyor"],
            },
        },
        "onboarding_message": _generate_welcome_message(concept),
        "created_at": datetime.utcnow().isoformat(),
    }


# ──────────────────────────────────────────────
# Agent class
# ──────────────────────────────────────────────

class CommunityAgent:
    NAME = "community_agent"

    def run(self, concepts: List[Dict]) -> AgentOutput:
        packages = [_generate_community_package(c) for c in concepts]
        existing = memory.load_json("community_packages.json", [])
        memory.save_json("community_packages.json", existing + packages)
        return AgentOutput(
            timestamp=datetime.utcnow(),
            agent_name=self.NAME,
            input_summary=f"Generated community packages for {len(concepts)} token concepts",
            output=packages,
            score=None,
            next_recommended_action="Set up Telegram channel + Discord, then broadcast CEO decision.",
        )

    def broadcast_ceo_decision(self, decision: Dict) -> Dict:
        """Auto-called when CEO approves — posts announcement to all channels."""
        text   = _generate_ceo_announcement(decision)
        title  = f"CEO Decision: {decision.get('recommended_token_name', 'Token')}"
        result = broadcast(text, title)
        result["message"] = text
        return result

    def send_daily_update(self) -> Dict:
        """Post daily community update to all channels."""
        text   = _generate_daily_update()
        result = broadcast(text, "Daily Update")
        result["message"] = text
        return result
