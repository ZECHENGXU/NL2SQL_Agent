from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import uuid
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from huatai_query_agent.agent.graph import QueryAgent
from huatai_query_agent.evaluation.agent_evaluator import (
    DEFAULT_REPORT_CSV,
    DEFAULT_REPORT_MD,
    DEFAULT_SQL_EVENTS_JSONL,
    AgentEvalRecord,
    AgentEvaluator,
    build_summary,
    write_csv_report,
    write_markdown_report,
    write_sql_generation_events,
)
from huatai_query_agent.evaluation.run_agent_eval import (
    DEFAULT_MANIFEST,
    _load_regression_suite,
    _write_manifest,
)
from huatai_query_agent.llm.config import LlmSettings


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    if args.case_timeout_seconds <= 0:
        parser.error("--case-timeout-seconds must be greater than 0")
    if args.worker_case_id:
        _run_worker(args)
        return
    _run_supervisor(args)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run each evaluation case in an isolated process with a hard wall-clock timeout."
    )
    parser.add_argument("--preview", type=int, default=3)
    parser.add_argument("--compare-limit", type=int, default=10000)
    parser.add_argument("--sql-mode", choices=["demo", "llm"], default="llm")
    parser.add_argument(
        "--case-set",
        choices=["official", "extended", "synthetic", "advanced", "all"],
        default="official",
    )
    parser.add_argument("--query-id", action="append")
    parser.add_argument("--regression-suite")
    parser.add_argument("--max-cases", type=int)
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--run-id")
    parser.add_argument("--use-case-hints", action="store_true")
    parser.add_argument("--case-timeout-seconds", type=float, default=50.0)
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT_MD)
    parser.add_argument("--report-csv", type=Path, default=DEFAULT_REPORT_CSV)
    parser.add_argument("--sql-events", type=Path, default=DEFAULT_SQL_EVENTS_JSONL)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--strict-result-match", action="store_true")
    parser.add_argument("--strict-semantic-match", action="store_true")
    parser.add_argument("--worker-case-id", help=argparse.SUPPRESS)
    parser.add_argument("--worker-repetition", type=int, default=1, help=argparse.SUPPRESS)
    parser.add_argument("--worker-output", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--worker-ready", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--worker-agent-timeout-seconds", type=float, help=argparse.SUPPRESS)
    return parser


def _run_worker(args: argparse.Namespace) -> None:
    evaluator = AgentEvaluator()
    case = evaluator._select_cases(
        case_set="all",
        query_ids=[args.worker_case_id],
        max_cases=1,
    )[0]
    agent = QueryAgent(
        repo=evaluator.repo,
        preview_limit=args.preview,
        sql_mode=args.sql_mode,
    )
    try:
        if args.worker_ready:
            args.worker_ready.parent.mkdir(parents=True, exist_ok=True)
            args.worker_ready.write_text(
                datetime.now(timezone.utc).isoformat(),
                encoding="utf-8",
            )
        record = evaluator._run_case(
            case,
            agent=agent,
            sql_mode=args.sql_mode,
            compare_limit=args.compare_limit,
            repetition=args.worker_repetition,
            run_id=args.run_id,
            use_case_hints=args.use_case_hints,
            case_timeout_seconds=(
                args.worker_agent_timeout_seconds
                if args.worker_agent_timeout_seconds is not None
                else args.case_timeout_seconds
            ),
        )
    finally:
        agent.close()
    if not args.worker_output:
        raise RuntimeError("Worker output path is required.")
    args.worker_output.parent.mkdir(parents=True, exist_ok=True)
    args.worker_output.write_text(
        json.dumps(asdict(record), ensure_ascii=False, default=str),
        encoding="utf-8",
    )


