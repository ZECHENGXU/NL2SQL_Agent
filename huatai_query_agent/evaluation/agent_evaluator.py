from __future__ import annotations

import csv
import hashlib
import json
import math
import time
import uuid
from collections import Counter
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable

import yaml

from huatai_query_agent.agent.contracts import (
    align_columns,
    derive_join_contract,
    derive_output_contract,
    derive_window_contract,
    infer_top_n,
    normalize_output_columns,
)
from huatai_query_agent.agent.demo_cases import DemoCase, DemoCaseRepository
from huatai_query_agent.agent.graph import QueryAgent
from huatai_query_agent.executors.base import QueryResult
from huatai_query_agent.executors.duckdb_executor import DuckDBExecutor
from huatai_query_agent.llm.client import CaseDeadlineExceeded


PACKAGE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_DIR = PACKAGE_DIR / "evaluation"
DEFAULT_REPORT_MD = DEFAULT_REPORT_DIR / "agent_eval_report.md"
DEFAULT_REPORT_CSV = DEFAULT_REPORT_DIR / "agent_eval_results.csv"
DEFAULT_SQL_EVENTS_JSONL = DEFAULT_REPORT_DIR / "agent_eval_sql_generation_events.jsonl"
DEFAULT_EXTENDED_CASES_PATH = DEFAULT_REPORT_DIR / "extended_query_cases.yaml"
DEFAULT_SYNTHETIC_CASES_PATH = DEFAULT_REPORT_DIR / "synthetic_query_cases.yaml"
DEFAULT_ADVANCED_CASES_PATH = DEFAULT_REPORT_DIR / "advanced_query_cases.yaml"


@dataclass(frozen=True)
class ResultComparison:
    standard_success: bool
    agent_success: bool
    executable_match: bool
    row_count_match: bool
    columns_match: bool
    ordered_rows_match: bool
    unordered_rows_match: bool
    exact_match: bool
    projection_arity_match: bool
    semantic_schema_match: bool
    ordered_semantic_match: bool
    unordered_semantic_match: bool
    semantic_result_match: bool
    column_mapping: dict[str, str]
    standard_hash: str
    agent_hash: str
    error_type: str = ""
    error_tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AgentEvalRecord:
    query_id: str
    question: str
    sql_mode: str
    standard_rows: int
    agent_rows: int
    standard_columns: list[str]
    agent_columns: list[str]
    executable: bool
    agent_completed: bool
    candidate_executable: bool
    row_count_match: bool
    columns_match: bool
    projection_arity_match: bool
    semantic_schema_match: bool
    ordered_rows_match: bool
    unordered_rows_match: bool
    ordered_semantic_match: bool
    unordered_semantic_match: bool
    semantic_result_match: bool
    order_sensitive: bool
    exact_match: bool
    matched_score: float
    confidence: float
    elapsed_ms: float
    error_type: str
    error_tags: list[str] = field(default_factory=list)
    column_mapping: dict[str, str] = field(default_factory=dict)
    validation_errors: list[str] = field(default_factory=list)
    execution_error: str = ""
    trace_nodes: list[str] = field(default_factory=list)
    candidate_sql: str = ""
    standard_sql: str = ""
    final_answer: str = ""
    llm_call_count: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    standard_hash: str = ""
    agent_hash: str = ""
    thread_id: str = ""
    repetition: int = 1
    run_id: str = ""
    model: str = ""
    sql_generation_attempt_count: int = 0
    sql_generation_elapsed_ms: float = 0.0
    sql_generation_started_at: str = ""
    sql_generation_completed_at: str = ""
    sql_generation_attempts: list[dict[str, Any]] = field(default_factory=list)
    sql_plan: dict[str, Any] = field(default_factory=dict)
    case_elapsed_ms: float = 0.0
    case_timeout_seconds: float = 50.0
    case_timed_out: bool = False

    def to_csv_row(self) -> dict[str, Any]:
        return {
            "query_id": self.query_id,
            "sql_mode": self.sql_mode,
            "executable": self.executable,
            "agent_completed": self.agent_completed,
            "candidate_executable": self.candidate_executable,
            "exact_match": self.exact_match,
            "row_count_match": self.row_count_match,
            "columns_match": self.columns_match,
            "projection_arity_match": self.projection_arity_match,
            "semantic_schema_match": self.semantic_schema_match,
            "ordered_rows_match": self.ordered_rows_match,
            "unordered_rows_match": self.unordered_rows_match,
            "ordered_semantic_match": self.ordered_semantic_match,
            "unordered_semantic_match": self.unordered_semantic_match,
            "semantic_result_match": self.semantic_result_match,
            "order_sensitive": self.order_sensitive,
            "standard_rows": self.standard_rows,
            "agent_rows": self.agent_rows,
            "standard_columns": json.dumps(self.standard_columns, ensure_ascii=False),
            "agent_columns": json.dumps(self.agent_columns, ensure_ascii=False),
            "matched_score": self.matched_score,
            "confidence": self.confidence,
            "elapsed_ms": round(self.elapsed_ms, 4),
            "case_elapsed_ms": round(self.case_elapsed_ms, 4),
            "case_timeout_seconds": self.case_timeout_seconds,
            "case_timed_out": self.case_timed_out,
            "error_type": self.error_type,
            "error_tags": json.dumps(self.error_tags, ensure_ascii=False),
            "column_mapping": json.dumps(self.column_mapping, ensure_ascii=False),
            "validation_errors": "; ".join(self.validation_errors),
            "execution_error": self.execution_error,
            "trace_nodes": " -> ".join(self.trace_nodes),
            "llm_call_count": self.llm_call_count,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "standard_hash": self.standard_hash,
            "agent_hash": self.agent_hash,
            "thread_id": self.thread_id,
            "repetition": self.repetition,
            "run_id": self.run_id,
            "model": self.model,
            "final_answer": self.final_answer,
            "sql_generation_attempt_count": self.sql_generation_attempt_count,
            "sql_generation_elapsed_ms": round(self.sql_generation_elapsed_ms, 4),
            "sql_generation_started_at": self.sql_generation_started_at,
            "sql_generation_completed_at": self.sql_generation_completed_at,
            "sql_generation_attempts": json.dumps(
                self.sql_generation_attempts,
                ensure_ascii=False,
                default=str,
            ),
            "sql_plan": json.dumps(self.sql_plan, ensure_ascii=False, default=str),
            "candidate_sql": self.candidate_sql,
            "standard_sql": self.standard_sql,
        }


