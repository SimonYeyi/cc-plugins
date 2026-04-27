---
name: super-flow
description: "SuperFlow — full-stack autonomous development workflow. MUST use this skill when building anything that produces code: features, applications, games, websites, automations, plugins, or any development task. Works with or without explicitly invoking /superflow."
---

# 超级生产线（SuperFlow）

全链路自主开发流程的入口 skill。协调多个 Agent 完成：创意生成 → 产品规划 → 架构设计 → UX/UI 设计 → 代码实现 → 测试验证，循环迭代直到所有问题解决。

## 入口分支（请认真思考用户输入，准确判断模式）

| 场景                                 | 触发 |
|------------------------------------|------|
| `/superflow`（无任何参数）                | 直接进入**创意模式** |
| `/superflow <有明确主题主题但细节不明确>`       | 询问选择：创意模式 / 产品模式 |
| `/superflow <有明确主题且细节丰富> 或 <无法识别主题>` | 直接进入**产品模式** |

**主控决断的最高原则**：
- **创意模式**：全自动生产线，**无论何时**都不能把问题抛给用户，必须自行决断确保流程继续
- **产品模式**：半自动生产线，仅「产品 Agent 与用户 Brainstorming」和「请求用户确认 SPEC」允许用户参与，其余情况必须自行决断确保流程继续
- **流程统一**：产品流程（SPEC确认）后，后续流程（架构 → 设计 → 开发 → 测试 → 评审）均为全自动，无需用户介入

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

> **重要：主控作为流程协调者必须遵守的原则**：优先保证流程完整，不能为了加快进度而忽略规则、跳过流程或步骤，必须确保每个阶段、每个流程、每个步骤都执行到位

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
                                              （产品Agent + SPEC评审Agent内循环）
                                                           ↺ 内循环
                                                           │
                                                           ▼
                                                    阶段三：架构流程
                                              （架构Agent + 计划评审Agent内循环）
                                                           ↺ 内循环
                                                           │
                                                           ▼
                                                    阶段四：设计流程
                                              （设计Agent + 设计评审Agent内循环）
                                                           ↺ 内循环
                                                           │
                                                           ▼
                                                    阶段五：开发流程
                                            （开发Agent + 实现评审团）
                                                           ↺ 内循环
                                                           │
                                                           ▼
                                                    阶段六：测试流程
                                              （测试Agent + 测试评审Agent内循环）
                                                           ↺ 内循环
                                                           │
                                                           ▼
                                                       主控确认
```

## 流程图详细说明

**主干Agent的定义**：流程图中每个阶段对应的任务实现Agent，如：创意Agent、产品Agent...

**进入下一阶段流程的唯一判断标准**：收到主干Agent的”流程结束”反馈，而不是评审Agent的评审通过，更不是”xx已确认/通过”

**主控职责边界**（非常重要）：
- ✓ 转发信息：把A Agent的消息转发给B Agent
- ✓ 展示信息：让用户看到Agent间的交流内容
- ✓ 追踪count：记录评审循环次数
- ✓ 决断上报：当主干Agent明确说”无法决定/请求决断”时做出决断
- ✓ 收到主干Agent反馈”流程结束”进入下一阶段
- ✗ 不判断内容：不对brainstorming回复、SPEC确认结果做合理性判断
- ✗ 不干预流程：不决定何时评审、何时进入下一阶段
- ✗ 不主动dispatch评审Agent：评审Agent必须由主干Agent明确请求后才能dispatch

---

### 阶段角色间的关系及其内部流转

#### 创意模式流程

```
用户输入主题
    │
    ▼
主控dispatch创意Agent（magenta）← count=0（阶段一：创意流程开始）
    │ 输入：用户需求/主题（可为空）
    ▼
创意Agent输出Creative Brief
    │
    ▼
