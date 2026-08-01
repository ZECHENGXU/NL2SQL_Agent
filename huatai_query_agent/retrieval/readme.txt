本目录实现元数据检索链路，包括文本切块、关键词/向量召回、混合融合、Embedding 和 Cross-Encoder 重排。

文件说明：
- types.py：检索结果、候选项和诊断信息的数据类型。
- chunk_builder.py：从元数据构建检索文档块。
- keyword_retriever.py：关键词和精确匹配检索。
- embedding.py：Embedding 模型及向量生成。
- qdrant_retriever.py：Qdrant 向量库读写和检索。
- hybrid_retriever.py：精确召回、关键词召回、向量召回和 RRF 融合。
- reranker.py：Cross-Encoder 重排及失败降级逻辑。
- build_vector_index.py：构建元数据向量索引。
- search_metadata.py：命令行元数据检索工具。
- README.md：检索配置、索引构建和运行说明。
- __init__.py：检索子包初始化文件。
