-- DuckDB-compatible demo queries for the Huatai Agentic intelligent query prototype.
-- Each query is marked by `-- query_id: qXXX` for automated parsing.

-- query_id: q001
-- question: 学历本科以上的男性客户，年龄超过50岁的有多少个？
select
    count(*) as customer_count
from ads_cust_info_d
where data_dt = '20260531'
  and edu_cd in ('6000002', '6000003', '6000004')
  and gender_cd = '5000002'
  and cust_age > 50;

-- query_id: q002
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
    end;

-- query_id: q003
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
order by q1_profit_loss desc;

-- query_id: q004
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
order by customer_count desc, branch.up_org_name, branch.org_name;

-- query_id: q005
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
order by trader.cmb_transaction_amount desc;

-- query_id: q006
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
order by total_market_value desc;

-- query_id: q007
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
order by total_transaction_amount desc;
