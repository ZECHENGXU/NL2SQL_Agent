# Agent M4 原型

本模块实现华泰 Text-to-SQL 项目的可运行 LangGraph Agent 原型。

## 当前范围

- 当已安装 `langgraph` 时，运行文档化的 LangGraph `StateGraph` 节点流程。
- 对 7 条官方演示问题使用确定性匹配，生成标准 DuckDB SQL。
- 通过 `HybridMetadataRetriever` 检索元数据上下文，结合 YAML 精确/关键词检索与 Qdrant Local 向量检索。
- 支持 M4 LLM 模式，并将意图解析、槽位补全、SQL 规划、SQL 生成、SQL 修复和结果解释拆成可观测节点。
- 通过结构化 JSON 输出、元数据约束 Prompt、`sqlglot` 解析、只读检查、表白名单、限定字段白名单和真实 DuckDB 执行来抑制幻觉。
- 在 `huatai_query_agent/data/cust_data.duckdb` 上执行 SQL。
- 返回 Trace、SQL 元数据上下文、结果预览、行数和最终回答。
- 当未安装 `langgraph` 时，使用备用 runner。

M2 检索层使用 `HashingEmbedding` 作为确定性的本地向量兜底方案。它不是语义嵌入模型；它的作用是在本地 embedding API 接入前，保证 Qdrant 路径可运行。

## 运行

从项目根目录执行：

```powershell
conda activate huatai-agent
```

```powershell
python -m huatai_query_agent.agent.run_agent --all --preview 2
```

如果 shell 没有正确激活 Conda，直接使用环境中的 Python：

```powershell
& "E:\anaconda\envs\huatai-agent\python.exe" -m huatai_query_agent.agent.run_agent --all --preview 2
```

运行单个用例：

```powershell
python -m huatai_query_agent.agent.run_agent --query-id q005 --preview 5
```

按问题文本运行：

```powershell
python -m huatai_query_agent.agent.run_agent --question "2026年Q1交易过招商银行A股，并且在Q1末普通账户持有中国平安A股的客户有哪些？"
```

检查 DeepSeek API 连接：

```powershell
python -m huatai_query_agent.llm.check_connection
```

使用 LLM SQL 生成运行单个用例：

```powershell
python -m huatai_query_agent.agent.run_agent --query-id q005 --sql-mode llm --preview 5
```

使用 LLM SQL 生成运行任意自然语言问题：

```powershell
python -m huatai_query_agent.agent.run_agent --question "学历本科以上的男性客户，年龄超过50岁的有多少个？" --sql-mode llm --preview 5
```

批量评测：

```powershell
python huatai_query_agent\evaluation\run_agent_eval.py
```

预期 demo 结果：

```text
langgraph_available=True
agent_executable_rate[demo]=7/7 (100.00%)
```

预期 LLM Trace 包含：

```text
parse_intent -> retrieve_metadata -> fill_slots -> plan_sql -> generate_sql -> validate_sql -> execute_sql -> validate_result -> render_answer
```

## LLM 配置

LLM 设置从项目 `.env` 读取：

```text
HUATAI_LLM_PROVIDER=deepseek
HUATAI_LLM_API_KEY=sk-your-key
HUATAI_LLM_BASE_URL=https://api.deepseek.com
HUATAI_LLM_MODEL=deepseek-v4-pro
HUATAI_LLM_TIMEOUT_SECONDS=60
HUATAI_LLM_TEMPERATURE=0
HUATAI_LLM_MAX_TOKENS=4096
```

`.env` 已被 git 忽略。共享配置模板请使用 `.env.example`。

## 下一步实现

将当前 M4 原型升级为覆盖更广的评测版本：

1. 用本地语义 embedding API 替换 hashing 向量。
2. 增加 7 条官方样例之外的评测用例。
3. 基于已批准的本地模型网关，运行并归档完整 LLM 模式评测。
