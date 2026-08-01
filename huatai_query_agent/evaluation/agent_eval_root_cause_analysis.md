# 81 道完整 LLM 评测根因分析与解决方案

## 1. 分析范围

本报告基于 `deepseek-v4-pro` 对 81 道题的完整 LLM 评测：official 7 题、extended 14 题、synthetic 30 题、advanced 30 题。全程共 360 次 LLM 调用，消耗 2,302,907 tokens。原始依据为 `agent_eval_report_all_llm.md` 与 `agent_eval_results_all_llm.csv`。

分析时区分三类来源：

1. **Agent 缺陷**：意图、槽位、SQL 计划、生成、校验或结果验证存在问题。
2. **评测器缺陷**：评分不能正确区分别名、列顺序、数值精度和真正的业务错误。
3. **测试题缺陷**：问题未声明标准 SQL 隐含使用的分段、排序或输出口径。

## 2. 总体结论

| 指标 | 结果 |
|---|---:|
| 候选 SQL 可独立执行 | 68/81，83.95% |
| 行数匹配 | 60/81，74.07% |
| 严格列名及列顺序匹配 | 8/81，9.88% |
| 严格有序结果匹配 | 5/81，6.17% |
| 忽略行顺序后的值匹配 | 15/81，18.52% |

“可执行”表示评测器取得 `candidate_sql` 后直接在 DuckDB 执行成功，不等同于 Agent 端到端完成查询。`a027` 的候选 SQL 可以执行，但 Agent 自身的 SQL 校验器将其误判并转入人工复核，因此端到端成功数实际少于 68。

主要瓶颈按影响排序如下：

1. **完整问题被错误判为需要澄清**：13 题没有生成 SQL，其中高级题 12 题。
2. **缺少刚性的输出列契约**：51 题被归为列不匹配，其中 32 题确实漏列或多列。
3. **复杂口径没有结构化进入 SQL 计划**：快照日期、缺失值、母集、窗口分区和 Top N 资格条件容易漂移。
4. **SQL 校验器不了解 CTE 输出血缘**：`a027` 被误杀。
5. **评测指标过于单一且题目存在隐含口径**：严格命中率低估部分语义正确结果，也掩盖部分实质错误。

因此，下一阶段重点应是增加“意图到 SQL 之间的结构化契约和确定性校验”，而不是只更换更大的模型或继续堆叠自然语言提示词。

## 3. 问题一：完整查询被错误阻断

### 3.1 现象

13 题没有生成 SQL：

`s028, a002, a004, a006, a008, a013, a018, a020, a022, a024, a025, a026, a029`

所有题都走了相同路径：

```text
parse_intent -> retrieve_metadata -> fill_slots ->
check_intent_slots -> ask_clarification -> persist_state
```

其中 12 题来自 advanced 集，且多数已经明确给出日期、指标、分组、筛选、缺失值、排序和 Top N 口径。例如：

- `a004` 明确了客户母集、七项营业部指标、缺失值按 0、分公司内 `dense_rank` 和 Top 3。
- `a022` 明确了月度粒度、普通/信用账户、月末最后可用日期、`FULL OUTER JOIN` 和 `LAG`。
- `a025` 明确了客户等级内 `NTILE(4)`、各项指标、字典翻译和缺失值政策。
- `s028` 只是“3 月 31 日信用账户持仓按等级统计”，也被错误阻断，说明问题不限于长文本。

### 3.2 根因

1. `fill_slots` 直接接受 LLM 返回的任意 `missing_slots`，没有确定性复核。
2. `route_after_slot_check` 只判断列表是否非空，一个低风险不确定项也会立即触发澄清。
3. Prompt 中“信息不足时返回 missing_slots，不要猜测”偏保守，但没有区分真正阻断项、可采用默认值的假设和仅影响展示的低风险不确定项。
4. `ask_clarification` 仍返回“当前 M1 只支持 7 条样例”的旧文案，与已经开放的 LLM 查询能力不一致。
5. 复杂度越高，模型越容易把“需要推导的实现细节”误判为“用户没有提供的信息”。

