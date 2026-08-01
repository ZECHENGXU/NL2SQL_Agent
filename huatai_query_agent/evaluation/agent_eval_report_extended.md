# Agent Evaluation Report

- SQL mode: `demo`
- Total cases: 21
- Executable rate: 21/21 (100.00%)
- Exact result match rate: 21/21 (100.00%)
- Row count match rate: 21/21 (100.00%)
- Average execution elapsed: 30.74 ms
- LLM calls: 0
- LLM total tokens: 0

| Query ID | Executable | Exact Match | Row Count | Columns | Error Type |
|----------|------------|-------------|-----------|---------|------------|
| q001 | Y | Y | 1/1 | Y | ok |
| q002 | Y | Y | 3/3 | Y | ok |
| q003 | Y | Y | 1/1 | Y | ok |
| q004 | Y | Y | 15/15 | Y | ok |
| q005 | Y | Y | 1/1 | Y | ok |
| q006 | Y | Y | 24/24 | Y | ok |
| q007 | Y | Y | 3/3 | Y | ok |
| v001 | Y | Y | 1/1 | Y | ok |
| v002 | Y | Y | 1/1 | Y | ok |
| v003 | Y | Y | 3/3 | Y | ok |
| v004 | Y | Y | 3/3 | Y | ok |
| v005 | Y | Y | 1/1 | Y | ok |
| v006 | Y | Y | 1/1 | Y | ok |
| v007 | Y | Y | 15/15 | Y | ok |
| v008 | Y | Y | 15/15 | Y | ok |
| v009 | Y | Y | 1/1 | Y | ok |
| v010 | Y | Y | 1/1 | Y | ok |
| v011 | Y | Y | 24/24 | Y | ok |
| v012 | Y | Y | 24/24 | Y | ok |
| v013 | Y | Y | 3/3 | Y | ok |
| v014 | Y | Y | 3/3 | Y | ok |

## Case Details

### q001

- Question: 学历本科以上的男性客户，年龄超过50岁的有多少个？
- Executable: Y
- Exact match: Y
- Standard rows: 1
- Agent rows: 1
- Standard columns: `['customer_count']`
- Agent columns: `['customer_count']`
- Error type: `ok`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
-- question: 学历本科以上的男性客户，年龄超过50岁的有多少个？
select
    count(*) as customer_count
from ads_cust_info_d
where data_dt = '20260531'
  and edu_cd in ('6000002', '6000003', '6000004')
  and gender_cd = '5000002'
  and cust_age > 50
```

### q002

- Question: 不同年龄段的客户总资产分布情况如何？
- Executable: Y
- Exact match: Y
- Standard rows: 3
- Agent rows: 3
- Standard columns: `['cust_age_type', 'customer_count', 'total_asset']`
- Agent columns: `['cust_age_type', 'customer_count', 'total_asset']`
- Error type: `ok`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
-- question: 不同年龄段的客户总资产分布情况如何？
select
    case
        when cust.cust_age < 30 then '<30'
        when cust.cust_age >= 30 and cust.cust_age < 50 then '[30,50)'
        when cust.cust_age >= 50 and cust.cust_age < 60 then '[50,60)'
        when cust.cust_age >= 60 then '[60,)'
    end as cust_age_type,
    count(distinct cust.pty_id) as customer_count,
    sum(coalesce(aset.nm_tot_aset, 0) + coalesce(aset.fc_pur_aset, 0)) as total_asset
from ads_cust_info_d cust
left join dws_cust_aset_d aset
  on cust.pty_id = aset.pty_id
 and aset.data_dt = '20260331'
where cust.data_dt = '20260531'
group by cust_age_type
order by
    case cust_age_type
        when '<30' then 1
        when '[30,50)' then 2
        when '[50,60)' then 3
        when '[60,)' then 4
        else 99
    end
```

### q003