def _run_supervisor(args: argparse.Namespace) -> None:
    if args.regression_suite:
        args.case_set = "all"
        suite_ids = _load_regression_suite(args.regression_suite)
        args.query_id = list(dict.fromkeys((args.query_id or []) + suite_ids))
    evaluator = AgentEvaluator()
    cases = evaluator._select_cases(
        case_set=args.case_set,
        query_ids=args.query_id,
        max_cases=args.max_cases,
    )
    if args.repetitions < 1:
        raise SystemExit("--repetitions must be at least 1")
    args.run_id = args.run_id or uuid.uuid4().hex[:12]
    records: list[AgentEvalRecord] = []
    total = len(cases) * args.repetitions

    with tempfile.TemporaryDirectory(
        prefix="huatai-hard-eval-",
        dir=DEFAULT_REPORT_MD.parent,
    ) as temp_dir:
        temp_root = Path(temp_dir)
        for repetition in range(1, args.repetitions + 1):
            for case in cases:
                record = _run_isolated_case(
                    args,
                    evaluator=evaluator,
                    case=case,
                    repetition=repetition,
                    temp_root=temp_root,
                )
                records.append(record)
                summary = build_summary(records, sql_mode=args.sql_mode)
                write_markdown_report(records, summary, args.report_md)
                write_csv_report(records, args.report_csv)
                write_sql_generation_events(records, args.sql_events)
                print(
                    f"[{len(records)}/{total}] {record.query_id}: "
                    f"completed={_yn(record.agent_completed)}, "
                    f"semantic={_yn(record.semantic_result_match)}, "
                    f"timeout={_yn(record.case_timed_out)}, "
                    f"case_ms={record.case_elapsed_ms:.2f}, "
                    f"sql_attempts={record.sql_generation_attempt_count}",
                    flush=True,
                )

    summary = build_summary(records, sql_mode=args.sql_mode)
    manifest_args = SimpleNamespace(
        sql_mode=args.sql_mode,
        case_set=args.case_set,
        query_id=args.query_id,
        max_cases=args.max_cases,
        repetitions=args.repetitions,
        use_case_hints=args.use_case_hints,
        preview=args.preview,
        compare_limit=args.compare_limit,
        case_timeout_seconds=args.case_timeout_seconds,
        sql_events=args.sql_events,
        run_id=args.run_id,
    )
    _write_manifest(args.manifest, args=manifest_args, records=records, summary=summary)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    manifest["configuration"]["hard_process_timeout"] = True
    manifest["configuration"]["timeout_starts_after_agent_initialization"] = True
    args.manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(
        f"completed={summary.agent_completed_cases}/{summary.total_cases}, "
        f"semantic={summary.semantic_result_match_cases}/{summary.total_cases}, "
        f"timeouts={summary.timed_out_cases}/{summary.total_cases}, "
        f"max_case_ms={summary.max_case_elapsed_ms:.2f}",
        flush=True,
    )
    if summary.agent_completed_cases != summary.total_cases:
        raise SystemExit(1)
    if args.strict_result_match and summary.exact_match_cases != summary.total_cases:
        raise SystemExit(1)
    if args.strict_semantic_match and summary.semantic_result_match_cases != summary.total_cases:
        raise SystemExit(1)


