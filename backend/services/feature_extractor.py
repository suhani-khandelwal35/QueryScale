"""Generate ML-ready index feature rows from QueryScale query logs."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from backend.services.query_analyzer import analyze_query

TABLE_SIZES = {
    "Branches": 50,
    "Customers": 10000,
    "Accounts": 15000,
    "Transactions": 100000,
    "Loans": 5000,
}

EXISTING_INDEXES = {
    "Branches.branch_id": True,
    "Branches.ifsc_code": True,
    "Customers.customer_id": True,
    "Customers.branch_id": True,
    "Accounts.account_id": True,
    "Accounts.customer_id": True,
    "Accounts.branch_id": True,
    "Transactions.txn_id": True,
    "Transactions.account_id": True,
    "Transactions.txn_date": True,
    "Loans.loan_id": True,
    "Loans.customer_id": True,
}
EXISTING_COMPOSITE_INDEXES = {
    "Transactions.txn_type,txn_date": True,
}


def _has_existing_index(table: str, columns: List[str]) -> bool:
    """Match the complete indexed column signature, not only its first column."""

    if len(columns) == 1:
        return bool(EXISTING_INDEXES.get(f"{table}.{columns[0]}", False))
    return bool(EXISTING_COMPOSITE_INDEXES.get(f"{table}.{','.join(columns)}", False))


def _candidate_id(table: str, columns: List[str]) -> str:
    normalized = [column.upper().replace(".", "_") for column in columns]
    return f"IDX_{table.upper()}_{'_'.join(normalized)}"


def _read_query_logs(path: str | Path) -> List[Dict[str, str]]:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Query log file not found: {csv_path}")

    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def _normalize_field(value: str) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(";") if item.strip()]


def _candidate_rows_for_query(row: Dict[str, str]) -> List[Tuple[str, str, List[str]]]:
    query_template = row.get("query_template", "")
    analysis = analyze_query(query_template)
    tables = analysis.get("tables", [])
    if not tables:
        return []

    candidates: List[Tuple[str, str, List[str]]] = []
    table_map = {table: table for table in tables}

    for table in tables:
        columns = []
        for column in analysis.get("where_columns", []):
            if column in ("customer_id", "account_id", "txn_date", "branch_id"):
                columns.append(column)
        for column in analysis.get("join_columns", []):
            if column not in columns:
                columns.append(column)
        for column in analysis.get("order_columns", []):
            if column not in columns:
                columns.append(column)

        if columns:
            candidates.append((table, table, columns))

    if not candidates:
        for table in tables:
            candidates.append((table, table, ["id"]))

    return candidates


def _merge_features(rows: Iterable[Dict[str, object]]) -> List[Dict[str, object]]:
    aggregates: Dict[str, Dict[str, object]] = {}

    for row in rows:
        candidate_key = str(row["candidate_id"])
        if candidate_key not in aggregates:
            aggregates[candidate_key] = {
                "candidate_id": row["candidate_id"],
                "table": row["table"],
                "columns": row["columns"],
                "frequency": 0,
                "average_execution_time": 0.0,
                "where_usage": 0,
                "join_usage": 0,
                "order_usage": 0,
                "table_size": row["table_size"],
                "existing_index": row["existing_index"],
            }

        aggregate = aggregates[candidate_key]
        aggregate["frequency"] = int(aggregate["frequency"]) + 1
        aggregate["average_execution_time"] = float(aggregate["average_execution_time"]) + float(row["execution_time_ms"])
        aggregate["where_usage"] = int(aggregate["where_usage"]) + int(bool(row["where_usage"]))
        aggregate["join_usage"] = int(aggregate["join_usage"]) + int(bool(row["join_usage"]))
        aggregate["order_usage"] = int(aggregate["order_usage"]) + int(bool(row["order_usage"]))

    final_rows: List[Dict[str, object]] = []
    for candidate in aggregates.values():
        count = int(candidate["frequency"])
        candidate["average_execution_time"] = round(float(candidate["average_execution_time"]) / count, 3)
        final_rows.append(candidate)

    return final_rows


def extract_features(log_path: str | Path, output_path: str | Path) -> List[Dict[str, object]]:
    log_rows = _read_query_logs(log_path)
    feature_rows: List[Dict[str, object]] = []

    for row in log_rows:
        query_template = row.get("query_template", "")
        analysis = analyze_query(query_template)
        execution_time_ms = float(row.get("execution_time_ms", 0.0) or 0.0)
        where_columns = _normalize_field(row.get("where_columns", ""))
        join_columns = _normalize_field(row.get("join_columns", ""))
        order_columns = _normalize_field(row.get("order_columns", ""))

        candidate_list = _candidate_rows_for_query(row)
        for table_name, _, columns in candidate_list:
            column_list = [column for column in columns if column]
            candidate_id = _candidate_id(table_name, column_list)
            table_size = TABLE_SIZES.get(table_name, 0)
            existing_index = _has_existing_index(table_name, column_list) if column_list else False
            feature_rows.append({
                "candidate_id": candidate_id,
                "query_id": row.get("query_id", ""),
                "table": table_name,
                "columns": ",".join(column_list),
                "frequency": 1,
                "execution_time_ms": execution_time_ms,
                "average_execution_time": execution_time_ms,
                "where_usage": int(bool(where_columns and any(col in column_list for col in where_columns))),
                "join_usage": int(bool(join_columns and any(col in column_list for col in join_columns))),
                "order_usage": int(bool(order_columns and any(col in column_list for col in order_columns))),
                "table_size": table_size,
                "existing_index": str(existing_index).lower(),
            })

    merged = _merge_features(feature_rows)
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "candidate_id",
        "table",
        "columns",
        "frequency",
        "average_execution_time",
        "where_usage",
        "join_usage",
        "order_usage",
        "table_size",
        "existing_index",
    ]

    with output_file.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged)

    return merged


if __name__ == "__main__":
    extract_features("data/query_logs.csv", "data/candidate_features.csv")
