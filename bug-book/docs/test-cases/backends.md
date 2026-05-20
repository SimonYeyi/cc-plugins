# 后端单元测试 - test_backends.py

本文档覆盖 `tests/test_backends.py` 中所有测试用例。文档和测试代码一一对应，TC-XX 编号在两侧保持一致。

**测试文件**: `tests/test_backends.py`
**测试对象**: JSONLBackend（通过 `backend_factory.create_backend()` 创建）
**总用例数**: **68 个测试函数**

---

## 用例统计

| 分类 | 用例数 | 编号区间 |
|------|--------|----------|
| add_bug 新增记录 | 8 | TC-A01 ~ TC-A08 |
| update_bug 更新记录 | 6 | TC-B01 ~ TC-B06 |
| delete_bug 删除记录 | 3 | TC-C01 ~ TC-C03 |
| increment_score 分数累加 | 3 | TC-D01 ~ TC-D03 |
| update_bug_paths / add_module_pattern | 3 | TC-E01 ~ TC-E03 |
| search_by_keyword 关键词搜索 | 5 | TC-F01 ~ TC-F05 |
| recall_by_path / search_by_module_patterns 路径和模块搜索 | 6 | TC-H01 ~ TC-H06 |
| 高级搜索 | 5 | TC-S01 ~ TC-S05 |
| get_bug_detail 详情查询 | 4 | TC-I01 ~ TC-I04 |
| list_bugs 列表查询 | 4 | TC-J01 ~ TC-J04 |
| mark_invalid 失效标记 | 3 | TC-K01 ~ TC-K03 |
| 懒初始化与集成 | 3 | TC-L01 ~ TC-L03 |
| 影响关系管理 | 6 | TC-M01 ~ TC-M05, P04 |
| 路径和 module_patterns 管理 | 4 | TC-N01 ~ TC-N04 |
| 路径迁移 | 2 | TC-O01 ~ TC-O02 |
| 路径检查 | 3 | TC-P01 ~ TC-P03 |
| **总计** | **68** | |

---

## TC-A01 ~ TC-A08：add_bug 新增记录

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-A01 | 新增最小字段 | `title="测试", phenomenon="现象", verified=True` | 返回 `(id>0, score=0)` |
| TC-A02 | 新增完整字段 | 所有字段含7维分数 | id>0, scores=7维 |
| TC-A03 | 新增含中文 | 中文 title/phenomenon | 中文正确存储 |
| TC-A04 | 新增 verified=False | verified=False | verified=0, status=active |
| TC-A05 | 新增空 scores | scores={} | score=0 |
| TC-A06 | 新增多条 paths | paths=["a.ts", "b.ts"] | len(paths)=2 |
| TC-A07 | 新增多条 module_patterns | module_patterns=["auth/*", "src/*"] | len(module_patterns)=2 |
| TC-A08 | 新增后立即查询 | add 后 get_bug_detail | 返回完整记录 |

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

## TC-C01 ~ TC-C03：delete_bug 删除记录（软删除）

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-C01 | 删除存在记录 | delete_bug(id) | status='invalid'，数据仍存在 |
| TC-C02 | 删除不存在 | delete_bug(9999) | 静默返回 |
| TC-C03 | 删除后 cascade | delete 后搜索 | 软删除后仍可搜索（status='invalid'） |

> **注意**：`delete_bug` 是软删除，不会真正删除数据。数据仍可通过 `get_bug_detail` 查询到（status='invalid'）。

---

## TC-D01 ~ TC-D03：increment_score 分数累加

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-D01 | 累加已存在维度 | occurrences +1.0 | occurrences=1.0 |
| TC-D02 | 累加新维度 | 新维度 new_dim +5.0 | new_dim=5.0 |
| TC-D03 | 连续累加 | 累加 3 次 | occurrences=3.0 |

---

