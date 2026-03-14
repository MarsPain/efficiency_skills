---
name: craft-mcp
description: "Connect to Craft via MCP and operate on notes/documents: create pages, append meeting notes, manage daily notes, route and write ARR notes into fixed category documents, run scoped search across folders/documents/daily notes with optional model-generated expansions, summarize evidence-backed findings, organize content, and keep a Craft knowledge base up to date. Use when a user mentions Craft/Craft Docs, MCP, arr笔记, append and review note, The_append_and_review_notes, 笔记/文档/知识库, 会议纪要, 每日笔记, 在指定文件夹/文档/日期范围内检索并总结, 检索并更新 Craft 内容, or wants to write back results into Craft."
---

# Craft MCP

## 前置检查（一次性/必要时）

- 确认已在宿主应用（例如 Codex / ChatGPT Desktop / Claude Desktop 等）里配置并启用 Craft MCP Server。
- 只要用户没有明确说“已经连好了”，先确认是否可见 Craft 相关 MCP 工具。
- 将 Craft MCP URL 视为“可访问整个空间的链接/凭证”，不要在公共渠道传播；除非用户明确授权，不要把 URL 写进仓库或日志。

如需让用户自行配置，按 Craft 官方指引操作（见 `references/craft-mcp-setup.md`）。

若请求涉及 arr 笔记，额外读取 `references/categories.md`。

## 开工前：发现并映射工具

1. 列出当前可用 MCP 工具，并筛出 Craft 相关工具（通常名称包含 `craft`）。
2. 识别并记录能力与动作映射（至少覆盖）：
   - 范围发现：`folders_list`、`documents_list`
   - 粗召回：`documents_search`
   - 细粒度证据提取：`document_search`
   - 全文/块读取：`blocks_get`
   - 创建与更新：`documents_create`、`markdown_add`、`blocks_add`、`blocks_update`
3. 如果缺少“搜索”或“追加”能力：
   - 先问用户目标文档的精确标题/链接/位置；
   - 或改为“创建新文档并引用原文档链接”的保守方案。

## 交互原则（减少误写入）

- 任何会修改既有文档的操作：先用 1 句话复述“将修改哪个文档、以何种方式修改”，再执行。
- 默认采用“追加到末尾”或“在指定标题下追加”，除非用户要求重排全文。
- 不整篇覆盖写回；优先块级/段落级修改（若 MCP 支持）。
- 保留原有排版（标题层级、列表、分隔线）；新增内容沿用原文风格。
- `arr笔记` 是例外：新内容始终写到目标文档顶部，而不是末尾。

## ARR 笔记协议（The Append and Review Notes）

目标：支持 Karpathy 风格的 append-and-review notes，在固定分类文档中将新条目严格插到最上方。

### 1) 触发与范围

- 只要用户提到 `arr笔记`，始终把工作范围锁定到顶层文件夹 `The_append_and_review_notes/`。
- 不在该文件夹外创建、搜索或更新 ARR 内容，除非用户明确撤销这一约束。
- 先在 Craft 中定位这个文件夹；若找不到，再向用户说明缺失并请求更精确的位置或由你创建。

### 2) 文档选择

- ARR 只允许使用 `references/categories.md` 中定义的固定类别文档。
- 将 `思想` 与 `思想.md` 视为同一类别；文档解析时允许用户省略 `.md` 后缀。
- 若用户明确指定类别或文档，始终写入该目标文档。
- 若用户未指定类别，读取 `references/categories.md` 的“路由提示”和“歧义规则”，选择最匹配的固定类别，并在回复中用 1 句话简短说明判断依据。
- 若用户指定的类别不在白名单内，不新增白名单外新类别；改为请用户从白名单中确认，或按最匹配的既有类别处理并说明原因。

### 3) ARR 检索复用规则

- 一旦已经确定 ARR 笔记所在的类别文档，后续如果用户提出搜索、查询、回顾、汇总、对比等需求，改为基于下方“范围检索协议”执行，而不是另起一套检索流程。
- 若用户指定了明确类别或文档，则将 `scope_type` 视为 `document`，`scope` 锁定到该类别文档。
- 若用户只说“arr笔记”但未指定类别，先按本协议完成类别路由；确定类别文档后，再按 `document` 范围执行检索。
- 若用户明确要求跨多个 ARR 类别搜索，则将 `scope_type` 视为 `folder`，`scope` 锁定到 `The_append_and_review_notes/`，再按“范围检索协议”执行。
- 在 ARR 场景下复用“范围检索协议”时，仍优先遵守 ARR 的范围约束：默认不扩展到 `The_append_and_review_notes/` 之外。

