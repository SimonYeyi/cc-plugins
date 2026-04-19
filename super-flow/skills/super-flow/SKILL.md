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

## 角色与职责

| 角色 | 职责 | 规模 |
|------|------|------|
| **主控（我）** | 按顺序启动各主干Agent、协调阶段交接、监控内循环、**裁断所有主干Agent升级问题（除brainstorming转发和SPEC确认外）** | 当前 session |
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
- 循环直到达成共识，或升级主控裁断
- **评审最大重试次数**：每个内循环最多重试 **5 次**，5 次后仍未通过需升级主控裁断

**主控职责**：
- 按顺序启动各主干Agent
- **转发brainstorming对话**：产品Agent与创意Agent/用户之间的brainstorming通过主控转发（此过程**不需要裁断**）
- **展示SPEC文档**：创意Agent/用户确认SPEC时，由主控展示完整文档（**确认过程不需要裁断**）
- **裁断所有主干Agent的升级问题**：除brainstorming转发和SPEC确认外，任何主干Agent抛出的问题主控都必须裁断，根据问题内容做出决策并继续流程

**测试Agent响应与主控执行**：

测试Agent返回时必须包含ESCALATE指令，主控只做传递：

| 响应 | 主控操作 |
|------|----------|
| ESCALATE_TEST_AGENT_STAGE1 / ESCALATE_TEST_AGENT_STAGE2 | 把枚举传回测试Agent，由测试Agent解析决定下一步 |
| ESCALATE_DEVELOPER | 打回开发Agent修复 |
| ESCALATE_MAIN_CONTROLLER | 主控确认流程完成 |

**主控执行规则**：
```
收到测试Agent响应：
├── ESCALATE_TEST_AGENT_STAGE1 → 把枚举传回测试Agent
├── ESCALATE_TEST_AGENT_STAGE2 → 把枚举传回测试Agent
├── ESCALATE_DEVELOPER → 打回开发Agent
└── ESCALATE_MAIN_CONTROLLER → 主控确认流程完成

主干Agent升级问题：
└── 主控裁断（除brainstorming转发和SPEC确认外，所有主干Agent抛出的问题都必须裁断）
```

**终止条件**：全部问题修复，所有评审/审查 agent 全部通过，且主控确认。

**完成定义**：测试评审通过后，由主控 Agent 最终确认所有产出物齐全、流程无遗漏，正式宣告流程完成。

**产出物流程**：
1. 测试Agent执行测试 → 生成**测试报告**
2. 测试评审Agent审查测试用例覆盖率
3. 覆盖率达到要求 → 主控确认所有产出物 → 流程完成
4. 覆盖率达到要求但有遗留问题 → 记录在案 → 主控确认 → 流程完成
5. 5次循环后仍有分歧 → 主控决断 → 根据决断结果处理

**产出物清单**：
- Creative Brief（仅创意模式）
- SPEC.md
- 实现计划
- 代码实现
- 测试用例文档 + 单元测试代码
- **测试报告**
- 所有产出物已保存至对应目录

**内循环描述**（按执行顺序）：

**创意评审循环**（仅创意模式）：
创意评审失败 → 创意Agent根据意见修改Creative Brief → 重新进入创意评审团讨论 → 通过？进入产品流程

**SPEC审查循环**：
SPEC审查失败 → 产品Agent根据意见修改SPEC → 重新进入SPEC审查Agent → 通过？进入架构流程

**计划评审循环**：
计划评审失败 → 架构Agent根据意见重新设计 → 计划评审复审 → 直到计划评审通过 → 进入开发流程

**架构阶段SPEC问题处理**：
1. 架构Agent或计划评审发现SPEC可实现性问题
2. 标记问题类型：
   - **技术约束冲突**（如性能要求超出硬件能力）
   - **依赖缺失**（如需第三方 API 但未说明集成方式）
   - **逻辑矛盾**（如同时要求实时性和离线可用）
3. 打回产品Agent修改SPEC文档（覆盖更新）
4. **重新进入SPEC评审循环**（由 SPEC 评审 Agent 验证修改后的 SPEC）
5. SPEC评审通过后重新进入架构流程

**实现评审循环**：
实现评审失败 → 开发Agent根据意见修复代码 → 重新进入实现评审团（内循环） → 通过？进入测试流程

**测试评审循环**：
- 阶段一评审失败 → 测试Agent补充测试用例 → 重新提交阶段一评审 → 通过？进入阶段二
- 阶段二评审失败 → 测试Agent修复问题 → 重新提交阶段二评审 → 通过？进入主控确认

**测试修复循环**：
- 阶段二测试执行失败（TEST_CODE_ERROR）→ 测试Agent修复测试代码 → 重新执行阶段二测试
- 阶段二测试执行失败（FUNCTIONAL_BUG）→ 打回开发Agent修复 → 重新进入测试Agent（从阶段二继续）

## 实现计划编写规则

架构 Agent 生成实现计划时，计划文档必须包含以下内容：

**必含章节：**
1. **目标**：简述要实现什么
2. **架构概述**：模块划分、模块职责、模块依赖关系
3. **接口设计**：关键模块的 API/函数签名（可用伪代码）
4. **数据流**：核心数据从输入到输出的处理路径
5. **设计模式**：采用的模式及理由（如有）
6. **Task 分解**：按实现顺序分解为若干 Task，每个 Task 包含：
   - **Files**：涉及的文件（Create/Edit/Delete）
   - **Steps**：具体步骤
7. **Spec 覆盖检查**：表格列出每条 SPEC 需求及对应实现 Task

**原则：**
- 计划文档是架构审查的唯一依据，必须完整
- 架构审查只审查计划文档，不审查代码
- 计划应足够详细，使架构审查能发现设计问题

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

| 视角 | 检查内容 |
|------|---------|
| **SPEC** | SPEC 是否完全执行 Creative Brief 的创意 |
| **架构** | 设计模式、模块边界、性能考虑、可扩展性 |
| **实现完整性** | 实现是否完整覆盖 SPEC 需求（不多不少），验收标准是否满足 |
| **测试用例覆盖率** | 测试用例是否覆盖 SPEC 中的每一条验收标准，逻辑测试和非逻辑测试是否区分清晰 |
| **代码质量** | 代码风格、可维护性、测试覆盖（基于 SPEC）、SOLID 原则 |
| **安全** | 注入漏洞、依赖安全、敏感信息泄露、权限控制 |
