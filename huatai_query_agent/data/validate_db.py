from __future__ import annotations

import argparse
from pathlib import Path

try:
    import duckdb
except ImportError as exc:  # pragma: no cover - dependency guard
    raise SystemExit(
        "Missing dependency: duckdb. Install with `python -m pip install -r huatai_query_agent/requirements.txt`."
    ) from exc


DEFAULT_DB_PATH = Path(__file__).resolve().parent / "cust_data.duckdb"


EXPECTED_TABLES = {
    "ads_cust_info_d": {
        "rows": 500,
        "columns": [
            "data_dt",
            "pty_id",
            "sor_pty_id",
            "cust_lvl_cd",
            "cust_status",
            "cust_type",
            "prov_name",
            "city_name",
            "birth_dt",
            "cust_age",
            "name",
            "gender_cd",
            "edu_cd",
            "prof_cd",
            "org_id",
        ],
    },
    "dim_branch": {
        "rows": 312,
        "columns": ["data_dt", "org_id", "org_name", "up_org_id", "up_org_name"],
    },
    "dim_product": {
        "rows": 334694,
        "columns": [
            "prdt_id",
            "prdt_name",
            "sor_prdt_id",
            "market_id",
            "prdt_type_id",
            "prdt_type_name",
            "up_prdt_type_id",
            "up_prdt_type_name",
        ],
    },
    "dim_public": {
        "rows": 155,
        "columns": ["code", "code_type_id", "describe"],
    },
    "dwd_cust_hold_d": {
        "rows": 408150,
        "columns": ["data_dt", "pty_id", "prdt_id", "sys_source", "ccy", "hold_cnt", "mkt_val"],
    },
    "dwd_cust_tran_d": {
        "rows": 39060,
        "columns": [
            "data_dt",
            "pty_id",
            "prdt_id",
            "sys_source",
            "ccy",
            "buy_cnt",
            "buy_mnt",
            "buy_rake",
            "buy_amt",
            "buy_fare",
            "sell_cnt",
            "sell_mnt",
            "sell_rake",
            "sell_amt",
            "sell_fare",
        ],
    },
    "dws_cust_aset_d": {
        "rows": 43684,
        "columns": ["data_dt", "pty_id", "nm_tot_aset", "nm_bal", "fc_pur_aset", "fc_bal"],
    },
    "dws_cust_fin_d": {
        "rows": 4892,
        "columns": [
            "data_dt",
            "pty_id",
            "sys_source",
            "cash_in",
            "cash_out",
            "tran_in",
            "tran_out",
            "assign_in",
            "assign_out",
        ],
    },
}


SMOKE_TESTS = [
    (
        "customer_count",
        "select count(*) from ads_cust_info_d",
    ),
    (
        "q1_asset_dates",
        "select min(data_dt), max(data_dt), count(distinct data_dt) from dws_cust_aset_d",
    ),
    (
        "product_join",
        """
        select count(*)
        from dwd_cust_hold_d h
        inner join dim_product p on h.prdt_id = p.prdt_id
        where h.data_dt = '20260331'
        """,
    ),
]


def list_columns(conn: duckdb.DuckDBPyConnection, table_name: str) -> list[str]:
    rows = conn.execute(f"pragma table_info('{table_name}')").fetchall()
    return [row[1] for row in rows]


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the imported DuckDB database.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="DuckDB database path.")
    args = parser.parse_args()

    if not args.db.exists():
        raise SystemExit(f"Database not found: {args.db}")

    failures: list[str] = []
    conn = duckdb.connect(str(args.db), read_only=True)
    try:
        existing_tables = {
            row[0]
            for row in conn.execute(
                "select table_name from information_schema.tables where table_schema = 'main'"
            ).fetchall()
        }

        for table_name, expected in EXPECTED_TABLES.items():
            if table_name not in existing_tables:
                failures.append(f"missing table: {table_name}")
                continue

            actual_rows = conn.execute(f"select count(*) from {table_name}").fetchone()[0]
            actual_columns = list_columns(conn, table_name)

            row_status = "OK" if actual_rows == expected["rows"] else "FAIL"
            col_status = "OK" if actual_columns == expected["columns"] else "FAIL"
            print(f"{table_name}: rows={actual_rows} ({row_status}), columns={len(actual_columns)} ({col_status})")

            if actual_rows != expected["rows"]:
                failures.append(f"{table_name} row count: expected {expected['rows']}, got {actual_rows}")
            if actual_columns != expected["columns"]:
                failures.append(f"{table_name} columns mismatch: {actual_columns}")

        for name, sql in SMOKE_TESTS:
            result = conn.execute(sql).fetchall()
            print(f"smoke {name}: {result}")

    finally:
        conn.close()

    if failures:
        print("validation failed:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("validation passed")


if __name__ == "__main__":
    main()
