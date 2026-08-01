# Agent 评测报告

- SQL 模式: `llm`
- 总用例数: 81
- 可执行率: 68/81 (83.95%)
- 精确结果匹配率: 5/81 (6.17%)
- 行数匹配率: 60/81 (74.07%)
- 平均执行耗时: 27.67 ms
- LLM 调用次数: 360
- LLM 总 Token 数: 2302907

| 查询 ID | 可执行 | 精确匹配 | 行数 | 字段 | 错误类型 |
|----------|------------|-------------|-----------|---------|------------|
| q001 | Y | Y | 1/1 | Y | 通过 |
| q002 | Y | N | 3/3 | N | 字段不匹配 |
| q003 | Y | N | 1/1 | N | 字段不匹配 |
| q004 | Y | N | 15/15 | Y | 行值不匹配 |
| q005 | Y | N | 1/1 | N | 字段不匹配 |
| q006 | Y | N | 24/24 | N | 字段不匹配 |
| q007 | Y | N | 3/3 | N | 字段不匹配 |
| v001 | Y | N | 1/1 | N | 字段不匹配 |
| v002 | Y | Y | 1/1 | Y | 通过 |
| v003 | Y | N | 3/3 | N | 字段不匹配 |
| v004 | Y | N | 5/3 | N | 行数不匹配 |
| v005 | Y | N | 1/1 | N | 字段不匹配 |
| v006 | Y | N | 1/1 | N | 字段不匹配 |
| v007 | Y | N | 15/15 | N | 字段不匹配 |
| v008 | Y | N | 15/15 | Y | 行值不匹配 |
| v009 | Y | N | 1/1 | N | 字段不匹配 |
| v010 | Y | N | 1/1 | N | 字段不匹配 |
| v011 | Y | N | 24/24 | N | 字段不匹配 |
| v012 | Y | N | 6/24 | N | 行数不匹配 |
| v013 | Y | N | 3/3 | N | 字段不匹配 |
| v014 | Y | N | 3/3 | N | 字段不匹配 |
| s001 | Y | N | 1/1 | N | 字段不匹配 |
| s002 | Y | N | 12/12 | N | 字段不匹配 |
| s003 | Y | N | 8/8 | N | 字段不匹配 |
| s004 | Y | N | 4/4 | N | 字段不匹配 |
| s005 | Y | N | 20/20 | N | 字段不匹配 |
| s006 | Y | N | 2/2 | Y | 行值不匹配 |
| s007 | Y | N | 5/5 | N | 字段不匹配 |
| s008 | Y | N | 10/10 | N | 字段不匹配 |
| s009 | Y | N | 20/20 | N | 字段不匹配 |
| s010 | Y | N | 8/8 | N | 字段不匹配 |
| s011 | Y | N | 10/10 | N | 字段不匹配 |
| s012 | Y | Y | 1/1 | Y | 通过 |
| s013 | Y | N | 4/4 | N | 字段不匹配 |
| s014 | Y | N | 10/10 | N | 字段不匹配 |
| s015 | Y | Y | 1/1 | Y | 通过 |
| s016 | Y | N | 1/1 | N | 字段不匹配 |
| s017 | Y | N | 0/6 | N | 行数不匹配 |
| s018 | Y | N | 6/6 | N | 字段不匹配 |
| s019 | Y | Y | 1/1 | Y | 通过 |
| s020 | Y | N | 10/10 | N | 字段不匹配 |
| s021 | Y | N | 3/3 | N | 字段不匹配 |
| s022 | Y | N | 10/10 | N | 字段不匹配 |
| s023 | Y | N | 4/4 | N | 字段不匹配 |
| s024 | Y | N | 10/10 | N | 字段不匹配 |
| s025 | Y | N | 4/4 | N | 字段不匹配 |
| s026 | Y | N | 6/6 | N | 字段不匹配 |
| s027 | Y | N | 10/10 | N | 字段不匹配 |
| s028 | N | N | 0/4 | N | agent_sql_execution_failed |
| s029 | Y | N | 20/15 | N | 行数不匹配 |
| s030 | Y | N | 10/10 | N | 字段不匹配 |
| a001 | Y | N | 20/20 | N | 字段不匹配 |
| a002 | N | N | 0/9 | N | agent_sql_execution_failed |
| a003 | Y | N | 20/20 | N | 字段不匹配 |
| a004 | N | N | 0/14 | N | agent_sql_execution_failed |
| a005 | Y | N | 20/20 | N | 字段不匹配 |
| a006 | N | N | 0/20 | N | agent_sql_execution_failed |
| a007 | Y | N | 20/20 | N | 字段不匹配 |
| a008 | N | N | 0/20 | N | agent_sql_execution_failed |
| a009 | Y | N | 15/15 | N | 字段不匹配 |
| a010 | Y | N | 73/44 | N | 行数不匹配 |
| a011 | Y | N | 17/17 | N | 字段不匹配 |
| a012 | Y | N | 20/15 | N | 行数不匹配 |
| a013 | N | N | 0/4 | N | agent_sql_execution_failed |
| a014 | Y | N | 20/20 | N | 字段不匹配 |
| a015 | Y | N | 6/6 | N | 字段不匹配 |
| a016 | Y | N | 20/20 | N | 字段不匹配 |
| a017 | Y | N | 13/12 | N | 行数不匹配 |
| a018 | N | N | 0/15 | N | agent_sql_execution_failed |
| a019 | Y | N | 0/20 | N | 行数不匹配 |
| a020 | N | N | 0/20 | N | agent_sql_execution_failed |
| a021 | Y | N | 20/20 | N | 字段不匹配 |
| a022 | N | N | 0/6 | N | agent_sql_execution_failed |
| a023 | Y | N | 9/9 | N | 字段不匹配 |
| a024 | N | N | 0/4 | N | agent_sql_execution_failed |
| a025 | N | N | 0/24 | N | agent_sql_execution_failed |
| a026 | N | N | 0/15 | N | agent_sql_execution_failed |
| a027 | Y | N | 20/20 | N | sql_validation_failed |
| a028 | Y | N | 20/20 | N | 字段不匹配 |
| a029 | N | N | 0/30 | N | agent_sql_execution_failed |
| a030 | Y | N | 20/20 | N | 字段不匹配 |

## 用例详情

### q001

- 问题: 学历本科以上的男性客户，年龄超过50岁的有多少个？
- 可执行: Y
- 精确匹配: Y
- 标准 SQL 行数: 1
- Agent SQL 行数: 1
- 标准 SQL 字段: `['customer_count']`
- Agent SQL 字段: `['customer_count']`
- 错误类型: `通过`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT COUNT(DISTINCT pty_id) AS customer_count FROM ads_cust_info_d WHERE data_dt = '20260531' AND edu_cd IN ('6000002', '6000003', '6000004') AND gender_cd = '5000002' AND cust_age > 50
```

### q002

- 问题: 不同年龄段的客户总资产分布情况如何？
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 3
- Agent SQL 行数: 3
- 标准 SQL 字段: `['cust_age_type', 'customer_count', 'total_asset']`
- Agent SQL 字段: `['age_group', 'total_asset']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT CASE WHEN cust.cust_age < 30 THEN '<30' WHEN cust.cust_age BETWEEN 30 AND 39 THEN '30-39' WHEN cust.cust_age BETWEEN 40 AND 49 THEN '40-49' WHEN cust.cust_age BETWEEN 50 AND 59 THEN '50-59' ELSE '>=60' END AS age_group, SUM(COALESCE(aset.nm_tot_aset, 0) + COALESCE(aset.fc_pur_aset, 0)) AS total_asset FROM ads_cust_info_d cust LEFT JOIN dws_cust_aset_d aset ON cust.pty_id = aset.pty_id AND aset.data_dt = '20260331' WHERE cust.data_dt = '20260531' GROUP BY age_group ORDER BY CASE age_group WHEN '<30' THEN 1 WHEN '30-39' THEN 2 WHEN '40-49' THEN 3 WHEN '50-59' THEN 4 ELSE 5 END
```

### q003

- 问题: 钻石卡男性客户、年龄大于40岁、持有比亚迪市值超过1000元，计算2026年Q1盈亏。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 1
- Agent SQL 行数: 1
- 标准 SQL 字段: `['pty_id', 'byd_mkt_val', 'begin_total_asset', 'end_total_asset', 'asset_in', 'asset_out', 'q1_盈亏分析']`
- Agent SQL 字段: `['pty_id', 'period_盈亏分析']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH customer_filter AS (
    SELECT pty_id
    FROM ads_cust_info_d
    WHERE data_dt = '20260531'
      AND cust_lvl_cd = '1000001'
      AND gender_cd = '5000002'
      AND cust_age > 40
),
by_hold AS (
    SELECT h.pty_id, SUM(COALESCE(h.mkt_val, 0)) AS hold_mkt_val
    FROM dwd_cust_hold_d h
    JOIN dim_product p ON h.prdt_id = p.prdt_id
    WHERE h.data_dt = '20260331'
      AND h.ccy = '0'
      AND p.prdt_name = '比亚迪'
      AND p.prdt_type_name = 'A股'
    GROUP BY h.pty_id
    HAVING SUM(COALESCE(h.mkt_val, 0)) > 1000
),
end_asset AS (
    SELECT pty_id, 
           COALESCE(nm_tot_aset, 0) + COALESCE(fc_pur_aset, 0) AS end_total_asset
    FROM dws_cust_aset_d
    WHERE data_dt = '20260331'
),
begin_asset AS (
    SELECT pty_id, 
           COALESCE(nm_tot_aset, 0) + COALESCE(fc_pur_aset, 0) AS begin_total_asset
    FROM dws_cust_aset_d
    WHERE data_dt = '20251231'
),
fin_flow AS (
    SELECT pty_id,
           SUM(COALESCE(cash_in, 0) + COALESCE(tran_in, 0) + COALESCE(assign_in, 0)) AS total_inflow,
           SUM(COALESCE(cash_out, 0) + COALESCE(tran_out, 0) + COALESCE(assign_out, 0)) AS total_outflow
    FROM dws_cust_fin_d
    WHERE data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY pty_id
)
SELECT cf.pty_id,
       COALESCE(e.end_total_asset, 0) - COALESCE(b.begin_total_asset, 0) + COALESCE(f.total_outflow, 0) - COALESCE(f.total_inflow, 0) AS period_profit_loss
FROM customer_filter cf
JOIN by_hold bh ON cf.pty_id = bh.pty_id
LEFT JOIN end_asset e ON cf.pty_id = e.pty_id
LEFT JOIN begin_asset b ON cf.pty_id = b.pty_id
LEFT JOIN fin_flow f ON cf.pty_id = f.pty_id
```

### q004

- 问题: 分公司和营业部的客户省份分布统计。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 15
- Agent SQL 行数: 15
- 标准 SQL 字段: `['up_org_name', 'org_name', 'prov_name', 'city_name', 'customer_count']`
- Agent SQL 字段: `['up_org_name', 'org_name', 'prov_name', 'city_name', 'customer_count']`
- 错误类型: `行值不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT branch.up_org_name, branch.org_name, cust.prov_name, cust.city_name, COUNT(DISTINCT cust.pty_id) AS customer_count FROM ads_cust_info_d cust LEFT JOIN dim_branch branch ON cust.org_id = branch.org_id WHERE cust.data_dt = '20260531' AND branch.data_dt = '20260531' GROUP BY branch.up_org_name, branch.org_name, cust.prov_name, cust.city_name ORDER BY branch.up_org_name, branch.org_name, cust.prov_name, cust.city_name
```

### q005

- 问题: 2026年Q1交易过招商银行A股，并且在Q1末普通账户持有中国平安A股的客户有哪些？
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 1
- Agent SQL 行数: 1
- 标准 SQL 字段: `['pty_id', 'cmb_transaction_amount', 'pingan_market_value']`
- Agent SQL 字段: `['pty_id']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> repair_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT pty_id FROM (SELECT DISTINCT t.pty_id FROM dwd_cust_tran_d t INNER JOIN dim_product p ON t.prdt_id = p.prdt_id WHERE p.prdt_name = '招商银行' AND p.prdt_type_name = 'A股' AND t.data_dt BETWEEN '20260101' AND '20260331' AND coalesce(t.buy_amt,0) + coalesce(t.sell_amt,0) > 0) AS traders INTERSECT SELECT pty_id FROM (SELECT DISTINCT h.pty_id FROM dwd_cust_hold_d h INNER JOIN dim_product p ON h.prdt_id = p.prdt_id WHERE p.prdt_name = '中国平安' AND p.prdt_type_name = 'A股' AND h.data_dt = '20260331' AND h.sys_source = 'nm') AS holders
```

### q006

- 问题: 2026年Q1日均资产大于30万，且股票交易金额大于10万的客户，持有哪些产品类型？
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 24
- Agent SQL 行数: 24
- 标准 SQL 字段: `['up_prdt_type_name', 'prdt_type_name', 'customer_count', 'total_market_value']`
- Agent SQL 字段: `['product_top_category', 'product_sub_category', 'total_holding_market_value']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH customer_asset AS (
  SELECT pty_id
  FROM dws_cust_aset_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY pty_id
  HAVING SUM(COALESCE(nm_tot_aset,0) + COALESCE(fc_pur_aset,0)) / 90 > 300000
),
customer_stock_trade AS (
  SELECT tran.pty_id
  FROM dwd_cust_tran_d tran
  INNER JOIN dim_product prdt ON tran.prdt_id = prdt.prdt_id
  WHERE tran.data_dt BETWEEN '20260101' AND '20260331'
    AND prdt.up_prdt_type_name = '股票'
  GROUP BY tran.pty_id
  HAVING SUM(COALESCE(buy_amt,0) + COALESCE(sell_amt,0)) > 100000
),
eligible_customers AS (
  SELECT a.pty_id FROM customer_asset a
  INNER JOIN customer_stock_trade t ON a.pty_id = t.pty_id
)
SELECT 
  prdt.up_prdt_type_name AS product_top_category,
  prdt.prdt_type_name AS product_sub_category,
  SUM(COALESCE(hold.mkt_val,0)) AS total_holding_market_value
FROM eligible_customers c
INNER JOIN dwd_cust_hold_d hold ON c.pty_id = hold.pty_id AND hold.data_dt = '20260331'
INNER JOIN dim_product prdt ON hold.prdt_id = prdt.prdt_id
GROUP BY prdt.up_prdt_type_name, prdt.prdt_type_name
ORDER BY total_holding_market_value DESC
```

### q007

- 问题: 查询2026年1月10日至2026年2月15日期间，科创板交易金额超过25万的客户营业部分布。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 3
- Agent SQL 行数: 3
- 标准 SQL 字段: `['up_org_name', 'org_name', 'customer_count', 'total_transaction_amount']`
- Agent SQL 字段: `['上级分公司', '营业部', '客户数']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH customer_total_trade AS (
  SELECT
    t.pty_id,
    SUM(COALESCE(t.buy_amt,0) + COALESCE(t.sell_amt,0)) AS total_trade_amt
  FROM dwd_cust_tran_d t
  INNER JOIN dim_product p ON t.prdt_id = p.prdt_id
  WHERE t.data_dt BETWEEN '20260110' AND '20260215'
    AND p.prdt_type_name = '科创板'
  GROUP BY t.pty_id
  HAVING SUM(COALESCE(t.buy_amt,0) + COALESCE(t.sell_amt,0)) > 250000
)
SELECT
  b.up_org_name AS 上级分公司,
  b.org_name AS 营业部,
  COUNT(DISTINCT cust.pty_id) AS 客户数
FROM customer_total_trade cust
INNER JOIN ads_cust_info_d info ON cust.pty_id = info.pty_id AND info.data_dt = '20260531'
LEFT JOIN dim_branch b ON info.org_id = b.org_id AND b.data_dt = '20260531'
GROUP BY b.up_org_name, b.org_name
ORDER BY b.up_org_name ASC, b.org_name ASC
```

### v001

- 问题: 本科及以上男性客户，年龄大于50岁的客户数是多少？
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 1
- Agent SQL 行数: 1
- 标准 SQL 字段: `['customer_count']`
- Agent SQL 字段: `['cust_cnt']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
select count(pty_id) as cust_cnt from ads_cust_info_d where data_dt = '20260531' and edu_cd in ('6000002','6000003','6000004') and gender_cd = '5000002' and cust_age > 50
```

### v002

- 问题: 统计男性、本科以上、50岁以上客户数量。
- 可执行: Y
- 精确匹配: Y
- 标准 SQL 行数: 1
- Agent SQL 行数: 1
- 标准 SQL 字段: `['customer_count']`
- Agent SQL 字段: `['customer_count']`
- 错误类型: `通过`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT COUNT(pty_id) AS customer_count FROM ads_cust_info_d WHERE data_dt = '20260531' AND gender_cd = '5000002' AND edu_cd IN ('6000002','6000003','6000004') AND cust_age > 50
```

### v003