- Question: 钻石卡男性客户、年龄大于40岁、持有比亚迪市值超过1000元，计算2026年Q1盈亏。
- Executable: Y
- Exact match: Y
- Standard rows: 1
- Agent rows: 1
- Standard columns: `['pty_id', 'byd_mkt_val', 'begin_total_asset', 'end_total_asset', 'asset_in', 'asset_out', 'q1_profit_loss']`
- Agent columns: `['pty_id', 'byd_mkt_val', 'begin_total_asset', 'end_total_asset', 'asset_in', 'asset_out', 'q1_profit_loss']`
- Error type: `ok`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
-- question: 钻石卡男性客户、年龄大于40岁、持有比亚迪市值超过1000元，计算2026年Q1盈亏。
with custinfo as (
    select pty_id
    from ads_cust_info_d
    where data_dt = '20260531'
      and cust_lvl_cd = '1000001'
      and gender_cd = '5000002'
      and cust_age > 40
),
byd_holders as (
    select
        hold.pty_id,
        sum(coalesce(hold.mkt_val, 0)) as byd_mkt_val
    from dwd_cust_hold_d hold
    inner join dim_product prdt
      on hold.prdt_id = prdt.prdt_id
    where hold.data_dt = '20260331'
      and prdt.prdt_name = '比亚迪'
      and prdt.prdt_type_name = 'A股'
      and exists (
          select 1 from custinfo c
          where c.pty_id = hold.pty_id
      )
    group by hold.pty_id
    having sum(coalesce(hold.mkt_val, 0)) > 1000
),
begin_asset as (
    select
        pty_id,
        coalesce(nm_tot_aset, 0) + coalesce(fc_pur_aset, 0) as begin_total_asset
    from dws_cust_aset_d
    where data_dt = '20260101'
),
end_asset as (
    select
        pty_id,
        coalesce(nm_tot_aset, 0) + coalesce(fc_pur_aset, 0) as end_total_asset
    from dws_cust_aset_d
    where data_dt = '20260331'
),
asset_flow as (
    select
        pty_id,
        sum(coalesce(cash_in, 0) + coalesce(tran_in, 0) + coalesce(assign_in, 0)) as asset_in,
        sum(coalesce(cash_out, 0) + coalesce(tran_out, 0) + coalesce(assign_out, 0)) as asset_out
    from dws_cust_fin_d
    where data_dt between '20260101' and '20260331'
    group by pty_id
)
select
    h.pty_id,
    h.byd_mkt_val,
    coalesce(b.begin_total_asset, 0) as begin_total_asset,
    coalesce(e.end_total_asset, 0) as end_total_asset,
    coalesce(f.asset_in, 0) as asset_in,
    coalesce(f.asset_out, 0) as asset_out,
    coalesce(e.end_total_asset, 0)
      - coalesce(b.begin_total_asset, 0)
      + coalesce(f.asset_out, 0)
      - coalesce(f.asset_in, 0) as q1_profit_loss
from byd_holders h
left join begin_asset b on h.pty_id = b.pty_id
left join end_asset e on h.pty_id = e.pty_id
left join asset_flow f on h.pty_id = f.pty_id
order by q1_profit_loss desc
```

### q004

- Question: 分公司和营业部的客户省份分布统计。
- Executable: Y
- Exact match: Y
- Standard rows: 15
- Agent rows: 15
- Standard columns: `['up_org_name', 'org_name', 'prov_name', 'city_name', 'customer_count']`
- Agent columns: `['up_org_name', 'org_name', 'prov_name', 'city_name', 'customer_count']`
- Error type: `ok`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
-- question: 分公司和营业部的客户省份分布统计。
select
    branch.up_org_name,
    branch.org_name,
    cust.prov_name,
    cust.city_name,
    count(*) as customer_count
from ads_cust_info_d cust
inner join dim_branch branch
  on cust.org_id = branch.org_id
where cust.data_dt = '20260531'
group by
    branch.up_org_name,
    branch.org_name,
    cust.prov_name,
    cust.city_name
order by customer_count desc, branch.up_org_name, branch.org_name
```

### q005

- Question: 2026年Q1交易过招商银行A股，并且在Q1末普通账户持有中国平安A股的客户有哪些？
- Executable: Y
- Exact match: Y
- Standard rows: 1
- Agent rows: 1
- Standard columns: `['pty_id', 'cmb_transaction_amount', 'pingan_market_value']`
- Agent columns: `['pty_id', 'cmb_transaction_amount', 'pingan_market_value']`
- Error type: `ok`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
-- question: 2026年Q1交易过招商银行A股，并且在Q1末普通账户持有中国平安A股的客户有哪些？
with cmb_traders as (
    select
        tran.pty_id,
        sum(coalesce(tran.buy_amt, 0) + coalesce(tran.sell_amt, 0)) as cmb_transaction_amount
    from dwd_cust_tran_d tran
    inner join dim_product prdt
      on tran.prdt_id = prdt.prdt_id
    where tran.data_dt between '20260101' and '20260331'
      and prdt.prdt_name = '招商银行'
      and prdt.prdt_type_name = 'A股'
    group by tran.pty_id
    having sum(coalesce(tran.buy_amt, 0) + coalesce(tran.sell_amt, 0)) > 0
),
pingan_holders as (
    select
        hold.pty_id,
        sum(coalesce(hold.mkt_val, 0)) as pingan_market_value
    from dwd_cust_hold_d hold
    inner join dim_product prdt
      on hold.prdt_id = prdt.prdt_id
    where hold.data_dt = '20260331'
      and hold.sys_source = 'nm'
      and prdt.prdt_name = '中国平安'
      and prdt.prdt_type_name = 'A股'
    group by hold.pty_id
    having sum(coalesce(hold.mkt_val, 0)) > 0
)
select
    trader.pty_id,
    trader.cmb_transaction_amount,
    holder.pingan_market_value
