---
name: super-flow
description: "SuperFlow — full-stack autonomous development workflow. MUST use this skill when building anything that produces code: features, applications, games, websites, automations, plugins, or any development task. Works with or without explicitly invoking /superflow."
---

# 超级生产线（SuperFlow）

全链路自主开发流程的入口 skill。协调多个 Agent 完成：创意生成 → 产品规划 → 开发 → 测试 → 完成，循环迭代直到所有问题解决。

## 入口分支（请认真思考用户输入，准确判断模式）

| 场景                                 | 触发 |
|------------------------------------|------|
| `/superflow`（无任何参数）                | 直接进入**创意模式** |
| `/superflow <有明确主题主题但细节不明确>`       | 询问选择：创意模式 / 产品模式 |
| `/superflow <有明确主题且细节丰富> 或 <无法识别主题>` | 直接进入**产品模式** |

**主控决断的最高原则**：
- **创意模式**：全自动生产线，**无论何时**都不能把问题抛给用户，必须自行决断确保流程继续
- **产品模式**：半自动生产线，仅「产品 Agent 与用户 Brainstorming」和「请求用户确认 SPEC」允许用户参与，其余情况必须自行决断确保流程继续
- **流程统一**：产品流程（SPEC确认）后，后续流程（架构 → 开发 → 测试 → 评审）均为全自动，无需用户介入

**主控询问固定格式**：
当需要询问用户选择模式时，主控应使用以下格式：
```
主控：根据"<入口分支规则：/superflow <有主题但细节不明确>"，我判断你的输入属于"有主题但细节不明确"的场景。
请选择工作模式：

| 序号 | 模式 | 适用场景 |
|:----:|------|---------|
| 1 | 创意模式 | 无明确规划、探索性需求、需要创新方案 |
| 2 | 产品模式 | 需求明确、有参考实现、渐进式功能 |
```

## 完整流程

> **主干Agent的定义**：流程图中每个阶段对应的任务实现Agent，如：创意Agent、产品Agent...

> **主控作为流程协调者必须要遵守的原则**：优先保证流程完整，不能为了加快进度而忽略规则、跳过流程或步骤，必须确保每个阶段、每个流程、每个步骤都执行到位

> **进入下一阶段流程的唯一依据**：收到主干Agent的”流程结束”反馈，而不是评审Agent的评审通过，更不是”xx已确认/通过”

