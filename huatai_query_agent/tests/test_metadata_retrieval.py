from __future__ import annotations

import unittest
import warnings

from huatai_query_agent.retrieval.chunk_builder import build_metadata_chunks
from huatai_query_agent.retrieval.hybrid_retriever import HybridMetadataRetriever
from huatai_query_agent.retrieval.reranker import (
    CrossEncoderMetadataReranker,
    RerankerSettings,
)
from huatai_query_agent.retrieval.types import MetadataChunk, RetrievalResult


class _EmptyQdrantStore:
    def __init__(self, results: list[RetrievalResult] | None = None) -> None:
        self.results = results or []
        self.chunk_types: set[str] | None = None
        self.top_k: int | None = None

    def search(self, query: str, *, top_k: int = 12, chunk_types=None):
        self.chunk_types = chunk_types
        self.top_k = top_k
        return self.results[:top_k]

    def close(self) -> None:
        pass


class _StaticKeywordRetriever:
    def __init__(self, results: list[RetrievalResult]) -> None:
        self.results = results
        self.top_k: int | None = None

    def search(self, query: str, *, top_k: int = 12, chunk_types=None):
        self.top_k = top_k
        return self.results[:top_k]


class _StaticCrossEncoderModel:
    def __init__(self, scores: list[float]) -> None:
        self.scores = scores
        self.inputs = []
        self.batch_size: int | None = None

    def predict(self, inputs, *, batch_size, **kwargs):
        self.inputs = inputs
        self.batch_size = batch_size
        return self.scores[: len(inputs)]


class _FailingCrossEncoderModel:
    def predict(self, inputs, **kwargs):
        raise RuntimeError("inference failed")


class ExactMetadataSearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.retriever = HybridMetadataRetriever(
            chunks=[
                MetadataChunk(
                    id="term.currency.0",
                    chunk_type="term",
                    text="币种人民币，编码0。",
                    metadata={
                        "term_category": "currency",
                        "field_name": "dwd_cust_hold_d.ccy",
                        "code_value": "0",
                        "aliases": ["人民币", "CNY"],
                    },
                ),
                MetadataChunk(
                    id="term.currency.1",
                    chunk_type="term",
                    text="币种美元，编码1。",
                    metadata={
                        "term_category": "currency",
                        "field_name": "dwd_cust_hold_d.ccy",
                        "code_value": "1",
                        "aliases": ["美元", "USD"],
                    },
                ),
                MetadataChunk(
                    id="term.currency.2",
                    chunk_type="term",
                    text="币种港币，编码2。",
                    metadata={
                        "term_category": "currency",
                        "field_name": "dwd_cust_hold_d.ccy",
                        "code_value": "2",
                        "aliases": ["港币", "HKD"],
                    },
                ),
                MetadataChunk(
                    id="term.gender.5000002",
                    chunk_type="term",
                    text="男性，编码5000002。",
                    metadata={
                        "term_category": "gender",
                        "field_name": "ads_cust_info_d.gender_cd",
                        "code_value": "5000002",
                        "aliases": ["男", "男性"],
                    },
                ),
            ],
            qdrant_store=_EmptyQdrantStore(),
            enable_reranker=False,
        )

    def tearDown(self) -> None:
        self.retriever.close()

    def test_dates_amounts_and_quarter_do_not_match_numeric_codes(self) -> None:
        results = self.retriever._exact_search(
            "查询2026年1月资产大于100万的客户，计算Q1表现"
        )

        self.assertEqual([], [result.chunk.id for result in results])

    def test_distant_field_name_does_not_turn_month_into_code(self) -> None:
        results = self.retriever._exact_search(
            "查询dwd_cust_hold_d表2026年1月的持仓"
        )

        self.assertEqual([], [result.chunk.id for result in results])

    def test_explicit_code_label_matches_numeric_code(self) -> None:
        results = self.retriever._exact_search("查询编码为5000002的客户")

        self.assertEqual(["term.gender.5000002"], [result.chunk.id for result in results])

    def test_field_assignment_matches_numeric_code(self) -> None:
        results = self.retriever._exact_search("筛选ccy=0的持仓")

        self.assertEqual(["term.currency.0"], [result.chunk.id for result in results])

    def test_text_alias_matching_is_unchanged(self) -> None:
        results = self.retriever._exact_search("查询人民币持仓")

        self.assertEqual(["term.currency.0"], [result.chunk.id for result in results])


