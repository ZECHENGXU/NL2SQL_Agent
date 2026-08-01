from __future__ import annotations

import re
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from typing import Any

import sqlglot
import yaml
from sqlglot import exp
from sqlglot.optimizer.scope import Scope, build_scope, traverse_scope


PACKAGE_DIR = Path(__file__).resolve().parents[1]
SCHEMA_CATALOG_PATH = PACKAGE_DIR / "metadata" / "schema_catalog.yaml"

ORDER_MARKERS = (
    "排序",
    "排名",
    "从高到低",
    "从低到高",
    "倒序",
    "降序",
    "升序",
    "依次",
    "最高",
    "最低",
    "前",
    "top",
    "rank",
)

EXPLICIT_COLUMN_ALIASES = {
    "cust_count": "customer_count",
    "cust_cnt": "customer_count",
    "fund_cust_cnt": "fund_customer_count",
    "active_cust_cnt": "active_customer_count",
    "tran_cust_cnt": "trading_customer_count",
    "hold_cust_cnt": "holder_count",
    "cust_lvl_name": "customer_level",
    "cust_lvl_cd": "customer_level",
    "edu_cd": "education",
    "ccy": "currency_name",
    "total_mkt_val": "total_market_value",
    "holding_mkt_val": "holding_market_value",
    "hold_mkt_val": "market_value",
    "end_mkt_val": "end_holding_value",
    "end_hold_value": "end_holding_value",
    "prod_count": "holding_product_count",
    "total_trade_amt": "turnover",
    "total_tran_amt": "turnover",
    "q1_trade_amt": "turnover",
    "q1_transaction_amount": "turnover",
    "transaction_amount_q1": "turnover",
    "total_buy_amt": "total_buy_amount",
    "total_sell_amt": "total_sell_amount",
    "buy_amt": "buy_amount",
    "sell_amt": "sell_amount",
    "net_buy_amt": "net_buy_amount",
    "fund_mkt_val": "fund_market_value",
    "fund_mkv": "fund_market_value",
    "stock_mkv": "stock_market_value",
    "stddev_asset": "asset_stddev",
    "cv": "asset_cv",
    "active_rate": "active_customer_rate",
    "avg_daily_asset": "avg_daily_asset",
    "begin_total_asset": "begin_asset",
    "end_total_asset": "end_asset",
    "init_etf_mktval": "begin_etf_value",
    "etf_buy_amt": "etf_buy_amount",
    "etf_sell_amt": "etf_sell_amount",
    "customer_id": "pty_id",
    "customer_name": "name",
    "branch_company": "up_org_name",
    "branch_name": "org_name",
    "asset_tier": "asset_band",
}

TOKEN_ALIASES = {
    "amt": "amount",
    "aset": "asset",
    "avg": "average",
    "cnt": "count",
    "cust": "customer",
    "fin": "fund",
    "hold": "holding",
    "mkt": "market",
    "mkv": "market_value",
    "nm": "normal",
    "prdt": "product",
    "prod": "product",
    "q1": "",
    "tran": "transaction",
    "val": "value",
}

CODE_OUTPUT_FIELDS = {"cust_lvl_cd", "gender_cd", "edu_cd", "ccy"}
TRANSLATED_OUTPUTS = {"customer_level", "gender_name", "education", "currency_name"}
WINDOW_FUNCTION_NAMES = {
    "rownumber": "row_number",
    "denserank": "dense_rank",
    "percentrank": "percent_rank",
    "lag": "lag",
    "lead": "lead",
    "ntile": "ntile",
    "rank": "rank",
}
SQL_KEYWORDS = {
    "and",
    "asc",
    "between",
    "by",
    "case",
    "desc",
    "else",
    "end",
    "from",
    "in",
    "is",
    "not",
    "null",
    "or",
    "over",
    "partition",
    "then",
    "when",
}
MULTIROW_FACT_TABLES = {
    "dwd_cust_tran_d",
    "dws_cust_fin_d",
    "dwd_cust_hold_d",
}


@lru_cache(maxsize=1)
def schema_catalog() -> dict[str, Any]:
    return yaml.safe_load(SCHEMA_CATALOG_PATH.read_text(encoding="utf-8")) or {}


@lru_cache(maxsize=1)
def known_columns_by_table() -> dict[str, set[str]]:
    return {
        table_name: set(table.get("columns", {}).keys())
        for table_name, table in schema_catalog().get("tables", {}).items()
    }


@lru_cache(maxsize=1)
def table_date_ranges() -> dict[str, str]:
    return {
        table_name: str(table.get("data_date_range") or "")
        for table_name, table in schema_catalog().get("tables", {}).items()
        if table.get("data_date_range")
    }


