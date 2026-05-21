# 后端单元测试 - test_bug_backend.py

本文档覆盖 `tests/test_bug_backend.py` 中所有测试用例。文档和测试代码一一对应，TC-XX 编号在两侧保持一致。

**测试文件**: `tests/test_bug_backend.py`
**测试对象**: BugBackend（JSONLBackend 实现，通过 `backend_factory.create_backend()` 创建）

## 架构说明

后端层（BugBackend）提供**原子操作方法**，供 BugService 业务编排层调用：
1. `add_bug()` / `update_bug()` / `get_bug()` / `get_all_bugs()` - 基础 CRUD
2. `add_impact()` / `delete_impact()` - 影响关系管理
3. `find_by_keyword()` / `find_by_tag()` / `find_by_created_after()` / `find_by_min_score()` / `find_all_sorted()` / `find_by_created_after_unverified()` / `query()` / `find_by_pattern()` - 查询原语
4. `find_by_path()` - 路径召回
5. `count_bugs()` / `find_unverified_old()` / `compact_file()` - 辅助方法

**总用例数**: **34 个测试函数**

---

## 用例统计

| 分类 | 用例数 | 编号区间                    |
|------|--------|-------------------------|
| add_bug 新增记录 | 8 | TC-A01 ~ TC-A08         |
| update_bug 更新记录 | 6 | TC-B01 ~ TC-B06         |
| 软删除 | 2 | TC-C01 ~ TC-C02         |
| 影响关系管理 | 3 | TC-D01 ~ TC-D03         |
| 查询原语 | 7 | TC-E01 ~ TC-E07         |
| 路径召回 | 3 | TC-F01 ~ TC-F03         |
| 辅助方法 | 3 | TC-G01 ~ TC-G03 |
| 路径迁移/列表 | 2 | TC-H01 ~ TC-H02         |
| **总计** | **34** |                         |

---

## TC-A01 ~ TC-A08：add_bug 新增记录

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-A01 | 新增最小字段 | `title="测试", phenomenon="现象", verified=True` | 返回 `(id>0, score=0)` |
| TC-A02 | 新增完整字段 | 所有字段含7维分数 | id>0, scores=7维 |
| TC-A03 | 新增含中文 | 中文 title/phenomenon/root_cause/solution | 中文正确存储 |
| TC-A04 | 新增 verified=False | verified=False | verified=0, status=active |
| TC-A05 | 新增空 scores | scores={} | score=0 |
| TC-A06 | 新增多条 paths | paths=["a.ts", "b.ts"] | len(paths)=2 |
| TC-A07 | 新增多条 module_patterns | module_patterns=["auth/*", "src/*"] | len(module_patterns)=2 |
| TC-A08 | 新增后立即查询 | add 后 get_bug | 返回完整记录 |

---

## TC-B01 ~ TC-B06：update_bug 更新记录

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-B01 | 更新单字段 | `update_bug(id, title="新标题")` | title 更新 |
| TC-B02 | 同时更新多字段 | title + root_cause | 全部更新 |
| TC-B03 | 更新 verified 相关 | verified=True, verified_by="User" | verified=1, status=resolved |
| TC-B04 | 更新 status | status="resolved" | status=resolved |
| TC-B05 | 更新不存在的 bug | update_bug(9999, ...) | 静默返回 |
| TC-B06 | 不传任何字段 | update_bug(id) | 无修改 |

---

## TC-C01 ~ TC-C02：软删除

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-C01 | 通过 update 软删除 | update_bug(id, status="invalid") | status='invalid' |
| TC-C02 | 软删除后仍可查询 | 更新为 invalid 后 get_bug | 数据仍存在 |

---

## TC-D01 ~ TC-D03：影响关系管理

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-D01 | 添加回归影响 | add_impact(..., impact_type="regression", severity=8) | impact_id>0 |
| TC-D02 | 添加副作用影响 | impact_type="side_effect" | impact_id>0 |
| TC-D03 | 无效影响类型 | impact_type="invalid" | 抛出异常 |

---

## TC-E01 ~ TC-E07：查询原语

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-E01 | 关键词查询 | find_by_keyword("XYZ123", limit=10) | 返回匹配的 bugs |
| TC-E02 | 关键词查询无结果 | find_by_keyword("不存在", limit=10) | 返回 [] |
| TC-E03 | 最近创建查询 | find_by_created_after(days=7, limit=10) | 返回最近创建的 |
| TC-E04 | 高分查询 | find_by_min_score(min_score=30, limit=10) | score>=30 |
| TC-E05 | 最严重查询 | find_all_sorted(limit=10) | 返回最严重的 |
| TC-E06 | 模块模式查询 | find_by_pattern("src/modules/*") | 模式匹配 |
| TC-E07 | 模块模式无匹配 | find_by_pattern("xyz/*") | 返回 [] |

---

## TC-F01 ~ TC-F03：路径召回

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-F01 | 精确路径召回 | find_by_path("src/auth/session.ts") | 召回匹配的 bug |
| TC-F02 | 不相关路径不召回 | 存储 api 问题，查询 auth | 无召回 |
| TC-F03 | 召回结果含 impacts | 存储 impacts 后召回 | 结果包含 impacts 字段 |

---

## TC-G01 ~ TC-G03：辅助方法

| 用例编号   | 测试点描述 | 输入 | 预期 |
|--------|-----------|------|------|
| TC-G01 | 获取所有 bugs | get_all_bugs() | 返回 dict[id->bug] |
| TC-G02 | 统计 bug 总数 | count_bugs() | 返回 >=1 的整数 |
| TC-G03 | 压缩文件 | compact_file() | 返回清理数量 |

---

## TC-H01 ~ TC-H02：路径迁移/列表

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-H01 | 路径迁移召回 | find_by_path 传入迁移路径 | 召回迁移后的 bug |
| TC-H02 | 列出长期未验证 | find_unverified_old(days=30, limit=10) | 返回未验证列表 |

---

## 执行指南

```bash
cd D:/yeyi/AI/cc-plugins/bug-book
python -m pytest tests/test_bug_backend.py -v
```

---