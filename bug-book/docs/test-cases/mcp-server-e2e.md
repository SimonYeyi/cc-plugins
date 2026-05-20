# MCP Server E2E 测试 - test_mcp_server_e2e.py

本文档覆盖 `tests/test_mcp_server_e2e.py` 中所有测试用例。

**测试文件**: `tests/test_mcp_server_e2e.py`
**测试方式**: 通过 stdio 协议与 MCP Server 真实通信
**测试对象**: 4 个 MCP 工具 + 2 个 Hook 专用函数

---

## MCP Server 工具列表（重构后）

| 工具名 | 描述 | 返回格式 |
|--------|------|---------|
| `mcp__bug_book__save_bugs` | 统一保存接口 | `{content: [{text: JSON}]}` |
| `mcp__bug_book__get_bug_detail` | 获取 bug 详情 | `{content: [{text: JSON}]}` |
| `mcp__bug_book__search_bugs` | 统一搜索 | `{content: [{text: JSON}]}` |
| `mcp__bug_book__organize_bugs` | 整理错题集 | `{content: [{text: 报告}]}` |

---

## TC-SB01 ~ TC-SB08：save_bugs 工具

### TC-SB01：add 模式

| 用例 | 描述 | 输入 | 预期 |
|------|------|------|------|
| TC-SB01-01 | 新增最小字段 | `{mode: "add", title, phenomenon}` | 返回 `{id: >0}` |
| TC-SB01-02 | 新增带完整字段 | `{mode: "add", title, phenomenon, scores, paths, tags, keywords, recalls}` | id>0, score>0 |
| TC-SB01-03 | add 禁止传 id | `{mode: "add", id: 123, title, phenomenon}` | 返回错误 |
| TC-SB01-04 | add 缺少必填 | `{mode: "add", title: "x"}` | 返回错误 |

### TC-SB02：add_paths 模式

| 用例 | 描述 | 输入 | 预期 |
|------|------|------|------|
| TC-SB02-01 | 追加新 paths | `{mode: "add_paths", id, paths: [{file: "a.ts", functions: ["f1"]}]}` | paths 合并 |
| TC-SB02-02 | 相同 file 合并 | 追加同 file 不同 functions | functions 去重 |

### TC-SB03：remove_paths 模式

| 用例 | 描述 | 输入 | 预期 |
|------|------|------|------|
| TC-SB03-01 | 移除整个 file | `{mode: "remove_paths", id, paths: [{file: "a.ts"}]}` | file 删除 |
| TC-SB03-02 | 只移除 functions | `{mode: "remove_paths", id, paths: [{file: "a.ts", functions: ["f1"]}]}` | 其他 functions 保留 |

### TC-SB04：update_fields 模式

| 用例 | 描述 | 输入 | 预期 |
|------|------|------|------|
| TC-SB04-01 | 更新单字段 | `{mode: "update_fields", id, title: "新标题"}` | title 更新 |
| TC-SB04-02 | 更新多字段 | `{mode: "update_fields", id, title, solution, status}` | 全部更新 |
| TC-SB04-03 | bug 不存在 | `{mode: "update_fields", id: 9999, title}` | 返回错误 |

### TC-SB05：delete 模式

| 用例 | 描述 | 输入 | 预期 |
|------|------|------|------|
| TC-SB05-01 | 软删除 | `{mode: "delete", id}` | status='invalid' |
| TC-SB05-02 | 删除不存在 | `{mode: "delete", id: 9999}` | 返回错误 |

### TC-SB06：increment_scores / decrement_scores 模式

| 用例 | 描述 | 输入 | 预期 |
|------|------|------|------|
| TC-SB06-01 | 累加分数 | `{mode: "increment_scores", id, scores: {occurrences: 1.0}}` | 分数增加 |
| TC-SB06-02 | 扣减分数 | `{mode: "decrement_scores", id, scores: {occurrences: 0.5}}` | 分数减少 |

### TC-SB07：add_impacts 模式