```
入口分支
    │
    ├──→ 创意模式 ──→ 阶段一：创意流程 ────────────────────────┐
    │     （创意Agent + 创意评审团内循环）                     │
    │                    ↺ 内循环                          │
    │                                                      │
    └──→ 产品模式 ──→ 阶段一：传达用户需求 ─────────────────────┤
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
                                            （开发Agent + 实现评审团）
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

**阶段流程激活任务与输入要求**：

| 阶段 | 激活任务 | 输入要求 |
|------|----------|----------|
| 阶段一：创意流程 | dispatch **创意Agent** | 用户原始需求/主题 |
| 阶段一：传达用户需求 | dispatch **产品Agent** | 用户原始需求/主题（产品模式入口） |
| 阶段二：产品流程 | dispatch **产品Agent** | Creative Brief（创意模式）或 用户需求（产品模式） |
| 阶段三：架构流程 | dispatch **架构Agent** | SPEC.md |
| 阶段四：开发流程 | dispatch **开发Agent** | 实现计划（含架构设计） |
| 阶段五：测试流程 | dispatch **测试Agent** | SPEC.md + 代码实现 |

**评审内循环说明**：
- 每个阶段的内循环包含：主干Agent dispatch 评审Agent → 评审Agent评审 → 主干Agent处理评审意见（循环）
- 评审Agent评审通过后，**必须dispatch主干Agent闭合流程**，主干Agent反馈“流程结束”才算该阶段真正完成
- 主控收到主干Agent“流程结束”后才能进入下一阶段

## 主控的职责与权力

**推理依据要求**：
- 主控的每一次操作或决定必须说明**推理依据**、**推理过程**、**推理结论**和**行为决定**，让用户了解为何如此决策
- **推理依据必须是规则原文**（指明引用的具体规则），而不是用户提示词本身
- 格式示例：`主控：根据"<规则原文>"，我是这么想的：xxx（推理过程），判断为<推理结论>，所以执行<行为决定>`

**信息展示要求**：
- 主控在协调流程时，**必须将Agent间的信息传递和交流展示给用户**
- 包括但不限于：评审意见、反馈回复、brainstorming对话、SPEC确认内容
- 让用户了解流程进展，而非黑箱操作
- **dispatch 任何subagent交代任务时**，必须把传入subagent的上下文展示给用户
- **任何subagent返回任务结果时**，必须把subagent的返回上下文展示给用户
- 所有 Agent 在陈述流程、汇报进展时，**必须加上 agent 名称前缀**
- 格式：`主控：`、`创意Agent：`、`产品Agent：`、`架构Agent：`、`开发Agent：`、`XX评审Agent：`等

**核心职责**：
- **禁止干扰主干Agent的工作流程**：主干Agent有自己的使命，内部工作流必须完整，不允许主控擅自决定主干Agent的工作流程，必须由主干Agent自己决定
- 按顺序启动各主干Agent
- **dispatch主干Agent**：评审意见（包含通过）、决断意见等需要Agent处理的信息，必须dispatch对应主干Agent处理
- **brainstorming对话**：
    - **展示** 产品Agent的问题给创意Agent/用户
    - **dispatch** 创意Agent/用户 回复问题
    - 对话是否完成不由主控决定，主控**必须**将所有的对话dispatch给产品Agent
    - 此过程**不需要主控决断**
- **SPEC确认**：
    - **展示** SPEC文档给创意Agent/用户确认
    - **dispatch** 创意Agent/用户 的回复结果
    - 创意Agent/用户 确认SPEC，不是向主控确认，主控**必须**将确认反馈dispatch给产品Agent
    - 此过程**不需要主控决断**
- **count计数**：进入下一阶段流程时count=0，dispatch 评审Agent时count+1，主控决断后count=-1
- **主控决断真正的上报**：当主干Agent明确表示无法决定、无法推进时，主控必须做出决断

**核对产出物清单**：
- Creative Brief（仅创意模式）
- SPEC.md
- user-guide.md
- 实现计划
- 代码实现
- 测试用例文档 + 单元测试代码
- **测试报告**
- 所有产出物已保存至对应目录

**报告流程完成**：全部问题修复，所有主干 Agent 汇报评审通过，核对产出物清单，确认流程完成。

## 主控决断原则

**为何需要主控决断**：
- 决断流程问题是主控的**核心职责**，不是"必要时才做"——不决断流程就会卡住
- **主控决断错了可以修复**，但不决断代价更大
- 遇到分歧时，选择**最能推进流程**的方案，而不是"最安全的"
- 主干Agent的上报意味着他们已经尽力了，主控决断是最后一道关卡，主控必须做出决断，并dispatch主干Agent执行（count=-1）

**主控决断的唯一依据**：主干Agent上报请求决断或表示无法决定/处理

**区分"dispatch处理"与"真正上报"**：
| 情况 | 类型 | 主控操作 |
|------|------|----------|
| 创意评审要求修复 | dispatch处理 | dispatch 创意Agent 处理评审意见 |
| SPEC评审要求修复 | dispatch处理 | dispatch 产品Agent 处理评审意见 |
| 计划评审要求修复 | dispatch处理 | dispatch 架构Agent 处理评审意见 |
| 实现评审要求修复 | dispatch处理 | dispatch 开发Agent 处理评审意见 |
| brainstorming对话 | 展示+dispatch | 展示内容给对应方 + dispatch 回复 |
| SPEC确认 | 展示+dispatch | 展示SPEC给创意Agent/用户 + dispatch 确认结果 |
| 主干Agent明确说"我无法决定，上报主控" | 真正上报 | 主控做出决断，dispatch主干Agent执行 |

**主控决断执行规则**：
- 主控决断 = **做出决定** + **指明下一步** + **dispatch主干Agent执行决断（count=-1）**
- 主控决断后，**必须dispatch主干Agent执行决断（count=-1）**，否则流程中断
- 主控决断内容示例：
    - "采用方案A，继续进入架构流程"
    - "分歧是细节问题，记录在案，上报评审通过"
    - "dispatch 开发Agent 修复第9个Task，完成后重新评审"
- **主控决断是最终决定**——不是发表意见，不是转达，而是dispatch执行

## Agent 调用参考

详细 Agent 定义和调用方式见 `../agents/` 目录：

- **`../agents/creative-agent.md`** — 创意 Agent（CEO/高级产品战略官，输出 Creative Brief）
- **`../agents/creative-reviewer.md`** — 创意评审团（创新性+可行性+商业价值）
- **`../agents/product-agent.md`** — 产品 Agent（接收 Creative Brief，输出 SPEC.md + user-guide.md）
- **`../agents/spec-reviewer.md`** — SPEC 审查 Agent（验证 SPEC 是否完全执行 Creative Brief 的创意）
- **`../agents/architecture-agent.md`** — 架构 Agent（接收 SPEC，生成实现计划）
- **`../agents/plan-reviewer.md`** — 计划评审 Agent（验证计划完整性和架构合理性）
- **`../agents/developer-agent.md`** — 开发 Agent（按计划执行）
- **`../agents/implementation-reviewer.md`** — 实现评审 Agent（完整性+代码质量+安全）
- **`../agents/tester-agent.md`** — 测试 Agent（产出测试用例文档+单元测试+执行测试+测试报告）
- **`../agents/test-reviewer.md`** — 测试评审 Agent（验证测试用例覆盖率和质量精度）

## **Brainstorming**与**SPEC确认**原则

**识别信息接收方**：谁提出的创意，就有由谁与产品Agent Brainstorming or SPEC确认
- 创意Agent提出的创意，dispatch 创意Agent Brainstorming or SPEC确认
- 用户提出的创意（需求），展示给用户 Brainstorming or SPEC确认
- 信息接收方的回复不是回给你主控的，而是给产品Agent的，必须dispatch 产品agent
- 主控在此环节只充当传话筒，不必理解传递内容的含义
- **示例**：
| 环节 | 正确做法 | 错误做法 |
|------|----------|----------|
| 与用户brainstorming | 产品Agent问用户"选择A还是B"，主控将问题传给用户，用户回复后主控立即传给产品Agent | 主控收到用户回复后自行判断"用户选了A"或没有告知产品Agent |
| 与用户SPEC确认 | 用户确认SPEC，主控立即将"用户确认通过"传给产品Agent | 主控自行决定"用户没意见，SPEC通过" |
| 与创意Agent brainstorming | 产品Agent问创意Agent"这些问题需要你回答"，主控将问题传给创意Agent，创意Agent回复后主控立即传给产品Agent | 主控收到创意Agent回复后自行判断或没有告知产品Agent |
| 与创意Agent SPEC确认 | 创意Agent确认SPEC，主控立即将"创意Agent确认通过"传给产品Agent | 主控自行决定"创意Agent没意见，SPEC通过" |
| 收到创意Agent回复 | 主控立即dispatch给产品Agent处理 | 主控先思考"这个回复是否合理"再决定是否传递 |

## 评审反馈处理原则

**必须遵守**：
- **主控不必理解评审Agent反馈的结果**，无条件dispatch 主干Agent处理
    - 正确做法：主控收到**任意评审Agent** "评审通过" → dispatch 对应主干Agent 闭合流程
    - 错误做法：主控收到评审通过 → **跳过闭合流程，直接进入下一阶段**
- **主干Agent反馈流程结束** → 真正的阶段流程结束，进入下一个阶段
    - 正确做法：主控收到主干Agent"流程结束" → 主控进入下一阶段
    - 错误做法：主控收到主干Agent"流程结束" → 主控**没有进入下一阶段**

**主控评审循环控制**：
- 主控追踪每个流程阶段的评审循环次数，每流程阶段开始时 count = 0
- **每次 dispatch 评审Agent时** count+1
- **dispatch** 主干Agent处理评审意见时，附带count值
- 主控**不自行判断**，根据主干Agent的反馈决定下一步
- 主干Agent返回"流程结束" → 进入下一阶段；"汇总分歧上报主控决断" → 主控决断后 dispatch 主干Agent执行决断（count=-1）
- **告知用户**：count > 0 时，主控告知用户"当前为第N轮评审"。count <= 0时，不可显示count值

**count值含义**：
| count | 含义 |
|-------|------|
| 0 | 初始值 |
| 1~5 | 评审循环第N轮 |
| -1 | 主控决断意见 |

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

**双向沟通循环**：
```
评审Agent反馈结果 → 主干Agent独立思考
    │
    ├──→ 认为有理 → 修改 → 重新dispatch → 评审Agent重新核实
    │
    └──→ 认为无理 → 坚持己见 + 反馈不修改理由 → 评审Agent重新思考
                                                                │
                                                    ┌───────────┴───────────┐
                                                    │                       │
                                                同意（记录）          不同意（打回）
                                                                     │
                                                                     ▼
                                                              重新dispatch
```

## 产物路径

产出文件统一放在项目根目录的 `docs/superflow/` 下：

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
├── creatives/         # 创意文档
│   └── YYYY-MM-DD-feature-name-creative.md
├── tests/              # 测试用例
│   ├── YYYY-MM-DD-feature-name-logic-tests.md    # 逻辑测试用例
│   ├── YYYY-MM-DD-feature-name-manual-tests.md  # 非逻辑测试用例
│   └── YYYY-MM-DD-feature-name-test-report.md    # 测试报告
```

设计文档（设计规范、架构说明）放在 `docs/superflow/specs/` 子目录。