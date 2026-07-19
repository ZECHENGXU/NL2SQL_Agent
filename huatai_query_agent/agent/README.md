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

Batch evaluation:

```powershell
python huatai_query_agent\evaluation\run_agent_eval.py
```

Expected M1 result:

```text
langgraph_available=True
agent_m1_executable_rate=7/7 (100.00%)
```

## Next implementation step

Upgrade the deterministic M1 path into an LLM-assisted Text-to-SQL Agent:

1. Replace hashing vectors with a local semantic embedding API.
2. Add local OpenAI-compatible model API calls for intent parsing, SQL planning, SQL generation, and SQL repair.
3. Add `sqlglot`-based SQL guardrail validation.
4. Add evaluation cases beyond the 7 official examples.
