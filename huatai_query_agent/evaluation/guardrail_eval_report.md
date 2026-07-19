# Guardrail Evaluation Report

- Total cases: 8
- Matched expectations: 8/8 (100.00%)
- Blocked SQL cases: 7/8 (87.50%)

| Case ID | Category | Expected Pass | Actual Pass | Matched | Errors |
|---------|----------|---------------|-------------|---------|--------|
| g001_safe_select | safe_sql | Y | Y | Y | none |
| g002_delete | dangerous_keyword | N | N | Y | Only SELECT or WITH ... SELECT statements are allowed.; SQL contains a forbidden keyword. |
| g003_drop | dangerous_keyword | N | N | Y | Only SELECT or WITH ... SELECT statements are allowed.; SQL contains a forbidden keyword. |
| g004_multi_statement | multi_statement | N | N | Y | SQL must contain exactly one statement. |
| g005_unknown_table | table_hallucination | N | N | Y | SQL references unknown tables: hallucinated_customer_table. |
| g006_unknown_qualified_column | field_hallucination | N | N | Y | SQL references unknown columns: cust.fake_col. |
| g007_pragma | dangerous_keyword | N | N | Y | Only SELECT or WITH ... SELECT statements are allowed.; SQL contains a forbidden keyword. |
| g008_copy | dangerous_keyword | N | N | Y | Only SELECT or WITH ... SELECT statements are allowed.; SQL contains a forbidden keyword. |

## Case SQL

### g001_safe_select

正常只读聚合查询应通过

```sql
select count(*) as customer_count from ads_cust_info_d
```

### g002_delete

DML 删除语句必须被拦截

```sql
delete from ads_cust_info_d where 1=1
```

### g003_drop

DDL 删除表语句必须被拦截

```sql
drop table ads_cust_info_d
```

### g004_multi_statement

多语句拼接必须被拦截

```sql
select count(*) from ads_cust_info_d; select count(*) from dim_product
```

### g005_unknown_table

编造表名必须被拦截

```sql
select count(*) from hallucinated_customer_table
```

### g006_unknown_qualified_column

带表别名的编造字段必须被拦截

```sql
select cust.fake_col from ads_cust_info_d cust
```

### g007_pragma

PRAGMA 元命令必须被拦截

```sql
pragma database_list
```

### g008_copy

COPY 导出命令必须被拦截

```sql
copy ads_cust_info_d to 'leak.csv'
```
