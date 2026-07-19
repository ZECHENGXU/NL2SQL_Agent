# Agent M1/M2 Prototype

This module implements the first runnable Agent prototype for the Huatai Text-to-SQL project.

## Current scope

- Runs the documented LangGraph `StateGraph` node flow when `langgraph` is installed.
- Uses deterministic matching from the 7 official demo questions to standard DuckDB SQL.
- Retrieves metadata context through `HybridMetadataRetriever` with YAML exact/keyword retrieval and Qdrant Local vector retrieval.
- Executes SQL against `huatai_query_agent/data/cust_data.duckdb`.
- Returns trace, SQL metadata context, result preview, row count, and final answer.
- Uses a fallback runner when `langgraph` is not installed.

The M2 retrieval layer uses `HashingEmbedding` as a deterministic local vector fallback. It is not a semantic embedding model; it keeps the Qdrant path executable before the local embedding API is connected.

## Run

From the project root:

```powershell
conda activate huatai-agent
```

```powershell
python -m huatai_query_agent.agent.run_agent --all --preview 2
```

If the shell has not activated Conda correctly, use the environment Python directly:

```powershell
& "E:\anaconda\envs\huatai-agent\python.exe" -m huatai_query_agent.agent.run_agent --all --preview 2
```

Run one case:

```powershell
python -m huatai_query_agent.agent.run_agent --query-id q005 --preview 5
```

Run by question text:

```powershell
python -m huatai_query_agent.agent.run_agent --question "2026年Q1交易过招商银行A股，并且在Q1末普通账户持有中国平安A股的客户有哪些？"
```

Check DeepSeek API connection:

```powershell
python -m huatai_query_agent.llm.check_connection
```

Run one case with LLM SQL generation:

```powershell
python -m huatai_query_agent.agent.run_agent --query-id q005 --sql-mode llm --preview 5
```

Run an arbitrary natural language question with LLM SQL generation:

```powershell
python -m huatai_query_agent.agent.run_agent --question "学历本科以上的男性客户，年龄超过50岁的有多少个？" --sql-mode llm --preview 5
```

Batch evaluation:

```powershell
python huatai_query_agent\evaluation\run_agent_eval.py
```

Expected M1 result:

```text
langgraph_available=True
agent_executable_rate[demo]=7/7 (100.00%)
```

## LLM Configuration

LLM settings are loaded from project `.env`:

```text
HUATAI_LLM_PROVIDER=deepseek
HUATAI_LLM_API_KEY=sk-your-key
HUATAI_LLM_BASE_URL=https://api.deepseek.com
HUATAI_LLM_MODEL=deepseek-v4-pro
HUATAI_LLM_TIMEOUT_SECONDS=60
HUATAI_LLM_TEMPERATURE=0
HUATAI_LLM_MAX_TOKENS=4096
```

`.env` is ignored by git. Use `.env.example` as the shareable template.

## Next implementation step

Upgrade the current LLM-assisted path into a stronger Text-to-SQL Agent:

1. Replace hashing vectors with a local semantic embedding API.
2. Split intent parsing, SQL planning, SQL generation, and SQL repair into separately evaluated LLM nodes.
3. Add metric-level SQL rule validation beyond table whitelist and read-only checks.
4. Add evaluation cases beyond the 7 official examples.
