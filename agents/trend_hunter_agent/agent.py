from __future__ import annotations
import uuid
from datetime import datetime
from typing import List, Dict, Any

from core import memory
from core.scoring import score_trend
from core.schemas import AgentOutput


MOCK_TRENDS = [
    {
        "phrase": "AI agents doing crypto trades",
        "source_platform": "twitter",
        "velocity_score": 88, "novelty_score": 82, "meme_potential": 79,
        "crypto_relevance": 95, "community_size": 72, "saturation_level": 25,
        "expected_lifespan_days": 21,
        "related_communities": ["AI Twitter", "DeFi CT", "Autonomous agents Discord"],
        "related_figures": ["@elonmusk", "@VitalikButerin", "@sama"],
        "why_it_matters": "Autonomous AI agents with wallets are live. New token narrative: 'AI-native money'.",
        "token_narrative_opportunities": [
            "Native currency for AI agent transactions",
            "Meme: AI agents are here for your bags",
            "Utility token rewarding humans who deploy agents"
        ],
        "raw_data": {"tweet_volume_24h": 142000, "reddit_mentions": 4800, "google_trend_index": 78}
    },
    {
        "phrase": "pepe has a son",
        "source_platform": "reddit",
        "velocity_score": 94, "novelty_score": 71, "meme_potential": 97,
        "crypto_relevance": 88, "community_size": 91, "saturation_level": 40,
        "expected_lifespan_days": 14,
        "related_communities": ["r/memecoins", "r/CryptoCurrency", "4chan /biz/"],
        "related_figures": [],
        "why_it_matters": "Pepe lineage memes have massive CT loyalty. 'Son' framing is fresh next-gen narrative.",
        "token_narrative_opportunities": [
            "PEPEJI — next generation Pepe meme coin",
            "Baby Pepe who learned DeFi",
            "Community decides frog identity"
        ],
        "raw_data": {"tweet_volume_24h": 88000, "reddit_mentions": 12000, "google_trend_index": 61}
    },
    {
        "phrase": "dogs with jobs meme wave",
        "source_platform": "tiktok",
        "velocity_score": 86, "novelty_score": 69, "meme_potential": 92,
        "crypto_relevance": 70, "community_size": 88, "saturation_level": 32,
        "expected_lifespan_days": 18,
        "related_communities": ["TikTok Pets", "Reddit aww", "Doge communities"],
        "related_figures": [],
        "why_it_matters": "Dog-with-job memes: 340M TikTok views in 48h. Enormous normie crossover.",
        "token_narrative_opportunities": [
            "WOOF — employed dog token",
            "GOODBOY — token for doing right in crypto",
            "LABRADOR — stable as a retriever"
        ],
        "raw_data": {"tweet_volume_24h": 55000, "tiktok_views_48h": 340000000}
    },
    {
        "phrase": "nuclear energy crypto mining",
        "source_platform": "youtube",
        "velocity_score": 71, "novelty_score": 85, "meme_potential": 55,
        "crypto_relevance": 80, "community_size": 58, "saturation_level": 15,
        "expected_lifespan_days": 45,
        "related_communities": ["Energy Twitter", "Bitcoin Miners", "Tech YouTube"],
        "related_figures": ["@TuurDemeester"],
        "why_it_matters": "Nuclear-powered mining backed by US states. Early, institutional, macro tailwinds.",
        "token_narrative_opportunities": [
            "Clean-energy mining credit token",
            "REACTOR — unstoppable energy meme",
            "Energy sovereignty narrative"
        ],
        "raw_data": {"tweet_volume_24h": 31000, "reddit_mentions": 2100, "google_trend_index": 55}
    },
    {
        "phrase": "on-chain identity crisis",
        "source_platform": "crypto_news",
        "velocity_score": 62, "novelty_score": 90, "meme_potential": 48,
        "crypto_relevance": 93, "community_size": 55, "saturation_level": 10,
        "expected_lifespan_days": 60,
        "related_communities": ["ENS community", "Ethereum builders", "Privacy advocates"],
        "related_figures": ["@VitalikButerin", "@nicksdjohnson"],
        "why_it_matters": "On-chain identity is a core emerging primitive. Early movers capture developer mindshare.",
        "token_narrative_opportunities": [
            "SOUL — soulbound token economy",
            "SELF — you are your on-chain history",
            "PROOF — prove yourself without revealing everything"
        ],
        "raw_data": {"tweet_volume_24h": 18000, "reddit_mentions": 3400, "google_trend_index": 42}
    },
]