@dataclass(frozen=True)
class AgentEvalSummary:
    sql_mode: str
    total_cases: int
    executable_cases: int
    agent_completed_cases: int
    candidate_executable_cases: int
    exact_match_cases: int
    row_count_match_cases: int
    columns_match_cases: int
    projection_arity_match_cases: int
    semantic_schema_match_cases: int
    ordered_rows_match_cases: int
    unordered_rows_match_cases: int
    semantic_result_match_cases: int
    total_llm_calls: int
    total_tokens: int
    average_elapsed_ms: float
    total_sql_generation_attempts: int
    total_sql_generation_elapsed_ms: float
    average_sql_generation_elapsed_ms: float
    timed_out_cases: int
    average_case_elapsed_ms: float
    max_case_elapsed_ms: float

    @property
    def executable_rate(self) -> float:
        return _ratio(self.executable_cases, self.total_cases)

    @property
    def agent_completed_rate(self) -> float:
        return _ratio(self.agent_completed_cases, self.total_cases)

    @property
    def semantic_result_match_rate(self) -> float:
        return _ratio(self.semantic_result_match_cases, self.total_cases)

    @property
    def exact_match_rate(self) -> float:
        return _ratio(self.exact_match_cases, self.total_cases)

    @property
    def row_count_match_rate(self) -> float:
        return _ratio(self.row_count_match_cases, self.total_cases)


