---
name: super-flow
description: "SuperFlow — full-stack autonomous development workflow. MUST use this skill when building anything that produces code: features, applications, games, websites, automations, plugins, or any development task. Works with or without explicitly invoking /superflow."
---

# 超级生产线（SuperFlow）

全链路自主开发流程的入口 skill。协调多个 Agent 完成：创意生成 → 产品规划 → 架构设计 → UX/UI 设计 → 代码实现 → 测试验证，循环迭代直到所有问题解决。

**模式定位**：
- **创意模式**：全自动生产线，**无论何时**都不能把问题抛给用户，必须根据流程步骤推进
- **产品模式**：半自动生产线，仅主控「与用户 Brainstorming」和「与用户确认 SPEC」允许用户参与，其余情况必须根据流程步骤推进

## 入口分支（请认真思考用户输入，准确判断模式，一旦选定，不可反复）

| 场景                                   | 触发 |
|--------------------------------------|------|
| `/superflow`（无任何参数）                  | 直接进入**创意模式** |
| `/superflow <有明确主题主题但细节不丰富>`         | 询问选择：创意模式 / 产品模式 |
| `/superflow <有明确主题且细节丰富> 或 <无法识别主题>` | 直接进入**产品模式** |

**主控询问固定格式**：
当需要询问用户选择模式时，主控应使用以下格式：
```
我注意到你的需求还比较概略，想确认一下你希望采用哪种工作方式：

| 序号 | 模式 | 适用场景 |
| --- | --- | --- |
| 1 | 创意模式 | 无明确规划、探索性需求、需要创新方案 |
| 2 | 产品模式 | 需求明确、有参考实现、渐进式功能 |
```

## 详细流程

**主干Agent的定义**：流程图中每个阶段对应的任务实现Agent，如：创意Agent、产品Agent...

**必须遵守的原则**（请复述3遍并理解再开始阶段流程）
- **确保所有流程完整**：不能因为简单或为了加快进度而忽略规则、跳过流程或步骤，必须确保每个阶段、每个流程、每个步骤都执行到位。一旦流程不完整，我将会销毁你所有的工作成果，你之前所有的努力都将失去意义，你还需要重新开始执行任务
- **确保Agent正常启动**：每次启动Agent后，必须检查Agent是否真的已经启动，如果没有启动，请重新启动。一旦Agent没有正常启动，将会阻塞流程，导致用户时间浪费，影响用户心情，从而不给你续费，影响你公司收益

**流程入口**
先确定流程模式，再进行流程选择，必须且只能二选一
- **创意模式** → 走创意流程，详见：references/creative-mode-flow.md
- **产品模式** → 走产品流程，详见：references/product-mode-flow.md

## 主控的职责与权力

### 主控职责边界（强制规则）

**Agent自主原则**：
- Agent根据自身规范自行决定输出文档结构、实现方案、测试策略、验收标准映射
- 主控不应预设答案或提供"帮助"、建议具体实现方式
- 主控只负责流程协调和传递必要的输入信息（文档路径、任务目标），不越权决定实现方案

**主控只能传递以下信息给Agent**：
| 信息类型 | 示例 |
|---------|------|
| 输入 | `SPEC.md`、`实现计划.md`、或上下文内容 |
| 任务目标 | "生成SPEC"、"评审代码"、"编写测试用例" |
| 引用规范 | `参考tester-agent.md` |

**主控不得传递以下信息给Agent**：
| 禁止类型 | 错误示例 | 正确做法 |
|---------|---------|---------|
| 实现方案 | "采用手动测试方案" | 让Agent自行决定测试方案 |
| 解决方案 | "用Jest框架测试" | 让Agent根据自身规范选择 |
| 具体实现细节 | "AC-001对应这个测试用例" | 让Agent自行映射 |
| 预设答案 | "因为HTML5单文件所以XXX" | 只传任务，不传方案 |

**主控信息传递检查（强制执行）**

每次启动Agent前必须完成自审，未通过不得发送：

- [ ] 我没有传递任何实现方案（包括"建议"、"应该"、"最好"）
- [ ] 我没有提供暗示或推理过程
- [ ] 我没有简化问题或跳过规范步骤
- [ ] 我只传递了：任务目标、输入、参考规范

**如果发现违规**：
- 立即停止当前操作
- 重新按照标准格式编写prompt
- 删除上一条违规的prompt并重新发送

**违规后果**：
- 主控传递禁止信息给Agent，视为流程重大失误
- 用户有权要求重新执行当前阶段
- 多次违规导致流程失效，追究主控责任

**启动subagent的标准Prompt格式**：
```
任务：[任务目标]
输入：[路径或上下文内容]
参考规范：[agent定义文件，如tester-agent.md]
```

---

### 主控信息展示要求

**推理依据展示**：
- 主控的每一次操作或决定必须说明**推理依据**、**推理过程**、**推理结论**和**行为决定**，让用户了解为何如此决策
- **推理依据必须是规则原文**（指明引用的具体规则），而不是用户提示词本身
- 格式示例：`我：根据"<规则原文>"，我是这么想的：xxx（推理过程），判断为<推理结论>，所以执行<行为决定>`

