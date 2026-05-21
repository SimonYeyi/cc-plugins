# BugService 单元测试 - test_bug_service.py

本文档覆盖 `tests/test_bug_service.py` 中所有测试用例。文档和测试代码一一对应，TC-XX 编号在两侧保持一致。

**测试文件**: `tests/test_bug_service.py`
**测试对象**: BugService（业务编排层，通过 `mcp_server.py` 调用）

## 架构说明

BugService 是**业务编排层**，提供 6 个公共接口供 MCP Server 调用：
1. `save_bugs()` - 统一保存（18 种 mode）
2. `search_bugs()` - 统一搜索（8 种 mode）
3. `get_bug_detail()` - 获取详情
4. `recall_by_path()` - 路径召回
5. `migrate_bug_paths_after_refactor()` - 路径迁移
6. `organize_bugs()` - 整理 bug-book

**总用例数**: **30 个测试函数**

---

## 用例统计

| 分类 | 用例数 | 编号区间 |
|------|--------|----------|
| save_bugs add 模式 | 4 | TC-S01 ~ TC-S04 |
| save_bugs update_fields 模式 | 3 | TC-U01 ~ TC-U03 |
| save_bugs delete 模式 | 2 | TC-D01 ~ TC-D02 |
| save_bugs add_paths 模式 | 2 | TC-P01 ~ TC-P02 |
| save_bugs increment_scores 模式 | 1 | TC-INC01 |
| save_bugs add_impacts 模式 | 1 | TC-IMP01 |
| search_bugs 接口 | 6 | TC-SE01 ~ TC-SE06 |
| get_bug_detail 接口 | 3 | TC-G01 ~ TC-G03 |
| recall_by_path 接口 | 3 | TC-R01 ~ TC-R03 |
| migrate_bug_paths_after_refactor 接口 | 3 | TC-M01 ~ TC-M03 |
| organize_bugs 接口 | 1 | TC-O01 |
| 完整 CRUD 流程 | 1 | TC-CRUD01 |
| **总计** | **30** | |

---

## TC-S01 ~ TC-S04：save_bugs - add 模式

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-S01 | 新增最小字段 | `{mode: "add", title, phenomenon}` | 返回 `{results: [{id: >0}], count: 1}` |
| TC-S02 | 新增完整字段 | 包含 scores/paths/tags/keywords/module_patterns | 全部正确存储，status=resolved |
| TC-S03 | 新增含中文 | title/phenomenon 含中文 | 中文正确存储 |
| TC-S04 | 批量新增 | `[{mode: "add"...}, {mode: "add"...}]` | 返回多个结果 |

---

## TC-U01 ~ TC-U03：save_bugs - update_fields 模式

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-U01 | 更新单字段 | `{mode: "update_fields", id, title}` | title 更新，其他字段不变 |
| TC-U02 | 更新多字段 | `{mode: "update_fields", id, title, root_cause}` | 全部更新 |
| TC-U03 | 更新 verified 字段 | `verified=True, verified_by="User"` | verified=1, status=resolved |

---

## TC-D01 ~ TC-D02：save_bugs - delete 模式

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-D01 | 删除存在的记录 | `{mode: "delete", id}` | status='invalid' |
| TC-D02 | 删除不存在的 id | `{mode: "delete", id: 9999}` | 抛出异常 |

---

## TC-P01 ~ TC-P02：save_bugs - add_paths 模式

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-P01 | 添加路径 | `{mode: "add_paths", id, paths: [{file: "a.ts", functions: ["f1"]}]}` | paths 增加 |
| TC-P02 | 合并函数 | 同 file 不同 functions | functions 去重合并 |

---

## TC-INC01：save_bugs - increment_scores 模式

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-INC01 | 累加分数 | 累加 3 次 occurrences=1.0 | occurrences=3.0 |

---

## TC-IMP01：save_bugs - add_impacts 模式

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-IMP01 | 添加影响 | `{mode: "add_impacts", id, impacts: [...]}` | impacts 数组增加一项 |

---

## TC-SE01 ~ TC-SE06：search_bugs 接口

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-SE01 | keyword 模式 | `mode='keyword', keyword='XYZ123'` | 返回匹配的 bugs |
| TC-SE02 | recent 模式 | `mode='recent', days=7` | 返回最近创建的 |
| TC-SE03 | high_score 模式 | `mode='high_score', min_score=30` | score>=30 |
| TC-SE04 | critical 模式 | `mode='critical', limit=5` | 最多 5 条 |
| TC-SE05 | custom 模式 | `mode='custom', status='resolved', min_score=30` | 按条件过滤 |
| TC-SE06 | 无结果 | `mode='keyword', keyword='不存在的关键词'` | total=0 |

---

## TC-G01 ~ TC-G03：get_bug_detail 接口

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-G01 | 查询存在的 bug | bug_id 有效 | 返回完整记录 |
| TC-G02 | 查询不存在的 bug | bug_id=9999 | 抛出异常 |
| TC-G03 | 完整字段 | 创建时带所有字段 | 各字段正确返回 |

---

## TC-R01 ~ TC-R03：recall_by_path 接口

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-R01 | 精确路径召回 | `recall_by_path("src/auth/session.ts")` | 召回匹配的 bug |
| TC-R02 | 不相关路径不召回 | 查询 auth，存储 api | 无召回 |
| TC-R03 | 返回含 impacts | 存储 impacts 后召回 | 结果包含 impacts 字段 |

---

## TC-M01 ~ TC-M03：migrate_bug_paths_after_refactor 接口

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-M01 | 精确路径迁移 | old_path → new_path | 返回迁移的 bug_id 列表 |
| TC-M02 | 无匹配 | old_path 不存在 | 返回 [] |
| TC-M03 | module_pattern 迁移 | 触发 module_pattern 匹配 | module_patterns 同步更新 |

---

## TC-O01：organize_bugs 接口

| 用例编号 | 测试点描述 | 预期 |
|---------|-----------|------|
| TC-O01 | 返回结构化数据 | 包含 invalid_candidates/unverified_old/statistics/last_organize_time |

---

## TC-CRUD01：完整 CRUD 流程

| 用例编号 | 测试点描述 | 步骤 | 预期 |
|---------|-----------|------|------|
| TC-CRUD01 | 完整 CRUD | add → get → update_fields → get → delete → get | 各步骤正确执行 |

---

## 执行指南

```bash
cd D:/yeyi/AI/cc-plugins/bug-book
python -m pytest tests/test_bug_service.py -v
```

---

## 相关文档

- [BugBackend 单元测试](./bug-backend.md) - `tests/test_bug_backend.py`
- [MCP Server E2E 测试](./mcp-server-e2e.md) - `tests/test_mcp_server_e2e.py`