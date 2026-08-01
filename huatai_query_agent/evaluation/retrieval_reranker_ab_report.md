# 元数据 Reranker A/B 实验报告

评测日期：2026-08-02

## 结论

最终采用的不是“用 Cross-Encoder 分数覆盖 RRF”，而是：

1. 精确匹配结果保持置顶。
2. 关键词和向量候选继续使用 RRF 融合。
3. 仅在最终 Top 16 候选集合内部运行 `BAAI/bge-reranker-base`。
4. Cross-Encoder 原始分数只用于生成名次，再以权重 `0.5` 的
   reciprocal-rank 贡献加入原 RRF 分数。

最终方案保证生产 Top 16 的候选集合、Recall 和 Precision 不发生变化，
同时改善 Top 5/10 的指标前排覆盖。它属于真实 Cross-Encoder rerank，
但保留首阶段检索先验，不直接比较异构原始分数。

## 实验设置

- 评测集：`advanced_query_cases.yaml` 全部 30 题。
- 元数据：143 个 chunk，不包含 `example_sql`。
- 已定义指标：11 个。
- 30 题中有 14 题包含当前元数据可检索的已定义指标。
- Embedding：本地 `bge-small-zh-v1.5`。
- Reranker：本地 `BAAI/bge-reranker-base`，CPU 推理。
- 首阶段候选：关键词 Top 48、向量 Top 48，`rrf_k=60`。
- 生产输出：Top 16。
- A/B 基线：RRF，不启用 reranker。
- A/B 实验：RRF + Cross-Encoder rank fusion。

最终排序公式：

```text
final_score(d) = rrf_score(d) + 0.5 / (60 + cross_encoder_rank(d))
```

Cross-Encoder 的 logit 不与关键词相似度、向量余弦分数直接相加。

## 指标口径

- Schema Table Recall：目标表是否通过 table 或 field chunk 命中。
- Direct Table Recall：目标表是否通过 table chunk 直接命中。
- All Tables Hit：一道题的全部目标表是否命中。
- Defined Metric Recall：只统计当前 11 个指标定义覆盖的预期指标。
- Business Metric Recall：全部预期业务指标均进入分母，未定义指标无法命中。
- Judged Context Precision：table/field、metric，以及两端均属于目标表的
  relationship chunk 记为相关；没有人工标注的 term/time chunk 按严格口径
  不记为相关。
- MRR：第一个相关 chunk 的 reciprocal rank。

## 最终结果

### Top 16：生产上下文

| 指标 | RRF | RRF + Reranker | 变化 |
|---|---:|---:|---:|
| Schema Table Recall | 80.86% | 80.86% | 0.00 pp |
| Direct Table Recall | 69.96% | 69.96% | 0.00 pp |
| 所有 Schema 表命中 | 30.00% | 30.00% | 0.00 pp |
| 所有 Direct 表命中 | 13.33% | 13.33% | 0.00 pp |
| Defined Metric Recall | 100.00% | 100.00% | 0.00 pp |
| 所有已定义指标命中 | 100.00% | 100.00% | 0.00 pp |
| Business Metric Recall | 9.67% | 9.67% | 0.00 pp |
| Judged Context Precision | 55.00% | 55.00% | 0.00 pp |
| MRR | 62.89% | 63.06% | +0.17 pp |

Top 16 的集合型指标完全相同，符合“只在输出集合内部精排”的设计约束。
MRR 的提升来自 `a028`，该题第一个相关 chunk 的 reciprocal rank 提升 5 pp。

### Top 10：头部上下文

| 指标 | RRF | RRF + Reranker | 变化 |
|---|---:|---:|---:|
| Schema Table Recall | 68.62% | 67.88% | -0.75 pp |
| Direct Table Recall | 63.76% | 64.51% | +0.75 pp |
| 所有 Direct 表命中 | 6.67% | 10.00% | +3.33 pp |
| Defined Metric Recall | 57.14% | 64.29% | +7.14 pp |
| 所有已定义指标命中 | 57.14% | 64.29% | +7.14 pp |
| Business Metric Recall | 4.89% | 5.56% | +0.67 pp |
| Judged Context Precision | 54.67% | 54.67% | 0.00 pp |
| MRR | 62.89% | 63.06% | +0.17 pp |

