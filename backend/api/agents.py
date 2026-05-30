from fastapi import APIRouter
from backend.services.dashboard_service import get_agent_statuses

router = APIRouter(prefix="/api/agents", tags=["Agents"])


@router.get("/status")
def get_all_agent_statuses():
    return {"agents": get_agent_statuses()}
