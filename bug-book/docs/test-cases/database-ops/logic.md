# 逻辑测试用例 - bug_ops 数据库操作

本文档覆盖 `scripts/bug_ops.py` 中所有数据库操作函数。文档和 `tests/test_bug_ops.py` 一一对应，TC-XX 编号在两侧保持一致。

## 用例统计

| 分类 | 用例数 | 编号区间 |
|------|--------|----------|
| add_bug 新增记录 | 8 | TC-A01 ~ TC-A08 |
| update_bug 更新记录 | 6 | TC-B01 ~ TC-B06 |
| delete_bug 删除记录 | 3 | TC-C01 ~ TC-C03 |
| increment_score 分数累加 | 3 | TC-D01 ~ TC-D03 |
| add_path / add_recall | 3 | TC-E01 ~ TC-E03 |
| search_by_keyword 关键词搜索 | 7 | TC-F01 ~ TC-F07 |
| _match_path 路径匹配 | 15 | TC-G01 ~ TC-G15 |
| recall_by_path / recall_by_pattern 路径召回 | 7 | TC-H01 ~ TC-H07 |
| get_bug_detail 详情查询 | 5 | TC-I01 ~ TC-I05 |
| list_bugs 列表查询 | 4 | TC-J01 ~ TC-J04 |
| mark_invalid 失效标记 | 3 | TC-K01 ~ TC-K03 |
| 懒初始化与集成 | 3 | TC-L01 ~ TC-L03 |
| **总计** | **67** | |

---

## TC-A01 ~ TC-A08：add_bug 新增记录

| 用例编号 | 测试点描述 | 输入 | 预期输出 | 测试类型 |
|---------|-----------|------|---------|---------|
| TC-A01 | 新增最小字段记录 | `title="测试", phenomenon="现象", verified=True` | 返回 `(id=1, score=0)`，数据库有1条记录 | 正常流程 |
| TC-A02 | 新增完整字段记录 | 所有字段完整填写，含7维度评分、paths、tags、keywords、recalls | 返回正确 id 和分数，detail 查询各字段完整 | 正常流程 |
| TC-A03 | 新增记录含中文标题和描述 | 中文 title/phenomenon/root_cause/solution | 中文正确存储和返回 | 正常流程 |
| TC-A04 | 新增记录 verified=False | `verified=False` | verified=0，分数正常计算 | 正常流程 |
| TC-A05 | 新增空 scores dict | `scores={}` | 不插入 bug_scores，分数为 0 | 边界条件 |
| TC-A06 | 新增多条 paths | `paths=["a/b.py", "c/d.py"]` | 两条路径都正确插入 | 正常流程 |
| TC-A07 | 新增多条 recalls | `recalls=["auth/*", "src/*"]` | 两条模式都正确插入 | 正常流程 |
| TC-A08 | 新增记录后立即查询 detail | add 后不关闭连接，直接 get_bug_detail | 返回完整记录 | 正常流程 |

---

## TC-B01 ~ TC-B06：update_bug 更新记录

| 用例编号 | 测试点描述 | 输入 | 预期输出 | 测试类型 |
|---------|-----------|------|---------|---------|
| TC-B01 | 更新单字段 title | `update_bug(id, title="新标题")` | title 更新，其他字段不变 | 正常流程 |
| TC-B02 | 同时更新多字段 | 同时更新 title、root_cause、solution | 所有字段同时更新 | 正常流程 |
| TC-B03 | 更新 verified 相关字段 | `verified=True, verified_at="CURRENT_TIMESTAMP", verified_by="User"` | verified=1，verified_at 为当前时间，verified_by="User" | 正常流程 |
| TC-B04 | 更新 status 为 resolved | `status="resolved"` | status 字段正确更新 | 正常流程 |
| TC-B05 | 更新不存在的 bug_id | `update_bug(9999, title="x")` | 无报错，不修改任何数据 | 异常处理 |
| TC-B06 | 不传任何字段（空调用） | `update_bug(id)` | 无修改，不报错 | 边界条件 |

---

## TC-C01 ~ TC-C03：delete_bug 删除记录

| 用例编号 | 测试点描述 | 输入 | 预期输出 | 测试类型 |
|---------|-----------|------|---------|---------|
| TC-C01 | 删除存在的记录 | `delete_bug(id)` | 记录删除，关联的 bug_scores/paths/tags 等 CASCADE 删除 | 正常流程 |
| TC-C02 | 删除不存在的 id | `delete_bug(9999)` | 无报错 | 异常处理 |
| TC-C03 | 删除后关联数据也被删除 | 先 add_bug 含关联数据，再 delete | bug_scores/paths/tags/keywords/recalls 全部删除 | 正常流程 |

