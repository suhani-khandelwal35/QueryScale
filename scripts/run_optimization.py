#!/usr/bin/env python3
"""Run recommendation generation and benchmark one recommendation end to end."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Sequence


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.services.benchmark import DEFAULT_OUTPUT_PATH, run_benchmark
from backend.services.pipeline import run_pipeline


def _select_recommendation(
    recommendations: Sequence[dict[str, Any]], candidate_id: str | None,
) -> dict[str, Any]:
    if not recommendations:
        raise ValueError("The recommendation pipeline produced no benchmarkable recommendations")
    if candidate_id is not None:
        for recommendation in recommendations:
            if recommendation.get("candidate_id") == candidate_id:
                return recommendation
        raise ValueError(f"Recommendation not found: {candidate_id}")
    return recommendations[0]


def run_optimization(
    log_path: str | Path = "data/query_logs.csv",
    feature_path: str | Path = "data/candidate_features.csv",
    candidate_path: str | Path = "data/index_candidates.csv",
    recommendation_path: str | Path = "data/recommendations.csv",
    candidate_id: str | None = None,
    iterations: int = 100,
    benchmark_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> list[dict[str, object]]:
    """Generate recommendations, then benchmark the selected recommendation."""

    recommendations = run_pipeline(log_path, feature_path, candidate_path, recommendation_path)
    recommendation = _select_recommendation(recommendations, candidate_id)
    return run_benchmark(
        candidate_id=str(recommendation["candidate_id"]),
        table=str(recommendation["table"]),
        columns=str(recommendation["columns"]),
        iterations=iterations,
        output_path=benchmark_path,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate QueryScale recommendations and benchmark one on the test database."
    )
    parser.add_argument("--log-path", default="data/query_logs.csv")
    parser.add_argument("--feature-path", default="data/candidate_features.csv")
    parser.add_argument("--candidate-path", default="data/index_candidates.csv")
    parser.add_argument("--recommendation-path", default="data/recommendations.csv")
    parser.add_argument("--candidate-id", help="Candidate to benchmark; defaults to the highest-ranked recommendation.")
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--benchmark-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args(argv)

    try:
        results = run_optimization(
            log_path=args.log_path,
            feature_path=args.feature_path,
            candidate_path=args.candidate_path,
            recommendation_path=args.recommendation_path,
            candidate_id=args.candidate_id,
            iterations=args.iterations,
            benchmark_path=args.benchmark_path,
        )
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"Optimization failed: {exc}", file=sys.stderr)
        return 1

    print(f"Benchmarked {len(results)} query groups.")
    for result in results:
        print(
            f"{result['query_id']}: {result['before_avg_ms']} ms -> "
            f"{result['after_avg_ms']} ms | speedup {result['speedup']}x | "
            f"improvement {result['improvement_percentage']}%"
        )
    print(f"Benchmark results written to: {args.benchmark_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())