from cmb_traders trader
inner join pingan_holders holder
  on trader.pty_id = holder.pty_id
order by trader.cmb_transaction_amount desc
```

### q006

- Question: 2026年Q1日均资产大于30万，且股票交易金额大于10万的客户，持有哪些产品类型？
- Executable: Y
- Exact match: Y
- Standard rows: 24
- Agent rows: 24
- Standard columns: `['up_prdt_type_name', 'prdt_type_name', 'customer_count', 'total_market_value']`
- Agent columns: `['up_prdt_type_name', 'prdt_type_name', 'customer_count', 'total_market_value']`
- Error type: `ok`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
-- question: 2026年Q1日均资产大于30万，且股票交易金额大于10万的客户，持有哪些产品类型？
with high_asset_customers as (
    select
        pty_id,
        sum(coalesce(nm_tot_aset, 0) + coalesce(fc_pur_aset, 0)) / 90.0 as avg_daily_asset
    from dws_cust_aset_d
    where data_dt between '20260101' and '20260331'
    group by pty_id
    having sum(coalesce(nm_tot_aset, 0) + coalesce(fc_pur_aset, 0)) / 90.0 > 300000
),
stock_active_customers as (
    select
        tran.pty_id,
        sum(coalesce(tran.buy_amt, 0) + coalesce(tran.sell_amt, 0)) as stock_transaction_amount
    from dwd_cust_tran_d tran
    inner join dim_product prdt
      on tran.prdt_id = prdt.prdt_id
    inner join high_asset_customers high_asset
      on tran.pty_id = high_asset.pty_id
    where tran.data_dt between '20260101' and '20260331'
      and prdt.up_prdt_type_name = '股票'
    group by tran.pty_id
    having sum(coalesce(tran.buy_amt, 0) + coalesce(tran.sell_amt, 0)) > 100000
)
select
    prdt.up_prdt_type_name,
    prdt.prdt_type_name,
    count(distinct active.pty_id) as customer_count,
    sum(coalesce(hold.mkt_val, 0)) as total_market_value
from stock_active_customers active
inner join dwd_cust_hold_d hold
  on active.pty_id = hold.pty_id
 and hold.data_dt = '20260331'
inner join dim_product prdt
  on hold.prdt_id = prdt.prdt_id
group by
    prdt.up_prdt_type_name,
    prdt.prdt_type_name
order by total_market_value desc
```

### q007

- Question: 查询2026年1月10日至2026年2月15日期间，科创板交易金额超过25万的客户营业部分布。
- Executable: Y
- Exact match: Y
- Standard rows: 3
- Agent rows: 3
- Standard columns: `['up_org_name', 'org_name', 'customer_count', 'total_transaction_amount']`
- Agent columns: `['up_org_name', 'org_name', 'customer_count', 'total_transaction_amount']`
- Error type: `ok`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
-- question: 查询2026年1月10日至2026年2月15日期间，科创板交易金额超过25万的客户营业部分布。
with star_market_active as (
    select
        tran.pty_id,
        sum(coalesce(tran.buy_amt, 0) + coalesce(tran.sell_amt, 0)) as star_market_transaction_amount
    from dwd_cust_tran_d tran
    inner join dim_product prdt
      on tran.prdt_id = prdt.prdt_id
    where tran.data_dt between '20260110' and '20260215'
      and prdt.prdt_type_name = '科创板'
    group by tran.pty_id
    having sum(coalesce(tran.buy_amt, 0) + coalesce(tran.sell_amt, 0)) > 250000
)
select
    branch.up_org_name,
    branch.org_name,
    count(distinct cust.pty_id) as customer_count,
    sum(active.star_market_transaction_amount) as total_transaction_amount
from star_market_active active
inner join ads_cust_info_d cust
  on active.pty_id = cust.pty_id
 and cust.data_dt = '20260531'
left join dim_branch branch
  on cust.org_id = branch.org_id
group by
    branch.up_org_name,
    branch.org_name
order by total_transaction_amount desc
```

### v001

- Question: 本科及以上男性客户，年龄大于50岁的客户数是多少？
- Executable: Y
- Exact match: Y
- Standard rows: 1
- Agent rows: 1
- Standard columns: `['customer_count']`
- Agent columns: `['customer_count']`
- Error type: `ok`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
-- question: 学历本科以上的男性客户，年龄超过50岁的有多少个？
select
    count(*) as customer_count
from ads_cust_info_d
where data_dt = '20260531'
  and edu_cd in ('6000002', '6000003', '6000004')
  and gender_cd = '5000002'
  and cust_age > 50
```

