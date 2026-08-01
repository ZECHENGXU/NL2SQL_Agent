# 华泰证券 Agentic 智能问数项目

本项目面向“金融大模型与智能体赛道 - 华泰证券 Agentic 智能问数在客户营销场景的应用”，目标是构建一个可控、可审计、可评测的证券客户营销 Text-to-SQL Agent。

系统不是静态 SQL 模板集合，而是基于 LangGraph 的 Agent 工作流：自然语言问题进入后，依次经过意图解析、元数据检索、槽位补全、SQL 规划、SQL 生成、安全围栏、真实数据库执行、结果校验和业务回答。

## 当前进度

已完成到 M6 可演示 MVP：

| 阶段 | 状态 | 交付 |
|------|------|------|
| M1 | 已完成 | LangGraph Agent 骨架、7 条官方样例标准 SQL、DuckDB 真实执行 |
| M2 | 已完成 | YAML + Qdrant Local 混合元数据检索 |
| M3 | 已完成 | DeepSeek OpenAI-compatible LLM 调用层 |
| M4 | 已完成 | 多节点 LLM Agent、SQL 围栏、幻觉抑制 |
| M5 | 已完成 | 标准 SQL vs Agent SQL 自动化评测、围栏评测 |
| M6 | 已完成 | 本地 Web 演示工作台 |

## 核心能力

- 真实连接 DuckDB 执行 SQL，不是模拟结果。
- 支持 7 条赛题官方样例。
- 支持 `demo` 稳定路径和 `llm` 生成路径。
- 元数据检索使用结构化 YAML + Qdrant Local。
- LLM 输出强制 JSON，节点输出可追踪。
- SQL 执行前使用 `sqlglot` 做 AST 校验。
- 已实现只读校验、危险 SQL 拦截、多语句拦截、表白名单、字段白名单、指标公式校验。
- 支持 thread 级短期记忆，可演示一次条件追问；模糊产品名会进入澄清路径。
- 自动化评测可输出 Markdown / CSV 报告。
- 本地 Web 页面可展示结果、SQL、Trace、围栏、元数据和评测报告。

## 目录结构

```text
huatai_query_agent/
  agent/          LangGraph Agent 状态图、节点和命令行入口
  data/           CSV 导入 DuckDB 与数据库校验脚本
  evaluation/     自动化评测、围栏评测和评测报告
  executors/      SQL 执行器抽象与 DuckDBExecutor
  llm/            DeepSeek/OpenAI-compatible LLM 客户端和 Prompt
  metadata/       表结构、业务术语、指标口径、关系、样例问题 YAML
  retrieval/      YAML chunk 构建、关键词检索、Qdrant Local 检索
  sql/            官方 7 条样例 DuckDB SQL
  web/            M6 本地 Web 演示工作台
```

关键文档：

- `00_PRD_产品需求文档.md`
- `01_元数据与业务术语映射文档.md`
- `02_技术实现方案文档.md`
- `03_DuckDB数据库选型调研文档.md`
- `04_RAG向量数据库选型调研文档.md`
- `05_Data_Stream_Report_数据流转报告.md`
- `06_Demo_Runbook_答辩演示脚本.md`

## 环境

当前推荐环境：

```text
conda env: huatai-agent
python: E:\anaconda\envs\huatai-agent\python.exe
```

激活环境：

```powershell
conda activate huatai-agent
```

如果 VSCode 终端无法正确激活 conda，直接使用完整 Python 路径：

```powershell
E:\anaconda\envs\huatai-agent\python.exe --version
```

## 配置

`.env` 存放本地私密配置，不进入 git。示例见 `.env.example`。

当前支持 DeepSeek 官方云 API 或本地 OpenAI-compatible 模型网关：

```text
HUATAI_LLM_PROVIDER=deepseek
HUATAI_LLM_BASE_URL=https://api.deepseek.com
HUATAI_LLM_MODEL=deepseek-v4-pro
HUATAI_LLM_API_KEY=sk-your-key
```

