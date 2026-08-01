# Agent Evaluation Report

- SQL mode: `llm`
- Total cases: 1
- Agent completed rate: 0/1 (0.00%)
- Candidate SQL executable rate: 1/1 (100.00%)
- Exact result match rate: 0/1 (0.00%)
- Semantic result match rate: 0/1 (0.00%)
- Row count match rate: 0/1 (0.00%)
- Average execution elapsed: 114.35 ms
- SQL generation attempts: 3
- Total SQL generation elapsed: 186945.36 ms
- Average SQL generation attempt elapsed: 62315.12 ms
- LLM calls: 6
- LLM total tokens: 88816

| Query ID | Completed | Candidate SQL | Semantic | Strict Exact | Rows | Semantic Schema | SQL Gen Attempts | SQL Gen ms | Error Tags |
|----------|-----------|---------------|----------|--------------|------|-----------------|------------------|------------|------------|
| a004 | N | Y | N | N | 16/14 | Y | 3 | 186945.36 | validator_false_positive, missing_period_policy_violation, row_count_mismatch, semantic_value_error |

## Case Details

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
- Error tags: `['validator_false_positive', 'missing_period_policy_violation', 'row_count_mismatch', 'semantic_value_error']`
- Final answer: 查询未能自动完成，已进入人工复核路径。原因：Missing period policy is zero_fill, but SQL has no period scaffold or full-outer zero-fill strategy.
- Thread id: `eval:p1p2-a004-smoke4-20260731:r1:a004`
- SQL generation attempts: 3
- SQL generation elapsed: 186945.36 ms
- SQL plan: `{"target": "营业部经营对比表：计算每个营业部客户数、期末总资产、活跃客户率、买卖交易额、佣金及费用合计、资金净流入、期末持仓市值，并在分公司内部按总资产降序排名，只取前3名", "tables": ["ads_cust_info_d", "dim_branch", "dws_cust_aset_d", "dwd_cust_tran_d", "dws_cust_fin_d", "dwd_cust_hold_d"], "joins": ["以 ads_cust_info_d (快照20260531) 为基础客户集，通过 org_id 关联 dim_branch (快照20260531) 获取营业部名称和分公司名称", "客户集 LEFT JOIN 期末资产子查询 (dws_cust_aset_d, data_dt='20260331') 按 pty_id 关联", "客户集 LEFT JOIN 交易聚合子查询 (dwd_cust_tran_d, data_dt BETWEEN '20260101' AND '20260331') 按 pty_id 关联", "客户集 LEFT JOIN 资金聚合子查询 (dws_cust_fin_d, data_dt BETWEEN '20260101' AND '20260331') 按 pty_id 关联", "客户集 LEFT JOIN 持仓聚合子查询 (dwd_cust_hold_d, data_dt='20260331') 按 pty_id 关联"], "filters": ["ads_cust_info_d.data_dt = '20260531'", "dim_branch.data_dt = '20260531'", "dws_cust_aset_d.data_dt = '20260331'", "dwd_cust_tran_d.data_dt BETWEEN '20260101' AND '20260331'", "dws_cust_fin_d.data_dt BETWEEN '20260101' AND '20260331'", "dwd_cust_hold_d.data_dt = '20260331'"], "metrics": ["customer_count = COUNT(DISTINCT cust.pty_id)", "total_asset = SUM(COALESCE(aset.total_asset, 0))", "active_customer_rate = SUM(CASE WHEN COALESCE(tran.turnover, 0) > 0 THEN 1 ELSE 0 END) / COUNT(DISTINCT cust.pty_id)", "turnover = SUM(COALESCE(tran.turnover, 0))", "total_fee = SUM(COALESCE(tran.total_fee, 0))", "net_inflow = SUM(COALESCE(fin.net_inflow, 0))", "holding_market_value = SUM(COALESCE(hold.mkt_val, 0))"], "population": "2026年5月31日客户归属快照中的全部营业部客户（取自 ads_cust_info_d.data_dt='20260531'）", "grain": ["org_id (营业部)"], "output_columns": [{"name": "up_org_name", "alias": "up_org_name", "semantic_type": "up_org_name", "required": true, "position": 1, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "org_name", "alias": "org_name", "semantic_type": "org_name", "required": true, "position": 2, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "customer_count", "alias": "customer_count", "semantic_type": "customer_count", "required": true, "position": 3, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "total_asset", "alias": "total_asset", "semantic_type": "total_asset", "required": true, "position": 4, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "active_customer_rate", "alias": "active_customer_rate", "semantic_type": "active_customer_rate", "required": true, "position": 5, "alias_strict": false, "numeric_tolerance": {"atol": 1e-07, "rtol": 1e-06}}, {"name": "turnover", "alias": "turnover", "semantic_type": "turnover", "required": true, "position": 6, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "total_fee", "alias": "total_fee", "semantic_type": "total_fee", "required": true, "position": 7, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "net_inflow", "alias": "net_inflow", "semantic_type": "net_inflow", "required": true, "position": 8, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "holding_market_value", "alias": "holding_market_value", "semantic_type": "holding_market_value", "required": true, "position": 9, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "asset_rank_in_company", "alias": "asset_rank_in_company", "semantic_type": "asset_rank_in_company", "required": true, "position": 10, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}], "group_by": ["cust.org_id", "branch.up_org_name", "branch.org_name"], "eligibility_filters": ["最终过滤 asset_rank_in_company <= 3"], "snapshot_policy": {"customer_snapshot": "20260531", "asset_snapshot": "20260331", "branch_snapshot": "20260531", "ads_cust_info_d": "20260531", "dim_branch": "20260531", "dws_cust_aset_d": "20260331", "dwd_cust_tran_d": "20260101 to 20260331", "dws_cust_fin_d": "20260101 to 20260331", "dwd_cust_hold_d": "20260331"}, "missing_fact_policy": {"期末总资产": "zero_fill_after_aggregation", "买卖交易额": "zero_fill_after_aggregation", "佣金及费用合计": "zero_fill_after_aggregation", "资金净流入": "zero_fill_after_aggregation", "期末持仓市值": "zero_fill_after_aggregation"}, "missing_period_policy": "zero_fill", "dictionary_translation": [], "window": [{"function": "dense_rank", "partition_by": ["up_org_name"], "order_by": [{"expression": "total_asset", "direction": "desc"}], "tie_breaker": []}], "order_by": [{"expression": "up_org_name", "direction": "asc", "nulls": "last"}, {"expression": "asset_rank_in_company", "direction": "asc", "nulls": "last"}], "top_n": 3, "expect_nonempty": true, "calculation_notes": ["营业部客户数以客户快照为母集；交易、资金数据缺失按0。", "活跃客户率为一季度交易额大于0的客户数除以营业部客户数。", "在各分公司内部按期末总资产排名。"], "strategy": "llm_text_to_sql", "matched_query_id": null}`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> repair_sql -> validate_sql -> repair_sql -> validate_sql -> human_review_or_explain -> persist_state`

SQL generation timeline:

| Attempt | Type | Status | Started UTC | Completed UTC | Elapsed ms | Model |
|---------|------|--------|-------------|---------------|------------|-------|
| 1 | initial | ok | 2026-07-31T14:54:53.071388+00:00 | 2026-07-31T14:55:47.818822+00:00 | 54744.54 | deepseek-v4-pro |
| 2 | repair | ok | 2026-07-31T14:55:47.899828+00:00 | 2026-07-31T14:57:11.065214+00:00 | 83163.19 | deepseek-v4-pro |
| 3 | repair | ok | 2026-07-31T14:57:11.143612+00:00 | 2026-07-31T14:58:00.183803+00:00 | 49037.63 | deepseek-v4-pro |

SQL attempt 1 (initial):

```sql
WITH cust_branch AS (
  SELECT c.pty_id, c.org_id, b.up_org_name, b.org_name
  FROM ads_cust_info_d c
  LEFT JOIN dim_branch b ON c.org_id = b.org_id AND b.data_dt = '20260531'
  WHERE c.data_dt = '20260531'
),