class MetadataExampleExclusionTests(unittest.TestCase):
    def test_chunk_builder_does_not_create_example_chunks(self) -> None:
        chunks = build_metadata_chunks()

        self.assertNotIn("example_sql", {chunk.chunk_type for chunk in chunks})

    def test_local_and_legacy_qdrant_examples_are_both_excluded(self) -> None:
        example = MetadataChunk(
            id="example_sql.q001",
            chunk_type="example_sql",
            text="样例问题",
            metadata={"question_id": "q001"},
        )
        qdrant = _EmptyQdrantStore(
            [RetrievalResult(chunk=example, score=1.0, source="qdrant")]
        )
        retriever = HybridMetadataRetriever(
            chunks=[example],
            qdrant_store=qdrant,
            enable_reranker=False,
        )
        try:
            results = retriever.search("样例问题")
        finally:
            retriever.close()

        self.assertEqual([], results)
        self.assertNotIn("example_sql", qdrant.chunk_types or set())


class RrfFusionTests(unittest.TestCase):
    @staticmethod
    def _chunk(chunk_id: str) -> MetadataChunk:
        return MetadataChunk(
            id=chunk_id,
            chunk_type="table",
            text=chunk_id,
            metadata={"table_name": chunk_id.removeprefix("table.")},
        )

    @staticmethod
    def _result(chunk: MetadataChunk, score: float, source: str) -> RetrievalResult:
        return RetrievalResult(chunk=chunk, score=score, source=source)

    def test_rrf_is_independent_of_raw_score_scale(self) -> None:
        first = self._chunk("table.first")
        second = self._chunk("table.second")
        original = HybridMetadataRetriever._rrf_fuse(
            {
                "keyword": [
                    self._result(first, 0.01, "keyword"),
                    self._result(second, 0.001, "keyword"),
                ],
                "qdrant": [
                    self._result(second, 0.9, "qdrant"),
                    self._result(first, 0.8, "qdrant"),
                ],
            },
            rrf_k=60,
        )
        rescaled = HybridMetadataRetriever._rrf_fuse(
            {
                "keyword": [
                    self._result(first, 10_000.0, "keyword"),
                    self._result(second, -5_000.0, "keyword"),
                ],
                "qdrant": [
                    self._result(second, 0.00009, "qdrant"),
                    self._result(first, 0.00008, "qdrant"),
                ],
            },
            rrf_k=60,
        )

        self.assertEqual(
            [result.chunk.id for result in original],
            [result.chunk.id for result in rescaled],
        )
        self.assertEqual(
            [result.score for result in original],
            [result.score for result in rescaled],
        )

    def test_result_present_in_both_rankings_is_boosted(self) -> None:
        keyword_first = self._chunk("table.keyword_first")
        shared = self._chunk("table.shared")
        keyword_third = self._chunk("table.keyword_third")
        qdrant_first = self._chunk("table.qdrant_first")
        qdrant_third = self._chunk("table.qdrant_third")

        fused = HybridMetadataRetriever._rrf_fuse(
            {
                "keyword": [
                    self._result(keyword_first, 0.9, "keyword"),
                    self._result(shared, 0.8, "keyword"),
                    self._result(keyword_third, 0.7, "keyword"),
                ],
                "qdrant": [
                    self._result(qdrant_first, 0.6, "qdrant"),
                    self._result(shared, 0.5, "qdrant"),
                    self._result(qdrant_third, 0.4, "qdrant"),
                ],
            },
            rrf_k=60,
        )

        self.assertEqual("table.shared", fused[0].chunk.id)
        self.assertEqual(
            {"keyword": 2, "qdrant": 2},
            fused[0].details["ranks"],
        )

    def test_exact_results_are_pinned_before_rrf_results(self) -> None:
        exact = self._chunk("table.exact_table")
        shared = self._chunk("table.shared")
        keyword = _StaticKeywordRetriever(
            [self._result(shared, 10_000.0, "keyword")]
        )
        qdrant = _EmptyQdrantStore(
            [self._result(shared, 0.99, "qdrant")]
        )
        retriever = HybridMetadataRetriever(
            chunks=[exact, shared],
            qdrant_store=qdrant,
            enable_reranker=False,
            candidate_multiplier=3,
        )
        retriever.keyword = keyword
        try:
            results = retriever.search("使用table.exact_table查询", top_k=2)
        finally:
            retriever.close()

        self.assertEqual(
            ["table.exact_table", "table.shared"],
            [result.chunk.id for result in results],
        )
        self.assertEqual("exact", results[0].source)
        self.assertEqual("rrf", results[1].source)
        self.assertEqual(6, keyword.top_k)
        self.assertEqual(6, qdrant.top_k)
        self.assertEqual(
            {"keyword": 1, "qdrant": 1},
            results[1].to_dict()["details"]["ranks"],
        )