### v002

- Question: 统计男性、本科以上、50岁以上客户数量。
- Executable: Y
- Exact match: Y
- Standard rows: 1
- Agent rows: 1
- Standard columns: `['customer_count']`
- Agent columns: `['customer_count']`
- Error type: `ok`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
-- question: 学历本科以上的男性客户，年龄超过50岁的有多少个？
select
    count(*) as customer_count
from ads_cust_info_d
where data_dt = '20260531'
  and edu_cd in ('6000002', '6000003', '6000004')
  and gender_cd = '5000002'
  and cust_age > 50
```

### v003

- Question: 客户总资产按不同年龄段怎么分布？
- Executable: Y
- Exact match: Y
- Standard rows: 3
- Agent rows: 3
- Standard columns: `['cust_age_type', 'customer_count', 'total_asset']`
- Agent columns: `['cust_age_type', 'customer_count', 'total_asset']`
- Error type: `ok`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
-- question: 不同年龄段的客户总资产分布情况如何？
select
    case
        when cust.cust_age < 30 then '<30'
        when cust.cust_age >= 30 and cust.cust_age < 50 then '[30,50)'
        when cust.cust_age >= 50 and cust.cust_age < 60 then '[50,60)'
        when cust.cust_age >= 60 then '[60,)'
    end as cust_age_type,
    count(distinct cust.pty_id) as customer_count,
    sum(coalesce(aset.nm_tot_aset, 0) + coalesce(aset.fc_pur_aset, 0)) as total_asset
from ads_cust_info_d cust
left join dws_cust_aset_d aset
  on cust.pty_id = aset.pty_id
 and aset.data_dt = '20260331'
where cust.data_dt = '20260531'
group by cust_age_type
order by
    case cust_age_type
        when '<30' then 1
        when '[30,50)' then 2
        when '[50,60)' then 3
        when '[60,)' then 4
        else 99
    end
```

### v004

- Question: 按年龄段统计客户数量和总资产分布情况。
- Executable: Y
- Exact match: Y
- Standard rows: 3
- Agent rows: 3
- Standard columns: `['cust_age_type', 'customer_count', 'total_asset']`
- Agent columns: `['cust_age_type', 'customer_count', 'total_asset']`
- Error type: `ok`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
-- question: 不同年龄段的客户总资产分布情况如何？
select
    case
        when cust.cust_age < 30 then '<30'
        when cust.cust_age >= 30 and cust.cust_age < 50 then '[30,50)'
        when cust.cust_age >= 50 and cust.cust_age < 60 then '[50,60)'
        when cust.cust_age >= 60 then '[60,)'
    end as cust_age_type,
    count(distinct cust.pty_id) as customer_count,
    sum(coalesce(aset.nm_tot_aset, 0) + coalesce(aset.fc_pur_aset, 0)) as total_asset
from ads_cust_info_d cust
left join dws_cust_aset_d aset
  on cust.pty_id = aset.pty_id
 and aset.data_dt = '20260331'
where cust.data_dt = '20260531'
group by cust_age_type
order by
    case cust_age_type
        when '<30' then 1
        when '[30,50)' then 2
        when '[50,60)' then 3
        when '[60,)' then 4
        else 99
    end