asset AS (
  SELECT pty_id, sum(coalesce(nm_tot_aset, 0) + coalesce(fc_pur_aset, 0)) AS total_asset
  FROM dws_cust_aset_d
  WHERE data_dt = '20260331'
  GROUP BY pty_id
),

trade AS (
  SELECT pty_id,
         sum(coalesce(buy_amt, 0) + coalesce(sell_amt, 0)) AS turnover,
         sum(coalesce(buy_rake, 0) + coalesce(sell_rake, 0) + coalesce(buy_fare, 0) + coalesce(sell_fare, 0)) AS total_fee
  FROM dwd_cust_tran_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY pty_id
),

fin AS (
  SELECT pty_id,
         sum(coalesce(cash_in, 0) - coalesce(cash_out, 0) + coalesce(tran_in, 0) - coalesce(tran_out, 0) + coalesce(assign_in, 0) - coalesce(assign_out, 0)) AS net_inflow
  FROM dws_cust_fin_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY pty_id
),

hold AS (
  SELECT pty_id, sum(coalesce(mkt_val, 0)) AS mkt_val
  FROM dwd_cust_hold_d
  WHERE data_dt = '20260331'
  GROUP BY pty_id
),

branch_agg AS (
  SELECT cb.up_org_name,
         cb.org_name,
         COUNT(DISTINCT cb.pty_id) AS customer_count,
         COALESCE(SUM(a.total_asset), 0) AS total_asset,
         CAST(SUM(CASE WHEN COALESCE(t.turnover, 0) > 0 THEN 1 ELSE 0 END) AS DOUBLE) / COUNT(DISTINCT cb.pty_id) AS active_customer_rate,
         COALESCE(SUM(t.turnover), 0) AS turnover,
         COALESCE(SUM(t.total_fee), 0) AS total_fee,
         COALESCE(SUM(f.net_inflow), 0) AS net_inflow,
         COALESCE(SUM(h.mkt_val), 0) AS holding_market_value
  FROM cust_branch cb
  LEFT JOIN asset a ON cb.pty_id = a.pty_id
  LEFT JOIN trade t ON cb.pty_id = t.pty_id
  LEFT JOIN fin f ON cb.pty_id = f.pty_id
  LEFT JOIN hold h ON cb.pty_id = h.pty_id
  GROUP BY cb.org_id, cb.up_org_name, cb.org_name
)

SELECT up_org_name,
       org_name,
       customer_count,
       total_asset,
       active_customer_rate,
       turnover,
       total_fee,
       net_inflow,
       holding_market_value,
       DENSE_RANK() OVER (PARTITION BY up_org_name ORDER BY total_asset DESC) AS asset_rank_in_company
FROM branch_agg
WHERE asset_rank_in_company <= 3
ORDER BY up_org_name, asset_rank_in_company
```

SQL attempt 2 (repair):

```sql
WITH cust_branch AS (
  SELECT c.pty_id, c.org_id, b.up_org_name, b.org_name
  FROM ads_cust_info_d c
  LEFT JOIN dim_branch b ON c.org_id = b.org_id AND b.data_dt = '20260531'
  WHERE c.data_dt = '20260531'
),

dates AS (
  SELECT unnest(generate_series('2026-01-01'::date, '2026-03-31'::date, '1 day'::interval)) AS dt
),

cust_branch_dates AS (
  SELECT cb.pty_id, cb.org_id, cb.up_org_name, cb.org_name, d.dt
  FROM cust_branch cb
  CROSS JOIN dates d
),

asset AS (
  SELECT pty_id, sum(coalesce(nm_tot_aset, 0) + coalesce(fc_pur_aset, 0)) AS total_asset
  FROM dws_cust_aset_d
  WHERE data_dt = '20260331'
  GROUP BY pty_id
),

trade AS (
  SELECT cbd.pty_id, cbd.org_id, cbd.up_org_name, cbd.org_name,
         sum(coalesce(t.buy_amt, 0) + coalesce(t.sell_amt, 0)) AS turnover,
         sum(coalesce(t.buy_rake, 0) + coalesce(t.sell_rake, 0) + coalesce(t.buy_fare, 0) + coalesce(t.sell_fare, 0)) AS total_fee
  FROM cust_branch_dates cbd
  LEFT JOIN dwd_cust_tran_d t ON cbd.pty_id = t.pty_id AND t.data_dt = to_char(cbd.dt, 'yyyymmdd')
  GROUP BY cbd.pty_id, cbd.org_id, cbd.up_org_name, cbd.org_name
),

fin AS (
  SELECT cbd.pty_id, cbd.org_id, cbd.up_org_name, cbd.org_name,
         sum(coalesce(f.cash_in, 0) - coalesce(f.cash_out, 0) + coalesce(f.tran_in, 0) - coalesce(f.tran_out, 0) + coalesce(f.assign_in, 0) - coalesce(f.assign_out, 0)) AS net_inflow
  FROM cust_branch_dates cbd
  LEFT JOIN dws_cust_fin_d f ON cbd.pty_id = f.pty_id AND f.data_dt = to_char(cbd.dt, 'yyyymmdd')
  GROUP BY cbd.pty_id, cbd.org_id, cbd.up_org_name, cbd.org_name
),

hold AS (
  SELECT pty_id, sum(coalesce(mkt_val, 0)) AS mkt_val
  FROM dwd_cust_hold_d
  WHERE data_dt = '20260331'
  GROUP BY pty_id
),

branch_agg AS (
  SELECT cb.up_org_name,
         cb.org_name,
         COUNT(DISTINCT cb.pty_id) AS customer_count,
         COALESCE(SUM(a.total_asset), 0) AS total_asset,
         CAST(SUM(CASE WHEN COALESCE(t.turnover, 0) > 0 THEN 1 ELSE 0 END) AS DOUBLE) / COUNT(DISTINCT cb.pty_id) AS active_customer_rate,
         COALESCE(SUM(t.turnover), 0) AS turnover,
         COALESCE(SUM(t.total_fee), 0) AS total_fee,
         COALESCE(SUM(f.net_inflow), 0) AS net_inflow,
         COALESCE(SUM(h.mkt_val), 0) AS holding_market_value
  FROM cust_branch cb
  LEFT JOIN asset a ON cb.pty_id = a.pty_id
  LEFT JOIN trade t ON cb.pty_id = t.pty_id
  LEFT JOIN fin f ON cb.pty_id = f.pty_id
  LEFT JOIN hold h ON cb.pty_id = h.pty_id
  GROUP BY cb.org_id, cb.up_org_name, cb.org_name
)

SELECT up_org_name,
       org_name,
       customer_count,
       total_asset,
       active_customer_rate,
       turnover,
       total_fee,
       net_inflow,
       holding_market_value,
       DENSE_RANK() OVER (PARTITION BY up_org_name ORDER BY total_asset DESC) AS asset_rank_in_company
FROM branch_agg
QUALIFY asset_rank_in_company <= 3
ORDER BY up_org_name, asset_rank_in_company
```

SQL attempt 3 (repair):

```sql
WITH cust_branch AS (
  SELECT c.pty_id, c.org_id, b.up_org_name, b.org_name
  FROM ads_cust_info_d c
  LEFT JOIN dim_branch b ON c.org_id = b.org_id AND b.data_dt = '20260531'
  WHERE c.data_dt = '20260531'
),

asset AS (
  SELECT pty_id,
         SUM(COALESCE(nm_tot_aset, 0) + COALESCE(fc_pur_aset, 0)) AS total_asset
  FROM dws_cust_aset_d
  WHERE data_dt = '20260331'
  GROUP BY pty_id
),

trade AS (
  SELECT pty_id,
         SUM(COALESCE(buy_amt, 0) + COALESCE(sell_amt, 0)) AS turnover,
         SUM(COALESCE(buy_rake, 0) + COALESCE(sell_rake, 0) + COALESCE(buy_fare, 0) + COALESCE(sell_fare, 0)) AS total_fee
  FROM dwd_cust_tran_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY pty_id
),

fin AS (
  SELECT pty_id,
         SUM(COALESCE(cash_in, 0) - COALESCE(cash_out, 0) + COALESCE(tran_in, 0) - COALESCE(tran_out, 0) + COALESCE(assign_in, 0) - COALESCE(assign_out, 0)) AS net_inflow
  FROM dws_cust_fin_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY pty_id
),

hold AS (
  SELECT pty_id,
         SUM(COALESCE(mkt_val, 0)) AS mkt_val
  FROM dwd_cust_hold_d
  WHERE data_dt = '20260331'
  GROUP BY pty_id
),

branch_agg AS (
  SELECT
    cb.up_org_name,
    cb.org_name,
    COUNT(DISTINCT cb.pty_id) AS customer_count,
    COALESCE(SUM(a.total_asset), 0) AS total_asset,
    CAST(COUNT(DISTINCT CASE WHEN COALESCE(t.turnover, 0) > 0 THEN cb.pty_id END) AS DOUBLE) / COUNT(DISTINCT cb.pty_id) AS active_customer_rate,
    COALESCE(SUM(t.turnover), 0) AS turnover,
    COALESCE(SUM(t.total_fee), 0) AS total_fee,
    COALESCE(SUM(f.net_inflow), 0) AS net_inflow,
    COALESCE(SUM(h.mkt_val), 0) AS holding_market_value
  FROM cust_branch cb
  LEFT JOIN asset a ON cb.pty_id = a.pty_id
  LEFT JOIN trade t ON cb.pty_id = t.pty_id
  LEFT JOIN fin f ON cb.pty_id = f.pty_id
  LEFT JOIN hold h ON cb.pty_id = h.pty_id
  GROUP BY cb.org_id, cb.up_org_name, cb.org_name
)

SELECT
  up_org_name,
  org_name,
  customer_count,
  total_asset,
  active_customer_rate,
  turnover,
  total_fee,
  net_inflow,
  holding_market_value,
  DENSE_RANK() OVER (PARTITION BY up_org_name ORDER BY total_asset DESC) AS asset_rank_in_company
FROM branch_agg
QUALIFY asset_rank_in_company <= 3
ORDER BY up_org_name, asset_rank_in_company
```

Final candidate SQL:

```sql
WITH cust_branch AS (
  SELECT c.pty_id, c.org_id, b.up_org_name, b.org_name
  FROM ads_cust_info_d c
  LEFT JOIN dim_branch b ON c.org_id = b.org_id AND b.data_dt = '20260531'
  WHERE c.data_dt = '20260531'
),

asset AS (
  SELECT pty_id,
         SUM(COALESCE(nm_tot_aset, 0) + COALESCE(fc_pur_aset, 0)) AS total_asset
  FROM dws_cust_aset_d
  WHERE data_dt = '20260331'
  GROUP BY pty_id
),

trade AS (
  SELECT pty_id,
         SUM(COALESCE(buy_amt, 0) + COALESCE(sell_amt, 0)) AS turnover,
         SUM(COALESCE(buy_rake, 0) + COALESCE(sell_rake, 0) + COALESCE(buy_fare, 0) + COALESCE(sell_fare, 0)) AS total_fee
  FROM dwd_cust_tran_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY pty_id
),

fin AS (
  SELECT pty_id,
         SUM(COALESCE(cash_in, 0) - COALESCE(cash_out, 0) + COALESCE(tran_in, 0) - COALESCE(tran_out, 0) + COALESCE(assign_in, 0) - COALESCE(assign_out, 0)) AS net_inflow
  FROM dws_cust_fin_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY pty_id
),

hold AS (
  SELECT pty_id,
         SUM(COALESCE(mkt_val, 0)) AS mkt_val
  FROM dwd_cust_hold_d
  WHERE data_dt = '20260331'
  GROUP BY pty_id
),

branch_agg AS (
  SELECT
    cb.up_org_name,
    cb.org_name,
    COUNT(DISTINCT cb.pty_id) AS customer_count,
    COALESCE(SUM(a.total_asset), 0) AS total_asset,
    CAST(COUNT(DISTINCT CASE WHEN COALESCE(t.turnover, 0) > 0 THEN cb.pty_id END) AS DOUBLE) / COUNT(DISTINCT cb.pty_id) AS active_customer_rate,
    COALESCE(SUM(t.turnover), 0) AS turnover,
    COALESCE(SUM(t.total_fee), 0) AS total_fee,
    COALESCE(SUM(f.net_inflow), 0) AS net_inflow,
    COALESCE(SUM(h.mkt_val), 0) AS holding_market_value
  FROM cust_branch cb
  LEFT JOIN asset a ON cb.pty_id = a.pty_id
  LEFT JOIN trade t ON cb.pty_id = t.pty_id
  LEFT JOIN fin f ON cb.pty_id = f.pty_id
  LEFT JOIN hold h ON cb.pty_id = h.pty_id
  GROUP BY cb.org_id, cb.up_org_name, cb.org_name
)

SELECT
  up_org_name,
  org_name,
  customer_count,
  total_asset,
  active_customer_rate,
  turnover,
  total_fee,
  net_inflow,
  holding_market_value,
  DENSE_RANK() OVER (PARTITION BY up_org_name ORDER BY total_asset DESC) AS asset_rank_in_company
FROM branch_agg
QUALIFY asset_rank_in_company <= 3
ORDER BY up_org_name, asset_rank_in_company
```
