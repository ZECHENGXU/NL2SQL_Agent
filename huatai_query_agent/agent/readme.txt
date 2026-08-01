本目录实现面向业务问数的 Agent 工作流，包括案例仓库、状态管理、图编排、节点逻辑和输出契约。

文件说明：
- __init__.py：Agent 包初始化。
- contracts.py：输出契约推导和 SQL 结果约束校验。
- demo_cases.py：演示案例仓库及案例加载逻辑。
- graph.py：查询 Agent 的图结构和节点编排。
- run_agent.py：命令行运行 Agent 的入口。
- state.py：Agent 状态数据结构。
- nodes/m1_nodes.py：M1 阶段的规划、生成、校验和修复节点。
- README.md、README.zh.md：Agent 模块的中英文使用说明。