- 问题: 客户总资产按不同年龄段怎么分布？
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 3
- Agent SQL 行数: 3
- 标准 SQL 字段: `['cust_age_type', 'customer_count', 'total_asset']`
- Agent SQL 字段: `['age_group', 'total_asset']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT CASE WHEN cust.cust_age < 30 THEN '30岁以下' WHEN cust.cust_age BETWEEN 30 AND 40 THEN '30-40岁' WHEN cust.cust_age BETWEEN 41 AND 50 THEN '40-50岁' WHEN cust.cust_age BETWEEN 51 AND 60 THEN '50-60岁' ELSE '60岁以上' END AS age_group, SUM(COALESCE(aset.nm_tot_aset, 0) + COALESCE(aset.fc_pur_aset, 0)) AS total_asset FROM ads_cust_info_d cust LEFT JOIN dws_cust_aset_d aset ON cust.pty_id = aset.pty_id AND aset.data_dt = '20260331' WHERE cust.data_dt = '20260531' GROUP BY age_group ORDER BY age_group ASC
```

### v004

- 问题: 按年龄段统计客户数量和总资产分布情况。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 3
- Agent SQL 行数: 5
- 标准 SQL 字段: `['cust_age_type', 'customer_count', 'total_asset']`
- Agent SQL 字段: `['age_group', 'cust_cnt', 'total_asset']`
- 错误类型: `行数不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH age_data AS (
  SELECT cust.pty_id, cust.cust_age,
         COALESCE(aset.nm_tot_aset, 0) + COALESCE(aset.fc_pur_aset, 0) AS total_asset
  FROM ads_cust_info_d cust
  LEFT JOIN dws_cust_aset_d aset 
    ON cust.pty_id = aset.pty_id AND aset.data_dt = '20260331'
  WHERE cust.data_dt = '20260531'
)
SELECT
  CASE 
    WHEN cust_age < 40 THEN '40岁以下'
    WHEN cust_age BETWEEN 40 AND 49 THEN '40-49岁'
    WHEN cust_age BETWEEN 50 AND 59 THEN '50-59岁'
    WHEN cust_age BETWEEN 60 AND 69 THEN '60-69岁'
    WHEN cust_age BETWEEN 70 AND 79 THEN '70-79岁'
    ELSE '80岁及以上'
  END AS age_group,
  COUNT(DISTINCT pty_id) AS cust_cnt,
  SUM(total_asset) AS total_asset
FROM age_data
GROUP BY age_group
ORDER BY MIN(cust_age)
```

### v005

- 问题: 钻石卡男客户、40岁以上、期末持有比亚迪A股市值超过1000元，算一下2026年一季度盈亏。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 1
- Agent SQL 行数: 1
- 标准 SQL 字段: `['pty_id', 'byd_mkt_val', 'begin_total_asset', 'end_total_asset', 'asset_in', 'asset_out', 'q1_盈亏分析']`
- Agent SQL 字段: `['pty_id', '盈亏分析']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH qualified_cust AS (
    SELECT cust.pty_id
    FROM ads_cust_info_d cust
    JOIN dwd_cust_hold_d hold ON cust.pty_id = hold.pty_id AND hold.data_dt = '20260331'
    JOIN dim_product p ON hold.prdt_id = p.prdt_id
    WHERE cust.data_dt = '20260531'
      AND cust.cust_lvl_cd = '1000001'
      AND cust.gender_cd = '5000002'
      AND cust.cust_age > 40
      AND p.prdt_name = '比亚迪'
      AND p.prdt_type_name = 'A股'
    GROUP BY cust.pty_id
    HAVING SUM(COALESCE(hold.mkt_val, 0)) > 1000
),
begin_asset AS (
    SELECT pty_id, (COALESCE(nm_tot_aset,0) + COALESCE(fc_pur_aset,0)) AS begin_total_asset
    FROM dws_cust_aset_d
    WHERE data_dt = '20260101'
),
end_asset AS (
    SELECT pty_id, (COALESCE(nm_tot_aset,0) + COALESCE(fc_pur_aset,0)) AS end_total_asset
    FROM dws_cust_aset_d
    WHERE data_dt = '20260331'
),
flow AS (
    SELECT pty_id,
           SUM( COALESCE(cash_in,0) + COALESCE(tran_in,0) + COALESCE(assign_in,0) ) AS total_inflow,
           SUM( COALESCE(cash_out,0) + COALESCE(tran_out,0) + COALESCE(assign_out,0) ) AS total_outflow
    FROM dws_cust_fin_d
    WHERE data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY pty_id
)
SELECT q.pty_id,
       COALESCE(ea.end_total_asset, 0) - COALESCE(ba.begin_total_asset, 0) + COALESCE(flow.total_outflow, 0) - COALESCE(flow.total_inflow, 0) AS profit_loss
FROM qualified_cust q
LEFT JOIN begin_asset ba ON q.pty_id = ba.pty_id
LEFT JOIN end_asset ea ON q.pty_id = ea.pty_id
LEFT JOIN flow ON q.pty_id = flow.pty_id
ORDER BY profit_loss DESC
```

### v006

- 问题: 钻石卡男性客户、年龄大于40岁、持有比亚迪市值超过1000元，请计算2026年Q1盈亏。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 1
- Agent SQL 行数: 1
- 标准 SQL 字段: `['pty_id', 'byd_mkt_val', 'begin_total_asset', 'end_total_asset', 'asset_in', 'asset_out', 'q1_盈亏分析']`
- Agent SQL 字段: `['total_盈亏分析']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH target_cust AS (
    SELECT cust.pty_id
    FROM ads_cust_info_d cust
    INNER JOIN dwd_cust_hold_d hold ON cust.pty_id = hold.pty_id AND hold.data_dt = '20260331'
    INNER JOIN dim_product prod ON hold.prdt_id = prod.prdt_id
    WHERE cust.data_dt = '20260531'
      AND cust.cust_lvl_cd = '1000001'
      AND cust.gender_cd = '5000002'
      AND cust.cust_age > 40
      AND prod.prdt_name = '比亚迪' AND prod.prdt_type_name = 'A股'
    GROUP BY cust.pty_id
    HAVING SUM(COALESCE(hold.mkt_val, 0)) > 1000
),
cust_profit AS (
    SELECT 
        cust.pty_id,
        COALESCE(aset_end.nm_tot_aset, 0) + COALESCE(aset_end.fc_pur_aset, 0) AS end_total_asset,
        COALESCE(aset_begin.nm_tot_aset, 0) + COALESCE(aset_begin.fc_pur_aset, 0) AS begin_total_asset,
        SUM(COALESCE(fin.cash_in, 0) + COALESCE(fin.tran_in, 0) + COALESCE(fin.assign_in, 0)) AS total_inflow,
        SUM(COALESCE(fin.cash_out, 0) + COALESCE(fin.tran_out, 0) + COALESCE(fin.assign_out, 0)) AS total_outflow
    FROM target_cust cust
    LEFT JOIN dws_cust_aset_d aset_begin ON cust.pty_id = aset_begin.pty_id AND aset_begin.data_dt = '20260101'
    LEFT JOIN dws_cust_aset_d aset_end ON cust.pty_id = aset_end.pty_id AND aset_end.data_dt = '20260331'
    LEFT JOIN dws_cust_fin_d fin ON cust.pty_id = fin.pty_id AND fin.data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY cust.pty_id, aset_end.nm_tot_aset, aset_end.fc_pur_aset, aset_begin.nm_tot_aset, aset_begin.fc_pur_aset
)
SELECT SUM(end_total_asset - begin_total_asset + total_outflow - total_inflow) AS total_profit_loss
FROM cust_profit
```

### v007

- 问题: 请按分公司、营业部、省份和城市统计客户分布。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 15
- Agent SQL 行数: 15
- 标准 SQL 字段: `['up_org_name', 'org_name', 'prov_name', 'city_name', 'customer_count']`
- Agent SQL 字段: `['分公司', '营业部', '省份', '城市', '客户数量']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT
    branch.up_org_name AS 分公司,
    branch.org_name AS 营业部,
    cust.prov_name AS 省份,
    cust.city_name AS 城市,
    COUNT(cust.pty_id) AS "客户数量"
FROM ads_cust_info_d cust
LEFT JOIN dim_branch branch ON cust.org_id = branch.org_id AND branch.data_dt = cust.data_dt
WHERE cust.data_dt = '20260531'
GROUP BY branch.up_org_name, branch.org_name, cust.prov_name, cust.city_name
ORDER BY "客户数量" DESC
```

### v008

- 问题: 各分公司和营业部客户都来自哪些省市？
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 15
- Agent SQL 行数: 15
- 标准 SQL 字段: `['up_org_name', 'org_name', 'prov_name', 'city_name', 'customer_count']`
- Agent SQL 字段: `['up_org_name', 'org_name', 'prov_name', 'city_name', 'customer_count']`
- 错误类型: `行值不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT dim_branch.up_org_name, dim_branch.org_name, ads_cust_info_d.prov_name, ads_cust_info_d.city_name, COUNT(DISTINCT ads_cust_info_d.pty_id) AS customer_count FROM ads_cust_info_d INNER JOIN dim_branch ON ads_cust_info_d.org_id = dim_branch.org_id AND dim_branch.data_dt = '20260531' WHERE ads_cust_info_d.data_dt = '20260531' GROUP BY dim_branch.up_org_name, dim_branch.org_name, ads_cust_info_d.prov_name, ads_cust_info_d.city_name ORDER BY dim_branch.up_org_name ASC, dim_branch.org_name ASC, ads_cust_info_d.prov_name ASC, ads_cust_info_d.city_name ASC
```

### v009

- 问题: 找出一季度买卖过招商银行A股，并且季末普通账户仍持有中国平安A股的客户。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 1
- Agent SQL 行数: 1
- 标准 SQL 字段: `['pty_id', 'cmb_transaction_amount', 'pingan_market_value']`
- Agent SQL 字段: `['pty_id']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT pty_id FROM (SELECT DISTINCT tran.pty_id FROM dwd_cust_tran_d tran INNER JOIN dim_product prdt ON tran.prdt_id = prdt.prdt_id WHERE tran.data_dt BETWEEN '20260101' AND '20260331' AND prdt.prdt_name = '招商银行' AND prdt.prdt_type_name = 'A股') AS tran_cust INTERSECT SELECT pty_id FROM (SELECT DISTINCT hold.pty_id FROM dwd_cust_hold_d hold INNER JOIN dim_product prdt ON hold.prdt_id = prdt.prdt_id WHERE hold.data_dt = '20260331' AND hold.sys_source = 'nm' AND prdt.prdt_name = '中国平安' AND prdt.prdt_type_name = 'A股' AND coalesce(hold.hold_cnt, 0) > 0) AS hold_cust
```

### v010

- 问题: 2026年第一季度交易招商银行A股且Q1末普通账户持仓中国平安A股的客户有哪些？
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 1
- Agent SQL 行数: 1
- 标准 SQL 字段: `['pty_id', 'cmb_transaction_amount', 'pingan_market_value']`
- Agent SQL 字段: `['pty_id']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> repair_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH tran_cust AS (
    SELECT DISTINCT t.pty_id
    FROM dwd_cust_tran_d t
    INNER JOIN dim_product p ON t.prdt_id = p.prdt_id
    WHERE t.data_dt BETWEEN '20260101' AND '20260331'
      AND p.prdt_name = '招商银行' AND p.prdt_type_name = 'A股'
      AND t.ccy = '0'
      AND coalesce(t.buy_amt, 0) + coalesce(t.sell_amt, 0) > 0
),
hold_cust AS (
    SELECT DISTINCT h.pty_id
    FROM dwd_cust_hold_d h
    INNER JOIN dim_product p ON h.prdt_id = p.prdt_id
    WHERE h.data_dt = '20260331'
      AND h.sys_source = 'nm'
      AND p.prdt_name = '中国平安' AND p.prdt_type_name = 'A股'
      AND h.ccy = '0'
)
SELECT pty_id FROM tran_cust
INTERSECT
SELECT pty_id FROM hold_cust
```

### v011

- 问题: 一季度日均总资产超过30万、股票成交金额超过10万的客户，期末持仓产品类型分布如何？
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 24
- Agent SQL 行数: 24
- 标准 SQL 字段: `['up_prdt_type_name', 'prdt_type_name', 'customer_count', 'total_market_value']`
- Agent SQL 字段: `['product_first_category', 'product_second_category', 'total_holding_market_value']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH cust_aset AS (
  SELECT pty_id,
         (SUM(COALESCE(nm_tot_aset,0) + COALESCE(fc_pur_aset,0)) / 90) AS avg_aset
  FROM dws_cust_aset_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY pty_id
  HAVING (SUM(COALESCE(nm_tot_aset,0) + COALESCE(fc_pur_aset,0)) / 90) > 300000
),
cust_tran AS (
  SELECT t.pty_id,
         SUM(COALESCE(buy_amt,0) + COALESCE(sell_amt,0)) AS tran_amt
  FROM dwd_cust_tran_d t
  INNER JOIN dim_product p ON t.prdt_id = p.prdt_id
  WHERE t.data_dt BETWEEN '20260101' AND '20260331'
    AND p.up_prdt_type_name = '股票'
  GROUP BY t.pty_id
  HAVING SUM(COALESCE(buy_amt,0) + COALESCE(sell_amt,0)) > 100000
),
qualified_cust AS (
  SELECT pty_id FROM cust_aset
  INTERSECT
  SELECT pty_id FROM cust_tran
)
SELECT p.up_prdt_type_name AS product_first_category,
       p.prdt_type_name AS product_second_category,
       SUM(COALESCE(h.mkt_val,0)) AS total_holding_market_value
FROM dwd_cust_hold_d h
INNER JOIN qualified_cust q ON h.pty_id = q.pty_id
INNER JOIN dim_product p ON h.prdt_id = p.prdt_id
WHERE h.data_dt = '20260331'
GROUP BY p.up_prdt_type_name, p.prdt_type_name
ORDER BY total_holding_market_value DESC
```

### v012

- 问题: Q1平均资产大于300000且股票交易额大于100000的客户持有哪些产品类别？
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 24
- Agent SQL 行数: 6
- 标准 SQL 字段: `['up_prdt_type_name', 'prdt_type_name', 'customer_count', 'total_market_value']`
- Agent SQL 字段: `['product_category']`
- 错误类型: `行数不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH daily_asset AS (
    SELECT pty_id,
           SUM(COALESCE(nm_tot_aset,0) + COALESCE(fc_pur_aset,0)) / 90.0 AS avg_daily_asset
    FROM dws_cust_aset_d
    WHERE data_dt >= '20260101' AND data_dt <= '20260331'
    GROUP BY pty_id
    HAVING SUM(COALESCE(nm_tot_aset,0) + COALESCE(fc_pur_aset,0)) / 90.0 > 300000
),
stock_tran AS (
    SELECT t.pty_id,
           SUM(COALESCE(t.buy_amt,0) + COALESCE(t.sell_amt,0)) AS total_stock_trade_amt
    FROM dwd_cust_tran_d t
    INNER JOIN dim_product p ON t.prdt_id = p.prdt_id
    WHERE t.data_dt >= '20260101' AND t.data_dt <= '20260331'
      AND p.up_prdt_type_name = '股票'
    GROUP BY t.pty_id
    HAVING SUM(COALESCE(t.buy_amt,0) + COALESCE(t.sell_amt,0)) > 100000
),
qualified_cust AS (
    SELECT a.pty_id
    FROM daily_asset a
    INNER JOIN stock_tran s ON a.pty_id = s.pty_id
)
SELECT DISTINCT p.up_prdt_type_name AS product_category
FROM qualified_cust q
INNER JOIN dwd_cust_hold_d h ON q.pty_id = h.pty_id
INNER JOIN dim_product p ON h.prdt_id = p.prdt_id
WHERE h.data_dt = '20260331'
ORDER BY product_category
```

### v013

- 问题: 2026年1月10日到2月15日，科创板成交金额超过25万的客户按营业部分布情况。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 3
- Agent SQL 行数: 3
- 标准 SQL 字段: `['up_org_name', 'org_name', 'customer_count', 'total_transaction_amount']`
- Agent SQL 字段: `['branch_name', 'customer_count']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH cust_trade_agg AS (
  SELECT 
    t.pty_id,
    SUM(COALESCE(t.buy_amt, 0) + COALESCE(t.sell_amt, 0)) AS total_trade_amt
  FROM dwd_cust_tran_d t
  INNER JOIN dim_product p ON t.prdt_id = p.prdt_id
  WHERE t.data_dt BETWEEN '20260110' AND '20260215'
    AND p.prdt_type_name = '科创板'
    AND t.ccy = '0'
  GROUP BY t.pty_id
  HAVING SUM(COALESCE(t.buy_amt, 0) + COALESCE(t.sell_amt, 0)) > 250000
)
SELECT 
  b.org_name AS branch_name,
  COUNT(DISTINCT c.pty_id) AS customer_count
FROM cust_trade_agg ct
INNER JOIN ads_cust_info_d c ON ct.pty_id = c.pty_id AND c.data_dt = '20260531'
LEFT JOIN dim_branch b ON c.org_id = b.org_id AND b.data_dt = '20260531'
GROUP BY b.org_name
ORDER BY b.org_name
```

### v014

