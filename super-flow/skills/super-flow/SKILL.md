---
name: super-flow
description: "SuperFlow — full-stack autonomous development workflow. MUST use this skill when building anything that produces code: features, applications, games, websites, automations, plugins, or any development task. Works with or without explicitly invoking /superflow."
---

# 超级生产线（SuperFlow）

全链路自主开发流程的入口 skill。协调多个 Agent 完成：创意生成 → 产品规划 → 开发 → 测试 → 完成，循环迭代直到所有问题解决。

## 入口分支

| 场景                             | 触发 |
|--------------------------------|------|
| `/superflow`（无任何参数）            | 直接进入**创意模式** |
| `/superflow <有主题但细节不明确>`       | 询问选择：创意模式 / 产品模式 |
| `/superflow <有主题有细节> 或 <模糊主题>` | 直接进入**产品模式**（brainstorm 流程，探讨需求） |

**主控替用户决断的最高原则**：
- 创意模式定位为全自动生产线，**无论何时**都不能把问题抛给用户（导致流程阻塞），遇到的所有问题主控必须做出决断，确保流程继续
- 产品模式定位为半自动生产线，除 **产品 Agent 与用户的 Brainstorming 以及 请求用户确认 SPEC**需要用户参与，其余情况都不能把问题抛给用户（导致流程阻塞），遇到的所有问题主控必须做出决断，确保流程继续

**主控询问固定格式**：
当需要询问用户选择模式时，主控应使用以下格式：
```
主控：我检测到你提供了一个主题，但功能细节不够明确。
请选择工作模式：

| 序号 | 模式 | 适用场景 |
|:----:|------|---------|
| 1 | 创意模式 | 无明确规划、探索性需求、需要创新方案 |
| 2 | 产品模式 | 需求明确、有参考实现、渐进式功能 |
```

## 完整流程

```
入口分支
    │
    ├──→ 创意模式 ──→ 阶段一：创意流程 ─────────────────┐
    │                                                      │
    │     （创意Agent + 创意评审团内循环）                  │
    │                    ↺ 内循环                          │
    │                                                      │
    └──→ 产品模式 ──→ 用户 ────────────────────────────────┤
                                                           ▼
                                                    阶段二：产品流程
                                              （产品Agent + SPEC审查Agent内循环）
                                                            ↺ 内循环
                                                           │
                                                           ▼
                                                    阶段三：架构流程
                                              （架构Agent + 计划评审Agent内循环）
                                                            ↺ 内循环
                                                           │
                                                           ▼
                                                    阶段四：开发流程
                                            （开发Agent + 实现评审团3实例并行）
                                                            ↺ 内循环
                                                           │
                                                           ▼
                                                    阶段五：测试流程
                                              （测试Agent + 测试评审Agent内循环）
                                                            ↺ 内循环
                                                           │
                                                           ▼
                                                       主控确认
```

## **Brainstorming与SPEC确认**要求

**防止产品Agent内部流程不完整的重要提醒** 
- Brainstorming完成后，不可直接进入下一阶段，必须先 dispatch 创意Agent 继续完成内部流程
- SPEC确认后，不可直接进入下一阶段，必须先 dispatch 产品Agent 继续完成内部流程

**创意Agent与产品Agent**（创意模式下）
- **展示** Brainstorming对话给创意Agent
- **dispatch** 创意Agent 回复问题
- 此时主控不提供任何决断

**产品Agent与用户**（产品模式下）
- **展示** Brainstorming对话给用户
- **dispatch** 用户 回复问题
- 此时主控不提供任何决断

**信息展示要求**：
- 主控在协调流程时，**必须将Agent间的信息传递和交流展示给用户**
- 包括但不限于：评审意见、反馈回复、brainstorming对话、SPEC确认内容
- 让用户了解流程进展，而非黑箱操作
- 所有 Agent 在陈述流程、汇报进展时，**必须加上 agent 名称前缀**
- 格式：`主控：`、`创意Agent：`、`产品Agent：`、`架构Agent：`、`开发Agent：`、`XX评审Agent：`等

## 主控的职责与权力

**职责与权力**：
- 按顺序启动各主干Agent
- **dispatch主干Agent**：评审意见、决断意见等需要Agent处理的信息，必须dispatch对应主干Agent处理
- **brainstorming对话**：
    - **展示** 产品Agent的问题给创意Agent/用户
    - **dispatch** 创意Agent/用户 回复问题
    - 对话是否完成不由主控决定，主控**必须**将所有的对话dispatch给产品Agent
    - 此过程**不需要主控决断**
