"""Recommendation endpoints backed by Person A's generated CSV output."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from backend.config import ROOT_DIR, settings


router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def _configured_recommendation_path() -> Path:
    path = Path(settings.recommendation_path)
    return path if path.is_absolute() else ROOT_DIR / path


def read_recommendations(path: str | Path | None = None) -> list[dict[str, Any]]:
    """Read generated recommendations from the configured CSV file."""

    recommendation_path = Path(path) if path is not None else _configured_recommendation_path()
    if not recommendation_path.exists():
        raise FileNotFoundError(f"Recommendation file not found: {recommendation_path}")

    recommendations: list[dict[str, Any]] = []
    with recommendation_path.open("r", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            recommendations.append({
                "candidate_id": row.get("candidate_id", ""),
                "table": row.get("table", ""),
                "columns": [column.strip() for column in row.get("columns", "").split(",") if column.strip()],
                "score": float(row.get("score", "0") or 0),
                "priority": row.get("priority", ""),
                "recommended_sql": row.get("recommended_sql", ""),
                "reason": row.get("reason", ""),
            })
    return recommendations


def _load_or_raise() -> list[dict[str, Any]]:
    try:
        return read_recommendations()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("")
def get_recommendations(limit: int = Query(default=100, ge=1, le=1000)) -> list[dict[str, Any]]:
    """Return generated index recommendations."""

    return _load_or_raise()[:limit]


@router.get("/{recommendation_id}")
def get_recommendation(recommendation_id: str) -> dict[str, Any]:
    """Return one generated recommendation by candidate ID."""

    for recommendation in _load_or_raise():
        if recommendation["candidate_id"] == recommendation_id:
            return recommendation
    raise HTTPException(status_code=404, detail=f"Recommendation not found: {recommendation_id}")