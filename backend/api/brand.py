from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core import memory

router = APIRouter(prefix="/api/brand", tags=["Brand"])


class ApprovalRequest(BaseModel):
    notes: str = ""


@router.get("")
def list_brand_packages(token_idea_id: str = None):
    brands = memory.load_brand_packages()
    if token_idea_id:
        brands = [b for b in brands if b.get("token_idea_id") == token_idea_id]
    return {"brands": brands, "total": len(brands)}


@router.get("/{brand_id}")
def get_brand(brand_id: str):
    brands = memory.load_brand_packages()
    b = next((x for x in brands if x["id"] == brand_id), None)
    if not b:
        raise HTTPException(404, "Brand package not found")
    return b


@router.post("/{brand_id}/approve")
def approve_brand(brand_id: str, req: ApprovalRequest = ApprovalRequest()):
    brands = memory.load_brand_packages()
    for b in brands:
        if b["id"] == brand_id:
            b["approval_status"] = "approved"
            memory.save_brand_packages(brands)
            return {"status": "approved", "id": brand_id}
    raise HTTPException(404, "Brand package not found")


@router.post("/{brand_id}/reject")
def reject_brand(brand_id: str, req: ApprovalRequest = ApprovalRequest()):
    brands = memory.load_brand_packages()
    for b in brands:
        if b["id"] == brand_id:
            b["approval_status"] = "rejected"
            memory.save_brand_packages(brands)
            return {"status": "rejected", "id": brand_id}
    raise HTTPException(404, "Brand package not found")


@router.post("/generate")
def generate_brands(token_idea_id: str = None):
    ideas = memory.load_token_ideas()
    if token_idea_id:
        ideas = [i for i in ideas if i["id"] == token_idea_id]
    if not ideas:
        raise HTTPException(400, "No token ideas found")
    from agents.brand_agent.agent import BrandAgent
    result = BrandAgent().run(ideas)
    return {"status": "ok", "generated": len(result.output or []), "output": result.output}