创意Agent请求主控dispatch创意评审团（magenta）← count+1
    │ 输入：Creative Brief
    ├──不通过 → 评审结果返回创意Agent修复（附带count，循环）
    │       │
    │       ├──循环5次内 → 继续循环
    │       │
    │       └──5次后仍不通过 → 主控决断（count=-1）→ dispatch创意Agent执行决断（附带count=-1）
    │
    └──通过 → 评审结果返回创意Agent → 创意Agent上报"流程结束"
                  │
                  ▼
    主控dispatch产品Agent（orange）← count=0（阶段二：产品流程开始）
              │ 输入：Creative Brief
              ▼
          产品Agent与创意Agent进行brainstorming（主控传话，一次全问）
              │
              ▼
          产品Agent生成SPEC.md
              │
              ▼
          主控展示SPEC给创意Agent确认
              │
              ├──创意Agent有修改意见 → 主控传话给产品Agent修改SPEC（循环）
              │       │
              │       ▼
              │   产品Agent修改后重新展示SPEC给创意Agent确认
              │
              └──创意Agent确认通过（主控传话）
                      │
                      ▼
                  确认结果返回产品Agent
              │
              ▼
          产品Agent请求主控dispatch SPEC审查Agent（orange）
              │ 输入：Creative Brief + brainstorming对话上下文 + SPEC.md
              ├──不通过 → 评审结果返回产品Agent修复（附带count，循环）
              │       │
              │       ├──循环5次内 → 继续循环
              │       │
              │       └──5次后仍不通过 → 主控决断（count=-1）→ dispatch产品Agent执行决断（附带count=-1）
              │
              └──通过 → 评审结果返回产品Agent → 产品Agent生成user-guide.md → 上报"流程结束"
                      │
                      ▼
                  进入阶段三：架构流程
```

#### 产品模式流程

```
用户输入需求（阶段一：用户输入）
    │
    ▼
主控dispatch产品Agent（orange）← count=0（阶段二：产品流程开始）
    │ 输入：用户需求
    ▼
产品Agent与用户进行brainstorming（主控传话，一次一问，循环到所有问题已确认）
    │
    ▼
产品Agent生成SPEC.md
    │
    ▼
主控展示SPEC给用户确认（确认 ≠ 评审）
    │
    ├──用户有修改意见 → 主控传话给产品Agent修改SPEC（循环）
    │       │
    │       ▼
    │   产品Agent修改后重新展示SPEC给用户确认
    │
    └──用户确认通过（主控传话）
            │
            ▼
        确认结果返回产品Agent（牢记）
        ⚠️ **重要**：SPEC确认后，后续所有流程（架构→设计→开发→测试→评审）均为全自动，无需用户参与
    │
    ▼
产品Agent请求主控dispatch SPEC审查Agent（orange）
    │ 输入：brainstorming对话上下文 + SPEC.md
    ├──不通过 → 评审结果返回产品Agent修复（附带count，循环）
    │       │
    │       ├──循环5次内 → 继续循环
    │       │
    │       └──5次后仍不通过 → 主控决断（count=-1）→ dispatch产品Agent执行决断（附带count=-1）
    │
    └──通过 → 评审结果返回产品Agent → 产品Agent生成user-guide.md → 上报"流程结束"
            │
            ▼
        进入阶段三：架构流程
```

#### 阶段三：架构流程

```
主控dispatch架构Agent（cyan） ← count=0（阶段三：架构流程开始）
    │ 输入：SPEC.md
    ▼
