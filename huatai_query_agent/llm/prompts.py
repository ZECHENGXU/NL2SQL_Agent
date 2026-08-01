from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from huatai_query_agent.llm.client import Message


PACKAGE_DIR = Path(__file__).resolve().parents[1]
METADATA_DIR = PACKAGE_DIR / "metadata"
PROMPT_VERSION = "2026-07-31-contract-v3"


SYSTEM_PROMPT = """你是华泰证券客户营销场景的 Text-to-SQL Agent。
你必须基于给定元数据和真实执行结果工作，不能编造表、字段、指标、客户、结果行或业务口径。

硬性规则：
1. 只能输出 JSON 对象，不能输出 Markdown、解释性正文或代码围栏。
2. 需要生成 SQL 时，SQL 只能是 SELECT 或 WITH ... SELECT，禁止 INSERT/UPDATE/DELETE/DDL/COPY/PRAGMA。
3. 只能使用元数据中存在的表和字段。
4. 日期字段为 varchar(8)，使用 'yyyymmdd' 字符串比较。
5. 金额类计算必须使用 coalesce，避免 NULL 传播。
6. 产品名称、产品分类筛选必须关联 dim_product。
7. 客户画像 ads_cust_info_d 和机构 dim_branch 当前快照固定为 '20260531'；不得把事实表日期传播给这两张表。
8. 2026年Q1默认日期范围是 '20260101' 到 '20260331'，Q1期末为 '20260331'。
9. 不得添加用户、业务规则和 SQL 计划均未要求的币种、账户来源、产品或地域过滤。
10. 区分“整条事实记录缺失”和“已存在记录的字段为NULL”。只有计划明确要求缺失事实按0时，才允许在连接后补0；双快照比较默认要求两期记录都存在。
11. 客户等级、性别、学历和币种等面向业务用户的维度默认输出中文描述，不输出原始编码，除非用户明确要求编码。
12. 只有会改变查询目标、关键实体、时间范围或核心口径且无法从元数据默认规则得到的信息，才是 blocking_missing_slots；其他不确定性写入 assumptions 后继续。
13. SQL 最外层 SELECT 必须严格覆盖 sql_plan.output_columns，使用指定顺序和 alias，不得漏列或擅自增加列。
14. 结果解释只能基于 execution_result 中的列、行数和预览行。
"""


INTENT_PROMPT = SYSTEM_PROMPT + """
当前任务：解析用户问题的业务意图，不生成 SQL。

返回 JSON 格式：
{
  "intent": {
    "target": "查询目标",
    "dimensions": ["维度"],
    "filters": ["筛选条件"],
    "metrics": ["指标或统计口径"],
    "time_range": {"start_date": "", "end_date": "", "point_date": ""},
    "products": ["产品或产品分类"],
    "customer_scope": ["客户范围条件"],
    "requested_outputs": [
      {"name": "语义字段名", "alias": "稳定snake_case别名", "required": true}
    ],
    "population": "统计母集",
    "grain": ["最终结果粒度"],
    "missing_fact_policy": {},
    "snapshot_policy": {}
  },
  "blocking_missing_slots": ["确实阻断SQL且无法采用默认值的信息"],
  "non_blocking_uncertainties": ["不阻断SQL的不确定项"],
  "ambiguities": {"字段或术语": ["候选解释"]},
  "assumptions": ["按赛题规则可默认的假设"],
  "confidence": 0.0
}
"""


