# Agent Evaluation Report

- SQL mode: `llm`
- Total cases: 1
- Agent completed rate: 0/1 (0.00%)
- Candidate SQL executable rate: 0/1 (0.00%)
- Exact result match rate: 0/1 (0.00%)
- Semantic result match rate: 0/1 (0.00%)
- Row count match rate: 0/1 (0.00%)
- Average execution elapsed: 0.00 ms
- SQL generation attempts: 3
- Total SQL generation elapsed: 265037.95 ms
- Average SQL generation attempt elapsed: 88345.98 ms
- LLM calls: 2
- LLM total tokens: 18390

| Query ID | Completed | Candidate SQL | Semantic | Strict Exact | Rows | Semantic Schema | SQL Gen Attempts | SQL Gen ms | Error Tags |
|----------|-----------|---------------|----------|--------------|------|-----------------|------------------|------------|------------|
| a004 | N | N | N | N | 0/14 | N | 3 | 265037.95 | no_candidate_sql, candidate_sql_execution_failed, sql_validation_failed, row_count_mismatch, missing_output_column |

## Case Details

### a004

- Question: 区域负责人希望做一张营业部经营对比表。请以2026年5月31日客户归属为准，以营业部全部客户作为统计母集，计算每个营业部的客户数、2026年3月31日期末总资产、一季度有交易金额的活跃客户率、一季度买卖交易额、佣金及费用合计、资金净流入和期末持仓市值。交易或资金记录不存在时按0计算。最后在每个分公司内部按照期末总资产从高到低进行排名，只返回总资产最高的前3个营业部；同一分公司内并列时使用dense rank，不要强行打散并列名次。
- Executable: N
- Agent completed: N
- Semantic result match: N
- Exact match: N
- Standard rows: 14
- Agent rows: 0
- Standard columns: `['up_org_name', 'org_name', 'customer_count', 'total_asset', 'active_customer_rate', 'turnover', 'total_fee', 'net_inflow', 'holding_market_value', 'asset_rank_in_company']`
- Agent columns: `[]`
- Semantic column mapping: `{}`
- Error type: `sql_validation_failed`
- Error tags: `['no_candidate_sql', 'candidate_sql_execution_failed', 'sql_validation_failed', 'row_count_mismatch', 'missing_output_column']`
- Final answer: 查询未能自动完成，已进入人工复核路径。原因：SQL is empty.; Only SELECT or WITH ... SELECT statements are allowed.
- Thread id: `eval:p1p2-a004-smoke3-20260731:r1:a004`
- SQL generation attempts: 3
- SQL generation elapsed: 265037.95 ms
- SQL plan: `{}`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> repair_sql -> validate_sql -> repair_sql -> validate_sql -> human_review_or_explain -> persist_state`

SQL generation timeline:

| Attempt | Type | Status | Started UTC | Completed UTC | Elapsed ms | Model |
|---------|------|--------|-------------|---------------|------------|-------|
| 1 | initial | failed | 2026-07-31T14:34:44.132084+00:00 | 2026-07-31T14:35:49.649408+00:00 | 65517.78 |  |
| 2 | repair | failed | 2026-07-31T14:35:49.651037+00:00 | 2026-07-31T14:38:03.899240+00:00 | 134248.45 |  |
| 3 | repair | failed | 2026-07-31T14:38:03.899240+00:00 | 2026-07-31T14:39:09.171973+00:00 | 65271.72 |  |

SQL attempt 1 (initial):

```sql

```

SQL attempt 2 (repair):

```sql

```

SQL attempt 3 (repair):

```sql

```

Final candidate SQL:

```sql

```
