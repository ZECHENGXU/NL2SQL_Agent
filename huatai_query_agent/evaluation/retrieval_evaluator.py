from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from huatai_query_agent.retrieval.chunk_builder import build_metadata_chunks
from huatai_query_agent.retrieval.hybrid_retriever import HybridMetadataRetriever
from huatai_query_agent.retrieval.qdrant_retriever import QdrantMetadataStore
from huatai_query_agent.retrieval.reranker import build_reranker_from_env
from huatai_query_agent.retrieval.types import RetrievalResult


PACKAGE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CASES_PATH = PACKAGE_DIR / "evaluation" / "advanced_query_cases.yaml"
DEFAULT_TEMP_QDRANT_PATH = PACKAGE_DIR / "runtime" / "retrieval_eval_qdrant"
DEFAULT_CUTOFFS = (5, 10, 16)


@dataclass(frozen=True)
class RetrievalMetrics:
    schema_table_recall: float
    direct_table_recall: float
    all_schema_tables_hit: float
    all_direct_tables_hit: float
    defined_metric_recall: float | None
    all_defined_metrics_hit: float | None
    business_metric_recall: float
    judged_context_precision: float
    mrr: float


@dataclass(frozen=True)
class AggregateMetrics:
    case_count: int
    cases_with_defined_metrics: int
    schema_table_recall: float
    direct_table_recall: float
    all_schema_tables_hit: float
    all_direct_tables_hit: float
    defined_metric_recall: float
    all_defined_metrics_hit: float
    business_metric_recall: float
    judged_context_precision: float
    mrr: float


def evaluate_advanced_cases(
    *,
    cases_path: Path = DEFAULT_CASES_PATH,
    cutoffs: tuple[int, ...] = DEFAULT_CUTOFFS,
    temp_qdrant_path: Path | None = None,
) -> dict[str, Any]:
    cases = _load_cases(cases_path)
    chunks = build_metadata_chunks()
    defined_metrics = {
        str(chunk.metadata.get("metric_name"))
        for chunk in chunks
        if chunk.chunk_type == "metric" and chunk.metadata.get("metric_name")
    }

    qdrant = QdrantMetadataStore(path=temp_qdrant_path) if temp_qdrant_path else QdrantMetadataStore()
    if temp_qdrant_path:
        qdrant.rebuild(chunks)
    retriever = HybridMetadataRetriever(
        chunks=chunks,
        qdrant_store=qdrant,
        enable_reranker=False,
    )
    reranker = build_reranker_from_env()
    if reranker is None:
        retriever.close()
        raise RuntimeError("Reranker is disabled; A/B evaluation requires a reranker.")

    max_cutoff = max(cutoffs)
    per_mode: dict[str, dict[int, list[RetrievalMetrics]]] = {
        "rrf": {cutoff: [] for cutoff in cutoffs},
        "rrf_reranker": {cutoff: [] for cutoff in cutoffs},
    }
    per_case: list[dict[str, Any]] = []
    try:
        for case in cases:
            question = str(case["question"])
            retriever.reranker = None
            rrf_results = retriever.search(question, top_k=max_cutoff)
            retriever.reranker = reranker
            reranked_results = retriever.search(question, top_k=max_cutoff)

            case_record: dict[str, Any] = {"id": case["id"], "cutoffs": {}}
            for cutoff in cutoffs:
                baseline = _score_case(
                    case,
                    rrf_results[:cutoff],
                    defined_metrics=defined_metrics,
                )
                experiment = _score_case(
                    case,
                    reranked_results[:cutoff],
                    defined_metrics=defined_metrics,
                )
                per_mode["rrf"][cutoff].append(baseline)
                per_mode["rrf_reranker"][cutoff].append(experiment)
                case_record["cutoffs"][str(cutoff)] = {
                    "rrf": asdict(baseline),
                    "rrf_reranker": asdict(experiment),
                }
            per_case.append(case_record)
    finally:
        retriever.close()

    aggregates = {
        mode: {
            str(cutoff): asdict(_aggregate(metrics))
            for cutoff, metrics in by_cutoff.items()
        }
        for mode, by_cutoff in per_mode.items()
    }
    deltas = {
        str(cutoff): _metric_deltas(
            aggregates["rrf"][str(cutoff)],
            aggregates["rrf_reranker"][str(cutoff)],
        )
        for cutoff in cutoffs
    }
    return {
        "cases_path": str(cases_path),
        "case_count": len(cases),
        "defined_metric_count": len(defined_metrics),
        "cutoffs": list(cutoffs),
        "aggregates": aggregates,
        "deltas": deltas,
        "cases": per_case,
    }


