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
# HUATAI_RERANKER_MODEL=BAAI/bge-reranker-base
HUATAI_RERANKER_BATCH_SIZE=8
HUATAI_RERANKER_MAX_LENGTH=512
HUATAI_RERANKER_DEVICE=cpu
HUATAI_RERANKER_FAIL_OPEN=true
HUATAI_RERANKER_FUSION_WEIGHT=0.5
HUATAI_RERANKER_FUSION_RRF_K=60
```

设为 `HUATAI_RERANKER_PROVIDER=disabled` 可以保留 RRF、关闭精排。启用
`fail_open` 时，模型加载或推理失败会保留原 RRF 顺序，并在结果的
`details.reranker` 中记录 `fallback` 状态。

Cross-Encoder 原始分数不与关键词、向量分数直接相加。系统将模型打分
转换为候选名次，再以 reciprocal-rank 贡献加入原 RRF 分数，从而保留
首阶段检索先验并限制纯模型重排造成的召回波动。

默认只对最终输出窗口内的 RRF 候选重新排序，不扩大 Cross-Encoder 的
候选窗口，因此 Top 16 的候选集合保持不变。需要实验更激进的精排召回时，
可以通过 `HybridMetadataRetriever(rerank_candidate_multiplier=3)` 扩大窗口。

完整的 30 题 A/B 过程、被否决方案、最终指标和延迟见
[`../evaluation/retrieval_reranker_ab_report.md`](../evaluation/retrieval_reranker_ab_report.md)。

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
