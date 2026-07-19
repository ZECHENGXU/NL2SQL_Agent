from __future__ import annotations

import time
import uuid
from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    thread_id: str
    query_id: str
    question: str
    normalized_question: str
    is_followup: bool
    thread_summary: dict[str, Any]
    intent: dict[str, Any]
    missing_slots: list[str]
    ambiguities: dict[str, Any]
    metadata_context: dict[str, Any]
    context_ids: list[str]
    sql_plan: dict[str, Any]
    candidate_sql: str
    matched_query_id: str
    matched_score: float
    validation_report: dict[str, Any]
    execution_result: dict[str, Any]
    result_check: dict[str, Any]
    confidence: float
    retry_count: int
    max_retries: int
    next_action: str
    final_answer: str
    audit_record: dict[str, Any]
    trace: list[dict[str, Any]]
    sql_mode: str
    llm_generation: dict[str, Any]
    llm_repair: dict[str, Any]
    llm_error: str


def new_agent_state(
    *,
    question: str = "",
    query_id: str | None = None,
    thread_id: str | None = None,
    max_retries: int = 2,
) -> AgentState:
    return AgentState(
        thread_id=thread_id or "default",
        query_id=query_id or f"qrun_{uuid.uuid4().hex[:12]}",
        question=question,
        retry_count=0,
        max_retries=max_retries,
        trace=[],
        audit_record={},
        missing_slots=[],
        ambiguities={},
        confidence=0.0,
    )


def add_trace(
    state: AgentState,
    node: str,
    *,
    status: str = "ok",
    message: str = "",
    **extra: Any,
) -> dict[str, Any]:
    trace = list(state.get("trace", []))
    event: dict[str, Any] = {
        "node": node,
        "status": status,
        "message": message,
        "ts": round(time.time(), 3),
    }
    if extra:
        event.update(extra)
    trace.append(event)
    return {"trace": trace}
