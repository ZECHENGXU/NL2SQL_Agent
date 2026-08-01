# Web Demo M6

本目录包含华泰 Agentic 问数系统的本地浏览器演示工作台。

该演示使用 Python 标准库 HTTP server 和原生 HTML/CSS/JS，不需要 Streamlit、Node.js 或前端构建步骤。

## 运行

从项目根目录执行：

```powershell
E:\anaconda\envs\huatai-agent\python.exe -m huatai_query_agent.web.server --host 127.0.0.1 --port 8501
```

打开：

```text
http://127.0.0.1:8501
```

## 视图

- 查询控制：选择 `demo` 或 `llm`，输入问题或选择官方样例。
- SQL 确认：先生成并校验候选 SQL，用户明确确认后才执行。
- 结果：最终回答和结果预览。
- SQL：SQL plan 和候选 SQL。

## LLM 模式

如果 `.env` 指向 DeepSeek 官方云等云端 API，页面在运行 `llm` 模式前需要显式确认。这是有意设计，因为 Prompt 元数据、问题上下文、SQL plan 和结果摘要可能会发送给已配置的服务商。

选择 `llm` 模式时，页面会检查已配置 API 是否可达以及模型是否存在。检查失败时会在 SQL 生成前停止，并直接显示连接或模型错误，不再进入空 SQL 校验和修复流程。

点击 SQL 模式选择器旁的“测试 LLM”，可绕过健康检查缓存，立即重新检查连通性和模型可用性。

## 查询流程

1. 点击“生成 SQL”，完成意图解析、元数据检索、SQL 规划、生成和 SQL 校验。
2. 在 SQL 页签检查候选 SQL。
3. 点击“执行 SQL”，后端会再次校验并执行该条服务器端 SQL。
