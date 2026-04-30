# Efficiency Skills Repository

A curated collection of reusable Codex skills for productivity-focused workflows.

## Overview

This repository stores standalone skills. Each skill lives in its own folder and is anchored by a `SKILL.md` file.

Typical skill folder contents:

- `SKILL.md`: Skill definition, trigger guidance, and workflow
- `agents/`: Provider-specific agent configuration
- `scripts/`: Helper scripts used by the skill
- `assets/`: Reusable templates and static resources
- `references/`: Supporting docs or setup notes

## Skills Included

| Skill | Description | Path |
| --- | --- | --- |
| `arxiv-deep-research` | Academic deep research centered on arXiv papers: systematic search, screening with a quantitative rubric, structured reading notes, taxonomy building, bias detection, and synthesis into a citation-backed survey report. | `arxiv-deep-research/` |
| `craft-mcp` | Connect to Craft via MCP to search, summarize, create, and update notes/documents. Supports ARR (append-and-review) notes, daily notes, meeting minutes, and scoped retrieval protocols. | `craft-mcp/` |
| `harness-engineering-context` | Restructure repository context systems, define roles for AGENTS.md/README.md/ARCHITECTURE.md, migrate canonical knowledge into docs/, manage versioned execution plans, and add automated validation for documentation hygiene. | `harness-engineering-context/` |
| `omnifocus-mcp` | Reliable OmniFocus execution with MCP tools for task and project management. Includes safe fuzzy retrieval, mutation safety protocols, and end-to-end GTD workflows. | `omnifocus-mcp/` |
| `paper-research-assistant` | Read, analyze, critique, and synthesize academic papers from PDFs, arXiv links, DOI links, titles, or pasted text. Supports source resolution, deep reading, comparison, research-gap identification, and reusable paper cards. | `paper-research-assistant/` |
| `social-science-reading-notes` | Convert social science/psychology/behavioral science resources into text and generate detailed evidence-based reading notes. Supports chapter-level deep reading, incremental writing, and keyword-based review. | `social-science-reading-notes/` |

---

<details>
<summary><strong>中文版本（点击展开）</strong></summary>

# Efficiency Skills 仓库

一个面向效率工作流的可复用 Codex Skills 集合。

## 仓库说明

本仓库按"一个技能一个目录"组织，每个技能以 `SKILL.md` 为核心入口。

常见目录结构：

- `SKILL.md`：技能定义、触发说明与执行流程
- `agents/`：针对不同模型/平台的代理配置
- `scripts/`：技能配套脚本
- `assets/`：模板与静态资源
- `references/`：参考文档或配置说明

## 已包含技能

| 技能 | 说明 | 路径 |
| --- | --- | --- |
| `arxiv-deep-research` | 以 arXiv 论文为核心的学术深度研究：系统性检索、量化筛选评分、结构化阅读笔记、分类体系构建、偏见检测，并合成为带引用的综述报告。 | `arxiv-deep-research/` |
| `craft-mcp` | 通过 MCP 连接 Craft，执行笔记/文档的检索、总结、创建与更新，支持 ARR 笔记、每日笔记、会议纪要等协议。 | `craft-mcp/` |
| `harness-engineering-context` | 重构仓库上下文系统，定义 AGENTS.md/README.md/ARCHITECTURE.md 的角色，将规范知识迁移至 docs/，管理版本化执行计划，并增加文档结构与交叉链接的自动化校验。 | `harness-engineering-context/` |
| `omnifocus-mcp` | 通过 OmniFocus MCP 工具可靠地执行任务和项目管理，包含安全模糊检索、变更安全协议与完整 GTD 工作流。 | `omnifocus-mcp/` |
| `paper-research-assistant` | 从 PDF、arXiv 链接、DOI、标题或粘贴文本中阅读、分析、批判与综合学术论文。支持来源解析、深读、方法对比、研究缺口识别与可复用论文卡片。 | `paper-research-assistant/` |
| `social-science-reading-notes` | 将社会科学/心理学/行为科学资料转为文本，产出基于原文证据的深度阅读笔记，支持章节深读、增量续写与关键词复盘。 | `social-science-reading-notes/` |

</details>
