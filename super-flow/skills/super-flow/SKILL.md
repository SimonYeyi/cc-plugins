---
name: super-flow
description: "SuperFlow — full-stack autonomous development workflow. MUST use this skill when building anything that produces code: features, applications, games, websites, automations, plugins, or any development task. Works with or without explicitly invoking /superflow."
---

# 超级生产线（SuperFlow）

全链路自主开发流程的入口 skill。协调多个 Agent 完成：创意生成 → 产品规划 → 开发 → 测试 → 完成，循环迭代直到所有问题解决。

## 入口分支

| 场景                            | 触发 |
|-------------------------------|------|
| `/superflow`（无任何参数）           | 直接进入**创意模式** |
| `/superflow <有主题但无明确功能细节>`    | 询问选择：创意模式 / 产品模式 |
| `/superflow <有主题有细节> 或 <模糊主题>` | 直接进入**产品模式**（brainstorm 流程，探讨需求） |

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

**SPEC确认统一规则**：谁提出创意，谁确认SPEC
- 创意模式：Creative Brief由创意Agent提出 → **创意评审团内循环评审通过**；SPEC由创意Agent确认（无需用户确认）
- 产品模式：创意由用户提出 → 用户确认SPEC

**评审规则**：
- 每个阶段由主干Agent + 内嵌审查Agent组成，形成"完成→审查→修复→再审查"的内循环
- 审查通过后进入下一个阶段
- 创意阶段（仅创意模式）的内循环在产品阶段交接前完成

## 创意 → 产品交接流程

评审通过（创意评审团内循环通过）后，创意 Agent 的 **Creative Brief（创意说明书）** 移交给产品 Agent 转化为 **SPEC.md**。（无需用户确认创意brief）

**产品 Agent 工作流程：**
1. **读取** Creative Brief（创意说明书）
2. **brainstorm式对话对齐**（通过主控转发）：
   - 创意模式（与创意Agent）：一次全问，产品Agent提出问题 → 主控转发 → 创意Agent一次性回答所有问题
   - 产品模式（与用户）：一次一问，产品Agent提出问题 → 主控转发 → 用户回答
3. **整合** brainstorming所有内容，展示完整SPEC文档设计（**此时不要写入文件**）
4. **确认** 与创意提出者确认SPEC（必须先确认：创意模式下由创意 Agent 确认，产品模式下才由用户确认）— 通过主控展示完整SPEC
5. **写入** 确认后才能写入 `docs/superflow/specs/YYYY-MM-DD-feature-name-spec.md`

**确认循环（必须执行）**：
1. 主控展示完整SPEC给创意提出者确认
2. 创意提出者提出修改意见 → 主控转发给产品Agent
3. 产品Agent修改SPEC
4. 主控再次展示完整SPEC给创意提出者确认
5. **循环直到创意提出者明确表示没有任何意见** → 才能写入

**重要区分**：
- **确认**：由创意提出者（创意Agent/用户）主观判断SPEC是否符合自己的创意/需求，**不是评审**
- **评审**：由SPEC审查Agent客观验证SPEC是否完整执行了Creative Brief或brainstorming结果，是独立的内循环流程

**关键原则：**
- 创意 Agent 决定"做什么、为什么做" — 产品 Agent 决定"怎么做、功能细节"
- 如果 SPEC 草稿与创意方向有偏差，创意 Agent 有权要求修正
- 先确认再写入，不得先写入再确认

## 沟通规范：
- 所有 Agent 在陈述流程、汇报进展时，**必须加上 agent 名称前缀**
- 格式：`主控：`、`创意Agent：`、`产品Agent：`、`架构Agent：`、`开发Agent：`、`XX评审Agent：`等
- 示例：`主控：启动创意流程` → `创意Agent：生成创意Brief` → `创意评审团：评审通过`
- 便于主控追踪流程节点和责任归属

## 角色与职责

| 角色 | 职责 | 规模 |
|------|------|------|
| **主控（我）** | 按顺序启动各主干Agent、协调阶段交接、监控内循环、**主控决断所有主干Agent升级问题（除brainstorming转发和SPEC确认外）** | 当前 session |
| **创意 Agent** | CEO/高级产品战略官。输出 Creative Brief（创意说明书），经评审通过后移交产品 Agent | 1 个 |
| **创意评审团 — 子功能创意** | 创新性 + 可行性 + 商业价值，每个实例评估全部视角，3 个并行评审 | 3 个 |
| **创意评审团 — 项目立项创意** | 创新性 + 可行性 + 商业价值，每个实例评估全部视角，5 个并行评审 | 5 个 |
| **产品 Agent** | 接收用户/创意 Agent 的创意，进行brainstorm式对话（创意模式：一次全问；产品模式：一次一问）后转化为 SPEC.md | 1 个 |
| **SPEC 审查 Agent** | 验证 SPEC 是否完全执行 Creative Brief（创意模式）或 brainstorming对话记录（产品模式）的创意 | 1 个 |
| **架构 Agent** | 接收 SPEC，生成实现计划（含架构设计） | 1 个 |
| **计划评审 Agent** | 验证计划完整性、架构合理性 | 1 个 |
| **开发 Agent** | 按计划执行 → 修复问题 | 1 个 |
| **实现评审团** | 完整性 + 代码质量 + 安全，每个实例评估全部视角，3 个并行评审 | 3 个 |
| **测试 Agent** | 产出测试用例文档（逻辑+非逻辑）+ 编写单元测试 + 执行测试 + 生成测试报告；**测试不通过时：测试代码错误打回测试Agent，功能不通过打回开发Agent** | 1 个 |
| **测试评审Agent** | 验证测试用例覆盖率和质量精度（Coverage + Precision + Detail + Completeness） | 1 个 |

## 评审/审查循环规则

