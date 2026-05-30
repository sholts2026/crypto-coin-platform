from __future__ import annotations
import uuid
from datetime import datetime
from typing import List, Dict

from core import memory
from core.schemas import AgentOutput


def _generate_community_package(concept: Dict) -> Dict:
    name = concept.get("token_name", "Token")
    ticker = concept.get("ticker", "TKN")
    community = concept.get("target_community", "crypto community")

    return {
        "id": f"comm_{str(uuid.uuid4())[:8]}",
        "token_idea_id": concept.get("id"),
        "faq_drafts": [
            {"q": f"What is ${ticker}?", "a": concept.get("one_line_narrative", "A community token.")},
            {"q": "Is this a rug pull?", "a": f"${ticker} is a community project. Liquidity will be locked. Contract will be published and verifiable on Etherscan. We encourage you to DYOR."},
            {"q": "When listing on Binance?", "a": "We focus on building community first. CEX listings happen organically when a community is strong enough. Not financial advice."},
            {"q": "Who is the team?", "a": f"The ${ticker} team is pseudonymous. The project is community-driven. The contract is the source of truth."},
            {"q": "What is the total supply?", "a": "1,000,000,000 tokens. No minting. No burning unless governance votes."},
            {"q": "Is there a whitepaper?", "a": f"There is a manifesto. ${ticker} is a meme token. The narrative IS the product. Manifesto available on the website."},
            {"q": "How do I buy?", "a": f"After launch, ${ticker} will be available on DEX. Instructions will be posted in the official channels. Never buy from links in DMs."},
        ],
        "ama_topics": [
            "Why we chose this narrative and trend",
            "How tokenomics were designed for fairness",
            "What makes this community different from other meme coins",
            "Roadmap: what happens after launch",
            "How community members can contribute",
        ],
        "community_events": [
            "Week 1: Launch Telegram AMA — founders answer top 10 questions",
            "Week 2: Meme competition — best meme wins community prize",
            "Week 3: Twitter Spaces discussion about the trend narrative",
            "Week 4: Discord community call — community votes on next milestone",
            "Ongoing: weekly meme Monday, tweet your wallet Wednesday",
        ],
        "channel_structure": {
            "telegram": [
                f"{name} Official — main community channel",
                f"{name} Announcements — one-way broadcast channel",
                f"{name} Trading — price discussion (no advice rule)",
                f"{name} Memes — meme drops only",
            ],
            "discord": {
                "Information": ["#rules", "#announcements", "#roadmap"],
                "Community": ["#general", "#introductions", "#off-topic"],
                "Creative": ["#memes", "#art", "#content-creators"],
                "Discussion": ["#price-chat", "#trading-ideas", "#partnerships"],
                "Dev": ["#contract-info", "#dev-talk", "#bugs"],
            },
        },
        "moderation_guidelines": [
            "No price predictions or financial advice — immediate warning",
            "No spam or promotional content — immediate ban",
            "No FUD without evidence — request sources or remove",
            "No doxxing — immediate ban",
            "No impersonation of team members — immediate ban",
            "Memes encouraged. Toxicity not tolerated.",
            "English is primary language. Other languages allowed in dedicated threads.",
        ],
        "onboarding_message": (
            f"Welcome to {name}! 🎉\n\n"
            f"You're early. That's the only advantage that matters.\n\n"
            f"${ticker} is a community-driven token. No VCs. No insiders. Just us.\n\n"
            f"Read the pinned messages. Introduce yourself. Get involved.\n\n"
            f"The community is the product. You are the community.\n\n"
            f"WAGMI. 🟢"
        ),
        "recurring_questions": [
            "Contract address?",
            "When DEX?",
            "Team doxxed?",
            "Liquidity locked?",
            "CoinGecko/CMC listed?",
        ],
        "sentiment_summary": "Community is in pre-launch excitement phase. Primary concerns are rug safety and liquidity lock. Recommend proactive transparency on contract and tokenomics before launch.",
        "created_at": datetime.utcnow().isoformat(),
    }


class CommunityAgent:
    NAME = "community_agent"

    def run(self, concepts: List[Dict]) -> AgentOutput:
        packages = []
        for concept in concepts:
            pkg = _generate_community_package(concept)
            packages.append(pkg)

        existing = memory.load_json("community_packages.json", [])
        all_packages = existing + packages
        memory.save_json("community_packages.json", all_packages)

        return AgentOutput(
            timestamp=datetime.utcnow(),
            agent_name=self.NAME,
            input_summary=f"Generated community packages for {len(concepts)} token concepts",
            output=packages,
            score=None,
            next_recommended_action="Set up Telegram and Discord channels. Copy onboarding messages. Prepare mods.",
        )
