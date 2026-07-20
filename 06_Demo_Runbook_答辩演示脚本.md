# 答辩演示脚本

> 目标：用 5-8 分钟展示“自然语言 -> Agent 推理 -> SQL -> 安全围栏 -> 真实数据库结果 -> 自动化评测”的完整闭环。

---

## 一、演示前检查

进入项目目录：

```powershell
cd "E:\HKUST\农行杯\01-金融大模型与智能体赛道-华泰证券-Agentic智能问数在客户营销场景的应用"
```

确认环境：

```powershell
E:\anaconda\envs\huatai-agent\python.exe --version
```

确认数据库和配置存在：

```powershell
Test-Path .env
Test-Path huatai_query_agent\data\cust_data.duckdb
```

确认 demo 基线：

```powershell
E:\anaconda\envs\huatai-agent\python.exe huatai_query_agent\evaluation\run_agent_eval.py --sql-mode demo --preview 2 --strict-result-match --no-write-report
```

确认围栏评测：

```powershell
E:\anaconda\envs\huatai-agent\python.exe huatai_query_agent\evaluation\run_guardrail_eval.py --no-write-report
```

---

## 二、启动 Web 工作台

```powershell
E:\anaconda\envs\huatai-agent\python.exe -m huatai_query_agent.web.server --host 127.0.0.1 --port 8501
```

浏览器打开：

```text
http://127.0.0.1:8501
```

讲解口径：

> 这是本项目的本地答辩工作台。它不只是聊天框，而是展示完整 Agent 问数链路：自然语言输入、SQL Plan、候选 SQL、LangGraph Trace、安全围栏、元数据召回和真实数据库结果。

---

## 三、演示 1：简单客户圈选 q001

选择样例：

```text
q001 学历本科以上的男性客户，年龄超过50岁的有多少个？
```

使用：

```text
SQL 模式：Demo
```

点击：

```text
运行问数
```

预期结果：

```text
customer_count = 75
```

讲解口径：

> 这个问题是客户圈选。系统将“本科以上”“男性”“年龄超过50”映射为客户画像表中的学历编码、性别编码和年龄字段，生成只读 SQL，并连接 DuckDB 返回真实结果。

需要展示的页面区域：

- 结果：客户数 75；
- SQL：`ads_cust_info_d`，`edu_cd in (...)`，`gender_cd='5000002'`，`cust_age > 50`；
- Trace：从 `parse_intent` 到 `execute_sql` 的完整链路；
- 围栏：SQL 校验通过。

---

## 四、演示 2：复杂交叉筛选 q005

选择样例：

```text
q005 2026年Q1交易过招商银行A股，并且在Q1末普通账户持有中国平安A股的客户有哪些？
```

使用：

```text
SQL 模式：Demo
```

预期结果：

```text
客户号：C000000000000050
```

讲解口径：

> 这个问题涉及交易事实表、持仓事实表和产品维表。Agent 需要同时理解 Q1 交易区间、Q1 期末持仓日期、普通账户、招商银行 A股、中国平安 A股，并通过客户号做交叉筛选。

需要展示的页面区域：

- SQL Plan：涉及 `dwd_cust_tran_d`、`dwd_cust_hold_d`、`dim_product`；
- SQL：两个 CTE 分别处理交易客户和持仓客户；
- 元数据：展示召回的表、指标和产品术语 context ids；
- 结果：返回客户列表。

---

## 五、演示 3：LLM 多节点路径

如需展示 DeepSeek 生成链路，切换：

```text
SQL 模式：LLM
```

如果 `.env` 指向 DeepSeek 官方云 API，页面会要求勾选：

```text
允许云端 LLM 接收问题、元数据上下文和结果摘要
```

推荐问题：

```text
男性客户有多少个？
```

预期结果：

```text
318
```

讲解口径：

> LLM 模式不是一次性生成 SQL，而是拆成意图解析、元数据检索、槽位补全、SQL 规划、SQL 生成、SQL 校验、真实执行、结果解释。每个节点都写入状态和 trace，因此可观测、可复核、可评测。

