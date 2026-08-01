from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

import sqlglot
import yaml
from sqlglot import exp

from huatai_query_agent.agent.contracts import (
    normalize_output_columns,
    output_columns_from_plan,
    table_date_ranges,
    unrequested_filter_warnings,
    validate_dictionary_projection,
    validate_eligibility_filters,
    validate_fact_preaggregation,
    validate_join_contract,
    validate_missing_fact_policy,
    validate_missing_period_policy,
    validate_projection_contract,
    validate_scoped_metadata,
    validate_snapshot_dates,
    validate_snapshot_policy,
    validate_top_n_contract,
    validate_window_contract,
)
from huatai_query_agent.agent.demo_cases import DemoCaseRepository
from huatai_query_agent.agent.state import AgentState, add_trace
from huatai_query_agent.executors.base import SqlExecutor
from huatai_query_agent.llm.client import CaseDeadlineExceeded, LlmClientError
from huatai_query_agent.llm.sql_generator import TextToSqlGenerator
from huatai_query_agent.retrieval.hybrid_retriever import HybridMetadataRetriever


DANGEROUS_SQL_PATTERN = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|create|copy|attach|detach|pragma)\b",
    flags=re.IGNORECASE,
)
PACKAGE_DIR = Path(__file__).resolve().parents[2]
SCHEMA_CATALOG_PATH = PACKAGE_DIR / "metadata" / "schema_catalog.yaml"
METRICS_PATH = PACKAGE_DIR / "metadata" / "metrics.yaml"
BUSINESS_TERMS_PATH = PACKAGE_DIR / "metadata" / "business_terms.yaml"


