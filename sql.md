CREATE TABLE dim_product (
    prdt_id character varying(12) ,
    prdt_name character varying(100) ,
    sor_prdt_id character varying(12) ,
    market_id character varying(50) ,
    prdt_type_id character varying(12) ,
    prdt_type_name character varying(40) ,
    up_prdt_type_id character varying(12) ,
    up_prdt_type_name character varying(40) 
)
 ;
COMMENT ON TABLE dim_product IS '产品属性维表';
COMMENT ON COLUMN dim_product.prdt_id IS '产品ID';
COMMENT ON COLUMN dim_product.prdt_name IS '产品名称';
COMMENT ON COLUMN dim_product.sor_prdt_id IS '产品代码';
COMMENT ON COLUMN dim_product.prdt_type_id IS '产品二级分类ID';
COMMENT ON COLUMN dim_product.prdt_type_name IS '产品二级分类名称';
COMMENT ON COLUMN dim_product.up_prdt_type_id IS '产品一级分类ID';
COMMENT ON COLUMN dim_product.up_prdt_type_name IS '产品一级分类名称';

CREATE TABLE ads_cust_info_d (
    data_dt character varying(8) ,
    pty_id character varying(32) ,
    sor_pty_id character varying(32) ,
    cust_lvl_cd character varying(12) ,
    cust_status character varying(12) ,
    cust_type character varying(1) ,
    prov_name character varying(50) ,
    city_name character varying(50) ,
    birth_dt character varying(8) ,
    cust_age numeric(20,0) ,
    name character varying(40) ,
    gender_cd character varying(12) ,
    edu_cd character varying(32) ,
    prof_cd character varying(100),
    org_id  character varying(100)
) ;
COMMENT ON TABLE ads_cust_info_d IS '客户信息表';
COMMENT ON COLUMN ads_cust_info_d.data_dt IS '日期';
COMMENT ON COLUMN ads_cust_info_d.pty_id IS '客户号';
COMMENT ON COLUMN ads_cust_info_d.sor_pty_id IS '经纪客户号';
COMMENT ON COLUMN ads_cust_info_d.cust_lvl_cd IS '客户等级';
COMMENT ON COLUMN ads_cust_info_d.cust_status IS '账户状态';
COMMENT ON COLUMN ads_cust_info_d.cust_type IS '客户类型';
COMMENT ON COLUMN ads_cust_info_d.prov_name IS '省份';
COMMENT ON COLUMN ads_cust_info_d.city_name IS '城市';
COMMENT ON COLUMN ads_cust_info_d.birth_dt IS '出生日期';
COMMENT ON COLUMN ads_cust_info_d.cust_age IS '年龄';
COMMENT ON COLUMN ads_cust_info_d.name IS '姓名';
COMMENT ON COLUMN ads_cust_info_d.gender_cd IS '性别代码';
COMMENT ON COLUMN ads_cust_info_d.edu_cd IS '学历代码';
COMMENT ON COLUMN ads_cust_info_d.prof_cd IS '职业类型编码';
COMMENT ON COLUMN ads_cust_info_d.org_id IS '所属营业部ID';

CREATE TABLE dws_cust_fin_d (
    data_dt character varying(8) NOT NULL ,
    pty_id character varying(32) NOT NULL ,
    sys_source  character varying(20) NOT NULL ,
    cash_in numeric(20,4) ,
    cash_out numeric(20,4) ,
    tran_in numeric(20,4) ,
    tran_out numeric(20,4) ,
    assign_in numeric(20,4) ,
    assign_out numeric(20,4) 
);
COMMENT ON TABLE dws_cust_fin_d IS '客户资金流动日事实';
COMMENT ON COLUMN dws_cust_fin_d.data_dt IS '日期';
COMMENT ON COLUMN dws_cust_fin_d.pty_id IS '客户号';
COMMENT ON COLUMN dws_cust_fin_d.sys_source IS '系统来源：普通(nm)、信用(fc)';
COMMENT ON COLUMN dws_cust_fin_d.cash_in IS '现金转入';
COMMENT ON COLUMN dws_cust_fin_d.cash_out IS '现金转出';
COMMENT ON COLUMN dws_cust_fin_d.tran_in IS '证券转入、托管转入、转托转入';
COMMENT ON COLUMN dws_cust_fin_d.tran_out IS '证券转出、托管转出、转托转出';
COMMENT ON COLUMN dws_cust_fin_d.assign_in IS '指定转入';
COMMENT ON COLUMN dws_cust_fin_d.assign_out IS '撤指定转出';

