from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from huatai_query_agent.evaluation.agent_evaluator import (
    AgentEvaluator,
    compare_query_results,
    write_csv_report,
    write_sql_generation_events,
)
from huatai_query_agent.executors.base import QueryResult


def result(columns, rows) -> QueryResult:
    return QueryResult(
        success=True,
        columns=list(columns),
        rows=list(rows),
        row_count=len(rows),
        preview_rows=list(rows),
        elapsed_ms=0.0,
    )


class EvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.demo_records, cls.demo_summary = AgentEvaluator().run(
            sql_mode="demo",
            case_set="official",
            query_ids=["q001", "q004"],
            repetitions=2,
        )

    def test_aliases_and_column_reordering_match_semantically(self) -> None:
        standard = result(
            ["pty_id", "begin_etf_value", "etf_buy_amount", "etf_sell_amount"],
            [("C1", Decimal("100"), Decimal("30"), Decimal("70"))],
        )
        candidate = result(
            ["pty_id", "etf_buy_amt", "etf_sell_amt", "init_etf_mktval"],
            [("C1", Decimal("30"), Decimal("70"), Decimal("100"))],
        )
        comparison = compare_query_results(
            standard,
            candidate,
            {"candidate_sql": "select 1"},
            output_contract={
                "columns": [
                    {"alias": "pty_id"},
                    {"alias": "begin_etf_value"},
                    {"alias": "etf_buy_amount"},
                    {"alias": "etf_sell_amount"},
                ],
                "order_sensitive": False,
            },
        )
        self.assertTrue(comparison.semantic_schema_match)
        self.assertTrue(comparison.semantic_result_match)
        self.assertFalse(comparison.exact_match)

    def test_float_tolerance_is_applied(self) -> None:
        comparison = compare_query_results(
            result(["active_rate"], [(0.9655172413793104,)]),
            result(["active_customer_rate"], [(0.9655172228813171,)]),
            {"candidate_sql": "select 1"},
            output_contract={
                "columns": [
                    {
                        "alias": "active_rate",
                        "numeric_tolerance": {"atol": 1e-7, "rtol": 1e-6},
                    }
                ],
                "order_sensitive": False,
            },
        )
        self.assertTrue(comparison.semantic_result_match)

    def test_order_sensitivity_is_case_specific(self) -> None:
        standard = result(["value"], [(1,), (2,)])
        candidate = result(["value"], [(2,), (1,)])
        insensitive = compare_query_results(
            standard,
            candidate,
            {"candidate_sql": "select 1"},
            output_contract={"columns": [{"alias": "value"}], "order_sensitive": False},
        )
        sensitive = compare_query_results(
            standard,
            candidate,
            {"candidate_sql": "select 1"},
            output_contract={"columns": [{"alias": "value"}], "order_sensitive": True},
        )
        self.assertTrue(insensitive.semantic_result_match)
        self.assertFalse(sensitive.semantic_result_match)
        self.assertIn("order_sensitive_mismatch", sensitive.error_tags)

    def test_demo_repetitions_use_unique_threads(self) -> None:
        self.assertEqual(4, self.demo_summary.total_cases)
        self.assertEqual(4, self.demo_summary.agent_completed_cases)
        self.assertEqual(4, len({record.thread_id for record in self.demo_records}))

    def test_csv_contains_sql_and_layered_metrics(self) -> None:
        records = [self.demo_records[0]]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.csv"
            write_csv_report(records, path)
            content = path.read_text(encoding="utf-8-sig")
        self.assertIn("candidate_sql", content)
        self.assertIn("standard_sql", content)
        self.assertIn("semantic_result_match", content)
        self.assertIn("thread_id", content)
        self.assertIn("sql_generation_elapsed_ms", content)

    def test_sql_generation_events_preserve_every_attempt_timing(self) -> None:
        records = [self.demo_records[0]]
        attempts = [
            {
                "attempt": 1,
                "attempt_type": "initial",
                "status": "ok",
                "started_at": "2026-07-31T01:00:00+00:00",
                "completed_at": "2026-07-31T01:00:02+00:00",
                "elapsed_ms": 2000.0,
                "model": "test-model",
                "usage": {"total_tokens": 10},
                "sql": "select 1",
                "error": "",
            },
            {
                "attempt": 2,
                "attempt_type": "repair",
                "status": "ok",
                "started_at": "2026-07-31T01:00:03+00:00",
                "completed_at": "2026-07-31T01:00:04+00:00",
                "elapsed_ms": 1000.0,
                "model": "test-model",
                "usage": {"total_tokens": 5},
                "sql": "select 2",
                "error": "",
            },
        ]
        record = replace(
            records[0],
            sql_generation_attempt_count=2,
            sql_generation_elapsed_ms=3000.0,
            sql_generation_attempts=attempts,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sql-events.jsonl"
            write_sql_generation_events([record], path)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(2, len(lines))
        self.assertIn('"attempt_type": "initial"', lines[0])
        self.assertIn('"elapsed_ms": 1000.0', lines[1])


if __name__ == "__main__":
    unittest.main()