### 3.3 解决方案

**P0：重构槽位状态。**

```json
{
  "blocking_missing_slots": [],
  "assumptions": [],
  "non_blocking_uncertainties": []
}
```

只有缺失信息会改变查询目标、关键筛选范围或核心业务口径，并且无法从元数据默认规则得到时，才允许进入 `blocking_missing_slots`。

**P0：增加确定性完整性检查器。**

澄清前从原问题和结构化意图检查查询粒度、时间、维度/指标、实体、筛选、排序、Top N、NULL 和缺失值规则。如果 LLM 声称某项缺失，而原文或元数据中已经存在，则删除该 missing slot 并记录审计告警。

**P0：增加批处理模式。**

评测和离线批处理使用 `continue_with_assumptions=True`。非阻断不确定性进入 assumptions 后继续生成 SQL；交互式生产模式仍可对真正的阻断信息澄清。

**P1：澄清前二次验证。**

用轻量 verifier 判断“该缺失项是否会产生两条业务含义不同的 SQL”，只有答案为是时才澄清。

### 3.4 验收标准

- 13 个 no-SQL 用例中，除非人工复审确认题目确实不完整，否则都必须进入 SQL 计划阶段。
- 同样输入重复 3 次，阻断决策一致。
- 澄清回复不再出现“只支持 7 条样例”的过时文案。

## 4. 问题二：输出列契约缺失

### 4.1 现象与拆分

51 题被归类为 `column_mismatch`，内部实际有三种情况：

| 子类 | 数量 | 含义 |
|---|---:|---|
| 输出列数量不同 | 32 | 确实漏字段或添加了额外字段 |
| 列数相同、值也相同 | 7 | 主要是别名不同，业务结果基本正确 |
| 列数相同、值不同 | 12 | 包含字典未翻译、列顺序错误和实质口径错误 |

7 个“值一致、仅列契约不同”的用例为：`v001, v007, s022, s025, a001, a016, a030`。

典型真实漏列：

| 用例 | 标准/Agent 列数 | 问题 |
|---|---:|---|
| `q003` | 7/2 | 漏持仓市值、期初/期末资产、流入、流出 |
| `q005` | 3/1 | 漏招行交易额和平安持仓市值 |
| `q006` | 4/3 | 漏客户数 |
| `q007` | 4/3 | 漏营业部交易总额 |
| `s003` | 4/2 | 漏客户数和平均资产 |
| `a003` | 10/9 | 漏客户姓名 |
| `a005` | 8/5 | 漏姓名、持仓总市值和产品数 |
| `a021` | 12/9 | 漏姓名、组织名称、快照数等 |

### 4.2 根因

1. `SQL_PLAN_PROMPT` 只有 metrics、group_by、order_by，没有逐列 `output_columns`。
2. `expected_metrics` 只记录指标，没有记录标识字段、展示字段、维度和最终列顺序。
3. SQL 生成 Prompt 要求按计划生成，但计划本身没有投影契约。
4. 校验器只验证字段是否合法，没有验证用户要求的列是否全部投影。
5. “列出、输出、补充、同时给出、返回”没有被转换为强制字段列表。
6. 特定英文 snake_case 别名没有稳定来源，模型会选择中文、英文缩写或原始字段名。

### 4.3 同列数但值不同的具体原因

| 用例 | 原因 |
|---|---|
| `s001` | 输出学历编码而非“大专” |
| `s004` | 分层边界相同，但标签文本不同，属于展示合同问题 |
| `s007` | 输出客户等级编码而非中文，并且排序不同 |
| `s009` | 买入、卖出列顺序与标准相反，数值本身正确 |
| `s013` | 输出币种编码而非中文名称 |
| `s014` | 多输出产品 ID，漏持仓客户数 |
| `s018` | 多输出等级编码，漏客户数 |
| `s027` | 按 org_id 分组，标准按营业部名称分组，同名营业部被拆开 |
| `a009` | 用省份和机构 ID 冒充分公司、营业部；还违反“按实际快照平均”的明示口径 |
| `a015` | 业务值一致，主要是别名和浮点精度差异 |
| `a023` | 期初 ETF 市值、买入、卖出三列顺序不同，数值正确 |
| `a028` | 漏客户姓名，额外输出总持仓值 |

