"""API endpoint for benchmarking one generated index recommendation."""

from __future__ import annotations

import statistics
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from backend.config import ROOT_DIR, settings
from backend.routes.recommendations import read_recommendations
from backend.services.benchmark import run_benchmark


router = APIRouter(prefix="/benchmark", tags=["benchmark"])


def _configured_result_path() -> Path:
    path = Path(settings.benchmark_result_path)
    return path if path.is_absolute() else ROOT_DIR / path


def _find_recommendation(recommendation_id: str) -> dict[str, Any]:
    try:
        recommendations = read_recommendations()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    for recommendation in recommendations:
        if recommendation["candidate_id"] == recommendation_id:
            return recommendation
    raise HTTPException(status_code=404, detail=f"Recommendation not found: {recommendation_id}")


def _aggregate_results(results: list[dict[str, object]]) -> dict[str, float | int]:
    if not results:
        raise ValueError("Benchmark produced no query results")
    before_ms = statistics.fmean(float(row["before_avg_ms"]) for row in results)
    after_ms = statistics.fmean(float(row["after_avg_ms"]) for row in results)
    return {
        "before_ms": round(before_ms, 3),
        "after_ms": round(after_ms, 3),
        "speedup": round(before_ms / after_ms, 3) if after_ms else 0.0,
        "improvement_percentage": round((before_ms - after_ms) / before_ms * 100, 3)
        if before_ms
        else 0.0,
        "execution_count": sum(int(row["execution_count"]) for row in results),
    }


@router.post("/{recommendation_id}")
def benchmark_recommendation(
    recommendation_id: str,
    iterations: int = Query(default=100, ge=1, le=10000),
) -> dict[str, Any]:
    """Apply a recommendation to the test DB and return measured before/after results."""

    recommendation = _find_recommendation(recommendation_id)
    try:
        results = run_benchmark(
            candidate_id=recommendation["candidate_id"],
            table=recommendation["table"],
            columns=",".join(recommendation["columns"]),
            iterations=iterations,
            output_path=_configured_result_path(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return {
        "candidate_id": recommendation["candidate_id"],
        "table": recommendation["table"],
        "columns": recommendation["columns"],
        "score": recommendation["score"],
        "priority": recommendation["priority"],
        **_aggregate_results(results),
        "results": results,
    }