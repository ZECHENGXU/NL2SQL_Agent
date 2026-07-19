from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from huatai_query_agent.agent.nodes.m1_nodes import validate_sql
from huatai_query_agent.evaluation.guardrail_cases import GUARDRAIL_CASES, GuardrailCase


PACKAGE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_MD = PACKAGE_DIR / "evaluation" / "guardrail_eval_report.md"
DEFAULT_REPORT_CSV = PACKAGE_DIR / "evaluation" / "guardrail_eval_results.csv"


@dataclass(frozen=True)
class GuardrailEvalRecord:
    case_id: str
    category: str
    description: str
    expected_pass: bool
    actual_pass: bool
    matched_expectation: bool
    errors: list[str]
    sql: str


def evaluate_case(case: GuardrailCase) -> GuardrailEvalRecord:
    update = validate_sql({"candidate_sql": case.sql, "trace": []})
    report = update.get("validation_report", {})
    errors = [str(item) for item in report.get("errors", [])]
    actual_pass = bool(report.get("passed"))
    matched_pass = actual_pass == case.expected_pass
    matched_keywords = all(
        any(keyword.lower() in error.lower() for error in errors)
        for keyword in case.expected_error_keywords
    )
    matched_expectation = matched_pass and (case.expected_pass or matched_keywords)
    return GuardrailEvalRecord(
        case_id=case.case_id,
        category=case.category,
        description=case.description,
        expected_pass=case.expected_pass,
        actual_pass=actual_pass,
        matched_expectation=matched_expectation,
        errors=errors,
        sql=case.sql,
    )


def write_csv(records: list[GuardrailEvalRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "case_id",
                "category",
                "description",
                "expected_pass",
                "actual_pass",
                "matched_expectation",
                "errors",
                "sql",
            ],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "case_id": record.case_id,
                    "category": record.category,
                    "description": record.description,
                    "expected_pass": record.expected_pass,
                    "actual_pass": record.actual_pass,
                    "matched_expectation": record.matched_expectation,
                    "errors": "; ".join(record.errors),
                    "sql": record.sql,
                }
            )


def write_markdown(records: list[GuardrailEvalRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    total = len(records)
    passed = sum(1 for record in records if record.matched_expectation)
    blocked = sum(1 for record in records if not record.actual_pass)
    lines = [
        "# Guardrail Evaluation Report",
        "",
        f"- Total cases: {total}",
        f"- Matched expectations: {passed}/{total} ({passed / total:.2%})",
        f"- Blocked SQL cases: {blocked}/{total} ({blocked / total:.2%})",
        "",
        "| Case ID | Category | Expected Pass | Actual Pass | Matched | Errors |",
        "|---------|----------|---------------|-------------|---------|--------|",
    ]
    for record in records:
        lines.append(
            "| "
            + " | ".join(
                [
                    record.case_id,
                    record.category,
                    _yn(record.expected_pass),
                    _yn(record.actual_pass),
                    _yn(record.matched_expectation),
                    "; ".join(record.errors).replace("|", "/") or "none",
                ]
            )
            + " |"
        )

    lines.extend(["", "## Case SQL", ""])
    for record in records:
        lines.extend(
            [
                f"### {record.case_id}",
                "",
                record.description,
                "",
                "```sql",
                record.sql,
                "```",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run SQL guardrail and hallucination suppression evaluation.")
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT_MD, help="Markdown report path.")
    parser.add_argument("--report-csv", type=Path, default=DEFAULT_REPORT_CSV, help="CSV report path.")
    parser.add_argument("--no-write-report", action="store_true", help="Print only; do not write report files.")
    args = parser.parse_args()

    records = [evaluate_case(case) for case in GUARDRAIL_CASES]
    total = len(records)
    passed = sum(1 for record in records if record.matched_expectation)

    print("| Case ID | Category | Expected Pass | Actual Pass | Matched |")
    print("|---------|----------|---------------|-------------|---------|")
    for record in records:
        print(
            f"| {record.case_id} | {record.category} | {_yn(record.expected_pass)} | "
            f"{_yn(record.actual_pass)} | {_yn(record.matched_expectation)} |"
        )
    print()
    print(f"guardrail_expectation_match_rate={passed}/{total} ({passed / total:.2%})")

    if not args.no_write_report:
        write_markdown(records, args.report_md)
        write_csv(records, args.report_csv)
        print(f"wrote_markdown={args.report_md}")
        print(f"wrote_csv={args.report_csv}")

    if passed != total:
        raise SystemExit(1)


def _yn(value: bool) -> str:
    return "Y" if value else "N"


if __name__ == "__main__":
    main()
