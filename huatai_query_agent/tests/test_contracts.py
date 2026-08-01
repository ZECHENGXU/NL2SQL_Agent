from __future__ import annotations

import unittest

import sqlglot

from huatai_query_agent.agent.contracts import (
    derive_window_contract,
    derive_join_contract,
    normalize_output_columns,
    projection_names,
    validate_fact_preaggregation,
    validate_snapshot_dates,
)
from huatai_query_agent.agent.nodes.m1_nodes import (
    _enrich_sql_plan,
    check_intent_slots,
    plan_sql,
    validate_result,
    validate_sql,
)
from huatai_query_agent.evaluation.agent_evaluator import AgentEvaluator
from huatai_query_agent.llm.client import LlmClientError


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.evaluator = AgentEvaluator()
        cls.cases = cls.evaluator._select_cases(
            case_set="all",
            query_ids=None,
            max_cases=None,
        )

    def test_all_81_cases_have_materialized_output_contracts(self) -> None:
        self.assertEqual(81, len(self.cases))
        for case in self.cases:
            aliases = [
                item.get("alias")
                for item in case.output_contract.get("columns", [])
            ]
            self.assertTrue(aliases, case.query_id)
            self.assertNotIn("*", aliases, case.query_id)
            self.assertIn("order_sensitive", case.output_contract)

    def test_reference_projection_contract_matches_duckdb(self) -> None:
        for case in self.cases:
            result = self.evaluator.executor.execute(case.sql, preview_limit=1)
            self.assertTrue(result.success, f"{case.query_id}: {result.error}")
            aliases = [
                item.get("alias")
                for item in case.output_contract.get("columns", [])
            ]
            self.assertEqual(aliases, result.columns, case.query_id)

    def test_cte_projection_is_validated_in_scope(self) -> None:
        sql = """
        with holding as (
            select prdt_id, count(distinct pty_id) as holder_count
            from dwd_cust_hold_d
            where data_dt = '20260331'
            group by prdt_id
        )
        select h.prdt_id, h.holder_count
        from holding h
        """
        update = validate_sql(
            {
                "candidate_sql": sql,
                "question": "按产品统计持仓客户数",
                "sql_plan": {
                    "output_columns": ["prdt_id", "holder_count"],
                },
            }
        )
        self.assertTrue(update["validation_report"]["passed"])
        self.assertEqual([], update["validation_report"]["errors"])

    def test_wrong_static_snapshot_is_rejected(self) -> None:
        sql = """
        select pty_id
        from ads_cust_info_d
        where data_dt = '20260331'
        """
        update = validate_sql(
            {
                "candidate_sql": sql,
                "question": "查询客户",
                "sql_plan": {"output_columns": ["pty_id"]},
            }
        )
        report = update["validation_report"]
        self.assertFalse(report["passed"])
        self.assertEqual("failed", report["checks"]["snapshot_policy"])

    def test_fact_date_range_can_cover_available_range(self) -> None:
        expression = sqlglot.parse_one(
            """
            select pty_id
            from dwd_cust_tran_d
            where data_dt between '20260101' and '20260331'
            """,
            read="duckdb",
        )
        self.assertEqual([], validate_snapshot_dates(expression))

    def test_projection_contract_detects_missing_column(self) -> None:
        update = validate_sql(
            {
                "candidate_sql": "select pty_id from ads_cust_info_d",
                "question": "输出客户和姓名",
                "sql_plan": {"output_columns": ["pty_id", "name"]},
            }
        )
        report = update["validation_report"]
        self.assertFalse(report["passed"])
        self.assertIn("name", report["projection"]["missing"])

    def test_batch_mode_converts_low_risk_missing_slots_to_assumptions(self) -> None:
        state = {
            "question": "按分公司统计2026年一季度客户数和交易额，按交易额降序。",
            "intent": {
                "target": "分公司经营统计",
                "dimensions": ["分公司"],
                "metrics": ["客户数", "交易额"],
            },
            "missing_slots": ["未明确币种，是否只看人民币"],
            "continue_with_assumptions": True,
            "trace": [],
        }
        update = check_intent_slots(state)
        self.assertEqual([], update["blocking_missing_slots"])
        self.assertTrue(update["non_blocking_uncertainties"])
        self.assertTrue(update["assumptions"])

    def test_projection_names_expand_select_star_from_cte(self) -> None:
        case = next(case for case in self.cases if case.query_id == "a004")
        self.assertEqual(
            [item["alias"] for item in case.output_contract["columns"]],
            projection_names(case.sql),
        )

    def test_output_contract_deduplicates_aliases_after_intent_merge(self) -> None:
        columns = normalize_output_columns(
            [
                {"alias": "pty_id", "semantic_type": "customer_id"},
                {"name": "pty_id", "alias": "pty_id"},
                "name",
            ]
        )
        self.assertEqual(["pty_id", "name"], [item["alias"] for item in columns])
        self.assertEqual([1, 2], [item["position"] for item in columns])

    def test_advanced_window_contract_is_materialized_from_reference(self) -> None:
        case = next(case for case in self.cases if case.query_id == "a004")
        windows = derive_window_contract(case.sql)
        self.assertEqual("dense_rank", windows[0]["function"])
        self.assertEqual(["up_org_name"], windows[0]["partition_by"])
        self.assertEqual("total_asset", windows[0]["order_by"][0]["expression"])
        self.assertEqual("desc", windows[0]["order_by"][0]["direction"])

    def test_net_inflow_requires_all_six_flow_fields(self) -> None:
        update = validate_sql(
            {
                "candidate_sql": """
                    select sum(coalesce(cash_in, 0)) - sum(coalesce(cash_out, 0)) as net_inflow
                    from dws_cust_fin_d
                    where data_dt between '20260101' and '20260331'
                """,
                "question": "统计资金净流入",
                "sql_plan": {
                    "output_columns": ["net_inflow"],
                    "metrics": ["net_inflow"],
                },
            }
        )
        report = update["validation_report"]
        self.assertFalse(report["passed"])
        self.assertEqual("failed", report["checks"]["metric_rules"])

    def test_plan_failure_uses_request_contract_fallback(self) -> None:
        class FailingPlanner:
            def plan_sql(self, **kwargs):
                raise LlmClientError("invalid JSON")

        update = plan_sql(generator=FailingPlanner(), sql_mode="llm")(
            {
                "question": "每个营业部取前三名",
                "intent": {"target": "营业部排名"},
                "metadata_context": {
                    "request_context": {
                        "required_tables": ["ads_cust_info_d"],
                        "expected_metrics": ["customer_count"],
                        "output_contract": {
                            "columns": ["org_name", "customer_count", "branch_rank"]
                        },
                        "window": [{
                            "function": "dense_rank",
                            "partition_by": ["up_org_name"],
                            "order_by": [{"expression": "customer_count", "direction": "desc"}],
                        }],
                        "top_n": 3,
                    }
                },
                "request_context": {
                    "required_tables": ["ads_cust_info_d"],
                    "expected_metrics": ["customer_count"],
                },
                "trace": [],
            }
        )
        self.assertEqual("batch_contract_fallback", update["sql_plan"]["strategy"])
        self.assertEqual(3, update["sql_plan"]["top_n"])
        self.assertEqual(3, len(update["sql_plan"]["output_columns"]))

    def test_population_join_contract_rejects_optional_branch_mapping(self) -> None:
        update = validate_sql(
            {
                "candidate_sql": """
                    select branch.org_name, count(*) as customer_count
                    from ads_cust_info_d cust
                    left join dim_branch branch
                      on cust.org_id = branch.org_id
                     and branch.data_dt = '20260531'
                    where cust.data_dt = '20260531'
                    group by branch.org_name
                """,
                "question": "以有营业部归属的客户为母集统计营业部客户数",
                "sql_plan": {
                    "output_columns": ["org_name", "customer_count"],
                    "join_contract": [{"table": "dim_branch", "join_type": "inner"}],
                },
            }
        )
        report = update["validation_report"]
        self.assertFalse(report["passed"])
        self.assertEqual("failed", report["checks"]["join_contract"])

    def test_a004_reference_join_contract_requires_branch_inner_join(self) -> None:
        case = next(case for case in self.cases if case.query_id == "a004")
        branch_contracts = [
            item for item in derive_join_contract(case.sql) if item["table"] == "dim_branch"
        ]
        self.assertIn({"table": "dim_branch", "join_type": "inner"}, branch_contracts)

    def test_join_contract_ignores_cte_names_that_resemble_fact_domains(self) -> None:
        sql = """
            with asset as (
                select pty_id, max(nm_tot_aset) as total_asset
                from dws_cust_aset_d
                where data_dt = '20260331'
                group by pty_id
            ), trade as (
                select pty_id, sum(buy_amt + sell_amt) as turnover
                from dwd_cust_tran_d
                where data_dt between '20260101' and '20260331'
                group by pty_id
            )
            select asset.pty_id, asset.total_asset, trade.turnover
            from asset
            inner join trade on asset.pty_id = trade.pty_id
        """
        self.assertEqual([], derive_join_contract(sql))

    def test_join_contract_accepts_inner_join_through_single_table_cte(self) -> None:
        update = validate_sql(
            {
                "candidate_sql": """
                    with branch as (
                        select org_id, org_name
                        from dim_branch
                        where data_dt = '20260531'
                    )
                    select cust.pty_id, branch.org_name
                    from ads_cust_info_d cust
                    inner join branch on cust.org_id = branch.org_id
                    where cust.data_dt = '20260531'
                """,
                "question": "只保留有营业部归属的客户",
                "sql_plan": {
                    "output_columns": ["pty_id", "org_name"],
                    "join_contract": [{"table": "dim_branch", "join_type": "inner"}],
                },
            }
        )
        self.assertTrue(update["validation_report"]["passed"])

    def test_direct_join_between_multirow_fact_tables_is_rejected(self) -> None:
        expression = sqlglot.parse_one(
            """
            select tran.pty_id
            from dwd_cust_tran_d tran
            inner join dws_cust_fin_d flow on tran.pty_id = flow.pty_id
            """,
            read="duckdb",
        )
        failures = validate_fact_preaggregation(expression)
        self.assertEqual(1, len(failures))
        self.assertIn("customer-level pre-aggregation", failures[0])

    def test_preaggregated_fact_ctes_can_be_joined(self) -> None:
        expression = sqlglot.parse_one(
            """
            with trade as (
                select pty_id, sum(buy_amt + sell_amt) as turnover
                from dwd_cust_tran_d
                group by pty_id
            ), flow as (
                select pty_id, sum(cash_in + tran_in + assign_in) as inflow
                from dws_cust_fin_d
                group by pty_id
            )
            select trade.pty_id, trade.turnover, flow.inflow
            from trade
            inner join flow on trade.pty_id = flow.pty_id
            """,
            read="duckdb",
        )
        self.assertEqual([], validate_fact_preaggregation(expression))

    def test_single_calendar_date_does_not_create_missing_period_contract(self) -> None:
        plan = _enrich_sql_plan(
            {
                "question": "统计截至2026年3月31日的客户资产",
                "intent": {},
                "metadata_context": {},
            },
            {
                "output_columns": ["pty_id", "total_asset"],
                "missing_period_policy": "zero_fill",
            },
        )
        self.assertNotIn("missing_period_policy", plan)

    def test_partitioned_top_n_result_is_not_treated_as_global_limit(self) -> None:
        update = validate_result(
            {
                "execution_result": {
                    "success": True,
                    "row_count": 14,
                    "columns": ["up_org_name", "asset_rank_in_company"],
                },
                "sql_plan": {
                    "output_columns": ["up_org_name", "asset_rank_in_company"],
                    "top_n": 3,
                    "window": [{
                        "function": "dense_rank",
                        "partition_by": ["up_org_name"],
                    }],
                },
            }
        )
        self.assertTrue(update["result_check"]["passed"])

    def test_global_top_n_result_still_enforces_row_limit(self) -> None:
        update = validate_result(
            {
                "execution_result": {
                    "success": True,
                    "row_count": 4,
                    "columns": ["pty_id"],
                },
                "sql_plan": {
                    "output_columns": ["pty_id"],
                    "top_n": 3,
                },
            }
        )
        self.assertFalse(update["result_check"]["passed"])

    def test_window_contract_rejects_wrong_partition_and_order(self) -> None:
        update = validate_sql(
            {
                "candidate_sql": """
                    select
                        pty_id,
                        row_number() over (partition by org_id order by mkt_val asc) as product_rank
                    from dwd_cust_hold_d
                    where data_dt = '20260331'
                """,
                "question": "每个营业部按市值降序排名，并列按产品编号打散",
                "sql_plan": {
                    "output_columns": ["pty_id", "product_rank"],
                    "window": [{
                        "function": "row_number",
                        "partition_by": ["up_org_name", "org_name"],
                        "order_by": [{"expression": "mkt_val", "direction": "desc"}],
                        "tie_breaker": ["prdt_id"],
                    }],
                },
            }
        )
        report = update["validation_report"]
        self.assertFalse(report["passed"])
        self.assertEqual("failed", report["checks"]["window_contract"])

    def test_window_contract_accepts_partition_order_and_tie_breaker(self) -> None:
        update = validate_sql(
            {
                "candidate_sql": """
                    select
                        pty_id,
                        row_number() over (
                            partition by sys_source
                            order by mkt_val desc, prdt_id asc
                        ) as product_rank
                    from dwd_cust_hold_d
                    where data_dt = '20260331'
                """,
                "question": "每个营业部按市值降序排名，并列按产品编号打散",
                "sql_plan": {
                    "output_columns": ["pty_id", "product_rank"],
                    "window": [{
                        "function": "row_number",
                        "partition_by": ["sys_source"],
                        "order_by": [{"expression": "mkt_val", "direction": "desc"}],
                        "tie_breaker": ["prdt_id"],
                    }],
                },
            }
        )
        self.assertTrue(update["validation_report"]["passed"])

    def test_require_record_rejects_outer_join_zero_fill(self) -> None:
        update = validate_sql(
            {
                "candidate_sql": """
                    with begin_asset as (
                        select pty_id, nm_tot_aset as begin_asset
                        from dws_cust_aset_d
                        where data_dt = '20260101'
                    )
                    select c.pty_id, coalesce(b.begin_asset, 0) as begin_asset
                    from ads_cust_info_d c
                    left join begin_asset b on c.pty_id = b.pty_id
                    where c.data_dt = '20260531'
                """,
                "question": "仅保留期初有资产记录的客户",
                "sql_plan": {
                    "output_columns": ["pty_id", "begin_asset"],
                    "missing_fact_policy": {"begin_asset": "require_record"},
                },
            }
        )
        report = update["validation_report"]
        self.assertFalse(report["passed"])
        self.assertEqual("failed", report["checks"]["missing_fact_policy"])

    def test_require_record_accepts_inner_join(self) -> None:
        update = validate_sql(
            {
                "candidate_sql": """
                    with begin_asset as (
                        select pty_id, nm_tot_aset as begin_asset
                        from dws_cust_aset_d
                        where data_dt = '20260101'
                    )
                    select c.pty_id, b.begin_asset
                    from ads_cust_info_d c
                    inner join begin_asset b on c.pty_id = b.pty_id
                    where c.data_dt = '20260531'
                """,
                "question": "仅保留期初有资产记录的客户",
                "sql_plan": {
                    "output_columns": ["pty_id", "begin_asset"],
                    "missing_fact_policy": {"begin_asset": "require_record"},
                },
            }
        )
        self.assertTrue(update["validation_report"]["passed"])

    def test_exclude_missing_period_rejects_period_scaffold(self) -> None:
        update = validate_sql(
            {
                "candidate_sql": """
                    select trade_month
                    from (values ('202602'), ('202603')) as months(trade_month)
                """,
                "question": "未出现的月份不补零",
                "sql_plan": {
                    "output_columns": ["trade_month"],
                    "missing_period_policy": "exclude",
                },
            }
        )
        report = update["validation_report"]
        self.assertFalse(report["passed"])
        self.assertEqual("failed", report["checks"]["missing_period_policy"])

    def test_eligibility_filter_is_required(self) -> None:
        update = validate_sql(
            {
                "candidate_sql": """
                    select pty_id, sum(buy_rake) as total_fee
                    from dwd_cust_tran_d
                    where data_dt between '20260101' and '20260331'
                    group by pty_id
                """,
                "question": "只对费用大于0的客户排名",
                "sql_plan": {
                    "output_columns": ["pty_id", "total_fee"],
                    "eligibility_filters": ["total_fee > 0"],
                },
            }
        )
        report = update["validation_report"]
        self.assertFalse(report["passed"])
        self.assertEqual("failed", report["checks"]["eligibility_filters"])

    def test_partition_top_n_rejects_global_limit(self) -> None:
        update = validate_sql(
            {
                "candidate_sql": """
                    select
                        pty_id,
                        row_number() over (partition by org_id order by mkt_val desc) as product_rank
                    from dwd_cust_hold_d
                    where data_dt = '20260331'
                    limit 3
                """,
                "question": "每个营业部前三名",
                "sql_plan": {
                    "output_columns": ["pty_id", "product_rank"],
                    "top_n": 3,
                    "window": [{
                        "function": "row_number",
                        "partition_by": ["org_id"],
                        "order_by": [{"expression": "mkt_val", "direction": "desc"}],
                    }],
                },
            }
        )
        report = update["validation_report"]
        self.assertFalse(report["passed"])
        self.assertEqual("failed", report["checks"]["top_n_contract"])

    def test_snapshot_policy_requires_static_table_predicate(self) -> None:
        update = validate_sql(
            {
                "candidate_sql": "select pty_id from ads_cust_info_d",
                "question": "查询客户",
                "sql_plan": {
                    "output_columns": ["pty_id"],
                    "snapshot_policy": {"ads_cust_info_d": "20260531"},
                },
            }
        )
        report = update["validation_report"]
        self.assertFalse(report["passed"])
        self.assertEqual("failed", report["checks"]["snapshot_policy"])


if __name__ == "__main__":
    unittest.main()
