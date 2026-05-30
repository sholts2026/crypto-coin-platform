from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core import memory

router = APIRouter(prefix="/api/social", tags=["Social"])


class DraftAction(BaseModel):
    notes: str = ""


@router.get("/drafts")
def list_drafts(platform: str = None, status: str = None, token_idea_id: str = None):
    drafts = memory.load_social_drafts()
    if platform:
        drafts = [d for d in drafts if d.get("platform") == platform]
    if status:
        drafts = [d for d in drafts if d.get("approval_status") == status]
    if token_idea_id:
        drafts = [d for d in drafts if d.get("token_idea_id") == token_idea_id]
    return {"drafts": drafts, "total": len(drafts)}


@router.get("/drafts/{draft_id}")
def get_draft(draft_id: str):
    drafts = memory.load_social_drafts()
    d = next((x for x in drafts if x["id"] == draft_id), None)
    if not d:
        raise HTTPException(404, "Draft not found")
    return d


def _update_draft_status(draft_id: str, status: str, notes: str = "") -> dict:
    drafts = memory.load_social_drafts()
    for d in drafts:
        if d["id"] == draft_id:
            d["approval_status"] = status
            if notes:
                d["notes"] = notes
            memory.save_social_drafts(drafts)
            return {"status": status, "id": draft_id}
    raise HTTPException(404, "Draft not found")


@router.post("/drafts/{draft_id}/approve")
def approve_draft(draft_id: str, req: DraftAction = DraftAction()):
    return _update_draft_status(draft_id, "approved", req.notes)


@router.post("/drafts/{draft_id}/reject")
def reject_draft(draft_id: str, req: DraftAction = DraftAction()):
    return _update_draft_status(draft_id, "rejected", req.notes)


@router.post("/drafts/{draft_id}/mark-published")
def mark_published(draft_id: str):
    from datetime import datetime
    drafts = memory.load_social_drafts()
    for d in drafts:
        if d["id"] == draft_id:
            d["approval_status"] = "published"
            d["published_at"] = datetime.utcnow().isoformat()
            memory.save_social_drafts(drafts)
            return {"status": "published", "id": draft_id}
    raise HTTPException(404, "Draft not found")


@router.post("/generate")
def generate_social_calendar(token_idea_id: str = None):
    ideas = memory.load_token_ideas()
    if token_idea_id:
        ideas = [i for i in ideas if i["id"] == token_idea_id]
    if not ideas:
        raise HTTPException(400, "No token ideas found")
    from agents.social_strategy_agent.agent import SocialStrategyAgent
    result = SocialStrategyAgent().run(ideas)
    return {"status": "ok", "generated": len(result.output or []), "output": result.output}


@router.get("/performance")
def get_social_performance():
    """Returns mock social performance data. Connect real APIs via adapters."""
    return {
        "note": "Connect real social accounts via API adapters in .env",
        "platforms": [
            {"platform": "twitter",  "followers": 0, "impressions_7d": 0, "engagement_rate": 0, "status": "not_connected"},
            {"platform": "reddit",   "members": 0,   "posts_7d": 0,       "engagement_rate": 0, "status": "not_connected"},
            {"platform": "telegram", "members": 0,   "messages_7d": 0,    "status": "not_connected"},
            {"platform": "discord",  "members": 0,   "messages_7d": 0,    "status": "not_connected"},
            {"platform": "tiktok",   "followers": 0, "views_7d": 0,       "engagement_rate": 0, "status": "not_connected"},
        ],
        "drafts_pending": len([d for d in memory.load_social_drafts() if d.get("approval_status") == "pending"]),
        "drafts_approved": len([d for d in memory.load_social_drafts() if d.get("approval_status") == "approved"]),
    }
