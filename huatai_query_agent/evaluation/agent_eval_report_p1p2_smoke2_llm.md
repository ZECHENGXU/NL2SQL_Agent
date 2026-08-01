# Agent Evaluation Report

- SQL mode: `llm`
- Total cases: 3
- Agent completed rate: 2/3 (66.67%)
- Candidate SQL executable rate: 3/3 (100.00%)
- Exact result match rate: 1/3 (33.33%)
- Semantic result match rate: 2/3 (66.67%)
- Row count match rate: 2/3 (66.67%)
- Average execution elapsed: 60.77 ms
- SQL generation attempts: 5
- Total SQL generation elapsed: 386750.71 ms
- Average SQL generation attempt elapsed: 77350.14 ms
- LLM calls: 12
- LLM total tokens: 124007

| Query ID | Completed | Candidate SQL | Semantic | Strict Exact | Rows | Semantic Schema | SQL Gen Attempts | SQL Gen ms | Error Tags |
|----------|-----------|---------------|----------|--------------|------|-----------------|------------------|------------|------------|
| s028 | Y | Y | Y | N | 4/4 | Y | 1 | 23525.50 | order_only_difference |
| a004 | N | Y | N | N | 16/14 | Y | 3 | 298842.32 | validator_false_positive, wrong_column_order, row_count_mismatch, semantic_value_error |
| a027 | Y | Y | Y | Y | 20/20 | Y | 1 | 64382.90 | ok |

## Case Details

### s028

- Question: 2026年3月31日信用账户持仓客户按等级统计人数和持仓市值。
- Executable: Y
- Agent completed: Y
- Semantic result match: Y
- Exact match: N
- Standard rows: 4
- Agent rows: 4
- Standard columns: `['customer_level', 'customer_count', 'credit_market_value']`
- Agent columns: `['customer_level', 'customer_count', 'credit_market_value']`
- Semantic column mapping: `{'customer_level': 'customer_level', 'customer_count': 'customer_count', 'credit_market_value': 'credit_market_value'}`
- Error type: `order_only_difference`
- Error tags: `['order_only_difference']`
- Final answer: 2026年3月31日，信用账户持仓市值大于0的客户按等级统计，共4个等级。预览数据显示：紫金理财白金卡客户14人，持仓市值23636654.57元；紫金理财金卡客户13人，持仓市值6435744.05元；紫金理财钻石卡客户9人，持仓市值65340298.56元。其余等级客户数及市值请查看完整结果。
- Thread id: `eval:p1p2-smoke2-20260731:r1:s028`
- SQL generation attempts: 1
- SQL generation elapsed: 23525.50 ms
- SQL plan: `{"target": "统计2026年3月31日信用账户持仓客户按等级的人数及持仓市值", "tables": ["ads_cust_info_d", "dwd_cust_hold_d", "dim_public"], "joins": ["ads_cust_info_d LEFT JOIN dim_public ON ads_cust_info_d.cust_lvl_cd = dim_public.code AND dim_public.code_type_id = '100'", "ads_cust_info_d INNER JOIN dwd_cust_hold_d ON ads_cust_info_d.pty_id = dwd_cust_hold_d.pty_id"], "filters": ["ads_cust_info_d.data_dt = '20260531'", "dwd_cust_hold_d.data_dt = '20260331'", "dwd_cust_hold_d.sys_source = 'fc'", "coalesce(dwd_cust_hold_d.mkt_val, 0) > 0"], "metrics": ["customer_count: COUNT(DISTINCT ads_cust_info_d.pty_id)", "credit_market_value: SUM(coalesce(dwd_cust_hold_d.mkt_val, 0))"], "population": "2026-03-31持有信用账户且持仓市值大于0的客户", "grain": ["dim_public.\"describe\" (客户等级中文描述)"], "output_columns": [{"expression": "dim_public.\"describe\"", "alias": "customer_level", "semantic_type": "customer_level", "required": true, "position": 1, "name": "customer_level", "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"expression": "COUNT(DISTINCT ads_cust_info_d.pty_id)", "alias": "customer_count", "semantic_type": "customer_count", "required": true, "position": 2, "name": "customer_count", "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"expression": "SUM(coalesce(dwd_cust_hold_d.mkt_val, 0))", "alias": "credit_market_value", "semantic_type": "credit_market_value", "required": true, "position": 3, "name": "credit_market_value", "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}], "group_by": ["dim_public.\"describe\""], "eligibility_filters": [], "snapshot_policy": {"cust_info": "20260531", "fact_table": "20260331", "ads_cust_info_d": "20260531", "dwd_cust_hold_d": "20260331"}, "missing_fact_policy": {"credit_market_value": "require_record"}, "missing_period_policy": "exclude", "dictionary_translation": ["ads_cust_info_d.cust_lvl_cd → dim_public.\"describe\" (code_type_id='100')"], "window": [], "order_by": [], "top_n": null, "expect_nonempty": true, "strategy": "llm_text_to_sql", "matched_query_id": null}`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