### 4.4 解决方案

**P0：增加完整输出契约。**

```json
{
  "output_columns": [
    {
      "expression": "cust.pty_id",
      "alias": "pty_id",
      "semantic_type": "customer_id",
      "required": true,
      "position": 1
    }
  ]
}
```

列表必须包含标识、名称、维度、指标、派生指标和排名字段，不能只含 expected_metrics。

**P0：增加 AST 投影校验器。**

使用 `sqlglot` 解析最外层 SELECT，检查缺失列、多余列、列顺序、别名和指标表达式。发现问题时进入 repair，并明确提供 missing、extra 和 wrong_order 列表。

**P0：测试用例增加 expected_columns。**

每列显式保存 name、semantic_type、required、order、alias_strict 和 display_translation，不能再用标准 SQL 的偶然别名反推唯一输出要求。

**P1：建立字典翻译策略。**

客户等级、性别、学历、币种等面向业务用户时默认翻译；只有用户明确要求编码时才输出代码。

### 4.5 验收标准

- 输出列数量匹配率至少达到 90%。
- 用户明确要求的字段漏列数为 0。
- 纯别名差异在语义指标中通过，严格 schema 指标仍单独报告。

## 5. 问题三：行数不匹配及复杂口径漂移

8 题出现行数不匹配，需要分别处理：

| 用例 | Agent/标准行数 | 直接原因 | 解决方案 |
|---|---:|---|---|
| `v004` | 5/3 | 题目未写年龄边界，Agent 自行分段，标准使用另一套隐含分段 | 明确边界；否则标为多解，不做严格行数比较 |
| `v012` | 6/24 | 只返回一级类别 DISTINCT | 明确一级/二级分类及客户数、市值输出契约 |
| `s017` | 0/6 | 客户快照错误限定为 20260331 | 表级快照政策和日期值域校验；客户表固定 20260531 |
| `s029` | 20/15 | 缺少总费用大于 0 的资格条件，机械 LIMIT 20 | plan 增加 eligibility_filters，Top N 前先应用有效母集 |
| `a010` | 73/44 | 额外限定 ccy=0，按 org_id 分区，且缺正市值过滤 | 禁止无依据过滤；结构化窗口和资格条件 |
| `a012` | 20/15 | 为所有营业部补齐 2/3 月并填 0 | 增加 missing_period_policy，题目未要求时不得扩展母集 |
| `a017` | 13/12 | 缺期初记录的客户被 COALESCE 为 0 后纳入 | 双快照比较默认要求两期均存在，不把事实缺失当数值 0 |
| `a019` | 0/20 | 客户表和机构表错误使用 20260331 | 表级日期政策和生成后值域校验 |

### 5.1 共性根因

1. SQL plan 没有保存母集、粒度、资格条件、缺失事实政策和快照政策。
2. `COALESCE` 被过度使用，既处理字段 NULL，也错误填补整条事实记录缺失。
3. 窗口函数没有结构化分区键、排名函数和并列策略。
4. 模型会添加题目未要求的常见过滤，例如 `ccy='0'`。
5. `validate_result` 只检查执行是否成功，空结果也通过，无法发现 `s017/a019` 这种明显异常。

### 5.2 结构化解决方案

SQL plan 应增加：

```json
{
  "population": "客户归属快照中的全部客户",
  "grain": ["up_org_name", "org_name"],
  "snapshot_policy": {
    "ads_cust_info_d": "20260531",
    "dim_branch": "20260531",
    "dws_cust_aset_d": "20260331"
  },
  "missing_fact_policy": {
    "begin_asset": "require_record",
    "trade": "zero_fill_after_customer_aggregation"
  },
  "eligibility_filters": ["total_fee > 0"],
  "window": {
    "function": "row_number",
    "partition_by": ["up_org_name", "org_name"],
    "order_by": ["market_value desc", "prdt_id asc"]
  }
}
```

