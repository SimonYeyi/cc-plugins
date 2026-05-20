# CLAUDE.md - bug-book

## Skills 职责

| Skill | 文件位置 | 职责 |
|-------|----------|------|
| `bug-record` | `skills/bug-record/SKILL.md` | 记录问题到数据库，包括现象、根因、解决方案、评分等 |

修改 Skill 时，在对应的 SKILL.md 文件中实现逻辑。

**MCP Server 提供**：搜索、召回、整理功能（`mcp/mcp_server.py`）

## 开发规范

修改 `scripts/*.py` 或 `mcp/*.py` 后，必须按以下顺序：

1. **先**：在 `docs/test-cases/` 对应的测试文档中添加测试用例（TC-XX 分类编号）
   - 后端 API → `docs/test-cases/backends.md`
   - 路径工具 → `docs/test-cases/path-utils.md`
   - 元数据存储 → `docs/test-cases/metadata-store.md`
   - MCP Server → `docs/test-cases/mcp-server-e2e.md`

2. **再**：在对应的测试文件中实现测试代码，用例编号与文档一致
   - `tests/test_backends.py` - 后端单元测试（JSONL）
   - `tests/test_path_utils.py` - 路径匹配工具测试
   - `tests/test_metadata_store.py` - 元数据存储测试
   - `tests/test_mcp_server_e2e.py` - MCP Server 端到端测试

3. **然后**：运行测试确保通过
   
   ```bash
   # 运行所有 pytest 测试
   python -m pytest tests/test_backends.py tests/test_path_utils.py tests/test_metadata_store.py -v
   
   # E2E 测试是独立脚本，不能用 pytest 运行
   python tests/test_mcp_server_e2e.py
   ```

4. **最后**：更新相关 Skill 文档中的 API 调用说明或示例
   - `skills/bug-record/SKILL.md` - Bug 记录相关 API

**重要原则**：
- 文档和代码必须一一对应，每个用例编号在两侧保持一致
- 测试文件位于 `docs/test-cases/README.md` 有完整索引
- 新增功能时，先查看现有测试文档的分类和编号规则