SQL generation timeline:

| Attempt | Type | Status | Started UTC | Completed UTC | Elapsed ms | Model |
|---------|------|--------|-------------|---------------|------------|-------|
| 1 | initial | ok | 2026-07-31T14:01:16.146456+00:00 | 2026-07-31T14:01:39.673060+00:00 | 23525.50 | deepseek-v4-pro |

SQL attempt 1 (initial):

```sql
SELECT dim_public."describe" AS customer_level, COUNT(DISTINCT ads_cust_info_d.pty_id) AS customer_count, SUM(COALESCE(dwd_cust_hold_d.mkt_val, 0)) AS credit_market_value FROM ads_cust_info_d LEFT JOIN dim_public ON ads_cust_info_d.cust_lvl_cd = dim_public.code AND dim_public.code_type_id = '100' INNER JOIN dwd_cust_hold_d ON ads_cust_info_d.pty_id = dwd_cust_hold_d.pty_id WHERE ads_cust_info_d.data_dt = '20260531' AND dwd_cust_hold_d.data_dt = '20260331' AND dwd_cust_hold_d.sys_source = 'fc' AND COALESCE(dwd_cust_hold_d.mkt_val, 0) > 0 GROUP BY dim_public."describe"
```

Final candidate SQL:

```sql
SELECT dim_public."describe" AS customer_level, COUNT(DISTINCT ads_cust_info_d.pty_id) AS customer_count, SUM(COALESCE(dwd_cust_hold_d.mkt_val, 0)) AS credit_market_value FROM ads_cust_info_d LEFT JOIN dim_public ON ads_cust_info_d.cust_lvl_cd = dim_public.code AND dim_public.code_type_id = '100' INNER JOIN dwd_cust_hold_d ON ads_cust_info_d.pty_id = dwd_cust_hold_d.pty_id WHERE ads_cust_info_d.data_dt = '20260531' AND dwd_cust_hold_d.data_dt = '20260331' AND dwd_cust_hold_d.sys_source = 'fc' AND COALESCE(dwd_cust_hold_d.mkt_val, 0) > 0 GROUP BY dim_public."describe"
```

### a004

