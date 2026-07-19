# DuckDB 数据库选型调研文档

> 项目：华泰证券 Agentic 智能问数在客户营销场景的应用  
> 版本：v1.1  
> 日期：2026-07-19  
> 结论：原型阶段推荐使用 DuckDB 作为本地分析型SQL执行引擎；生产化阶段保留替换为企业数仓、PostgreSQL 或 ClickHouse 的能力。

---

## 一、调研结论

针对本赛题当前阶段，DuckDB 是较优选择，但不是所有阶段的唯一最优解。

本项目当前目标是构建一个竞赛原型系统，核心要求包括：
- 使用赛题提供的本地 CSV 脱敏数据；
- 跑通 7 条样例问答；
- 支持自然语言生成 SQL 后真实执行；
- 快速展示结果、SQL、业务口径和评测结果；
- 降低本地部署和演示复杂度。

在这些约束下，DuckDB 的优势非常明显：它是嵌入式分析型数据库，不需要单独部署数据库服务，能直接读取或导入 CSV，支持复杂 SQL、CTE、聚合分析，适合本项目这种几十 MB 到数百 MB 级别的本地 OLAP 查询。

但如果未来进入生产环境，面对多用户并发、权限体系、审计留痕、统一数据治理、实时数据接入等要求，应优先考虑企业数仓、PostgreSQL、ClickHouse 或公司现有数据平台。DuckDB 在本项目中应定位为“原型执行引擎”，而不是“生产最终数据库”。

---

## 二、项目数据与查询特征

### 2.1 当前数据规模

| 表名 | 实测记录数 | 数据特点 |
|------|-----------:|----------|
| ads_cust_info_d | 500 | 客户画像快照 |
| dim_branch | 312 | 营业部维表 |
| dim_product | 334,694 | 产品维表，数据量最大 |
| dim_public | 155 | 公共字典 |
| dws_cust_aset_d | 43,684 | Q1每日资产快照 |
| dws_cust_fin_d | 4,892 | Q1资金流水 |
| dwd_cust_hold_d | 408,150 | Q1持仓快照 |
| dwd_cust_tran_d | 39,060 | Q1交易事实 |

总体规模属于单机本地可轻松承载的数据量。

### 2.2 查询类型

赛题样例SQL主要包括：
- 客户圈选：按客户等级、性别、年龄、学历筛选；
- 聚合统计：按年龄段、营业部、产品分类聚合；
- 多表关联：客户表 + 资产表 + 持仓表 + 交易表 + 产品维表；
- 时间范围筛选：Q1区间、Q1期初、Q1期末；
- 指标计算：总资产、日均资产、交易金额、资金流入/流出、区间盈亏。

这些查询以扫描、过滤、聚合、多表分析为主，属于典型 OLAP 场景，而不是高并发事务写入场景。

---

## 三、候选方案对比

| 方案 | 优点 | 不足 | 是否适合当前阶段 |
|------|------|------|------------------|
| DuckDB | 嵌入式、免服务部署、CSV友好、OLAP性能好、支持复杂SQL、Python集成简单 | 不适合作为多用户生产服务的最终数据库；多进程写入能力有限 | 推荐 |
| SQLite | 极简、单文件、部署方便 | 面向本地应用存储和轻量事务，分析型聚合性能与CSV处理能力不如DuckDB | 不推荐作为主执行引擎 |
| PostgreSQL | 成熟稳定、权限/并发/生态强、适合生产服务 | 本地竞赛Demo部署成本更高；分析型CSV原型不如DuckDB轻 | 适合作为生产化备选 |
| ClickHouse | 列式OLAP性能强，适合大规模实时分析 | 对当前几十MB数据和单机Demo过重；部署维护复杂度更高 | 适合大规模生产分析备选 |
| Pandas/Polars | 数据处理灵活，上手快 | 不是数据库，不利于Text-to-SQL、SQL校验和真实数据库执行演示 | 可做辅助分析，不适合作为主执行层 |

---

## 四、为什么当前阶段选择 DuckDB

### 4.1 与赛题数据形态高度匹配

赛题提供的是本地 CSV 数据。DuckDB 官方文档明确支持直接读取 CSV，也支持通过 `CREATE TABLE AS SELECT * FROM 'file.csv'` 或 `COPY` 导入为数据库表。这正好满足“快速把赛题CSV变成可查询数据库”的需求。

对本项目来说，这意味着：
- 不需要安装和配置数据库服务器；
- 不需要复杂ETL；
- 可以快速把 8 张 CSV 导入成 8 张真实 SQL 表；
- 方便后续用同一套 SQL 执行7条样例和评测集。

### 4.2 查询模式是分析型而非事务型

DuckDB 官方定位是面向分析查询工作负载（OLAP）的数据库。赛题查询大量使用分组聚合、时间范围筛选、事实表扫描、多表关联，正好属于分析型查询。

相比 SQLite 这类更偏本地存储/轻量事务的数据库，DuckDB 对此类分析查询更合适。

### 4.3 原型部署复杂度最低

DuckDB 是嵌入式数据库，不需要启动单独的数据库服务。Python 应用可以直接连接一个 `.duckdb` 文件。

这对竞赛Demo很重要：
- 环境更少；
- 启动更快；
- 演示更稳；
- 迁移方便；
- 出问题时排查链路更短。

