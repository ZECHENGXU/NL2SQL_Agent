from __future__ import annotations

import time
import unittest

from huatai_query_agent.agent.demo_cases import DemoCaseRepository
from huatai_query_agent.agent.graph import QueryAgent
from huatai_query_agent.agent.nodes.m1_nodes import generate_sql
from huatai_query_agent.evaluation.agent_evaluator import AgentEvaluator
from huatai_query_agent.llm.client import (
    CaseDeadlineExceeded,
    case_deadline,
    remaining_case_seconds,
)


class _TimeoutGenerator:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def parse_intent(self, **kwargs):
        self.calls.append("parse_intent")
        raise CaseDeadlineExceeded("case budget exhausted")

    def generate_sql(self, **kwargs):
        self.calls.append("generate_sql")
        raise CaseDeadlineExceeded("case budget exhausted during SQL generation")


class _Retriever:
    def build_context(self, query: str, *, top_k: int = 16):
        return {
            "query": query,
            "context_ids": [],
            "tables": [],
            "metrics": [],
        }


class _TimedOutAgent:
    def run(self, **kwargs):
        return {
            "candidate_sql": "",
            "confidence": 0.0,
            "case_timed_out": True,
            "validation_report": {"errors": ["case budget exhausted"]},
            "execution_result": {"success": False, "error": "", "elapsed_ms": 0.0},
            "trace": [{"node": "human_review_or_explain", "status": "timeout"}],
            "final_answer": "case_timeout",
        }


class CaseTimeoutTests(unittest.TestCase):
    def test_case_deadline_counts_down_to_zero(self) -> None:
        with case_deadline(0.01):
            self.assertGreater(remaining_case_seconds() or 0.0, 0.0)
            time.sleep(0.02)
            self.assertEqual(0.0, remaining_case_seconds())
        self.assertIsNone(remaining_case_seconds())

    def test_timeout_stops_before_second_llm_stage(self) -> None:
        generator = _TimeoutGenerator()
        agent = QueryAgent(
            repo=DemoCaseRepository(),
            retriever=_Retriever(),
            llm_generator=generator,
            sql_mode="llm",
            use_langgraph=False,
        )
        try:
            state = agent.run(
                question="统计客户数量",
                continue_with_assumptions=True,
                case_timeout_seconds=0.1,
            )
        finally:
            agent.close()
        self.assertTrue(state["case_timed_out"])
        self.assertEqual(["parse_intent"], generator.calls)
        self.assertIn("case_timeout", state["final_answer"])

    def test_sql_timeout_attempt_keeps_timing_fields(self) -> None:
        generator = _TimeoutGenerator()
        update = generate_sql(
            DemoCaseRepository(),
            generator=generator,
            sql_mode="llm",
        )(
            {
                "question": "统计客户数量",
                "metadata_context": {},
                "intent": {},
                "sql_plan": {},
                "sql_generation_attempts": [],
                "trace": [],
            }
        )
        attempt = update["sql_generation_attempts"][0]
        self.assertTrue(update["case_timed_out"])
        self.assertEqual("initial", attempt["attempt_type"])
        self.assertEqual("failed", attempt["status"])
        self.assertTrue(attempt["started_at"])
        self.assertTrue(attempt["completed_at"])
        self.assertGreaterEqual(attempt["elapsed_ms"], 0.0)

    def test_evaluator_labels_case_timeout(self) -> None:
        evaluator = AgentEvaluator()
        case = evaluator.repo.list_cases()[0]
        record = evaluator._run_case(
            case,
            agent=_TimedOutAgent(),
            sql_mode="llm",
            compare_limit=100,
            repetition=1,
            run_id="timeout-test",
            use_case_hints=False,
            case_timeout_seconds=50.0,
        )
        self.assertTrue(record.case_timed_out)
        self.assertFalse(record.agent_completed)
        self.assertEqual("case_timeout", record.error_type)
        self.assertIn("case_timeout", record.error_tags)


if __name__ == "__main__":
    unittest.main()