- Question: 区域负责人希望做一张营业部经营对比表。请以2026年5月31日客户归属为准，以营业部全部客户作为统计母集，计算每个营业部的客户数、2026年3月31日期末总资产、一季度有交易金额的活跃客户率、一季度买卖交易额、佣金及费用合计、资金净流入和期末持仓市值。交易或资金记录不存在时按0计算。最后在每个分公司内部按照期末总资产从高到低进行排名，只返回总资产最高的前3个营业部；同一分公司内并列时使用dense rank，不要强行打散并列名次。
- Executable: Y
- Agent completed: N
- Semantic result match: N
- Exact match: N
- Standard rows: 14
- Agent rows: 16
- Standard columns: `['up_org_name', 'org_name', 'customer_count', 'total_asset', 'active_customer_rate', 'turnover', 'total_fee', 'net_inflow', 'holding_market_value', 'asset_rank_in_company']`
- Agent columns: `['up_org_name', 'org_name', 'customer_count', 'total_asset', 'active_customer_rate', 'turnover', 'total_fee', 'net_inflow', 'holding_market_value', 'asset_rank_in_company']`
- Semantic column mapping: `{'up_org_name': 'up_org_name', 'org_name': 'org_name', 'customer_count': 'customer_count', 'total_asset': 'total_asset', 'active_customer_rate': 'active_customer_rate', 'turnover': 'turnover', 'total_fee': 'total_fee', 'net_inflow': 'net_inflow', 'holding_market_value': 'holding_market_value', 'asset_rank_in_company': 'asset_rank_in_company'}`
- Error type: `validator_false_positive`
- Error tags: `['validator_false_positive', 'wrong_column_order', 'row_count_mismatch', 'semantic_value_error']`
- Final answer: 查询未能自动完成，已进入人工复核路径。原因：Projection contract column order mismatch: expected ['up_org_name', 'org_name', 'customer_count', 'total_asset', 'active_customer_rate', 'turnover', 'total_fee', 'net_inflow', 'holding_market_value', 'asset_rank_in_company', 'up_org_name', 'org_name', 'customer_count', 'total_asset', 'active_customer_rate', 'turnover', 'total_fee', 'net_inflow', 'holding_market_value', 'asset_rank_in_company'], got ['up_org_name', 'org_name', 'customer_count', 'total_asset', 'active_customer_rate', 'turnover', 'total_fee', 'net_inflow', 'holding_market_value', 'asset_rank_in_company'].
- Thread id: `eval:p1p2-smoke2-20260731:r1:a004`
- SQL generation attempts: 3
- SQL generation elapsed: 298842.32 ms
- SQL plan: `{"output_columns": [{"name": "up_org_name", "alias": "up_org_name", "semantic_type": "up_org_name", "required": true, "position": 1, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "org_name", "alias": "org_name", "semantic_type": "org_name", "required": true, "position": 2, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "customer_count", "alias": "customer_count", "semantic_type": "customer_count", "required": true, "position": 3, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "total_asset", "alias": "total_asset", "semantic_type": "total_asset", "required": true, "position": 4, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "active_customer_rate", "alias": "active_customer_rate", "semantic_type": "active_customer_rate", "required": true, "position": 5, "alias_strict": false, "numeric_tolerance": {"atol": 1e-07, "rtol": 1e-06}}, {"name": "turnover", "alias": "turnover", "semantic_type": "turnover", "required": true, "position": 6, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "total_fee", "alias": "total_fee", "semantic_type": "total_fee", "required": true, "position": 7, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "net_inflow", "alias": "net_inflow", "semantic_type": "net_inflow", "required": true, "position": 8, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "holding_market_value", "alias": "holding_market_value", "semantic_type": "holding_market_value", "required": true, "position": 9, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "asset_rank_in_company", "alias": "asset_rank_in_company", "semantic_type": "asset_rank_in_company", "required": true, "position": 10, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "up_org_name", "alias": "up_org_name", "required": true, "semantic_type": "up_org_name", "position": 11, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "org_name", "alias": "org_name", "required": true, "semantic_type": "org_name", "position": 12, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "customer_count", "alias": "customer_count", "required": true, "semantic_type": "customer_count", "position": 13, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "total_asset", "alias": "total_asset", "required": true, "semantic_type": "total_asset", "position": 14, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "active_customer_rate", "alias": "active_customer_rate", "required": true, "semantic_type": "active_customer_rate", "position": 15, "alias_strict": false, "numeric_tolerance": {"atol": 1e-07, "rtol": 1e-06}}, {"name": "turnover", "alias": "turnover", "required": true, "semantic_type": "turnover", "position": 16, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "total_fee", "alias": "total_fee", "required": true, "semantic_type": "total_fee", "position": 17, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "net_inflow", "alias": "net_inflow", "required": true, "semantic_type": "net_inflow", "position": 18, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "holding_market_value", "alias": "holding_market_value", "required": true, "semantic_type": "holding_market_value", "position": 19, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "asset_rank_in_company", "alias": "asset_rank_in_company", "required": true, "semantic_type": "asset_rank_in_company", "position": 20, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}], "tables": ["dwd_cust_tran_d", "dim_product", "ads_cust_info_d", "dim_branch", "dws_cust_aset_d", "dws_cust_fin_d", "dwd_cust_hold_d"], "metrics": ["customer_count", "total_asset", "active_customer_rate", "turnover", "total_fee", "net_inflow", "holding_market_value", "asset_rank_in_company"], "snapshot_policy": {"ads_cust_info_d": "20260531", "dws_cust_aset_d": "20260331", "dwd_cust_hold_d": "20260331", "dim_branch": "20260531"}, "population": "2026年5月31日客户归属的全部营业部客户", "grain": ["分公司", "营业部"], "missing_fact_policy": {"fact_tables": ["dws_cust_aset_d", "dwd_cust_tran_d", "dws_cust_fin_d", "dwd_cust_hold_d"], "policy": "缺失时指标按0计算"}, "expect_nonempty": true, "calculation_notes": ["营业部客户数以客户快照为母集；交易、资金数据缺失按0。", "活跃客户率为一季度交易额大于0的客户数除以营业部客户数。", "在各分公司内部按期末总资产排名。"], "dictionary_translation": false}`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> repair_sql -> validate_sql -> repair_sql -> validate_sql -> human_review_or_explain -> persist_state`

SQL generation timeline:

| Attempt | Type | Status | Started UTC | Completed UTC | Elapsed ms | Model |
|---------|------|--------|-------------|---------------|------------|-------|
| 1 | initial | failed | 2026-07-31T14:06:31.010531+00:00 | 2026-07-31T14:07:40.878377+00:00 | 69867.70 |  |
| 2 | repair | ok | 2026-07-31T14:07:40.926553+00:00 | 2026-07-31T14:10:50.444102+00:00 | 189513.88 | deepseek-v4-pro |
| 3 | repair | ok | 2026-07-31T14:10:50.506392+00:00 | 2026-07-31T14:11:29.968455+00:00 | 39460.74 | deepseek-v4-pro |

SQL attempt 1 (initial):

```sql

