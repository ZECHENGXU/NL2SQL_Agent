# Web Demo M6

This directory contains the local browser demo for the Huatai Agentic query system.

The demo uses the Python standard library HTTP server plus native HTML/CSS/JS. It does not require Streamlit, Node.js, or a frontend build step.

## Run

From the project root:

```powershell
E:\anaconda\envs\huatai-agent\python.exe -m huatai_query_agent.web.server --host 127.0.0.1 --port 8501
```

Open:

```text
http://127.0.0.1:8501
```

## Views

- Query control: choose `demo` or `llm`, enter a question, choose a demo case.
- Result: final answer and result preview.
- SQL: SQL plan and candidate SQL.
- Trace: LangGraph node execution path.
- Guardrail: SQL validation and result checks.
- Metadata: retrieved context ids and top metadata chunks.
- Reports: generated M5 agent and guardrail evaluation reports.

## LLM Mode

If `.env` points to a cloud API such as DeepSeek official cloud, the page requires explicit confirmation before running `llm` mode. This is intentional because prompt metadata, question context, SQL plan, and result summaries may be sent to the configured provider.
