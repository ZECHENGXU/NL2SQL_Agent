from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import yaml

from huatai_query_agent.agent.contracts import derive_output_contract


PACKAGE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SQL_PATH = PACKAGE_DIR / "sql" / "demo_queries_duckdb.sql"
DEFAULT_EXAMPLES_PATH = PACKAGE_DIR / "metadata" / "query_examples.yaml"


@dataclass(frozen=True)
class DemoCase:
    query_id: str
    question: str
    sql: str
    scenario: str = ""
    difficulty: str = ""
    intent: dict[str, Any] = field(default_factory=dict)
    required_tables: list[str] = field(default_factory=list)
    expected_metrics: list[str] = field(default_factory=list)
    output_contract: dict[str, Any] = field(default_factory=dict)


def _normalize_text(value: str) -> str:
    value = value.strip().lower()
    return re.sub(r"[\s，。？?、；;：:,.!！\"'`]+", "", value)


def load_sql_cases(sql_path: Path = DEFAULT_SQL_PATH) -> dict[str, str]:
    content = sql_path.read_text(encoding="utf-8")
    parts = re.split(r"^--\s*query_id:\s*([a-zA-Z0-9_-]+)\s*$", content, flags=re.MULTILINE)
    if len(parts) < 3:
        raise ValueError(f"No query_id blocks found in {sql_path}")

    cases: dict[str, str] = {}
    for idx in range(1, len(parts), 2):
        query_id = parts[idx].strip()
        sql = parts[idx + 1].strip()
        if sql.endswith(";"):
            sql = sql[:-1].strip()
        cases[query_id] = sql
    return cases


class DemoCaseRepository:
    def __init__(
        self,
        *,
        sql_path: Path = DEFAULT_SQL_PATH,
        examples_path: Path = DEFAULT_EXAMPLES_PATH,
    ) -> None:
        self.sql_path = sql_path
        self.examples_path = examples_path
        self._cases = self._load_cases()

    def _load_cases(self) -> dict[str, DemoCase]:
        sql_cases = load_sql_cases(self.sql_path)
        examples_doc = yaml.safe_load(self.examples_path.read_text(encoding="utf-8"))
        cases: dict[str, DemoCase] = {}

        for item in examples_doc.get("examples", []):
            query_id = item["id"]
            if query_id not in sql_cases:
                continue
            intent = item.get("intent", {})
            cases[query_id] = DemoCase(
                query_id=query_id,
                question=item.get("question", ""),
                scenario=item.get("scenario", ""),
                difficulty=item.get("difficulty", ""),
                intent=intent,
                required_tables=list(item.get("required_tables", [])),
                expected_metrics=list(item.get("expected_metrics", [])),
                output_contract=derive_output_contract(
                    sql_cases[query_id],
                    question=str(item["question"]),
                    override=dict(item.get("output_contract") or {}),
                ),
                sql=sql_cases[query_id],
            )
        return cases

    def list_cases(self) -> list[DemoCase]:
        return [self._cases[key] for key in sorted(self._cases)]

    def get(self, query_id: str) -> DemoCase:
        try:
            return self._cases[query_id]
        except KeyError as exc:
            raise KeyError(f"Unknown demo query id: {query_id}") from exc

    def match(self, question: str, query_id: str | None = None) -> tuple[DemoCase | None, float]:
        if query_id:
            return self.get(query_id), 1.0

        qid_match = re.search(r"\bq00[1-7]\b", question, flags=re.IGNORECASE)
        if qid_match:
            return self.get(qid_match.group(0).lower()), 1.0

        normalized = _normalize_text(question)
        if not normalized:
            return None, 0.0

        best_case: DemoCase | None = None
        best_score = 0.0
        for case in self._cases.values():
            candidate = _normalize_text(case.question)
            if normalized == candidate:
                return case, 1.0
            if normalized in candidate or candidate in normalized:
                score = 0.95
            else:
                score = SequenceMatcher(None, normalized, candidate).ratio()
            if score > best_score:
                best_case = case
                best_score = score

        if best_score < 0.30:
            return None, best_score
        return best_case, best_score