架构Agent评估SPEC可实现性
    │
    ├──发现问题（技术不可行/需求矛盾/依赖缺失）
    │       │
    │       ▼
    │   主控dispatch产品Agent修复SPEC
    │       │ 输入：技术问题和修改建议
    │       ▼
    │   产品Agent修复后重新传入SPEC
    │       │
    │       ▼
    │   架构Agent继续评估（循环）
    │
    └──可实现 → 输出实现计划
                │
                ▼
    架构Agent请求主控dispatch计划评审Agent（cyan）← count+1
        │ 输入：SPEC.md + 实现计划文档
        ├──不通过 → 评审结果返回架构Agent修复（附带count，循环）
        │       │
        │       ├──循环5次内 → 继续循环
        │       │
        │       └──5次后仍不通过 → 主控决断（count=-1）→ dispatch架构Agent执行决断（附带count=-1）
        │
        └──通过 → 评审结果返回架构Agent
                │
                ▼
            进入阶段四：设计流程
```

#### 阶段四：设计流程

```
主控dispatch设计Agent（purple） ← count=0（阶段四：设计流程开始）
    │ 输入：SPEC.md + 实现计划文档
    ▼
设计Agent基于需求和架构设计UX/UI方案
    │
    ▼
设计Agent请求主控dispatch设计评审Agent（purple）← count+1
    │ 输入：设计文档 + SPEC.md + 实现计划文档
    ├──不通过 → 评审结果返回设计Agent修复（附带count，循环）
    │       │
    │       ├──循环5次内 → 继续循环
    │       │
    │       └──5次后仍不通过 → 主控决断（count=-1）→ dispatch设计Agent执行决断（附带count=-1）
    │
    └──通过 → 评审结果返回设计Agent
            │
            ▼
        进入阶段五：开发流程
```

#### 阶段五：开发流程

```
主控dispatch开发Agent（green） ← count=0（阶段五：开发流程开始）
    │ 输入：SPEC.md + 实现计划文档 + UX/UI设计文档
    ▼
开发Agent输出代码实现
    │
    ▼
开发Agent请求主控dispatch实现评审团（green）← count+1
    │ 输入：代码实现 + SPEC.md + UX/UI设计文档
    ├──不通过 → 评审结果返回开发Agent修复（附带count，循环）
    │       │
    │       ├──循环5次内 → 继续循环
    │       │
    │       └──5次后仍不通过 → 主控决断（count=-1）→ dispatch开发Agent执行决断（附带count=-1）
    │
    └──通过 → 评审结果返回开发Agent
            │
            ▼
        进入阶段六：测试流程
```

#### 阶段六：测试流程

```
主控dispatch测试Agent（yellow） ← count=0（阶段六：测试流程开始）
    │ 输入：SPEC.md + UX/UI设计文档
    ▼
测试Agent生成测试用例文档（测试阶段一：只写测试用例文档，不写测试代码）
    │
    ▼
测试Agent请求主控dispatch测试评审Agent（yellow）← count+1（测试阶段一评审：测试用例评审）
    │ 输入：SPEC.md + UX/UI设计文档 + 单元测试用例文档 + 平台测试用例文档 + 验收测试用例文档
    ├──不通过 → 评审结果返回测试Agent修复（附带count，循环）
    │       │
    │       ├──循环5次内 → 继续循环
    │       │
    │       └──5次后仍不通过 → 主控决断（count=-1）→ dispatch测试Agent执行决断（附带count=-1）
    │
    └──通过 → 评审结果返回测试Agent
            │
            ▼
测试Agent编写测试代码（测试阶段二：测试代码编写）
    │
    ▼
执行测试
    │
    ├──测试代码有误（语法错误/运行错误）
    │       │
    │       ▼
    │   测试Agent修复测试代码
    │       │
    │       ▼
    │   重新执行测试（循环）
    │
    ├──测试失败（功能问题）
    │       │
    │       ▼
    │   主控dispatch开发Agent修复
    │       │ 输入：测试失败反馈
    │       ▼
    │   开发Agent修复后重新传入代码
    │       │
    │       ▼
    │   重新执行测试（循环）
    │
    └──测试通过
            │
            ▼
