from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from huatai_query_agent.llm.client import OpenAICompatibleChatClient
from huatai_query_agent.llm.config import LlmSettings


def main() -> None:
    parser = argparse.ArgumentParser(description="Check OpenAI-compatible LLM gateway connectivity.")
    parser.add_argument("--expected-model", action="append", help="Model id that must be present in /v1/models.")
    parser.add_argument("--skip-chat", action="store_true", help="Only list models; skip chat completion ping.")
    parser.add_argument("--require-local", action="store_true", help="Fail if base_url does not point to localhost/LAN.")
    args = parser.parse_args()

    settings = LlmSettings.from_env()
    print(f"provider={settings.provider}")
    print(f"base_url={settings.base_url}")
    print(f"model={settings.model}")
    print(f"api_key={settings.masked_api_key}")

    if args.require_local and not _is_local_url(settings.base_url):
        raise SystemExit(f"base_url is not local: {settings.base_url}")

    client = OpenAICompatibleChatClient(settings)
    models = client.list_models()
    print(f"models_count={len(models)}")
    print("models=" + ", ".join(models[:50]))

    expected_models = args.expected_model or [settings.model]
    missing = [model for model in expected_models if model not in models]
    if missing:
        raise SystemExit("missing_models=" + ", ".join(missing))

    if args.skip_chat:
        return

    result = client.chat_json(
        [
            {"role": "system", "content": "Return JSON only."},
            {"role": "user", "content": "返回 {\"ok\": true, \"message\": \"pong\"}"},
        ],
        max_tokens=128,
    )
    print(f"response_model={result.model}")
    print(json.dumps(json.loads(result.content), ensure_ascii=False))


def _is_local_url(url: str) -> bool:
    host = urlparse(url).hostname or ""
    return (
        host in {"localhost", "127.0.0.1", "0.0.0.0", "::1"}
        or host.startswith("192.168.")
        or host.startswith("10.")
        or any(host.startswith(f"172.{idx}.") for idx in range(16, 32))
    )


if __name__ == "__main__":
    main()
