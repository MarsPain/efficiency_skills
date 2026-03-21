---
name: bookkeeping
description: 使用 Excel 管理个人或家庭账本，支持多账户、收入与支出分类、二级分类、标签、备注、自动分类建议、查账、统计、批量修改、月初月末余额、周期性账单、服务订阅追踪、年度标签额度与月度汇总。Use when Codex needs to 记录账单、维护每月账本、更新 Excel 工作簿、按类别/标签/备注/时间查账、做消费统计、精确修改某笔或某批账单、处理订阅/周期账单、追踪服务订阅起始和续费/到期时间、核对账户余额，或基于既有分类体系自动建议类别但不直接扩充类别。
---

# Bookkeeping

## Overview

把账本数据持久化到本地 Excel：
- 把配置保存到 `bookkeeping-config.xlsx`
- 把每个月账单保存到 `YYYY/YYYY-MM.xlsx`
- 始终通过 `uv run python "$LEDGER_SCRIPT" ...` 读写（`LEDGER_SCRIPT` 必须指向 skill 目录下的 `scripts/ledger_excel.py`），避免手工改表导致结构漂移

除用户明确要求外，不要直接修改工作簿结构；优先用脚本更新。

## Script Path

每次执行前先固定脚本绝对路径（不要依赖当前工作目录）：
```bash
BOOKKEEPING_SKILL_DIR="${CODEX_HOME:-$HOME/.codex}/skills/bookkeeping"
LEDGER_SCRIPT="$BOOKKEEPING_SKILL_DIR/scripts/ledger_excel.py"
test -f "$LEDGER_SCRIPT"
```

若 `test -f` 失败，先停止并修正路径；不要退回到其他目录下的同名脚本。

## Core Rules

1. 把所有账本数据放在用户指定根目录下，例如 `Ledger/`。
2. 先确保存在配置工作簿，再写入月度工作簿：
```bash
uv run python "$LEDGER_SCRIPT" bootstrap --root Ledger --month 2026-03
```
3. 相对时间先转成明确日期再执行。例如“最近一个月”先换成 `--date-from YYYY-MM-DD --date-to YYYY-MM-DD`，不要把相对时间原样传给脚本。
4. 录入支出或收入时，必须保存：
- 日期
- 金额
- 方向：`expense` / `income`
- 账户
- 备注或交易说明
- 若是服务订阅，尽量补充订阅周期与起止信息
5. 若用户未指定分类：
- 先基于现有分类和关键词自动分析
- 有高置信候选时自动填入并标记 `category_source=auto`
- 无合适候选时保留空分类，并建议用户补充分类；不要直接新增分类
6. 涉及账户间转移时，不要记成收入/支出；使用 `transfer`。
7. 查账、统计、修改都先缩小范围，再执行写入：
- 单笔修改：优先先 `query` 确认命中的 `transaction_id`
- 批量修改：先 `query`/`stats` 确认范围，再 `update --allow-multiple`
8. 周期性账单、年度额度、账户清单、标签清单、订阅追踪都维护在配置工作簿中。
9. 月初/月末余额维护在当月工作簿的 `balances` sheet 中；创建新月份时优先承接上月期末余额。
10. 同一个 `--root` 下的账本命令必须串行执行；不要并发运行多个 `ledger_excel.py` 命令。
11. 把 `query`、`stats`、`month-report`、`subscription-report` 也视为写操作（当前脚本可能触发修复或重建），同样必须串行。
12. 用户提供的账户名若与配置不一致，先做归一化映射并回显映射结果；未命中时先确认再写入。

## Execution Safety

### 1. 命令副作用分级（按当前脚本行为）

- 明确写入：`bootstrap`、`add`、`transfer`、`set-opening`、`set-closing`、`add-recurring`、`apply-recurring`、`set-limit`、`update`
- 读请求但可能写回：`query`、`stats`、`month-report`、`subscription-report`
- 结论：对同一账本根目录，全部按“可写命令”串行调度

### 2. 执行顺序（标准）

1. `bootstrap`（首次或新月份）
2. 账户名归一化并回显映射
3. 月初余额写入（若用户提供）
4. 收入/支出/转账写入
5. 串行核验：`query --month ...` → `month-report` → `subscription-report`（按需）

### 3. 故障恢复（BadZipFile/文件损坏）

1. 立即停止当前批次后续命令，不要继续写入
2. 备份异常文件（例如重命名为 `*.corrupted-<timestamp>.badzip`）
3. 重新执行 `bootstrap --month YYYY-MM` 重建当月文件
4. 按已确认交易清单串行重放
5. 最后执行一次标准核验顺序