CREATE TABLE dwd_cust_hold_d (
    data_dt character varying(8) NOT NULL ,
    pty_id character varying(32) NOT NULL ,
    prdt_id character varying(12) NOT NULL ,
    sys_source character varying(20) NOT NULL ,
    ccy character varying(12) NOT NULL ,
    hold_cnt numeric(20,4),
    mkt_val numeric(20,4)
);
COMMENT ON TABLE dwd_cust_hold_d IS '客户持有产品日事实';
COMMENT ON COLUMN dwd_cust_hold_d.data_dt IS '日期';
COMMENT ON COLUMN dwd_cust_hold_d.pty_id IS '客户号';
COMMENT ON COLUMN dwd_cust_hold_d.prdt_id IS '产品ID';
COMMENT ON COLUMN dwd_cust_hold_d.sys_source IS '系统来源：普通(nm)、信用(fc)';
COMMENT ON COLUMN dwd_cust_hold_d.ccy IS '币种,0 人民币；1 美元；2 港币';
COMMENT ON COLUMN dwd_cust_hold_d.hold_cnt IS '持有份额';
COMMENT ON COLUMN dwd_cust_hold_d.mkt_val IS '持有市值';

CREATE TABLE dwd_cust_tran_d (
    data_dt character varying(8) NOT NULL ,
    pty_id character varying(32) NOT NULL ,
    prdt_id character varying(12) NOT NULL ,
    sys_source character varying(20) NOT NULL ,
    ccy character varying(12) NOT NULL ,
    buy_cnt integer ,
    buy_mnt numeric(20,4) ,
    buy_rake numeric(20,4) ,
    buy_amt numeric(20,4) ,
    buy_fare numeric(20,4) ,
    sell_cnt integer ,
    sell_mnt numeric(20,4) ,
    sell_rake numeric(20,4) ,
    sell_amt numeric(20,4) ,
    sell_fare numeric(20,4) 
);
COMMENT ON TABLE dwd_cust_tran_d IS '客户交易类买卖日事实';
COMMENT ON COLUMN dwd_cust_tran_d.data_dt IS '日期';
COMMENT ON COLUMN dwd_cust_tran_d.pty_id IS '客户号';
COMMENT ON COLUMN dwd_cust_tran_d.prdt_id IS '产品ID';
COMMENT ON COLUMN dwd_cust_tran_d.sys_source IS '系统来源：普通(nm)、信用(fc)';
COMMENT ON COLUMN dwd_cust_tran_d.ccy IS '币种,0 人民币；1 美元；2 港币';
COMMENT ON COLUMN dwd_cust_tran_d.buy_cnt IS '买入次数';
COMMENT ON COLUMN dwd_cust_tran_d.buy_mnt IS '买入数量';
COMMENT ON COLUMN dwd_cust_tran_d.buy_rake IS '买入佣金';
COMMENT ON COLUMN dwd_cust_tran_d.buy_amt IS '买入金额';
COMMENT ON COLUMN dwd_cust_tran_d.buy_fare IS '买入费用';
COMMENT ON COLUMN dwd_cust_tran_d.sell_cnt IS '卖出次数';
COMMENT ON COLUMN dwd_cust_tran_d.sell_mnt IS '卖出数量';
COMMENT ON COLUMN dwd_cust_tran_d.sell_rake IS '卖出佣金';
COMMENT ON COLUMN dwd_cust_tran_d.sell_amt IS '卖出金额';
COMMENT ON COLUMN dwd_cust_tran_d.sell_fare IS '卖出费用';

CREATE TABLE dws_cust_aset_d (
    data_dt character varying(8) NOT NULL ,
    pty_id character varying(32) NOT NULL ,
    nm_tot_aset numeric(20,4) ,
    nm_bal numeric(20,4) ,
    fc_pur_aset numeric(20,4) ,
    fc_bal numeric(20,4)
);
COMMENT ON TABLE dws_cust_aset_d IS '客户资产日汇总';
COMMENT ON COLUMN dws_cust_aset_d.data_dt IS '日期';
COMMENT ON COLUMN dws_cust_aset_d.pty_id IS '客户号';
COMMENT ON COLUMN dws_cust_aset_d.nm_tot_aset IS '普通账户总资产';
COMMENT ON COLUMN dws_cust_aset_d.nm_bal IS '普通账户现金资产';
COMMENT ON COLUMN dws_cust_aset_d.fc_pur_aset IS '信用账户净资产';
COMMENT ON COLUMN dws_cust_aset_d.fc_bal IS '信用账户现金资产';

CREATE TABLE dim_public (
    code character varying(12) NOT NULL,
    code_type_id character varying(6) NOT NULL,
    describe character varying(50) NOT NULL
);
COMMENT ON TABLE dim_public IS '标准化编码字典表';
COMMENT ON COLUMN dim_public.code IS '标准字典码';
COMMENT ON COLUMN dim_public.code_type_id IS '标准字典码类型';
COMMENT ON COLUMN dim_public.describe IS '标准字典描述';

create table dim_branch(
    data_dt character varying(8) NOT NULL,
    org_id character varying(50) NOT NULL,
    org_name character varying(100) NOT NULL,
    up_org_id character varying(50) NOT NULL,
    up_org_name character varying(100) NOT NULL
);
COMMENT ON TABLE dim_branch IS '营业部表';
COMMENT ON column dim_branch.org_id IS '营业部ID';
COMMENT ON column dim_branch.org_name IS '营业部名称';
COMMENT ON column dim_branch.org_id IS '上级营业部/分公司ID';
COMMENT ON column dim_branch.org_name IS '上级营业部/分公司名称';