class AgentEvaluator:
    def __init__(
        self,
        *,
        repo: DemoCaseRepository | None = None,
        executor: DuckDBExecutor | None = None,
    ) -> None:
        self.repo = repo or DemoCaseRepository()
        self.executor = executor or DuckDBExecutor()

    def run(
        self,
        *,
        sql_mode: str = "demo",
        case_set: str = "official",
        query_ids: list[str] | None = None,
        max_cases: int | None = None,
        preview_limit: int = 5,
        compare_limit: int = 10000,
        repetitions: int = 1,
        run_id: str | None = None,
        use_case_hints: bool = False,
        case_timeout_seconds: float = 50.0,
        on_record: Callable[[AgentEvalRecord, list[AgentEvalRecord], int], None] | None = None,
    ) -> tuple[list[AgentEvalRecord], AgentEvalSummary]:
        cases = self._select_cases(case_set=case_set, query_ids=query_ids, max_cases=max_cases)
        if repetitions < 1:
            raise ValueError("repetitions must be at least 1.")
        if case_timeout_seconds <= 0:
            raise ValueError("case_timeout_seconds must be greater than 0.")
        run_id = run_id or uuid.uuid4().hex[:12]
        agent = QueryAgent(repo=self.repo, preview_limit=preview_limit, sql_mode=sql_mode)
        records: list[AgentEvalRecord] = []
        total_runs = len(cases) * repetitions
        try:
            for repetition in range(1, repetitions + 1):
                for case in cases:
                    record = self._run_case(
                        case,
                        agent=agent,
                        sql_mode=sql_mode,
                        compare_limit=compare_limit,
                        repetition=repetition,
                        run_id=run_id,
                        use_case_hints=use_case_hints,
                        case_timeout_seconds=case_timeout_seconds,
                    )
                    records.append(record)
                    if on_record is not None:
                        on_record(record, records, total_runs)
        finally:
            agent.close()
        return records, build_summary(records, sql_mode=sql_mode)

    def _select_cases(self, *, case_set: str, query_ids: list[str] | None, max_cases: int | None) -> list[DemoCase]:
        if case_set not in {"official", "extended", "synthetic", "advanced", "all"}:
            raise ValueError("case_set must be official, extended, synthetic, advanced, or all.")
        official_cases = self.repo.list_cases()
        extended_cases = load_extended_eval_cases(self.repo)
        synthetic_cases = load_synthetic_eval_cases()
        advanced_cases = load_advanced_eval_cases()
        if case_set == "official":
            cases = official_cases
        elif case_set == "extended":
            cases = extended_cases
        elif case_set == "synthetic":
            cases = synthetic_cases
        elif case_set == "advanced":
            cases = advanced_cases
        else:
            cases = official_cases + extended_cases + synthetic_cases + advanced_cases

        if query_ids:
            wanted = set(query_ids)
            cases = [case for case in cases if case.query_id in wanted]
        if max_cases is not None:
            cases = cases[:max_cases]
        return cases

    def _run_case(
        self,
        case: DemoCase,
        *,
        agent: QueryAgent,
        sql_mode: str,
        compare_limit: int,
        repetition: int,
        run_id: str,
        use_case_hints: bool,
        case_timeout_seconds: float,
    ) -> AgentEvalRecord:
        case_started = time.perf_counter()
        standard_result = self.executor.execute(case.sql, preview_limit=compare_limit)
        base_query_id = str(case.intent.get("_eval_base_query_id", ""))
        use_question = bool(base_query_id or case.intent.get("_eval_use_question"))
        thread_id = f"eval:{run_id}:r{repetition}:{case.query_id}"
        request_context = None
        if use_case_hints:
            request_context = {
                "required_tables": case.required_tables,
                "expected_metrics": case.expected_metrics,
                "calculation_notes": case.intent.get("_eval_calculation_notes", []),
                "output_contract": case.output_contract,
                "expect_nonempty": bool(standard_result.success and standard_result.row_count > 0),
                "window": derive_window_contract(case.sql),
                "top_n": infer_top_n(case.question),
                "join_contract": derive_join_contract(case.sql),
            }
        try:
            remaining_seconds = max(
                0.001,
                case_timeout_seconds - (time.perf_counter() - case_started),
            )
            state = (
                agent.run(
                    question=case.question,
                    thread_id=thread_id,
                    continue_with_assumptions=True,
                    request_context=request_context,
                    case_timeout_seconds=remaining_seconds,
                )
                if use_question
                else agent.run(
                    query_id=case.query_id,
                    thread_id=thread_id,
                    continue_with_assumptions=True,
                    request_context=request_context,
                    case_timeout_seconds=remaining_seconds,
                )
            )
        except CaseDeadlineExceeded as exc:
            error = str(exc)
            state = {
                "candidate_sql": "",
                "confidence": 0.0,
                "case_timed_out": True,
                "validation_report": {"errors": [error]},
                "execution_result": {"success": False, "error": error, "elapsed_ms": 0.0},
                "trace": [{"node": "agent_run", "status": "timeout", "message": error}],
            }
        except Exception as exc:
            error = f"Unhandled agent error ({type(exc).__name__}): {exc}"
            state = {
                "candidate_sql": "",
                "confidence": 0.0,
                "validation_report": {"errors": [error]},
                "execution_result": {"success": False, "error": error, "elapsed_ms": 0.0},
                "trace": [{"node": "agent_run", "status": "failed", "message": error}],
            }
        candidate_sql = state.get("candidate_sql", "")
        agent_result = (
            self.executor.execute(candidate_sql, preview_limit=compare_limit)
            if candidate_sql
            else _empty_query_result("Agent did not produce SQL.")
        )
        comparison = compare_query_results(
            standard_result,
            agent_result,
            state,
            output_contract=case.output_contract,
        )
        case_elapsed_ms = (time.perf_counter() - case_started) * 1000
        case_timed_out = bool(state.get("case_timed_out")) or (
            case_elapsed_ms >= case_timeout_seconds * 1000
        )
        usage = collect_llm_usage(state)
        sql_generation_attempts = [
            dict(item)
            for item in state.get("sql_generation_attempts", [])
            if isinstance(item, dict)
        ]
        trace_nodes = [str(event.get("node", "")) for event in state.get("trace", [])]
        validation = state.get("validation_report", {})
        execution = state.get("execution_result", {})
        result_check = state.get("result_check", {})
        agent_completed = bool(
            not case_timed_out
            and
            execution.get("success")
            and validation.get("passed")
            and result_check.get("passed")
            and "execute_sql" in trace_nodes
        )
        model = _state_model(state)
        order_sensitive = bool(case.output_contract.get("order_sensitive", False))
        error_tags = list(comparison.error_tags)
        if case_timed_out and "case_timeout" not in error_tags:
            error_tags.insert(0, "case_timeout")
        timeout_error = (
            f"Case exceeded the {case_timeout_seconds:.2f}s evaluation deadline."
            if case_timed_out
            else ""
        )
        validation_errors = [str(item) for item in validation.get("errors", [])]
        if timeout_error and timeout_error not in validation_errors:
            validation_errors.append(timeout_error)

        return AgentEvalRecord(
            query_id=case.query_id,
            question=case.question,
            sql_mode=sql_mode,
            standard_rows=standard_result.row_count,
            agent_rows=agent_result.row_count,
            standard_columns=standard_result.columns,
            agent_columns=agent_result.columns,
            executable=comparison.agent_success,
            agent_completed=agent_completed,
            candidate_executable=comparison.agent_success,
            row_count_match=comparison.row_count_match,
            columns_match=comparison.columns_match,
            projection_arity_match=comparison.projection_arity_match,
            semantic_schema_match=comparison.semantic_schema_match,
            ordered_rows_match=comparison.ordered_rows_match,
            unordered_rows_match=comparison.unordered_rows_match,
            ordered_semantic_match=comparison.ordered_semantic_match,
            unordered_semantic_match=comparison.unordered_semantic_match,
            semantic_result_match=comparison.semantic_result_match,
            order_sensitive=order_sensitive,
            exact_match=comparison.exact_match,
            matched_score=float(state.get("matched_score", 0.0)),
            confidence=float(state.get("confidence", 0.0)),
            elapsed_ms=float(execution.get("elapsed_ms", agent_result.elapsed_ms)),
            error_type="case_timeout" if case_timed_out else comparison.error_type,
            error_tags=error_tags,
            column_mapping=comparison.column_mapping,
            validation_errors=validation_errors,
            execution_error=timeout_error or str(execution.get("error") or agent_result.error or ""),
            trace_nodes=trace_nodes,
            candidate_sql=candidate_sql,
            standard_sql=case.sql,
            final_answer=str(state.get("final_answer", "")),
            llm_call_count=usage["llm_call_count"],
            prompt_tokens=usage["prompt_tokens"],
            completion_tokens=usage["completion_tokens"],
            total_tokens=usage["total_tokens"],
            standard_hash=comparison.standard_hash,
            agent_hash=comparison.agent_hash,
            thread_id=thread_id,
            repetition=repetition,
            run_id=run_id,
            model=model,
            sql_generation_attempt_count=len(sql_generation_attempts),
            sql_generation_elapsed_ms=sum(
                float(item.get("elapsed_ms", 0.0) or 0.0)
                for item in sql_generation_attempts
            ),
            sql_generation_started_at=str(
                sql_generation_attempts[0].get("started_at", "")
                if sql_generation_attempts
                else ""
            ),
            sql_generation_completed_at=str(
                sql_generation_attempts[-1].get("completed_at", "")
                if sql_generation_attempts
                else ""
            ),
            sql_generation_attempts=sql_generation_attempts,
            sql_plan=dict(state.get("sql_plan", {})),
            case_elapsed_ms=case_elapsed_ms,
            case_timeout_seconds=case_timeout_seconds,
            case_timed_out=case_timed_out,
        )


