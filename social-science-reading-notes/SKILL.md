---
name: social-science-reading-notes
description: "Convert social science / psychology / behavioral science book resources (PDF/EPUB/TXT/MD/HTML) into model-friendly text (skip if already converted), then deeply read user-requested chapters/sections and write detailed, structured Markdown reading notes focused strictly on the original book content, with short direct quotes as evidence (no location markers). Save outputs under {书名}-notes/ (create folder if missing)."
---

# Social Science Reading Notes

## Inputs (ask and confirm)

- Ask for: `书名`、`阅读范围`（章节/小节/主题关键词）、`原始资源路径`（文件或文件夹）、`输出语言`（默认中文）、`是否要追加到已有笔记`（默认新建）。
- If the user specifies chapters but the text headings are unclear, ask for 1-2 anchor phrases that appear near the start/end of the target section.

## Step 1: Convert sources (only if needed)

1. Create notes folder: `{书名}-notes/`.
2. Convert the user-provided resource(s) into UTF-8 text, and cache results under `{书名}-notes/_sources/`.

Run:

```bash
python3 scripts/convert_to_text.py \
  --input "<原始资源路径>" \
  --book-title "<书名>"
```

Notes:
- Run the command from this skill folder (so `scripts/convert_to_text.py` resolves), or use an absolute path to the script.
- Use `--notes-dir "<自定义路径>"` when the user wants the `{书名}-notes/` folder in a specific location.
- The converter skips work if an identical input (same absolute path + sha256) was already converted.
- PDF conversion requires `pdftotext` (Poppler). If extraction is extremely short, treat it as a scanned PDF and ask the user to OCR first (e.g. `ocrmypdf`), then re-run conversion.

## Step 2: Locate the requested section(s)

- Prefer searching within `{书名}-notes/_sources/*.txt` (or `{书名}-notes/_chunks/` when the book is large).
- Use tight keyword anchors for chapter titles, section titles, or repeated terms; extract only the relevant span to reason about.
- If the user wants “深读某章/某节”, first outline the chapter’s internal structure as the author presents it, then proceed in that order.

## Step 3: Deep reading and note writing (requirements)

### Content constraints (must follow)

- Write notes at a **detailed** granularity; mild redundancy is OK.
- Do **not** extend beyond the book: no extra research, no external examples, no personal speculation. Stay inside the author’s claims, definitions, examples, and argument structure.
- Quote actively, but keep quotes **short** (prefer 1-2 sentences). Use quotes only to support the specific point being noted.
- Do not add location markers (no page/section numbers).

### Markdown style constraints (must follow)

- Use clear hierarchy and spacing, with tasteful use of: paragraphs, soft line breaks (two spaces + newline), blockquotes, tables, lists, and horizontal rules.
- Use headings **sparingly** and use **only level-4 headings** (`####`). Everything else must be normal text (plus bold, quotes, lists, etc.).
- Bold important claims and selected “golden lines”: `**...**`.

### Output rules (must follow)

- Save Markdown notes into `{书名}-notes/` (create the folder if missing).
- Default note file: `{书名}-notes/notes.md` (unless the user requests a different filename).
- Prefer using `assets/note-template.md` as the starting point, and fill it with the requested section(s).
- If `notes.md` already exists and the user asked to append, append a new dated block at the end separated by `---`.