- 问题: 查询1月10日至2月15日期间科创板交易额大于25万客户所在分公司和营业部。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 3
- Agent SQL 行数: 3
- 标准 SQL 字段: `['up_org_name', 'org_name', 'customer_count', 'total_transaction_amount']`
- Agent SQL 字段: `['分公司', '营业部']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH cust_tran_amt AS (
    SELECT
        tran.pty_id,
        SUM(COALESCE(buy_amt, 0) + COALESCE(sell_amt, 0)) AS total_tran_amt
    FROM dwd_cust_tran_d tran
    INNER JOIN dim_product prod ON tran.prdt_id = prod.prdt_id
    WHERE tran.data_dt BETWEEN '20260110' AND '20260215'
        AND prod.prdt_type_name = '科创板'
        AND tran.ccy = '0'
    GROUP BY tran.pty_id
    HAVING SUM(COALESCE(buy_amt, 0) + COALESCE(sell_amt, 0)) > 250000
),
cust_branch AS (
    SELECT DISTINCT
        branch.up_org_name AS 分公司,
        branch.org_name AS 营业部
    FROM cust_tran_amt
    INNER JOIN ads_cust_info_d cust ON cust_tran_amt.pty_id = cust.pty_id
        AND cust.data_dt = '20260531'
    LEFT JOIN dim_branch branch ON cust.org_id = branch.org_id
        AND branch.data_dt = '20260531'
)
SELECT * FROM cust_branch
```

### s001

- 问题: 统计白金卡女性客户中，年龄在30到50岁之间的人数，并按学历分组。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 1
- Agent SQL 行数: 1
- 标准 SQL 字段: `['education', 'customer_count']`
- Agent SQL 字段: `['edu_cd', 'cust_count']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT edu_cd, count(pty_id) AS cust_count FROM ads_cust_info_d WHERE data_dt = '20260531' AND gender_cd = '5000003' AND cust_lvl_cd = '1000002' AND cust_age BETWEEN 30 AND 50 GROUP BY edu_cd
```

### s002

- 问题: 正常状态客户按客户等级和性别分别有多少人？
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 12
- Agent SQL 行数: 12
- 标准 SQL 字段: `['customer_level', 'gender_name', 'customer_count']`
- Agent SQL 字段: `['cust_lvl_cd', 'lvl_desc', 'gender_cd', 'gender_desc', '客户数']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT cust.cust_lvl_cd, lvl."describe" AS lvl_desc, cust.gender_cd, gender."describe" AS gender_desc, COUNT(DISTINCT cust.pty_id) AS "客户数" FROM ads_cust_info_d cust LEFT JOIN dim_public lvl ON cust.cust_lvl_cd = lvl.code AND lvl.code_type_id = '100' LEFT JOIN dim_public gender ON cust.gender_cd = gender.code AND gender.code_type_id = '500' WHERE cust.data_dt = '20260531' AND cust.cust_status = '2000001' GROUP BY cust.cust_lvl_cd, lvl."describe", cust.gender_cd, gender."describe" ORDER BY cust.cust_lvl_cd, cust.gender_cd
```

### s003

- 问题: 2026年3月31日各省客户总资产最高的前10名省份是哪几个？
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 8
- Agent SQL 行数: 8
- 标准 SQL 字段: `['prov_name', 'customer_count', 'total_asset', 'avg_asset']`
- Agent SQL 字段: `['province', 'total_asset']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT cust.prov_name AS province, SUM(COALESCE(aset.nm_tot_aset, 0) + COALESCE(aset.fc_pur_aset, 0)) AS total_asset FROM ads_cust_info_d cust INNER JOIN dws_cust_aset_d aset ON cust.pty_id = aset.pty_id AND aset.data_dt = '20260331' WHERE cust.data_dt = '20260531' GROUP BY cust.prov_name ORDER BY total_asset DESC LIMIT 10
```

### s004

- 问题: 按2026年3月31日期末总资产分层统计客户数和资产总额，分层为10万以下、10到30万、30到100万、100万以上。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 4
- Agent SQL 行数: 4
- 标准 SQL 字段: `['asset_band', 'customer_count', 'total_asset']`
- Agent SQL 字段: `['asset_tier', 'cust_count', 'total_asset_amount']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT 
    CASE 
        WHEN coalesce(nm_tot_aset,0) + coalesce(fc_pur_aset,0) < 100000 THEN '10万以下'
        WHEN coalesce(nm_tot_aset,0) + coalesce(fc_pur_aset,0) >= 100000 AND coalesce(nm_tot_aset,0) + coalesce(fc_pur_aset,0) < 300000 THEN '10-30万'
        WHEN coalesce(nm_tot_aset,0) + coalesce(fc_pur_aset,0) >= 300000 AND coalesce(nm_tot_aset,0) + coalesce(fc_pur_aset,0) < 1000000 THEN '30-100万'
        WHEN coalesce(nm_tot_aset,0) + coalesce(fc_pur_aset,0) >= 1000000 THEN '100万以上'
        ELSE '其他'
    END AS asset_tier,
    COUNT(pty_id) AS cust_count,
    SUM(coalesce(nm_tot_aset,0) + coalesce(fc_pur_aset,0)) AS total_asset_amount
FROM dws_cust_aset_d
WHERE data_dt = '20260331'
GROUP BY 
    CASE 
        WHEN coalesce(nm_tot_aset,0) + coalesce(fc_pur_aset,0) < 100000 THEN '10万以下'
        WHEN coalesce(nm_tot_aset,0) + coalesce(fc_pur_aset,0) >= 100000 AND coalesce(nm_tot_aset,0) + coalesce(fc_pur_aset,0) < 300000 THEN '10-30万'
        WHEN coalesce(nm_tot_aset,0) + coalesce(fc_pur_aset,0) >= 300000 AND coalesce(nm_tot_aset,0) + coalesce(fc_pur_aset,0) < 1000000 THEN '30-100万'
        WHEN coalesce(nm_tot_aset,0) + coalesce(fc_pur_aset,0) >= 1000000 THEN '100万以上'
        ELSE '其他'
    END
ORDER BY 
    CASE asset_tier
        WHEN '10万以下' THEN 1
        WHEN '10-30万' THEN 2
        WHEN '30-100万' THEN 3
        WHEN '100万以上' THEN 4
        ELSE 5
    END
```

### s005

- 问题: 找出2026年一季度末总资产比期初增长超过10万元的客户，按增长额倒序列出前20名。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 20
- Agent SQL 行数: 20
- 标准 SQL 字段: `['pty_id', 'begin_total_asset', 'end_total_asset', 'asset_growth']`
- Agent SQL 字段: `['pty_id', 'asset_growth']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT e.pty_id,
       (COALESCE(e.nm_tot_aset, 0) + COALESCE(e.fc_pur_aset, 0)) 
       - (COALESCE(b.nm_tot_aset, 0) + COALESCE(b.fc_pur_aset, 0)) AS asset_growth
FROM dws_cust_aset_d e
LEFT JOIN dws_cust_aset_d b ON e.pty_id = b.pty_id AND b.data_dt = '20260101'
WHERE e.data_dt = '20260331'
  AND (COALESCE(e.nm_tot_aset, 0) + COALESCE(e.fc_pur_aset, 0)) 
      - (COALESCE(b.nm_tot_aset, 0) + COALESCE(b.fc_pur_aset, 0)) > 100000
ORDER BY asset_growth DESC
LIMIT 20
```

### s006

- 问题: 分别统计2026年一季度普通账户和信用账户的总流入、总流出和净流入。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 2
- Agent SQL 行数: 2
- 标准 SQL 字段: `['sys_source', 'total_inflow', 'total_outflow', 'net_inflow']`
- Agent SQL 字段: `['sys_source', 'total_inflow', 'total_outflow', 'net_inflow']`
- 错误类型: `行值不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT sys_source, SUM(COALESCE(cash_in,0) + COALESCE(tran_in,0) + COALESCE(assign_in,0)) AS total_inflow, SUM(COALESCE(cash_out,0) + COALESCE(tran_out,0) + COALESCE(assign_out,0)) AS total_outflow, (SUM(COALESCE(cash_in,0) + COALESCE(tran_in,0) + COALESCE(assign_in,0)) - SUM(COALESCE(cash_out,0) + COALESCE(tran_out,0) + COALESCE(assign_out,0))) AS net_inflow FROM dws_cust_fin_d WHERE data_dt BETWEEN '20260101' AND '20260331' AND sys_source IN ('nm', 'fc') GROUP BY sys_source ORDER BY sys_source
```

### s007

- 问题: 2026年一季度净流入超过5万元的客户，按客户等级统计人数和净流入总额。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 5
- Agent SQL 行数: 5
- 标准 SQL 字段: `['customer_level', 'customer_count', 'total_net_inflow']`
- Agent SQL 字段: `['cust_lvl_cd', 'customer_count', 'total_net_inflow']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH fin_agg AS (
  SELECT 
    pty_id, 
    SUM(coalesce(cash_in,0) + coalesce(tran_in,0) + coalesce(assign_in,0) - (coalesce(cash_out,0) + coalesce(tran_out,0) + coalesce(assign_out,0))) AS net_inflow
  FROM dws_cust_fin_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY pty_id
  HAVING SUM(coalesce(cash_in,0) + coalesce(tran_in,0) + coalesce(assign_in,0) - (coalesce(cash_out,0) + coalesce(tran_out,0) + coalesce(assign_out,0))) > 50000
)
SELECT 
  cust.cust_lvl_cd, 
  COUNT(DISTINCT cust.pty_id) AS customer_count, 
  SUM(fin.net_inflow) AS total_net_inflow
FROM fin_agg fin
JOIN ads_cust_info_d cust ON fin.pty_id = cust.pty_id AND cust.data_dt = '20260531'
GROUP BY cust.cust_lvl_cd
```

### s008

- 问题: 2026年一季度A股买入金额最高的前10只产品是什么？同时给出交易客户数和卖出金额。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 10
- Agent SQL 行数: 10
- 标准 SQL 字段: `['prdt_name', 'customer_count', 'total_buy_amount', 'total_sell_amount']`
- Agent SQL 字段: `['prdt_id', 'prdt_name', 'total_buy_amt', 'trade_cust_cnt', 'total_sell_amt']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT p.prdt_id, p.prdt_name, SUM(COALESCE(t.buy_amt, 0)) AS total_buy_amt, COUNT(DISTINCT t.pty_id) AS trade_cust_cnt, SUM(COALESCE(t.sell_amt, 0)) AS total_sell_amt FROM dwd_cust_tran_d t INNER JOIN dim_product p ON t.prdt_id = p.prdt_id WHERE p.prdt_type_name = 'A股' AND t.data_dt BETWEEN '20260101' AND '20260331' AND t.ccy = '0' GROUP BY p.prdt_id, p.prdt_name ORDER BY total_buy_amt DESC LIMIT 10
```

### s009

- 问题: 找出2026年一季度创业板卖出金额大于买入金额的客户，按差额倒序列出前20名。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 20
- Agent SQL 行数: 20
- 标准 SQL 字段: `['pty_id', 'total_sell_amount', 'total_buy_amount', 'sell_buy_gap']`
- Agent SQL 字段: `['pty_id', 'total_buy_amt', 'total_sell_amt', 'net_sell_amt']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT t.pty_id, SUM(COALESCE(t.buy_amt, 0)) AS total_buy_amt, SUM(COALESCE(t.sell_amt, 0)) AS total_sell_amt, SUM(COALESCE(t.sell_amt, 0)) - SUM(COALESCE(t.buy_amt, 0)) AS net_sell_amt FROM dwd_cust_tran_d t INNER JOIN dim_product p ON t.prdt_id = p.prdt_id WHERE t.data_dt BETWEEN '20260101' AND '20260331' AND p.prdt_type_name = '创业板' GROUP BY t.pty_id HAVING SUM(COALESCE(t.sell_amt, 0)) > SUM(COALESCE(t.buy_amt, 0)) ORDER BY net_sell_amt DESC LIMIT 20
```

### s010

- 问题: 统计2026年一季度股票交易金额按一级和二级产品类型的分布。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 8
- Agent SQL 行数: 8
- 标准 SQL 字段: `['up_prdt_type_name', 'prdt_type_name', 'customer_count', 'transaction_amount']`
- Agent SQL 字段: `['up_prdt_type_id', 'up_prdt_type_name', 'prdt_type_id', 'prdt_type_name', '交易金额']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
select dp.up_prdt_type_id, dp.up_prdt_type_name, dp.prdt_type_id, dp.prdt_type_name, sum(coalesce(t.buy_amt,0) + coalesce(t.sell_amt,0)) as "交易金额" from dwd_cust_tran_d t inner join dim_product dp on t.prdt_id = dp.prdt_id where t.data_dt between '20260101' and '20260331' and t.ccy = '0' and dp.up_prdt_type_name = '股票' group by dp.up_prdt_type_id, dp.up_prdt_type_name, dp.prdt_type_id, dp.prdt_type_name order by "交易金额" desc
```

### s011

- 问题: 2026年一季度A股交易金额最高的前10个营业部是哪几个？
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 10
- Agent SQL 行数: 10
- 标准 SQL 字段: `['up_org_name', 'org_name', 'customer_count', 'stock_transaction_amount']`
- Agent SQL 字段: `['branch_name', 'transaction_amount']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT
  branch.org_name AS branch_name,
  SUM(COALESCE(tran.buy_amt, 0) + COALESCE(tran.sell_amt, 0)) AS transaction_amount
FROM dwd_cust_tran_d tran
INNER JOIN dim_product prod ON tran.prdt_id = prod.prdt_id
INNER JOIN ads_cust_info_d cust ON tran.pty_id = cust.pty_id AND cust.data_dt = '20260531'
LEFT JOIN dim_branch branch ON cust.org_id = branch.org_id AND branch.data_dt = '20260531'
WHERE prod.prdt_type_name = 'A股'
  AND tran.data_dt BETWEEN '20260101' AND '20260331'
  AND tran.ccy = '0'
GROUP BY branch.org_name
ORDER BY transaction_amount DESC
LIMIT 10
```

### s012

- 问题: 2026年一季度同时交易过利欧股份A股和特变电工A股的客户有多少人？
- 可执行: Y
- 精确匹配: Y
- 标准 SQL 行数: 1
- Agent SQL 行数: 1
- 标准 SQL 字段: `['customer_count']`
- Agent SQL 字段: `['customer_count']`
- 错误类型: `通过`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH liou_traders AS (
  SELECT DISTINCT t.pty_id
  FROM dwd_cust_tran_d t
  INNER JOIN dim_product p ON t.prdt_id = p.prdt_id
  WHERE t.data_dt BETWEEN '20260101' AND '20260331'
    AND p.prdt_name = '利欧股份'
    AND p.prdt_type_name = 'A股'
),
tebian_traders AS (
  SELECT DISTINCT t.pty_id
  FROM dwd_cust_tran_d t
  INNER JOIN dim_product p ON t.prdt_id = p.prdt_id
  WHERE t.data_dt BETWEEN '20260101' AND '20260331'
    AND p.prdt_name = '特变电工'
    AND p.prdt_type_name = 'A股'
)
SELECT COUNT(*) AS customer_count
FROM liou_traders
INNER JOIN tebian_traders ON liou_traders.pty_id = tebian_traders.pty_id
```

### s013

- 问题: 2026年3月31日期末持仓按账户来源和币种统计客户数和市值。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 4
- Agent SQL 行数: 4
- 标准 SQL 字段: `['sys_source', 'currency_name', 'customer_count', 'total_market_value']`
- Agent SQL 字段: `['sys_source', 'ccy', 'cust_cnt', 'total_mkt_val']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT sys_source, ccy, count(distinct pty_id) as cust_cnt, sum(coalesce(mkt_val, 0)) as total_mkt_val FROM dwd_cust_hold_d WHERE data_dt = '20260331' GROUP BY sys_source, ccy ORDER BY sys_source, ccy
```

### s014

- 问题: 2026年3月31日A股持仓市值最高的前10只股票是什么？
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 10
- Agent SQL 行数: 10
- 标准 SQL 字段: `['prdt_name', 'customer_count', 'total_market_value']`
- Agent SQL 字段: `['prdt_id', 'prdt_name', 'total_mkt_val']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT p.prdt_id, p.prdt_name, SUM(COALESCE(h.mkt_val, 0)) AS total_mkt_val
FROM dwd_cust_hold_d h
INNER JOIN dim_product p ON h.prdt_id = p.prdt_id
WHERE h.data_dt = '20260331'
  AND p.prdt_type_name = 'A股'
GROUP BY p.prdt_id, p.prdt_name
ORDER BY total_mkt_val DESC
LIMIT 10
```

### s015

- 问题: 2026年3月31日同时持有华泰紫金天天发货币市场基金和南方天天利货币市场基金的客户有多少人？
- 可执行: Y
- 精确匹配: Y
- 标准 SQL 行数: 1
- Agent SQL 行数: 1
- 标准 SQL 字段: `['customer_count']`
- Agent SQL 字段: `['customer_count']`
- 错误类型: `通过`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT COUNT(*) AS customer_count FROM (SELECT h.pty_id FROM dwd_cust_hold_d h INNER JOIN dim_product p ON h.prdt_id = p.prdt_id WHERE h.data_dt = '20260331' AND p.prdt_name IN ('华泰紫金天天发货币市场基金', '南方天天利货币市场基金') GROUP BY h.pty_id HAVING COUNT(DISTINCT p.prdt_name) = 2) AS t
```

### s016

