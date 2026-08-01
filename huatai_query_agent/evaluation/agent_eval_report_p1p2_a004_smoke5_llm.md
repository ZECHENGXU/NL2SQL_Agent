# Agent Evaluation Report

- SQL mode: `llm`
- Total cases: 1
- Agent completed rate: 0/1 (0.00%)
- Candidate SQL executable rate: 1/1 (100.00%)
- Exact result match rate: 0/1 (0.00%)
- Semantic result match rate: 0/1 (0.00%)
- Row count match rate: 1/1 (100.00%)
- Average execution elapsed: 18843.28 ms
- SQL generation attempts: 3
- Total SQL generation elapsed: 219783.08 ms
- Average SQL generation attempt elapsed: 73261.03 ms
- LLM calls: 6
- LLM total tokens: 100128

| Query ID | Completed | Candidate SQL | Semantic | Strict Exact | Rows | Semantic Schema | SQL Gen Attempts | SQL Gen ms | Error Tags |
|----------|-----------|---------------|----------|--------------|------|-----------------|------------------|------------|------------|
| a004 | N | Y | N | N | 14/14 | Y | 3 | 219783.08 | validator_false_positive, population_join_mismatch, missing_period_policy_violation, semantic_value_error |

## Case Details

### a004

- Question: 区域负责人希望做一张营业部经营对比表。请以2026年5月31日客户归属为准，以营业部全部客户作为统计母集，计算每个营业部的客户数、2026年3月31日期末总资产、一季度有交易金额的活跃客户率、一季度买卖交易额、佣金及费用合计、资金净流入和期末持仓市值。交易或资金记录不存在时按0计算。最后在每个分公司内部按照期末总资产从高到低进行排名，只返回总资产最高的前3个营业部；同一分公司内并列时使用dense rank，不要强行打散并列名次。
- Executable: Y
- Agent completed: N
- Semantic result match: N
- Exact match: N
- Standard rows: 14
- Agent rows: 14
- Standard columns: `['up_org_name', 'org_name', 'customer_count', 'total_asset', 'active_customer_rate', 'turnover', 'total_fee', 'net_inflow', 'holding_market_value', 'asset_rank_in_company']`
- Agent columns: `['up_org_name', 'org_name', 'customer_count', 'total_asset', 'active_customer_rate', 'turnover', 'total_fee', 'net_inflow', 'holding_market_value', 'asset_rank_in_company']`
- Semantic column mapping: `{'up_org_name': 'up_org_name', 'org_name': 'org_name', 'customer_count': 'customer_count', 'total_asset': 'total_asset', 'active_customer_rate': 'active_customer_rate', 'turnover': 'turnover', 'total_fee': 'total_fee', 'net_inflow': 'net_inflow', 'holding_market_value': 'holding_market_value', 'asset_rank_in_company': 'asset_rank_in_company'}`
- Error type: `validator_false_positive`
- Error tags: `['validator_false_positive', 'population_join_mismatch', 'missing_period_policy_violation', 'semantic_value_error']`
- Final answer: 查询未能自动完成，已进入人工复核路径。原因：Join contract requires LEFT JOIN asset, but SQL uses ['no physical join'].; Join contract requires LEFT JOIN trade, but SQL uses ['no physical join'].; Join contract requires LEFT JOIN flow, but SQL uses ['no physical join'].; Join contract requires LEFT JOIN holding, but SQL uses ['no physical join'].; Missing period policy is zero_fill, but SQL has no period scaffold or full-outer zero-fill strategy.
- Thread id: `eval:p1p2-a004-smoke5-20260731:r1:a004`
- SQL generation attempts: 3
- SQL generation elapsed: 219783.08 ms
- SQL plan: `{"target": "营业部经营对比表，显示每个分公司内按期末总资产排名前三的营业部，包含客户数、期末总资产、活跃客户率、买卖交易额、佣金及费用合计、资金净流入、期末持仓市值", "tables": ["ads_cust_info_d", "dim_branch", "dws_cust_aset_d", "dws_cust_fin_d", "dwd_cust_tran_d", "dwd_cust_hold_d"], "joins": ["客户母集：ads_cust_info_d 快照 20260531", "左连接 dim_branch on org_id and branch.data_dt='20260531' 获取分公司/营业部名称", "左连接 dws_cust_aset_d on pty_id and asset.data_dt='20260331' 获取期末总资产", "客户级交易汇总（一季度）：dwd_cust_tran_d group by pty_id, sum(turnover, fee) -> cust_trade，左连接客户母集", "客户级资金汇总（一季度）：dws_cust_fin_d group by pty_id, sum(net_inflow) -> cust_fin，左连接客户母集", "客户级持仓汇总（期末）：dwd_cust_hold_d group by pty_id, sum(mkt_val) -> cust_hold，左连接客户母集"], "filters": ["ads_cust_info_d.data_dt = '20260531'", "dim_branch.data_dt = '20260531'", "dws_cust_aset_d.data_dt = '20260331'", "交易、资金区间数据：'20260101' <= data_dt <= '20260331'", "无产品、客户状态等额外筛选"], "metrics": ["customer_count = count(c.pty_id)", "total_asset = sum(coalesce(a.nm_tot_aset,0) + coalesce(a.fc_pur_aset,0))", "active_customer_rate = 1.0 * sum(case when t.turnover > 0 then 1 else 0 end) / count(c.pty_id)", "turnover = sum(coalesce(t.turnover,0))", "total_fee = sum(coalesce(t.total_fee,0))", "net_inflow = sum(coalesce(f.net_inflow,0))", "holding_market_value = sum(coalesce(h.total_hold_mv,0))", "asset_rank_in_company = dense_rank() over (partition by b.up_org_name order by sum(coalesce(a.nm_tot_aset,0) + coalesce(a.fc_pur_aset,0)) desc)"], "population": "以2026年5月31日客户归属为准的营业部全部客户（ads_cust_info_d.data_dt='20260531'）", "grain": ["up_org_name", "org_name"], "output_columns": [{"name": "up_org_name", "alias": "up_org_name", "semantic_type": "up_org_name", "required": true, "position": 1, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "org_name", "alias": "org_name", "semantic_type": "org_name", "required": true, "position": 2, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "customer_count", "alias": "customer_count", "semantic_type": "customer_count", "required": true, "position": 3, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "total_asset", "alias": "total_asset", "semantic_type": "total_asset", "required": true, "position": 4, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "active_customer_rate", "alias": "active_customer_rate", "semantic_type": "active_customer_rate", "required": true, "position": 5, "alias_strict": false, "numeric_tolerance": {"atol": 1e-07, "rtol": 1e-06}}, {"name": "turnover", "alias": "turnover", "semantic_type": "turnover", "required": true, "position": 6, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "total_fee", "alias": "total_fee", "semantic_type": "total_fee", "required": true, "position": 7, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "net_inflow", "alias": "net_inflow", "semantic_type": "net_inflow", "required": true, "position": 8, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "holding_market_value", "alias": "holding_market_value", "semantic_type": "holding_market_value", "required": true, "position": 9, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}, {"name": "asset_rank_in_company", "alias": "asset_rank_in_company", "semantic_type": "asset_rank_in_company", "required": true, "position": 10, "alias_strict": false, "numeric_tolerance": {"atol": 1e-08, "rtol": 1e-09}}], "group_by": ["up_org_name", "org_name"], "eligibility_filters": [], "snapshot_policy": {"客户归属": "20260531", "期末总资产": "20260331", "期末持仓市值": "20260331", "ads_cust_info_d": "20260531", "dim_branch": "20260531", "dws_cust_aset_d": "20260331", "dwd_cust_hold_d": "20260331", "dwd_cust_tran_d": "20260101-20260331", "dws_cust_fin_d": "20260101-20260331"}, "missing_fact_policy": {"turnover": "zero_fill", "total_fee": "zero_fill", "net_inflow": "zero_fill", "holding_market_value": "zero_fill", "total_asset": "zero_fill"}, "missing_period_policy": "zero_fill", "dictionary_translation": [], "window": [{"function": "dense_rank", "partition_by": ["up_org_name"], "order_by": [{"expression": "total_asset", "direction": "desc"}], "tie_breaker": []}], "order_by": [{"expression": "up_org_name", "direction": "asc", "nulls": "last"}, {"expression": "asset_rank_in_company", "direction": "asc", "nulls": "last"}], "top_n": 3, "expect_nonempty": true, "join_contract": [{"table": "dim_branch", "join_type": "inner"}, {"table": "asset", "join_type": "left"}, {"table": "trade", "join_type": "left"}, {"table": "flow", "join_type": "left"}, {"table": "holding", "join_type": "left"}], "calculation_notes": ["营业部客户数以客户快照为母集；交易、资金数据缺失按0。", "活跃客户率为一季度交易额大于0的客户数除以营业部客户数。", "在各分公司内部按期末总资产排名。"], "strategy": "llm_text_to_sql", "matched_query_id": null}`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> repair_sql -> validate_sql -> repair_sql -> validate_sql -> human_review_or_explain -> persist_state`

SQL generation timeline:

| Attempt | Type | Status | Started UTC | Completed UTC | Elapsed ms | Model |
|---------|------|--------|-------------|---------------|------------|-------|
| 1 | initial | ok | 2026-07-31T15:10:34.340489+00:00 | 2026-07-31T15:11:13.037200+00:00 | 38692.82 | deepseek-v4-pro |
| 2 | repair | ok | 2026-07-31T15:11:13.117980+00:00 | 2026-07-31T15:12:07.203471+00:00 | 54084.73 | deepseek-v4-pro |
| 3 | repair | ok | 2026-07-31T15:12:07.270913+00:00 | 2026-07-31T15:14:14.279926+00:00 | 127005.53 | deepseek-v4-pro |

SQL attempt 1 (initial):

```sql
WITH cust_base AS (
    SELECT c.pty_id, c.org_id, b.up_org_name, b.org_name
    FROM ads_cust_info_d c
    INNER JOIN dim_branch b ON c.org_id = b.org_id AND b.data_dt = '20260531'
    WHERE c.data_dt = '20260531'
),
asset_eop AS (
    SELECT pty_id,
           COALESCE(nm_tot_aset, 0) + COALESCE(fc_pur_aset, 0) AS total_asset
    FROM dws_cust_aset_d
    WHERE data_dt = '20260331'
),
trade_q1 AS (
    SELECT pty_id,
           SUM(COALESCE(buy_amt, 0) + COALESCE(sell_amt, 0)) AS turnover,
           SUM(COALESCE(buy_rake, 0) + COALESCE(buy_fare, 0) + COALESCE(sell_rake, 0) + COALESCE(sell_fare, 0)) AS total_fee
    FROM dwd_cust_tran_d
    WHERE data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY pty_id
),
fin_q1 AS (
    SELECT pty_id,
           SUM(COALESCE(cash_in, 0) - COALESCE(cash_out, 0)) AS net_inflow
    FROM dws_cust_fin_d
    WHERE data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY pty_id
),
hold_eop AS (
    SELECT pty_id,
           SUM(COALESCE(mkt_val, 0)) AS holding_market_value
    FROM dwd_cust_hold_d
    WHERE data_dt = '20260331'
    GROUP BY pty_id
),
branch_agg AS (
    SELECT
        cb.up_org_name,
        cb.org_name,
        COUNT(cb.pty_id) AS customer_count,
        COALESCE(SUM(a.total_asset), 0) AS total_asset,
        1.0 * SUM(CASE WHEN COALESCE(t.turnover, 0) > 0 THEN 1 ELSE 0 END) / COUNT(cb.pty_id) AS active_customer_rate,
        COALESCE(SUM(t.turnover), 0) AS turnover,
        COALESCE(SUM(t.total_fee), 0) AS total_fee,
        COALESCE(SUM(f.net_inflow), 0) AS net_inflow,
        COALESCE(SUM(h.holding_market_value), 0) AS holding_market_value
    FROM cust_base cb
    LEFT JOIN asset_eop a ON cb.pty_id = a.pty_id
    LEFT JOIN trade_q1 t ON cb.pty_id = t.pty_id
    LEFT JOIN fin_q1 f ON cb.pty_id = f.pty_id
    LEFT JOIN hold_eop h ON cb.pty_id = h.pty_id
    GROUP BY cb.up_org_name, cb.org_name
),
ranked AS (
    SELECT *,
           DENSE_RANK() OVER (PARTITION BY up_org_name ORDER BY total_asset DESC) AS asset_rank_in_company
    FROM branch_agg
)
SELECT up_org_name, org_name, customer_count, total_asset, active_customer_rate, turnover, total_fee, net_inflow, holding_market_value, asset_rank_in_company
FROM ranked
WHERE asset_rank_in_company <= 3
ORDER BY up_org_name ASC, asset_rank_in_company ASC
```

SQL attempt 2 (repair):

```sql
SELECT up_org_name, org_name, customer_count, total_asset, active_customer_rate, turnover, total_fee, net_inflow, holding_market_value, asset_rank_in_company FROM ( SELECT up_org_name, org_name, customer_count, total_asset, active_customer_rate, turnover, total_fee, net_inflow, holding_market_value, DENSE_RANK() OVER (PARTITION BY up_org_name ORDER BY total_asset DESC) AS asset_rank_in_company FROM ( SELECT cb.up_org_name, cb.org_name, COUNT(cb.pty_id) AS customer_count, COALESCE(SUM(asset.total_asset), 0) AS total_asset, 1.0 * SUM(CASE WHEN COALESCE(trade.turnover, 0) > 0 THEN 1 ELSE 0 END) / COUNT(cb.pty_id) AS active_customer_rate, COALESCE(SUM(trade.turnover), 0) AS turnover, COALESCE(SUM(trade.total_fee), 0) AS total_fee, COALESCE(SUM(flow.net_inflow), 0) AS net_inflow, COALESCE(SUM(holding.holding_market_value), 0) AS holding_market_value FROM ( SELECT c.pty_id, c.org_id, b.up_org_name, b.org_name FROM ads_cust_info_d c INNER JOIN dim_branch b ON c.org_id = b.org_id AND b.data_dt = '20260531' WHERE c.data_dt = '20260531' ) AS cb LEFT JOIN ( SELECT pty_id, COALESCE(nm_tot_aset, 0) + COALESCE(fc_pur_aset, 0) AS total_asset FROM dws_cust_aset_d WHERE data_dt = '20260331' ) AS asset ON cb.pty_id = asset.pty_id LEFT JOIN ( SELECT pty_id, SUM(COALESCE(buy_amt, 0) + COALESCE(sell_amt, 0)) AS turnover, SUM(COALESCE(buy_rake, 0) + COALESCE(buy_fare, 0) + COALESCE(sell_rake, 0) + COALESCE(sell_fare, 0)) AS total_fee FROM dwd_cust_tran_d WHERE data_dt BETWEEN '20260101' AND '20260331' GROUP BY pty_id ) AS trade ON cb.pty_id = trade.pty_id LEFT JOIN ( SELECT pty_id, SUM(COALESCE(cash_in, 0) - COALESCE(cash_out, 0)) AS net_inflow FROM dws_cust_fin_d WHERE data_dt BETWEEN '20260101' AND '20260331' GROUP BY pty_id ) AS flow ON cb.pty_id = flow.pty_id LEFT JOIN ( SELECT pty_id, SUM(COALESCE(mkt_val, 0)) AS holding_market_value FROM dwd_cust_hold_d WHERE data_dt = '20260331' GROUP BY pty_id ) AS holding ON cb.pty_id = holding.pty_id GROUP BY cb.up_org_name, cb.org_name ) AS branch_agg ) AS ranked WHERE asset_rank_in_company <= 3 ORDER BY up_org_name ASC, asset_rank_in_company ASC
```

SQL attempt 3 (repair):

```sql
SELECT up_org_name, org_name, customer_count, total_asset, active_customer_rate, turnover, total_fee, net_inflow, holding_market_value, asset_rank_in_company FROM ( SELECT up_org_name, org_name, customer_count, total_asset, active_customer_rate, turnover, total_fee, net_inflow, holding_market_value, DENSE_RANK() OVER (PARTITION BY up_org_name ORDER BY total_asset DESC) AS asset_rank_in_company FROM ( SELECT b.up_org_name, b.org_name, COUNT(DISTINCT c.pty_id) AS customer_count, COALESCE(SUM(COALESCE(a.nm_tot_aset,0) + COALESCE(a.fc_pur_aset,0)), 0) AS total_asset, COUNT(DISTINCT CASE WHEN COALESCE(t.buy_amt,0) + COALESCE(t.sell_amt,0) > 0 THEN c.pty_id END) * 1.0 / COUNT(DISTINCT c.pty_id) AS active_customer_rate, COALESCE(SUM(COALESCE(t.buy_amt,0) + COALESCE(t.sell_amt,0)), 0) AS turnover, COALESCE(SUM(COALESCE(t.buy_rake,0) + COALESCE(t.buy_fare,0) + COALESCE(t.sell_rake,0) + COALESCE(t.sell_fare,0)), 0) AS total_fee, COALESCE(SUM(COALESCE(f.cash_in,0) - COALESCE(f.cash_out,0)), 0) AS net_inflow, COALESCE(SUM(COALESCE(h.mkt_val,0)), 0) AS holding_market_value FROM ads_cust_info_d c INNER JOIN dim_branch b ON c.org_id = b.org_id AND b.data_dt = '20260531' LEFT JOIN dws_cust_aset_d a ON c.pty_id = a.pty_id AND a.data_dt = '20260331' LEFT JOIN dwd_cust_tran_d t ON c.pty_id = t.pty_id AND t.data_dt BETWEEN '20260101' AND '20260331' LEFT JOIN dws_cust_fin_d f ON c.pty_id = f.pty_id AND f.data_dt BETWEEN '20260101' AND '20260331' LEFT JOIN dwd_cust_hold_d h ON c.pty_id = h.pty_id AND h.data_dt = '20260331' WHERE c.data_dt = '20260531' GROUP BY b.up_org_name, b.org_name ) AS branch_agg ) AS ranked WHERE asset_rank_in_company <= 3 ORDER BY up_org_name ASC, asset_rank_in_company ASC
```

Final candidate SQL:

```sql
SELECT up_org_name, org_name, customer_count, total_asset, active_customer_rate, turnover, total_fee, net_inflow, holding_market_value, asset_rank_in_company FROM ( SELECT up_org_name, org_name, customer_count, total_asset, active_customer_rate, turnover, total_fee, net_inflow, holding_market_value, DENSE_RANK() OVER (PARTITION BY up_org_name ORDER BY total_asset DESC) AS asset_rank_in_company FROM ( SELECT b.up_org_name, b.org_name, COUNT(DISTINCT c.pty_id) AS customer_count, COALESCE(SUM(COALESCE(a.nm_tot_aset,0) + COALESCE(a.fc_pur_aset,0)), 0) AS total_asset, COUNT(DISTINCT CASE WHEN COALESCE(t.buy_amt,0) + COALESCE(t.sell_amt,0) > 0 THEN c.pty_id END) * 1.0 / COUNT(DISTINCT c.pty_id) AS active_customer_rate, COALESCE(SUM(COALESCE(t.buy_amt,0) + COALESCE(t.sell_amt,0)), 0) AS turnover, COALESCE(SUM(COALESCE(t.buy_rake,0) + COALESCE(t.buy_fare,0) + COALESCE(t.sell_rake,0) + COALESCE(t.sell_fare,0)), 0) AS total_fee, COALESCE(SUM(COALESCE(f.cash_in,0) - COALESCE(f.cash_out,0)), 0) AS net_inflow, COALESCE(SUM(COALESCE(h.mkt_val,0)), 0) AS holding_market_value FROM ads_cust_info_d c INNER JOIN dim_branch b ON c.org_id = b.org_id AND b.data_dt = '20260531' LEFT JOIN dws_cust_aset_d a ON c.pty_id = a.pty_id AND a.data_dt = '20260331' LEFT JOIN dwd_cust_tran_d t ON c.pty_id = t.pty_id AND t.data_dt BETWEEN '20260101' AND '20260331' LEFT JOIN dws_cust_fin_d f ON c.pty_id = f.pty_id AND f.data_dt BETWEEN '20260101' AND '20260331' LEFT JOIN dwd_cust_hold_d h ON c.pty_id = h.pty_id AND h.data_dt = '20260331' WHERE c.data_dt = '20260531' GROUP BY b.up_org_name, b.org_name ) AS branch_agg ) AS ranked WHERE asset_rank_in_company <= 3 ORDER BY up_org_name ASC, asset_rank_in_company ASC
```