def canonical_column_name(name: str) -> str:
    normalized = re.sub(r"[^a-z0-9_]+", "_", str(name).strip().lower()).strip("_")
    if normalized in EXPLICIT_COLUMN_ALIASES:
        return EXPLICIT_COLUMN_ALIASES[normalized]
    tokens: list[str] = []
    for token in normalized.split("_"):
        replacement = TOKEN_ALIASES.get(token, token)
        if not replacement:
            continue
        tokens.extend(part for part in replacement.split("_") if part)
    canonical = "_".join(tokens)
    return EXPLICIT_COLUMN_ALIASES.get(canonical, canonical)


def column_similarity(expected: str, actual: str) -> float:
    left = canonical_column_name(expected)
    right = canonical_column_name(actual)
    if left == right:
        return 1.0
    left_tokens = set(left.split("_"))
    right_tokens = set(right.split("_"))
    token_score = len(left_tokens & right_tokens) / max(len(left_tokens | right_tokens), 1)
    sequence_score = SequenceMatcher(None, left, right).ratio()
    suffix_bonus = 0.15 if left.endswith(right) or right.endswith(left) else 0.0
    return min(1.0, max(token_score, sequence_score * 0.85) + suffix_bonus)


def infer_order_sensitive(question: str) -> bool:
    lowered = question.lower()
    if re.search(r"(?:前|top\s*)\d+", lowered):
        return True
    return any(marker in lowered for marker in ORDER_MARKERS)


def infer_semantic_type(alias: str) -> str:
    return canonical_column_name(alias)


def numeric_tolerance_for(alias: str) -> dict[str, float]:
    canonical = canonical_column_name(alias)
    if any(token in canonical for token in ("ratio", "rate", "average", "avg", "stddev", "cv")):
        return {"atol": 1e-7, "rtol": 1e-6}
    return {"atol": 1e-8, "rtol": 1e-9}


