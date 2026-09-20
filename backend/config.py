"""Application configuration loaded from the project environment file."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    """Runtime settings shared by the API and database services."""

    db_host: str = os.getenv("DB_HOST", "127.0.0.1")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_name: str = os.getenv("DB_NAME", "queryscale")
    db_test_name: str = os.getenv("DB_TEST_NAME", "queryscale_test")
    db_user: str = os.getenv("DB_USER", "root")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_charset: str = os.getenv("DB_CHARSET", "utf8mb4")
    query_log_path: str = os.getenv("QUERY_LOG_PATH", "data/query_logs.csv")

    def mysql_config(self) -> dict[str, object]:
        return {
            "host": self.db_host,
            "port": self.db_port,
            "database": self.db_name,
            "user": self.db_user,
            "password": self.db_password,
            "charset": self.db_charset,
            "autocommit": True,
            "raise_on_warnings": True,
        }


settings = Settings()