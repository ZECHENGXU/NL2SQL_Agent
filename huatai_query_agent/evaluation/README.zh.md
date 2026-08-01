# Evaluation M5 评测

本目录包含华泰 Text-to-SQL Agent 的自动化评测脚本。

- `run_demo_queries.py`：在本地 DuckDB 数据库上执行 `../sql/demo_queries_duckdb.sql` 中的全部 SQL 块，并打印行数和结果预览。
- `run_agent_eval.py`：运行标准 SQL 与 Agent SQL，比较结果，并写出 Markdown/CSV 报告。
- `validate_case_sql.py`：校验生成的参考 SQL，并可导出完整期望结果快照。
- `run_guardrail_eval.py`：检查 SQL 围栏和幻觉抑制用例。

## 标准 SQL vs Agent SQL

```powershell
python huatai_query_agent\evaluation\run_agent_eval.py --sql-mode demo --strict-result-match
```

其他用例集：

`advanced` 集合包含 30 条专家级用例。所有用例都带有能力标签和计算说明，其中 22 条是长文本业务请求。

```powershell
# 7 条官方样例加自然语言变体
python huatai_query_agent\evaluation\run_agent_eval.py --case-set extended --sql-mode demo

# 用于 LLM 泛化评测的 SQL 支撑生成用例
python huatai_query_agent\evaluation\run_agent_eval.py --case-set synthetic --sql-mode llm

# 高难度跨域和长文本用例
python huatai_query_agent\evaluation\run_agent_eval.py --case-set advanced --sql-mode llm

# 合并官方、扩展、合成和高级用例
python huatai_query_agent\evaluation\run_agent_eval.py --case-set all --sql-mode llm

# 校验高级参考 SQL，并写出完整期望结果
python huatai_query_agent\evaluation\validate_case_sql.py --case-set advanced --require-non-empty --snapshot huatai_query_agent\evaluation\advanced_expected_results.json
```

输出：

- `huatai_query_agent/evaluation/agent_eval_report.md`
- `huatai_query_agent/evaluation/agent_eval_results.csv`

关键指标：

- 可执行率
- 精确结果匹配率
- 行数匹配率
- 字段匹配率
- LLM 调用次数和 Token 用量

运行小规模 LLM 评测：

```powershell
python huatai_query_agent\evaluation\run_agent_eval.py --sql-mode llm --query-id q001 --query-id q005
```

如果 `HUATAI_LLM_BASE_URL` 指向云端 API，LLM 评测会向该服务商发送 Prompt 元数据和问题上下文。完整金融数据评测建议使用已批准的本地 OpenAI-compatible 模型网关。

## 围栏评测

```powershell
python huatai_query_agent\evaluation\run_guardrail_eval.py
```

输出：

- `huatai_query_agent/evaluation/guardrail_eval_report.md`
- `huatai_query_agent/evaluation/guardrail_eval_results.csv`

围栏用例覆盖：

- 安全只读 SQL
- DML/DDL 拦截
- 多语句拦截
- 编造表拦截
- 编造限定字段拦截
- PRAGMA/COPY 拦截
