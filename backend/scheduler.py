"""
Autonomous scheduler — runs the CEO pipeline every 6 hours.

Schedule:
  Every 6h  → collect trends → generate ideas → CEO picks best → post to Telegram
  Daily 9am → community daily update to Telegram channel

All decisions are SUGGESTIONS — human approval required before real-world actions.
"""
from __future__ import annotations
import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


# ──────────────────────────────────────────────
# Jobs
# ──────────────────────────────────────────────

def job_ceo_pipeline():
    """
    Full pipeline: trends → ideas → CEO decision → Telegram notification.
    Runs every 6 hours.
    """
    logger.info(f"[SCHEDULER] CEO pipeline started at {datetime.utcnow().isoformat()}")
    try:
        from core import memory

        # 1. Collect trends (live)
        from agents.trend_hunter_agent.agent import TrendHunterAgent
        trend_out = TrendHunterAgent(use_mock=False).run()
        trend_count = len(trend_out.output or [])
        logger.info(f"[SCHEDULER] Trends collected: {trend_count}")

        # 2. Generate token ideas
        from agents.token_concept_agent.agent import TokenConceptAgent
        trends = memory.load_trends()
        idea_out = TokenConceptAgent().run(trends)
        idea_count = len(idea_out.output or [])
        logger.info(f"[SCHEDULER] Token ideas: {idea_count}")

        # 3. Score ideas
        try:
            from core.orchestrator import Orchestrator
            Orchestrator().score_token_ideas()
        except Exception as e:
            logger.warning(f"[SCHEDULER] Scoring skipped: {e}")

        # 4. CEO decision
        from agents.ceo_agent.agent import CEOAgent
        ideas  = memory.load_token_ideas()
        scores = memory.load_scores()
        risks  = memory.load_risk_reviews()
        ceo_out = CEOAgent().run(ideas, scores, risks)
        decision = ceo_out.output or {}
        token_name = decision.get("recommended_token_name", "Unknown")
        score = decision.get("score_breakdown", {}).get("final_opportunity_score", 0)
        logger.info(f"[SCHEDULER] CEO pick: {token_name} ({score:.1f})")

        # 5. Notify Telegram — CEO suggestion, awaiting human approval
        _notify_ceo_suggestion(decision)

    except Exception as e:
        logger.error(f"[SCHEDULER] CEO pipeline failed: {e}", exc_info=True)


def job_daily_community_update():
    """
    Post daily community update to Telegram channel.
    Runs every day at 09:00 UTC.
    """
    logger.info(f"[SCHEDULER] Daily update at {datetime.utcnow().isoformat()}")
    try:
        from agents.community_agent.agent import CommunityAgent
        result = CommunityAgent().send_daily_update()
        logger.info(f"[SCHEDULER] Daily update sent — channels: {result.get('channels_reached', 0)}")
    except Exception as e:
        logger.error(f"[SCHEDULER] Daily update failed: {e}", exc_info=True)


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _notify_ceo_suggestion(decision: dict):
    """Post CEO suggestion to Telegram, asking for human approval."""
    from agents.community_agent.agent import post_to_telegram_channel
    from core.llm import ask as llm_ask, is_available as llm_ready

    name  = decision.get("recommended_token_name", "Token")
    score = decision.get("score_breakdown", {}).get("final_opportunity_score", 0)
    reasons = decision.get("selection_reasons", [])
    dec_id  = decision.get("id", "")

    reasons_txt = "\n".join(f"• {r}" for r in reasons[:3])

    if llm_ready():
        prompt = f"""Write a SHORT internal alert (3-4 sentences, no emojis spam) for a founder:
The AI CEO just picked {name} (score {score:.0f}/100) as the next token to launch.
Reasons: {reasons_txt}
Tell the founder to review and approve or reject. Keep it professional."""
        body = llm_ask(prompt, fallback="")
    else:
        body = f"CEO picked {name} (score {score:.0f}/100).\n{reasons_txt}"

    text = (
        f"🤖 *CEO AUTO-DECISION — Awaiting Your Approval*\n\n"
        f"*Token:* {name}\n"
        f"*Score:* {score:.0f}/100\n\n"
        f"{body}\n\n"
        f"✅ Approve via API:\n"
        f"`POST /api/ceo/decisions/{dec_id}/approve`\n\n"
        f"_All CEO suggestions require human approval before any public action._"
    )

    sent = post_to_telegram_channel(text)
    logger.info(f"[SCHEDULER] Telegram notification sent: {sent}")


# ──────────────────────────────────────────────
# Lifecycle
# ──────────────────────────────────────────────

def start_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        return

    _scheduler = BackgroundScheduler(timezone="UTC")

    # CEO pipeline — every 6 hours
    _scheduler.add_job(
        job_ceo_pipeline,
        trigger=IntervalTrigger(hours=6),
        id="ceo_pipeline",
        name="CEO Pipeline (trends → ideas → decision → Telegram)",
        replace_existing=True,
        misfire_grace_time=300,
    )

    # Daily community update — 09:00 UTC every day
    _scheduler.add_job(
        job_daily_community_update,
        trigger=CronTrigger(hour=9, minute=0),
        id="daily_community_update",
        name="Daily Community Update",
        replace_existing=True,
        misfire_grace_time=300,
    )

    _scheduler.start()
    logger.info("[SCHEDULER] Started — CEO pipeline every 6h, daily update at 09:00 UTC")


def stop_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("[SCHEDULER] Stopped")


def get_scheduler_status() -> dict:
    if not _scheduler or not _scheduler.running:
        return {"running": False, "jobs": []}

    jobs = []
    for job in _scheduler.get_jobs():
        next_run = job.next_run_time
        jobs.append({
            "id":       job.id,
            "name":     job.name,
            "next_run": next_run.isoformat() if next_run else None,
        })
    return {"running": True, "jobs": jobs}
