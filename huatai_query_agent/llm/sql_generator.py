from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from huatai_query_agent.llm.client import ChatCompletionResult, LlmClientError, OpenAICompatibleChatClient
from huatai_query_agent.llm.config import LlmSettings
from huatai_query_agent.llm.prompts import build_sql_generation_messages, build_sql_repair_messages


@dataclass(frozen=True)
class GeneratedSql:
    sql: str
    sql_plan: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    assumptions: list[str] = field(default_factory=list)
    referenced_context_ids: list[str] = field(default_factory=list)
    model: str = ""
    usage: dict[str, Any] = field(default_factory=dict)
    raw_content: str = ""

    def to_state(self) -> dict[str, Any]:
        return {
            "sql": self.sql,
            "sql_plan": self.sql_plan,
            "confidence": self.confidence,
            "assumptions": self.assumptions,
            "referenced_context_ids": self.referenced_context_ids,
            "model": self.model,
            "usage": self.usage,
        }


class TextToSqlGenerator:
    def __init__(self, client: OpenAICompatibleChatClient | None = None) -> None:
        self.client = client or OpenAICompatibleChatClient()

    @classmethod
    def from_env(cls) -> "TextToSqlGenerator":
        settings = LlmSettings.from_env()
        return cls(OpenAICompatibleChatClient(settings))

    def generate_sql(self, *, question: str, metadata_context: dict[str, Any]) -> GeneratedSql:
        messages = build_sql_generation_messages(question, metadata_context)
        result = self.client.chat_json(messages)
        return _parse_generated_sql(result)

    def repair_sql(
        self,
        *,
        question: str,
        metadata_context: dict[str, Any],
        previous_sql: str,
        validation_report: dict[str, Any],
        execution_result: dict[str, Any],
    ) -> GeneratedSql:
        messages = build_sql_repair_messages(
            question=question,
            metadata_context=metadata_context,
            previous_sql=previous_sql,
            validation_report=validation_report,
            execution_result=execution_result,
        )
        result = self.client.chat_json(messages)
        return _parse_generated_sql(result)


def _parse_generated_sql(result: ChatCompletionResult) -> GeneratedSql:
    payload = _loads_json_object(result.content)
    sql = _clean_sql(str(payload.get("sql", "")))
    if not sql:
        raise LlmClientError("LLM response did not contain a non-empty SQL string.")

    confidence = payload.get("confidence", 0.0)
    try:
        confidence_value = float(confidence)
    except (TypeError, ValueError):
        confidence_value = 0.0

    return GeneratedSql(
        sql=sql,
        sql_plan=dict(payload.get("sql_plan") or {}),
        confidence=confidence_value,
        assumptions=[str(item) for item in payload.get("assumptions", [])],
        referenced_context_ids=[str(item) for item in payload.get("referenced_context_ids", [])],
        model=result.model,
        usage=result.usage,
        raw_content=result.content,
    )


def _loads_json_object(content: str) -> dict[str, Any]:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, flags=re.DOTALL)
        if not match:
            raise LlmClientError("LLM response is not a JSON object.")
        payload = json.loads(match.group(0))
    if not isinstance(payload, dict):
        raise LlmClientError("LLM JSON response is not an object.")
    return payload


def _clean_sql(sql: str) -> str:
    sql = sql.strip()
    sql = re.sub(r"^```(?:sql)?", "", sql, flags=re.IGNORECASE).strip()
    sql = re.sub(r"```$", "", sql).strip()
    if sql.endswith(";"):
        sql = sql[:-1].strip()
    return sql

