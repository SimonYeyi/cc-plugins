---
name: ppt-report
description: "Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates, layouts, speaker notes, or comments. Trigger whenever the user mentions \"deck,\" \"slides,\" \"presentation,\" or references a .pptx filename, regardless of what they plan to do with the content afterward. If a .pptx file needs to be opened, created, or touched, use this skill."
---

# PPT 分享生成工作流

## 架构说明

- **主控**：本skill控制工作流，在关键节点暂停等待用户确认，所有步骤由主agent直接执行

## 路径规则

> **注意：** 以下路径均为 Unix 格式（~/.pptx-plus/）。

**输入保存路径：** ~/.pptx-plus/<话题>/input/
**PPT 产物输出路径：** ~/.pptx-plus/<话题>/output/[主题]-[YYYY-MM-DD].pptx

**话题 slug：** 中文话题翻译为英文语义，小写，空格变 -，特殊字符变 _（如"AI发展趋势"→ai-development-trends）。

## 原始材料定义

> 用户输入的提示词本身不算原始材料；提示词中包含的链接、本地文件/文件夹才是原始材料。

## 8步工作流

**严格按顺序执行 STEP 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8，不得跳步，不得使用subagent。**

---

### STEP 1：解析输入

**操作：**
- 从用户输入中提取主题、关键词
- 处理多种输入类型：自然语言、文件路径、文件夹路径、飞书文档链接
- 使用 Read 工具读取引用文件；调用 feishu-doc skill 读取飞书文档
- 整合所有来源形成统一的输入摘要
- 推导话题 slug 用于路径构建
**输出：** [STEP1] 输入摘要

---

### STEP 2：生成大纲

**操作：** 基于 STEP1 的输入摘要，直接生成 PPT 大纲。

**输出：** [STEP2] 大纲内容

**等待用户确认或修改大纲，不要提示下一步动作。**

---

### STEP 3：确认大纲并保存

**操作：** 用户确认大纲后，**立即**将以下内容写入 ~/.pptx-plus/<话题>/input/ 目录：
- **本地文件/文件夹** — 用户提示词中提到的所有文件资料（原封不动地复制保存），用户提示词本身不保存
- **links.txt** — 所有链接的列表（一行一个 URL），包括飞书文档链接
- **outline.md** — 最终大纲（大纲修改时直接更新此文件）

> 确认和保存为同一原子操作，确认后立即执行保存，无独立保存步骤。

**输出：** [STEP3] 已确认大纲并写入input目录

---

### STEP 4：选择丰富级别

**操作：** 呈现四个丰富级别（L1-L4）的描述，等待用户选择。

**丰富级别说明：**
- L1：极简，仅大纲结构
- L2：基础，包含核心内容
- L3：标准，内容较完整
- L4：详细，深度扩展

**输出：** [STEP4] 用户选择: Lx

**等待用户选择，不要提示下一步动作。**

---

### STEP 5：丰富内容

**操作：** 基于 STEP1 的原始材料、STEP2 的大纲和选定的丰富级别（Lx），直接丰富 PPT 内容。L3/L4 级别需触发网络搜索补充数据。读取 tools/content-enricher/SKILL.md 作为工具指南。

**输出：** [STEP5] 丰富完成

---

### STEP 6：预览确认并保存预览内容

**操作：** 以完整 Markdown 格式向用户呈现丰富后的内容进行预览。使用来源标注：
- [用户提供] — 用户原始材料
- [AI知识] — AI 知识补充（仅输出有把握的准确内容）
- [网络搜索] — 搜索结果补充

用户确认后，**立即**将丰富后的内容写入 ~/.pptx-plus/<话题>/input/content.md。

> 确认和保存为同一原子操作，确认后立即执行保存，无独立保存步骤。

**输出：** [STEP6] 已预览确认并写入content.md

**等待用户确认。如有修改则应用修改后，必须再次等待用户确认后才能继续，不得自动进入下一步。如有结构调整，需同步更新 outline.md。**

---

### STEP 7：生成 PPT

**操作：**
1. 切换到 output 目录：`cd ~/.pptx-plus/<话题>/`
2. 读取 input/content.md
3. 读取 tools/pptx/SKILL.md 作为工具指南
4. 使用其中的工具生成 PPT
5. 生成的 PPT 文件保存在 output/ 目录

**输出：** [STEP7] PPT生成完成

---

### STEP 8：报告完成

**操作：**
- 确认文件已保存
- 报告输出路径
- 通过 metabot 在飞书对话中发送 PPT 文件

**输出：** [STEP8] 完成
