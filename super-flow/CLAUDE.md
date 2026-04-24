# CLAUDE.md — super-flow

## 插件概述

超级生产线（SuperFlow）— 从创意到上线的全链路自主开发流程插件。

> 详细文档请参考 [README.md](./README.md)

## 核心组件

| 组件 | 颜色 | 路径 | 说明 |
|------|------|------|------|
| 主控 | — | `skills/super-flow/SKILL.md` | 按顺序启动主干 Agent、协调阶段交接、监控内循环、决断所有上报问题 |
| 创意 Agent | magenta | `agents/creative-agent.md` | CEO/高级产品战略官，输出 Creative Brief，经评审后移交产品 Agent |
| 创意评审团 | magenta | `agents/creative-reviewer.md` | 创新性+可行性+商业价值，每个实例评估全部视角 |
| 产品 Agent | orange | `agents/product-agent.md` | brainstorming 后输出 SPEC.md + user-guide.md，负责与创意提出者/用户确认 SPEC |
| SPEC 审查 Agent | orange | `agents/spec-reviewer.md` | 验证 SPEC 是否完整执行 Creative Brief（创意模式）或 brainstorming（产品模式）的创意 |
| 架构 Agent | cyan | `agents/architecture-agent.md` | 接收 SPEC，生成实现计划 |
| 计划评审 Agent | cyan | `agents/plan-reviewer.md` | 验证计划完整性、架构合理性 |
| 开发 Agent | green | `agents/developer-agent.md` | 按计划执行实现 |
| 实现评审团 | green | `agents/implementation-reviewer.md` | 完整性+代码质量+安全 |
| 测试 Agent | yellow | `agents/tester-agent.md` | 测试用例生成 + 单元测试 + 执行，产出测试报告 |
| 测试评审 Agent | yellow | `agents/test-reviewer.md` | 验证测试用例覆盖率和质量精度 |

> **颜色规范**：主干Agent与对应的评审Agent使用相同颜色，不同主干Agent使用不同颜色以区分

## 文件输出目录

**feature-name命名规则**：
- 创意模式：由创意Agent决定
- 产品模式：由产品Agent决定
- 所有文档使用**同一个** feature-name，便于关联

```
docs/superflow/
├── specs/              # SPEC 文档
│   └── YYYY-MM-DD-feature-name-spec.md
├── plans/              # 实现计划
│   └── YYYY-MM-DD-feature-name-plan.md
├── creatives/          # 创意文档
│   └── YYYY-MM-DD-feature-name-creative.md
├── tests/              # 测试用例
│   ├── YYYY-MM-DD-feature-name-logic-tests.md    # 逻辑测试用例
│   ├── YYYY-MM-DD-feature-name-manual-tests.md    # 非逻辑测试用例
│   └── YYYY-MM-DD-feature-name-test-report.md     # 测试报告
```

设计文档（设计规范、架构说明）放在 `docs/superflow/specs/` 子目录。

## Agent 设计原则

### 评审 Agent（Reviewer）

- **架构约束**：作为 subagent，只能与主控通信，无法绕过主控直接与任何 Agent 或用户交互
- **职责边界**：只与对应的主干 Agent 交流（经主控转发），不与用户或其他 Agent 交互评审意见，不做流程判断
- **颜色规范**：与对应的主干 Agent 使用相同颜色

### 主干 Agent（主干）

- **架构约束**：作为 subagent，只能与主控通信，无法绕过主控直接与任何 Agent 或用户交互
- **职责边界**：对内，与评审Agent交流，处理评审意见；对外，向主控汇报评审结果及请求主控转发内容，不做流程判断
- **核心任务**：高质量完成角色核心任务
- **评审闭环**（经主控转发）：接收到评审意见 → 整改 → 发给主控 → 主控转发给评审 Agent
- **上报机制**：评审通过（count=5）→ 发给主控汇报；接受主控终审决断（count=-1）
- **颜色规范**：与对应的评审 Agent 使用相同颜色，不同主干Agent使用不同颜色以区分

### 主控（Orchestrator）

- **唯一职能**：控制流程
- **具体职责**：
  1. 入口模式选择（创意模式 / 产品模式）
  2. 开启流程（启动创意 Agent 或产品 Agent）
  3. 转发产品与创意（或用户）的对话
  4. 转发 SPEC 确认请求及确认结果
  5. 辅助主干 Agent 的内循环评审计数（不判断计数含义）
  6. 根据主干 Agent 上报的评审结果进入下一阶段，或做出终审决断（count=-1）令主干 Agent 无条件服从整改
  7. 守门员 —— 替用户做决定，确保流程不阻塞

## 设计参考

完整设计文档：`superflow-design.md`