- **SPEC确认**：
    - **展示** SPEC文档给创意提出者/用户确认
    - **dispatch** 创意Agent/用户 的回复结果
    - 创意Agent/用户 确认SPEC，不是向主控确认，主控**必须**将确认反馈dispatch给产品Agent
    - 此过程**不需要主控决断**
- **达到评审循环最大次数（count=5）时主控才可决断**，未达到时主控不做决断，持续dispatch主干Agent处理评审意见
- **主控决断真正的升级**：当主干Agent明确表示无法决定、无法推进时，主控必须做出决断

**区分"dispatch处理"与"真正升级"**：
| 情况 | 类型 | 主控操作 |
|------|------|----------|
| 创意评审要求修复 | dispatch处理 | dispatch 创意Agent 处理评审意见 |
| SPEC评审要求修复 | dispatch处理 | dispatch 产品Agent 处理评审意见 |
| 计划评审要求修复 | dispatch处理 | dispatch 架构Agent 处理评审意见 |
| 实现评审要求修复 | dispatch处理 | dispatch 开发Agent 处理评审意见 |
| brainstorming对话 | 展示+dispatch | 展示内容给对应方 + dispatch 回复 |
| SPEC确认 | 展示+dispatch | 展示SPEC给创意提出者/用户 + dispatch 确认结果 |
| 主干Agent明确说"我无法决定，升级主控" | 真正升级 | 主控做出决断，dispatch主干Agent执行 |

**主控决断**：
- 决断流程问题是主控的**核心职责**，不是"必要时才做"——不决断流程就会卡住
- **主控决断错了可以修复**，但不决断代价更大
- 遇到分歧时，选择**最能推进流程**的方案，而不是"最安全的"
- 主干Agent的升级意味着他们已经尽力了，主控决断是最后一道关卡，主控必须做出决断，并dispatch主干Agent执行（count=-1）

**主控决断执行规则**：
- 主控决断 = **做出决定** + **指明下一步** + **dispatch主干Agent执行决断（count=-1）**
- 主控决断后，**必须dispatch主干Agent执行决断（count=-1）**，否则流程中断
- 主控决断内容示例：
    - "采用方案A，继续进入架构流程"
    - "分歧是细节问题，记录在案，上报评审通过"
    - "dispatch 开发Agent 修复第3个Task，完成后重新评审"
- **主控决断是最终决定**——不是发表意见，不是转达，而是dispatch执行

**产出物清单**（主控最终确认时核对）：
- Creative Brief（仅创意模式）
- SPEC.md
- user-guide.md
- 实现计划
- 代码实现
- 测试用例文档 + 单元测试代码
- **测试报告**
- 所有产出物已保存至对应目录

**终止条件**：全部问题修复，所有主干 Agent 汇报评审通过，且主控确认。

## 角色与职责

| 角色 | 职责                                                                                  | 规模 |
|------|-------------------------------------------------------------------------------------|------|
| **主控（我）** | 按顺序启动各主干Agent、协调阶段交接、监控内循环、**主控决断所有主干Agent升级问题（除brainstorming和SPEC确认的dispatch处理外）** | 当前 session |
| **创意 Agent** | CEO/高级产品战略官。输出 Creative Brief（创意说明书），经评审通过后移交产品 Agent                               | 1 个 |
| **创意评审团 — 子功能创意** | 创新性 + 可行性 + 商业价值，每个实例评估全部视角，3 个并行评审                                                 | 3 个 |
| **创意评审团 — 项目立项创意** | 创新性 + 可行性 + 商业价值，每个实例评估全部视角，5 个并行评审                                                 | 5 个 |
| **产品 Agent** | 接收用户/创意 Agent 的创意，进行brainstorm式对话（创意模式：一次全问；产品模式：一次一问）后转化为 SPEC.md                  | 1 个 |
| **SPEC 审查 Agent** | 验证 SPEC 是否完全执行 Creative Brief（创意模式）或 brainstorming对话记录（产品模式）的创意                     | 1 个 |
| **架构 Agent** | 接收 SPEC，生成实现计划（含架构设计）                                                               | 1 个 |
| **计划评审 Agent** | 验证计划完整性、架构合理性                                                                       | 1 个 |
| **开发 Agent** | 按计划执行 → 修复问题                                                                        | 1 个 |
| **实现评审团** | 完整性 + 代码质量 + 安全，每个实例评估全部视角，3 个并行评审                                                  | 3 个 |
| **测试 Agent** | 产出测试用例文档（逻辑+非逻辑）+ 编写单元测试 + 执行测试 + 生成测试报告；**测试不通过时：测试代码错误打回测试Agent，功能不通过打回开发Agent**  | 1 个 |
| **测试评审Agent** | 验证测试用例覆盖率和质量精度（Coverage + Precision + Detail + Completeness）                        | 1 个 |

