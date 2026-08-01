from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from huatai_query_agent.retrieval.hybrid_retriever import HybridMetadataRetriever


def main() -> None:
    parser = argparse.ArgumentParser(description="Search metadata with YAML + keyword + Qdrant hybrid retrieval.")
    parser.add_argument("query", help="Natural language query.")
    parser.add_argument("--top-k", type=int, default=12)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    retriever = HybridMetadataRetriever()
    try:
        context = retriever.build_context(args.query, top_k=args.top_k)
        if args.json:
            print(json.dumps(context, ensure_ascii=False, indent=2, default=_json_default))
            return

        print(f"query={context['query']}")
        print(f"tables={context['tables']}")
        print(f"metrics={context['metrics']}")
        print(f"terms={context['terms']}")
        print("chunks=")
        for chunk in context["chunks"]:
            print(f"- {chunk['id']} [{chunk['chunk_type']}] {chunk['source']} score={chunk['score']}")
            print(f"  {chunk['text'][:180]}")
    finally:
        retriever.close()


def _json_default(value: Any) -> str:
    return str(value)


if __name__ == "__main__":
    main()
