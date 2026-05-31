"""
PEPEJI Telegram Community Bot
Runs as background thread inside the FastAPI server.
Commands: /start /status /decision /token /drafts /help
"""
from __future__ import annotations
import os
import sys
import logging
import threading
import json
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


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

    best = None
    if decisions:
        d = decisions[-1]
        best = d.get("recommended_token_name", "?")
        score = d.get("score_breakdown", {}).get("final_opportunity_score", 0)
    else:
        score = 0

    return (
        f"🚀 *CRYPTO COIN — System Status*\n\n"
        f"🔍 Trends detected: *{len(trends)}*\n"
        f"💡 Token ideas: *{len(ideas)}*\n"
        f"✍️ Social drafts: *{len(drafts)}*\n"
        f"👑 CEO pick: *{best or 'Pending'}*\n"
        f"📊 Score: *{score:.1f}/100*\n\n"
        f"_All decisions require human approval._"
    )


def _decision_text() -> str:
    decisions = _load("decisions.json")
    if not decisions:
        return "❌ No CEO decision yet. Run the pipeline first."
    d = decisions[-1]
    name   = d.get("recommended_token_name", "?")
    score  = d.get("score_breakdown", {}).get("final_opportunity_score", 0)
    report = d.get("summary_report", "")
    reasons = d.get("selection_reasons", [])
    reasons_text = "\n".join(f"• {r}" for r in reasons[:4])
    return (
        f"👑 *CEO RECOMMENDATION*\n\n"
        f"*{name}*\n"
        f"Score: *{score:.1f}/100*\n\n"
        f"*Why:*\n{reasons_text}\n\n"
        f"_Approval status: {d.get('human_approval_status','pending').upper()}_"
    )


def _token_text() -> str:
    ideas = _load("token_ideas.json")
    if not ideas:
        return "❌ No token ideas yet."
    idea = next((i for i in ideas if i.get("id") == "idea_002"), ideas[0])
    return (
        f"💎 *{idea.get('token_name')} (${idea.get('ticker')})*\n\n"
        f"_{idea.get('one_line_narrative', '')}_\n\n"
        f"🎯 Target: {idea.get('target_community', '')}\n"
        f"😂 Meme: {idea.get('meme_angle', '')[:120]}\n\n"
        f"📈 Meme potential: *{idea.get('meme_potential',0)}/100*\n"
        f"👥 Community: *{idea.get('community_potential',0)}/100*\n"
        f"⚡ Timing: *{idea.get('timing',0)}/100*"
    )


def _drafts_text() -> str:
    drafts = _load("social_drafts.json")
    if not drafts:
        return "❌ No social drafts yet."
    twitter = [d for d in drafts if d.get("platform") == "twitter"][:3]
    if not twitter:
        twitter = drafts[:3]
    lines = ["📝 *Latest Social Drafts*\n"]
    for i, d in enumerate(twitter, 1):
        content = d.get("content", "")[:200]
        platform = d.get("platform", "?").upper()
        status = d.get("approval_status", "pending")
        lines.append(f"*{i}. [{platform}]* _{status}_\n{content}\n")
    return "\n".join(lines)


def start_bot():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN not set — bot disabled")
        return

    try:
        import telebot
    except ImportError:
        logger.warning("pyTelegramBotAPI not installed — bot disabled")
        return

    bot = telebot.TeleBot(token, parse_mode="Markdown")

    @bot.message_handler(commands=["start", "hello"])
    def handle_start(msg):
        bot.reply_to(msg,
            "🚀 *Welcome to PEPEJI Command Center!*\n\n"
            "I'm the AI agent bot for the PEPEJI token launch.\n\n"
            "Commands:\n"
            "/status — System overview\n"
            "/decision — CEO recommendation\n"
            "/token — Token details\n"
            "/drafts — Latest social drafts\n"
            "/help — Show commands\n\n"
            "_All outputs require human approval before execution._"
        )

    @bot.message_handler(commands=["status"])
    def handle_status(msg):
        bot.reply_to(msg, _status_text())

    @bot.message_handler(commands=["decision"])
    def handle_decision(msg):
        bot.reply_to(msg, _decision_text())

    @bot.message_handler(commands=["token", "pepeji"])
    def handle_token(msg):
        bot.reply_to(msg, _token_text())

    @bot.message_handler(commands=["drafts"])
    def handle_drafts(msg):
        bot.reply_to(msg, _drafts_text())

    @bot.message_handler(commands=["help"])
    def handle_help(msg):
        bot.reply_to(msg,
            "📋 *Commands*\n\n"
            "/status — System overview\n"
            "/decision — CEO recommendation\n"
            "/token — PEPEJI token details\n"
            "/drafts — Latest social drafts\n"
        )

    @bot.message_handler(func=lambda m: True)
    def handle_all(msg):
        bot.reply_to(msg, "Use /help to see available commands.")

    logger.info("Telegram bot polling started ✓")
    bot.infinity_polling(timeout=30, long_polling_timeout=20)


def start_bot_thread():
    """Start the bot in a background daemon thread."""
    t = threading.Thread(target=start_bot, daemon=True, name="telegram-bot")
    t.start()
    return t
