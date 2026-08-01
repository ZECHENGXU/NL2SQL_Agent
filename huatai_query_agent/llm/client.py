from __future__ import annotations

import time
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterator

from huatai_query_agent.llm.config import LlmSettings


Message = dict[str, str]
CASE_FINALIZATION_MARGIN_SECONDS = 5.0


class LlmClientError(RuntimeError):
    pass


class CaseDeadlineExceeded(LlmClientError):
    pass


_CASE_DEADLINE: ContextVar[float | None] = ContextVar(
    "huatai_case_deadline",
    default=None,
)


@contextmanager
def case_deadline(timeout_seconds: float | None) -> Iterator[None]:
    deadline = (
        time.perf_counter() + float(timeout_seconds)
        if timeout_seconds is not None
        else None
    )
    token = _CASE_DEADLINE.set(deadline)
    try:
        yield
    finally:
        _CASE_DEADLINE.reset(token)


def remaining_case_seconds() -> float | None:
    deadline = _CASE_DEADLINE.get()
    if deadline is None:
        return None
    return max(0.0, deadline - time.perf_counter())


@dataclass(frozen=True)
class ChatCompletionResult:
    content: str
    model: str
    usage: dict[str, Any]
    started_at: str
    completed_at: str
    elapsed_ms: float


class OpenAICompatibleChatClient:
    def __init__(self, settings: LlmSettings | None = None) -> None:
        self.settings = settings or LlmSettings.from_env()
        self.settings.require_api_key()
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - dependency check
            raise LlmClientError("openai package is not installed. Install huatai_query_agent/requirements.txt.") from exc

        self._client = OpenAI(
            api_key=self.settings.api_key or "local-llm-key",
            base_url=self.settings.base_url,
            timeout=self.settings.timeout_seconds,
            max_retries=0,
        )

    def list_models(self) -> list[str]:
        try:
            response = self._client.models.list()
        except Exception as exc:  # pragma: no cover - external API
            raise LlmClientError(str(exc)) from exc
        return sorted(str(item.id) for item in response.data)

    def chat_json(
        self,
        messages: list[Message],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ChatCompletionResult:
        started_at = datetime.now(timezone.utc).isoformat()
        started = time.perf_counter()
        remaining = remaining_case_seconds()
        if remaining is not None and remaining <= CASE_FINALIZATION_MARGIN_SECONDS:
            raise CaseDeadlineExceeded("Case evaluation deadline exceeded before LLM request started.")
        request_timeout = (
            min(
                self.settings.timeout_seconds,
                remaining - CASE_FINALIZATION_MARGIN_SECONDS,
            )
            if remaining is not None
            else self.settings.timeout_seconds
        )
        deadline_limited = (
            remaining is not None
            and request_timeout < self.settings.timeout_seconds
        )
        try:
            response = self._client.chat.completions.create(
                model=self.settings.model,
                messages=messages,  # type: ignore[arg-type]
                temperature=self.settings.temperature if temperature is None else temperature,
                max_tokens=self.settings.max_tokens if max_tokens is None else max_tokens,
                response_format={"type": "json_object"},
                timeout=max(0.001, request_timeout),
            )
        except Exception as exc:  # pragma: no cover - external API
            is_request_timeout = type(exc).__name__ in {
                "APITimeoutError",
                "ConnectTimeout",
                "ReadTimeout",
                "TimeoutError",
                "TimeoutException",
            }
            remaining_after = remaining_case_seconds()
            if (
                remaining_after is not None
                and (
                    remaining_after <= CASE_FINALIZATION_MARGIN_SECONDS
                    or (deadline_limited and is_request_timeout)
                )
            ):
                elapsed_ms = (time.perf_counter() - started) * 1000
                raise CaseDeadlineExceeded(
                    f"Case evaluation deadline exceeded during LLM request after {elapsed_ms:.2f} ms."
                ) from exc
            raise LlmClientError(str(exc)) from exc

        message = response.choices[0].message
        content = message.content or ""
        usage = response.usage.model_dump() if response.usage else {}
        completed_at = datetime.now(timezone.utc).isoformat()
        return ChatCompletionResult(
            content=content,
            model=response.model,
            usage=usage,
            started_at=started_at,
            completed_at=completed_at,
            elapsed_ms=(time.perf_counter() - started) * 1000,
        )
