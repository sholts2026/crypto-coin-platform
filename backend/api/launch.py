from fastapi import APIRouter, HTTPException
from core import memory
import os

router = APIRouter(prefix="/api/launch-readiness", tags=["Launch"])


@router.get("")
def get_launch_readiness():
    decs    = memory.load_decisions()
    ideas   = memory.load_token_ideas()
    risks   = memory.load_risk_reviews()
    drafts  = memory.load_social_drafts()
    brands  = memory.load_brand_packages()
    contracts = memory.load_contracts()

    approved_ideas  = [i for i in ideas if i.get("approval_status") == "approved"]
    completed_risks = len(risks) > 0
    approved_brands = [b for b in brands if b.get("approval_status") == "approved"]
    approved_drafts = [d for d in drafts if d.get("approval_status") == "approved"]
    latest_decision = decs[-1] if decs else None
    human_approved  = latest_decision and latest_decision.get("human_approval_status") == "approved"

    checklist = {
        "trend_validated":               len(memory.load_trends()) > 0,
        "token_concept_approved":        len(approved_ideas) > 0,
        "brand_package_approved":        len(approved_brands) > 0,
        "risk_review_completed":         completed_risks,
        "social_infrastructure_prepared":len(approved_drafts) >= 3,
        "first_content_calendar_ready":  len(approved_drafts) >= 10,
        "community_channels_ready":      bool(
            (os.environ.get("TELEGRAM_BOT_TOKEN") and os.environ.get("TELEGRAM_CHANNEL_ID"))
            or os.environ.get("DISCORD_WEBHOOK_URL")
        ),
        "smart_contract_generated":      len(contracts) > 0,
        "smart_contract_tests_passed":   False,  # manual check — run pytest after audit
        "tokenomics_reviewed":           len(contracts) > 0,
        "launch_report_generated":       latest_decision is not None,
        "human_approval_received":       bool(human_approved),
    }

    done = sum(1 for v in checklist.values() if v)
    total = len(checklist)
    pct = round(done / total * 100, 1)

    blockers = [k.replace("_", " ").title() for k, v in checklist.items() if not v]
    warnings = []
    if not completed_risks:
        warnings.append("Risk review not completed — launch without review is high risk")
    if not human_approved:
        warnings.append("Human approval required before any public launch activity")

    next_action = blockers[0] if blockers else "Ready for launch"

    return {
        "readiness_pct": pct,
        "checklist": checklist,
        "blockers": blockers,
        "warnings": warnings,
        "next_action": next_action,
        "done_count": done,
        "total_count": total,
    }
