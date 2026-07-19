from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from huatai_query_agent.agent.demo_cases import DemoCaseRepository
from huatai_query_agent.agent.graph import QueryAgent


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the query agent against all demo cases.")
    parser.add_argument("--preview", type=int, default=3, help="Preview rows stored in state.")
    parser.add_argument("--sql-mode", choices=["demo", "llm"], default="demo", help="SQL generation mode.")
    args = parser.parse_args()

    repo = DemoCaseRepository()
    agent = QueryAgent(repo=repo, preview_limit=args.preview, sql_mode=args.sql_mode)
    total = 0
    passed = 0

    print("| Query ID | Status | Rows | Matched Score | Final Answer |")
    print("|----------|--------|-----:|--------------:|--------------|")
    for case in repo.list_cases():
        total += 1
        state = agent.run(query_id=case.query_id)
        result = state.get("execution_result", {})
        ok = bool(result.get("success"))
        if ok:
            passed += 1
        status = "OK" if ok else "FAIL"
        answer = state.get("final_answer", "").replace("|", "/")
        print(
            f"| {case.query_id} | {status} | {result.get('row_count', 0)} | "
            f"{state.get('matched_score', 0):.2f} | {answer} |"
        )

    print()
    print(f"agent_executable_rate[{args.sql_mode}]={passed}/{total} ({passed / total:.2%})")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