## TC-E01 ~ TC-E03：update_bug_paths / add_module_pattern

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-E01 | 批量更新 paths | update_bug_paths(id, ["new/a.ts"]) | 替换旧 paths |
| TC-E02 | 清空 paths | update_bug_paths(id, []) | paths=[] |
| TC-E03 | 添加 module_pattern | add_module_pattern(id, "auth/*") | module_patterns 包含 auth/* |

---

## TC-F01 ~ TC-F05：search_by_keyword 关键词搜索

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-F01 | 匹配 title | 搜索唯一标题关键词 | 能搜到 |
| TC-F02 | 匹配 phenomenon | 搜索 phenomenon 关键词 | 能搜到 |
| TC-F03 | 匹配 tag | 搜索 tag 关键词 | 能搜到 |
| TC-F04 | 匹配 keyword | 搜索 keyword | 能搜到 |
| TC-F05 | 无结果 | 不存在的关键词 | 返回 [] |

---

## TC-H01 ~ TC-H06：recall_by_path / search_by_module_patterns 路径和模块搜索

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-H01 | 精确路径搜索 | recall_by_path("src/a.ts") | 搜索相关 bug |
| TC-H02 | 目录前缀搜索 | paths=["src/auth/s.ts"] 查 "src/auth/s.ts" | 搜索 |
| TC-H03 | 不相关不搜索 | api 问题不搜索 auth | 无搜索 |
| TC-H04 | search_by_module_patterns 基本匹配 | 模式搜索 src/modules/* | 搜索 |
| TC-H05 | 无 module_patterns 不被召回 | 查询无模式的 bug | 无搜索 |
| TC-H06 | pattern 无匹配 | xyz/* 不匹配 auth/login.ts | 无搜索 |

---

## TC-S01 ~ TC-S05：高级搜索

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-S01 | search_recent | 最近 7 天 | 返回最近创建的 |
| TC-S02 | search_high_score | min_score=30 | score>=30 |
| TC-S03 | search_top_critical | limit=5 | 返回最严重的 |
| TC-S04 | search_recent_unverified | verified=False | 只返回未验证 |
| TC-S05 | search_by_status_and_score | status + min/max score | 组合过滤 |

---

## TC-I01 ~ TC-I04：get_bug_detail 详情查询

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-I01 | 查询存在的 bug | get_bug_detail(id) | 返回完整记录 |
| TC-I02 | 查询不存在的 bug | get_bug_detail(9999) | 抛出 ValidationError |
| TC-I03 | 详情包含 7 维分数 | 带 scores 创建 | len(scores)=7 |
| TC-I04 | 详情包含关联数据 | tags/keywords/module_patterns | 各字段完整 |

---

## TC-J01 ~ TC-J04：list_bugs 列表查询

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-J01 | 按 status 过滤 | status="active" | 只返回 active |
| TC-J02 | order_by score | score 排序 | 按分数降序 |
| TC-J03 | order_by 白名单 | 非白名单字段 | 自动降级为 score |
| TC-J04 | 分页 | limit=2, offset=0 | 最多 2 条 |

---

## TC-K01 ~ TC-K03：mark_invalid 失效标记

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-K01 | 带原因标记失效 | mark_invalid(id, "功能已删除") | status=invalid, solution 含原因 |
| TC-K02 | 不带原因 | mark_invalid(id) | status=invalid |
| TC-K03 | 标记不存在 | mark_invalid(9999) | 静默返回 |

---

## TC-L01 ~ TC-L03：懒初始化与集成

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-L01 | 文件不存在自动创建 | 删除文件后 add | 文件自动创建 |
| TC-L02 | 完整 CRUD | add→update→get→delete | 全流程正常 |
| TC-L03 | 复发流程 | verified=False → increment | verified=0, occurrences=1 |

---

## TC-M01 ~ TC-M05：影响关系管理

| 用例编号   | 测试点描述 | 输入 | 预期 |
|--------|-----------|------|------|
| TC-M01 | 添加回归影响 | add_impact(..., impact_type="regression") | impact_id>0 |
| TC-M02 | 添加副作用 | impact_type="side_effect" | impact_id>0 |
| TC-M03 | 添加依赖 | impact_type="dependency" | impact_id>0 |
| TC-M04 | 无效类型 | impact_type="invalid" | 抛出 ValidationError |
| TC-M05 | 无效 severity | severity=15 | 抛出 ValidationError |
| TC-M06 | prevention 自动累加 | add_impact(prevention_delta=5) | prevention+=5 |

> **注意**：`add_impact` 参数为 `(source_bug_id, solution_change, impact_description, impact_type, severity, prevention_delta)`

---

## TC-N01 ~ TC-N04：路径和 module_patterns 管理

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-N01 | 批量更新 paths | update_bug_paths | paths 替换 |
| TC-N02 | 添加 module_pattern | add_module_pattern | module_patterns 增加 |
| TC-N03 | 批量更新 module_patterns | update_bug_module_patterns | module_patterns 替换 |
| TC-N04 | 清空 module_patterns | update_bug_module_patterns([]) | module_patterns=[] |

---

## TC-O01 ~ TC-O02：路径迁移

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-O01 | 迁移 paths | migrate_bug_paths_after_refactor | 返回迁移的 bug_id 列表 |
| TC-O02 | 迁移 module_patterns | migrate_bug_paths_after_refactor(通配符) | module_patterns 模式更新 |

> **注意**：`migrate_bug_paths_after_refactor` 返回 `list[int]`，是被迁移的 bug_id 列表。

---

## TC-P01 ~ TC-P03：路径检查

| 用例编号 | 测试点描述 | 输入 | 预期 |
|---------|-----------|------|------|
| TC-P01 | paths 有效 | check_bug_paths(id) | 返回 [] |
| TC-P02 | paths 无效 | paths=["不存在.ts"] | 返回无效路径列表 |
| TC-P03 | module_patterns 无效 | module_patterns=["不存在/*"] | 返回无效路径列表 |



## 执行指南

```bash
cd D:/yeyi/AI/cc-plugins/bug-book
python -m pytest tests/test_backends.py -v
```

---

## 相关文档

- [MCP Server E2E 测试](./mcp-server-e2e.md) - `tests/test_mcp_server_e2e.py`