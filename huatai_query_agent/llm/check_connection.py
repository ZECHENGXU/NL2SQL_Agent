from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from huatai_query_agent.llm.client import OpenAICompatibleChatClient
from huatai_query_agent.llm.config import LlmSettings


def main() -> None:
    settings = LlmSettings.from_env()
    print(f"provider={settings.provider}")
    print(f"base_url={settings.base_url}")
    print(f"model={settings.model}")
    print(f"api_key={settings.masked_api_key}")

    client = OpenAICompatibleChatClient(settings)
    result = client.chat_json(
        [
            {"role": "system", "content": "Return JSON only."},
            {"role": "user", "content": "返回 {\"ok\": true, \"message\": \"pong\"}"},
        ],
        max_tokens=128,
    )
    print(f"response_model={result.model}")
    print(json.dumps(json.loads(result.content), ensure_ascii=False))


if __name__ == "__main__":
    main()