```

### v005

- Question: 钻石卡男客户、40岁以上、期末持有比亚迪A股市值超过1000元，算一下2026年一季度盈亏。
- Executable: Y
- Exact match: Y
- Standard rows: 1
- Agent rows: 1
- Standard columns: `['pty_id', 'byd_mkt_val', 'begin_total_asset', 'end_total_asset', 'asset_in', 'asset_out', 'q1_profit_loss']`
- Agent columns: `['pty_id', 'byd_mkt_val', 'begin_total_asset', 'end_total_asset', 'asset_in', 'asset_out', 'q1_profit_loss']`
- Error type: `ok`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
-- question: 钻石卡男性客户、年龄大于40岁、持有比亚迪市值超过1000元，计算2026年Q1盈亏。
with custinfo as (
    select pty_id
    from ads_cust_info_d
    where data_dt = '20260531'
      and cust_lvl_cd = '1000001'
      and gender_cd = '5000002'
      and cust_age > 40
),
byd_holders as (
    select
        hold.pty_id,
        sum(coalesce(hold.mkt_val, 0)) as byd_mkt_val
    from dwd_cust_hold_d hold
    inner join dim_product prdt
      on hold.prdt_id = prdt.prdt_id
    where hold.data_dt = '20260331'
      and prdt.prdt_name = '比亚迪'
      and prdt.prdt_type_name = 'A股'
      and exists (
          select 1 from custinfo c
          where c.pty_id = hold.pty_id
      )
    group by hold.pty_id
    having sum(coalesce(hold.mkt_val, 0)) > 1000
),
begin_asset as (
    select
        pty_id,
        coalesce(nm_tot_aset, 0) + coalesce(fc_pur_aset, 0) as begin_total_asset
    from dws_cust_aset_d
    where data_dt = '20260101'
),
end_asset as (
    select
        pty_id,
        coalesce(nm_tot_aset, 0) + coalesce(fc_pur_aset, 0) as end_total_asset
    from dws_cust_aset_d
    where data_dt = '20260331'
),
asset_flow as (
    select
        pty_id,
        sum(coalesce(cash_in, 0) + coalesce(tran_in, 0) + coalesce(assign_in, 0)) as asset_in,
        sum(coalesce(cash_out, 0) + coalesce(tran_out, 0) + coalesce(assign_out, 0)) as asset_out
    from dws_cust_fin_d
    where data_dt between '20260101' and '20260331'
    group by pty_id
)
select
    h.pty_id,
    h.byd_mkt_val,
    coalesce(b.begin_total_asset, 0) as begin_total_asset,
    coalesce(e.end_total_asset, 0) as end_total_asset,
    coalesce(f.asset_in, 0) as asset_in,
    coalesce(f.asset_out, 0) as asset_out,
    coalesce(e.end_total_asset, 0)
      - coalesce(b.begin_total_asset, 0)
      + coalesce(f.asset_out, 0)
      - coalesce(f.asset_in, 0) as q1_profit_loss
from byd_holders h
left join begin_asset b on h.pty_id = b.pty_id
left join end_asset e on h.pty_id = e.pty_id
left join asset_flow f on h.pty_id = f.pty_id
order by q1_profit_loss desc
```

### v006

- Question: 钻石卡男性客户、年龄大于40岁、持有比亚迪市值超过1000元，请计算2026年Q1盈亏。
- Executable: Y
- Exact match: Y
- Standard rows: 1
- Agent rows: 1
- Standard columns: `['pty_id', 'byd_mkt_val', 'begin_total_asset', 'end_total_asset', 'asset_in', 'asset_out', 'q1_profit_loss']`
- Agent columns: `['pty_id', 'byd_mkt_val', 'begin_total_asset', 'end_total_asset', 'asset_in', 'asset_out', 'q1_profit_loss']`
- Error type: `ok`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
-- question: 钻石卡男性客户、年龄大于40岁、持有比亚迪市值超过1000元，计算2026年Q1盈亏。
with custinfo as (
    select pty_id
    from ads_cust_info_d
    where data_dt = '20260531'
      and cust_lvl_cd = '1000001'
      and gender_cd = '5000002'
      and cust_age > 40
),
byd_holders as (
    select
        hold.pty_id,
        sum(coalesce(hold.mkt_val, 0)) as byd_mkt_val
    from dwd_cust_hold_d hold
    inner join dim_product prdt
      on hold.prdt_id = prdt.prdt_id
    where hold.data_dt = '20260331'
      and prdt.prdt_name = '比亚迪'
      and prdt.prdt_type_name = 'A股'
      and exists (
          select 1 from custinfo c
          where c.pty_id = hold.pty_id
      )
    group by hold.pty_id
    having sum(coalesce(hold.mkt_val, 0)) > 1000
),
begin_asset as (
    select
        pty_id,
        coalesce(nm_tot_aset, 0) + coalesce(fc_pur_aset, 0) as begin_total_asset
    from dws_cust_aset_d
    where data_dt = '20260101'
),
end_asset as (
    select
        pty_id,
        coalesce(nm_tot_aset, 0) + coalesce(fc_pur_aset, 0) as end_total_asset
    from dws_cust_aset_d
    where data_dt = '20260331'
),
asset_flow as (
    select
        pty_id,
        sum(coalesce(cash_in, 0) + coalesce(tran_in, 0) + coalesce(assign_in, 0)) as asset_in,
        sum(coalesce(cash_out, 0) + coalesce(tran_out, 0) + coalesce(assign_out, 0)) as asset_out
    from dws_cust_fin_d
    where data_dt between '20260101' and '20260331'
    group by pty_id
)
select
    h.pty_id,
    h.byd_mkt_val,
    coalesce(b.begin_total_asset, 0) as begin_total_asset,
    coalesce(e.end_total_asset, 0) as end_total_asset,
    coalesce(f.asset_in, 0) as asset_in,
    coalesce(f.asset_out, 0) as asset_out,
    coalesce(e.end_total_asset, 0)
      - coalesce(b.begin_total_asset, 0)
      + coalesce(f.asset_out, 0)
      - coalesce(f.asset_in, 0) as q1_profit_loss