- 问题: 2026年3月31日持有张家港行A股市值超过1万元的客户按分公司和营业部怎么分布？
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 1
- Agent SQL 行数: 1
- 标准 SQL 字段: `['up_org_name', 'org_name', 'customer_count', 'total_market_value']`
- Agent SQL 字段: `['branch_company', 'branch_name', 'customer_count']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH eligible_customers AS (
    SELECT 
        h.pty_id,
        SUM(COALESCE(h.mkt_val, 0)) AS total_mkt_val
    FROM dwd_cust_hold_d h
    INNER JOIN dim_product p ON h.prdt_id = p.prdt_id
    WHERE h.data_dt = '20260331'
        AND p.prdt_name = '张家港行'
        AND p.prdt_type_name = 'A股'
    GROUP BY h.pty_id
    HAVING SUM(COALESCE(h.mkt_val, 0)) > 10000
)
SELECT 
    COALESCE(b.up_org_name, '未知分公司') AS branch_company,
    COALESCE(b.org_name, '未知营业部') AS branch_name,
    COUNT(DISTINCT ec.pty_id) AS customer_count
FROM eligible_customers ec
LEFT JOIN ads_cust_info_d ci ON ec.pty_id = ci.pty_id AND ci.data_dt = '20260531'
LEFT JOIN dim_branch b ON ci.org_id = b.org_id AND b.data_dt = '20260531'
GROUP BY b.up_org_name, b.org_name
ORDER BY customer_count DESC
```

### s017

- 问题: 2026年3月31日普通账户现金余额大于信用账户现金余额的客户，按等级统计人数和平均现金差额。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 6
- Agent SQL 行数: 0
- 标准 SQL 字段: `['customer_level', 'customer_count', 'avg_cash_balance_gap']`
- Agent SQL 字段: `['cust_lvl_cd', 'customer_count', 'avg_cash_diff']`
- 错误类型: `行数不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT cust.cust_lvl_cd, COUNT(DISTINCT cust.pty_id) AS customer_count, AVG(COALESCE(aset.nm_bal, 0) - COALESCE(aset.fc_bal, 0)) AS avg_cash_diff FROM ads_cust_info_d cust INNER JOIN dws_cust_aset_d aset ON cust.pty_id = aset.pty_id AND aset.data_dt = '20260331' AND cust.data_dt = '20260331' WHERE COALESCE(aset.nm_bal, 0) > COALESCE(aset.fc_bal, 0) GROUP BY cust.cust_lvl_cd ORDER BY customer_count DESC
```

### s018

- 问题: 2026年一季度各客户等级的日均总资产是多少？
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 6
- Agent SQL 行数: 6
- 标准 SQL 字段: `['customer_level', 'customer_count', 'avg_daily_total_asset']`
- Agent SQL 字段: `['cust_lvl_cd', 'cust_lvl_name', 'avg_daily_asset']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
select 
  cust.cust_lvl_cd,
  lvl."describe" as cust_lvl_name,
  sum(coalesce(aset.nm_tot_aset, 0) + coalesce(aset.fc_pur_aset, 0)) / 90.0 as avg_daily_asset
from ads_cust_info_d cust
left join dws_cust_aset_d aset on cust.pty_id = aset.pty_id and aset.data_dt between '20260101' and '20260331'
left join dim_public lvl on cust.cust_lvl_cd = lvl.code and lvl.code_type_id = '100'
where cust.data_dt = '20260531'
group by cust.cust_lvl_cd, lvl."describe"
order by cust.cust_lvl_cd
```

### s019

- 问题: 2026年一季度日均总资产超过30万元但没有任何交易金额的客户有多少人？
- 可执行: Y
- 精确匹配: Y
- 标准 SQL 行数: 1
- Agent SQL 行数: 1
- 标准 SQL 字段: `['customer_count']`
- Agent SQL 字段: `['customer_count']`
- 错误类型: `通过`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH cust_base AS (
    SELECT pty_id
    FROM ads_cust_info_d
    WHERE data_dt = '20260531'
),
cust_asset AS (
    SELECT c.pty_id,
           SUM(COALESCE(a.nm_tot_aset, 0) + COALESCE(a.fc_pur_aset, 0)) / 90 AS avg_daily_asset
    FROM cust_base c
    LEFT JOIN dws_cust_aset_d a
        ON c.pty_id = a.pty_id
        AND a.data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY c.pty_id
),
cust_tran AS (
    SELECT c.pty_id,
           COALESCE(SUM(COALESCE(t.buy_amt, 0) + COALESCE(t.sell_amt, 0)), 0) AS total_tran_amount
    FROM cust_base c
    LEFT JOIN dwd_cust_tran_d t
        ON c.pty_id = t.pty_id
        AND t.data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY c.pty_id
)
SELECT COUNT(DISTINCT ca.pty_id) AS customer_count
FROM cust_asset ca
JOIN cust_tran ct ON ca.pty_id = ct.pty_id
WHERE ca.avg_daily_asset > 300000
  AND ct.total_tran_amount = 0
```

### s020

- 问题: 列出2026年一季度总交易金额最高的前10个客户，并带上所属分公司和营业部。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 10
- Agent SQL 行数: 10
- 标准 SQL 字段: `['pty_id', 'up_org_name', 'org_name', 'total_buy_amount', 'total_sell_amount', 'transaction_amount']`
- Agent SQL 字段: `['pty_id', 'name', 'up_org_name', 'org_name', 'total_tran_amt']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH cust_tran_summary AS (
  SELECT 
    cust.pty_id,
    cust.name,
    branch.up_org_name,
    branch.org_name,
    SUM(COALESCE(tran.buy_amt, 0) + COALESCE(tran.sell_amt, 0)) AS total_tran_amt
  FROM ads_cust_info_d cust
  INNER JOIN dwd_cust_tran_d tran ON cust.pty_id = tran.pty_id
  LEFT JOIN dim_branch branch ON cust.org_id = branch.org_id AND branch.data_dt = '20260531'
  WHERE cust.data_dt = '20260531'
    AND tran.data_dt BETWEEN '20260101' AND '20260331'
    AND tran.ccy = '0'
  GROUP BY cust.pty_id, cust.name, branch.up_org_name, branch.org_name
)
SELECT pty_id, name, up_org_name, org_name, total_tran_amt
FROM cust_tran_summary
ORDER BY total_tran_amt DESC
LIMIT 10
```

### s021

- 问题: 2026年一季度科创板交易金额按月份分别是多少？
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 3
- Agent SQL 行数: 3
- 标准 SQL 字段: `['trade_month', 'customer_count', 'transaction_amount']`
- Agent SQL 字段: `['month', 'transaction_amount']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
select
  substr(dwd_cust_tran_d.data_dt, 1, 6) as month,
  sum(coalesce(dwd_cust_tran_d.buy_amt, 0) + coalesce(dwd_cust_tran_d.sell_amt, 0)) as transaction_amount
from dwd_cust_tran_d
inner join dim_product on dwd_cust_tran_d.prdt_id = dim_product.prdt_id
where dwd_cust_tran_d.data_dt between '20260101' and '20260331'
  and dim_product.prdt_type_name = '科创板'
group by substr(dwd_cust_tran_d.data_dt, 1, 6)
order by month asc
```

### s022

- 问题: 2026年3月31日持有ETF的客户，按性别和学历统计人数和持仓市值。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 10
- Agent SQL 行数: 10
- 标准 SQL 字段: `['gender_name', 'education', 'customer_count', 'total_market_value']`
- Agent SQL 字段: `['gender', 'education', 'customer_count', 'total_market_value']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT gender."describe" AS gender, edu."describe" AS education, COUNT(DISTINCT cust.pty_id) AS customer_count, SUM(COALESCE(hold.mkt_val, 0)) AS total_market_value FROM ads_cust_info_d cust INNER JOIN dwd_cust_hold_d hold ON cust.pty_id = hold.pty_id AND hold.data_dt = '20260331' AND hold.ccy = '0' INNER JOIN dim_product prod ON hold.prdt_id = prod.prdt_id AND prod.prdt_type_name = 'ETF' LEFT JOIN dim_public gender ON cust.gender_cd = gender.code AND gender.code_type_id = '500' LEFT JOIN dim_public edu ON cust.edu_cd = edu.code AND edu.code_type_id = '600' WHERE cust.data_dt = '20260531' GROUP BY gender."describe", edu."describe" ORDER BY gender."describe", edu."describe"
```

### s023

- 问题: 2026年3月31日债券类产品持仓市值按客户等级怎么分布？
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 4
- Agent SQL 行数: 4
- 标准 SQL 字段: `['customer_level', 'customer_count', 'bond_market_value']`
- Agent SQL 字段: `['客户等级', '持仓市值']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT cust.cust_lvl_cd AS "客户等级", SUM(COALESCE(hold.mkt_val, 0)) AS "持仓市值" FROM ads_cust_info_d cust LEFT JOIN dwd_cust_hold_d hold ON cust.pty_id = hold.pty_id AND hold.data_dt = '20260331' INNER JOIN dim_product prdt ON hold.prdt_id = prdt.prdt_id WHERE cust.data_dt = '20260531' AND prdt.up_prdt_type_name = '债券' GROUP BY cust.cust_lvl_cd
```

### s024

- 问题: 2026年一季度股票交易金额最高的前10个城市是哪些？
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 10
- Agent SQL 行数: 10
- 标准 SQL 字段: `['city_name', 'active_customer_count', 'stock_transaction_amount']`
- Agent SQL 字段: `['city_name', 'total_trade_amount']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT
    c.city_name,
    SUM(COALESCE(t.buy_amt, 0) + COALESCE(t.sell_amt, 0)) AS total_trade_amount
FROM ads_cust_info_d c
INNER JOIN dwd_cust_tran_d t
    ON c.pty_id = t.pty_id
    AND t.data_dt BETWEEN '20260101' AND '20260331'
INNER JOIN dim_product p
    ON t.prdt_id = p.prdt_id
WHERE c.data_dt = '20260531'
    AND p.up_prdt_type_name = '股票'
GROUP BY c.city_name
ORDER BY total_trade_amount DESC
LIMIT 10
```

### s025

- 问题: 找出2026年一季度净流出超过10万元且3月31日期末总资产低于10万元的客户。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 4
- Agent SQL 行数: 4
- 标准 SQL 字段: `['pty_id', 'net_outflow', 'end_total_asset']`
- Agent SQL 字段: `['pty_id', 'net_outflow', 'total_asset']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH fin_flow AS (
  SELECT
    pty_id,
    SUM(COALESCE(cash_out,0) + COALESCE(tran_out,0) + COALESCE(assign_out,0) 
       - COALESCE(cash_in,0) - COALESCE(tran_in,0) - COALESCE(assign_in,0)) AS net_outflow
  FROM dws_cust_fin_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY pty_id
)
SELECT
  cust.pty_id,
  f.net_outflow,
  COALESCE(a.nm_tot_aset,0) + COALESCE(a.fc_pur_aset,0) AS total_asset
FROM ads_cust_info_d cust
LEFT JOIN fin_flow f ON cust.pty_id = f.pty_id
LEFT JOIN dws_cust_aset_d a ON cust.pty_id = a.pty_id AND a.data_dt = '20260331'
WHERE cust.data_dt = '20260531'
  AND f.net_outflow > 100000
  AND COALESCE(a.nm_tot_aset,0) + COALESCE(a.fc_pur_aset,0) < 100000
ORDER BY f.net_outflow DESC
```

### s026

- 问题: 2026年一季度日均总资产超过30万元的客户，在3月31日持仓的产品一级分类分布如何？
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 6
- Agent SQL 行数: 6
- 标准 SQL 字段: `['up_prdt_type_name', 'customer_count', 'product_count', 'total_market_value']`
- Agent SQL 字段: `['product_level1_name', 'holding_market_value']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH cust_daily_avg AS (
    SELECT 
        pty_id,
        SUM(COALESCE(nm_tot_aset,0) + COALESCE(fc_pur_aset,0)) / 90 AS avg_daily_asset
    FROM dws_cust_aset_d
    WHERE data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY pty_id
    HAVING SUM(COALESCE(nm_tot_aset,0) + COALESCE(fc_pur_aset,0)) / 90 > 300000
),
cust_list AS (
    SELECT pty_id FROM cust_daily_avg
)
SELECT 
    dp.up_prdt_type_name AS product_level1_name,
    SUM(COALESCE(h.mkt_val,0)) AS holding_market_value
FROM dwd_cust_hold_d h
INNER JOIN cust_list c ON h.pty_id = c.pty_id
INNER JOIN dim_product dp ON h.prdt_id = dp.prdt_id
WHERE h.data_dt = '20260331'
GROUP BY dp.up_prdt_type_name
ORDER BY holding_market_value DESC
```

### s027

- 问题: 客户数最多的前10个营业部，分别有多少客户、平均年龄是多少？
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 10
- Agent SQL 行数: 10
- 标准 SQL 字段: `['up_org_name', 'org_name', 'customer_count', 'avg_age']`
- Agent SQL 字段: `['org_id', 'org_name', 'customer_count', 'avg_age']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT b.org_id, b.org_name, COUNT(a.pty_id) AS customer_count, AVG(a.cust_age) AS avg_age FROM ads_cust_info_d a LEFT JOIN dim_branch b ON a.org_id = b.org_id AND b.data_dt = '20260531' WHERE a.data_dt = '20260531' GROUP BY b.org_id, b.org_name ORDER BY customer_count DESC LIMIT 10
```

### s028

- 问题: 2026年3月31日信用账户持仓客户按等级统计人数和持仓市值。
- 可执行: N
- 精确匹配: N
- 标准 SQL 行数: 4
- Agent SQL 行数: 0
- 标准 SQL 字段: `['customer_level', 'customer_count', 'credit_market_value']`
- Agent SQL 字段: `[]`
- 错误类型: `agent_sql_execution_failed`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> ask_clarification -> persist_state`

Agent SQL:

```sql

```

### s029

- 问题: 2026年一季度交易佣金和费用按产品一级、二级分类排名，取费用最高的前20类。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 15
- Agent SQL 行数: 20
- 标准 SQL 字段: `['up_prdt_type_name', 'prdt_type_name', 'total_rake', 'total_fare', 'total_fee']`
- Agent SQL 字段: `['up_prdt_type_id', 'up_prdt_type_name', 'prdt_type_id', 'prdt_type_name', 'total_comm_fare']`
- 错误类型: `行数不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT p.up_prdt_type_id, p.up_prdt_type_name, p.prdt_type_id, p.prdt_type_name, SUM(COALESCE(t.buy_rake,0) + COALESCE(t.sell_rake,0) + COALESCE(t.buy_fare,0) + COALESCE(t.sell_fare,0)) AS total_comm_fare FROM dwd_cust_tran_d t INNER JOIN dim_product p ON t.prdt_id = p.prdt_id WHERE t.data_dt BETWEEN '20260101' AND '20260331' GROUP BY p.up_prdt_type_id, p.up_prdt_type_name, p.prdt_type_id, p.prdt_type_name ORDER BY total_comm_fare DESC LIMIT 20
```

### s030

- 问题: 2026年3月31日持仓客户数最多的前10个产品是什么？
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 10
- Agent SQL 行数: 10
- 标准 SQL 字段: `['prdt_name', 'prdt_type_name', 'up_prdt_type_name', 'customer_count', 'total_market_value']`
- Agent SQL 字段: `['prdt_id', 'prdt_name', 'cust_count']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT dim_product.prdt_id, dim_product.prdt_name, COUNT(DISTINCT dwd_cust_hold_d.pty_id) AS cust_count FROM dwd_cust_hold_d INNER JOIN dim_product ON dwd_cust_hold_d.prdt_id = dim_product.prdt_id WHERE dwd_cust_hold_d.data_dt = '20260331' GROUP BY dim_product.prdt_id, dim_product.prdt_name ORDER BY cust_count DESC LIMIT 10
```

### a001