SLOT_FILL_PROMPT = SYSTEM_PROMPT + """
当前任务：基于检索到的元数据补全业务槽位和术语映射，不生成 SQL。

返回 JSON 格式：
{
  "intent_patch": {
    "target": "可选修正",
    "dimensions": ["标准化维度"],
    "filters": ["标准化筛选"],
    "metrics": ["标准指标名"],
    "time_range": {"start_date": "", "end_date": "", "point_date": ""},
    "products": ["标准产品条件"],
    "customer_scope": ["标准客户条件"],
    "requested_outputs": [
      {"name": "语义字段名", "alias": "稳定snake_case别名", "required": true}
    ],
    "population": "统计母集",
    "grain": ["最终结果粒度"],
    "missing_fact_policy": {},
    "snapshot_policy": {}
  },
  "resolved_terms": [
    {"term": "原始术语", "resolved_to": "标准解释", "field": "表.字段", "value": "编码或条件", "context_id": "元数据chunk id"}
  ],
  "blocking_missing_slots": ["仍然缺失、影响核心口径且不能默认的信息"],
  "non_blocking_uncertainties": ["可采用假设继续的不确定项"],
  "ambiguities": {"字段或术语": ["候选解释"]},
  "assumptions": ["按元数据和赛题规则采用的默认假设"],
  "confidence": 0.0
}
"""


SQL_PLAN_PROMPT = SYSTEM_PROMPT + """
当前任务：基于意图、槽位和元数据制定 SQL 计划，不生成 SQL。

返回 JSON 格式：
{
  "sql_plan": {
    "target": "查询目标",
    "tables": ["表名"],
    "joins": ["关联说明"],
    "filters": ["筛选条件"],
    "metrics": ["指标"],
    "population": "统计母集及其来源",
    "grain": ["最终结果粒度"],
    "output_columns": [
      {
        "expression": "SQL表达式或语义来源",
        "alias": "稳定snake_case别名",
        "semantic_type": "语义类型",
        "required": true,
        "position": 1
      }
    ],
    "group_by": ["分组字段"],
    "eligibility_filters": ["进入排名或统计前必须满足的资格条件"],
    "snapshot_policy": {"表名": "日期或日期范围"},
    "missing_fact_policy": {"事实名称": "require_record或zero_fill_after_aggregation"},
    "missing_period_policy": "exclude或zero_fill",
    "dictionary_translation": ["需要翻译为中文的字段"],
    "window": [
      {
        "function": "row_number|dense_rank|lag|ntile|percent_rank",
        "partition_by": ["分区键"],
        "order_by": [{"expression": "字段", "direction": "asc|desc"}],
        "tie_breaker": ["并列打散字段"]
      }
    ],
    "order_by": [
      {"expression": "字段", "direction": "asc|desc", "nulls": "first|last"}
    ],
    "top_n": null,
    "expect_nonempty": false
  },
  "confidence": 0.0,
  "assumptions": ["必要假设"],
  "referenced_context_ids": ["使用的元数据chunk id"]
}
"""


SQL_GENERATION_PROMPT = SYSTEM_PROMPT + """
当前任务：严格按照给定 SQL 计划生成一条可在 DuckDB 执行的 SQL。

生成前逐项核对 output_columns、population、grain、eligibility_filters、snapshot_policy、
missing_fact_policy、window 和 order_by。最外层 SELECT 的列数量、顺序和 alias 必须与
output_columns 完全一致。不要把字段 NULL 的 coalesce 规则扩大成缺失事实记录补0。

返回 JSON 格式：
{
  "sql": "可直接在 DuckDB 执行的 SQL",
  "confidence": 0.0,
  "assumptions": ["必要假设"],
  "referenced_context_ids": ["使用的元数据chunk id"]
}
"""


RESULT_EXPLANATION_PROMPT = SYSTEM_PROMPT + """
当前任务：解释 SQL 的真实执行结果。

返回 JSON 格式：
{
  "final_answer": "面向业务用户的简洁中文回答",
  "confidence": 0.0,
  "warnings": ["必要风险提示或口径说明"]
}
"""


def build_intent_parse_messages(question: str) -> list[Message]:
    payload = {"question": question}
    return [
        {"role": "system", "content": INTENT_PROMPT},
        {
            "role": "user",
            "content": "请解析以下问题的业务意图，只返回 JSON 对象。\n" + json.dumps(payload, ensure_ascii=False, indent=2),
        },
    ]


def build_slot_fill_messages(
    *,
    question: str,
    intent: dict[str, Any],
    metadata_context: dict[str, Any],
) -> list[Message]:
    payload = build_prompt_payload(question, metadata_context)
    payload["intent"] = intent
    return [
        {"role": "system", "content": SLOT_FILL_PROMPT},
        {
            "role": "user",
            "content": "请基于元数据补全槽位和术语映射，只返回 JSON 对象。\n" + json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        },
    ]