def _run_isolated_case(
    args: argparse.Namespace,
    *,
    evaluator: AgentEvaluator,
    case: Any,
    repetition: int,
    temp_root: Path,
) -> AgentEvalRecord:
    stem = f"r{repetition}-{case.query_id}"
    output_path = temp_root / f"{stem}.json"
    ready_path = temp_root / f"{stem}.ready"
    live_path = temp_root / f"{stem}.jsonl"
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--worker-case-id", case.query_id,
        "--worker-repetition", str(repetition),
        "--worker-output", str(output_path),
        "--worker-ready", str(ready_path),
        "--sql-mode", args.sql_mode,
        "--preview", str(args.preview),
        "--compare-limit", str(args.compare_limit),
        "--case-timeout-seconds", str(args.case_timeout_seconds),
        "--worker-agent-timeout-seconds", str(args.case_timeout_seconds + 60.0),
        "--run-id", args.run_id,
    ]
    if args.use_case_hints:
        command.append("--use-case-hints")
    env = dict(os.environ)
    env["HUATAI_LIVE_SQL_EVENTS_PATH"] = str(live_path)
    creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    process = subprocess.Popen(
        command,
        cwd=str(PROJECT_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=creationflags,
    )
    ready_error = _wait_until_ready(process, ready_path, timeout_seconds=60.0)
    if ready_error:
        _kill(process)
        return _failed_record(
            case,
            evaluator=evaluator,
            repetition=repetition,
            run_id=args.run_id,
            sql_mode=args.sql_mode,
            case_timeout_seconds=args.case_timeout_seconds,
            elapsed_ms=0.0,
            error=ready_error,
            timed_out=False,
            attempts=[],
        )

    case_started = time.perf_counter()
    try:
        stdout, stderr = process.communicate(timeout=args.case_timeout_seconds)
    except subprocess.TimeoutExpired:
        _kill(process)
        completed_at = datetime.now(timezone.utc)
        attempts = _recover_live_attempts(live_path, completed_at)
        elapsed_ms = min(
            args.case_timeout_seconds * 1000,
            (time.perf_counter() - case_started) * 1000,
        )
        return _failed_record(
            case,
            evaluator=evaluator,
            repetition=repetition,
            run_id=args.run_id,
            sql_mode=args.sql_mode,
            case_timeout_seconds=args.case_timeout_seconds,
            elapsed_ms=elapsed_ms,
            error=f"Hard case timeout after {args.case_timeout_seconds:.2f} seconds.",
            timed_out=True,
            attempts=attempts,
        )
    if output_path.exists():
        record = AgentEvalRecord(**json.loads(output_path.read_text(encoding="utf-8")))
        return replace(
            record,
            case_timeout_seconds=args.case_timeout_seconds,
            case_timed_out=False,
        )
    error = (stderr or stdout or f"Worker exited with code {process.returncode}.").strip()
    return _failed_record(
        case,
        evaluator=evaluator,
        repetition=repetition,
        run_id=args.run_id,
        sql_mode=args.sql_mode,
        case_timeout_seconds=args.case_timeout_seconds,
        elapsed_ms=(time.perf_counter() - case_started) * 1000,
        error=error,
        timed_out=False,
        attempts=_recover_live_attempts(live_path, datetime.now(timezone.utc)),
    )


def _wait_until_ready(
    process: subprocess.Popen[str],
    ready_path: Path,
    *,
    timeout_seconds: float,
) -> str:
    deadline = time.perf_counter() + timeout_seconds
    while time.perf_counter() < deadline:
        if ready_path.exists():
            return ""
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            return (stderr or stdout or f"Worker exited with code {process.returncode}.").strip()
        time.sleep(0.05)
    return f"Worker initialization exceeded {timeout_seconds:.2f} seconds."


def _kill(process: subprocess.Popen[str]) -> None:
    if process.poll() is None:
        process.kill()
    process.communicate()


def _recover_live_attempts(path: Path, completed_at: datetime) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    completed = {
        int(event["attempt"]): event
        for event in events
        if event.get("phase") == "completed"
    }
    attempts: list[dict[str, Any]] = []
    for event in events:
        if event.get("phase") != "started":
            continue
        number = int(event.get("attempt", len(attempts) + 1))
        if number in completed:
            item = dict(completed[number])
            item.pop("phase", None)
            item.pop("query_id", None)
            item.pop("thread_id", None)
            attempts.append(item)
            continue
        started_at = str(event.get("started_at") or "")
        try:
            started = datetime.fromisoformat(started_at)
            elapsed_ms = max(0.0, (completed_at - started).total_seconds() * 1000)
        except ValueError:
            elapsed_ms = 0.0
        attempts.append(
            {
                "attempt": number,
                "attempt_type": event.get("attempt_type", "initial"),
                "status": "timeout",
                "started_at": started_at,
                "completed_at": completed_at.isoformat(),
                "elapsed_ms": round(elapsed_ms, 4),
                "model": LlmSettings.from_env().model,
                "usage": {},
                "sql": "",
                "error": "Worker was terminated at the hard case deadline.",
            }
        )
    return attempts


def _failed_record(
    case: Any,
    *,
    evaluator: AgentEvaluator,
    repetition: int,
    run_id: str,
    sql_mode: str,
    case_timeout_seconds: float,
    elapsed_ms: float,
    error: str,
    timed_out: bool,
    attempts: list[dict[str, Any]],
) -> AgentEvalRecord:
    standard = evaluator.executor.execute(case.sql, preview_limit=1)
    tags = ["case_timeout", "no_candidate_sql"] if timed_out else ["worker_failed"]
    return AgentEvalRecord(
        query_id=case.query_id,
        question=case.question,
        sql_mode=sql_mode,
        standard_rows=standard.row_count,
        agent_rows=0,
        standard_columns=standard.columns,
        agent_columns=[],
        executable=False,
        agent_completed=False,
        candidate_executable=False,
        row_count_match=False,
        columns_match=False,
        projection_arity_match=False,
        semantic_schema_match=False,
        ordered_rows_match=False,
        unordered_rows_match=False,
        ordered_semantic_match=False,
        unordered_semantic_match=False,
        semantic_result_match=False,
        order_sensitive=bool(case.output_contract.get("order_sensitive", False)),
        exact_match=False,
        matched_score=0.0,
        confidence=0.0,
        elapsed_ms=0.0,
        error_type="case_timeout" if timed_out else "worker_failed",
        error_tags=tags,
        validation_errors=[error],
        execution_error=error,
        trace_nodes=["hard_timeout" if timed_out else "worker_failed"],
        standard_sql=case.sql,
        final_answer=error,
        thread_id=f"eval:{run_id}:r{repetition}:{case.query_id}",
        repetition=repetition,
        run_id=run_id,
        model=LlmSettings.from_env().model,
        sql_generation_attempt_count=len(attempts),
        sql_generation_elapsed_ms=sum(float(item.get("elapsed_ms", 0.0)) for item in attempts),
        sql_generation_started_at=str(attempts[0].get("started_at", "")) if attempts else "",
        sql_generation_completed_at=str(attempts[-1].get("completed_at", "")) if attempts else "",
        sql_generation_attempts=attempts,
        case_elapsed_ms=elapsed_ms,
        case_timeout_seconds=case_timeout_seconds,
        case_timed_out=timed_out,
    )


def _yn(value: bool) -> str:
    return "Y" if value else "N"


if __name__ == "__main__":
    main()