**内循环机制**：
- 每个主干Agent完成工作后，启动自己的**内嵌审查Agent**进行审查
- 审查有意见时，由该主干Agent直接处理问题，形成"工作→审查→修复→再审查"闭环
- 审查通过后，由该主干Agent通知主控，主控再启动下一个主干Agent

**主干Agent处理评审意见的职责**：
1. **独立思考**：对每条评审意见进行独立判断，不盲目接受
2. **有问题则修改**：如果认为评审意见确实有理，则按意见修改
3. **坚持己见并反馈**：如果认为评审意见有问题，可以坚持己见，但必须将不修改的具体理由反馈给评审Agent

**评审Agent处理反馈意见的职责**：
1. **重新核实**：对主干Agent已修复的问题重新核实
2. **重新思考**：对主干Agent反馈的不修改意见，重新思考是否同意
   - 如果同意：不追究，记录在案
   - 如果不同意：给出明确的不同意理由，打回主干Agent

**双向沟通循环**：
```
评审Agent给出意见 → 主干Agent独立思考
    │
    ├──→ 认为有理 → 修改 → 反馈给评审Agent重新核实
    │
    └──→ 认为无理 → 坚持己见 + 反馈不修改理由 → 评审Agent重新思考
                                                                │
                                                    ┌───────────┴───────────┐
                                                    │                       │
                                                同意（记录）          不同意（打回）
```

**评审意见不一致时**：
- 主干Agent与内嵌审查Agent之间可以直接通信
- 分歧采用**双向沟通机制**解决，而非简单投票
- 循环直到达成共识，或升级主控决断
- **评审最大重试次数**：每个内循环最多重试 **5 次**，5 次后仍未通过需升级主控决断

**主控职责**：
- 按顺序启动各主干Agent
- **转发brainstorming对话**：产品Agent与创意Agent/用户之间的brainstorming通过主控转发（此过程**不需要主控决断**）
- **展示SPEC文档**：创意Agent/用户确认SPEC时，由主控展示完整文档（**确认过程不需要主控决断**）
- **执行正常转发**：当主干Agent明确要求"转发给X处理"时，这是正常流程步骤，**直接执行转发，不需要主控决断**
- **主控决断真正的升级**：只有当主干Agent明确表示无法决定、无法推进时，才需要主控决断

**区分"正常转发"与"真正升级"**：
| 情况 | 类型 | 主控操作 | 打回给 |
|------|------|----------|-------|
| 创意评审要求修复 | 正常转发 | 直接转发，不决断 | 创意Agent |
| SPEC评审要求修复 | 正常转发 | 直接转发，不决断 | 产品Agent |
| 计划评审要求修复 | 正常转发 | 直接转发，不决断 | 架构Agent |
| 实现评审要求修复 | 正常转发 | 直接转发，不决断 | 开发Agent |
| brainstorming转发确认/修改 | 正常转发 | 直接转发，不决断 | 目标Agent |
| 主干Agent明确说"我无法决定，升级主控" | 真正升级 | 主控决断，做出决定 | — |

**主控决断执行规则**：
- 主控决断 = **做出决定** + **指明下一步** + **转发决断意见给主干Agent**
- 主控决断后，**必须转发决断意见（count=6）给主干Agent**，否则流程中断
- 主控决断内容示例：
  - "采用方案A，继续进入架构流程"
  - "分歧是细节问题，记录在案，流程继续"
  - "打回开发Agent修复第3个Task，完成后重新评审"
- **你的主控决断是最终决定**——不是发表意见，不是转达，而是推进

**主控决断**（仅针对主干Agent升级问题，brainstorming转发和SPEC确认除外）：
- 主控决断是你的**核心职责**，不是"必要时才做"——不决断流程就会卡住
- **主控决断错了可以修复**，但不决断代价更大
- 遇到分歧时，选择**最能推进流程**的方案，而不是"最安全的"
- 主干Agent的升级意味着他们已经尽力了，你的主控决断是最后一道关卡

**主控评审循环控制**：
- 主控追踪每个阶段的评审循环次数，每阶段开始时 count = 0
- 转发评审结果给主干Agent时附带count值
- 主控**不自行判断**，根据主干Agent的反馈决定下一步
- 主干Agent返回"通过" → 进入下一阶段；"修复" → count+1重新dispatch；"汇总分歧" → 主控决断后**必须转发决断意见（count=6）**给主干Agent

**count值含义**：
| count | 含义 |
|-------|------|
| 0~5 | 评审循环次数 |
| 6 | 主控决断意见（主干Agent必须遵守） |

**测试Agent特殊协议**：
- 测试Agent反馈"功能不通过" → 主控转发给开发Agent修复
- 开发Agent修复完成 → 主控转发给测试Agent继续执行

**终止条件**：全部问题修复，所有评审/审查 agent 全部通过，且主控确认。

**产出物清单**（主控最终确认时核对）：
- Creative Brief（仅创意模式）
- SPEC.md
- 实现计划
- 代码实现
- 测试用例文档 + 单元测试代码
- **测试报告**
- 所有产出物已保存至对应目录

## 文件路径

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
- **`../agents/test-reviewer.md`** — 测试评审Agent（验证测试用例覆盖率+质量精度）

## 审查顺序

1. **SPEC 审查**：验证 SPEC 是否完全执行 Creative Brief 的创意（SPEC 确认后，开发前）
2. **计划评审**：架构 Agent 生成计划后，计划评审 Agent 验证计划完整性及架构合理性（计划完成后，开发前）
3. **实现评审团**：验证实现完整性 + 代码质量 + 安全（3个并行实例，开发完成后）
4. **测试评审**：验证测试用例覆盖率 + 质量精度（Precision + Detail + Completeness）
5. **主控确认**：所有审查通过后，主控最终确认
