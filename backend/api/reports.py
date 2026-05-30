from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from backend.services.report_service import generate_full_report, export_as_markdown

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("")
def get_report():
    return generate_full_report()


@router.get("/markdown", response_class=PlainTextResponse)
def get_report_markdown():
    report = generate_full_report()
    return export_as_markdown(report)


@router.get("/json")
def get_report_json():
    return generate_full_report()


@router.post("/export")
def export_report(format: str = "json"):
    report = generate_full_report()
    if format == "markdown":
        return {"format": "markdown", "content": export_as_markdown(report)}
    return {"format": "json", "content": report}
