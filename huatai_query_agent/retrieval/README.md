# Metadata Retrieval M2

This package implements the M2 metadata retrieval layer:

- YAML chunk construction from `metadata/*.yaml`.
- Local keyword retrieval.
- Qdrant Local vector index.
- Hybrid context assembly for Agent nodes.

The current embedding implementation is `HashingEmbedding`, a deterministic local fallback. It is intentionally swappable with a real local embedding API, such as `bge-m3`, in the next model-integration stage.

## Build Qdrant index

```powershell
conda activate huatai-agent
python -m huatai_query_agent.retrieval.build_vector_index
```

Direct environment Python:

```powershell
& "E:\anaconda\envs\huatai-agent\python.exe" -m huatai_query_agent.retrieval.build_vector_index
```

## Search

```powershell
python -m huatai_query_agent.retrieval.search_metadata "2026年Q1交易过招商银行A股，并且在Q1末普通账户持有中国平安A股的客户有哪些？"
```

Expected q005 context should include:

- `dwd_cust_tran_d`
- `dwd_cust_hold_d`
- `dim_product`
- `transaction_amount`
- `example_sql.q005`
