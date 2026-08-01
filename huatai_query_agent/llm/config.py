from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


PACKAGE_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = PACKAGE_DIR.parent
DEFAULT_ENV_PATH = PROJECT_DIR / ".env"
DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-pro"


def load_project_dotenv(path: Path = DEFAULT_ENV_PATH, *, override: bool = False) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            continue
        if override or key not in os.environ:
            os.environ[key] = value


def _env(name: str, fallback: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None or value == "":
        return fallback
    return value


@dataclass(frozen=True)
class LlmSettings:
    provider: str
    api_key: str | None
    base_url: str
    model: str
    timeout_seconds: float
    temperature: float
    max_tokens: int

    @classmethod
    def from_env(cls, *, load_dotenv: bool = True) -> "LlmSettings":
        if load_dotenv:
            load_project_dotenv()

        provider = _env("HUATAI_LLM_PROVIDER", "deepseek") or "deepseek"
        api_key = _env("HUATAI_LLM_API_KEY") or _env("DEEPSEEK_API_KEY")
        base_url = (
            _env("HUATAI_LLM_BASE_URL")
            or _env("DEEPSEEK_BASE_URL")
            or DEFAULT_DEEPSEEK_BASE_URL
        )
        model = _env("HUATAI_LLM_MODEL") or _env("DEEPSEEK_MODEL") or DEFAULT_DEEPSEEK_MODEL
        timeout_seconds = float(_env("HUATAI_LLM_TIMEOUT_SECONDS", "60") or "60")
        temperature = float(_env("HUATAI_LLM_TEMPERATURE", "0") or "0")
        max_tokens = int(_env("HUATAI_LLM_MAX_TOKENS", "8192") or "8192")

        return cls(
            provider=provider,
            api_key=api_key,
            base_url=base_url,
            model=model,
            timeout_seconds=timeout_seconds,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def require_api_key(self) -> None:
        if _is_local_url(self.base_url):
            return
        if not self.api_key:
            raise ValueError("LLM API key is missing. Set HUATAI_LLM_API_KEY or DEEPSEEK_API_KEY in .env.")

    @property
    def masked_api_key(self) -> str:
        if not self.api_key:
            return ""
        if len(self.api_key) <= 10:
            return "***"
        return f"{self.api_key[:6]}...{self.api_key[-4:]}"


def _is_local_url(url: str) -> bool:
    host = urlparse(url).hostname or ""
    return (
        host in {"localhost", "127.0.0.1", "0.0.0.0", "::1"}
        or host.startswith("192.168.")
        or host.startswith("10.")
        or any(host.startswith(f"172.{idx}.") for idx in range(16, 32))
    )
