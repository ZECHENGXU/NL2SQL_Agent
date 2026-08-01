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

- Query control: choose `demo` or `llm`, enter a question, or choose an official sample.
- SQL approval: generate and validate candidate SQL first, then execute it only after explicit confirmation.
- Result: final answer and result preview.
- SQL: SQL plan and candidate SQL.

## LLM Mode

If `.env` points to a cloud API such as DeepSeek official cloud, the page requires explicit confirmation before running `llm` mode. This is intentional because prompt metadata, question context, SQL plan, and result summaries may be sent to the configured provider.

When `llm` mode is selected, the page checks that the configured API is reachable and that the configured model exists. A failed check stops before SQL generation and reports the original connectivity or model error; it does not continue into empty-SQL validation or repair.

Click `Test LLM` beside the SQL mode selector to bypass the health cache and run a fresh connectivity and model-availability check.

## Query Workflow

1. Click `Generate SQL` to run intent parsing, metadata retrieval, SQL planning, generation, and SQL validation.
2. Review the candidate SQL in the SQL tab.
3. Click `Execute SQL` to revalidate and execute that exact server-side SQL.