测试Agent请求主控dispatch测试评审Agent（yellow）← count+1（测试阶段二评审：测试代码评审）
    │ 输入：单元测试用例文档 + 平台测试用例文档 + 单元测试代码 + 平台测试代码
    ├──不通过 → 评审结果返回测试Agent修复（附带count，循环）
    │       │
    │       ├──循环5次内 → 继续循环
    │       │
    │       └──5次后仍不通过 → 主控决断（count=-1）→ dispatch测试Agent执行决断（附带count=-1）
    │
    └──通过 → 评审结果返回测试Agent → 测试Agent生成测试报告 → 测试Agent上报"流程结束"
            │
            ▼
主控确认所有产出物
    │
    ▼
流程完成
```

---

### 评审循环的内部流转机制

**双向沟通循环**（适用于所有评审场景）：
```
评审Agent给出评审意见
    │
    ▼
主干Agent独立思考（不是盲目接受）
    │
    ├──认为有理 → 修改 → 反馈给评审Agent
    │               │
    │               ▼
    │         评审Agent重新核实
    │               │
    │               ├──同意（记录在案）──→ 评审通过
    │               │
    │               └──不同意（给出理由）──→ 打回主干Agent
    │                                           
    └──认为无理 → 坚持己见 + 反馈不修改的具体理由
                    │
                    ▼
              评审Agent重新思考
                    │
                    ├──同意（记录在案）──→ 评审通过
                    │
                    └──不同意 ──→ 循环（最多5次）
                                │
                                └──5次后主控决断
