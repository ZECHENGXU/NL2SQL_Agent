# Agent Evaluation Report

- SQL mode: `llm`
- Total cases: 1
- Agent completed rate: 0/1 (0.00%)
- Candidate SQL executable rate: 0/1 (0.00%)
- Exact result match rate: 0/1 (0.00%)
- Semantic result match rate: 0/1 (0.00%)
- Row count match rate: 0/1 (0.00%)
- Average execution elapsed: 0.00 ms
- Timed out cases: 1/1
- Average case elapsed: 49623.47 ms
- Maximum case elapsed: 49623.47 ms
- SQL generation attempts: 0
- Total SQL generation elapsed: 0.00 ms
- Average SQL generation attempt elapsed: 0.00 ms
- LLM calls: 1
- LLM total tokens: 2162

| Query ID | Completed | Timeout | Case ms | Candidate SQL | Semantic | Strict Exact | Rows | Semantic Schema | SQL Gen Attempts | SQL Gen ms | Error Tags |
|----------|-----------|---------|---------|---------------|----------|--------------|------|-----------------|------------------|------------|------------|
| s028 | N | Y | 49623.47 | N | N | N | 0/4 | N | 0 | 0.00 | case_timeout, no_candidate_sql, candidate_sql_execution_failed, row_count_mismatch, missing_output_column |

## Case Details

### s028

- Question: 2026年3月31日信用账户持仓客户按等级统计人数和持仓市值。
- Executable: N
- Agent completed: N
- Case timed out: Y
- Case elapsed: 49623.47 ms
- Case timeout: 50.00 s
- Semantic result match: N
- Exact match: N
- Standard rows: 4
- Agent rows: 0
- Standard columns: `['customer_level', 'customer_count', 'credit_market_value']`
- Agent columns: `[]`
- Semantic column mapping: `{}`
- Error type: `case_timeout`
- Error tags: `['case_timeout', 'no_candidate_sql', 'candidate_sql_execution_failed', 'row_count_mismatch', 'missing_output_column']`
- Final answer: 查询在 49.94 秒单题时限内未完成，已终止本题并记录为 case_timeout。
- Thread id: `eval:p2-s028-50s-20260801:r1:s028`
- SQL generation attempts: 0
- SQL generation elapsed: 0.00 ms
- SQL plan: `{}`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> human_review_or_explain -> persist_state`

Final candidate SQL:

```sql

```
