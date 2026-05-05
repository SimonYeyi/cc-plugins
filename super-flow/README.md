# SuperFlow — 超级生产线

全链路自主开发流程框架，通过多 Agent 协作实现从创意到代码的自动化生产。

## 是什么

SuperFlow 是一个基于 Claude Code 的开发框架，将软件开发拆解为 6 个标准化阶段：

```
创意 → 产品 → 设计 → 架构 → 开发 → 测试
```

每个阶段都有对应的评审机制，确保质量可控、流程可追溯。

## 快速开始

在 Claude Code 中输入：

```bash
/superflow [你的需求描述]
```

### 示例

```bash
# 创意模式 - 让 AI 自由发挥
/superflow

# 产品模式 - 需求明确
/superflow 做一个待办事项应用，支持分类、优先级、提醒功能，使用 React + TypeScript

# 模糊需求 - 会询问模式
/superflow 做一个游戏
```

## 核心特点

### 双模式入口

| 模式 | 适用场景 |
|------|---------|
| **创意模式** | 无明确规划、探索性需求、需要创新方案 |
| **产品模式** | 需求明确、有参考实现、渐进式功能 |

### 六阶段流程

1. **创意流程**（仅创意模式）：创意生成与评审
2. **产品流程**：SPEC文档生成与评审
3. **设计流程**：UX/UI设计与评审
4. **架构流程**：技术评估、设计检查、实现计划与评审
5. **开发流程**：代码实现与评审
6. **测试流程**：测试用例/代码编写、执行测试、生成报告

### 评审循环机制

- 每个阶段都有对应的评审 Agent
- 评审不通过时循环修复，最多 5 次
- 5 次后仍不通过，主控做出决断强制推进

## 产出物

所有文档统一存放在 `docs/superflow/` 目录下：

```
docs/superflow/
├── creatives/              # 创意文档（仅创意模式）
│   └── YYYY-MM-DD-feature-name-creative.md
├── specs/                  # 产品规格文档
│   ├── YYYY-MM-DD-feature-name-spec.md
│   └── YYYY-MM-DD-feature-name-user-guide.md   # 用户指南
├── plans/                  # 实现计划
│   └── YYYY-MM-DD-feature-name-plan.md
├── designs/                # UX/UI 设计文档
│   └── YYYY-MM-DD-feature-name-design.md
└── tests/                  # 测试相关
    ├── YYYY-MM-DD-feature-name-unit-tests.md       # 单元测试用例
    ├── YYYY-MM-DD-feature-name-platform-tests.md   # 平台测试用例
    ├── YYYY-MM-DD-feature-name-acceptance-tests.md # 验收测试用例
    └── YYYY-MM-DD-feature-name-test-report.md      # 测试报告
```

## 深入了解

详细的流程规则、评审循环逻辑等，请查看 [SKILL.md](skills/super-flow/SKILL.md)。

## 许可证

本项目遵循原仓库的许可证协议。
