# Metadata README

本目录是智能问数 Agent 的结构化元数据底座，对应赛题攻关任务 1：定义 AI 友好的元数据及其组织形式。

这些文件的用途：

- `schema_catalog.yaml`：表、字段、中文释义、业务说明，用于 RAG 检索和字段白名单校验。
- `business_terms.yaml`：业务术语、同义词、编码值映射，用于用户问题解析。
- `metrics.yaml`：指标口径、SQL表达式、涉及表，用于 SQL 生成和指标合法性校验。
- `relationships.yaml`：表间关联关系和标准 JOIN 模板，用于多表查询生成。
- `query_examples.yaml`：7条样例问题的结构化拆解，仅用于评测集种子和演示入口，不参与元数据检索。

后续开发中，Agent 不应直接依赖散落的 Markdown 描述，而应优先读取本目录中的结构化元数据。