### 4) 写入方式

- 每个类别一个单独文档；缺失时在 `The_append_and_review_notes/` 下创建对应类别文档，再继续写入。
- 新笔记一律严格插入到文档顶部，保持“最新在最前”的时间序。
- 优先使用支持页面顶部插入的操作：例如 `markdown_add` 或 `blocks_add` 配合 `position: "start"` 和目标 `pageId`。
- 若工具不支持直接写到页面起始位置，则先读取首块，再用 `before` 插入到首块之前；不要退化为追加到末尾。
- 除非用户明确要求整理或改写，原有历史条目不重排、不覆盖。

### 5) 回复约定

- 执行前先复述：将在哪个类别文档中，以“顶部插入新 block/段落”的方式写入什么内容。
- 若是模型自动路由类别，在执行前附一句简短判断，例如“我会放到 `工程`，因为内容重点是工具链与实现权衡。”

### 6) 示例

- 用户：`arr笔记，以下内容添加到“思想”中：xxx`
- 处理：在 `The_append_and_review_notes/` 中定位 `思想` 文档，并把 `xxx` 作为新 block 插入到页面顶部。

## 范围检索协议（核心）

当用户请求“在 xxx 下搜索 yyy ”时，始终先显式构造检索参数：

- `scope_type`：`folder` / `document` / `daily_notes` / `global`
- `scope`：`folderIds` / `documentIds` / `location` / 日期区间
- `topic`：核心主题词（用户原话）
- `fuzzy_search`：`true` / `false`（默认 `false`；仅在用户明确要求或确认开启时设为 `true`）
- `expansions`：由模型自行分析并生成的同义词、别名、中英文变体、缩写/全称；`fuzzy_search=false` 时留空或仅保留原词
- `time_window`：可选，最近 N 天/周
- `output_style`：摘要、要点、行动项、对比结论

### 1) 范围解析（Scope Resolution）

- 先根据用户措辞判断 `xxx` 的范围类型：
  - 若用户明确说“文件夹 / 目录 / folder”，解析为文件夹范围（`folderIds`）。
  - 若用户明确说“文档 / 页面 / note / doc”，解析为文档范围（`documentIds`）。
  - 若用户明确说“日记 / daily note / daily notes”，或 `xxx` 是明确日期、相对日期或日期区间，只在 `location: "daily_notes"` 内搜索，并加对应日期过滤。
  - 若无法判断 `xxx` 是什么类型，优先视为文件夹范围。
- 若匹配多个候选范围：先返回候选并让用户确认一次。
- 若用户未给范围：默认全空间，但必须在输出里明确写明“全空间检索”。

### 2) 查询扩展（Query Expansion）

- 不把扩展词生成这一步甩给用户；由模型先分析 `topic`，再决定是否生成 `expansions`。
- 若 `fuzzy_search=false`：
  - 仅搜索用户指定的关键词 `yyy`。
  - 不额外加入同义词、别名、中英文变体、缩写/全称。
- 若 `fuzzy_search=true`：至少生成 3 组扩展查询，并优先保留高相关扩展，避免无关发散：
  - 原词：`yyy`
  - 近义/别名：术语别称、团队内部叫法
  - 变体：中英混合、缩写/全称、常见拼写差异

- `fuzzy_search=true` 时的优先顺序：精确词 > include 多词 AND > regex 模糊匹配。

### 3) 两阶段检索（Recall -> Rerank）

- 阶段 A（粗召回）：
  - `fuzzy_search=false`：在 `scope` 内仅用原词执行查询。
  - `fuzzy_search=true`：在 `scope` 内用 `documents_search` 执行多轮查询（原词 + 扩展词）。
  - 合并去重，得到候选文档集。
- 阶段 B（重排）：
  - 按“标题命中 > 内容命中密度 > 最近修改时间”排序。
  - 选 Top-K（默认 8）进入精读。

### 4) 证据提取（Evidence Extraction）

- 对 Top-K 文档使用 `document_search` 提取命中块及上下文（`beforeBlockCount`/`afterBlockCount`）。
- 证据不足时再用 `blocks_get` 读取对应文档局部结构。
- 摘要中的每条结论都要可追溯到来源文档与命中片段。