```

SQL attempt 2 (repair):

```sql
WITH cust_base AS (SELECT a.pty_id, a.org_id, b.up_org_id, b.up_org_name, b.org_name FROM ads_cust_info_d a LEFT JOIN dim_branch b ON a.org_id = b.org_id AND b.data_dt = '20260531' WHERE a.data_dt = '20260531'), asset AS (SELECT pty_id, coalesce(nm_tot_aset,0) + coalesce(fc_pur_aset,0) AS total_asset FROM dws_cust_aset_d WHERE data_dt = '20260331'), tran AS (SELECT pty_id, sum(coalesce(buy_amt,0) + coalesce(sell_amt,0)) AS turnover, sum(coalesce(buy_rake,0) + coalesce(buy_fare,0) + coalesce(sell_rake,0) + coalesce(sell_fare,0)) AS total_fee FROM dwd_cust_tran_d WHERE data_dt BETWEEN '20260101' AND '20260331' GROUP BY pty_id), fin AS (SELECT pty_id, sum(coalesce(cash_in,0)) - sum(coalesce(cash_out,0)) AS net_inflow FROM dws_cust_fin_d WHERE data_dt BETWEEN '20260101' AND '20260331' GROUP BY pty_id), hold AS (SELECT pty_id, sum(coalesce(mkt_val,0)) AS holding_market_value FROM dwd_cust_hold_d WHERE data_dt = '20260331' GROUP BY pty_id), cust_metrics AS (SELECT c.pty_id, c.org_id, c.up_org_id, c.up_org_name, c.org_name, coalesce(a.total_asset, 0) AS total_asset_ind, coalesce(t.turnover, 0) AS turnover_ind, coalesce(t.total_fee, 0) AS total_fee_ind, coalesce(f.net_inflow, 0) AS net_inflow_ind, coalesce(h.holding_market_value, 0) AS holding_market_value_ind FROM cust_base c LEFT JOIN asset a ON c.pty_id = a.pty_id LEFT JOIN tran t ON c.pty_id = t.pty_id LEFT JOIN fin f ON c.pty_id = f.pty_id LEFT JOIN hold h ON c.pty_id = h.pty_id), branch_agg AS (SELECT up_org_id, up_org_name, org_id, org_name, count(*) AS customer_count, sum(total_asset_ind) AS total_asset, sum(CASE WHEN turnover_ind > 0 THEN 1 ELSE 0 END) AS active_cust_count, sum(turnover_ind) AS turnover, sum(total_fee_ind) AS total_fee, sum(net_inflow_ind) AS net_inflow, sum(holding_market_value_ind) AS holding_market_value FROM cust_metrics GROUP BY up_org_id, up_org_name, org_id, org_name), ranked AS (SELECT *, DENSE_RANK() OVER (PARTITION BY up_org_id ORDER BY total_asset DESC) AS asset_rank_in_company FROM branch_agg) SELECT up_org_name, org_name, customer_count, total_asset, (active_cust_count * 1.0 / customer_count) AS active_customer_rate, turnover, total_fee, net_inflow, holding_market_value, asset_rank_in_company FROM ranked WHERE asset_rank_in_company <= 3 ORDER BY up_org_id, asset_rank_in_company
```

SQL attempt 3 (repair):

```sql
WITH cust_base AS (SELECT a.pty_id, a.org_id, b.up_org_id, b.up_org_name, b.org_name FROM ads_cust_info_d a LEFT JOIN dim_branch b ON a.org_id = b.org_id AND b.data_dt = '20260531' WHERE a.data_dt = '20260531'), asset AS (SELECT pty_id, coalesce(nm_tot_aset,0) + coalesce(fc_pur_aset,0) AS total_asset FROM dws_cust_aset_d WHERE data_dt = '20260331'), tran AS (SELECT pty_id, sum(coalesce(buy_amt,0) + coalesce(sell_amt,0)) AS turnover, sum(coalesce(buy_rake,0) + coalesce(buy_fare,0) + coalesce(sell_rake,0) + coalesce(sell_fare,0)) AS total_fee FROM dwd_cust_tran_d WHERE data_dt BETWEEN '20260101' AND '20260331' GROUP BY pty_id), fin AS (SELECT pty_id, sum(coalesce(cash_in,0)) - sum(coalesce(cash_out,0)) AS net_inflow FROM dws_cust_fin_d WHERE data_dt BETWEEN '20260101' AND '20260331' GROUP BY pty_id), hold AS (SELECT pty_id, sum(coalesce(mkt_val,0)) AS holding_market_value FROM dwd_cust_hold_d WHERE data_dt = '20260331' GROUP BY pty_id), cust_metrics AS (SELECT c.pty_id, c.org_id, c.up_org_id, c.up_org_name, c.org_name, coalesce(a.total_asset, 0) AS total_asset_ind, coalesce(t.turnover, 0) AS turnover_ind, coalesce(t.total_fee, 0) AS total_fee_ind, coalesce(f.net_inflow, 0) AS net_inflow_ind, coalesce(h.holding_market_value, 0) AS holding_market_value_ind FROM cust_base c LEFT JOIN asset a ON c.pty_id = a.pty_id LEFT JOIN tran t ON c.pty_id = t.pty_id LEFT JOIN fin f ON c.pty_id = f.pty_id LEFT JOIN hold h ON c.pty_id = h.pty_id), branch_agg AS (SELECT up_org_id, up_org_name, org_id, org_name, count(*) AS customer_count, sum(total_asset_ind) AS total_asset, sum(CASE WHEN turnover_ind > 0 THEN 1 ELSE 0 END) AS active_cust_count, sum(turnover_ind) AS turnover, sum(total_fee_ind) AS total_fee, sum(net_inflow_ind) AS net_inflow, sum(holding_market_value_ind) AS holding_market_value FROM cust_metrics GROUP BY up_org_id, up_org_name, org_id, org_name), ranked AS (SELECT *, DENSE_RANK() OVER (PARTITION BY up_org_id ORDER BY total_asset DESC) AS asset_rank_in_company FROM branch_agg) SELECT up_org_name, org_name, customer_count, total_asset, (active_cust_count * 1.0 / customer_count) AS active_customer_rate, turnover, total_fee, net_inflow, holding_market_value, asset_rank_in_company FROM ranked WHERE asset_rank_in_company <= 3 ORDER BY up_org_id, asset_rank_in_company
```

Final candidate SQL:

```sql
WITH cust_base AS (SELECT a.pty_id, a.org_id, b.up_org_id, b.up_org_name, b.org_name FROM ads_cust_info_d a LEFT JOIN dim_branch b ON a.org_id = b.org_id AND b.data_dt = '20260531' WHERE a.data_dt = '20260531'), asset AS (SELECT pty_id, coalesce(nm_tot_aset,0) + coalesce(fc_pur_aset,0) AS total_asset FROM dws_cust_aset_d WHERE data_dt = '20260331'), tran AS (SELECT pty_id, sum(coalesce(buy_amt,0) + coalesce(sell_amt,0)) AS turnover, sum(coalesce(buy_rake,0) + coalesce(buy_fare,0) + coalesce(sell_rake,0) + coalesce(sell_fare,0)) AS total_fee FROM dwd_cust_tran_d WHERE data_dt BETWEEN '20260101' AND '20260331' GROUP BY pty_id), fin AS (SELECT pty_id, sum(coalesce(cash_in,0)) - sum(coalesce(cash_out,0)) AS net_inflow FROM dws_cust_fin_d WHERE data_dt BETWEEN '20260101' AND '20260331' GROUP BY pty_id), hold AS (SELECT pty_id, sum(coalesce(mkt_val,0)) AS holding_market_value FROM dwd_cust_hold_d WHERE data_dt = '20260331' GROUP BY pty_id), cust_metrics AS (SELECT c.pty_id, c.org_id, c.up_org_id, c.up_org_name, c.org_name, coalesce(a.total_asset, 0) AS total_asset_ind, coalesce(t.turnover, 0) AS turnover_ind, coalesce(t.total_fee, 0) AS total_fee_ind, coalesce(f.net_inflow, 0) AS net_inflow_ind, coalesce(h.holding_market_value, 0) AS holding_market_value_ind FROM cust_base c LEFT JOIN asset a ON c.pty_id = a.pty_id LEFT JOIN tran t ON c.pty_id = t.pty_id LEFT JOIN fin f ON c.pty_id = f.pty_id LEFT JOIN hold h ON c.pty_id = h.pty_id), branch_agg AS (SELECT up_org_id, up_org_name, org_id, org_name, count(*) AS customer_count, sum(total_asset_ind) AS total_asset, sum(CASE WHEN turnover_ind > 0 THEN 1 ELSE 0 END) AS active_cust_count, sum(turnover_ind) AS turnover, sum(total_fee_ind) AS total_fee, sum(net_inflow_ind) AS net_inflow, sum(holding_market_value_ind) AS holding_market_value FROM cust_metrics GROUP BY up_org_id, up_org_name, org_id, org_name), ranked AS (SELECT *, DENSE_RANK() OVER (PARTITION BY up_org_id ORDER BY total_asset DESC) AS asset_rank_in_company FROM branch_agg) SELECT up_org_name, org_name, customer_count, total_asset, (active_cust_count * 1.0 / customer_count) AS active_customer_rate, turnover, total_fee, net_inflow, holding_market_value, asset_rank_in_company FROM ranked WHERE asset_rank_in_company <= 3 ORDER BY up_org_id, asset_rank_in_company
```

### a027

- Question: 产品经理希望同时观察交易方向和期末沉淀。请按产品统计2026年一季度买入金额、卖出金额、净买入金额、交易客户数和交易客户覆盖的营业部数量，再补充3月31日持仓客户数与持仓市值。只保留买入或卖出金额大于0的产品。最终按净买入金额绝对值从高到低取前20只产品，并返回产品一级、二级分类；净买入为负表示净卖出。
- Executable: Y
- Agent completed: Y
- Semantic result match: Y
- Exact match: Y
- Standard rows: 20
- Agent rows: 20
- Standard columns: `['prdt_id', 'prdt_name', 'up_prdt_type_name', 'prdt_type_name', 'buy_amount', 'sell_amount', 'net_buy_amount', 'trading_customer_count', 'branch_coverage', 'holder_count', 'market_value']`
- Agent columns: `['prdt_id', 'prdt_name', 'up_prdt_type_name', 'prdt_type_name', 'buy_amount', 'sell_amount', 'net_buy_amount', 'trading_customer_count', 'branch_coverage', 'holder_count', 'market_value']`
- Semantic column mapping: `{'prdt_id': 'prdt_id', 'prdt_name': 'prdt_name', 'up_prdt_type_name': 'up_prdt_type_name', 'prdt_type_name': 'prdt_type_name', 'buy_amount': 'buy_amount', 'sell_amount': 'sell_amount', 'net_buy_amount': 'net_buy_amount', 'trading_customer_count': 'trading_customer_count', 'branch_coverage': 'branch_coverage', 'holder_count': 'holder_count', 'market_value': 'market_value'}`
- Error type: `ok`
- Error tags: `['ok']`
- Final answer: 根据2026年一季度交易数据，已为您筛选买入或卖出金额大于0的产品，并计算净买入金额绝对值前20名。其中，净卖出最大的产品为GC001（国债逆回购），净卖出金额13.24亿元，交易客户57户覆盖9个营业部；净买入最大的为华泰紫金天天发货币市场基金（天天发），净买入3071.68万元，交易客户205户覆盖17个营业部，期末持仓市值2445.79万元。其余产品详情见完整列表。
- Thread id: `eval:p1p2-smoke2-20260731:r1:a027`
- SQL generation attempts: 1
- SQL generation elapsed: 64382.90 ms
- SQL plan: `{"target": "统计2026年一季度按产品的买入金额、卖出金额、净买入金额、交易客户数、营业部覆盖数，以及3月31日的持仓客户数与持仓市值，筛选买入或卖出金额大于0的产品，按净买入绝对值降序取前20", "tables": ["dwd_cust_tran_d", "dim_product", "ads_cust_info_d", "dim_branch", "dwd_cust_hold_d"], "joins": ["dwd_cust_tran_d INNER JOIN dim_product ON dwd_cust_tran_d.prdt_id = dim_product.prdt_id", "dwd_cust_tran_d LEFT JOIN ads_cust_info_d ON dwd_cust_tran_d.pty_id = ads_cust_info_d.pty_id AND ads_cust_info_d.data_dt = '20260531'", "ads_cust_info_d LEFT JOIN dim_branch ON ads_cust_info_d.org_id = dim_branch.org_id AND dim_branch.data_dt = '20260531'", "交易聚合结果 LEFT JOIN 持仓聚合结果 ON 交易.prdt_id = 持仓.prdt_id", "持仓聚合：dwd_cust_hold_d INNER JOIN dim_product ON dwd_cust_hold_d.prdt_id = dim_product.prdt_id WHERE dwd_cust_hold_d.data_dt = '20260331'"], "filters": ["交易日期 BETWEEN '20260101' AND '20260331'", "持仓日期 = '20260331'", "客户信息快照 = '20260531'", "营业部快照 = '20260531'", "按产品聚合后 HAVING SUM(COALESCE(buy_amt,0)) > 0 OR SUM(COALESCE(sell_amt,0)) > 0"], "metrics": ["买入金额 = SUM(COALESCE(buy_amt, 0))", "卖出金额 = SUM(COALESCE(sell_amt, 0))", "净买入金额 = SUM(COALESCE(buy_amt, 0)) - SUM(COALESCE(sell_amt, 0))", "交易客户数 = COUNT(DISTINCT dwd_cust_tran_d.pty_id)", "营业部覆盖数 = COUNT(DISTINCT ads_cust_info_d.org_id)", "持仓客户数 = COUNT(DISTINCT dwd_cust_hold_d.pty_id)", "持仓市值 = SUM(COALESCE(mkt_val, 0))"], "population": "2026年一季度内在dwd_cust_tran_d中有交易记录的产品，且买入或卖出金额大于0", "grain": ["产品 (prdt_id)"], "output_columns": [{"expression": "dim_product.prdt_id", "alias": "prdt_id", "semantic_type": "product_id", "required": true, "position": 1, "name": "prdt_id", "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"expression": "dim_product.prdt_name", "alias": "prdt_name", "semantic_type": "product_name", "required": true, "position": 2, "name": "prdt_name", "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"expression": "dim_product.up_prdt_type_name", "alias": "up_prdt_type_name", "semantic_type": "up_product_type_name", "required": true, "position": 3, "name": "up_prdt_type_name", "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"expression": "dim_product.prdt_type_name", "alias": "prdt_type_name", "semantic_type": "product_type_name", "required": true, "position": 4, "name": "prdt_type_name", "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"expression": "SUM(COALESCE(buy_amt,0))", "alias": "buy_amount", "semantic_type": "buy_amount", "required": true, "position": 5, "name": "buy_amount", "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"expression": "SUM(COALESCE(sell_amt,0))", "alias": "sell_amount", "semantic_type": "sell_amount", "required": true, "position": 6, "name": "sell_amount", "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"expression": "SUM(COALESCE(buy_amt,0)) - SUM(COALESCE(sell_amt,0))", "alias": "net_buy_amount", "semantic_type": "net_buy_amount", "required": true, "position": 7, "name": "net_buy_amount", "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"expression": "COUNT(DISTINCT dwd_cust_tran_d.pty_id)", "alias": "trading_customer_count", "semantic_type": "trading_customer_count", "required": true, "position": 8, "name": "trading_customer_count", "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"expression": "COUNT(DISTINCT ads_cust_info_d.org_id)", "alias": "branch_coverage", "semantic_type": "branch_coverage", "required": true, "position": 9, "name": "branch_coverage", "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"expression": "COALESCE(hold.holder_count, 0)", "alias": "holder_count", "semantic_type": "holder_count", "required": true, "position": 10, "name": "holder_count", "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"expression": "COALESCE(hold.market_value, 0)", "alias": "market_value", "semantic_type": "market_value", "required": true, "position": 11, "name": "market_value", "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}], "group_by": ["dim_product.prdt_id", "dim_product.prdt_name", "dim_product.up_prdt_type_name", "dim_product.prdt_type_name"], "eligibility_filters": [], "snapshot_policy": {"customer": "20260531", "branch": "20260531", "holdings": "20260331", "dwd_cust_tran_d": "20260101-20260331", "dwd_cust_hold_d": "20260331", "ads_cust_info_d": "20260531", "dim_branch": "20260531"}, "missing_fact_policy": {"end-of-quarter holdings": "zero_fill_after_aggregation (COALESCE(holder_count,0), COALESCE(market_value,0))"}, "missing_period_policy": "exclude", "dictionary_translation": [], "window": [], "order_by": [{"expression": "abs(net_buy_amount)", "direction": "desc", "nulls": "last"}, {"expression": "prdt_id", "direction": "asc", "nulls": "last"}], "top_n": 20, "expect_nonempty": true, "calculation_notes": ["产品净买入等于买入金额减卖出金额。", "持仓客户数和持仓市值取3月31日，营业部覆盖数取一季度有交易客户所属营业部去重数。"], "strategy": "llm_text_to_sql", "matched_query_id": null}`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

SQL generation timeline:

| Attempt | Type | Status | Started UTC | Completed UTC | Elapsed ms | Model |
|---------|------|--------|-------------|---------------|------------|-------|
| 1 | initial | ok | 2026-07-31T14:15:54.533447+00:00 | 2026-07-31T14:16:58.917629+00:00 | 64382.90 | deepseek-v4-pro |

SQL attempt 1 (initial):

```sql
WITH trade_agg AS (
  SELECT 
    p.prdt_id,
    p.prdt_name,
    p.up_prdt_type_name,
    p.prdt_type_name,
    SUM(COALESCE(t.buy_amt, 0)) AS buy_amount,
    SUM(COALESCE(t.sell_amt, 0)) AS sell_amount,
    SUM(COALESCE(t.buy_amt, 0)) - SUM(COALESCE(t.sell_amt, 0)) AS net_buy_amount,
    COUNT(DISTINCT t.pty_id) AS trading_customer_count,
    COUNT(DISTINCT c.org_id) AS branch_coverage
  FROM dwd_cust_tran_d t
  INNER JOIN dim_product p ON t.prdt_id = p.prdt_id
  LEFT JOIN ads_cust_info_d c ON t.pty_id = c.pty_id AND c.data_dt = '20260531'
  LEFT JOIN dim_branch b ON c.org_id = b.org_id AND b.data_dt = '20260531'
  WHERE t.data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY p.prdt_id, p.prdt_name, p.up_prdt_type_name, p.prdt_type_name
  HAVING SUM(COALESCE(t.buy_amt, 0)) > 0 OR SUM(COALESCE(t.sell_amt, 0)) > 0
),
hold_agg AS (
  SELECT 
    prdt_id,
    COUNT(DISTINCT pty_id) AS holder_count,
    SUM(COALESCE(mkt_val, 0)) AS market_value
  FROM dwd_cust_hold_d
  WHERE data_dt = '20260331'
  GROUP BY prdt_id
)
SELECT 
  trade_agg.prdt_id,
  trade_agg.prdt_name,
  trade_agg.up_prdt_type_name,
  trade_agg.prdt_type_name,
  trade_agg.buy_amount,
  trade_agg.sell_amount,
  trade_agg.net_buy_amount,
  trade_agg.trading_customer_count,
  trade_agg.branch_coverage,
  COALESCE(hold_agg.holder_count, 0) AS holder_count,
  COALESCE(hold_agg.market_value, 0) AS market_value
FROM trade_agg
LEFT JOIN hold_agg ON trade_agg.prdt_id = hold_agg.prdt_id
ORDER BY ABS(trade_agg.net_buy_amount) DESC, trade_agg.prdt_id ASC
LIMIT 20
```

Final candidate SQL:

```sql
WITH trade_agg AS (
  SELECT 
    p.prdt_id,
    p.prdt_name,
    p.up_prdt_type_name,
    p.prdt_type_name,
    SUM(COALESCE(t.buy_amt, 0)) AS buy_amount,
    SUM(COALESCE(t.sell_amt, 0)) AS sell_amount,
    SUM(COALESCE(t.buy_amt, 0)) - SUM(COALESCE(t.sell_amt, 0)) AS net_buy_amount,
    COUNT(DISTINCT t.pty_id) AS trading_customer_count,
    COUNT(DISTINCT c.org_id) AS branch_coverage
  FROM dwd_cust_tran_d t
  INNER JOIN dim_product p ON t.prdt_id = p.prdt_id
  LEFT JOIN ads_cust_info_d c ON t.pty_id = c.pty_id AND c.data_dt = '20260531'
  LEFT JOIN dim_branch b ON c.org_id = b.org_id AND b.data_dt = '20260531'
  WHERE t.data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY p.prdt_id, p.prdt_name, p.up_prdt_type_name, p.prdt_type_name
  HAVING SUM(COALESCE(t.buy_amt, 0)) > 0 OR SUM(COALESCE(t.sell_amt, 0)) > 0
),
hold_agg AS (
  SELECT 
    prdt_id,
    COUNT(DISTINCT pty_id) AS holder_count,
    SUM(COALESCE(mkt_val, 0)) AS market_value
  FROM dwd_cust_hold_d
  WHERE data_dt = '20260331'
  GROUP BY prdt_id
)
SELECT 
  trade_agg.prdt_id,
  trade_agg.prdt_name,
  trade_agg.up_prdt_type_name,
  trade_agg.prdt_type_name,
  trade_agg.buy_amount,
  trade_agg.sell_amount,
  trade_agg.net_buy_amount,
  trade_agg.trading_customer_count,
  trade_agg.branch_coverage,
  COALESCE(hold_agg.holder_count, 0) AS holder_count,
  COALESCE(hold_agg.market_value, 0) AS market_value
FROM trade_agg
LEFT JOIN hold_agg ON trade_agg.prdt_id = hold_agg.prdt_id
ORDER BY ABS(trade_agg.net_buy_amount) DESC, trade_agg.prdt_id ASC
LIMIT 20
```