Top 10 的主要收益是指标 chunk 和直接表 chunk 更靠前。`a012` 的 Schema
与 Direct Table Recall 均提升 33.33 pp，`a013` 的 Defined Metric Recall
提升 100 pp。回归主要出现在 `a008`、`a010` 和 `a026` 的表排序。

### Top 5：最前排上下文

| 指标 | RRF | RRF + Reranker | 变化 |
|---|---:|---:|---:|
| Schema Table Recall | 48.76% | 47.65% | -1.11 pp |
| Direct Table Recall | 47.37% | 46.82% | -0.56 pp |
| Defined Metric Recall | 10.71% | 17.86% | +7.14 pp |
| 所有已定义指标命中 | 7.14% | 14.29% | +7.14 pp |
| Judged Context Precision | 59.33% | 59.33% | 0.00 pp |
| MRR | 62.89% | 63.06% | +0.17 pp |

`a018` 的 Defined Metric Recall 提升 100 pp；`a015` 和 `a025` 的
Schema Table Recall 各下降 16.67 pp。由于 Agent 实际消费 Top 16，
这些是集合内部的位置变化，不会导致生产上下文丢失对应 chunk。

## 被否决方案

### 纯 Cross-Encoder 排序

第一版让 Cross-Encoder 对扩大后的候选池直接排序并截取 Top 16。结果：

- Schema Table Recall：-4.73 pp。
- Direct Table Recall：-2.56 pp。
- Defined Metric Recall：-28.57 pp。
- Judged Context Precision：-5.42 pp。
- MRR：-6.02 pp。

模型能够改变排序，但长问题下存在 chunk 类型偏置，不能直接替换 RRF。

### 扩大窗口的融合排序

保留 RRF，并以 Cross-Encoder 名次做融合后，回归明显缩小；但允许 reranker
从 3 倍窗口替换 Top 16 集合时，仍出现约 0.39 pp 的 Schema Recall 下降和
1.67 pp 的 Precision 下降。因此最终将 rerank 窗口限制为输出窗口。

## 延迟与资源

当前机器为 CPU-only：

| 模式 | 单题耗时 |
|---|---:|
| RRF-only | 0.052 s |
| Reranker 冷启动 | 4.67 s |
| Reranker 热启动 | 2.20 s |

- 本地 reranker 运行文件约 1.13 GB。
- 30 题最终 A/B 总耗时 74.4 s，包含隔离索引初始化和模型加载。
- 推理失败时 `fail_open=true` 会保留 RRF 顺序，并在结果中记录 fallback。
- 对延迟敏感的环境可设置 `HUATAI_RERANKER_PROVIDER=disabled`。

## 上线参数

```text
HUATAI_RERANKER_PROVIDER=cross-encoder
HUATAI_RERANKER_BATCH_SIZE=8
HUATAI_RERANKER_MAX_LENGTH=512
HUATAI_RERANKER_DEVICE=cpu
HUATAI_RERANKER_FAIL_OPEN=true
HUATAI_RERANKER_FUSION_WEIGHT=0.5
HUATAI_RERANKER_FUSION_RRF_K=60
```

`HybridMetadataRetriever` 默认使用 `rerank_candidate_multiplier=1`。扩大到 3
只作为实验开关，不作为当前生产默认值。

## 限制

- 本实验评估检索，不代表端到端 SQL 准确率提升。
- 100% Defined Metric Recall 只针对 14 道可由当前指标元数据覆盖的题。
- Business Metric Recall 较低主要是指标定义覆盖不足，不是排序问题。
- 当前 reranker 是通用中文模型，尚未使用华泰元数据相关性样本微调。
- 最终策略刻意保持 Top 16 集合不变，因此主要收益是上下文顺序，而非
  Top 16 召回集合扩张。

机器可读明细见 `retrieval_reranker_final_ab_results.json`。复现脚本：

```powershell
python -m huatai_query_agent.evaluation.retrieval_evaluator `
  --temp-qdrant huatai_query_agent\runtime\retrieval_eval_qdrant `
  --output huatai_query_agent\evaluation\retrieval_reranker_final_ab_results.json
```
