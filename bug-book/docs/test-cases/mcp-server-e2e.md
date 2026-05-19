# MCP Server 端到端测试 - test_mcp_server_e2e.py

本文档覆盖 `tests/test_mcp_server_e2e.py` 中所有测试用例。文档和测试代码一一对应，TC-XX 编号在两侧保持一致。

**测试文件**: `tests/test_mcp_server_e2e.py`
**测试对象**: MCP Server 通过 stdio 协议的所有工具函数
**总用例数**: **27 个 MCP 工具** × 2 后端 = **54 次调用**（Hook 专用工具仅测试通用流程）

---

## 用例统计

| 分类 | 工具数 | 编号区间 | 说明 |
|------|--------|----------|------|
| CRUD 操作 | 5 | TC-M01 ~ TC-M05 | add_bug, update_bug, delete_bug, mark_invalid, increment_score |
| 查询功能 | 3 | TC-Q01 ~ TC-Q03 | get_bug_detail, list_bugs, count_bugs |
| 搜索功能 | 7 | TC-S01 ~ TC-S07 | search_by_keyword, search_by_tag, search_recent, search_high_score, search_top_critical, search_recent_unverified, search_by_status_and_score |
| 召回功能 | 1 | TC-R01 | recall_by_pattern |
| 影响关系管理 | 6 | TC-I01 ~ TC-I06 | add_impact, get_bug_impacts, get_impacted_bugs, analyze_impact_patterns, update_impacted_paths, delete_impact |
| 高级功能 | 2 | TC-A01 ~ TC-A02 | list_unverified_old, check_path_valid |
| Hook 专用功能 | 2 | TC-H01 ~ TC-H02 | recall_by_path_for_hook, migrate_from_bash_command |
| **总计** | **27** | | 每个工具在 SQLite 和 JSONL 后端各测试一次 |

---

## TC-M01 ~ TC-M05：CRUD 操作

| 用例编号 | 测试点描述 | MCP 工具 | 输入参数 | 预期输出 | 测试类型 |
|---------|-----------|---------|---------|---------|---------|
| TC-M01 | 新增 bug 记录 | `add_bug` | title, phenomenon, root_cause, solution, paths, tags, keywords | 返回 `[bug_id, score]`，bug_id > 0 | 正常流程 |
| TC-M02 | 更新 bug 记录 | `update_bug` | bug_id, title="更新后的标题" | 标题更新成功 | 正常流程 |
| TC-M03 | 删除 bug | `delete_bug` | bug_id | bug 被标记为无效或删除 | 正常流程 |
| TC-M04 | 标记 bug 失效 | `mark_invalid` | bug_id, reason="测试标记失效" | status="invalid", solution 包含原因 | 正常流程 |
| TC-M05 | 累加分数 | `increment_score` | bug_id, dimension="occurrences", delta=1.0 | occurrences 维度 +1 | 正常流程 |

---

## TC-Q01 ~ TC-Q03：查询功能

| 用例编号 | 测试点描述 | MCP 工具 | 输入参数 | 预期输出 | 测试类型 |
|---------|-----------|---------|---------|---------|---------|
| TC-Q01 | 获取 bug 详情 | `get_bug_detail` | bug_id | 返回完整的 bug 信息，包含 scores, paths, tags, recalls, impacts | 正常流程 |
| TC-Q02 | 列出 bugs | `list_bugs` | limit=5 | 返回最多 5 条 bug 列表 | 正常流程 |
| TC-Q03 | 统计 bug 总数 | `count_bugs` | 无 | 返回整数，表示数据库中的 bug 总数 | 正常流程 |

---

## TC-S01 ~ TC-S07：搜索功能

| 用例编号 | 测试点描述 | MCP 工具 | 输入参数 | 预期输出 | 测试类型 |
|---------|-----------|---------|---------|---------|---------|
| TC-S01 | 关键词搜索 | `search_by_keyword` | keyword="测试" | 返回匹配的 bug 列表（匹配 title/phenomenon/tags/keywords） | 正常流程 |
| TC-S02 | 标签搜索 | `search_by_tag` | tag="test" | 返回包含该标签的 bug 列表 | 正常流程 |
| TC-S03 | 最近创建的 bugs | `search_recent` | days=7, limit=10 | 返回最近 7 天创建的 bugs，最多 10 条 | 正常流程 |
| TC-S04 | 高分 bugs 搜索 | `search_high_score` | min_score=0, limit=10 | 返回分数 >= 0 的 bugs，最多 10 条 | 正常流程 |
| TC-S05 | 最严重的未验证 bugs | `search_top_critical` | limit=5 | 返回 verified=0 且分数最高的前 5 个 bugs | 正常流程 |
| TC-S06 | 最近未验证的 bugs | `search_recent_unverified` | days=7, limit=10 | 返回最近 7 天创建且 verified=0 的 bugs | 正常流程 |
| TC-S07 | 组合搜索（状态+分数） | `search_by_status_and_score` | status="active", min_score=0, max_score=100, limit=10 | 返回符合状态的 bugs，分数在范围内 | 正常流程 |