class TrendHunterAgent:
    NAME = "trend_hunter_agent"

    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock

    def run(self) -> AgentOutput:
        raw_trends = self._fetch_trends()
        trends = self._process_trends(raw_trends)
        memory.save_trends(trends)
        output = AgentOutput(
            timestamp=datetime.utcnow(),
            agent_name=self.NAME,
            input_summary=f"Collected {len(trends)} trends from {'mock data' if self.use_mock else 'live APIs'}",
            output=trends,
            score=self._avg_score(trends),
            next_recommended_action="Run generate-token-ideas to convert top trends into token concepts",
        )
        return output

    def _fetch_trends(self) -> List[Dict]:
        if self.use_mock:
            return MOCK_TRENDS
        return self._fetch_live_trends()

    def _fetch_live_trends(self) -> List[Dict]:
        """Live API adapters. Falls back to mock if all sources fail."""
        results = []
        results += self._fetch_coingecko_trends()   # free, no key needed ✓
        results += self._fetch_reddit_trends()       # free, no key needed ✓
        results += self._fetch_google_trends()       # free, no key needed ✓
        results += self._fetch_twitter_trends()      # requires paid API key
        if not results:
            return MOCK_TRENDS
        return results

    def _fetch_twitter_trends(self) -> List[Dict]:
        from core.config import settings
        if not settings.twitter_api_key:
            return []
        # Adapter stub — replace with tweepy or twitter-api-v2 client
        return []

    def _fetch_reddit_trends(self) -> List[Dict]:
        """Fetch hot posts from crypto subreddits — no API key needed."""
        import httpx
        from core.llm import ask as llm_ask, is_available as llm_ready

        SUBREDDITS = [
            "CryptoCurrency", "memecoins", "SatoshiStreetBets", "defi", "altcoin"
        ]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        }
        results = []

        # Collect top posts across subreddits
        all_posts = []
        for sub in SUBREDDITS:
            try:
                r = httpx.get(
                    f"https://www.reddit.com/r/{sub}/hot.json?limit=15",
                    headers=headers,
                    timeout=10,
                    follow_redirects=True,
                )
                if r.status_code == 200:
                    posts = r.json().get("data", {}).get("children", [])
                    for p in posts:
                        d = p.get("data", {})
                        score = d.get("score", 0)
                        if score > 10:  # lower threshold — subreddits vary in size
                            all_posts.append({
                                "title":     d.get("title", ""),
                                "score":     score,
                                "comments":  d.get("num_comments", 0),
                                "subreddit": sub,
                                "url":       d.get("url", ""),
                            })
            except Exception:
                continue

        if not all_posts:
            return []

        # Sort by score and take top 10
        all_posts.sort(key=lambda x: x["score"] + x["comments"] * 2, reverse=True)
        top_posts = all_posts[:10]

        # Group into trend phrases using AI
        if llm_ready():
            titles_txt = "\n".join(f"- {p['title']} (r/{p['subreddit']}, {p['score']} upvotes)"
                                   for p in top_posts)
            prompt = f"""These are the hottest crypto Reddit posts right now:
{titles_txt}

Identify 3-4 distinct trending NARRATIVES or THEMES from these posts.
For each, output exactly:
PHRASE: <short catchy phrase describing the trend>
WHY: <1 sentence why it matters>
IDEA1: <token narrative idea>
IDEA2: <token narrative idea>
---"""
            raw = llm_ask(prompt, fallback="")
            blocks = [b.strip() for b in raw.split("---") if b.strip()]
            for block in blocks[:4]:
                lines = block.splitlines()
                data = {}
                for line in lines:
                    for key in ("PHRASE", "WHY", "IDEA1", "IDEA2"):
                        if line.startswith(f"{key}:"):
                            data[key] = line[len(key)+1:].strip()
                if "PHRASE" not in data:
                    continue
                # Estimate velocity from post scores
                avg_score = sum(p["score"] for p in top_posts[:3]) / 3
                velocity = min(90, max(40, int(avg_score / 100)))
                results.append({
                    "phrase": data["PHRASE"],
                    "source_platform": "reddit",
                    "velocity_score": velocity,
                    "novelty_score": 72,
                    "meme_potential": 80,
                    "crypto_relevance": 88,
                    "community_size": 85,
                    "saturation_level": 35,
                    "expected_lifespan_days": 10,
                    "related_communities": [f"r/{s}" for s in SUBREDDITS[:3]],
                    "related_figures": [],
                    "why_it_matters": data.get("WHY", ""),
                    "token_narrative_opportunities": [
                        data.get("IDEA1", ""), data.get("IDEA2", "")
                    ],
                    "raw_data": {
                        "top_post_score": top_posts[0]["score"] if top_posts else 0,
                        "posts_analyzed": len(all_posts),
                    },
                })
        else:
            # Fallback: one trend per top post
            for post in top_posts[:3]:
                results.append({
                    "phrase": post["title"][:80],
                    "source_platform": "reddit",
                    "velocity_score": min(90, post["score"] // 100 + 40),
                    "novelty_score": 65,
                    "meme_potential": 70,
                    "crypto_relevance": 80,
                    "community_size": 80,
                    "saturation_level": 30,
                    "expected_lifespan_days": 7,
                    "related_communities": [f"r/{post['subreddit']}"],
                    "related_figures": [],
                    "why_it_matters": f"Hot post on r/{post['subreddit']} with {post['score']} upvotes.",
                    "token_narrative_opportunities": [],
                    "raw_data": {"score": post["score"], "comments": post["comments"]},
                })

        return results

    def _fetch_google_trends(self) -> List[Dict]:
        """Fetch rising crypto search terms from Google Trends — no API key needed."""
        try:
            from pytrends.request import TrendReq
            from core.llm import ask as llm_ask, is_available as llm_ready

            pytrends = TrendReq(hl="en-US", tz=0, timeout=(10, 25))

            # Search for rising queries around crypto topics
            kw_groups = [
                ["crypto token", "meme coin", "new coin 2025"],
                ["DeFi", "crypto launch", "altcoin"],
            ]

            rising_terms = []
            for kws in kw_groups:
                try:
                    pytrends.build_payload(kws, timeframe="now 7-d", geo="")
                    related = pytrends.related_queries()
                    for kw in kws:
                        rising = related.get(kw, {}).get("rising")
                        if rising is not None and not rising.empty:
                            for _, row in rising.head(3).iterrows():
                                term = str(row.get("query", ""))
                                val  = int(row.get("value", 0))
                                if term and val > 0:
                                    rising_terms.append({"term": term, "value": val})
                except Exception:
                    continue

            if not rising_terms:
                return []

            # Filter to crypto-relevant terms only
            CRYPTO_KEYWORDS = [
                "coin", "token", "crypto", "defi", "nft", "blockchain", "bitcoin",
                "ethereum", "altcoin", "wallet", "dex", "swap", "launch", "mint",
                "airdrop", "memecoin", "solana", "base", "layer", "protocol",
            ]
            filtered = [
                t for t in rising_terms
                if any(kw in t["term"].lower() for kw in CRYPTO_KEYWORDS)
            ]
            # Fall back to all rising terms if filter removes everything
            rising_terms = filtered if filtered else rising_terms
            rising_terms.sort(key=lambda x: x["value"], reverse=True)
            top_terms = rising_terms[:6]

            results = []
            for item in top_terms:
                term  = item["term"]
                value = item["value"]  # breakout = >5000%

                why = ""
                opportunities = []
                if llm_ready():
                    prompt = f""""{term}" is a rapidly rising Google search trend in the crypto space (breakout score: {value}).
In 1-2 sentences, explain what this trend signals and what token opportunity it creates.
Then give 2 short token narrative ideas (max 8 words each).
Format:
WHY: <reason>
IDEA1: <idea>
IDEA2: <idea>"""
                    raw = llm_ask(prompt, fallback="")
                    for line in raw.splitlines():
                        if line.startswith("WHY:"):
                            why = line[4:].strip()
                        elif line.startswith("IDEA1:"):
                            opportunities.append(line[6:].strip())
                        elif line.startswith("IDEA2:"):
                            opportunities.append(line[6:].strip())

                velocity = min(92, max(50, 50 + value // 100)) if value < 5000 else 90
                results.append({
                    "phrase": f"{term} (Google rising search)",
                    "source_platform": "google_trends",
                    "velocity_score": velocity,
                    "novelty_score": 85,
                    "meme_potential": 65,
                    "crypto_relevance": 78,
                    "community_size": 60,
                    "saturation_level": 20,
                    "expected_lifespan_days": 14,
                    "related_communities": ["CT", "Google searchers", "normie crypto"],
                    "related_figures": [],
                    "why_it_matters": why or f"'{term}' is breaking out on Google Search — early signal.",
                    "token_narrative_opportunities": opportunities or [
                        f"Token riding the {term} wave",
                        f"Community around {term} narrative",
                    ],
                    "raw_data": {"google_breakout_score": value, "term": term},
                })

            return results

        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Google Trends fetch failed: {e}")
            return []

    def _fetch_coingecko_trends(self) -> List[Dict]:
        """Fetch real trending coins from CoinGecko (free, no API key needed)."""
        try:
            import httpx
            from core.llm import ask as llm_ask, is_available as llm_ready

            results = []

            # 1. Trending coins (top 7 in 24h)
            r = httpx.get(
                "https://api.coingecko.com/api/v3/search/trending",
                headers={"Accept": "application/json"},
                timeout=10,
            )
            if r.status_code == 200:
                coins = r.json().get("coins", [])
                for entry in coins[:7]:
                    coin = entry.get("item", {})
                    name   = coin.get("name", "Unknown")
                    symbol = coin.get("symbol", "???").upper()
                    rank   = coin.get("market_cap_rank") or 999
                    phrase = f"{name} ({symbol}) trending on CoinGecko"

                    # Use AI to analyse why this coin is trending
                    why = ""
                    opportunities = []
                    if llm_ready():
                        prompt = f"""A crypto coin called {name} (${symbol}) is currently trending on CoinGecko (rank #{rank}).
In 1-2 sentences, explain why this might be trending and what meme/narrative opportunity it creates for a new token launch.
Then list 2-3 short token narrative ideas (each max 8 words).
Format:
WHY: <reason>
IDEAS:
- <idea 1>
- <idea 2>
- <idea 3>"""
                        raw = llm_ask(prompt, fallback="")
                        lines = raw.splitlines()
                        for line in lines:
                            if line.startswith("WHY:"):
                                why = line[4:].strip()
                            elif line.strip().startswith("-"):
                                opportunities.append(line.strip().lstrip("- ").strip())

                    results.append({
                        "phrase": phrase,
                        "source_platform": "crypto_news",
                        "velocity_score": max(30, min(95, 100 - rank // 2)),
                        "novelty_score":  70,
                        "meme_potential": 75,
                        "crypto_relevance": 95,
                        "community_size": max(40, min(90, 90 - rank // 10)),
                        "saturation_level": min(60, rank // 5),
                        "expected_lifespan_days": 7,
                        "related_communities": ["CT", "CoinGecko community", f"${symbol} holders"],
                        "related_figures": [],
                        "why_it_matters": why or f"{name} is in CoinGecko top trending — high visibility window.",
                        "token_narrative_opportunities": opportunities or [
                            f"Rival or successor to {name}",
                            f"Community fork of {name} narrative",
                        ],
                        "raw_data": {"coingecko_rank": rank, "symbol": symbol},
                    })

            return results

        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"CoinGecko fetch failed: {e}")
            return []

    def _process_trends(self, raw: List[Dict]) -> List[Dict]:
        processed = []
        for i, t in enumerate(raw):
            trend_score = score_trend(
                velocity=t.get("velocity_score", 50),
                novelty=t.get("novelty_score", 50),
                meme=t.get("meme_potential", 50),
                crypto_rel=t.get("crypto_relevance", 50),
                community=t.get("community_size", 50),
                saturation=t.get("saturation_level", 50),
            )
            processed.append({
                "id": f"trend_{str(uuid.uuid4())[:8]}",
                "phrase": t["phrase"],
                "source_platform": t.get("source_platform", "unknown"),
                "detected_at": datetime.utcnow().isoformat(),
                "velocity_score": t.get("velocity_score", 50),
                "novelty_score": t.get("novelty_score", 50),
                "meme_potential": t.get("meme_potential", 50),
                "crypto_relevance": t.get("crypto_relevance", 50),
                "community_size": t.get("community_size", 50),
                "saturation_level": t.get("saturation_level", 50),
                "expected_lifespan_days": t.get("expected_lifespan_days", 14),
                "related_communities": t.get("related_communities", []),
                "related_figures": t.get("related_figures", []),
                "why_it_matters": t.get("why_it_matters", ""),
                "token_narrative_opportunities": t.get("token_narrative_opportunities", []),
                "raw_data": t.get("raw_data", {}),
                "composite_score": trend_score,
            })
        return sorted(processed, key=lambda x: x["composite_score"], reverse=True)

    def _avg_score(self, trends: List[Dict]) -> float:
        if not trends:
            return 0.0
        return round(sum(t.get("composite_score", 0) for t in trends) / len(trends), 2)