from byd_holders h
left join begin_asset b on h.pty_id = b.pty_id
left join end_asset e on h.pty_id = e.pty_id
left join asset_flow f on h.pty_id = f.pty_id
order by q1_profit_loss desc
```

### v007

- Question: 请按分公司、营业部、省份和城市统计客户分布。
- Executable: Y
- Exact match: Y
- Standard rows: 15
- Agent rows: 15
- Standard columns: `['up_org_name', 'org_name', 'prov_name', 'city_name', 'customer_count']`
- Agent columns: `['up_org_name', 'org_name', 'prov_name', 'city_name', 'customer_count']`
- Error type: `ok`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
-- question: 分公司和营业部的客户省份分布统计。
select
    branch.up_org_name,
    branch.org_name,
    cust.prov_name,
    cust.city_name,
    count(*) as customer_count
from ads_cust_info_d cust
inner join dim_branch branch
  on cust.org_id = branch.org_id
where cust.data_dt = '20260531'
group by
    branch.up_org_name,
    branch.org_name,
    cust.prov_name,
    cust.city_name
order by customer_count desc, branch.up_org_name, branch.org_name
```

### v008

- Question: 各分公司和营业部客户都来自哪些省市？
- Executable: Y
- Exact match: Y
- Standard rows: 15
- Agent rows: 15
- Standard columns: `['up_org_name', 'org_name', 'prov_name', 'city_name', 'customer_count']`
- Agent columns: `['up_org_name', 'org_name', 'prov_name', 'city_name', 'customer_count']`
- Error type: `ok`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
-- question: 分公司和营业部的客户省份分布统计。
select
    branch.up_org_name,
    branch.org_name,
    cust.prov_name,
    cust.city_name,
    count(*) as customer_count
from ads_cust_info_d cust
inner join dim_branch branch
  on cust.org_id = branch.org_id
where cust.data_dt = '20260531'
group by
    branch.up_org_name,
    branch.org_name,
    cust.prov_name,
    cust.city_name
order by customer_count desc, branch.up_org_name, branch.org_name
```

### v009

- Question: 找出一季度买卖过招商银行A股，并且季末普通账户仍持有中国平安A股的客户。
- Executable: Y
- Exact match: Y
- Standard rows: 1
- Agent rows: 1
- Standard columns: `['pty_id', 'cmb_transaction_amount', 'pingan_market_value']`
- Agent columns: `['pty_id', 'cmb_transaction_amount', 'pingan_market_value']`
- Error type: `ok`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
-- question: 2026年Q1交易过招商银行A股，并且在Q1末普通账户持有中国平安A股的客户有哪些？
with cmb_traders as (
    select
        tran.pty_id,
        sum(coalesce(tran.buy_amt, 0) + coalesce(tran.sell_amt, 0)) as cmb_transaction_amount
    from dwd_cust_tran_d tran
    inner join dim_product prdt
      on tran.prdt_id = prdt.prdt_id
    where tran.data_dt between '20260101' and '20260331'
      and prdt.prdt_name = '招商银行'
      and prdt.prdt_type_name = 'A股'
    group by tran.pty_id
    having sum(coalesce(tran.buy_amt, 0) + coalesce(tran.sell_amt, 0)) > 0
),
pingan_holders as (
    select
        hold.pty_id,
        sum(coalesce(hold.mkt_val, 0)) as pingan_market_value
    from dwd_cust_hold_d hold
    inner join dim_product prdt
      on hold.prdt_id = prdt.prdt_id
    where hold.data_dt = '20260331'
      and hold.sys_source = 'nm'
      and prdt.prdt_name = '中国平安'
      and prdt.prdt_type_name = 'A股'
    group by hold.pty_id
    having sum(coalesce(hold.mkt_val, 0)) > 0
)
select
    trader.pty_id,
    trader.cmb_transaction_amount,
    holder.pingan_market_value
from cmb_traders trader
inner join pingan_holders holder
  on trader.pty_id = holder.pty_id
order by trader.cmb_transaction_amount desc
```

### v010