def _score_case(
    case: dict[str, Any],
    results: list[RetrievalResult],
    *,
    defined_metrics: set[str],
) -> RetrievalMetrics:
    required_tables = {str(value) for value in case.get("required_tables", [])}
    expected_metrics = {str(value) for value in case.get("expected_metrics", [])}
    expected_defined_metrics = expected_metrics & defined_metrics

    schema_tables_hit: set[str] = set()
    direct_tables_hit: set[str] = set()
    metrics_hit: set[str] = set()
    relevance: list[bool] = []

    for result in results:
        chunk = result.chunk
        metadata = chunk.metadata
        table_name = str(metadata.get("table_name") or "")
        metric_name = str(metadata.get("metric_name") or "")
        is_relevant = False

        if chunk.chunk_type in {"table", "field"} and table_name in required_tables:
            schema_tables_hit.add(table_name)
            is_relevant = True
        if chunk.chunk_type == "table" and table_name in required_tables:
            direct_tables_hit.add(table_name)
        if chunk.chunk_type == "metric" and metric_name in expected_metrics:
            metrics_hit.add(metric_name)
            is_relevant = True
        if chunk.chunk_type == "relationship":
            left_table = str(metadata.get("left_table") or "")
            right_table = str(metadata.get("right_table") or "")
            is_relevant = left_table in required_tables and right_table in required_tables
        relevance.append(is_relevant)

    schema_recall = _recall(schema_tables_hit, required_tables)
    direct_recall = _recall(direct_tables_hit, required_tables)
    defined_recall = (
        _recall(metrics_hit, expected_defined_metrics)
        if expected_defined_metrics
        else None
    )
    return RetrievalMetrics(
        schema_table_recall=schema_recall,
        direct_table_recall=direct_recall,
        all_schema_tables_hit=float(schema_recall == 1.0),
        all_direct_tables_hit=float(direct_recall == 1.0),
        defined_metric_recall=defined_recall,
        all_defined_metrics_hit=(
            float(defined_recall == 1.0) if defined_recall is not None else None
        ),
        business_metric_recall=_recall(metrics_hit, expected_metrics),
        judged_context_precision=(sum(relevance) / len(relevance) if relevance else 0.0),
        mrr=next((1.0 / rank for rank, hit in enumerate(relevance, start=1) if hit), 0.0),
    )


def _aggregate(metrics: list[RetrievalMetrics]) -> AggregateMetrics:
    defined = [item for item in metrics if item.defined_metric_recall is not None]
    return AggregateMetrics(
        case_count=len(metrics),
        cases_with_defined_metrics=len(defined),
        schema_table_recall=_mean([item.schema_table_recall for item in metrics]),
        direct_table_recall=_mean([item.direct_table_recall for item in metrics]),
        all_schema_tables_hit=_mean([item.all_schema_tables_hit for item in metrics]),
        all_direct_tables_hit=_mean([item.all_direct_tables_hit for item in metrics]),
        defined_metric_recall=_mean(
            [float(item.defined_metric_recall) for item in defined]
        ),
        all_defined_metrics_hit=_mean(
            [float(item.all_defined_metrics_hit) for item in defined]
        ),
        business_metric_recall=_mean(
            [item.business_metric_recall for item in metrics]
        ),
        judged_context_precision=_mean(
            [item.judged_context_precision for item in metrics]
        ),
        mrr=_mean([item.mrr for item in metrics]),
    )


def _metric_deltas(
    baseline: dict[str, Any],
    experiment: dict[str, Any],
) -> dict[str, float]:
    ignored = {"case_count", "cases_with_defined_metrics"}
    return {
        key: float(experiment[key]) - float(value)
        for key, value in baseline.items()
        if key not in ignored
    }


def _load_cases(path: Path) -> list[dict[str, Any]]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    cases = document.get("cases", [])
    if not isinstance(cases, list):
        raise ValueError(f"Expected a case list in {path}.")
    return [dict(case) for case in cases]


def _recall(hits: set[str], expected: set[str]) -> float:
    if not expected:
        return 0.0
    return len(hits & expected) / len(expected)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="A/B test RRF against RRF + reranker.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--temp-qdrant",
        type=Path,
        default=None,
        help="Rebuild and use an isolated Qdrant directory.",
    )
    args = parser.parse_args()

    if args.temp_qdrant:
        resolved = args.temp_qdrant.resolve()
        runtime_root = (PACKAGE_DIR / "runtime").resolve()
        if runtime_root not in resolved.parents:
            raise ValueError(f"Temporary Qdrant path must be inside {runtime_root}.")
        if resolved.exists():
            shutil.rmtree(resolved)

    report = evaluate_advanced_cases(
        cases_path=args.cases,
        temp_qdrant_path=args.temp_qdrant,
    )
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        print(
            json.dumps(
                {
                    "case_count": report["case_count"],
                    "defined_metric_count": report["defined_metric_count"],
                    "aggregates": report["aggregates"],
                    "deltas": report["deltas"],
                    "output": str(args.output),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(payload)


if __name__ == "__main__":
    main()