### 5) 输出格式（Evidence-backed Summary）

默认按以下结构输出：

- 检索范围：文件夹/文档/日期范围
- 模糊搜索：开启 / 关闭
- 检索式：关闭时仅原词；开启时为原词 + 模型生成扩展词
- 命中概览：文档数、精读数、主要主题
- 主题总结：
  - 结论
  - 证据来源（文档标题 + blockId/命中段落）
- 待确认点：证据冲突或信息缺口

## 常用工作流

### 1) 快速记录（Inbox Note）

目标：把用户给的一段碎片想法/清单写入 Craft，便于后续整理。

- 若用户未指定位置：创建新文档，标题用 `YYYY-MM-DD HH:mm` + 简短主题。
- 内容结构：`# 背景`、`# 记录`、`# 下一步`
- 将对话要点转为项目符号；必要时保留关键原话。

### 2) 每日笔记（Daily Note / Worklog）

目标：将工作记录写入指定日期（默认今天）的 Daily Note，支持回溯历史日记并做增量修改，避免信息分散。

- 先解析目标日期（优先级：用户明确日期 > 相对日期 > 默认今天；使用用户时区）。
- 先判断用户的日记体系：
  - 已有 Daily Notes/日志：优先检索并打开目标日期条目（不仅限今天，可搜索和修改历史日期）。
  - 无体系或目标日期条目不存在：直接在 Daily Note 创建该日期条目（通过 `date` 参数写入）；不要先创建普通文档再移动。
- 写入模式：
  - 默认“追加到末尾”；若用户要求修订，则在目标日期条目内做块级/段落级增量修改。
  - 跨日期请求（如“补上周三日志”）按指定日期执行，不回退到今天。
- 追加/修订时优先按小节写入（若不存在则创建）：
  - `## 今日目标`
  - `## 进展`
  - `## 阻塞`
  - `## 学到的`
  - `## 明日计划`

### 3) 会议纪要（Meeting Minutes）

目标：生成结构化纪要并写回 Craft，便于追踪行动项。

- 标题建议：`YYYY-MM-DD 会议纪要 - <会议名>`
- 模板（按需增删）：
  - `## 与会者`
  - `## 议程`
  - `## 讨论要点`
  - `## 结论/决策`
  - `## 行动项`
    - `- [ ] <Owner>：<Action>（Due: YYYY-MM-DD）`
- 若输入是长转写：先给精炼摘要，再写入 Craft，并保留关键引用段落。

### 4) 检索并更新既有笔记（Search -> Read -> Patch）

目标：找到相关文档，读取后做增量更新（补充、纠错、总结、行动项）。

1. 先按“范围检索协议”完成召回与精读。
2. 输出候选及理由；唯一高置信匹配时可直接说明将操作该文档。
3. 完成用户请求（如补缺失小节、加 `## TL;DR`、整理行动项）。
4. 写回遵循：
   - 汇总内容放顶部（`## TL;DR` / `## Summary`）
   - 原文尽量不删改（除非用户明确要求重写）

### 5) 整理为知识库条目（Structure / Taxonomy）

目标：把零散笔记整理成可复用条目（术语表、FAQ、教程）。

- 先确认目标产物类型：`术语/FAQ/教程/决策记录(ADR)/读书笔记/项目文档`
- 输出结构建议：
  - 教程：`背景 -> 步骤 -> 示例 -> 常见问题 -> 参考`
  - ADR：`Context -> Decision -> Consequences -> Links`
- 写回策略：
  - 若原文是原始记录：创建“整理版”新文档，并在原文顶部加链接；
  - 若要求原地整理：优先“新增小节 + 重排标题”，避免破坏时间线。

## 性能预算与降级

- 默认预算：粗召回最多 50 篇文档，精读最多 8 篇。
- 范围过大（例如命中 > 200）时：先返回主题分布与 Top 文档，再建议用户缩小范围。
- 低置信度（高冲突/低覆盖）时：明确标注“不确定结论”，并给最小追问。

## 失败与安全兜底

- 找不到文档：请求更精确的标题/链接/位置；或创建新文档并说明原因。
- 目标日期 Daily Note 缺失：直接在该日期创建 Daily Note 并继续写入；不要改为“先建文档再移动”。
- 权限/空间范围不符：检查 Craft MCP URL 是否指向正确空间（full space vs single doc）。
- 工具返回不稳定或能力不足：使用“新建文档 + 引用原文链接”的保守方案。
