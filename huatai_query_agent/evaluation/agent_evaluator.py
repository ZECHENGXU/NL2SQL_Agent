from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any

from huatai_query_agent.agent.demo_cases import DemoCase, DemoCaseRepository
from huatai_query_agent.agent.graph import QueryAgent
from huatai_query_agent.executors.base import QueryResult
from huatai_query_agent.executors.duckdb_executor import DuckDBExecutor


PACKAGE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_DIR = PACKAGE_DIR / "evaluation"
DEFAULT_REPORT_MD = DEFAULT_REPORT_DIR / "agent_eval_report.md"
DEFAULT_REPORT_CSV = DEFAULT_REPORT_DIR / "agent_eval_results.csv"


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
    standard_hash: str
    agent_hash: str
    error_type: str = ""


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
    row_count_match: bool
    columns_match: bool
    ordered_rows_match: bool
    unordered_rows_match: bool
    exact_match: bool
    matched_score: float
    confidence: float
    elapsed_ms: float
    error_type: str
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

    def to_csv_row(self) -> dict[str, Any]:
        return {
            "query_id": self.query_id,
            "sql_mode": self.sql_mode,
            "executable": self.executable,
            "exact_match": self.exact_match,
            "row_count_match": self.row_count_match,
            "columns_match": self.columns_match,
            "ordered_rows_match": self.ordered_rows_match,
            "unordered_rows_match": self.unordered_rows_match,
            "standard_rows": self.standard_rows,
            "agent_rows": self.agent_rows,
            "standard_columns": json.dumps(self.standard_columns, ensure_ascii=False),
            "agent_columns": json.dumps(self.agent_columns, ensure_ascii=False),
            "matched_score": self.matched_score,
            "confidence": self.confidence,
            "elapsed_ms": round(self.elapsed_ms, 4),
            "error_type": self.error_type,
            "validation_errors": "; ".join(self.validation_errors),
            "execution_error": self.execution_error,
            "trace_nodes": " -> ".join(self.trace_nodes),
            "llm_call_count": self.llm_call_count,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "standard_hash": self.standard_hash,
            "agent_hash": self.agent_hash,
        }


@dataclass(frozen=True)
class AgentEvalSummary:
    sql_mode: str
    total_cases: int
    executable_cases: int
    exact_match_cases: int
    row_count_match_cases: int
    columns_match_cases: int
    ordered_rows_match_cases: int
    unordered_rows_match_cases: int
    total_llm_calls: int
    total_tokens: int
    average_elapsed_ms: float

    @property
    def executable_rate(self) -> float:
        return _ratio(self.executable_cases, self.total_cases)

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
        query_ids: list[str] | None = None,
        max_cases: int | None = None,
        preview_limit: int = 5,
        compare_limit: int = 10000,
    ) -> tuple[list[AgentEvalRecord], AgentEvalSummary]:
        cases = self._select_cases(query_ids=query_ids, max_cases=max_cases)
        agent = QueryAgent(repo=self.repo, preview_limit=preview_limit, sql_mode=sql_mode)
        records = [
            self._run_case(
                case,
                agent=agent,
                sql_mode=sql_mode,
                compare_limit=compare_limit,
            )
            for case in cases
        ]
        return records, build_summary(records, sql_mode=sql_mode)

    def _select_cases(self, *, query_ids: list[str] | None, max_cases: int | None) -> list[DemoCase]:
        if query_ids:
            cases = [self.repo.get(query_id) for query_id in query_ids]
        else:
            cases = self.repo.list_cases()
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
    ) -> AgentEvalRecord:
        standard_result = self.executor.execute(case.sql, preview_limit=compare_limit)
        state = agent.run(query_id=case.query_id)
        candidate_sql = state.get("candidate_sql", "")
        agent_result = (
            self.executor.execute(candidate_sql, preview_limit=compare_limit)
            if candidate_sql
            else _empty_query_result("Agent did not produce SQL.")
        )
        comparison = compare_query_results(standard_result, agent_result, state)
        usage = collect_llm_usage(state)
        trace_nodes = [str(event.get("node", "")) for event in state.get("trace", [])]
        validation = state.get("validation_report", {})
        execution = state.get("execution_result", {})

        return AgentEvalRecord(
            query_id=case.query_id,
            question=case.question,
            sql_mode=sql_mode,
            standard_rows=standard_result.row_count,
            agent_rows=agent_result.row_count,
            standard_columns=standard_result.columns,
            agent_columns=agent_result.columns,
            executable=comparison.agent_success,
            row_count_match=comparison.row_count_match,
            columns_match=comparison.columns_match,
            ordered_rows_match=comparison.ordered_rows_match,
            unordered_rows_match=comparison.unordered_rows_match,
            exact_match=comparison.exact_match,
            matched_score=float(state.get("matched_score", 0.0)),
            confidence=float(state.get("confidence", 0.0)),
            elapsed_ms=float(execution.get("elapsed_ms", agent_result.elapsed_ms)),
            error_type=comparison.error_type,
            validation_errors=[str(item) for item in validation.get("errors", [])],
            execution_error=str(execution.get("error") or agent_result.error or ""),
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
        )