### 4.4 便于后续工程化评测

本赛题要求设计“取数评测流程”。DuckDB 很适合做评测执行引擎：
- 批量执行标准SQL和生成SQL；
- 对比执行结果；
- 记录执行耗时；
- 输出准确率、失败原因和错误类型。

用 DuckDB 可以把评测流程做成简单的本地脚本，不依赖外部数据库服务。

---

## 五、DuckDB 的边界与风险

DuckDB 并不是生产阶段的万能选择，需要明确边界。

### 5.1 不适合作为复杂多用户生产系统的唯一数据库

DuckDB 的核心模式是嵌入式、本地进程内执行。官方并发说明中提到，在常规 in-process 模式下，读写并发围绕单进程设计；多进程读写不是它最传统的强项。

因此，如果系统未来需要：
- 多业务人员同时访问；
- 多服务实例并发写入；
- 数据权限体系；
- 统一审计；
- 与企业数据平台同步；
- 高可用部署；

就应考虑 PostgreSQL、ClickHouse 或企业数仓。

### 5.2 样例SQL存在方言迁移工作

赛题样例SQL更接近 PostgreSQL 写法，例如 `to_date(... )::integer` 这类表达式。DuckDB 支持大量SQL能力，但仍需要做少量方言适配。

解决方式：
- 建立 `demo_queries.sql`；
- 将7条样例统一改写为 DuckDB 可执行版本；
- 评测时以 DuckDB 版本作为标准答案。

### 5.3 不替代数据治理

DuckDB 只解决“本地SQL执行引擎”问题，不解决：
- 业务术语治理；
- 指标口径治理；
- 元数据可持续运营；
- LLM幻觉抑制；
- SQL自动评测。

这些仍需要通过元数据、围栏、评测模块完成。

---

## 六、推荐架构定位

### 6.1 原型阶段架构

```
CSV数据文件
   |
   v
DuckDB本地数据库
   |
   v
SQL执行器
   |
   v
Agent问数系统 / 评测脚本 / Streamlit演示页面
```

在完整Agent数据流中，DuckDB只承担“只读SQL执行引擎”职责，不承担元数据检索、向量召回、上下文记忆或模型推理职责：

```text
LangGraph Agent
  -> SQL安全围栏
  -> DuckDBExecutor
  -> cust_data.duckdb
  -> 结果摘要/预览
```

DuckDB查询出的客户明细结果不写入Qdrant，也不进入长期记忆；审计日志只记录SQL hash、行数、耗时和结果checksum，必要时保存脱敏预览。

### 6.2 生产演进架构

```
企业数据平台 / 数仓 / 湖仓
   |
   v
PostgreSQL / ClickHouse / 企业分析数据库
   |
   v
统一权限、审计、指标中心
   |
   v
Agent问数系统
```

### 6.3 代码层设计建议

为了避免被 DuckDB 绑定，执行层应抽象为 `SqlExecutor`：
- `DuckDBExecutor`：原型阶段使用；
- `PostgresExecutor`：生产化备选；
- `ClickHouseExecutor`：大规模OLAP备选。

Agent、元数据、Prompt、围栏、评测、上下文记忆和RAG模块不直接依赖具体数据库，只依赖执行器接口。

---

## 七、答辩建议表述

推荐表述：

> 原型阶段我们选择 DuckDB 作为本地分析型SQL执行引擎，原因是赛题数据以CSV形式提供，查询模式以多表关联、过滤、聚合为主，属于轻量级本地OLAP验证场景。DuckDB 可以免服务部署、快速导入CSV、支持复杂SQL，并便于构建自动化评测流程。  
> 同时我们没有把 DuckDB 作为生产最终架构绑定，而是将SQL执行层抽象成可替换模块。未来若进入生产环境，可平滑替换为企业数仓、PostgreSQL 或 ClickHouse，同时复用上层的元数据、Agent、安全围栏和评测体系。

---

## 八、最终建议

| 阶段 | 推荐数据库 | 原因 |
|------|------------|------|
| 竞赛MVP / 本地Demo | DuckDB | 最快导入CSV，低部署成本，适合OLAP查询和评测 |
| 小规模内部试点 | DuckDB 或 PostgreSQL | 若单机只读分析可继续DuckDB；若多用户服务化则用PostgreSQL |
| 生产级营销问数 | 企业数仓 / PostgreSQL / ClickHouse | 需要权限、审计、并发、治理和稳定运维 |
| 大规模实时分析 | ClickHouse | 更适合大规模列式分析和实时聚合 |

因此，本项目当前开发阶段建议：**使用 DuckDB 作为原型执行引擎，但在架构上保持数据库可替换。**

---

## 九、参考资料

- DuckDB 官方：Why DuckDB  
  https://duckdb.org/why_duckdb
- DuckDB 官方：CSV Import  
  https://duckdb.org/docs/current/data/csv/overview
- DuckDB 官方：Concurrency  
  https://duckdb.org/docs/stable/connect/concurrency.html
- SQLite 官方：Appropriate Uses For SQLite  
  https://www.sqlite.org/whentouse.html
- PostgreSQL 官方：Architectural Fundamentals  
  https://www.postgresql.org/docs/17/tutorial-arch.html
- ClickHouse 官方：Real-Time Data Analytics Platform  
  https://clickhouse.com/clickhouse
