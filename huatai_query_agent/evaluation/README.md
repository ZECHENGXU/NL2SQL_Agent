# Evaluation M5

This directory contains automated evaluation scripts for the Huatai Text-to-SQL Agent.

- `run_demo_queries.py`: executes all SQL blocks in `../sql/demo_queries_duckdb.sql` against the local DuckDB database and prints row counts plus previews.
- `run_agent_eval.py`: runs standard SQL and Agent SQL, compares results, and writes Markdown/CSV reports.
- `run_guardrail_eval.py`: checks SQL guardrails and hallucination suppression cases.

## Standard SQL vs Agent SQL

```powershell
python huatai_query_agent\evaluation\run_agent_eval.py --sql-mode demo --strict-result-match
```

Outputs:

- `huatai_query_agent/evaluation/agent_eval_report.md`
- `huatai_query_agent/evaluation/agent_eval_results.csv`

Key metrics:

- executable rate
- exact result match rate
- row count match rate
- column match rate
- LLM call count and token usage

Run a small LLM evaluation:

```powershell
python huatai_query_agent\evaluation\run_agent_eval.py --sql-mode llm --query-id q001 --query-id q005
```

If `HUATAI_LLM_BASE_URL` points to a cloud API, LLM evaluation sends prompt metadata and question context to that provider. For full financial-data evaluation, use an approved local OpenAI-compatible model gateway.

## Guardrail Evaluation

```powershell
python huatai_query_agent\evaluation\run_guardrail_eval.py
```

Outputs:

- `huatai_query_agent/evaluation/guardrail_eval_report.md`
- `huatai_query_agent/evaluation/guardrail_eval_results.csv`

Guardrail cases cover:

- safe read-only SQL
- DML/DDL blocking
- multi-statement blocking
- hallucinated table blocking
- hallucinated qualified field blocking
- PRAGMA/COPY blocking
