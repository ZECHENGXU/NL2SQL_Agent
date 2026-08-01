# Metadata Retrieval M2 元数据检索

本包实现 M2 元数据检索层：

- 从 `metadata/*.yaml` 构建 YAML chunk。
- 本地关键词检索。
- Qdrant Local 向量索引。
- 精确结果优先固定，关键词与向量候选使用 RRF 融合。
- 使用 Cross-Encoder 对 RRF 候选进行逐对相关性精排。
- 为 Agent 节点组装混合上下文。

当前 embedding 实现是 `HashingEmbedding`，作为确定性的本地兜底方案。它可以在下一阶段模型集成中替换为真实的本地 embedding API，例如 `bge-m3`。

## Reranker 配置

默认 reranker 是 `BAAI/bge-reranker-base`。如果模型已下载到
`retrieval/models/bge-reranker-base`，系统会优先使用本地目录；否则由
`sentence-transformers` 按模型名称加载。可通过环境变量配置：

```text
HUATAI_RERANKER_PROVIDER=cross-encoder
HUATAI_RERANKER_MODEL=BAAI/bge-reranker-base
HUATAI_RERANKER_BATCH_SIZE=8
HUATAI_RERANKER_MAX_LENGTH=512
HUATAI_RERANKER_DEVICE=cpu
HUATAI_RERANKER_FAIL_OPEN=true
```

设为 `HUATAI_RERANKER_PROVIDER=disabled` 可以保留 RRF、关闭精排。启用
`fail_open` 时，模型加载或推理失败会保留原 RRF 顺序，并在结果的
`details.reranker` 中记录 `fallback` 状态。

## 构建 Qdrant 索引

```powershell
conda activate huatai-agent
python -m huatai_query_agent.retrieval.build_vector_index
```

直接使用环境 Python：

```powershell
& "E:\anaconda\envs\huatai-agent\python.exe" -m huatai_query_agent.retrieval.build_vector_index
```

## 检索

```powershell
python -m huatai_query_agent.retrieval.search_metadata "2026年Q1交易过招商银行A股，并且在Q1末普通账户持有中国平安A股的客户有哪些？"
```

预期 q005 上下文应包含：

- `dwd_cust_tran_d`
- `dwd_cust_hold_d`
- `dim_product`
- `transaction_amount`
