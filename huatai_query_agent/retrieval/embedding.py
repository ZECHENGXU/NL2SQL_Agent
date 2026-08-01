from __future__ import annotations

import hashlib
import math
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


DEFAULT_VECTOR_SIZE = 384
DEFAULT_BGE_M3_VECTOR_SIZE = 1024
DEFAULT_BGE_SMALL_ZH_VECTOR_SIZE = 512
DEFAULT_BGE_SMALL_ZH_MODEL = "BAAI/bge-small-zh-v1.5"
LOCAL_BGE_SMALL_ZH_MODEL = str(Path(__file__).resolve().parent / "models" / "bge-small-zh-v1.5")
DEFAULT_SENTENCE_TRANSFORMERS_MODEL = (
    LOCAL_BGE_SMALL_ZH_MODEL
    if Path(LOCAL_BGE_SMALL_ZH_MODEL).is_dir()
    else DEFAULT_BGE_SMALL_ZH_MODEL
)


def tokenize_text(text: str) -> list[str]:
    text = text.lower()
    ascii_tokens = re.findall(r"[a-z0-9_]+", text)
    chinese_chars = re.findall(r"[一-鿿]", text)
    chinese_bigrams = [a + b for a, b in zip(chinese_chars, chinese_chars[1:])]
    return ascii_tokens + chinese_chars + chinese_bigrams


class EmbeddingModel(Protocol):
    vector_size: int

    def embed(self, text: str) -> list[float]:
        ...


class HashingEmbedding:
    """Deterministic local embedding fallback for MVP vector indexing.

    This is not a semantic model. It lets the Qdrant path run without external
    model services, while keeping the embedding interface swappable for bge-m3
    or another local OpenAI-compatible embedding API later.
    """

    def __init__(self, vector_size: int = DEFAULT_VECTOR_SIZE) -> None:
        self.vector_size = vector_size

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.vector_size
        for token in tokenize_text(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "little") % self.vector_size
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


class SentenceTransformersEmbedding:
    """Local sentence-transformers model for semantic vector embedding.

    Defaults to BAAI/bge-small-zh-v1.5 (512-dim, Chinese-optimized).
    Supports any sentence-transformers compatible model via env override.
    """

    def __init__(self, model_name: str = DEFAULT_SENTENCE_TRANSFORMERS_MODEL) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "sentence-transformers is not installed. Install huatai_query_agent/requirements.txt."
            ) from exc

        self.model_name = model_name
        self._model = SentenceTransformer(model_name)
        self.vector_size = getattr(self._model, "get_embedding_dimension", self._model.get_sentence_embedding_dimension)() or DEFAULT_BGE_SMALL_ZH_VECTOR_SIZE

    def embed(self, text: str) -> list[float]:
        vector = self._model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return [float(value) for value in vector]


try:
    from sentence_transformers import SentenceTransformer  # noqa: F811

    _SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    _SENTENCE_TRANSFORMERS_AVAILABLE = False


def _is_sentence_transformers_available() -> bool:
    if not _SENTENCE_TRANSFORMERS_AVAILABLE:
        return False
    return True


@dataclass(frozen=True)
class EmbeddingSettings:
    provider: str
    model: str
    base_url: str | None
    api_key: str | None
    vector_size: int
    normalize: bool

    @classmethod
    def from_env(cls) -> "EmbeddingSettings":
        provider = _env("HUATAI_EMBEDDING_PROVIDER") or (
            "sentence-transformers" if _is_sentence_transformers_available() else "hashing"
        )
        default_model = (
            DEFAULT_SENTENCE_TRANSFORMERS_MODEL
            if provider == "sentence-transformers"
            else "BAAI/bge-m3"
        )
        model = _env("HUATAI_EMBEDDING_MODEL", default_model) or default_model
        default_vector_size = (
            DEFAULT_VECTOR_SIZE
            if provider.lower() in {"hashing", "local_hashing", "fallback"}
            else DEFAULT_BGE_M3_VECTOR_SIZE
            if "bge-m3" in model.lower()
            else DEFAULT_BGE_SMALL_ZH_VECTOR_SIZE
            if "bge-small" in model.lower()
            else DEFAULT_VECTOR_SIZE
        )
        return cls(
            provider=provider,
            model=model,
            base_url=_env("HUATAI_EMBEDDING_BASE_URL"),
            api_key=_env("HUATAI_EMBEDDING_API_KEY"),
            vector_size=int(_env("HUATAI_EMBEDDING_VECTOR_SIZE", str(default_vector_size)) or default_vector_size),
            normalize=(_env("HUATAI_EMBEDDING_NORMALIZE", "true") or "true").lower() in {"1", "true", "yes", "y"},
        )


class OpenAICompatibleEmbedding:
    """Embedding backend for local OpenAI-compatible services such as bge-m3."""

    def __init__(self, settings: EmbeddingSettings) -> None:
        if not settings.base_url:
            raise ValueError("HUATAI_EMBEDDING_BASE_URL is required for OpenAI-compatible embedding.")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("openai package is not installed. Install huatai_query_agent/requirements.txt.") from exc

        self.settings = settings
        self.vector_size = settings.vector_size
        self._client = OpenAI(
            api_key=settings.api_key or "local-embedding-key",
            base_url=settings.base_url,
        )

    def embed(self, text: str) -> list[float]:
        response = self._client.embeddings.create(model=self.settings.model, input=[text])
        vector = [float(value) for value in response.data[0].embedding]
        if len(vector) != self.vector_size:
            self.vector_size = len(vector)
        if self.settings.normalize:
            vector = _normalize_vector(vector)
        return vector


def build_embedding_from_env() -> EmbeddingModel:
    settings = EmbeddingSettings.from_env()
    provider = settings.provider.lower()
    if provider in {"hashing", "local_hashing", "fallback"}:
        return HashingEmbedding(vector_size=settings.vector_size if settings.vector_size else DEFAULT_VECTOR_SIZE)
    if provider in {"sentence-transformers", "sentence_transformers", "local", "st"}:
        return SentenceTransformersEmbedding(model_name=settings.model)
    if provider in {"openai", "openai_compatible", "local_openai_compatible", "bge-m3", "bge_m3"}:
        return OpenAICompatibleEmbedding(settings)
    if _is_sentence_transformers_available():
        return SentenceTransformersEmbedding(model_name=settings.model or DEFAULT_SENTENCE_TRANSFORMERS_MODEL)
    return HashingEmbedding(vector_size=settings.vector_size if settings.vector_size else DEFAULT_VECTOR_SIZE)


def _normalize_vector(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def _env(name: str, fallback: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None or value == "":
        return fallback
    return value
