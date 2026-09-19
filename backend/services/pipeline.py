"""Pipeline that links log extraction, candidate generation, and recommendation output."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from backend.services.candidate_generator import generate_candidates
from backend.services.feature_extractor import extract_features
from backend.services.recommender import generate_recommendations


def run_pipeline(
    log_path: str | Path,
    feature_path: str | Path,
    candidate_path: str | Path,
    recommendation_path: str | Path,
) -> List[Dict[str, object]]:
    extract_features(log_path, feature_path)
    generate_candidates(feature_path, candidate_path)
    return generate_recommendations(candidate_path, recommendation_path)


if __name__ == "__main__":
    run_pipeline("data/query_logs.csv", "data/candidate_features.csv", "data/index_candidates.csv", "data/recommendations.csv")
