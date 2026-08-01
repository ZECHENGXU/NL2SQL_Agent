# Full LLM Evaluation Summary

## Run Configuration

- Model: `deepseek-v4-pro`
- Case set: `all`
- SQL mode: `llm`
- Cases: 81
- Wall time: 8568.2 seconds (about 2 hours 22 minutes 48 seconds)
- LLM calls recorded: 360
- Prompt tokens: 1,767,975
- Completion tokens: 534,932
- Total tokens: 2,302,907

All reference SQL was validated against the local DuckDB database before this run.

## Overall Results

| Metric | Result | Rate |
|---|---:|---:|
| Executable candidate SQL | 68 / 81 | 83.95% |
| Exact result match | 5 / 81 | 6.17% |
| Row-count match | 60 / 81 | 74.07% |
| Column match | 8 / 81 | 9.88% |
| Ordered row-value match | 10 / 81 | 12.35% |
| Unordered row-value match | 15 / 81 | 18.52% |

## Results By Case Set

| Case set | Cases | Executable | Exact | Row-count match | Column match | Calls | Tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| Official | 7 | 7 (100.00%) | 1 (14.29%) | 7 (100.00%) | 2 (28.57%) | 36 | 218,219 |
| Extended variants | 14 | 14 (100.00%) | 1 (7.14%) | 12 (85.71%) | 2 (14.29%) | 71 | 422,962 |
| Synthetic | 30 | 29 (96.67%) | 3 (10.00%) | 27 (90.00%) | 4 (13.33%) | 146 | 871,255 |
| Advanced | 30 | 18 (60.00%) | 0 (0.00%) | 14 (46.67%) | 0 (0.00%) | 107 | 790,471 |

Exact matches: `q001`, `v002`, `s012`, `s015`, `s019`.

## Failure Breakdown

| Result class | Cases |
|---|---:|
| Column mismatch | 51 |
| Agent produced no SQL | 13 |
| Row-count mismatch | 8 |
| Exact match | 5 |
| Row-value mismatch | 3 |
| SQL validation failure | 1 |

The 13 non-executable cases were `s028`, `a002`, `a004`, `a006`, `a008`, `a013`, `a018`, `a020`, `a022`, `a024`, `a025`, `a026`, and `a029`. All followed the same route: intent parsing and slot filling completed, `check_intent_slots` found unresolved information, and the Agent entered `ask_clarification` without generating SQL.

## Main Findings

1. SQL executability is substantially stronger than strict result equivalence. The Agent generated executable SQL for 83.95% of cases, but only 9.88% matched the required output columns and aliases. Column mismatch was the dominant failure class.
2. Difficulty stratification is effective. Executability fell from 96.67% on the synthetic set to 60.00% on the advanced set; advanced exact match was 0%.
3. Long, fully specified business requests are sometimes treated as incomplete. Twelve of the 30 advanced cases stopped at `ask_clarification`, despite the reference questions defining their calculation rules.
4. `a027` executed successfully when evaluated directly, but the Agent guardrail reported unknown CTE-projected alias columns and routed it to human review. This is a validator false positive rather than a DuckDB execution failure.
5. The strict exact-match score should be read together with row-count and unordered row-value metrics. Many candidate queries returned the expected number of rows but used different aliases, omitted requested display fields, or changed output ordering.

## Artifacts

- Full Markdown report: `agent_eval_report_all_llm.md`
- Machine-readable results: `agent_eval_results_all_llm.csv`
