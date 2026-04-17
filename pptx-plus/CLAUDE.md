# CLAUDE.md - pptx-plus

## 重要约定

### 维护原则

在维护 CLAUDE.md 时，如果有相关的内容（如工具说明、使用约束、配置等），应放在同一个部分中说明，便于查阅和维护，避免散落在文件各处。

### 禁止修改第三方工具pptx

**第三方工具 `tools/pptx/`**：来源于第三方，无需审查，更不能修改内容——无论何时都应保持原样。扩展和定制应在插件层面进行，而非改动底层工具。

### tools/ 目录下的文件可以有 skill frontmatter

tools/ 目录下的工具指南（如 `tools/pptx/SKILL.md`）应保留 skill 格式的 YAML frontmatter（name、description 等），不要改为非 skill frontmatter 格式（如 REFERENCE.md），除非有明确理由。

**原因**：这些文件存放在 tools/ 目录下，不会被 Claude Code 注册为独立的 skill，只会作为工具指南被主 agent 读取使用。

**意义**：保留 frontmatter 可以让文件保持自描述性，便于人类阅读和维护。

### 文件命名

- `tools/` 下的工具指南：使用 `SKILL.md` 后缀（如 `tools/pptx/SKILL.md`）
- `skills/` 下的 skill：使用 `SKILL.md`（如 `skills/ppt-report/SKILL.md`）

### 相关文件

- [README.md](README.md) — 插件使用说明和安装指南
- [test-workflow.md](test-workflow.md) — 测试场景和检查清单
- [docs/superpowers/specs/](docs/superpowers/specs/) — 设计规格文档
- [docs/superpowers/plans/](docs/superpowers/plans/) — 实施计划文档