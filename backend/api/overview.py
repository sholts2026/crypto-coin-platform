from fastapi import APIRouter
from backend.services.dashboard_service import get_overview

router = APIRouter(prefix="/api/overview", tags=["Overview"])


@router.get("")
def overview():
    return get_overview()
