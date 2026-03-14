# Workbook Layout

## Files

- `bookkeeping-config.xlsx`: 全局配置
- `YYYY/YYYY-MM.xlsx`: 月度账本

## Config Workbook

### `categories`

| column | meaning |
|---|---|
| `direction` | `expense` / `income` / `both` |
| `level1` | 一级分类 |
| `level2` | 二级分类 |
| `keywords` | 逗号分隔关键词，用于自动分类 |
| `active` | `TRUE` / `FALSE` |

默认支出分类使用当前用户提供的分类体系；默认收入分类补充：
- `收入 / 工资`
- `收入 / 奖金`
- `收入 / 报销`
- `收入 / 理财`
- `收入 / 红包礼金`
- `收入 / 其他收入`

### `tags`

| column | meaning |
|---|---|
| `tag` | 标签名 |
| `active` | 是否启用 |
| `note` | 说明 |

### `accounts`

| column | meaning |
|---|---|
| `account` | 账户名 |
| `account_type` | 如 `cash` / `bank` / `wallet` |
| `currency` | 默认 `CNY` |
| `opening_hint` | 初始化提示值 |
| `active` | 是否启用 |
| `note` | 说明 |

### `recurring`

| column | meaning |
|---|---|
| `recurring_id` | 唯一 ID |
| `name` | 周期账单名称 |
| `direction` | `expense` / `income` / `transfer` |
| `amount` | 金额 |
| `account` | 普通收支使用 |
| `from_account` | 转出账户 |
| `to_account` | 转入账户 |
| `level1` | 一级分类 |
| `level2` | 二级分类 |
| `tags` | 逗号分隔标签 |
| `note` | 备注 |
| `counterparty` | 交易对象 |
| `merchant` | 商户 |
| `frequency` | `monthly` / `yearly` |
| `interval` | 间隔期数 |
| `month` | 年账单用，1-12 |
| `day` | 记账日 |
| `start_date` | 起始日期 |
| `end_date` | 结束日期，可空 |
| `active` | 是否启用 |
| `last_applied_month` | 最近一次应用到的 `YYYY-MM` |

### `annual_limits`

| column | meaning |
|---|---|
| `year` | 年份 |
| `tag` | 额度对应标签 |
| `limit_amount` | 年度额度 |
| `note` | 说明 |
| `active` | 是否启用 |

### `subscriptions`

| column | meaning |
|---|---|
| `subscription_id` | 稳定订阅 ID |
| `name` | 订阅名称 |
| `vendor` | 服务提供方 |
| `account` | 扣款账户 |
| `amount` | 最近一次金额 |
| `billing_cycle` | `monthly` / `yearly` / 空 |
| `start_date` | 订阅起始日期 |
| `renewal_date` | 下一次续费或当前周期到期日期 |
| `contract_end_date` | 合同结束日期，可空 |
| `status` | `active` / `due` / `expired` |
| `tags` | 逗号分隔标签 |
| `note` | 说明或最近备注 |
| `source_transaction_id` | 最近一次来源交易 ID，可空 |
| `source_recurring_id` | 来源周期账单 ID，可空 |
| `updated_at` | 最近同步时间 |

## Monthly Workbook

### `transactions`

| column | meaning |
|---|---|
| `transaction_id` | 唯一交易 ID |
| `date` | 交易日期 |
| `direction` | `expense` / `income` / `transfer` |
| `amount` | 金额 |
| `account` | 普通收支账户 |
| `from_account` | 转账转出账户 |
| `to_account` | 转账转入账户 |
| `level1` | 一级分类 |
| `level2` | 二级分类 |
| `tags` | 逗号分隔标签 |
| `note` | 备注 |
| `counterparty` | 交易对象 |
| `merchant` | 商户 |
| `category_source` | `manual` / `auto` / `unclassified` |
| `recurring_id` | 周期账单来源，可空 |
| `subscription_name` | 订阅名称覆盖值，可空 |
| `subscription_cycle` | 订阅周期 `monthly` / `yearly`，可空 |
| `subscription_start_date` | 订阅起始日期，可空 |
| `subscription_renewal_date` | 续费/到期日期，可空 |
| `subscription_end_date` | 合同结束日期，可空 |
| `created_at` | 写入时间 |

### `balances`

| column | meaning |
|---|---|
| `account` | 账户 |
| `opening_balance` | 月初余额 |
| `closing_balance` | 月末实际余额 |
| `computed_closing` | 脚本根据交易推导的月末余额 |
| `difference` | `closing_balance - computed_closing` |
| `updated_at` | 最近更新时间 |

### `summary`

保留给脚本写入汇总信息，至少包括：
- 当月收入合计
- 当月支出合计
- 净流入
- 支出按一级分类汇总
- 额度超限提示

## Operational Notes

- 不要直接在月账本里新增未知列。
- 自动分类只能命中现有类别，不能偷加类别。
- 发现更合适的关键词时，优先建议用户更新 `categories.keywords`。
- 发现余额差额时，不要自动插入“修正”交易，除非用户明确要求。
- `query` / `stats` / `update` 都支持按 `transaction_id`、类别、标签、备注、商户、时间范围筛选。
- `update` 在命中多笔账单时，应该先由调用方确认，再使用 `--allow-multiple` 执行。
- `update --set-date` 若跨月，会把交易从原月工作簿移动到目标月工作簿。
- `stats --group-by tag` 会把一笔多标签账单分别计入多个标签分组。
- `subscriptions` 由脚本自动重建，不要手工维护 ID。