def load_extended_eval_cases(
    repo: DemoCaseRepository,
    path: Path = DEFAULT_EXTENDED_CASES_PATH,
) -> list[DemoCase]:
    if not path.exists():
        return []
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    cases: list[DemoCase] = []
    for item in doc.get("cases", []):
        base = repo.get(str(item["base_query_id"]))
        intent = dict(base.intent)
        intent["_eval_base_query_id"] = base.query_id
        intent["_eval_category"] = item.get("category", "")
        cases.append(
            DemoCase(
                query_id=str(item["id"]),
                question=str(item["question"]),
                scenario=base.scenario,
                difficulty=base.difficulty,
                intent=intent,
                required_tables=base.required_tables,
                expected_metrics=base.expected_metrics,
                output_contract=derive_output_contract(
                    base.sql,
                    question=str(item["question"]),
                    override=dict(item.get("output_contract") or base.output_contract),
                ),
                sql=base.sql,
            )
        )
    return cases


def load_synthetic_eval_cases(path: Path = DEFAULT_SYNTHETIC_CASES_PATH) -> list[DemoCase]:
    return _load_sql_eval_cases(path, source="synthetic")


def load_advanced_eval_cases(path: Path = DEFAULT_ADVANCED_CASES_PATH) -> list[DemoCase]:
    return _load_sql_eval_cases(path, source="advanced")


def _load_sql_eval_cases(path: Path, *, source: str) -> list[DemoCase]:
    if not path.exists():
        return []
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    cases: list[DemoCase] = []
    for item in doc.get("cases", []):
        intent = dict(item.get("intent") or {})
        intent["_eval_source"] = source
        intent["_eval_category"] = item.get("category", "")
        intent["_eval_use_question"] = True
        for key in ("input_style", "capability_tags", "calculation_notes"):
            if key in item:
                intent[f"_eval_{key}"] = item[key]
        sql = str(item["sql"]).strip()
        contract_override = dict(item.get("output_contract") or {})
        if "calculation_notes" in item:
            contract_override.setdefault("calculation_notes", item["calculation_notes"])
        cases.append(
            DemoCase(
                query_id=str(item["id"]),
                question=str(item["question"]),
                scenario=str(item.get("scenario", source)),
                difficulty=str(item.get("difficulty", "")),
                intent=intent,
                required_tables=[str(table) for table in item.get("required_tables", [])],
                expected_metrics=[str(metric) for metric in item.get("expected_metrics", [])],
                output_contract=derive_output_contract(
                    sql,
                    question=str(item["question"]),
                    override=contract_override,
                ),
                sql=sql,
            )
        )
    return cases


