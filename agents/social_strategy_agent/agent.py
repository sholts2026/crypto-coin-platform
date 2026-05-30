from __future__ import annotations
import uuid
from datetime import datetime, timedelta
from typing import List, Dict

from core import memory
from core.schemas import AgentOutput

PLATFORMS = ["twitter", "reddit", "telegram", "discord", "tiktok"]

POST_TEMPLATES = {
    "twitter": [
        {
            "post_type": "announcement",
            "template": "Introducing ${ticker}.\n\n{narrative}\n\nThis is the beginning. 🧵",
            "goal": "Launch awareness and thread engagement",
        },
        {
            "post_type": "meme",
            "template": "{meme_angle}\n\n${{ticker}}",
            "goal": "Viral spread via quote-tweet and share",
        },
        {
            "post_type": "thread",
            "template": "Why ${ticker} is different. A thread.\n\n1/ {why_now}\n\n2/ {utility_angle}\n\n3/ The community decides everything. WAGMI.",
            "goal": "Educate and build credibility",
        },
        {
            "post_type": "poll",
            "template": "What does ${ticker} need most right now?\n\n🟢 More memes\n🔵 CEX listing\n🟣 Real utility\n⚫ More holders\n\nVote and RT 👇",
            "goal": "Community engagement and algorithm boost",
        },
    ],
    "reddit": [
        {
            "post_type": "educational",
            "template": "## Why {token_name} is the most interesting token narrative this week\n\n{why_now}\n\n**The concept:** {narrative}\n\n**Community:** {community}\n\nNot financial advice. DYOR. This is a community discussion.",
            "goal": "Credibility and organic upvote growth",
        },
        {
            "post_type": "meme",
            "template": "When {meme_angle} [image post]",
            "goal": "r/memecoins front page hit",
        },
    ],
    "telegram": [
        {
            "post_type": "announcement",
            "template": "🚀 Welcome to {token_name} ({ticker})\n\n{narrative}\n\nThis group is the home of the {ticker} community. Share, discuss, and build together.\n\nRules:\n1. No spam\n2. No price predictions\n3. Be respectful\n4. Have fun\n\nLet's go! 🟢",
            "goal": "Community onboarding and culture setting",
        },
    ],
    "discord": [
        {
            "post_type": "announcement",
            "template": "**#{ticker}-general**\n\nWelcome to the official {token_name} Discord!\n\nChannels:\n📢 #announcements\n💬 #general\n🐸 #memes\n🤝 #introductions\n🔧 #dev-talk\n📊 #price-chat (no financial advice)\n\nRead the rules. Introduce yourself. Let's build.",
            "goal": "Discord server culture and onboarding",
        },
    ],
    "tiktok": [
        {
            "post_type": "educational",
            "template": "POV: you found {token_name} before it was everywhere 👀\n\n{meme_angle}\n\n${ticker} — follow for updates\n\n#crypto #{ticker_lower} #memecoins #cryptotok",
            "goal": "Normie discovery and follower growth",
        },
    ],
}


def _fill_template(template: str, concept: Dict) -> str:
    ticker = concept.get("ticker", "TKN")
    return (
        template
        .replace("{ticker}", ticker)
        .replace("{ticker_lower}", ticker.lower())
        .replace("{token_name}", concept.get("token_name", "Token"))
        .replace("{narrative}", concept.get("one_line_narrative", "")[:120])
        .replace("{meme_angle}", concept.get("meme_angle", "")[:140])
        .replace("{why_now}", concept.get("why_now", "")[:200])
        .replace("{utility_angle}", concept.get("utility_angle", "")[:120])
        .replace("{community}", concept.get("target_community", "crypto community"))
    )


def _check_risk_flags(text: str) -> List[str]:
    risky = ["100x", "guaranteed", "moon", "pump", "get rich", "risk-free"]
    return [r for r in risky if r.lower() in text.lower()]


class SocialStrategyAgent:
    NAME = "social_strategy_agent"

    def run(self, concepts: List[Dict]) -> AgentOutput:
        existing = memory.load_social_drafts()
        existing_ids = {d["token_idea_id"] for d in existing}

        new_drafts = []
        base_time = datetime.utcnow() + timedelta(days=1)

        for concept in concepts:
            cid = concept.get("id")
            for platform, templates in POST_TEMPLATES.items():
                for i, tmpl in enumerate(templates):
                    text = _fill_template(tmpl["template"], concept)
                    flags = _check_risk_flags(text)
                    publish_time = base_time + timedelta(hours=i * 6)
                    draft = {
                        "id": f"draft_{str(uuid.uuid4())[:8]}",
                        "token_idea_id": cid,
                        "platform": platform,
                        "post_type": tmpl["post_type"],
                        "text": text,
                        "media_prompt": f"Visual for {concept.get('token_name','')} {tmpl['post_type']} post on {platform}",
                        "target_audience": concept.get("target_community", "crypto community"),
                        "expected_goal": tmpl["goal"],
                        "suggested_publish_time": publish_time.isoformat(),
                        "risk_flags": flags,
                        "approval_status": "pending",
                        "created_at": datetime.utcnow().isoformat(),
                        "published_at": None,
                    }
                    new_drafts.append(draft)

        all_drafts = existing + new_drafts
        memory.save_social_drafts(all_drafts)

        return AgentOutput(
            timestamp=datetime.utcnow(),
            agent_name=self.NAME,
            input_summary=f"Generated {len(new_drafts)} social drafts across {len(PLATFORMS)} platforms for {len(concepts)} concepts",
            output=new_drafts,
            score=None,
            next_recommended_action="Review and approve drafts in the Social Draft Approval Center before publishing",
        )
