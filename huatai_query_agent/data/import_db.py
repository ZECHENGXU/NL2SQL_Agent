from __future__ import annotations

import argparse
from pathlib import Path

try:
    import duckdb
except ImportError as exc:  # pragma: no cover - dependency guard
    raise SystemExit(
        "Missing dependency: duckdb. Install with `python -m pip install -r huatai_query_agent/requirements.txt`."
    ) from exc


PROJECT_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_DIR / "原始文件"
DEFAULT_DB_PATH = Path(__file__).resolve().parent / "cust_data.duckdb"


TABLES = {
    "ads_cust_info_d": {
        "file": "ads_cust_info_d_202606031625.csv",
        "ddl": """
            create table ads_cust_info_d (
                data_dt varchar,
                pty_id varchar,
                sor_pty_id varchar,
                cust_lvl_cd varchar,
                cust_status varchar,
                cust_type varchar,
                prov_name varchar,
                city_name varchar,
                birth_dt varchar,
                cust_age decimal(20,0),
                name varchar,
                gender_cd varchar,
                edu_cd varchar,
                prof_cd varchar,
                org_id varchar
            )
        """,
    },
    "dim_branch": {
        "file": "dim_branch_202606021048.csv",
        "ddl": """
            create table dim_branch (
                data_dt varchar,
                org_id varchar,
                org_name varchar,
                up_org_id varchar,
                up_org_name varchar
            )
        """,
    },
    "dim_product": {
        "file": "dim_product_202606021049.csv",
        "ddl": """
            create table dim_product (
                prdt_id varchar,
                prdt_name varchar,
                sor_prdt_id varchar,
                market_id varchar,
                prdt_type_id varchar,
                prdt_type_name varchar,
                up_prdt_type_id varchar,
                up_prdt_type_name varchar
            )
        """,
    },
    "dim_public": {
        "file": "dim_public_202606021050.csv",
        "ddl": """
            create table dim_public (
                code varchar,
                code_type_id varchar,
                "describe" varchar
            )
        """,
    },
    "dwd_cust_hold_d": {
        "file": "dwd_cust_hold_d_202606021051.csv",
        "ddl": """
            create table dwd_cust_hold_d (
                data_dt varchar,
                pty_id varchar,
                prdt_id varchar,
                sys_source varchar,
                ccy varchar,
                hold_cnt decimal(20,4),
                mkt_val decimal(20,4)
            )
        """,
    },
    "dwd_cust_tran_d": {
        "file": "dwd_cust_tran_d_202606021051.csv",
        "ddl": """
            create table dwd_cust_tran_d (
                data_dt varchar,
                pty_id varchar,
                prdt_id varchar,
                sys_source varchar,
                ccy varchar,
                buy_cnt integer,
                buy_mnt decimal(20,4),
                buy_rake decimal(20,4),
                buy_amt decimal(20,4),
                buy_fare decimal(20,4),
                sell_cnt integer,
                sell_mnt decimal(20,4),
                sell_rake decimal(20,4),
                sell_amt decimal(20,4),
                sell_fare decimal(20,4)
            )
        """,
    },
    "dws_cust_aset_d": {
        "file": "dws_cust_aset_d_202606021051.csv",
        "ddl": """
            create table dws_cust_aset_d (
                data_dt varchar,
                pty_id varchar,
                nm_tot_aset decimal(20,4),
                nm_bal decimal(20,4),
                fc_pur_aset decimal(20,4),
                fc_bal decimal(20,4)
            )
        """,
    },
    "dws_cust_fin_d": {
        "file": "dws_cust_fin_d_202606021050.csv",
        "ddl": """
            create table dws_cust_fin_d (
                data_dt varchar,
                pty_id varchar,
                sys_source varchar,
                cash_in decimal(20,4),
                cash_out decimal(20,4),
                tran_in decimal(20,4),
                tran_out decimal(20,4),
                assign_in decimal(20,4),
                assign_out decimal(20,4)
            )
        """,
    },
}


INDEXES = [
    "create index if not exists idx_ads_cust_pty on ads_cust_info_d(pty_id)",
    "create index if not exists idx_ads_cust_org on ads_cust_info_d(org_id)",
    "create index if not exists idx_branch_org on dim_branch(org_id)",
    "create index if not exists idx_product_prdt on dim_product(prdt_id)",
    "create index if not exists idx_product_name_type on dim_product(prdt_name, prdt_type_name)",
    "create index if not exists idx_hold_pty_date on dwd_cust_hold_d(pty_id, data_dt)",
    "create index if not exists idx_hold_prdt on dwd_cust_hold_d(prdt_id)",
    "create index if not exists idx_tran_pty_date on dwd_cust_tran_d(pty_id, data_dt)",
    "create index if not exists idx_tran_prdt on dwd_cust_tran_d(prdt_id)",
    "create index if not exists idx_aset_pty_date on dws_cust_aset_d(pty_id, data_dt)",
    "create index if not exists idx_fin_pty_date on dws_cust_fin_d(pty_id, data_dt)",
]


def sql_string(path: Path) -> str:
    return path.as_posix().replace("'", "''")


def import_table(conn: duckdb.DuckDBPyConnection, table_name: str, config: dict[str, str]) -> int:
    csv_path = RAW_DIR / config["file"]
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing CSV for {table_name}: {csv_path}")

    conn.execute(f"drop table if exists {table_name}")
    conn.execute(config["ddl"])
    conn.execute(
        f"""
        copy {table_name}
        from '{sql_string(csv_path)}'
        (header true, delim ',', quote '"')
        """
    )
    return conn.execute(f"select count(*) from {table_name}").fetchone()[0]


def create_indexes(conn: duckdb.DuckDBPyConnection) -> None:
    for statement in INDEXES:
        conn.execute(statement)


def main() -> None:
    parser = argparse.ArgumentParser(description="Import contest CSV files into DuckDB.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="Output DuckDB database path.")
    parser.add_argument("--skip-indexes", action="store_true", help="Skip index creation.")
    args = parser.parse_args()

    args.db.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(args.db))
    try:
        for table_name, config in TABLES.items():
            row_count = import_table(conn, table_name, config)
            print(f"imported {table_name}: {row_count} rows")

        if not args.skip_indexes:
            create_indexes(conn)
            print("indexes created")

        conn.execute("checkpoint")
        print(f"database ready: {args.db}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
