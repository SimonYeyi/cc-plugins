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

## 流程图与Agent工作流输入同步规范

**核心原则**：SKILL.md流程图中的dispatch输入标注必须与对应Agent工作流中的"输入"定义完全一致。

**同步范围**：
- `skills/super-flow/SKILL.md` 流程图中的所有 "│ 输入：xxx" 标注
- `agents/*.md` 文件中各工作流章节的 "**输入**：xxx" 定义

**检查清单**：
1. 主控 → Agent启动：核对Agent工作流的第一个处理环节的输入
2. Agent → 评审Agent请求：核对评审Agent工作流的输入
3. 特殊dispatch（如修复SPEC、测试失败）：核对目标Agent对应处理环节的输入

**修改流程**：
- 修改SKILL.md流程图输入标注 → 立即同步修改对应Agent文件
- 修改Agent工作流输入定义 → 立即同步修改SKILL.md流程图
- 修改后必须进行双向验证

**缺失处理**：
- 流程图有dispatch输入标注，但Agent工作流中无对应处理章节 → 自行补充Agent工作流
- Agent工作流有处理章节，但流程图中无对应dispatch输入标注 → 自行补充流程图标注
- 补充时必须谨慎小心，确保准确理解上下文后正确补充
