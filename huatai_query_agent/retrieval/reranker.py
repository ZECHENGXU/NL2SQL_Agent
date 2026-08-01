from __future__ import annotations

import os
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from huatai_query_agent.retrieval.types import RetrievalResult


DEFAULT_BGE_RERANKER_MODEL = "BAAI/bge-reranker-base"
LOCAL_BGE_RERANKER_MODEL = Path(__file__).resolve().parent / "models" / "bge-reranker-base"
DEFAULT_RERANKER_MODEL = (
    str(LOCAL_BGE_RERANKER_MODEL)
    if LOCAL_BGE_RERANKER_MODEL.is_dir()
    else DEFAULT_BGE_RERANKER_MODEL
)


class MetadataReranker(Protocol):
    name: str

    def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
    ) -> list[RetrievalResult]:
        ...


@dataclass(frozen=True)
class RerankerSettings:
    provider: str = "cross-encoder"
    model: str = DEFAULT_RERANKER_MODEL
    batch_size: int = 8
    max_length: int = 512
    device: str | None = None
    fail_open: bool = True
    fusion_weight: float = 0.5
    fusion_rrf_k: int = 60

    @classmethod
    def from_env(cls) -> "RerankerSettings":
        return cls(
            provider=_env("HUATAI_RERANKER_PROVIDER", "cross-encoder")
            or "cross-encoder",
            model=_env("HUATAI_RERANKER_MODEL", DEFAULT_RERANKER_MODEL)
            or DEFAULT_RERANKER_MODEL,
            batch_size=_positive_int_env("HUATAI_RERANKER_BATCH_SIZE", 8),
            max_length=_positive_int_env("HUATAI_RERANKER_MAX_LENGTH", 512),
            device=_env("HUATAI_RERANKER_DEVICE"),
            fail_open=_boolean_env("HUATAI_RERANKER_FAIL_OPEN", True),
            fusion_weight=_positive_float_env("HUATAI_RERANKER_FUSION_WEIGHT", 0.5),
            fusion_rrf_k=_positive_int_env("HUATAI_RERANKER_FUSION_RRF_K", 60),
        )


class CrossEncoderMetadataReranker:
    """Score query-document pairs with a sequence-classification model."""

    name = "cross-encoder"

    def __init__(
        self,
        settings: RerankerSettings | None = None,
        *,
        model: Any | None = None,
    ) -> None:
        self.settings = settings or RerankerSettings.from_env()
        self._model = model
        self._load_error: Exception | None = None

    def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
    ) -> list[RetrievalResult]:
        if not results:
            return []

        try:
            model = self._get_model()
            raw_scores = model.predict(
                [(query, result.chunk.text) for result in results],
                batch_size=self.settings.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
            scores = _as_float_scores(raw_scores, expected_count=len(results))
        except Exception as exc:
            if not self.settings.fail_open:
                raise
            warnings.warn(
                f"Metadata reranker failed; retaining RRF order: {exc}",
                RuntimeWarning,
                stacklevel=2,
            )
            return self._fallback_results(results, exc)

        model_order = sorted(
            range(len(results)),
            key=lambda index: (-scores[index], index, results[index].chunk.id),
        )
        model_ranks = {
            result_index: rank
            for rank, result_index in enumerate(model_order, start=1)
        }

        scored_results = []
        for input_rank, (result, score) in enumerate(
            zip(results, scores),
            start=1,
        ):
            model_rank = model_ranks[input_rank - 1]
            rank_contribution = self.settings.fusion_weight / (
                self.settings.fusion_rrf_k + model_rank
            )
            fused_score = result.score + rank_contribution
            details = dict(result.details)
            details["rrf_score"] = result.score
            details["reranker"] = {
                "provider": self.name,
                "model": self.settings.model,
                "input_rank": input_rank,
                "score": score,
                "rank": model_rank,
                "fusion": "rrf_plus_cross_encoder_rank",
                "fusion_weight": self.settings.fusion_weight,
                "fusion_rrf_k": self.settings.fusion_rrf_k,
                "rank_contribution": rank_contribution,
                "status": "ok",
            }
            scored_results.append(
                RetrievalResult(
                    chunk=result.chunk,
                    score=fused_score,
                    source="reranker",
                    details=details,
                )
            )

        return sorted(
            scored_results,
            key=lambda result: (
                -result.score,
                result.details["reranker"]["input_rank"],
                result.chunk.id,
            ),
        )

    def _get_model(self) -> Any:
        if self._model is not None:
            return self._model
        if self._load_error is not None:
            raise RuntimeError("Reranker model previously failed to load.") from self._load_error

        try:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(
                self.settings.model,
                device=self.settings.device,
                max_length=self.settings.max_length,
            )
        except Exception as exc:
            self._load_error = exc
            raise
        return self._model

    def _fallback_results(
        self,
        results: list[RetrievalResult],
        error: Exception,
    ) -> list[RetrievalResult]:
        output = []
        for input_rank, result in enumerate(results, start=1):
            details = dict(result.details)
            details["reranker"] = {
                "provider": self.name,
                "model": self.settings.model,
                "input_rank": input_rank,
                "status": "fallback",
                "error_type": type(error).__name__,
            }
            output.append(
                RetrievalResult(
                    chunk=result.chunk,
                    score=result.score,
                    source=result.source,
                    details=details,
                )
            )
        return output


def build_reranker_from_env() -> MetadataReranker | None:
    settings = RerankerSettings.from_env()
    provider = settings.provider.strip().lower().replace("_", "-")
    if provider in {"", "none", "disabled", "off", "false", "0"}:
        return None
    if provider in {"cross-encoder", "sentence-transformers", "local"}:
        return CrossEncoderMetadataReranker(settings)
    raise ValueError(f"Unsupported metadata reranker provider: {settings.provider}")


def _as_float_scores(values: Any, *, expected_count: int) -> list[float]:
    if hasattr(values, "tolist"):
        values = values.tolist()
    if not isinstance(values, (list, tuple)):
        values = [values]

    scores: list[float] = []
    for value in values:
        while isinstance(value, (list, tuple)) and len(value) == 1:
            value = value[0]
        scores.append(float(value))
    if len(scores) != expected_count:
        raise ValueError(
            f"Reranker returned {len(scores)} scores for {expected_count} candidates."
        )
    return scores


def _positive_int_env(name: str, default: int) -> int:
    value = int(_env(name, str(default)) or default)
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero.")
    return value


def _positive_float_env(name: str, default: float) -> float:
    value = float(_env(name, str(default)) or default)
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero.")
    return value


def _boolean_env(name: str, default: bool) -> bool:
    fallback = "true" if default else "false"
    return (_env(name, fallback) or fallback).lower() in {"1", "true", "yes", "y"}


def _env(name: str, fallback: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None or value == "":
        return fallback
    return value