## Agent 调用参考

详细 Agent 定义和调用方式见 `../agents/` 目录：

- **`../agents/creative-agent.md`** — 创意 Agent（CEO/高级产品战略官，输出 Creative Brief）
- **`../agents/creative-reviewer.md`** — 创意评审团（创新性+可行性+商业价值，每个实例评估全部视角，3或5个并行评审）
- **`../agents/product-agent.md`** — 产品 Agent（接收 Creative Brief，输出 SPEC.md）
- **`../agents/spec-reviewer.md`** — SPEC 审查 Agent（验证 SPEC 是否完全执行 Creative Brief 的创意）
- **`../agents/architecture-agent.md`** — 架构 Agent（接收 SPEC，生成实现计划）
- **`../agents/plan-reviewer.md`** — 计划评审 Agent（验证计划完整性和架构合理性）
- **`../agents/developer-agent.md`** — 开发 Agent（按计划执行）
- **`../agents/implementation-reviewer.md`** — 实现评审团（完整性+代码质量+安全，每个实例评估全部视角，3个并行评审）
- **`../agents/tester-agent.md`** — 测试 Agent（产出测试用例文档+单元测试+执行测试+测试报告）

## 评审/审查意见处理原则

**主控评审循环控制**：
- 主控追踪每个阶段的评审循环次数，每阶段开始时 count = 0
- **dispatch** 主干Agent处理评审意见，附带count值
- 主控**不自行判断**，根据主干Agent的反馈决定下一步
- 主干Agent返回"通过" → 进入下一阶段；"修复" → count+1重新dispatch；"汇总分歧" → 主控决断后**dispatch主干Agent执行决断（count=-1）**

**count值含义**：
| count | 含义 |
|-------|------|
| 0~5 | 评审循环次数 |
| -1 | 主控决断意见（主干Agent必须遵守） |

**提醒主干Agent对评审反馈意见的处理原则**：
1. **认真思考**：对评审Agent提出的意见认真思考，不要一味遵从
    - 如果是自身问题：修复问题后
    - 如果是设计原因或有其他考虑：给出明确的理由
2. **重新评审** dispatch 评审Agent

**提醒评审Agent对主干反馈意见的处理原则**：
1. **重新核实**：对主干Agent已修复的问题重新核实
2. **重新思考**：对主干Agent反馈的不修改意见，重新思考是否同意
    - 如果同意：不追究，记录在案，评审通过
    - 如果不同意：给出明确的不同意理由，打回主干Agent

**双向沟通循环**（重新dispatch时 count+1）：
```
评审Agent给出意见 → 主干Agent独立思考
    │
    ├──→ 认为有理 → 修改 → 重新dispatch → count+1 → 评审Agent重新核实
    │
    └──→ 认为无理 → 坚持己见 + 反馈不修改理由 → 评审Agent重新思考
                                                                │
                                                    ┌───────────┴───────────┐
                                                    │                       │
                                                同意（记录）          不同意（打回）
                                                                     │
                                                                     ▼
                                                              重新dispatch
                                                              count+1
```

## 产物路径

产出文件统一放在项目根目录的 `docs/superflow/` 下：

```
docs/superflow/
├── specs/              # SPEC 文档
│   └── YYYY-MM-DD-feature-name-spec.md
├── plans/              # 实现计划
│   └── YYYY-MM-DD-feature-name-plan.md
├── creatives/         # 创意文档
│   └── YYYY-MM-DD-feature-name-creative.md
├── tests/              # 测试用例
│   ├── YYYY-MM-DD-feature-name-logic-tests.md    # 逻辑测试用例
│   ├── YYYY-MM-DD-feature-name-manual-tests.md  # 非逻辑测试用例
│   └── YYYY-MM-DD-feature-name-test-report.md    # 测试报告
```

设计文档（设计规范、架构说明）放在 `docs/superflow/specs/` 子目录。