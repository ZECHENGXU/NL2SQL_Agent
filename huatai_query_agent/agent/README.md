# Agent M1 Skeleton

This module implements the first runnable Agent skeleton for the Huatai Text-to-SQL prototype.

## Current scope

- Runs the documented LangGraph-style node flow.
- Uses deterministic matching from the 7 official demo questions to standard DuckDB SQL.
- Executes SQL against `huatai_query_agent/data/cust_data.duckdb`.
- Returns trace, SQL metadata context, result preview, row count, and final answer.
- Uses a fallback runner when `langgraph` is not installed; after installing requirements, `QueryAgent` will compile a `StateGraph`.

## Run

From the project root:

```powershell
python -m huatai_query_agent.agent.run_agent --all --preview 2
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

## Next implementation step

Replace deterministic demo SQL matching with:

1. `HybridMetadataRetriever` for YAML + Qdrant context retrieval.
2. Local OpenAI-compatible model API calls for intent parsing, SQL planning, SQL generation, and SQL repair.
3. `sqlglot`-based SQL guardrail validation.
