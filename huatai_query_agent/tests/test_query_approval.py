from __future__ import annotations

import unittest

from huatai_query_agent.agent.demo_cases import DemoCaseRepository
from huatai_query_agent.agent.graph import QueryAgent
from huatai_query_agent.executors.duckdb_executor import DuckDBExecutor
from huatai_query_agent.llm.client import LlmClientError


class _Retriever:
    def build_context(self, query: str, *, top_k: int = 16):
        return {
            "query": query,
            "context_ids": [],
            "tables": [],
            "metrics": [],
        }


class _CountingExecutor:
    def __init__(self) -> None:
        self.delegate = DuckDBExecutor()
        self.calls = 0

    def execute(self, sql: str, *, preview_limit: int = 20):
        self.calls += 1
        return self.delegate.execute(sql, preview_limit=preview_limit)


class _FailingGenerator:
    def __init__(self) -> None:
        self.generate_calls = 0
        self.repair_calls = 0

    def parse_intent(self, **kwargs):
        raise LlmClientError("Connection error.")

    def fill_slots(self, **kwargs):
        raise LlmClientError("Connection error.")

    def plan_sql(self, **kwargs):
        raise LlmClientError("Connection error.")

    def generate_sql(self, **kwargs):
        self.generate_calls += 1
        raise LlmClientError("Connection error.")

    def repair_sql(self, **kwargs):
        self.repair_calls += 1
        raise LlmClientError("Connection error.")


class QueryApprovalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = QueryAgent(
            repo=DemoCaseRepository(),
            retriever=_Retriever(),
            sql_mode="demo",
            use_langgraph=False,
        )
        self.executor = _CountingExecutor()
        self.agent.executor = self.executor

    def tearDown(self) -> None:
        self.agent.close()

    def test_prepare_waits_for_approval_before_execution(self) -> None:
        prepared = self.agent.prepare(query_id="q001", thread_id="approval-test")

        self.assertEqual(0, self.executor.calls)
        self.assertEqual("execute_sql", prepared["next_action"])
        self.assertTrue(prepared["validation_report"]["passed"])
        self.assertTrue(prepared["candidate_sql"])
        self.assertFalse(prepared.get("execution_result"))

        result = self.agent.execute_prepared(prepared)

        self.assertEqual(1, self.executor.calls)
        self.assertEqual("completed", result["next_action"])
        self.assertTrue(result["execution_result"]["success"])

    def test_execute_revalidates_the_approved_sql(self) -> None:
        prepared = self.agent.prepare(query_id="q001", thread_id="approval-test")
        prepared["candidate_sql"] = "delete from ads_cust_info_d"

        result = self.agent.execute_prepared(prepared)

        self.assertEqual(0, self.executor.calls)
        self.assertEqual("regenerate_sql", result["next_action"])
        self.assertFalse(result["validation_report"]["passed"])

    def test_llm_connection_failure_stops_before_empty_sql_repair(self) -> None:
        generator = _FailingGenerator()
        agent = QueryAgent(
            repo=DemoCaseRepository(),
            retriever=_Retriever(),
            llm_generator=generator,
            sql_mode="llm",
            use_langgraph=False,
        )
        try:
            result = agent.prepare(
                query_id="q001",
                thread_id="llm-failure-test",
            )
        finally:
            agent.close()

        self.assertEqual(1, generator.generate_calls)
        self.assertEqual(0, generator.repair_calls)
        self.assertNotIn("validation_report", result)
        self.assertIn("Connection error", result["final_answer"])


if __name__ == "__main__":
    unittest.main()