---

## TC-R01：召回功能

| 用例编号 | 测试点描述 | MCP 工具 | 输入参数 | 预期输出 | 测试类型 |
|---------|-----------|---------|---------|---------|---------|
| TC-R01 | 按模式召回 | `recall_by_pattern` | pattern="test/*", limit=10 | 返回 recalls 匹配该模式的 bugs | 正常流程 |

> **注意**：`recall_by_path` 和 `recall_by_path_full` 已改为内部使用，不再公开暴露。如需路径召回，使用 `recall_by_path_for_hook`。

---

## TC-I01 ~ TC-I06：影响关系管理

| 用例编号 | 测试点描述 | MCP 工具 | 输入参数 | 预期输出 | 测试类型 |
|---------|-----------|---------|---------|---------|---------|
| TC-I01 | 添加影响关系 | `add_impact` | source_bug_id, impacted_path, impact_type="regression", description, severity=7 | 返回 impact_id（整数） | 正常流程 |
| TC-I02 | 获取 bug 的影响 | `get_bug_impacts` | bug_id | 返回该 bug 导致的所有影响记录列表 | 正常流程 |
| TC-I03 | 获取受影响 bugs | `get_impacted_bugs` | file_path="affected.py" | 返回会影响该文件的 bugs 列表，包含影响信息 | 正常流程 |
| TC-I04 | 分析影响模式 | `analyze_impact_patterns` | limit=10 | 返回按受影响次数排序的路径模式列表 | 正常流程 |
| TC-I05 | 更新影响路径 | `update_impacted_paths` | old_path="old/path.py", new_path="new/path.py" | 返回更新的记录数 | 正常流程 |
| TC-I06 | 删除影响记录 | `delete_impact` | impact_id | 删除指定的影响记录 | 正常流程 |

---

## TC-A01 ~ TC-A02：高级功能

| 用例编号 | 测试点描述 | MCP 工具 | 输入参数 | 预期输出 | 测试类型 |
|---------|-----------|---------|---------|---------|---------|
| TC-A01 | 列出长期未验证的 bugs | `list_unverified_old` | days=30, limit=10 | 返回超过 30 天未验证的 bugs | 正常流程 |
| TC-A02 | 检查路径有效性 | `check_path_valid` | path="test.py" | 返回布尔值，表示路径是否存在于代码库 | 正常流程 |

> **注意**：`migrate_bug_paths_after_refactor` 已改为内部使用，不再公开暴露。路径迁移请使用 `migrate_from_bash_command`。

---

## TC-H01 ~ TC-H02：Hook 专用功能

| 用例编号 | 测试点描述 | MCP 工具 | 输入参数 | 预期输出 | 测试类型 |
|---------|-----------|---------|---------|---------|---------|
| TC-H01 | Hook 专用路径召回 | `recall_by_path_for_hook` | file_path, transcript_path, limit=10 | 返回 `{"content": [...], "additionalContext": "..."}` 格式，包含 bug 详情 | 正常流程 |
| TC-H02 | Bash 命令路径迁移 | `migrate_from_bash_command` | command="mv old.py new.py" | 返回 `{"content": [...], "additionalContext": "..."}` 格式，包含迁移摘要和详情 | 正常流程 |

> **注意**：Hook 专用工具返回 `{content, additionalContext}` 格式，其中 content 是简短摘要，additionalContext 是详细上下文。

---

## MCP 协议测试

除了工具调用，还测试了 MCP 协议本身：

| 用例编号 | 测试点描述 | MCP 方法 | 预期输出 | 测试类型 |
|---------|-----------|---------|---------|---------|
| TC-P01 | MCP 初始化 | `initialize` | 返回服务器能力声明 | 正常流程 |
| TC-P02 | 列出所有工具 | `tools/list` | 返回 27 个工具的定义列表 | 正常流程 |

---

## 执行说明

### 运行测试（独立脚本）

**注意**: 此测试文件不是 pytest 格式，而是一个独立的 Python 脚本。

```bash
cd D:/yeyi/AI/cc-plugins/bug-book
python tests/test_mcp_server_e2e.py
```

### 为什么不用 pytest？

