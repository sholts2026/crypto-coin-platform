from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core import memory

router = APIRouter(prefix="/api/contracts", tags=["Contracts"])


@router.get("")
def list_contracts(token_idea_id: str = None):
    contracts = memory.load_contracts()
    if token_idea_id:
        contracts = [c for c in contracts if c.get("token_idea_id") == token_idea_id]
    return {"contracts": contracts, "total": len(contracts)}


@router.get("/{contract_id}")
def get_contract(contract_id: str):
    contracts = memory.load_contracts()
    c = next((x for x in contracts if x["id"] == contract_id), None)
    if not c:
        raise HTTPException(404, "Contract not found")
    return c


@router.post("/generate")
def generate_contract(token_idea_id: str, chain: str = "ethereum"):
    ideas = memory.load_token_ideas()
    idea = next((i for i in ideas if i["id"] == token_idea_id), None)
    if not idea:
        raise HTTPException(404, "Token idea not found")
    from agents.token_builder_agent.agent import TokenBuilderAgent
    result = TokenBuilderAgent().run(idea, chain=chain)
    return {"status": "ok", "contract": result.output}


@router.get("/{contract_id}/solidity")
def get_solidity_code(contract_id: str):
    contracts = memory.load_contracts()
    c = next((x for x in contracts if x["id"] == contract_id), None)
    if not c:
        raise HTTPException(404, "Contract not found")
    return {"contract_code": c.get("contract_code", "")}


@router.get("/{contract_id}/deploy-script")
def get_deploy_script(contract_id: str):
    contracts = memory.load_contracts()
    c = next((x for x in contracts if x["id"] == contract_id), None)
    if not c:
        raise HTTPException(404, "Contract not found")
    return {"deploy_script": c.get("deploy_script", "")}