注意：

- 云 API 会外发上下文，正式金融环境建议切到本地模型网关；
- 如果现场网络不稳定，保留 demo 模式作为稳定演示路径。

---

## 六、演示 4：安全围栏与幻觉抑制

在终端运行：

```powershell
E:\anaconda\envs\huatai-agent\python.exe huatai_query_agent\evaluation\run_guardrail_eval.py --no-write-report
```

预期：

```text
guardrail_expectation_match_rate=8/8 (100.00%)
```

讲解口径：

> 幻觉抑制不是只靠 Prompt，而是三层机制：生成前强制结构化 JSON 和元数据上下文，执行前用 `sqlglot` 做 SQL AST 解析和表字段白名单校验，执行后只基于真实 DuckDB 结果解释。

可强调的拦截案例：

- `delete from ads_cust_info_d where 1=1`
- `select count(*) from hallucinated_customer_table`
- `select cust.fake_col from ads_cust_info_d cust`
- `select ...; select ...`

---

## 七、演示 5：自动化评测报告

在 Web 页面打开：

```text
评测报告
```

或终端运行：

```powershell
E:\anaconda\envs\huatai-agent\python.exe huatai_query_agent\evaluation\run_agent_eval.py --sql-mode demo --preview 2 --strict-result-match --no-write-report
```

预期：

```text
agent_executable_rate[demo]=7/7 (100.00%)
agent_exact_match_rate[demo]=7/7 (100.00%)
agent_row_count_match_rate[demo]=7/7 (100.00%)
```

讲解口径：

> 我们不是只展示一两条成功案例，而是把官方样例做成自动化评测集。系统会同时执行标准 SQL 和 Agent SQL，并比较可执行率、结果一致率、行数一致率、列一致率和错误类型。

---

## 八、答辩问答口径

### 为什么用 LangGraph？

> 金融问数需要可控流程，不适合让模型自由决定工具调用顺序。LangGraph 可以显式表达状态图，把意图解析、元数据检索、SQL 生成、校验、执行、修复和输出都拆成可审计节点。

### 为什么用 DuckDB？

> DuckDB 适合本地原型和比赛演示，能直接把 CSV 导入成真实数据库，执行标准 SQL 并返回结果。代码中通过 Executor 抽象封装，后续可以替换为企业数仓或 PostgreSQL/ClickHouse。

### LangChain 在哪里？

> 本项目不使用 LangChain 高层 Agent 做主流程。LangGraph 负责编排，模型调用和工具封装保持 OpenAI-compatible 接口，必要时可接 LangChain 的 Prompt、Retriever 和 Tool 生态。

### 怎么防幻觉？

> 第一，SQL 生成前必须通过元数据检索和结构化 SQL Plan；第二，执行前做只读、危险关键字、多语句、表白名单、字段白名单校验；第三，结果解释只能基于真实执行结果。

### 为什么不是全多 Agent？

> MVP 阶段单主 Agent 更稳定，金融场景优先准确、可审计、可评测。多 Agent 后续可以用于 SQL 修复、元数据解释和评测归因等低风险扩展点。

---

## 九、故障兜底

### Web 页面打不开

检查端口是否占用，换端口启动：

```powershell
E:\anaconda\envs\huatai-agent\python.exe -m huatai_query_agent.web.server --host 127.0.0.1 --port 8502
```

### LLM 模式失败

先检查 DeepSeek 连接：

```powershell
E:\anaconda\envs\huatai-agent\python.exe -m huatai_query_agent.llm.check_connection
```

如果网络或云 API 不稳定，切回：

```text
SQL 模式：Demo
```

### Qdrant 索引异常

重建索引：

```powershell
E:\anaconda\envs\huatai-agent\python.exe -m huatai_query_agent.retrieval.build_vector_index
```

### 数据库缺失

重新导入：

```powershell
E:\anaconda\envs\huatai-agent\python.exe huatai_query_agent\data\import_db.py
```
