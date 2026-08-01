from __future__ import annotations

import re

from huatai_query_agent.retrieval.chunk_builder import build_metadata_chunks
from huatai_query_agent.retrieval.keyword_retriever import KeywordRetriever
from huatai_query_agent.retrieval.qdrant_retriever import QdrantMetadataStore
from huatai_query_agent.retrieval.reranker import MetadataReranker, build_reranker_from_env
from huatai_query_agent.retrieval.types import MetadataChunk, RetrievalResult


RETRIEVABLE_CHUNK_TYPES = frozenset(
    {"table", "field", "term", "metric", "time_period", "relationship"}
)
DEFAULT_RRF_K = 60
DEFAULT_CANDIDATE_MULTIPLIER = 3
DEFAULT_RERANK_CANDIDATE_MULTIPLIER = 1


class HybridMetadataRetriever:
    def __init__(
        self,
        *,
        chunks: list[MetadataChunk] | None = None,
        qdrant_store: QdrantMetadataStore | None = None,
        reranker: MetadataReranker | None = None,
        enable_reranker: bool = True,
        rrf_k: int = DEFAULT_RRF_K,
        candidate_multiplier: int = DEFAULT_CANDIDATE_MULTIPLIER,
        rerank_candidate_multiplier: int = DEFAULT_RERANK_CANDIDATE_MULTIPLIER,
    ) -> None:
        if rrf_k <= 0:
            raise ValueError("rrf_k must be greater than zero.")
        if candidate_multiplier < 1:
            raise ValueError("candidate_multiplier must be at least one.")
        if rerank_candidate_multiplier < 1:
            raise ValueError("rerank_candidate_multiplier must be at least one.")
        source_chunks = chunks if chunks is not None else build_metadata_chunks()
        self.chunks = [
            chunk
            for chunk in source_chunks
            if chunk.chunk_type in RETRIEVABLE_CHUNK_TYPES
        ]
        self.keyword = KeywordRetriever(self.chunks)
        self.qdrant = qdrant_store or QdrantMetadataStore()
        self.reranker = reranker or (build_reranker_from_env() if enable_reranker else None)
        self.rrf_k = rrf_k
        self.candidate_multiplier = candidate_multiplier
        self.rerank_candidate_multiplier = rerank_candidate_multiplier

    def search(self, query: str, *, top_k: int = 12) -> list[RetrievalResult]:
        if top_k <= 0:
            return []
        candidate_k = top_k * self.candidate_multiplier
        exact_results = self._exact_search(query)
        keyword_results = self.keyword.search(query, top_k=candidate_k)
        qdrant_results = [
            result
            for result in self.qdrant.search(
                query,
                top_k=candidate_k,
                chunk_types=set(RETRIEVABLE_CHUNK_TYPES),
            )
            if result.chunk.chunk_type in RETRIEVABLE_CHUNK_TYPES
        ]
        fused_results = self._rrf_fuse(
            {"keyword": keyword_results, "qdrant": qdrant_results},
            rrf_k=self.rrf_k,
        )
        pinned_exact_results = exact_results[:top_k]
        exact_ids = {result.chunk.id for result in pinned_exact_results}
        fused_candidates = [
            result for result in fused_results if result.chunk.id not in exact_ids
        ][:candidate_k]
        if self.reranker is not None:
            non_exact_slots = top_k - len(pinned_exact_results)
            rerank_k = non_exact_slots * self.rerank_candidate_multiplier
            rerank_candidates = fused_candidates[:rerank_k]
            rerank_candidates = self.reranker.rerank(query, rerank_candidates)
        else:
            rerank_candidates = fused_candidates
        return _dedupe_results(pinned_exact_results + rerank_candidates)[:top_k]

    def build_context(self, query: str, *, top_k: int = 16) -> dict[str, object]:
        results = self.search(query, top_k=top_k)
        context_ids = [result.chunk.id for result in results]
        chunks = [result.to_dict() for result in results]
        tables = []
        metrics = []
        terms = []
        relationships = []

        for result in results:
            chunk = result.chunk
            metadata = chunk.metadata
            if chunk.chunk_type == "table":
                tables.append(metadata.get("table_name"))
            elif chunk.chunk_type == "metric":
                metrics.append(metadata.get("metric_name"))
            elif chunk.chunk_type == "term":
                terms.append(metadata.get("term_name") or metadata.get("code_value"))
            elif chunk.chunk_type == "relationship":
                relationships.append(metadata.get("relationship_name"))

        return {
            "query": query,
            "retrieval_mode": (
                "yaml_exact_keyword_qdrant_rrf_cross_encoder_hybrid"
                if self.reranker is not None
                else "yaml_exact_keyword_qdrant_rrf_hybrid"
            ),
            "context_ids": context_ids,
            "chunks": chunks,
            "tables": _dedupe(tables),
            "metrics": _dedupe(metrics),
            "terms": _dedupe(terms),
            "relationships": _dedupe(relationships),
        }

    def _exact_search(self, query: str) -> list[RetrievalResult]:
        results: list[RetrievalResult] = []
        normalized_query = query.lower()
        for chunk in self.chunks:
            score = 0.0
            metadata = chunk.metadata
            if chunk.id.lower() in normalized_query:
                score += 1.0
            for value in metadata.values():
                if isinstance(value, str) and _is_exact_metadata_match(value, normalized_query, metadata):
                    score += 0.8
                elif isinstance(value, list):
                    score += sum(
                        0.5
                        for item in value
                        if _is_exact_metadata_match(str(item), normalized_query, metadata)
                    )
            if score:
                results.append(RetrievalResult(chunk=chunk, score=score, source="exact"))
        results.sort(key=lambda item: item.score, reverse=True)
        return results

    @staticmethod
    def _rrf_fuse(
        rankings: dict[str, list[RetrievalResult]],
        *,
        rrf_k: int,
    ) -> list[RetrievalResult]:
        chunks_by_id: dict[str, MetadataChunk] = {}
        scores_by_id: dict[str, float] = {}
        ranks_by_id: dict[str, dict[str, int]] = {}
        raw_scores_by_id: dict[str, dict[str, float]] = {}
        for source, results in rankings.items():
            for rank, result in enumerate(results, start=1):
                chunk_id = result.chunk.id
                chunks_by_id.setdefault(chunk_id, result.chunk)
                scores_by_id[chunk_id] = scores_by_id.get(chunk_id, 0.0) + (
                    1.0 / (rrf_k + rank)
                )
                ranks_by_id.setdefault(chunk_id, {})[source] = rank
                raw_scores_by_id.setdefault(chunk_id, {})[source] = result.score

        ordered_ids = sorted(
            chunks_by_id,
            key=lambda chunk_id: (
                -scores_by_id[chunk_id],
                min(ranks_by_id[chunk_id].values()),
                chunk_id,
            ),
        )

        output: list[RetrievalResult] = []
        for chunk_id in ordered_ids:
            output.append(
                RetrievalResult(
                    chunk=chunks_by_id[chunk_id],
                    score=scores_by_id[chunk_id],
                    source="rrf",
                    details={
                        "fusion": "rrf",
                        "rrf_k": rrf_k,
                        "ranks": ranks_by_id[chunk_id],
                        "raw_scores": raw_scores_by_id[chunk_id],
                    },
                )
            )
        return output

    def close(self) -> None:
        self.qdrant.close()


