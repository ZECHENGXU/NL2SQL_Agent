from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from huatai_query_agent.agent.demo_cases import DemoCaseRepository
from huatai_query_agent.agent.graph import LANGGRAPH_AVAILABLE, QueryAgent


def _json_default(value: Any) -> str:
    return str(value)


def print_state_summary(state: dict[str, Any], *, as_json: bool = False) -> None:
    if as_json:
        print(json.dumps(state, ensure_ascii=False, indent=2, default=_json_default))
        return

    result = state.get("execution_result", {})
    print(f"query_id={state.get('matched_query_id')}")
    print(f"status={'OK' if result.get('success') else 'FAILED'}")
    print(f"rows={result.get('row_count', 0)} elapsed_ms={result.get('elapsed_ms', 0):.2f}")
    print(f"columns={result.get('columns', [])}")
    print(f"answer={state.get('final_answer', '')}")
    print("preview_rows=")
    for row in result.get("preview_rows", []):
        print(f"  {row}")
    print("trace=")
    for event in state.get("trace", []):
        print(f"  - {event.get('node')}: {event.get('status')} {event.get('message')}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the M1 query agent skeleton.")
    parser.add_argument("--query-id", help="Run one demo query id, for example q001.")
    parser.add_argument("--question", help="Run a natural language question.")
    parser.add_argument("--all", action="store_true", help="Run all 7 demo queries.")
    parser.add_argument("--preview", type=int, default=5, help="Rows to print per query.")
    parser.add_argument("--json", action="store_true", help="Print full state as JSON.")
    args = parser.parse_args()

    repo = DemoCaseRepository()
    agent = QueryAgent(repo=repo, preview_limit=args.preview)
    print(f"langgraph_available={LANGGRAPH_AVAILABLE}")

    if args.all:
        failures = 0
        for case in repo.list_cases():
            print(f"\n=== {case.query_id} ===")
            state = agent.run(query_id=case.query_id)
            print_state_summary(state, as_json=args.json)
            if not state.get("execution_result", {}).get("success"):
                failures += 1
        if failures:
            raise SystemExit(1)
        print("\nall agent demo queries passed")
        return

    if not args.query_id and not args.question:
        raise SystemExit("Use --all, --query-id q001, or --question \"...\".")

    state = agent.run(query_id=args.query_id, question=args.question or "")
    print_state_summary(state, as_json=args.json)
    if not state.get("execution_result", {}).get("success") and not state.get("final_answer"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