def compare_query_results(
    standard_result: QueryResult,
    agent_result: QueryResult,
    state: dict[str, Any] | None = None,
    *,
    output_contract: dict[str, Any] | None = None,
) -> ResultComparison:
    state = state or {}
    output_contract = dict(output_contract or {})
    standard_payload = _result_payload(standard_result)
    agent_payload = _result_payload(agent_result)
    row_count_match = standard_result.row_count == agent_result.row_count
    columns_match = standard_result.columns == agent_result.columns
    projection_arity_match = len(standard_result.columns) == len(agent_result.columns)
    ordered_rows_match = _normalize_rows(standard_result.rows) == _normalize_rows(agent_result.rows)
    unordered_rows_match = sorted(_normalize_rows(standard_result.rows)) == sorted(_normalize_rows(agent_result.rows))
    mapping, extras = align_columns(standard_result.columns, agent_result.columns)
    semantic_schema_match = (
        projection_arity_match
        and not extras
        and all(index is not None for index in mapping)
    )
    aligned_rows = _align_result_rows(agent_result.rows, mapping) if semantic_schema_match else []
    contract_columns = normalize_output_columns(output_contract.get("columns") or [])
    ordered_semantic_match = bool(
        standard_result.success
        and agent_result.success
        and semantic_schema_match
        and _ordered_semantic_rows_equal(
            standard_result.rows,
            aligned_rows,
            contract_columns,
        )
    )
    unordered_semantic_match = bool(
        standard_result.success
        and agent_result.success
        and semantic_schema_match
        and _unordered_semantic_rows_equal(
            standard_result.rows,
            aligned_rows,
            contract_columns,
        )
    )
    order_sensitive = bool(output_contract.get("order_sensitive", False))
    semantic_result_match = (
        ordered_semantic_match if order_sensitive else unordered_semantic_match
    )
    exact_match = (
        standard_result.success
        and agent_result.success
        and columns_match
        and ordered_rows_match
    )
    column_mapping = {
        expected: agent_result.columns[index]
        for expected, index in zip(standard_result.columns, mapping)
        if index is not None
    }
    error_tags = _classify_error_tags(
        standard_result,
        agent_result,
        state,
        exact_match=exact_match,
        row_count_match=row_count_match,
        columns_match=columns_match,
        projection_arity_match=projection_arity_match,
        semantic_schema_match=semantic_schema_match,
        ordered_semantic_match=ordered_semantic_match,
        unordered_semantic_match=unordered_semantic_match,
        semantic_result_match=semantic_result_match,
        output_contract=output_contract,
    )
    return ResultComparison(
        standard_success=standard_result.success,
        agent_success=agent_result.success,
        executable_match=standard_result.success == agent_result.success,
        row_count_match=row_count_match,
        columns_match=columns_match,
        ordered_rows_match=ordered_rows_match,
        unordered_rows_match=unordered_rows_match,
        exact_match=exact_match,
        projection_arity_match=projection_arity_match,
        semantic_schema_match=semantic_schema_match,
        ordered_semantic_match=ordered_semantic_match,
        unordered_semantic_match=unordered_semantic_match,
        semantic_result_match=semantic_result_match,
        column_mapping=column_mapping,
        standard_hash=_hash_payload(standard_payload),
        agent_hash=_hash_payload(agent_payload),
        error_type=_primary_error_type(error_tags),
        error_tags=error_tags,
    )


def _align_result_rows(
    rows: list[tuple[Any, ...]],
    mapping: list[int | None],
) -> list[tuple[Any, ...]]:
    return [
        tuple(row[index] for index in mapping if index is not None)
        for row in rows
    ]


def _column_tolerance(
    columns: list[dict[str, Any]],
    index: int,
) -> tuple[float, float]:
    if index >= len(columns):
        return 1e-8, 1e-9
    tolerance = columns[index].get("numeric_tolerance") or {}
    return float(tolerance.get("atol", 1e-8)), float(tolerance.get("rtol", 1e-9))


def _cells_semantically_equal(
    left: Any,
    right: Any,
    *,
    atol: float,
    rtol: float,
    value_aliases: dict[str, Any] | None = None,
) -> bool:
    if left is None or right is None:
        return left is right
    if isinstance(left, (int, float, Decimal)) and isinstance(right, (int, float, Decimal)):
        return math.isclose(float(left), float(right), abs_tol=atol, rel_tol=rtol)
    aliases = {str(key): str(value) for key, value in (value_aliases or {}).items()}
    return aliases.get(str(left), str(left)) == aliases.get(str(right), str(right))


def _ordered_semantic_rows_equal(
    standard_rows: list[tuple[Any, ...]],
    agent_rows: list[tuple[Any, ...]],
    columns: list[dict[str, Any]],
) -> bool:
    if len(standard_rows) != len(agent_rows):
        return False
    for standard_row, agent_row in zip(standard_rows, agent_rows):
        if len(standard_row) != len(agent_row):
            return False
        for index, (left, right) in enumerate(zip(standard_row, agent_row)):
            atol, rtol = _column_tolerance(columns, index)
            value_aliases = (
                dict(columns[index].get("value_aliases") or {})
                if index < len(columns)
                else {}
            )
            if not _cells_semantically_equal(
                left,
                right,
                atol=atol,
                rtol=rtol,
                value_aliases=value_aliases,
            ):
                return False
    return True


def _semantic_row_key(
    row: tuple[Any, ...],
    columns: list[dict[str, Any]],
) -> tuple[str, ...]:
    output: list[str] = []
    for index, value in enumerate(row):
        if value is None:
            output.append("<NULL>")
            continue
        if isinstance(value, (int, float, Decimal)):
            _, rtol = _column_tolerance(columns, index)
            digits = 6 if rtol >= 1e-6 else 9
            output.append(f"{float(value):.{digits}f}")
            continue
        value_aliases = (
            dict(columns[index].get("value_aliases") or {})
            if index < len(columns)
            else {}
        )
        output.append(str(value_aliases.get(str(value), value)))
    return tuple(output)


def _unordered_semantic_rows_equal(
    standard_rows: list[tuple[Any, ...]],
    agent_rows: list[tuple[Any, ...]],
    columns: list[dict[str, Any]],
) -> bool:
    if len(standard_rows) != len(agent_rows):
        return False
    return Counter(_semantic_row_key(row, columns) for row in standard_rows) == Counter(
        _semantic_row_key(row, columns) for row in agent_rows
    )


