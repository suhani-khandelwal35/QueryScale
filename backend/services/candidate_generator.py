"""Generate index-candidate recommendations from extracted feature rows."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List


def _read_feature_rows(path: str | Path) -> List[Dict[str, str]]:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Feature file not found: {csv_path}")

    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def _score_candidate(row: Dict[str, str]) -> float:
    try:
        frequency = float(row.get("frequency", 0) or 0)
        avg_time = float(row.get("average_execution_time", 0) or 0)
        where_usage = float(row.get("where_usage", 0) or 0)
        join_usage = float(row.get("join_usage", 0) or 0)
        order_usage = float(row.get("order_usage", 0) or 0)
        table_size = float(row.get("table_size", 0) or 0)
        existing_index = str(row.get("existing_index", "false")).lower() == "true"
    except ValueError:
        return 0.0

    if existing_index:
        return 0.0

    score = (frequency * 2.0) + (avg_time * 0.5) + (where_usage * 10.0) + (join_usage * 6.0) + (order_usage * 4.0)
    score += min(table_size / 1000.0, 50.0)
    return score


def generate_candidates(feature_path: str | Path, output_path: str | Path) -> List[Dict[str, object]]:
    feature_rows = _read_feature_rows(feature_path)
    recommendations: List[Dict[str, object]] = []

    for row in feature_rows:
        score = _score_candidate(row)
        if score <= 0:
            continue

        columns = [column.strip() for column in str(row.get("columns", "")).split(",") if column.strip()]
        table_name = row.get("table", "")
        candidate_id = row.get("candidate_id", "")
        statement = "CREATE INDEX "
        if columns:
            statement += f"idx_{table_name.lower()}_{'_'.join(c.lower() for c in columns)} ON {table_name} ({', '.join(columns)});"
        else:
            statement += f"idx_{table_name.lower()}_primary ON {table_name} (id);"

        recommendations.append({
            "candidate_id": candidate_id,
            "table": table_name,
            "columns": ", ".join(columns),
            "score": round(score, 3),
            "recommended_action": statement,
            "reason": "High query frequency and filter usage indicate this index would reduce expensive scans.",
        })

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["candidate_id", "table", "columns", "score", "recommended_action", "reason"]
    with output_file.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(recommendations)

    return recommendations


if __name__ == "__main__":
    generate_candidates("data/candidate_features.csv", "data/index_candidates.csv")
