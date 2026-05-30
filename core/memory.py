from __future__ import annotations
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from core.config import settings


def _path(filename: str) -> Path:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return settings.data_dir / filename


def _default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Not serializable: {type(obj)}")


def load_json(filename: str, default=None) -> Any:
    p = _path(filename)
    if not p.exists():
        return default if default is not None else []
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else []


def save_json(filename: str, data: Any) -> None:
    p = _path(filename)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=_default, ensure_ascii=False)


def append_json(filename: str, record: Dict) -> None:
    existing = load_json(filename, default=[])
    if isinstance(existing, list):
        existing.append(record)
    save_json(filename, existing)


def load_trends() -> List[Dict]:
    return load_json("trends.json", [])

def save_trends(data: List[Dict]) -> None:
    save_json("trends.json", data)

def load_token_ideas() -> List[Dict]:
    return load_json("token_ideas.json", [])

def save_token_ideas(data: List[Dict]) -> None:
    save_json("token_ideas.json", data)

def load_social_drafts() -> List[Dict]:
    return load_json("social_drafts.json", [])

def save_social_drafts(data: List[Dict]) -> None:
    save_json("social_drafts.json", data)

def load_decisions() -> List[Dict]:
    return load_json("decisions.json", [])

def save_decisions(data: List[Dict]) -> None:
    save_json("decisions.json", data)

def load_risk_reviews() -> List[Dict]:
    return load_json("risk_reviews.json", [])

def save_risk_reviews(data: List[Dict]) -> None:
    save_json("risk_reviews.json", data)

def load_brand_packages() -> List[Dict]:
    return load_json("brand_packages.json", [])

def save_brand_packages(data: List[Dict]) -> None:
    save_json("brand_packages.json", data)

def load_contracts() -> List[Dict]:
    return load_json("contracts_data.json", [])

def save_contracts(data: List[Dict]) -> None:
    save_json("contracts_data.json", data)

def load_scores() -> List[Dict]:
    return load_json("scores.json", [])

def save_scores(data: List[Dict]) -> None:
    save_json("scores.json", data)