def _state_model(state: dict[str, Any]) -> str:
    for attempt in reversed(state.get("sql_generation_attempts", [])):
        if isinstance(attempt, dict) and attempt.get("model"):
            return str(attempt["model"])
    for key in (
        "llm_generation",
        "llm_repair",
        "llm_plan",
        "llm_slot_fill",
        "llm_intent",
    ):
        item = state.get(key)
        if isinstance(item, dict) and item.get("model"):
            return str(item["model"])
    return ""


def collect_llm_usage(state: dict[str, Any]) -> dict[str, int]:
    usage_keys = [
        "llm_intent",
        "llm_slot_fill",
        "llm_plan",
        "llm_result_explanation",
    ]
    llm_call_count = 0
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    for key in usage_keys:
        item = state.get(key, {})
        usage = item.get("usage") if isinstance(item, dict) else None
        if not usage:
            continue
        llm_call_count += 1
        prompt_tokens += int(usage.get("prompt_tokens", 0) or 0)
        completion_tokens += int(usage.get("completion_tokens", 0) or 0)
        total_tokens += int(usage.get("total_tokens", 0) or 0)
    sql_attempts = [
        item
        for item in state.get("sql_generation_attempts", [])
        if isinstance(item, dict) and item.get("usage")
    ]
    if sql_attempts:
        for item in sql_attempts:
            usage = item["usage"]
            llm_call_count += 1
            prompt_tokens += int(usage.get("prompt_tokens", 0) or 0)
            completion_tokens += int(usage.get("completion_tokens", 0) or 0)
            total_tokens += int(usage.get("total_tokens", 0) or 0)
    else:
        for key in ("llm_generation", "llm_repair"):
            item = state.get(key, {})
            usage = item.get("usage") if isinstance(item, dict) else None
            if not usage:
                continue
            llm_call_count += 1
            prompt_tokens += int(usage.get("prompt_tokens", 0) or 0)
            completion_tokens += int(usage.get("completion_tokens", 0) or 0)
            total_tokens += int(usage.get("total_tokens", 0) or 0)
    return {
        "llm_call_count": llm_call_count,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
    }


def build_summary(records: list[AgentEvalRecord], *, sql_mode: str) -> AgentEvalSummary:
    total = len(records)
    total_generation_elapsed = sum(record.sql_generation_elapsed_ms for record in records)
    total_generation_attempts = sum(record.sql_generation_attempt_count for record in records)
    return AgentEvalSummary(
        sql_mode=sql_mode,
        total_cases=total,
        executable_cases=sum(1 for record in records if record.executable),
        agent_completed_cases=sum(1 for record in records if record.agent_completed),
        candidate_executable_cases=sum(1 for record in records if record.candidate_executable),
        exact_match_cases=sum(1 for record in records if record.exact_match),
        row_count_match_cases=sum(1 for record in records if record.row_count_match),
        columns_match_cases=sum(1 for record in records if record.columns_match),
        projection_arity_match_cases=sum(1 for record in records if record.projection_arity_match),
        semantic_schema_match_cases=sum(1 for record in records if record.semantic_schema_match),
        ordered_rows_match_cases=sum(1 for record in records if record.ordered_rows_match),
        unordered_rows_match_cases=sum(1 for record in records if record.unordered_rows_match),
        semantic_result_match_cases=sum(1 for record in records if record.semantic_result_match),
        total_llm_calls=sum(record.llm_call_count for record in records),
        total_tokens=sum(record.total_tokens for record in records),
        average_elapsed_ms=sum(record.elapsed_ms for record in records) / total if total else 0.0,
        total_sql_generation_attempts=total_generation_attempts,
        total_sql_generation_elapsed_ms=total_generation_elapsed,
        average_sql_generation_elapsed_ms=(
            total_generation_elapsed / total_generation_attempts
            if total_generation_attempts
            else 0.0
        ),
        timed_out_cases=sum(1 for record in records if record.case_timed_out),
        average_case_elapsed_ms=(
            sum(record.case_elapsed_ms for record in records) / total if total else 0.0
        ),
        max_case_elapsed_ms=max((record.case_elapsed_ms for record in records), default=0.0),
    )