def _strip_leading_comments(sql: str) -> str:
    lines = []
    for line in sql.strip().splitlines():
        if line.strip().startswith("--"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


@lru_cache(maxsize=1)
def _known_table_names() -> set[str]:
    doc = yaml.safe_load(SCHEMA_CATALOG_PATH.read_text(encoding="utf-8"))
    return set(doc.get("tables", {}).keys())


@lru_cache(maxsize=1)
def _known_columns_by_table() -> dict[str, set[str]]:
    doc = yaml.safe_load(SCHEMA_CATALOG_PATH.read_text(encoding="utf-8"))
    return {
        table_name: set(table.get("columns", {}).keys())
        for table_name, table in doc.get("tables", {}).items()
    }


@lru_cache(maxsize=1)
def _metrics_doc() -> dict[str, Any]:
    return yaml.safe_load(METRICS_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _business_terms_doc() -> dict[str, Any]:
    return yaml.safe_load(BUSINESS_TERMS_PATH.read_text(encoding="utf-8"))


def _question(state: AgentState) -> str:
    return state.get("normalized_question") or state.get("question", "")


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _merge_intent(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in patch.items():
        if value in (None, "", [], {}):
            continue
        if isinstance(value, list):
            existing = list(merged.get(key, [])) if isinstance(merged.get(key), list) else []
            seen = {str(item) for item in existing}
            for item in value:
                if str(item) not in seen:
                    existing.append(item)
                    seen.add(str(item))
            merged[key] = existing
        elif isinstance(value, dict) and isinstance(merged.get(key), dict):
            nested = dict(merged[key])
            nested.update({k: v for k, v in value.items() if v not in (None, "", [], {})})
            merged[key] = nested
        else:
            merged[key] = value
    return merged


def _dedupe_text(values: list[Any]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            output.append(text)
            seen.add(text)
    return output


def _sql_generation_attempt(
    state: AgentState,
    *,
    attempt_type: str,
    started_at: str,
    started_perf: float,
    generated: Any | None = None,
    error: str = "",
) -> list[dict[str, Any]]:
    attempts = list(state.get("sql_generation_attempts", []))
    completed_at = datetime.now(timezone.utc).isoformat()
    event = {
        "attempt": len(attempts) + 1,
        "attempt_type": attempt_type,
        "status": "ok" if generated is not None else "failed",
        "started_at": getattr(generated, "started_at", "") or started_at,
        "completed_at": getattr(generated, "completed_at", "") or completed_at,
        "elapsed_ms": round(
            float(getattr(generated, "elapsed_ms", 0.0) or (time.perf_counter() - started_perf) * 1000),
            4,
        ),
        "model": str(getattr(generated, "model", "") or ""),
        "usage": dict(getattr(generated, "usage", {}) or {}),
        "sql": str(getattr(generated, "sql", "") or ""),
        "error": error,
    }
    attempts.append(event)
    _write_live_sql_event(state, {"phase": "completed", **event})
    return attempts


def _start_live_sql_attempt(
    state: AgentState,
    *,
    attempt_type: str,
    started_at: str,
) -> None:
    _write_live_sql_event(
        state,
        {
            "phase": "started",
            "attempt": len(state.get("sql_generation_attempts", [])) + 1,
            "attempt_type": attempt_type,
            "started_at": started_at,
        },
    )


def _write_live_sql_event(state: AgentState, event: dict[str, Any]) -> None:
    raw_path = os.environ.get("HUATAI_LIVE_SQL_EVENTS_PATH", "").strip()
    if not raw_path:
        return
    payload = {
        "query_id": state.get("query_id", ""),
        "thread_id": state.get("thread_id", ""),
        **event,
    }
    path = Path(raw_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")
    except OSError:
        return


def _question_has_time_scope(question: str) -> bool:
    return bool(
        re.search(
            r"20\d{2}|Q[1-4]|q[1-4]|季度|月份|月末|期末|期初|当日|当前|最新|\d{1,2}月\d{1,2}日",
            question,
        )
    )


def _question_has_unresolved_placeholder(question: str) -> bool:
    return bool(re.search(r"某(?:个|只|类)?(?:产品|客户|营业部|分公司)|某段时间|某一天|待定|未指定", question))


def _classify_missing_slots(state: AgentState) -> tuple[list[str], list[str], list[str]]:
    raw_missing = _dedupe_text(
        list(state.get("missing_slots", []))
        + list(state.get("blocking_missing_slots", []))
    )
    assumptions = _dedupe_text(
        list(state.get("assumptions", []))
        + list(state.get("slot_report", {}).get("assumptions", []))
    )
    if not raw_missing:
        return [], [], assumptions

    question = _question(state)
    intent = state.get("intent", {})
    continue_with_assumptions = bool(state.get("continue_with_assumptions"))
    has_target = bool(
        intent.get("target")
        or intent.get("metrics")
        or intent.get("dimensions")
        or intent.get("requested_outputs")
    )
    has_time = _question_has_time_scope(question) or bool(intent.get("time_range"))
    has_placeholder = _question_has_unresolved_placeholder(question)
    blocking: list[str] = []
    non_blocking: list[str] = []

    for item in raw_missing:
        lowered = item.lower()
        hard_failure = "llm intent parsing failed" in lowered or "解析失败" in item
        target_missing = any(token in item for token in ("查询目标", "统计目标", "核心指标")) and not has_target
        time_missing = any(token in item for token in ("时间", "日期", "期间")) and not has_time
        entity_missing = any(token in item for token in ("目标实体", "产品名称", "客户范围")) and has_placeholder
        if hard_failure or target_missing or time_missing or entity_missing:
            blocking.append(item)
        elif continue_with_assumptions or has_target or len(question.strip()) >= 8:
            non_blocking.append(item)
        else:
            blocking.append(item)

    assumptions.extend(f"未澄清并按元数据默认规则继续：{item}" for item in non_blocking)
    return _dedupe_text(blocking), _dedupe_text(non_blocking), _dedupe_text(assumptions)


def _enrich_sql_plan(state: AgentState, plan: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(plan)
    intent = state.get("intent", {})
    metadata = state.get("metadata_context", {})
    matched_case = metadata.get("matched_demo_case", {}) if isinstance(metadata, dict) else {}
    request_context = metadata.get("request_context", {}) if isinstance(metadata, dict) else {}
    contract = (
        matched_case.get("output_contract")
        or request_context.get("output_contract")
        or {}
    )

    request_columns = dict(request_context.get("output_contract") or {}).get("columns") or []
    if request_columns:
        enriched["output_columns"] = request_columns
    elif not enriched.get("output_columns"):
        requested = intent.get("requested_outputs") or intent.get("output_columns")
        enriched["output_columns"] = requested or contract.get("columns") or []
    enriched["output_columns"] = normalize_output_columns(enriched.get("output_columns") or [])

    if not enriched.get("tables"):
        enriched["tables"] = (
            metadata.get("tables")
            or matched_case.get("required_tables")
            or request_context.get("required_tables")
            or []
        )
    if not enriched.get("metrics"):
        enriched["metrics"] = (
            intent.get("metrics")
            or matched_case.get("expected_metrics")
            or request_context.get("expected_metrics")
            or []
        )

    snapshot_policy = dict(intent.get("snapshot_policy") or {})
    snapshot_policy.update(dict(enriched.get("snapshot_policy") or {}))
    configured_ranges = table_date_ranges()
    for table in enriched.get("tables", []) or []:
        configured = configured_ranges.get(str(table), "")
        if re.fullmatch(r"\d{8}", configured):
            snapshot_policy.setdefault(str(table), configured)
    enriched["snapshot_policy"] = snapshot_policy

    for key in (
        "population",
        "grain",
        "eligibility_filters",
        "missing_fact_policy",
        "missing_period_policy",
        "window",
        "order_by",
        "top_n",
        "expect_nonempty",
        "join_contract",
    ):
        request_value = request_context.get(key)
        if request_value not in (None, "", [], {}):
            enriched[key] = request_value
            continue
        if enriched.get(key) not in (None, "", [], {}):
            continue
        value = intent.get(key)
        if value in (None, "", [], {}):
            value = contract.get(key)
        if value in (None, "", [], {}):
            value = request_context.get(key)
        if value not in (None, "", [], {}):
            enriched[key] = value
    if request_context.get("calculation_notes"):
        enriched.setdefault("calculation_notes", request_context["calculation_notes"])
    if (
        "missing_period_policy" in enriched
        and not request_context.get("missing_period_policy")
        and not re.search(r"按月|每月|逐月|月度|月份|月环比|缺失.{0,4}(?:期间|周期)|补齐.{0,4}(?:期间|周期)", _question(state))
    ):
        enriched.pop("missing_period_policy", None)
    enriched.setdefault(
        "dictionary_translation",
        contract.get("dictionary_translation", True),
    )
    return enriched


def _extract_org_followup_filter(question: str) -> dict[str, str] | None:
    match = re.search(r"(?:只看|改成|限定|筛选|看)([\u4e00-\u9fa5A-Za-z0-9]+(?:分公司|营业部))", question)
    if not match:
        return None

    org_name = match.group(1)
    if org_name.endswith("分公司"):
        return {
            "type": "branch",
            "field": "branch.up_org_name",
            "value": org_name,
            "description": f"限定分公司为 {org_name}",
        }
    if org_name.endswith("营业部"):
        return {
            "type": "branch",
            "field": "branch.org_name",
            "value": org_name,
            "description": f"限定营业部为 {org_name}",
        }
    return None


def _apply_outer_filter(sql: str, condition: str) -> str:
    group_match = list(re.finditer(r"\n\s*group\s+by\b", sql, flags=re.IGNORECASE))
    order_match = list(re.finditer(r"\n\s*order\s+by\b", sql, flags=re.IGNORECASE))
    limit_match = list(re.finditer(r"\n\s*limit\b", sql, flags=re.IGNORECASE))
    insertion_candidates = group_match or order_match or limit_match
    insert_at = insertion_candidates[-1].start() if insertion_candidates else len(sql)

    prefix = sql[:insert_at].rstrip()
    suffix = sql[insert_at:]
    last_from = prefix.lower().rfind("\nfrom ")
    last_where = prefix.lower().rfind("\nwhere ")
    if last_where > last_from:
        return f"{prefix}\n  and {condition}{suffix}"
    return f"{prefix}\nwhere {condition}{suffix}"


def _apply_followup_sql_patch(sql: str, patch: dict[str, str] | None) -> str:
    if not patch:
        return sql
    field = patch.get("field")
    value = patch.get("value")
    if not field or not value:
        return sql
    condition = f"{field} = '{value}'"
    if condition.lower() in sql.lower():
        return sql
    return _apply_outer_filter(sql, condition)


def _product_ambiguities_for_question(question: str) -> list[dict[str, str]]:
    doc = _business_terms_doc()
    rules = doc.get("product_terms", {}).get("name_matching_rules", [])
    classification_terms = {
        str(rule.get("term", ""))
        for rule in doc.get("product_terms", {}).get("classification_rules", [])
        if rule.get("term")
    }
    found: list[dict[str, str]] = []
    for rule in rules:
        term = str(rule.get("term") or "")
        note = str(rule.get("ambiguity_note") or "")
        if not term or not note or term not in question:
            continue
        has_classifier = any(classifier in question for classifier in classification_terms if classifier != term)
        if has_classifier:
            continue
        found.append(
            {
                "term": term,
                "message": note,
                "sql_condition": str(rule.get("sql_condition") or ""),
            }
        )
    return found


def _normalize_sql_text(value: str) -> str:
    return re.sub(r"[^a-z0-9_\u4e00-\u9fa5]+", "", value.lower())


def _select_aliases(parsed_statements: list[exp.Expression | None]) -> set[str]:
    aliases: set[str] = set()
    for statement in parsed_statements:
        if statement is None:
            continue
        for alias in statement.find_all(exp.Alias):
            if alias.alias:
                aliases.add(alias.alias.lower())
    return aliases


def _expected_metrics(state: AgentState, aliases: set[str]) -> set[str]:
    metrics = set()
    sql_plan = state.get("sql_plan", {})
    metadata = state.get("metadata_context", {})
    if isinstance(sql_plan, dict):
        metrics.update(str(item) for item in _as_list(sql_plan.get("metrics")))
    if isinstance(metadata, dict):
        matched_case = metadata.get("matched_demo_case", {})
        if isinstance(matched_case, dict):
            metrics.update(str(item) for item in _as_list(matched_case.get("expected_metrics")))

    known_metrics = set((_metrics_doc().get("metrics") or {}).keys())
    for alias in aliases:
        if alias in known_metrics:
            metrics.add(alias)
        elif alias.endswith("total_asset") or alias == "total_asset":
            metrics.add("total_asset")
        elif alias.endswith("transaction_amount") or alias == "transaction_amount":
            metrics.add("transaction_amount")
        elif "profit_loss" in alias:
            metrics.add("period_profit_loss")
        elif alias.endswith("asset_in") or alias.endswith("asset_inflow"):
            metrics.add("asset_inflow")
        elif alias.endswith("asset_out") or alias.endswith("asset_outflow"):
            metrics.add("asset_outflow")
        elif "market_value" in alias or "mkt_val" in alias:
            metrics.add("holding_market_value")
        elif "avg_daily_asset" in alias or "average_daily_asset" in alias:
            metrics.add("average_daily_asset")
        elif alias == "turnover":
            metrics.add("turnover")
        elif alias == "total_fee":
            metrics.add("total_fee")
        elif alias == "net_inflow":
            metrics.add("net_inflow")
    return {metric for metric in metrics if metric}


def _metric_formula_failures(sql: str, state: AgentState, parsed_statements: list[exp.Expression | None]) -> list[str]:
    normalized_sql = _normalize_sql_text(sql)
    aliases = _select_aliases(parsed_statements)
    metrics = _expected_metrics(state, aliases)
    failures: list[str] = []

    def has_all(*terms: str) -> bool:
        return all(_normalize_sql_text(term) in normalized_sql for term in terms)

    for metric in sorted(metrics):
        if metric == "count":
            continue
        if metric == "total_asset" and ("total_asset" in aliases or metric in metrics):
            if "total_asset" in aliases or any(alias.endswith("total_asset") for alias in aliases):
                if not has_all("nm_tot_aset", "fc_pur_aset"):
                    failures.append("Metric formula mismatch for total_asset: expected nm_tot_aset + fc_pur_aset.")
        elif metric == "average_daily_asset":
            actual_snapshot_average = bool(
                re.search(r"实际.*快照|存在的.*快照|不要固定.*90|按实际", _question(state))
            )
            normalized_compact = sql.replace(" ", "").lower()
            has_average = "avg(" in normalized_compact or (
                "sum(" in normalized_compact and "count(" in normalized_compact
            )
            if not has_all("nm_tot_aset", "fc_pur_aset"):
                failures.append(
                    "Metric formula mismatch for average_daily_asset: total asset fields are incomplete."
                )
            elif actual_snapshot_average and ("/90" in normalized_compact or not has_average):
                failures.append(
                    "Metric formula mismatch for average_daily_asset: use actual snapshot average, not a fixed divisor."
                )
            elif not actual_snapshot_average and "/90" not in normalized_compact and not has_average:
                failures.append(
                    "Metric formula mismatch for average_daily_asset: expected a declared daily-average denominator."
                )
        elif metric == "transaction_amount":
            if not has_all("buy_amt", "sell_amt"):
                failures.append("Metric formula mismatch for transaction_amount: expected buy_amt + sell_amt.")
        elif metric == "turnover":
            if not has_all("buy_amt", "sell_amt"):
                failures.append("Metric formula mismatch for turnover: expected buy_amt + sell_amt.")
        elif metric == "total_fee":
            if not has_all("buy_rake", "sell_rake", "buy_fare", "sell_fare"):
                failures.append(
                    "Metric formula mismatch for total_fee: expected buy/sell rake plus buy/sell fare."
                )
        elif metric == "net_inflow":
            if not has_all("cash_in", "tran_in", "assign_in", "cash_out", "tran_out", "assign_out"):
                failures.append(
                    "Metric formula mismatch for net_inflow: expected all cash/tran/assign inflow and outflow fields."
                )
        elif metric == "holding_market_value":
            if not has_all("mkt_val"):
                failures.append("Metric formula mismatch for holding_market_value: expected mkt_val.")
        elif metric == "asset_inflow":
            if not has_all("cash_in", "tran_in", "assign_in"):
                failures.append("Metric formula mismatch for asset_inflow: expected cash_in + tran_in + assign_in.")
        elif metric == "asset_outflow":
            if not has_all("cash_out", "tran_out", "assign_out"):
                failures.append("Metric formula mismatch for asset_outflow: expected cash_out + tran_out + assign_out.")
        elif metric == "period_profit_loss":
            uses_rollup_aliases = has_all("end_total_asset", "begin_total_asset") and (
                has_all("asset_out", "asset_in") or has_all("asset_outflow", "asset_inflow")
            )
            uses_raw_terms = has_all("nm_tot_aset", "fc_pur_aset", "cash_in", "tran_in", "assign_in", "cash_out", "tran_out", "assign_out")
            if not (uses_rollup_aliases or uses_raw_terms):
                failures.append(
                    "Metric formula mismatch for period_profit_loss: expected end asset - begin asset + outflow - inflow."
                )
    return failures


def init_run(state: AgentState) -> dict[str, Any]:
    return add_trace(state, "init_run", message="Initialized query run.")


def load_thread_context(state: AgentState) -> dict[str, Any]:
    summary = state.get("thread_summary", {})
    message = (
        f"Loaded thread summary from previous run: {summary.get('last_query_id')}."
        if summary
        else "No previous thread summary found."
    )
    update = {"thread_summary": summary}
    update.update(add_trace(state, "load_thread_context", message=message, context_source=bool(summary)))
    return update


def normalize_question(state: AgentState) -> dict[str, Any]:
    question = state.get("question", "").strip()
    normalized = re.sub(r"\s+", " ", question)
    update = {"normalized_question": normalized}
    update.update(add_trace(state, "normalize_question", message="Normalized question text."))
    return update


def detect_followup(state: AgentState) -> dict[str, Any]:
    question = state.get("normalized_question", "")
    followup_markers = ("继续", "上一个", "刚才", "只看", "改成", "再按")
    is_followup = any(marker in question for marker in followup_markers)
    followup_patch = _extract_org_followup_filter(question) if is_followup else None
    update: dict[str, Any] = {"is_followup": is_followup}
    if followup_patch:
        update["followup_patch"] = followup_patch
    update.update(
        add_trace(
            state,
            "detect_followup",
            message=f"is_followup={is_followup}",
            followup_patch=followup_patch or {},
        )
    )
    return update


def parse_intent(
    repo: DemoCaseRepository,
    *,
    generator: TextToSqlGenerator | None = None,
    sql_mode: str = "demo",
    allow_unmatched: bool = False,
):
    def node(state: AgentState) -> dict[str, Any]:
        inherited_query_id = None
        if state.get("is_followup"):
            inherited_query_id = str(state.get("thread_summary", {}).get("last_query_id") or "")
            if inherited_query_id:
                state = dict(state)  # type: ignore[assignment]
                state["matched_query_id"] = inherited_query_id

        case, score = repo.match(
            _question(state),
            state.get("matched_query_id"),
        )
        if allow_unmatched and case is not None and score < 0.85:
            case = None

        product_ambiguities = _product_ambiguities_for_question(_question(state))
        if case is None and product_ambiguities:
            update: dict[str, Any] = {
                "matched_score": round(score, 4),
                "intent": {
                    "target": "product_clarification",
                    "raw_question": state.get("normalized_question") or state.get("question", ""),
                },
                "missing_slots": [],
                "ambiguities": {"product": product_ambiguities},
                "confidence": 0.2,
            }
            update.update(
                add_trace(
                    state,
                    "parse_intent",
                    status="blocked",
                    message="Product ambiguity detected before SQL planning.",
                    product_ambiguities=product_ambiguities,
                )
            )
            return update

        if sql_mode == "llm" and generator is not None:
            try:
                parsed = generator.parse_intent(question=_question(state))
            except LlmClientError as exc:
                if isinstance(exc, CaseDeadlineExceeded):
                    contract = dict(state.get("request_context", {}).get("output_contract") or {})
                    update = {
                        "matched_score": round(score, 4),
                        "intent": {
                            "target": "case_timeout",
                            "raw_question": state.get("normalized_question") or state.get("question", ""),
                            "requested_outputs": contract.get("columns", []),
                        },
                        "missing_slots": [],
                        "blocking_missing_slots": [],
                        "confidence": 0.0,
                        "llm_error": str(exc),
                        "case_timed_out": True,
                    }
                    update.update(
                        add_trace(
                            state,
                            "parse_intent",
                            status="timeout",
                            message=str(exc),
                        )
                    )
                    return update
                if case is None:
                    if state.get("continue_with_assumptions") or state.get("request_context"):
                        contract = dict(state.get("request_context", {}).get("output_contract") or {})
                        update = {
                            "matched_score": round(score, 4),
                            "intent": {
                                "target": "llm_text_to_sql",
                                "raw_question": state.get("normalized_question") or state.get("question", ""),
                                "requested_outputs": contract.get("columns", []),
                            },
                            "missing_slots": [],
                            "blocking_missing_slots": [],
                            "non_blocking_uncertainties": ["LLM intent parsing failed; using batch fallback context."],
                            "assumptions": ["Intent parse failed; continued from the complete question and request contract."],
                            "confidence": 0.2,
                            "llm_error": str(exc),
                        }
                        update.update(
                            add_trace(
                                state,
                                "parse_intent",
                                status="warning",
                                message=f"{exc}; continued with deterministic batch fallback.",
                            )
                        )
                        return update
                    update = {
                        "missing_slots": ["LLM intent parsing failed."],
                        "confidence": 0.0,
                        "llm_error": str(exc),
                    }
                    update.update(add_trace(state, "parse_intent", status="failed", message=str(exc)))
                    return update
            else:
                payload = parsed.payload
                intent = dict(payload.get("intent") or {})
                if case is not None:
                    intent = _merge_intent(case.intent, intent)
                update = {
                    "matched_score": round(score, 4),
                    "intent": intent,
                    "missing_slots": [
                        str(item)
                        for item in _as_list(
                            payload.get("blocking_missing_slots")
                            or payload.get("missing_slots")
                        )
                    ],
                    "blocking_missing_slots": [
                        str(item)
                        for item in _as_list(payload.get("blocking_missing_slots"))
                    ],
                    "non_blocking_uncertainties": [
                        str(item)
                        for item in _as_list(payload.get("non_blocking_uncertainties"))
                    ],
                    "assumptions": [
                        str(item) for item in _as_list(payload.get("assumptions"))
                    ],
                    "ambiguities": dict(payload.get("ambiguities") or {}),
                    "confidence": parsed.confidence,
                    "llm_intent": parsed.to_state(),
                }
                if case is not None:
                    update["matched_query_id"] = case.query_id
                update.update(
                    add_trace(
                        state,
                        "parse_intent",
                        message=(
                            f"Parsed intent with {parsed.model}; matched demo case {case.query_id}."
                            if case is not None
                            else f"Parsed intent with {parsed.model}; no demo case matched."
                        ),
                        matched_score=round(score, 4),
                        confidence=parsed.confidence,
                    )
                )
                return update

        if case is None:
            if allow_unmatched:
                update = {
                    "matched_score": round(score, 4),
                    "intent": {
                        "target": "llm_text_to_sql",
                        "raw_question": state.get("normalized_question") or state.get("question", ""),
                    },
                    "missing_slots": [],
                    "ambiguities": {},
                    "confidence": 0.35,
                }
                update.update(
                    add_trace(
                        state,
                        "parse_intent",
                        message="No demo case matched; continuing with LLM Text-to-SQL path.",
                        matched_score=round(score, 4),
                    )
                )
                return update

            update: dict[str, Any] = {
                "missing_slots": ["M1 only supports the 7 official demo questions or query ids q001-q007."],
                "confidence": 0.0,
            }
            update.update(add_trace(state, "parse_intent", status="blocked", message="No demo case matched."))
            return update

        update = {
            "matched_query_id": case.query_id,
            "matched_score": round(score, 4),
            "intent": case.intent,
            "missing_slots": [],
            "ambiguities": {},
            "confidence": min(0.99, max(0.5, score)),
        }
        if inherited_query_id:
            update["intent"] = _merge_intent(
                case.intent,
                {"followup": {"base_query_id": inherited_query_id, "patch": state.get("followup_patch", {})}},
            )
        update.update(
            add_trace(
                state,
                "parse_intent",
                message=(
                    f"Inherited demo case {case.query_id} from thread context."
                    if inherited_query_id
                    else f"Matched demo case {case.query_id}."
                ),
                matched_score=round(score, 4),
            )
        )
        return update

    return node


def check_intent_slots(state: AgentState) -> dict[str, Any]:
    blocking, non_blocking, assumptions = _classify_missing_slots(state)
    status = "blocked" if blocking else "ok"
    message = "Missing required slots." if blocking else "Intent slots are complete."
    update = {
        "blocking_missing_slots": blocking,
        "non_blocking_uncertainties": non_blocking,
        "assumptions": assumptions,
    }
    update.update(
        add_trace(
            state,
            "check_intent_slots",
            status=status,
            message=message,
            blocking_missing_slots=blocking,
            non_blocking_uncertainties=non_blocking,
            continue_with_assumptions=bool(state.get("continue_with_assumptions")),
        )
    )
    return update


def retrieve_metadata(repo: DemoCaseRepository, retriever: HybridMetadataRetriever | None = None):
    def node(state: AgentState) -> dict[str, Any]:
        query_id = state.get("matched_query_id")
        case = repo.get(query_id) if query_id else None
        question = state.get("normalized_question") or (case.question if case else state.get("question", ""))
        fallback_context: dict[str, Any] = {}
        fallback_context_ids: list[str] = []

        if case is not None:
            fallback_context = {
                "source": "query_examples.yaml",
                "scenario": case.scenario,
                "difficulty": case.difficulty,
                "required_tables": case.required_tables,
                "expected_metrics": case.expected_metrics,
                "output_contract": case.output_contract,
                "example_question": case.question,
            }
            fallback_context_ids = [f"example_sql.{case.query_id}"]
            fallback_context_ids.extend(f"table.{table}" for table in case.required_tables)
            fallback_context_ids.extend(f"metric.{metric}" for metric in case.expected_metrics)

        if retriever is not None:
            metadata_context = retriever.build_context(question, top_k=16)
            if fallback_context:
                metadata_context["matched_demo_case"] = fallback_context
            context_ids = list(metadata_context.get("context_ids", []))
        else:
            metadata_context = fallback_context
            context_ids = fallback_context_ids

        request_context = dict(state.get("request_context", {}))
        if request_context:
            metadata_context["request_context"] = request_context
            metadata_context["tables"] = _dedupe_text(
                list(metadata_context.get("tables", []))
                + list(request_context.get("required_tables", []))
            )
            metadata_context["metrics"] = _dedupe_text(
                list(metadata_context.get("metrics", []))
                + list(request_context.get("expected_metrics", []))
            )

        update = {"metadata_context": metadata_context, "context_ids": context_ids}
        update.update(
            add_trace(
                state,
                "retrieve_metadata",
                message=f"Loaded metadata context for {query_id or 'natural_language_question'}.",
                context_ids=context_ids,
            )
        )
        return update

    return node


def fill_slots(
    *,
    generator: TextToSqlGenerator | None = None,
    sql_mode: str = "demo",
):
    def node(state: AgentState) -> dict[str, Any]:
        if state.get("case_timed_out"):
            return add_trace(
                state,
                "fill_slots",
                status="skipped",
                message="Skipped because the case deadline was exceeded.",
            )
        if sql_mode != "llm":
            update = {
                "slot_report": {
                    "mode": "demo",
                    "resolved_terms": [],
                    "assumptions": [],
                }
            }
            update.update(add_trace(state, "fill_slots", message="Slot filling skipped in demo mode."))
            return update

        if generator is None:
            update = {"llm_error": "LLM generator is not configured."}
            update.update(add_trace(state, "fill_slots", status="failed", message=update["llm_error"]))
            return update

        try:
            filled = generator.fill_slots(
                question=_question(state),
                intent=state.get("intent", {}),
                metadata_context=state.get("metadata_context", {}),
            )
        except LlmClientError as exc:
            update = {
                "llm_error": str(exc),
                "case_timed_out": isinstance(exc, CaseDeadlineExceeded),
            }
            update.update(add_trace(state, "fill_slots", status="failed", message=str(exc)))
            return update

        payload = filled.payload
        intent_patch = dict(payload.get("intent_patch") or {})
        intent = _merge_intent(state.get("intent", {}), intent_patch)
        missing_slots = [
            str(item)
            for item in _as_list(
                payload.get("blocking_missing_slots")
                or payload.get("missing_slots")
            )
        ]
        non_blocking_uncertainties = [
            str(item)
            for item in _as_list(payload.get("non_blocking_uncertainties"))
        ]
        ambiguities = dict(payload.get("ambiguities") or {})
        slot_report = {
            "resolved_terms": list(payload.get("resolved_terms") or []),
            "assumptions": [str(item) for item in _as_list(payload.get("assumptions"))],
            "non_blocking_uncertainties": non_blocking_uncertainties,
            "confidence": filled.confidence,
        }
        update = {
            "intent": intent,
            "missing_slots": missing_slots,
            "blocking_missing_slots": [
                str(item)
                for item in _as_list(payload.get("blocking_missing_slots"))
            ],
            "non_blocking_uncertainties": non_blocking_uncertainties,
            "ambiguities": ambiguities,
            "slot_report": slot_report,
            "confidence": max(float(state.get("confidence", 0.0)), filled.confidence),
            "llm_slot_fill": filled.to_state(),
        }
        update.update(
            add_trace(
                state,
                "fill_slots",
                message=f"Filled slots with {filled.model}.",
                missing_slots=missing_slots,
                confidence=filled.confidence,
            )
        )
        return update

    return node


def resolve_product(state: AgentState) -> dict[str, Any]:
    product_ambiguities = _product_ambiguities_for_question(_question(state))
    if product_ambiguities:
        ambiguities = dict(state.get("ambiguities", {}))
        ambiguities["product"] = product_ambiguities
        update = {"ambiguities": ambiguities}
        update.update(
            add_trace(
                state,
                "resolve_product",
                status="blocked",
                message="Product name requires clarification.",
                product_ambiguities=product_ambiguities,
            )
        )
        return update
    return add_trace(state, "resolve_product", message="No product ambiguity found.")


def plan_sql(
    *,
    generator: TextToSqlGenerator | None = None,
    sql_mode: str = "demo",
):
    def node(state: AgentState) -> dict[str, Any]:
        metadata = state.get("metadata_context", {})
        matched_demo_case = metadata.get("matched_demo_case", {}) if isinstance(metadata, dict) else {}

        if sql_mode == "llm":
            if generator is None:
                update = {"llm_error": "LLM generator is not configured."}
                update.update(add_trace(state, "plan_sql", status="failed", message=update["llm_error"]))
                return update

            try:
                planned = generator.plan_sql(
                    question=_question(state),
                    intent=state.get("intent", {}),
                    metadata_context=metadata,
                )
            except LlmClientError as exc:
                request_context = dict(state.get("request_context", {}))
                fallback_plan = _enrich_sql_plan(
                    state,
                    {
                        "strategy": "batch_contract_fallback",
                        "target": state.get("intent", {}).get("target", "llm_text_to_sql"),
                        "tables": request_context.get("required_tables", []),
                        "metrics": request_context.get("expected_metrics", []),
                    },
                )
                update = {
                    "sql_plan": fallback_plan,
                    "confidence": 0.2,
                    "llm_error": str(exc),
                    "case_timed_out": isinstance(exc, CaseDeadlineExceeded),
                }
                update.update(
                    add_trace(
                        state,
                        "plan_sql",
                        status="warning",
                        message=f"{exc}; continued with deterministic request-contract plan.",
                    )
                )
                return update

            payload = planned.payload
            sql_plan = _enrich_sql_plan(state, dict(payload.get("sql_plan") or {}))
            sql_plan.setdefault("strategy", "llm_text_to_sql")
            sql_plan.setdefault("matched_query_id", state.get("matched_query_id"))
            update = {
                "sql_plan": sql_plan,
                "confidence": planned.confidence,
                "llm_plan": planned.to_state(),
            }
            update.update(
                add_trace(
                    state,
                    "plan_sql",
                    message=f"Planned SQL with {planned.model}.",
                    confidence=planned.confidence,
                    referenced_context_ids=payload.get("referenced_context_ids", []),
                )
            )
            return update

        sql_plan = {
            "strategy": "deterministic_demo_sql",
            "matched_query_id": state.get("matched_query_id"),
            "tables": metadata.get("tables") or metadata.get("required_tables", []) or matched_demo_case.get("required_tables", []),
            "metrics": matched_demo_case.get("expected_metrics", []) or metadata.get("expected_metrics", []),
            "output_columns": (
                matched_demo_case.get("output_contract", {}).get("columns", [])
                or metadata.get("output_contract", {}).get("columns", [])
            ),
        }
        sql_plan = _enrich_sql_plan(state, sql_plan)
        update = {"sql_plan": sql_plan}
        update.update(add_trace(state, "plan_sql", message=f"Built {sql_plan['strategy']} plan."))
        return update

    return node


def generate_sql(
    repo: DemoCaseRepository,
    *,
    generator: TextToSqlGenerator | None = None,
    sql_mode: str = "demo",
):
    def node(state: AgentState) -> dict[str, Any]:
        if state.get("case_timed_out"):
            update = {"candidate_sql": state.get("candidate_sql", "")}
            update.update(
                add_trace(
                    state,
                    "generate_sql",
                    status="skipped",
                    message="Skipped because the case deadline was exceeded.",
                )
            )
            return update
        if sql_mode == "llm":
            if generator is None:
                update = {"candidate_sql": "", "llm_error": "LLM generator is not configured."}
                update.update(add_trace(state, "generate_sql", status="failed", message=update["llm_error"]))
                return update

            started_at = datetime.now(timezone.utc).isoformat()
            started_perf = time.perf_counter()
            _start_live_sql_attempt(
                state,
                attempt_type="initial",
                started_at=started_at,
            )
            try:
                generated = generator.generate_sql(
                    question=_question(state),
                    metadata_context=state.get("metadata_context", {}),
                    intent=state.get("intent", {}),
                    sql_plan=state.get("sql_plan", {}),
                )
            except LlmClientError as exc:
                update = {
                    "candidate_sql": "",
                    "llm_error": str(exc),
                    "case_timed_out": isinstance(exc, CaseDeadlineExceeded),
                    "sql_generation_attempts": _sql_generation_attempt(
                        state,
                        attempt_type="initial",
                        started_at=started_at,
                        started_perf=started_perf,
                        error=str(exc),
                    ),
                }
                update.update(add_trace(state, "generate_sql", status="failed", message=str(exc)))
                return update

            update = {
                "candidate_sql": generated.sql,
                "sql_plan": _enrich_sql_plan(state, dict(state.get("sql_plan", {}))),
                "confidence": generated.confidence,
                "llm_generation": generated.to_state(),
                "sql_generation_attempts": _sql_generation_attempt(
                    state,
                    attempt_type="initial",
                    started_at=started_at,
                    started_perf=started_perf,
                    generated=generated,
                ),
            }
            update.update(
                add_trace(
                    state,
                    "generate_sql",
                    message=f"Generated SQL with {generated.model}.",
                    confidence=generated.confidence,
                    sql_generation_elapsed_ms=round(generated.elapsed_ms, 4),
                )
            )
            return update

        case = repo.get(state["matched_query_id"])
        candidate_sql = _apply_followup_sql_patch(case.sql, state.get("followup_patch"))
        update = {"candidate_sql": candidate_sql}
        update.update(
            add_trace(
                state,
                "generate_sql",
                message=(
                    f"Loaded standard SQL for {case.query_id} and applied follow-up filter."
                    if state.get("followup_patch")
                    else f"Loaded standard SQL for {case.query_id}."
                ),
            )
        )
        return update

    return node


def validate_sql(state: AgentState) -> dict[str, Any]:
    sql = state.get("candidate_sql", "")
    executable_sql = _strip_leading_comments(sql)
    failures: list[str] = []
    warnings: list[str] = []
    referenced_tables: list[str] = []
    projection_details: dict[str, Any] = {}

    if not executable_sql:
        failures.append("SQL is empty.")
    if not re.match(r"^(select|with)\b", executable_sql, flags=re.IGNORECASE):
        failures.append("Only SELECT or WITH ... SELECT statements are allowed.")
    if DANGEROUS_SQL_PATTERN.search(executable_sql):
        failures.append("SQL contains a forbidden keyword.")
    if executable_sql:
        try:
            parsed_statements = sqlglot.parse(executable_sql, read="duckdb")
            if len(parsed_statements) != 1:
                failures.append("SQL must contain exactly one statement.")
            statement = parsed_statements[0] if parsed_statements else None
            if statement is None:
                raise ValueError("SQL parser returned an empty statement")

            unknown_tables, unknown_columns, referenced_tables = validate_scoped_metadata(statement)
            if unknown_tables:
                failures.append(f"SQL references unknown tables: {', '.join(unknown_tables)}.")
            if unknown_columns:
                failures.append(f"SQL references unknown columns: {', '.join(sorted(set(unknown_columns)))}.")

            sql_plan = state.get("sql_plan", {})
            snapshot_failures = validate_snapshot_dates(statement)
            snapshot_policy = dict(sql_plan.get("snapshot_policy") or {})
            configured_ranges = table_date_ranges()
            for table_name in referenced_tables:
                configured = configured_ranges.get(table_name, "")
                if re.fullmatch(r"\d{8}", configured):
                    snapshot_policy.setdefault(table_name, configured)
            snapshot_failures.extend(
                validate_snapshot_policy(
                    statement,
                    snapshot_policy,
                )
            )
            failures.extend(snapshot_failures)

            output_columns = output_columns_from_plan(sql_plan)
            projection_failures, projection_warnings, projection_details = validate_projection_contract(
                executable_sql,
                output_columns,
                allow_extra_columns=bool(sql_plan.get("allow_extra_columns", False)),
            )
            failures.extend(projection_failures)
            warnings.extend(projection_warnings)
            failures.extend(
                validate_dictionary_projection(
                    statement,
                    output_columns,
                    dictionary_translation=bool(sql_plan.get("dictionary_translation", False)),
                )
            )
            warnings.extend(
                unrequested_filter_warnings(
                    statement,
                    question=_question(state),
                    sql_plan=sql_plan,
                )
            )
            window_failures = validate_window_contract(statement, sql_plan.get("window"))
            join_failures = validate_join_contract(statement, sql_plan.get("join_contract"))
            fact_aggregation_failures = validate_fact_preaggregation(statement)
            missing_fact_failures = validate_missing_fact_policy(
                statement,
                sql_plan.get("missing_fact_policy"),
            )
            missing_period_failures = validate_missing_period_policy(
                statement,
                sql_plan.get("missing_period_policy"),
            )
            eligibility_failures = validate_eligibility_filters(
                statement,
                sql_plan.get("eligibility_filters"),
            )
            top_n_failures = validate_top_n_contract(
                statement,
                sql_plan.get("top_n"),
                sql_plan.get("window"),
            )
            failures.extend(window_failures)
            failures.extend(join_failures)
            failures.extend(fact_aggregation_failures)
            failures.extend(missing_fact_failures)
            failures.extend(missing_period_failures)
            failures.extend(eligibility_failures)
            failures.extend(top_n_failures)
            failures.extend(_metric_formula_failures(executable_sql, state, parsed_statements))
        except Exception as exc:
            failures.append(f"SQL syntax parse failed: {exc}.")

    passed = not failures
    metric_failures = [failure for failure in failures if failure.startswith("Metric formula mismatch")]
    snapshot_failures = [failure for failure in failures if failure.startswith("Snapshot ")]
    projection_failures = [failure for failure in failures if failure.startswith("Projection contract")]
    dictionary_failures = [failure for failure in failures if failure.startswith("Dictionary translation")]
    window_failures = [failure for failure in failures if failure.startswith("Window contract")]
    join_failures = [failure for failure in failures if failure.startswith("Join contract")]
    fact_aggregation_failures = [
        failure for failure in failures if failure.startswith("Fact aggregation contract")
    ]
    missing_fact_failures = [failure for failure in failures if failure.startswith("Missing fact policy")]
    missing_period_failures = [failure for failure in failures if failure.startswith("Missing period policy")]
    eligibility_failures = [failure for failure in failures if failure.startswith("Eligibility filter")]
    top_n_failures = [failure for failure in failures if failure.startswith("Top N contract")]
    validation_report = {
        "passed": passed,
        "checks": {
            "readonly": "failed" if any("Only SELECT" in failure or "forbidden keyword" in failure for failure in failures) else "passed",
            "basic_syntax": "failed" if any("syntax" in failure or "exactly one statement" in failure for failure in failures) else "passed",
            "metadata_whitelist": "failed" if any("unknown tables" in failure for failure in failures) else "passed",
            "field_whitelist": "failed" if any("unknown columns" in failure for failure in failures) else "passed",
            "metric_rules": "failed" if metric_failures else "passed",
            "snapshot_policy": "failed" if snapshot_failures else "passed",
            "projection_contract": "failed" if projection_failures else "passed",
            "dictionary_translation": "failed" if dictionary_failures else "passed",
            "window_contract": "failed" if window_failures else "passed",
            "join_contract": "failed" if join_failures else "passed",
            "fact_preaggregation": "failed" if fact_aggregation_failures else "passed",
            "missing_fact_policy": "failed" if missing_fact_failures else "passed",
            "missing_period_policy": "failed" if missing_period_failures else "passed",
            "eligibility_filters": "failed" if eligibility_failures else "passed",
            "top_n_contract": "failed" if top_n_failures else "passed",
        },
        "referenced_tables": referenced_tables,
        "projection": projection_details,
        "errors": failures,
        "warnings": _dedupe_text(warnings),
    }
    update = {"validation_report": validation_report, "confidence": 0.85 if passed else 0.2}
    attempts = list(state.get("sql_generation_attempts", []))
    if attempts:
        latest = dict(attempts[-1])
        latest["validation"] = {
            "passed": validation_report["passed"],
            "errors": list(validation_report["errors"]),
            "warnings": list(validation_report["warnings"]),
            "checks": dict(validation_report["checks"]),
        }
        attempts[-1] = latest
        update["sql_generation_attempts"] = attempts
    update.update(
        add_trace(
            state,
            "validate_sql",
            status="ok" if passed else "failed",
            message=(
                "SQL guardrail passed."
                + (f" Warnings: {'; '.join(_dedupe_text(warnings))}" if warnings else "")
                if passed
                else "; ".join(failures)
            ),
        )
    )
    return update


def execute_sql(executor: SqlExecutor, *, preview_limit: int = 20):
    def node(state: AgentState) -> dict[str, Any]:
        result = executor.execute(state.get("candidate_sql", ""), preview_limit=preview_limit)
        update = {"execution_result": result.to_state()}
        update.update(
            add_trace(
                state,
                "execute_sql",
                status="ok" if result.success else "failed",
                message=f"rows={result.row_count}, elapsed_ms={result.elapsed_ms:.2f}"
                if result.success
                else result.error,
            )
        )
        return update

    return node


def validate_result(state: AgentState) -> dict[str, Any]:
    result = state.get("execution_result", {})
    success = bool(result.get("success"))
    sql_plan = state.get("sql_plan", {})
    row_count = int(result.get("row_count", 0) or 0)
    errors: list[str] = []
    warnings: list[str] = []
    if not success:
        errors.append(str(result.get("error") or "SQL execution failed."))
    if success and row_count == 0:
        message = "Query returned zero rows."
        if bool(sql_plan.get("expect_nonempty")):
            errors.append(message)
        else:
            warnings.append(message)
    top_n = sql_plan.get("top_n")
    try:
        top_n_value = int(top_n) if top_n is not None else 0
    except (TypeError, ValueError):
        top_n_value = 0
    has_window_contract = any(
        isinstance(item, dict)
        for item in (sql_plan.get("window") or [])
    )
    if success and top_n_value > 0 and not has_window_contract and row_count > top_n_value:
        errors.append(
            f"Result row count {row_count} exceeds planned top_n={top_n_value}."
        )
    expected_columns = [
        str(item.get("alias") or item.get("name") or "")
        for item in output_columns_from_plan(sql_plan)
    ]
    actual_columns = [str(item) for item in result.get("columns", [])]
    if success and expected_columns and actual_columns != expected_columns:
        errors.append(
            f"Execution result columns do not satisfy output contract: "
            f"expected {expected_columns}, got {actual_columns}."
        )
    result_check = {
        "passed": success and not errors,
        "row_count": row_count,
        "empty_result": row_count == 0,
        "errors": errors,
        "warnings": warnings,
        "expected_columns": expected_columns,
        "actual_columns": actual_columns,
    }
    confidence = 0.90 if result_check["passed"] else 0.1
    update = {"result_check": result_check, "confidence": confidence}
    update.update(
        add_trace(
            state,
            "validate_result",
            status="ok" if result_check["passed"] else "failed",
            message=(
                "Result check passed."
                + (f" Warnings: {'; '.join(warnings)}" if warnings else "")
                if result_check["passed"]
                else "; ".join(errors)
            ),
        )
    )
    return update


def repair_sql(
    state: AgentState,
    *,
    generator: TextToSqlGenerator | None = None,
    sql_mode: str = "demo",
) -> dict[str, Any]:
    retry_count = int(state.get("retry_count", 0)) + 1

    if sql_mode == "llm" and generator is not None:
        started_at = datetime.now(timezone.utc).isoformat()
        started_perf = time.perf_counter()
        _start_live_sql_attempt(
            state,
            attempt_type="repair",
            started_at=started_at,
        )
        try:
            generated = generator.repair_sql(
                question=_question(state),
                metadata_context=state.get("metadata_context", {}),
                intent=state.get("intent", {}),
                sql_plan=state.get("sql_plan", {}),
                previous_sql=state.get("candidate_sql", ""),
                validation_report=state.get("validation_report", {}),
                execution_result=state.get("execution_result", {}),
                result_check=state.get("result_check", {}),
            )
        except LlmClientError as exc:
            update = {
                "retry_count": retry_count,
                "llm_error": str(exc),
                "case_timed_out": isinstance(exc, CaseDeadlineExceeded),
                "sql_generation_attempts": _sql_generation_attempt(
                    state,
                    attempt_type="repair",
                    started_at=started_at,
                    started_perf=started_perf,
                    error=str(exc),
                ),
            }
            update.update(add_trace(state, "repair_sql", status="failed", message=str(exc)))
            return update

        update = {
            "retry_count": retry_count,
            "candidate_sql": generated.sql,
            "sql_plan": _enrich_sql_plan(state, dict(state.get("sql_plan", {}))),
            "confidence": generated.confidence,
            "llm_repair": generated.to_state(),
            "sql_generation_attempts": _sql_generation_attempt(
                state,
                attempt_type="repair",
                started_at=started_at,
                started_perf=started_perf,
                generated=generated,
            ),
        }
        update.update(
            add_trace(
                state,
                "repair_sql",
                message=f"Repaired SQL with {generated.model}.",
                confidence=generated.confidence,
                sql_generation_elapsed_ms=round(generated.elapsed_ms, 4),
            )
        )
        return update

    update = {"retry_count": retry_count}
    update.update(add_trace(state, "repair_sql", status="skipped", message="M1 has no LLM repair path."))
    return update


def ask_clarification(state: AgentState) -> dict[str, Any]:
    missing = state.get("blocking_missing_slots", [])
    product_ambiguity = state.get("ambiguities", {}).get("product")
    if product_ambiguity:
        details = []
        for item in product_ambiguity:
            if isinstance(item, dict):
                details.append(f"{item.get('term')}: {item.get('message')}")
            else:
                details.append(str(item))
        answer = "产品名称存在歧义，请补充产品类别后再查询。" + (" " + "；".join(details) if details else "")
        update = {"final_answer": answer}
        update.update(add_trace(state, "ask_clarification", status="blocked", message=answer))
        return update

    answer = "需要补充以下会影响查询口径的信息后才能继续："
    answer += f"{'; '.join(missing)}" if missing else "请明确查询目标、关键实体或时间范围。"
    update = {"final_answer": answer}
    update.update(add_trace(state, "ask_clarification", status="blocked", message=answer))
    return update


def human_review_or_explain(state: AgentState) -> dict[str, Any]:
    if state.get("case_timed_out"):
        timeout_seconds = float(state.get("case_timeout_seconds", 0.0) or 0.0)
        answer = f"查询在 {timeout_seconds:.2f} 秒单题时限内未完成，已终止本题并记录为 case_timeout。"
        update = {"final_answer": answer}
        update.update(
            add_trace(
                state,
                "human_review_or_explain",
                status="timeout",
                message=answer,
            )
        )
        return update
    llm_error = str(state.get("llm_error") or "").strip()
    if llm_error and not str(state.get("candidate_sql") or "").strip():
        answer = f"LLM 未能生成 SQL，数据库未执行。原因：{llm_error}"
        update = {"final_answer": answer}
        update.update(
            add_trace(
                state,
                "human_review_or_explain",
                status="failed",
                message=answer,
            )
        )
        return update
    validation = state.get("validation_report", {})
    execution = state.get("execution_result", {})
    result_check = state.get("result_check", {})
    errors = (
        validation.get("errors")
        or result_check.get("errors")
        or [execution.get("error", "Unknown error")]
    )
    answer = "查询未能自动完成，已进入人工复核路径。原因：" + "; ".join(str(item) for item in errors if item)
    update = {"final_answer": answer}
    update.update(add_trace(state, "human_review_or_explain", status="failed", message=answer))
    return update


def _deterministic_answer(state: AgentState) -> str:
    result = state.get("execution_result", {})
    metadata = state.get("metadata_context", {})
    query_id = state.get("matched_query_id", "")
    if query_id:
        return (
            f"查询成功。匹配样例：{query_id}；场景：{metadata.get('scenario', '')}；"
            f"返回 {result.get('row_count', 0)} 行；执行耗时 {result.get('elapsed_ms', 0):.2f} ms。"
        )
    return (
        "查询成功。自然语言问题已通过 LLM Text-to-SQL 路径生成并执行；"
        f"返回 {result.get('row_count', 0)} 行；执行耗时 {result.get('elapsed_ms', 0):.2f} ms。"
    )


def render_answer(
    *,
    generator: TextToSqlGenerator | None = None,
    sql_mode: str = "demo",
):
    def node(state: AgentState) -> dict[str, Any]:
        if sql_mode == "llm" and generator is not None:
            try:
                explained = generator.explain_result(
                    question=_question(state),
                    sql_plan=state.get("sql_plan", {}),
                    sql=state.get("candidate_sql", ""),
                    execution_result=state.get("execution_result", {}),
                    result_check=state.get("result_check", {}),
                )
            except LlmClientError as exc:
                answer = _deterministic_answer(state)
                update = {
                    "final_answer": answer,
                    "llm_error": str(exc),
                    "case_timed_out": isinstance(exc, CaseDeadlineExceeded),
                }
                update.update(add_trace(state, "render_answer", status="fallback", message=f"LLM explanation failed: {exc}"))
                return update

            payload = explained.payload
            answer = str(payload.get("final_answer") or _deterministic_answer(state))
            result_explanation = {
                "warnings": [str(item) for item in _as_list(payload.get("warnings"))],
                "confidence": explained.confidence,
            }
            update = {
                "final_answer": answer,
                "result_explanation": result_explanation,
                "confidence": max(float(state.get("confidence", 0.0)), explained.confidence),
                "llm_result_explanation": explained.to_state(),
            }
            update.update(
                add_trace(
                    state,
                    "render_answer",
                    message=f"Rendered final answer with {explained.model}.",
                    confidence=explained.confidence,
                )
            )
            return update

        answer = _deterministic_answer(state)
        update = {"final_answer": answer}
        update.update(add_trace(state, "render_answer", message="Rendered final answer."))
        return update

    return node


def persist_state(state: AgentState) -> dict[str, Any]:
    summary = {
        "last_query_id": state.get("matched_query_id"),
        "last_question": state.get("question"),
        "last_intent": state.get("intent", {}),
        "last_sql_plan": state.get("sql_plan", {}),
        "last_sql": state.get("candidate_sql", ""),
        "last_followup_patch": state.get("followup_patch", {}),
        "last_context_ids": state.get("context_ids", []),
        "last_result": {
            "row_count": state.get("execution_result", {}).get("row_count"),
            "columns": state.get("execution_result", {}).get("columns", []),
        },
    }
    update = {"thread_summary": summary}
    update.update(add_trace(state, "persist_state", message="Persisted in-memory summary for M1."))
    return update
