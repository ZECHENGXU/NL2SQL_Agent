from __future__ import annotations

from collections import OrderedDict

from huatai_query_agent.retrieval.chunk_builder import build_metadata_chunks
from huatai_query_agent.retrieval.keyword_retriever import KeywordRetriever
from huatai_query_agent.retrieval.qdrant_retriever import QdrantMetadataStore
from huatai_query_agent.retrieval.types import MetadataChunk, RetrievalResult


class HybridMetadataRetriever:
    def __init__(
        self,
        *,
        chunks: list[MetadataChunk] | None = None,
        qdrant_store: QdrantMetadataStore | None = None,
    ) -> None:
        self.chunks = chunks or build_metadata_chunks()
        self.chunks_by_id = {chunk.id: chunk for chunk in self.chunks}
        self.keyword = KeywordRetriever(self.chunks)
        self.qdrant = qdrant_store or QdrantMetadataStore()

    def search(self, query: str, *, top_k: int = 12) -> list[RetrievalResult]:
        exact_results = self._exact_search(query)
        keyword_results = self.keyword.search(query, top_k=top_k)
        qdrant_results = self.qdrant.search(query, top_k=top_k)
        merged = self._merge_results(exact_results + keyword_results + qdrant_results)
        expanded = self._expand_from_examples(merged)
        return self._merge_results(merged + expanded)[:top_k]

    def build_context(self, query: str, *, top_k: int = 16) -> dict[str, object]:
        results = self.search(query, top_k=top_k)
        context_ids = [result.chunk.id for result in results]
        chunks = [result.to_dict() for result in results]
        tables = []
        metrics = []
        terms = []
        examples = []
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
            elif chunk.chunk_type == "example_sql":
                examples.append(metadata.get("question_id"))
                for table in metadata.get("required_tables", []):
                    if table not in tables:
                        tables.append(table)
                for metric in metadata.get("expected_metrics", []):
                    if metric not in metrics:
                        metrics.append(metric)
            elif chunk.chunk_type == "relationship":
                relationships.append(metadata.get("relationship_name"))

        return {
            "query": query,
            "retrieval_mode": "yaml_keyword_qdrant_hybrid",
            "context_ids": context_ids,
            "chunks": chunks,
            "tables": _dedupe(tables),
            "metrics": _dedupe(metrics),
            "terms": _dedupe(terms),
            "examples": _dedupe(examples),
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
                if isinstance(value, str) and value and value.lower() in normalized_query:
                    score += 0.8
                elif isinstance(value, list):
                    score += sum(0.5 for item in value if str(item).lower() in normalized_query)
            if score:
                results.append(RetrievalResult(chunk=chunk, score=score, source="exact"))
        results.sort(key=lambda item: item.score, reverse=True)
        return results

    def _expand_from_examples(self, results: list[RetrievalResult]) -> list[RetrievalResult]:
        expanded: list[RetrievalResult] = []
        for result in results:
            if result.chunk.chunk_type != "example_sql":
                continue
            metadata = result.chunk.metadata
            for table in metadata.get("required_tables", []):
                chunk = self.chunks_by_id.get(f"table.{table}")
                if chunk:
                    expanded.append(RetrievalResult(chunk=chunk, score=result.score * 0.85, source="example_expand"))
            for metric in metadata.get("expected_metrics", []):
                chunk = self.chunks_by_id.get(f"metric.{metric}")
                if chunk:
                    expanded.append(RetrievalResult(chunk=chunk, score=result.score * 0.85, source="example_expand"))
        return expanded

    @staticmethod
    def _merge_results(results: list[RetrievalResult]) -> list[RetrievalResult]:
        merged: OrderedDict[str, RetrievalResult] = OrderedDict()
        for result in sorted(results, key=lambda item: item.score, reverse=True):
            existing = merged.get(result.chunk.id)
            if existing is None or result.score > existing.score:
                merged[result.chunk.id] = result
        return list(merged.values())

    def close(self) -> None:
        self.qdrant.close()


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
