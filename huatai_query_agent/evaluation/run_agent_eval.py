from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import sqlglot
import yaml

PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from huatai_query_agent.evaluation.agent_evaluator import (
    DEFAULT_REPORT_CSV,
    DEFAULT_REPORT_MD,
    DEFAULT_SQL_EVENTS_JSONL,
    AgentEvaluator,
    build_summary,
    write_csv_report,
    write_markdown_report,
    write_sql_generation_events,
)
from huatai_query_agent.llm.config import LlmSettings
from huatai_query_agent.llm.prompts import PROMPT_VERSION


DEFAULT_MANIFEST = Path(__file__).resolve().parent / "agent_eval_manifest.json"
DEFAULT_REGRESSION_SUITES = Path(__file__).resolve().parent / "regression_suites.yaml"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the query agent evaluation pipeline.")
    parser.add_argument("--preview", type=int, default=3, help="Preview rows stored in agent state.")
    parser.add_argument("--compare-limit", type=int, default=10000, help="Max rows loaded for result comparison.")
    parser.add_argument("--sql-mode", choices=["demo", "llm"], default="demo", help="SQL generation mode.")
    parser.add_argument(
        "--case-set",
        choices=["official", "extended", "synthetic", "advanced", "all"],
        default="official",
        help="Evaluation case set.",
    )
    parser.add_argument("--query-id", action="append", help="Evaluate one query id. Can be used multiple times.")
    parser.add_argument(
        "--regression-suite",
        help="Run one named suite from regression_suites.yaml; implies --case-set all.",
    )
    parser.add_argument("--max-cases", type=int, help="Evaluate only the first N cases.")
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT_MD, help="Markdown report path.")
    parser.add_argument("--report-csv", type=Path, default=DEFAULT_REPORT_CSV, help="CSV report path.")
    parser.add_argument(
        "--sql-events",
        type=Path,
        default=DEFAULT_SQL_EVENTS_JSONL,
        help="JSONL path for every initial SQL generation and repair attempt with timestamps.",
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Evaluation run manifest path.")
    parser.add_argument("--repetitions", type=int, default=1, help="Repeat every selected case N times.")
    parser.add_argument(
        "--case-timeout-seconds",
        type=float,
        default=50.0,
        help="Hard wall-clock budget for each case across all LLM stages (default: 50).",
    )
    parser.add_argument("--run-id", help="Stable run identifier. Generated when omitted.")
    parser.add_argument(
        "--use-case-hints",
        action="store_true",
        help="Inject benchmark tables, metrics, calculation notes, and output contract into Agent context.",
    )
    parser.add_argument("--no-write-report", action="store_true", help="Print only; do not write report files.")
    parser.add_argument("--strict-result-match", action="store_true", help="Exit non-zero if any result differs from standard SQL.")
    parser.add_argument(
        "--strict-semantic-match",
        action="store_true",
        help="Exit non-zero if any case fails the order-aware semantic result contract.",
    )
    args = parser.parse_args()
    if args.case_timeout_seconds <= 0:
        parser.error("--case-timeout-seconds must be greater than 0")
    if args.regression_suite:
        args.case_set = "all"
        suite_ids = _load_regression_suite(args.regression_suite)
        args.query_id = list(dict.fromkeys((args.query_id or []) + suite_ids))

    def checkpoint(record, completed_records, total_cases) -> None:
        print(
            f"[{len(completed_records)}/{total_cases}] {record.query_id}: "
            f"completed={_yn(record.agent_completed)}, candidate={_yn(record.candidate_executable)}, "
            f"semantic={_yn(record.semantic_result_match)}, exact={_yn(record.exact_match)}, "
            f"sql_gen_attempts={record.sql_generation_attempt_count}, "
            f"sql_gen_ms={record.sql_generation_elapsed_ms:.2f}, "
            f"case_ms={record.case_elapsed_ms:.2f}, timeout={_yn(record.case_timed_out)}, "
            f"llm_calls={record.llm_call_count}, tokens={record.total_tokens}",
            flush=True,
        )
        if args.no_write_report:
            return
        partial_summary = build_summary(completed_records, sql_mode=args.sql_mode)
        write_markdown_report(completed_records, partial_summary, args.report_md)
        write_csv_report(completed_records, args.report_csv)
        write_sql_generation_events(completed_records, args.sql_events)

    records, summary = AgentEvaluator().run(
        sql_mode=args.sql_mode,
        case_set=args.case_set,
        query_ids=args.query_id,
        max_cases=args.max_cases,
        preview_limit=args.preview,
        compare_limit=args.compare_limit,
        repetitions=args.repetitions,
        run_id=args.run_id,
        use_case_hints=args.use_case_hints,
        case_timeout_seconds=args.case_timeout_seconds,
        on_record=checkpoint,
    )

    print("| Query ID | Completed | Candidate | Semantic | Exact | Row Count | Error Tags |")
    print("|----------|-----------|-----------|----------|-------|-----------|------------|")
    for record in records:
        print(
            f"| {record.query_id} | {_yn(record.agent_completed)} | {_yn(record.candidate_executable)} | "
            f"{_yn(record.semantic_result_match)} | {_yn(record.exact_match)} | "
            f"{record.agent_rows}/{record.standard_rows} | {', '.join(record.error_tags) or 'ok'} |"
        )

    print()
    print(f"agent_case_set={args.case_set}")
    print(f"agent_completed_rate[{args.sql_mode}]={summary.agent_completed_cases}/{summary.total_cases} ({summary.agent_completed_rate:.2%})")
    print(f"candidate_executable_rate[{args.sql_mode}]={summary.candidate_executable_cases}/{summary.total_cases} ({summary.executable_rate:.2%})")
    print(f"agent_semantic_match_rate[{args.sql_mode}]={summary.semantic_result_match_cases}/{summary.total_cases} ({summary.semantic_result_match_rate:.2%})")
    print(f"agent_exact_match_rate[{args.sql_mode}]={summary.exact_match_cases}/{summary.total_cases} ({summary.exact_match_rate:.2%})")
    print(f"agent_row_count_match_rate[{args.sql_mode}]={summary.row_count_match_cases}/{summary.total_cases} ({summary.row_count_match_rate:.2%})")
    print(f"agent_llm_calls[{args.sql_mode}]={summary.total_llm_calls}")
    print(f"agent_llm_tokens[{args.sql_mode}]={summary.total_tokens}")
    print(f"sql_generation_attempts[{args.sql_mode}]={summary.total_sql_generation_attempts}")
    print(f"sql_generation_elapsed_ms[{args.sql_mode}]={summary.total_sql_generation_elapsed_ms:.2f}")
    print(f"case_timeouts[{args.sql_mode}]={summary.timed_out_cases}/{summary.total_cases}")
    print(f"max_case_elapsed_ms[{args.sql_mode}]={summary.max_case_elapsed_ms:.2f}")

    if not args.no_write_report:
        write_markdown_report(records, summary, args.report_md)
        write_csv_report(records, args.report_csv)
        write_sql_generation_events(records, args.sql_events)
        _write_manifest(args.manifest, args=args, records=records, summary=summary)
        print(f"wrote_markdown={args.report_md}")
        print(f"wrote_csv={args.report_csv}")
        print(f"wrote_sql_events={args.sql_events}")
        print(f"wrote_manifest={args.manifest}")

    if summary.agent_completed_cases != summary.total_cases:
        raise SystemExit(1)
    if args.strict_result_match and summary.exact_match_cases != summary.total_cases:
        raise SystemExit(1)
    if args.strict_semantic_match and summary.semantic_result_match_cases != summary.total_cases:
        raise SystemExit(1)


def _yn(value: bool) -> str:
    return "Y" if value else "N"


def _write_manifest(path: Path, *, args, records, summary) -> None:
    settings = LlmSettings.from_env()
    evaluation_dir = Path(__file__).resolve().parent
    metadata_dir = evaluation_dir.parent / "metadata"
    run_id = records[0].run_id if records else args.run_id or ""
    payload = {
        "schema_version": "2.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "configuration": {
            "sql_mode": args.sql_mode,
            "case_set": args.case_set,
            "query_ids": args.query_id or [],
            "max_cases": args.max_cases,
            "repetitions": args.repetitions,
            "use_case_hints": args.use_case_hints,
            "preview_limit": args.preview,
            "compare_limit": args.compare_limit,
            "case_timeout_seconds": args.case_timeout_seconds,
            "sql_events": str(args.sql_events),
        },
        "llm": {
            "provider": settings.provider,
            "base_url": settings.base_url,
            "model": settings.model,
            "temperature": settings.temperature,
            "max_tokens": settings.max_tokens,
            "timeout_seconds": settings.timeout_seconds,
        },
        "versions": {
            "prompt": PROMPT_VERSION,
            "metadata": _yaml_version(metadata_dir / "schema_catalog.yaml"),
            "python": platform.python_version(),
            "duckdb": duckdb.__version__,
            "sqlglot": sqlglot.__version__,
        },
        "artifact_hashes": {
            "schema_catalog": _file_hash(metadata_dir / "schema_catalog.yaml"),
            "metrics": _file_hash(metadata_dir / "metrics.yaml"),
            "relationships": _file_hash(metadata_dir / "relationships.yaml"),
        },
        "summary": {
            "total_runs": summary.total_cases,
            "agent_completed": summary.agent_completed_cases,
            "candidate_executable": summary.candidate_executable_cases,
            "semantic_result_match": summary.semantic_result_match_cases,
            "strict_exact_match": summary.exact_match_cases,
            "llm_calls": summary.total_llm_calls,
            "tokens": summary.total_tokens,
            "sql_generation_attempts": summary.total_sql_generation_attempts,
            "sql_generation_elapsed_ms": summary.total_sql_generation_elapsed_ms,
            "average_sql_generation_attempt_elapsed_ms": summary.average_sql_generation_elapsed_ms,
            "timed_out_cases": summary.timed_out_cases,
            "average_case_elapsed_ms": summary.average_case_elapsed_ms,
            "max_case_elapsed_ms": summary.max_case_elapsed_ms,
        },
        "threads": [
            {
                "query_id": record.query_id,
                "repetition": record.repetition,
                "thread_id": record.thread_id,
                "model": record.model,
                "sql_generation_attempt_count": record.sql_generation_attempt_count,
                "sql_generation_elapsed_ms": record.sql_generation_elapsed_ms,
                "sql_generation_attempts": record.sql_generation_attempts,
                "sql_plan": record.sql_plan,
                "case_elapsed_ms": record.case_elapsed_ms,
                "case_timeout_seconds": record.case_timeout_seconds,
                "case_timed_out": record.case_timed_out,
            }
            for record in records
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16] if path.exists() else ""


def _yaml_version(path: Path) -> str:
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("version:"):
            return line.split(":", 1)[1].strip().strip('"')
    return _file_hash(path)


def _load_regression_suite(name: str) -> list[str]:
    document = yaml.safe_load(DEFAULT_REGRESSION_SUITES.read_text(encoding="utf-8")) or {}
    suite = document.get("suites", {}).get(name)
    if not suite:
        available = ", ".join(sorted(document.get("suites", {})))
        raise SystemExit(f"Unknown regression suite {name!r}. Available: {available}")
    return [str(item) for item in suite.get("query_ids", [])]


if __name__ == "__main__":
    main()