| 用例 | 描述 | 输入 | 预期 |
|------|------|------|------|
| TC-SB07-01 | 添加影响 | `{mode: "add_impacts", id, impacts: [{solution_change, impact_description, impact_type, severity}]}` | impact_id>0 |

### TC-SB08：批量操作

| 用例 | 描述 | 输入 | 预期 |
|------|------|------|------|
| TC-SB08-01 | 批量新增 | `bugs: [{mode: "add"...}, {mode: "add"...}]` | 返回多个结果 |
| TC-SB08-02 | 混合批量 | `bugs: [{mode: "add"...}, {mode: "update..."}]` | 各自执行 |

---

## TC-SR01 ~ TC-SR08：search_bugs 工具

| 用例 | 模式 | 输入 | 预期 |
|------|------|------|------|
| TC-SR01 | keyword | `{mode: "keyword", keyword: "session"}` | 返回匹配 bugs |
| TC-SR02 | tag | `{mode: "tag", tag: "auth"}` | 返回标签匹配 |
| TC-SR03 | recent | `{mode: "recent", days: 7}` | 返回最近创建 |
| TC-SR04 | high_score | `{mode: "high_score", min_score: 30}` | 返回 score>=30 |
| TC-SR05 | critical | `{mode: "critical", limit: 5}` | 返回最严重 |
| TC-SR06 | unverified | `{mode: "unverified", days: 30}` | 返回长期未验证 |
| TC-SR07 | custom | `{mode: "custom", status: "active", min_score: 0}` | 按条件过滤 |
| TC-SR08 | module | `{mode: "module", pattern: "auth/*"}` | 按模式召回 |

---

## TC-GD01 ~ TC-GD02：get_bug_detail 工具

| 用例 | 描述 | 输入 | 预期 |
|------|------|------|------|
| TC-GD01 | 查询存在 | `{bug_id}` | 返回完整 bug 信息 |
| TC-GD02 | 查询不存在 | `{bug_id: 9999}` | 返回错误 |

---

## TC-OB01 ~ TC-OB05：organize_bugs 工具

| 用例 | 描述 | 预期 |
|------|------|------|
| TC-OB01 | 执行整理 | 返回包含 4 个步骤的完整报告 |
| TC-OB02 | 压缩文件 | 移除 invalid 记录，报告清理数量 |
| TC-OB03 | 检查路径 | 识别无效路径 bugs |
| TC-OB04 | 检查未验证 | 识别 30 天以上未验证 bugs |
| TC-OB05 | 统计数据 | 总记录数、活跃数、解决数 |

---

## TC-HK01 ~ TC-HK07：Hook 专用函数

### recall_for_hook

| 用例 | 描述 | 输入 | 预期 |
|------|------|------|------|
| TC-HK01 | 正常召回 | `recall_for_hook(file_path, transcript_path, limit)` | hookSpecificOutput 格式 |
| TC-HK02 | 10轮内重复召回 | transcript 已有 recall 标记 | additionalContext="" |
| TC-HK03 | 缓存失效 | 12轮对话，recall 在第1轮 | 重新召回 |
| TC-HK04 | 无匹配 | 查询不存在文件 | 简短提示文本 |

### migrate_path_for_hook

| 用例 | 描述 | 输入 | 预期 |
|------|------|------|------|
| TC-HK05 | mv 命令 | `{command: "mv old.py new.py"}` | 返回迁移数量 |
| TC-HK06 | git mv | `{command: "git mv old.py new.py"}` | 同上 |
| TC-HK07 | 非迁移命令 | `{command: "echo hello"}` | 提示非迁移指令 |

---

## TC-P01 ~ TC-P02：MCP 协议

| 用例 | 描述 | 预期 |
|------|------|------|
| TC-P01 | initialize | 返回协议版本和能力声明 |
| TC-P02 | tools/list | 返回 4 个工具定义 |

---

## 执行说明

```bash
cd D:/yeyi/AI/cc-plugins/bug-book
python tests/test_mcp_server_e2e.py
```

---

## 相关文档

- [后端单元测试](./backends.md) - `tests/test_backends.py`
- [测试用例索引](./README.md)