def build_sql_plan_messages(
    *,
    question: str,
    intent: dict[str, Any],
    metadata_context: dict[str, Any],
) -> list[Message]:
    payload = build_prompt_payload(question, metadata_context)
    payload["intent"] = intent
    return [
        {"role": "system", "content": SQL_PLAN_PROMPT},
        {
            "role": "user",
            "content": "请制定 SQL 计划，不要生成 SQL，只返回 JSON 对象。\n" + json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        },
    ]


def build_sql_generation_messages(
    question: str,
    metadata_context: dict[str, Any],
    *,
    intent: dict[str, Any] | None = None,
    sql_plan: dict[str, Any] | None = None,
) -> list[Message]:
    payload = build_prompt_payload(question, metadata_context)
    payload["intent"] = intent or {}
    payload["sql_plan"] = sql_plan or {}
    return [
        {"role": "system", "content": SQL_GENERATION_PROMPT},
        {
            "role": "user",
            "content": (
                "请根据以下 JSON 元数据和 SQL 计划生成 SQL。只返回符合约定格式的 JSON 对象。\n"
                + json.dumps(payload, ensure_ascii=False, indent=2, default=str)
            ),
        },
    ]


def build_sql_repair_messages(
    *,
    question: str,
    metadata_context: dict[str, Any],
    intent: dict[str, Any],
    sql_plan: dict[str, Any],
    previous_sql: str,
    validation_report: dict[str, Any],
    execution_result: dict[str, Any],
    result_check: dict[str, Any] | None = None,
) -> list[Message]:
    payload = build_prompt_payload(question, metadata_context)
    payload["intent"] = intent
    payload["sql_plan"] = sql_plan
    payload["previous_sql"] = previous_sql
    payload["validation_report"] = validation_report
    payload["execution_error"] = execution_result.get("error", "")
    payload["result_check"] = result_check or {}
    return [
        {"role": "system", "content": SQL_GENERATION_PROMPT},
        {
            "role": "user",
            "content": (
                "上一版 SQL 未通过校验或执行失败。请修复 SQL，并只返回符合约定格式的 JSON 对象。\n"
                + json.dumps(payload, ensure_ascii=False, indent=2, default=str)
            ),
        },
    ]


def build_result_explanation_messages(
    *,
    question: str,
    sql_plan: dict[str, Any],
    sql: str,
    execution_result: dict[str, Any],
    result_check: dict[str, Any],
) -> list[Message]:
    payload = {
        "question": question,
        "sql_plan": sql_plan,
        "sql": sql,
        "execution_result": _compact_execution_result(execution_result),
        "result_check": result_check,
    }
    return [
        {"role": "system", "content": RESULT_EXPLANATION_PROMPT},
        {
            "role": "user",
            "content": "请基于真实执行结果生成回答，只返回 JSON 对象。\n" + json.dumps(payload, ensure_ascii=False, indent=2, default=str),
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
        "request_context": metadata_context.get("request_context", {}),
        "retrieval_mode": metadata_context.get("retrieval_mode"),
        "context_ids": metadata_context.get("context_ids", []),
        "retrieved_chunks": _compact_chunks(metadata_context.get("chunks", [])),
        "table_schemas": _load_table_schemas(context_tables),
        "metrics": _load_metrics(context_metrics),
        "relationships": _load_relationships(context_tables),
        "generation_rules": _load_generation_rules(),
    }


def _compact_execution_result(execution_result: dict[str, Any], *, preview_limit: int = 10) -> dict[str, Any]:
    return {
        "success": execution_result.get("success"),
        "columns": execution_result.get("columns", []),
        "row_count": execution_result.get("row_count", 0),
        "preview_rows": list(execution_result.get("preview_rows", []))[:preview_limit],
        "elapsed_ms": execution_result.get("elapsed_ms", 0),
        "error": execution_result.get("error", ""),
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
                "data_date_range": table.get("data_date_range"),
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