def compare_query_results(
    standard_result: QueryResult,
    agent_result: QueryResult,
    state: dict[str, Any] | None = None,
) -> ResultComparison:
    state = state or {}
    standard_payload = _result_payload(standard_result)
    agent_payload = _result_payload(agent_result)
    row_count_match = standard_result.row_count == agent_result.row_count
    columns_match = standard_result.columns == agent_result.columns
    ordered_rows_match = _normalize_rows(standard_result.rows) == _normalize_rows(agent_result.rows)
    unordered_rows_match = sorted(_normalize_rows(standard_result.rows)) == sorted(_normalize_rows(agent_result.rows))
    exact_match = (
        standard_result.success
        and agent_result.success
        and columns_match
        and ordered_rows_match
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
        standard_hash=_hash_payload(standard_payload),
        agent_hash=_hash_payload(agent_payload),
        error_type=_classify_error(standard_result, agent_result, state, exact_match, row_count_match, columns_match),
    )


def collect_llm_usage(state: dict[str, Any]) -> dict[str, int]:
    usage_keys = [
        "llm_intent",
        "llm_slot_fill",
        "llm_plan",
        "llm_generation",
        "llm_repair",
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
    return {
        "llm_call_count": llm_call_count,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
    }


def build_summary(records: list[AgentEvalRecord], *, sql_mode: str) -> AgentEvalSummary:
    total = len(records)
    return AgentEvalSummary(
        sql_mode=sql_mode,
        total_cases=total,
        executable_cases=sum(1 for record in records if record.executable),
        exact_match_cases=sum(1 for record in records if record.exact_match),
        row_count_match_cases=sum(1 for record in records if record.row_count_match),
        columns_match_cases=sum(1 for record in records if record.columns_match),
        ordered_rows_match_cases=sum(1 for record in records if record.ordered_rows_match),
        unordered_rows_match_cases=sum(1 for record in records if record.unordered_rows_match),
        total_llm_calls=sum(record.llm_call_count for record in records),
        total_tokens=sum(record.total_tokens for record in records),
        average_elapsed_ms=sum(record.elapsed_ms for record in records) / total if total else 0.0,
    )


def write_csv_report(records: list[AgentEvalRecord], path: Path = DEFAULT_REPORT_CSV) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [record.to_csv_row() for record in records]
    fieldnames = list(rows[0].keys()) if rows else list(AgentEvalRecord("", "", "", 0, 0, [], [], False, False, False, False, False, False, 0.0, 0.0, 0.0, "").to_csv_row().keys())
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


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
        f"- Executable rate: {summary.executable_cases}/{summary.total_cases} ({summary.executable_rate:.2%})",
        f"- Exact result match rate: {summary.exact_match_cases}/{summary.total_cases} ({summary.exact_match_rate:.2%})",
        f"- Row count match rate: {summary.row_count_match_cases}/{summary.total_cases} ({summary.row_count_match_rate:.2%})",
        f"- Average execution elapsed: {summary.average_elapsed_ms:.2f} ms",
        f"- LLM calls: {summary.total_llm_calls}",
        f"- LLM total tokens: {summary.total_tokens}",
        "",
        "| Query ID | Executable | Exact Match | Row Count | Columns | Error Type |",
        "|----------|------------|-------------|-----------|---------|------------|",
    ]
    for record in records:
        lines.append(
            "| "
            + " | ".join(
                [
                    record.query_id,
                    _bool_text(record.executable),
                    _bool_text(record.exact_match),
                    f"{record.agent_rows}/{record.standard_rows}",
                    _bool_text(record.columns_match),
                    record.error_type or "ok",
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
                f"- Exact match: {_bool_text(record.exact_match)}",
                f"- Standard rows: {record.standard_rows}",
                f"- Agent rows: {record.agent_rows}",
                f"- Standard columns: `{record.standard_columns}`",
                f"- Agent columns: `{record.agent_columns}`",
                f"- Error type: `{record.error_type or 'ok'}`",
                f"- Trace: `{ ' -> '.join(record.trace_nodes) }`",
                "",
                "Agent SQL:",
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


def _classify_error(
    standard_result: QueryResult,
    agent_result: QueryResult,
    state: dict[str, Any],
    exact_match: bool,
    row_count_match: bool,
    columns_match: bool,
) -> str:
    validation = state.get("validation_report", {})
    if validation and not validation.get("passed", False):
        return "sql_validation_failed"
    if not standard_result.success:
        return "standard_sql_failed"
    if not agent_result.success:
        return "agent_sql_execution_failed"
    if exact_match:
        return ""
    if not row_count_match:
        return "row_count_mismatch"
    if not columns_match:
        return "column_mismatch"
    return "row_value_mismatch"


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
