# Agent Evaluation Report

- SQL mode: `llm`
- Total cases: 3
- Agent completed rate: 2/3 (66.67%)
- Candidate SQL executable rate: 2/3 (66.67%)
- Exact result match rate: 0/3 (0.00%)
- Semantic result match rate: 1/3 (33.33%)
- Row count match rate: 2/3 (66.67%)
- Average execution elapsed: 37.37 ms
- SQL generation attempts: 3
- Total SQL generation elapsed: 124440.56 ms
- Average SQL generation attempt elapsed: 41480.19 ms
- LLM calls: 10
- LLM total tokens: 91247

| Query ID | Completed | Candidate SQL | Semantic | Strict Exact | Rows | Semantic Schema | SQL Gen Attempts | SQL Gen ms | Error Tags |
|----------|-----------|---------------|----------|--------------|------|-----------------|------------------|------------|------------|
| s028 | Y | Y | Y | N | 4/4 | Y | 1 | 34092.63 | order_only_difference |
| a004 | N | N | N | N | 0/14 | N | 0 | 0.00 | no_candidate_sql, clarification_false_positive, candidate_sql_execution_failed, row_count_mismatch, missing_output_column |
| a027 | Y | Y | N | N | 20/20 | N | 2 | 90347.93 | extra_output_column |

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
- Thread id: `eval:p1p2-smoke-20260731:r1:s028`
- SQL generation attempts: 1
- SQL generation elapsed: 34092.63 ms
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

SQL generation timeline:

| Attempt | Type | Status | Started UTC | Completed UTC | Elapsed ms | Model |
|---------|------|--------|-------------|---------------|------------|-------|
| 1 | initial | ok | 2026-07-31T10:54:50.578886+00:00 | 2026-07-31T10:55:24.674329+00:00 | 34092.63 | deepseek-v4-pro |

SQL attempt 1 (initial):

```sql
SELECT lvl."describe" AS customer_level, COUNT(DISTINCT hold.pty_id) AS customer_count, SUM(COALESCE(hold.mkt_val, 0)) AS credit_market_value FROM dwd_cust_hold_d hold INNER JOIN ads_cust_info_d cust ON hold.pty_id = cust.pty_id AND cust.data_dt = '20260531' LEFT JOIN dim_public lvl ON cust.cust_lvl_cd = lvl.code AND lvl.code_type_id = '100' WHERE hold.data_dt = '20260331' AND hold.sys_source = 'fc' GROUP BY lvl."describe"
```

Final candidate SQL:

```sql
SELECT lvl."describe" AS customer_level, COUNT(DISTINCT hold.pty_id) AS customer_count, SUM(COALESCE(hold.mkt_val, 0)) AS credit_market_value FROM dwd_cust_hold_d hold INNER JOIN ads_cust_info_d cust ON hold.pty_id = cust.pty_id AND cust.data_dt = '20260531' LEFT JOIN dim_public lvl ON cust.cust_lvl_cd = lvl.code AND lvl.code_type_id = '100' WHERE hold.data_dt = '20260331' AND hold.sys_source = 'fc' GROUP BY lvl."describe"
```

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
- Error type: `clarification_false_positive`
- Error tags: `['no_candidate_sql', 'clarification_false_positive', 'candidate_sql_execution_failed', 'row_count_mismatch', 'missing_output_column']`
- Thread id: `eval:p1p2-smoke-20260731:r1:a004`
- SQL generation attempts: 0
- SQL generation elapsed: 0.00 ms
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> ask_clarification -> persist_state`

Final candidate SQL:

```sql