def _is_exact_metadata_match(
    value: str,
    normalized_query: str,
    metadata: dict[str, object],
) -> bool:
    candidate = value.strip().lower()
    if not candidate:
        return False
    if not candidate.isdecimal():
        return candidate in normalized_query
    return _is_explicit_numeric_code(candidate, normalized_query, metadata)


def _is_explicit_numeric_code(
    candidate: str,
    normalized_query: str,
    metadata: dict[str, object],
) -> bool:
    number_pattern = rf"(?<![a-z0-9_]){re.escape(candidate)}(?![a-z0-9_])"
    number_match = re.search(number_pattern, normalized_query)
    if number_match is None:
        return False

    code_label_pattern = (
        r"(?:\u7f16\u7801|\u4ee3\u7801|code(?:_value)?)"
        r"\s*(?:\u4e3a|=|:|\uff1a)?\s*$"
    )
    if re.search(code_label_pattern, normalized_query[: number_match.start()]):
        return True

    identifier_values = (
        metadata.get("field_name"),
        metadata.get("term_category"),
    )
    identifiers = {
        identifier
        for value in identifier_values
        if value
        for identifier in re.findall(r"[a-z_][a-z0-9_]*", str(value).lower())
    }
    for identifier in identifiers:
        assignment_pattern = (
            rf"(?<![a-z0-9_]){re.escape(identifier)}(?![a-z0-9_])"
            rf"\s*(?:=|:|\uff1a|\u4e3a|\u662f)\s*['\"]?{re.escape(candidate)}"
            r"(?![a-z0-9_])"
        )
        if re.search(assignment_pattern, normalized_query):
            return True
    return False


def _dedupe(values: list[object]) -> list[object]:
    seen = set()
    output = []
    for value in values:
        if value is None:
            continue
        key = str(value)
        if key not in seen:
            seen.add(key)
            output.append(value)
    return output


def _dedupe_results(results: list[RetrievalResult]) -> list[RetrievalResult]:
    seen: set[str] = set()
    output: list[RetrievalResult] = []
    for result in results:
        if result.chunk.id in seen:
            continue
        seen.add(result.chunk.id)
        output.append(result)
    return output
