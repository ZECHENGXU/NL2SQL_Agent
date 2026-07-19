from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from huatai_query_agent.llm.client import Message


PACKAGE_DIR = Path(__file__).resolve().parents[1]
METADATA_DIR = PACKAGE_DIR / "metadata"


SYSTEM_PROMPT = """你是华泰证券客户营销场景的 Text-to-SQL Agent。
你的任务是基于给定元数据，把用户自然语言问题转换为 DuckDB SQL。

硬性规则：
1. 只能输出 JSON 对象，不能输出 Markdown、解释性正文或代码围栏。
2. SQL 只能是 SELECT 或 WITH ... SELECT，禁止 INSERT/UPDATE/DELETE/DDL/COPY/PRAGMA。
3. 只能使用元数据中存在的表和字段。
4. 日期字段为 varchar(8)，使用 'yyyymmdd' 字符串比较。
5. 金额类计算必须使用 coalesce，避免 NULL 传播。
6. 产品名称、产品分类筛选必须关联 dim_product。
7. 客户画像默认使用 ads_cust_info_d.data_dt = '20260531'。
8. 2026年Q1默认日期范围是 '20260101' 到 '20260331'，Q1期末为 '20260331'。

返回 JSON 格式：
{
  "sql_plan": {
    "target": "查询目标",
    "tables": ["表名"],
    "joins": ["关联说明"],
    "filters": ["筛选条件"],
    "metrics": ["指标"],
    "group_by": ["分组字段"],
    "order_by": ["排序规则"]
  },
  "sql": "可直接在 DuckDB 执行的 SQL",
  "confidence": 0.0,
  "assumptions": ["必要假设"],
  "referenced_context_ids": ["使用的元数据chunk id"]
}
"""


def build_sql_generation_messages(question: str, metadata_context: dict[str, Any]) -> list[Message]:
    payload = build_prompt_payload(question, metadata_context)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "请根据以下 JSON 元数据生成 SQL。只返回符合约定格式的 JSON 对象。\n"
                + json.dumps(payload, ensure_ascii=False, indent=2, default=str)
            ),
        },
    ]


def build_sql_repair_messages(
    *,
    question: str,
    metadata_context: dict[str, Any],
    previous_sql: str,
    validation_report: dict[str, Any],
    execution_result: dict[str, Any],
) -> list[Message]:
    payload = build_prompt_payload(question, metadata_context)
    payload["previous_sql"] = previous_sql
    payload["validation_report"] = validation_report
    payload["execution_error"] = execution_result.get("error", "")
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "上一版 SQL 未通过校验或执行失败。请修复 SQL，并只返回符合约定格式的 JSON 对象。\n"
                + json.dumps(payload, ensure_ascii=False, indent=2, default=str)
            ),
        },
    ]


def build_prompt_payload(question: str, metadata_context: dict[str, Any]) -> dict[str, Any]:
    context_tables = _dedupe(
        list(metadata_context.get("tables", []))
        + list(metadata_context.get("matched_demo_case", {}).get("required_tables", []))
    )
    context_metrics = _dedupe(
        list(metadata_context.get("metrics", []))
        + list(metadata_context.get("matched_demo_case", {}).get("expected_metrics", []))
    )

    return {
        "question": question,
        "retrieval_mode": metadata_context.get("retrieval_mode"),
        "context_ids": metadata_context.get("context_ids", []),
        "retrieved_chunks": _compact_chunks(metadata_context.get("chunks", [])),
        "table_schemas": _load_table_schemas(context_tables),
        "metrics": _load_metrics(context_metrics),
        "relationships": _load_relationships(context_tables),
        "generation_rules": _load_generation_rules(),
    }


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _compact_chunks(chunks: list[dict[str, Any]], *, limit: int = 18, text_limit: int = 700) -> list[dict[str, Any]]:
    compact = []
    for chunk in chunks[:limit]:
        compact.append(
            {
                "id": chunk.get("id"),
                "chunk_type": chunk.get("chunk_type"),
                "score": chunk.get("score"),
                "source": chunk.get("source"),
                "text": str(chunk.get("text", ""))[:text_limit],
            }
        )
    return compact


def _load_table_schemas(table_names: list[str]) -> list[dict[str, Any]]:
    doc = _load_yaml(METADATA_DIR / "schema_catalog.yaml")
    tables = doc.get("tables", {})
    output = []
    for table_name in table_names:
        table = tables.get(table_name)
        if not table:
            continue
        output.append(
            {
                "table_name": table_name,
                "name_zh": table.get("name_zh"),
                "grain": table.get("grain"),
                "primary_keys": table.get("primary_keys", []),
                "columns": [
                    {
                        "name": field_name,
                        "type": column.get("type"),
                        "name_zh": column.get("name_zh"),
                        "description": column.get("description"),
                        "dictionary_type": column.get("dictionary_type"),
                    }
                    for field_name, column in table.get("columns", {}).items()
                ],
            }
        )
    return output


def _load_metrics(metric_names: list[str]) -> list[dict[str, Any]]:
    doc = _load_yaml(METADATA_DIR / "metrics.yaml")
    metrics = doc.get("metrics", {})
    output = []
    for metric_name in metric_names:
        metric = metrics.get(metric_name)
        if not metric:
            continue
        item = {"metric_name": metric_name}
        item.update(metric)
        output.append(item)
    return output


def _load_relationships(table_names: list[str]) -> list[dict[str, Any]]:
    table_set = set(table_names)
    doc = _load_yaml(METADATA_DIR / "relationships.yaml")
    output = []
    for relationship in doc.get("relationships", []):
        if relationship.get("left_table") in table_set or relationship.get("right_table") in table_set:
            output.append(relationship)
    for name, join in doc.get("dictionary_joins", {}).items():
        if join.get("source_table") in table_set:
            item = {"name": f"dictionary_{name}"}
            item.update(join)
            output.append(item)
    return output


def _load_generation_rules() -> list[str]:
    doc = _load_yaml(METADATA_DIR / "relationships.yaml")
    return list(doc.get("generation_rules", []))


def _dedupe(values: list[Any]) -> list[str]:
    seen = set()
    output = []
    for value in values:
        if value is None:
            continue
        text = str(value)
        if text not in seen:
            seen.add(text)
            output.append(text)
    return output

