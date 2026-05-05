# CLAUDE.md - bug-book

## 概念

bug-book（错题集）让 AI 在开发过程中记住历史问题，避免重复犯错。

## 核心机制

- **记录**：AI 感知问题后记录到 SQLite，小问题自动验证，复杂问题后台记录待审核
- **召回**：改代码前查询相关 bug，主动预防
- **整理**：归类、去重、清理失效条目、按重要性排序
- **搜索**：关键词快速定位

## 数据库

SQLite，位于项目根目录 `bug-book.db`。首次记录时自动初始化。

## 评分体系

详见 [SPEC.md](SPEC.md)。

## 组件

| 类型 | 文件 |
|------|------|
| Skill | skills/bug-record/SKILL.md |
| Skill | skills/bug-search/SKILL.md |
| Skill | skills/bug-organize/SKILL.md |
| 规则 | rules/bug-book.md |
| 脚本 | scripts/init_db.py |
| 脚本 | scripts/bug_ops.py |
| 共享 | scripts/config.py |

## 开发规范

修改 `scripts/*.py` 后，必须按以下顺序：

1. **先**：在 `docs/test-cases/database-ops/logic.md` 中添加测试用例（TC-XX 分类编号，如 TC-A01）
2. **再**：在 `tests/test_bug_ops.py` 中实现对应测试代码，编号格式与文档一致
3. **最后**：运行测试确保通过：`python -m pytest tests/test_bug_ops.py -v`

文档和代码必须一一对应，每个用例编号在两侧保持一致（TC-A01 ~ TC-L03，共 67 个用例）。

## 相关文档

- [SPEC.md](SPEC.md) — 完整需求规格
- [README.md](README.md) — 使用说明
