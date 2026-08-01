from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from huatai_query_agent.retrieval.types import MetadataChunk


PACKAGE_DIR = Path(__file__).resolve().parents[1]
METADATA_DIR = PACKAGE_DIR / "metadata"


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _stringify_list(values: list[Any] | None) -> str:
    return "、".join(str(value) for value in (values or []))


class MetadataChunkBuilder:
    def __init__(self, metadata_dir: Path = METADATA_DIR) -> None:
        self.metadata_dir = metadata_dir

    def build_chunks(self) -> list[MetadataChunk]:
        chunks: list[MetadataChunk] = []
        chunks.extend(self._build_schema_chunks())
        chunks.extend(self._build_term_chunks())
        chunks.extend(self._build_metric_chunks())
        chunks.extend(self._build_relationship_chunks())
        return chunks

    def _build_schema_chunks(self) -> list[MetadataChunk]:
        doc = _load_yaml(self.metadata_dir / "schema_catalog.yaml")
        chunks: list[MetadataChunk] = []
        for table_name, table in doc.get("tables", {}).items():
            usage = _stringify_list(table.get("business_usage", []))
            text = (
                f"表 {table_name}，中文名 {table.get('name_zh')}，分层 {table.get('layer')}，"
                f"粒度 {table.get('grain')}，用途：{usage}。主键：{_stringify_list(table.get('primary_keys'))}。"
            )
            chunks.append(
                MetadataChunk(
                    id=f"table.{table_name}",
                    chunk_type="table",
                    text=text,
                    metadata={
                        "source_file": "schema_catalog.yaml",
                        "table_name": table_name,
                        "name_zh": table.get("name_zh"),
                        "layer": table.get("layer"),
                    },
                )
            )

            for field_name, column in table.get("columns", {}).items():
                text = (
                    f"字段 {table_name}.{field_name}，中文名 {column.get('name_zh')}，"
                    f"类型 {column.get('type')}，说明：{column.get('description')}。"
                )
                if column.get("dictionary_type"):
                    text += f" 字典类型：{column.get('dictionary_type')}。"
                chunks.append(
                    MetadataChunk(
                        id=f"field.{table_name}.{field_name}",
                        chunk_type="field",
                        text=text,
                        metadata={
                            "source_file": "schema_catalog.yaml",
                            "table_name": table_name,
                            "field_name": field_name,
                            "field_type": column.get("type"),
                        },
                    )
                )
        return chunks

    def _build_term_chunks(self) -> list[MetadataChunk]:
        doc = _load_yaml(self.metadata_dir / "business_terms.yaml")
        chunks: list[MetadataChunk] = []
        for category, term_group in doc.get("terms", {}).items():
            field_name = term_group.get("field") or _stringify_list(term_group.get("field_candidates", []))
            for value in term_group.get("values", []):
                aliases = value.get("aliases", [])
                code = value.get("code")
                standard_name = value.get("standard_name", "")
                text = (
                    f"业务术语类别 {category}，字段 {field_name}，别名：{_stringify_list(aliases)}，"
                    f"标准名 {standard_name}，编码 {code}。"
                )
                chunks.append(
                    MetadataChunk(
                        id=f"term.{category}.{code}",
                        chunk_type="term",
                        text=text,
                        metadata={
                            "source_file": "business_terms.yaml",
                            "term_category": category,
                            "field_name": field_name,
                            "code_value": code,
                            "aliases": aliases,
                        },
                    )
                )
            for combined in term_group.get("combined_terms", []):
                name = combined.get("name")
                aliases = [name] + list(combined.get("aliases", []))
                text = (
                    f"组合业务术语 {name}，字段 {field_name}，别名：{_stringify_list(aliases)}，"
                    f"SQL条件：{combined.get('sql_condition')}。"
                )
                chunks.append(
                    MetadataChunk(
                        id=f"term.{category}.{name}",
                        chunk_type="term",
                        text=text,
                        metadata={
                            "source_file": "business_terms.yaml",
                            "term_category": category,
                            "field_name": field_name,
                            "term_name": name,
                            "aliases": aliases,
                            "sql_condition": combined.get("sql_condition"),
                        },
                    )
                )

        product_terms = doc.get("product_terms", {})
        for rule in product_terms.get("classification_rules", []):
            term = rule.get("term")
            chunks.append(
                MetadataChunk(
                    id=f"term.product_class.{term}",
                    chunk_type="term",
                    text=f"产品分类术语 {term}，SQL条件：{rule.get('sql_condition')}。",
                    metadata={
                        "source_file": "business_terms.yaml",
                        "term_category": "product_class",
                        "term_name": term,
                        "sql_condition": rule.get("sql_condition"),
                    },
                )
            )
        for rule in product_terms.get("name_matching_rules", []):
            term = rule.get("term")
            text = f"产品名称匹配规则 {term}，SQL条件：{rule.get('sql_condition')}。"
            if rule.get("ambiguity_note"):
                text += f" 歧义说明：{rule.get('ambiguity_note')}。"
            chunks.append(
                MetadataChunk(
                    id=f"term.product_name.{term}",
                    chunk_type="term",
                    text=text,
                    metadata={
                        "source_file": "business_terms.yaml",
                        "term_category": "product_name",
                        "term_name": term,
                        "sql_condition": rule.get("sql_condition"),
                    },
                )
            )
        return chunks

    def _build_metric_chunks(self) -> list[MetadataChunk]:
        doc = _load_yaml(self.metadata_dir / "metrics.yaml")
        chunks: list[MetadataChunk] = []
        for metric_name, metric in doc.get("metrics", {}).items():
            tables = metric.get("source_tables") or [metric.get("source_table")]
            text = (
                f"指标 {metric_name}，中文名 {metric.get('name_zh')}，别名：{_stringify_list(metric.get('aliases'))}，"
                f"涉及表：{_stringify_list(tables)}，表达式：{metric.get('expression')}。"
            )
            if metric.get("aggregation_expression"):
                text += f" 聚合表达式：{metric.get('aggregation_expression')}。"
            if metric.get("description"):
                text += f" 说明：{metric.get('description')}。"
            chunks.append(
                MetadataChunk(
                    id=f"metric.{metric_name}",
                    chunk_type="metric",
                    text=text,
                    metadata={
                        "source_file": "metrics.yaml",
                        "metric_name": metric_name,
                        "name_zh": metric.get("name_zh"),
                        "tables": [table for table in tables if table],
                    },
                )
            )

        for period_name, period in doc.get("time_periods", {}).items():
            text = (
                f"时间口径 {period_name}，别名：{_stringify_list(period.get('aliases'))}，"
                f"开始日期 {period.get('start_date', period.get('date'))}，结束日期 {period.get('end_date', period.get('date'))}，"
                f"天数 {period.get('day_count', '')}。"
            )
            chunks.append(
                MetadataChunk(
                    id=f"time.{period_name}",
                    chunk_type="time_period",
                    text=text,
                    metadata={
                        "source_file": "metrics.yaml",
                        "period_name": period_name,
                    },
                )
            )
        return chunks

    def _build_relationship_chunks(self) -> list[MetadataChunk]:
        doc = _load_yaml(self.metadata_dir / "relationships.yaml")
        chunks: list[MetadataChunk] = []
        for relationship in doc.get("relationships", []):
            name = relationship.get("name")
            left_table = relationship.get("left_table")
            right_table = relationship.get("right_table")
            keys = ", ".join(f"{item.get('left')}={item.get('right')}" for item in relationship.get("keys", []))
            text = (
                f"表关系 {name}：{left_table} {relationship.get('join_type')} join {right_table}，"
                f"关联键 {keys}，模板：{relationship.get('template')}。"
            )
            if relationship.get("date_rule"):
                text += f" 日期规则：{relationship.get('date_rule')}。"
            chunks.append(
                MetadataChunk(
                    id=f"relationship.{name}",
                    chunk_type="relationship",
                    text=text,
                    metadata={
                        "source_file": "relationships.yaml",
                        "relationship_name": name,
                        "left_table": left_table,
                        "right_table": right_table,
                    },
                )
            )

        for name, join in doc.get("dictionary_joins", {}).items():
            text = (
                f"字典关联 {name}，源表 {join.get('source_table')}，源字段 {join.get('source_field')}，"
                f"字典类型 {join.get('dictionary_type')}，模板：{join.get('template')}。"
            )
            chunks.append(
                MetadataChunk(
                    id=f"relationship.dictionary.{name}",
                    chunk_type="relationship",
                    text=text,
                    metadata={
                        "source_file": "relationships.yaml",
                        "relationship_name": name,
                        "left_table": join.get("source_table"),
                        "right_table": "dim_public",
                    },
                )
            )
        return chunks

def build_metadata_chunks() -> list[MetadataChunk]:
    return MetadataChunkBuilder().build_chunks()