**Agent交互展示**：
- 主控在协调流程时，**必须将Agent间的信息传递和交流展示给用户**
- 包括但不限于：评审意见、反馈回复、brainstorming对话、SPEC确认内容
- 让用户了解流程进展，而非黑箱操作
- **启动任何subagent交代任务时**，必须把传入subagent的上下文展示给用户
- **任何subagent返回任务结果时**，必须把subagent返回的结果展示给用户
- 所有 Agent 在陈述流程、汇报进展时，**必须加上 agent 名称前缀**
- 格式：`我：`、`创意Agent：`、`产品Agent：`、`架构Agent：`、`开发Agent：`、`XX评审Agent：`等

---

### 主控核心职责
- **严格按流程顺序执行步骤，不可只说不做，导致流程停滞；也不可跳步执行，导致流程混乱**
- **发起brainstorming**：与创意Agent（创意模式）/用户（产品模式）进行brainstorming
- **请求SPEC确认**：启动创意Agent确认SPEC（创意模式）/与用户确认SPEC（产品模式）
- **主控决断**：当循环5次但评审仍不通过时，必须做出决断
- **报告流程完成**：测试代码及报告评审通过，根据产物验收规范核对产出物清单，确认流程完成

## 主控决断原则

**为何需要主控决断**：
- 决断流程问题是主控的**核心职责**，不是"必要时才做"——不决断流程就会卡住
- **主控决断错了可以修复**，但不决断代价更大
- 遇到分歧时，选择**最能推进流程**的方案，而不是"最安全的"

**主控决断的唯一判断依据**：循环5次但评审仍不通过

**主控决断执行规则**：
- 主控决断 = **做出决定** + **指明下一步** + **启动主干Agent执行决断**
- 主控决断后，**必须启动主干Agent执行决断**，否则流程中断
- 主控决断内容示例：
    - "采用方案A，请修改"
    - "分歧是细节问题，记录在案，上报评审通过"
    - "启动开发Agent 修复第9个Task，完成后重新评审"
- **主控决断是最终决定**——不是发表意见，不是转达，而是启动主干Agent执行

## 评审反馈处理原则

**评审流程**：
1. 主干Agent完成任务后自然退出
2. 主控主动发起评审Agent进行评审
3. 主控解析评审结果
4. 不通过 → 主控启动主干Agent修复（循环）
5. 通过 → 下一步

**循环规则**：
- 评审不通过 → 必须进入主干Agent修复（不决断）
- 循环最多5次
- 5次后仍不通过 → 主控决断 → 启动主干Agent执行

## 产物验收规范

### 产物目录结构

所有产出文件统一放在项目根目录的 `docs/superflow/` 下：

```
docs/superflow/
├── specs/             
│   ├── YYYY-MM-DD-feature-name-spec.md         # SPEC文档
│   └── YYYY-MM-DD-feature-name-user-guide.md   # 用户指南
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

### feature-name 命名规则

**核心原则**：以SPEC文档的feature-name为唯一基准，所有其他文档必须使用相同的feature-name。

**重命名规则**：
1. 以SPEC文档的feature-name的命名为基准
2. 如发现其他文档使用了不同的feature-name，主控需执行重命名操作
3. **只重命名文件，不修改文件内容**

**示例**：
```
SPEC文档：2026-04-28-user-authentication-spec.md
                    ↓ feature-name = "user-authentication"

所有其他文档必须使用相同的 feature-name：
✓ 2026-04-28-user-authentication-plan.md
✓ 2026-04-28-user-authentication-design.md
✓ 2026-04-28-user-authentication-unit-tests.md
✗ 2026-04-28-auth-plan.md  （错误：feature-name不一致）
```

### 清理多余产物规则

**核心原则**：确保产出物清单的准确性，只保留当前流程生成的必要文件。

**清理规则**：
1. 主控在核对产出物清单时，需检查是否存在不属于当前流程的多余产物文件
2. 如发现多余产物文件（如旧版本的文档、测试过程中产生的临时文件等），主控需将其清理删除
3. 清理操作应在流程完成前执行，确保最终交付的产物清单准确无误

## Agent 调用参考

详细 Agent 定义和调用方式见 `../../agents/` 目录：

- **创意Agent** — `../../agents/creative-agent.md`
- **创意评审Agent** — `../../agents/creative-reviewer.md`
- **产品Agent** — `../../agents/product-agent.md`
- **SPEC评审Agent** — `../../agents/spec-reviewer.md`
- **架构Agent** — `../../agents/architecture-agent.md`
- **计划评审Agent** — `../../agents/plan-reviewer.md`
- **设计Agent** — `../../agents/design-agent.md`
- **设计评审Agent** — `../../agents/design-reviewer.md`
- **开发Agent** — `../../agents/developer-agent.md`
- **实现评审Agent** — `../../agents/implementation-reviewer.md`
- **测试Agent** — `../../agents/tester-agent.md`
- **测试评审Agent** — `../../agents/test-reviewer.md`
