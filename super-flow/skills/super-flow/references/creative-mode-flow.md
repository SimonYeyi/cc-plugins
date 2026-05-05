# 创意模式流程

**定位**：全自动生产线，**无论何时**都不能把问题抛给用户，必须根据规则推进流程

**引用文件使用规则**：以下'references/xxx.md'文件是执行流程必要的规范文件，先内联展开理解后再执行流程

## 初始阶段：初始流程

@references/stage-initial.md

## 阶段一：创意流程

@references/review-loop.md
@references/brainstorming.md
@references/stage-dependency-check.md

```
阶段一：启动创意Agent(任务：生成Creative Brief；传入：项目现状分析 + 重叠情况标注) ← 阶段一：创意流程开始
    │
    ▼
启动创意评审Agent（任务：Creative Brief评审）
    │
    ├──不通过 → 启动创意Agent修复（循环）
    │       │
    │       ├──循环5次内 → 继续循环
    │       │
    │       └──5次后仍不通过 → 主控决断
    │
    └──通过
        │
        ▼
启动创意Agent（任务：回答Brainstorming问题；输入：从Creative Brief中识别出的Brainstorming问题列表）
        │
        ▼
启动产品Agent(任务：基于Creative Brief生成SPEC；传入：brainstorming结果) ← 阶段二：产品流程开始
        │
        ▼
启动创意Agent确认SPEC（确认 ≠ 评审）
        │
        ├──创意Agent有修改意见 → 启动产品Agent修改SPEC（循环）
        │       │
        │       ▼
        │   产品Agent修改后重新启动创意Agent确认SPEC
        │
        └──创意Agent确认通过
                │
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