- Question: 2026年第一季度交易招商银行A股且Q1末普通账户持仓中国平安A股的客户有哪些？
- Executable: Y
- Exact match: Y
- Standard rows: 1
- Agent rows: 1
- Standard columns: `['pty_id', 'cmb_transaction_amount', 'pingan_market_value']`
- Agent columns: `['pty_id', 'cmb_transaction_amount', 'pingan_market_value']`
- Error type: `ok`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
-- question: 2026年Q1交易过招商银行A股，并且在Q1末普通账户持有中国平安A股的客户有哪些？
with cmb_traders as (
    select
        tran.pty_id,
        sum(coalesce(tran.buy_amt, 0) + coalesce(tran.sell_amt, 0)) as cmb_transaction_amount
    from dwd_cust_tran_d tran
    inner join dim_product prdt
      on tran.prdt_id = prdt.prdt_id
    where tran.data_dt between '20260101' and '20260331'
      and prdt.prdt_name = '招商银行'
      and prdt.prdt_type_name = 'A股'
    group by tran.pty_id
    having sum(coalesce(tran.buy_amt, 0) + coalesce(tran.sell_amt, 0)) > 0
),
pingan_holders as (
    select
        hold.pty_id,
        sum(coalesce(hold.mkt_val, 0)) as pingan_market_value
    from dwd_cust_hold_d hold
    inner join dim_product prdt
      on hold.prdt_id = prdt.prdt_id
    where hold.data_dt = '20260331'
      and hold.sys_source = 'nm'
      and prdt.prdt_name = '中国平安'
      and prdt.prdt_type_name = 'A股'
    group by hold.pty_id
    having sum(coalesce(hold.mkt_val, 0)) > 0
)
select
    trader.pty_id,
    trader.cmb_transaction_amount,
    holder.pingan_market_value
from cmb_traders trader
inner join pingan_holders holder
  on trader.pty_id = holder.pty_id
order by trader.cmb_transaction_amount desc
```

### v011

- Question: 一季度日均总资产超过30万、股票成交金额超过10万的客户，期末持仓产品类型分布如何？
- Executable: Y
- Exact match: Y
- Standard rows: 24
- Agent rows: 24
- Standard columns: `['up_prdt_type_name', 'prdt_type_name', 'customer_count', 'total_market_value']`
- Agent columns: `['up_prdt_type_name', 'prdt_type_name', 'customer_count', 'total_market_value']`
- Error type: `ok`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
-- question: 2026年Q1日均资产大于30万，且股票交易金额大于10万的客户，持有哪些产品类型？
with high_asset_customers as (
    select
        pty_id,
        sum(coalesce(nm_tot_aset, 0) + coalesce(fc_pur_aset, 0)) / 90.0 as avg_daily_asset
    from dws_cust_aset_d
    where data_dt between '20260101' and '20260331'
    group by pty_id
    having sum(coalesce(nm_tot_aset, 0) + coalesce(fc_pur_aset, 0)) / 90.0 > 300000
),
stock_active_customers as (
    select
        tran.pty_id,
        sum(coalesce(tran.buy_amt, 0) + coalesce(tran.sell_amt, 0)) as stock_transaction_amount
    from dwd_cust_tran_d tran
    inner join dim_product prdt
      on tran.prdt_id = prdt.prdt_id
    inner join high_asset_customers high_asset
      on tran.pty_id = high_asset.pty_id
    where tran.data_dt between '20260101' and '20260331'
      and prdt.up_prdt_type_name = '股票'
    group by tran.pty_id
    having sum(coalesce(tran.buy_amt, 0) + coalesce(tran.sell_amt, 0)) > 100000
)
select
    prdt.up_prdt_type_name,
    prdt.prdt_type_name,
    count(distinct active.pty_id) as customer_count,
    sum(coalesce(hold.mkt_val, 0)) as total_market_value
from stock_active_customers active
inner join dwd_cust_hold_d hold
  on active.pty_id = hold.pty_id
 and hold.data_dt = '20260331'
inner join dim_product prdt
  on hold.prdt_id = prdt.prdt_id
group by
    prdt.up_prdt_type_name,
    prdt.prdt_type_name
order by total_market_value desc
```

### v012

- Question: Q1平均资产大于300000且股票交易额大于100000的客户持有哪些产品类别？
- Executable: Y
- Exact match: Y
- Standard rows: 24
- Agent rows: 24
- Standard columns: `['up_prdt_type_name', 'prdt_type_name', 'customer_count', 'total_market_value']`
- Agent columns: `['up_prdt_type_name', 'prdt_type_name', 'customer_count', 'total_market_value']`
- Error type: `ok`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
-- question: 2026年Q1日均资产大于30万，且股票交易金额大于10万的客户，持有哪些产品类型？
with high_asset_customers as (
    select
        pty_id,
        sum(coalesce(nm_tot_aset, 0) + coalesce(fc_pur_aset, 0)) / 90.0 as avg_daily_asset
    from dws_cust_aset_d
    where data_dt between '20260101' and '20260331'
    group by pty_id
    having sum(coalesce(nm_tot_aset, 0) + coalesce(fc_pur_aset, 0)) / 90.0 > 300000
),
stock_active_customers as (
    select
        tran.pty_id,
        sum(coalesce(tran.buy_amt, 0) + coalesce(tran.sell_amt, 0)) as stock_transaction_amount
    from dwd_cust_tran_d tran
    inner join dim_product prdt
      on tran.prdt_id = prdt.prdt_id
    inner join high_asset_customers high_asset
      on tran.pty_id = high_asset.pty_id
    where tran.data_dt between '20260101' and '20260331'
      and prdt.up_prdt_type_name = '股票'
    group by tran.pty_id
    having sum(coalesce(tran.buy_amt, 0) + coalesce(tran.sell_amt, 0)) > 100000
)
select
    prdt.up_prdt_type_name,
    prdt.prdt_type_name,
    count(distinct active.pty_id) as customer_count,
    sum(coalesce(hold.mkt_val, 0)) as total_market_value
