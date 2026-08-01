本目录存放 Agent、护栏和检索系统的评测案例、运行脚本、结果文件和分析报告。

文件说明：
- agent_evaluator.py：Agent 批量评测、结果汇总和评分逻辑。
- retrieval_evaluator.py：检索与重排评测执行器。
- run_agent_eval.py、run_guardrail_eval.py、run_hard_timeout_eval.py、run_demo_queries.py：不同评测场景的命令行入口。
- validate_case_sql.py：评测案例 SQL 的静态校验工具。
- guardrail_cases.py：护栏测试案例。
- advanced_query_cases.yaml、extended_query_cases.yaml、synthetic_query_cases.yaml、regression_suites.yaml：高级、扩展、合成和回归测试案例；对应 .zh.yaml 为中文版本。
- advanced_expected_results.json、advanced_expected_results.zh.json：高级案例的期望结果。
- retrieval_reranker_ab_report.md、retrieval_reranker_final_ab_results.json：检索重排 A/B 评测报告和最终结果。
- README.md、README.zh.md：评测目录的中英文说明。
- agent_eval_manifest_*.json：各评测批次的运行清单和参数。
- agent_eval_report*.md：各评测批次的详细报告；.zh.md 为中文报告。
- agent_eval_results*.csv：各评测批次的结构化结果；.zh.csv 为中文结果。
- agent_eval_sql_generation_events_*.jsonl：SQL 生成阶段的事件日志。
- agent_eval_summary*.md、agent_eval_root_cause_analysis.md、demo_query_results*.md：汇总、根因分析和演示查询结果。
- guardrail_eval_report*.md、guardrail_eval_results*.csv：护栏评测报告和结果。
