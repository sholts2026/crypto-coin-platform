from __future__ import annotations
import json
from datetime import datetime
from core import memory


def generate_full_report() -> dict:
    trends  = memory.load_trends()
    ideas   = memory.load_token_ideas()
    scores  = memory.load_scores()
    risks   = memory.load_risk_reviews()
    decs    = memory.load_decisions()
    drafts  = memory.load_social_drafts()
    brands  = memory.load_brand_packages()

    risk_map  = {r["subject_id"]: r for r in risks}
    score_map = {s["token_idea_id"]: s for s in scores}

    ranked_ideas = sorted(ideas, key=lambda i: score_map.get(i["id"], {}).get("final_opportunity_score", 0), reverse=True)

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "report_type": "full_launch_readiness",
        "summary": {
            "total_trends": len(trends),
            "total_token_ideas": len(ideas),
            "total_social_drafts": len(drafts),
            "total_risk_reviews": len(risks),
            "total_decisions": len(decs),
            "total_brand_packages": len(brands),
        },
        "top_trends": trends[:5],
        "top_token_ideas": [
            {
                **idea,
                "opportunity_score": score_map.get(idea["id"], {}).get("final_opportunity_score", 0),
                "risk_score": risk_map.get(idea["id"], {}).get("overall_risk_score", 0),
            }
            for idea in ranked_ideas[:3]
        ],
        "ceo_decision": decs[-1] if decs else None,
        "social_summary": {
            "by_platform": _count_by_key(drafts, "platform"),
            "by_status":   _count_by_key(drafts, "approval_status"),
            "total": len(drafts),
        },
        "risk_summary": {
            "avg_overall": _avg(risks, "overall_risk_score"),
            "avg_ip":      _avg(risks, "ip_trademark_risk"),
            "avg_marketing": _avg(risks, "marketing_risk_score"),
            "high_risk_items": [r for r in risks if r.get("overall_risk_score", 0) > 6],
        },
    }


def export_as_markdown(report: dict) -> str:
    lines = [
        f"# Crypto Coin Launch Report",
        f"Generated: {report['generated_at']}",
        "",
        "## Summary",
        *[f"- **{k.replace('_', ' ').title()}**: {v}" for k, v in report["summary"].items()],
        "",
        "## Top Token Ideas",
    ]
    for idea in report.get("top_token_ideas", []):
        lines += [
            f"### {idea['token_name']} (${idea['ticker']})",
            f"**Narrative:** {idea.get('one_line_narrative','')}",
            f"**Opportunity Score:** {idea.get('opportunity_score', 0):.1f}",
            f"**Risk Score:** {idea.get('risk_score', 0):.1f}/10",
            "",
        ]
    dec = report.get("ceo_decision")
    if dec:
        lines += [
            "## CEO Decision",
            f"**Recommended:** {dec.get('recommended_token_name','')}",
            f"**Status:** {dec.get('human_approval_status','pending')}",
            "",
            dec.get("summary_report", ""),
        ]
    return "\n".join(lines)


def _count_by_key(items: list, key: str) -> dict:
    result: dict = {}
    for item in items:
        v = item.get(key, "unknown")
        result[v] = result.get(v, 0) + 1
    return result


def _avg(items: list, key: str) -> float:
    vals = [i.get(key, 0) for i in items if key in i]
    return round(sum(vals) / len(vals), 2) if vals else 0.0
