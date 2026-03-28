---
name: social-science-reading-notes
description: "将社会科学/心理学/行为科学书籍资源（PDF/EPUB/TXT/MD/HTML）转换为模型友好文本（已转换则跳过），并对用户指定章节/小节进行深度阅读，输出仅基于原书的详细结构化 Markdown 笔记（含短引文证据、不含页码定位）。适用于单章深读、多章批量总结、增量续写与按关键词复盘。输出统一管理在 {书名}-notes/，按章节/小节分文件，默认不覆盖。"
---

# 社会科学阅读笔记

## 输入确认

- 必问：`书名`、`阅读范围`（章节/小节/主题关键词）、`原始资源路径`（文件或文件夹）、`输出语言`（默认中文）、`多章节输出策略`（默认按章拆分）、`写入模式`（默认 `new`）、`是否允许覆盖同名文件`（默认否）。
- 如果用户给了章节，但文本标题不清晰，补问 1-2 个锚点短语（位于目标段落开头/结尾附近）。

## 路径与文件策略（必须遵守）

1. 使用 `{书名}-notes/` 作为根目录（不存在则创建）。
2. 目录结构固定为：
   - `{书名}-notes/_sources/`：转换后的源文本
   - `{书名}-notes/_chunks/`：大文本分块
   - `{书名}-notes/notes/`：阅读笔记
   - `{书名}-notes/index.md`：笔记索引
3. 根据 `阅读范围` 生成 scope slug 作为默认文件名：
   - 例如：`第9章` -> `chapter-09.md`，`第10章` -> `chapter-10.md`
   - 兜底：转换为小写 ASCII slug（字母/数字/连字符）
   - 若无法可靠生成，使用 `section-YYYYMMDD-HHMMSS.md`
4. 默认目标文件：`{书名}-notes/notes/<scope-slug>.md`
5. 禁止默认写入 `{书名}-notes/notes.md`，仅当用户明确指定该文件时才允许。
6. 默认不覆盖：
   - 当目标已存在且模式是 `new`：创建同级新文件（如 `<scope-slug>-YYYYMMDD-HHMMSS.md`）
   - 仅当用户明确要求时才允许覆盖
7. 笔记写入和索引更新必须走 `scripts/write_note.py`，不要用临时手写文件方式绕过。
8. 当 `阅读范围` 覆盖多章（例如 `第9-10章`）时，默认按章拆分为多个文件；仅在用户明确要求“合并输出”时才写入单文件。

## Python 运行约定（必须遵守）

- 所有 Python 脚本统一使用 `uv` 虚拟环境执行：`uv run python ...`
- 若需要额外依赖，使用 `uv run --with <package> python ...`

## 步骤 1：转换源文件（仅在需要时）

1. 按上述结构创建目录。
2. 将用户资源转换为 UTF-8 文本，并缓存到 `{书名}-notes/_sources/`。

命令：

```bash
uv run python scripts/convert_to_text.py \
  --input "<原始资源路径>" \
  --notes-dir "<绝对路径>/<书名>-notes"
```

说明：
- 在 skill 目录执行该命令，或使用脚本绝对路径。
- 优先显式传 `--notes-dir "<绝对路径>"`，避免 cwd 变化导致输出落错目录。
- 仅在明确不传 `--notes-dir` 时，才改用 `--book-title "<书名>"`。
- 转换缓存主要按 `sha256` 命中；路径仅用于优先匹配而非硬条件。
- PDF 依赖 `pdftotext`（Poppler）。若提取文本异常短，视为扫描件，先 OCR（如 `ocrmypdf`）再转换。

## 步骤 2：定位目标章节/片段

- 优先在 `{书名}-notes/_sources/*.txt` 检索（大书可改查 `{书名}-notes/_chunks/`）。
- 使用紧凑锚词（章节标题/小节标题/重复关键词）截取相关文本范围。
- 若用户要求“深读某章/某节”，先按作者原始结构列出内部顺序，再按该顺序解读。

## 步骤 3：深读与写作要求

### 内容约束（必须遵守）

- 细粒度写作，允许适度冗余。
- 严禁超出原书：不做外部检索、不加书外例子、不做个人推演。
- 主动引用，但引用保持短句（优先 1-2 句），仅用于支撑当前观点。
- 不写页码/节号等位置标记。

### Markdown 约束（必须遵守）

- 使用清晰层次和留白，可适度使用段落、软换行、引用、表格、列表、分隔线。
- 标题只用四级标题 `####`，且数量克制；其余内容使用普通文本。
- 对关键结论和金句使用 `**加粗**`。

### 输出规则（必须遵守）

- 笔记写入 `{书名}-notes/`。
- 优先基于 `assets/note-template.md` 填写目标章节内容。
- 必须通过 `scripts/write_note.py` 写入（强制）。
- 默认目标为 `{书名}-notes/notes/<scope-slug>.md`，由脚本解析。
- 写入模式由脚本强制约束：
  - `new`（默认）：新建；若重名自动加时间戳
  - `append`：追加带日期块（`---` 分隔）；文件不存在则创建
  - `overwrite`：仅在显式确认后，并传 `--allow-overwrite`

命令模板：

```bash
uv run python scripts/write_note.py \
  --scope "<阅读范围>" \
  --notes-dir "<绝对路径>/<书名>-notes" \
  --mode "<new|append|overwrite>" \
  --content-file "<笔记内容文件>"
```

- 若用户指定精确输出路径，传 `--output-file "<路径>"`。
- 可选传入来源追踪参数：`--source "<来源文件或chunk>" --source-sha256 "<sha256>"`。
- 每次成功写入后，脚本会自动更新 `{书名}-notes/index.md`，包含结构化字段：`Time`、`Scope`、`File`、`Mode`、`Action`、`Source`、`SourceSHA256`、`ContentSHA256`、`EntryKey`。
- 兼容旧文件：
  - 若存在 legacy `{书名}-notes/notes.md`，默认保持不动
  - 仅在用户明确要求时才继续写入 legacy `notes.md`