---

## TC-D01 ~ TC-D03：increment_score 分数累加

| 用例编号 | 测试点描述 | 输入 | 预期输出 | 测试类型 |
|---------|-----------|------|---------|---------|
| TC-D01 | 累加已存在维度 | `increment_score(id, "occurrences", 1.0)` | occurrences 维度值 +1，总分更新 | 正常流程 |
| TC-D02 | 累加不存在的维度 | 维度从未插入过，第一次累加 | 自动 INSERT 新记录，value=delta | 正常流程 |
| TC-D03 | 连续累加 3 次 | 连续累加3次 | 值 = 3 * delta，updated_at 更新 | 边界条件 |

---

## TC-E01 ~ TC-E03：add_path / add_recall

| 用例编号 | 测试点描述 | 输入 | 预期输出 | 测试类型 |
|---------|-----------|------|---------|---------|
| TC-E01 | 添加路径 | `add_path(id, "src/auth.ts")` | 路径插入 bug_paths 表，updated_at 更新 | 正常流程 |
| TC-E02 | 添加 is_old=True 路径 | `add_path(id, "old/Auth.ts", is_old=True)` | 路径插入且 is_old=1，出现在 old_paths | 正常流程 |
| TC-E03 | 添加 autoRecall 模式 | `add_recall(id, "auth/*")` | 模式插入 bug_recalls 表，updated_at 更新 | 正常流程 |

---

## TC-F01 ~ TC-F07：search_by_keyword 关键词搜索

| 用例编号 | 测试点描述 | 输入 | 预期输出 | 测试类型 |
|---------|-----------|------|---------|---------|
| TC-F01 | 搜索匹配 title | title 包含关键词 | 能搜到 | 正常流程 |
| TC-F02 | 搜索匹配 phenomenon | phenomenon 包含关键词 | 能搜到 | 正常流程 |
| TC-F03 | 搜索匹配 tag | bug_tags 中有匹配 | 能搜到 | 正常流程 |
| TC-F04 | 搜索匹配 keyword | bug_keywords 中有匹配 | 能搜到 | 正常流程 |
| TC-F05 | 搜索无结果 | 不存在的关键词 | 返回空列表 | 正常流程 |
| TC-F06 | 搜索结果按分数排序 | 多条匹配 | 按 score DESC 返回 | 正常流程 |
| TC-F07 | 搜索结果分页 | `limit=2` | 最多返回2条 | 边界条件 |

---

## TC-G01 ~ TC-G15：_match_path 路径匹配

| 用例编号 | 测试点描述 | file_path | pattern | 预期 | 测试类型 |
|---------|-----------|-----------|---------|------|---------|
| TC-G01 | 单段通配符匹配子目录 | `src/auth/session.ts` | `auth/*` | True | 正常流程 |
| TC-G02 | 单段通配符不匹配 | `src/authority/index.ts` | `auth/*` | False | 边界条件 |
| TC-G03 | 多段前缀匹配子路径 | `src/auth/login.ts` | `src/auth/*` | True | 正常流程 |
| TC-G04 | 多段前缀不匹配 | `src/api/user.ts` | `src/auth/*` | False | 边界条件 |
| TC-G05 | 单段精确任意位置 | `src/auth/file.ts` | `auth` | True | 正常流程 |
| TC-G06 | 单段精确不匹配 | `authz/login.ts` | `auth` | False | 边界条件 |
| TC-G07 | 多段精确前缀 | `src/auth/file.ts` | `src/auth` | True | 正常流程 |
| TC-G08 | 精确匹配文件 | `src/auth/session.ts` | `src/auth/session.ts` | True | 正常流程 |
| TC-G09 | Windows 路径兼容 | `src\\auth\\session.ts` | `auth/*` | True | 正常流程 |
| TC-G10 | 目录不匹配通配符 | `src/auth` | `src/auth/*` | False | 边界条件 |
| TC-G11 | 路径长度不足 | `a/b` | `a/b/c/d` | False | 异常处理 |
| TC-G12 | 根目录文件不匹配 | `Makefile` | `auth/*` | False | 边界条件 |
| TC-G13 | 末尾斜杠去除 | `src/auth/` | `src/auth` | True | 边界条件 |
| TC-G14 | 空文件路径 | `` | `auth/*` | False | 异常处理 |
| TC-G15 | 单段路径匹配单段模式 | `auth/login.ts` | `auth` | True | 正常流程 |