注意：如果使用云端 LLM，问题、元数据上下文、SQL plan 和结果摘要可能发送到模型服务商。正式金融数据环境建议切换到本地模型网关。

本地模型网关检查：

```powershell
E:\anaconda\envs\huatai-agent\python.exe huatai_query_agent\llm\check_connection.py --require-local --expected-model deepseek-v4-rpo
```

Embedding 默认使用确定性 `HashingEmbedding` 兜底；如已部署 bge-m3/OpenAI-compatible embedding 服务，可在 `.env` 中配置 `HUATAI_EMBEDDING_PROVIDER=local_openai_compatible`、`HUATAI_EMBEDDING_BASE_URL` 和 `HUATAI_EMBEDDING_MODEL=BAAI/bge-m3` 后重建索引。

## 初始化数据和索引

通常仓库中已完成数据导入和索引构建。如需重建：

```powershell
E:\anaconda\envs\huatai-agent\python.exe huatai_query_agent\data\import_db.py
```

```powershell
E:\anaconda\envs\huatai-agent\python.exe -m huatai_query_agent.retrieval.build_vector_index
```

校验数据库：

```powershell
E:\anaconda\envs\huatai-agent\python.exe huatai_query_agent\data\validate_db.py
```

## 运行 Agent

运行全部官方样例，稳定 demo 模式：

```powershell
E:\anaconda\envs\huatai-agent\python.exe -m huatai_query_agent.agent.run_agent --all --preview 2
```

运行单条样例：

```powershell
E:\anaconda\envs\huatai-agent\python.exe -m huatai_query_agent.agent.run_agent --query-id q005 --preview 5
```

运行 LLM 模式：

```powershell
E:\anaconda\envs\huatai-agent\python.exe -m huatai_query_agent.agent.run_agent --query-id q001 --sql-mode llm --preview 2
```

## 运行自动化评测

标准 SQL vs Agent SQL：

```powershell
E:\anaconda\envs\huatai-agent\python.exe huatai_query_agent\evaluation\run_agent_eval.py --sql-mode demo --preview 2 --strict-result-match
```

扩展变体评测集：

```powershell
E:\anaconda\envs\huatai-agent\python.exe huatai_query_agent\evaluation\run_agent_eval.py --sql-mode demo --case-set all --preview 2 --strict-result-match
```

预期：

```text
agent_executable_rate[demo]=7/7 (100.00%)
agent_exact_match_rate[demo]=7/7 (100.00%)
agent_row_count_match_rate[demo]=7/7 (100.00%)
```

围栏/幻觉抑制评测：

```powershell
E:\anaconda\envs\huatai-agent\python.exe huatai_query_agent\evaluation\run_guardrail_eval.py
```

预期：

```text
guardrail_expectation_match_rate=10/10 (100.00%)
```

## 启动 Web 演示

```powershell
E:\anaconda\envs\huatai-agent\python.exe -m huatai_query_agent.web.server --host 127.0.0.1 --port 8501
```

打开：

```text
http://127.0.0.1:8501
```

页面可展示：

- 自然语言输入和官方样例选择
- 查询结果表格
- SQL Plan 和候选 SQL
- LangGraph Trace
- SQL 安全围栏状态
- 元数据召回上下文
- M5 评测报告

## Git 提交里程碑

```text
7f1545e add local web demo workbench
3d30fda add automated evaluation pipeline
f26de52 split llm agent nodes and guardrails
ae70038 integrate deepseek llm sql generation
8dbe076 implement hybrid metadata retrieval
fc9b80a document huatai agent environment
7b75b2a init project docs and m1 agent skeleton
```

## 下一步

建议继续做答辩交付打磨：

- 整理 PPT 架构图和状态图；
- 固化演示顺序；
- 如有本地模型网关，运行 `llm` 模式扩展评测并归档报告。
