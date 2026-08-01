from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from huatai_query_agent.retrieval.chunk_builder import build_metadata_chunks
from huatai_query_agent.retrieval.embedding import EmbeddingSettings, build_embedding_from_env
from huatai_query_agent.retrieval.qdrant_retriever import DEFAULT_COLLECTION, DEFAULT_QDRANT_PATH, QdrantMetadataStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Qdrant local vector index for metadata chunks.")
    parser.add_argument("--path", type=Path, default=DEFAULT_QDRANT_PATH, help="Qdrant local path.")
    parser.add_argument("--collection", default=DEFAULT_COLLECTION, help="Qdrant collection name.")
    args = parser.parse_args()

    chunks = build_metadata_chunks()
    settings = EmbeddingSettings.from_env()
    embedding = build_embedding_from_env()
    store = QdrantMetadataStore(path=args.path, collection_name=args.collection, embedding=embedding)
    store.rebuild(chunks)
    print(f"built_chunks={len(chunks)}")
    print(f"qdrant_path={args.path}")
    print(f"collection={args.collection}")
    print(f"embedding_provider={settings.provider}")
    print(f"embedding_model={settings.model}")
    print(f"embedding_vector_size={embedding.vector_size}")
    store.close()


if __name__ == "__main__":
    main()