- 问题: 财富管理团队准备做一轮基金配置提升营销，希望名单尽量聚焦在有资产基础、近期确实活跃、但基金配置仍然偏低的客户。请筛选2026年3月31日总资产不少于10万元、2026年一季度有股票交易且股票买卖合计金额大于0、同期资金净流入为正的客户；基金期末持仓市值占总资产比例达到30%及以上的不要纳入，没有基金持仓的客户按基金市值0处理。结果需要列出客户编号、姓名、分公司、营业部、总资产、基金持仓市值、基金资产占比、股票交易额和净流入，按总资产从高到低取前20名。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 20
- Agent SQL 行数: 20
- 标准 SQL 字段: `['pty_id', 'name', 'up_org_name', 'org_name', 'total_asset', 'fund_market_value', 'fund_asset_ratio', 'stock_turnover', 'net_inflow']`
- Agent SQL 字段: `['客户编号', '姓名', '分公司', '营业部', '总资产', '基金持仓市值', '基金资产占比', '股票交易额', '净流入']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH stock_trade AS (
    SELECT tran.pty_id, SUM(COALESCE(tran.buy_amt,0) + COALESCE(tran.sell_amt,0)) AS stock_trade_amt
    FROM dwd_cust_tran_d tran
    INNER JOIN dim_product prod ON tran.prdt_id = prod.prdt_id
    WHERE tran.data_dt BETWEEN '20260101' AND '20260331'
      AND prod.up_prdt_type_name = '股票'
      AND tran.ccy = '0'
    GROUP BY tran.pty_id
    HAVING SUM(COALESCE(tran.buy_amt,0) + COALESCE(tran.sell_amt,0)) > 0
),
net_inflow AS (
    SELECT pty_id, SUM(COALESCE(cash_in,0) - COALESCE(cash_out,0)) AS net_inflow
    FROM dws_cust_fin_d
    WHERE data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY pty_id
    HAVING SUM(COALESCE(cash_in,0) - COALESCE(cash_out,0)) > 0
),
fund_hold AS (
    SELECT hold.pty_id, SUM(COALESCE(hold.mkt_val,0)) AS fund_mkt_val
    FROM dwd_cust_hold_d hold
    INNER JOIN dim_product prod ON hold.prdt_id = prod.prdt_id
    WHERE hold.data_dt = '20260331'
      AND prod.up_prdt_type_name = '开放式基金'
      AND hold.ccy = '0'
    GROUP BY hold.pty_id
)
SELECT
    cust.pty_id AS 客户编号,
    cust.name AS 姓名,
    branch.up_org_name AS 分公司,
    branch.org_name AS 营业部,
    (COALESCE(aset.nm_tot_aset,0) + COALESCE(aset.fc_pur_aset,0)) AS 总资产,
    COALESCE(fund.fund_mkt_val, 0) AS 基金持仓市值,
    (COALESCE(fund.fund_mkt_val, 0) / (COALESCE(aset.nm_tot_aset,0) + COALESCE(aset.fc_pur_aset,0))) AS 基金资产占比,
    stock.stock_trade_amt AS 股票交易额,
    inflow.net_inflow AS 净流入
FROM ads_cust_info_d cust
INNER JOIN stock_trade stock ON cust.pty_id = stock.pty_id
INNER JOIN net_inflow inflow ON cust.pty_id = inflow.pty_id
LEFT JOIN dws_cust_aset_d aset ON cust.pty_id = aset.pty_id AND aset.data_dt = '20260331'
LEFT JOIN fund_hold fund ON cust.pty_id = fund.pty_id
LEFT JOIN dim_branch branch ON cust.org_id = branch.org_id AND branch.data_dt = '20260531'
WHERE cust.data_dt = '20260531'
  AND (COALESCE(aset.nm_tot_aset,0) + COALESCE(aset.fc_pur_aset,0)) >= 100000
  AND (COALESCE(fund.fund_mkt_val, 0) / (COALESCE(aset.nm_tot_aset,0) + COALESCE(aset.fc_pur_aset,0))) < 0.3
ORDER BY 总资产 DESC
LIMIT 20
```

### a002

- 问题: 按分公司汇总期末总资产不低于10万元、一季度有股票交易且基金持仓占总资产低于30%的营销候选客户数、总资产、平均基金配置比例、股票交易额和净流入，并按候选客户总资产降序取前15家分公司。
- 可执行: N
- 精确匹配: N
- 标准 SQL 行数: 9
- Agent SQL 行数: 0
- 标准 SQL 字段: `['up_org_name', 'candidate_count', 'candidate_total_asset', 'avg_fund_ratio', 'stock_turnover', 'net_inflow']`
- Agent SQL 字段: `[]`
- 错误类型: `agent_sql_execution_failed`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> ask_clarification -> persist_state`

Agent SQL:

```sql

```

### a003

- 问题: 找出一季度资产变动与资金净流入差异绝对值最大的20名客户，列出期初资产、期末资产、资产变动、净流入、非资金流因素影响、交易额以及所属分公司和营业部。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 20
- Agent SQL 行数: 20
- 标准 SQL 字段: `['pty_id', 'name', 'up_org_name', 'org_name', 'begin_asset', 'end_asset', 'asset_change', 'net_inflow', 'non_flow_change', 'turnover']`
- Agent SQL 字段: `['pty_id', 'begin_asset', 'end_asset', 'asset_change', 'net_inflow', 'non_fund_factor', 'transaction_amount', 'up_org_name', 'org_name']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH fin AS (SELECT pty_id, SUM(COALESCE(cash_in,0) + COALESCE(tran_in,0) + COALESCE(assign_in,0)) AS total_inflow, SUM(COALESCE(cash_out,0) + COALESCE(tran_out,0) + COALESCE(assign_out,0)) AS total_outflow FROM dws_cust_fin_d WHERE data_dt BETWEEN '20260101' AND '20260331' GROUP BY pty_id), tran AS (SELECT pty_id, SUM(COALESCE(buy_amt,0) + COALESCE(sell_amt,0)) AS total_tran_amt FROM dwd_cust_tran_d WHERE data_dt BETWEEN '20260101' AND '20260331' GROUP BY pty_id) SELECT cust.pty_id, COALESCE(begin_aset.nm_tot_aset,0) + COALESCE(begin_aset.fc_pur_aset,0) AS begin_asset, COALESCE(end_aset.nm_tot_aset,0) + COALESCE(end_aset.fc_pur_aset,0) AS end_asset, (COALESCE(end_aset.nm_tot_aset,0) + COALESCE(end_aset.fc_pur_aset,0)) - (COALESCE(begin_aset.nm_tot_aset,0) + COALESCE(begin_aset.fc_pur_aset,0)) AS asset_change, COALESCE(fin.total_inflow,0) - COALESCE(fin.total_outflow,0) AS net_inflow, (COALESCE(end_aset.nm_tot_aset,0) + COALESCE(end_aset.fc_pur_aset,0)) - (COALESCE(begin_aset.nm_tot_aset,0) + COALESCE(begin_aset.fc_pur_aset,0)) - (COALESCE(fin.total_inflow,0) - COALESCE(fin.total_outflow,0)) AS non_fund_factor, COALESCE(tran.total_tran_amt,0) AS transaction_amount, branch.up_org_name, branch.org_name FROM ads_cust_info_d cust LEFT JOIN dws_cust_aset_d begin_aset ON cust.pty_id = begin_aset.pty_id AND begin_aset.data_dt = '20260101' LEFT JOIN dws_cust_aset_d end_aset ON cust.pty_id = end_aset.pty_id AND end_aset.data_dt = '20260331' LEFT JOIN fin ON cust.pty_id = fin.pty_id LEFT JOIN tran ON cust.pty_id = tran.pty_id LEFT JOIN dim_branch branch ON cust.org_id = branch.org_id AND branch.data_dt = '20260531' WHERE cust.data_dt = '20260531' ORDER BY abs((COALESCE(end_aset.nm_tot_aset,0) + COALESCE(end_aset.fc_pur_aset,0)) - (COALESCE(begin_aset.nm_tot_aset,0) + COALESCE(begin_aset.fc_pur_aset,0)) - (COALESCE(fin.total_inflow,0) - COALESCE(fin.total_outflow,0))) DESC LIMIT 20
```

### a004

- 问题: 区域负责人希望做一张营业部经营对比表。请以2026年5月31日客户归属为准，以营业部全部客户作为统计母集，计算每个营业部的客户数、2026年3月31日期末总资产、一季度有交易金额的活跃客户率、一季度买卖交易额、佣金及费用合计、资金净流入和期末持仓市值。交易或资金记录不存在时按0计算。最后在每个分公司内部按照期末总资产从高到低进行排名，只返回总资产最高的前3个营业部；同一分公司内并列时使用dense rank，不要强行打散并列名次。
- 可执行: N
- 精确匹配: N
- 标准 SQL 行数: 14
- Agent SQL 行数: 0
- 标准 SQL 字段: `['up_org_name', 'org_name', 'customer_count', 'total_asset', 'active_customer_rate', 'turnover', 'total_fee', 'net_inflow', 'holding_market_value', 'asset_rank_in_company']`
- Agent SQL 字段: `[]`
- 错误类型: `agent_sql_execution_failed`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> ask_clarification -> persist_state`

Agent SQL:

```sql

```

### a005

- 问题: 计算3月31日每位客户的持仓HHI和最大单一产品持仓占比，筛选HHI大于0.35的客户，并补充期末总资产和一季度交易额，按HHI降序取前20名。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 20
- Agent SQL 行数: 20
- 标准 SQL 字段: `['pty_id', 'name', 'holding_market_value', 'product_count', 'top_product_ratio', 'holding_hhi', 'total_asset', 'turnover']`
- Agent SQL 字段: `['pty_id', 'holding_hhi', 'max_single_holding_ratio', 'total_asset', 'q1_transaction_amount']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH hold AS (
    SELECT 
        pty_id,
        prdt_id,
        COALESCE(mkt_val, 0) AS mkt_val
    FROM dwd_cust_hold_d
    WHERE data_dt = '20260331'
),
cust_hold_agg AS (
    SELECT 
        pty_id,
        SUM(mkt_val) AS total_mkt_val,
        SUM(POWER(mkt_val, 2)) AS sum_sq_mkt_val,
        MAX(mkt_val) AS max_mkt_val
    FROM hold
    GROUP BY pty_id
),
hhi_calc AS (
    SELECT
        pty_id,
        CASE WHEN total_mkt_val > 0 THEN sum_sq_mkt_val / POWER(total_mkt_val, 2) ELSE 0 END AS holding_hhi,
        CASE WHEN total_mkt_val > 0 THEN max_mkt_val / total_mkt_val ELSE 0 END AS max_single_holding_ratio
    FROM cust_hold_agg
),
asset AS (
    SELECT 
        pty_id,
        COALESCE(nm_tot_aset,0) + COALESCE(fc_pur_aset,0) AS total_asset
    FROM dws_cust_aset_d
    WHERE data_dt = '20260331'
),
tran AS (
    SELECT 
        pty_id,
        SUM(COALESCE(buy_amt,0) + COALESCE(sell_amt,0)) AS q1_transaction_amount
    FROM dwd_cust_tran_d
    WHERE data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY pty_id
)
SELECT 
    hhi_calc.pty_id,
    holding_hhi,
    max_single_holding_ratio,
    COALESCE(asset.total_asset, 0) AS total_asset,
    COALESCE(tran.q1_transaction_amount, 0) AS q1_transaction_amount
FROM hhi_calc
LEFT JOIN asset ON hhi_calc.pty_id = asset.pty_id
LEFT JOIN tran ON hhi_calc.pty_id = tran.pty_id
WHERE holding_hhi > 0.35
ORDER BY holding_hhi DESC
LIMIT 20
```

### a006

- 问题: 按客户计算3月31日持仓一级品类与一季度交易一级品类的Jaccard重合度，并列出持仓品类数、交易品类数、交集品类数、并集品类数和期末总资产，按并集品类数及总资产降序取前20名。
- 可执行: N
- 精确匹配: N
- 标准 SQL 行数: 20
- Agent SQL 行数: 0
- 标准 SQL 字段: `['pty_id', 'holding_category_count', 'trading_category_count', 'overlap_category_count', 'union_category_count', 'category_overlap_ratio', 'total_asset']`
- Agent SQL 字段: `[]`
- 错误类型: `agent_sql_execution_failed`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> ask_clarification -> persist_state`

Agent SQL:

```sql

```

### a007

- 问题: 产品团队想观察一类可能发生资产配置迁移的客户：他们在2026年1月卖出过股票，并在2026年3月买入过开放式基金。请按客户汇总1月股票卖出金额和3月基金买入金额，同时给出一季度资金净流入、3月31日期末总资产、客户姓名以及所属分公司和营业部。只有两项行为金额都大于0的客户才保留，结果按3月基金买入金额从高到低取前20名。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 20
- Agent SQL 行数: 20
- 标准 SQL 字段: `['pty_id', 'name', 'up_org_name', 'org_name', 'january_stock_sell', 'march_fund_buy', 'net_inflow', 'end_asset']`
- Agent SQL 字段: `['客户姓名', '所属分公司', '所属营业部', '一月股票卖出金额', '三月基金买入金额', '一季度资金净流入', '期末总资产']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH 
  cust_base AS (
    SELECT pty_id, name, org_id 
    FROM ads_cust_info_d 
    WHERE data_dt = '20260531'
  ),
  branch_info AS (
    SELECT org_id, org_name, up_org_name
    FROM dim_branch
    WHERE data_dt = '20260531'
  ),
  jan_sell AS (
    SELECT 
      t.pty_id, 
      SUM(COALESCE(t.sell_amt, 0)) AS jan_sell_amt
    FROM dwd_cust_tran_d t
    JOIN dim_product p ON t.prdt_id = p.prdt_id
    WHERE t.data_dt BETWEEN '20260101' AND '20260131'
      AND p.up_prdt_type_name = '股票'
      AND t.ccy = '0'
    GROUP BY t.pty_id
    HAVING SUM(COALESCE(t.sell_amt, 0)) > 0
  ),
  mar_buy AS (
    SELECT 
      t.pty_id, 
      SUM(COALESCE(t.buy_amt, 0)) AS mar_buy_amt
    FROM dwd_cust_tran_d t
    JOIN dim_product p ON t.prdt_id = p.prdt_id
    WHERE t.data_dt BETWEEN '20260301' AND '20260331'
      AND p.up_prdt_type_name = '开放式基金'
      AND t.ccy = '0'
    GROUP BY t.pty_id
    HAVING SUM(COALESCE(t.buy_amt, 0)) > 0
  ),
  asset_0331 AS (
    SELECT 
      pty_id,
      COALESCE(nm_tot_aset, 0) + COALESCE(fc_pur_aset, 0) AS total_asset_0331
    FROM dws_cust_aset_d
    WHERE data_dt = '20260331'
  ),
  fin_q1 AS (
    SELECT 
      pty_id,
      SUM(COALESCE(cash_in, 0) - COALESCE(cash_out, 0)) AS net_inflow_q1
    FROM dws_cust_fin_d
    WHERE data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY pty_id
  )
SELECT 
  cust.name AS 客户姓名,
  br.up_org_name AS 所属分公司,
  br.org_name AS 所属营业部,
  js.jan_sell_amt AS 一月股票卖出金额,
  mb.mar_buy_amt AS 三月基金买入金额,
  COALESCE(fin.net_inflow_q1, 0) AS 一季度资金净流入,
  COALESCE(ast.total_asset_0331, 0) AS 期末总资产
FROM cust_base cust
JOIN jan_sell js ON cust.pty_id = js.pty_id
JOIN mar_buy mb ON cust.pty_id = mb.pty_id
LEFT JOIN branch_info br ON cust.org_id = br.org_id
LEFT JOIN asset_0331 ast ON cust.pty_id = ast.pty_id
LEFT JOIN fin_q1 fin ON cust.pty_id = fin.pty_id
ORDER BY mb.mar_buy_amt DESC
LIMIT 20
```

### a008

- 问题: 筛选3月31日信用账户资产占总资产比例不低于20%且一季度普通、信用账户均有交易的客户，列出两类账户资产、信用资产占比、信用持仓市值、普通账户交易额和信用账户交易额，按信用账户资产降序取前20名。
- 可执行: N
- 精确匹配: N
- 标准 SQL 行数: 20
- Agent SQL 行数: 0
- 标准 SQL 字段: `['pty_id', 'name', 'normal_asset', 'credit_asset', 'credit_asset_ratio', 'credit_holding_value', 'normal_turnover', 'credit_turnover']`
- Agent SQL 字段: `[]`
- 错误类型: `agent_sql_execution_failed`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> ask_clarification -> persist_state`

Agent SQL:

```sql

```

### a009

- 问题: 客户运营团队准备唤醒一批“有资产、无交易”的沉默客户。请找出2026年一季度日均总资产不少于20万元、3月31日仍有正持仓市值，但整个一季度没有任何买入或卖出金额大于0记录的客户。日均资产按实际存在的每日资产快照平均，不要固定除以90；持仓先在客户粒度汇总。输出客户编号、姓名、分公司、营业部、日均资产、期末持仓市值和持仓产品数，按日均资产降序取前20名。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 15
- Agent SQL 行数: 15
- 标准 SQL 字段: `['pty_id', 'name', 'up_org_name', 'org_name', 'avg_daily_asset', 'end_holding_value', 'holding_product_count']`
- Agent SQL 字段: `['customer_id', 'customer_name', 'branch_company', 'branch_name', 'avg_daily_asset', 'end_hold_value', 'prod_count']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> repair_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH cust AS (
  SELECT pty_id, name, org_id, prov_name
  FROM ads_cust_info_d
  WHERE data_dt = '20260531'
),
daily_asset AS (
  SELECT pty_id,
         SUM(COALESCE(nm_tot_aset,0) + COALESCE(fc_pur_aset,0)) / 90 AS avg_daily_asset
  FROM dws_cust_aset_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY pty_id
),
hold_end AS (
  SELECT pty_id,
         SUM(COALESCE(mkt_val,0)) AS end_mkt_val,
         COUNT(DISTINCT prdt_id) AS prod_cnt
  FROM dwd_cust_hold_d
  WHERE data_dt = '20260331'
  GROUP BY pty_id
),
traded_cust AS (
  SELECT DISTINCT pty_id
  FROM dwd_cust_tran_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
    AND (COALESCE(buy_amt,0) > 0 OR COALESCE(sell_amt,0) > 0)
)
SELECT 
  c.pty_id AS customer_id,
  c.name AS customer_name,
  c.prov_name AS branch_company,
  c.org_id AS branch_name,
  da.avg_daily_asset,
  COALESCE(he.end_mkt_val, 0) AS end_hold_value,
  COALESCE(he.prod_cnt, 0) AS prod_count
FROM cust c
JOIN daily_asset da ON c.pty_id = da.pty_id
LEFT JOIN hold_end he ON c.pty_id = he.pty_id
WHERE da.avg_daily_asset >= 200000
  AND he.end_mkt_val > 0
  AND NOT EXISTS (
    SELECT 1 FROM traded_cust tc WHERE tc.pty_id = c.pty_id
  )
ORDER BY da.avg_daily_asset DESC
LIMIT 20
```

