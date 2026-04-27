# CLAUDE.md — super-flow

> @`skills/super-flow/SKILL.md`

## Agent Description 规范

**核心要求**：agent 文件的 description 必须与工作流章节完全匹配。

**格式规范**：
- description 使用 `processing xxx` 格式
- 工作流使用 `### 处理xxx` 格式
- 两者内容必须一一对应

**示例**：
```yaml
description: |
  Use this agent when:
  - processing Creative Brief generation
  - processing review feedback/control-decision
  - processing brainstorming problems
  - processing SPEC confirmation request
```

**同步要求**：
- 修改工作流章节时，必须同步更新 description
- 修改 description 时，必须同步更新工作流章节
