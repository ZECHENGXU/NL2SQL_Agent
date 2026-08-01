from __future__ import annotations

import argparse
import atexit
import json
import os
import sys
import threading
import time
import traceback
import uuid
import webbrowser
from decimal import Decimal
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from huatai_query_agent.agent.demo_cases import DemoCaseRepository
from huatai_query_agent.agent.graph import LANGGRAPH_AVAILABLE, QueryAgent
from huatai_query_agent.agent.state import AgentState
from huatai_query_agent.llm.client import OpenAICompatibleChatClient
from huatai_query_agent.llm.config import LlmSettings
from huatai_query_agent.retrieval.hybrid_retriever import HybridMetadataRetriever


DEFAULT_WEB_CASE_TIMEOUT_SECONDS = 180.0
PENDING_QUERY_TTL_SECONDS = 30 * 60
LLM_HEALTH_SUCCESS_TTL_SECONDS = 60.0
LLM_HEALTH_FAILURE_TTL_SECONDS = 5.0


class DemoRuntime:
    def __init__(self) -> None:
        self.repo = DemoCaseRepository()
        self.retriever = HybridMetadataRetriever()
        self.agents: dict[tuple[str, int], QueryAgent] = {}
        self.pending_queries: dict[str, tuple[float, str, int, AgentState]] = {}
        self.pending_lock = threading.Lock()
        self.llm_health_cache: tuple[tuple[str, str], float, dict[str, Any]] | None = None
        self.llm_health_lock = threading.Lock()

    def get_agent(self, *, sql_mode: str, preview_limit: int) -> QueryAgent:
        key = (sql_mode, preview_limit)
        if key not in self.agents:
            self.agents[key] = QueryAgent(
                repo=self.repo,
                retriever=self.retriever,
                sql_mode=sql_mode,
                preview_limit=preview_limit,
            )
        return self.agents[key]

    def store_pending(
        self,
        *,
        sql_mode: str,
        preview_limit: int,
        state: AgentState,
    ) -> str:
        token = uuid.uuid4().hex
        now = time.monotonic()
        with self.pending_lock:
            self._prune_pending(now)
            self.pending_queries[token] = (now, sql_mode, preview_limit, state)
        return token

    def take_pending(self, token: str) -> tuple[QueryAgent, AgentState] | None:
        now = time.monotonic()
        with self.pending_lock:
            self._prune_pending(now)
            pending = self.pending_queries.pop(token, None)
        if pending is None:
            return None
        _, sql_mode, preview_limit, state = pending
        return self.get_agent(sql_mode=sql_mode, preview_limit=preview_limit), state

    def _prune_pending(self, now: float) -> None:
        expired = [
            token
            for token, (created_at, _, _, _) in self.pending_queries.items()
            if now - created_at > PENDING_QUERY_TTL_SECONDS
        ]
        for token in expired:
            self.pending_queries.pop(token, None)

    def check_llm(self, *, force: bool = False) -> dict[str, Any]:
        settings = LlmSettings.from_env()
        config_key = (settings.base_url, settings.model)
        now = time.monotonic()
        with self.llm_health_lock:
            if not force and self.llm_health_cache is not None:
                cached_key, checked_at, cached_result = self.llm_health_cache
                ttl = (
                    LLM_HEALTH_SUCCESS_TTL_SECONDS
                    if cached_result.get("ok")
                    else LLM_HEALTH_FAILURE_TTL_SECONDS
                )
                if cached_key == config_key and now - checked_at <= ttl:
                    return dict(cached_result)

            started = time.perf_counter()
            try:
                models = OpenAICompatibleChatClient(settings).list_models()
                if settings.model not in models:
                    result = {
                        "ok": False,
                        "model": settings.model,
                        "error": f"已连接 LLM 服务，但未找到配置模型 {settings.model}。",
                    }
                else:
                    result = {
                        "ok": True,
                        "model": settings.model,
                        "error": "",
                    }
            except Exception as exc:
                result = {
                    "ok": False,
                    "model": settings.model,
                    "error": _llm_connectivity_error(exc, settings.base_url),
                }

            result["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 2)
            self.llm_health_cache = (config_key, now, dict(result))
            return result

    def close(self) -> None:
        with self.pending_lock:
            self.pending_queries.clear()
        self.retriever.close()


RUNTIME: DemoRuntime | None = None


def get_runtime() -> DemoRuntime:
    global RUNTIME
    if RUNTIME is None:
        RUNTIME = DemoRuntime()
    return RUNTIME


def close_runtime() -> None:
    if RUNTIME is not None:
        RUNTIME.close()


atexit.register(close_runtime)


class AgentDemoHandler(BaseHTTPRequestHandler):
    server_version = "HuataiAgentDemo/1.0"

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/":
            self._send_html(INDEX_HTML)
        elif path == "/api/health":
            self._send_json(self._health())
        elif path == "/api/examples":
            self._send_json(self._examples())
        elif path == "/api/llm/health":
            force = str(parse_qs(parsed.query).get("force", [""])[0]).lower() in {
                "1",
                "true",
                "yes",
                "on",
            }
            self._send_json(get_runtime().check_llm(force=force))
        else:
            self._send_json({"error": f"Not found: {path}"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        handlers = {
            "/api/query": self._run_query,
            "/api/query/prepare": self._prepare_query,
            "/api/query/execute": self._execute_query,
        }
        handler = handlers.get(path)
        if handler is None:
            self._send_json({"error": f"Not found: {path}"}, status=HTTPStatus.NOT_FOUND)
            return

        try:
            payload = self._read_json()
            response = handler(payload)
            self._send_json(response)
        except Exception as exc:  # pragma: no cover - local demo guard
            self._send_json(
                {
                    "ok": False,
                    "error": str(exc),
                    "traceback": traceback.format_exc(limit=6),
                },
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[web] {self.address_string()} - {fmt % args}")

    def _health(self) -> dict[str, Any]:
        settings = LlmSettings.from_env()
        return {
            "ok": True,
            "project_dir": str(PROJECT_DIR),
            "langgraph_available": LANGGRAPH_AVAILABLE,
            "llm_provider": settings.provider,
            "llm_base_url": settings.base_url,
            "llm_model": settings.model,
            "llm_cloud": _is_cloud_url(settings.base_url),
            "web_case_timeout_seconds": float(
                os.getenv("HUATAI_WEB_CASE_TIMEOUT_SECONDS", str(DEFAULT_WEB_CASE_TIMEOUT_SECONDS))
                or str(DEFAULT_WEB_CASE_TIMEOUT_SECONDS)
            ),
            "demo_cases": len(get_runtime().repo.list_cases()),
        }

    def _examples(self) -> dict[str, Any]:
        examples = [
            {
                "id": case.query_id,
                "question": case.question,
                "scenario": case.scenario,
                "difficulty": case.difficulty,
                "tables": case.required_tables,
                "metrics": case.expected_metrics,
            }
            for case in get_runtime().repo.list_cases()
        ]
        return {"ok": True, "examples": examples}

    def _run_query(self, payload: dict[str, Any]) -> dict[str, Any]:
        sql_mode = str(payload.get("sql_mode") or "demo")
        if sql_mode not in {"demo", "llm"}:
            raise ValueError("sql_mode must be demo or llm.")

        preview_limit = int(payload.get("preview_limit") or 5)
        question = str(payload.get("question") or "").strip()
        query_id = str(payload.get("query_id") or "").strip() or None
        allow_cloud_llm = bool(payload.get("allow_cloud_llm"))

        settings = LlmSettings.from_env()
        if sql_mode == "llm" and _is_cloud_url(settings.base_url) and not allow_cloud_llm:
            return {
                "ok": False,
                "error": "当前 LLM 配置指向云端 API。请先确认允许发送问题、元数据上下文和结果摘要。",
            }

        runtime = get_runtime()
        if sql_mode == "llm":
            llm_health = runtime.check_llm()
            if not llm_health.get("ok"):
                return {"ok": False, "error": llm_health.get("error") or "LLM 服务不可用。"}

        agent = runtime.get_agent(sql_mode=sql_mode, preview_limit=preview_limit)
        if sql_mode == "llm":
            case_timeout_seconds = float(
                os.getenv("HUATAI_WEB_CASE_TIMEOUT_SECONDS", str(DEFAULT_WEB_CASE_TIMEOUT_SECONDS))
                or str(DEFAULT_WEB_CASE_TIMEOUT_SECONDS)
            )
            state = agent.run(
                question=question,
                query_id=query_id,
                thread_id="web-demo",
                case_timeout_seconds=case_timeout_seconds,
            )
        else:
            state = agent.run(question=question, query_id=query_id, thread_id="web-demo")
        return {"ok": True, "state": _jsonable(state)}

    def _prepare_query(self, payload: dict[str, Any]) -> dict[str, Any]:
        sql_mode = str(payload.get("sql_mode") or "demo")
        if sql_mode not in {"demo", "llm"}:
            raise ValueError("sql_mode must be demo or llm.")

        preview_limit = int(payload.get("preview_limit") or 5)
        question = str(payload.get("question") or "").strip()
        query_id = str(payload.get("query_id") or "").strip() or None
        allow_cloud_llm = bool(payload.get("allow_cloud_llm"))

        settings = LlmSettings.from_env()
        if sql_mode == "llm" and _is_cloud_url(settings.base_url) and not allow_cloud_llm:
            return {
                "ok": False,
                "error": "当前 LLM 配置指向云端 API。请先确认允许发送问题、元数据上下文和结果摘要。",
            }

        runtime = get_runtime()
        if sql_mode == "llm":
            llm_health = runtime.check_llm()
            if not llm_health.get("ok"):
                return {"ok": False, "error": llm_health.get("error") or "LLM 服务不可用。"}

        agent = runtime.get_agent(sql_mode=sql_mode, preview_limit=preview_limit)
        case_timeout_seconds = (
            float(
                os.getenv("HUATAI_WEB_CASE_TIMEOUT_SECONDS", str(DEFAULT_WEB_CASE_TIMEOUT_SECONDS))
                or str(DEFAULT_WEB_CASE_TIMEOUT_SECONDS)
            )
            if sql_mode == "llm"
            else None
        )
        state = agent.prepare(
            question=question,
            query_id=query_id,
            thread_id="web-demo",
            case_timeout_seconds=case_timeout_seconds,
        )
        ready_to_execute = bool(
            state.get("next_action") == "execute_sql"
            and state.get("candidate_sql")
            and state.get("validation_report", {}).get("passed")
        )
        execution_token = (
            runtime.store_pending(
                sql_mode=sql_mode,
                preview_limit=preview_limit,
                state=state,
            )
            if ready_to_execute
            else ""
        )
        return {
            "ok": True,
            "state": _jsonable(state),
            "ready_to_execute": ready_to_execute,
            "execution_token": execution_token,
        }

    def _execute_query(self, payload: dict[str, Any]) -> dict[str, Any]:
        token = str(payload.get("execution_token") or "").strip()
        if not token:
            return {"ok": False, "error": "缺少 SQL 执行令牌，请重新生成 SQL。"}

        pending = get_runtime().take_pending(token)
        if pending is None:
            return {"ok": False, "error": "SQL 执行令牌已过期或已使用，请重新生成 SQL。"}

        agent, state = pending
        case_timeout_seconds = float(
            os.getenv("HUATAI_WEB_CASE_TIMEOUT_SECONDS", str(DEFAULT_WEB_CASE_TIMEOUT_SECONDS))
            or str(DEFAULT_WEB_CASE_TIMEOUT_SECONDS)
        )
        result = agent.execute_prepared(
            state,
            case_timeout_seconds=case_timeout_seconds,
        )
        return {"ok": True, "state": _jsonable(result)}

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(raw or "{}")

    def _send_html(self, content: str) -> None:
        body = content.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: dict[str, Any], *, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(_jsonable(payload), ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(*, host: str, port: int, open_browser: bool = False) -> None:
    server = ThreadingHTTPServer((host, port), AgentDemoHandler)
    url = f"http://{host}:{port}"
    print(f"Huatai Agent demo running at {url}")
    print("Press Ctrl+C to stop.")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        close_runtime()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Huatai Agent local web demo.")
    parser.add_argument("--host", default=os.getenv("HUATAI_WEB_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("HUATAI_WEB_PORT", "8501")))
    parser.add_argument("--open", action="store_true", help="Open the browser after starting.")
    args = parser.parse_args()
    run_server(host=args.host, port=args.port, open_browser=args.open)


def _is_cloud_url(base_url: str) -> bool:
    lowered = base_url.lower()
    return not (
        "127.0.0.1" in lowered
        or "localhost" in lowered
        or "0.0.0.0" in lowered
        or "host.docker.internal" in lowered
    )


def _llm_connectivity_error(exc: Exception, base_url: str) -> str:
    detail = str(exc).strip() or type(exc).__name__
    if "connection error" in detail.lower() or "connecterror" in detail.lower():
        return f"无法连接 LLM 服务 {base_url}。请检查当前进程的网络权限、代理和防火墙设置。"
    return f"LLM 连通性检查失败：{detail}"


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Path):
        return str(value)
    return value


INDEX_HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>华泰 Agentic 智能问数工作台</title>
  <style>
    :root {
      --paper: #f6f7f2;
      --surface: #ffffff;
      --ink: #17201b;
      --muted: #67736b;
      --line: #d8ded6;
      --line-strong: #b9c4bb;
      --jade: #246f5b;
      --blue: #2b5793;
      --amber: #a86518;
      --red: #a23a3a;
      --violet: #5b4a8b;
      --code: #101815;
      --shadow: 0 18px 45px rgba(23, 32, 27, 0.10);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      color: var(--ink);
      background:
        linear-gradient(90deg, rgba(36,111,91,0.06) 1px, transparent 1px),
        linear-gradient(0deg, rgba(43,87,147,0.05) 1px, transparent 1px),
        var(--paper);
      background-size: 28px 28px;
      font-family: "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
      letter-spacing: 0;
    }

    button, textarea, select, input {
      font: inherit;
    }

    button:focus-visible, textarea:focus-visible, select:focus-visible, input:focus-visible {
      outline: 3px solid rgba(36,111,91,0.28);
      outline-offset: 2px;
    }

    .shell {
      min-height: 100vh;
      padding: 24px;
    }

    .topbar {
      display: grid;
      grid-template-columns: minmax(280px, 1fr) auto;
      gap: 16px;
      align-items: end;
      padding-bottom: 18px;
      border-bottom: 1px solid var(--line-strong);
    }

    .brand h1 {
      margin: 0;
      font-size: clamp(24px, 3.2vw, 42px);
      line-height: 1.05;
      font-weight: 750;
    }

    .brand p {
      margin: 8px 0 0;
      color: var(--muted);
      font-size: 14px;
    }

    .status-strip {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: flex-end;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      min-height: 32px;
      padding: 0 10px;
      border: 1px solid var(--line-strong);
      background: rgba(255,255,255,0.74);
      color: var(--ink);
      font-size: 12px;
      font-weight: 650;
      white-space: nowrap;
    }

    .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--muted);
    }

    .dot.ok { background: var(--jade); }
    .dot.warn { background: var(--amber); }
    .dot.fail { background: var(--red); }

    .workspace {
      display: grid;
      grid-template-columns: minmax(300px, 380px) minmax(0, 1fr);
      gap: 18px;
      padding-top: 18px;
      align-items: start;
    }

    .panel {
      background: rgba(255,255,255,0.92);
      border: 1px solid var(--line);
      box-shadow: var(--shadow);
    }

    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      min-height: 48px;
      padding: 0 16px;
      border-bottom: 1px solid var(--line);
    }

    .panel-header h2 {
      margin: 0;
      font-size: 15px;
      font-weight: 760;
    }

    .panel-body {
      padding: 16px;
    }

    .field {
      display: grid;
      gap: 8px;
      margin-bottom: 14px;
    }

    label, .label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 720;
      text-transform: uppercase;
    }

    textarea, select, input[type="number"] {
      width: 100%;
      border: 1px solid var(--line-strong);
      background: #fff;
      color: var(--ink);
    }

    textarea {
      min-height: 132px;
      resize: vertical;
      padding: 12px;
      line-height: 1.55;
    }

    select, input[type="number"] {
      min-height: 38px;
      padding: 0 10px;
    }

    .segmented {
      display: grid;
      grid-template-columns: 1fr 1fr;
      border: 1px solid var(--line-strong);
      background: #eef2ec;
      min-height: 40px;
    }

    .segmented button {
      border: 0;
      background: transparent;
      color: var(--muted);
      cursor: pointer;
      font-weight: 760;
    }

    .segmented button.active {
      background: var(--ink);
      color: #fff;
    }

    .mode-control {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 8px;
      align-items: stretch;
    }

    .test-llm {
      min-width: 92px;
      min-height: 40px;
      white-space: nowrap;
    }

    .llm-test-result {
      min-height: 30px;
      margin-top: 8px;
      padding: 7px 9px;
      border-left: 3px solid var(--line-strong);
      background: #f5f7f5;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
      overflow-wrap: anywhere;
    }

    .llm-test-result.ok {
      border-left-color: var(--jade);
      color: var(--jade);
      background: #f4faf7;
    }

    .llm-test-result.fail {
      border-left-color: var(--red);
      color: var(--red);
      background: #fff6f6;
    }

    .sample-list {
      display: grid;
      gap: 7px;
      max-height: 245px;
      overflow: auto;
      padding-right: 3px;
    }

    .sample-button {
      width: 100%;
      border: 1px solid var(--line);
      background: #fff;
      padding: 10px;
      text-align: left;
      cursor: pointer;
    }

    .sample-button:hover {
      border-color: var(--jade);
      background: #f7fbf8;
    }

    .sample-id {
      color: var(--blue);
      font-size: 12px;
      font-weight: 800;
    }

    .sample-text {
      display: block;
      margin-top: 4px;
      font-size: 13px;
      line-height: 1.35;
    }

    .action-row {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      align-items: center;
    }

    .primary {
      min-height: 42px;
      border: 0;
      background: var(--jade);
      color: #fff;
      padding: 0 16px;
      cursor: pointer;
      font-weight: 800;
    }

    .primary:disabled {
      opacity: 0.55;
      cursor: wait;
    }

    .ghost {
      min-height: 36px;
      border: 1px solid var(--line-strong);
      background: #fff;
      color: var(--ink);
      cursor: pointer;
      padding: 0 12px;
      font-weight: 700;
    }

    .checkline {
      display: flex;
      gap: 8px;
      align-items: flex-start;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }

    .scoreboard {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 14px;
    }

    .metric {
      min-height: 80px;
      background: var(--surface);
      border: 1px solid var(--line);
      padding: 12px;
    }

    .metric strong {
      display: block;
      font-size: 24px;
      line-height: 1;
      font-family: Consolas, "Cascadia Mono", monospace;
      color: var(--ink);
    }

    .metric span {
      display: block;
      margin-top: 8px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 720;
    }

    .tabs {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      padding: 10px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.78);
      margin-bottom: 12px;
    }

    .tab {
      border: 0;
      background: transparent;
      color: var(--muted);
      min-height: 34px;
      padding: 0 12px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 760;
    }

    .tab.active {
      background: var(--blue);
      color: #fff;
    }

    .execution-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      min-height: 58px;
      margin-bottom: 12px;
      padding: 8px 10px 8px 14px;
      border: 1px solid var(--line-strong);
      border-left: 4px solid var(--jade);
      background: #f4faf7;
    }

    .execution-state {
      display: flex;
      align-items: center;
      gap: 9px;
      min-width: 0;
      font-size: 13px;
      font-weight: 760;
    }

    .execution-state .dot {
      flex: 0 0 auto;
    }

    [hidden] {
      display: none !important;
    }

    .content-panel {
      min-height: 510px;
      background: rgba(255,255,255,0.94);
      border: 1px solid var(--line);
      box-shadow: var(--shadow);
      padding: 16px;
      overflow: hidden;
    }

    .answer {
      border-left: 4px solid var(--jade);
      padding: 12px 14px;
      background: #f2f8f4;
      line-height: 1.55;
      margin-bottom: 14px;
      font-weight: 650;
    }

    .error {
      border-left-color: var(--red);
      background: #fff4f2;
      color: var(--red);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      background: #fff;
    }

    th, td {
      border-bottom: 1px solid var(--line);
      padding: 9px 10px;
      text-align: left;
      vertical-align: top;
      overflow-wrap: anywhere;
    }

    th {
      color: var(--muted);
      background: #f4f6f1;
      font-size: 12px;
      font-weight: 800;
    }

    pre, code {
      font-family: Consolas, "Cascadia Mono", "Courier New", monospace;
    }

    pre {
      margin: 0;
      max-height: 560px;
      overflow: auto;
      padding: 14px;
      background: var(--code);
      color: #dff4e8;
      line-height: 1.48;
      font-size: 12px;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }

    .split {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 12px;
    }

    .mini-title {
      margin: 0 0 8px;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      font-weight: 800;
    }

    .empty {
      display: grid;
      place-items: center;
      min-height: 360px;
      color: var(--muted);
      border: 1px dashed var(--line-strong);
      background: rgba(255,255,255,0.55);
      text-align: center;
      padding: 24px;
    }

    @media (max-width: 980px) {
      .workspace, .topbar, .split {
        grid-template-columns: 1fr;
      }
      .status-strip {
        justify-content: flex-start;
      }
      .scoreboard {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }

    @media (max-width: 560px) {
      .shell {
        padding: 14px;
      }
      .scoreboard {
        grid-template-columns: 1fr;
      }
      .action-row {
        grid-template-columns: 1fr;
      }
      .execution-bar {
        align-items: stretch;
        flex-direction: column;
      }
      .execution-bar .primary {
        width: 100%;
      }
      .mode-control {
        grid-template-columns: 1fr;
      }
      .test-llm {
        width: 100%;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header class="topbar">
      <div class="brand">
        <h1>华泰 Agentic 智能问数工作台</h1>
        <p>自然语言 -> 元数据检索 -> SQL 规划 -> 安全围栏 -> 真实数据库结果</p>
      </div>
      <div class="status-strip" id="statusStrip"></div>
    </header>

    <main class="workspace">
      <aside class="panel">
        <div class="panel-header">
          <h2>查询控制</h2>
          <button class="ghost" id="clearBtn" type="button">清空</button>
        </div>
        <div class="panel-body">
          <div class="field">
            <span class="label">SQL 模式</span>
            <div class="mode-control">
              <div class="segmented" role="tablist" aria-label="SQL mode">
                <button type="button" class="active" data-mode="demo">Demo</button>
                <button type="button" data-mode="llm">LLM</button>
              </div>
              <button class="ghost test-llm" id="testLlmBtn" type="button">测试 LLM</button>
            </div>
            <div class="llm-test-result" id="llmTestResult" role="status" aria-live="polite" hidden></div>
          </div>

          <div class="field">
            <label for="questionInput">问题</label>
            <textarea id="questionInput">学历本科以上的男性客户，年龄超过50岁的有多少个？</textarea>
          </div>

          <div class="field">
            <label for="previewInput">预览行数</label>
            <input id="previewInput" type="number" min="1" max="50" value="5" />
          </div>

          <label class="checkline" id="cloudAckLine">
            <input type="checkbox" id="cloudAck" />
            <span>允许云端 LLM 接收问题、元数据上下文和结果摘要</span>
          </label>

          <div class="field" style="margin-top:14px;">
            <button class="primary" id="runBtn" type="button">生成 SQL</button>
          </div>

          <div class="field">
            <span class="label">官方样例</span>
            <div class="sample-list" id="sampleList"></div>
          </div>
        </div>
      </aside>

      <section>
        <div class="scoreboard" id="scoreboard">
          <div class="metric"><strong>-</strong><span>返回行数</span></div>
          <div class="metric"><strong>-</strong><span>SQL 执行耗时</span></div>
          <div class="metric"><strong>-</strong><span>SQL 校验</span></div>
        </div>

        <nav class="tabs" id="tabs" aria-label="result tabs">
          <button class="tab active" data-tab="result">结果</button>
          <button class="tab" data-tab="sql">SQL</button>
        </nav>

        <div class="execution-bar" id="executionBar" hidden>
          <div class="execution-state">
            <span class="dot ok"></span>
            <span id="executionStateText">SQL 已生成并通过校验</span>
          </div>
          <button class="primary" id="executeBtn" type="button">执行 SQL</button>
        </div>

        <div class="content-panel" id="contentPanel">
          <div class="empty">选择样例或输入问题后生成 SQL。</div>
        </div>
      </section>
    </main>
  </div>

  <script>
    const app = {
      mode: 'demo',
      activeTab: 'result',
      examples: [],
      health: null,
      last: null,
      phase: 'idle',
      executionToken: '',
      llmHealth: null,
      llmChecking: false
    };

    const $ = (id) => document.getElementById(id);
    const WEB_QUERY_TIMEOUT_MS = 200000;

    function esc(value) {
      return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
    }

    async function getJson(url) {
      const res = await fetch(url);
      if (!res.ok) throw new Error(await res.text());
      return res.json();
    }

    async function postJson(url, payload, timeoutMs = WEB_QUERY_TIMEOUT_MS) {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), timeoutMs);
      try {
        const res = await fetch(url, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload),
          signal: controller.signal
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Request failed');
        return data;
      } finally {
        clearTimeout(timer);
      }
    }

    async function init() {
      wireEvents();
      app.health = await getJson('/api/health');
      app.examples = (await getJson('/api/examples')).examples || [];
      renderStatus();
      renderSamples();
      renderContent();
    }

    function wireEvents() {
      document.querySelectorAll('[data-mode]').forEach(button => {
        button.addEventListener('click', async () => {
          app.mode = button.dataset.mode;
          document.querySelectorAll('[data-mode]').forEach(item => item.classList.toggle('active', item === button));
          resetQueryState();
          renderStatus();
          if (app.mode === 'llm') await checkLlmHealth();
        });
      });

      document.querySelectorAll('[data-tab]').forEach(button => {
        button.addEventListener('click', () => {
          setActiveTab(button.dataset.tab);
          renderContent();
        });
      });

      $('runBtn').addEventListener('click', prepareQuery);
      $('executeBtn').addEventListener('click', executeQuery);
      $('testLlmBtn').addEventListener('click', () => {
        checkLlmHealth({force: true, announce: true});
      });
      $('questionInput').addEventListener('input', () => {
        if (app.last || app.executionToken) resetQueryState();
      });
      $('clearBtn').addEventListener('click', () => {
        $('questionInput').value = '';
        resetQueryState();
      });
    }

    function setActiveTab(tab) {
      app.activeTab = tab;
      document.querySelectorAll('[data-tab]').forEach(item => {
        item.classList.toggle('active', item.dataset.tab === tab);
      });
    }

    function resetQueryState() {
      app.last = null;
      app.phase = 'idle';
      app.executionToken = '';
      setActiveTab('result');
      renderExecutionBar();
      renderScoreboard();
      renderContent();
    }

    function renderStatus() {
      const h = app.health || {};
      const cloud = app.mode === 'llm' && h.llm_cloud;
      const modelKind = app.mode !== 'llm'
        ? 'ok'
        : app.llmChecking
          ? 'warn'
          : app.llmHealth?.ok === true
            ? 'ok'
            : app.llmHealth?.ok === false
              ? 'fail'
              : cloud ? 'warn' : 'ok';
      const modelValue = app.mode !== 'llm'
        ? 'demo'
        : app.llmChecking
          ? '检查中'
          : app.llmHealth?.ok === false
            ? '不可用'
            : (h.llm_model || '-');
      $('cloudAckLine').style.display = app.mode === 'llm' && h.llm_cloud ? 'flex' : 'none';
      $('statusStrip').innerHTML = [
        statusPill('LangGraph', h.langgraph_available ? 'ok' : 'fail', h.langgraph_available ? 'ON' : 'OFF'),
        statusPill('模型', modelKind, modelValue),
        statusPill('数据库', 'ok', 'DuckDB'),
        statusPill('样例', 'ok', `${h.demo_cases || 0} 题`)
      ].join('');
    }

    async function checkLlmHealth({force = false, announce = false} = {}) {
      const testBtn = $('testLlmBtn');
      app.llmChecking = true;
      if (announce) {
        testBtn.disabled = true;
        testBtn.textContent = '测试中';
        $('llmTestResult').hidden = true;
      }
      renderStatus();
      try {
        const endpoint = force ? '/api/llm/health?force=1' : '/api/llm/health';
        app.llmHealth = await getJson(endpoint);
        if (announce) renderLlmTestResult(app.llmHealth);
        if (!app.llmHealth.ok && !announce) {
          app.last = {error: app.llmHealth.error || 'LLM 服务不可用。'};
          renderContent();
        }
        return Boolean(app.llmHealth.ok);
      } catch (err) {
        app.llmHealth = {ok: false, error: err.message};
        if (announce) {
          renderLlmTestResult(app.llmHealth);
        } else {
          app.last = {error: `LLM 连通性检查失败：${err.message}`};
          renderContent();
        }
        return false;
      } finally {
        app.llmChecking = false;
        if (announce) {
          testBtn.disabled = false;
          testBtn.textContent = '测试 LLM';
        }
        renderStatus();
      }
    }

    function renderLlmTestResult(result) {
      const panel = $('llmTestResult');
      panel.hidden = false;
      panel.className = `llm-test-result ${result.ok ? 'ok' : 'fail'}`;
      panel.textContent = result.ok
        ? `已连接 ${result.model || 'LLM'} · ${Number(result.elapsed_ms || 0).toFixed(0)} ms`
        : (result.error || 'LLM 服务不可用。');
    }

    function statusPill(label, kind, value) {
      return `<span class="pill"><span class="dot ${kind}"></span>${esc(label)} · ${esc(value)}</span>`;
    }

    function renderSamples() {
      $('sampleList').innerHTML = app.examples.map(example => `
        <button class="sample-button" type="button" data-qid="${esc(example.id)}">
          <span class="sample-id">${esc(example.id)} · ${esc(example.scenario || '样例')}</span>
          <span class="sample-text">${esc(example.question)}</span>
        </button>
      `).join('');
      document.querySelectorAll('[data-qid]').forEach(button => {
        button.addEventListener('click', () => {
          const example = app.examples.find(item => item.id === button.dataset.qid);
          if (!example) return;
          resetQueryState();
          $('questionInput').value = example.question;
          $('questionInput').dataset.queryId = example.id;
        });
      });
    }

    async function prepareQuery() {
      const runBtn = $('runBtn');
      runBtn.disabled = true;
      runBtn.textContent = '生成中';
      const question = $('questionInput').value.trim();
      const matched = app.examples.find(item => item.question === question);
      const queryId = matched ? matched.id : '';
      const timeoutMs = Math.round((Number(app.health.web_case_timeout_seconds || 180) + 20) * 1000);
      app.phase = 'generating';
      app.executionToken = '';
      renderExecutionBar();
      try {
        const payload = {
          question,
          query_id: queryId,
          sql_mode: app.mode,
          preview_limit: Number($('previewInput').value || 5),
          allow_cloud_llm: $('cloudAck').checked
        };
        const response = await postJson('/api/query/prepare', payload, timeoutMs);
        if (!response.ok) {
          app.last = {error: response.error};
          app.phase = 'idle';
        } else {
          app.last = response.state;
          app.executionToken = response.execution_token || '';
          app.phase = response.ready_to_execute ? 'prepared' : 'idle';
          setActiveTab(response.ready_to_execute ? 'sql' : 'result');
        }
      } catch (err) {
        app.phase = 'idle';
        app.last = {
          error: err.name === 'AbortError'
            ? `SQL 生成超过 ${Math.round(timeoutMs / 1000)} 秒仍未完成，请稍后重试。`
            : err.message
        };
      } finally {
        runBtn.disabled = false;
        runBtn.textContent = '生成 SQL';
        renderExecutionBar();
        renderScoreboard();
        renderContent();
      }
    }

    async function executeQuery() {
      if (!app.executionToken) return;
      const executeBtn = $('executeBtn');
      executeBtn.disabled = true;
      executeBtn.textContent = '执行中';
      app.phase = 'executing';
      renderExecutionBar();
      const timeoutMs = Math.round((Number(app.health.web_case_timeout_seconds || 180) + 20) * 1000);
      try {
        const response = await postJson('/api/query/execute', {
          execution_token: app.executionToken
        }, timeoutMs);
        app.executionToken = '';
        if (!response.ok) {
          app.last = {error: response.error};
          app.phase = 'idle';
        } else {
          app.last = response.state;
          app.phase = 'completed';
          setActiveTab('result');
        }
      } catch (err) {
        app.executionToken = '';
        app.phase = 'idle';
        app.last = {
          error: err.name === 'AbortError'
            ? `执行请求超过 ${Math.round(timeoutMs / 1000)} 秒仍未完成，请重新生成 SQL。`
            : err.message
        };
      } finally {
        executeBtn.disabled = false;
        executeBtn.textContent = '执行 SQL';
        renderExecutionBar();
        renderScoreboard();
        renderContent();
      }
    }

    function renderExecutionBar() {
      const bar = $('executionBar');
      const visible = app.phase === 'prepared' || app.phase === 'executing';
      bar.hidden = !visible;
      $('executionStateText').textContent = app.phase === 'executing'
        ? '正在执行已确认的 SQL'
        : 'SQL 已生成并通过校验';
      $('executeBtn').disabled = app.phase === 'executing';
    }

    function renderScoreboard() {
      const s = app.last || {};
      const result = s.execution_result || {};
      const validation = s.validation_report || {};
      $('scoreboard').innerHTML = [
        metric(result.row_count ?? '-', '返回行数'),
        metric(result.elapsed_ms != null ? `${Number(result.elapsed_ms).toFixed(1)} ms` : '-', 'SQL 执行耗时'),
        metric(validation.passed === true ? '通过' : validation.passed === false ? '失败' : '-', 'SQL 校验')
      ].join('');
    }

    function metric(value, label) {
      return `<div class="metric"><strong>${esc(value)}</strong><span>${esc(label)}</span></div>`;
    }

    function renderContent() {
      const panel = $('contentPanel');
      if (!app.last) {
        panel.innerHTML = `<div class="empty">选择样例或输入问题后生成 SQL。</div>`;
        return;
      }
      if (app.last.error) {
        panel.innerHTML = `<div class="answer error">${esc(app.last.error)}</div>`;
        return;
      }
      const renderers = {
        result: renderResult,
        sql: renderSql
      };
      panel.innerHTML = (renderers[app.activeTab] || renderResult)();
    }

    function renderResult() {
      const s = app.last;
      const result = s.execution_result || {};
      if (s.next_action === 'execute_sql' && !result.success) {
        return `<div class="empty">SQL 已就绪，尚未执行。</div>`;
      }
      return `
        <div class="answer">${esc(s.final_answer || '查询已完成。')}</div>
        ${renderTable(result.columns || [], result.preview_rows || [])}
      `;
    }

    function renderTable(columns, rows) {
      if (!columns.length) return `<div class="empty">没有可展示的结果列。</div>`;
      return `
        <table>
          <thead><tr>${columns.map(col => `<th>${esc(col)}</th>`).join('')}</tr></thead>
          <tbody>
            ${rows.map(row => `<tr>${columns.map((_, idx) => `<td>${esc(row[idx])}</td>`).join('')}</tr>`).join('')}
          </tbody>
        </table>
      `;
    }

    function renderSql() {
      const s = app.last;
      const plan = JSON.stringify(s.sql_plan || {}, null, 2);
      return `
        <div class="split">
          <section>
            <p class="mini-title">SQL Plan</p>
            <pre>${esc(plan)}</pre>
          </section>
          <section>
            <p class="mini-title">Candidate SQL</p>
            <pre>${esc(s.candidate_sql || '')}</pre>
          </section>
        </div>
      `;
    }

    init().catch(err => {
      $('contentPanel').innerHTML = `<div class="answer error">${esc(err.message)}</div>`;
    });
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