### a010

- 问题: 统计每个营业部3月31日持仓市值最高的3只产品，返回分公司、营业部、产品、持仓客户数、持仓市值及营业部内排名；并列市值按产品ID升序打散。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 44
- Agent SQL 行数: 73
- 标准 SQL 字段: `['up_org_name', 'org_name', 'prdt_id', 'prdt_name', 'up_prdt_type_name', 'holder_count', 'market_value', 'product_rank']`
- Agent SQL 字段: `['up_org_id', 'up_org_name', 'org_id', 'org_name', 'prdt_id', 'prdt_name', 'holding_market_value', 'customer_count', 'rank_in_branch']`
- 错误类型: `行数不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH hold_agg AS (
  SELECT
    b.up_org_id,
    b.up_org_name,
    b.org_id,
    b.org_name,
    p.prdt_id,
    p.prdt_name,
    SUM(COALESCE(h.mkt_val, 0)) AS holding_market_value,
    COUNT(DISTINCT h.pty_id) AS customer_count,
    ROW_NUMBER() OVER (PARTITION BY b.org_id ORDER BY SUM(COALESCE(h.mkt_val, 0)) DESC, p.prdt_id ASC) AS rank_in_branch
  FROM dwd_cust_hold_d h
  INNER JOIN dim_product p ON h.prdt_id = p.prdt_id
  INNER JOIN ads_cust_info_d c ON h.pty_id = c.pty_id AND c.data_dt = '20260531'
  LEFT JOIN dim_branch b ON c.org_id = b.org_id AND b.data_dt = '20260531'
  WHERE h.data_dt = '20260331' AND h.ccy = '0'
  GROUP BY b.up_org_id, b.up_org_name, b.org_id, b.org_name, p.prdt_id, p.prdt_name
)
SELECT up_org_id, up_org_name, org_id, org_name, prdt_id, prdt_name, holding_market_value, customer_count, rank_in_branch
FROM hold_agg
WHERE rank_in_branch <= 3
ORDER BY up_org_name ASC, org_name ASC, rank_in_branch ASC
```

### a011

- 问题: 按一季度交易佣金及费用合计计算客户贡献，在每个省内取贡献最高的3名客户，并返回交易额、费用、交易天数、营业部和省内排名。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 17
- Agent SQL 行数: 17
- 标准 SQL 字段: `['prov_name', 'pty_id', 'name', 'org_name', 'turnover', 'total_fee', 'trade_days', 'fee_rank_in_province']`
- Agent SQL 字段: `['trans_amt', 'fee', 'trade_days', 'org_name', 'rank_in_prov']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH customer_contrib AS (
  SELECT 
    cust.pty_id,
    cust.prov_name,
    branch.org_name,
    SUM(COALESCE(buy_amt,0) + COALESCE(sell_amt,0)) AS trans_amt,
    SUM(COALESCE(buy_rake,0) + COALESCE(sell_rake,0) + COALESCE(buy_fare,0) + COALESCE(sell_fare,0)) AS contrib_fee,
    COUNT(DISTINCT tran.data_dt) AS trade_days
  FROM ads_cust_info_d cust
  LEFT JOIN dwd_cust_tran_d tran ON cust.pty_id = tran.pty_id 
    AND tran.data_dt BETWEEN '20260101' AND '20260331'
  LEFT JOIN dim_branch branch ON cust.org_id = branch.org_id 
    AND branch.data_dt = '20260531'
  WHERE cust.data_dt = '20260531'
  GROUP BY cust.pty_id, cust.prov_name, branch.org_name
),
ranked AS (
  SELECT 
    *,
    ROW_NUMBER() OVER (PARTITION BY prov_name ORDER BY contrib_fee DESC) AS rank_in_prov
  FROM customer_contrib
  WHERE contrib_fee > 0
)
SELECT trans_amt, contrib_fee AS fee, trade_days, org_name, rank_in_prov
FROM ranked
WHERE rank_in_prov <= 3
ORDER BY prov_name, rank_in_prov
```

### a012

- 问题: 经营分析会上需要查看3月份交易增长最快的营业部。请先按营业部和月份汇总2026年一季度买卖交易额及活跃客户数，再用窗口函数取得每个营业部上月交易额。最终只比较3月相对2月的变化，列出分公司、营业部、3月交易额、2月交易额、环比增加额、环比增幅和3月活跃客户数。2月交易额为0时环比增幅返回NULL，按环比增加额从高到低取前20个营业部。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 15
- Agent SQL 行数: 20
- 标准 SQL 字段: `['up_org_name', 'org_name', 'march_turnover', 'february_turnover', 'month_over_month_change', 'month_over_month_rate', 'active_customer_count']`
- Agent SQL 字段: `['branch_company', 'branch_name', 'march_amt', 'feb_amt', 'increase_amt', 'increase_rate', 'march_active_cust_cnt']`
- 错误类型: `行数不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH branches AS (
    SELECT DISTINCT org_id, org_name, up_org_name 
    FROM dim_branch 
    WHERE data_dt = '20260531'
),
months AS (
    SELECT '202602' AS month_id 
    UNION ALL 
    SELECT '202603'
),
branch_months AS (
    SELECT b.org_id, b.org_name, b.up_org_name, m.month_id
    FROM branches b
    CROSS JOIN months m
),
monthly_stats AS (
    SELECT 
        cust.org_id,
        substr(tran.data_dt, 1, 6) AS month_id,
        sum(coalesce(tran.buy_amt, 0) + coalesce(tran.sell_amt, 0)) AS total_amt,
        count(distinct tran.pty_id) AS active_cust_cnt
    FROM dwd_cust_tran_d tran
    JOIN ads_cust_info_d cust 
        ON tran.pty_id = cust.pty_id 
        AND cust.data_dt = '20260531'
    WHERE tran.data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY cust.org_id, substr(tran.data_dt, 1, 6)
),
filled_stats AS (
    SELECT 
        bm.org_id,
        bm.month_id,
        COALESCE(ms.total_amt, 0) AS total_amt,
        COALESCE(ms.active_cust_cnt, 0) AS active_cust_cnt
    FROM branch_months bm
    LEFT JOIN monthly_stats ms 
        ON bm.org_id = ms.org_id 
        AND bm.month_id = ms.month_id
),
with_lag AS (
    SELECT 
        org_id,
        month_id,
        total_amt,
        active_cust_cnt,
        LAG(total_amt, 1) OVER (PARTITION BY org_id ORDER BY month_id) AS prev_month_amt
    FROM filled_stats
)
SELECT 
    b.up_org_name AS branch_company,
    b.org_name AS branch_name,
    wl.total_amt AS march_amt,
    wl.prev_month_amt AS feb_amt,
    wl.total_amt - wl.prev_month_amt AS increase_amt,
    CASE 
        WHEN wl.prev_month_amt = 0 THEN NULL 
        ELSE (wl.total_amt - wl.prev_month_amt) / wl.prev_month_amt 
    END AS increase_rate,
    wl.active_cust_cnt AS march_active_cust_cnt
FROM with_lag wl
JOIN dim_branch b 
    ON wl.org_id = b.org_id 
    AND b.data_dt = '20260531'
WHERE wl.month_id = '202603'
ORDER BY increase_amt DESC
LIMIT 20
```

### a013

- 问题: ETF业务团队计划从现有股票客户中寻找现金较充裕但尚未配置ETF的潜客。请筛选2026年3月31日总资产不少于10万元、现金资产占总资产比例不低于40%、一季度股票交易额大于0且资金净流入为正的客户；如果客户在3月31日已经持有任何ETF且该持仓市值大于0，则必须排除。输出客户编号、姓名、分公司、营业部、总资产、现金资产、现金占比、股票交易额和净流入，按现金资产降序取前20名。
- 可执行: N
- 精确匹配: N
- 标准 SQL 行数: 4
- Agent SQL 行数: 0
- 标准 SQL 字段: `['pty_id', 'name', 'up_org_name', 'org_name', 'total_asset', 'cash_asset', 'cash_ratio', 'stock_turnover', 'net_inflow']`
- Agent SQL 字段: `[]`
- 错误类型: `agent_sql_execution_failed`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> ask_clarification -> persist_state`

Agent SQL:

```sql

```

### a014

- 问题: 找出3月31日持有ETF但未持有任何债券、期末总资产不低于10万元且一季度有股票交易的客户，列出ETF市值、总资产和股票交易额，按总资产降序取前20名。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 20
- Agent SQL 行数: 20
- 标准 SQL 字段: `['pty_id', 'name', 'total_asset', 'etf_market_value', 'stock_turnover']`
- Agent SQL 字段: `['pty_id', 'total_asset', 'etf_market_value', 'stock_trade_amount']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH cust_asset AS (
    SELECT pty_id, COALESCE(nm_tot_aset,0)+COALESCE(fc_pur_aset,0) AS total_asset
    FROM dws_cust_aset_d
    WHERE data_dt = '20260331' AND COALESCE(nm_tot_aset,0)+COALESCE(fc_pur_aset,0) >= 100000
),
hold_agg AS (
    SELECT h.pty_id, 
           SUM(CASE WHEN p.prdt_type_name = 'ETF' THEN COALESCE(h.mkt_val,0) ELSE 0 END) AS etf_mkt_val,
           MAX(CASE WHEN p.up_prdt_type_name = '债券' THEN 1 ELSE 0 END) AS has_bond
    FROM dwd_cust_hold_d h
    INNER JOIN dim_product p ON h.prdt_id = p.prdt_id
    WHERE h.data_dt = '20260331'
    GROUP BY h.pty_id
),
tran_agg AS (
    SELECT t.pty_id,
           SUM(CASE WHEN p.up_prdt_type_name = '股票' THEN COALESCE(t.buy_amt,0)+COALESCE(t.sell_amt,0) ELSE 0 END) AS stock_trade_amt,
           MAX(CASE WHEN p.up_prdt_type_name = '股票' THEN 1 ELSE 0 END) AS has_stock_trade
    FROM dwd_cust_tran_d t
    INNER JOIN dim_product p ON t.prdt_id = p.prdt_id
    WHERE t.data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY t.pty_id
)
SELECT ca.pty_id, ca.total_asset, 
       COALESCE(ha.etf_mkt_val,0) AS etf_market_value,
       COALESCE(ta.stock_trade_amt,0) AS stock_trade_amount
FROM cust_asset ca
LEFT JOIN hold_agg ha ON ca.pty_id = ha.pty_id
LEFT JOIN tran_agg ta ON ca.pty_id = ta.pty_id
WHERE (ha.has_bond = 0 OR ha.has_bond IS NULL)
  AND ha.etf_mkt_val > 0
  AND ta.has_stock_trade > 0
ORDER BY ca.total_asset DESC
LIMIT 20
```

### a015

- 问题: 请从客户等级维度分析基金持仓客户的交易活跃情况。统计母集限定为2026年3月31日开放式基金持仓市值大于0的客户，每位客户只能计数一次。对每个客户等级输出基金客户数、一季度交易额大于0的活跃客户数、活跃率、基金持仓市值、期末总资产和一季度全品类交易额。客户等级需要通过公共字典翻译，交易或资产缺失按0处理，按基金持仓市值从高到低排序。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 6
- Agent SQL 行数: 6
- 标准 SQL 字段: `['customer_level', 'fund_customer_count', 'active_customer_count', 'active_customer_rate', 'fund_market_value', 'total_asset', 'turnover']`
- Agent SQL 字段: `['customer_level', 'fund_cust_cnt', 'active_cust_cnt', 'active_rate', 'fund_mkt_val', 'total_asset', 'q1_trade_amt']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH fund_holders AS (SELECT h.pty_id, SUM(COALESCE(h.mkt_val, 0)) AS fund_mkt_val FROM dwd_cust_hold_d h INNER JOIN dim_product p ON h.prdt_id = p.prdt_id AND p.up_prdt_type_name = '开放式基金' WHERE h.data_dt = '20260331' GROUP BY h.pty_id HAVING SUM(COALESCE(h.mkt_val, 0)) > 0) SELECT COALESCE(lvl."describe", '未知') AS customer_level, COUNT(DISTINCT f.pty_id) AS fund_cust_cnt, COUNT(DISTINCT CASE WHEN COALESCE(t.q1_trade_amt, 0) > 0 THEN f.pty_id END) AS active_cust_cnt, CASE WHEN COUNT(DISTINCT f.pty_id) = 0 THEN 0 ELSE COUNT(DISTINCT CASE WHEN COALESCE(t.q1_trade_amt, 0) > 0 THEN f.pty_id END)::FLOAT / COUNT(DISTINCT f.pty_id) END AS active_rate, SUM(f.fund_mkt_val) AS fund_mkt_val, SUM(COALESCE(aset.total_asset, 0)) AS total_asset, SUM(COALESCE(t.q1_trade_amt, 0)) AS q1_trade_amt FROM fund_holders f LEFT JOIN ads_cust_info_d cust ON f.pty_id = cust.pty_id AND cust.data_dt = '20260531' LEFT JOIN dim_public lvl ON cust.cust_lvl_cd = lvl.code AND lvl.code_type_id = '100' LEFT JOIN (SELECT pty_id, SUM(COALESCE(nm_tot_aset, 0) + COALESCE(fc_pur_aset, 0)) AS total_asset FROM dws_cust_aset_d WHERE data_dt = '20260331' GROUP BY pty_id) aset ON f.pty_id = aset.pty_id LEFT JOIN (SELECT pty_id, SUM(COALESCE(buy_amt, 0) + COALESCE(sell_amt, 0)) AS q1_trade_amt FROM dwd_cust_tran_d WHERE data_dt BETWEEN '20260101' AND '20260331' GROUP BY pty_id) t ON f.pty_id = t.pty_id GROUP BY customer_level ORDER BY fund_mkt_val DESC
```

### a016

- 问题: 客户留存团队希望识别同时出现多项流失信号的人群。请筛选2026年3月31日总资产低于1月1日、整个一季度资金为净流出、并且证券卖出金额高于买入金额的客户。输出客户编号、姓名、分公司、营业部、期初资产、期末资产、资产下降额、净流出金额、卖出减买入差额和交易费用合计。结果按资产下降额从高到低取前20名；缺少期初或期末资产的客户不参与。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 20
- Agent SQL 行数: 20
- 标准 SQL 字段: `['pty_id', 'name', 'up_org_name', 'org_name', 'begin_asset', 'end_asset', 'asset_loss', 'net_outflow', 'sell_buy_gap', 'total_fee']`
- Agent SQL 字段: `['客户编号', '姓名', '分公司', '营业部', '期初资产', '期末资产', '资产下降额', '净流出金额', '卖出减买入差额', '交易费用合计']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH fin_agg AS (
  SELECT pty_id,
         SUM(coalesce(cash_out,0)+coalesce(tran_out,0)+coalesce(assign_out,0)) as total_outflow,
         SUM(coalesce(cash_in,0)+coalesce(tran_in,0)+coalesce(assign_in,0)) as total_inflow
  FROM dws_cust_fin_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY pty_id
),
tran_agg AS (
  SELECT pty_id,
         SUM(coalesce(sell_amt,0)) as total_sell_amt,
         SUM(coalesce(buy_amt,0)) as total_buy_amt,
         SUM(coalesce(buy_rake,0)+coalesce(buy_fare,0)+coalesce(sell_rake,0)+coalesce(sell_fare,0)) as total_fee
  FROM dwd_cust_tran_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY pty_id
)
SELECT cust.pty_id as 客户编号,
       cust.name as 姓名,
       branch.up_org_name as 分公司,
       branch.org_name as 营业部,
       coalesce(aset_begin.nm_tot_aset,0) + coalesce(aset_begin.fc_pur_aset,0) as 期初资产,
       coalesce(aset_end.nm_tot_aset,0) + coalesce(aset_end.fc_pur_aset,0) as 期末资产,
       (coalesce(aset_begin.nm_tot_aset,0) + coalesce(aset_begin.fc_pur_aset,0)) - (coalesce(aset_end.nm_tot_aset,0) + coalesce(aset_end.fc_pur_aset,0)) as 资产下降额,
       coalesce(fin_agg.total_outflow,0) - coalesce(fin_agg.total_inflow,0) as 净流出金额,
       coalesce(tran_agg.total_sell_amt,0) - coalesce(tran_agg.total_buy_amt,0) as 卖出减买入差额,
       coalesce(tran_agg.total_fee,0) as 交易费用合计
FROM ads_cust_info_d cust
INNER JOIN dws_cust_aset_d aset_begin ON cust.pty_id = aset_begin.pty_id AND aset_begin.data_dt = '20260101'
INNER JOIN dws_cust_aset_d aset_end ON cust.pty_id = aset_end.pty_id AND aset_end.data_dt = '20260331'
LEFT JOIN fin_agg ON cust.pty_id = fin_agg.pty_id
LEFT JOIN tran_agg ON cust.pty_id = tran_agg.pty_id
LEFT JOIN dim_branch branch ON cust.org_id = branch.org_id
WHERE cust.data_dt = '20260531'
  AND (coalesce(aset_end.nm_tot_aset,0) + coalesce(aset_end.fc_pur_aset,0)) < (coalesce(aset_begin.nm_tot_aset,0) + coalesce(aset_begin.fc_pur_aset,0))
  AND coalesce(fin_agg.total_outflow,0) - coalesce(fin_agg.total_inflow,0) > 0
  AND coalesce(tran_agg.total_sell_amt,0) > coalesce(tran_agg.total_buy_amt,0)