```

### a027

- Question: 产品经理希望同时观察交易方向和期末沉淀。请按产品统计2026年一季度买入金额、卖出金额、净买入金额、交易客户数和交易客户覆盖的营业部数量，再补充3月31日持仓客户数与持仓市值。只保留买入或卖出金额大于0的产品。最终按净买入金额绝对值从高到低取前20只产品，并返回产品一级、二级分类；净买入为负表示净卖出。
- Executable: Y
- Agent completed: Y
- Semantic result match: N
- Exact match: N
- Standard rows: 20
- Agent rows: 20
- Standard columns: `['prdt_id', 'prdt_name', 'up_prdt_type_name', 'prdt_type_name', 'buy_amount', 'sell_amount', 'net_buy_amount', 'trading_customer_count', 'branch_coverage', 'holder_count', 'market_value']`
- Agent columns: `['prod_code', 'prod_lvl1_type', 'prod_lvl2_type', 'buy_amt', 'sell_amt', 'net_buy_amt', 'trade_cust_cnt', 'branch_cnt', 'hold_cust_cnt', 'hold_mkt_val', 'prdt_id', 'prdt_name', 'up_prdt_type_name', 'prdt_type_name', 'buy_amount', 'sell_amount', 'net_buy_amount', 'trading_customer_count', 'branch_coverage', 'holder_count', 'market_value']`
- Semantic column mapping: `{'prdt_id': 'prdt_id', 'prdt_name': 'prdt_name', 'up_prdt_type_name': 'up_prdt_type_name', 'prdt_type_name': 'prdt_type_name', 'buy_amount': 'buy_amount', 'sell_amount': 'sell_amount', 'net_buy_amount': 'net_buy_amount', 'trading_customer_count': 'trading_customer_count', 'branch_coverage': 'branch_coverage', 'holder_count': 'holder_count', 'market_value': 'market_value'}`
- Error type: `extra_output_column`
- Error tags: `['extra_output_column']`
- Thread id: `eval:p1p2-smoke-20260731:r1:a027`
- SQL generation attempts: 2
- SQL generation elapsed: 90347.93 ms
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> repair_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

SQL generation timeline:

| Attempt | Type | Status | Started UTC | Completed UTC | Elapsed ms | Model |
|---------|------|--------|-------------|---------------|------------|-------|
| 1 | initial | ok | 2026-07-31T11:01:16.203816+00:00 | 2026-07-31T11:02:08.677822+00:00 | 52471.00 | deepseek-v4-pro |
| 2 | repair | ok | 2026-07-31T11:02:08.731532+00:00 | 2026-07-31T11:02:46.608511+00:00 | 37876.93 | deepseek-v4-pro |

SQL attempt 1 (initial):

```sql
WITH trade AS (
    SELECT 
        tran.prdt_id,
        SUM(COALESCE(buy_amt, 0)) AS buy_amount,
        SUM(COALESCE(sell_amt, 0)) AS sell_amount,
        COUNT(DISTINCT tran.pty_id) AS trading_customer_count,
        COUNT(DISTINCT CASE WHEN branch.org_id IS NOT NULL THEN branch.org_id END) AS branch_coverage
    FROM dwd_cust_tran_d tran
    LEFT JOIN ads_cust_info_d cust ON tran.pty_id = cust.pty_id AND cust.data_dt = '20260531'
    LEFT JOIN dim_branch branch ON cust.org_id = branch.org_id AND branch.data_dt = '20260531'
    WHERE tran.data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY tran.prdt_id
),
holding AS (
    SELECT 
        prdt_id,
        COUNT(DISTINCT pty_id) AS holder_count,
        SUM(COALESCE(mkt_val, 0)) AS market_value
    FROM dwd_cust_hold_d
    WHERE data_dt = '20260331'
    GROUP BY prdt_id
)
SELECT 
    t.prdt_id,
    p.prdt_name,
    p.up_prdt_type_name,
    p.prdt_type_name,
    t.buy_amount,
    t.sell_amount,
    (t.buy_amount - t.sell_amount) AS net_buy_amount,
    t.trading_customer_count,
    t.branch_coverage,
    COALESCE(h.holder_count, 0) AS holder_count,
    COALESCE(h.market_value, 0) AS market_value