def derive_output_contract(
    sql: str,
    *,
    question: str = "",
    override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    override = dict(override or {})
    column_overrides = dict(override.pop("column_overrides", {}) or {})
    names = projection_names(sql)
    columns = [
        {
            "name": name,
            "alias": name,
            "semantic_type": infer_semantic_type(name),
            "required": True,
            "position": index + 1,
            "alias_strict": bool(override.get("alias_strict", False)),
            "numeric_tolerance": numeric_tolerance_for(name),
        }
        for index, name in enumerate(names)
    ]
    contract: dict[str, Any] = {
        "columns": columns,
        "order_sensitive": infer_order_sensitive(question),
        "allow_extra_columns": False,
        "dictionary_translation": any(
            column["semantic_type"] in TRANSLATED_OUTPUTS for column in columns
        ),
        "null_policy": {},
        "missing_fact_policy": {},
        "snapshot_policy": {},
        "accepted_alternatives": [],
    }
    for column in columns:
        updates = column_overrides.get(column["alias"]) or column_overrides.get(column["name"])
        if isinstance(updates, dict):
            column.update(updates)
    for key, value in override.items():
        if key == "columns" and value:
            contract["columns"] = normalize_output_columns(value)
        else:
            contract[key] = value
    return contract


def derive_window_contract(sql: str) -> list[dict[str, Any]]:
    if not sql.strip():
        return []
    try:
        expression = sqlglot.parse_one(sql, read="duckdb")
    except Exception:
        return []
    contracts: list[dict[str, Any]] = []
    for window in expression.find_all(exp.Window):
        order = window.args.get("order")
        contracts.append(
            {
                "function": _window_function(window),
                "partition_by": [
                    item.sql(dialect="duckdb")
                    for item in window.args.get("partition_by") or []
                ],
                "order_by": [
                    {
                        "expression": item.this.sql(dialect="duckdb"),
                        "direction": "desc" if item.args.get("desc") else "asc",
                    }
                    for item in order.expressions
                ]
                if isinstance(order, exp.Order)
                else [],
                "tie_breaker": [],
            }
        )
    return contracts


def infer_top_n(question: str) -> int | None:
    match = re.search(r"(?:前|top\s*)(\d+)", question.lower())
    return int(match.group(1)) if match else None


def derive_join_contract(sql: str) -> list[dict[str, str]]:
    if not sql.strip():
        return []
    try:
        expression = sqlglot.parse_one(sql, read="duckdb")
    except Exception:
        return []
    contracts: list[dict[str, str]] = []
    physical_tables = set(known_columns_by_table())
    for join in expression.find_all(exp.Join):
        if not isinstance(join.this, exp.Table) or join.this.name not in physical_tables:
            continue
        contracts.append(
            {
                "table": join.this.name,
                "join_type": _join_type(join),
            }
        )
    return contracts


def normalize_output_columns(value: Any) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    seen_aliases: set[str] = set()
    for index, item in enumerate(value or []):
        if isinstance(item, str):
            name = item
            normalized = {
                "name": name,
                "alias": name,
                "semantic_type": infer_semantic_type(name),
                "required": True,
                "position": index + 1,
                "alias_strict": False,
                "numeric_tolerance": numeric_tolerance_for(name),
            }
        elif isinstance(item, dict):
            normalized = dict(item)
            name = str(normalized.get("name") or normalized.get("alias") or normalized.get("expression") or "")
            if not name:
                continue
            normalized.setdefault("name", name)
            normalized.setdefault("alias", normalized["name"])
            normalized.setdefault("semantic_type", infer_semantic_type(str(normalized["alias"])))
            normalized.setdefault("required", True)
            normalized.setdefault("position", index + 1)
            normalized.setdefault("alias_strict", False)
            normalized.setdefault(
                "numeric_tolerance",
                numeric_tolerance_for(str(normalized["alias"])),
            )
        else:
            continue
        alias_key = str(normalized.get("alias") or normalized.get("name") or "").strip().lower()
        if not alias_key or alias_key in seen_aliases:
            continue
        seen_aliases.add(alias_key)
        normalized["position"] = len(output) + 1
        output.append(normalized)
    return output


def output_columns_from_plan(sql_plan: dict[str, Any]) -> list[dict[str, Any]]:
    return normalize_output_columns(sql_plan.get("output_columns") or [])


def projection_names(sql: str) -> list[str]:
    if not sql.strip():
        return []
    try:
        expression = sqlglot.parse_one(sql, read="duckdb")
    except Exception:
        return []
    return projection_names_from_expression(expression)


def projection_names_from_expression(expression: exp.Expression) -> list[str]:
    scope = build_scope(expression)
    if scope is None:
        return list(expression.named_selects)
    return _scope_projection_names(scope)


def _scope_projection_names(scope: Scope) -> list[str]:
    expression = scope.expression
    if not isinstance(expression, exp.Select):
        return list(expression.named_selects)
    output: list[str] = []
    for selected in expression.selects:
        if isinstance(selected, exp.Star):
            for _, source in scope.selected_sources.values():
                output.extend(_source_projection_names(source))
            continue
        if isinstance(selected, exp.Column) and isinstance(selected.this, exp.Star):
            source_pair = scope.selected_sources.get(selected.table)
            if source_pair:
                output.extend(_source_projection_names(source_pair[1]))
            continue
        name = selected.alias_or_name
        if name:
            output.append(name)
    return output


def _source_projection_names(source: Any) -> list[str]:
    if isinstance(source, Scope):
        return _scope_projection_names(source)
    if isinstance(source, exp.Table):
        return sorted(known_columns_by_table().get(source.name, set()))
    return []


def align_columns(expected: list[str], actual: list[str]) -> tuple[list[int | None], list[int]]:
    available = set(range(len(actual)))
    mapping: list[int | None] = []
    for position, expected_name in enumerate(expected):
        ranked = sorted(
            (
                (column_similarity(expected_name, actual[index]), index)
                for index in available
            ),
            reverse=True,
        )
        best_score, best_index = ranked[0] if ranked else (0.0, -1)
        if best_score >= 0.58:
            mapping.append(best_index)
            available.remove(best_index)
        elif position in available and len(expected) == len(actual):
            mapping.append(position)
            available.remove(position)
        else:
            mapping.append(None)
    return mapping, sorted(available)


def validate_projection_contract(
    sql: str,
    output_columns: list[dict[str, Any]],
    *,
    allow_extra_columns: bool = False,
) -> tuple[list[str], list[str], dict[str, Any]]:
    expected = [str(item.get("alias") or item.get("name") or "") for item in output_columns]
    expected = [item for item in expected if item]
    actual = projection_names(sql)
    if not expected:
        return [], [], {"expected": [], "actual": actual}

    missing = [name for name in expected if name not in actual]
    extra = [name for name in actual if name not in expected]
    wrong_order = not missing and not extra and actual != expected
    errors: list[str] = []
    if missing:
        errors.append(f"Projection contract missing columns: {', '.join(missing)}.")
    if extra and not allow_extra_columns:
        errors.append(f"Projection contract has extra columns: {', '.join(extra)}.")
    if wrong_order:
        errors.append(
            "Projection contract column order mismatch: "
            f"expected {expected}, got {actual}."
        )
    details = {
        "expected": expected,
        "actual": actual,
        "missing": missing,
        "extra": extra,
        "wrong_order": wrong_order,
    }
    return errors, [], details


def validate_scoped_metadata(
    expression: exp.Expression,
) -> tuple[list[str], list[str], list[str]]:
    columns_by_table = known_columns_by_table()
    known_tables = set(columns_by_table)
    unknown_tables: set[str] = set()
    unknown_columns: set[str] = set()
    referenced_tables: set[str] = set()

    for scope in traverse_scope(expression):
        for _, source in scope.selected_sources.values():
            if isinstance(source, exp.Table):
                table_name = source.name
                if table_name in known_tables:
                    referenced_tables.add(table_name)
                else:
                    unknown_tables.add(table_name)

        for column in scope.columns:
            selected_source = _selected_source_for_column(scope, column)
            if selected_source is None:
                continue
            source = selected_source[1]
            if isinstance(source, exp.Table):
                table_name = source.name
                if table_name in known_tables and column.name not in columns_by_table[table_name]:
                    qualifier = column.table or table_name
                    unknown_columns.add(f"{qualifier}.{column.name}")
            elif isinstance(source, Scope):
                available = set(_scope_projection_names(source))
                if column.name not in available:
                    unknown_columns.add(f"{column.table}.{column.name}")

    return sorted(unknown_tables), sorted(unknown_columns), sorted(referenced_tables)


def _selected_source_for_column(
    scope: Scope,
    column: exp.Column,
) -> tuple[exp.Expression, Any] | None:
    if column.table:
        return scope.selected_sources.get(column.table)
    physical_sources = [
        selected
        for selected in scope.selected_sources.values()
        if isinstance(selected[1], exp.Table)
    ]
    return physical_sources[0] if len(physical_sources) == 1 else None


def validate_snapshot_dates(expression: exp.Expression) -> list[str]:
    failures: set[str] = set()
    ranges = table_date_ranges()
    for scope in traverse_scope(expression):
        for column in scope.columns:
            if column.name != "data_dt":
                continue
            selected_source = _selected_source_for_column(scope, column)
            if selected_source is None or not isinstance(selected_source[1], exp.Table):
                continue
            table_name = selected_source[1].name
            allowed = ranges.get(table_name)
            if not allowed:
                continue
            predicate = _date_predicate_ancestor(column, scope.expression)
            if predicate is None:
                continue
            dates = {
                str(literal.this)
                for literal in predicate.find_all(exp.Literal)
                if literal.is_string and re.fullmatch(r"\d{8}", str(literal.this))
            }
            if dates and not _predicate_overlaps_date_range(predicate, sorted(dates), allowed):
                failures.add(
                    f"Snapshot predicate {predicate.sql(dialect='duckdb')} does not overlap "
                    f"{table_name}.data_dt range {allowed}."
                )
    return sorted(failures)


def validate_snapshot_policy(
    expression: exp.Expression,
    snapshot_policy: dict[str, Any],
) -> list[str]:
    failures: set[str] = set()
    known_columns = known_columns_by_table()
    for table_name, configured in (snapshot_policy or {}).items():
        table_name = str(table_name)
        if "data_dt" not in known_columns.get(table_name, set()):
            continue
        expected_dates = re.findall(r"\b\d{8}\b", str(configured))
        if not expected_dates:
            continue
        matched_source = False
        for scope in traverse_scope(expression):
            for alias, (_, source) in scope.selected_sources.items():
                if not isinstance(source, exp.Table) or source.name != table_name:
                    continue
                matched_source = True
                predicates: list[exp.Expression] = []
                for column in scope.columns:
                    if column.name != "data_dt":
                        continue
                    selected = _selected_source_for_column(scope, column)
                    if selected is None or selected[1] is not source:
                        continue
                    predicate = _date_predicate_ancestor(column, scope.expression)
                    if predicate is not None:
                        predicates.append(predicate)
                if not predicates:
                    failures.add(
                        f"Snapshot policy requires {table_name} ({alias}).data_dt = {configured}, "
                        "but no date predicate was found."
                    )
                    continue
                actual_dates = {
                    str(literal.this)
                    for predicate in predicates
                    for literal in predicate.find_all(exp.Literal)
                    if literal.is_string and re.fullmatch(r"\d{8}", str(literal.this))
                }
                if len(expected_dates) == 1 and actual_dates != {expected_dates[0]}:
                    failures.add(
                        f"Snapshot policy for {table_name} expects {expected_dates[0]}, "
                        f"but SQL uses {sorted(actual_dates) or ['no literal date']}."
                    )
                elif len(expected_dates) >= 2:
                    expected_bounds = {min(expected_dates), max(expected_dates)}
                    if not expected_bounds.issubset(actual_dates):
                        failures.add(
                            f"Snapshot policy for {table_name} expects range "
                            f"{min(expected_dates)}-{max(expected_dates)}, but SQL uses "
                            f"{sorted(actual_dates) or ['no literal date']}."
                        )
        if not matched_source:
            continue
    return sorted(failures)


def validate_window_contract(
    expression: exp.Expression,
    window_contract: Any,
) -> list[str]:
    expected_windows = (
        list(window_contract)
        if isinstance(window_contract, list)
        else [window_contract]
        if isinstance(window_contract, dict)
        else []
    )
    expected_windows = [item for item in expected_windows if isinstance(item, dict)]
    if not expected_windows:
        return []

    actual_windows = list(expression.find_all(exp.Window))
    failures: list[str] = []
    for expected in expected_windows:
        expected_function = _normalize_window_function(expected.get("function"))
        candidates = [
            window
            for window in actual_windows
            if not expected_function or _window_function(window) == expected_function
        ]
        if not candidates:
            failures.append(
                f"Window contract requires {expected_function or 'a window function'}, but SQL has no matching window."
            )
            continue

        matched = False
        mismatch_details: list[str] = []
        for window in candidates:
            details = _window_contract_mismatches(window, expected)
            if not details:
                matched = True
                break
            mismatch_details.extend(details)
        if not matched:
            failures.append(
                f"Window contract mismatch for {expected_function or 'window'}: "
                + "; ".join(dict.fromkeys(mismatch_details))
                + "."
            )
    return failures


def validate_join_contract(
    expression: exp.Expression,
    join_contract: Any,
) -> list[str]:
    expected = join_contract if isinstance(join_contract, list) else []
    if not expected:
        return []
    actual: dict[str, list[str]] = {}
    for scope in traverse_scope(expression):
        for join in scope.expression.args.get("joins") or []:
            alias = str(join.this.alias_or_name or "")
            selected = scope.selected_sources.get(alias)
            source = selected[1] if selected else join.this
            physical_tables = _physical_tables_in_source(source)
            if len(physical_tables) != 1:
                continue
            table = next(iter(physical_tables))
            actual.setdefault(table, []).append(_join_type(join))
    failures: list[str] = []
    for item in expected:
        if not isinstance(item, dict):
            continue
        table = str(item.get("table") or "")
        expected_type = str(item.get("join_type") or "inner").lower()
        if not table:
            continue
        actual_types = actual.get(table, [])
        if expected_type not in actual_types:
            failures.append(
                f"Join contract requires {expected_type.upper()} JOIN {table}, "
                f"but SQL uses {actual_types or ['no physical join']}."
            )
    return failures


def _physical_tables_in_source(source: Any) -> set[str]:
    if isinstance(source, exp.Table):
        return {source.name} if source.name in known_columns_by_table() else set()
    if not isinstance(source, Scope):
        return set()
    tables: set[str] = set()
    for _, nested_source in source.selected_sources.values():
        tables.update(_physical_tables_in_source(nested_source))
    return tables


def validate_fact_preaggregation(expression: exp.Expression) -> list[str]:
    failures: list[str] = []
    for scope in traverse_scope(expression):
        physical_facts = {
            source.name
            for _, source in scope.selected_sources.values()
            if isinstance(source, exp.Table) and source.name in MULTIROW_FACT_TABLES
        }
        if len(physical_facts) >= 2:
            failures.append(
                "Fact aggregation contract requires customer-level pre-aggregation before joining "
                f"multiple fact tables; the same SQL scope joins {', '.join(sorted(physical_facts))}."
            )
    return failures


def validate_missing_fact_policy(
    expression: exp.Expression,
    missing_fact_policy: Any,
) -> list[str]:
    if not isinstance(missing_fact_policy, dict) or not missing_fact_policy:
        return []
    outer_aliases = _outer_join_aliases(expression)
    failures: list[str] = []
    for fact_name, raw_policy in missing_fact_policy.items():
        policy, sources = _normalize_fact_policy(raw_policy)
        if policy not in {"require_record", "zero_fill_after_aggregation"}:
            continue
        signals = _expression_tokens(str(fact_name))
        for source in sources:
            signals.update(_expression_tokens(source))
        if not signals:
            continue

        matching_aliases = {
            alias
            for alias in outer_aliases
            if _outer_alias_matches_policy(expression, alias, signals)
        }
        zero_fills = [
            coalesce
            for coalesce in expression.find_all(exp.Coalesce)
            if _coalesce_is_zero_fill(coalesce)
            and any(
                column.table in outer_aliases
                and _column_matches_policy(column, signals)
                for column in coalesce.find_all(exp.Column)
            )
        ]
        if policy == "require_record":
            if matching_aliases:
                failures.append(
                    f"Missing fact policy requires a record for {fact_name}, but source(s) "
                    f"{', '.join(sorted(matching_aliases))} are outer-joined."
                )
            if zero_fills:
                failures.append(
                    f"Missing fact policy requires a record for {fact_name}; SQL zero-fills a missing outer-joined fact."
                )
        elif not zero_fills:
            failures.append(
                f"Missing fact policy requires zero_fill_after_aggregation for {fact_name}, "
                "but no matching post-aggregation zero fill was found."
            )
    return list(dict.fromkeys(failures))


def validate_missing_period_policy(
    expression: exp.Expression,
    missing_period_policy: Any,
) -> list[str]:
    if isinstance(missing_period_policy, dict):
        policy = str(missing_period_policy.get("policy") or "").lower()
    else:
        policy = str(missing_period_policy or "").lower()
    if policy not in {"exclude", "zero_fill"}:
        return []

    sql = expression.sql(dialect="duckdb").lower()
    has_period_literal = bool(re.search(r"['\"]20\d{4}(?:\d{2})?['\"]", sql))
    has_scaffold = bool(
        re.search(r"\bgenerate_series\s*\(|\bvalues\s*\(", sql)
        or ("cross join" in sql and has_period_literal)
    )
    has_full_outer = any(
        join.side.upper() == "FULL" for join in expression.find_all(exp.Join)
    )
    has_zero_fill = any(_coalesce_is_zero_fill(item) for item in expression.find_all(exp.Coalesce))
    if policy == "exclude" and has_scaffold:
        return [
            "Missing period policy is exclude, but SQL creates a period scaffold that can fabricate absent periods."
        ]
    if policy == "zero_fill" and not (has_scaffold or (has_full_outer and has_zero_fill)):
        return [
            "Missing period policy is zero_fill, but SQL has no period scaffold or full-outer zero-fill strategy."
        ]
    return []


def validate_eligibility_filters(
    expression: exp.Expression,
    eligibility_filters: Any,
) -> list[str]:
    filters = eligibility_filters if isinstance(eligibility_filters, list) else []
    if not filters:
        return []
    comparisons = [
        item
        for item in expression.walk()
        if isinstance(item, (exp.EQ, exp.NEQ, exp.GT, exp.GTE, exp.LT, exp.LTE))
        and item.find_ancestor(exp.Where, exp.Having, exp.Qualify) is not None
    ]
    failures: list[str] = []
    for raw_filter in filters:
        filter_text = str(
            raw_filter.get("expression") if isinstance(raw_filter, dict) else raw_filter
        ).strip()
        signature = _comparison_signature(filter_text)
        if signature is None:
            continue
        expected_operator, expected_literal, expected_tokens = signature
        if not any(
            _comparison_matches_contract(
                comparison,
                expected_operator=expected_operator,
                expected_literal=expected_literal,
                expected_tokens=expected_tokens,
                expression=expression,
            )
            for comparison in comparisons
        ):
            failures.append(f"Eligibility filter is not enforced before ranking/aggregation: {filter_text}.")
    return failures


def validate_top_n_contract(
    expression: exp.Expression,
    top_n: Any,
    window_contract: Any,
) -> list[str]:
    value = top_n.get("value") if isinstance(top_n, dict) else top_n
    match = re.search(r"\d+", str(value or ""))
    if not match:
        return []
    expected_n = int(match.group())
    expected_windows = window_contract if isinstance(window_contract, list) else [window_contract]
    is_partitioned = any(
        isinstance(item, dict)
        and item.get("partition_by")
        and _normalize_window_function(item.get("function"))
        in {"row_number", "rank", "dense_rank", "ntile"}
        for item in expected_windows
    )
    rank_aliases = {
        selected.alias
        for selected in expression.find_all(exp.Alias)
        if isinstance(selected.this, exp.Window) and selected.alias
    }
    has_rank_bound = False
    for comparison in expression.find_all(exp.LT, exp.LTE):
        columns = {column.name for column in comparison.find_all(exp.Column)}
        literals = [
            int(str(item.this))
            for item in comparison.find_all(exp.Literal)
            if not item.is_string and str(item.this).isdigit()
        ]
        if (columns & rank_aliases or comparison.find(exp.Window)) and literals:
            bound = min(literals)
            has_rank_bound = bound <= expected_n if isinstance(comparison, exp.LTE) else bound <= expected_n + 1
            if has_rank_bound:
                break
    limit_values = [
        int(str(item.this))
        for limit in expression.find_all(exp.Limit)
        for item in limit.find_all(exp.Literal)
        if not item.is_string and str(item.this).isdigit()
    ]
    has_global_limit = bool(limit_values and min(limit_values) <= expected_n)
    if is_partitioned and not has_rank_bound:
        return [f"Top N contract requires a per-partition rank bound of {expected_n}, but none was found."]
    if not is_partitioned and not (has_rank_bound or has_global_limit):
        return [f"Top N contract requires a rank bound or LIMIT of {expected_n}, but none was found."]
    return []


def _normalize_window_function(value: Any) -> str:
    compact = re.sub(r"[^a-z]", "", str(value or "").lower())
    return WINDOW_FUNCTION_NAMES.get(compact, str(value or "").lower())


def _join_type(join: exp.Join) -> str:
    side = join.side.lower()
    kind = join.kind.lower()
    if side:
        return side
    if kind == "cross":
        return "cross"
    return "inner"


def _window_function(window: exp.Window) -> str:
    return WINDOW_FUNCTION_NAMES.get(str(window.this.key).lower(), str(window.this.key).lower())


def _window_contract_mismatches(window: exp.Window, expected: dict[str, Any]) -> list[str]:
    mismatches: list[str] = []
    actual_partitions = list(window.args.get("partition_by") or [])
    expected_partitions = list(expected.get("partition_by") or [])
    for item in expected_partitions:
        if not any(_expressions_match(item, actual) for actual in actual_partitions):
            mismatches.append(f"missing partition key {item}")

    order = window.args.get("order")
    actual_orders = list(order.expressions) if isinstance(order, exp.Order) else []
    expected_orders = list(expected.get("order_by") or [])
    for item in expected_orders:
        expected_expression, expected_direction = _normalize_order_contract(item)
        matching = [actual for actual in actual_orders if _expressions_match(expected_expression, actual.this)]
        if not matching:
            mismatches.append(f"missing order key {expected_expression}")
            continue
        actual_direction = "desc" if bool(matching[0].args.get("desc")) else "asc"
        if expected_direction and actual_direction != expected_direction:
            mismatches.append(
                f"order direction for {expected_expression} is {actual_direction}, expected {expected_direction}"
            )

    for tie_breaker in expected.get("tie_breaker") or []:
        if not any(_expressions_match(tie_breaker, actual.this) for actual in actual_orders):
            mismatches.append(f"missing tie breaker {tie_breaker}")
    return mismatches


def _normalize_order_contract(value: Any) -> tuple[str, str]:
    if isinstance(value, dict):
        return (
            str(value.get("expression") or value.get("field") or ""),
            str(value.get("direction") or "").lower(),
        )
    text = str(value or "").strip()
    match = re.search(r"\s+(asc|desc)\s*$", text, flags=re.IGNORECASE)
    if not match:
        return text, ""
    return text[: match.start()].strip(), match.group(1).lower()


def _expressions_match(expected: Any, actual: Any) -> bool:
    expected_text = str(expected)
    actual_sql = actual.sql(dialect="duckdb") if isinstance(actual, exp.Expression) else str(actual)
    expected_names = _identifier_names(expected_text)
    actual_names = _identifier_names(actual_sql)
    if expected_names and expected_names.issubset(actual_names):
        return True
    if len(expected_names) == 1:
        return False
    expected_tokens = _expression_tokens(expected_text)
    actual_tokens = _expression_tokens(actual_sql)
    if not expected_tokens:
        return re.sub(r"\s+", "", str(expected).lower()) == re.sub(r"\s+", "", actual_sql.lower())
    return expected_tokens.issubset(actual_tokens)


def _identifier_names(value: str) -> set[str]:
    return {
        canonical_column_name(raw)
        for raw in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", value.lower())
        if raw not in SQL_KEYWORDS
    }


def _expression_tokens(value: str) -> set[str]:
    tokens: set[str] = set()
    for raw in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", value.lower()):
        if raw in SQL_KEYWORDS:
            continue
        canonical = canonical_column_name(raw)
        if not canonical:
            continue
        tokens.add(canonical)
        tokens.update(part for part in canonical.split("_") if part)
    synonym_groups = (
        {"trade", "transaction", "turnover", "tran"},
        {"asset", "aset"},
        {"holding", "hold", "position"},
        {"fee", "fare", "rake", "commission"},
        {"month", "monthly", "period"},
    )
    for group in synonym_groups:
        if tokens & group:
            tokens.update(group)
    return tokens


def _outer_join_aliases(expression: exp.Expression) -> set[str]:
    aliases: set[str] = set()
    for scope in traverse_scope(expression):
        joins = list(scope.expression.args.get("joins") or [])
        for join in joins:
            side = join.side.upper()
            alias = str(join.this.alias_or_name or "")
            if side in {"LEFT", "FULL"} and alias:
                aliases.add(alias)
            if side in {"RIGHT", "FULL"}:
                aliases.update(str(item) for item in scope.selected_sources if str(item) != alias)
    return aliases


def _normalize_fact_policy(value: Any) -> tuple[str, list[str]]:
    if isinstance(value, dict):
        policy = str(value.get("policy") or value.get("mode") or "").lower()
        sources_raw = value.get("sources") or value.get("source") or []
        sources = sources_raw if isinstance(sources_raw, list) else [sources_raw]
        return policy, [str(item) for item in sources if item]
    return str(value or "").lower(), []


def _outer_alias_matches_policy(
    expression: exp.Expression,
    alias: str,
    signals: set[str],
) -> bool:
    alias_tokens = _expression_tokens(alias)
    if signals & alias_tokens:
        return True
    return any(
        column.table == alias and _column_matches_policy(column, signals)
        for column in expression.find_all(exp.Column)
    )


def _column_matches_policy(column: exp.Column, signals: set[str]) -> bool:
    if not signals:
        return False
    column_tokens = _expression_tokens(column.name)
    return bool(signals & column_tokens)


def _coalesce_is_zero_fill(coalesce: exp.Coalesce) -> bool:
    return any(
        isinstance(item, exp.Literal)
        and not item.is_string
        and re.fullmatch(r"0+(?:\.0+)?", str(item.this)) is not None
        for item in coalesce.expressions
    )


def _comparison_signature(text: str) -> tuple[str, str, set[str]] | None:
    normalized = (
        text.replace("大于等于", ">=")
        .replace("小于等于", "<=")
        .replace("不等于", "!=")
        .replace("大于", ">")
        .replace("小于", "<")
        .replace("等于", "=")
    )
    match = re.search(r"(>=|<=|!=|<>|=|>|<)\s*(['\"]?[A-Za-z0-9_.-]+['\"]?)", normalized)
    if not match:
        return None
    return match.group(1), match.group(2).strip("'\""), _expression_tokens(normalized[: match.start()])


def _comparison_matches_contract(
    comparison: exp.Expression,
    *,
    expected_operator: str,
    expected_literal: str,
    expected_tokens: set[str],
    expression: exp.Expression,
) -> bool:
    operator_by_type = {
        exp.EQ: "=",
        exp.NEQ: "!=",
        exp.GT: ">",
        exp.GTE: ">=",
        exp.LT: "<",
        exp.LTE: "<=",
    }
    actual_operator = operator_by_type.get(type(comparison), "")
    if expected_operator == "<>":
        expected_operator = "!="
    if actual_operator != expected_operator:
        return False
    actual_literals = {str(item.this) for item in comparison.find_all(exp.Literal)}
    if expected_literal not in actual_literals:
        return False
    actual_tokens = _expression_tokens(comparison.sql(dialect="duckdb"))
    if not expected_tokens or expected_tokens & actual_tokens:
        return True
    aliases = {
        canonical_column_name(item.alias): _expression_tokens(item.this.sql(dialect="duckdb"))
        for item in expression.find_all(exp.Alias)
        if item.alias
    }
    if any(expected in aliases and aliases[expected] & actual_tokens for expected in expected_tokens):
        return True
    return comparison.find_ancestor(exp.Having) is not None


def _date_predicate_ancestor(
    column: exp.Column,
    scope_expression: exp.Expression,
) -> exp.Expression | None:
    current = column.parent
    predicate_types = (exp.EQ, exp.NEQ, exp.GT, exp.GTE, exp.LT, exp.LTE, exp.Between, exp.In)
    while current is not None and current is not scope_expression:
        if isinstance(current, predicate_types):
            return current
        current = current.parent
    return None


def _date_in_range(date: str, configured_range: str) -> bool:
    if re.fullmatch(r"\d{8}", configured_range):
        return date == configured_range
    match = re.fullmatch(r"(\d{8})-(\d{8})", configured_range)
    if not match:
        return True
    return match.group(1) <= date <= match.group(2)


def _predicate_overlaps_date_range(
    predicate: exp.Expression,
    dates: list[str],
    configured_range: str,
) -> bool:
    range_match = re.fullmatch(r"(\d{8})-(\d{8})", configured_range)
    available_start = range_match.group(1) if range_match else configured_range
    available_end = range_match.group(2) if range_match else configured_range
    if not re.fullmatch(r"\d{8}", available_start) or not re.fullmatch(r"\d{8}", available_end):
        return True

    if isinstance(predicate, exp.Between) and len(dates) >= 2:
        query_start, query_end = dates[0], dates[-1]
        return query_start <= available_end and query_end >= available_start
    if isinstance(predicate, exp.In):
        return any(available_start <= date <= available_end for date in dates)
    if isinstance(predicate, (exp.EQ, exp.NEQ)):
        return any(available_start <= date <= available_end for date in dates)
    if isinstance(predicate, (exp.GT, exp.GTE)):
        return min(dates) <= available_end
    if isinstance(predicate, (exp.LT, exp.LTE)):
        return max(dates) >= available_start
    return all(_date_in_range(date, configured_range) for date in dates)


def unrequested_filter_warnings(
    expression: exp.Expression,
    *,
    question: str,
    sql_plan: dict[str, Any],
) -> list[str]:
    context = " ".join(
        [
            question,
            " ".join(str(item) for item in sql_plan.get("filters", []) or []),
            " ".join(str(item) for item in sql_plan.get("eligibility_filters", []) or []),
        ]
    ).lower()
    rules = {
        "ccy": ("币种", "人民币", "美元", "港币", "currency", "ccy"),
        "sys_source": ("账户", "普通", "信用", "来源", "sys_source"),
    }
    warnings: set[str] = set()
    for comparison in expression.find_all(exp.EQ):
        for column in comparison.find_all(exp.Column):
            keywords = rules.get(column.name)
            if keywords and not any(keyword in context for keyword in keywords):
                warnings.add(
                    f"SQL adds a {column.name} filter that is not requested by the question or plan."
                )
    return sorted(warnings)


def validate_dictionary_projection(
    expression: exp.Expression,
    output_columns: list[dict[str, Any]],
    *,
    dictionary_translation: bool,
) -> list[str]:
    if not dictionary_translation:
        return []
    expected = {
        canonical_column_name(str(item.get("semantic_type") or item.get("alias") or item.get("name") or ""))
        for item in output_columns
    }
    required = expected & TRANSLATED_OUTPUTS
    if not required:
        return []
    failures: list[str] = []
    projections = {
        canonical_column_name(selected.alias_or_name): selected
        for selected in expression.selects
        if selected.alias_or_name
    } if isinstance(expression, exp.Select) else {}
    for semantic in sorted(required):
        selected = projections.get(semantic)
        if selected is None:
            continue
        inner = selected.this if isinstance(selected, exp.Alias) else selected
        if isinstance(inner, exp.Column) and inner.name in CODE_OUTPUT_FIELDS:
            failures.append(
                f"Dictionary translation required for {semantic}; raw code field {inner.name} is projected."
            )
    return failures
