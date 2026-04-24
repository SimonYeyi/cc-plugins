# SuperFlow — 超级生产线

从创意到上线的全链路自主开发流程。

## 概述

通过 `/superflow` 斜杠命令或任何功能性开发请求触发，拦截所有"构建/开发/实现"类需求，多 Agent 协作完成：创意生成 → 评审 → 产品规划 → 开发 → 测试 → 多视角审查，循环迭代直到所有问题解决。

**注意**：本流程分为两种模式：
- **创意模式**：创意由创意Agent提出 → 产品Agent brainstorming → 创意Agent确认SPEC
- **产品模式**：创意由用户提出 → 产品Agent brainstorming → 用户确认SPEC

**统一规则**：谁提出创意，谁确认SPEC

## 功能

- **创意模式**：创意 Agent 自主发散构思 + 评审团多视角并行评审
- **产品模式**：产品 Agent 探讨需求，输出 SPEC.md
- **自动化开发**：架构 Agent 生成计划，计划评审 Agent 评审，开发 Agent 按计划执行
- **自动化测试**：测试 Agent 产出测试用例 + 单元测试 + 执行验证
- **多视角审查**：完整性 + 代码质量 + 安全三视角并行审查，循环修复直到通过

## 入口

```
/superflow [提示词]
```

- 无参数 → 创意模式
- 有主题无细节 → 询问：创意模式 / 产品模式
- 有主题有细节 → 产品模式（brainstorm 探讨需求）

## 文件结构

```
super-flow/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── super-flow/
│       └── SKILL.md           # 主工作流 skill
├── agents/
│   ├── creative-agent.md      # 创意 Agent
│   ├── creative-reviewer.md # 创意评审团（创新性+可行性+商业价值）
│   ├── product-agent.md       # 产品 Agent
│   ├── spec-reviewer.md        # SPEC 审查 Agent
│   ├── architecture-agent.md  # 架构 Agent
│   ├── plan-reviewer.md        # 计划评审 Agent
│   ├── developer-agent.md      # 开发 Agent
│   ├── tester-agent.md         # 测试 Agent
│   ├── test-reviewer.md           # 测试评审Agent（验证覆盖率+质量精度）
│   └── implementation-reviewer.md  # 实现评审团（完整性+代码质量+安全）
├── docs/
│   └── superflow/
│       ├── specs/              # SPEC 文档
│       ├── plans/              # 实现计划
│       ├── creatives/          # 创意文档
│       └── tests/              # 测试用例
├── superflow-design.md         # 设计文档（顶层）
├── CLAUDE.md
└── README.md
```

## 使用方式

在 Claude Code 中输入 `/superflow` 启动完整流程。

## 详细设计

参见 `superflow-design.md`