FROM trade t
INNER JOIN dim_product p ON t.prdt_id = p.prdt_id
LEFT JOIN holding h ON t.prdt_id = h.prdt_id
WHERE t.buy_amount > 0 OR t.sell_amount > 0
ORDER BY ABS(t.buy_amount - t.sell_amount) DESC
LIMIT 20
```

SQL attempt 2 (repair):

```sql
WITH trade AS (
    SELECT 
        tran.prdt_id,
        SUM(COALESCE(buy_amt, 0)) AS buy_amount,
        SUM(COALESCE(sell_amt, 0)) AS sell_amount,
        COUNT(DISTINCT tran.pty_id) AS trading_customer_count,
        COUNT(DISTINCT CASE WHEN branch.org_id IS NOT NULL THEN branch.org_id END) AS branch_coverage
    FROM dwd_cust_tran_d tran
    LEFT JOIN ads_cust_info_d cust ON tran.pty_id = cust.pty_id AND cust.data_dt = '20260531'
    LEFT JOIN dim_branch branch ON cust.org_id = branch.org_id AND branch.data_dt = '20260531'
    WHERE tran.data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY tran.prdt_id
),
holding AS (
    SELECT 
        prdt_id,
        COUNT(DISTINCT pty_id) AS holder_count,
        SUM(COALESCE(mkt_val, 0)) AS market_value
    FROM dwd_cust_hold_d
    WHERE data_dt = '20260331'
    GROUP BY prdt_id
)
SELECT 
    p.sor_prdt_id AS prod_code,
    p.up_prdt_type_name AS prod_lvl1_type,
    p.prdt_type_name AS prod_lvl2_type,
    t.buy_amount AS buy_amt,
    t.sell_amount AS sell_amt,
    (t.buy_amount - t.sell_amount) AS net_buy_amt,
    t.trading_customer_count AS trade_cust_cnt,
    t.branch_coverage AS branch_cnt,
    COALESCE(h.holder_count, 0) AS hold_cust_cnt,
    COALESCE(h.market_value, 0) AS hold_mkt_val,
    t.prdt_id,
    p.prdt_name,
    p.up_prdt_type_name,
    p.prdt_type_name,
    t.buy_amount,
    t.sell_amount,
    (t.buy_amount - t.sell_amount) AS net_buy_amount,
    t.trading_customer_count,
    t.branch_coverage,
    COALESCE(h.holder_count, 0) AS holder_count,
    COALESCE(h.market_value, 0) AS market_value
FROM trade t
INNER JOIN dim_product p ON t.prdt_id = p.prdt_id
LEFT JOIN holding h ON t.prdt_id = h.prdt_id
WHERE t.buy_amount > 0 OR t.sell_amount > 0
ORDER BY ABS(t.buy_amount - t.sell_amount) DESC
LIMIT 20
```

Final candidate SQL:

```sql
WITH trade AS (
    SELECT 
        tran.prdt_id,
        SUM(COALESCE(buy_amt, 0)) AS buy_amount,
        SUM(COALESCE(sell_amt, 0)) AS sell_amount,
        COUNT(DISTINCT tran.pty_id) AS trading_customer_count,
        COUNT(DISTINCT CASE WHEN branch.org_id IS NOT NULL THEN branch.org_id END) AS branch_coverage
    FROM dwd_cust_tran_d tran
    LEFT JOIN ads_cust_info_d cust ON tran.pty_id = cust.pty_id AND cust.data_dt = '20260531'
    LEFT JOIN dim_branch branch ON cust.org_id = branch.org_id AND branch.data_dt = '20260531'
    WHERE tran.data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY tran.prdt_id
),
holding AS (
    SELECT 
        prdt_id,
        COUNT(DISTINCT pty_id) AS holder_count,
        SUM(COALESCE(mkt_val, 0)) AS market_value
    FROM dwd_cust_hold_d
    WHERE data_dt = '20260331'
    GROUP BY prdt_id
)
SELECT 
    p.sor_prdt_id AS prod_code,
    p.up_prdt_type_name AS prod_lvl1_type,
    p.prdt_type_name AS prod_lvl2_type,
    t.buy_amount AS buy_amt,
    t.sell_amount AS sell_amt,
    (t.buy_amount - t.sell_amount) AS net_buy_amt,
    t.trading_customer_count AS trade_cust_cnt,
    t.branch_coverage AS branch_cnt,
    COALESCE(h.holder_count, 0) AS hold_cust_cnt,
    COALESCE(h.market_value, 0) AS hold_mkt_val,
    t.prdt_id,
    p.prdt_name,
    p.up_prdt_type_name,
    p.prdt_type_name,
    t.buy_amount,
    t.sell_amount,
    (t.buy_amount - t.sell_amount) AS net_buy_amount,
    t.trading_customer_count,
    t.branch_coverage,
    COALESCE(h.holder_count, 0) AS holder_count,
    COALESCE(h.market_value, 0) AS market_value
FROM trade t
INNER JOIN dim_product p ON t.prdt_id = p.prdt_id
LEFT JOIN holding h ON t.prdt_id = h.prdt_id
WHERE t.buy_amount > 0 OR t.sell_amount > 0
ORDER BY ABS(t.buy_amount - t.sell_amount) DESC
LIMIT 20
```
