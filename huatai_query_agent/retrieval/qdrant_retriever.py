from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams

from huatai_query_agent.retrieval.embedding import EmbeddingModel, build_embedding_from_env
from huatai_query_agent.retrieval.types import MetadataChunk, RetrievalResult


PACKAGE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_QDRANT_PATH = PACKAGE_DIR / "vectorstore" / "qdrant"
DEFAULT_COLLECTION = "huatai_metadata"


def _chunk_to_payload(chunk: MetadataChunk) -> dict[str, Any]:
    payload = {
        "chunk_id": chunk.id,
        "chunk_type": chunk.chunk_type,
        "text": chunk.text,
    }
    payload.update(chunk.metadata)
    return payload


def _payload_to_chunk(payload: dict[str, Any]) -> MetadataChunk:
    payload = dict(payload)
    chunk_id = str(payload.pop("chunk_id"))
    chunk_type = str(payload.pop("chunk_type"))
    text = str(payload.pop("text"))
    return MetadataChunk(id=chunk_id, chunk_type=chunk_type, text=text, metadata=payload)


class QdrantMetadataStore:
    def __init__(
        self,
        *,
        path: Path = DEFAULT_QDRANT_PATH,
        collection_name: str = DEFAULT_COLLECTION,
        embedding: EmbeddingModel | None = None,
    ) -> None:
        self.path = path
        self.collection_name = collection_name
        self.embedding = embedding or build_embedding_from_env()
        self.client = QdrantClient(path=str(path))

    def rebuild(self, chunks: list[MetadataChunk]) -> None:
        embedded_chunks = [(chunk, self.embedding.embed(chunk.text)) for chunk in chunks]
        vector_size = len(embedded_chunks[0][1]) if embedded_chunks else self.embedding.vector_size
        self.client.close()
        if self.path.exists():
            shutil.rmtree(self.path, ignore_errors=True)
        self.path.mkdir(parents=True, exist_ok=True)
        self.client = QdrantClient(path=str(self.path))
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        points = [
            PointStruct(
                id=idx,
                vector=vector,
                payload=_chunk_to_payload(chunk),
            )
            for idx, (chunk, vector) in enumerate(embedded_chunks)
        ]
        if points:
            self.client.upsert(collection_name=self.collection_name, points=points)

    def search(
        self,
        query: str,
        *,
        top_k: int = 12,
        chunk_types: set[str] | None = None,
    ) -> list[RetrievalResult]:
        if not self.client.collection_exists(self.collection_name):
            return []

        query_filter = None
        if chunk_types:
            query_filter = Filter(
                should=[
                    FieldCondition(key="chunk_type", match=MatchValue(value=chunk_type))
                    for chunk_type in sorted(chunk_types)
                ]
            )

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=self.embedding.embed(query),
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
        )
        points = getattr(response, "points", response)
        results: list[RetrievalResult] = []
        for point in points:
            payload = point.payload or {}
            results.append(
                RetrievalResult(
                    chunk=_payload_to_chunk(payload),
                    score=float(point.score),
                    source="qdrant",
                )
            )
        return results

    def close(self) -> None:
        self.client.close()