这是一个端到端（E2E）测试，具有以下特点：

1. **需要启动子进程**：通过 `subprocess.Popen` 启动 MCP Server
2. **有执行顺序依赖**：必须先 add_bug 才能测试其他工具
3. **自定义输出格式**：显示每个工具的测试结果和错误信息
4. **双后端验证**：自动测试 SQLite 和 JSONL 两个后端

这些特性使得它更适合用独立脚本而非 pytest 格式实现。

### 如果要用 pytest

可以改造为 pytest 格式，但会失去一些灵活性。当前设计更符合 E2E 测试的最佳实践。

### 运行特定后端测试

```bash
# 只测试 SQLite 后端
python -m pytest tests/test_mcp_server_e2e.py -v -k sqlite

# 只测试 JSONL 后端
python -m pytest tests/test_mcp_server_e2e.py -v -k jsonl
```

### 直接运行测试脚本

```bash
# 不通过 pytest，直接运行脚本
python tests/test_mcp_server_e2e.py
```

---

## 测试架构说明

### 端到端测试特点

与单元测试不同，E2E 测试通过 **stdio 协议** 与真实的 MCP Server 进程通信：

1. **启动子进程**：使用 `subprocess.Popen` 启动 MCP Server
2. **JSON-RPC 2.0 协议**：通过 stdin/stdout 发送和接收 JSON-RPC 消息
3. **真实环境**：测试完整的 MCP Server → Backend 调用链
4. **双后端验证**：每个工具在 SQLite 和 JSONL 两个后端上都执行

### 测试流程

```
测试脚本 (Python)
    ↓ stdio (JSON-RPC 2.0)
MCP Server 进程
    ↓ 调用
Backend (SQLite/JSONL)
    ↓ 返回
MCP Server 进程
    ↓ stdio (JSON-RPC 2.0)
测试脚本 (Python)
```

### 测试隔离

- **临时数据**：每次测试使用独立的数据库/文件
- **进程隔离**：每个后端测试启动独立的 MCP Server 进程
- **自动清理**：测试结束后终止子进程

---

## 覆盖率说明

### MCP 工具覆盖率

✅ **100% 覆盖**：所有 31 个 MCP 工具都被测试

| 类别 | 工具数 | 覆盖率 |
|------|--------|--------|
| CRUD | 5 | 100% |
| 查询 | 3 | 100% |
| 搜索 | 7 | 100% |
| 召回 | 1 | 100% |
| 影响关系 | 6 | 100% |
| 高级功能 | 2 | 100% |
| Hook 专用 | 2 | 100% |
| **总计** | **27** | **100%** |

### 后端接口覆盖率

所有 MCP 工具都直接映射到后端公共 API，因此：

- ✅ **后端 API 100% 覆盖**（通过 MCP 层间接测试）
- ✅ **双后端兼容性验证**（SQLite + JSONL）

---

## 与单元测试的关系

### 测试分层

1. **单元测试层** (`test_backends.py`)
   - 直接调用后端 API
   - 细粒度的功能验证
   - 150 个测试用例（75 函数 × 2 后端）

2. **端到端测试层** (`test_mcp_server_e2e.py`)
   - 通过 MCP 协议调用
   - 完整的调用链验证
   - 62 次工具调用（31 工具 × 2 后端）

### 互补关系

- **单元测试**：验证后端逻辑的正确性
- **E2E 测试**：验证 MCP Server 与后端的集成
- **两者结合**：确保从协议层到数据层的完整可靠性

---

## 常见问题

### Q: 为什么 E2E 测试比单元测试慢？

A: E2E 测试需要：
1. 启动子进程（MCP Server）
2. 通过 stdio 通信（JSON 序列化/反序列化）
3. 完整的调用链（MCP → Backend → Database）

而单元测试直接调用 Python 函数，没有这些开销。

### Q: 如果 E2E 测试失败，如何调试？

A: 
1. 查看 stderr 输出：`proc.stderr.read()`
2. 检查 MCP Server 日志
3. 单独运行某个工具的测试
4. 对比单元测试结果，定位是 MCP 层还是 Backend 层的问题

### Q: 为什么需要双后端测试？

A: 确保：
1. SQLite 和 JSONL 实现的行为一致
2. MCP Server 对不同后端的兼容性
3. 用户切换后端时不会影响功能

---

## 相关文档

- [后端双实现测试](./backends.md) - `tests/test_backends.py`
- [路径匹配工具测试](./path-utils.md) - `tests/test_path_utils.py`
- [元数据存储测试](./metadata-store.md) - `tests/test_metadata_store.py`
- [测试用例索引](./README.md) - 所有测试文档的索引
