from fastapi import APIRouter, HTTPException
from core import memory

router = APIRouter(prefix="/api/trends", tags=["Trends"])


@router.get("")
def list_trends(platform: str = None, min_score: float = None):
    trends = memory.load_trends()
    if platform:
        trends = [t for t in trends if t.get("source_platform") == platform]
    if min_score is not None:
        trends = [t for t in trends if t.get("composite_score", 0) >= min_score]
    return {"trends": trends, "total": len(trends)}


@router.get("/{trend_id}")
def get_trend(trend_id: str):
    trends = memory.load_trends()
    trend = next((t for t in trends if t["id"] == trend_id), None)
    if not trend:
        raise HTTPException(404, "Trend not found")
    return trend


@router.post("/{trend_id}/send-to-token-agent")
def send_to_token_agent(trend_id: str):
    trends = memory.load_trends()
    trend = next((t for t in trends if t["id"] == trend_id), None)
    if not trend:
        raise HTTPException(404, "Trend not found")
    from agents.token_concept_agent.agent import TokenConceptAgent
    agent = TokenConceptAgent()
    result = agent.run([trend])
    return {"status": "ok", "concepts_generated": len(result.output or []), "output": result.output}


@router.post("/collect")
def collect_trends(use_mock: bool = True):
    from agents.trend_hunter_agent.agent import TrendHunterAgent
    agent = TrendHunterAgent(use_mock=use_mock)
    result = agent.run()
    return {"status": "ok", "trends_collected": len(result.output or []), "output": result.output}