class CrossEncoderRerankerTests(unittest.TestCase):
    @staticmethod
    def _result(chunk_id: str, score: float) -> RetrievalResult:
        chunk = MetadataChunk(
            id=chunk_id,
            chunk_type="table",
            text=f"metadata for {chunk_id}",
            metadata={"table_name": chunk_id.removeprefix("table.")},
        )
        return RetrievalResult(
            chunk=chunk,
            score=score,
            source="rrf",
            details={"fusion": "rrf", "ranks": {"keyword": 1}},
        )

    def test_cross_encoder_reorders_rrf_candidates_and_keeps_diagnostics(self) -> None:
        model = _StaticCrossEncoderModel([0.1, 0.9])
        reranker = CrossEncoderMetadataReranker(
            RerankerSettings(model="test-reranker", batch_size=4),
            model=model,
        )
        first = self._result("table.first", 0.03)
        second = self._result("table.second", 0.02)

        results = reranker.rerank("find second", [first, second])

        self.assertEqual(
            ["table.second", "table.first"],
            [result.chunk.id for result in results],
        )
        self.assertEqual(["reranker", "reranker"], [result.source for result in results])
        self.assertEqual(4, model.batch_size)
        self.assertEqual("find second", model.inputs[0][0])
        self.assertEqual(0.02, results[0].details["rrf_score"])
        self.assertEqual(2, results[0].details["reranker"]["input_rank"])
        self.assertEqual(0.9, results[0].details["reranker"]["score"])
        self.assertEqual("rrf", results[0].details["fusion"])

    def test_exact_result_stays_pinned_before_cross_encoder_results(self) -> None:
        exact = self._result("table.exact_table", 0.03).chunk
        first = self._result("table.first", 0.03)
        second = self._result("table.second", 0.02)
        keyword = _StaticKeywordRetriever([first, second])
        qdrant = _EmptyQdrantStore([first, second])
        reranker = CrossEncoderMetadataReranker(
            RerankerSettings(model="test-reranker"),
            model=_StaticCrossEncoderModel([0.1, 0.9]),
        )
        retriever = HybridMetadataRetriever(
            chunks=[exact, first.chunk, second.chunk],
            qdrant_store=qdrant,
            reranker=reranker,
        )
        retriever.keyword = keyword
        try:
            results = retriever.search("use table.exact_table", top_k=3)
        finally:
            retriever.close()

        self.assertEqual(
            ["table.exact_table", "table.second", "table.first"],
            [result.chunk.id for result in results],
        )
        self.assertEqual(["exact", "reranker", "reranker"], [r.source for r in results])

    def test_fail_open_retains_rrf_order_and_marks_fallback(self) -> None:
        reranker = CrossEncoderMetadataReranker(
            RerankerSettings(model="test-reranker", fail_open=True),
            model=_FailingCrossEncoderModel(),
        )
        candidates = [
            self._result("table.first", 0.03),
            self._result("table.second", 0.02),
        ]

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            results = reranker.rerank("query", candidates)

        self.assertTrue(
            any("retaining RRF order" in str(item.message) for item in caught)
        )
        self.assertEqual(
            ["table.first", "table.second"],
            [result.chunk.id for result in results],
        )
        self.assertEqual(["rrf", "rrf"], [result.source for result in results])
        self.assertEqual("fallback", results[0].details["reranker"]["status"])
        self.assertEqual("RuntimeError", results[0].details["reranker"]["error_type"])


if __name__ == "__main__":
    unittest.main()
