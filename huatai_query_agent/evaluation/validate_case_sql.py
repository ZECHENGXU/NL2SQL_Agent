from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from huatai_query_agent.evaluation.agent_evaluator import (
    load_advanced_eval_cases,
    load_synthetic_eval_cases,
)
from huatai_query_agent.executors.duckdb_executor import DuckDBExecutor


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate SQL-backed evaluation cases.")
    parser.add_argument(
        "--case-set",
        choices=["synthetic", "advanced", "all"],
        default="advanced",
    )
    parser.add_argument(
        "--require-non-empty",
        action="store_true",
        help="Fail validation when a reference query returns zero rows.",
    )
    parser.add_argument(
        "--snapshot",
        type=Path,
        help="Optional JSON path for complete expected results.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cases = []
    if args.case_set in {"synthetic", "all"}:
        cases.extend(load_synthetic_eval_cases())
    if args.case_set in {"advanced", "all"}:
        cases.extend(load_advanced_eval_cases())

    errors = validate_case_metadata(cases)
    executor = DuckDBExecutor()
    snapshot_cases: list[dict[str, Any]] = []

    for case in cases:
        result = executor.execute(case.sql, preview_limit=10000)
        status = "ok" if result.success else "error"
        print(f"{case.query_id}: {status}, rows={result.row_count}, elapsed_ms={result.elapsed_ms:.2f}")
        if not result.success:
            errors.append(f"{case.query_id}: SQL failed: {result.error}")
            continue
        if args.require_non_empty and result.row_count == 0:
            errors.append(f"{case.query_id}: reference SQL returned zero rows")
        contract_columns = [
            str(item.get("alias") or item.get("name") or "")
            for item in case.output_contract.get("columns", [])
        ]
        if contract_columns != result.columns:
            errors.append(
                f"{case.query_id}: output contract columns {contract_columns} "
                f"do not match reference columns {result.columns}"
            )

        payload = {
            "id": case.query_id,
            "columns": result.columns,
            "output_contract": case.output_contract,
            "row_count": result.row_count,
            "rows": result.rows,
        }
        normalized = to_json_value(payload)
        encoded = json.dumps(normalized, ensure_ascii=False, sort_keys=True).encode("utf-8")
        normalized["result_sha256"] = hashlib.sha256(encoded).hexdigest()
        snapshot_cases.append(normalized)

    if args.snapshot:
        snapshot_path = args.snapshot
        if not snapshot_path.is_absolute():
            snapshot_path = PROJECT_DIR / snapshot_path
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        snapshot = {
            "case_set": args.case_set,
            "case_count": len(snapshot_cases),
            "cases": snapshot_cases,
        }
        snapshot_path.write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"snapshot={snapshot_path}")

    if errors:
        print("validation_errors:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"validated={len(cases)}")
    return 0


def validate_case_metadata(cases: list[Any]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    for case in cases:
        if case.query_id in seen_ids:
            errors.append(f"{case.query_id}: duplicate case id")
        seen_ids.add(case.query_id)
        if not case.question.strip():
            errors.append(f"{case.query_id}: question is empty")
        if not case.required_tables:
            errors.append(f"{case.query_id}: required_tables is empty")
        if not case.expected_metrics:
            errors.append(f"{case.query_id}: expected_metrics is empty")
        if not case.sql.strip():
            errors.append(f"{case.query_id}: SQL is empty")
        contract = case.output_contract
        if not contract or not contract.get("columns"):
            errors.append(f"{case.query_id}: output_contract.columns is empty")
        else:
            positions = [
                int(item.get("position", 0))
                for item in contract.get("columns", [])
            ]
            if positions != list(range(1, len(positions) + 1)):
                errors.append(f"{case.query_id}: output contract positions are invalid")
        if "order_sensitive" not in contract:
            errors.append(f"{case.query_id}: output contract lacks order_sensitive")
        if case.intent.get("_eval_source") == "advanced":
            input_style = case.intent.get("_eval_input_style")
            if input_style not in {"concise", "long_form"}:
                errors.append(f"{case.query_id}: invalid or missing input_style")
            if not case.intent.get("_eval_capability_tags"):
                errors.append(f"{case.query_id}: capability_tags is empty")
            if not case.intent.get("_eval_calculation_notes"):
                errors.append(f"{case.query_id}: calculation_notes is empty")
            if case.difficulty != "expert":
                errors.append(f"{case.query_id}: advanced difficulty must be expert")
    return errors


def to_json_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if is_dataclass(value):
        return to_json_value(asdict(value))
    if isinstance(value, dict):
        return {str(key): to_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json_value(item) for item in value]
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
