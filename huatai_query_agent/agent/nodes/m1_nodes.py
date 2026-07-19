from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import sqlglot
import yaml
from sqlglot import exp

from huatai_query_agent.agent.demo_cases import DemoCaseRepository
from huatai_query_agent.agent.state import AgentState, add_trace
from huatai_query_agent.executors.base import SqlExecutor
from huatai_query_agent.llm.client import LlmClientError
from huatai_query_agent.llm.sql_generator import TextToSqlGenerator
from huatai_query_agent.retrieval.hybrid_retriever import HybridMetadataRetriever


DANGEROUS_SQL_PATTERN = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|create|copy|attach|detach|pragma)\b",
    flags=re.IGNORECASE,
)
PACKAGE_DIR = Path(__file__).resolve().parents[2]
SCHEMA_CATALOG_PATH = PACKAGE_DIR / "metadata" / "schema_catalog.yaml"


def _strip_leading_comments(sql: str) -> str:
    lines = []
    for line in sql.strip().splitlines():
        if line.strip().startswith("--"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


@lru_cache(maxsize=1)
def _known_table_names() -> set[str]:
    doc = yaml.safe_load(SCHEMA_CATALOG_PATH.read_text(encoding="utf-8"))
    return set(doc.get("tables", {}).keys())


def init_run(state: AgentState) -> dict[str, Any]:
    return add_trace(state, "init_run", message="Initialized query run.")


def load_thread_context(state: AgentState) -> dict[str, Any]:
    update = {"thread_summary": state.get("thread_summary", {})}
    update.update(add_trace(state, "load_thread_context", message="No persisted checkpoint in M1 runner."))
    return update


def normalize_question(state: AgentState) -> dict[str, Any]:
    question = state.get("question", "").strip()
    normalized = re.sub(r"\s+", " ", question)
    update = {"normalized_question": normalized}
    update.update(add_trace(state, "normalize_question", message="Normalized question text."))
    return update


def detect_followup(state: AgentState) -> dict[str, Any]:
    question = state.get("normalized_question", "")
    followup_markers = ("继续", "上一个", "刚才", "只看", "改成", "再按")
    is_followup = any(marker in question for marker in followup_markers)
    update = {"is_followup": is_followup}
    update.update(add_trace(state, "detect_followup", message=f"is_followup={is_followup}"))
    return update


def parse_intent(repo: DemoCaseRepository, *, allow_unmatched: bool = False):
    def node(state: AgentState) -> dict[str, Any]:
        case, score = repo.match(
            state.get("normalized_question") or state.get("question", ""),
            state.get("matched_query_id"),
        )
        if allow_unmatched and case is not None and score < 0.85:
            case = None
        if case is None:
            if allow_unmatched:
                update = {
                    "matched_score": round(score, 4),
                    "intent": {
                        "target": "llm_text_to_sql",
                        "raw_question": state.get("normalized_question") or state.get("question", ""),
                    },
                    "missing_slots": [],
                    "ambiguities": {},
                    "confidence": 0.35,
                }
                update.update(
                    add_trace(
                        state,
                        "parse_intent",
                        message="No demo case matched; continuing with LLM Text-to-SQL path.",
                        matched_score=round(score, 4),
                    )
                )
                return update

            update: dict[str, Any] = {
                "missing_slots": ["M1 only supports the 7 official demo questions or query ids q001-q007."],
                "confidence": 0.0,
            }
            update.update(add_trace(state, "parse_intent", status="blocked", message="No demo case matched."))
            return update

        update = {
            "matched_query_id": case.query_id,
            "matched_score": round(score, 4),
            "intent": case.intent,
            "missing_slots": [],
            "ambiguities": {},
            "confidence": min(0.99, max(0.5, score)),
        }
        update.update(
            add_trace(
                state,
                "parse_intent",
                message=f"Matched demo case {case.query_id}.",
                matched_score=round(score, 4),
            )
        )
        return update

    return node


def check_intent_slots(state: AgentState) -> dict[str, Any]:
    missing_slots = state.get("missing_slots", [])
    status = "blocked" if missing_slots else "ok"
    message = "Missing required slots." if missing_slots else "Intent slots are complete."
    return add_trace(state, "check_intent_slots", status=status, message=message)


def retrieve_metadata(repo: DemoCaseRepository, retriever: HybridMetadataRetriever | None = None):
    def node(state: AgentState) -> dict[str, Any]:
        query_id = state.get("matched_query_id")
        case = repo.get(query_id) if query_id else None
        question = state.get("normalized_question") or (case.question if case else state.get("question", ""))
        fallback_context: dict[str, Any] = {}
        fallback_context_ids: list[str] = []

        if case is not None:
            fallback_context = {
                "source": "query_examples.yaml",
                "scenario": case.scenario,
                "difficulty": case.difficulty,
                "required_tables": case.required_tables,
                "expected_metrics": case.expected_metrics,
                "example_question": case.question,
            }
            fallback_context_ids = [f"example_sql.{case.query_id}"]
            fallback_context_ids.extend(f"table.{table}" for table in case.required_tables)
            fallback_context_ids.extend(f"metric.{metric}" for metric in case.expected_metrics)

        if retriever is not None:
            metadata_context = retriever.build_context(question, top_k=16)
            if fallback_context:
                metadata_context["matched_demo_case"] = fallback_context
            context_ids = list(metadata_context.get("context_ids", []))
        else:
            metadata_context = fallback_context
            context_ids = fallback_context_ids

        update = {"metadata_context": metadata_context, "context_ids": context_ids}
        update.update(
            add_trace(
                state,
                "retrieve_metadata",
                message=f"Loaded metadata context for {query_id or 'natural_language_question'}.",
                context_ids=context_ids,
            )
        )
        return update

    return node


def resolve_product(state: AgentState) -> dict[str, Any]:
    return add_trace(state, "resolve_product", message="Product resolution currently handled by metadata context and SQL generation.")


def plan_sql(state: AgentState) -> dict[str, Any]:
    metadata = state.get("metadata_context", {})
    matched_demo_case = metadata.get("matched_demo_case", {}) if isinstance(metadata, dict) else {}
    sql_mode = state.get("sql_mode", "demo")
    sql_plan = {
        "strategy": "llm_text_to_sql" if sql_mode == "llm" else "deterministic_demo_sql",
        "matched_query_id": state.get("matched_query_id"),
        "tables": metadata.get("tables") or metadata.get("required_tables", []) or matched_demo_case.get("required_tables", []),
        "metrics": metadata.get("metrics") or metadata.get("expected_metrics", []) or matched_demo_case.get("expected_metrics", []),
    }
    update = {"sql_plan": sql_plan}
    update.update(add_trace(state, "plan_sql", message=f"Built {sql_plan['strategy']} plan."))
    return update


def generate_sql(
    repo: DemoCaseRepository,
    *,
    generator: TextToSqlGenerator | None = None,
    sql_mode: str = "demo",
):
    def node(state: AgentState) -> dict[str, Any]:
        if sql_mode == "llm":
            if generator is None:
                update = {"candidate_sql": "", "llm_error": "LLM generator is not configured."}
                update.update(add_trace(state, "generate_sql", status="failed", message=update["llm_error"]))
                return update

            try:
                generated = generator.generate_sql(
                    question=state.get("normalized_question") or state.get("question", ""),
                    metadata_context=state.get("metadata_context", {}),
                )
            except LlmClientError as exc:
                update = {"candidate_sql": "", "llm_error": str(exc)}
                update.update(add_trace(state, "generate_sql", status="failed", message=str(exc)))
                return update

            update = {
                "candidate_sql": generated.sql,
                "sql_plan": generated.sql_plan or state.get("sql_plan", {}),
                "confidence": generated.confidence,
                "llm_generation": generated.to_state(),
            }
            update.update(
                add_trace(
                    state,
                    "generate_sql",
                    message=f"Generated SQL with {generated.model}.",
                    confidence=generated.confidence,
                )
            )
            return update

        case = repo.get(state["matched_query_id"])
        update = {"candidate_sql": case.sql}
        update.update(add_trace(state, "generate_sql", message=f"Loaded standard SQL for {case.query_id}."))
        return update

    return node


def validate_sql(state: AgentState) -> dict[str, Any]:
    sql = state.get("candidate_sql", "")
    executable_sql = _strip_leading_comments(sql)
    failures: list[str] = []
    referenced_tables: list[str] = []

    if not executable_sql:
        failures.append("SQL is empty.")
    if not re.match(r"^(select|with)\b", executable_sql, flags=re.IGNORECASE):
        failures.append("Only SELECT or WITH ... SELECT statements are allowed.")
    if DANGEROUS_SQL_PATTERN.search(executable_sql):
        failures.append("SQL contains a forbidden keyword.")
    if executable_sql:
        try:
            parsed_statements = sqlglot.parse(executable_sql, read="duckdb")
            if len(parsed_statements) != 1:
                failures.append("SQL must contain exactly one statement.")
            cte_names = {
                cte.alias
                for statement in parsed_statements
                if statement is not None
                for cte in statement.find_all(exp.CTE)
                if cte.alias
            }
            referenced_tables = sorted(
                {
                    table.name
                    for statement in parsed_statements
                    if statement is not None
                    for table in statement.find_all(exp.Table)
                    if table.name not in cte_names
                }
            )
            unknown_tables = [table for table in referenced_tables if table not in _known_table_names()]
            if unknown_tables:
                failures.append(f"SQL references unknown tables: {', '.join(unknown_tables)}.")
        except Exception as exc:
            failures.append(f"SQL syntax parse failed: {exc}.")

    passed = not failures
    validation_report = {
        "passed": passed,
        "checks": {
            "readonly": "passed" if passed else "failed",
            "basic_syntax": "passed" if passed else "failed",
            "metadata_whitelist": "passed" if passed else "failed",
            "metric_rules": "not_checked_in_m1",
        },
        "referenced_tables": referenced_tables,
        "errors": failures,
    }
    update = {"validation_report": validation_report, "confidence": 0.85 if passed else 0.2}
    update.update(
        add_trace(
            state,
            "validate_sql",
            status="ok" if passed else "failed",
            message="SQL guardrail passed." if passed else "; ".join(failures),
        )
    )
    return update


def execute_sql(executor: SqlExecutor, *, preview_limit: int = 20):
    def node(state: AgentState) -> dict[str, Any]:
        result = executor.execute(state.get("candidate_sql", ""), preview_limit=preview_limit)
        update = {"execution_result": result.to_state()}
        update.update(
            add_trace(
                state,
                "execute_sql",
                status="ok" if result.success else "failed",
                message=f"rows={result.row_count}, elapsed_ms={result.elapsed_ms:.2f}"
                if result.success
                else result.error,
            )
        )
        return update

    return node


def validate_result(state: AgentState) -> dict[str, Any]:
    result = state.get("execution_result", {})
    success = bool(result.get("success"))
    result_check = {
        "passed": success,
        "row_count": result.get("row_count", 0),
        "empty_result": result.get("row_count", 0) == 0,
    }
    confidence = 0.90 if success else 0.1
    update = {"result_check": result_check, "confidence": confidence}
    update.update(
        add_trace(
            state,
            "validate_result",
            status="ok" if success else "failed",
            message="Result check passed." if success else "Execution failed before result validation.",
        )
    )
    return update


def repair_sql(
    state: AgentState,
    *,
    generator: TextToSqlGenerator | None = None,
    sql_mode: str = "demo",
) -> dict[str, Any]:
    retry_count = int(state.get("retry_count", 0)) + 1

    if sql_mode == "llm" and generator is not None:
        try:
            generated = generator.repair_sql(
                question=state.get("normalized_question") or state.get("question", ""),
                metadata_context=state.get("metadata_context", {}),
                previous_sql=state.get("candidate_sql", ""),
                validation_report=state.get("validation_report", {}),
                execution_result=state.get("execution_result", {}),
            )
        except LlmClientError as exc:
            update = {"retry_count": retry_count, "llm_error": str(exc)}
            update.update(add_trace(state, "repair_sql", status="failed", message=str(exc)))
            return update

        update = {
            "retry_count": retry_count,
            "candidate_sql": generated.sql,
            "sql_plan": generated.sql_plan or state.get("sql_plan", {}),
            "confidence": generated.confidence,
            "llm_repair": generated.to_state(),
        }
        update.update(
            add_trace(
                state,
                "repair_sql",
                message=f"Repaired SQL with {generated.model}.",
                confidence=generated.confidence,
            )
        )
        return update

    update = {"retry_count": retry_count}
    update.update(add_trace(state, "repair_sql", status="skipped", message="M1 has no LLM repair path."))
    return update


def ask_clarification(state: AgentState) -> dict[str, Any]:
    missing = state.get("missing_slots", [])
    answer = "当前M1版本只支持7条赛题样例问题。请使用 q001-q007，或输入样例问题原文。"
    if missing:
        answer += f" 缺失信息：{'; '.join(missing)}"
    update = {"final_answer": answer}
    update.update(add_trace(state, "ask_clarification", status="blocked", message=answer))
    return update


def human_review_or_explain(state: AgentState) -> dict[str, Any]:
    validation = state.get("validation_report", {})
    execution = state.get("execution_result", {})
    errors = validation.get("errors") or [execution.get("error", "Unknown error")]
    answer = "查询未能自动完成，已进入人工复核路径。原因：" + "; ".join(str(item) for item in errors if item)
    update = {"final_answer": answer}
    update.update(add_trace(state, "human_review_or_explain", status="failed", message=answer))
    return update


def render_answer(state: AgentState) -> dict[str, Any]:
    result = state.get("execution_result", {})
    metadata = state.get("metadata_context", {})
    query_id = state.get("matched_query_id", "")
    if query_id:
        answer = (
            f"查询成功。匹配样例：{query_id}；场景：{metadata.get('scenario', '')}；"
            f"返回 {result.get('row_count', 0)} 行；执行耗时 {result.get('elapsed_ms', 0):.2f} ms。"
        )
    else:
        answer = (
            "查询成功。自然语言问题已通过 LLM Text-to-SQL 路径生成并执行；"
            f"返回 {result.get('row_count', 0)} 行；执行耗时 {result.get('elapsed_ms', 0):.2f} ms。"
        )
    update = {"final_answer": answer}
    update.update(add_trace(state, "render_answer", message="Rendered final answer."))
    return update


def persist_state(state: AgentState) -> dict[str, Any]:
    summary = {
        "last_query_id": state.get("matched_query_id"),
        "last_question": state.get("question"),
        "last_intent": state.get("intent", {}),
        "last_sql_plan": state.get("sql_plan", {}),
        "last_result": {
            "row_count": state.get("execution_result", {}).get("row_count"),
            "columns": state.get("execution_result", {}).get("columns", []),
        },
    }
    update = {"thread_summary": summary}
    update.update(add_trace(state, "persist_state", message="Persisted in-memory summary for M1."))
    return update