ORDER BY 资产下降额 DESC
LIMIT 20
```

### a017

- 问题: 分析一季度内跨过10万元资产门槛的客户：要求客户1月1日总资产低于10万元，3月31日总资产达到或超过10万元。请列出客户等级、期初资产、期末资产、资产增长额、一季度净流入、净流入对资产增长的贡献率以及交易额。净流入贡献率以资产增长额为分母，分母为0时返回NULL。按资产增长额从高到低取前20名。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 12
- Agent SQL 行数: 13
- 标准 SQL 字段: `['pty_id', 'customer_level', 'begin_asset', 'end_asset', 'asset_growth', 'net_inflow', 'net_inflow_contribution', 'turnover']`
- Agent SQL 字段: `['customer_level', 'begin_total_asset', 'end_total_asset', 'asset_growth', 'net_inflow_q1', 'net_inflow_contribution', 'transaction_amount_q1']`
- 错误类型: `行数不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> repair_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH begin_asset AS (
  SELECT pty_id, coalesce(nm_tot_aset,0) + coalesce(fc_pur_aset,0) AS begin_total_asset
  FROM dws_cust_aset_d
  WHERE data_dt = '20260101'
),
end_asset AS (
  SELECT pty_id, coalesce(nm_tot_aset,0) + coalesce(fc_pur_aset,0) AS end_total_asset
  FROM dws_cust_aset_d
  WHERE data_dt = '20260331'
),
net_inflow AS (
  SELECT pty_id,
    SUM(coalesce(cash_in,0) + coalesce(tran_in,0) + coalesce(assign_in,0) - coalesce(cash_out,0) - coalesce(tran_out,0) - coalesce(assign_out,0)) AS net_inflow_q1
  FROM dws_cust_fin_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY pty_id
),
transaction_q1 AS (
  SELECT pty_id,
    SUM(coalesce(buy_amt,0) + coalesce(sell_amt,0)) AS transaction_amount_q1
  FROM dwd_cust_tran_d
  WHERE data_dt BETWEEN '20260101' AND '20260331'
  GROUP BY pty_id
),
cust AS (
  SELECT pty_id, cust_lvl_cd
  FROM ads_cust_info_d
  WHERE data_dt = '20260531'
)
SELECT
  c.cust_lvl_cd AS customer_level,
  coalesce(ba.begin_total_asset, 0) AS begin_total_asset,
  coalesce(ea.end_total_asset, 0) AS end_total_asset,
  (coalesce(ea.end_total_asset, 0) - coalesce(ba.begin_total_asset, 0)) AS asset_growth,
  coalesce(net.net_inflow_q1, 0) AS net_inflow_q1,
  CASE WHEN (coalesce(ea.end_total_asset, 0) - coalesce(ba.begin_total_asset, 0)) = 0 THEN NULL 
       ELSE coalesce(net.net_inflow_q1, 0) / (coalesce(ea.end_total_asset, 0) - coalesce(ba.begin_total_asset, 0)) 
  END AS net_inflow_contribution,
  coalesce(t.transaction_amount_q1, 0) AS transaction_amount_q1
FROM cust c
LEFT JOIN begin_asset ba ON c.pty_id = ba.pty_id
LEFT JOIN end_asset ea ON c.pty_id = ea.pty_id
LEFT JOIN net_inflow net ON c.pty_id = net.pty_id
LEFT JOIN transaction_q1 t ON c.pty_id = t.pty_id
WHERE coalesce(ba.begin_total_asset, 0) < 100000
  AND coalesce(ea.end_total_asset, 0) >= 100000
ORDER BY asset_growth DESC
LIMIT 20
```

### a018

- 问题: 请构建营业部综合经营排名。先以客户归属快照为母集，在营业部粒度统计3月31日总资产、一季度交易额、一季度净流入和交易活跃客户率；随后分别对四个指标在全部营业部中计算percent_rank，并将四个percent_rank直接相加作为综合得分，不做额外权重。输出各原始指标、四个分项得分、综合得分和综合名次，按综合得分降序取前20名。交易及资金数据缺失按0处理。
- 可执行: N
- 精确匹配: N
- 标准 SQL 行数: 15
- Agent SQL 行数: 0
- 标准 SQL 字段: `['up_org_name', 'org_name', 'total_asset', 'turnover', 'net_inflow', 'active_rate', 'asset_score', 'turnover_score', 'flow_score', 'activity_score', 'composite_score', 'overall_rank']`
- Agent SQL 字段: `[]`
- 错误类型: `agent_sql_execution_failed`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> ask_clarification -> persist_state`

Agent SQL:

```sql

```

### a019

- 问题: 风险管理希望查看持仓是否过度集中在单一营业部。请在产品粒度统计3月31日持仓客户数和总持仓市值，并找出每只产品持仓市值最大的营业部及其贡献比例；同时补充该产品一季度交易额。只分析至少有2名持仓客户且总持仓市值大于0的产品，按最大营业部贡献比例降序、总持仓市值降序取前20只产品。最大营业部市值并列时按营业部名称升序取一个。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 20
- Agent SQL 行数: 0
- 标准 SQL 字段: `['prdt_id', 'prdt_name', 'up_prdt_type_name', 'holder_count', 'total_market_value', 'top_branch_name', 'top_branch_market_value', 'top_branch_ratio', 'turnover']`
- Agent SQL 字段: `['prdt_id', 'prdt_name', 'cust_cnt', 'total_mkt_val', 'max_branch_name', 'max_branch_mkt_val', 'contribution_ratio', 'q1_tran_amt']`
- 错误类型: `行数不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH prod_branch_mkt AS (
    SELECT 
        hold.prdt_id,
        cust.org_id,
        branch.org_name,
        SUM(COALESCE(hold.mkt_val, 0)) AS branch_mkt_val
    FROM dwd_cust_hold_d hold
    JOIN ads_cust_info_d cust ON hold.pty_id = cust.pty_id AND cust.data_dt = '20260331'
    JOIN dim_branch branch ON cust.org_id = branch.org_id AND branch.data_dt = '20260331'
    WHERE hold.data_dt = '20260331' AND hold.ccy = '0'
    GROUP BY hold.prdt_id, cust.org_id, branch.org_name
),
prod_total AS (
    SELECT 
        hold.prdt_id,
        COUNT(DISTINCT hold.pty_id) AS cust_cnt,
        SUM(COALESCE(hold.mkt_val, 0)) AS total_mkt_val
    FROM dwd_cust_hold_d hold
    WHERE hold.data_dt = '20260331' AND hold.ccy = '0'
    GROUP BY hold.prdt_id
    HAVING COUNT(DISTINCT hold.pty_id) >= 2 AND SUM(COALESCE(hold.mkt_val, 0)) > 0
),
top_branch_per_prod AS (
    SELECT 
        prdt_id,
        org_name,
        branch_mkt_val,
        ROW_NUMBER() OVER (PARTITION BY prdt_id ORDER BY branch_mkt_val DESC, org_name ASC) AS rn
    FROM prod_branch_mkt
),
prod_tran_amt AS (
    SELECT 
        tran.prdt_id,
        SUM(COALESCE(tran.buy_amt, 0) + COALESCE(tran.sell_amt, 0)) AS q1_tran_amt
    FROM dwd_cust_tran_d tran
    WHERE tran.data_dt BETWEEN '20260101' AND '20260331' AND tran.ccy = '0'
    GROUP BY tran.prdt_id
)
SELECT 
    pt.prdt_id,
    dp.prdt_name,
    pt.cust_cnt,
    pt.total_mkt_val,
    tb.org_name AS max_branch_name,
    tb.branch_mkt_val AS max_branch_mkt_val,
    tb.branch_mkt_val / pt.total_mkt_val AS contribution_ratio,
    COALESCE(pa.q1_tran_amt, 0) AS q1_tran_amt
FROM prod_total pt
JOIN top_branch_per_prod tb ON pt.prdt_id = tb.prdt_id AND tb.rn = 1
LEFT JOIN dim_product dp ON pt.prdt_id = dp.prdt_id
LEFT JOIN prod_tran_amt pa ON pt.prdt_id = pa.prdt_id
ORDER BY contribution_ratio DESC, pt.total_mkt_val DESC
LIMIT 20
```

### a020

- 问题: 数据核对人员想比较客户期末持仓市值与资产汇总口径。请分别汇总2026年3月31日每位客户的普通账户持仓市值、信用账户持仓市值和总持仓市值，再与同日普通账户总资产加信用账户购买资产进行比较。输出客户、分公司、营业部、总资产、三项持仓指标、持仓市值占总资产比例以及“总持仓市值减总资产”的差额。总资产为0时比例返回NULL，不设置异常阈值，直接按持仓资产比降序并以差额降序作为第二排序，取前20名。
- 可执行: N
- 精确匹配: N
- 标准 SQL 行数: 20
- Agent SQL 行数: 0
- 标准 SQL 字段: `['pty_id', 'name', 'up_org_name', 'org_name', 'total_asset', 'holding_market_value', 'normal_holding_value', 'credit_holding_value', 'holding_asset_ratio', 'difference_amount']`
- Agent SQL 字段: `[]`
- 错误类型: `agent_sql_execution_failed`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> ask_clarification -> persist_state`

Agent SQL:

```sql

```

### a021

- 问题: 风控团队希望识别资产规模较高但波动明显的客户。请基于2026年一季度每日资产快照，计算每位客户总资产的日均值、样本标准差、最小值、最大值和变异系数，其中变异系数等于样本标准差除以日均总资产。只保留日均总资产不少于10万元、至少有2个快照且日均资产不为0的客户；再补充一季度资金净流入、交易额以及分公司和营业部。按变异系数从高到低取前20名。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 20
- Agent SQL 行数: 20
- 标准 SQL 字段: `['pty_id', 'name', 'up_org_name', 'org_name', 'snapshot_count', 'avg_daily_asset', 'asset_stddev', 'asset_cv', 'min_asset', 'max_asset', 'net_inflow', 'turnover']`
- Agent SQL 字段: `['pty_id', 'avg_daily_asset', 'stddev_asset', 'min_asset', 'max_asset', 'cv', 'net_cash_in', 'total_trade_amt', 'branch_org_id']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> repair_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH asset_stats AS (
    SELECT pty_id,
           SUM(COALESCE(nm_tot_aset,0)+COALESCE(fc_pur_aset,0)) AS sum_asset,
           COUNT(*) AS day_count,
           STDDEV_SAMP(COALESCE(nm_tot_aset,0)+COALESCE(fc_pur_aset,0)) AS stddev_asset,
           MIN(COALESCE(nm_tot_aset,0)+COALESCE(fc_pur_aset,0)) AS min_asset,
           MAX(COALESCE(nm_tot_aset,0)+COALESCE(fc_pur_aset,0)) AS max_asset
    FROM dws_cust_aset_d
    WHERE data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY pty_id
),
fin_net_in AS (
    SELECT pty_id,
           SUM(COALESCE(cash_in,0) - COALESCE(cash_out,0)) AS net_cash_in
    FROM dws_cust_fin_d
    WHERE data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY pty_id
),
trade_amt AS (
    SELECT pty_id,
           SUM(COALESCE(buy_amt,0) + COALESCE(sell_amt,0)) AS total_trade_amt
    FROM dwd_cust_tran_d
    WHERE data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY pty_id
),
cust_info AS (
    SELECT pty_id, org_id
    FROM ads_cust_info_d
    WHERE data_dt = '20260531'
)
SELECT s.pty_id,
       s.sum_asset / 90.0 AS avg_daily_asset,
       s.stddev_asset,
       s.min_asset,
       s.max_asset,
       s.stddev_asset / (s.sum_asset / 90.0) AS cv,
       COALESCE(f.net_cash_in, 0) AS net_cash_in,
       COALESCE(t.total_trade_amt, 0) AS total_trade_amt,
       c.org_id AS branch_org_id
FROM asset_stats s
LEFT JOIN cust_info c ON s.pty_id = c.pty_id
LEFT JOIN fin_net_in f ON s.pty_id = f.pty_id
LEFT JOIN trade_amt t ON s.pty_id = t.pty_id
WHERE s.day_count >= 2
  AND s.sum_asset / 90.0 >= 100000
  AND s.sum_asset / 90.0 > 0
ORDER BY cv DESC
LIMIT 20
```

### a022

- 问题: 请生成2026年一季度普通账户和信用账户的月度联报。每个月、每种账户来源分别统计资金净流入、买卖交易额、佣金及费用合计、交易活跃客户数，以及月末持仓市值。月末持仓必须取该自然月最后一个可用持仓日期，而不是写死31日。还要用窗口函数计算同一账户来源交易额相对上月的增加额；1月没有上月数据时返回NULL。即使某个月某类账户只出现在资金、交易或持仓中的一张表，也要通过FULL OUTER JOIN保留。
- 可执行: N
- 精确匹配: N
- 标准 SQL 行数: 6
- Agent SQL 行数: 0
- 标准 SQL 字段: `['stat_month', 'sys_source', 'net_inflow', 'turnover', 'total_fee', 'active_customer_count', 'month_end_market_value', 'turnover_mom_change']`
- Agent SQL 字段: `[]`
- 错误类型: `agent_sql_execution_failed`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> ask_clarification -> persist_state`

Agent SQL:

```sql

```

### a023

- 问题: 请追踪一季度退出ETF持仓的客户。客户必须在2026年1月1日持有ETF且ETF市值大于0，同时在3月31日已经没有任何ETF正市值持仓。对这些客户汇总一季度ETF买入金额、卖出金额，并补充1月1日ETF市值、期初总资产、期末总资产和资产变动。输出客户编号和姓名，按ETF卖出金额降序、期初ETF市值降序取前20名。3月31日存在ETF记录但市值为0仍视为已经退出。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 9
- Agent SQL 行数: 9
- 标准 SQL 字段: `['pty_id', 'name', 'begin_etf_value', 'etf_buy_amount', 'etf_sell_amount', 'begin_asset', 'end_asset', 'asset_change']`
- Agent SQL 字段: `['pty_id', 'name', 'etf_buy_amt', 'etf_sell_amt', 'init_etf_mktval', 'begin_total_asset', 'end_total_asset', 'asset_change']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH cust_base AS (
    SELECT pty_id, name
    FROM ads_cust_info_d
    WHERE data_dt = '20260531'
),
init_etf_hold AS (
    SELECT h.pty_id, SUM(COALESCE(h.mkt_val,0)) AS init_etf_mktval
    FROM dwd_cust_hold_d h
    INNER JOIN dim_product p ON h.prdt_id = p.prdt_id
    WHERE h.data_dt = '20260101'
      AND p.prdt_type_name = 'ETF'
    GROUP BY h.pty_id
    HAVING SUM(COALESCE(h.mkt_val,0)) > 0
),
final_etf_hold AS (
    SELECT h.pty_id, SUM(COALESCE(h.mkt_val,0)) AS final_etf_mktval
    FROM dwd_cust_hold_d h
    INNER JOIN dim_product p ON h.prdt_id = p.prdt_id
    WHERE h.data_dt = '20260331'
      AND p.prdt_type_name = 'ETF'
    GROUP BY h.pty_id
),
etf_tran AS (
    SELECT t.pty_id,
           SUM(COALESCE(t.buy_amt,0)) AS total_buy_amt,
           SUM(COALESCE(t.sell_amt,0)) AS total_sell_amt
    FROM dwd_cust_tran_d t
    INNER JOIN dim_product p ON t.prdt_id = p.prdt_id
    WHERE t.data_dt BETWEEN '20260101' AND '20260331'
      AND p.prdt_type_name = 'ETF'
    GROUP BY t.pty_id
),
asset_start AS (
    SELECT pty_id,
           COALESCE(nm_tot_aset,0) + COALESCE(fc_pur_aset,0) AS begin_total_asset
    FROM dws_cust_aset_d
    WHERE data_dt = '20260101'
),
asset_end AS (
    SELECT pty_id,
           COALESCE(nm_tot_aset,0) + COALESCE(fc_pur_aset,0) AS end_total_asset
    FROM dws_cust_aset_d
    WHERE data_dt = '20260331'
)
SELECT cust.pty_id,
       cust.name,
       COALESCE(tran.total_buy_amt,0) AS etf_buy_amt,
       COALESCE(tran.total_sell_amt,0) AS etf_sell_amt,
       init.init_etf_mktval AS init_etf_mktval,
       COALESCE(s.begin_total_asset,0) AS begin_total_asset,
       COALESCE(e.end_total_asset,0) AS end_total_asset,
       COALESCE(e.end_total_asset,0) - COALESCE(s.begin_total_asset,0) AS asset_change
FROM cust_base cust
INNER JOIN init_etf_hold init ON cust.pty_id = init.pty_id
LEFT JOIN final_etf_hold fin ON cust.pty_id = fin.pty_id
LEFT JOIN etf_tran tran ON cust.pty_id = tran.pty_id
LEFT JOIN asset_start s ON cust.pty_id = s.pty_id
LEFT JOIN asset_end e ON cust.pty_id = e.pty_id
WHERE COALESCE(fin.final_etf_mktval, 0) = 0
ORDER BY etf_sell_amt DESC, init.init_etf_mktval DESC
LIMIT 20
```

