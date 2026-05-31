"""
PEPEJI Telegram Bot — Webhook mode (no polling thread needed).
FastAPI receives POST /telegram/webhook from Telegram.
"""
from __future__ import annotations
import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR  = BASE_DIR / "data"
TOKEN     = os.environ.get("TELEGRAM_BOT_TOKEN", "")


def _load(filename: str) -> list:
    try:
        p = DATA_DIR / filename
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []


def _status_text() -> str:
    decisions = _load("decisions.json")
    ideas     = _load("token_ideas.json")
    trends    = _load("trends.json")
    drafts    = _load("social_drafts.json")
    best  = decisions[-1].get("recommended_token_name", "?") if decisions else "Pending"
    score = decisions[-1].get("score_breakdown", {}).get("final_opportunity_score", 0) if decisions else 0
    return (
        f"🚀 *CRYPTO COIN — System Status*\n\n"
        f"🔍 Trends detected: *{len(trends)}*\n"
        f"💡 Token ideas: *{len(ideas)}*\n"
        f"✍️ Social drafts: *{len(drafts)}*\n"
        f"👑 CEO pick: *{best}*\n"
        f"📊 Score: *{score:.1f}/100*\n\n"
        f"_All decisions require human approval\\._"
    )


def _decision_text() -> str:
    decisions = _load("decisions.json")
    if not decisions:
        return "❌ No CEO decision yet\\."
    d = decisions[-1]
    name    = d.get("recommended_token_name", "?")
    score   = d.get("score_breakdown", {}).get("final_opportunity_score", 0)
    reasons = d.get("selection_reasons", [])
    txt     = "\n".join(f"• {r}" for r in reasons[:4])
    return (
        f"👑 *CEO RECOMMENDATION*\n\n"
        f"*{name}*\n"
        f"Score: *{score:.1f}/100*\n\n"
        f"*Why:*\n{txt}\n\n"
        f"_Status: {d.get('human_approval_status','pending').upper()}_"
    )


def _token_text() -> str:
    ideas = _load("token_ideas.json")
    if not ideas:
        return "❌ No token ideas yet\\."
    idea = next((i for i in ideas if i.get("id") == "idea_002"), ideas[0])
    return (
        f"💎 *{idea.get('token_name')} \\(${idea.get('ticker')}\\)*\n\n"
        f"_{idea.get('one_line_narrative', '')}_\n\n"
        f"📈 Meme potential: *{idea.get('meme_potential',0)}/100*\n"
        f"👥 Community: *{idea.get('community_potential',0)}/100*\n"
        f"⚡ Timing: *{idea.get('timing',0)}/100*"
    )


def _drafts_text() -> str:
    drafts = _load("social_drafts.json")
    if not drafts:
        return "❌ No social drafts yet\\."
    items = [d for d in drafts if d.get("platform") == "twitter"][:3] or drafts[:3]
    lines = ["📝 *Latest Social Drafts*\n"]
    for i, d in enumerate(items, 1):
        content  = d.get("content", "")[:200]
        platform = d.get("platform", "?").upper()
        lines.append(f"*{i}\\. \\[{platform}\\]*\n{content}\n")
    return "\n".join(lines)


def get_reply(text: str) -> str:
    cmd = text.strip().lower().split()[0] if text.strip() else ""
    if cmd in ("/start", "/hello"):
        return (
            "🚀 *Welcome to PEPEJI Command Center\\!*\n\n"
            "I'm the AI agent bot for the PEPEJI token launch\\.\n\n"
            "Commands:\n"
            "/status — System overview\n"
            "/decision — CEO recommendation\n"
            "/token — Token details\n"
            "/drafts — Latest social drafts\n"
        )
    if cmd == "/status":    return _status_text()
    if cmd == "/decision":  return _decision_text()
    if cmd in ("/token", "/pepeji"): return _token_text()
    if cmd == "/drafts":    return _drafts_text()
    if cmd == "/help":
        return (
            "📋 *Commands*\n\n"
            "/status — System overview\n"
            "/decision — CEO recommendation\n"
            "/token — PEPEJI details\n"
            "/drafts — Social drafts\n"
        )
    return "Use /help to see available commands\\."


def send_message(chat_id: int, text: str):
    if not TOKEN:
        return
    import httpx
    try:
        httpx.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "MarkdownV2"},
            timeout=10,
        )
    except Exception as e:
        logger.warning(f"Telegram send failed: {e}")


def handle_update(update: dict):
    """Process one Telegram update dict."""
    msg = update.get("message") or update.get("edited_message")
    if not msg:
        return
    chat_id = msg["chat"]["id"]
    text    = msg.get("text", "")
    reply   = get_reply(text)
    send_message(chat_id, reply)


def register_webhook(base_url: str):
    """Tell Telegram to POST updates to our FastAPI endpoint."""
    if not TOKEN or not base_url:
        return
    import httpx
    webhook_url = f"{base_url}/telegram/webhook"
    try:
        r = httpx.post(
            f"https://api.telegram.org/bot{TOKEN}/setWebhook",
            json={"url": webhook_url},
            timeout=10,
        )
        logger.info(f"Webhook set: {r.json()}")
    except Exception as e:
        logger.warning(f"Webhook registration failed: {e}")
