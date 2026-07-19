from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from huatai_query_agent.evaluation.agent_evaluator import (
    DEFAULT_REPORT_CSV,
    DEFAULT_REPORT_MD,
    AgentEvaluator,
    write_csv_report,
    write_markdown_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the query agent evaluation pipeline.")
    parser.add_argument("--preview", type=int, default=3, help="Preview rows stored in agent state.")
    parser.add_argument("--compare-limit", type=int, default=10000, help="Max rows loaded for result comparison.")
    parser.add_argument("--sql-mode", choices=["demo", "llm"], default="demo", help="SQL generation mode.")
    parser.add_argument("--query-id", action="append", help="Evaluate one query id. Can be used multiple times.")
    parser.add_argument("--max-cases", type=int, help="Evaluate only the first N cases.")
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT_MD, help="Markdown report path.")
    parser.add_argument("--report-csv", type=Path, default=DEFAULT_REPORT_CSV, help="CSV report path.")
    parser.add_argument("--no-write-report", action="store_true", help="Print only; do not write report files.")
    parser.add_argument("--strict-result-match", action="store_true", help="Exit non-zero if any result differs from standard SQL.")
    args = parser.parse_args()

    records, summary = AgentEvaluator().run(
        sql_mode=args.sql_mode,
        query_ids=args.query_id,
        max_cases=args.max_cases,
        preview_limit=args.preview,
        compare_limit=args.compare_limit,
    )

    print("| Query ID | Executable | Exact Match | Row Count | Columns | Error Type |")
    print("|----------|------------|-------------|-----------|---------|------------|")
    for record in records:
        print(
            f"| {record.query_id} | {_yn(record.executable)} | {_yn(record.exact_match)} | "
            f"{record.agent_rows}/{record.standard_rows} | {_yn(record.columns_match)} | {record.error_type or 'ok'} |"
        )

    print()
    print(f"agent_executable_rate[{args.sql_mode}]={summary.executable_cases}/{summary.total_cases} ({summary.executable_rate:.2%})")
    print(f"agent_exact_match_rate[{args.sql_mode}]={summary.exact_match_cases}/{summary.total_cases} ({summary.exact_match_rate:.2%})")
    print(f"agent_row_count_match_rate[{args.sql_mode}]={summary.row_count_match_cases}/{summary.total_cases} ({summary.row_count_match_rate:.2%})")
    print(f"agent_llm_calls[{args.sql_mode}]={summary.total_llm_calls}")
    print(f"agent_llm_tokens[{args.sql_mode}]={summary.total_tokens}")

    if not args.no_write_report:
        write_markdown_report(records, summary, args.report_md)
        write_csv_report(records, args.report_csv)
        print(f"wrote_markdown={args.report_md}")
        print(f"wrote_csv={args.report_csv}")

    if summary.executable_cases != summary.total_cases:
        raise SystemExit(1)
    if args.strict_result_match and summary.exact_match_cases != summary.total_cases:
        raise SystemExit(1)


def _yn(value: bool) -> str:
    return "Y" if value else "N"


if __name__ == "__main__":
    main()