from stock_active_customers active
inner join dwd_cust_hold_d hold
  on active.pty_id = hold.pty_id
 and hold.data_dt = '20260331'
inner join dim_product prdt
  on hold.prdt_id = prdt.prdt_id
group by
    prdt.up_prdt_type_name,
    prdt.prdt_type_name
order by total_market_value desc
```

### v013

- Question: 2026年1月10日到2月15日，科创板成交金额超过25万的客户按营业部分布情况。
- Executable: Y
- Exact match: Y
- Standard rows: 3
- Agent rows: 3
- Standard columns: `['up_org_name', 'org_name', 'customer_count', 'total_transaction_amount']`
- Agent columns: `['up_org_name', 'org_name', 'customer_count', 'total_transaction_amount']`
- Error type: `ok`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
-- question: 查询2026年1月10日至2026年2月15日期间，科创板交易金额超过25万的客户营业部分布。
with star_market_active as (
    select
        tran.pty_id,
        sum(coalesce(tran.buy_amt, 0) + coalesce(tran.sell_amt, 0)) as star_market_transaction_amount
    from dwd_cust_tran_d tran
    inner join dim_product prdt
      on tran.prdt_id = prdt.prdt_id
    where tran.data_dt between '20260110' and '20260215'
      and prdt.prdt_type_name = '科创板'
    group by tran.pty_id
    having sum(coalesce(tran.buy_amt, 0) + coalesce(tran.sell_amt, 0)) > 250000
)
select
    branch.up_org_name,
    branch.org_name,
    count(distinct cust.pty_id) as customer_count,
    sum(active.star_market_transaction_amount) as total_transaction_amount
from star_market_active active
inner join ads_cust_info_d cust
  on active.pty_id = cust.pty_id
 and cust.data_dt = '20260531'
left join dim_branch branch
  on cust.org_id = branch.org_id
group by
    branch.up_org_name,
    branch.org_name
order by total_transaction_amount desc
```

### v014

- Question: 查询1月10日至2月15日期间科创板交易额大于25万客户所在分公司和营业部。
- Executable: Y
- Exact match: Y
- Standard rows: 3
- Agent rows: 3
- Standard columns: `['up_org_name', 'org_name', 'customer_count', 'total_transaction_amount']`
- Agent columns: `['up_org_name', 'org_name', 'customer_count', 'total_transaction_amount']`
- Error type: `ok`
- Trace: `init_run -> load_thread_context -> normalize_question -> detect_followup -> parse_intent -> retrieve_metadata -> fill_slots -> check_intent_slots -> resolve_product -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer -> persist_state`

Agent SQL:

```sql
-- question: 查询2026年1月10日至2026年2月15日期间，科创板交易金额超过25万的客户营业部分布。
with star_market_active as (
    select
        tran.pty_id,
        sum(coalesce(tran.buy_amt, 0) + coalesce(tran.sell_amt, 0)) as star_market_transaction_amount
    from dwd_cust_tran_d tran
    inner join dim_product prdt
      on tran.prdt_id = prdt.prdt_id
    where tran.data_dt between '20260110' and '20260215'
      and prdt.prdt_type_name = '科创板'
    group by tran.pty_id
    having sum(coalesce(tran.buy_amt, 0) + coalesce(tran.sell_amt, 0)) > 250000
)
select
    branch.up_org_name,
    branch.org_name,
    count(distinct cust.pty_id) as customer_count,
    sum(active.star_market_transaction_amount) as total_transaction_amount
from star_market_active active
inner join ads_cust_info_d cust
  on active.pty_id = cust.pty_id
 and cust.data_dt = '20260531'
left join dim_branch branch
  on cust.org_id = branch.org_id
group by
    branch.up_org_name,
    branch.org_name
order by total_transaction_amount desc
```
