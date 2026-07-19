from __future__ import annotations

import argparse
import atexit
import json
import os
import sys
import traceback
import webbrowser
from decimal import Decimal
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from huatai_query_agent.agent.demo_cases import DemoCaseRepository
from huatai_query_agent.agent.graph import LANGGRAPH_AVAILABLE, QueryAgent
from huatai_query_agent.llm.config import LlmSettings
from huatai_query_agent.retrieval.hybrid_retriever import HybridMetadataRetriever


REPORT_DIR = PROJECT_DIR / "huatai_query_agent" / "evaluation"
AGENT_REPORT = REPORT_DIR / "agent_eval_report.md"
GUARDRAIL_REPORT = REPORT_DIR / "guardrail_eval_report.md"


class DemoRuntime:
    def __init__(self) -> None:
        self.repo = DemoCaseRepository()
        self.retriever = HybridMetadataRetriever()
        self.agents: dict[tuple[str, int], QueryAgent] = {}

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

    def close(self) -> None:
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
        path = urlparse(self.path).path
        if path == "/":
            self._send_html(INDEX_HTML)
        elif path == "/api/health":
            self._send_json(self._health())
        elif path == "/api/examples":
            self._send_json(self._examples())
        elif path == "/api/reports":
            self._send_json(self._reports())
        else:
            self._send_json({"error": f"Not found: {path}"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path != "/api/query":
            self._send_json({"error": f"Not found: {path}"}, status=HTTPStatus.NOT_FOUND)
            return

        try:
            payload = self._read_json()
            response = self._run_query(payload)
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
            "demo_cases": len(get_runtime().repo.list_cases()),
            "agent_report_exists": AGENT_REPORT.exists(),
            "guardrail_report_exists": GUARDRAIL_REPORT.exists(),
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

    def _reports(self) -> dict[str, Any]:
        return {
            "ok": True,
            "agent_report": _read_report(AGENT_REPORT),
            "guardrail_report": _read_report(GUARDRAIL_REPORT),
        }

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

        agent = get_runtime().get_agent(sql_mode=sql_mode, preview_limit=preview_limit)
        state = agent.run(question=question, query_id=query_id, thread_id="web-demo")
        return {"ok": True, "state": _jsonable(state)}

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


def _read_report(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "path": str(path), "content": ""}
    return {
        "exists": True,
        "path": str(path),
        "content": path.read_text(encoding="utf-8"),
    }


def _is_cloud_url(base_url: str) -> bool:
    lowered = base_url.lower()
    return not (
        "127.0.0.1" in lowered
        or "localhost" in lowered
        or "0.0.0.0" in lowered
        or "host.docker.internal" in lowered
    )


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
      grid-template-columns: repeat(4, minmax(0, 1fr));
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

    .trace {
      display: grid;
      gap: 0;
    }

    .trace-item {
      display: grid;
      grid-template-columns: 28px minmax(0, 1fr);
      gap: 10px;
      min-height: 48px;
    }

    .trace-mark {
      position: relative;
      display: grid;
      justify-items: center;
    }

    .trace-mark::after {
      content: "";
      position: absolute;
      top: 18px;
      bottom: -18px;
      width: 1px;
      background: var(--line-strong);
    }

    .trace-item:last-child .trace-mark::after {
      display: none;
    }

    .trace-dot {
      z-index: 1;
      display: grid;
      place-items: center;
      width: 24px;
      height: 24px;
      background: var(--jade);
      color: #fff;
      font-size: 11px;
      font-weight: 800;
    }

    .trace-dot.failed, .trace-dot.blocked { background: var(--red); }
    .trace-dot.fallback { background: var(--amber); }

    .trace-body {
      padding: 1px 0 14px;
      border-bottom: 1px solid var(--line);
    }

    .trace-name {
      font-weight: 800;
    }

    .trace-msg {
      margin-top: 4px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.4;
    }

    .chip-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }

    .chip {
      border: 1px solid var(--line-strong);
      background: #fff;
      padding: 5px 8px;
      font-size: 12px;
      font-weight: 700;
      color: var(--ink);
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
            <div class="segmented" role="tablist" aria-label="SQL mode">
              <button type="button" class="active" data-mode="demo">Demo</button>
              <button type="button" data-mode="llm">LLM</button>
            </div>
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
            <button class="primary" id="runBtn" type="button">运行问数</button>
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
          <div class="metric"><strong>-</strong><span>执行耗时</span></div>
          <div class="metric"><strong>-</strong><span>SQL 校验</span></div>
          <div class="metric"><strong>-</strong><span>Trace 节点</span></div>
        </div>

        <nav class="tabs" id="tabs" aria-label="result tabs">
          <button class="tab active" data-tab="result">结果</button>
          <button class="tab" data-tab="sql">SQL</button>
          <button class="tab" data-tab="trace">Trace</button>
          <button class="tab" data-tab="guardrail">围栏</button>
          <button class="tab" data-tab="metadata">元数据</button>
          <button class="tab" data-tab="reports">评测报告</button>
        </nav>

        <div class="content-panel" id="contentPanel">
          <div class="empty">选择样例或输入问题后运行。</div>
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
      reports: null
    };

    const $ = (id) => document.getElementById(id);

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

    async function postJson(url, payload) {
      const res = await fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Request failed');
      return data;
    }

    async function init() {
      wireEvents();
      app.health = await getJson('/api/health');
      app.examples = (await getJson('/api/examples')).examples || [];
      app.reports = await getJson('/api/reports');
      renderStatus();
      renderSamples();
      renderContent();
    }

    function wireEvents() {
      document.querySelectorAll('[data-mode]').forEach(button => {
        button.addEventListener('click', () => {
          app.mode = button.dataset.mode;
          document.querySelectorAll('[data-mode]').forEach(item => item.classList.toggle('active', item === button));
          renderStatus();
        });
      });

      document.querySelectorAll('[data-tab]').forEach(button => {
        button.addEventListener('click', async () => {
          app.activeTab = button.dataset.tab;
          document.querySelectorAll('[data-tab]').forEach(item => item.classList.toggle('active', item === button));
          if (app.activeTab === 'reports') {
            app.reports = await getJson('/api/reports');
          }
          renderContent();
        });
      });

      $('runBtn').addEventListener('click', runQuery);
      $('clearBtn').addEventListener('click', () => {
        $('questionInput').value = '';
        app.last = null;
        renderScoreboard();
        renderContent();
      });
    }

    function renderStatus() {
      const h = app.health || {};
      const cloud = app.mode === 'llm' && h.llm_cloud;
      $('cloudAckLine').style.display = app.mode === 'llm' && h.llm_cloud ? 'flex' : 'none';
      $('statusStrip').innerHTML = [
        statusPill('LangGraph', h.langgraph_available ? 'ok' : 'fail', h.langgraph_available ? 'ON' : 'OFF'),
        statusPill('模型', cloud ? 'warn' : 'ok', app.mode === 'llm' ? (h.llm_model || '-') : 'demo'),
        statusPill('数据库', 'ok', 'DuckDB'),
        statusPill('样例', 'ok', `${h.demo_cases || 0} 题`)
      ].join('');
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
          $('questionInput').value = example.question;
          $('questionInput').dataset.queryId = example.id;
        });
      });
    }

    async function runQuery() {
      const runBtn = $('runBtn');
      runBtn.disabled = true;
      runBtn.textContent = '运行中';
      const question = $('questionInput').value.trim();
      const matched = app.examples.find(item => item.question === question);
      const queryId = matched ? matched.id : '';
      try {
        const payload = {
          question,
          query_id: queryId,
          sql_mode: app.mode,
          preview_limit: Number($('previewInput').value || 5),
          allow_cloud_llm: $('cloudAck').checked
        };
        const response = await postJson('/api/query', payload);
        if (!response.ok) {
          app.last = {error: response.error};
        } else {
          app.last = response.state;
        }
      } catch (err) {
        app.last = {error: err.message};
      } finally {
        runBtn.disabled = false;
        runBtn.textContent = '运行问数';
        renderScoreboard();
        renderContent();
      }
    }

    function renderScoreboard() {
      const s = app.last || {};
      const result = s.execution_result || {};
      const validation = s.validation_report || {};
      const trace = s.trace || [];
      $('scoreboard').innerHTML = [
        metric(result.row_count ?? '-', '返回行数'),
        metric(result.elapsed_ms != null ? `${Number(result.elapsed_ms).toFixed(1)} ms` : '-', '执行耗时'),
        metric(validation.passed === true ? '通过' : validation.passed === false ? '失败' : '-', 'SQL 校验'),
        metric(trace.length || '-', 'Trace 节点')
      ].join('');
    }

    function metric(value, label) {
      return `<div class="metric"><strong>${esc(value)}</strong><span>${esc(label)}</span></div>`;
    }

    function renderContent() {
      const panel = $('contentPanel');
      if (!app.last) {
        panel.innerHTML = `<div class="empty">选择样例或输入问题后运行。</div>`;
        return;
      }
      if (app.last.error) {
        panel.innerHTML = `<div class="answer error">${esc(app.last.error)}</div>`;
        return;
      }
      const renderers = {
        result: renderResult,
        sql: renderSql,
        trace: renderTrace,
        guardrail: renderGuardrail,
        metadata: renderMetadata,
        reports: renderReports
      };
      panel.innerHTML = (renderers[app.activeTab] || renderResult)();
    }

    function renderResult() {
      const s = app.last;
      const result = s.execution_result || {};
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

    function renderTrace() {
      const trace = app.last.trace || [];
      if (!trace.length) return `<div class="empty">暂无 Trace。</div>`;
      return `<div class="trace">${
        trace.map((event, idx) => `
          <div class="trace-item">
            <div class="trace-mark"><span class="trace-dot ${esc(event.status)}">${idx + 1}</span></div>
            <div class="trace-body">
              <div class="trace-name">${esc(event.node)} · ${esc(event.status)}</div>
              <div class="trace-msg">${esc(event.message || '')}</div>
            </div>
          </div>
        `).join('')
      }</div>`;
    }

    function renderGuardrail() {
      const validation = app.last.validation_report || {};
      const resultCheck = app.last.result_check || {};
      const checks = validation.checks || {};
      const rows = Object.keys(checks).map(key => [key, checks[key]]);
      return `
        <div class="split">
          <section>
            <p class="mini-title">SQL Guardrail</p>
            ${renderTable(['check', 'status'], rows)}
          </section>
          <section>
            <p class="mini-title">Result Check</p>
            <pre>${esc(JSON.stringify(resultCheck, null, 2))}</pre>
          </section>
        </div>
        <p class="mini-title" style="margin-top:14px;">Errors</p>
        <div class="chip-row">${(validation.errors || []).map(item => `<span class="chip">${esc(item)}</span>`).join('') || '<span class="chip">none</span>'}</div>
      `;
    }

    function renderMetadata() {
      const context = app.last.metadata_context || {};
      const ids = app.last.context_ids || context.context_ids || [];
      const chunks = context.chunks || [];
      return `
        <p class="mini-title">Context IDs</p>
        <div class="chip-row">${ids.map(id => `<span class="chip">${esc(id)}</span>`).join('') || '<span class="chip">none</span>'}</div>
        <p class="mini-title" style="margin-top:16px;">Retrieved Chunks</p>
        <pre>${esc(JSON.stringify(chunks.slice(0, 10), null, 2))}</pre>
      `;
    }

    function renderReports() {
      const reports = app.reports || {};
      const agent = reports.agent_report || {};
      const guardrail = reports.guardrail_report || {};
      return `
        <div class="split">
          <section>
            <p class="mini-title">Agent Eval</p>
            <pre>${esc(agent.exists ? agent.content : 'agent_eval_report.md not found')}</pre>
          </section>
          <section>
            <p class="mini-title">Guardrail Eval</p>
            <pre>${esc(guardrail.exists ? guardrail.content : 'guardrail_eval_report.md not found')}</pre>
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
