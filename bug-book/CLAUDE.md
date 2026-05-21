# CLAUDE.md - bug-book

## MCP Server 职责

入口位于 `mcp/mcp_server.py`

**MCP Server 提供** 记录、搜索、召回、整理等功能API

## Skills 职责

| Skill | 文件位置 | 职责 |
|-------|----------|------|
| `bug-record` | `skills/bug-record/SKILL.md` | 记录问题到数据库，包括现象、根因、解决方案、评分等 |

修改 Skill 时，务必确认是否需要在 MCP Server 后端做相应修改。

## 三层架构

```
MCP Server → BugService (业务编排) → BugBackend (原子操作) → JSONLBackend (存储实现)
```

| 层级    | 文件 | 职责                                                                                           |
|-------|------|----------------------------------------------------------------------------------------------|
| 业务编排层 | `mcp/bug_service.py` | 6 个公共接口：save_bugs, search_bugs, organize_bugs, get_bug_detail, recall_by_path, migrate_paths |
| 存储接口层 | `mcp/bug_backend.py` | add_bug, update_bug, get_bug, find_*, query 等原子方法                                            |
| 存储实现层 | `mcp/jsonl_backend.py` | JSONL 文件持久化                                                                                  |

## 开发规范

修改 `scripts/*.py` 或 `mcp/*.py` 后，必须按以下顺序：

1. **先**：在 `docs/test-cases/` 对应的测试文档中添加测试用例（TC-XX 分类编号）
   - 存储后端 → `docs/test-cases/bug-backend.md`
   - 业务服务层 → `docs/test-cases/bug-service.md`
   - 路径工具 → `docs/test-cases/path-utils.md`
   - 本地元数据存储 → `docs/test-cases/metadata-store.md`
   - MCP Server → `docs/test-cases/mcp-server-e2e.md`

2. **再**：在对应的测试文件中实现测试代码，用例编号与文档一致
   - `tests/test_bug_backend.py` - 存储后端单元测试（35个原子操作测试）
   - `tests/test_bug_service.py` - 业务服务层测试（30个业务编排测试）
   - `tests/test_path_utils.py` - 路径匹配工具测试
   - `tests/test_metadata_store.py` - 元数据存储测试
   - `tests/test_mcp_server_e2e.py` - MCP Server 端到端测试

3. **然后**：运行测试确保通过

   ```bash
   # 运行核心测试（存储层 + 服务层）
   python -m pytest tests/test_bug_backend.py tests/test_bug_service.py -v

   # 运行所有 pytest 测试
   python -m pytest tests/ -v

   # E2E 测试是独立脚本
   python tests/test_mcp_server_e2e.py
   ```

4. **最后**：更新相关 Skill 文档中的 API 调用说明或示例
   - `skills/bug-record/SKILL.md` - Bug 记录相关 API

**重要原则**：
- 测试用例文档和代码必须一一对应，每个用例编号在两侧保持一致
- 新增/修改功能时，Bug Backend / Bug Service（后端实现）、MCP Server（后端接口）、Skill（前端应用）及测试用例/函数都必须配套修改

