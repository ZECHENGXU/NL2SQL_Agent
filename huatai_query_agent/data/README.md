# Data Layer

This directory contains scripts and generated local database files for the contest prototype.

- `import_db.py`: imports the original CSV files into DuckDB.
- `validate_db.py`: validates row counts, columns, and basic database readiness.
- `cust_data.duckdb`: generated local DuckDB database file. This file is not created by patch; run `import_db.py`.

The source CSV files stay in `../原始文件/`.