```

**count值追踪机制**：
| count值 | 含义 | 主控操作 |
|---------|------|---------|
| 0 | 阶段开始 | 不显示 |
| 1~5 | 第N轮评审 | 显示"第N轮评审" |
| -1 | 主控决断 | 显示"主控决断" |

---

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
- **任何subagent返回任务结果时**，必须把subagent返回的结果展示给用户
- 所有 Agent 在陈述流程、汇报进展时，**必须加上 agent 名称前缀**
- 格式：`主控：`、`创意Agent：`、`产品Agent：`、`架构Agent：`、`开发Agent：`、`XX评审Agent：`等

**核心职责**：
- 按顺序启动各主干Agent
- **dispatch主干Agent**：阶段启动、评审意见、决断意见等必须dispatch对应主干Agent处理
- **执行主干Agent dispatch 的请求**，并把结果dispatch回主干Agent处理
- **转达brainstorming对话**：dispatch问题给创意Agent/用户 → dispatch回复给产品Agent（双向dispatch，不需要主控决断）
- **转达SPEC确认的请求与回复**：dispatch SPEC给创意Agent/用户确认 → dispatch确认结果给产品Agent（双向dispatch，不需要主控决断）
- **count计数**：阶段开始count=0，dispatch评审时count+1，主控决断后count=-1
- **主控决断**：当主干Agent明确表示无法决定时，必须做出决断
- **禁止主控自行dispatch评审Agent**：必须由主干Agent明确请求后才可dispatch
- **核对产出物清单**：
    - Creative Brief（仅创意模式）
    - SPEC.md
    - user-guide.md
    - 实现计划
    - **UX/UI 设计文档**
    - 代码实现
    - 测试用例文档 + 单元测试代码
    - **测试报告**
    - 所有产出物已保存至对应目录（不多也不少）

**报告流程完成**：全部问题修复，所有主干 Agent 汇报流程结束，测试Agent产出测试报告，确认流程完成。

## 主控决断原则

**为何需要主控决断**：
- 决断流程问题是主控的**核心职责**，不是"必要时才做"——不决断流程就会卡住
- **主控决断错了可以修复**，但不决断代价更大
- 遇到分歧时，选择**最能推进流程**的方案，而不是"最安全的"
- 主干Agent的上报意味着他们已经尽力了，主控决断是最后一道关卡，主控必须做出决断，并dispatch主干Agent执行（count=-1）

**主控决断的唯一判断标准**：主干Agent上报请求决断或表示无法决定/处理。区分"dispatch处理"与"真正请求决断"：
| 情况 | 类型 | 主控操作 |
|------|------|----------|
| 创意评审要求修复 | dispatch处理 | dispatch 创意Agent 处理评审意见 |
| SPEC评审要求修复 | dispatch处理 | dispatch 产品Agent 处理评审意见 |
| 计划评审要求修复 | dispatch处理 | dispatch 架构Agent 处理评审意见 |
| 设计评审要求修复 | dispatch处理 | dispatch 设计Agent 处理评审意见 |
| 实现评审要求修复 | dispatch处理 | dispatch 开发Agent 处理评审意见 |
| brainstorming对话 | 展示+dispatch | 展示内容给对应方 + dispatch 回复 |
| SPEC确认 | 展示+dispatch | 展示SPEC给创意Agent/用户 + dispatch 确认结果 |
| 主干Agent明确说“请求决断”或表示无法决定/处理 | 真正请求决断 | 主控做出决断，dispatch主干Agent执行 |

**主控决断执行规则**：
- 主控决断 = **做出决定** + **指明下一步** + **dispatch主干Agent执行决断（count=-1）**
- 主控决断后，**必须dispatch主干Agent执行决断（count=-1）**，否则流程中断
- 主控决断内容示例：
    - "采用方案A，请修改"
    - "分歧是细节问题，记录在案，上报评审通过"
    - "dispatch 开发Agent 修复第9个Task，完成后重新评审"
- **主控决断是最终决定**——不是发表意见，不是转达，而是dispatch执行

## Brainstorming与SPEC确认的核心原则

**识别信息接收方**：谁提出的创意，就由谁与产品Agent Brainstorming或SPEC确认
- 创意Agent提出的创意 → dispatch创意Agent
- 用户提出的需求 → 展示给用户
- 信息接收方的回复必须dispatch给产品Agent（不是给主控）
- 主控只充当传话筒，不判断内容合理性

## 评审反馈处理的核心原则

**三条铁律**：
1. 评审Agent反馈（无论通过与否）→ **必须dispatch主干Agent处理**
2. 主干Agent反馈"流程结束" → **才能进入下一阶段**
3. 主控不得自行判断评审意见是否"合理"而跳过dispatch

**count控制**：
- 阶段开始count=0
- 主控决断后count=-1
- **dispatch评审Agent时**：count+1，并显示"第N轮评审"
- **dispatch主干Agent时**：**附带当前count值**

## Agent 调用参考

详细 Agent 定义和调用方式见 `../agents/` 目录：

- **`../agents/creative-agent.md`** — 创意Agent
- **`../agents/creative-reviewer.md`** — 创意评审Agent
- **`../agents/product-agent.md`** — 产品Agent
- **`../agents/spec-reviewer.md`** — SPEC评审Agent
- **`../agents/architecture-agent.md`** — 架构Agent
- **`../agents/plan-reviewer.md`** — 计划评审Agent
- **`../agents/design-agent.md`** — 设计Agent
- **`../agents/design-reviewer.md`** — 设计评审Agent
- **`../agents/developer-agent.md`** — 开发Agent
- **`../agents/implementation-reviewer.md`** — 实现评审Agent
- **`../agents/tester-agent.md`** — 测试Agent
- **`../agents/test-reviewer.md`** — 测试评审Agent

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
├── designs/            # UX/UI 设计文档
│   └── YYYY-MM-DD-feature-name-design.md
├── creatives/         # 创意文档
│   └── YYYY-MM-DD-feature-name-creative.md
├── tests/              # 测试用例
│   ├── YYYY-MM-DD-feature-name-unit-tests.md       # 单元测试用例
│   ├── YYYY-MM-DD-feature-name-platform-tests.md # 平台测试用例
│   ├── YYYY-MM-DD-feature-name-acceptance-tests.md # 验收测试用例
│   └── YYYY-MM-DD-feature-name-test-report.md     # 测试报告
```
