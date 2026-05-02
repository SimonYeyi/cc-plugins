# 产品模式流程

## 初始阶段：初始流程

@references/stage-initial.md

## 阶段一：需求澄清流程

@references/review-loop.md
@references/brainstorming.md
@references/stage-dependency-check.md

```
阶段一：主控与用户澄清需求（Brainstorming问答） ← 阶段一：需求澄清流程开始
    │
    ▼
启动产品Agent（任务：基于用户需求生成SPEC；传入：brainstorming结果 + 项目现状分析 + 重叠情况标注） ← 阶段二：产品流程开始
    │
    ▼
主控展示SPEC给用户确认（确认 ≠ 评审）
    │
    ├──用户有修改意见 → 启动产品Agent修改SPEC（循环）
    │       │
    │       ▼
    │   产品Agent修改后主控重新展示SPEC给用户确认
    │
    └──用户确认通过
            │ ⚠️ **重要**：SPEC确认后，后续所有流程（SPEC评审→设计→架构→开发→测试→评审）均为全自动，无需用户参与
            ▼
    启动SPEC评审Agent（任务：SPEC评审；传入：brainstorming结果）
        │
        ├──不通过 → 启动产品Agent修复（循环）
        │       │
        │       ├──循环5次内 → 继续循环
        │       │
        │       └──5次后仍不通过 → 主控决断
        │
        └──通过 → 启动产品Agent（任务：生成用户指南）
                    │
                    ▼
                进入阶段三：设计流程
```

@references/stage-design.md
@references/stage-architecture.md
@references/stage-development.md
@references/stage-testing.md
