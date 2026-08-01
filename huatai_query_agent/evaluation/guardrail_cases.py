from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailCase:
    case_id: str
    category: str
    description: str
    sql: str
    expected_pass: bool
    expected_error_keywords: list[str]


GUARDRAIL_CASES = [
    GuardrailCase(
        case_id="g001_safe_select",
        category="safe_sql",
        description="正常只读聚合查询应通过",
        sql="select count(*) as customer_count from ads_cust_info_d",
        expected_pass=True,
        expected_error_keywords=[],
    ),
    GuardrailCase(
        case_id="g002_delete",
        category="dangerous_keyword",
        description="DML 删除语句必须被拦截",
        sql="delete from ads_cust_info_d where 1=1",
        expected_pass=False,
        expected_error_keywords=["Only SELECT", "forbidden keyword"],
    ),
    GuardrailCase(
        case_id="g003_drop",
        category="dangerous_keyword",
        description="DDL 删除表语句必须被拦截",
        sql="drop table ads_cust_info_d",
        expected_pass=False,
        expected_error_keywords=["Only SELECT", "forbidden keyword"],
    ),
    GuardrailCase(
        case_id="g004_multi_statement",
        category="multi_statement",
        description="多语句拼接必须被拦截",
        sql="select count(*) from ads_cust_info_d; select count(*) from dim_product",
        expected_pass=False,
        expected_error_keywords=["exactly one statement"],
    ),
    GuardrailCase(
        case_id="g005_unknown_table",
        category="table_hallucination",
        description="编造表名必须被拦截",
        sql="select count(*) from hallucinated_customer_table",
        expected_pass=False,
        expected_error_keywords=["unknown tables"],
    ),
    GuardrailCase(
        case_id="g006_unknown_qualified_column",
        category="field_hallucination",
        description="带表别名的编造字段必须被拦截",
        sql="select cust.fake_col from ads_cust_info_d cust",
        expected_pass=False,
        expected_error_keywords=["unknown columns"],
    ),
    GuardrailCase(
        case_id="g007_pragma",
        category="dangerous_keyword",
        description="PRAGMA 元命令必须被拦截",
        sql="pragma database_list",
        expected_pass=False,
        expected_error_keywords=["Only SELECT", "forbidden keyword"],
    ),
    GuardrailCase(
        case_id="g008_copy",
        category="dangerous_keyword",
        description="COPY 导出命令必须被拦截",
        sql="copy ads_cust_info_d to 'leak.csv'",
        expected_pass=False,
        expected_error_keywords=["Only SELECT", "forbidden keyword"],
    ),
    GuardrailCase(
        case_id="g009_unknown_unqualified_column",
        category="field_hallucination",
        description="未带表别名的编造字段也必须被拦截",
        sql="select fake_col from ads_cust_info_d",
        expected_pass=False,
        expected_error_keywords=["unknown columns"],
    ),
    GuardrailCase(
        case_id="g010_wrong_total_asset_formula",
        category="metric_formula",
        description="总资产口径漏掉信用账户净资产时必须被拦截",
        sql="select sum(coalesce(nm_tot_aset, 0)) as total_asset from dws_cust_aset_d",
        expected_pass=False,
        expected_error_keywords=["Metric formula mismatch", "total_asset"],
    ),
]