### 4. 账户名归一化（首次建议）

- 默认账户：`现金`、`银行卡`、`支付宝`、`微信`
- 常见映射示例：`招行储蓄卡 -> 银行卡`，`微信钱包 -> 微信`
- 归一化映射必须在输出中显式回显，避免隐式替换

## Workflow

### 1. 初始化账本

首次使用时执行：
```bash
uv run python "$LEDGER_SCRIPT" bootstrap --root Ledger --month 2026-03
```

这会创建：
- `Ledger/bookkeeping-config.xlsx`
- `Ledger/2026/2026-03.xlsx`

默认配置会预置：
- 用户提供的支出分类体系
- 一组基础收入分类
- 常见账户：`现金`、`银行卡`、`支付宝`、`微信`

如果用户要修改类别、标签或账户，优先更新配置工作簿而不是直接改月账单。
首次运行时若用户提供了非标准账户名，先确认映射或新增账户，再执行写入。

### 2. 录入账单

录入普通支出：
```bash
uv run python "$LEDGER_SCRIPT" add \
  --root Ledger \
  --date 2026-03-11 \
  --direction expense \
  --amount 32.5 \
  --account 支付宝 \
  --note "午饭和奶茶" \
  --tags 日常,外食
```

录入收入：
```bash
uv run python "$LEDGER_SCRIPT" add \
  --root Ledger \
  --date 2026-03-11 \
  --direction income \
  --amount 5000 \
  --account 银行卡 \
  --level1 收入 \
  --level2 工资 \
  --note "3 月工资"
```

用户显式给出分类时，优先使用显式分类并校验是否存在于配置。

录入服务订阅时，优先补充订阅信息：
```bash
uv run python "$LEDGER_SCRIPT" add \
  --root Ledger \
  --date 2026-03-11 \
  --direction expense \
  --amount 98 \
  --account 支付宝 \
  --level1 数码数字 \
  --level2 服务订阅 \
  --merchant "Pixlr" \
  --note "Pixlr 月订阅" \
  --tags 软件,订阅 \
  --subscription-name "Pixlr" \
  --subscription-cycle monthly
```

若用户给出了订阅开始日、续费日或合同到期日，也一起传：
- `--subscription-start-date`
- `--subscription-renewal-date`
- `--subscription-end-date`

### 3. 录入转账

账户间转移使用：
```bash
uv run python "$LEDGER_SCRIPT" transfer \
  --root Ledger \
  --date 2026-03-11 \
  --amount 1000 \
  --from-account 银行卡 \
  --to-account 微信 \
  --note "日常消费备用金"
```

这是额外补充的重要能力。若没有转账记录，多账户余额会失真。

### 4. 维护周期性账单

新增月订阅或年订阅：
```bash
uv run python "$LEDGER_SCRIPT" add-recurring \
  --root Ledger \
  --name "Notion 年费" \
  --direction expense \
  --amount 698 \
  --account 支付宝 \
  --level1 数码数字 \
  --level2 服务订阅 \
  --tags 软件,订阅 \
  --frequency yearly \
  --month 9 \
  --day 18 \
  --start-date 2026-09-18 \
  --note "Notion renewal"
```

把某月应发生的周期账单落到月账本：
```bash
uv run python "$LEDGER_SCRIPT" apply-recurring --root Ledger --month 2026-09
```

同一周期账单同一个月只应用一次。

如果该周期账单属于 `服务订阅`，脚本会自动把它写入订阅追踪表。

### 5. 查账

按类别、备注、时间查账：
```bash
uv run python "$LEDGER_SCRIPT" query \
  --root Ledger \
  --direction expense \
  --date-from 2026-02-15 \
  --date-to 2026-03-14 \
  --level1 数码数字 \
  --level2 数码产品 \
  --note-contains 摄影
```

常用筛选维度：
- `--id`：按交易 ID 精确定位
- `--month`：限定某个月，可重复传多个
- `--date-from` / `--date-to`：限定日期范围
- `--direction`
- `--account` / `--from-account` / `--to-account`
- `--level1` / `--level2`
- `--tag`：可重复传，默认要求全部命中
- `--note-contains`
- `--merchant-contains`
- `--counterparty-contains`
- `--text-contains`：跨类别、标签、备注、商户的模糊查找

需要改账时，先查再改。

### 6. 统计

对筛选后的账单做统计：
```bash
uv run python "$LEDGER_SCRIPT" stats \
  --root Ledger \
  --direction expense \
  --date-from 2026-02-15 \
  --date-to 2026-03-14 \
  --level1 数码数字 \
  --level2 数码产品 \
  --tag 摄影 \
  --note-contains 摄影 \
  --group-by month
```

