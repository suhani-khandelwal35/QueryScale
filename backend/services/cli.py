"""CLI entry point for QueryScale recommendation generation."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from backend.services.pipeline import run_pipeline


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate QueryScale index recommendations from SQL workload logs.")
    parser.add_argument("--log-path", default="data/query_logs.csv", help="Path to the query log CSV file.")
    parser.add_argument("--feature-path", default="data/candidate_features.csv", help="Output path for extracted feature rows.")
    parser.add_argument("--candidate-path", default="data/index_candidates.csv", help="Output path for generated index candidates.")
    parser.add_argument("--recommendation-path", default="data/recommendations.csv", help="Output path for final recommendations.")
    args = parser.parse_args(argv)

    try:
        rows = run_pipeline(args.log_path, args.feature_path, args.candidate_path, args.recommendation_path)
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return 1

    print(f"Generated {len(rows)} recommendations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