生成后确定性检查静态表日期、无依据新增过滤、双快照连接策略、Top N 资格条件和窗口定义。

## 6. 问题四：排序差异被当成结果错误

`q004, v008, s006` 的列和无序行值都正确，仅行顺序不同：前两题标准按客户数优先，Agent 按组织地域名称；`s006` 标准按净流入，Agent 按账户来源。自然语言没有明确这些排序，标准 SQL 却包含隐含要求。

解决方案：

- 每题增加 `order_sensitive`。
- 用户明确要求 Top N、排名或时间顺序时严格比较顺序。
- 用户未指定顺序时，以 unordered semantic match 为主语义指标。
- 若标准必须要求顺序，应把规则写进问题。
- SQL plan 使用结构化 order_by，包含表达式、方向、NULL 和 tie-breaker。

## 7. 问题五：SQL 校验器误杀合法 CTE

### 7.1 现象与根因

`a027` 候选 SQL 可在 DuckDB 返回 20 行，但校验器把 `h.hold_cust_cnt`、`t.branch_cnt` 等合法 CTE 投影列报告为未知字段。Agent 两次 repair 后进入人工复核，评测器绕过流程直接执行候选 SQL，因此同时出现 `executable=True` 与 `sql_validation_failed`。

校验器目前跳过 CTE 的物理表映射，后续字段检查只认识物理表 schema，不认识 CTE 投影；`_select_aliases` 还是全局集合，没有 SQL scope 和 lineage。

### 7.2 解决方案

1. 使用 `sqlglot` scope/lineage API 为每个 CTE 构建投影 schema。
2. 限定列的 qualifier 指向 CTE 时，在 CTE 输出列中校验。
3. 无法完整解析只读 SELECT 的 lineage 时，降级为 warning 并允许 DuckDB 只读预执行，不要误阻断。
4. 增加多 CTE、CTE 连接、FULL OUTER JOIN、窗口列、嵌套 CTE 回归测试。
5. 将 `a027` 固化为 validator regression case。

## 8. 问题六：评测器不能准确表达业务正确性

### 8.1 当前问题

当前逻辑严格比较完整列数组和完整行数组，导致：

1. 中文别名、英文别名和缩写全部判错。
2. 列顺序不同与数值错误无法区分。
3. `a015` 仅因浮点类型精度差异也不能匹配。
4. `column_mismatch` 优先级高，掩盖同题中的值错误。
5. candidate_sql 和 standard_sql 未写入 CSV，不利于机器化复盘。
6. 候选 SQL 独立执行成功不代表 Agent 端到端成功。
7. 81 题共用一个 QueryAgent，调用未传独立 thread_id，全部使用 default；上一题摘要进入下一题状态，破坏测试隔离和可复现性。

### 8.2 分层评测方案

应同时报告：

1. `agent_completed`：Agent 是否通过校验并实际执行完成。
2. `candidate_executable`：候选 SQL 绕过 Agent 后能否执行。
3. `projection_arity_match`：列数量是否一致。
4. `strict_schema_match`：列名和顺序是否完全一致。
5. `semantic_schema_match`：按 semantic type 对齐后是否一致。
6. `row_count_match`。
7. `value_match_by_semantic_column`。
8. `unordered_semantic_match`。
9. `ordered_semantic_match`。
10. `strict_exact_match`：保留现有最严格指标。

数值比较应支持字段级容差。金额 Decimal 按小数位或绝对误差；比率使用 `abs(a-b) <= atol + rtol * abs(b)`；NULL 不与 0 混同。

一个题可以有多个 error_tags，例如 missing_output_column、dictionary_not_translated、wrong_snapshot_date、order_only_difference，不再用单一 error_type 掩盖次要错误。

