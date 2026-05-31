from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core import memory

router = APIRouter(prefix="/api/ceo", tags=["CEO Decisions"])


class ApprovalRequest(BaseModel):
    notes: str = ""


@router.get("/decisions")
def list_decisions():
    return {"decisions": memory.load_decisions()}


@router.get("/decisions/{decision_id}")
def get_decision(decision_id: str):
    decs = memory.load_decisions()
    dec = next((d for d in decs if d["id"] == decision_id), None)
    if not dec:
        raise HTTPException(404, "Decision not found")
    return dec


@router.post("/decisions/{decision_id}/approve")
def approve_decision(decision_id: str, req: ApprovalRequest = ApprovalRequest()):
    decs = memory.load_decisions()
    for dec in decs:
        if dec["id"] == decision_id:
            dec["human_approval_status"] = "approved"
            if dec.get("launch_checklist_status"):
                dec["launch_checklist_status"]["human_approval_received"] = True
            memory.save_decisions(decs)

            # Auto-broadcast CEO decision to community channels
            broadcast_result = {"telegram": False, "discord": False, "channels_reached": 0}
            try:
                from agents.community_agent.agent import CommunityAgent
                broadcast_result = CommunityAgent().broadcast_ceo_decision(dec)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Community broadcast failed: {e}")

            return {
                "status": "approved",
                "id": decision_id,
                "broadcast": broadcast_result,
            }
    raise HTTPException(404, "Decision not found")


@router.post("/decisions/{decision_id}/revise")
def request_revision(decision_id: str, req: ApprovalRequest = ApprovalRequest()):
    decs = memory.load_decisions()
    for dec in decs:
        if dec["id"] == decision_id:
            dec["human_approval_status"] = "needs_revision"
            memory.save_decisions(decs)
            return {"status": "needs_revision", "id": decision_id}
    raise HTTPException(404, "Decision not found")


@router.post("/run")
def run_ceo_decision():
    ideas  = memory.load_token_ideas()
    scores = memory.load_scores()
    risks  = memory.load_risk_reviews()
    if not ideas:
        raise HTTPException(400, "No token ideas. Run generate-token-ideas first.")
    from agents.ceo_agent.agent import CEOAgent
    result = CEOAgent().run(ideas, scores, risks)
    return {"status": "ok", "decision": result.output}


@router.post("/score")
def score_ideas():
    from core.orchestrator import Orchestrator
    scores = Orchestrator().score_token_ideas()
    return {"status": "ok", "scores": scores}