def write_csv_report(records: list[AgentEvalRecord], path: Path = DEFAULT_REPORT_CSV) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [record.to_csv_row() for record in records]
    fieldnames = list(rows[0].keys()) if rows else []
    if not fieldnames:
        path.write_text("", encoding="utf-8-sig")
        return
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_sql_generation_events(
    records: list[AgentEvalRecord],
    path: Path = DEFAULT_SQL_EVENTS_JSONL,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for record in records:
        for attempt in record.sql_generation_attempts:
            event = {
                "run_id": record.run_id,
                "query_id": record.query_id,
                "repetition": record.repetition,
                "thread_id": record.thread_id,
                **attempt,
            }
            lines.append(json.dumps(event, ensure_ascii=False, default=str))
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def write_markdown_report(
    records: list[AgentEvalRecord],
    summary: AgentEvalSummary,
    path: Path = DEFAULT_REPORT_MD,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Agent Evaluation Report",
        "",
        f"- SQL mode: `{summary.sql_mode}`",
        f"- Total cases: {summary.total_cases}",
        f"- Agent completed rate: {summary.agent_completed_cases}/{summary.total_cases} ({summary.agent_completed_rate:.2%})",
        f"- Candidate SQL executable rate: {summary.candidate_executable_cases}/{summary.total_cases} ({summary.executable_rate:.2%})",
        f"- Exact result match rate: {summary.exact_match_cases}/{summary.total_cases} ({summary.exact_match_rate:.2%})",
        f"- Semantic result match rate: {summary.semantic_result_match_cases}/{summary.total_cases} ({summary.semantic_result_match_rate:.2%})",
        f"- Row count match rate: {summary.row_count_match_cases}/{summary.total_cases} ({summary.row_count_match_rate:.2%})",
        f"- Average execution elapsed: {summary.average_elapsed_ms:.2f} ms",
        f"- Timed out cases: {summary.timed_out_cases}/{summary.total_cases}",
        f"- Average case elapsed: {summary.average_case_elapsed_ms:.2f} ms",
        f"- Maximum case elapsed: {summary.max_case_elapsed_ms:.2f} ms",
        f"- SQL generation attempts: {summary.total_sql_generation_attempts}",
        f"- Total SQL generation elapsed: {summary.total_sql_generation_elapsed_ms:.2f} ms",
        f"- Average SQL generation attempt elapsed: {summary.average_sql_generation_elapsed_ms:.2f} ms",
        f"- LLM calls: {summary.total_llm_calls}",
        f"- LLM total tokens: {summary.total_tokens}",
        "",
        "| Query ID | Completed | Timeout | Case ms | Candidate SQL | Semantic | Strict Exact | Rows | Semantic Schema | SQL Gen Attempts | SQL Gen ms | Error Tags |",
        "|----------|-----------|---------|---------|---------------|----------|--------------|------|-----------------|------------------|------------|------------|",
    ]
    for record in records:
        lines.append(
            "| "
            + " | ".join(
                [
                    record.query_id,
                    _bool_text(record.agent_completed),
                    _bool_text(record.case_timed_out),
                    f"{record.case_elapsed_ms:.2f}",
                    _bool_text(record.candidate_executable),
                    _bool_text(record.semantic_result_match),
                    _bool_text(record.exact_match),
                    f"{record.agent_rows}/{record.standard_rows}",
                    _bool_text(record.semantic_schema_match),
                    str(record.sql_generation_attempt_count),
                    f"{record.sql_generation_elapsed_ms:.2f}",
                    ", ".join(record.error_tags) or "ok",
                ]
            )
            + " |"
        )

    lines.extend(["", "## Case Details", ""])
    for record in records:
        lines.extend(
            [
                f"### {record.query_id}",
                "",
                f"- Question: {record.question}",
                f"- Executable: {_bool_text(record.executable)}",
                f"- Agent completed: {_bool_text(record.agent_completed)}",
                f"- Case timed out: {_bool_text(record.case_timed_out)}",
                f"- Case elapsed: {record.case_elapsed_ms:.2f} ms",
                f"- Case timeout: {record.case_timeout_seconds:.2f} s",
                f"- Semantic result match: {_bool_text(record.semantic_result_match)}",
                f"- Exact match: {_bool_text(record.exact_match)}",
                f"- Standard rows: {record.standard_rows}",
                f"- Agent rows: {record.agent_rows}",
                f"- Standard columns: `{record.standard_columns}`",
                f"- Agent columns: `{record.agent_columns}`",
                f"- Semantic column mapping: `{record.column_mapping}`",
                f"- Error type: `{record.error_type or 'ok'}`",
                f"- Error tags: `{record.error_tags or ['ok']}`",
                f"- Final answer: {record.final_answer}",
                f"- Thread id: `{record.thread_id}`",
                f"- SQL generation attempts: {record.sql_generation_attempt_count}",
                f"- SQL generation elapsed: {record.sql_generation_elapsed_ms:.2f} ms",
                f"- SQL plan: `{json.dumps(record.sql_plan, ensure_ascii=False, default=str)}`",
                f"- Trace: `{ ' -> '.join(record.trace_nodes) }`",
            ]
        )
        if record.sql_generation_attempts:
            lines.extend(
                [
                    "",
                    "SQL generation timeline:",
                    "",
                    "| Attempt | Type | Status | Started UTC | Completed UTC | Elapsed ms | Model |",
                    "|---------|------|--------|-------------|---------------|------------|-------|",
                ]
            )
            for attempt in record.sql_generation_attempts:
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            str(attempt.get("attempt", "")),
                            str(attempt.get("attempt_type", "")),
                            str(attempt.get("status", "")),
                            str(attempt.get("started_at", "")),
                            str(attempt.get("completed_at", "")),
                            f"{float(attempt.get('elapsed_ms', 0.0) or 0.0):.2f}",
                            str(attempt.get("model", "")),
                        ]
                    )
                    + " |"
                )
            for attempt in record.sql_generation_attempts:
                lines.extend(
                    [
                        "",
                        f"SQL attempt {attempt.get('attempt', '')} ({attempt.get('attempt_type', '')}):",
                        "",
                        "```sql",
                        str(attempt.get("sql", "")).strip(),
                        "```",
                    ]
                )
        lines.extend(
            [
                "",
                "Final candidate SQL:",
                "",
                "```sql",
                record.candidate_sql.strip(),
                "```",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def _empty_query_result(error: str) -> QueryResult:
    return QueryResult(
        success=False,
        columns=[],
        rows=[],
        row_count=0,
        preview_rows=[],
        elapsed_ms=0.0,
        error=error,
    )


def _classify_error_tags(
    standard_result: QueryResult,
    agent_result: QueryResult,
    state: dict[str, Any],
    *,
    exact_match: bool,
    row_count_match: bool,
    columns_match: bool,
    projection_arity_match: bool,
    semantic_schema_match: bool,
    ordered_semantic_match: bool,
    unordered_semantic_match: bool,
    semantic_result_match: bool,
    output_contract: dict[str, Any],
) -> list[str]:
    tags: list[str] = []
    validation = state.get("validation_report", {})
    validation_errors = [str(item) for item in validation.get("errors", [])]
    validation_warnings = [str(item) for item in validation.get("warnings", [])]
    trace_nodes = [str(item.get("node", "")) for item in state.get("trace", [])]
    candidate_sql = str(state.get("candidate_sql") or "")

    if not standard_result.success:
        tags.append("standard_sql_failed")
        return tags
    if not candidate_sql and not agent_result.success:
        tags.append("no_candidate_sql")
        if "ask_clarification" in trace_nodes:
            tags.append("clarification_false_positive")
    if not agent_result.success:
        tags.append("candidate_sql_execution_failed")
    if validation and not validation.get("passed", False):
        tags.append(
            "validator_false_positive"
            if agent_result.success
            else "sql_validation_failed"
        )
    if any(item.startswith("Snapshot ") for item in validation_errors):
        tags.append("wrong_snapshot_date")
    if any("Dictionary translation" in item for item in validation_errors):
        tags.append("dictionary_not_translated")
    projection = validation.get("projection", {})
    if projection.get("missing"):
        tags.append("missing_output_column")
    if projection.get("extra"):
        tags.append("extra_output_column")
    if projection.get("wrong_order"):
        tags.append("wrong_column_order")
    if any("not requested" in item for item in validation_warnings):
        tags.append("unrequested_filter")
    if any(item.startswith("Window contract") for item in validation_errors):
        tags.append("window_contract_mismatch")
    if any(item.startswith("Join contract") for item in validation_errors):
        tags.append("population_join_mismatch")
    if any(item.startswith("Fact aggregation contract") for item in validation_errors):
        tags.append("fact_preaggregation_missing")
    if any(item.startswith("Missing fact policy") for item in validation_errors):
        tags.append("missing_fact_policy_violation")
    if any(item.startswith("Missing period policy") for item in validation_errors):
        tags.append("missing_period_policy_violation")
    if any(item.startswith("Eligibility filter") for item in validation_errors):
        tags.append("eligibility_filter_missing")
    if any(item.startswith("Top N contract") for item in validation_errors):
        tags.append("top_n_contract_violation")
    if exact_match:
        return _dedupe(tags)
    if not row_count_match:
        tags.append("row_count_mismatch")
    if not projection_arity_match:
        standard_count = len(standard_result.columns)
        agent_count = len(agent_result.columns)
        tags.append(
            "missing_output_column"
            if agent_count < standard_count
            else "extra_output_column"
        )
    elif not columns_match and semantic_schema_match:
        tags.append("schema_only_difference")
    elif not semantic_schema_match:
        tags.append("semantic_schema_mismatch")
    if semantic_schema_match and not unordered_semantic_match:
        tags.append("semantic_value_error")
    elif unordered_semantic_match and not ordered_semantic_match:
        tags.append("order_only_difference")
    if not semantic_result_match and semantic_schema_match and unordered_semantic_match:
        tags.append("order_sensitive_mismatch")
    if output_contract.get("ambiguous") or output_contract.get("accepted_alternatives"):
        tags.append("test_case_ambiguity")
    return _dedupe(tags)


def _primary_error_type(tags: list[str]) -> str:
    priorities = (
        "case_timeout",
        "standard_sql_failed",
        "clarification_false_positive",
        "sql_validation_failed",
        "validator_false_positive",
        "candidate_sql_execution_failed",
        "window_contract_mismatch",
        "population_join_mismatch",
        "fact_preaggregation_missing",
        "missing_fact_policy_violation",
        "missing_period_policy_violation",
        "eligibility_filter_missing",
        "top_n_contract_violation",
        "row_count_mismatch",
        "missing_output_column",
        "extra_output_column",
        "semantic_schema_mismatch",
        "semantic_value_error",
        "order_sensitive_mismatch",
        "order_only_difference",
        "schema_only_difference",
        "unrequested_filter",
    )
    for item in priorities:
        if item in tags:
            return item
    return ""


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def _result_payload(result: QueryResult) -> dict[str, Any]:
    return {
        "success": result.success,
        "columns": result.columns,
        "rows": _normalize_rows(result.rows),
        "row_count": result.row_count,
        "error": result.error,
    }


def _normalize_rows(rows: list[tuple[Any, ...]]) -> list[list[str]]:
    return [[_normalize_cell(cell) for cell in row] for row in rows]


def _normalize_cell(value: Any) -> str:
    if value is None:
        return "<NULL>"
    if isinstance(value, Decimal):
        return format(value.normalize(), "f")
    return str(value)


def _hash_payload(payload: dict[str, Any]) -> str:
    content = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def _bool_text(value: bool) -> str:
    return "Y" if value else "N"


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator
