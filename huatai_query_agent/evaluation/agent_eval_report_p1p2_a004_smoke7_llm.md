# Agent Evaluation Report

- SQL mode: `llm`
- Total cases: 1
- Agent completed rate: 1/1 (100.00%)
- Candidate SQL executable rate: 1/1 (100.00%)
- Exact result match rate: 0/1 (0.00%)
- Semantic result match rate: 0/1 (0.00%)
- Row count match rate: 1/1 (100.00%)
- Average execution elapsed: 54.12 ms
- SQL generation attempts: 3
- Total SQL generation elapsed: 621087.89 ms
- Average SQL generation attempt elapsed: 207029.30 ms
- LLM calls: 6
- LLM total tokens: 77298

| Query ID | Completed | Candidate SQL | Semantic | Strict Exact | Rows | Semantic Schema | SQL Gen Attempts | SQL Gen ms | Error Tags |
|----------|-----------|---------------|----------|--------------|------|-----------------|------------------|------------|------------|
| a004 | Y | Y | N | N | 14/14 | Y | 3 | 621087.89 | order_only_difference, order_sensitive_mismatch |

## Case Details

### a004

- Question: 区域负责人希望做一张营业部经营对比表。请以2026年5月31日客户归属为准，以营业部全部客户作为统计母集，计算每个营业部的客户数、2026年3月31日期末总资产、一季度有交易金额的活跃客户率、一季度买卖交易额、佣金及费用合计、资金净流入和期末持仓市值。交易或资金记录不存在时按0计算。最后在每个分公司内部按照期末总资产从高到低进行排名，只返回总资产最高的前3个营业部；同一分公司内并列时使用dense rank，不要强行打散并列名次。
- Executable: Y
- Agent completed: Y
- Semantic result match: N
- Exact match: N
- Standard rows: 14
- Agent rows: 14
- Standard columns: `['up_org_name', 'org_name', 'customer_count', 'total_asset', 'active_customer_rate', 'turnover', 'total_fee', 'net_inflow', 'holding_market_value', 'asset_rank_in_company']`
- Agent columns: `['up_org_name', 'org_name', 'customer_count', 'total_asset', 'active_customer_rate', 'turnover', 'total_fee', 'net_inflow', 'holding_market_value', 'asset_rank_in_company']`
- Semantic column mapping: `{'up_org_name': 'up_org_name', 'org_name': 'org_name', 'customer_count': 'customer_count', 'total_asset': 'total_asset', 'active_customer_rate': 'active_customer_rate', 'turnover': 'turnover', 'total_fee': 'total_fee', 'net_inflow': 'net_inflow', 'holding_market_value': 'holding_market_value', 'asset_rank_in_company': 'asset_rank_in_company'}`
- Error type: `order_sensitive_mismatch`
- Error tags: `['order_only_difference', 'order_sensitive_mismatch']`
- Final answer: 已生成营业部经营对比表，展示各分公司内部2026年3月31日期末总资产排名前三的营业部核心指标，共14个营业部入榜。例如：苏州分公司中，张家**营业部客户407人，期末总资产约5.66亿元，一季度活跃客户率77.4%，交易额约56.35亿元；安徽分公司仅有一个营业部入选，客户1人，资产约50万元。详细指标包括客户数、期末总资产、活跃客户率、交易额、佣金费用、资金净流入及期末持仓市值。
- Thread id: `eval:p1p2-a004-smoke7-20260731:r1:a004`
- SQL generation attempts: 3
- SQL generation elapsed: 621087.89 ms
- SQL plan: `{"target": "营业部经营对比表", "tables": ["ads_cust_info_d", "dim_branch", "dws_cust_aset_d", "dwd_cust_tran_d", "dws_cust_fin_d", "dwd_cust_hold_d"], "joins": ["ads_cust_info_d (cust) LEFT JOIN dim_branch (branch) ON cust.org_id = branch.org_id AND branch.data_dt = '20260531'  -- 获取分公司和营业部名称", "cust LEFT JOIN dws_cust_aset_d (aset) ON cust.pty_id = aset.pty_id AND aset.data_dt = '20260331'  -- 期末总资产", "cust LEFT JOIN dwd_cust_tran_d (tran) ON cust.pty_id = tran.pty_id AND tran.data_dt BETWEEN '20260101' AND '20260331'  -- 一季度交易", "cust LEFT JOIN dws_cust_fin_d (fin) ON cust.pty_id = fin.pty_id AND fin.data_dt BETWEEN '20260101' AND '20260331'  -- 一季度资金流动", "cust LEFT JOIN dwd_cust_hold_d (hold) ON cust.pty_id = hold.pty_id AND hold.data_dt = '20260331'  -- 期末持仓"], "filters": ["ads_cust_info_d.data_dt = '20260531'"], "metrics": ["customer_count: COUNT(DISTINCT cust.pty_id) per branch", "total_asset: SUM(COALESCE(aset.nm_tot_aset, 0) + COALESCE(aset.fc_pur_aset, 0))", "active_customer_rate: (活跃客户数) / (总客户数). 活跃客户数定义为在20260101-20260331期间 SUM(COALESCE(tran.buy_amt,0)+COALESCE(tran.sell_amt,0)) > 0 的不同pty_id数量", "turnover: SUM(COALESCE(tran.buy_amt, 0) + COALESCE(tran.sell_amt, 0))", "total_fee: SUM(COALESCE(tran.buy_rake, 0) + COALESCE(tran.sell_rake, 0) + COALESCE(tran.buy_fare, 0) + COALESCE(tran.sell_fare, 0))", "net_inflow: SUM(COALESCE(fin.cash_in, 0) - COALESCE(fin.cash_out, 0))", "holding_market_value: SUM(COALESCE(hold.mkt_val, 0))"], "population": "2026年5月31日归属的营业部全部客户，取自 ads_cust_info_d WHERE data_dt='20260531'", "grain": ["分公司 (up_org_name)", "营业部 (org_name)"], "output_columns": [{"name": "up_org_name", "alias": "up_org_name", "semantic_type": "up_org_name", "required": true, "position": 1, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "org_name", "alias": "org_name", "semantic_type": "org_name", "required": true, "position": 2, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "customer_count", "alias": "customer_count", "semantic_type": "customer_count", "required": true, "position": 3, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "total_asset", "alias": "total_asset", "semantic_type": "total_asset", "required": true, "position": 4, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "active_customer_rate", "alias": "active_customer_rate", "semantic_type": "active_customer_rate", "required": true, "position": 5, "alias_strict": false, "numeric_tolerance": {"atol": 1e-07, "rtol": 1e-06}}, {"name": "turnover", "alias": "turnover", "semantic_type": "turnover", "required": true, "position": 6, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "total_fee", "alias": "total_fee", "semantic_type": "total_fee", "required": true, "position": 7, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "net_inflow", "alias": "net_inflow", "semantic_type": "net_inflow", "required": true, "position": 8, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "holding_market_value", "alias": "holding_market_value", "semantic_type": "holding_market_value", "required": true, "position": 9, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "asset_rank_in_company", "alias": "asset_rank_in_company", "semantic_type": "asset_rank_in_company", "required": true, "position": 10, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}], "group_by": ["branch.up_org_name", "branch.org_name", "cust.org_id"], "eligibility_filters": [], "snapshot_policy": {"客户归属": "20260531", "期末资产和持仓": "2026年3月31日", "期末资产": "20260331", "期末持仓": "20260331", "ads_cust_info_d": "20260531", "dim_branch": "20260531", "dws_cust_aset_d": "20260331", "dwd_cust_hold_d": "20260331", "dwd_cust_tran_d": "20260101 to 20260331", "dws_cust_fin_d": "20260101 to 20260331"}, "missing_fact_policy": {"交易记录": "zero_fill_after_aggregation", "资金记录": "zero_fill_after_aggregation", "资产记录": "zero_fill_after_aggregation", "持仓记录": "zero_fill_after_aggregation"}, "dictionary_translation": [], "window": [{"function": "dense_rank", "partition_by": ["up_org_name"], "order_by": [{"expression": "total_asset", "direction": "desc"}], "tie_breaker": []}], "order_by": [], "top_n": 3, "expect_nonempty": true, "join_contract": [{"table": "dim_branch", "join_type": "inner"}], "calculation_notes": ["营业部客户数以客户快照为母集；交易、资金数据缺失按0。", "活跃客户率为一季度交易额大于0的客户数除以营业部客户数。", "在各分公司内部按期末总资产排名。"], "strategy": "llm_text_to_sql", "matched_query_id": null}`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> repair_sql -> validate_sql -> repair_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

SQL generation timeline:

| Attempt | Type | Status | Started UTC | Completed UTC | Elapsed ms | Model |
|---------|------|--------|-------------|---------------|------------|-------|
| 1 | initial | failed | 2026-07-31T16:00:44.848989+00:00 | 2026-07-31T16:04:46.652190+00:00 | 241802.69 |  |
| 2 | repair | ok | 2026-07-31T16:04:46.707560+00:00 | 2026-07-31T16:10:48.629595+00:00 | 361921.25 | deepseek-v4-pro |
| 3 | repair | ok | 2026-07-31T16:10:48.701860+00:00 | 2026-07-31T16:11:06.068520+00:00 | 17363.95 | deepseek-v4-pro |

SQL attempt 1 (initial):

```sql

```

SQL attempt 2 (repair):

```sql
WITH cust_base AS (
  SELECT pty_id, org_id FROM ads_cust_info_d WHERE data_dt = '20260531'
),
cust_asset AS (
  SELECT pty_id, (COALESCE(nm_tot_aset, 0) + COALESCE(fc_pur_aset, 0)) AS total_asset
  FROM dws_cust_aset_d
  WHERE data_dt = '20260331'
),
cust_tran_agg AS (
  SELECT pty_id,
    SUM(COALESCE(buy_amt, 0) + COALESCE(sell_amt, 0)) AS turnover,
    SUM(COALESCE(buy_rake, 0) + COALESCE(sell_rake, 0) + COALESCE(buy_fare, 0) + COALESCE(sell_fare, 0)) AS total_fee
  FROM dwd_cust_tran_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY pty_id
),
cust_fin_agg AS (
  SELECT pty_id,
    SUM(COALESCE(cash_in, 0) - COALESCE(cash_out, 0)) AS net_inflow
  FROM dws_cust_fin_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY pty_id
),
cust_hold_agg AS (
  SELECT pty_id,
    SUM(COALESCE(mkt_val, 0)) AS holding_market_value
  FROM dwd_cust_hold_d
  WHERE data_dt = '20260331'
  GROUP BY pty_id
),
cust_full AS (
  SELECT
    cb.pty_id,
    cb.org_id,
    COALESCE(ca.total_asset, 0) AS total_asset,
    COALESCE(ct.turnover, 0) AS turnover,
    COALESCE(ct.total_fee, 0) AS total_fee,
    COALESCE(cf.net_inflow, 0) AS net_inflow,
    COALESCE(ch.holding_market_value, 0) AS holding_market_value,
    CASE WHEN ct.turnover > 0 THEN 1 ELSE 0 END AS is_active
  FROM cust_base cb
  LEFT JOIN cust_asset ca ON cb.pty_id = ca.pty_id
  LEFT JOIN cust_tran_agg ct ON cb.pty_id = ct.pty_id
  LEFT JOIN cust_fin_agg cf ON cb.pty_id = cf.pty_id
  LEFT JOIN cust_hold_agg ch ON cb.pty_id = ch.pty_id
),
branch_metrics AS (
  SELECT
    branch.up_org_name,
    branch.org_name,
    COUNT(DISTINCT cf.pty_id) AS customer_count,
    SUM(cf.total_asset) AS total_asset,
    CAST(SUM(cf.is_active) AS DOUBLE) / NULLIF(COUNT(DISTINCT cf.pty_id), 0) AS active_customer_rate,
    SUM(cf.turnover) AS turnover,
    SUM(cf.total_fee) AS total_fee,
    SUM(cf.net_inflow) AS net_inflow,
    SUM(cf.holding_market_value) AS holding_market_value
  FROM cust_full cf
  INNER JOIN dim_branch branch ON cf.org_id = branch.org_id AND branch.data_dt = '20260531'
  GROUP BY branch.up_org_name, branch.org_name
),
ranked AS (
  SELECT *,
    DENSE_RANK() OVER (PARTITION BY up_org_name ORDER BY total_asset DESC) AS asset_rank_in_company
  FROM branch_metrics
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
  asset_rank_in_company
FROM ranked
WHERE asset_rank_in_company <= 3
```

SQL attempt 3 (repair):

```sql
WITH cust_base AS (
  SELECT pty_id, org_id FROM ads_cust_info_d WHERE data_dt = '20260531'
),
cust_asset AS (
  SELECT pty_id, (COALESCE(nm_tot_aset, 0) + COALESCE(fc_pur_aset, 0)) AS total_asset
  FROM dws_cust_aset_d
  WHERE data_dt = '20260331'
),
cust_tran_agg AS (
  SELECT pty_id,
    SUM(COALESCE(buy_amt, 0) + COALESCE(sell_amt, 0)) AS turnover,
    SUM(COALESCE(buy_rake, 0) + COALESCE(sell_rake, 0) + COALESCE(buy_fare, 0) + COALESCE(sell_fare, 0)) AS total_fee
  FROM dwd_cust_tran_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY pty_id
),
cust_fin_agg AS (
  SELECT pty_id,
    SUM(COALESCE(cash_in, 0) - COALESCE(cash_out, 0) + COALESCE(tran_in, 0) - COALESCE(tran_out, 0) + COALESCE(assign_in, 0) - COALESCE(assign_out, 0)) AS net_inflow
  FROM dws_cust_fin_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY pty_id
),
cust_hold_agg AS (
  SELECT pty_id,
    SUM(COALESCE(mkt_val, 0)) AS holding_market_value
  FROM dwd_cust_hold_d
  WHERE data_dt = '20260331'
  GROUP BY pty_id
),
cust_full AS (
  SELECT
    cb.pty_id,
    cb.org_id,
    COALESCE(ca.total_asset, 0) AS total_asset,
    COALESCE(ct.turnover, 0) AS turnover,
    COALESCE(ct.total_fee, 0) AS total_fee,
    COALESCE(cf.net_inflow, 0) AS net_inflow,
    COALESCE(ch.holding_market_value, 0) AS holding_market_value,
    CASE WHEN ct.turnover > 0 THEN 1 ELSE 0 END AS is_active
  FROM cust_base cb
  LEFT JOIN cust_asset ca ON cb.pty_id = ca.pty_id
  LEFT JOIN cust_tran_agg ct ON cb.pty_id = ct.pty_id
  LEFT JOIN cust_fin_agg cf ON cb.pty_id = cf.pty_id
  LEFT JOIN cust_hold_agg ch ON cb.pty_id = ch.pty_id
),
branch_metrics AS (
  SELECT
    branch.up_org_name,
    branch.org_name,
    COUNT(DISTINCT cf.pty_id) AS customer_count,
    SUM(cf.total_asset) AS total_asset,
    CAST(SUM(cf.is_active) AS DOUBLE) / NULLIF(COUNT(DISTINCT cf.pty_id), 0) AS active_customer_rate,
    SUM(cf.turnover) AS turnover,
    SUM(cf.total_fee) AS total_fee,
    SUM(cf.net_inflow) AS net_inflow,
    SUM(cf.holding_market_value) AS holding_market_value
  FROM cust_full cf
  INNER JOIN dim_branch branch ON cf.org_id = branch.org_id AND branch.data_dt = '20260531'
  GROUP BY branch.up_org_name, branch.org_name
),
ranked AS (
  SELECT *,
    DENSE_RANK() OVER (PARTITION BY up_org_name ORDER BY total_asset DESC) AS asset_rank_in_company
  FROM branch_metrics
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
  asset_rank_in_company
FROM ranked
WHERE asset_rank_in_company <= 3
```

Final candidate SQL:

```sql
WITH cust_base AS (
  SELECT pty_id, org_id FROM ads_cust_info_d WHERE data_dt = '20260531'
),
cust_asset AS (
  SELECT pty_id, (COALESCE(nm_tot_aset, 0) + COALESCE(fc_pur_aset, 0)) AS total_asset
  FROM dws_cust_aset_d
  WHERE data_dt = '20260331'
),
cust_tran_agg AS (
  SELECT pty_id,
    SUM(COALESCE(buy_amt, 0) + COALESCE(sell_amt, 0)) AS turnover,
    SUM(COALESCE(buy_rake, 0) + COALESCE(sell_rake, 0) + COALESCE(buy_fare, 0) + COALESCE(sell_fare, 0)) AS total_fee
  FROM dwd_cust_tran_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY pty_id
),
cust_fin_agg AS (
  SELECT pty_id,
    SUM(COALESCE(cash_in, 0) - COALESCE(cash_out, 0) + COALESCE(tran_in, 0) - COALESCE(tran_out, 0) + COALESCE(assign_in, 0) - COALESCE(assign_out, 0)) AS net_inflow
  FROM dws_cust_fin_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY pty_id
),
cust_hold_agg AS (
  SELECT pty_id,
    SUM(COALESCE(mkt_val, 0)) AS holding_market_value
  FROM dwd_cust_hold_d
  WHERE data_dt = '20260331'
  GROUP BY pty_id
),
cust_full AS (
  SELECT
    cb.pty_id,
    cb.org_id,
    COALESCE(ca.total_asset, 0) AS total_asset,
    COALESCE(ct.turnover, 0) AS turnover,
    COALESCE(ct.total_fee, 0) AS total_fee,
    COALESCE(cf.net_inflow, 0) AS net_inflow,
    COALESCE(ch.holding_market_value, 0) AS holding_market_value,
    CASE WHEN ct.turnover > 0 THEN 1 ELSE 0 END AS is_active
  FROM cust_base cb
  LEFT JOIN cust_asset ca ON cb.pty_id = ca.pty_id
  LEFT JOIN cust_tran_agg ct ON cb.pty_id = ct.pty_id
  LEFT JOIN cust_fin_agg cf ON cb.pty_id = cf.pty_id
  LEFT JOIN cust_hold_agg ch ON cb.pty_id = ch.pty_id
),
branch_metrics AS (
  SELECT
    branch.up_org_name,
    branch.org_name,
    COUNT(DISTINCT cf.pty_id) AS customer_count,
    SUM(cf.total_asset) AS total_asset,
    CAST(SUM(cf.is_active) AS DOUBLE) / NULLIF(COUNT(DISTINCT cf.pty_id), 0) AS active_customer_rate,
    SUM(cf.turnover) AS turnover,
    SUM(cf.total_fee) AS total_fee,
    SUM(cf.net_inflow) AS net_inflow,
    SUM(cf.holding_market_value) AS holding_market_value
  FROM cust_full cf
  INNER JOIN dim_branch branch ON cf.org_id = branch.org_id AND branch.data_dt = '20260531'
  GROUP BY branch.up_org_name, branch.org_name
),
ranked AS (
  SELECT *,
    DENSE_RANK() OVER (PARTITION BY up_org_name ORDER BY total_asset DESC) AS asset_rank_in_company
  FROM branch_metrics
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
  asset_rank_in_company
FROM ranked
WHERE asset_rank_in_company <= 3
```
