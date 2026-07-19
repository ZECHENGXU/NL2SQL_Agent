from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import duckdb

from huatai_query_agent.executors.base import QueryResult


PACKAGE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PACKAGE_DIR / "data" / "cust_data.duckdb"


class DuckDBExecutor:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path

    def execute(self, sql: str, *, preview_limit: int = 20) -> QueryResult:
        if not self.db_path.exists():
            return QueryResult(
                success=False,
                columns=[],
                rows=[],
                row_count=0,
                preview_rows=[],
                elapsed_ms=0.0,
                error=f"Database not found: {self.db_path}",
            )

        started = time.perf_counter()
        conn = duckdb.connect(str(self.db_path), read_only=True)
        try:
            result = conn.execute(sql)
            rows: list[tuple[Any, ...]] = result.fetchall()
            columns = [item[0] for item in result.description]
            elapsed_ms = (time.perf_counter() - started) * 1000
            return QueryResult(
                success=True,
                columns=columns,
                rows=rows,
                row_count=len(rows),
                preview_rows=rows[:preview_limit],
                elapsed_ms=elapsed_ms,
            )
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - started) * 1000
            return QueryResult(
                success=False,
                columns=[],
                rows=[],
                row_count=0,
                preview_rows=[],
                elapsed_ms=elapsed_ms,
                error=str(exc),
            )
        finally:
            conn.close()

