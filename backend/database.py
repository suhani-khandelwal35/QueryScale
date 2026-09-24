"""MySQL connection handling for the QueryScale application."""

from __future__ import annotations

from typing import Any

import mysql.connector
from mysql.connector import MySQLConnection
from mysql.connector.errors import Error as MySQLError

from backend.config import settings


def get_connection() -> MySQLConnection:
    """Open a connection using the configured database settings."""

    try:
        return mysql.connector.connect(**settings.mysql_config())
    except MySQLError as exc:
        raise RuntimeError(
            f"Unable to connect to MySQL at {settings.db_host}:{settings.db_port} "
            f"using database '{settings.db_name}'. Check .env and ensure MySQL is running."
        ) from exc


def close_connection(connection: Any) -> None:
    """Close a connection when it is open."""

    if connection is not None and connection.is_connected():
        connection.close()