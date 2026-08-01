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
- Average case elapsed: 49624.96 ms
- Maximum case elapsed: 49624.96 ms
- SQL generation attempts: 0
- Total SQL generation elapsed: 0.00 ms
- Average SQL generation attempt elapsed: 0.00 ms
- LLM calls: 1
- LLM total tokens: 4005

| Query ID | Completed | Timeout | Case ms | Candidate SQL | Semantic | Strict Exact | Rows | Semantic Schema | SQL Gen Attempts | SQL Gen ms | Error Tags |
|----------|-----------|---------|---------|---------------|----------|--------------|------|-----------------|------------------|------------|------------|
| a004 | N | Y | 49624.96 | N | N | N | 0/14 | N | 0 | 0.00 | case_timeout, no_candidate_sql, candidate_sql_execution_failed, row_count_mismatch, missing_output_column |

## Case Details

### a004

- Question: 区域负责人希望做一张营业部经营对比表。请以2026年5月31日客户归属为准，以营业部全部客户作为统计母集，计算每个营业部的客户数、2026年3月31日期末总资产、一季度有交易金额的活跃客户率、一季度买卖交易额、佣金及费用合计、资金净流入和期末持仓市值。交易或资金记录不存在时按0计算。最后在每个分公司内部按照期末总资产从高到低进行排名，只返回总资产最高的前3个营业部；同一分公司内并列时使用dense rank，不要强行打散并列名次。
- Executable: N
- Agent completed: N
- Case timed out: Y
- Case elapsed: 49624.96 ms
- Case timeout: 50.00 s
- Semantic result match: N
- Exact match: N
- Standard rows: 14
- Agent rows: 0
- Standard columns: `['up_org_name', 'org_name', 'customer_count', 'total_asset', 'active_customer_rate', 'turnover', 'total_fee', 'net_inflow', 'holding_market_value', 'asset_rank_in_company']`
- Agent columns: `[]`
- Semantic column mapping: `{}`
- Error type: `case_timeout`
- Error tags: `['case_timeout', 'no_candidate_sql', 'candidate_sql_execution_failed', 'row_count_mismatch', 'missing_output_column']`
- Final answer: 查询在 49.91 秒单题时限内未完成，已终止本题并记录为 case_timeout。
- Thread id: `eval:p1p2-a004-smoke9-20260801:r1:a004`
- SQL generation attempts: 0
- SQL generation elapsed: 0.00 ms
- SQL plan: `{}`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> human_review_or_explain -> persist_state`

Final candidate SQL:

```sql

```
