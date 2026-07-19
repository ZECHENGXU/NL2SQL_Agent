from __future__ import annotations

import argparse
import re
import time
from dataclasses import dataclass
from pathlib import Path

try:
    import duckdb
except ImportError as exc:  # pragma: no cover - dependency guard
    raise SystemExit(
        "Missing dependency: duckdb. Install with `python -m pip install -r huatai_query_agent/requirements.txt`."
    ) from exc


PROJECT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = PROJECT_DIR / "huatai_query_agent" / "data" / "cust_data.duckdb"
DEFAULT_SQL_PATH = PROJECT_DIR / "huatai_query_agent" / "sql" / "demo_queries_duckdb.sql"


@dataclass(frozen=True)
class QueryCase:
    query_id: str
    sql: str


def load_query_cases(sql_path: Path) -> list[QueryCase]:
    content = sql_path.read_text(encoding="utf-8")
    parts = re.split(r"^--\s*query_id:\s*([a-zA-Z0-9_-]+)\s*$", content, flags=re.MULTILINE)
    if len(parts) < 3:
        raise ValueError(f"No query_id blocks found in {sql_path}")

    cases: list[QueryCase] = []
    for idx in range(1, len(parts), 2):
        query_id = parts[idx].strip()
        sql = parts[idx + 1].strip()
        if sql.endswith(";"):
            sql = sql[:-1].strip()
        cases.append(QueryCase(query_id=query_id, sql=sql))
    return cases


def preview_rows(rows: list[tuple], limit: int) -> list[tuple]:
    return rows[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run DuckDB demo SQL queries.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="DuckDB database path.")
    parser.add_argument("--sql", type=Path, default=DEFAULT_SQL_PATH, help="SQL file path.")
    parser.add_argument("--query-id", help="Run one query id, for example q001.")
    parser.add_argument("--preview", type=int, default=5, help="Rows to print per query.")
    args = parser.parse_args()

    if not args.db.exists():
        raise SystemExit(f"Database not found: {args.db}")
    if not args.sql.exists():
        raise SystemExit(f"SQL file not found: {args.sql}")

    cases = load_query_cases(args.sql)
    if args.query_id:
        cases = [case for case in cases if case.query_id == args.query_id]
        if not cases:
            raise SystemExit(f"Query id not found: {args.query_id}")

    conn = duckdb.connect(str(args.db), read_only=True)
    failures: list[tuple[str, str]] = []
    try:
        for case in cases:
            started = time.perf_counter()
            try:
                result = conn.execute(case.sql)
                rows = result.fetchall()
                columns = [item[0] for item in result.description]
                elapsed = time.perf_counter() - started
                print(f"\n[{case.query_id}] OK rows={len(rows)} elapsed={elapsed:.3f}s")
                print(f"columns={columns}")
                for row in preview_rows(rows, args.preview):
                    print(row)
            except Exception as exc:  # pragma: no cover - integration script
                elapsed = time.perf_counter() - started
                failures.append((case.query_id, str(exc)))
                print(f"\n[{case.query_id}] FAIL elapsed={elapsed:.3f}s")
                print(exc)
    finally:
        conn.close()

    if failures:
        print("\nFailures:")
        for query_id, message in failures:
            print(f"- {query_id}: {message}")
        raise SystemExit(1)

    print("\nall demo queries passed")


if __name__ == "__main__":
    main()
