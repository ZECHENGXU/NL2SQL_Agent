from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from huatai_query_agent.llm.config import LlmSettings


Message = dict[str, str]


class LlmClientError(RuntimeError):
    pass


@dataclass(frozen=True)
class ChatCompletionResult:
    content: str
    model: str
    usage: dict[str, Any]


class OpenAICompatibleChatClient:
    def __init__(self, settings: LlmSettings | None = None) -> None:
        self.settings = settings or LlmSettings.from_env()
        self.settings.require_api_key()
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - dependency check
            raise LlmClientError("openai package is not installed. Install huatai_query_agent/requirements.txt.") from exc

        self._client = OpenAI(
            api_key=self.settings.api_key,
            base_url=self.settings.base_url,
            timeout=self.settings.timeout_seconds,
        )

    def chat_json(
        self,
        messages: list[Message],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ChatCompletionResult:
        try:
            response = self._client.chat.completions.create(
                model=self.settings.model,
                messages=messages,  # type: ignore[arg-type]
                temperature=self.settings.temperature if temperature is None else temperature,
                max_tokens=self.settings.max_tokens if max_tokens is None else max_tokens,
                response_format={"type": "json_object"},
            )
        except Exception as exc:  # pragma: no cover - external API
            raise LlmClientError(str(exc)) from exc

        message = response.choices[0].message
        content = message.content or ""
        usage = response.usage.model_dump() if response.usage else {}
        return ChatCompletionResult(content=content, model=response.model, usage=usage)

