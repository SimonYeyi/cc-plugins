# CLAUDE.md — super-flow

> @`skills/super-flow/SKILL.md`

## 流程设计

```
入口分支
    │
    ├──→ 创意模式 ──→ 阶段一：创意流程 ────────────────────────┐
    │     （创意Agent + 创意评审团内循环）                     │
    │                    ↺ 内循环                          │
    │                                                      │
    └──→ 产品模式 ──→ 阶段一：澄清用户需求 ─────────────────────┤
                                                           ▼
                                                    阶段二：产品流程
                                              （产品Agent + SPEC评审Agent内循环）
                                                           ↺ 内循环
                                                           │
                                                           ▼
                                                    阶段三：设计流程
                                              （设计Agent + 设计评审Agent内循环）
                                                           ↺ 内循环
                                                           │
                                                           ▼
                                                    阶段四：架构流程
                                              （架构Agent + 计划评审Agent内循环）
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

## Agent Description 规范

**核心要求**：agent 文件的 description 必须与工作流章节完全匹配。

**格式规范**：
- description 使用 `processing xxx` 格式
- 工作流使用 `### 处理xxx` 格式
- 两者内容必须一一对应

**示例**：
```yaml
description: |
  Use this agent when:
  - processing Creative Brief generation
  - processing review feedback/control-decision
  - processing brainstorming problems
  - processing SPEC confirmation request
```

**同步要求**：
- 修改工作流章节时，必须同步更新 description
- 修改 description 时，必须同步更新工作流章节

---

## Product Agent 与 Design Agent 职责边界

**核心原则**：SPEC (Product) = What（功能） | Design = How（交互/UI）

- **Product Agent**：定义功能需求、业务逻辑、验收标准，提供UX示意但非最终方案
- **Design Agent**：拥有交互和UI的最终决定权，可调整Product的UX建议

**示例**：
```markdown
✅ Product应该写："游戏结束时显示胜利界面，包含得分和重新开始按钮"
❌ Product不应该写："胜利界面使用#4CAF50绿色背景，按钮圆角8px"

✅ Design应该做：决定胜利界面的布局、颜色、动画效果
```

---

## 业务Agent与Reviewer同步修改原则

**核心规则**：修改业务Agent时，必须同步更新对应的评审Agent

**对应关系**：Product↔SPEC Reviewer, Design↔Design Reviewer, Architecture↔Plan Reviewer, Developer↔Implementation Reviewer, Tester↔Test Reviewer, Creative↔Creative Reviewer

**检查要点**：
1. **工作流变更** → 评审流程相应调整
2. **输出格式变更** → 评审检查清单更新
3. **职责边界变更** → 评审责任边界对齐
4. **质量标准变更** → 评审通过标准匹配
5. **依赖关系变更** → 评审前置条件更新

**示例**：
```markdown
Tester Agent增加"强制自动执行测试"要求
→ Test Reviewer必须同步增加"验证测试已实际执行"的检查项
```

---

## 测试Agent职责专属原则

**核心规则**：测试相关工作（框架集成、代码编写、执行验证）全部由Tester Agent负责，Architecture和Developer不涉及任何测试工作。

**示例**：
```markdown
✅ Architecture应该写："前端框架：React 18 + TypeScript"
❌ Architecture不应该写："测试框架：Jest"

✅ Developer应该做：实现UserService.create_user()方法
❌ Developer不应该做：编写test_create_user()测试代码

✅ Tester应该做：选择pytest框架 → 编写测试代码 → 执行测试 → 生成报告
```