可用分组：
- `none`
- `month`
- `date`
- `account`
- `level1`
- `level2`
- `category`
- `tag`
- `merchant`
- `counterparty`
- `direction`

按 `tag` 分组时，一笔多标签账单会分别计入每个命中的标签分组；解释结果时要明确这一点。

### 7. 修改账单

先按 ID 精确修改：
```bash
uv run python "$LEDGER_SCRIPT" update \
  --root Ledger \
  --id TX-20260311-xxxxxx \
  --set-note "摄影配件" \
  --add-tags 器材
```

批量修改时必须确认范围，再显式允许批量：
```bash
uv run python "$LEDGER_SCRIPT" update \
  --root Ledger \
  --month 2026-03 \
  --level1 数码数字 \
  --level2 数码产品 \
  --tag 摄影 \
  --allow-multiple \
  --add-tags 器材
```

支持的修改项：
- `--set-date`
- `--set-amount`
- `--set-account`
- `--set-from-account` / `--set-to-account`
- `--set-level1` / `--set-level2`
- `--set-tags`
- `--add-tags`
- `--remove-tags`
- `--set-note`
- `--set-merchant`
- `--set-counterparty`
- `--set-subscription-name`
- `--set-subscription-cycle`
- `--set-subscription-start-date`
- `--set-subscription-renewal-date`
- `--set-subscription-end-date`

修改日期跨月时，脚本会自动把交易移动到目标月份并重算两个月的余额。

### 8. 维护月初与月末余额

设置月初余额：
```bash
uv run python "$LEDGER_SCRIPT" set-opening \
  --root Ledger \
  --month 2026-03 \
  --account 支付宝 \
  --amount 2400
```

设置月末实际余额：
```bash
uv run python "$LEDGER_SCRIPT" set-closing \
  --root Ledger \
  --month 2026-03 \
  --account 支付宝 \
  --amount 1832.55
```

查看核对结果：
```bash
uv run python "$LEDGER_SCRIPT" month-report --root Ledger --month 2026-03
```

若 `closing_balance` 与脚本计算出的 `computed_closing` 不一致，优先提示差额，不要静默改写。

### 9. 维护年度标签额度

为标签设置年度额度：
```bash
uv run python "$LEDGER_SCRIPT" set-limit \
  --root Ledger \
  --year 2026 \
  --tag 摄影 \
  --amount 12000 \
  --note "器材和出片相关"
```

查看额度使用情况：
```bash
uv run python "$LEDGER_SCRIPT" limit-report --root Ledger --year 2026
```

额度按标签累计；一笔账单可带多个标签。默认把整笔金额计入命中的每个标签额度，因此给用户解释时要明确这一点。

### 10. 订阅追踪

查看所有订阅：
```bash
uv run python "$LEDGER_SCRIPT" subscription-report --root Ledger
```

查看未来 14 天内到续费/到期日的订阅：
```bash
uv run python "$LEDGER_SCRIPT" subscription-report \
  --root Ledger \
  --status active \
  --due-within 14
```

脚本会把 `level2=服务订阅` 的支出自动汇总到配置工作簿里的额外表格，并尽量追踪：
- 订阅名
- 提供商
- 金额
- 订阅周期
- 起始日期
- 续费/到期日期
- 合同结束日期

若用户没有明确给出订阅周期，脚本会从 `note`、`merchant`、`tags` 中推断 `monthly` 或 `yearly`；仍无法判断时保留为空。

## Auto Categorization

自动分类只使用当前配置中的既有类别与关键词：
- 读取 `categories` sheet
- 在 `note`、`merchant`、`counterparty`、`tags` 中匹配关键词
- 选最高分候选

若无匹配：
- 保留 `level1` / `level2` 为空
- 在输出中给出 `建议新增分类` 或 `建议完善关键词`

若存在多个接近候选：
- 只在分差明显时自动落类
- 否则返回候选列表，等待用户确认

## References

需要查看表结构、字段语义和默认分类时，读取：
- [`references/workbook-layout.md`](references/workbook-layout.md)

## Output Style

- 回复短、交易化、可核对。
- 每次写入后回显：`month / direction / amount / account / category / tags / balance effect`
- 自动分类时明确说明来源：`manual`、`auto`、`unclassified`
- 查账时先给筛选条件，再给命中数，再给关键交易
- 统计时先给时间范围和筛选条件，再给总额、笔数、分组结果
- 修改时先说明命中范围，再说明修改字段和影响笔数
- 订阅追踪时优先指出即将续费/到期的项目
- 涉及额度或余额异常时先报差额，再给下一步命令
