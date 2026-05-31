from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os

router = APIRouter(prefix="/api/community", tags=["Community"])


class BroadcastRequest(BaseModel):
    text: str
    title: Optional[str] = ""


@router.post("/broadcast")
def manual_broadcast(req: BroadcastRequest):
    """Manually broadcast a message to all configured channels."""
    from agents.community_agent.agent import broadcast
    result = broadcast(req.text, req.title)
    return {"status": "ok", **result}


@router.post("/ceo-announcement")
def broadcast_ceo_announcement(decision_id: Optional[str] = None):
    """Generate AI announcement for the latest (or specified) CEO decision and broadcast."""
    from core import memory
    decs = memory.load_decisions()
    if not decs:
        raise HTTPException(400, "No CEO decisions found. Run /api/ceo/run first.")

    if decision_id:
        dec = next((d for d in decs if d["id"] == decision_id), None)
        if not dec:
            raise HTTPException(404, "Decision not found")
    else:
        dec = decs[-1]

    from agents.community_agent.agent import CommunityAgent
    result = CommunityAgent().broadcast_ceo_decision(dec)
    return {"status": "ok", **result}


@router.post("/daily-update")
def send_daily_update():
    """Generate and broadcast today's community status update."""
    from agents.community_agent.agent import CommunityAgent
    result = CommunityAgent().send_daily_update()
    return {"status": "ok", **result}


@router.get("/config")
def get_config():
    """Check which broadcast channels are configured."""
    tg_token   = bool(os.environ.get("TELEGRAM_BOT_TOKEN", ""))
    tg_channel = bool(os.environ.get("TELEGRAM_CHANNEL_ID", ""))
    dc_webhook = bool(os.environ.get("DISCORD_WEBHOOK_URL", ""))

    return {
        "telegram": {
            "bot_token_set":   tg_token,
            "channel_id_set":  tg_channel,
            "ready":           tg_token and tg_channel,
        },
        "discord": {
            "webhook_url_set": dc_webhook,
            "ready":           dc_webhook,
        },
        "any_channel_ready": (tg_token and tg_channel) or dc_webhook,
        "instructions": {
            "telegram": "Add TELEGRAM_CHANNEL_ID (e.g. @yourchannel or -100xxxxxxxx) to Railway env vars",
            "discord":  "Add DISCORD_WEBHOOK_URL from Discord server → Integrations → Webhooks",
        },
    }


@router.post("/test")
def test_broadcast():
    """Send a test message to verify all channels are working."""
    from agents.community_agent.agent import broadcast
    text = (
        "🧪 *Test Message — CryptoLaunch AI*\n\n"
        "Community broadcast system is online and working.\n"
        "AI CEO is watching the markets. 👀\n\n"
        "_This is an automated system test._"
    )
    result = broadcast(text, "System Test")
    if result["channels_reached"] == 0:
        return {
            "status": "no_channels",
            "message": "No channels configured. Set TELEGRAM_CHANNEL_ID and/or DISCORD_WEBHOOK_URL.",
            **result,
        }
    return {"status": "ok", **result}
