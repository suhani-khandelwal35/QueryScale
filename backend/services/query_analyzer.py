"""Lightweight SQL query analyzer for the QueryScale banking workload."""

from __future__ import annotations

import re
from typing import Dict, List


def _normalize_table_name(name: str) -> str:
    cleaned = name.strip()
    if cleaned.startswith("`") and cleaned.endswith("`"):
        return cleaned[1:-1]
    return cleaned


def _extract_tables(sql: str) -> List[str]:
    match = re.search(r"FROM\s+([a-zA-Z0-9_`]+)(?:\s+(?:AS\s+)?[a-zA-Z0-9_]+)?", sql, flags=re.IGNORECASE)
    tables: List[str] = []
    if match:
        tables.append(_normalize_table_name(match.group(1)))

    join_matches = re.findall(r"JOIN\s+([a-zA-Z0-9_`]+)(?:\s+(?:AS\s+)?[a-zA-Z0-9_]+)?", sql, flags=re.IGNORECASE)
    for join_table in join_matches:
        table_name = _normalize_table_name(join_table)
        if table_name not in tables:
            tables.append(table_name)
    return tables


def _extract_where_columns(sql: str) -> List[str]:
    where_pattern = re.compile(r"WHERE\s+(.*?)(?:GROUP\s+BY|ORDER\s+BY|LIMIT|$)", flags=re.IGNORECASE | re.DOTALL)
    where_match = where_pattern.search(sql)
    if not where_match:
        return []

    clause = where_match.group(1)
    column_names = re.findall(r"([a-zA-Z_][a-zA-Z0-9_\.]*)\s*(?:=|!=|<>|<|>|LIKE|IN|BETWEEN|IS\s+NULL|IS\s+NOT\s+NULL)", clause, flags=re.IGNORECASE)
    normalized = []
    for name in column_names:
        if "." in name:
            candidate = name.split(".")[-1]
        else:
            candidate = name
        if candidate not in normalized:
            normalized.append(candidate)
    return normalized


def _extract_join_columns(sql: str) -> List[str]:
    matches = re.findall(r"ON\s+([a-zA-Z0-9_`]+)\.?([a-zA-Z0-9_`]+)\s*=\s*([a-zA-Z0-9_`]+)\.?([a-zA-Z0-9_`]+)", sql, flags=re.IGNORECASE)
    columns: List[str] = []
    for match in matches:
        left = match[1] if match[1] else match[0]
        right = match[3] if match[3] else match[2]
        if left == right:
            columns.append(left)
        else:
            columns.append(left)
    return columns


def _extract_order_columns(sql: str) -> List[str]:
    order_match = re.search(r"ORDER\s+BY\s+(.+?)(?:LIMIT|$)", sql, flags=re.IGNORECASE | re.DOTALL)
    if not order_match:
        return []

    clause = order_match.group(1)
    columns = re.findall(r"([a-zA-Z_][a-zA-Z0-9_\.]*)", clause, flags=re.IGNORECASE)
    normalized = []
    for name in columns:
        if "." in name:
            candidate = name.split(".")[-1]
        else:
            candidate = name
        if candidate.lower() not in {"asc", "desc"} and candidate not in normalized:
            normalized.append(candidate)
    return normalized


def analyze_query(sql: str) -> Dict[str, List[str]]:
    normalized_sql = " ".join(sql.strip().split())
    return {
        "tables": _extract_tables(normalized_sql),
        "where_columns": _extract_where_columns(normalized_sql),
        "join_columns": _extract_join_columns(normalized_sql),
        "order_columns": _extract_order_columns(normalized_sql),
    }
