# 数据层

本目录包含竞赛原型所需的脚本和生成的本地数据库文件。

- `import_db.py`：将原始 CSV 文件导入 DuckDB。
- `validate_db.py`：校验行数、字段和数据库基础可用性。
- `cust_data.duckdb`：生成的本地 DuckDB 数据库文件。该文件不是通过补丁创建的，需要运行 `import_db.py` 生成。

源 CSV 文件保留在 `../原始文件/`。
