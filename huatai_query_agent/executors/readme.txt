本目录封装生成 SQL 的执行能力，为 Agent 提供统一的执行接口和 DuckDB 实现。

文件说明：
- base.py：执行器抽象接口、结果和错误类型。
- duckdb_executor.py：DuckDB SQL 执行器。
- __init__.py：执行器子包初始化文件。
