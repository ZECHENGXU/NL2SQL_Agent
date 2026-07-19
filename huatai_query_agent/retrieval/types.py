from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MetadataChunk:
    id: str
    chunk_type: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievalResult:
    chunk: MetadataChunk
    score: float
    source: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.chunk.id,
            "chunk_type": self.chunk.chunk_type,
            "score": round(self.score, 6),
            "source": self.source,
            "text": self.chunk.text,
            "metadata": self.chunk.metadata,
        }

