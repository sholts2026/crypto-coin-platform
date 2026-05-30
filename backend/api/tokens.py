from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core import memory

router = APIRouter(prefix="/api/token-ideas", tags=["Token Ideas"])


class ApprovalRequest(BaseModel):
    notes: str = ""


@router.get("")
def list_token_ideas(status: str = None):
    ideas = memory.load_token_ideas()
    if status:
        ideas = [i for i in ideas if i.get("approval_status") == status]
    scores = {s["token_idea_id"]: s for s in memory.load_scores()}
    risks  = {r["subject_id"]: r for r in memory.load_risk_reviews()}
    for idea in ideas:
        iid = idea["id"]
        idea["opportunity_score"] = scores.get(iid, {}).get("final_opportunity_score", 0)
        idea["risk_score"]        = risks.get(iid, {}).get("overall_risk_score", 0)
    ideas = sorted(ideas, key=lambda x: x.get("opportunity_score", 0), reverse=True)
    return {"ideas": ideas, "total": len(ideas)}


@router.get("/{idea_id}")
def get_token_idea(idea_id: str):
    ideas = memory.load_token_ideas()
    idea = next((i for i in ideas if i["id"] == idea_id), None)
    if not idea:
        raise HTTPException(404, "Token idea not found")
    return idea


@router.post("/{idea_id}/approve")
def approve_token_idea(idea_id: str, req: ApprovalRequest = ApprovalRequest()):
    ideas = memory.load_token_ideas()
    for idea in ideas:
        if idea["id"] == idea_id:
            idea["approval_status"] = "approved"
            idea["ceo_notes"] = req.notes or idea.get("ceo_notes", "")
            memory.save_token_ideas(ideas)
            return {"status": "approved", "id": idea_id}
    raise HTTPException(404, "Token idea not found")


@router.post("/{idea_id}/reject")
def reject_token_idea(idea_id: str, req: ApprovalRequest = ApprovalRequest()):
    ideas = memory.load_token_ideas()
    for idea in ideas:
        if idea["id"] == idea_id:
            idea["approval_status"] = "rejected"
            idea["ceo_notes"] = req.notes
            memory.save_token_ideas(ideas)
            return {"status": "rejected", "id": idea_id}
    raise HTTPException(404, "Token idea not found")


@router.post("/{idea_id}/revise")
def revise_token_idea(idea_id: str, req: ApprovalRequest = ApprovalRequest()):
    ideas = memory.load_token_ideas()
    for idea in ideas:
        if idea["id"] == idea_id:
            idea["approval_status"] = "needs_revision"
            idea["ceo_notes"] = req.notes
            memory.save_token_ideas(ideas)
            return {"status": "needs_revision", "id": idea_id}
    raise HTTPException(404, "Token idea not found")


@router.post("/generate")
def generate_token_ideas():
    trends = memory.load_trends()
    if not trends:
        raise HTTPException(400, "No trends found. Run collect-trends first.")
    from agents.token_concept_agent.agent import TokenConceptAgent
    result = TokenConceptAgent().run(trends)
    return {"status": "ok", "generated": len(result.output or []), "output": result.output}