### 8.3 测试隔离修复

```python
state = agent.run(
    question=case.question,
    thread_id=f"eval:{case.query_id}",
)
```

也可为每题新建 Agent，但独立线程可以保留初始化资源复用，成本更低。

## 9. 问题七：测试题存在隐含标准

| 用例 | 隐含标准 | 建议 |
|---|---|---|
| `v004` | 标准年龄分段未写进题目 | 明确边界，或允许多种合理分段 |
| `v012` | “产品类别”实际要求一级+二级分类及两个指标 | 在问题或 output_contract 中明确 |
| `q004/v008` | 标准优先按客户数排序，但问题未要求 | 声明排序，或 order_sensitive=false |
| `s006` | 标准按净流入排序，但问题未要求 | 同上 |
| 多个别名题 | 标准要求特定英文别名，但用户未要求 | 将严格 schema 与语义正确分开评分 |

每个测试用例建议增加：

```yaml
output_contract:
  columns: []
  order_sensitive: false
  numeric_tolerance: {}
  dictionary_translation: true
  null_policy: {}
  missing_fact_policy: {}
  snapshot_policy: {}
  accepted_alternatives: []
```

参考 SQL 继续保留，但不应被视为唯一可能正确的 SQL；评测应以输出合同和语义结果为准。

## 10. 推荐实施路线

### P0：先修阻断和评测可信度

1. 每题使用独立 thread_id。
2. 分离 agent_completed 与 candidate_executable。
3. 拆分 blocking missing slots 和 assumptions，增加澄清前完整性复核。
4. 为计划增加 output_columns，实现投影校验和定向 repair。
5. 加入表级快照日期政策和日期值域校验。
6. 修复 CTE scope/lineage 校验，加入 a027 回归测试。
7. 增加 order_sensitive、浮点容差和语义列比较。

### P1：修复杂业务口径

1. 结构化保存 population、grain、eligibility、missing fact 和 zero-fill 策略。
2. 结构化保存窗口函数、partition、order 和 tie-breaker。
3. 建立字典字段默认翻译规则。
4. 对无依据新增过滤做差异检查。
5. 对预期非空查询的 0 行结果、异常放大行数和缺列触发语义 repair。
6. 将 advanced 的 calculation_notes 真正注入计划或输出合同。

### P2：形成稳定回归体系

1. 按错误标签建立小型确定性回归集。
2. 先跑 validator/evaluator 单元测试，再跑 LLM smoke test，最后跑 81 题全量评测。
3. 保存模型、Prompt、元数据版本、随机性参数、线程 ID 和候选 SQL。
4. 同一模型重复运行 2 至 3 次，报告均值和稳定性。

## 11. 建议验收门槛

完成 P0 后：

- no-SQL 从 13 题降到不超过 2 题；
- CTE validator false positive 为 0；
- 静态维表非法快照日期为 0；
- 输出列数量匹配率不低于 90%；
- 每题线程完全隔离；
- 分别显示端到端完成率和候选 SQL 可执行率。

完成 P1 后：

- advanced 候选 SQL 可执行率至少 90%；
- advanced 端到端完成率至少 85%；
- 语义 schema 匹配率至少 90%；
- unordered semantic value match 至少 80%；
- 所有行数不匹配都有明确 Agent 错误或测试口径标签。

## 12. 最终判断

系统已经具备较强 SQL 语法生成能力，83.95% 的题能产生可独立执行的候选 SQL；但从“能执行”到“严格满足复杂业务请求”之间缺少结构化约束。核心改进闭环应为：

```text
原问题
  -> 可阻断/不可阻断槽位判断
  -> 完整输出合同
  -> 母集、粒度、日期、缺失值和窗口策略
  -> SQL AST 合同校验
  -> 执行结果语义校验
  -> 定向修复
  -> 分层评测
```

按 P0 到 P2 推进后，评测结果才能同时真实反映 Agent 能力、定位失败环节并指导下一轮工程修复。