---

## TC-H01 ~ TC-H07：recall_by_path / recall_by_pattern 路径召回

| 用例编号 | 测试点描述 | 输入 | 预期输出 | 测试类型 |
|---------|-----------|------|---------|---------|
| TC-H01 | 按文件精确路径召回 | 修改 `src/auth/session.ts` | 召回相关的 bug | 正常流程 |
| TC-H02 | 按目录前缀召回 | 修改 `src/auth/login.ts` | 召回 auth 相关 bug | 正常流程 |
| TC-H03 | 不相关路径不召回 | 修改 `src/api/user.ts` | 不召回 | 正常流程 |
| TC-H04 | 只有 recalls 无 paths | bug 只有 recalls 无 paths | 仍能召回 | 正常流程 |
| TC-H05 | 结果按分数排序 | 多条匹配 | 按 score DESC | 正常流程 |
| TC-H06 | recall_by_pattern 模式匹配 | `recall_by_pattern("auth")` | 匹配 auth/* 相关 bug | 正常流程 |
| TC-H07 | recall_by_pattern 无匹配 | `recall_by_pattern("nonexist")` | 空列表 | 正常流程 |

---

## TC-I01 ~ TC-I05：get_bug_detail 详情查询

| 用例编号 | 测试点描述 | 输入 | 预期输出 | 测试类型 |
|---------|-----------|------|---------|---------|
| TC-I01 | 查询存在的 bug | `get_bug_detail(1)` | 返回所有字段完整 | 正常流程 |
| TC-I02 | 查询不存在的 bug | `get_bug_detail(9999)` | 返回 None | 异常处理 |
| TC-I03 | 详情包含 7 维度分数 | 7维度分数完整 | scores 列表正确 | 正常流程 |
| TC-I04 | paths 和 old_paths 分离 | 路径分类正确 | 非 old 和 old 分离 | 正常流程 |
| TC-I05 | 详情包含 tags/keywords/recalls | 各关联表数据 | 全部返回 | 正常流程 |

---

## TC-J01 ~ TC-J04：list_bugs 列表查询

| 用例编号 | 测试点描述 | 输入 | 预期输出 | 测试类型 |
|---------|-----------|------|---------|---------|
| TC-J01 | 按 status=active 过滤 | `status="active"` | 只返回 active 记录 | 正常流程 |
| TC-J02 | order_by=score（白名单） | `order_by="score"`（白名单内） | 正常排序 | 正常流程 |
| TC-J03 | order_by=invalid_col（非白名单） | `order_by="invalid_col"` | 自动降级为 score | 异常处理 |
| TC-J04 | 分页参数 | `limit=2, offset=1` | 返回第2页，每页2条 | 边界条件 |

---

## TC-K01 ~ TC-K03：mark_invalid 失效标记

| 用例编号 | 测试点描述 | 输入 | 预期输出 | 测试类型 |
|---------|-----------|------|---------|---------|
| TC-K01 | 标记失效带原因 | `mark_invalid(id, "功能已删除")` | status=invalid，solution 追加原因，updated_at 更新 | 正常流程 |
| TC-K02 | 标记失效不带原因 | `mark_invalid(id)` | status=invalid，solution 不变，updated_at 更新 | 正常流程 |
| TC-K03 | 标记不存在的 bug | `mark_invalid(9999)` | 无报错 | 异常处理 |

---

## TC-L01 ~ TC-L03：懒初始化与集成

| 用例编号 | 测试点描述 | 输入 | 预期输出 | 测试类型 |
|---------|-----------|------|---------|---------|
| TC-L01 | 数据库不存在时自动创建 | 删除 db，调用 add_bug | 数据库文件自动创建 | 正常流程 |
| TC-L02 | 完整 CRUD 流程 | add→update→get→delete | 全流程无报错 | 正常流程 |
| TC-L03 | 复发处理流程 | add→update verified=True→increment_score | verified 打回 False，累加分数，updated_at 更新 | 正常流程 |

---

## 执行说明

测试文件位于 `tests/test_bug_ops.py`，执行：

```bash
cd D:/yeyi/AI/cc-plugins/bug-book
python -m pytest tests/test_bug_ops.py -v
```

每个测试用例执行前清理数据库文件，执行后清理。