### a024

- 问题: 分析一季度新增开放式基金持仓客户的营业部分布。新增客户定义为2026年1月1日没有开放式基金正市值持仓，但3月31日开放式基金持仓市值大于0。请按分公司和营业部统计新增客户数、期末基金市值、期末总资产、一季度净流入，以及其中净流入为正的客户数。事实表先汇总到客户粒度，无资金流水按净流入0处理，按新增客户数和基金市值依次降序取前20个营业部。
- 可执行: N
- 精确匹配: N
- 标准 SQL 行数: 4
- Agent SQL 行数: 0
- 标准 SQL 字段: `['up_org_name', 'org_name', 'new_fund_customer_count', 'fund_market_value', 'total_asset', 'net_inflow', 'positive_flow_customer_count']`
- Agent SQL 字段: `[]`
- 错误类型: `agent_sql_execution_failed`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> ask_clarification -> persist_state`

Agent SQL:

```sql

```

### a025

- 问题: 为了避免不同客户等级的资产规模差异干扰，请在每个客户等级内部，按照2026年3月31日总资产从低到高使用NTILE(4)划分四个资产组。然后按“客户等级+四分位组”统计客户数、平均总资产、一季度净流入、一季度交易额、期末持仓市值和交易活跃率。客户等级需翻译为中文，交易、资金和持仓缺失按0处理。四分位编号1表示本等级最低资产组，4表示最高资产组，结果按客户等级和四分位编号排序。
- 可执行: N
- 精确匹配: N
- 标准 SQL 行数: 24
- Agent SQL 行数: 0
- 标准 SQL 字段: `['customer_level', 'asset_quartile', 'customer_count', 'avg_asset', 'net_inflow', 'turnover', 'holding_market_value', 'active_rate']`
- Agent SQL 字段: `[]`
- 错误类型: `agent_sql_execution_failed`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> ask_clarification -> persist_state`

Agent SQL:

```sql

```

### a026

- 问题: 管理层想评估营业部对少数头部客户的资产依赖程度。请按3月31日总资产对每个营业部的客户从高到低编号，计算营业部总客户数、总资产、前5名客户资产合计及其占比，同时补充一季度净流入和交易活跃率。营业部不足5名客户时，前5名资产按实际全部客户计算；总资产为0时占比返回NULL。按前5名资产占比降序、营业部总资产降序取前20名。
- 可执行: N
- 精确匹配: N
- 标准 SQL 行数: 15
- Agent SQL 行数: 0
- 标准 SQL 字段: `['up_org_name', 'org_name', 'customer_count', 'total_asset', 'top5_asset', 'top5_asset_ratio', 'net_inflow', 'active_rate']`
- Agent SQL 字段: `[]`
- 错误类型: `agent_sql_execution_failed`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> ask_clarification -> persist_state`

Agent SQL:

```sql

```

### a027

- 问题: 产品经理希望同时观察交易方向和期末沉淀。请按产品统计2026年一季度买入金额、卖出金额、净买入金额、交易客户数和交易客户覆盖的营业部数量，再补充3月31日持仓客户数与持仓市值。只保留买入或卖出金额大于0的产品。最终按净买入金额绝对值从高到低取前20只产品，并返回产品一级、二级分类；净买入为负表示净卖出。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 20
- Agent SQL 行数: 20
- 标准 SQL 字段: `['prdt_id', 'prdt_name', 'up_prdt_type_name', 'prdt_type_name', 'buy_amount', 'sell_amount', 'net_buy_amount', 'trading_customer_count', 'branch_coverage', 'holder_count', 'market_value']`
- Agent SQL 字段: `['prdt_id', 'up_prdt_type_name', 'prdt_type_name', 'buy_amt', 'sell_amt', 'net_buy_amt', 'tran_cust_cnt', 'branch_cnt', 'hold_cust_cnt', 'hold_mkt_val']`
- 错误类型: `sql_validation_failed`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> repair_sql -> validate_sql -> repair_sql -> validate_sql -> human_review_or_explain -> persist_state`

Agent SQL:

```sql
WITH tran_agg AS (
  SELECT 
    t.prdt_id,
    MAX(p.up_prdt_type_name) AS up_prdt_type_name,
    MAX(p.prdt_type_name) AS prdt_type_name,
    SUM(COALESCE(t.buy_amt, 0)) AS buy_amt,
    SUM(COALESCE(t.sell_amt, 0)) AS sell_amt,
    COUNT(DISTINCT t.pty_id) AS tran_cust_cnt,
    COUNT(DISTINCT c.org_id) AS branch_cnt
  FROM dwd_cust_tran_d t
  INNER JOIN dim_product p ON t.prdt_id = p.prdt_id
  LEFT JOIN ads_cust_info_d c ON t.pty_id = c.pty_id AND c.data_dt = '20260531'
  WHERE t.data_dt BETWEEN '20260101' AND '20260331'
    AND t.ccy = '0'
  GROUP BY t.prdt_id, p.up_prdt_type_name, p.prdt_type_name
),
hold_agg AS (
  SELECT 
    h.prdt_id,
    MAX(p.up_prdt_type_name) AS up_prdt_type_name,
    MAX(p.prdt_type_name) AS prdt_type_name,
    COUNT(DISTINCT h.pty_id) AS hold_cust_cnt,
    SUM(COALESCE(h.mkt_val, 0)) AS hold_mkt_val
  FROM dwd_cust_hold_d h
  INNER JOIN dim_product p ON h.prdt_id = p.prdt_id
  WHERE h.data_dt = '20260331'
    AND h.ccy = '0'
  GROUP BY h.prdt_id, p.up_prdt_type_name, p.prdt_type_name
)
SELECT 
  COALESCE(t.prdt_id, h.prdt_id) AS prdt_id,
  COALESCE(t.up_prdt_type_name, h.up_prdt_type_name) AS up_prdt_type_name,
  COALESCE(t.prdt_type_name, h.prdt_type_name) AS prdt_type_name,
  COALESCE(t.buy_amt, 0) AS buy_amt,
  COALESCE(t.sell_amt, 0) AS sell_amt,
  COALESCE(t.buy_amt, 0) - COALESCE(t.sell_amt, 0) AS net_buy_amt,
  COALESCE(t.tran_cust_cnt, 0) AS tran_cust_cnt,
  COALESCE(t.branch_cnt, 0) AS branch_cnt,
  COALESCE(h.hold_cust_cnt, 0) AS hold_cust_cnt,
  COALESCE(h.hold_mkt_val, 0) AS hold_mkt_val
FROM tran_agg t
FULL OUTER JOIN hold_agg h ON t.prdt_id = h.prdt_id
WHERE COALESCE(t.buy_amt, 0) > 0 OR COALESCE(t.sell_amt, 0) > 0
ORDER BY ABS(COALESCE(t.buy_amt, 0) - COALESCE(t.sell_amt, 0)) DESC
LIMIT 20
```

### a028

- 问题: 请找出2026年3月31日同时持有股票和开放式基金、但没有任何债券正市值持仓的客户。股票和基金都必须是持仓市值大于0，单纯存在零市值记录不算持有。对符合条件的客户分别汇总股票市值和基金市值，并补充期末总资产、一季度交易额和净流入，按股票市值与基金市值之和从高到低取前20名。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 20
- Agent SQL 行数: 20
- 标准 SQL 字段: `['pty_id', 'name', 'stock_market_value', 'fund_market_value', 'total_asset', 'turnover', 'net_inflow']`
- Agent SQL 字段: `['pty_id', 'stock_mkv', 'fund_mkv', 'total_asset', 'trans_amt', 'net_inflow', 'total_mkv']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> repair_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
SELECT
    h.pty_id,
    SUM(CASE WHEN p.up_prdt_type_name = '股票' THEN COALESCE(h.mkt_val, 0) ELSE 0 END) AS stock_mkv,
    SUM(CASE WHEN p.up_prdt_type_name = '开放式基金' THEN COALESCE(h.mkt_val, 0) ELSE 0 END) AS fund_mkv,
    COALESCE(a.total_asset, 0) AS total_asset,
    COALESCE(t.trans_amt, 0) AS trans_amt,
    COALESCE(f.total_in, 0) - COALESCE(f.total_out, 0) AS net_inflow,
    (SUM(CASE WHEN p.up_prdt_type_name = '股票' THEN COALESCE(h.mkt_val, 0) ELSE 0 END) + SUM(CASE WHEN p.up_prdt_type_name = '开放式基金' THEN COALESCE(h.mkt_val, 0) ELSE 0 END)) AS total_mkv
FROM dwd_cust_hold_d h
INNER JOIN dim_product p ON h.prdt_id = p.prdt_id
LEFT JOIN (
    SELECT pty_id, COALESCE(nm_tot_aset, 0) + COALESCE(fc_pur_aset, 0) AS total_asset
    FROM dws_cust_aset_d
    WHERE data_dt = '20260331'
) a ON h.pty_id = a.pty_id
LEFT JOIN (
    SELECT pty_id, SUM(COALESCE(buy_amt, 0) + COALESCE(sell_amt, 0)) AS trans_amt
    FROM dwd_cust_tran_d
    WHERE data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY pty_id
) t ON h.pty_id = t.pty_id
LEFT JOIN (
    SELECT pty_id,
           SUM(COALESCE(cash_in, 0) + COALESCE(tran_in, 0) + COALESCE(assign_in, 0)) AS total_in,
           SUM(COALESCE(cash_out, 0) + COALESCE(tran_out, 0) + COALESCE(assign_out, 0)) AS total_out
    FROM dws_cust_fin_d
    WHERE data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY pty_id
) f ON h.pty_id = f.pty_id
WHERE h.data_dt = '20260331'
GROUP BY h.pty_id, a.total_asset, t.trans_amt, f.total_in, f.total_out
HAVING 
    SUM(CASE WHEN p.up_prdt_type_name = '股票' THEN COALESCE(h.mkt_val, 0) ELSE 0 END) > 0
    AND SUM(CASE WHEN p.up_prdt_type_name = '开放式基金' THEN COALESCE(h.mkt_val, 0) ELSE 0 END) > 0
    AND SUM(CASE WHEN p.up_prdt_type_name = '债券' THEN COALESCE(h.mkt_val, 0) ELSE 0 END) = 0
ORDER BY total_mkv DESC
LIMIT 20
```

### a029

- 问题: 请从人口属性角度比较客户价值。将客户年龄划分为30岁以下、30至44岁、45至59岁、60岁及以上四档，并按性别、学历和年龄档组合统计客户数、3月31日平均总资产、一季度净流入、一季度交易额、开放式基金持仓客户率及基金持仓市值。性别和学历都要通过公共字典翻译；没有资产、交易、资金或基金持仓时按0处理。按客户数降序、平均资产降序排列。
- 可执行: N
- 精确匹配: N
- 标准 SQL 行数: 30
- Agent SQL 行数: 0
- 标准 SQL 字段: `['gender_name', 'education', 'age_band', 'customer_count', 'avg_asset', 'net_inflow', 'turnover', 'fund_customer_rate', 'fund_market_value']`
- Agent SQL 字段: `[]`
- 错误类型: `agent_sql_execution_failed`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> ask_clarification -> persist_state`

Agent SQL:

```sql

```

### a030

- 问题: 请制作一张供管理层查看的“分公司×客户等级”综合经营报表。以2026年5月31日客户快照为唯一母集，客户等级通过公共字典翻译；资产取1月1日和3月31日两个快照，资金、交易统计整个一季度，持仓取3月31日。每个分公司和客户等级需要输出客户数、期末总资产、资产增长额、净流入、交易额、交易佣金及费用、期末持仓市值、基金持仓客户数和基金渗透率。基金客户指开放式基金期末持仓市值大于0。各事实表必须先聚合到客户粒度再连接，缺失指标按0处理，按期末总资产降序取前20个组合。
- 可执行: Y
- 精确匹配: N
- 标准 SQL 行数: 20
- Agent SQL 行数: 20
- 标准 SQL 字段: `['up_org_name', 'customer_level', 'customer_count', 'end_asset', 'asset_growth', 'net_inflow', 'turnover', 'total_fee', 'holding_market_value', 'fund_customer_count', 'fund_penetration_rate']`
- Agent SQL 字段: `['branch_name', 'customer_level', 'customer_count', 'total_end_asset', 'asset_growth', 'net_inflow', 'trade_amount', 'trade_commission_fee', 'total_holding_mv', 'fund_holder_count', 'fund_penetration']`
- 错误类型: `字段不匹配`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> repair_sql -> validate_sql -> repair_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
WITH cust_base AS (
    SELECT cust.pty_id, branch.up_org_name, lvl."describe" AS cust_lvl_name
    FROM ads_cust_info_d cust
    LEFT JOIN dim_branch branch ON cust.org_id = branch.org_id AND branch.data_dt = '20260531'
    LEFT JOIN dim_public lvl ON cust.cust_lvl_cd = lvl.code AND lvl.code_type_id = '100'
    WHERE cust.data_dt = '20260531'
),
asset_begin AS (
    SELECT pty_id, SUM(COALESCE(nm_tot_aset,0) + COALESCE(fc_pur_aset,0)) AS begin_asset
    FROM dws_cust_aset_d
    WHERE data_dt = '20260101'
    GROUP BY pty_id
),
asset_end AS (
    SELECT pty_id, SUM(COALESCE(nm_tot_aset,0) + COALESCE(fc_pur_aset,0)) AS end_asset
    FROM dws_cust_aset_d
    WHERE data_dt = '20260331'
    GROUP BY pty_id
),
fin_agg AS (
    SELECT pty_id, SUM(COALESCE(cash_in,0) + COALESCE(tran_in,0) + COALESCE(assign_in,0) - COALESCE(cash_out,0) - COALESCE(tran_out,0) - COALESCE(assign_out,0)) AS net_inflow
    FROM dws_cust_fin_d
    WHERE data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY pty_id
),
tran_agg AS (
    SELECT pty_id,
        SUM(COALESCE(buy_amt,0) + COALESCE(sell_amt,0)) AS trade_amt,
        SUM(COALESCE(buy_rake,0) + COALESCE(sell_rake,0) + COALESCE(buy_fare,0) + COALESCE(sell_fare,0)) AS trade_fee
    FROM dwd_cust_tran_d
    WHERE data_dt BETWEEN '20260101' AND '20260331'
    GROUP BY pty_id
),
hold_agg AS (
    SELECT pty_id, SUM(COALESCE(mkt_val,0)) AS holding_mv
    FROM dwd_cust_hold_d
    WHERE data_dt = '20260331'
    GROUP BY pty_id
),
fund_holders AS (
    SELECT DISTINCT hold.pty_id
    FROM dwd_cust_hold_d hold
    JOIN dim_product prdt ON hold.prdt_id = prdt.prdt_id
    WHERE hold.data_dt = '20260331'
      AND prdt.up_prdt_type_name = '开放式基金'
      AND hold.mkt_val > 0
),
customer_metrics AS (
    SELECT 
        c.up_org_name,
        c.cust_lvl_name,
        c.pty_id,
        COALESCE(ae.end_asset, 0) AS end_asset,
        COALESCE(ab.begin_asset, 0) AS begin_asset,
        COALESCE(fn.net_inflow, 0) AS net_inflow,
        COALESCE(ta.trade_amt, 0) AS trade_amt,
        COALESCE(ta.trade_fee, 0) AS trade_fee,
        COALESCE(ha.holding_mv, 0) AS holding_mv,
        CASE WHEN fh.pty_id IS NOT NULL THEN 1 ELSE 0 END AS is_fund_holder
    FROM cust_base c
    LEFT JOIN asset_end ae ON c.pty_id = ae.pty_id
    LEFT JOIN asset_begin ab ON c.pty_id = ab.pty_id
    LEFT JOIN fin_agg fn ON c.pty_id = fn.pty_id
    LEFT JOIN tran_agg ta ON c.pty_id = ta.pty_id
    LEFT JOIN hold_agg ha ON c.pty_id = ha.pty_id
    LEFT JOIN fund_holders fh ON c.pty_id = fh.pty_id
)
SELECT 
    up_org_name AS branch_name,
    cust_lvl_name AS customer_level,
    COUNT(DISTINCT pty_id) AS customer_count,
    SUM(end_asset) AS total_end_asset,
    SUM(end_asset - begin_asset) AS asset_growth,
    SUM(net_inflow) AS net_inflow,
    SUM(trade_amt) AS trade_amount,
    SUM(trade_fee) AS trade_commission_fee,
    SUM(holding_mv) AS total_holding_mv,
    COUNT(DISTINCT CASE WHEN is_fund_holder = 1 THEN pty_id END) AS fund_holder_count,
    CASE WHEN COUNT(DISTINCT pty_id) = 0 THEN 0 
         ELSE CAST(COUNT(DISTINCT CASE WHEN is_fund_holder = 1 THEN pty_id END) AS DOUBLE) / COUNT(DISTINCT pty_id) 
    END AS fund_penetration
FROM customer_metrics
GROUP BY up_org_name, cust_lvl_name
ORDER BY total_end_asset DESC
LIMIT 20
```
