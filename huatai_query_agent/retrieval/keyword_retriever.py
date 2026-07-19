from __future__ import annotations

import math

from huatai_query_agent.retrieval.embedding import tokenize_text
from huatai_query_agent.retrieval.types import MetadataChunk, RetrievalResult


class KeywordRetriever:
    def __init__(self, chunks: list[MetadataChunk]) -> None:
        self.chunks = chunks
        self._chunk_tokens = [set(tokenize_text(chunk.text + " " + " ".join(map(str, chunk.metadata.values())))) for chunk in chunks]

    def search(
        self,
        query: str,
        *,
        top_k: int = 12,
        chunk_types: set[str] | None = None,
    ) -> list[RetrievalResult]:
        query_tokens = set(tokenize_text(query))
        if not query_tokens:
            return []

        results: list[RetrievalResult] = []
        normalized_query = query.lower()
        for chunk, chunk_tokens in zip(self.chunks, self._chunk_tokens):
            if chunk_types and chunk.chunk_type not in chunk_types:
                continue

            overlap = query_tokens & chunk_tokens
            if not overlap and normalized_query not in chunk.text.lower():
                continue

            score = len(overlap) / math.sqrt(max(len(query_tokens), 1) * max(len(chunk_tokens), 1))
            if normalized_query and normalized_query in chunk.text.lower():
                score += 0.5
            for value in chunk.metadata.values():
                if isinstance(value, str) and value and value.lower() in normalized_query:
                    score += 0.2
                elif isinstance(value, list):
                    score += sum(0.1 for item in value if str(item).lower() in normalized_query)

            if score > 0:
                results.append(RetrievalResult(chunk=chunk, score=score, source="keyword"))

        results.sort(key=lambda item: item.score, reverse=True)
        return results[:top_k]

